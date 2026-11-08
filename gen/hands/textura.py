"""Blackletter: Textura Quadrata.

Measured on a Textura exemplar (the sheet with numbered ductus arrows), x-height 75.5 px there:

  x-height in nib widths    5.0   (stem 11.5 px wide = nib x cos 40°, so the nib is about 15 px)
  ascender / descender      1.38 / 0.35 x-heights (b, h, k, l; g, p, q, y)
  capital height            1.36 x-heights (the ascender line); T's top 1.52, Y and J descend 0.4-0.45
  stem pitch (n, m, u)      0.32-0.33 x-heights: the counter (0.17) equals the stem (0.15)
  widths (ink)              n 0.73, o 0.53, m 1.06, a 0.65; A 1.03, B 0.97, C 0.93, D 1.13, H 1.07, M 1.51,
                            N 1.15, O 0.90, T 1.23, W 1.38 x-heights
  slant                     0° (upright)
  nib angle                 about 40° (the hairline of e and the cut of the stem ends)

Forms and stroke order follow the sheet's numbered arrows. Every minim is a diamond head (a short stroke down to the
right, across the nib), the stem and a diamond foot; the second and third stems of n, m, u begin with their own
diamond right against the stem before. Round letters are a box: the left stem with its foot along the bottom
(rising as a hairline into the right side), then the roof, a heavy stroke down to the right from the top of the
left stem, and the right stem. The d's back is a curved ascender sweeping over the bowl; g and y close with a
heavy tail written from the left under the bent descender; the round s and the z are broken into a stem, a
diagonal and a tail. Capitals are as wide as they are tall or wider, built from the same strokes with the round
capitals' doubled stem (C, E, G, O, Q, T: a second thick stroke just inside the first, written after it), curved
lead-in roofs (D, K), the diagonal hairlines of B, E, G, K, R, Z, diamonds in the counters and thorns on the left
of the stems. Simplified: the long straight vertical hairlines that cross B, D, L, N, S and T (drawn with the
nib's corner) are left out, since a broad nib held at one angle draws every vertical at full width. The sheet has
no figures: these are written as Textura scribes wrote them, broken like the letters, at 1.2 x-heights.
The unit is the x-height.
"""
from gen.pen import bez, chain, line, poly

P = 0.33                                     # stem pitch of n, m, u (the counter equals the stem)
HD = (0.13, 0.16)                            # the diamond: a short stroke down to the right, about one nib long
FT = 0.21                                    # where a stem ends and turns into its foot


def head(u, top=1.0):
    """the diamond head: from just below the line, down to the right into the stem at u"""
    return line((u - HD[0], top - 0.05), (u, top - 0.05 - HD[1]))


def foot(u, b=FT):
    """the diamond foot: from the stem's end down to the right, to the baseline"""
    return line((u, b), (u + HD[0], b - HD[1]))


def minim(u, top=1.0, bot=FT, hd=True, ft=True):
    st = chain(head(u, top), line((u, top - 0.05 - HD[1]), (u, bot))) if hd else line((u, top), (u, bot))
    return chain(st, foot(u, bot)) if ft else st


def tall(u, top=1.31, bot=FT, ft=True):
    """an ascender stem: from its cut top straight down (b, h, k, l)"""
    st = line((u, top), (u, bot))
    return chain(st, foot(u, bot)) if ft else st


def bowl(w=0.30, top=0.9, rise=0.14):
    """the left of a round letter: the stem down, the foot, and a hairline rising into the right side"""
    return poly((0.0, top), (0.0, FT), (HD[0] + 0.02, 0.05), (w - 0.05, rise))


def roof(w=0.30, u0=0.05, top=0.95, drop=0.15):
    """the top of a round letter: from the top of the left stem down to the right"""
    return line((u0, top), (w, top - drop))


