"""Foundational hand (Edward Johnston, after the 10th-century English Carolingian minuscule).

Measured on a Foundational exemplar sheet (small letters with ductus arrows; px of that sheet, ink):

  x-height            97 px (n, o; the ink's top to its foot)   skeleton (pen centre) 85.5 px = 1 unit
  ascender (b d h k l) 149 px above the baseline = 1.53 x-heights of ink; skeleton 1.6 units
  descender (p q j)    47 px below = 0.48 x-heights of ink; skeleton 0.55 units;  t 1.24 of ink
  stem                 20 px across (b, d, a, h, n), horizontals and the o's thin parts 10-12 px: nib 23 px at 30 deg
  x-height in nibs     97 / 23 = 4.2 nib widths (ink; Johnston: 4), 3.7 nib widths centre to centre
  slant                0 (b, d, h stems vertical to the pixel over 100 px)
  widths (ink / x-height of ink)  o 1.05 (a circle)  n 1.03  m 1.63  w 1.63  a .95  b 1.07  c .95  d 1.11  e .97
                       h 1.04  k 1.07  l .75  p 1.14  q 1.15  r .85  s .84  t .99  u 1.18  v 1.01  x .95  y 1.05  z .94
The sheet has no capitals or figures: the capitals are Johnston's Roman-proportioned pen capitals (6 nib widths below
the 7 of the ascenders in his scheme: here 1.4 x-heights), the figures his old-style pen figures.
"""
from gen.pen import arc, bez, chain, dot, line, scaled  # noqa: F401

ASC, DESC, CAP = 1.6, -0.55, 1.4


# ---- the pen's small parts ----------------------------------------------------------------------------------------------
def serif(u, top=1.0):
    """the wedge head: a short stroke from the left down into the top of a stem, written after the stem (the sheet's
    last number on b, d, h, i, k, l, n, p, r, u)"""
    return bez((u - 0.15, top - 0.087), (u - 0.1, top - 0.125), (u - 0.05, top - 0.162), (u - 0.005, top - 0.2), 6)


def foot(u, out=0.17):
    """the stem's end turning out to the right"""
    return bez((u, 0.16), (u, 0.03), (u + 0.05, -0.01), (u + out, 0.04), 8)


def stem(u, top=1.0, bot=0.0, ft=True):
    """a stem pulled down from top, ending in the small foot (or cut square at bot)"""
    return chain(line((u, top), (u, 0.16 if ft else bot)), *([foot(u)] if ft else []))


def arch(u0, u1, ft=True):
    """the n's arch: a hairline springing from high on the stem, round over the top as the o, down the right stem"""
    return chain(bez((u0 + 0.01, 0.58), (u0 + 0.1, 0.94), (u1 - 0.06, 1.06), (u1, 0.66)), line((u1, 0.66), (u1, 0.16 if ft else 0.0)),
                 *([foot(u1)] if ft else []))


