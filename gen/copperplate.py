"""Copperplate model letters, authored as pen strokes.

Measured on a Copperplate exemplar sheet (its pixels; x-height 40 px), the source of these forms:

  x-height                          40 px      1
  ascender line above the baseline  102 px     2.55   (loops of b d f h k l reach it)
  descender line below the baseline 61 px      1.53   (loops of f g j p q y z reach it)
  capital height                    100-102 px 2.5-2.6 (capitals stand on the baseline and reach the ascender line)
  t, d, p, r, s tops                           1.65, 1.95, 1.3, 1.45, 1.35
  slant (slant guides; stems of b, k)          55 degrees (0.70 across per unit up); stems 53-56
  shade (stem) width                6 px       0.15 (across the line); hairline 1-2 px, 0.04
  stem to stem at half the x-height            n 0.59, m 0.57, h 0.65, u 0.62, a 0.58, d 0.60, g 0.66; o 0.55 wide
  ascender loop, descender loop widths         about 0.45 and 0.6 at their widest
  entries                                      every small letter begins with a hairline rising from the baseline
                                               about half an x-height to its left (stroke 1 on the sheet)

Geometry: letters are written in an upright (u, v) frame, v up from the baseline in x-heights (x-height = 1,
ascender line 2.5, descender line -1.5), then sheared to the copperplate slant of 55 degrees and scaled to the
96 x 96 canvas (20 px per x-height, baseline at y = 58). Capitals are 2.5 x-heights tall, as on the exemplar.

Pen width follows the pointed-pen rule: pressure (a wide stroke) only while the pen moves down along the slant;
hairlines everywhere else. So shading is not drawn in by hand per letter: it comes from each stroke's direction. At
20 px per x-height the canvas pen (shade 4 px = 0.2, hairline 1.3 px = 0.065 x-heights) is heavier than the
exemplar's (the pen widths are left as the network was written for them): the letters' widths and loops follow the
exemplar's, so the counters are a little fuller. The entry hairline is written into the first stroke of every letter
that begins with a stem, a loop or e, r, s, t, x; the oval letters (a c d g o q) begin at the oval, without the
sheet's separate entry stroke, which is too short to carry the order and direction marks as a first stroke.

The sheet has no figures: they are the copybooks' figures, 1.8 x-heights tall, shaded by the same rule.

Each letter is a list of strokes in writing order; each stroke is a chain of cubic Bezier segments in (u, v).
"""
import math

S = 20.0                                  # pixels per x-height
BASE_Y = 58.0                             # canvas y of the baseline
SLANT = 1 / math.tan(math.radians(55))    # 55 degrees from the horizontal -> 0.700 of horizontal per unit up
HAIR, SHADE, DOT = 1.3, 4.0, 3.4          # pen widths in pixels
GUIDES = {"ascender": BASE_Y - 2.5 * S, "x-height": BASE_Y - S, "baseline": BASE_Y, "descender": BASE_Y + 1.5 * S}


def bez(p0, p1, p2, p3, n=18):
    pts = []
    for k in range(n + 1):
        t = k / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t ** 2, t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def line(p0, p1):
    return bez(p0, ((2 * p0[0] + p1[0]) / 3, (2 * p0[1] + p1[1]) / 3), ((p0[0] + 2 * p1[0]) / 3, (p0[1] + 2 * p1[1]) / 3), p1, 8)


def chain(*parts):
    out = []
    for p in parts:
        out += p if not out else p[1:]
    return out


# ---- basic strokes (upright frame) ------------------------------------------------------------
def entrance(u, v_end=1.0):
    """hairline rising from the baseline on the left to the top of a stem at u (the exemplar's stroke 1), bowed to the
    left so that it meets the stem only near the top"""
    return bez((u - 0.5, 0.0), (u - 0.38, 0.45), (u - 0.2, 0.85 * v_end), (u, v_end))


def stem(u, v0, v1):
    """straight stroke along the slant from height v0 down to v1"""
    return line((u, v0), (u, v1))


def underturn_exit(u, reach=0.5, top=0.75):
    """from the foot of a stem at u: turn along the baseline and rise as a hairline to the right"""
    return chain(bez((u, 0.3), (u, -0.06), (u + reach * 0.7, -0.06), (u + reach * 0.84, 0.3)),
                 bez((u + reach * 0.84, 0.3), (u + reach * 0.9, 0.48), (u + reach * 0.96, 0.62), (u + reach, top)))


def arch(u0, u1):
    """branching from a stem at u0 halfway up: hairline rising over the top to the next stem at u1"""
    return chain(bez((u0, 0.45), (u0 + 0.04, 0.88), (u1 - 0.18, 1.06), (u1 - 0.03, 0.95)),
                 bez((u1 - 0.03, 0.95), (u1 + 0.01, 0.9), (u1, 0.82), (u1, 0.65)))


def oval(u, start=(0.48, 0.86), w=0.5):
    """counter-clockwise oval: from the top right over the top, down the left side (shaded), round the bottom,
    up the right side as a hairline (w = from its left side to the stem that closes it)"""
    f = w / 0.5
    P = lambda a, b: (u + f * a, b)  # noqa: E731
    s = P(start[0] - u, start[1])
    return chain(bez(s, P(0.4, 1.06), P(0.02, 1.02), P(-0.04, 0.5)),
                 bez(P(-0.04, 0.5), P(-0.08, 0.02), P(0.38, -0.06), P(0.5, 0.38)),
                 bez(P(0.5, 0.38), P(0.55, 0.6), P(0.54, 0.78), s))


def dot(u, v):
    return [(u, v)]


def overturn(u, top=0.9):
    """hairline rising from the baseline on the left, over the top into the head of a downstroke at u"""
    return chain(bez((u - 0.48, 0.0), (u - 0.4, 0.3), (u - 0.34, 0.6), (u - 0.26, 0.8)),
                 bez((u - 0.26, 0.8), (u - 0.18, 1.0), (u - 0.05, 1.06), (u, top)))