def _small():
    L = {}
    L["a"] = [poly((-0.02, 0.98), (0.0, FT), (0.15, 0.05), (0.26, 0.13)),
              chain(roof(0.32, 0.03, 1.0, 0.2), line((0.32, 0.8), (0.32, FT)), foot(0.32))]
    L["b"] = [chain(tall(0.0, 1.31, FT, False), line((0.0, FT), (0.15, 0.05)), line((0.15, 0.05), (0.26, 0.13))),
              chain(roof(0.32, 0.05, 0.93, 0.13), line((0.32, 0.8), (0.32, 0.22)))]
    L["c"] = [bowl(0.32, 0.9, 0.12), roof(0.3, 0.05, 0.95, 0.1)]
    L["d"] = [bowl(0.34),
              chain(bez((-0.16, 1.36), (0.08, 1.3), (0.34, 1.06), (0.34, 0.8)), line((0.34, 0.8), (0.34, 0.22)))]
    L["e"] = [bowl(0.34, 0.9, 0.12), poly((0.05, 0.95), (0.31, 0.84), (0.1, 0.66))]
    L["f"] = [tall(0.0, 1.27), line((0.06, 1.33), (0.31, 1.24)), line((-0.18, 0.88), (0.3, 0.88))]
    L["g"] = [bowl(),
              chain(roof(0.32), line((0.32, 0.8), (0.32, 0.12)), bez((0.32, 0.12), (0.32, 0.0), (0.42, -0.06), (0.42, -0.14)),
                    bez((0.42, -0.14), (0.42, -0.24), (0.36, -0.3), (0.3, -0.32))),
              bez((-0.16, -0.38), (-0.1, -0.16), (0.1, -0.14), (0.25, -0.3))]
    L["h"] = [tall(0.0), minim(P)]
    L["i"] = [minim(0.0), line((-0.06, 1.3), (0.04, 1.18))]
    L["j"] = [chain(head(0.0), poly((0.0, 0.79), (0.0, -0.1), (-0.06, -0.24), (-0.18, -0.36))),
              line((-0.06, 1.3), (0.04, 1.18))]
    L["k"] = [tall(0.0), poly((0.04, 0.8), (0.24, 0.7), (0.1, 0.58)), minim(0.3, 0.68)]
    L["l"] = [tall(0.0)]
    L["m"] = [minim(0.0), minim(P), minim(2 * P)]
    L["n"] = [minim(0.0), minim(P)]
    L["o"] = [bowl(), chain(roof(), line((0.3, 0.8), (0.3, 0.22)))]
    L["p"] = [chain(head(0.0), line((0.0, 0.79), (0.0, -0.3)), line((0.0, -0.3), (0.08, -0.38))),
              chain(roof(0.32, 0.06, 0.95, 0.15), poly((0.32, 0.8), (0.32, 0.22), (0.2, 0.06), (0.06, 0.06)))]
    L["q"] = [bowl(0.32, 0.9, 0.1), chain(roof(0.32), line((0.32, 0.8), (0.32, -0.36)))]
    L["r"] = [minim(0.0), roof(0.3, 0.05, 0.95, 0.1)]
    L["s"] = [poly((0.0, 0.9), (0.0, 0.62), (0.32, 0.42), (0.32, 0.2)), line((0.05, 0.95), (0.34, 0.86)),
              bez((-0.16, 0.08), (-0.1, 0.28), (0.12, 0.28), (0.28, 0.06))]
    L["t"] = [tall(0.0, 1.22), line((-0.15, 0.88), (0.24, 0.88))]
    L["u"] = [chain(minim(0.0, ft=False), line((0.0, FT), (0.15, 0.05)), line((0.15, 0.05), (0.24, 0.12))), minim(P)]
    L["v"] = [chain(minim(0.0, ft=False), line((0.0, FT), (0.15, 0.05)), line((0.15, 0.05), (0.28, 0.2))),
              chain(head(P), line((P, 0.79), (P, 0.3)))]
    L["w"] = [chain(minim(0.0, ft=False), line((0.0, FT), (0.15, 0.05)), line((0.15, 0.05), (0.24, 0.12))),
              chain(minim(P, ft=False), line((P, FT), (P + 0.15, 0.05)), line((P + 0.15, 0.05), (2 * P - 0.04, 0.2))),
              chain(head(2 * P), line((2 * P, 0.79), (2 * P, 0.3)))]
    L["x"] = [chain(head(0.0), poly((0.0, 0.79), (0.0, 0.2), (-0.16, -0.3))), poly((0.06, 0.8), (0.2, 0.98), (0.34, 0.86)),
              line((-0.14, 0.5), (0.18, 0.5)), poly((0.08, 0.42), (0.34, 0.16), (0.36, 0.04))]
    L["y"] = [chain(minim(0.0, ft=False), line((0.0, FT), (0.15, 0.05)), line((0.15, 0.05), (0.24, 0.12))),
              chain(head(P), line((P, 0.79), (P, 0.12)), bez((P, 0.12), (P, 0.0), (P + 0.1, -0.06), (P + 0.1, -0.14)),
                    bez((P + 0.1, -0.14), (P + 0.1, -0.24), (P + 0.04, -0.3), (P - 0.02, -0.32))),
              bez((-0.16, -0.38), (-0.1, -0.16), (0.1, -0.14), (P - 0.07, -0.3))]
    L["z"] = [poly((-0.02, 0.95), (0.26, 0.84), (0.04, 0.6)), chain(line((0.02, 0.62), (0.3, 0.5)), line((0.3, 0.5), (0.3, 0.22))),
              bez((-0.16, 0.06), (-0.1, 0.28), (0.1, 0.28), (0.25, 0.08))]
    return L


