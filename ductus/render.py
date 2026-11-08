"""Strokes -> the maps the network reads (96 x 96).

A letter is a list of strokes in writing order; a stroke is a list of points (x, y, w): canvas pixels (y down) and
the pen width there in pixels. The same function renders the model letter and the attempt, so both go through
exactly the same steps.

Maps (all in [0, 1] except `wid`, in pixels):
  ink   how much of the pixel the pen covered (anti-aliased)
  path  the same for a thin pen of constant width (1.2 px): where the pen went, whatever the pressure
  wid   pen width where the ink is
  t     writing time: how far along the whole letter (all strokes, in order) the pen was, 0 at the start, 1 at the end
  dn, up, lf, rt   pen direction: the share of the movement going down / up / left / right, times the ink
"""
import math

import numpy as np

H = W = 96
STEP = 0.35                        # sample spacing along a stroke, in pixels
PATH_WIDTH = 1.2                   # the thin pen of the `path` map


def stroke_length(st):
    return sum(math.dist(a[:2], b[:2]) for a, b in zip(st, st[1:]))


def render(strokes):
    M = {k: np.zeros((H, W)) for k in ("ink", "path", "wid", "t", "dn", "up", "lf", "rt")}
    total = sum(stroke_length(s) for s in strokes) or 1.0
    done = 0.0
    for st in strokes:
        if len(st) == 1:                                  # a dot: no direction
            _stamp(M, st[0][0], st[0][1], st[0][2], done / total, (0.0, 0.0))
            continue
        for (x0, y0, w0), (x1, y1, w1) in zip(st, st[1:]):
            seg = math.dist((x0, y0), (x1, y1))
            if seg == 0:
                continue
            d = ((x1 - x0) / seg, (y1 - y0) / seg)
            n = max(1, int(math.ceil(seg / STEP)))
            for k in range(n + 1):
                f = k / n
                _stamp(M, x0 + f * (x1 - x0), y0 + f * (y1 - y0), w0 + f * (w1 - w0), (done + f * seg) / total, d)
            done += seg
    return M


def _stamp(M, cx, cy, w, t, d):
    r = max(w, 0.8) / 2
    rp = PATH_WIDTH / 2
    x0, x1 = max(0, int(cx - r - 1)), min(W - 1, int(cx + r + 1))
    y0, y1 = max(0, int(cy - r - 1)), min(H - 1, int(cy + r + 1))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dist = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            M["path"][y, x] = max(M["path"][y, x], min(1.0, max(0.0, rp - dist + 0.5)))
            cov = min(1.0, max(0.0, r - dist + 0.5))
            if cov <= 0:
                continue
            if cov > M["ink"][y, x] + 1e-9:
                M["ink"][y, x] = cov
                M["wid"][y, x] = w
                M["t"][y, x] = t
            M["dn"][y, x] = max(M["dn"][y, x], cov * max(0.0, d[1]))
            M["up"][y, x] = max(M["up"][y, x], cov * max(0.0, -d[1]))
            M["rt"][y, x] = max(M["rt"][y, x], cov * max(0.0, d[0]))
            M["lf"][y, x] = max(M["lf"][y, x], cov * max(0.0, -d[0]))


TRACE_WIDEN, COPY_WIDEN = 1, 3     # extra tolerance steps after the first: a 2 px band for tracing, 4 px for copying


# Copy mode: before comparing, your letter is fitted onto the model, so the marks for shape, ductus and shading are
# about the precision of your strokes and not about where on the sheet, how big or how slanted you wrote. Slant and
# size are marked separately (the form mark, from your letter before the fit); where you wrote is not marked.
FIT_STEP = 0.5            # sample spacing along the pen path for the fit, in pixels
FIT_SCALE = (0.7, 1.45)   # the fit may resize your letter by these factors at most (beyond: not the same letter)
FIT_SHEAR = 0.6           # and straighten its slant by at most this slope (about 25 degrees at the copperplate slant)
FIT_ROUNDS = 6            # rounds of fine adjustment (each: match to the nearest path, refit size, slant and place)
FIT_KEEP = 0.8            # on the best 80% of matches each way, so a stray mark or a missing stroke does not pull it
FIT_PRIOR = 0.1           # a pull toward your own size and slant, a tenth as strong as the matched points themselves:
                          # you write on the same guidelines, so a part of a letter is not blown up to cover the whole
FIT_CORE = 0.9            # the fit reads size and slant from the 90% of the path nearest its centre
FIT_NEAR = 3.0            # the form mark reads the paths where they lie within 3 px of each other once fitted


