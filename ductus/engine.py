"""WP-Ductus engine: build parameters from the edit list, run the forward pass.

Same design as WP-CharNet's engine: every parameter starts at zero and only the edit list writes into it.
Differences: several named input maps (the model letter's and the attempt's), a 96 x 96 grid, and a `ratio` op.

Edit kinds (one per line, `#` starts a comment):
  TAP   <layer> <out> <in> <dy> <dx> <value>      conv kernel tap (dy, dx relative to the centre)
  BIAS  <layer> <out> <value>                     bias of an output map / scalar
  ZONE  <layer> <feat> <in> <rows> <cols> <scale> pooling mask over one input map (rows/cols "a:b"); the scale is a
                                                  number, or `x`, `y`, `xy`, `yy` (products of the pixel's column and
                                                  row centres), or `|y-c|` (its distance from row c): weighted sums for
                                                  centres, spreads and slopes
  LINK  <layer> <out> <in> <value>                one weight of a linear layer

Ops:
  conv     k x k convolution, zero padding, activation relu / clip01 / none
  max3     max over the 3 x 3 neighbourhood (widens a stroke by 1 px per step)
  loop     repeat a block of layers n times (`n`), or as many times as an input scalar says (`n_from`)
  zone     weighted sum of maps over a region -> scalar
  linear   scalars -> scalars
  ratio    out = (sum of numerators) / (sum of denominators); a part may name its value when the denominator is empty:
           a fixed op, no weights
  moments  from the sums n, Σx, Σy, Σxy, Σyy of a map: mean y, variance of y, and the slope of x on y (how far x moves
           per pixel down): a fixed op, no weights
"""
import json

import numpy as np

H = W = 96

ACT = {
    "relu": lambda v: np.maximum(v, 0),
    "clip01": lambda v: np.clip(v, 0, 1),
    "none": lambda v: v,
}


def band(spec, n):
    a, b = (float(v) for v in spec.split(":"))
    c = np.arange(n) + 0.5
    return ((c >= a) & (c < b)).astype(float)


