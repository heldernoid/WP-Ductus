"""Roman Capitals (Capitalis monumentalis), written with a broad pen, after the inscriptions of imperial Rome.

Measured on the sheet "La capital romana" (letters made after a flat-brush model; px of that sheet, ink):

  capital height       148 px (H, I, N); skeleton (pen centre) 141 px = 1 unit; J falls 0.14 below, Q's tail 0.4
  stem                 13-14 px across (H, I, L, T); arms and serifs 6-8 px tall; thin stems of N, M 8-9 px
  nib                  stems 13.5 / arms 7 -> a nib of 15 px held at about 27 deg; capital height 9.7 nib widths
  slant                0
  widths (skeleton, incl. serifs, / capital height)
                       O .94 (151 tall: a circle)  C .83  D .95  G .88  Q 2.2 with its tail
                       H .97  N .97  A 1.0  K .97  U .94  V 1.06  T .80  X .76  Y .83  Z .67  R .92
                       B .57  E .63  F .50  L .58  P .57  S .45  I .2  J .27
                       M 1.26  W 1.5 (its middle strokes cross)
"""
from gen.pen import arc, bez, chain, dot, line  # noqa: F401

SER = 0.09                       # a serif's reach either side of the stem


# ---- the pen's parts --------------------------------------------------------------------------------------------------
# Serifs are short flat hairlines written left to right: the top serif before its stem, the foot serif after it.
def top(u, v=1.0, l=SER, r=SER):
    return line((u - l, v), (u + r, v))


def base(u, l=SER, r=SER):
    return line((u - l, 0.0), (u + r, 0.0))


def stem(u, v0=1.0, v1=0.0):
    return line((u, v0), (u, v1))


def pillar(u, t=True, b=True, l=SER, r=SER):
    """a stem with its top serif (written first) and its foot serif (last)"""
    return ([top(u, 1.0, l, r)] if t else []) + [stem(u)] + ([base(u, l, r)] if b else [])


def lead(u, v=1.0, l=SER):
    """a stem begun with a short flat serif to its left only (B, D, E, P, R: the bowl or arm is the right side)"""
    return chain(line((u - l, v), (u, v)), line((u, v), (u, 0.0)))


