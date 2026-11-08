"""Neuland (Rudolf Koch, 1923): heavy, blocky, angular unicase capitals, as calligraphers write them.

Measured on a Neuland exemplar sheet (numbered ductus arrows; the letters overshoot the 95.5 px guide lines a
little, so the capital height is taken from the ink):

  | measure                           | px     | in capital heights                                      |
  |-----------------------------------|--------|---------------------------------------------------------|
  | capital height (ink)              | 98     | 1                                                       |
  | descender: J's hook; Q's tail     | 25; 17 | 0.26; 0.17                                              |
  | stem across (H, I, L, T)          | 30-31  | 0.31                                                    |
  | arms and bars (E, F, T)           | 27-30  | 0.29 (C's arms 0.17-0.19, tops of B, P, R 0.12-0.2)     |
  | diagonals, across (V, X)          | 29-30  | 0.30                                                    |
  | pen (here)                        | 21.5   | 0.22: 4.5 pen widths to the capital height (see below)  |
  | slant                             |        | 0° (upright)                                            |
  | ink widths: I 0.34, S 0.52, L 0.62, C 0.77, E/F 0.73, H 0.96, N 1.05, O 1.01, A 1.23, M 1.55, W 1.59 | | |

Forms and stroke order follow the sheet's arrows: A of two splayed legs meeting in a flat top, then a low heavy bar,
leaving a small triangular counter; B, D, P, R with angular bowls (B stem, upper bowl, lower bowl); C a single "<"
stroke with level arms; E stem, top arm, bottom arm, middle arm; G a "<" stroke, a short right stem from the middle,
the top arm last; J the stem, then the hook from the left below the line; K stem, arm down to it, leg; M splayed legs
with the middle V reaching nearly to the line (left leg, V, V, right leg); O and Q in two halves round a pointed lens
counter, Q's flat tail last; narrow S in one stroke; T stem first, then the bar; U one stroke down and round, then the
right stem; V, W left to right; X the right-to-left diagonal first; Y arms and stem; Z top, diagonal, base.

The pen is one even width with a square end (`square`), 0.22 of the capital height, lighter than the sheet's 0.31
stems on purpose: the sheet's pen is turned, so its level strokes, bowl tops and the tops of O and Q are much thinner
than its stems (0.12-0.2), while one even width has to make all of them; a square end along a diagonal also leaves a
stroke up to 1.4 times as wide. At 0.31 and at 0.26 the counters of A, B, P, R closed to slits, O's lens to a small
diamond and S to a block; at 0.22 every counter is open and O keeps its tall lens (about 0.6 of the height), which
matters more for reading the forms than the stem weight. Points are the centre lines, half a pen width inside the cap
height and the baseline (T and B below), so the ink fills the capital height.
"""
import math

from gen.pen import arc, bez, chain, dot, line, poly  # noqa: F401

S = 56                               # pixels per capital height
M = 0.22                             # the pen's width in capital heights (see the docstring)
H = M / 2                            # half the pen: the centre line of a stroke whose ink edge is at 0
T, B = 1 - H, H                      # the centre lines at the top and the bottom of the letters
TO, BO = T + 0.04, B - 0.02          # ... where a bowl overshoots them a little, as on the sheet


def stem(u, top=T, bot=B):
    return line((u, top), (u, bot))


def lens(cx, hc, sc, end=None):
    """the two halves of O, Q and 0 round a pointed lens counter centred at (cx, 0.5), hc high and sc wide (halves):
    each half is an arc whose inner edge bounds the counter, from the top line round to the bottom line (the right
    half stops at angle `end` if given)"""
    R = (hc * hc + sc * sc) / (2 * sc)               # radius of the counter's edge
    Rc = R + 1.15 * H                                # the centre line, half a (square) pen outside it
    a = math.degrees(math.asin(min(1.0, (T - 0.5) / Rc)))
    x0 = cx + R - sc                                 # the left half's arc centre, right of the counter
    left = arc(x0, 0.5, Rc, Rc, 180 - a, 180 + a)
    right = arc(2 * cx - x0, 0.5, Rc, Rc, a, -a if end is None else end)
    left = chain(line((cx, T), left[0]), left, line(left[-1], (cx, B)))           # the halves meet at the top and the
    right = chain(line((cx, T), right[0]), right) if end is not None else chain(line((cx, T), right[0]), right, line(right[-1], (cx, B)))
    return [left, right]                                                          # bottom on a short level run