def asc_loop(u, start=(-0.45, 0.0), w=1.0):
    """ascending loop: hairline rising from the baseline on the left up to the ascender line, turning left over the top
    into the head of the stem at u (height 2.2); the stem itself follows. The loop is about 0.45 x-heights wide at
    its widest, as on the exemplar (w narrows it)"""
    s0 = (u + start[0], start[1])
    return chain(bez(s0, (u + 0.12, 0.7), (u + 0.62 * w, 1.8), (u + 0.46 * w, 2.35)),
                 bez((u + 0.46 * w, 2.35), (u + 0.36 * w, 2.68), (u - 0.03, 2.56), (u, 2.2)))


def desc_loop(u, w=1.0):
    """descending loop on the left of a stem at u that has reached -1.1: round the bottom to the left (about half an
    x-height wide, as on the exemplar; w narrows it), then a hairline rising to the right, crossing the stem at the
    baseline"""
    return chain(bez((u, -1.1), (u, -1.6), (u - 0.6 * w, -1.55), (u - 0.5 * w, -0.95)),
                 bez((u - 0.5 * w, -0.95), (u - 0.38 * w, -0.4), (u + 0.15, -0.1), (u + 0.55, 0.4)))


def desc_loop_right(u):
    """descending loop on the right of a stem at u (f, q): round the bottom to the right, up to the stem at the
    baseline, then the exit hairline"""
    return chain(bez((u, -1.1), (u, -1.5), (u + 0.38, -1.45), (u + 0.32, -0.85)),
                 bez((u + 0.32, -0.85), (u + 0.28, -0.4), (u + 0.12, -0.1), (u + 0.03, 0.03)),
                 bez((u + 0.03, 0.03), (u + 0.2, 0.06), (u + 0.42, 0.3), (u + 0.52, 0.6)))


def bowl_tick(u, top=0.88):
    """the small loop that closes b, v and w at the x-height on the right (u = where the rising hairline ends), then
    the exit"""
    return chain(bez((u, top), (u + 0.02, top + 0.15), (u - 0.18, top + 0.13), (u - 0.17, top + 0.02)),
                 bez((u - 0.17, top + 0.02), (u - 0.08, top - 0.06), (u + 0.08, top - 0.06), (u + 0.25, top)))


# ---- letters -------------------------------------------------------------------------------------
W = 0.58     # from stem to stem in n and h, and from the oval's left side to the stem in a, d, g, q (measured)


