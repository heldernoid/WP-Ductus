"""Gothicized Italic (italic's structure written with blackletter's angles and weight): small letters, capitals and
figures, authored for this hand from a Gothicized Italic exemplar sheet (with its stroke numbers and
arrows).

Measured on the exemplar sheet (x-height 76 px; the hand's numbers are these, rounded):

  quantity                              exemplar                 hand
  x-height                              76 px (guide lines)      1 (S = 42 px)
  ascender (b d h k l)                  104 px = 1.37 xh         1.37
  descender (g p q y)                   26-33 px = 0.35-0.43 xh  0.42
  capital height                        107-110 px = 1.42 xh     1.42 (decorations to 1.5)
  nib (widest stroke)                   13-13.5 px               x-height 5.7 nib widths (nib 7.4 px)
  stems (vertical, horizontal run)      10 px = nib x cos 40      nib angle 35 (between the stems' 40 and ...
  horizontals (f, t bars)               5-7 px = nib x sin 30     ... the bars' 30)
  slant (stems of h k l)                0-1 deg                  0 deg
  n: stem to stem                       28 px = 0.37 xh          0.38 (ink 0.72 wide with head and foot)
  m: stem to stem                       26 px = 0.34 xh          0.35
  a: bowl to stem at mid height         29 px = 0.38 xh          0.38
  o (lens)                              0.43 xh between sides    0.48
  capitals, upright width               A 1.37, B 1.2, M 1.4, W 1.58, O 1.1, I 0.5 xh
"""
from gen.pen import arc, bez, chain, dot, line, poly  # noqa: F401


# ---- Gothicized Italic small letters ------------------------------------------------------------------------------------
# Upright and heavy; stems with a head bent to the left; ascenders with a forked head (a spur on the left below the
# point); arches that leave the stem high up (0.8) as a straight hairline to a sharp peak at the top right, then fall
# straight; a, d, g, q, u, c, e, o built on a lens-shaped left side that comes to a point at the foot; a two-part a and g
# (the left side, a hairline up into the stem, a separate top, the stem); pointed feet turning out as a hairline.
W = 0.38                                         # stem to stem in n, a
ASC, DESC = 1.37, -0.42


def head(u, top=1.0):                            # a stem's head: a short stroke up into the top, bent to the left
    return line((u - 0.1, top - 0.1), (u, top))


def fork(u, top=ASC):                            # an ascender's forked head: a spur on the left, then up to the point
    return poly((u - 0.13, top - 0.16), (u - 0.03, top - 0.1), (u + 0.01, top))


def foot(u, v=0.12):                             # the pointed foot: down to the baseline, out as a hairline
    return poly((u, v), (u + 0.08, 0.0), (u + 0.2, 0.09))


def arch(u0, u1, ft=True, end=0.0, spring=0.8):  # the pointed arch: a straight hairline from the stem to the peak
    a = chain(line((u0, spring), (u1 - 0.06, 1.02)), line((u1 - 0.06, 1.02), (u1, 0.92)))
    if ft:
        return chain(a, line((u1, 0.92), (u1, 0.12)), foot(u1))
    return chain(a, line((u1, 0.92), (u1, end)))


def left(ut=0.24, ub=0.14):                      # the lens's left side: from the top point, out to the left, to the foot
    return chain(bez((ut, 1.0), (0.06, 0.88), (-0.04, 0.6), (0.0, 0.38)), bez((0.0, 0.38), (0.02, 0.2), (0.08, 0.08), (ub, 0.0)))


def hair_up(ub=0.14, u=W):                       # a, g, q, u: the hairline from the foot up into the stem
    return line((ub, 0.0), (u, 0.4))


def top(u=W):                                    # a, g, q: the top, from the left side's head to the stem's head
    return bez((0.24, 1.0), (0.3, 1.04), (u - 0.08, 1.05), (u, 1.02))