def _small():
    L = {}
    # -- the o and its family
    L["o"] = [arc(0.48, 0.5, 0.48, 0.5, 115, 300), arc(0.48, 0.5, 0.48, 0.5, 115, -60)]      # from the thin at 11 o'clock
    L["c"] = [arc(0.45, 0.5, 0.45, 0.5, 105, 318),                                           # the back, ending in a flick
              chain(arc(0.45, 0.5, 0.45, 0.5, 105, 38), line((0.805, 0.81), (0.83, 0.75)))]  # the top, cut by the pen
    L["e"] = [arc(0.45, 0.5, 0.45, 0.5, 105, 318),
              arc(0.45, 0.5, 0.45, 0.5, 105, 2),                                           # over the top, down to the eye
              line((0.89, 0.52), (0.12, 0.3))]                                             # the thin bar, right to left
    # -- arched letters
    L["n"] = [stem(0), arch(0, 0.72), serif(0)]
    L["m"] = [stem(0), arch(0, 0.68), arch(0.68, 1.36), serif(0)]
    L["h"] = [stem(0, ASC), arch(0, 0.74), serif(0, ASC)]
    L["r"] = [stem(0), chain(bez((0.01, 0.6), (0.1, 0.95), (0.38, 1.04), (0.6, 0.95)), line((0.6, 0.95), (0.62, 0.84))), serif(0)]
    L["u"] = [chain(line((0, 1.0), (0, 0.34)), bez((0, 0.34), (0.0, -0.04), (0.58, -0.06), (0.71, 0.34))),
              stem(0.76), serif(0), serif(0.76)]
    # -- a, and the letters with a bowl on a stem
    L["a"] = [chain(bez((0.06, 0.74), (0.18, 1.04), (0.7, 1.08), (0.7, 0.62)), line((0.7, 0.62), (0.7, 0.16)), foot(0.7)),
              chain(line((0.69, 0.54), (0.26, 0.44)), bez((0.26, 0.44), (-0.04, 0.37), (-0.04, -0.02), (0.3, 0.0)),
                    bez((0.3, 0.0), (0.48, 0.0), (0.6, 0.06), (0.68, 0.16)))]
    L["b"] = [chain(line((0, ASC), (0, 0.24)), bez((0, 0.24), (0.0, 0.06), (0.14, -0.01), (0.32, 0.0))),
              chain(bez((0.01, 0.6), (0.14, 0.98), (0.88, 1.06), (0.88, 0.5)), bez((0.88, 0.5), (0.88, 0.1), (0.62, -0.01), (0.34, 0.0))),
              serif(0, ASC)]
    L["p"] = [stem(0, 1.0, DESC, ft=False),
              chain(bez((0.01, 0.6), (0.14, 0.98), (0.88, 1.06), (0.88, 0.48)), bez((0.88, 0.48), (0.88, 0.2), (0.8, 0.1), (0.66, 0.05))),
              bez((0.02, 0.1), (0.2, -0.02), (0.44, -0.03), (0.64, 0.04)), serif(0)]
    L["d"] = [chain(bez((0.4, 1.0), (0.1, 1.0), (0.0, 0.74), (0.0, 0.5)), bez((0.0, 0.5), (0.0, 0.08), (0.42, -0.08), (0.75, 0.16))),
              bez((0.36, 1.0), (0.52, 1.01), (0.66, 0.98), (0.78, 0.9)),
              stem(0.8, ASC), serif(0.8, ASC)]
    L["q"] = [chain(bez((0.4, 1.0), (0.1, 1.0), (0.0, 0.74), (0.0, 0.5)), bez((0.0, 0.5), (0.0, 0.08), (0.42, -0.08), (0.78, 0.18))),
              bez((0.36, 1.0), (0.56, 1.01), (0.72, 1.02), (0.84, 1.06)),
              chain(line((0.86, 1.08), (0.86, -0.4)), bez((0.86, -0.4), (0.86, -0.5), (0.9, -0.55), (1.0, -0.53), 8))]
    L["g"] = [arc(0.34, 0.71, 0.26, 0.28, 100, 270),                                        # upper bowl, left side
              arc(0.34, 0.71, 0.26, 0.28, 100, -85),                                        # right side
              chain(line((0.54, 0.96), (0.86, 1.01)), line((0.86, 1.01), (0.88, 0.95))),    # the ear
              chain(bez((0.34, 0.43), (0.62, 0.34), (0.88, 0.14), (0.86, -0.14)),           # the link, down the right side
                    bez((0.86, -0.14), (0.84, -0.42), (0.62, -0.53), (0.42, -0.52))),
              chain(bez((0.54, 0.12), (0.3, 0.04), (0.06, -0.12), (0.08, -0.32)),           # the lower bowl's left, to meet it
                    bez((0.08, -0.32), (0.1, -0.48), (0.28, -0.53), (0.4, -0.52)))]
    # -- stems
    L["i"] = [stem(0), serif(0), line((0.09, 1.52), (0.0, 1.32))]
    L["j"] = [chain(line((0.1, 1.0), (0.1, -0.3)), bez((0.1, -0.3), (0.1, -0.45), (0.0, -0.53), (-0.12, -0.56))), serif(0.1),
              line((0.19, 1.52), (0.1, 1.32))]
    L["l"] = [chain(line((0, ASC), (0, 0.28)), bez((0, 0.28), (0.0, 0.0), (0.26, -0.03), (0.52, 0.1))), serif(0, ASC)]
    L["k"] = [stem(0, ASC),
              chain(bez((0.01, 0.58), (0.12, 0.94), (0.7, 1.02), (0.68, 0.74)), bez((0.68, 0.74), (0.66, 0.52), (0.3, 0.45), (0.04, 0.44))),
              chain(line((0.3, 0.45), (0.62, 0.1)), bez((0.62, 0.1), (0.68, 0.02), (0.74, 0.0), (0.82, 0.03), 8)),
              serif(0, ASC)]
    L["f"] = [line((0.2, 1.4), (0.2, 0.02)),
              line((0.0, 0.0), (0.5, 0.0)),                                                  # the foot, left to right
              chain(bez((0.2, 1.4), (0.24, 1.58), (0.5, 1.62), (0.72, 1.48)), line((0.72, 1.48), (0.73, 1.4))),  # the hook
              line((-0.06, 0.96), (0.6, 0.96))]
    L["t"] = [chain(line((0.18, 1.28), (0.18, 0.26)), bez((0.18, 0.26), (0.18, -0.02), (0.46, -0.04), (0.7, 0.1))),
              line((-0.08, 0.96), (0.64, 0.96))]
    L["s"] = [chain(bez((0.5, 0.99), (0.16, 1.02), (0.02, 0.88), (0.06, 0.72)), bez((0.06, 0.72), (0.12, 0.52), (0.62, 0.5), (0.64, 0.26)),
                    bez((0.64, 0.26), (0.65, 0.06), (0.52, 0.0), (0.34, 0.0))),
              chain(line((0.5, 0.99), (0.64, 0.96)), line((0.64, 0.96), (0.65, 0.88))),
              bez((0.0, 0.14), (0.08, 0.02), (0.2, -0.005), (0.32, 0.0))]
    # -- diagonals: the thick strokes down to the right, the thin ones down to the left from a curled head
    L["v"] = [chain(bez((-0.08, 0.92), (-0.04, 0.98), (0.0, 1.0), (0.04, 0.97)), line((0.04, 0.97), (0.42, 0.0))),
              chain(bez((0.74, 0.9), (0.78, 1.02), (0.9, 1.04), (0.9, 0.92)), line((0.9, 0.92), (0.44, 0.0)))]
    L["w"] = [chain(bez((-0.08, 0.92), (-0.04, 0.98), (0.0, 1.0), (0.04, 0.97)), line((0.04, 0.97), (0.36, 0.0))),
              line((0.7, 0.98), (0.38, 0.02)),
              line((0.73, 0.98), (1.05, 0.0)),
              chain(bez((1.36, 0.9), (1.4, 1.02), (1.52, 1.04), (1.52, 0.92)), line((1.52, 0.92), (1.07, 0.0)))]
    L["x"] = [chain(bez((-0.06, 0.92), (-0.02, 0.98), (0.02, 1.0), (0.06, 0.96)), line((0.06, 0.96), (0.62, 0.1)),
                    bez((0.62, 0.1), (0.68, 0.02), (0.74, 0.0), (0.82, 0.03), 8)),
              chain(line((0.0, 0.02), (0.74, 0.96)), line((0.74, 0.96), (0.86, 1.0)))]
    L["y"] = [chain(bez((-0.08, 0.92), (-0.04, 0.98), (0.0, 1.0), (0.04, 0.97)), line((0.04, 0.97), (0.46, 0.06))),
              chain(bez((0.76, 0.9), (0.8, 1.02), (0.92, 1.04), (0.92, 0.92)), line((0.92, 0.92), (0.46, -0.1)),
                    bez((0.46, -0.1), (0.38, -0.28), (0.34, -0.42), (0.34, -0.56)))]
    L["z"] = [chain(line((0.06, 0.94), (0.08, 1.0)), line((0.08, 1.0), (0.76, 1.0))),
              line((0.76, 1.0), (0.02, 0.0)),
              chain(line((0.02, 0.0), (0.8, 0.0)), line((0.8, 0.0), (0.82, 0.07)))]
    return L