def _letters():
    L = {}
    L["i"] = [chain(entrance(0), stem(0, 1, 0.3), underturn_exit(0)), dot(0.02, 1.55)]
    L["u"] = [chain(entrance(0), stem(0, 1, 0.3), underturn_exit(0, reach=0.6, top=1.0)),
              chain(stem(0.6, 1, 0.3), underturn_exit(0.6))]
    L["n"] = [chain(entrance(0), stem(0, 1, 0)),
              chain(arch(0, W), stem(W, 0.65, 0.3), underturn_exit(W))]
    L["m"] = [chain(entrance(0), stem(0, 1, 0)),
              chain(arch(0, 0.55), stem(0.55, 0.65, 0)),
              chain(arch(0.55, 1.1), stem(1.1, 0.65, 0.3), underturn_exit(1.1))]
    L["a"] = [oval(0, w=W), chain(stem(W, 1, 0.3), underturn_exit(W))]
    L["o"] = [chain(oval(0, start=(0.42, 0.95)), bez((0.42, 0.95), (0.5, 0.9), (0.62, 0.86), (0.74, 0.88)))]
    L["c"] = [chain(bez((0.46, 0.78), (0.52, 0.9), (0.46, 1.0), (0.3, 1.0)),
                    bez((0.3, 1.0), (0.08, 1.0), (-0.04, 0.75), (-0.04, 0.5)),
                    bez((-0.04, 0.5), (-0.06, 0.08), (0.3, -0.06), (0.62, 0.3)))]
    L["e"] = [chain(bez((-0.5, 0.0), (-0.36, 0.12), (-0.18, 0.3), (0.0, 0.42)), bez((0.0, 0.42), (0.2, 0.55), (0.46, 0.7), (0.4, 0.92)),
                    bez((0.4, 0.92), (0.33, 1.06), (0.0, 1.0), (-0.04, 0.5)),
                    bez((-0.04, 0.5), (-0.06, 0.08), (0.3, -0.06), (0.62, 0.3)))]
    L["l"] = [chain(asc_loop(0), stem(0.0, 2.2, 0.3), underturn_exit(0.0))]
    L["t"] = [chain(bez((-0.5, 0.0), (-0.38, 0.6), (-0.2, 1.35), (0.0, 1.65)), stem(0.0, 1.65, 0.3), underturn_exit(0.0)),
              line((-0.25, 1.06), (0.32, 1.06))]
    L["b"] = [chain(asc_loop(0), stem(0, 2.2, 0.3), underturn_exit(0, reach=0.5, top=0.88), bowl_tick(0.5))]
    L["d"] = [oval(0, w=W), chain(stem(W, 1.95, 0.3), underturn_exit(W))]
    L["h"] = [chain(asc_loop(0), stem(0, 2.2, 0)),
              chain(arch(0, W), stem(W, 0.65, 0.3), underturn_exit(W))]
    L["k"] = [chain(asc_loop(0), stem(0, 2.2, 0)),
              chain(bez((0, 0.45), (0.05, 0.9), (0.52, 1.12), (0.5, 0.82)),
                    bez((0.5, 0.82), (0.48, 0.6), (0.22, 0.5), (0.06, 0.5)),
                    bez((0.06, 0.5), (0.3, 0.52), (0.42, 0.5), (0.42, 0.3)), underturn_exit(0.42))]
    L["f"] = [chain(asc_loop(0, w=0.75), stem(0, 2.2, -1.1), desc_loop_right(0))]
    L["g"] = [oval(0, w=W), chain(stem(W, 1, -1.1), desc_loop(W))]
    L["j"] = [chain(entrance(0), stem(0, 1, -1.1), desc_loop(0)), dot(0.02, 1.55)]
    L["p"] = [chain(bez((-0.5, 0.0), (-0.38, 0.5), (-0.16, 1.05), (0.0, 1.3)), stem(0, 1.3, -1.5)),
              chain(arch(0, W), stem(W, 0.65, 0.3), bez((W, 0.3), (W, -0.06), (0.14, -0.08), (0.02, 0.14)))]
    L["q"] = [oval(0, w=W), chain(stem(W, 1, -1.1), desc_loop_right(W))]
    L["r"] = [chain(bez((-0.5, 0.0), (-0.36, 0.5), (-0.14, 1.12), (0.0, 1.38)),
                    bez((0.0, 1.38), (0.06, 1.2), (0.2, 1.1), (0.38, 1.12)),
                    stem(0.38, 1.12, 0.3), underturn_exit(0.38))]
    L["s"] = [chain(bez((-0.5, 0.0), (-0.24, 0.45), (0.0, 0.95), (0.12, 1.3)),
                    bez((0.12, 1.3), (0.42, 0.85), (0.6, 0.45), (0.46, 0.16)),
                    bez((0.46, 0.16), (0.34, -0.07), (-0.02, -0.07), (-0.08, 0.16)),
                    bez((-0.08, 0.16), (-0.04, 0.3), (0.14, 0.26), (0.2, 0.2)))]
    L["v"] = [chain(overturn(0), stem(0, 0.9, 0.3), underturn_exit(0, reach=0.48, top=0.88), bowl_tick(0.48))]
    L["w"] = [chain(entrance(0), stem(0, 1.0, 0.3), underturn_exit(0, reach=0.55, top=1.0), stem(0.55, 1.0, 0.3),
                    underturn_exit(0.55, reach=0.46, top=0.88), bowl_tick(1.01))]
    # x: the overturn, shaded down and turned out to the x-height; then the second stroke from the top right down to the
    # bottom left, across the first (as the exemplar's arrows go)
    L["x"] = [chain(overturn(0.1), stem(0.1, 0.9, 0.3), underturn_exit(0.1, reach=0.7, top=0.95)),
              bez((0.56, 0.98), (0.36, 0.78), (0.0, 0.25), (-0.36, 0.02))]
    L["y"] = [chain(overturn(0), stem(0, 0.9, 0.3), underturn_exit(0, reach=0.6, top=1.0)), chain(stem(0.6, 1, -1.1), desc_loop(0.6))]
    L["z"] = [chain(bez((-0.22, 0.72), (-0.12, 1.02), (0.3, 1.08), (0.42, 0.9)),
                    bez((0.42, 0.9), (0.48, 0.72), (0.2, 0.26), (0.0, 0.12)),
                    bez((0.0, 0.12), (0.2, 0.3), (0.42, 0.22), (0.42, -0.1)), stem(0.42, -0.1, -1.1), desc_loop(0.42))]
    # digits stand on the baseline and reach 1.8 x-heights (between the x-height and the ascender line)
    L["0"] = [chain(bez((0.5, 1.6), (0.38, 1.9), (0.0, 1.85), (-0.05, 0.9)),
                    bez((-0.05, 0.9), (-0.08, 0.0), (0.38, -0.06), (0.5, 0.6)),
                    bez((0.5, 0.6), (0.58, 1.1), (0.58, 1.45), (0.5, 1.6)))]
    L["1"] = [chain(bez((-0.28, 1.25), (-0.12, 1.45), (0.0, 1.65), (0.06, 1.8)), stem(0.06, 1.8, 0.0))]
    L["2"] = [chain(bez((-0.12, 1.35), (-0.05, 1.82), (0.55, 1.95), (0.52, 1.45)),
                    bez((0.52, 1.45), (0.48, 1.0), (0.05, 0.45), (-0.2, 0.05)),
                    bez((-0.2, 0.05), (0.05, 0.18), (0.3, -0.05), (0.55, 0.08)))]
    L["3"] = [chain(bez((-0.1, 1.5), (0.05, 1.9), (0.6, 1.9), (0.5, 1.4)),
                    bez((0.5, 1.4), (0.44, 1.1), (0.22, 1.02), (0.12, 1.0)),
                    bez((0.12, 1.0), (0.45, 0.95), (0.55, 0.6), (0.45, 0.3)),
                    bez((0.45, 0.3), (0.32, -0.06), (-0.1, -0.08), (-0.18, 0.25)))]
    L["4"] = [chain(line((0.42, 1.8), (-0.12, 0.6)), line((-0.12, 0.6), (0.62, 0.6))), stem(0.38, 1.25, 0.0)]
    L["5"] = [chain(stem(0.1, 1.75, 1.05),
                    bez((0.1, 1.05), (0.4, 1.2), (0.62, 0.9), (0.52, 0.45)),
                    bez((0.52, 0.45), (0.42, -0.05), (-0.05, -0.08), (-0.15, 0.25))),
              line((0.1, 1.75), (0.6, 1.78))]
    L["6"] = [chain(bez((0.52, 1.62), (0.4, 1.88), (0.0, 1.85), (-0.06, 0.9)),
                    bez((-0.06, 0.9), (-0.1, 0.0), (0.38, -0.08), (0.5, 0.4)),
                    bez((0.5, 0.4), (0.56, 0.8), (0.2, 1.0), (0.0, 0.62)))]
    L["7"] = [chain(line((-0.15, 1.72), (0.62, 1.8)), bez((0.62, 1.8), (0.4, 1.4), (0.2, 0.7), (0.1, 0.0)))]
    L["8"] = [chain(bez((0.5, 1.55), (0.42, 1.9), (-0.05, 1.85), (0.0, 1.45)),
                    bez((0.0, 1.45), (0.05, 1.1), (0.5, 0.8), (0.48, 0.38)),
                    bez((0.48, 0.38), (0.45, -0.06), (-0.1, -0.06), (-0.1, 0.35)),
                    bez((-0.1, 0.35), (-0.1, 0.8), (0.48, 1.1), (0.5, 1.55)))]
    L["9"] = [chain(bez((0.5, 1.55), (0.42, 1.85), (0.0, 1.85), (0.0, 1.35)),
                    bez((0.0, 1.35), (0.0, 0.9), (0.42, 0.9), (0.52, 1.3)), stem(0.52, 1.3, 0.25), bez((0.52, 0.25), (0.52, -0.06), (0.15, -0.08), (0.02, 0.12)))]
    return {k: L[k] for k in sorted(L)}