def _capitals():
    L = {}
    # A: left leg, right leg, both from the flat top; the low heavy bar
    L["A"] = [line((0.58, T), (H, B)), line((0.78, T), (1.2 - H, B)), line((0.25, 0.3), (1.0, 0.3))]
    # B: stem; the upper bowl from its top, out to a point and back to the waist; the larger lower bowl to the foot
    # B: stem; the upper bowl from the top, out to a point and back along the waist to the stem; the lower bowl from
    # the waist round to the foot. The bowls run level where they bound a counter and reach a little past the sheet
    # (to 0.88 and 1.0), so that the two counters stay open, the upper one smaller.
    L["B"] = [stem(H),
              poly((H + 0.05, TO), (0.5, TO), (0.88 - H, 0.72), (0.5, 0.525), (H + 0.07, 0.525)),
              poly((0.5, 0.525), (1.0 - H, 0.33), (0.66, B), (H + 0.05, B))]
    # C: one stroke, "<" with level arms
    L["C"] = [chain(line((0.75 - H, T), (0.46, T)), bez((0.46, T), (0.34, T - 0.04), (0.22, 0.66), (H, 0.5)),
                    bez((H, 0.5), (0.22, 0.34), (0.34, B + 0.04), (0.46, B)), line((0.46, B), (0.74 - H, B)))]
    L["D"] = [stem(H), poly((H + 0.05, T), (0.47, T + 0.02), (0.9 - H, 0.55), (0.6, B), (H + 0.05, B))]
    L["E"] = [stem(H), line((H + 0.05, T), (0.72 - H, T)), line((H + 0.05, B), (0.7 - H, B)), line((H + 0.05, 0.49), (0.62 - H, 0.49))]
    L["F"] = [stem(H), line((H + 0.05, T), (0.72 - H, T)), line((H + 0.05, 0.475), (0.62 - H, 0.475))]
    # G: the "<" from the top, the short right stem from the middle, the top arm last
    L["G"] = [chain(bez((0.45, T), (0.32, 0.75), (0.2, 0.6), (H, 0.5)), bez((H, 0.5), (0.24, 0.3), (0.34, B), (0.6, B))),
              stem(0.85 - H, 0.6 - H, B), line((0.3, T + 0.005), (0.85 - H, T + 0.005))]
    L["H"] = [stem(H), stem(0.95 - H), line((H + 0.05, 0.52), (0.9 - H, 0.52))]
    L["I"] = [stem(H)]
    # J: the stem, then the hook from the left below the line
    L["J"] = [stem(0.9 - H, T, 0.0),
              chain(bez((0.03 + H, 0.18 - H), (0.03 + H, 0.0), (0.2, -0.25 + H), (0.4, -0.25 + H)), line((0.4, -0.25 + H), (0.8 - H, -0.25 + H)))]
    L["K"] = [stem(H), line((0.88 - H, T), (0.36, 0.5)), line((0.42, 0.53), (1.05 - H, B))]
    L["L"] = [stem(H), line((H + 0.05, B), (0.62 - H, B))]
    # M: splayed left leg, the V down nearly to the line, splayed right leg
    L["M"] = [line((0.45, T), (H, B)), line((0.52, T), (0.8, 0.06 + H)), line((1.1, T), (0.86, 0.06 + H)), line((1.17, T), (1.55 - H, B))]
    L["N"] = [stem(H), line((0.3, T), (0.8, B)), stem(1.05 - H)]
    # O: two halves round a pointed lens counter
    L["O"] = lens(0.5, 0.33, 0.16)
    L["P"] = [stem(H), poly((H + 0.05, TO), (0.52, TO), (0.9 - H, 0.67), (0.52, 0.44), (H + 0.07, 0.44))]
    # Q: the two halves, the right one stopping above the tail; the flat tail from the lower left, down to the right
    L["Q"] = lens(0.5, 0.33, 0.16, -30) + [line((0.3, 0.06), (0.9, -0.06))]
    L["R"] = [stem(H), poly((H + 0.05, TO), (0.5, TO), (0.88 - H, 0.68), (0.5, 0.46), (H + 0.07, 0.46)),
              line((0.44, 0.4), (1.05 - H, B))]
    # S: one narrow stroke from the top right
    # S: one narrow, wavy stroke from the top right: over the top, round the upper left, down the slanting spine,
    # round the lower right and out to the lower left, open on both sides
    L["S"] = [chain(bez((0.47, 0.84), (0.42, 0.88), (0.36, T), (0.3, T)), bez((0.3, T), (0.18, T), (H, 0.82), (0.15, 0.71)),
                    line((0.15, 0.71), (0.42, 0.37)), bez((0.42, 0.37), (0.48, 0.3), (0.46, B), (0.3, B)),
                    bez((0.3, B), (0.2, B), (0.13, 0.13), (0.09, 0.17)))]
    L["T"] = [stem(0.45, 0.72, B), line((H + 0.02, T), (0.98 - H, T))]
    # U: down the left and round the bottom, then the right stem
    L["U"] = [chain(line((H, T), (H, 0.42)), bez((H, 0.42), (H, 0.22), (0.24, B), (0.42, B)), line((0.42, B), (0.68, B + 0.01))),
              stem(0.95 - H)]
    L["V"] = [line((H, T), (0.33 + H, B)), line((1.0 - H, T), (0.68 - H, B))]
    L["W"] = [line((H, T), (0.35 + H, B)), line((0.65 + H, T), (0.65 - H, B)), line((1.0 - H, T), (0.95 + H, B)), line((1.6 - H, T), (1.3 - H, B))]
    # X: the right-to-left diagonal first
    L["X"] = [line((1.02 - H, T), (H, B)), line((0.08 + H, T), (0.95 - H, B))]
    L["Y"] = [line((H + 0.02, T), (0.45, 0.47)), stem(0.49, 0.5, B), line((0.92 - H, T), (0.53, 0.47))]
    # Z: the top bar (its left end cut on a slant), the diagonal, the base (its right end cut on a slant)
    L["Z"] = [poly((0.04 + H, T - 0.1), (0.12 + H, T), (0.98 - H, T)), line((0.96 - H, T - 0.02), (H + 0.02, B + 0.02)),
              poly((H, B), (0.87 - H, B), (0.95 - H, B + 0.1))]
    return L