# ---- capitals: Roman proportions written with the same pen (unit = capital height, scaled by CAP) ----------------------
# Johnston's groups: round O Q C G D; wide M W; medium H A N T U V X Y Z (about 4/5); narrow B E F L P R S K (half).
def _c_serif(u, top=1.0):
    return bez((u - 0.1, top - 0.03), (u - 0.07, top - 0.06), (u - 0.035, top - 0.09), (u - 0.004, top - 0.12), 6)


def _c_foot(u, out=0.12):
    return bez((u, 0.11), (u, 0.02), (u + 0.035, -0.008), (u + out, 0.03), 8)


def _c_stem(u, ft=True):
    return chain(line((u, 1.0), (u, 0.11 if ft else 0.0)), *([_c_foot(u)] if ft else []))


def _capitals():
    L = {}
    L["O"] = [arc(0.5, 0.5, 0.5, 0.5, 115, 300), arc(0.5, 0.5, 0.5, 0.5, 115, -60)]
    L["Q"] = [arc(0.5, 0.5, 0.5, 0.5, 115, 300), arc(0.5, 0.5, 0.5, 0.5, 115, -60),
              bez((0.5, 0.02), (0.66, -0.1), (0.9, -0.12), (1.1, -0.2))]
    L["C"] = [arc(0.48, 0.5, 0.48, 0.5, 105, 315), chain(arc(0.48, 0.5, 0.48, 0.5, 105, 40), line((0.848, 0.82), (0.86, 0.72)))]
    L["G"] = [arc(0.48, 0.5, 0.48, 0.5, 105, 318), chain(arc(0.48, 0.5, 0.48, 0.5, 105, 40), line((0.848, 0.82), (0.86, 0.72))),
              chain(line((0.66, 0.44), (0.9, 0.44)), line((0.9, 0.44), (0.9, 0.06)))]
    L["D"] = [_c_stem(0, ft=False),
              chain(line((0.0, 1.0), (0.36, 1.0)), bez((0.36, 1.0), (0.98, 1.0), (0.98, 0.0), (0.36, 0.0)), line((0.36, 0.0), (0.0, 0.0))),
              _c_serif(0)]
    L["M"] = [line((0.06, 1.0), (-0.02, 0.0)), line((0.08, 1.0), (0.52, 0.02)), line((0.96, 1.0), (0.54, 0.02)),
              chain(line((0.97, 1.0), (1.04, 0.11)), _c_foot(1.04, 0.1))]
    L["W"] = [line((0.0, 1.0), (0.32, 0.0)), line((0.64, 1.0), (0.33, 0.02)), line((0.66, 1.0), (0.98, 0.0)), line((1.3, 1.0), (0.99, 0.02))]
    L["H"] = [_c_stem(0), _c_stem(0.78), line((0.0, 0.52), (0.78, 0.52)), _c_serif(0), _c_serif(0.78)]
    L["A"] = [line((0.44, 1.0), (0.0, 0.0)), chain(line((0.46, 1.0), (0.84, 0.1)), _c_foot(0.84, 0.1)), line((0.18, 0.36), (0.68, 0.36))]
    L["N"] = [line((0.0, 1.0), (0.0, 0.0)), line((0.02, 1.0), (0.76, 0.0)), line((0.78, 1.0), (0.78, 0.02)), _c_serif(0)]
    L["T"] = [chain(line((0.0, 0.92), (0.01, 1.0)), line((0.01, 1.0), (0.8, 1.0)), line((0.8, 1.0), (0.81, 0.92))), _c_stem(0.405)]
    L["U"] = [chain(line((0.0, 1.0), (0.0, 0.32)), bez((0.0, 0.32), (0.0, -0.06), (0.62, -0.08), (0.74, 0.3))), _c_stem(0.78),
              _c_serif(0), _c_serif(0.78)]
    L["V"] = [line((0.0, 1.0), (0.41, 0.0)), line((0.84, 1.0), (0.43, 0.02))]
    L["X"] = [chain(line((0.02, 1.0), (0.72, 0.1)), bez((0.72, 0.1), (0.75, 0.02), (0.79, 0.0), (0.86, 0.02), 8)), line((0.76, 1.0), (0.04, 0.0))]
    L["Y"] = [line((0.0, 1.0), (0.4, 0.5)), line((0.8, 1.0), (0.41, 0.49)), chain(line((0.405, 0.48), (0.405, 0.11)), _c_foot(0.405))]
    L["Z"] = [chain(line((0.04, 0.92), (0.05, 1.0)), line((0.05, 1.0), (0.74, 1.0))), line((0.74, 1.0), (0.0, 0.0)),
              chain(line((0.0, 0.0), (0.76, 0.0)), line((0.76, 0.0), (0.77, 0.09)))]
    L["B"] = [_c_stem(0, ft=False),
              chain(line((0.0, 1.0), (0.26, 1.0)), bez((0.26, 1.0), (0.52, 1.0), (0.52, 0.54), (0.26, 0.54)), line((0.26, 0.54), (0.02, 0.54))),
              chain(line((0.02, 0.54), (0.3, 0.54)), bez((0.3, 0.54), (0.6, 0.54), (0.6, 0.0), (0.3, 0.0)), line((0.3, 0.0), (0.0, 0.0))),
              _c_serif(0)]
    L["E"] = [_c_stem(0, ft=False), chain(line((0.0, 1.0), (0.46, 1.0)), line((0.46, 1.0), (0.47, 0.91))),
              line((0.0, 0.53), (0.4, 0.53)), chain(line((0.0, 0.0), (0.5, 0.0)), line((0.5, 0.0), (0.51, 0.1))), _c_serif(0)]
    L["F"] = [_c_stem(0), chain(line((0.0, 1.0), (0.48, 1.0)), line((0.48, 1.0), (0.49, 0.91))), line((0.0, 0.5), (0.4, 0.5)),
              _c_serif(0)]
    L["L"] = [_c_stem(0, ft=False), chain(line((0.0, 0.0), (0.5, 0.0)), line((0.5, 0.0), (0.51, 0.11))), _c_serif(0)]
    L["P"] = [_c_stem(0), chain(line((0.0, 1.0), (0.28, 1.0)), bez((0.28, 1.0), (0.58, 1.0), (0.58, 0.46), (0.28, 0.46)),
                                line((0.28, 0.46), (0.02, 0.46))), _c_serif(0)]
    L["R"] = [_c_stem(0), chain(line((0.0, 1.0), (0.27, 1.0)), bez((0.27, 1.0), (0.55, 1.0), (0.55, 0.49), (0.27, 0.49)),
                                line((0.27, 0.49), (0.02, 0.49))),
              chain(line((0.22, 0.47), (0.56, 0.08)), bez((0.56, 0.08), (0.61, 0.02), (0.66, 0.0), (0.74, 0.02), 8)), _c_serif(0)]
    L["S"] = [chain(bez((0.46, 0.93), (0.36, 1.02), (0.02, 1.02), (0.04, 0.76)), bez((0.04, 0.76), (0.06, 0.54), (0.5, 0.5), (0.51, 0.26)),
                    bez((0.51, 0.26), (0.52, -0.02), (0.12, -0.04), (0.0, 0.1)))]
    L["K"] = [_c_stem(0), line((0.6, 1.0), (0.03, 0.46)), chain(line((0.2, 0.62), (0.6, 0.1)), bez((0.6, 0.1), (0.64, 0.02), (0.68, 0.0), (0.75, 0.02), 8)), _c_serif(0)]
    L["I"] = [_c_stem(0), _c_serif(0)]
    L["J"] = [chain(line((0.3, 1.0), (0.3, 0.05)), bez((0.3, 0.05), (0.3, -0.18), (0.1, -0.25), (-0.04, -0.2))), _c_serif(0.3)]
    return L


