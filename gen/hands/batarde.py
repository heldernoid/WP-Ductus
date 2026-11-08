"""Blackletter: Bâtarde (lettre bâtarde, the Burgundian bastarda of the 15th century).

Measured on the sheet "La gothique bâtarde" (a French teaching exemplar with numbered ductus; its pen diagram reads
"3 becs de plume", 40°, and its note gives the capitals about 6 nib widths), x-height 32 px there:

  x-height in nib widths    3     (stem 8 px = nib x cos 40°, nib about 10.4 px; the sheet's "3 becs de plume")
  ascender / descender      1.62 / 0.56 x-heights (h, k, l; f, g, p)
  capital height            about 1.45 x-heights (45-50 px; about 4.5 measured nib widths)
  stem pitch (n, m)         0.44 x-heights; widths with the pen: n 1.15 (with its lead-in and turn), m 1.53, o 0.81,
                            e 0.94; capitals wide: B 1.6, D 1.8, E 1.7, G 1.85, M 2.25, N 1.8, Q 2.3, S 1.85
  slant                     about 8° (k and l stems)
  nib angle                 40° (the sheet's diagram; the hairlines of o and the lead-ins)

Forms and stroke order follow the sheet, checked against the Burgundian court manuscripts of the 1460s-1480s. A
heavy cursive gothic: stems begin with a hairline lead-in and end in a point or a small turn, the arches of h, m, n
are broken (a hairline out of the stem, a flat heavy roof, a sharp corner into the next stem), the o is a pointed
almond of two strokes (left side, then right side, both from the top point to the bottom point), the a is
single-storey (its bowl first, then a pointed top and the stem), the d's back rises from the bowl and sweeps over
it, f descends as a long pointed stroke with its head written after it, g, h, j, p, q, y descend and the g, h, y
descenders sweep to the left, v and w begin with a tall curved stroke and close with a bowl rising on the right,
the x is a heavy diagonal crossed by a descending hairline. The capitals are wide Burgundian capitals built from
great curved strokes with the hand's curled hairline lead-ins and diamonds in the counters (O, P, Q); each is
widened to its measured width on the sheet. Figures are authored in the same pen (lining, 1.2 x-heights); the sheet
has none. Simplified: the long s (not part of the a-z alphabet) is left out; the thin vertical hairlines inside C and
E and the long hairline tails of the capitals are left out or shortened (a nib held at one angle draws every
vertical thick, and the tails would leave the canvas); the swelling of a stroke comes only from its direction (the
nib's angle), not from pressure. The unit is the x-height.
"""
from gen.pen import bez, chain, line

W = 0.46                                     # stem to stem in n
ASC, DESC = 1.62, -0.56


def lead(u, top=1.0):
    """the hairline lead-in into the head of a stem at u"""
    return line((u - 0.13, top - 0.11), (u, top))


def stem(u, top=1.0, bot=0.12, lead_in=True):
    s = line((u, top), (u, bot))
    return chain(lead(u, top), s) if lead_in else s


def turn(u, bot=0.12, reach=0.16):
    """the foot: the stem turns to the right at the line"""
    return bez((u, bot), (u, 0.02), (u + reach * 0.5, -0.02), (u + reach, 0.04))


def point(u, bot):
    """a descender that ends in a point, curving off to the left"""
    return bez((u, bot + 0.35), (u, bot + 0.12), (u - 0.04, bot + 0.04), (u - 0.16, bot))


def arch(u0, u1, top=1.0, spring=0.62):
    """the broken arch: out of the stem at u0, up and over, turning sharply at the top right into the stem at u1"""
    return chain(line((u0 + 0.03, spring), (u0 + 0.12, top - 0.02)), line((u0 + 0.12, top - 0.02), (u1 - 0.04, top - 0.02)),
                 line((u1 - 0.04, top - 0.02), (u1, top - 0.14)))


def almond_left(t=(0.3, 1.0), b=(0.24, 0.0), lw=0.0):
    """the left side of the pointed o: from the top point round the left down to the bottom point"""
    return chain(bez(t, (t[0] - 0.2, t[1] - 0.04), (lw, t[1] - 0.24), (lw, t[1] * 0.5)),
                 bez((lw, t[1] * 0.5), (lw, 0.18), (b[0] - 0.14, b[1]), b))


