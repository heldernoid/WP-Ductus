// WP-Ductus in the browser: the same renderer and engine as ductus/render.py and ductus/engine.py, line for line.
// Every parameter starts at zero; only the edit list (model/ductus.edits) writes into it. Nothing is trained.

export const H = 96, W = 96, N = H * W;
const STEP = 0.35;                       // sample spacing along a stroke, in pixels (as in render.py)
const PATH_WIDTH = 1.2;                  // the thin pen of the `path` map

// ---- rendering: strokes [[x, y, w], ...] -> maps ink, path, wid, t, dn, up, lf, rt (Float64Array, row-major) ----------
export function strokeLength(st) {
  let L = 0;
  for (let k = 1; k < st.length; k++) L += Math.hypot(st[k][0] - st[k - 1][0], st[k][1] - st[k - 1][1]);
  return L;
}

export function render(strokes) {
  const M = {};
  for (const k of ["ink", "path", "wid", "t", "dn", "up", "lf", "rt"]) M[k] = new Float64Array(N);
  const total = strokes.reduce((a, s) => a + strokeLength(s), 0) || 1;
  let done = 0;
  for (const st of strokes) {
    if (st.length === 1) { stamp(M, st[0][0], st[0][1], st[0][2], done / total, 0, 0); continue; }
    for (let k = 1; k < st.length; k++) {
      const [x0, y0, w0] = st[k - 1], [x1, y1, w1] = st[k];
      const seg = Math.hypot(x1 - x0, y1 - y0);
      if (seg === 0) continue;
      const dx = (x1 - x0) / seg, dy = (y1 - y0) / seg;
      const n = Math.max(1, Math.ceil(seg / STEP));
      for (let j = 0; j <= n; j++) {
        const f = j / n;
        stamp(M, x0 + f * (x1 - x0), y0 + f * (y1 - y0), w0 + f * (w1 - w0), (done + f * seg) / total, dx, dy);
      }
      done += seg;
    }
  }
  return M;
}

function stamp(M, cx, cy, w, t, dx, dy) {
  const r = Math.max(w, 0.8) / 2, rp = PATH_WIDTH / 2;
  // Python's int() truncates toward zero; Math.trunc matches it for the negative edge case too
  const x0 = Math.max(0, Math.trunc(cx - r - 1)), x1 = Math.min(W - 1, Math.trunc(cx + r + 1));
  const y0 = Math.max(0, Math.trunc(cy - r - 1)), y1 = Math.min(H - 1, Math.trunc(cy + r + 1));
  for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) {
    const dist = Math.hypot(x + 0.5 - cx, y + 0.5 - cy), i = y * W + x;
    M.path[i] = Math.max(M.path[i], Math.min(1, Math.max(0, rp - dist + 0.5)));
    const cov = Math.min(1, Math.max(0, r - dist + 0.5));
    if (cov <= 0) continue;
    if (cov > M.ink[i] + 1e-9) { M.ink[i] = cov; M.wid[i] = w; M.t[i] = t; }
    M.dn[i] = Math.max(M.dn[i], cov * Math.max(0, dy));
    M.up[i] = Math.max(M.up[i], cov * Math.max(0, -dy));
    M.rt[i] = Math.max(M.rt[i], cov * Math.max(0, dx));
    M.lf[i] = Math.max(M.lf[i], cov * Math.max(0, -dx));
  }
}

export const TRACE_WIDEN = 1, COPY_WIDEN = 3;   // extra tolerance steps: a 2 px band for tracing, 4 px for copying

// Copy mode: your letter is fitted onto the model before comparing (as fit() in render.py, line for line), so shape,
// ductus and shading mark the precision of your strokes, not where, how big or how slanted you wrote.
const FIT_STEP = 0.5, FIT_SCALE = [0.7, 1.45], FIT_SHEAR = 0.6, FIT_ROUNDS = 6, FIT_KEEP = 0.8, FIT_PRIOR = 0.1,
  FIT_CORE = 0.9, FIT_NEAR = 3.0;

export function samples(strokes) {
  const out = [];
  for (const st of strokes) {
    if (st.length === 1) { out.push([st[0][0], st[0][1]]); continue; }
    for (let k = 1; k < st.length; k++) {
      const a = st[k - 1], b = st[k], n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / FIT_STEP));
      for (let j = 0; j < n; j++) out.push([a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n]);
    }
    out.push([st[st.length - 1][0], st[st.length - 1][1]]);
  }
  return out;
}

function moments(pts) {
  const n = pts.length;
  let sx = 0, sy = 0;
  for (const p of pts) sx += p[0];
  for (const p of pts) sy += p[1];
  const mx = sx / n, my = sy / n;
  let v = 0, c = 0;
  for (const p of pts) v += (p[1] - my) * (p[1] - my);
  for (const p of pts) c += (p[0] - mx) * (p[1] - my);
  const vy = v / n, cxy = c / n;
  return [mx, my, vy, vy > 1e-6 ? cxy / vy : 0];
}