# ---- capitals ------------------------------------------------------------------------------------------------------
# The capitals of the English Roundhand copybooks (Bickham's Universal Penman and the writing masters it collects) as
# today's teaching sheets give them (the exemplar measured above among them). They stand on the baseline
# and reach the ascender line, 2.5 x-heights, as on the exemplar. They are drawn on a grid 2.2 high (CAP) and scaled
# up to CAP_HEIGHT whole. They follow
# the same rule as the small letters: authored strokes in writing order, shaded only where the pen moves down along the
# slant. They are built from a few capital strokes:
#   the capital stem: a shaded compound curve down the slant whose foot sweeps left along the baseline and turns up
#     into a ball (B, F, H, I, K, P, R, T);
#   the reverse oval that opens many capitals: begun inside on the right, shaded down, round the bottom, up the left
#     side and over the top to the right (B, F, I, J, T, U, V, W, X, Y, Z);
#   the looped entry of H and K: a hairline rising from the left, over the top into the stem;
#   the large oval: closed in an inner loop (O, Q), or begun in a hook at the top right and ended in a ball (C, G; E
#     is its double form);
#   the hairline entrance begun with a little shaded hook (A, M, N).
# T and F carry their wavy top a little above the capital height, as in the copybooks (they take no accent). A few
# capitals are a little narrower than the exemplar's where the copy game's slant mark needs it (the foot of T, F and H,
# the hook of A, the loop of Y): written wider, a letter leaned 0.45 off no longer fits the sheet well enough for the
# mark to name the lean.
CAP = 2.2                       # the grid the capitals are drawn on (in x-heights) ...
CAP_HEIGHT = 2.5                # ... and the height they are written at: the exemplar's, the ascender line


def cap_head(u, top=CAP, reach=1.0):
    """the looped entry of H and K: from inside on the left a hairline rising up the left side, over the top to the
    right, into the head of the stem at u"""
    return chain(bez((u - 0.8 * reach, top - 0.72), (u - 1.12 * reach, top - 0.5), (u - 1.05 * reach, top - 0.02), (u - 0.6 * reach, top)),
                 bez((u - 0.6 * reach, top), (u - 0.3 * reach, top + 0.01), (u - 0.05, top + 0.03), (u + 0.2, top)))


def cap_stem(u, top=CAP, lean=0.2, foot=1.0):
    """the capital stem: a compound curve shaded down along the slant from (u + lean, top), its foot sweeping left along
    the baseline and turning up into a ball on the left (foot = how far it sweeps, in x-heights)"""
    f = foot
    return chain(bez((u + lean, top), (u + 0.35 * lean, top - 0.6), (u - 0.03, 1.1), (u, 0.42)),
                 bez((u, 0.42), (u + 0.01, 0.02), (u - 0.45 * f, -0.06), (u - 0.78 * f, 0.08)),
                 bez((u - 0.78 * f, 0.08), (u - 1.02 * f, 0.2), (u - 0.98 * f, 0.56), (u - 0.78 * f, 0.55)),
                 bez((u - 0.78 * f, 0.55), (u - 0.62 * f, 0.54), (u - 0.6 * f, 0.36), (u - 0.7 * f, 0.3)))


def rev_oval(u, top, w=0.6, h=1.0):
    """the reverse oval: begun inside on the right, shaded down, round the bottom to the left, up the left side as a
    hairline and over the top, ending at the top heading right (u = its middle, w its width, h its height)"""
    return chain(bez((u + 0.3 * w, top - 0.28 * h), (u + 0.32 * w, top - 0.7 * h), (u + 0.12 * w, top - h), (u - 0.15 * w, top - h)),
                 bez((u - 0.15 * w, top - h), (u - 0.55 * w, top - h), (u - 0.62 * w, top - 0.35 * h), (u - 0.32 * w, top - 0.08 * h)),
                 bez((u - 0.32 * w, top - 0.08 * h), (u - 0.12 * w, top + 0.02 * h), (u + 0.25 * w, top + 0.01 * h), (u + 0.55 * w, top - 0.03 * h)))


def big_oval(top=CAP - 0.02):
    """the large capital oval, written as O: from the top, shaded down the left side, round the bottom, up the right
    side as a hairline and over the top again, crossing the start and closing in an inner loop down the left inside"""
    return chain(bez((0.45, top), (0.0, top + 0.02), (-0.3, 1.6), (-0.27, 1.0)),
                 bez((-0.27, 1.0), (-0.24, 0.25), (0.15, -0.03), (0.5, -0.02)),
                 bez((0.5, -0.02), (0.95, 0.0), (1.12, 0.7), (1.05, 1.35)),
                 bez((1.05, 1.35), (1.0, 1.95), (0.8, top + 0.02), (0.6, top - 0.06)),
                 bez((0.6, top - 0.06), (0.35, top - 0.2), (0.12, 1.75), (0.25, 1.38)))


def c_oval():
    """the oval of C and G: from inside, up into the hook at the top right, over the top, shaded down the left side,
    round the bottom and up the right, ending in a ball"""
    return chain(bez((0.6, 1.55), (0.78, 1.72), (1.05, 2.06), (0.85, 2.18)), bez((0.85, 2.18), (0.6, 2.3), (0.08, 2.15), (-0.1, 1.5)),
                 bez((-0.1, 1.5), (-0.3, 0.7), (-0.05, -0.03), (0.4, -0.03)), bez((0.4, -0.03), (0.75, -0.03), (0.95, 0.25), (0.9, 0.5)),
                 bez((0.9, 0.5), (0.85, 0.7), (0.6, 0.66), (0.62, 0.46)))


def top_bar(top=2.3):
    """the top of T and F: the reverse oval and the wavy hairline over the stem, rising at its end (it stands a
    little above the capital height, as in the copybooks)"""
    return chain(rev_oval(-0.55, top, w=0.5, h=1.05),
                 bez((-0.27, top - 0.03), (0.05, top + 0.15), (0.5, top - 0.17), (0.7, top - 0.11)),
                 bez((0.7, top - 0.11), (0.85, top - 0.07), (0.97, top - 0.01), (1.02, top + 0.09)))