class Net:
    def __init__(self, arch):
        self.arch = arch
        self.L, self.P = {}, {}
        for L in self._all(arch["layers"]):
            self.L[L["id"]] = L
            op = L["op"]
            if op == "conv":
                self.P[L["id"]] = {"W": np.zeros((len(L["out"]), len(L["in"]), L["k"], L["k"])), "b": np.zeros(len(L["out"]))}
            elif op == "zone":
                self.P[L["id"]] = {"W": np.zeros((len(L["out"]), len(L["in"]), H, W)), "b": np.zeros(len(L["out"]))}
            elif op == "linear":
                self.P[L["id"]] = {"W": np.zeros((len(L["out"]), len(L["in"]))), "b": np.zeros(len(L["out"]))}

    @staticmethod
    def _all(layers):
        for L in layers:
            if L["op"] == "loop":
                yield from Net._all(L["body"])
            else:
                yield L

    def apply_edits(self, text):
        self.why = {}
        for n, raw in enumerate(text.splitlines(), 1):
            line = raw.split("#")[0].strip()
            if not line:
                continue
            t = line.split()
            kind, lid = t[0], t[1]
            L, P = self.L[lid], self.P[lid]
            try:
                if kind == "TAP":
                    o, i = L["out"].index(t[2]), L["in"].index(t[3])
                    c = L["k"] // 2
                    P["W"][o, i, c + int(t[4]), c + int(t[5])] = float(t[6])
                elif kind == "BIAS":
                    P["b"][L["out"].index(t[2])] = float(t[3])
                    if "#" in raw:
                        self.why[f"{lid} {t[2]}"] = raw.split("#", 1)[1].strip()
                elif kind == "ZONE":
                    o, i = L["out"].index(t[2]), L["in"].index(t[3])
                    rows, cols = band(t[4], H), band(t[5], W)
                    s = t[6]
                    cx, cy = np.arange(W) + 0.5, np.arange(H) + 0.5
                    if s == "x":
                        cols = cols * cx
                    elif s == "y":
                        rows = rows * cy
                    elif s == "xy":
                        rows, cols = rows * cy, cols * cx
                    elif s == "yy":
                        rows = rows * cy * cy
                    elif s.startswith("|y-") and s.endswith("|"):
                        rows = rows * np.abs(np.arange(H) + 0.5 - float(s[3:-1]))
                    else:
                        rows = rows * float(s)
                    P["W"][o, i] += np.outer(rows, cols)
                elif kind == "LINK":
                    P["W"][L["out"].index(t[2]), L["in"].index(t[3])] = float(t[4])
                else:
                    raise ValueError(f"unknown edit kind {kind}")
            except (ValueError, IndexError) as e:
                raise ValueError(f"edit line {n}: {raw!r}: {e}") from None
        return self

    # ---- forward ------------------------------------------------------------------------------
    def forward(self, inputs):
        """inputs: dict of named 96 x 96 maps and scalars. Returns the trace of every named value."""
        T = {k: (np.asarray(v, dtype=float) if np.ndim(v) else float(v)) for k, v in inputs.items()}
        self._run(self.arch["layers"], T)
        return T

    def _run(self, layers, T):
        for L in layers:
            getattr(self, "_" + L["op"])(L, T)

    def _loop(self, L, T):
        n = int(round(T[L["n_from"]])) if "n_from" in L else L["n"]
        for _ in range(n):
            self._run(L["body"], T)

    def _conv(self, L, T):
        P, k = self.P[L["id"]], L["k"]
        c = k // 2
        X = np.stack([np.pad(T[n], c) for n in L["in"]])
        out = np.zeros((len(L["out"]), H, W)) + P["b"][:, None, None]
        for o, i, dy, dx in zip(*np.nonzero(P["W"])):
            out[o] += P["W"][o, i, dy, dx] * X[i, dy:dy + H, dx:dx + W]
        out = ACT[L["act"]](out)
        for o, n in enumerate(L["out"]):
            T[n] = out[o]

    def _max3(self, L, T):
        for src, dst in zip(L["in"], L["out"]):
            p = np.pad(T[src], 1)
            T[dst] = np.maximum.reduce([p[dy:dy + H, dx:dx + W] for dy in range(3) for dx in range(3)])

    def _zone(self, L, T):
        P = self.P[L["id"]]
        X = np.stack([T[n] for n in L["in"]])
        v = np.einsum("fihw,ihw->f", P["W"], X) + P["b"]
        for o, n in enumerate(L["out"]):
            T[n] = float(ACT[L["act"]](v[o]))

    def _linear(self, L, T):
        P = self.P[L["id"]]
        v = ACT[L["act"]](P["W"] @ np.array([T[n] for n in L["in"]], dtype=float) + P["b"])
        for o, n in enumerate(L["out"]):
            T[n] = float(v[o])

    def _ratio(self, L, T):
        # a part may name its own value for an empty denominator: (num, den, empty)
        for out, (num, den, *rest) in L["parts"].items():
            d = sum(T[n] for n in den)
            empty = rest[0] if rest else L.get("empty", 0.0)
            T[out] = float(sum(T[n] for n in num) / d) if d > L.get("eps", 1e-6) else float(empty)


    def _moments(self, L, T):
        for p, (n, sx, sy, sxy, syy) in L["parts"].items():
            n, sx, sy, sxy, syy = (T[k] for k in (n, sx, sy, sxy, syy))
            if n <= 1e-6:
                T[p + "_my"] = T[p + "_vy"] = T[p + "_slope"] = 0.0
                continue
            my, vy = sy / n, syy / n - (sy / n) ** 2
            T[p + "_my"], T[p + "_vy"] = float(my), float(vy)
            T[p + "_slope"] = float((sxy / n - (sx / n) * my) / vy) if vy > 1e-6 else 0.0


def load(arch_path, edits_path):
    with open(arch_path) as f:
        arch = json.load(f)
    with open(edits_path) as f:
        return Net(arch).apply_edits(f.read())
