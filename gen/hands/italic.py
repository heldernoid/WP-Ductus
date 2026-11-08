"""Italic (Cancelleresca corsiva, the chancery hand of Arrighi's La Operina, 1522, as taught today): small letters,
swash capitals and old-style figures, all authored for this hand from an italic exemplar sheet (with its
stroke numbers and arrows) and Arrighi's printed page.

Measured on the exemplar sheet (x-height 76 px; the hand's numbers are these, rounded):

  quantity                              exemplar             hand
  x-height                              76 px                1 (S = 27 px)
  ascender (b d h k l, top of f)        152 px = 2.0 xh      2.0
  descender (f g j p q y; G J)          77-79 px = 1.02 xh   1.02
  capital height                        107-109 px = 1.42 xh 1.42
  nib (widest stroke)                   13-15 px             x-height 5.3 nib widths (nib 5.1 px)
  stems (horizontal run)                10 px                nib 5.1 x sin(80 - 35) ...
  horizontals (f, t bars)               6-7 px               ... and nib x sin 35: the nib angle 35 (measured 31-35)
  slant (stems of b d h k l m)          9.5-10.8 deg         10 deg
  n, m: stem to stem                    33 px = 0.43 xh      0.44
  o (centre lines at mid height)        37 px = 0.49 xh      0.5
  a: bowl to stem                       33 px = 0.43 xh      0.44
  capitals, upright width with swash    H 1.2, M 1.6, W 1.65, A 1.45, O 0.65 xh
"""
from gen.pen import arc, bez, chain, dot, line, poly  # noqa: F401


# ---- Italic small letters -----------------------------------------------------------------------------------------------
# Springing arches that leave the stem about two thirds up and turn at the top right; a, d, g, q, u are the same shape
# the other way up (round at the bottom left, a hairline back up into the stem). Ascenders start with a small wedge to
# the left; stems that end a letter turn out into a hairline exit; f, g, j, y end in a long tail swept to the left, its
# end written as a separate stroke from the left (the sheet's arrows).
W = 0.44                                         # stem to stem in n, and the width of the a-bowl
ASC, DESC = 2.0, -1.02                           # ascender and descender lines
SP = 0.62                                        # where an arch springs from the stem


def entry(u, top=1.0):                           # the small hairline lead-in at the head of a stem (a wedge)
    return line((u - 0.1, top - 0.08), (u, top))


def exit_(u, v=0.2):                             # the foot: the stem turns and leaves as a hairline (the start of a join)
    return bez((u, v), (u, 0.03), (u + 0.08, -0.01), (u + 0.22, 0.09))


def stem(u, top=1.0, end=0.0, foot=True):        # entry, straight stem, and (if foot) the turn out at the baseline
    if foot:
        return chain(entry(u, top), line((u, top), (u, 0.2)), exit_(u))
    return chain(entry(u, top), line((u, top), (u, end)))


def arch(u0, u1, foot=True, end=0.0):            # springs from the stem at u0, round at the top right, down the stem u1
    w = u1 - u0
    a = bez((u0, SP), (u0 + 0.04 * w / W, 0.88), (u0 + 0.22 * w / W, 1.02), (u0 + 0.5 * w, 1.0))
    b = bez((u0 + 0.5 * w, 1.0), (u1 - 0.02, 0.99), (u1, 0.9), (u1, 0.72))
    if foot:
        return chain(a, b, line((u1, 0.72), (u1, 0.2)), exit_(u1))
    return chain(a, b, line((u1, 0.72), (u1, end)))


def bowl(top=(0.26, 0.98)):                      # a, d, g, q: from the top, down the left, round the foot, up to the stem
    return chain(bez(top, (0.08, 0.96), (0.0, 0.72), (0.0, 0.42)), bez((0.0, 0.42), (0.0, 0.1), (0.08, -0.01), (0.18, 0.01)),
                 line((0.18, 0.01), (W, 0.45)))


def bowl_top():                                  # a, d, g, q: the hairline top, from the bowl's start to the stem's head
    return bez((0.26, 0.98), (0.32, 1.0), (0.38, 1.01), (W + 0.02, 1.0))