def _small():
    L = {}
    L["a"] = [left(), hair_up(), top(), chain(line((W, 1.02), (W, 0.12)), foot(W))]
    L["b"] = [chain(fork(0), line((0.01, ASC), (0.0, 0.12)), line((0.0, 0.12), (0.1, 0.0))),
              chain(line((0.0, 0.8), (W - 0.04, 1.02)), line((W - 0.04, 1.02), (W + 0.02, 0.9)),
                    bez((W + 0.02, 0.9), (W + 0.06, 0.6), (W + 0.02, 0.3), (0.14, 0.0)))]
    L["c"] = [chain(left(0.26, 0.16), line((0.16, 0.0), (0.44, 0.14))), poly((0.26, 1.0), (0.4, 1.03), (0.46, 0.86))]
    L["d"] = [left(0.24, 0.16),
              chain(bez((0.0, ASC), (0.3, 1.26), (0.5, 1.0), (0.5, 0.62)), bez((0.5, 0.62), (0.5, 0.3), (0.34, 0.08), (0.18, 0.0)))]
    L["e"] = [chain(left(0.26, 0.16), line((0.16, 0.0), (0.44, 0.14))),
              chain(poly((0.26, 1.0), (0.4, 1.02), (0.45, 0.84)), line((0.45, 0.84), (-0.12, 0.46)))]
    L["f"] = [chain(line((0.12, 1.12), (0.12, DESC + 0.02))), poly((0.12, 1.12), (0.34, ASC), (0.46, 1.1)), line((-0.1, 0.78), (0.42, 0.82))]
    L["g"] = [left(), hair_up(), top(), chain(line((W, 1.02), (W, -0.26)), bez((W, -0.26), (W, -0.36), (0.34, DESC), (0.24, DESC))),
              chain(line((-0.08, -0.06), (-0.02, -0.32)), line((-0.02, -0.32), (0.24, DESC)))]
    L["h"] = [chain(fork(0), line((0.01, ASC), (0.0, 0.0))), arch(0, W + 0.06)]
    L["i"] = [chain(head(0), line((0, 1.0), (0, 0.12)), foot(0)), line((0.12, 1.32), (0.04, 1.18))]
    L["j"] = [chain(head(0), line((0, 1.0), (0, -0.24)), bez((0, -0.24), (0, -0.34), (-0.04, -0.4), (-0.1, DESC))), line((0.12, 1.32), (0.04, 1.18))]
    L["k"] = [chain(fork(0), line((0.01, ASC), (0.0, 0.0))),
              chain(line((0.0, 0.8), (0.28, 1.02)), line((0.28, 1.02), (0.38, 0.84)), line((0.38, 0.84), (0.06, 0.6))),
              chain(line((0.12, 0.6), (0.36, 0.12)), foot(0.36))]
    L["l"] = [chain(fork(0), line((0.01, ASC), (0.0, 0.12)), foot(0))]
    L["m"] = [chain(head(0), line((0, 1.0), (0, 0.0))), arch(0, 0.35, ft=False), arch(0.35, 0.7)]
    L["n"] = [chain(head(0), line((0, 1.0), (0, 0.0))), arch(0, W)]
    L["o"] = [bez((0.36, 1.02), (0.0, 0.88), (-0.06, 0.24), (0.16, 0.0)), bez((0.36, 1.02), (0.58, 0.8), (0.56, 0.2), (0.16, 0.0))]
    L["p"] = [chain(head(0), line((0, 1.0), (0, DESC))),
              chain(line((0.0, 0.8), (W - 0.04, 1.02)), line((W - 0.04, 1.02), (W + 0.02, 0.9)),
                    bez((W + 0.02, 0.9), (W + 0.06, 0.6), (W + 0.04, 0.3), (0.3, 0.02))),
              line((-0.14, -0.02), (0.3, 0.02))]
    L["q"] = [left(), hair_up(), top(), line((W, 1.02), (W, DESC))]
    L["r"] = [chain(head(0), line((0, 1.0), (0, 0.12)), foot(0)), poly((0.0, 0.8), (0.28, 1.02), (0.38, 0.84))]
    L["s"] = [chain(bez((0.06, 0.94), (0.0, 0.72), (0.4, 0.5), (0.42, 0.26)), bez((0.42, 0.26), (0.43, 0.12), (0.36, 0.04), (0.24, 0.0))),
              chain(line((-0.06, 0.22), (0.02, 0.04)), line((0.02, 0.04), (0.24, 0.0))),
              poly((0.06, 0.94), (0.34, 1.03), (0.42, 0.88))]
    L["t"] = [chain(line((0.04, 1.3), (0.04, 0.12)), foot(0.04)), line((-0.12, 0.88), (0.44, 0.94))]
    L["u"] = [chain(head(0), line((0, 1.0), (0, 0.3)), bez((0, 0.3), (0.01, 0.14), (0.06, 0.04), (0.12, 0.0))), hair_up(0.12),
              chain(head(W), line((W, 1.0), (W, 0.12)), foot(W))]
    L["v"] = [chain(head(0, 0.88), bez((0, 0.88), (0.02, 0.5), (0.18, 0.2), (0.32, 0.0))),
              chain(line((0.16, 0.86), (0.44, 1.03)), bez((0.44, 1.03), (0.56, 0.86), (0.56, 0.4), (0.34, 0.02)))]
    L["w"] = [chain(head(0, 0.88), bez((0, 0.88), (0.02, 0.5), (0.14, 0.18), (0.28, -0.04))),
              line((0.28, -0.04), (0.42, 0.42)),
              chain(line((0.32, 0.88), (0.46, 1.02)), bez((0.46, 1.02), (0.44, 0.6), (0.48, 0.24), (0.6, -0.02))),
              chain(line((0.54, 0.86), (0.8, 1.03)), bez((0.8, 1.03), (0.92, 0.86), (0.9, 0.4), (0.62, 0.0)))]
    L["x"] = [chain(head(0, 0.88), bez((0, 0.88), (0.24, 0.8), (0.34, 0.62), (0.28, 0.46)), bez((0.28, 0.46), (0.2, 0.2), (0.06, -0.1), (-0.06, -0.26))),
              bez((0.28, 0.46), (0.34, 0.3), (0.42, 0.12), (0.52, 0.0)),
              chain(line((0.48, 1.02), (0.52, 0.86)), line((0.52, 0.86), (0.32, 0.6))),
              line((-0.04, 0.48), (0.56, 0.52))]
    L["y"] = [chain(head(0, 0.88), bez((0, 0.88), (0.02, 0.5), (0.18, 0.2), (0.32, 0.0))),
              chain(line((0.16, 0.86), (0.44, 1.03)), bez((0.44, 1.03), (0.56, 0.86), (0.56, 0.3), (0.42, 0.0)),
                    bez((0.42, 0.0), (0.34, -0.14), (0.38, -0.3), (0.34, DESC)))]
    L["z"] = [poly((0.02, 0.9), (0.14, 1.0), (0.52, 1.02)), line((0.52, 1.02), (0.0, 0.03)), poly((0.0, 0.03), (0.38, 0.0), (0.56, 0.1)),
              line((0.04, 0.5), (0.54, 0.54))]
    return L