def samples(strokes):
    """points along the pen path every FIT_STEP px (a dot is one point)"""
    out = []
    for st in strokes:
        if len(st) == 1:
            out.append((st[0][0], st[0][1]))
            continue
        for a, b in zip(st, st[1:]):
            n = max(1, math.ceil(math.dist(a[:2], b[:2]) / FIT_STEP))
            for j in range(n):
                out.append((a[0] + (b[0] - a[0]) * j / n, a[1] + (b[1] - a[1]) * j / n))
        out.append((st[-1][0], st[-1][1]))
    return out


def _moments(pts):
    """mean x, mean y, variance of y, slope of x on y (sequential sums, as in ductus.js)"""
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    vy = sum((p[1] - my) * (p[1] - my) for p in pts) / n
    cxy = sum((p[0] - mx) * (p[1] - my) for p in pts) / n
    return mx, my, vy, (cxy / vy if vy > 1e-6 else 0.0)


def _core(pts):
    """the FIT_CORE share of points nearest their centre (ties kept in order)"""
    mx, my, _, _ = _moments(pts)
    d = [(p[0] - mx) * (p[0] - mx) + (p[1] - my) * (p[1] - my) for p in pts]
    cut = sorted(d)[int(FIT_CORE * (len(pts) - 1))]
    return [p for p, v in zip(pts, d) if v <= cut]


def _nearest(ax, ay, bx, by):
    """for each point a: the index of the nearest point b and the squared distance (first of equals)"""
    DX = bx[None, :] - ax[:, None]; DY = by[None, :] - ay[:, None]
    D = DX * DX + DY * DY
    j = D.argmin(axis=1)
    return [int(v) for v in j], [float(D[i, j[i]]) for i in range(len(ax))]


def _trimmed(dist):
    cut = sorted(dist)[int(FIT_KEEP * (len(dist) - 1))]
    return [i for i in range(len(dist)) if dist[i] <= cut]


def _refine(P, Q, A, B, e, f):
    """rounds of: match your points to the nearest model points and the model's to the nearest of yours, keep the best
    FIT_KEEP of each, and solve for the size, slant and place (x' = A x + B y + e, y' = A y + f) that bring all kept
    pairs nearest (least squares). Matching both ways keeps the fit from shrinking your letter onto part of the model;
    trimming both ways lets a stray mark (yours) and a stroke you left out (the model's) go unmatched."""
    px = np.array([p[0] for p in P]); py = np.array([p[1] for p in P])
    cost = 0.0
    for _ in range(FIT_ROUNDS + 1):
        qx = np.array([A * x + B * y + e for x, y in Q]); qy = np.array([A * y + f for x, y in Q])
        jq, dq = _nearest(qx, qy, px, py)
        jp, dp = _nearest(px, py, qx, qy)
        # the two starts are compared on all points (a fit that matches only part of the letter is not the closer)
        cost = sum(dq) / len(dq) + sum(dp) / len(dp)
        if _ == FIT_ROUNDS:
            break
        kq, kp = _trimmed(dq), _trimmed(dp)
        pairs = [(Q[i], P[jq[i]]) for i in kq] + [(Q[jp[i]], P[i]) for i in kp]
        n = len(pairs)
        x0 = sum(q[0] for q, _ in pairs) / n; y0 = sum(q[1] for q, _ in pairs) / n
        X0 = sum(p[0] for _, p in pairs) / n; Y0 = sum(p[1] for _, p in pairs) / n
        sxx = syy = sxy = sXx = sYy = sXy = 0.0
        for q, p in pairs:
            x, y, X, Y = q[0] - x0, q[1] - y0, p[0] - X0, p[1] - Y0
            sxx += x * x; syy += y * y; sxy += x * y; sXx += X * x; sYy += Y * y; sXy += X * y
        w = FIT_PRIOR * (sxx + syy)     # the pull toward A = 1, B = 0
        det = (sxx + syy + w) * (syy + w) - sxy * sxy
        A = ((sXx + sYy + w) * (syy + w) - sxy * sXy) / det
        B = ((sxx + syy + w) * sXy - sxy * (sXx + sYy + w)) / det
        A = min(FIT_SCALE[1], max(FIT_SCALE[0], A))
        B = min(FIT_SHEAR * A, max(-FIT_SHEAR * A, B))
        e, f = X0 - A * x0 - B * y0, Y0 - A * y0
    return cost, (A, 0.0, B, A, e, f)


