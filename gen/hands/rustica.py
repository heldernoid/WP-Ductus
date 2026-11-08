"""Rustic Capitals (Capitalis rustica), after the 5th-century Codex Palatinus as taught on the sheet "La Rustica".

Measured on that sheet (px of the sheet, ink; the 1st-century row for comparison):

                       5th century (with ductus)       1st century
  capital height       50 px (I, L, T; head to foot)   40 px
  ascending letters    B 1.22, F 1.12, H 1.12, L 1.08, E's arm 1.1 (the sheet: B, F, L, Y pass the top line)
  stem                 3 px across                      2 px
  feet, arms           7 px tall                        8-9 px
  nib                  ~7.5 px; stems / feet = 3 / 7 -> the pen at about 67 deg (the sheet: 70 deg for the verticals,
                       45 deg for horizontals and curves); capital height 6.7 nib widths (the sheet: 6.5 to 7; the
                       1st century 6); skeleton (pen centre) 43 px = 1 unit
  slant                0 (stems upright; diagonals and curves lean)
  widths (skeleton, / capital height)  A .76  B .62  C .46  D .62  E .44  F .44  G .55  H 1.0  I .37  L .58  M 1.16
                       N .83  O .51  P .37  Q .83  R .81  S .53  T .44  V .9  X .86  Y 1.0  Z .69
"""
from gen.pen import arc, bez, chain, dot, line  # noqa: F401


# ---- the pen's parts ----------------------------------------------------------------------------------------------------
# With the steep pen a stem is a hairline and a foot or an arm is thick: the foot is its own stroke, written left to
# right across the stem's end (the sheet's "2"), its ends cut at the pen's angle.
def stem(u, top=1.0, bot=0.0):
    """a stem: a short hairline up to the right into its head, then pulled down"""
    return chain(line((u - 0.05, top - 0.1), (u, top)), line((u, top), (u, bot)))


def foot(u, l=0.12, r=0.16):
    """the thick foot across a stem's end, left to right, dipping a little at the end"""
    return bez((u - l, 0.015), (u - l / 3, 0.02), (u + r / 2, 0.0), (u + r, -0.02), 6)


def arm(u0, u1, v, rise=0.05):
    """a thick arm left to right with the rustic wave (down, up), ending a little higher"""
    w = u1 - u0
    return bez((u0, v - 0.01), (u0 + 0.35 * w, v - 0.06), (u0 + 0.6 * w, v + rise), (u1, v + rise), 10)


def hook(u, v=1.0):
    """the curled head of a thick diagonal (V, X, Y): in from the left, over, and down"""
    return bez((u - 0.07, v - 0.07), (u - 0.05, v + 0.01), (u + 0.02, v + 0.02), (u + 0.06, v - 0.05), 8)