# ---- Gothicized Italic capitals -----------------------------------------------------------------------------------------
# Blackletter capitals in the exemplar's forms: round (uncial-like) C, D, E, G, M, O, Q, T and straight A, H, I, K, L, N;
# begun with a hairline curl at the top left, heavy curved sides, hairline decorations (a hairline crossing the round
# letters' left side, crossbars through M, W, X, a hairline beside the stems of H, I, K, L), and sweeping feet.
C = 1.42


def ccurl(u=0.12, v=1.2):                        # the hairline curl at the top left, written down
    return bez((u, v), (u - 0.1, v - 0.04), (u - 0.12, v - 0.16), (u - 0.06, v - 0.26))


def _capitals():
    L = {}
    L["A"] = [line((0.82, C), (0.24, 0.08)),
              poly((0.0, 0.02), (0.3, 0.04), (0.44, 0.16)),
              chain(line((0.82, C), (1.1, 0.12)), foot(1.1)),
              line((0.12, 0.54), (1.2, 0.62)),
              bez((0.14, 1.2), (0.3, 1.38), (0.6, 1.42), (0.82, C)), ccurl(0.14, 1.2)]
    L["B"] = [bez((0.36, 1.22), (0.26, 0.9), (0.26, 0.4), (0.3, 0.12)),
              ccurl(0.18, 1.24),
              line((-0.04, 0.0), (0.86, 0.02)),
              chain(line((0.2, 1.24), (0.72, 1.46)), line((0.72, 1.46), (0.8, 1.14)), line((0.8, 1.14), (0.62, 0.94))),
              chain(bez((0.62, 0.94), (1.0, 0.78), (1.04, 0.4), (0.96, 0.2)), line((0.96, 0.2), (0.86, 0.02)))]
    L["C"] = [chain(bez((0.5, 1.3), (0.12, 1.12), (0.0, 0.7), (0.06, 0.4)), bez((0.06, 0.4), (0.12, 0.12), (0.3, 0.0), (0.5, 0.0)),
                    line((0.5, 0.0), (0.82, 0.26))),
              line((0.3, 1.0), (-0.16, 0.34)),
              poly((0.5, 1.3), (0.66, C), (0.86, 1.2))]
    L["D"] = [bez((0.34, 1.16), (0.16, 0.9), (0.14, 0.4), (0.22, 0.06)),
              ccurl(0.22, 1.2),
              line((-0.02, 0.0), (0.82, 0.04)),
              chain(line((0.34, 1.16), (0.64, C)), bez((0.64, C), (1.04, 1.1), (1.06, 0.5), (0.82, 0.04)))]
    L["E"] = [chain(bez((0.5, 1.26), (0.1, 1.06), (0.0, 0.6), (0.08, 0.34)), bez((0.08, 0.34), (0.16, 0.08), (0.36, 0.0), (0.58, 0.0)),
                    line((0.58, 0.0), (0.84, 0.24))),
              bez((0.42, 1.14), (0.26, 0.9), (0.1, 0.6), (-0.14, 0.4)),
              poly((0.5, 1.26), (0.64, C), (0.86, 1.38), (0.84, 1.18)),
              line((0.36, 0.84), (0.82, 0.88))]
    L["F"] = [chain(fork(0.0, 1.24), line((0.01, 1.24), (0.0, -0.36))),
              chain(bez((0.01, 1.24), (0.1, 1.38), (0.3, 1.42), (0.56, 1.36)), line((0.56, 1.36), (0.62, 1.2))),
              line((-0.34, 0.78), (0.46, 0.84))]
    L["G"] = [chain(bez((0.5, 1.3), (0.12, 1.12), (0.0, 0.7), (0.06, 0.4)), bez((0.06, 0.4), (0.12, 0.12), (0.3, 0.0), (0.56, 0.0))),
              line((0.3, 1.0), (-0.16, 0.34)),
              poly((0.5, 1.3), (0.66, C), (0.86, 1.22)),
              chain(bez((0.4, 0.84), (0.7, 0.96), (0.96, 0.78), (0.94, 0.46)), line((0.94, 0.46), (0.76, 0.06)), line((0.76, 0.06), (0.56, 0.0)))]
    L["H"] = [chain(fork(0.0, 1.36), line((0.01, 1.36), (0.0, 0.08))),
              poly((-0.18, 0.0), (0.06, 0.0), (0.18, 0.06)),
              chain(line((0.04, 1.02), (0.38, 1.3)), bez((0.38, 1.3), (0.62, 1.12), (0.66, 0.6), (0.6, 0.2)),
                    bez((0.6, 0.2), (0.56, 0.0), (0.48, -0.14), (0.44, -0.26))),
              line((0.17, 1.3), (0.17, 0.08))]
    L["I"] = [line((0.0, 1.26), (0.0, 0.1)),
              poly((-0.26, 0.0), (0.06, 0.0), (0.2, 0.06)),
              poly((-0.3, 1.28), (-0.12, C), (0.18, 1.4)),
              line((-0.14, 0.76), (0.0, 0.66)),
              line((0.18, 1.32), (0.18, 0.08))]
    L["J"] = [bez((0.0, 1.18), (0.04, 1.4), (0.3, C), (0.56, 1.38)),
              chain(line((0.56, 1.38), (0.5, 0.1)), bez((0.5, 0.1), (0.46, -0.2), (0.3, -0.32), (0.04, -0.28))),
              ccurl(0.0, 1.18),
              line((0.32, 0.64), (0.5, 0.56))]
    L["K"] = [chain(fork(0.0, 1.36), line((0.01, 1.36), (0.0, 0.08))),
              poly((-0.14, 0.0), (0.1, 0.0), (0.24, 0.06)),
              chain(line((0.24, 1.2), (0.5, C)), bez((0.5, C), (0.7, 1.24), (0.64, 0.96), (0.44, 0.8)), line((0.44, 0.8), (0.2, 0.72))),
              chain(line((0.34, 0.74), (0.8, 0.12)), foot(0.8)),
              line((0.18, 1.12), (0.18, 0.1))]
    L["L"] = [bez((0.2, 1.22), (0.12, 0.9), (0.16, 0.4), (0.08, 0.06)),
              poly((-0.08, 0.0), (0.4, 0.02), (0.76, 0.1)),
              chain(line((0.2, 1.22), (0.44, C)), line((0.44, C), (0.62, 1.22))),
              line((0.0, 0.68), (0.14, 0.58)),
              line((0.36, 1.2), (0.36, 0.12))]
    L["M"] = [bez((0.34, 1.24), (-0.02, 1.0), (-0.06, 0.4), (0.18, 0.02)),
              line((0.54, 1.12), (0.54, 0.08)),
              poly((0.38, 0.0), (0.6, 0.0), (0.72, 0.06)),
              chain(line((0.34, 1.24), (0.48, C)), line((0.48, C), (0.54, 1.12))),
              chain(line((0.54, 1.12), (0.92, C)), bez((0.92, C), (1.2, 1.1), (1.16, 0.4), (1.0, 0.0)),
                    bez((1.0, 0.0), (0.96, -0.1), (0.92, -0.18), (0.9, -0.26))),
              line((0.36, 0.62), (0.86, 0.66))]
    L["N"] = [chain(fork(0.0, 1.32), line((0.01, 1.32), (0.0, 0.02))),
              line((0.04, 1.1), (0.92, 0.26)),
              line((0.96, 1.4), (0.92, 0.02)),
              line((0.48, 0.86), (0.48, 0.6))]
    L["O"] = [chain(bez((0.52, 1.3), (0.1, 1.12), (0.0, 0.6), (0.1, 0.3)), bez((0.1, 0.3), (0.2, 0.06), (0.4, 0.0), (0.62, 0.0))),
              line((0.34, 1.04), (-0.16, 0.34)),
              chain(line((0.52, 1.3), (0.72, C)), bez((0.72, C), (1.14, 1.1), (1.14, 0.3), (0.62, 0.0)))]
    L["P"] = [chain(line((0.2, 1.26), (0.2, -0.38))),
              chain(line((0.2, 1.26), (0.5, C)), bez((0.5, C), (0.9, 1.2), (0.92, 0.6), (0.6, 0.08))),
              line((-0.26, 0.02), (0.6, 0.08)),
              bez((0.1, 1.26), (-0.04, 1.12), (-0.06, 0.9), (0.02, 0.72))]
    L["Q"] = [chain(bez((0.52, 1.3), (0.1, 1.12), (0.0, 0.6), (0.1, 0.3)), bez((0.1, 0.3), (0.2, 0.06), (0.4, 0.0), (0.62, 0.0))),
              line((0.34, 1.04), (-0.16, 0.34)),
              chain(line((0.52, 1.3), (0.72, C)), bez((0.72, C), (1.14, 1.1), (1.14, 0.3), (0.62, 0.0))),
              line((0.4, 0.0), (0.12, -0.2)),
              bez((0.12, -0.2), (0.4, -0.24), (0.7, -0.32), (1.04, -0.14))]
    L["R"] = [chain(bez((0.4, 1.3), (0.32, 0.9), (0.4, 0.4), (0.16, 0.06))),
              poly((-0.02, 0.0), (0.18, 0.02), (0.44, 0.1)),
              ccurl(0.26, 1.18),
              chain(line((0.4, 1.3), (0.74, C)), bez((0.74, C), (1.0, 1.24), (0.9, 0.9), (0.62, 0.76)), line((0.62, 0.76), (0.42, 0.72))),
              chain(line((0.56, 0.74), (1.02, 0.12)), foot(1.02))]
    L["S"] = [bez((0.5, 1.32), (0.08, 1.26), (-0.02, 0.92), (0.3, 0.72)),
              bez((0.3, 0.72), (0.72, 0.54), (0.8, 0.2), (0.52, 0.0)),
              bez((-0.02, 0.14), (0.08, 0.02), (0.3, -0.02), (0.52, 0.0)),
              poly((0.5, 1.32), (0.7, C), (0.76, 1.3))]
    L["T"] = [chain(bez((0.56, 1.28), (0.16, 1.12), (0.02, 0.7), (0.1, 0.36)), bez((0.1, 0.36), (0.18, 0.08), (0.4, 0.0), (0.66, 0.0)),
                    line((0.66, 0.0), (0.96, 0.22))),
              line((0.7, 1.36), (0.68, 0.44)),
              bez((0.0, 1.16), (0.16, 1.4), (0.8, 1.34), (1.24, 1.52)),
              ccurl(0.0, 1.16)]
    L["U"] = [chain(line((-0.14, 1.24), (0.02, 1.38)), line((0.02, 1.38), (0.02, 0.3)), bez((0.02, 0.3), (0.04, 0.12), (0.2, 0.02), (0.34, 0.0))),
              line((0.34, 0.0), (0.68, 0.44)),
              chain(line((0.62, 1.32), (0.72, 1.4)), line((0.72, 1.4), (0.72, 0.12)), foot(0.72))]
    L["V"] = [chain(line((-0.04, 1.24), (0.08, 1.34)), bez((0.08, 1.34), (0.08, 0.8), (0.24, 0.3), (0.44, 0.0))),
              chain(line((0.3, 1.24), (0.6, C)), bez((0.6, C), (0.8, 1.2), (0.8, 0.5), (0.46, 0.02)))]
    L["W"] = [chain(line((-0.04, 1.24), (0.08, 1.34)), bez((0.08, 1.34), (0.06, 0.8), (0.18, 0.3), (0.38, 0.0))),
              line((0.38, 0.0), (0.6, 0.5)),
              chain(line((0.46, 1.3), (0.62, C)), bez((0.62, C), (0.6, 0.8), (0.64, 0.3), (0.82, 0.0))),
              chain(line((0.76, 1.3), (1.0, C)), bez((1.0, C), (1.2, 1.2), (1.18, 0.5), (0.84, 0.02))),
              line((0.3, 0.86), (1.08, 0.9))]
    L["X"] = [chain(line((-0.04, 1.26), (0.08, 1.36)), bez((0.08, 1.36), (0.44, 1.2), (0.52, 0.86), (0.44, 0.62)),
                    bez((0.44, 0.62), (0.32, 0.3), (0.16, -0.06), (-0.04, -0.24))),
              bez((0.44, 0.62), (0.52, 0.4), (0.66, 0.16), (0.82, 0.02)),
              chain(line((0.82, C), (0.86, 1.22)), line((0.86, 1.22), (0.5, 0.76))),
              line((0.08, 0.64), (0.88, 0.68))]
    L["Y"] = [chain(line((-0.06, 1.22), (0.06, 1.34)), bez((0.06, 1.34), (0.14, 1.0), (0.4, 0.74), (0.46, 0.5)), line((0.46, 0.5), (0.46, 0.08))),
              chain(line((0.86, C), (0.92, 1.26)), line((0.92, 1.26), (0.5, 0.62))),
              poly((0.24, 0.0), (0.5, 0.0), (0.72, 0.08))]
    L["Z"] = [poly((0.02, 1.2), (0.2, 1.38), (0.92, 1.4)), line((0.92, 1.4), (0.04, 0.04)),
              poly((0.04, 0.04), (0.5, 0.0), (1.0, 0.12)), line((0.16, 0.68), (0.86, 0.72))]
    return L