def _capitals():
    L = {}
    # -- round letters: two strokes from the thin at the upper left (the pen's angle), left side first
    L["O"] = [arc(0.47, 0.5, 0.47, 0.515, 117, 297), arc(0.47, 0.5, 0.47, 0.515, 117, -63)]
    L["Q"] = [arc(0.47, 0.5, 0.47, 0.515, 117, 297), arc(0.47, 0.5, 0.47, 0.515, 117, -63),
              bez((0.4, -0.01), (0.7, -0.16), (1.3, -0.34), (2.0, -0.2))]                  # the long tail, last
    L["C"] = [arc(0.47, 0.5, 0.47, 0.515, 100, 312),
              chain(arc(0.47, 0.5, 0.47, 0.515, 100, 44), line((0.808, 0.858), (0.82, 0.72)))]
    L["G"] = [arc(0.47, 0.5, 0.47, 0.515, 100, 302),
              chain(arc(0.47, 0.5, 0.47, 0.515, 100, 44), line((0.808, 0.858), (0.82, 0.72))),
              top(0.86, 0.46, 0.09, 0.06), chain(line((0.86, 0.46), (0.86, 0.12)), line((0.86, 0.12), (0.84, 0.0)))]
    L["D"] = [lead(0),
              chain(line((0.0, 1.0), (0.4, 1.0)), bez((0.4, 1.0), (1.03, 1.0), (1.03, 0.0), (0.4, 0.0)), line((0.4, 0.0), (-SER, 0.0)))]
    # -- wide letters
    L["M"] = [chain(line((0.07, 1.0), (0.13, 1.0)), line((0.13, 1.0), (0.04, 0.0))),          # thin leg from the apex serif
              line((0.14, 1.0), (0.58, 0.0)),                                                  # thick diagonal
              line((1.04, 1.0), (0.6, 0.0)),                                                   # thin diagonal
              chain(line((1.05, 1.0), (1.14, 1.0)), line((1.14, 1.0), (1.11, 0.0))),
              base(0.04, 0.09, 0.08), base(1.11, 0.08, 0.1)]
    L["W"] = [top(0.0), line((0.0, 1.0), (0.34, 0.0)),
              top(0.71, 1.0, 0.08, 0.08), line((0.71, 1.0), (0.35, 0.0)),                     # thin, crossing the next
              line((0.56, 1.0), (0.98, 0.0)),
              top(1.32), line((1.32, 1.0), (0.99, 0.0))]
    # -- medium letters
    L["H"] = pillar(0) + pillar(0.78) + [line((0.0, 0.55), (0.78, 0.55))]
    L["A"] = [chain(line((0.39, 1.0), (0.47, 1.0)), line((0.47, 1.0), (0.06, 0.0))),          # thin leg from the apex
              line((0.48, 1.0), (0.89, 0.0)),                                                  # thick leg
              line((0.24, 0.31), (0.73, 0.31)), base(0.06, 0.09, 0.08), base(0.89, 0.09, 0.1)]
    L["N"] = [line((0.0, 1.0), (0.0, 0.0)), base(0.0),                                       # thin stem, then its foot
              line((0.01, 1.0), (0.8, 0.0)),                                                   # thick diagonal
              top(0.8), line((0.8, 1.0), (0.8, 0.01))]
    L["T"] = [chain(line((0.0, 0.89), (0.01, 1.0)), line((0.01, 1.0), (0.79, 1.0)), line((0.79, 1.0), (0.8, 0.89))),
              stem(0.4, 1.0), base(0.4)]
    L["U"] = [top(0.0), chain(line((0.0, 1.0), (0.0, 0.3)), bez((0.0, 0.3), (0.0, -0.06), (0.6, -0.08), (0.74, 0.22))),
              top(0.76, 1.0, 0.07, 0.07), chain(line((0.76, 1.0), (0.76, 0.0)), line((0.76, 0.0), (0.85, 0.0)))]
    L["V"] = [top(0.0), line((0.0, 1.0), (0.43, 0.0)), top(0.86, 1.0, 0.08, 0.08), line((0.86, 1.0), (0.44, 0.02))]
    L["X"] = [top(0.02, 1.0, 0.08, 0.08), line((0.02, 1.0), (0.62, 0.0)), base(0.62, 0.08, 0.08),
              top(0.6, 1.0, 0.07, 0.07), line((0.6, 1.0), (0.04, 0.0)), base(0.04, 0.08, 0.07)]
    L["Y"] = [top(0.0, 1.0, 0.08, 0.08), line((0.0, 1.0), (0.38, 0.5)),
              top(0.76, 1.0, 0.07, 0.07), line((0.76, 1.0), (0.39, 0.49)),
              stem(0.385, 0.48), base(0.385)]
    L["Z"] = [chain(line((0.04, 0.88), (0.05, 1.0)), line((0.05, 1.0), (0.62, 1.0))), line((0.62, 1.0), (0.0, 0.0)),
              chain(line((0.0, 0.0), (0.66, 0.0)), line((0.66, 0.0), (0.68, 0.13)))]
    L["K"] = pillar(0) + [top(0.72, 1.0, 0.08, 0.08), line((0.72, 1.0), (0.03, 0.47)),
                          chain(line((0.16, 0.57), (0.7, 0.03)), line((0.7, 0.03), (0.88, -0.01)))]
    # -- narrow letters
    L["B"] = [lead(0),
              chain(line((0.0, 1.0), (0.22, 1.0)), bez((0.22, 1.0), (0.48, 1.0), (0.48, 0.55), (0.22, 0.55)), line((0.22, 0.55), (0.02, 0.55))),
              chain(line((0.02, 0.55), (0.26, 0.55)), bez((0.26, 0.55), (0.58, 0.55), (0.58, 0.0), (0.26, 0.0)), line((0.26, 0.0), (-SER, 0.0)))]
    L["E"] = [lead(0), chain(line((0.0, 1.0), (0.46, 1.0)), line((0.46, 1.0), (0.47, 0.89))),
              chain(line((0.0, 0.53), (0.38, 0.53)), line((0.38, 0.53), (0.385, 0.47))),
              chain(line((-SER, 0.0), (0.53, 0.0)), line((0.53, 0.0), (0.55, 0.14)))]
    L["F"] = [lead(0), base(0), chain(line((0.0, 1.0), (0.44, 1.0)), line((0.44, 1.0), (0.45, 0.89))),
              chain(line((0.0, 0.5), (0.36, 0.5)), line((0.36, 0.5), (0.365, 0.44)))]
    L["L"] = [top(0), stem(0), chain(line((-SER, 0.0), (0.47, 0.0)), line((0.47, 0.0), (0.49, 0.15)))]
    L["P"] = [lead(0), base(0),
              chain(line((0.0, 1.0), (0.2, 1.0)), bez((0.2, 1.0), (0.54, 1.0), (0.54, 0.44), (0.2, 0.44)), line((0.2, 0.44), (0.07, 0.45)))]
    L["R"] = [lead(0), base(0),
              chain(line((0.0, 1.0), (0.2, 1.0)), bez((0.2, 1.0), (0.56, 1.0), (0.56, 0.49), (0.2, 0.49)), line((0.2, 0.49), (0.02, 0.49))),
              chain(line((0.22, 0.47), (0.64, 0.07)), bez((0.64, 0.07), (0.72, 0.0), (0.82, -0.01), (0.94, 0.01), 8))]   # the leg
    L["S"] = [chain(bez((0.4, 0.92), (0.32, 1.02), (0.02, 1.02), (0.03, 0.77)), bez((0.03, 0.77), (0.04, 0.56), (0.44, 0.48), (0.45, 0.25)),
                    bez((0.45, 0.25), (0.46, 0.0), (0.12, -0.04), (0.02, 0.06)), line((0.02, 0.06), (0.0, 0.18))),
              chain(line((0.4, 0.92), (0.41, 0.8)))]
    # -- stems
    L["I"] = pillar(0)
    L["J"] = [top(0.12, 1.0, 0.08, 0.08), chain(line((0.12, 1.0), (0.12, 0.06)), bez((0.12, 0.06), (0.12, -0.08), (0.04, -0.13), (-0.1, -0.14)))]
    return L