def _capitals():
    L = {}
    # A: the shaded hook at the start, the hairline left side up to the apex; the shaded right side; the looped bar
    L["A"] = [chain(bez((-1.0, 0.55), (-1.1, 0.28), (-1.03, 0.02), (-0.75, 0.02)), bez((-0.75, 0.02), (-0.4, 0.04), (0.25, 1.3), (0.62, CAP))),
              bez((0.66, CAP), (0.62, 1.5), (0.56, 0.7), (0.56, 0.0)),
              chain(bez((0.12, 1.02), (-0.2, 1.02), (-0.5, 0.72), (-0.32, 0.47)), bez((-0.32, 0.47), (-0.08, 0.22), (0.6, 0.48), (1.1, 0.8)))]
    # B: the capital stem; then the reverse oval at the top left, over into the upper bowl, the loop at the waist, the
    # lower bowl and the ball inside it
    L["B"] = [cap_stem(0.0, lean=0.22),
              chain(rev_oval(-1.05, 2.05, w=0.6, h=0.95),
                    bez((-0.72, 2.02), (-0.3, 2.28), (0.55, 2.3), (0.52, 1.8)), bez((0.52, 1.8), (0.5, 1.42), (0.25, 1.22), (0.02, 1.2)),
                    bez((0.02, 1.2), (-0.28, 1.2), (-0.28, 0.97), (0.02, 1.03)),
                    bez((0.02, 1.03), (0.85, 1.1), (1.1, 0.62), (0.92, 0.28)), bez((0.92, 0.28), (0.74, -0.05), (0.32, -0.05), (0.26, 0.16)),
                    bez((0.26, 0.16), (0.22, 0.36), (0.42, 0.46), (0.48, 0.34)))]
    # C: the oval, from the hook at the top right to the ball
    L["C"] = [c_oval()]
    # D: the stem, the flat loop on the baseline, the bowl rising on the right, over the top and down in the curl on the left
    L["D"] = [chain(bez((-0.12, 1.88), (-0.04, 1.5), (0.0, 0.8), (0.0, 0.4)),
                    bez((0.0, 0.4), (0.0, 0.14), (-0.3, 0.22), (-0.62, 0.22)), bez((-0.62, 0.22), (-0.95, 0.22), (-0.9, -0.08), (-0.55, -0.06)),
                    bez((-0.55, -0.06), (0.1, -0.05), (0.92, -0.05), (0.96, 0.8)), bez((0.96, 0.8), (1.0, 1.7), (0.5, 2.25), (-0.3, 2.2)),
                    bez((-0.3, 2.2), (-1.0, 2.15), (-1.15, 1.6), (-0.95, 1.1)), bez((-0.95, 1.1), (-0.8, 0.75), (-0.5, 0.72), (-0.4, 0.88)))]
    # E: the small upper bowl from the ball at the top right, the loop at the waist, the large lower bowl, the ball
    L["E"] = [chain(bez((0.55, 1.8), (0.8, 2.0), (0.7, 2.28), (0.35, 2.22)), bez((0.35, 2.22), (-0.1, 2.15), (-0.25, 1.75), (0.0, 1.45)),
                    bez((0.0, 1.45), (0.15, 1.28), (0.35, 1.2), (0.55, 1.2)), bez((0.55, 1.2), (0.7, 1.2), (0.68, 1.04), (0.5, 1.05)),
                    bez((0.5, 1.05), (-0.2, 1.08), (-0.35, 0.5), (-0.15, 0.18)), bez((-0.15, 0.18), (0.1, -0.1), (0.75, -0.05), (0.9, 0.35)),
                    bez((0.9, 0.35), (0.95, 0.6), (0.65, 0.66), (0.62, 0.45)))]
    # F: the stem, the reverse oval and the wavy top, then the little bar across the waist
    L["F"] = [cap_stem(0.0, top=2.15, lean=0.3, foot=0.5),
              top_bar(),
              chain(bez((-0.42, 1.02), (-0.1, 1.2), (0.25, 1.08), (0.48, 1.18)), bez((0.48, 1.18), (0.58, 1.22), (0.6, 1.08), (0.56, 0.92)))]
    # G: the oval of C, open on the right; then the stem, down into the loop below the baseline
    L["G"] = [c_oval(),
              chain(bez((1.15, 1.1), (1.25, 1.18), (1.3, 1.0), (1.25, 0.6)), line((1.25, 0.6), (1.15, -1.1)), desc_loop(1.15))]
    # H: the looped entry and the stem; then the bar, begun in a curl on the left, rising across the stem into the loop
    # at the top of the second stem, which comes down and turns out
    L["H"] = [chain(cap_head(0.0), cap_stem(0.0, lean=0.2, foot=0.7)),
              chain(bez((-0.35, 0.62), (-0.6, 0.6), (-0.6, 0.92), (-0.3, 0.95)), bez((-0.3, 0.95), (0.2, 1.0), (0.6, 1.4), (0.85, 2.0)),
                    bez((0.85, 2.0), (0.95, 2.28), (1.25, 2.28), (1.2, 2.0)), bez((1.2, 2.0), (1.15, 1.5), (1.05, 0.8), (1.05, 0.3)),
                    underturn_exit(1.05, reach=0.5, top=0.8))]
    # I: the reverse oval and the top; then the stem
    L["I"] = [chain(rev_oval(-0.5, 2.15, w=0.55, h=1.15), bez((-0.2, 2.12), (-0.05, 2.18), (0.1, 2.2), (0.25, 2.2))),
              cap_stem(0.0, lean=0.3)]
    # J: as I, the stem going on down into the loop below the baseline
    L["J"] = [chain(rev_oval(-0.5, 2.15, w=0.7, h=1.35), bez((-0.12, 2.12), (0.05, 2.19), (0.2, 2.2), (0.35, 2.2))),
              chain(bez((0.35, 2.2), (0.18, 1.6), (0.05, 0.5), (0.02, -0.95)), bez((0.02, -0.95), (0.0, -1.45), (-0.42, -1.42), (-0.36, -0.9)),
                    bez((-0.36, -0.9), (-0.28, -0.45), (0.05, -0.1), (0.42, 0.28)))]
    # K: the looped entry and the stem; then the arm from the top right down to the stem, a little loop, the leg
    L["K"] = [chain(cap_head(0.0), cap_stem(0.0, lean=0.2, foot=0.95)),
              chain(bez((1.3, 2.0), (1.32, 2.25), (1.08, 2.25), (0.88, 1.95)), bez((0.88, 1.95), (0.62, 1.55), (0.35, 1.25), (0.05, 1.15)),
                    bez((0.05, 1.15), (-0.12, 1.1), (-0.08, 0.95), (0.1, 1.0)), bez((0.1, 1.0), (0.5, 1.1), (0.65, 0.8), (0.65, 0.35)),
                    underturn_exit(0.65, reach=0.5, top=0.8))]
    # L: from inside the top loop, over the top, down the stem, the flat loop on the baseline and the wavy foot
    L["L"] = [chain(bez((-0.6, 1.55), (-0.95, 1.6), (-1.0, 2.1), (-0.55, 2.2)), bez((-0.55, 2.2), (-0.2, 2.28), (0.25, 2.25), (0.15, 2.0)),
                    bez((0.15, 2.0), (0.05, 1.6), (0.0, 0.8), (0.0, 0.42)),
                    bez((0.0, 0.42), (0.0, 0.16), (-0.3, 0.24), (-0.6, 0.24)), bez((-0.6, 0.24), (-0.92, 0.24), (-0.88, -0.08), (-0.5, -0.06)),
                    bez((-0.5, -0.06), (0.0, -0.05), (0.3, 0.16), (0.7, 0.06)), bez((0.7, 0.06), (0.9, 0.0), (1.05, 0.05), (1.15, 0.2)))]
    # M: the shaded hook, a hairline up, shaded down, a hairline up, shaded down and out
    L["M"] = [chain(bez((-0.3, 0.42), (-0.4, 0.15), (-0.3, -0.02), (-0.1, 0.02)), bez((-0.1, 0.02), (0.0, 0.6), (0.0, 1.6), (0.05, CAP)),
                    bez((0.05, CAP), (0.3, 1.5), (0.6, 0.6), (0.72, 0.0)), bez((0.72, 0.0), (0.7, 0.8), (0.68, 1.6), (0.72, CAP)),
                    bez((0.72, CAP), (0.95, 1.5), (1.3, 0.6), (1.32, 0.3)), underturn_exit(1.32, reach=0.5, top=0.8))]
    # N: the shaded hook, a hairline up, the shaded diagonal down, a hairline up to the top and the curl (as wide as the
    # exemplar's, a little narrower than first drawn)
    L["N"] = [chain(bez((-0.28, 0.45), (-0.37, 0.2), (-0.28, 0.0), (-0.05, 0.05)), bez((-0.05, 0.05), (0.18, 0.7), (0.37, 1.6), (0.51, CAP)),
                    bez((0.51, CAP), (0.74, 1.5), (1.20, 0.6), (1.33, 0.0)), bez((1.33, 0.0), (1.38, 0.8), (1.43, 1.6), (1.49, 2.05)),
                    bez((1.49, 2.05), (1.55, 2.3), (1.89, 2.3), (1.89, 2.0)), bez((1.89, 2.0), (1.89, 1.75), (1.75, 1.62), (1.67, 1.78)))]
    L["O"] = [big_oval()]
    # P: the stem; then the bowl, begun on the left of the stem, up and over, down the right and back across the stem
    L["P"] = [cap_stem(0.0, lean=0.2),
              chain(bez((-0.55, 1.15), (-0.85, 1.3), (-0.8, 1.95), (-0.45, 2.12)), bez((-0.45, 2.12), (-0.05, 2.3), (0.75, 2.3), (0.7, 1.75)),
                    bez((0.7, 1.75), (0.65, 1.3), (0.25, 1.05), (-0.05, 1.08)), bez((-0.05, 1.08), (-0.15, 1.09), (-0.22, 1.1), (-0.27, 1.13)))]
    # Q: the oval of O; then the tail, from a hook on the left, under the oval and away to the right
    L["Q"] = [big_oval(),
              chain(bez((-0.55, 0.38), (-0.72, 0.1), (-0.45, -0.2), (0.0, -0.25)), bez((0.0, -0.25), (0.5, -0.3), (0.9, -0.3), (1.2, -0.2)),
                    bez((1.2, -0.2), (1.35, -0.15), (1.45, -0.05), (1.5, 0.1)))]
    # R: the stem; the bowl of P, a little loop at the stem, the leg shaded down and out
    L["R"] = [cap_stem(0.0, lean=0.2),
              chain(bez((-0.55, 1.15), (-0.85, 1.3), (-0.8, 1.95), (-0.45, 2.12)), bez((-0.45, 2.12), (-0.05, 2.3), (0.75, 2.3), (0.7, 1.75)),
                    bez((0.7, 1.75), (0.65, 1.3), (0.25, 1.05), (0.02, 1.08)), bez((0.02, 1.08), (-0.18, 1.1), (-0.18, 0.95), (0.05, 0.98)),
                    bez((0.05, 0.98), (0.45, 1.0), (0.62, 0.8), (0.62, 0.35)), underturn_exit(0.62, reach=0.5, top=0.8))]
    # S: a hairline rising from the left to the loop at the top, the shaded spine, round the bottom into the ball
    L["S"] = [chain(bez((-0.25, 0.3), (0.1, 0.8), (0.6, 1.65), (0.95, 2.12)), bez((0.95, 2.12), (1.05, 2.28), (0.6, 2.32), (0.15, 2.18)),
                    bez((0.15, 2.18), (-0.2, 2.06), (-0.22, 1.72), (0.05, 1.5)), bez((0.05, 1.5), (0.4, 1.22), (0.82, 0.85), (0.72, 0.4)),
                    bez((0.72, 0.4), (0.62, -0.04), (-0.2, -0.1), (-0.52, 0.1)), bez((-0.52, 0.1), (-0.72, 0.26), (-0.58, 0.48), (-0.45, 0.36)))]
    # T: the stem; then the reverse oval and the wavy top
    L["T"] = [cap_stem(0.0, top=2.15, lean=0.3, foot=0.5),
              top_bar()]
    # U: the reverse oval, the first stem, round the bottom and up; the second stem, down and out
    L["U"] = [chain(rev_oval(-0.5, 2.1, w=0.5, h=0.9), bez((-0.23, 2.07), (-0.05, 2.25), (0.12, 2.2), (0.12, 1.9)),
                    bez((0.12, 1.9), (0.1, 1.2), (0.02, 0.6), (0.05, 0.35)), bez((0.05, 0.35), (0.1, -0.05), (0.65, -0.08), (0.8, 0.35)),
                    bez((0.8, 0.35), (0.9, 0.8), (1.0, 1.6), (1.05, CAP))),
              chain(line((1.05, CAP), (1.0, 0.3)), underturn_exit(1.0))]
    # V: the reverse oval, the stem down to the point, a hairline up to the top right and the little hook
    L["V"] = [chain(rev_oval(-0.65, 2.1, w=0.55, h=0.9), bez((-0.35, 2.07), (-0.05, 2.25), (0.15, 2.2), (0.15, 1.9)),
                    bez((0.15, 1.9), (0.13, 1.2), (0.12, 0.4), (0.2, 0.02)), bez((0.2, 0.02), (0.55, 0.3), (0.95, 1.4), (1.05, 2.05)),
                    bez((1.05, 2.05), (1.1, 2.22), (1.02, 2.28), (0.88, 2.26)))]
    # W: the reverse oval, the first stem down, a hairline up; the second stem down, a hairline up and the hook
    L["W"] = [chain(rev_oval(-0.6, 2.1, w=0.5, h=0.9), bez((-0.33, 2.07), (-0.05, 2.25), (0.12, 2.2), (0.12, 1.9)),
                    bez((0.12, 1.9), (0.1, 1.2), (0.1, 0.4), (0.16, 0.02)), bez((0.16, 0.02), (0.45, 0.3), (0.7, 1.4), (0.8, CAP))),
              chain(bez((0.84, CAP), (0.82, 1.5), (0.78, 0.6), (0.8, 0.02)), bez((0.8, 0.02), (1.1, 0.3), (1.4, 1.4), (1.5, 2.05)),
                    bez((1.5, 2.05), (1.55, 2.22), (1.47, 2.28), (1.33, 2.26)))]
    # X: the reverse oval and the stem, turned out at the foot; then the hairline from the hook at the bottom left
    # crossing it up to the top right
    L["X"] = [chain(rev_oval(-0.65, 2.1, w=0.55, h=0.9), bez((-0.35, 2.07), (-0.05, 2.25), (0.15, 2.2), (0.15, 1.9)),
                    bez((0.15, 1.9), (0.13, 1.2), (0.08, 0.6), (0.1, 0.3)), underturn_exit(0.1, reach=0.55, top=0.75)),
              chain(bez((-0.5, 0.48), (-0.72, 0.32), (-0.6, 0.0), (-0.35, 0.05)), bez((-0.35, 0.05), (0.2, 0.3), (0.8, 1.4), (1.0, 2.0)),
                    bez((1.0, 2.0), (1.1, 2.3), (1.38, 2.25), (1.36, 2.04)))]
    # Y: the first part of U; then the stem, down into the loop below the baseline
    L["Y"] = [chain(rev_oval(-0.65, 2.1, w=0.55, h=0.9), bez((-0.35, 2.07), (-0.05, 2.25), (0.12, 2.2), (0.12, 1.9)),
                    bez((0.12, 1.9), (0.1, 1.2), (0.02, 0.6), (0.05, 0.35)), bez((0.05, 0.35), (0.1, -0.05), (0.7, -0.08), (0.85, 0.35)),
                    bez((0.85, 0.35), (0.92, 0.8), (1.0, 1.6), (1.05, CAP))),
              chain(line((1.05, CAP), (0.9, -1.1)), desc_loop(0.9, w=0.6))]
    # Z: the reverse oval, over the top and down the right, a little loop on the baseline, then the stem below the
    # baseline and its loop, the hairline rising out to the right
    L["Z"] = [chain(rev_oval(-0.3, 2.15, w=0.5, h=1.1), bez((-0.05, 2.12), (0.25, 2.2), (0.45, 2.0), (0.45, 1.7)),
                    bez((0.45, 1.7), (0.45, 1.1), (0.25, 0.6), (-0.05, 0.3)), bez((-0.05, 0.3), (-0.25, 0.12), (-0.1, -0.05), (0.15, 0.05)),
                    bez((0.15, 0.05), (0.45, 0.2), (0.55, -0.4), (0.45, -0.95)), bez((0.45, -0.95), (0.38, -1.42), (0.1, -1.42), (0.12, -1.05)),
                    bez((0.12, -1.05), (0.16, -0.6), (0.5, -0.1), (0.85, 0.35)))]
    k = CAP_HEIGHT / CAP          # drawn on the 2.2 grid, written at the exemplar's 2.5 x-heights
    return {ch: [[(k * u, k * v) for u, v in st] for st in strokes] for ch, strokes in L.items()}