def tail(u, top=1.0, ent=True):                  # a descender stem curving left; its end is the tail stroke
    st = [line((u, top), (u, -0.45)), bez((u, -0.45), (u - 0.01, -0.8), (u - 0.1, -0.96), (u - 0.26, DESC + 0.04))]
    return chain(entry(u, top), *st) if ent else chain(*st)


def tail_end(u):                                 # the tail's end: from the left, along the descender line into the stem's curve
    return chain(line((u - 0.8, DESC + 0.05), (u - 0.7, DESC)), bez((u - 0.7, DESC), (u - 0.56, DESC + 0.01), (u - 0.42, DESC + 0.02), (u - 0.26, DESC + 0.04)))


def _small():
    L = {}
    L["a"] = [bowl(), bowl_top(), stem(W)]
    L["b"] = [stem(0, ASC, 0.03, foot=False),
              chain(bez((0, SP), (0.04, 0.88), (0.2, 1.02), (0.28, 1.0)), bez((0.28, 1.0), (0.42, 0.98), (W + 0.04, 0.82), (W + 0.04, 0.55)),
                    bez((W + 0.04, 0.55), (W + 0.04, 0.2), (0.4, 0.0), (0.2, 0.0))),
              line((0.02, 0.05), (0.2, 0.0))]
    L["c"] = [chain(bez((0.3, 0.98), (0.1, 0.96), (0.0, 0.72), (0.0, 0.45)), bez((0.0, 0.45), (0.0, 0.12), (0.1, -0.01), (0.24, 0.0)),
                    bez((0.24, 0.0), (0.32, 0.0), (0.38, 0.04), (0.44, 0.13))),
              bez((0.3, 0.98), (0.38, 1.01), (0.44, 1.0), (0.46, 0.9))]
    L["d"] = [bowl(), bowl_top(), stem(W, ASC)]
    L["e"] = [chain(bez((0.3, 0.98), (0.1, 0.96), (0.0, 0.72), (0.0, 0.45)), bez((0.0, 0.45), (0.0, 0.12), (0.1, -0.01), (0.24, 0.0)),
                    bez((0.24, 0.0), (0.32, 0.0), (0.38, 0.04), (0.44, 0.13))),
              chain(bez((0.3, 0.98), (0.42, 1.0), (0.47, 0.9), (0.44, 0.78)), bez((0.44, 0.78), (0.4, 0.62), (0.2, 0.5), (0.02, 0.46)))]
    L["f"] = [chain(line((0.3, 1.72), (0.16, -0.45)), bez((0.16, -0.45), (0.13, -0.8), (0.06, -0.96), (-0.1, DESC + 0.04))),
              bez((0.3, 1.72), (0.34, 1.94), (0.5, 2.03), (0.76, 1.98)),
              tail_end(0.16),
              line((-0.06, 1.0), (0.5, 1.02))]
    L["g"] = [bowl(), bowl_top(), tail(W, ent=False), tail_end(W)]
    L["h"] = [stem(0, ASC, 0.0, foot=False), arch(0, W)]
    L["i"] = [stem(0), line((0.1, 1.42), (0.03, 1.3))]
    L["j"] = [tail(0), tail_end(0), line((0.1, 1.42), (0.03, 1.3))]
    L["k"] = [stem(0, ASC, 0.0, foot=False),
              chain(bez((0, 0.5), (0.06, 0.82), (0.24, 1.02), (0.36, 0.98)), bez((0.36, 0.98), (0.5, 0.92), (0.44, 0.62), (0.1, 0.52))),
              chain(bez((0.12, 0.52), (0.26, 0.48), (0.34, 0.36), (0.38, 0.2)), exit_(0.38))]
    L["l"] = [stem(0, ASC)]
    L["m"] = [stem(0, 1.0, 0.0, foot=False), arch(0, W - 0.01, foot=False), arch(W - 0.01, 2 * W - 0.02)]
    L["n"] = [stem(0, 1.0, 0.0, foot=False), arch(0, W)]
    L["o"] = [chain(bez((0.34, 0.99), (0.1, 0.98), (0.0, 0.7), (0.0, 0.42)), bez((0.0, 0.42), (0.0, 0.12), (0.1, 0.0), (0.24, 0.0))),
              chain(bez((0.34, 0.99), (0.5, 1.0), (0.56, 0.82), (0.56, 0.58)), bez((0.56, 0.58), (0.56, 0.25), (0.44, 0.0), (0.24, 0.0)))]
    L["p"] = [stem(0, 1.0, DESC, foot=False),
              chain(bez((0, SP), (0.04, 0.88), (0.2, 1.02), (0.28, 1.0)), bez((0.28, 1.0), (0.42, 0.98), (W + 0.04, 0.82), (W + 0.04, 0.55)),
                    bez((W + 0.04, 0.55), (W + 0.04, 0.2), (0.4, 0.0), (0.2, 0.0))),
              line((0.03, 0.05), (0.2, 0.0))]
    L["q"] = [bowl(), bowl_top(), chain(line((W, 1.0), (W, DESC + 0.06)), line((W, DESC + 0.06), (W + 0.03, DESC)))]
    L["r"] = [stem(0, 1.0, 0.0, foot=False),
              chain(bez((0, SP), (0.06, 0.88), (0.2, 1.02), (0.32, 1.0)), bez((0.32, 1.0), (0.42, 0.99), (0.48, 0.97), (0.52, 0.9)))]
    L["s"] = [chain(bez((0.32, 0.99), (0.12, 0.99), (0.04, 0.88), (0.06, 0.72)), bez((0.06, 0.72), (0.08, 0.54), (0.48, 0.5), (0.48, 0.24)),
                    bez((0.48, 0.24), (0.48, 0.06), (0.34, -0.01), (0.16, 0.0))),
              bez((0.32, 0.99), (0.4, 1.0), (0.48, 0.98), (0.52, 0.92)),
              bez((-0.06, 0.08), (0.0, 0.03), (0.08, 0.0), (0.16, 0.0))]
    L["t"] = [chain(line((0.1, 1.32), (0.1, 0.2)), exit_(0.1)), line((-0.06, 1.0), (0.48, 1.02))]
    L["u"] = [chain(entry(0), line((0, 1.0), (0, 0.4)), bez((0, 0.4), (0, 0.08), (0.08, -0.01), (0.18, 0.01)), line((0.18, 0.01), (W, 0.45))),
              stem(W)]
    L["v"] = [chain(entry(0.0), line((0.0, 1.0), (0.2, 0.04)), line((0.2, 0.04), (0.22, 0.0))),
              chain(bez((0.5, 1.02), (0.46, 0.98), (0.44, 0.9), (0.42, 0.78)), line((0.42, 0.78), (0.24, 0.04)))]
    L["w"] = [chain(entry(0.0), line((0.0, 1.0), (0.2, 0.06)), bez((0.2, 0.06), (0.22, 0.0), (0.25, -0.01), (0.27, 0.0))),
              line((0.5, 0.94), (0.29, 0.03)),
              chain(line((0.5, 0.94), (0.68, 0.06)), bez((0.68, 0.06), (0.7, 0.0), (0.73, -0.01), (0.75, 0.0))),
              chain(bez((1.0, 1.02), (0.96, 0.98), (0.94, 0.9), (0.92, 0.8)), line((0.92, 0.8), (0.77, 0.03)))]
    L["x"] = [chain(bez((-0.08, 0.9), (-0.02, 1.0), (0.04, 1.0), (0.08, 0.92)), line((0.08, 0.92), (0.46, 0.1)),
                    bez((0.46, 0.1), (0.49, 0.01), (0.54, 0.0), (0.6, 0.06))),
              chain(line((0.6, 1.0), (0.38, 0.6)), bez((0.38, 0.6), (0.24, 0.32), (0.06, 0.02), (-0.12, 0.02)))]
    L["y"] = [chain(entry(0), line((0, 1.0), (0, 0.4)), bez((0, 0.4), (0, 0.08), (0.08, -0.01), (0.18, 0.01)), line((0.18, 0.01), (W, 0.45))),
              tail(W), tail_end(W)]
    L["z"] = [bez((0.02, 0.94), (0.18, 1.02), (0.36, 0.96), (0.56, 1.0)), line((0.56, 1.0), (0.0, 0.0)),
              bez((0.0, 0.0), (0.2, 0.06), (0.4, -0.04), (0.62, 0.05))]
    return L