# ---- figures: the Romans wrote numbers with letters (I V X L C D M); these are lining figures in the capitals' style
def _figures():
    F = {}
    F["0"] = [arc(0.3, 0.5, 0.3, 0.5, 117, 297), arc(0.3, 0.5, 0.3, 0.5, 117, -63)]
    F["1"] = [chain(line((0.12, 0.84), (0.3, 1.0)), line((0.3, 1.0), (0.3, 0.0))), base(0.3, 0.1, 0.1)]
    F["2"] = [chain(bez((0.03, 0.8), (0.07, 1.03), (0.54, 1.04), (0.54, 0.72)), bez((0.54, 0.72), (0.54, 0.5), (0.22, 0.3), (0.0, 0.0)),
                    line((0.0, 0.0), (0.6, 0.0)), line((0.6, 0.0), (0.61, 0.11)))]
    F["3"] = [chain(bez((0.04, 0.86), (0.12, 1.02), (0.5, 1.04), (0.49, 0.78)), bez((0.49, 0.78), (0.48, 0.6), (0.32, 0.56), (0.22, 0.56))),
              chain(bez((0.21, 0.54), (0.52, 0.54), (0.59, 0.34), (0.58, 0.25)), bez((0.58, 0.25), (0.56, 0.0), (0.12, -0.04), (0.0, 0.1)))]
    F["4"] = [chain(line((0.44, 1.0), (0.0, 0.3)), line((0.0, 0.3), (0.62, 0.3))), stem(0.45, 0.72), base(0.45, 0.1, 0.1)]
    F["5"] = [chain(line((0.1, 1.0), (0.07, 0.56)), bez((0.07, 0.56), (0.22, 0.64), (0.58, 0.63), (0.57, 0.32)),
                    bez((0.57, 0.32), (0.56, 0.0), (0.12, -0.04), (0.0, 0.1))),
              chain(line((0.1, 1.0), (0.52, 1.0)), line((0.52, 1.0), (0.53, 0.92)))]
    F["6"] = [chain(bez((0.54, 0.92), (0.43, 1.03), (0.06, 1.02), (0.03, 0.55)), bez((0.03, 0.55), (0.0, 0.05), (0.2, 0.0), (0.3, 0.0)),
                    bez((0.3, 0.0), (0.54, 0.0), (0.59, 0.2), (0.58, 0.3)), bez((0.58, 0.3), (0.57, 0.55), (0.32, 0.62), (0.22, 0.6)),
                    bez((0.22, 0.6), (0.12, 0.58), (0.06, 0.52), (0.04, 0.44)))]
    F["7"] = [chain(line((0.0, 0.9), (0.01, 1.0)), line((0.01, 1.0), (0.58, 1.0)), bez((0.58, 1.0), (0.42, 0.75), (0.27, 0.4), (0.22, 0.0)))]
    F["8"] = [chain(bez((0.3, 1.0), (0.08, 1.0), (0.04, 0.84), (0.08, 0.75)), bez((0.08, 0.75), (0.14, 0.6), (0.59, 0.52), (0.59, 0.26)),
                    bez((0.59, 0.26), (0.59, 0.02), (0.38, 0.0), (0.3, 0.0)), bez((0.3, 0.0), (0.06, 0.0), (0.0, 0.16), (0.02, 0.28)),
                    bez((0.02, 0.28), (0.04, 0.46), (0.43, 0.55), (0.49, 0.7)), bez((0.49, 0.7), (0.55, 0.86), (0.47, 1.0), (0.29, 1.0)))]
    F["9"] = [chain(bez((0.32, 1.0), (0.1, 1.0), (0.03, 0.85), (0.03, 0.72)), bez((0.03, 0.72), (0.03, 0.5), (0.26, 0.4), (0.54, 0.52))),
              chain(bez((0.32, 1.0), (0.52, 1.0), (0.58, 0.86), (0.58, 0.66)), bez((0.58, 0.66), (0.58, 0.2), (0.42, 0.0), (0.2, 0.0)),
                    bez((0.2, 0.0), (0.1, 0.0), (0.04, 0.03), (0.0, 0.1)))]
    return F


