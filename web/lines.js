// Lines of text: lay a phrase out on several rows of guidelines, cut what was written into one piece per letter, and
// hand each letter to the same network as a single letter (in its own 96 x 96 frame). Page logic, not the network:
// nothing here has weights; it decides which ink belongs to which letter.

export const PITCH = 88;      // rows of guidelines 88 px apart: a descender line (88) sits 8 px above the next ascender (96)
export const ROW_SPLIT = 92;  // ink below this y (and its multiples of PITCH) belongs to the next row
const GAP = 1;                // between neighbouring letters in the upright frame: their hairlines (almost) meet
const DIGIT_GAP = 5;          // beside a digit: digits are not joined, and at 1 px "1733" ran together
const WORD = 14;              // between words, 0.7 of an x-height
const EDGE = 4;               // free margin left and right of each row

// the upright ("unslanted") x of a point: the x where the 55-degree line through it meets the row's baseline
export const ux = (x, y, row, st) => x - (st.guides.baseline + row * PITCH - y) * st.slant;

function extent(strokes, st) {
  let lo = Infinity, hi = -Infinity, xmin = Infinity, xmax = -Infinity;
  for (const s of strokes) for (const [x, y, w] of s) {
    const u = ux(x, y, 0, st);
    lo = Math.min(lo, u); hi = Math.max(hi, u);
    xmin = Math.min(xmin, x - w / 2); xmax = Math.max(xmax, x + w / 2);
  }
  return { lo, hi, xmin, xmax };
}

// the model for a character: as it is; else its small letter (a hand without capitals); else its capital (a hand of
// capitals only); null when the hand has neither
export function pickLetter(st, ch) {
  if (st.letters[ch]) return ch;
  const lo = ch.toLowerCase(), up = ch.toUpperCase();
  return st.letters[lo] ? lo : st.letters[up] ? up : null;
}

// a hand with a bouncing baseline (modern calligraphy) lifts and drops its letters in a fixed pattern
const BOUNCE = [0, -1, 0.6, -0.4, 1, -0.7, 0.3];
const bounce = (st, k) => (st.bounce ? st.bounce * BOUNCE[k % BOUNCE.length] : 0);

// each model letter's extent, worked out once per set of letters
const EXTENTS = new WeakMap();
function extents(st) {
  if (!EXTENTS.has(st)) {
    const ext = {};
    for (const ch of Object.keys(st.letters)) ext[ch] = extent(st.letters[ch], st);
    EXTENTS.set(st, ext);
  }
  return EXTENTS.get(st);
}

// text -> rows of letters. Each item: ch, row, word (the index of its word in the text), start (first letter of a word),
// ox, oy (the letter's 96 x 96 frame on the sheet), lo / hi (its upright extent on the sheet) and b0 / b1 (its slot: ink
// between them, in the upright frame, is this letter's). A line break in the text starts a new row. `edge` is the free
// margin at the left and right of each row (the notebook leaves room for its margin line).
export function layout(text, st, width, { edge = EDGE } = {}) {
  const pick = ch => pickLetter(st, ch);
  const tokens = [];                         // words, and "\n" where the text breaks its line
  text.normalize("NFC").split(/\r?\n/).forEach((para, k) => {
    if (k) tokens.push("\n");
    for (const w of para.split(/\s+/)) { const word = [...w].map(pick).filter(Boolean); if (word.length) tokens.push(word); }
  });
  const ext = extents(st);
  const rows = [[]];
  let nword = -1;
  const place = (row, word, id) => {         // the row with the word added, upright positions from 0
    const out = row.map(it => ({ ...it }));
    let cur = out.length ? out[out.length - 1].hi + WORD : 0;
    word.forEach((ch, i) => {
      const e = ext[ch], ox = cur - e.lo;
      out.push({ ch, ox, lo: cur, hi: ox + e.hi, xmin: ox + e.xmin, xmax: ox + e.xmax, word: id });
      cur = ox + e.hi + (/\d/.test(ch) || /\d/.test(word[i + 1] ?? "") ? DIGIT_GAP : GAP);
    });
    out[out.length - word.length].start = true;   // first letter of a word
    return out;
  };
  const span = row => Math.max(...row.map(i => i.xmax)) - Math.min(...row.map(i => i.xmin));
  const room = width - 2 * edge;
  for (const word of tokens) {
    if (word === "\n") { if (rows[rows.length - 1].length) rows.push([]); continue; }
    const id = ++nword;
    let next = place(rows[rows.length - 1], word, id);
    if (rows[rows.length - 1].length && span(next) > room) { rows.push([]); next = place([], word, id); }
    // a word wider than the row on its own: break it
    while (span(next) > room && next.length > 1) {
      let k = next.length;
      while (k > 1 && span(next.slice(0, k)) > room) k--;
      rows[rows.length - 1] = next.slice(0, k);
      rows.push([]);
      next = place([], next.slice(k).map(i => i.ch), id);
    }
    rows[rows.length - 1] = next;
  }
  const items = [];
  rows.filter(row => row.length).forEach((row, r) => {
    const shift = edge - Math.min(...row.map(i => i.xmin));   // the row starts at the left margin
    row.forEach((it, k) => {
      const prev = row[k - 1], nxt = row[k + 1];
      items.push({
        ch: it.ch, row: r, word: it.word, start: !!it.start, ox: it.ox + shift, oy: r * PITCH + bounce(st, items.length),
        lo: it.lo + shift, hi: it.hi + shift, xmin: it.xmin + shift, xmax: it.xmax + shift,
        b0: prev ? (prev.hi + it.lo) / 2 + shift : -Infinity,
        b1: nxt ? (it.hi + nxt.lo) / 2 + shift : Infinity,
      });
    });
  });
  const nrows = Math.max(1, rows.filter(r => r.length).length);
  return { items, rows: nrows, width, height: nrows * PITCH + 8 };
}