def fit(model, attempt):
    """the affine map (a, b, c, d, e, f): x' = a x + c y + e, y' = b x + d y + f, that puts the attempt onto the model.
    Two starts, refined (see _refine), and the closer one kept: centre on centre with your own size and slant, and
    centre on centre with the model's height spread and slant (from the core of each path)."""
    P, Q = samples(model), samples(attempt)
    if not P or not Q:
        return (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
    mxm, mym, vym, km = _moments(_core(P))
    mxa, mya, vya, ka = _moments(_core(Q))
    s = min(FIT_SCALE[1], max(FIT_SCALE[0], math.sqrt(vym / vya))) if vya > 1e-6 and vym > 1e-6 else 1.0
    dk = min(FIT_SHEAR, max(-FIT_SHEAR, ka - km))
    starts = [(1.0, 0.0, mxm - mxa, mym - mya),                                        # as written, centred
              (s, -s * dk, mxm - s * mxa + s * dk * mya, mym - s * mya)]               # the model's size and slant
    best = None
    for A, B, e, f in starts:
        c, T = _refine(P, Q, A, B, e, f)
        if best is None or c < best[0]:
            best = (c, T)
    return best[1]


def apply(T, strokes):
    a, b, c, d, e, f = T
    return [[(a * x + c * y + e, b * x + d * y + f, *rest) for x, y, *rest in st] for st in strokes]


def centred(model, attempt):
    """the attempt only moved, centre on the model's centre: for the form mark (slant and size), which does not
    depend on position but must see the attempt's own slant and size"""
    P, Q = samples(model), samples(attempt)
    if not P or not Q:
        return attempt
    mxm, mym, _, _ = _moments(P)
    mxa, mya, _, _ = _moments(Q)
    return apply((1.0, 0.0, 0.0, 1.0, mxm - mxa, mym - mya), attempt)


def keep_near(strokes, T, ref):
    """the strokes resampled every FIT_STEP px, keeping only the path that lies within FIT_NEAR px of the points `ref`
    once mapped by T (cut where it leaves), in the strokes' own coordinates"""
    rx = np.array([p[0] for p in ref]); ry = np.array([p[1] for p in ref])
    a, b, c, d, e, f = T
    out = []
    for st in strokes:
        if len(st) == 1:
            pts = [tuple(st[0][:3])]
        else:
            pts = []
            for u, v in zip(st, st[1:]):
                n = max(1, math.ceil(math.dist(u[:2], v[:2]) / FIT_STEP))
                for j in range(n):
                    pts.append(tuple(u[i] + (v[i] - u[i]) * j / n for i in range(3)))
            pts.append(tuple(st[-1][:3]))
        qx = np.array([a * x + c * y + e for x, y, _ in pts]); qy = np.array([b * x + d * y + f for x, y, _ in pts])
        DX = rx[None, :] - qx[:, None]; DY = ry[None, :] - qy[:, None]
        near = (DX * DX + DY * DY).min(axis=1) <= FIT_NEAR * FIT_NEAR
        cur = []
        for p, ok in zip(pts, near):
            if ok:
                cur.append(p)
            else:
                if len(cur) > 1 or (cur and len(st) == 1):
                    out.append(cur)
                cur = []
        if len(cur) > 1 or (cur and len(st) == 1):
            out.append(cur)
    return out


def form_pair(model, attempt, T):
    """what the form mark compares: your path where it lies on the fitted model (a stray mark is left out), centred on
    the model; and the model's path where your fitted path covers it (a stroke you left out is left out of both). Slant
    and size errors are undone by the fit, so they keep all their ink and are measured in full."""
    if not samples(attempt):
        return attempt, model
    a = keep_near(attempt, T, samples(model))
    m = keep_near(model, (1.0, 0.0, 0.0, 1.0, 0.0, 0.0), samples(apply(T, attempt)))
    return centred(model, a), m


def align(model, attempt):
    """Copy mode: the attempt fitted onto the model (see fit)"""
    return apply(fit(model, attempt), attempt)


def inputs(model, attempt, has_pressure=True, copy=False):
    """The network's inputs: the model letter's maps (m_*), the attempt's (a_*), the attempt's own path for the form
    and the model's that the form mark compares (a_form, m_form: see form_pair), and the mode scalars."""
    if copy:
        T = fit(model, attempt)
        (form, mform), attempt = form_pair(model, attempt, T), apply(T, attempt)
    out = {"widen": float(COPY_WIDEN if copy else TRACE_WIDEN), "copy": 1.0 if copy else 0.0}
    for prefix, strokes in (("m_", model), ("a_", attempt)):
        for k, v in render(strokes).items():
            out[prefix + k] = v
    out["a_form"] = render(form)["path"] if copy else out["a_path"]
    out["m_form"] = render(mform)["path"] if copy else out["m_path"]
    out["has_pressure"] = 1.0 if has_pressure else 0.0
    return out