# ---- accents -------------------------------------------------------------------------------------------------------
# Accented letters are the base letter followed by the accent's strokes (in copperplate, as in the copybooks, the
# accent is added after the letter). Accents above sit over the body of the letter, between 1.3 and 1.8 x-heights
# (under the ascender line); cedilla and ogonek hang below the baseline. Each accent is drawn round (u, v) = its
# anchor: the middle of the letter's body above, the foot of the body below.
ACCENTS = {
    "\u0301": lambda u: [line((u + 0.2, 1.75), (u - 0.02, 1.35))],                                   # acute: down to the left
    "\u0300": lambda u: [line((u - 0.12, 1.75), (u + 0.1, 1.38))],                                   # grave: down to the right
    "\u0302": lambda u: [chain(line((u - 0.22, 1.35), (u, 1.68)), line((u, 1.68), (u + 0.22, 1.35)))],  # circumflex
    "\u030c": lambda u: [chain(line((u - 0.22, 1.68), (u, 1.35)), line((u, 1.35), (u + 0.22, 1.68)))],  # caron
    "\u0308": lambda u: [dot(u - 0.17, 1.5), dot(u + 0.2, 1.5)],                                       # diaeresis
    "\u0303": lambda u: [bez((u - 0.27, 1.4), (u - 0.12, 1.68), (u + 0.08, 1.3), (u + 0.27, 1.6))],    # tilde
    "\u030a": lambda u: [chain(bez((u + 0.12, 1.62), (u - 0.02, 1.72), (u - 0.18, 1.6), (u - 0.12, 1.45)),
                               bez((u - 0.12, 1.45), (u - 0.06, 1.32), (u + 0.14, 1.36), (u + 0.12, 1.62)))],  # ring
    "\u0304": lambda u: [line((u - 0.24, 1.45), (u + 0.26, 1.45))],                                   # macron
    "\u0306": lambda u: [bez((u - 0.22, 1.7), (u - 0.18, 1.35), (u + 0.18, 1.35), (u + 0.24, 1.7))],  # breve
    "\u030b": lambda u: [line((u + 0.02, 1.75), (u - 0.16, 1.38)), line((u + 0.32, 1.75), (u + 0.14, 1.38))],  # double acute
    "\u0327": lambda u: [bez((u, 0.02), (u + 0.12, -0.18), (u + 0.32, -0.3), (u + 0.02, -0.48))],     # cedilla
    "\u0328": lambda u: [bez((u + 0.32, 0.02), (u - 0.02, -0.22), (u + 0.08, -0.5), (u + 0.38, -0.4))],  # ogonek
}
# where an accent above goes, per letter (u of the middle of the body, by eye on the sheet, a little left of it: the
# 55-degree shear carries an accent 1.5 x-heights up about a third of an x-height to the right): the oval letters
# over the oval, not over the stem that closes them; i where its dot was; s over its top
ANCHOR = {"a": 0.18, "c": 0.12, "e": 0.08, "i": 0.0, "n": 0.2, "o": 0.14, "r": 0.14, "s": 0.08, "u": 0.2,
          "y": 0.22, "z": 0.04}