def almond_right(t=(0.3, 1.0), b=(0.24, 0.0), rw=W):
    """the right side of the pointed o: from the top point over and down the right side to the bottom point"""
    return chain(bez(t, (t[0] + 0.14, t[1]), (rw, t[1] - 0.14), (rw, t[1] * 0.55)),
                 bez((rw, t[1] * 0.55), (rw, 0.2), (b[0] + 0.18, b[1] + 0.02), b))


def _small():
    L = {}
    L["a"] = [chain(almond_left((0.3, 0.98), (0.22, 0.0)), line((0.22, 0.0), (W - 0.02, 0.3))),
              chain(line((0.3, 0.98), (W, 0.86)), line((W, 0.86), (W, 0.12)), turn(W))]
    L["b"] = [chain(lead(0.0, ASC), line((0.0, ASC), (0.0, 0.08))),
              chain(line((0.03, 0.66), (0.14, 0.98)), line((0.14, 0.98), (0.5, 0.96)), bez((0.5, 0.96), (0.62, 0.7), (0.6, 0.2), (0.36, 0.0)),
                    line((0.36, 0.0), (0.06, 0.0)))]
    L["c"] = [chain(almond_left((0.3, 0.98), (0.26, 0.0)), bez((0.26, 0.0), (0.34, 0.0), (0.42, 0.04), (0.46, 0.12))),
              bez((0.3, 0.98), (0.38, 1.04), (0.48, 1.02), (0.48, 0.84))]
    L["d"] = [chain(almond_left((0.34, 0.92), (0.3, 0.0)), line((0.3, 0.0), (0.44, 0.04))),
              chain(bez((-0.08, 1.5), (0.18, 1.72), (0.62, 1.4), (0.56, 0.72)), bez((0.56, 0.72), (0.54, 0.4), (0.56, 0.2), (0.5, 0.08)))]
    L["e"] = [chain(almond_left((0.3, 0.98), (0.26, 0.0)), bez((0.26, 0.0), (0.34, 0.0), (0.42, 0.04), (0.46, 0.12))),
              chain(bez((0.3, 0.98), (0.4, 1.04), (0.5, 0.98), (0.46, 0.8)), line((0.46, 0.8), (0.06, 0.52)))]
    L["f"] = [bez((0.12, 1.42), (0.14, 0.6), (0.08, -0.4), (-0.12, DESC + 0.05)),
              bez((0.12, 1.42), (0.18, 1.68), (0.48, 1.72), (0.56, 1.48)),
              line((-0.12, 0.96), (0.38, 0.96))]
    L["g"] = [chain(almond_left((0.3, 0.98), (0.22, 0.0)), line((0.22, 0.0), (W - 0.02, 0.3))),
              chain(line((0.3, 0.98), (W, 0.86)), line((W, 0.86), (W, -0.3)),
                    bez((W, -0.3), (W - 0.04, -0.62), (0.14, -0.76), (-0.18, -0.56)))]
    L["h"] = [stem(0.0, ASC, 0.06),
              chain(arch(0.0, W), line((W, 0.86), (W, -0.1)), bez((W, -0.1), (W, -0.42), (0.36, -0.6), (0.14, -0.62)))]
    L["i"] = [chain(stem(0.0), turn(0.0)), line((-0.02, 1.4), (0.07, 1.28))]
    L["j"] = [chain(stem(0.0), line((0.0, 0.12), (0.0, -0.3)), point(0.0, -0.66)), line((-0.02, 1.4), (0.07, 1.28))]
    L["k"] = [stem(0.0, ASC, 0.06),
              chain(bez((0.03, 0.46), (0.16, 0.84), (0.44, 1.12), (0.5, 0.86)), bez((0.5, 0.86), (0.5, 0.7), (0.3, 0.6), (0.12, 0.52)),
                    bez((0.12, 0.52), (0.34, 0.38), (0.38, 0.06), (0.58, 0.02)))]
    L["l"] = [chain(stem(0.0, ASC), turn(0.0))]
    L["m"] = [stem(0.0, 1.0, 0.06), chain(arch(0.0, 0.44), line((0.44, 0.86), (0.44, 0.06))),
              chain(arch(0.44, 0.88), line((0.88, 0.86), (0.88, 0.12)), turn(0.88))]
    L["n"] = [stem(0.0, 1.0, 0.06), chain(arch(0.0, W), line((W, 0.86), (W, 0.12)), turn(W))]
    L["o"] = [almond_left((0.26, 1.0), (0.3, 0.0)), almond_right((0.26, 1.0), (0.3, 0.0), 0.56)]
    L["p"] = [chain(stem(0.0, 1.0, -0.4), point(0.0, DESC + 0.05)),
              chain(line((0.03, 0.66), (0.14, 0.98)), line((0.14, 0.98), (0.5, 0.96)), bez((0.5, 0.96), (0.62, 0.7), (0.6, 0.2), (0.36, 0.0)),
                    line((0.36, 0.0), (0.06, 0.02)))]
    L["q"] = [chain(almond_left((0.3, 0.98), (0.22, 0.0)), line((0.22, 0.0), (W - 0.02, 0.3))),
              chain(line((0.3, 0.98), (W, 0.86)), line((W, 0.86), (W, -0.4)), point(W, DESC + 0.05))]
    L["r"] = [chain(stem(0.0), turn(0.0)), bez((0.03, 0.66), (0.1, 0.94), (0.3, 1.06), (0.44, 0.9))]
    L["s"] = [chain(bez((0.36, 0.98), (0.12, 1.06), (-0.04, 0.9), (0.06, 0.68)), bez((0.06, 0.68), (0.14, 0.5), (0.46, 0.5), (0.46, 0.24)),
                    bez((0.46, 0.24), (0.46, 0.0), (0.12, -0.06), (-0.04, 0.1))),
              bez((0.36, 0.98), (0.44, 1.02), (0.52, 0.98), (0.5, 0.84))]
    L["t"] = [chain(line((0.0, 1.32), (0.0, 0.12)), turn(0.0)), line((-0.14, 0.96), (0.36, 0.96))]
    L["u"] = [chain(stem(0.0), bez((0.0, 0.12), (0.0, 0.0), (0.12, -0.02), (W - 0.04, 0.26))), chain(stem(W), turn(W))]
    L["v"] = [chain(bez((-0.16, 1.3), (-0.02, 1.5), (0.08, 1.36), (0.06, 0.9)), bez((0.06, 0.9), (0.04, 0.5), (0.04, 0.12), (0.2, 0.0))),
              chain(bez((0.2, 0.0), (0.5, 0.06), (0.62, 0.6), (0.5, 1.0)), bez((0.5, 1.0), (0.46, 1.08), (0.36, 1.06), (0.34, 0.94)))]
    L["w"] = [chain(bez((-0.16, 1.18), (-0.02, 1.36), (0.08, 1.2), (0.06, 0.9)), bez((0.06, 0.9), (0.04, 0.5), (0.04, 0.12), (0.18, 0.0)),
                    line((0.18, 0.0), (0.4, 0.26))),
              chain(stem(0.46, 1.0, 0.12, False), bez((0.46, 0.12), (0.46, 0.02), (0.54, 0.0), (0.6, 0.0))),
              chain(bez((0.6, 0.0), (0.88, 0.06), (0.98, 0.6), (0.88, 1.0)), bez((0.88, 1.0), (0.84, 1.08), (0.74, 1.06), (0.72, 0.94)))]
    L["x"] = [chain(lead(0.0), bez((0.0, 1.0), (0.2, 0.7), (0.3, 0.2), (0.5, 0.02))),
              line((0.5, 1.0), (-0.08, -0.44))]
    L["y"] = [chain(bez((-0.16, 1.18), (-0.02, 1.36), (0.08, 1.2), (0.06, 0.9)), bez((0.06, 0.9), (0.04, 0.5), (0.04, 0.12), (0.18, 0.0)),
                    line((0.18, 0.0), (W - 0.04, 0.28))),
              chain(stem(W, 1.0, -0.2), bez((W, -0.2), (W, -0.52), (0.3, -0.72), (0.0, -0.62)))]
    L["z"] = [chain(bez((-0.02, 0.88), (0.1, 1.02), (0.28, 0.92), (0.46, 0.98)), line((0.46, 0.98), (0.02, 0.04))),
              chain(bez((0.02, 0.04), (0.18, 0.12), (0.34, -0.02), (0.48, 0.04)), bez((0.48, 0.04), (0.58, 0.1), (0.56, -0.3), (0.3, -0.42)))]
    return L