// a long text in pages of `perPage` rows: each page is a layout of its own (rows and frames counted from its top), and
// remembers where its letters sit in the whole text (`index`)
export function paginate(lay, perPage) {
  const pages = [];
  for (let p = 0; p * perPage < lay.rows; p++) {
    const r0 = p * perPage, rows = Math.min(perPage, lay.rows - r0);
    const items = [], index = [];
    lay.items.forEach((it, k) => {
      if (it.row < r0 || it.row >= r0 + rows) return;
      items.push({ ...it, row: it.row - r0, oy: it.oy - r0 * PITCH });
      index.push(k);
    });
    pages.push({ items, index, rows, width: lay.width, height: rows * PITCH + 8 });
  }
  return pages.length ? pages : [{ items: [], index: [], rows: 1, width: lay.width, height: PITCH + 8 }];
}

// the width a row needs for the longest word of the text (so that no word has to be broken)
export function longestWord(text, st, edge = EDGE) {
  return Math.max(0, ...[...new Set(text.split(/\s+/).filter(Boolean))].map(w => {
    const its = layout(w, st, 1e6).items;
    return its.length ? Math.max(...its.map(i => i.xmax)) - Math.min(...its.map(i => i.xmin)) + 2 * edge + 1 : 0;
  }));
}

// the model of the whole text, on the sheet
export function sheetModel(lay, st) {
  return lay.items.map(it => st.letters[it.ch].map(s => s.map(([x, y, w]) => [x + it.ox, y + it.oy, w])));
}

export const rowOf = (y, rows) => Math.min(rows - 1, Math.max(0, Math.floor((y - ROW_SPLIT) / PITCH) + 1));

// ink profile of one row: for each 1 px column of the upright frame, how much pen path lies in the ascender zone,
// the x-height zone and the descender zone (the path sampled every half pixel; a dot counts as one sample)
function profile(strokes, r, rows, st) {
  const G = st.guides, top = (G["x-height"] ?? G["cap height"]) + r * PITCH, base = G.baseline + r * PITCH, pts = [];
  const add = (x, y) => { if (rowOf(y, rows) === r) pts.push([ux(x, y, r, st), y < top ? 0 : y <= base ? 1 : 2]); };
  for (const s of strokes) {
    if (s.length === 1) add(s[0][0], s[0][1]);
    for (let k = 1; k < s.length; k++) {
      const [x0, y0] = s[k - 1], [x1, y1] = s[k], n = Math.max(1, Math.ceil(Math.hypot(x1 - x0, y1 - y0) / 0.5));
      for (let j = 0; j < n; j++) add(x0 + (x1 - x0) * j / n, y0 + (y1 - y0) * j / n);
    }
  }
  if (pts.length < 4) return null;
  const u0 = Math.min(...pts.map(p => p[0])), n = Math.floor(Math.max(...pts.map(p => p[0])) - u0) + 1;
  const bins = Array.from({ length: n }, () => [0, 0, 0]);
  for (const [u, z] of pts) bins[Math.floor(u - u0)][z]++;
  return { u0, bins };
}