def _capitals():
    L = {}
    # -- stems with feet and arms
    L["I"] = [stem(0.12), foot(0.12)]
    L["J"] = [chain(line((0.07, 0.9), (0.12, 1.0)), line((0.12, 1.0), (0.12, -0.12)), bez((0.12, -0.12), (0.12, -0.24), (0.04, -0.3), (-0.08, -0.3)))]
    L["L"] = [stem(0.1, 1.1), chain(arm(-0.02, 0.5, 0.0, 0.04), line((0.5, 0.04), (0.52, 0.12)))]
    L["T"] = [stem(0.22, 0.97), foot(0.22, 0.12, 0.14), arm(-0.02, 0.44, 0.98, 0.04)]
    L["E"] = [stem(0.1), foot(0.1, 0.12, 0.32), arm(0.1, 0.44, 1.04, 0.07), arm(0.1, 0.36, 0.55, 0.04)]
    L["F"] = [stem(0.1, 1.08), foot(0.1), arm(0.1, 0.46, 1.04, 0.07), arm(0.1, 0.38, 0.55, 0.04)]
    L["H"] = [stem(0.1, 1.12), foot(0.1, 0.12, 0.14),
              chain(line((0.8, 0.92), (0.85, 1.0)), bez((0.85, 1.0), (0.78, 0.7), (0.8, 0.3), (0.84, 0.02)), line((0.84, 0.02), (0.96, 0.0))),
              arm(-0.02, 0.84, 0.78, 0.04)]
    L["P"] = [stem(0.1, 1.08), foot(0.1, 0.12, 0.14),
              chain(bez((0.1, 1.08), (0.3, 1.1), (0.42, 1.0), (0.4, 0.86)), bez((0.4, 0.86), (0.38, 0.7), (0.24, 0.62), (0.12, 0.62)))]
    L["B"] = [stem(0.08, 1.22), foot(0.08, 0.12, 0.38),
              chain(bez((0.08, 1.22), (0.3, 1.24), (0.4, 1.08), (0.32, 0.92)), bez((0.32, 0.92), (0.26, 0.8), (0.16, 0.7), (0.1, 0.66))),
              bez((0.1, 0.66), (0.5, 0.62), (0.64, 0.3), (0.46, 0.03))]
    L["D"] = [stem(0.08), foot(0.08, 0.12, 0.26),
              chain(bez((0.08, 1.0), (0.3, 1.04), (0.5, 0.94), (0.58, 0.62)), bez((0.58, 0.62), (0.64, 0.34), (0.54, 0.12), (0.36, 0.02)))]
    L["R"] = [chain(line((0.07, 0.9), (0.12, 1.0)), line((0.12, 1.0), (0.12, 0.02)), line((0.12, 0.02), (-0.02, 0.0))),
              chain(bez((0.12, 1.0), (0.34, 1.04), (0.46, 0.92), (0.42, 0.78)), bez((0.42, 0.78), (0.38, 0.64), (0.24, 0.58), (0.14, 0.56))),
              chain(line((0.2, 0.56), (0.7, 0.04)), bez((0.7, 0.04), (0.73, 0.0), (0.77, -0.01), (0.82, 0.0), 6))]
    L["K"] = [chain(line((0.07, 0.98), (0.12, 1.08)), line((0.12, 1.08), (0.12, 0.02)), line((0.12, 0.02), (-0.02, 0.0))),
              chain(line((0.56, 0.96), (0.64, 1.02)), line((0.64, 1.02), (0.14, 0.5))),
              chain(line((0.2, 0.56), (0.66, 0.04)), bez((0.66, 0.04), (0.69, 0.0), (0.73, -0.01), (0.78, 0.0), 6))]
    # -- round letters: narrow, the back a hairline, the top and the foot thick
    L["O"] = [arc(0.26, 0.5, 0.26, 0.5, 100, 290), arc(0.26, 0.5, 0.26, 0.5, 100, -70)]
    L["Q"] = [arc(0.27, 0.5, 0.27, 0.5, 100, 290), arc(0.27, 0.5, 0.27, 0.5, 100, -70),
              chain(line((0.28, 0.02), (0.72, -0.18)), line((0.72, -0.18), (0.8, -0.2)))]
    L["C"] = [chain(bez((0.32, 0.98), (0.06, 0.96), (0.0, 0.66), (0.01, 0.42)), bez((0.01, 0.42), (0.02, 0.1), (0.2, -0.01), (0.44, 0.04))),
              arm(0.2, 0.46, 0.98, 0.0)]
    L["G"] = [chain(bez((0.32, 0.98), (0.06, 0.96), (0.0, 0.66), (0.01, 0.42)), bez((0.01, 0.42), (0.02, 0.1), (0.2, -0.01), (0.4, 0.03))),
              arm(0.2, 0.52, 0.98, 0.0),
              chain(line((0.32, 0.5), (0.48, 0.5)), bez((0.48, 0.5), (0.54, 0.38), (0.52, 0.18), (0.44, 0.04)))]
    L["S"] = [chain(bez((0.12, 0.96), (0.02, 0.84), (0.1, 0.66), (0.26, 0.52)), bez((0.26, 0.52), (0.44, 0.36), (0.5, 0.2), (0.4, 0.04))),
              foot(0.12, 0.14, 0.32),
              arm(0.12, 0.52, 0.96, 0.05)]
    L["U"] = [chain(hook(0.04), bez((0.1, 0.95), (0.08, 0.5), (0.02, 0.1), (0.3, 0.02)), bez((0.3, 0.02), (0.46, -0.02), (0.6, 0.1), (0.66, 0.3))),
              chain(line((0.66, 0.9), (0.72, 1.0)), line((0.72, 1.0), (0.72, 0.02)), line((0.72, 0.02), (0.84, 0.0)))]
    # -- diagonals: thick down to the right, hairlines down to the left
    L["A"] = [chain(line((0.36, 1.0), (0.1, 0.03)), line((0.1, 0.03), (-0.04, 0.0))),          # the thin leg, its foot to the left
              chain(line((0.28, 0.94), (0.37, 1.04)), line((0.37, 1.04), (0.66, 0.06)), bez((0.66, 0.06), (0.68, 0.0), (0.72, -0.01), (0.76, 0.0), 6))]
    L["V"] = [chain(hook(0.04), bez((0.1, 0.95), (0.2, 0.6), (0.4, 0.2), (0.5, 0.02))),
              chain(line((0.76, 0.98), (0.86, 1.02)), line((0.86, 1.02), (0.52, 0.04)))]
    L["N"] = [chain(line((0.0, 0.92), (0.04, 1.0)), line((0.04, 1.0), (0.02, 0.03)), line((0.02, 0.03), (-0.1, 0.0))),
              line((0.06, 1.0), (0.7, 0.02)),
              chain(line((0.68, 0.98), (0.74, 1.08)), line((0.74, 1.08), (0.72, 0.04)))]
    L["M"] = [chain(line((0.24, 0.94), (0.31, 1.02)), line((0.31, 1.02), (0.56, 0.04))),      # 1: the first thick diagonal
              chain(line((0.29, 0.98), (0.08, 0.03)), line((0.08, 0.03), (-0.06, 0.0))),      # 2: the thin leg, its foot
              line((0.82, 1.0), (0.58, 0.04)),                                                 # 3: the thin middle
              chain(line((0.84, 1.0), (1.04, 0.06)), bez((1.04, 0.06), (1.06, 0.0), (1.1, -0.01), (1.14, 0.0), 6))]
    L["W"] = [chain(hook(0.04), line((0.1, 0.95), (0.36, 0.02))), line((0.62, 1.0), (0.38, 0.04)),
              chain(line((0.6, 0.94), (0.66, 1.0)), line((0.66, 1.0), (0.94, 0.02))),
              chain(line((1.14, 0.98), (1.24, 1.02)), line((1.24, 1.02), (0.96, 0.04)))]
    L["X"] = [chain(hook(0.06), line((0.12, 0.95), (0.74, 0.04)), bez((0.74, 0.04), (0.76, 0.0), (0.8, -0.01), (0.84, 0.0), 6)),
              chain(line((0.7, 0.98), (0.8, 1.04)), line((0.8, 1.04), (0.44, 0.5))),
              chain(line((0.43, 0.48), (0.1, 0.03)), line((0.1, 0.03), (-0.02, 0.0)))]
    L["Y"] = [chain(hook(0.04), bez((0.1, 0.95), (0.2, 0.7), (0.4, 0.5), (0.48, 0.4)), line((0.48, 0.4), (0.48, 0.02))),
              foot(0.48, 0.14, 0.16),
              chain(line((0.9, 1.0), (1.0, 1.06)), bez((1.0, 1.06), (0.8, 0.96), (0.6, 0.7), (0.5, 0.46)))]
    L["Z"] = [arm(0.04, 0.62, 0.98, 0.04), line((0.6, 1.0), (0.04, 0.03)), arm(-0.02, 0.66, 0.0, 0.03)]
    return L