C = 1.45                                      # capital height (the sheet's capitals stand about 4.5 nib widths)


def cap_bowl(u0, top, w, bot=0.0, end=None):
    """the great round left side of C, E, G, O, Q: from the top round the left and along the bottom"""
    end = end or (u0 + w, 0.14)
    return chain(bez((u0 + 0.42, top), (u0 + 0.1, top - 0.02), (u0 - 0.06, top - 0.4), (u0 - 0.06, top * 0.5)),
                 bez((u0 - 0.06, top * 0.5), (u0 - 0.06, 0.16), (u0 + 0.2, bot), (u0 + 0.5, bot)),
                 bez((u0 + 0.5, bot), (u0 + 0.7, bot), (end[0] - 0.1, end[1] - 0.1), end))


def cap_arch(u0, u1, top=C, spring=0.9):
    """the round shoulder of M and N: a hairline out of the stem, then over and down into the next stem"""
    return chain(bez((u0 + 0.02, spring), (u0 + 0.06, top - 0.16), (u0 + 0.2, top + 0.02), (u0 + 0.4 * (u1 - u0) + 0.1, top)),
                 bez((u0 + 0.4 * (u1 - u0) + 0.1, top), (u1 - 0.1, top - 0.02), (u1, top - 0.1), (u1, top - 0.24)))


