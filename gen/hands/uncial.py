"""Uncial: round, wide unicase book letters written with a broad pen held at a low angle.

Measured on an Uncial exemplar sheet (numbered ductus arrows; the guide lines are 95.5 px apart):

  | measure                           | px            | in x-heights (= letter height)             |
  |-----------------------------------|---------------|--------------------------------------------|
  | x-height (= capital height)       | 95.5          | 1                                          |
  | ascender (d h k l, F's arm)       | 120-124       | 1.26-1.30                                  |
  | descender (j, then y g p)         | 31; 24; 23; 22| 0.32; 0.25; 0.24; 0.23 (q's tail 0.2, x 0.12) |
  | stem across (i, l, t, h)          | 20-22         | 0.22                                       |
  | level stroke (t's bar, l's foot)  | 9-11          | 0.10                                       |
  | nib width  sqrt(21^2 + 10^2)      | 23.3          | 0.244, so the x-height is 4.1 nib widths   |
  | nib angle  atan(10 / 21)          |               | 25° (thinnest at the o's upper left)       |
  | slant                             |               | 0° (upright)                               |
  | ink widths: n 1.07, o 1.22, m 1.75, w 1.76, a 1.40, u 1.45, h 1.19, l 0.87, s 0.94 |  |  |

Forms and stroke order follow the sheet's arrows: the a-shaped A with its heavy diagonal first (beaked at the top, a
flick at the foot), then the thin leg and the hairline bowl; B stem, upper bowl, lower bowl, base; C, E, G, S a round
bow and a head that ends in a drop; the round d with an ascender hooked at the top and swept over to the right; F
standing on the line with a wave-shaped arm at the ascender; the h-shaped H; i and j with a hairline above; the
m-shaped M of a c-shaped bow, an arched middle stem and an h-like arch; N with a heavy diagonal; P and Y below the
line; Q's tail sweeping right under the line; U as a flagged bar, a round bow and a stem; V, W, X, Y with a hooked
entry into the heavy diagonal. Stems start with the flag the sheet shows: the pen moves up to the right along its own
edge (a hairline wedge) and turns down. Points are centre lines of the nib in x-heights; the ink reaches about 0.11
beyond them sideways on a stem and 0.05 above and below a level stroke.
"""
from gen.pen import arc, bez, chain, dot, line  # noqa: F401


def stem(u, top, bot, flag=0.12):
    """a downstroke at u from top to bot, entered by a flag: the pen moves in from the left, curving up into the top of
    the stem (a wedge, thickest where it runs level), and turns down"""
    st = line((u, top), (u, bot))
    if flag:
        st = chain(bez((u - flag, top - 0.07), (u - 0.6 * flag, top - 0.065), (u - 0.25 * flag, top - 0.04), (u, top)), st)
    return st


def hooked(u0, v0, u1, v1, tail=None):
    """a heavy diagonal entered by a small hook from the left (V, W, X, Y, A): from (u0, v0) to (u1, v1)"""
    st = chain(bez((u0 - 0.28, v0 - 0.09), (u0 - 0.18, v0 - 0.02), (u0 - 0.08, v0 + 0.01), (u0, v0)), line((u0, v0), (u1, v1)))
    if tail:
        st = chain(st, bez((u1, v1), (u1 + 0.04, v1 - 0.03), (u1 + 0.1, v1 - 0.03), (tail[0], tail[1])))
    return st


def bow(u0, end):
    """the round left side of C, E, G, S-like letters: from the top at u0 to the left, round the bottom, to `end`"""
    return chain(bez((u0, 0.965), (0.32, 0.965), (0.11, 0.78), (0.11, 0.5)), bez((0.11, 0.5), (0.11, 0.2), (0.3, 0.045), (0.55, 0.045)),
                 bez((0.55, 0.045), (0.72, 0.045), (end[0] - 0.08, end[1] - 0.06), end))


def head(u0, u1):
    """the head of C, E, G, S: from u0 over the top to u1, ending in a drop down to the left"""
    return chain(bez((u0, 0.95), (u0 + 0.12, 0.985), (u0 + 0.3, 0.99), (u1, 0.94)), line((u1, 0.94), (u1 - 0.07, 0.82)))