# ---- Italic capitals ----------------------------------------------------------------------------------------------------
# The exemplar's swash capitals: wide (H 1.2, M 1.6 x-heights), slanted with the small letters, most begun with an
# entry swash, a thick arc that rises from a curl at the left and runs over the head of the first stem, and many with
# a sweeping foot at the bottom left written from the left. The stroke numbers are the sheet's.
C = 1.42


def swash(u_end, u0=-0.36, v0=0.98):             # the entry swash: from its low left end, up and over to the stem's head
    return bez((u0, v0), (u0 + 0.04, C - 0.1), (u_end - 0.24, C + 0.02), (u_end, C))


def curl(u0=-0.36, v0=0.98):                     # the curl at the swash's left end (the A's stroke 6), written down
    return bez((u0, v0), (u0 - 0.04, v0 - 0.05), (u0 - 0.04, v0 - 0.1), (u0 - 0.01, v0 - 0.16))


def cstem(u_top=0.12, foot=False, end=0.04):     # a capital's stem, leaning a little more than the slant
    if foot:                                     # ends turning left into the sweep of the foot stroke
        return chain(line((u_top, C - 0.1), (0.0, 0.2)), bez((0.0, 0.2), (-0.02, 0.06), (-0.08, 0.01), (-0.16, 0.0)))
    return line((u_top, C - 0.1), (0.0, end))