def wave(u, top=C):
    """the Burgundian lead-in: a hairline rising from the left in a curl into the head of a stem at u"""
    return bez((u - 0.34, top - 0.5), (u - 0.36, top - 0.12), (u - 0.14, top + 0.04), (u, top - 0.04))


def _capitals():
    L = {}
    L["A"] = [bez((-0.24, 0.9), (-0.26, 1.42), (0.24, 1.62), (0.6, 1.42)),
              chain(line((0.6, 1.42), (1.12, 0.12)), bez((1.12, 0.12), (1.16, 0.02), (1.24, 0.0), (1.32, 0.06))),
              line((0.52, 1.32), (0.0, 0.0)),
              line((0.36, 0.56), (0.98, 0.6))]
    L["B"] = [chain(wave(0.14), line((0.14, C - 0.04), (0.08, 0.1))),
              chain(bez((0.2, 1.4), (0.66, 1.6), (1.06, 1.4), (0.86, 1.06)), bez((0.86, 1.06), (0.76, 0.9), (0.56, 0.84), (0.34, 0.84))),
              chain(bez((0.44, 0.86), (1.26, 0.9), (1.3, 0.2), (0.78, 0.04)), bez((0.78, 0.04), (0.5, -0.04), (0.0, -0.02), (-0.3, 0.06)))]
    L["C"] = [cap_bowl(0.1, 1.36, 1.0),
              bez((0.46, 1.36), (0.66, 1.56), (0.98, 1.5), (1.06, 1.24))]
    L["D"] = [chain(bez((0.3, 0.84), (-0.06, 0.96), (-0.06, 1.3), (0.3, 1.42)), bez((0.3, 1.42), (0.9, 1.6), (1.5, 1.3), (1.42, 0.7)),
                    bez((1.42, 0.7), (1.36, 0.16), (0.8, -0.02), (0.36, 0.0)), line((0.36, 0.0), (-0.14, 0.04))),
              line((0.36, 0.22), (0.78, 0.58))]
    L["E"] = [cap_bowl(0.1, 1.36, 0.96),
              bez((0.46, 1.36), (0.64, 1.54), (0.92, 1.5), (1.0, 1.26)),
              chain(line((0.3, 0.76), (0.86, 0.8)), line((0.86, 0.8), (0.96, 0.7)))]
    L["F"] = [chain(bez((0.5, 1.4), (0.52, 0.8), (0.4, 0.2), (0.1, -0.1)), line((0.1, -0.1), (-0.12, -0.04))),
              bez((0.5, 1.4), (0.6, 1.58), (0.94, 1.6), (1.04, 1.38)),
              line((0.04, 0.8), (0.9, 0.84))]
    L["G"] = [cap_bowl(0.1, 1.36, 0.7, 0.0, (0.8, 0.06)),
              bez((0.46, 1.36), (0.66, 1.56), (0.98, 1.5), (1.06, 1.24)),
              chain(bez((0.44, 0.8), (0.8, 0.96), (1.14, 0.84), (1.1, 0.5)), bez((1.1, 0.5), (1.08, 0.26), (1.0, 0.12), (0.86, 0.06)))]
    L["H"] = [chain(wave(0.14), line((0.14, C - 0.04), (0.08, 0.06))),
              chain(bez((0.12, 0.66), (0.24, 1.0), (0.56, 1.1), (0.84, 0.96)), bez((0.84, 0.96), (1.0, 0.82), (0.96, 0.4), (0.96, 0.0)),
                    bez((0.96, 0.0), (0.96, -0.36), (0.76, -0.56), (0.46, -0.58))),
              line((0.4, 1.5), (0.56, 1.36))]
    L["I"] = [chain(bez((0.0, 0.3), (-0.1, 1.0), (0.2, 1.5), (0.46, 1.42)), bez((0.46, 1.42), (0.56, 1.0), (0.52, 0.3), (0.24, 0.0))),
              line((0.62, 0.84), (0.8, 0.72))]
    L["J"] = [chain(bez((0.0, 0.3), (-0.1, 1.0), (0.2, 1.5), (0.46, 1.42)), bez((0.46, 1.42), (0.56, 0.8), (0.5, -0.2), (0.12, -0.58))),
              line((0.62, 0.84), (0.8, 0.72))]
    L["K"] = [chain(wave(0.14), line((0.14, C - 0.04), (0.08, 0.06))),
              chain(bez((0.22, 0.6), (0.5, 0.8), (0.7, 1.38), (1.02, 1.42)), bez((1.02, 1.42), (1.14, 1.38), (1.12, 1.24), (1.0, 1.16))),
              bez((0.3, 0.64), (0.7, 0.66), (0.76, 0.12), (1.2, 0.02))]
    L["L"] = [chain(bez((0.8, 1.36), (0.76, 0.9), (0.6, 0.3), (0.12, 0.04)), bez((0.12, 0.04), (0.5, 0.18), (0.9, -0.04), (1.36, 0.06))),
              bez((0.8, 1.36), (0.9, 1.6), (1.22, 1.6), (1.26, 1.36))]
    L["M"] = [chain(wave(0.12), line((0.12, C - 0.04), (0.08, 0.06))),
              chain(cap_arch(0.1, 0.66), line((0.66, C - 0.24), (0.64, 0.06))),
              chain(cap_arch(0.66, 1.22), line((1.22, C - 0.24), (1.22, 0.12)), turn(1.22))]
    L["N"] = [chain(wave(0.12), line((0.12, C - 0.04), (0.08, 0.06))),
              chain(cap_arch(0.1, 0.84), line((0.84, C - 0.24), (0.84, 0.12)), turn(0.84))]
    L["O"] = [almond_left((0.6, 1.48), (0.62, 0.0), -0.04), almond_right((0.6, 1.48), (0.62, 0.0), 1.26), line((0.54, 0.82), (0.7, 0.68))]
    L["P"] = [chain(wave(0.16), line((0.16, C - 0.04), (0.12, -0.24)), point(0.12, -0.6)),
              chain(bez((0.2, 1.4), (0.8, 1.62), (1.34, 1.4), (1.2, 0.9)), bez((1.2, 0.9), (1.1, 0.56), (0.66, 0.46), (0.24, 0.5))),
              line((0.6, 1.08), (0.76, 0.94))]
    L["Q"] = [almond_left((0.6, 1.48), (0.62, 0.0), -0.04), almond_right((0.6, 1.48), (0.62, 0.0), 1.26), line((0.54, 0.82), (0.7, 0.68)),
              bez((0.5, 0.06), (0.8, -0.14), (1.16, -0.2), (1.44, -0.08))]
    L["R"] = [chain(wave(0.14), line((0.14, C - 0.04), (0.08, 0.06))),
              chain(bez((0.2, 1.4), (0.74, 1.6), (1.12, 1.38), (0.96, 1.04)), bez((0.96, 1.04), (0.84, 0.82), (0.54, 0.74), (0.28, 0.74))),
              bez((0.46, 0.72), (0.8, 0.66), (0.84, 0.1), (1.26, 0.02))]
    L["S"] = [chain(bez((0.86, 1.4), (0.36, 1.54), (0.1, 1.3), (0.26, 1.02)), bez((0.26, 1.02), (0.44, 0.76), (1.1, 0.78), (1.06, 0.36)),
                    bez((1.06, 0.36), (1.02, 0.0), (0.3, -0.06), (-0.12, 0.12))),
              bez((0.84, 1.34), (0.94, 1.5), (1.1, 1.5), (1.16, 1.3))]
    L["T"] = [bez((-0.2, 1.24), (0.06, 1.56), (0.6, 1.32), (1.3, 1.5)),
              cap_bowl(0.12, 1.3, 0.96),
              line((0.62, 1.24), (0.6, 0.6))]
    L["U"] = [chain(wave(0.12), bez((0.12, C - 0.04), (0.1, 0.8), (0.08, 0.1), (0.3, 0.0)), line((0.3, 0.0), (0.76, 0.3))),
              chain(stem(0.86, C - 0.04, 0.12), turn(0.86))]
    L["V"] = [chain(wave(0.14), bez((0.14, C - 0.04), (0.14, 0.8), (0.1, 0.14), (0.4, 0.0))),
              chain(bez((0.4, 0.0), (1.0, 0.04), (1.26, 0.8), (1.06, 1.42)), bez((1.06, 1.42), (1.0, 1.52), (0.86, 1.5), (0.84, 1.38)))]
    L["W"] = [chain(wave(0.12), bez((0.12, C - 0.04), (0.12, 0.8), (0.08, 0.14), (0.3, 0.0)), line((0.3, 0.0), (0.56, 0.3))),
              chain(stem(0.68, C - 0.04, 0.12, False), bez((0.68, 0.12), (0.68, 0.02), (0.78, 0.0), (0.86, 0.0))),
              chain(bez((0.86, 0.0), (1.3, 0.06), (1.44, 0.8), (1.28, 1.42)), bez((1.28, 1.42), (1.22, 1.52), (1.1, 1.5), (1.08, 1.38)))]
    L["X"] = [chain(wave(0.14), bez((0.14, C - 0.04), (0.44, 1.0), (0.66, 0.3), (1.12, 0.02))),
              line((1.06, C), (0.0, -0.3)),
              line((0.14, 0.74), (1.06, 0.78))]
    L["Y"] = [chain(wave(0.14), bez((0.14, C - 0.04), (0.14, 0.9), (0.12, 0.4), (0.32, 0.3)), line((0.32, 0.3), (0.8, 0.5))),
              chain(stem(0.9, C - 0.04, -0.2), bez((0.9, -0.2), (0.9, -0.5), (0.5, -0.66), (0.08, -0.58)))]
    L["Z"] = [chain(bez((-0.06, 1.28), (0.14, 1.5), (0.5, 1.36), (1.0, 1.46)), line((1.0, 1.46), (0.04, 0.04))),
              bez((0.04, 0.04), (0.4, 0.16), (0.76, -0.04), (1.12, 0.06)),
              line((0.18, 0.76), (0.9, 0.8))]
    # the capitals are drawn above at their structure; the sheet's are wider still (B 1.6, E 1.7, M 2.25, N 1.8 x-heights
    # with the pen): each is widened to its measured width
    for ch, k in WIDE.items():
        L[ch] = [[(u * k, v) for u, v in st] for st in L[ch]]
    return L