function core(pts) {
  const [mx, my] = moments(pts);
  const d = pts.map(p => (p[0] - mx) * (p[0] - mx) + (p[1] - my) * (p[1] - my));
  const cut = [...d].sort((u, v) => u - v)[Math.floor(FIT_CORE * (pts.length - 1))];
  return pts.filter((p, i) => d[i] <= cut);
}

function nearest(A, B) {             // for each point of A: the index of the nearest point of B, and the squared distance
  const j = [], d = [];
  for (const [ax, ay] of A) {
    let best = Infinity, bi = 0;
    for (let k = 0; k < B.length; k++) {
      const DX = B[k][0] - ax, DY = B[k][1] - ay, D = DX * DX + DY * DY;
      if (D < best) { best = D; bi = k; }
    }
    j.push(bi); d.push(best);
  }
  return [j, d];
}

function trimmed(dist) {
  const cut = [...dist].sort((u, v) => u - v)[Math.floor(FIT_KEEP * (dist.length - 1))];
  const keep = [];
  for (let i = 0; i < dist.length; i++) if (dist[i] <= cut) keep.push(i);
  return keep;
}

function refine(P, Q, A, B, e, f) {
  let cost = 0;
  for (let r = 0; r <= FIT_ROUNDS; r++) {
    const q = Q.map(([x, y]) => [A * x + B * y + e, A * y + f]);
    const [jq, dq] = nearest(q, P), [jp, dp] = nearest(P, q);
    let cq = 0, cp = 0;
    for (const v of dq) cq += v;
    for (const v of dp) cp += v;
    cost = cq / dq.length + cp / dp.length;
    if (r === FIT_ROUNDS) break;
    const kq = trimmed(dq), kp = trimmed(dp);
    const pairs = kq.map(i => [Q[i], P[jq[i]]]).concat(kp.map(i => [Q[jp[i]], P[i]]));
    const n = pairs.length;
    let x0 = 0, y0 = 0, X0 = 0, Y0 = 0;
    for (const [u] of pairs) x0 += u[0];
    for (const [u] of pairs) y0 += u[1];
    for (const [, v] of pairs) X0 += v[0];
    for (const [, v] of pairs) Y0 += v[1];
    x0 /= n; y0 /= n; X0 /= n; Y0 /= n;
    let sxx = 0, syy = 0, sxy = 0, sXx = 0, sYy = 0, sXy = 0;
    for (const [u, v] of pairs) {
      const x = u[0] - x0, y = u[1] - y0, X = v[0] - X0, Y = v[1] - Y0;
      sxx += x * x; syy += y * y; sxy += x * y; sXx += X * x; sYy += Y * y; sXy += X * y;
    }
    const w = FIT_PRIOR * (sxx + syy);
    const det = (sxx + syy + w) * (syy + w) - sxy * sxy;
    A = ((sXx + sYy + w) * (syy + w) - sxy * sXy) / det;
    B = ((sxx + syy + w) * sXy - sxy * (sXx + sYy + w)) / det;
    A = Math.min(FIT_SCALE[1], Math.max(FIT_SCALE[0], A));
    B = Math.min(FIT_SHEAR * A, Math.max(-FIT_SHEAR * A, B));
    e = X0 - A * x0 - B * y0; f = Y0 - A * y0;
  }
  return [cost, [A, 0, B, A, e, f]];
}

// the affine map [a, b, c, d, e, f]: x' = a x + c y + e, y' = b x + d y + f (as fit() in render.py)
export function fit(model, attempt) {
  const P = samples(model), Q = samples(attempt);
  if (!P.length || !Q.length) return [1, 0, 0, 1, 0, 0];
  const [mxm, mym, vym, km] = moments(core(P)), [mxa, mya, vya, ka] = moments(core(Q));
  const s = vya > 1e-6 && vym > 1e-6 ? Math.min(FIT_SCALE[1], Math.max(FIT_SCALE[0], Math.sqrt(vym / vya))) : 1;
  const dk = Math.min(FIT_SHEAR, Math.max(-FIT_SHEAR, ka - km));
  const starts = [[1, 0, mxm - mxa, mym - mya], [s, -s * dk, mxm - s * mxa + s * dk * mya, mym - s * mya]];
  let best = null;
  for (const [A, B, e, f] of starts) {
    const r = refine(P, Q, A, B, e, f);
    if (!best || r[0] < best[0]) best = r;
  }
  return best[1];
}

export const apply = ([a, b, c, d, e, f], strokes) =>
  strokes.map(st => st.map(([x, y, ...rest]) => [a * x + c * y + e, b * x + d * y + f, ...rest]));