ACCENT_BASES = "".join(ANCHOR)   # letters with no ascender, so an accent fits under the ascender line
LIFT = 0.04                      # accents above, raised a little more clear of the x-height line (body tops reach 1.05)


def _accented(letters):
    import unicodedata
    out = {}
    for base in ACCENT_BASES:
        strokes = letters[base]
        if base == "i":
            strokes = strokes[:1]            # the dotless i: the accent takes the dot's place
        body = [p for st in strokes for p in st if 0.15 <= p[1] <= 1.1]
        foot = min(body, key=lambda p: (p[1], -p[0]))[0]
        for mark, draw in ACCENTS.items():
            ch = unicodedata.normalize("NFC", base + mark)
            if len(ch) != 1:
                continue                     # no such letter in Unicode
            if mark in ("\u0327", "\u0328"):
                out[ch] = strokes + draw(foot)
            else:
                # r and s rise above the x-height (to 1.38 and 1.3): their accent sits that much higher
                acc = draw(ANCHOR[base])
                dv = max(LIFT, max(v for st in strokes for _, v in st) + 0.12 - min(v for st in acc for _, v in st))
                out[ch] = strokes + [[(u, v + dv) for u, v in st] for st in acc]
    return out


CAP_ACCENT_BASES = "ACEINORSUYZ"