WIDE = dict(A=1.1, B=1.2, C=1.25, D=1.15, E=1.3, F=1.1, G=1.3, H=1.25, K=1.25, M=1.45, N=1.6, O=1.25, P=1.2, Q=1.25, R=1.2,
            S=1.2, T=1.2, U=1.3, V=1.25, W=1.15, X=1.2, Y=1.1, Z=1.15)


F = 1.2                                       # figure height


def _figures():
    L = {}
    L["0"] = [almond_left((0.26, F), (0.3, 0.0)), almond_right((0.26, F), (0.3, 0.0), 0.56)]
    L["1"] = [chain(lead(0.1, F), line((0.1, F), (0.1, 0.12)), turn(0.1))]
    L["2"] = [chain(bez((0.0, 0.96), (0.06, 1.24), (0.5, 1.28), (0.48, 0.9)), bez((0.48, 0.9), (0.46, 0.6), (0.2, 0.3), (0.02, 0.04))),
              bez((0.02, 0.04), (0.2, 0.12), (0.38, -0.02), (0.56, 0.06))]
    L["3"] = [chain(bez((0.0, 1.0), (0.08, 1.26), (0.48, 1.26), (0.44, 0.94)), bez((0.44, 0.94), (0.42, 0.74), (0.3, 0.66), (0.16, 0.64))),
              chain(bez((0.24, 0.66), (0.56, 0.64), (0.58, 0.18), (0.36, 0.02)), bez((0.36, 0.02), (0.2, -0.06), (0.04, 0.02), (-0.04, 0.14)))]
    L["4"] = [chain(line((0.36, F), (0.0, 0.4)), line((0.0, 0.4), (0.56, 0.4))), chain(line((0.4, 0.84), (0.4, 0.12)), turn(0.4))]
    L["5"] = [chain(line((0.08, F), (0.06, 0.66)), bez((0.06, 0.66), (0.3, 0.84), (0.56, 0.7), (0.52, 0.36)),
                    bez((0.52, 0.36), (0.48, 0.02), (0.14, -0.04), (-0.02, 0.12))),
              line((0.12, F), (0.5, F))]
    L["6"] = [chain(bez((0.46, F), (0.14, 1.1), (0.0, 0.7), (0.02, 0.4)), bez((0.02, 0.4), (0.04, 0.0), (0.42, -0.04), (0.5, 0.24)),
                    bez((0.5, 0.24), (0.56, 0.56), (0.28, 0.7), (0.06, 0.54)))]
    L["7"] = [chain(lead(0.0, F), line((0.0, F), (0.5, F - 0.04)), bez((0.5, F - 0.04), (0.36, 0.8), (0.2, 0.4), (0.18, 0.0)))]
    L["8"] = [chain(bez((0.4, 1.14), (0.2, 1.3), (-0.04, 1.12), (0.08, 0.88)), bez((0.08, 0.88), (0.2, 0.66), (0.54, 0.56), (0.5, 0.26)),
                    bez((0.5, 0.26), (0.46, -0.04), (0.04, -0.04), (0.02, 0.26)), bez((0.02, 0.26), (0.0, 0.56), (0.42, 0.7), (0.46, 0.92)),
                    bez((0.46, 0.92), (0.48, 1.06), (0.44, 1.12), (0.4, 1.14)))]
    L["9"] = [chain(bez((0.5, 0.7), (0.3, 0.52), (0.0, 0.6), (0.02, 0.88)), bez((0.02, 0.88), (0.04, 1.2), (0.46, 1.26), (0.5, 0.92)),
                    bez((0.5, 0.92), (0.54, 0.5), (0.36, 0.12), (0.04, -0.02)))]
    return L