export function centred(model, attempt) {
  const P = samples(model), Q = samples(attempt);
  if (!P.length || !Q.length) return attempt;
  const [mxm, mym] = moments(P), [mxa, mya] = moments(Q);
  return apply([1, 0, 0, 1, mxm - mxa, mym - mya], attempt);
}

export function keepNear(strokes, [a, b, c, d, e, f], ref) {
  const out = [];
  for (const st of strokes) {
    let pts;
    if (st.length === 1) pts = [st[0].slice(0, 3)];
    else {
      pts = [];
      for (let k = 1; k < st.length; k++) {
        const u = st[k - 1], v = st[k], n = Math.max(1, Math.ceil(Math.hypot(v[0] - u[0], v[1] - u[1]) / FIT_STEP));
        for (let j = 0; j < n; j++) pts.push([0, 1, 2].map(i => u[i] + (v[i] - u[i]) * j / n));
      }
      pts.push(st[st.length - 1].slice(0, 3));
    }
    let cur = [];
    for (const p of pts) {
      const qx = a * p[0] + c * p[1] + e, qy = b * p[0] + d * p[1] + f;
      let best = Infinity;
      for (const [rx, ry] of ref) { const DX = rx - qx, DY = ry - qy, D = DX * DX + DY * DY; if (D < best) best = D; }
      if (best <= FIT_NEAR * FIT_NEAR) cur.push(p);
      else { if (cur.length > 1 || (cur.length && st.length === 1)) out.push(cur); cur = []; }
    }
    if (cur.length > 1 || (cur.length && st.length === 1)) out.push(cur);
  }
  return out;
}

export function formPair(model, attempt, T) {
  if (!samples(attempt).length) return [attempt, model];
  const a = keepNear(attempt, T, samples(model)), m = keepNear(model, [1, 0, 0, 1, 0, 0], samples(apply(T, attempt)));
  return [centred(model, a), m];
}

export const align = (model, attempt) => apply(fit(model, attempt), attempt);

export function inputs(model, attempt, hasPressure, copy = false) {
  let form = attempt, mform = model;
  if (copy) { const T = fit(model, attempt); [form, mform] = formPair(model, attempt, T); attempt = apply(T, attempt); }
  const out = { widen: copy ? COPY_WIDEN : TRACE_WIDEN, copy: copy ? 1 : 0 };
  for (const [p, s] of [["m_", model], ["a_", attempt]]) for (const [k, v] of Object.entries(render(s))) out[p + k] = v;
  out.a_form = copy ? render(form).path : out.a_path;
  out.m_form = copy ? render(mform).path : out.m_path;
  out.has_pressure = hasPressure ? 1 : 0;
  return out;
}

// ---- the engine ------------------------------------------------------------------------------------------------
const ACT = { relu: v => Math.max(v, 0), clip01: v => Math.min(1, Math.max(0, v)), none: v => v };

function* allLayers(layers) {
  for (const L of layers) { if (L.op === "loop") yield* allLayers(L.body); else yield L; }
}

export class Net {
  constructor(arch, edits) {
    this.arch = arch; this.L = {}; this.P = {}; this.why = {};
    for (const L of allLayers(arch.layers)) {
      this.L[L.id] = L;
      if (L.op === "conv") this.P[L.id] = { taps: [], b: new Float64Array(L.out.length) };
      else if (L.op === "zone") this.P[L.id] = { rects: [], b: new Float64Array(L.out.length) };
      else if (L.op === "linear") this.P[L.id] = { W: L.out.map(() => new Float64Array(L.in.length)), b: new Float64Array(L.out.length) };
    }
    edits.split("\n").forEach((raw, n) => {
      const line = raw.split("#")[0].trim();
      if (!line) return;
      const t = line.split(/\s+/), L = this.L[t[1]], P = this.P[t[1]];
      const idx = (list, name) => { const i = list.indexOf(name); if (i < 0) throw new Error(`edit line ${n + 1}: unknown ${name}`); return i; };
      if (t[0] === "TAP") {
        const o = idx(L.out, t[2]), i = idx(L.in, t[3]), key = `${o},${i},${t[4]},${t[5]}`;
        const old = P.taps.findIndex(q => q.key === key);           // a repeated tap keeps its last value, as in Python
        const tap = { key, o, i, dy: +t[4], dx: +t[5], v: +t[6] };
        if (old >= 0) P.taps[old] = tap; else P.taps.push(tap);
      } else if (t[0] === "BIAS") {
        P.b[idx(L.out, t[2])] = +t[3];
        if (raw.includes("#")) this.why[`${t[1]} ${t[2]}`] = raw.split("#").slice(1).join("#").trim();
      } else if (t[0] === "ZONE") {
        const [r0, r1] = t[4].split(":").map(Number), [c0, c1] = t[5].split(":").map(Number);
        // the scale: a number, `x` / `y` (the pixel's column / row centre) or `|y-c|` (its distance from row c)
        const s = t[6], c = s.startsWith("|y-") ? +s.slice(3, -1) : 0;
        const f = s === "x" ? (y, x) => x + 0.5 : s === "y" ? (y, x) => y + 0.5
          : s === "xy" ? (y, x) => (x + 0.5) * (y + 0.5) : s === "yy" ? (y, x) => (y + 0.5) * (y + 0.5)
          : s.startsWith("|y-") ? (y, x) => Math.abs(y + 0.5 - c) : (() => { const v = +s; return () => v; })();
        P.rects.push({ o: idx(L.out, t[2]), i: idx(L.in, t[3]), r0, r1, c0, c1, f });
      } else if (t[0] === "LINK") {
        P.W[idx(L.out, t[2])][idx(L.in, t[3])] = +t[4];
      } else throw new Error(`edit line ${n + 1}: unknown edit kind ${t[0]}`);
    });
  }