def _letters():
    L = {}
    # A: the heavy diagonal, beaked at the top and flicked at the foot; the thin leg from it; the hairline bowl
    L["A"] = [chain(bez((0.14, 0.88), (0.24, 0.95), (0.36, 0.99), (0.49, 0.97)), line((0.49, 0.97), (1.1, 0.07)),
                    bez((1.1, 0.07), (1.15, 0.02), (1.24, 0.02), (1.34, 0.08))),
              line((0.55, 0.69), (0.04, 0.03)),
              bez((0.1, 0.05), (0.26, 0.15), (0.42, 0.23), (0.62, 0.27))]
    # B: flagged stem, upper bowl into the waist, the larger lower bowl, the base from the foot of the stem
    L["B"] = [stem(0.36, 0.98, 0.02, 0.2),
              chain(bez((0.44, 0.95), (0.6, 0.99), (0.88, 1.0), (0.93, 0.83)), bez((0.93, 0.83), (0.96, 0.7), (0.78, 0.6), (0.56, 0.6))),
              chain(bez((0.6, 0.62), (0.86, 0.62), (1.04, 0.52), (1.04, 0.35)), bez((1.04, 0.35), (1.04, 0.18), (0.96, 0.12), (0.88, 0.09))),
              bez((0.42, 0.02), (0.56, 0.03), (0.72, 0.05), (0.84, 0.07))]
    L["C"] = [bow(0.6, (0.98, 0.19)), head(0.46, 0.98)]
    # d: the bowl from its top, then the ascender: hooked at the top left, swept right and down the right side
    L["D"] = [chain(bez((0.5, 0.92), (0.3, 0.9), (0.21, 0.7), (0.21, 0.47)), bez((0.21, 0.47), (0.21, 0.18), (0.4, 0.05), (0.62, 0.05)),
                    bez((0.62, 0.05), (0.72, 0.05), (0.8, 0.07), (0.86, 0.1))),
              chain(bez((0.3, 1.29), (0.22, 1.24), (0.1, 1.18), (0.1, 1.12)), bez((0.1, 1.12), (0.3, 1.04), (0.78, 1.0), (0.94, 0.82)),
                    bez((0.94, 0.82), (1.04, 0.66), (1.04, 0.36), (0.92, 0.16)))]
    L["E"] = [bow(0.58, (1.0, 0.16)), head(0.46, 0.99), bez((0.22, 0.52), (0.45, 0.52), (0.7, 0.53), (0.96, 0.53))]
    # F: flagged stem from the ascender to the line, the wave-shaped arm, the bar
    L["F"] = [stem(0.35, 1.15, 0.0, 0.24),
              chain(bez((0.46, 1.06), (0.6, 1.14), (0.84, 1.15), (1.1, 1.13)), line((1.1, 1.13), (1.0, 1.06))),
              bez((0.46, 0.47), (0.66, 0.48), (0.88, 0.5), (1.08, 0.53))]
    # G: the bow, the head, the tail from the right side down below the line
    L["G"] = [bow(0.58, (0.82, 0.12)), head(0.46, 1.02), bez((1.04, 0.34), (1.03, 0.12), (0.93, -0.08), (0.76, -0.24))]
    # h: tall flagged stem; the arch from it, over and down to a point on the line
    L["H"] = [stem(0.22, 1.24, 0.02, 0.2),
              chain(bez((0.32, 0.8), (0.42, 0.92), (0.55, 0.96), (0.68, 0.96)), bez((0.68, 0.96), (0.98, 0.96), (1.09, 0.75), (1.09, 0.55)),
                    bez((1.09, 0.55), (1.09, 0.3), (0.96, 0.1), (0.76, 0.0)))]
    # i, j: a flagged stem (j's turns left below the line), then the hairline above, written down to the left
    L["I"] = [stem(0.3, 0.98, 0.04, 0.2), line((0.48, 1.29), (0.24, 1.11))]
    L["J"] = [chain(stem(0.4, 0.98, -0.06, 0.2), bez((0.4, -0.06), (0.4, -0.2), (0.28, -0.3), (0.08, -0.34))), line((0.6, 1.29), (0.36, 1.11))]
    # k: tall flagged stem; the arm from the upper right down to the stem; the leg out to a flick on the line
    L["K"] = [stem(0.25, 1.24, 0.02, 0.2), bez((1.03, 0.99), (0.94, 0.84), (0.62, 0.6), (0.39, 0.48)),
              chain(line((0.41, 0.5), (1.0, 0.07)), bez((1.0, 0.07), (1.06, 0.02), (1.16, 0.03), (1.24, 0.09)))]
    L["L"] = [stem(0.32, 1.24, 0.04, 0.2), chain(line((0.42, 0.045), (0.9, 0.06)), line((0.9, 0.06), (0.98, 0.12)))]
    # m: the c-shaped bow from the top; the arched middle stem from the same place; the h-like arch
    L["M"] = [chain(bez((0.46, 0.97), (0.22, 0.95), (0.11, 0.75), (0.11, 0.48)), bez((0.11, 0.48), (0.11, 0.2), (0.26, 0.05), (0.4, 0.05)),
                    bez((0.4, 0.05), (0.47, 0.05), (0.52, 0.09), (0.56, 0.14))),
              chain(bez((0.46, 0.99), (0.64, 1.0), (0.84, 0.94), (0.84, 0.7)), line((0.84, 0.7), (0.83, 0.02))),
              chain(bez((0.95, 0.84), (1.06, 0.94), (1.2, 0.97), (1.32, 0.97)), bez((1.32, 0.97), (1.56, 0.97), (1.61, 0.78), (1.61, 0.55)),
                    bez((1.61, 0.55), (1.61, 0.3), (1.44, 0.08), (1.22, 0.0)))]
    # N: flagged left stem below the line, the heavy diagonal, the short right stem down to it
    L["N"] = [stem(0.11, 1.03, -0.1, 0.1), line((0.2, 0.86), (0.94, 0.07)), stem(0.98, 1.0, 0.12, 0.14)]
    # O: wider than tall, in two halves from the top
    L["O"] = [arc(0.61, 0.51, 0.5, 0.465, 92, 268), arc(0.61, 0.51, 0.5, 0.465, 88, -88)]
    # P: flagged stem below the line, the bowl from its top, closed by a hairline from the stem
    L["P"] = [stem(0.3, 0.98, -0.2, 0.2),
              chain(bez((0.4, 0.95), (0.55, 0.99), (0.66, 0.97), (0.72, 0.97)), bez((0.72, 0.97), (0.98, 0.97), (1.11, 0.8), (1.11, 0.58)),
                    bez((1.11, 0.58), (1.11, 0.35), (0.98, 0.2), (0.84, 0.15))),
              bez((0.4, 0.07), (0.54, 0.09), (0.68, 0.12), (0.8, 0.14))]
    # Q: the bowl in two halves, then the tail sweeping right under the line
    L["Q"] = [arc(0.62, 0.52, 0.5, 0.47, 92, 268), arc(0.62, 0.52, 0.5, 0.47, 88, -70),
              chain(line((0.66, 0.03), (1.5, -0.17)), line((1.5, -0.17), (1.6, -0.14)))]
    # R: flagged stem; the bowl back into the stem; the long leg with a flat foot
    L["R"] = [stem(0.17, 0.98, 0.02, 0.17),
              chain(bez((0.26, 0.95), (0.4, 0.99), (0.52, 0.97), (0.62, 0.97)), bez((0.62, 0.97), (0.85, 0.97), (0.95, 0.86), (0.94, 0.74)),
                    bez((0.94, 0.74), (0.93, 0.56), (0.66, 0.44), (0.4, 0.41))),
              chain(bez((0.3, 0.37), (0.55, 0.32), (0.75, 0.16), (0.95, 0.07)), bez((0.95, 0.07), (1.05, 0.03), (1.18, 0.04), (1.3, 0.08)))]
    # S: the spine from the top round the upper left, across and round the lower right; the head; the base from the left
    L["S"] = [chain(bez((0.6, 0.965), (0.3, 0.965), (0.12, 0.88), (0.17, 0.74)), bez((0.17, 0.74), (0.22, 0.6), (0.5, 0.54), (0.7, 0.44)),
                    bez((0.7, 0.44), (0.88, 0.35), (0.92, 0.2), (0.8, 0.1)), bez((0.8, 0.1), (0.75, 0.06), (0.7, 0.05), (0.64, 0.045))),
              head(0.5, 0.98),
              bez((0.05, 0.16), (0.2, 0.07), (0.38, 0.04), (0.6, 0.045))]
    # T: the stem first, then the bar from the left, rising to a point
    L["T"] = [chain(line((0.53, 0.95), (0.54, 0.08)), bez((0.54, 0.08), (0.54, 0.04), (0.58, 0.03), (0.63, 0.04))),
              chain(bez((0.02, 0.91), (0.12, 0.96), (0.22, 0.975), (0.34, 0.975)), line((0.34, 0.975), (1.0, 0.98)), line((1.0, 0.98), (1.1, 1.03)))]
    # U: the bar flagged at its left end; the bow from its middle round to the right; the flagged stem
    L["U"] = [chain(bez((0.02, 0.91), (0.12, 0.96), (0.22, 0.975), (0.34, 0.975)), line((0.34, 0.975), (0.68, 0.98))),
              chain(bez((0.6, 0.97), (0.38, 0.85), (0.29, 0.66), (0.29, 0.46)), bez((0.29, 0.46), (0.29, 0.18), (0.45, 0.05), (0.62, 0.05)),
                    bez((0.62, 0.05), (0.76, 0.05), (0.88, 0.09), (0.98, 0.15))),
              chain(stem(1.28, 0.97, 0.06, 0.14), bez((1.28, 0.06), (1.3, 0.03), (1.36, 0.03), (1.42, 0.06)))]
    # V: the hooked heavy diagonal; the right arm from a small hook at the top right, curving down to it
    L["V"] = [hooked(0.31, 0.97, 0.6, 0.04),
              chain(bez((0.93, 0.9), (1.0, 0.97), (1.07, 0.99), (1.14, 0.98)), bez((1.14, 0.98), (1.12, 0.7), (0.88, 0.36), (0.63, 0.06)))]
    # W: hooked heavy, the thin arm down to its foot, hooked heavy, the curved right arm
    L["W"] = [hooked(0.33, 0.97, 0.63, 0.04),
              line((0.96, 0.62), (0.67, 0.08)),
              hooked(0.97, 0.98, 1.27, 0.04),
              chain(bez((1.38, 0.9), (1.45, 0.97), (1.53, 0.99), (1.6, 0.98)), bez((1.6, 0.98), (1.58, 0.7), (1.52, 0.4), (1.3, 0.07)))]
    # X: the hooked heavy diagonal with a flick; the long thin one from a hook at the top right, thickening below the line
    L["X"] = [hooked(0.3, 0.98, 1.0, 0.08, (1.2, 0.11)),
              chain(bez((0.76, 0.93), (0.84, 0.98), (0.92, 0.99), (1.0, 0.98)), bez((1.0, 0.98), (0.75, 0.66), (0.4, 0.3), (0.16, 0.08)),
                    bez((0.16, 0.08), (0.1, 0.02), (0.08, -0.05), (0.1, -0.1)))]
    # Y: the hooked heavy diagonal to the middle; the stem from there below the line; the right arm down to it
    L["Y"] = [hooked(0.36, 0.98, 0.74, 0.43),
              line((0.77, 0.45), (0.77, -0.24)),
              chain(bez((1.04, 0.92), (1.12, 0.98), (1.2, 0.99), (1.28, 0.98)), bez((1.28, 0.98), (1.2, 0.8), (1.0, 0.58), (0.87, 0.46)))]
    # Z: the top bar from a small hook; the heavy diagonal down to the left; the base rising at its end
    L["Z"] = [chain(bez((0.16, 0.92), (0.24, 0.96), (0.32, 0.975), (0.42, 0.975)), line((0.42, 0.975), (1.06, 0.99))),
              line((0.98, 0.96), (0.1, 0.05)),
              chain(line((0.03, 0.025), (0.95, 0.04)), line((0.95, 0.04), (1.14, 0.1)))]
    return L