def _figures():
    """figures in the same blocky, angular, even weight, the height of the capitals (Koch's type has them; calligraphers
    write them with the same pen)"""
    F = {}
    F["0"] = lens(0.4, 0.33, 0.13)
    F["1"] = [chain(line((H, 0.7), (0.4, T)), line((0.4, T), (0.4, B)))]
    F["2"] = [poly((H, 0.7), (0.32, T), (0.8 - H, T), (0.8 - H, 0.62), (H, B)), line((H + 0.05, B), (0.85 - H, B))]
    F["3"] = [poly((H, T), (0.8 - H, T), (0.42, 0.56), (0.88 - H, 0.42), (0.62, B), (H, B))]
    F["4"] = [poly((0.6, T), (H, 0.3), (1.0 - H, 0.3)), stem(0.74, 0.72, B)]
    F["5"] = [poly((H + 0.03, T), (H + 0.01, 0.52), (0.6, 0.55), (0.9 - H, 0.35), (0.62, B), (H, B)), line((H + 0.07, T), (0.86 - H, T))]
    F["6"] = [poly((0.84 - H, T), (0.34, T), (H, 0.7), (H, 0.24), (0.26, BO), (0.66, BO), (0.9 - H, 0.24), (0.9 - H, 0.44), (0.66, 0.56),
                   (H + 0.07, 0.56))]
    F["7"] = [poly((H, T), (0.9 - H, T), (0.34, B))]
    F["8"] = [poly((0.45, 0.53), (H + 0.03, 0.62), (H + 0.03, 0.8), (0.24, TO), (0.62, TO), (0.84 - H, 0.8), (0.84 - H, 0.62),
                   (0.47, 0.52), (H, 0.42), (H, 0.22), (0.24, BO), (0.68, BO), (0.92 - H, 0.22), (0.92 - H, 0.42), (0.51, 0.53))]
    F["9"] = [poly((0.9 - H - 0.07, 0.44), (0.34, 0.44), (H, 0.56), (H, 0.76), (0.24, TO), (0.66, TO), (0.9 - H, 0.76), (0.9 - H, 0.3),
                   (0.6, B), (H + 0.04, B))]
    return F


def letters():
    L = _capitals()
    L.update(_figures())
    return L


HAND = dict(
    id="neuland", name="Neuland", family="neuland", variant=None, pen="mono", S=S, base=69, slant_deg=0, ext=(1.0, 0.26),
    start="ILTEHN", sample="NEU", keys="AMRS", mono=M * S, dot_w=M * S, square=True, cap=1.0, unicase=True,
    about={
        "tool": "A broad-edged pen used for weight, turned as the strokes need (or a heavy marker); modelled here as one "
                "even width with a square end, about a fifth of the capital height. The sheet's stems are nearly a "
                "third, but its turned pen makes the level strokes and the tops of the bowls much thinner; at that width "
                "one even stroke closes the counters, so the pen is lighter here to keep them open.",
        "slant": "Upright.",
        "proportions": "About 3.3 stem widths tall on the sheet (4.5 pen widths here); compact, mostly square letters with "
                       "small, angular counters; M and W "
                       "half as wide again as they are tall, S narrow.",
        "features": "Heavy, blocky capitals with almost no contrast: an A with a flat top and a low bar, angular "
                    "bowls with pointed counters, C and G as a \"<\" with level arms, a splayed M whose V reaches nearly to "
                    "the line, O with a pointed lens counter, S in one narrow stroke, J and Q with flat tails below the "
                    "line. Simplified here: the strokes are one width, lighter than the sheet's stems, so the wedge shapes "
                    "of the legs and the contrast between stems and bowl tops are left out.",
        "history": "Rudolf Koch's typeface of 1923, cut by hand at the Klingspor foundry without drawings first; "
                   "calligraphers took the forms up as a written hand. Capitals only."})