def sweep(u_end=-0.16, u0=-0.58):                # the sweeping foot, written from the left into the stem's foot
    return bez((u0, -0.02), (u0 + 0.12, 0.01), (u_end - 0.14, 0.0), (u_end, 0.0))


def _capitals():
    L = {}
    L["A"] = [line((0.06, C), (-0.6, 0.3)),
              bez((-1.42, 0.03), (-1.1, 0.12), (-0.82, 0.12), (-0.6, 0.3)),
              chain(line((0.06, C), (0.0, 0.2)), exit_(0.0)),
              line((-0.56, 0.48), (-0.02, 0.52)),
              swash(0.06, -0.92, 1.08), curl(-0.92, 1.08)]
    L["B"] = [cstem(0.12, end=0.04),
              chain(bez((0.12, C), (0.4, C + 0.01), (0.58, 1.32), (0.56, 1.1)), bez((0.56, 1.1), (0.54, 0.86), (0.36, 0.78), (0.08, 0.76))),
              chain(bez((0.08, 0.76), (0.5, 0.76), (0.74, 0.6), (0.7, 0.32)), bez((0.7, 0.32), (0.66, 0.06), (0.44, 0.0), (0.24, 0.0))),
              bez((-0.3, -0.02), (-0.1, 0.03), (0.06, 0.0), (0.24, 0.0)),
              swash(0.12), curl()]
    L["C"] = [chain(bez((0.62, 1.36), (0.24, 1.44), (0.0, 1.2), (0.0, 0.72)), bez((0.0, 0.72), (0.0, 0.2), (0.2, 0.0), (0.4, 0.0)),
                    bez((0.4, 0.0), (0.5, 0.0), (0.58, 0.06), (0.64, 0.16))),
              bez((0.62, 1.36), (0.7, 1.4), (0.76, 1.44), (0.84, 1.42))]
    L["D"] = [cstem(0.12, end=0.04),
              chain(bez((0.12, C), (0.6, C + 0.03), (0.98, 1.2), (0.96, 0.72)), bez((0.96, 0.72), (0.94, 0.2), (0.64, 0.0), (0.3, 0.0))),
              bez((-0.36, -0.02), (-0.14, 0.03), (0.08, 0.0), (0.3, 0.0)),
              swash(0.12), curl()]
    L["E"] = [cstem(0.12, end=0.04),
              bez((-0.32, -0.02), (0.0, 0.04), (0.32, -0.02), (0.64, 0.08)),
              bez((0.12, C), (0.3, C + 0.03), (0.5, C), (0.72, C + 0.04)),
              line((0.05, 0.72), (0.5, 0.74)),
              swash(0.12), curl()]
    L["F"] = [chain(line((0.12, C - 0.1), (0.0, -0.1)), bez((0.0, -0.1), (-0.02, -0.34), (-0.1, -0.44), (-0.22, -0.46))),
              bez((0.12, C), (0.4, C + 0.04), (0.7, C), (1.0, C + 0.04)),
              bez((-0.66, -0.47), (-0.52, -0.44), (-0.38, -0.44), (-0.22, -0.46)),
              line((-0.1, 0.74), (0.42, 0.76)),
              swash(0.12), curl()]
    L["G"] = [chain(bez((0.62, 1.36), (0.24, 1.44), (0.0, 1.2), (0.0, 0.72)), bez((0.0, 0.72), (0.0, 0.2), (0.2, 0.0), (0.4, 0.0)),
                    bez((0.4, 0.0), (0.56, 0.0), (0.68, 0.08), (0.74, 0.2))),
              bez((0.62, 1.36), (0.7, 1.4), (0.76, 1.44), (0.84, 1.42)),
              chain(line((0.8, 0.68), (0.76, -0.45)), bez((0.76, -0.45), (0.75, -0.8), (0.64, -0.96), (0.46, DESC + 0.04))),
              bez((0.38, 0.6), (0.54, 0.68), (0.7, 0.7), (0.92, 0.7)),
              bez((-0.04, DESC), (0.12, DESC + 0.01), (0.28, DESC + 0.02), (0.46, DESC + 0.04))]
    L["H"] = [cstem(0.12, foot=True),
              swash(0.62, -0.44, 1.16),
              sweep(),
              chain(line((0.84, C - 0.06), (0.74, 0.2)), exit_(0.74)),
              line((0.04, 0.76), (0.76, 0.8))]
    L["I"] = [cstem(0.1, end=0.04),
              bez((-0.28, -0.02), (-0.06, 0.03), (0.14, -0.01), (0.4, 0.06)),
              bez((-0.2, C - 0.06), (0.0, C + 0.02), (0.2, C - 0.02), (0.44, C + 0.04))]
    L["J"] = [chain(line((0.24, C - 0.04), (0.18, -0.45)), bez((0.18, -0.45), (0.17, -0.8), (0.08, -0.96), (-0.08, DESC + 0.04))),
              bez((-0.48, 1.3), (-0.2, C + 0.04), (0.2, C), (0.6, C + 0.04)),
              bez((-0.6, DESC), (-0.44, DESC + 0.01), (-0.26, DESC + 0.02), (-0.08, DESC + 0.04)),
              curl(-0.48, 1.3)]
    L["K"] = [cstem(0.12, foot=True),
              chain(bez((0.86, 1.36), (0.7, 1.4), (0.56, 1.2), (0.4, 0.92)), bez((0.4, 0.92), (0.28, 0.72), (0.18, 0.62), (0.04, 0.6))),
              chain(bez((0.18, 0.62), (0.32, 0.48), (0.48, 0.3), (0.62, 0.18)), exit_(0.66, 0.15)),
              sweep(),
              swash(0.12), curl()]
    L["L"] = [chain(line((0.16, C - 0.06), (0.0, 0.2)), bez((0.0, 0.2), (-0.02, 0.06), (-0.08, 0.01), (-0.16, 0.0))),
              bez((-0.44, -0.03), (-0.1, 0.06), (0.3, -0.04), (0.66, 0.06)),
              chain(bez((-0.14, 1.02), (-0.12, 1.3), (0.04, C + 0.02), (0.24, C)), bez((0.24, C), (0.36, C - 0.01), (0.46, C + 0.02), (0.52, C + 0.06)))]
    L["M"] = [chain(line((0.34, C), (0.0, 0.2)), bez((0.0, 0.2), (-0.04, 0.06), (-0.1, 0.01), (-0.18, 0.0))),
              sweep(-0.18, -0.6),
              line((0.34, C), (0.74, 0.0)),
              line((1.24, C + 0.02), (0.76, 0.02)),
              chain(line((1.24, C + 0.02), (1.16, 0.2)), exit_(1.16)),
              swash(0.34, -0.3, 1.06), curl(-0.3, 1.06)]
    L["N"] = [chain(line((0.22, C), (0.0, 0.2)), bez((0.0, 0.2), (-0.03, 0.06), (-0.09, 0.01), (-0.17, 0.0))),
              line((0.22, C), (0.84, 0.0)),
              line((0.98, C + 0.02), (0.86, 0.04)),
              sweep(-0.17, -0.6),
              swash(0.22, -0.36, 1.04), curl(-0.36, 1.04)]
    L["O"] = [chain(bez((0.42, C), (0.12, C), (0.0, 1.06), (0.0, 0.66)), bez((0.0, 0.66), (0.0, 0.24), (0.14, 0.0), (0.34, 0.0))),
              chain(bez((0.42, C), (0.64, C), (0.74, 1.12), (0.74, 0.76)), bez((0.74, 0.76), (0.74, 0.3), (0.56, 0.0), (0.34, 0.0)))]
    L["P"] = [cstem(0.12, foot=True),
              chain(bez((0.12, C), (0.5, C + 0.03), (0.8, 1.32), (0.78, 1.04)), bez((0.78, 1.04), (0.76, 0.72), (0.44, 0.62), (0.06, 0.62))),
              sweep(),
              swash(0.12), curl()]
    L["Q"] = [chain(bez((0.42, C), (0.12, C), (0.0, 1.06), (0.0, 0.66)), bez((0.0, 0.66), (0.0, 0.24), (0.14, 0.0), (0.34, 0.0))),
              chain(bez((0.42, C), (0.64, C), (0.74, 1.12), (0.74, 0.76)), bez((0.74, 0.76), (0.74, 0.3), (0.56, 0.0), (0.34, 0.0))),
              line((0.3, -0.03), (0.06, -0.2)),
              bez((0.06, -0.2), (0.3, -0.22), (0.5, -0.34), (0.82, -0.24))]
    L["R"] = [cstem(0.12, foot=True),
              chain(bez((0.12, C), (0.5, C + 0.03), (0.8, 1.32), (0.78, 1.06)), bez((0.78, 1.06), (0.76, 0.76), (0.44, 0.66), (0.06, 0.66))),
              chain(bez((0.28, 0.66), (0.44, 0.5), (0.6, 0.3), (0.7, 0.18)), exit_(0.74, 0.15)),
              sweep(),
              swash(0.12), curl()]
    L["S"] = [chain(bez((0.5, C - 0.02), (0.2, C), (0.04, 1.28), (0.06, 1.06)), bez((0.06, 1.06), (0.1, 0.78), (0.62, 0.66), (0.62, 0.34)),
                    bez((0.62, 0.34), (0.62, 0.08), (0.42, -0.01), (0.2, 0.0))),
              bez((0.5, C - 0.02), (0.6, C), (0.68, C + 0.02), (0.76, C + 0.04)),
              bez((-0.2, 0.08), (-0.1, 0.03), (0.04, 0.0), (0.2, 0.0))]
    L["T"] = [chain(line((0.16, C - 0.02), (0.0, 0.2)), bez((0.0, 0.2), (-0.02, 0.06), (-0.08, 0.01), (-0.16, 0.0))),
              bez((-0.6, 1.08), (-0.5, C + 0.02), (0.4, C - 0.02), (0.92, C + 0.06)),
              bez((-0.44, -0.02), (-0.34, 0.01), (-0.26, 0.0), (-0.16, 0.0)),
              curl(-0.6, 1.08)]
    L["U"] = [chain(line((0.12, C - 0.1), (0.02, 0.4)), bez((0.02, 0.4), (-0.04, 0.06), (0.1, -0.01), (0.26, 0.01)),
                    bez((0.26, 0.01), (0.46, 0.04), (0.62, 0.2), (0.74, 0.48))),
              chain(line((0.86, C), (0.76, 0.2)), exit_(0.76)),
              swash(0.12), curl()]
    L["V"] = [chain(entry(0.04, C - 0.06), line((0.04, C - 0.06), (0.4, 0.02))),
              chain(bez((1.12, C + 0.08), (1.02, C + 0.04), (0.94, C - 0.06), (0.86, 1.2)), line((0.86, 1.2), (0.42, 0.02)))]
    L["W"] = [chain(entry(0.04, C - 0.06), line((0.04, C - 0.06), (0.36, 0.02))),
              line((0.72, C - 0.04), (0.38, 0.04)),
              line((0.72, C - 0.04), (1.04, 0.02)),
              chain(bez((1.44, C + 0.06), (1.38, C + 0.02), (1.34, C - 0.06), (1.3, 1.2)), line((1.3, 1.2), (1.06, 0.04))),
              bez((0.3, C + 0.04), (0.0, C + 0.04), (-0.3, 1.32), (-0.4, 1.12)), line((-0.4, 1.12), (-0.38, 0.96))]
    L["X"] = [chain(bez((-0.12, 1.28), (-0.04, C + 0.02), (0.06, C), (0.12, 1.3)), line((0.12, 1.3), (0.7, 0.14)),
                    bez((0.7, 0.14), (0.75, 0.03), (0.82, 0.0), (0.9, 0.04))),
              chain(bez((-0.3, 0.02), (-0.1, 0.04), (0.04, 0.16), (0.2, 0.36)), line((0.2, 0.36), (0.86, 1.26)),
                    bez((0.86, 1.26), (0.94, 1.36), (1.0, 1.42), (1.06, C + 0.04)))]
    L["Y"] = [chain(entry(0.04, C - 0.06), bez((0.04, C - 0.06), (0.06, 1.0), (0.22, 0.72), (0.32, 0.56)), line((0.32, 0.56), (0.3, 0.02))),
              bez((0.06, -0.02), (0.18, 0.01), (0.34, -0.01), (0.5, 0.03)),
              line((1.02, C + 0.04), (0.36, 0.6))]
    L["Z"] = [bez((0.0, C - 0.12), (0.24, C + 0.02), (0.56, C - 0.06), (0.86, C + 0.02)), line((0.86, C + 0.02), (0.04, 0.02)),
              bez((0.04, 0.02), (0.34, 0.08), (0.62, -0.06), (0.96, 0.06)),
              line((0.22, 0.7), (0.72, 0.74))]
    return L