// copy game: where the letters of a freehand row are. The model row's ink profile is matched to yours column by column
// (dynamic time warping: each column of the model goes to a column of yours, in order, stretching where your spacing is
// wider and squeezing where it is tighter), and each slot boundary of the model goes where its column landed.
// Returns one [b0, b1] per item.
export function copySlots(strokes, lay, st) {
  const out = lay.items.map(it => [it.b0, it.b1]);
  const model = sheetModel(lay, st).flat();
  for (let r = 0; r < lay.rows; r++) {
    const idx = lay.items.map((it, k) => (it.row === r ? k : -1)).filter(k => k >= 0);
    if (idx.length < 2) continue;
    const A = profile(strokes, r, lay.rows, st), M = profile(model, r, lay.rows, st);
    if (!A) continue;
    const n = M.bins.length, m = A.bins.length, INF = 1e18;
    const d = (i, j) => Math.abs(M.bins[i][0] - A.bins[j][0]) + Math.abs(M.bins[i][1] - A.bins[j][1]) + Math.abs(M.bins[i][2] - A.bins[j][2]);
    const STEP = 4;   // stretching or squeezing a column costs as much as 4 samples of ink mismatch (0.5, 1 and 2 cut a letter short in the tests; 8 changed nothing)
    const D = new Float64Array(n * m).fill(INF), from = new Int8Array(n * m);
    for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) {
      const c = d(i, j);
      if (!i && !j) { D[0] = c; continue; }
      let best = INF, f = 0;
      if (i && j && D[(i - 1) * m + j - 1] < best) { best = D[(i - 1) * m + j - 1]; f = 0; }
      if (i && D[(i - 1) * m + j] + STEP < best) { best = D[(i - 1) * m + j] + STEP; f = 1; }
      if (j && D[i * m + j - 1] + STEP < best) { best = D[i * m + j - 1] + STEP; f = 2; }
      D[i * m + j] = best + c; from[i * m + j] = f;
    }
    // walk back: for each model column, the mean of the columns of yours it was matched to
    const sum = new Float64Array(n), cnt = new Float64Array(n);
    for (let i = n - 1, j = m - 1; ;) {
      sum[i] += j; cnt[i]++;
      if (!i && !j) break;
      const f = from[i * m + j];
      if (f === 0) { i--; j--; } else if (f === 1) i--; else j--;
    }
    const map = u => {                                 // a model upright x -> yours
      const t = Math.min(n - 1, Math.max(0, u - M.u0)), i = Math.floor(t), g = t - i;
      const at = k => sum[k] / cnt[k];
      return A.u0 + (i + 1 < n ? at(i) * (1 - g) + at(i + 1) * g : at(i)) + (t - i - g);
    };
    for (let j = 0; j < idx.length - 1; j++) out[idx[j]][1] = out[idx[j + 1]][0] = map(lay.items[idx[j]].b1);
  }
  return out;
}

// cut the strokes into one list of pieces per item, each moved into that letter's 96 x 96 frame. A stroke that crosses
// a slot boundary is cut there (the cut point goes to both sides), so joined writing is split into its letters.
export function segment(strokes, lay, st, slots = lay.items.map(it => [it.b0, it.b1])) {
  const byRow = [];
  lay.items.forEach((it, k) => (byRow[it.row] ??= []).push(k));
  const slotOf = (x, y) => {
    const r = rowOf(y, lay.rows), u = ux(x, y, r, st);
    for (const k of byRow[r] ?? []) if (u >= slots[k][0] && u < slots[k][1]) return k;
    return -1;
  };
  const pieces = lay.items.map(() => []);
  const local = (k, p) => [p[0] - lay.items[k].ox, p[1] - lay.items[k].oy, p[2]];
  for (const s of strokes) {
    if (s.length === 1) { const k = slotOf(s[0][0], s[0][1]); if (k >= 0) { const pc = [local(k, s[0])]; pc.dot = true; pieces[k].push(pc); } continue; }
    let cur = null, ck = -2;
    for (let i = 0; i < s.length; i++) {
      const p = s[i], k = slotOf(p[0], p[1]);
      if (k !== ck) {
        const q = s[i - 1];
        let cut = null;
        if (q && k >= 0 && ck >= 0 && lay.items[k].row === lay.items[ck].row) {
          // where the segment q -> p crosses the boundary between the two slots
          const r = lay.items[k].row, uq = ux(q[0], q[1], r, st), up = ux(p[0], p[1], r, st);
          const b = k > ck ? slots[ck][1] : slots[ck][0], f = up !== uq ? (b - uq) / (up - uq) : 0;
          cut = q.map((v, j) => v + Math.min(1, Math.max(0, f)) * (p[j] - v));
        }
        if (cur && cut) cur.push(local(ck, cut));
        cur = k >= 0 ? (cut ? [local(k, cut)] : []) : null;
        if (cur) pieces[k].push(cur);
        ck = k;
      }
      if (cur) cur.push(local(k, p));
    }
  }
  // a stroke that only grazes a slot (one sample) is not a piece of that letter
  return pieces.map(list => list.filter(pc => pc.length > 1 || pc.dot));
}