# ---- figures: old-style, as Johnston wrote them with this hand -----------------------------------------------------------
# 0 1 2 at x-height, 6 8 rising to the capitals' height, 3 4 5 7 9 hanging to the descender; authored in a box 1 high
def _figures():
    F = {}
    F["0"] = [arc(0.4, 0.5, 0.4, 0.5, 115, 300), arc(0.4, 0.5, 0.4, 0.5, 115, -60)]
    F["1"] = [chain(line((0.12, 0.8), (0.32, 1.0)), line((0.32, 1.0), (0.32, 0.14)), foot(0.32, 0.14))]
    F["2"] = [chain(bez((0.04, 0.72), (0.08, 1.04), (0.66, 1.06), (0.66, 0.66)), bez((0.66, 0.66), (0.66, 0.4), (0.2, 0.22), (0.0, 0.0)),
                    line((0.0, 0.0), (0.7, 0.0)), line((0.7, 0.0), (0.72, 0.1)))]
    F["3"] = [chain(bez((0.06, 0.86), (0.14, 1.02), (0.6, 1.04), (0.6, 0.78)), bez((0.6, 0.78), (0.6, 0.6), (0.42, 0.56), (0.26, 0.56))),
              chain(bez((0.26, 0.54), (0.6, 0.54), (0.68, 0.34), (0.68, 0.26)), bez((0.68, 0.26), (0.66, 0.0), (0.14, -0.04), (0.0, 0.12)))]
    F["4"] = [chain(line((0.5, 1.0), (0.0, 0.32)), line((0.0, 0.32), (0.74, 0.32))), chain(line((0.54, 0.7), (0.54, 0.12)), foot(0.54, 0.12))]
    F["5"] = [chain(line((0.12, 1.0), (0.08, 0.56)), bez((0.08, 0.56), (0.24, 0.66), (0.68, 0.64), (0.68, 0.32)),
                    bez((0.68, 0.32), (0.68, 0.0), (0.14, -0.04), (0.0, 0.12))),
              line((0.12, 1.0), (0.64, 1.0))]
    F["6"] = [chain(bez((0.6, 0.94), (0.46, 1.04), (0.06, 1.0), (0.04, 0.5)), bez((0.04, 0.5), (0.02, 0.06), (0.22, 0.0), (0.36, 0.0)),
                    bez((0.36, 0.0), (0.62, 0.0), (0.7, 0.18), (0.7, 0.3)), bez((0.7, 0.3), (0.7, 0.54), (0.42, 0.62), (0.24, 0.58)),
                    bez((0.24, 0.58), (0.14, 0.56), (0.08, 0.5), (0.05, 0.42)))]
    F["7"] = [chain(line((0.02, 0.9), (0.03, 1.0)), line((0.03, 1.0), (0.7, 1.0)), bez((0.7, 1.0), (0.5, 0.72), (0.34, 0.4), (0.28, 0.0)))]
    F["8"] = [chain(bez((0.36, 1.0), (0.1, 1.0), (0.06, 0.84), (0.1, 0.74)), bez((0.1, 0.74), (0.18, 0.58), (0.7, 0.52), (0.7, 0.26)),
                    bez((0.7, 0.26), (0.7, 0.02), (0.46, 0.0), (0.36, 0.0)), bez((0.36, 0.0), (0.08, 0.0), (0.0, 0.16), (0.02, 0.28)),
                    bez((0.02, 0.28), (0.04, 0.46), (0.5, 0.55), (0.58, 0.7)), bez((0.58, 0.7), (0.66, 0.86), (0.56, 1.0), (0.34, 1.0)))]
    F["9"] = [chain(bez((0.38, 1.0), (0.12, 1.0), (0.04, 0.85), (0.04, 0.7)), bez((0.04, 0.7), (0.04, 0.46), (0.32, 0.38), (0.64, 0.52))),
              chain(bez((0.38, 1.0), (0.6, 1.0), (0.68, 0.86), (0.68, 0.64)), bez((0.68, 0.64), (0.68, 0.2), (0.5, 0.0), (0.24, 0.0)),
                    bez((0.24, 0.0), (0.12, 0.0), (0.05, 0.03), (0.0, 0.1)))]
    return F