# ---- Italic figures -----------------------------------------------------------------------------------------------------
# The sheet has no figures. Italic is written with old-style (hanging) figures, as in the writing books: 0, 1, 2 within
# the x-height, 6 and 8 rise to the ascender's half, 3, 4, 5, 7, 9 descend.
def _figures():
    L = {}
    L["0"] = [chain(bez((0.28, 1.0), (0.06, 1.0), (0.0, 0.7), (0.0, 0.45)), bez((0.0, 0.45), (0.0, 0.12), (0.12, 0.0), (0.24, 0.0))),
              chain(bez((0.28, 1.0), (0.44, 1.0), (0.5, 0.8), (0.5, 0.56)), bez((0.5, 0.56), (0.5, 0.2), (0.38, 0.0), (0.24, 0.0)))]
    L["1"] = [chain(entry(0.06), line((0.06, 1.0), (0.06, 0.0)))]
    L["2"] = [chain(bez((0.02, 0.78), (0.08, 1.02), (0.42, 1.04), (0.44, 0.75)), bez((0.44, 0.75), (0.46, 0.5), (0.1, 0.25), (0.0, 0.0)),
                    bez((0.0, 0.0), (0.16, 0.05), (0.34, -0.03), (0.52, 0.05)))]
    L["3"] = [chain(bez((0.04, 0.85), (0.12, 1.02), (0.42, 1.04), (0.42, 0.8)), bez((0.42, 0.8), (0.42, 0.6), (0.26, 0.5), (0.12, 0.48)),
                    bez((0.12, 0.48), (0.4, 0.46), (0.52, 0.25), (0.5, 0.0)), bez((0.5, 0.0), (0.48, -0.4), (0.1, -0.6), (-0.08, -0.4)))]
    L["4"] = [chain(line((0.36, 1.0), (0.0, 0.1)), line((0.0, 0.1), (0.56, 0.1))), line((0.42, 0.62), (0.4, -0.6))]
    L["5"] = [chain(line((0.12, 1.0), (0.06, 0.5)), bez((0.06, 0.5), (0.3, 0.62), (0.52, 0.45), (0.5, 0.1)), bez((0.5, 0.1), (0.48, -0.38), (0.1, -0.6), (-0.08, -0.4))),
              line((0.12, 1.0), (0.5, 1.02))]
    L["6"] = [chain(bez((0.48, 1.38), (0.3, 1.52), (0.02, 1.3), (0.0, 0.6)), bez((0.0, 0.6), (-0.02, 0.1), (0.14, 0.0), (0.26, 0.0)),
                    bez((0.26, 0.0), (0.44, 0.0), (0.5, 0.25), (0.5, 0.42)), bez((0.5, 0.42), (0.5, 0.7), (0.24, 0.82), (0.03, 0.52)))]
    L["7"] = [chain(bez((0.0, 0.96), (0.16, 1.02), (0.34, 0.97), (0.52, 1.0)), bez((0.52, 1.0), (0.32, 0.6), (0.18, 0.0), (0.14, -0.6)))]
    L["8"] = [chain(bez((0.4, 1.32), (0.3, 1.46), (0.04, 1.46), (0.04, 1.2)), bez((0.04, 1.2), (0.04, 0.94), (0.5, 0.75), (0.5, 0.38)),
                    bez((0.5, 0.38), (0.5, 0.05), (0.36, 0.0), (0.24, 0.0)), bez((0.24, 0.0), (0.08, 0.0), (0.0, 0.14), (0.0, 0.36)),
                    bez((0.0, 0.36), (0.0, 0.72), (0.44, 0.9), (0.44, 1.18)), bez((0.44, 1.18), (0.44, 1.36), (0.36, 1.44), (0.28, 1.45)))]
    L["9"] = [chain(bez((0.46, 0.8), (0.4, 1.02), (0.04, 1.04), (0.02, 0.66)), bez((0.02, 0.66), (0.0, 0.35), (0.3, 0.3), (0.46, 0.56))),
              chain(line((0.48, 1.0), (0.48, 0.2)), bez((0.48, 0.2), (0.46, -0.3), (0.2, -0.6), (-0.06, -0.46)))]
    return L