def letters():
    L = _capitals()
    L.update(_figures())
    return L


HAND = dict(
    id="roman", name="Roman Capitals", family="roman", variant="Capitalis", pen="broad", S=42, base=63, slant_deg=0,
    ext=(1.0, 0.3), start="OILTHEN", sample="ROMA", keys="OMRS", nib_angle=27, nib=4.5, hair=1.0, dot_w=4.5, cap=1.0,
    unicase=True,
    about={
        "tool": "A broad-edged pen (the models were laid out with a flat brush) held at about 27° throughout, the angle "
                "that tilts the O's stress back and makes the diagonals thick going down to the right and thin going "
                "down to the left. Scribes steepen the pen for the thin stems of N and M and flatten it for Z's "
                "diagonal; here the angle stays fixed, so those strokes come out heavier (N, M) or lighter (Z) than on "
                "the sheet.",
        "slant": "Upright.",
        "proportions": "Capital height about 9½ nib widths; stems about a tenth of the height. Classical widths: O, Q, C, "
                       "G, D round, about as wide as high; M and W wide (W's middle strokes cross); H, A, N, K, U, V "
                       "about as wide as high with their serifs, T, X, Y four fifths; B, E, F, L, P, R, S about half.",
        "features": "Flat hairline serifs either side of the stems, written as short strokes (the top serif before its "
                    "stem, the foot serif after); arms end in a short tick. Pointed apexes in A, M, N and V; P's bowl "
                    "left open; R's leg and Q's very long tail sweep out past the letter. Stems pulled top-down, the "
                    "round letters in two strokes from the top. Capitals only.",
        "history": "The inscriptional capitals of imperial Rome (the Trajan column, AD 113, and stones such as Nero's in "
                   "Cologne, AD 67), painted with a flat brush before they were cut; Edward Johnston's broad-pen study "
                   "of them is how they are taught today. The Romans had no J, U or W, and no figures but letters: those "
                   "forms follow the same proportions."})