# ---- Gothicized Italic figures ------------------------------------------------------------------------------------------
# The sheet has no figures: old-style figures with their curves broken, as gothic hands write them: 0, 1, 2 within the
# x-height, 6 and 8 rise, 3, 4, 5, 7, 9 descend (short, as the descenders are).
def _figures():
    L = {}
    L["0"] = [bez((0.3, 1.02), (0.0, 0.86), (-0.04, 0.24), (0.14, 0.0)), bez((0.3, 1.02), (0.48, 0.8), (0.48, 0.2), (0.14, 0.0))]
    L["1"] = [chain(head(0.04, 1.02), line((0.04, 1.02), (0.04, 0.12)), foot(0.04))]
    L["2"] = [poly((0.0, 0.84), (0.14, 1.0), (0.38, 0.98), (0.42, 0.7), (0.0, 0.04), (0.3, 0.0), (0.48, 0.1))]
    L["3"] = [poly((0.02, 0.88), (0.14, 1.0), (0.4, 0.98), (0.42, 0.74), (0.16, 0.5), (0.44, 0.3), (0.44, -0.1), (0.26, -0.36), (-0.02, -0.3))]
    L["4"] = [poly((0.34, 1.0), (0.0, 0.14), (0.5, 0.14)), line((0.38, 0.7), (0.38, -0.4))]
    L["5"] = [poly((0.1, 1.0), (0.06, 0.52), (0.3, 0.6), (0.44, 0.4), (0.44, -0.1), (0.26, -0.36), (-0.02, -0.3)), line((0.1, 1.0), (0.46, 1.02))]
    L["6"] = [poly((0.42, 1.3), (0.24, 1.4), (0.06, 1.2), (0.0, 0.2), (0.16, 0.0), (0.4, 0.1), (0.44, 0.5), (0.26, 0.66), (0.02, 0.5))]
    L["7"] = [poly((0.0, 0.94), (0.46, 1.0), (0.2, 0.2), (0.16, -0.4))]
    L["8"] = [poly((0.38, 1.26), (0.26, 1.36), (0.08, 1.3), (0.04, 1.08), (0.44, 0.5), (0.44, 0.16), (0.26, 0.0), (0.06, 0.04), (0.0, 0.3),
                   (0.38, 0.86), (0.38, 1.2), (0.3, 1.34))]
    L["9"] = [poly((0.42, 0.84), (0.3, 1.0), (0.06, 0.94), (0.0, 0.6), (0.12, 0.4), (0.44, 0.5)), poly((0.44, 1.0), (0.44, -0.2), (0.28, -0.4), (0.0, -0.34))]
    return L