FIG_BOX = {"0": (0, 1), "1": (0, 1), "2": (0, 1), "6": (0, CAP), "8": (0, CAP),
           "3": (DESC, 1), "4": (DESC, 1), "5": (DESC, 1), "7": (DESC, 1), "9": (DESC, 1)}


def letters():
    L = _small()
    L.update(scaled(_capitals(), CAP))
    for ch, strokes in _figures().items():
        b, t = FIG_BOX[ch]
        L[ch] = [[(u * 1.15, b + (t - b) * v) for u, v in st] for st in strokes]
    return L


HAND = dict(
    id="foundational", name="Foundational", family="foundational", variant=None, pen="broad", S=39, base=68, slant_deg=0,
    ext=(ASC, -DESC), start="onadbcehi", sample="Hand", keys="onad", nib_angle=30, nib=10.5, hair=1.0, dot_w=6.0, cap=CAP,
    about={
        "tool": "A broad-edged pen held at a constant 30°. Some teachers flatten the pen for the thick diagonal of z and "
                "steepen it a little for v, w, x, y; here it stays at 30°, so z's diagonal comes out thin.",
        "slant": "Upright.",
        "proportions": "x-height about 4 nib widths; ascenders and descenders half an x-height more (taller in "
                       "Johnston's own scheme, 7 nib widths to the ascender). Capitals 1.4 x-heights, below the ascenders.",
        "features": "The o is a circle and the key to the hand: the arches of n, m, h and r spring from high on the stem and "
                    "follow its curve; b, d, p, q and c, e share its bowl. Wedge-shaped heads added after the stem, small "
                    "feet turning out to the right; a thin rising bar in e; a two-storey g; thick diagonals down to the "
                    "right, thin ones from a curled head. The capitals are Roman in proportion, written with the same pen; "
                    "the figures are old-style (0 1 2 at x-height, 6 8 rising, 3 4 5 7 9 hanging).",
        "history": "Created by Edward Johnston in the early 20th century from a 10th-century English Carolingian minuscule "
                   "(the Ramsey Psalter, British Library Harley MS 2904); a teaching hand, made popular by his pupils."})