def _figures():
    """figures the height of the letters, round, wide and open, written with the same pen and flags (the old uncial
    books used Roman numerals; these are the figures modern uncial calligraphers write to sit with the hand)"""
    F = {}
    F["0"] = [arc(0.45, 0.51, 0.36, 0.465, 92, 268), arc(0.45, 0.51, 0.36, 0.465, 88, -88)]
    F["1"] = [stem(0.32, 0.97, 0.03, 0.2)]
    F["2"] = [chain(bez((0.1, 0.78), (0.2, 0.98), (0.72, 1.02), (0.74, 0.72)), bez((0.74, 0.72), (0.74, 0.5), (0.4, 0.26), (0.06, 0.05))),
              chain(line((0.1, 0.045), (0.78, 0.05)), line((0.78, 0.05), (0.88, 0.1)))]
    F["3"] = [chain(bez((0.1, 0.84), (0.24, 1.0), (0.68, 1.0), (0.66, 0.78)), bez((0.66, 0.78), (0.64, 0.6), (0.48, 0.56), (0.34, 0.56)),
                    bez((0.34, 0.56), (0.92, 0.56), (0.9, 0.045), (0.44, 0.045)), bez((0.44, 0.045), (0.26, 0.045), (0.12, 0.08), (0.04, 0.16)))]
    F["4"] = [chain(line((0.62, 0.97), (0.04, 0.3)), line((0.04, 0.3), (0.92, 0.3))), stem(0.68, 0.72, 0.03, 0.14)]
    F["5"] = [chain(line((0.18, 0.97), (0.14, 0.58)), bez((0.14, 0.58), (0.46, 0.68), (0.84, 0.62), (0.82, 0.32)),
                    bez((0.82, 0.32), (0.8, 0.0), (0.24, 0.0), (0.04, 0.14))),
              line((0.22, 0.975), (0.8, 0.99))]
    F["6"] = [chain(bez((0.74, 0.95), (0.26, 0.97), (0.1, 0.66), (0.1, 0.38)), bez((0.1, 0.38), (0.1, 0.0), (0.8, 0.0), (0.8, 0.32)),
                    bez((0.8, 0.32), (0.8, 0.6), (0.3, 0.64), (0.14, 0.42)))]
    F["7"] = [chain(line((0.06, 0.975), (0.86, 0.98)), bez((0.86, 0.98), (0.64, 0.72), (0.46, 0.38), (0.4, 0.02)))]
    F["8"] = [chain(bez((0.7, 0.86), (0.6, 1.0), (0.14, 1.0), (0.16, 0.78)), bez((0.16, 0.78), (0.18, 0.55), (0.8, 0.52), (0.8, 0.26)),
                    bez((0.8, 0.26), (0.8, 0.0), (0.1, 0.0), (0.1, 0.26)), bez((0.1, 0.26), (0.1, 0.52), (0.72, 0.56), (0.72, 0.8)))]
    F["9"] = [chain(bez((0.76, 0.88), (0.6, 1.0), (0.1, 0.98), (0.1, 0.7)), bez((0.1, 0.7), (0.1, 0.4), (0.58, 0.38), (0.78, 0.6))),
              bez((0.82, 0.96), (0.84, 0.6), (0.74, 0.2), (0.36, 0.02))]
    return F