C = 1.36                                     # capital height (the ascender line)


def stem(u, top=1.22, bot=FT):
    return line((u, top), (u, bot))


def round_left(top=1.2, w=0.78, end=0.14):
    """the outer stroke of a round capital: the stem down, then the bottom swinging right and up"""
    return chain(line((0.0, top), (0.0, 0.38)), bez((0.0, 0.38), (0.0, 0.12), (0.16, 0.0), (0.38, 0.0)),
                 bez((0.38, 0.0), (0.54, 0.0), (w - 0.12, 0.04), (w, end)))


def double(u=0.25, top=1.24, bot=0.5):
    """the doubled stem of a round capital: a second stroke just inside the first, a few pixels clear of it"""
    return line((u, top), (u - 0.01, bot))


def cap_roof(u0, w, top=1.3):
    """the curved top of a round capital, from the doubled stem's head over to the right"""
    return bez((u0, top), (u0 + 0.14, top + 0.1), (w - 0.2, top + 0.08), (w, top + 0.02))


def thorn(u, v):
    """the small diamond on the left of a capital's stem"""
    return line((u - 0.2, v + 0.12), (u - 0.08, v - 0.02))


def diamond(u, v):
    return line((u - 0.05, v + 0.06), (u + 0.05, v - 0.06))