  forward(inp) {
    const T = { ...inp };
    this.run(this.arch.layers, T);
    return T;
  }

  run(layers, T) { for (const L of layers) this[L.op](L, T); }
  loop(L, T) {
    const n = L.n_from != null ? Math.round(T[L.n_from]) : L.n;    // a fixed count, or one an input scalar sets
    for (let k = 0; k < n; k++) this.run(L.body, T);
  }

  conv(L, T) {
    const P = this.P[L.id], act = ACT[L.act];
    const out = L.out.map((_, o) => new Float64Array(N).fill(P.b[o]));
    for (const { o, i, dy, dx, v } of P.taps) {
      const X = T[L.in[i]], Y = out[o];
      for (let y = 0; y < H; y++) {
        const yy = y + dy;
        if (yy < 0 || yy >= H) continue;
        for (let x = 0; x < W; x++) {
          const xx = x + dx;
          if (xx >= 0 && xx < W) Y[y * W + x] += v * X[yy * W + xx];
        }
      }
    }
    L.out.forEach((name, o) => { const Y = out[o]; for (let k = 0; k < N; k++) Y[k] = act(Y[k]); T[name] = Y; });
  }

  max3(L, T) {
    L.in.forEach((src, j) => {
      const X = T[src], Y = new Float64Array(N);
      for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
        let m = -Infinity;                                   // zero padding, as np.pad: the border sees 0
        for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
          const yy = y + dy, xx = x + dx;
          const v = yy < 0 || yy >= H || xx < 0 || xx >= W ? 0 : X[yy * W + xx];
          if (v > m) m = v;
        }
        Y[y * W + x] = m;
      }
      T[L.out[j]] = Y;
    });
  }

  zone(L, T) {
    const P = this.P[L.id], v = Float64Array.from(P.b);
    for (const { o, i, r0, r1, c0, c1, f } of P.rects) {
      const X = T[L.in[i]];
      let sum = 0;
      for (let y = 0; y < H; y++) {
        if (!(y + 0.5 >= r0 && y + 0.5 < r1)) continue;
        for (let x = 0; x < W; x++) if (x + 0.5 >= c0 && x + 0.5 < c1) sum += f(y, x) * X[y * W + x];
      }
      v[o] += sum;
    }
    L.out.forEach((name, o) => { T[name] = ACT[L.act](v[o]); });
  }

  linear(L, T) {
    const P = this.P[L.id], x = L.in.map(n => T[n]);
    L.out.forEach((name, o) => {
      let s = P.b[o];
      for (let i = 0; i < x.length; i++) s += P.W[o][i] * x[i];
      T[name] = ACT[L.act](s);
    });
  }

  // mean y, variance of y and the slope of x on y, from the sums n, Σx, Σy, Σxy, Σyy (a fixed op, as in engine.py)
  moments(L, T) {
    for (const [p, names] of Object.entries(L.parts)) {
      const [n, sx, sy, sxy, syy] = names.map(k => T[k]);
      if (n <= 1e-6) { T[p + "_my"] = T[p + "_vy"] = T[p + "_slope"] = 0; continue; }
      const my = sy / n, vy = syy / n - (sy / n) ** 2;
      T[p + "_my"] = my; T[p + "_vy"] = vy;
      T[p + "_slope"] = vy > 1e-6 ? (sxy / n - (sx / n) * my) / vy : 0;
    }
  }

  ratio(L, T) {
    const eps = L.eps ?? 1e-6, empty = L.empty ?? 0;
    for (const [out, [num, den, own]] of Object.entries(L.parts)) {   // a part may name its own empty value
      const d = den.reduce((a, n) => a + T[n], 0);
      T[out] = d > eps ? num.reduce((a, n) => a + T[n], 0) / d : own ?? empty;
    }
  }
}