# ---- figures: the Romans wrote numbers with letters; these are calligraphers' figures in the Rustic manner (the steep
# pen: hairline uprights, thick tops and feet), at the capitals' height
def _figures():
    F = {}
    F["0"] = [arc(0.26, 0.5, 0.26, 0.5, 100, 290), arc(0.26, 0.5, 0.26, 0.5, 100, -70)]
    F["1"] = [chain(line((0.04, 0.84), (0.2, 1.0)), line((0.2, 1.0), (0.2, 0.0))), foot(0.2, 0.14, 0.16)]
    F["2"] = [chain(bez((0.04, 0.84), (0.1, 1.04), (0.46, 1.04), (0.46, 0.76)), bez((0.46, 0.76), (0.46, 0.5), (0.2, 0.26), (0.02, 0.02))),
              arm(0.0, 0.52, 0.0, 0.03)]
    F["3"] = [chain(arm(0.04, 0.44, 0.98, 0.02), line((0.44, 1.0), (0.2, 0.6))),
              bez((0.2, 0.6), (0.62, 0.6), (0.6, 0.0), (0.02, 0.04))]
    F["4"] = [chain(line((0.36, 1.0), (0.0, 0.32)), arm(0.0, 0.54, 0.32, 0.02)), line((0.4, 0.62), (0.4, 0.0)), foot(0.4, 0.12, 0.14)]
    F["5"] = [chain(line((0.08, 0.98), (0.06, 0.58)), bez((0.06, 0.58), (0.5, 0.66), (0.54, 0.2), (0.4, 0.08)), bez((0.4, 0.08), (0.28, -0.02), (0.1, 0.0), (0.0, 0.06))),
              arm(0.08, 0.5, 0.98, 0.04)]
    F["6"] = [chain(bez((0.42, 0.98), (0.1, 0.9), (0.0, 0.6), (0.02, 0.3)), bez((0.02, 0.3), (0.04, 0.0), (0.42, -0.04), (0.46, 0.24)),
                    bez((0.46, 0.24), (0.48, 0.5), (0.2, 0.56), (0.04, 0.42)))]
    F["7"] = [arm(0.0, 0.5, 0.98, 0.04), bez((0.5, 1.02), (0.38, 0.7), (0.24, 0.4), (0.16, 0.02))]
    F["8"] = [chain(bez((0.4, 0.94), (0.3, 1.04), (0.02, 1.0), (0.06, 0.78)), bez((0.06, 0.78), (0.1, 0.56), (0.48, 0.5), (0.48, 0.24)),
                    bez((0.48, 0.24), (0.48, -0.02), (0.06, -0.04), (0.02, 0.2)), bez((0.02, 0.2), (0.0, 0.42), (0.42, 0.6), (0.42, 0.8)))]
    F["9"] = [chain(bez((0.44, 0.6), (0.3, 0.44), (0.02, 0.5), (0.04, 0.76)), bez((0.04, 0.76), (0.06, 1.02), (0.44, 1.04), (0.46, 0.76)),
                    bez((0.46, 0.76), (0.48, 0.4), (0.3, 0.1), (0.04, 0.0)))]
    return F