def _capitals():
    L = {}
    L["A"] = [poly((0.6, 1.2), (0.0, 0.16), (0.32, 0.04)),
              minim(0.76, C, hd=False),
              line((0.24, 0.5), (0.66, 0.5)),
              line((0.02, 1.32), (0.66, 1.36)),
              bez((-0.02, 1.24), (-0.08, 1.16), (-0.08, 1.06), (-0.04, 0.98))]
    L["B"] = [chain(line((-0.24, 1.3), (-0.02, 1.12)), line((0.0, 1.12), (0.0, 0.16))),
              line((-0.22, 0.08), (0.54, 0.02)),
              poly((0.07, 1.02), (0.32, 1.36), (0.54, 1.1), (0.38, 0.94)),
              chain(line((0.2, 0.84), (0.6, 0.84)), line((0.6, 0.84), (0.6, 0.12))),
              diamond(0.3, 0.52), thorn(0.0, 0.66)]
    L["C"] = [round_left(1.2, 0.8), double(), cap_roof(0.27, 0.82)]
    L["D"] = [stem(0.0, 1.18, 0.24),
              bez((-0.38, 0.04), (-0.22, 0.2), (0.1, 0.04), (0.52, 0.04)),
              chain(bez((-0.38, 1.12), (-0.24, 1.36), (0.2, 1.34), (0.66, 1.28)), line((0.66, 1.28), (0.66, 0.2)), line((0.66, 0.2), (0.58, 0.1))),
              diamond(0.3, 0.6), thorn(0.0, 0.6)]
    L["E"] = [round_left(1.2, 0.78), double(), chain(cap_roof(0.27, 0.74), line((0.74, 1.32), (0.42, 0.98))),
              line((0.36, 0.8), (0.66, 0.8))]
    L["F"] = [stem(0.0, 1.28, 0.06), line((-0.34, 0.32), (-0.06, 0.02)), line((-0.32, 0.78), (0.34, 0.78)),
              bez((0.04, 1.32), (0.16, 1.4), (0.3, 1.38), (0.46, 1.34))]
    L["G"] = [round_left(1.2, 0.6, 0.04), double(), chain(cap_roof(0.27, 0.72), line((0.72, 1.32), (0.42, 0.98))),
              chain(line((0.4, 0.84), (0.71, 0.84)), line((0.71, 0.84), (0.71, 0.16)))]
    L["H"] = [chain(bez((0.4, 1.3), (0.04, 1.18), (0.0, 0.92), (0.2, 0.72)), bez((0.2, 0.72), (0.38, 0.56), (0.44, 0.36), (0.36, 0.2))),
              line((-0.06, 0.12), (0.62, 0.04)),
              line((0.44, 1.34), (0.9, 1.32)),
              chain(line((0.5, 1.02), (0.86, 0.92)), line((0.86, 0.92), (0.86, -0.16)))]
    L["I"] = [chain(line((0.0, 1.28), (0.0, 0.22)), line((0.0, 0.22), (-0.1, 0.08))),
              bez((-0.6, 0.18), (-0.5, 0.0), (-0.3, -0.02), (-0.12, 0.04)),
              line((-0.32, 1.3), (-0.04, 1.36)),
              diamond(-0.2, 0.74)]
    L["J"] = [chain(line((0.0, 1.28), (0.0, -0.22)), line((0.0, -0.22), (-0.1, -0.34))),
              bez((-0.6, -0.12), (-0.5, -0.3), (-0.3, -0.34), (-0.12, -0.3)),
              line((-0.32, 1.3), (-0.04, 1.36)),
              diamond(-0.2, 0.74)]
    L["K"] = [chain(bez((0.2, 1.2), (-0.1, 1.0), (-0.06, 0.8), (0.1, 0.62)), bez((0.1, 0.62), (0.22, 0.48), (0.2, 0.3), (0.1, 0.16))),
              line((-0.12, 0.08), (0.36, 0.02)),
              poly((0.16, 0.8), (0.36, 1.06), (0.54, 0.88), (0.38, 0.72)),
              line((0.34, 0.68), (0.84, 0.06)),
              bez((0.0, 1.16), (0.2, 1.48), (0.72, 1.48), (0.92, 1.18))]
    L["L"] = [chain(bez((0.28, 1.28), (0.04, 1.1), (0.0, 0.94), (0.08, 0.76)), bez((0.08, 0.76), (0.16, 0.56), (0.14, 0.34), (0.08, 0.18))),
              line((-0.06, 0.06), (0.74, 0.1)),
              line((0.3, 1.34), (0.7, 1.3)),
              diamond(0.42, 0.54)]
    L["M"] = [chain(head(0.0, C), line((0.0, 1.15), (0.0, 0.28)), line((0.0, 0.28), (-0.1, 0.16))),
              bez((-0.34, 0.06), (-0.2, 0.14), (0.0, 0.08), (0.14, 0.02)),
              minim(0.44, C), minim(0.9, C),
              line((0.12, 0.66), (0.72, 0.66)),
              thorn(0.0, 0.6)]
    L["N"] = [chain(head(0.0, C), line((0.0, 1.15), (0.0, 0.28)), line((0.0, 0.28), (-0.1, 0.16))),
              bez((-0.34, 0.06), (-0.2, 0.14), (0.0, 0.08), (0.14, 0.02)),
              chain(line((0.06, 1.32), (0.5, 1.12)), line((0.5, 1.12), (0.5, FT)), foot(0.5)),
              diamond(0.26, 0.52), thorn(0.0, 0.6)]
    L["O"] = [round_left(1.2, 0.6, 0.04), double(), chain(cap_roof(0.27, 0.74, 1.28), line((0.74, 1.3), (0.74, 0.22)), line((0.74, 0.22), (0.66, 0.1)))]
    L["P"] = [chain(line((-0.18, 1.04), (0.0, 1.26)), line((0.0, 1.26), (0.0, -0.36))),
              chain(cap_roof(0.04, 0.5, 1.28), line((0.5, 1.3), (0.5, 0.2))),
              line((-0.3, 0.1), (0.56, 0.04)),
              thorn(0.0, 0.6)]
    L["Q"] = [round_left(1.2, 0.6, 0.04), double(), chain(cap_roof(0.27, 0.74, 1.28), line((0.74, 1.3), (0.74, 0.22)), line((0.74, 0.22), (0.66, 0.1))),
              line((0.42, 0.3), (0.86, -0.16))]
    L["R"] = [chain(line((-0.18, 1.04), (0.0, 1.26)), line((0.0, 1.26), (0.0, 0.2))),
              line((-0.3, 0.1), (0.24, 0.04)),
              poly((0.07, 1.04), (0.3, 1.36), (0.52, 1.12), (0.3, 0.88)),
              poly((0.1, 0.8), (0.42, 0.8), (0.82, 0.06)),
              thorn(0.0, 0.6)]
    L["S"] = [poly((0.0, 1.2), (0.0, 0.88), (0.6, 0.6), (0.6, 0.16)),
              bez((-0.2, 0.04), (-0.12, 0.34), (0.28, 0.3), (0.52, 0.04)),
              bez((0.04, 1.3), (0.2, 1.4), (0.5, 1.38), (0.72, 1.3))]
    L["T"] = [round_left(1.12, 0.8), double(0.25, 1.14, 0.56),
              bez((-0.34, 1.32), (-0.2, 1.5), (0.4, 1.46), (0.86, 1.4)),
              diamond(0.5, 0.62)]
    L["U"] = [chain(bez((-0.16, 1.2), (-0.06, 1.34), (0.0, 1.3), (0.0, 1.14)), line((0.0, 1.14), (0.0, FT)), line((0.0, FT), (0.15, 0.05)),
                    line((0.15, 0.05), (0.42, 0.14))),
              minim(0.56, C)]
    L["V"] = [chain(bez((-0.16, 1.2), (-0.06, 1.34), (0.0, 1.3), (0.0, 1.14)), line((0.0, 1.14), (0.0, FT)), line((0.0, FT), (0.15, 0.05)),
                    line((0.15, 0.05), (0.5, 0.2))),
              poly((0.06, 1.02), (0.3, 1.34), (0.56, 1.22)),
              line((0.56, 1.22), (0.56, 0.3)),
              thorn(0.0, 0.62)]
    L["W"] = [chain(bez((-0.16, 1.2), (-0.06, 1.34), (0.0, 1.3), (0.0, 1.14)), line((0.0, 1.14), (0.0, FT)), line((0.0, FT), (0.15, 0.05)),
                    line((0.15, 0.05), (0.36, 0.14))),
              poly((0.06, 1.02), (0.3, 1.34), (0.44, 1.2)),
              minim(0.44, C, hd=False),
              poly((0.5, 1.02), (0.72, 1.34), (0.92, 1.2)),
              line((0.92, 1.2), (0.92, 0.3)),
              line((0.16, 0.66), (0.78, 0.66))]
    L["X"] = [chain(line((-0.1, 1.32), (0.08, 1.14)), line((0.08, 1.14), (0.08, 0.3)), line((0.08, 0.3), (-0.14, 0.04))),
              line((0.12, 0.66), (0.66, 0.06)),
              poly((0.14, 1.04), (0.4, 1.36), (0.62, 1.22)),
              bez((-0.38, 0.06), (-0.2, 0.14), (0.0, 0.1), (0.1, 0.02)),
              line((-0.2, 0.62), (0.5, 0.62))]
    L["Y"] = [chain(bez((-0.16, 1.2), (-0.06, 1.34), (0.0, 1.3), (0.0, 1.14)), line((0.0, 1.14), (0.0, 0.42)), line((0.0, 0.42), (0.15, 0.26)),
                    line((0.15, 0.26), (0.46, 0.34))),
              chain(line((0.56, 1.32), (0.56, -0.24)), line((0.56, -0.24), (0.48, -0.36))),
              bez((-0.12, -0.3), (0.0, -0.22), (0.2, -0.3), (0.42, -0.4)),
              thorn(0.0, 0.72)]
    L["Z"] = [line((0.1, 1.3), (0.74, 1.26)),
              line((0.66, 1.2), (0.06, 0.14)),
              line((0.86, 1.28), (0.24, 0.12)),
              line((-0.02, 0.06), (0.8, 0.04)),
              line((0.1, 0.66), (0.62, 0.66))]
    return L