def letters():
    L = _small()
    L.update(_capitals())
    L.update(_figures())
    return L


HAND = dict(
    id="gothicized", name="Gothicized Italic", family="gothicized", variant=None, pen="broad", S=42, base=71, slant_deg=0,
    ext=(ASC, -DESC), start="inmuahdo", sample="gothic", keys="anog", nib_angle=35, nib=7.4, hair=1.0, dot_w=6.0, cap=C,
    about={
        "tool": "A broad-edged pen held at about 35°.", "slant": "Upright (the exemplar's stems are vertical).",
        "proportions": "x-height about 5¾ nib widths; ascenders 0.37 x-heights above it, descenders 0.42 below; capitals "
                       "1.4 x-heights.",
        "features": "Italic's structure with blackletter's angles and weight: arches that leave the stem high up as a straight "
                    "hairline and turn at a sharp peak, a lens-shaped o, a two-part a and g (the left side, a hairline up "
                    "into the stem, a separate top, the stem), heads bent to the left, forked ascender heads, pointed feet. "
                    "The capitals mix round (uncial-like) C, D, E, G, M, O, T with straight A, H, I, K, L, N, begun with a "
                    "hairline curl and decorated with hairlines: across the round letters' left side, through M, W, X, "
                    "beside the stems of H, I, K, L. Simplified: the hairlines are set a little further from the stems "
                    "than on the sheet, so a copy can tell them apart; the figures (the sheet has none) are old-style.",
        "history": "A 20th-century calligrapher's hand: italic written with the angularity and weight of blackletter, close "
                   "to the Bâtarde and the gothic cursives of the 15th and 16th centuries."})