def _accented_capitals(letters):
    """capitals with a cedilla or an ogonek, under the foot of the letter. At the exemplar's 2.5 x-heights the
    capitals reach the ascender line, and an accent above one would not fit on the canvas (it would reach 3 x-heights;
    a diaeresis alone would fit, crowded against the top of the letter): those are left out, and the page writes the
    small accented letter instead."""
    import unicodedata
    out = {}
    for base in CAP_ACCENT_BASES:
        strokes = letters[base]
        low = [p for st in strokes for p in st if 0.0 <= p[1] <= 0.6]
        foot = min(low, key=lambda p: (p[1], -p[0]))[0]
        for mark in ("\u0327", "\u0328"):
            ch = unicodedata.normalize("NFC", base + mark)
            if len(ch) == 1:
                out[ch] = strokes + ACCENTS[mark](foot)
    return out


LETTERS = _letters()
LETTERS.update(_accented(LETTERS))
LETTERS.update(_capitals())
LETTERS.update(_accented_capitals(LETTERS))


# ---- to canvas ------------------------------------------------------------------------------------
def _width(dx, dy):
    """pressure only while moving down along the slant"""
    sx, sy = -SLANT / math.hypot(SLANT, 1), 1 / math.hypot(SLANT, 1)      # the slant direction, going down
    n = math.hypot(dx, dy) or 1
    p = (dx * sx + dy * sy) / n
    f = min(1.0, max(0.0, (p - 0.55) / 0.4))
    return HAIR + (SHADE - HAIR) * f * f * (3 - 2 * f)                     # smooth step


def to_canvas(strokes, centre=48.0):
    """upright (u, v) strokes -> canvas strokes [(x, y, w), ...], sheared to 55 degrees and centred"""
    xy = [[(S * (u + v * SLANT), BASE_Y - S * v) for u, v in st] for st in strokes]
    xs = [x for st in xy for x, _ in st]
    shift = centre - (min(xs) + max(xs)) / 2
    out = []
    for st in xy:
        st = [(x + shift, y) for x, y in st]
        if len(st) == 1:
            out.append([(st[0][0], st[0][1], DOT)])
            continue
        pts = []
        for k, (x, y) in enumerate(st):
            a, b = st[max(0, k - 1)], st[min(len(st) - 1, k + 1)]
            pts.append((x, y, _width(b[0] - a[0], b[1] - a[1])))
        out.append(pts)
    return out


def model(ch):
    return to_canvas(LETTERS[ch])