def letters():
    L = _capitals()
    L.update(_figures())
    return L


HAND = dict(
    id="rustica", name="Rustic Capitals", family="roman", variant="Rustica", pen="broad", S=54, base=72, slant_deg=0,
    ext=(1.2, 0.3), start="ILTEFO", sample="ROMA", keys="AMRS", nib_angle=60, nib=10.0, hair=1.0, dot_w=6.0, cap=1.0,
    unicase=True,
    about={
        "tool": "A broad-edged pen held steeply, at 65° here: hairline stems, thick feet, arms and diagonals down to the "
                "right. The scribes turned the pen, about 70° for the uprights and 45° for horizontals and curves; with "
                "one angle per hand, 65° keeps the thin stems and thick feet that make the hand, so the curves of O, C, "
                "G and S are a little thinner than on the sheet.",
        "slant": "Upright stems; the curves and diagonals lean.",
        "proportions": "Capital height about 6½ to 7 nib widths (the 1st-century form about 6). Narrow letters: O, C, E, "
                       "F, P, T, S about half as wide as high, H, Y and M as wide as high or wider. B, F, H, L and the arms "
                       "of E and T rise above the top line.",
        "features": "Every stem begins with a hairline up into its head and ends on a thick wedge foot written as its own "
                    "stroke, left to right; arms are thick wavy strokes. A has no bar; thin legs end in a foot to the "
                    "left; thick diagonals end in a small turn. The Romans had no J, U, W or figures (numbers were "
                    "letters): those forms, and the figures, are written as calligraphers write them in the Rustic manner.",
        "history": "The everyday book and poster capital of Rome, from the 1st century (painted notices, papyri) to the "
                   "great Virgil manuscripts of the 4th and 5th centuries such as the Codex Palatinus; used later for "
                   "titles and headings."})