def letters():
    L = _letters()
    L.update(_figures())
    return L


HAND = dict(
    id="uncial", name="Uncial", family="uncial", variant=None, pen="broad", S=50, base=72, slant_deg=0, ext=(1.28, 0.3),
    start="OCEIHN", sample="ADGM", keys="ADGMN", nib_angle=25, nib=12.2, hair=1.2, dot_w=7.0, cap=1.0, unicase=True,
    about={
        "tool": "A broad-edged pen held at a low angle, about 25° on this exemplar (the old books go as flat as 10-20°), "
                "so stems are heavy, level strokes about half as thick, and the thinnest point of a round letter is at its "
                "upper left.",
        "slant": "Upright.",
        "proportions": "About 4 nib widths tall; round and wide: O 1.2 times as wide as tall, M and W 1.75. d, h, k, l "
                       "and F's arm rise about a quarter of the height; j, g, p, y fall about a quarter, and q's tail and x "
                       "a little.",
        "features": "Round unicase letters: the a-shaped A, the round d whose ascender hooks back over the bowl, the "
                    "h-shaped H, the three-stroke m-shaped M, the U of a flagged bar, a bow and a stem; stems start with a "
                    "flag and the heavy diagonals of A, V, W, X, Y with a hook. Simplified here: the flags are drawn as "
                    "the pen sliding along its edge, and the pen angle stays fixed (the sheet turns it steeper for N's thin "
                    "right stem and the thin leg of A, which come out heavier here).",
        "history": "The book hand of the late Roman and early Christian world, 4th to 8th centuries, grown from Roman "
                   "capitals written quickly with a broad pen; Insular scribes in Ireland and Britain carried it on, and its "
                   "cousin Half-Uncial is the hand of the Book of Kells. The figures are a modern addition."})