def letters():
    L = _small()
    L.update(_capitals())
    L.update(_figures())
    return L


HAND = dict(
    id="italic", name="Italic", family="italic", variant=None, pen="broad", S=27, base=61, slant_deg=10, ext=(ASC, -DESC),
    start="inmuahdo", sample="Italic", keys="anog", nib_angle=35, nib=5.1, hair=0.9, dot_w=4.4, cap=C,
    about={
        "tool": "A broad-edged pen held at about 35°.", "slant": "About 10°, the same for every letter.",
        "proportions": "x-height about 5¼ nib widths; ascenders and descenders one x-height more each (ascender line at 2, "
                       "descender at 1); capitals 1.4 x-heights.",
        "features": "Compressed and springing: the arches of n, m, h, b, p, r leave the stem about two thirds up and turn at "
                    "the top right; a, d, g, q, u are the same shape the other way up (round at the bottom left, a hairline "
                    "back up into the stem), with a separate hairline top. Small wedge heads, hairline exits, and long tails "
                    "on f, g, j, y finished from the left. The capitals are swash capitals: wide, begun with a thick entry "
                    "swash from a curl at the left, many with a sweeping foot. Simplified: the joins between letters are "
                    "not drawn; the figures (the sheet has none) are the old-style figures of the writing books.",
        "history": "The chancery hand (cancelleresca) of the papal scribes in Renaissance Italy; Ludovico degli Arrighi's "
                   "La Operina (1522) is its classic manual. Revived in the 20th century by Edward Johnston and Alfred Fairbank."})