def letters():
    L = _small()
    L.update(_capitals())
    L.update(_figures())
    return L


HAND = dict(
    id="batarde", name="Bâtarde", family="blackletter", variant="Bâtarde", pen="broad", S=34, base=63, slant_deg=8,
    ext=(ASC, -DESC), start="ilnmo", sample="font", keys="afgo", nib_angle=40, nib=11.3, hair=1.0, dot_w=8.0, cap=C,
    about={
        "tool": "A broad-edged pen held at about 40°.", "slant": "Slightly forward, about 8°.",
        "proportions": "x-height 3 nib widths (the sheet's \"3 becs de plume\"); ascenders 1.6 x-heights, descenders 0.55; "
                       "capitals about 1.45 x-heights tall and wider than tall.",
        "features": "A heavy cursive blackletter: hairline lead-ins, arches broken into a flat roof and a corner, a pointed almond o, "
                    "a single-storey a, the d's back sweeping left over its bowl, f plunging below the line as a "
                    "pointed stroke, descenders of g, h and y sweeping left; wide capitals of great curved strokes with "
                    "curled hairline lead-ins and diamonds. The long s, the thin vertical hairlines inside C and E and "
                    "the longest hairline flourishes are left out here.",
        "history": "The lettre bâtarde of the court of the Dukes of Burgundy, 15th century: the book hand of its "
                   "great illuminated manuscripts (the scribes David Aubert and Jean Miélot)."})