F = 1.2                                      # figure height


def _figures():
    L = {}
    L["0"] = [poly((0.0, F - 0.1), (0.0, FT), (0.15, 0.05), (0.3, 0.14)),
              chain(line((0.05, F - 0.05), (0.38, F - 0.2)), line((0.38, F - 0.2), (0.38, 0.22)))]
    L["1"] = [chain(line((-0.16, F - 0.24), (0.0, F - 0.06)), line((0.0, F - 0.06), (0.0, FT)), foot(0.0))]
    L["2"] = [poly((0.0, F - 0.16), (0.12, F - 0.02), (0.38, F - 0.16), (0.38, 0.8), (0.02, 0.16)),
              line((0.0, 0.1), (0.46, 0.06))]
    L["3"] = [poly((0.0, F - 0.06), (0.36, F - 0.18), (0.08, 0.7)),
              chain(line((0.06, 0.72), (0.38, 0.6)), line((0.38, 0.6), (0.38, 0.22))),
              bez((-0.12, 0.14), (-0.04, 0.24), (0.12, 0.2), (0.32, 0.08))]
    L["4"] = [poly((0.28, F - 0.04), (-0.04, 0.42), (0.5, 0.42)), chain(line((0.34, 0.8), (0.34, FT)), foot(0.34))]
    L["5"] = [poly((0.04, F - 0.06), (0.0, 0.66), (0.38, 0.6), (0.38, 0.22)),
              line((0.06, F - 0.04), (0.44, F - 0.1)),
              bez((-0.12, 0.14), (-0.04, 0.24), (0.12, 0.2), (0.32, 0.08))]
    L["6"] = [poly((0.36, F - 0.02), (0.0, F - 0.22), (0.0, FT), (0.15, 0.05), (0.3, 0.14)),
              chain(line((0.04, 0.68), (0.38, 0.58)), line((0.38, 0.58), (0.38, 0.22)))]
    L["7"] = [line((0.0, F - 0.06), (0.44, F - 0.1)), poly((0.44, F - 0.1), (0.2, 0.5), (0.2, FT), (0.3, 0.06))]
    L["8"] = [poly((0.0, F - 0.1), (0.0, 0.8), (0.38, 0.5), (0.38, 0.22)),
              chain(line((0.05, F - 0.04), (0.38, F - 0.16)), line((0.38, F - 0.16), (0.38, 0.84))),
              poly((0.3, 0.7), (0.0, 0.48), (0.0, FT), (0.15, 0.05), (0.3, 0.14))]
    L["9"] = [poly((0.0, F - 0.1), (0.0, 0.62), (0.15, 0.48), (0.32, 0.56)),
              chain(line((0.05, F - 0.04), (0.38, F - 0.2)), line((0.38, F - 0.2), (0.38, 0.22)), line((0.38, 0.22), (0.02, 0.04)))]
    return L


def letters():
    L = _small()
    L.update(_capitals())
    L.update(_figures())
    return L


HAND = dict(
    id="blackletter", name="Blackletter", family="blackletter", variant="Textura", pen="broad", S=40, base=69, slant_deg=0,
    ext=(1.36, 0.35), start="inmuoce", sample="text", keys="inoa", nib_angle=40, nib=8.0, hair=1.0, dot_w=7.0, cap=C,
    about={
        "tool": "A broad-edged pen held at about 40°.", "slant": "Upright.",
        "proportions": "x-height 5 nib widths; ascenders and capitals 1.36 x-heights, descenders 0.35; the stems "
                       "a third of an x-height apart, so the white between them is as wide as a stem.",
        "features": "Textura Quadrata: dense vertical stems (minims) with diamond heads and feet, round letters "
                    "broken into a box of stems, roof and foot, the d's back curving over its bowl, g and y closed by "
                    "a heavy tail; wide capitals with doubled stems, diagonal hairlines, diamonds in the counters "
                    "and thorns beside the stems. The long vertical hairlines that cross some capitals (drawn with "
                    "the nib's corner) are left out here: a nib held at one angle draws every vertical thick.",
        "history": "The formal book hand of northern Europe from the 12th to the 15th century (Gutenberg's Bible is "
                   "set in it); also Fraktur, Rotunda and Bâtarde."})
