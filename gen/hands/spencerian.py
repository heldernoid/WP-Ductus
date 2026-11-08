"""Spencerian (Platt Rogers Spencer's American business and ladies' hand, 19th century).

After the Spencerian authors' "Theory of Spencerian Penmanship" (1874) and "Spencerian Key to Practical Penmanship"
(1866): every letter is built from the seven principles, in the order and direction the books describe.

  1 straight line (main slant 52 degrees)       2 right curve, 3 left curve (connective slant 30 degrees)
  4 extended loop (3 spaces, crossing 1 space above the base)
  5 direct oval (capital O)    6 reversed oval    7 capital stem (with its base oval)

The unit is the "space", the height of small i. Short letters are 1 space high (r and s 1 1/4), t d p reach 2,
the loop letters and the capitals 3; the lower loops (and J, Y, Z) drop 2, p and q 1 1/2. Widths are measured in
the same space along the horizontal (the distance between the straight lines of u is one space). Turns at the top
of short letters are short and the joinings at the base angular ("semi-angular"); upstrokes are long connective
curves. Letters are authored upright (the hand shears them to 52 degrees), one unit = one space.

Measured (the 1874 Theory's plates, about 35 px a space; and an 1884 business-college letter, about 14 px a space):

  heights        short letters 1, r s 1 1/4, t d p 2, loops and capitals 3 above; loops 2, p q 1 1/2 below
                 (letter: loops 2.8-3.0 above, about 2.1 below)
  slant          main 52 degrees in the books; six shades in the letter 49-61, about 55; connectives about 30
  widths         u, n: straight lines one space apart; o, a oval about 1/2 space across the middle (plates 0.3-0.45);
                 stem capitals with their base ovals A 3.8, N 4.4, M 5.5, H 4.4, K 4.7 spaces; O 2 across the slant;
                 figures 1 1/2 high, 1 wide
  weight         letter: shades about 0.2 space, hairlines about 0.07; the plates' small letters are nearly all hairline

Set from these: S = 17.5 px a space (3 + 2 spaces fill the canvas), slant 52 degrees, hairline 1 px, shade 2.5 px (a
light hand: Spencerian shades few strokes and lightly).

Simplified here: the capitals are the books' standard forms, without flourishes; M, H, K, T and F are 2-7% narrower
than the plates so that they fit the canvas, and the figures 2, 3, 5 are narrowed to the plates' one space; shading
follows the pointed-pen rule, so every downstroke along the slant swells a little, where a Spencerian writer shades
only a few strokes (and capitals once).
"""
import math

from gen.pen import bez, chain, dot, line  # noqa: F401

K = math.tan(math.radians(38))       # the main slant, 52 degrees from the horizontal, as the hand shears it

# ---- the small letters' basic movements ----------------------------------------------------------------------------


def up(p0, p1, a=0.45, b=0.4):
    """right curve rising (second principle): leaves flat, arrives steeper"""
    du, dv = p1[0] - p0[0], p1[1] - p0[1]
    return bez(p0, (p0[0] + a * du, p0[1] + 0.08 * dv), (p1[0] - 0.12 * du, p1[1] - b * dv), p1)


def over(p0, u, top=1.0):
    """left curve rising (third principle) from p0 and a short turn over into the head of a straight line at u"""
    return chain(bez(p0, (p0[0] + 0.3 * (u - p0[0]), p0[1] + 0.62 * (top - p0[1])), (u - 0.3, top + 0.01), (u - 0.1, top + 0.01)),
                 bez((u - 0.1, top + 0.01), (u - 0.03, top + 0.01), (u, top - 0.03), (u, top - 0.16)))


def down(u, v0, v1=0.25):
    """straight line on the main slant (first principle)"""
    return line((u, v0), (u, v1))


def foot(u, u1, v1=1.0):
    """a short turn at the base of a straight line at u, then a right curve rising to (u1, v1)"""
    return chain(bez((u, 0.25), (u, -0.02), (u + 0.18, -0.04), (u + 0.36, 0.1)),
                 bez((u + 0.36, 0.1), (u + 0.5, 0.21), (u1 - 0.12 * (u1 - u), v1 - 0.35), (u1, v1)))


def tick(u, v=1.0, out=0.5):
    """the dot at the top of b, o, v, w (a slight pressure and a tiny turn), then the horizontal right curve"""
    return chain(bez((u, v - 0.02), (u + 0.01, v + 0.12), (u - 0.14, v + 0.13), (u - 0.13, v + 0.03)),
                 bez((u - 0.13, v + 0.03), (u - 0.04, v - 0.06), (u + 0.5 * out, v - 0.07), (u + out, v + 0.02)))


def loop_up(u, start=(-0.8, 0.0), top=3.0):
    """the extended loop (fourth principle): right curve from the base rising to the top, a short turn, a slight left
    curve down crossing the upstroke 1 space above the base, then straight to the base (ends at 0.25)"""
    s = (u + start[0], start[1])
    return chain(bez(s, (u - 0.45, 0.12), (u - 0.12, 0.6), (u, 1.0)),
                 bez((u, 1.0), (u + 0.18, 1.5), (u + 0.5, 2.2), (u + 0.36, top - 0.2)),
                 bez((u + 0.36, top - 0.2), (u + 0.27, top + 0.06), (u - 0.1, top + 0.06), (u - 0.18, top - 0.28)),
                 bez((u - 0.18, top - 0.28), (u - 0.24, top - 0.85), (u - 0.1, 1.45), (u, 1.0)),
                 line((u, 1.0), (u, 0.25)))


def loop_down(u, v0=1.0, out=0.8, bottom=-2.0):
    """the inverted loop: straight down from v0 past the base, a short turn at the bottom, a left curve rising on the
    left, crossing at the base line and rising on the connective slant to (u + out, 1)"""
    return chain(line((u, v0), (u, -0.9)),
                 bez((u, -0.9), (u, -1.55), (u - 0.06, bottom - 0.04), (u - 0.28, bottom + 0.04)),
                 bez((u - 0.28, bottom + 0.04), (u - 0.55, bottom + 0.2), (u - 0.5, -0.85), (u, 0.0)),
                 bez((u, 0.0), (u + 0.18, 0.42), (u + out - 0.3, 0.92), (u + out, 1.0)))


def pointed_oval(u0=0.0, top=1.0, entry=True):
    """the pointed oval of a, d, g, q: a left curve rising from the base to the top (T), back a little along it, then
    down the left side (left curve), a short turn at the base and up the right side to T on the connective slant"""
    T = (u0 + 0.42, top)
    head = chain(bez((u0 - 0.55, 0.0), (u0 - 0.45, 0.55 * top), (u0 - 0.05, 0.98 * top), T),
                 bez(T, (u0 + 0.36, top), (u0 + 0.3, top), (u0 + 0.22, 0.985 * top))) if entry else \
        bez(T, (u0 + 0.36, top), (u0 + 0.3, top), (u0 + 0.22, 0.985 * top))
    return chain(head,
                 bez((u0 + 0.22, 0.985 * top), (u0 - 0.1, 0.93 * top), (u0 - 0.32, 0.35 * top), (u0 - 0.17, 0.08)),
                 bez((u0 - 0.17, 0.08), (u0 - 0.1, -0.04), (u0 + 0.08, -0.03), (u0 + 0.15, 0.08)),
                 bez((u0 + 0.15, 0.08), (u0 + 0.26, 0.3), (u0 + 0.36, 0.65 * top), T))


def _small():
    L = {}
    E = (-0.75, 0.0)                                   # where the first curve leaves the base line
    L["i"] = [chain(up(E, (0, 1)), down(0, 1), foot(0, 0.75)), dot(0.0, 2.0)]
    L["u"] = [chain(up(E, (0, 1)), down(0, 1), foot(0, 1.0), down(1, 1), foot(1, 1.75))]
    L["w"] = [chain(up(E, (0, 1)), down(0, 1), foot(0, 1.0), down(1, 1), foot(1, 1.5), tick(1.5))]
    L["n"] = [chain(over((-0.7, 0), 0), down(0, 0.84, 0.0), over((0, 0), 1), down(1, 0.84), foot(1, 1.75))]
    L["m"] = [chain(over((-0.7, 0), 0), down(0, 0.84, 0.0), over((0, 0), 1), down(1, 0.84, 0.0), over((1, 0), 2),
                    down(2, 0.84), foot(2, 2.75))]
    L["v"] = [chain(over((-0.7, 0), 0), down(0, 0.84), foot(0, 0.5), tick(0.5))]
    L["x"] = [chain(over((-0.7, 0), 0), down(0, 0.84), foot(0, 0.75)), line((-0.35, 0.0), (0.36, 1.0))]
    L["o"] = [chain(bez((-0.6, 0.0), (-0.5, 0.6), (-0.15, 0.98), (0.28, 1.0)),
                    bez((0.28, 1.0), (-0.06, 0.95), (-0.2, 0.4), (-0.08, 0.1)),
                    bez((-0.08, 0.1), (0.0, -0.05), (0.3, -0.05), (0.37, 0.15)),
                    bez((0.37, 0.15), (0.45, 0.4), (0.42, 0.75), (0.33, 0.98)), tick(0.33))]
    L["a"] = [chain(pointed_oval(0), down(0.42, 1.0), foot(0.42, 1.17))]
    L["e"] = [chain(bez((-0.75, 0.0), (-0.4, 0.06), (0.12, 0.5), (0.12, 0.85)),
                    bez((0.12, 0.85), (0.12, 1.08), (-0.2, 1.1), (-0.24, 0.78)),
                    bez((-0.24, 0.78), (-0.27, 0.5), (-0.22, 0.2), (-0.1, 0.06)),
                    bez((-0.1, 0.06), (0.02, -0.05), (0.2, -0.04), (0.3, 0.1)),
                    bez((0.3, 0.1), (0.42, 0.28), (0.55, 0.7), (0.75, 1.0)))]
    L["c"] = [chain(up(E, (-0.02, 1.0)), line((-0.02, 1.0), (-0.02, 0.72)),
                    bez((-0.02, 0.72), (-0.02, 0.62), (0.18, 0.64), (0.2, 0.86)),
                    bez((0.2, 0.86), (0.21, 1.04), (0.0, 1.08), (-0.1, 0.95)),
                    bez((-0.1, 0.95), (-0.3, 0.7), (-0.28, 0.2), (-0.1, 0.06)),
                    bez((-0.1, 0.06), (0.02, -0.05), (0.2, -0.04), (0.3, 0.1)),
                    bez((0.3, 0.1), (0.42, 0.28), (0.55, 0.7), (0.75, 1.0)))]
    L["r"] = [chain(up(E, (0.0, 1.25)), bez((0.0, 1.25), (0.08, 1.16), (0.18, 1.1), (0.26, 1.0)),
                    bez((0.26, 1.0), (0.3, 0.97), (0.3, 0.92), (0.3, 0.84)), down(0.3, 0.84), foot(0.3, 1.05))]
    L["s"] = [chain(up(E, (0.0, 1.25)),
                    bez((0.0, 1.25), (0.0, 1.0), (0.4, 0.6), (0.36, 0.3)),
                    bez((0.36, 0.3), (0.32, -0.04), (-0.05, -0.06), (-0.17, 0.16)),
                    bez((-0.17, 0.16), (-0.12, 0.3), (0.05, 0.2), (0.14, 0.04)),
                    bez((0.14, 0.04), (0.35, 0.1), (0.6, 0.6), (0.8, 1.0)))]
    L["t"] = [chain(up(E, (-0.08, 1.0), b=0.3), bez((-0.08, 1.0), (-0.05, 1.4), (-0.01, 1.75), (0.0, 2.0)), down(0, 2.0),
                    foot(0, 0.75)), line((-0.33, 1.5), (0.67, 1.5))]
    L["d"] = [chain(pointed_oval(0), bez((0.42, 1.0), (0.45, 1.4), (0.49, 1.75), (0.5, 2.0)), down(0.5, 2.0), foot(0.5, 1.25))]
    # p: down to 1 1/2 spaces below, "retrace lightly to base line, and diverging finish like the right half of n"
    L["p"] = [chain(up((-0.8, 0.0), (0.0, 2.0), a=0.35, b=0.45), line((0.0, 2.0), (0.0, -1.5)), line((0.0, -1.5), (0.0, 0.0)),
                    over((0.0, 0.0), 1.0), down(1.0, 0.84), foot(1.0, 1.75))]
    L["q"] = [chain(pointed_oval(0), line((0.42, 1.0), (0.42, -1.1)),
                    bez((0.42, -1.1), (0.42, -1.55), (0.72, -1.6), (0.72, -1.1)),
                    bez((0.72, -1.1), (0.72, -0.6), (0.55, -0.15), (0.44, 0.0)),
                    bez((0.44, 0.0), (0.75, 0.15), (1.05, 0.55), (1.3, 1.0)))]
    L["l"] = [chain(loop_up(0), foot(0, 0.75))]
    L["b"] = [chain(loop_up(0), foot(0, 0.5), tick(0.5))]
    L["h"] = [chain(loop_up(0), line((0, 0.25), (0, 0.0)), over((0, 0), 1), down(1, 0.84), foot(1, 1.75))]
    L["k"] = [chain(loop_up(0), line((0, 0.25), (0, 0.0)),
                    bez((0, 0), (0.12, 0.75), (0.6, 1.35), (0.82, 1.2)),
                    bez((0.82, 1.2), (0.95, 1.1), (0.75, 0.95), (0.5, 0.97)),
                    bez((0.5, 0.97), (0.54, 0.9), (0.56, 0.85), (0.56, 0.75)), down(0.56, 0.75), foot(0.56, 1.3))]
    L["f"] = [chain(loop_up(0), line((0, 0.25), (0, -1.2)),
                    bez((0, -1.2), (0, -1.75), (0.3, -2.05), (0.32, -1.5)),
                    bez((0.32, -1.5), (0.33, -1.0), (0.2, 0.2), (0.02, 0.5)),
                    bez((0.02, 0.5), (0.3, 0.55), (0.65, 0.75), (1.0, 1.0)))]
    L["j"] = [chain(up(E, (0, 1)), loop_down(0)), dot(0.0, 2.0)]
    L["y"] = [chain(over((-0.7, 0), 0), down(0, 0.84), foot(0, 1.0), loop_down(1.0))]
    L["g"] = [chain(pointed_oval(0), loop_down(0.42))]
    L["z"] = [chain(over((-0.7, 0), 0), down(0, 0.84, 0.0),
                    bez((0, 0), (0.03, 0.3), (0.3, 0.38), (0.32, 0.1)),
                    bez((0.32, 0.1), (0.34, -0.2), (0.32, -0.6), (0.32, -0.9)),
                    bez((0.32, -0.9), (0.32, -1.6), (0.28, -2.05), (0.12, -1.97)),
                    bez((0.12, -1.97), (-0.08, -1.85), (-0.04, -0.9), (0.32, 0.0)),
                    bez((0.32, 0.0), (0.5, 0.42), (0.75, 0.92), (1.0, 1.0)))]
    return L


# ---- capitals and figures --------------------------------------------------------------------------------------------
# The capitals' proportions are given in the books along the page (horizontal distances, the base oval "on a slant of
# fifteen degrees"), so they are drawn here with points (x, v) on the slanted page, unslanted by `cv` into the upright
# frame the hand shears back (the same strokes, only another way of writing the coordinates).


def cv(x, v):
    return (x - K * v, v)


def B(p0, p1, p2, p3, n=18):
    return bez(cv(*p0), cv(*p1), cv(*p2), cv(*p3), n)


def S_(p0, p1):
    return line(cv(*p0), cv(*p1))


def ell(c, a, b, tilt, t0, t1, n=None):
    """an elliptic arc on the page: centre c, half-axes a (along `tilt` degrees) and b, from angle t0 to t1 (degrees;
    decreasing angles go clockwise)"""
    n = n or max(8, int(abs(t1 - t0) / 6))
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    out = []
    for k in range(n + 1):
        t = math.radians(t0 + (t1 - t0) * k / n)
        x = c[0] + a * math.cos(t) * ct - b * math.sin(t) * st
        v = c[1] + a * math.cos(t) * st + b * math.sin(t) * ct
        out.append(cv(x, v))
    return out


def ell_at(c, a, b, tilt, t):
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    t = math.radians(t)
    return (c[0] + a * math.cos(t) * ct - b * math.sin(t) * st, c[1] + a * math.cos(t) * st + b * math.sin(t) * ct)


def ell_dir(c, a, b, tilt, t, cw=True):
    """unit direction of travel on the ellipse at angle t (clockwise: decreasing t)"""
    ct, st = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    t = math.radians(t)
    dx = -a * math.sin(t) * ct - b * math.cos(t) * st
    dv = -a * math.sin(t) * st + b * math.cos(t) * ct
    n = math.hypot(dx, dv) * (-1 if cw else 1)
    return (dx / n, dv / n)


# the base oval of the capital stem: 15 degrees from the horizontal, lying to the left of the stem's foot
OVAL_A, OVAL_B, OVAL_TILT = 1.05, 0.62, 15


def stem(x0, top=3.0, end=15, full=0.0):
    """the capital stem (seventh principle) on the slant line through (x0, 0): from the top a slight left curve, then a
    right curve into the base oval (clockwise, on a slant of 15 degrees), whose upper curve finishes near the stem at
    about 1 1/4 spaces (oval angle `end`)"""
    c = (x0 - 0.62, 0.66)
    t_in = -38
    P = ell_at(c, OVAL_A, OVAL_B, OVAL_TILT, t_in)
    d = ell_dir(c, OVAL_A, OVAL_B, OVAL_TILT, t_in)
    T = (x0 + K * top, top)
    M = (x0 + K * 1.45 + 0.04, 1.45)
    return chain(B(T, (T[0] - 0.36 - 0.1 - full, top - 0.5), (M[0] + 0.3 - 0.06, M[1] + 0.42), M),
                 B(M, (M[0] - 0.3, M[1] - 0.4), (P[0] - 0.4 * d[0], P[1] - 0.4 * d[1]), P),
                 ell(c, OVAL_A, OVAL_B, OVAL_TILT, t_in, end - 360))


def finish_a(x, v=1.25, reach=1.0):
    """the finish of A and H: from the right side at height v down to the left into the opening, a short turn, and a
    right curve crossing the right side and ending a space to its right, a space high"""
    return chain(B((x, v), (x - 0.18, v - 0.2), (x - 0.62, v - 0.55), (x - 0.72, v - 0.42)),
                 B((x - 0.72, v - 0.42), (x - 0.8, v - 0.3), (x - 0.5, v - 0.3), (x - 0.1, v - 0.33)),
                 B((x - 0.1, v - 0.33), (x + 0.3, v - 0.36), (x + reach - 0.3, v - 0.33), (x + reach, v - 0.22)))


def rev_oval(xs, part=False):
    """the reversed oval (sixth principle), clockwise: from the base at xs up the left side with a full left curve to the
    top, an oval turn to the right and down the right side with a full right curve, touching the base a third of a space
    to the right of the beginning. With part=True only to the end of the upper third of the right side (V, U, Y)."""
    up_turn = chain(B((xs, 0.0), (xs - 0.28, 0.85), (xs + 0.95, 2.97), (xs + 1.75, 3.0)),
                    B((xs + 1.75, 3.0), (xs + 2.4, 3.03), (xs + 2.38, 2.4), (xs + 2.12, 2.0)))
    if part:
        return up_turn
    return chain(up_turn, B((xs + 2.12, 2.0), (xs + 1.7, 1.3), (xs + 0.62, 0.2), (xs + 0.33, 0.0)))


def _caps():
    L = {}
    # -- the stem capitals (seventh principle): A N M T F H K S L G P B R
    T3 = (K * 3, 3.0)
    L["A"] = [stem(0), chain(B(T3, (T3[0] - 0.2, 2.0), (1.85, 0.9), (1.68, 0.0))), finish_a(1.68 + 0.38 * 1.25 / 3 * 1.0 + 0.04)]
    L["N"] = [stem(0), chain(B(T3, (T3[0] - 0.2, 2.0), (1.8, 0.9), (1.66, 0.16)),
                             B((1.66, 0.16), (1.62, -0.03), (1.82, -0.05), (1.92, 0.08)),
                             B((1.92, 0.08), (2.2, 0.55), (2.45, 1.75), (3.0, 2.0)))]
    L["M"] = [stem(0), chain(B(T3, (T3[0] - 0.2, 2.0), (1.65, 0.9), (1.5, 0.16)),
                             B((1.5, 0.16), (1.46, -0.03), (1.66, -0.05), (1.76, 0.08)),
                             B((1.76, 0.08), (1.85, 0.9), (2.45, 2.75), (3.25, 3.0)),
                             B((3.25, 3.0), (3.05, 2.3), (2.65, 0.9), (2.56, 0.2)),
                             B((2.56, 0.2), (2.52, -0.03), (2.74, -0.05), (2.86, 0.08)),
                             B((2.86, 0.08), (3.05, 0.4), (3.35, 0.85), (3.7, 1.0)))]
    T25 = (K * 2.5, 2.5)

    def cap(x):                                                   # the cap of T and F
        return chain(B((x, 2.0), (x + 0.15, 2.5), (x + 0.45, 2.98), (x + 0.75, 3.0)),
                     B((x + 0.75, 3.0), (x + 0.92, 3.0), (x + 0.75, 2.6), (x + 0.55, 2.25)),
                     B((x + 0.55, 2.25), (x + 0.45, 2.05), (x + 0.68, 2.05), (x + 0.82, 2.25)),
                     B((x + 0.82, 2.25), (x + 1.1, 2.7), (x + 1.6, 3.05), (x + 2.1, 2.98)),
                     B((x + 2.1, 2.98), (x + 2.6, 2.9), (x + 2.9, 2.82), (x + 3.3, 2.95)))
    L["T"] = [stem(0, 2.5, full=0.08), cap(0.15)]
    c_f = (-0.62, 0.66)
    L["F"] = [chain(stem(0, 2.5, end=-20, full=0.08), B(ell_at(c_f, OVAL_A, OVAL_B, OVAL_TILT, -20), (1.3, 1.45), (1.38, 1.5), (1.42, 1.55)),
                    S_((1.42, 1.55), (1.3, 1.3))), cap(0.15)]
    L["H"] = [chain(B((-0.95, 0.0), (-0.3, 0.6), (1.2, 2.0), T25), stem(0, 2.5)[1:]),
              B((3.55, 3.0), (3.2, 2.0), (2.0, 0.6), (1.75, 0.0)), finish_a(2.2, 1.25)]
    L["K"] = [chain(B((-0.95, 0.0), (-0.3, 0.6), (1.2, 2.0), T25), stem(0, 2.5)[1:]),
              chain(B((3.45, 2.9), (2.85, 2.65), (1.95, 2.0), (1.45, 1.62)),
                    B((1.45, 1.62), (1.2, 1.38), (1.0, 1.25), (1.1, 1.18)),
                    B((1.1, 1.18), (1.25, 1.1), (1.6, 1.3), (1.75, 1.15)),
                    B((1.75, 1.15), (1.95, 0.9), (1.9, 0.4), (1.88, 0.18)),
                    B((1.88, 0.18), (1.86, -0.03), (2.08, -0.05), (2.2, 0.08)),
                    B((2.2, 0.08), (2.45, 0.4), (2.75, 0.85), (3.0, 1.0)))]
    # S, L, G: a right curve from the base to the top, a loop, then the stem's oval
    up_s = B((-0.4, 0.0), (0.4, 0.4), (1.6, 1.6), (2.3, 2.88))
    L["S"] = [chain(up_s, B((2.3, 2.88), (2.45, 3.2), (1.95, 3.05), (1.62, 2.15)),
                    B((1.62, 2.15), (1.35, 1.4), (2.15, 0.7), (1.6, 0.15)),
                    B((1.6, 0.15), (1.1, -0.25), (-0.3, -0.05), (-0.75, 0.45)),
                    B((-0.75, 0.45), (-0.95, 0.75), (-0.6, 1.1), (-0.1, 1.15)),
                    B((-0.1, 1.15), (0.25, 1.15), (0.5, 1.05), (0.62, 0.98)))]
    L["L"] = [chain(up_s, B((2.3, 2.88), (2.45, 3.2), (1.95, 3.05), (1.62, 2.15)),
                    B((1.62, 2.15), (1.35, 1.4), (1.95, 0.6), (1.3, 0.2)),
                    B((1.3, 0.2), (0.85, -0.05), (0.15, -0.02), (0.05, 0.15)),
                    B((0.05, 0.15), (0.0, 0.3), (0.6, 0.15), (1.0, 0.05)),
                    B((1.0, 0.05), (1.5, -0.08), (2.2, 0.0), (2.9, 1.0)))]
    L["G"] = [chain(B((-0.4, 0.0), (0.4, 0.4), (1.6, 1.6), (2.3, 2.88)), B((2.3, 2.88), (2.45, 3.2), (1.85, 3.05), (1.3, 1.9)),
                    B((1.3, 1.9), (1.0, 1.3), (0.75, 0.8), (0.95, 0.75)),
                    B((0.95, 0.75), (1.25, 0.72), (1.55, 1.2), (1.95, 1.5)),
                    stem(1.95 - K * 1.5, 1.5)[1:])]
    # P, B, R: the stem, a turn at its foot, a full left curve up to the top, the bowl to the right recrossing the stem
    top_s = (K * 2.5 + 0.1, 2.5)

    def bowl_up():
        return chain(B(top_s, (top_s[0] - 0.55, 1.8), (0.7, 0.6), (0.3, 0.12)),
                     B((0.3, 0.12), (0.05, -0.12), (-0.5, -0.05), (-0.55, 0.45)),
                     B((-0.55, 0.45), (-0.62, 1.4), (0.6, 2.95), (1.65, 3.0)),
                     B((1.65, 3.0), (2.6, 3.02), (2.75, 2.3), (2.4, 1.95)))
    L["P"] = [chain(bowl_up(), B((2.4, 1.95), (2.0, 1.55), (1.4, 1.5), (0.95, 1.55)))]
    L["B"] = [chain(bowl_up(), B((2.4, 1.95), (2.1, 1.65), (1.6, 1.55), (1.15, 1.62)),
                    B((1.15, 1.62), (1.0, 1.65), (1.0, 1.5), (1.2, 1.46)),
                    B((1.2, 1.46), (2.15, 1.3), (2.1, 0.2), (1.3, -0.12)),
                    B((1.3, -0.12), (0.8, -0.28), (0.25, -0.05), (0.32, 0.3)),
                    B((0.32, 0.3), (0.36, 0.5), (0.5, 0.62), (0.62, 0.66)))]
    L["R"] = [chain(bowl_up(), B((2.4, 1.95), (2.1, 1.65), (1.6, 1.55), (1.15, 1.62)),
                    B((1.15, 1.62), (1.0, 1.65), (1.0, 1.5), (1.2, 1.46)),
                    B((1.2, 1.46), (1.7, 1.35), (1.85, 0.6), (1.9, 0.18)),
                    B((1.9, 0.18), (1.9, -0.03), (2.1, -0.05), (2.22, 0.08)),
                    B((2.22, 0.08), (2.45, 0.4), (2.75, 0.85), (3.0, 1.0)))]
    # -- the direct-oval capitals (fifth principle): O C D E
    c_o, a_o, b_o = (1.2, 1.5), 1.72, 1.0
    t_top = math.degrees(math.atan2(b_o * math.cos(math.radians(52)), a_o * math.sin(math.radians(52))))
    inner = ell((1.5, 1.64), a_o * 0.84, b_o * 0.55, 52, t_top + 352, t_top + 545)
    L["O"] = [chain(ell(c_o, a_o, b_o, 52, t_top, t_top + 342),
                    bez(ell(c_o, a_o, b_o, 52, t_top + 342, t_top + 342)[0], ell(c_o, a_o, b_o, 52, t_top + 352, t_top + 352)[0],
                        inner[0], inner[0], 6), inner[1:])]
    L["C"] = [chain(B((2.3, 2.72), (2.0, 2.4), (1.0, 1.2), (1.0, 0.95)),
                    B((1.0, 0.95), (1.0, 0.7), (1.4, 0.85), (1.65, 1.35)),
                    B((1.65, 1.35), (1.9, 1.85), (2.0, 2.55), (2.15, 2.9)),
                    B((2.15, 2.9), (2.25, 3.1), (1.6, 3.05), (1.1, 2.75)),
                    B((1.1, 2.8), (0.2, 2.1), (-0.35, 0.8), (0.1, 0.15)),
                    B((0.1, 0.15), (0.4, -0.15), (1.0, -0.05), (1.3, 0.3)),
                    B((1.3, 0.3), (1.5, 0.55), (1.8, 0.9), (2.1, 1.0)))]
    # E (plate): a small closed loop at the top, the outer left curve down to a small loop at about 2 spaces, then a
    # direct Capital O: down the left, round the base, up the right and an inner left curve ending 1/3 space above base
    L["E"] = [chain(B((2.45, 3.0), (2.25, 2.8), (2.12, 2.45), (2.18, 2.33)),
                    B((2.18, 2.33), (2.28, 2.2), (2.62, 2.6), (2.62, 2.85)),
                    B((2.62, 2.85), (2.62, 3.1), (2.2, 3.12), (2.0, 2.85)),
                    B((2.0, 2.85), (1.8, 2.55), (1.72, 2.25), (1.75, 2.02)),
                    B((1.75, 2.02), (1.78, 1.85), (1.98, 1.85), (1.92, 1.98)),
                    B((1.92, 1.98), (1.86, 2.08), (1.7, 2.0), (1.55, 1.85)),
                    B((1.55, 1.85), (0.9, 1.6), (-0.15, 1.15), (0.0, 0.45)),
                    B((0.0, 0.45), (0.12, -0.08), (1.2, -0.1), (1.7, 0.6)),
                    B((1.7, 0.6), (2.05, 1.15), (1.9, 1.62), (1.4, 1.64)),
                    B((1.4, 1.64), (0.75, 1.6), (0.32, 1.1), (0.4, 0.36)))]
    L["D"] = [chain(B((1.95, 2.5), (1.5, 1.8), (1.2, 0.8), (0.55, 0.12)),
                    B((0.55, 0.12), (0.35, -0.05), (0.05, 0.0), (0.1, 0.18)),
                    B((0.1, 0.18), (0.15, 0.4), (0.6, 0.35), (1.0, 0.12)),
                    B((1.0, 0.12), (1.3, -0.05), (2.2, -0.1), (2.75, 0.6)),
                    B((2.75, 0.6), (3.25, 1.3), (3.4, 2.7), (2.65, 2.95)),
                    B((2.65, 2.95), (1.9, 3.2), (1.2, 2.6), (1.0, 2.1)))]
    # -- the reversed-oval capitals (sixth principle): X W V U Y Q Z
    xs = 0.0
    L["X"] = [rev_oval(xs), chain(B((xs + 3.25, 2.95), (xs + 2.55, 2.85), (xs + 1.8, 2.4), (xs + 1.68, 1.67)),
                                  B((xs + 1.68, 1.67), (xs + 1.64, 0.9), (xs + 1.5, 0.1), (xs + 1.72, 0.03)),
                                  B((xs + 1.72, 0.03), (xs + 1.95, -0.02), (xs + 2.4, 0.5), (xs + 2.75, 1.0)))]
    L["W"] = [chain(rev_oval(xs), B((xs + 0.33, 0.0), (xs + 1.2, 0.7), (xs + 2.8, 2.4), (xs + 3.42, 3.0)),
                    B((xs + 3.42, 3.0), (xs + 2.95, 2.3), (xs + 2.1, 0.8), (xs + 2.0, 0.0)),
                    B((xs + 2.0, 0.0), (xs + 2.3, 0.7), (xs + 3.0, 1.85), (xs + 3.9, 2.0)), tick_c(xs + 3.9, 2.0))]

    def down_turn(x_top, v_top, x_base):                         # a straight line on the main slant, a short turn
        return chain(S_((x_top, v_top), (x_base + 0.2 * K, 0.2)),
                     B((x_base + 0.2 * K, 0.2), (x_base + 0.02, -0.03), (x_base + 0.22, -0.05), (x_base + 0.34, 0.08)))
    v_part = chain(rev_oval(xs, True), down_turn(xs + 2.12, 2.0, xs + 2.12 - 2 * K))
    xb = xs + 2.12 - 2 * K + 0.34                                 # where the turn ends
    L["V"] = [chain(v_part, B((xb, 0.08), (xb + 0.75, 0.6), (xb + 1.1, 1.75), (xs + 3.25, 2.0)), tick_c(xs + 3.25, 2.0))]
    u_part = chain(v_part, B((xb, 0.08), (xb + 0.6, 0.5), (xb + 1.1, 1.4), (xs + 3.12, 2.0)))
    x2 = xs + 3.12 - 2 * K                                        # the second straight line's foot
    L["U"] = [chain(u_part, down_turn(xs + 3.12, 2.0, x2), B((x2 + 0.34, 0.08), (x2 + 0.55, 0.35), (x2 + 0.9, 0.85), (x2 + 1.25, 1.0)))]
    L["Y"] = [chain(u_part, loop_down(cv(xs + 3.12, 2.0)[0], 2.0, out=1.0))]
    L["Q"] = [chain(rev_oval(xs, True), B((xs + 2.12, 2.0), (xs + 1.7, 1.2), (xs + 0.9, 0.12), (xs - 0.2, 0.06)),
                    B((xs - 0.2, 0.06), (xs - 0.75, 0.02), (xs - 1.05, 0.12), (xs - 0.95, 0.3)),
                    B((xs - 0.95, 0.3), (xs - 0.85, 0.45), (xs - 0.3, 0.2), (xs + 0.4, 0.03)),
                    B((xs + 0.4, 0.03), (xs + 0.8, -0.05), (xs + 1.3, 0.3), (xs + 1.75, 1.0)))]
    zx = xs + 0.33
    L["Z"] = [chain(rev_oval(xs), B((zx, 0.0), (zx + 0.08, 0.3), (zx - 0.02, 0.52), (zx - 0.12, 0.45)),
                    B((zx - 0.12, 0.45), (zx - 0.25, 0.35), (zx + 0.2, 0.05), (zx + 0.75, 0.05)),
                    B((zx + 0.75, 0.05), (zx + 1.15, 0.05), (zx + 1.1, -0.4), (zx + 0.85, -0.8)),
                    B((zx + 0.85, -0.8), (zx + 0.4, -1.6), (zx - 0.3, -2.3), (zx - 0.42, -1.85)),
                    B((zx - 0.42, -1.85), (zx - 0.5, -1.2), (zx + 0.4, -0.2), (zx + 0.8, 0.05)),
                    B((zx + 0.8, 0.05), (zx + 1.2, 0.35), (zx + 1.5, 0.75), (zx + 1.8, 1.0)))]
    # I and J: a left curve from the base to the top, a right curve down crossing it a third of a space above the base
    L["I"] = [chain(B((0.6, 0.0), (0.4, 1.2), (1.6, 3.0), (2.25, 3.0)),
                    B((2.25, 3.0), (2.8, 3.0), (2.3, 2.0), (1.5, 1.0)),
                    B((1.5, 1.0), (0.9, 0.25), (0.2, -0.15), (-0.5, 0.05)),
                    B((-0.5, 0.05), (-1.1, 0.25), (-1.0, 1.0), (-0.3, 1.05)),
                    B((-0.3, 1.05), (0.1, 1.08), (0.4, 0.85), (0.55, 0.7)))]
    L["J"] = [chain(B((0.6, 0.0), (0.4, 1.2), (1.6, 3.0), (2.25, 3.0)),
                    B((2.25, 3.0), (2.8, 3.0), (2.2, 2.0), (1.2, 0.6)),
                    B((1.2, 0.6), (0.6, -0.3), (-0.4, -1.6), (-0.75, -1.95)),
                    B((-0.75, -1.95), (-1.05, -2.2), (-1.2, -1.85), (-0.7, -1.1)),
                    B((-0.7, -1.1), (-0.2, -0.4), (0.6, 0.6), (1.6, 1.0)))]
    # the widest capitals a little narrower than the plates (M about 7%), so that they fit the canvas at this x-height
    for ch, f in (("M", 0.93), ("H", 0.94), ("K", 0.97), ("F", 0.98), ("T", 0.98)):
        L[ch] = [[(f * u, v) for u, v in st] for st in L[ch]]
    return L


def tick_c(x, v):
    """the dot ending V and W, on the page"""
    return chain(B((x, v), (x + 0.05, v + 0.1), (x - 0.12, v + 0.14), (x - 0.12, v + 0.04)),
                 B((x - 0.12, v + 0.04), (x - 0.1, v - 0.04), (x, v - 0.06), (x + 0.12, v - 0.02)))


def _figures():
    """the figures, 1 1/2 spaces high (6 reaches 2; 7 and 9 drop half a space), a space wide"""
    L = {}
    h = 1.5
    L["0"] = [chain(B((0.95 + 0.05, h), (0.5, h + 0.02), (0.05, 0.6), (0.2, 0.12)),
                    B((0.2, 0.12), (0.35, -0.12), (0.85, 0.0), (1.05, 0.5)),
                    B((1.05, 0.5), (1.25, 1.05), (1.25, h), (0.95, h)))]
    L["1"] = [S_((K * h, h), (0.0, 0.0))]
    L["2"] = [chain(B((0.95, h), (0.75, 1.3), (0.55, 0.85), (0.6, 0.8)),
                    B((0.6, 0.8), (0.7, 0.75), (0.75, 1.35), (1.25, h)),
                    B((1.25, h), (1.75, 1.6), (1.85, 1.1), (1.2, 0.6)),
                    B((1.2, 0.6), (0.6, 0.15), (0.15, 0.1), (0.05, 0.18)),
                    B((0.05, 0.18), (0.0, 0.32), (0.4, 0.25), (0.7, 0.05)),
                    B((0.7, 0.05), (0.95, -0.05), (1.15, 0.05), (1.3, 0.33)))]
    L["3"] = [chain(B((0.95, h), (0.85, 1.25), (0.75, 1.1), (0.85, 1.12)),
                    B((0.85, 1.12), (0.95, 1.15), (1.0, 1.45), (1.3, h)),
                    B((1.3, h), (1.75, 1.55), (1.75, 1.05), (1.25, 0.85)),
                    B((1.25, 0.85), (1.1, 0.8), (1.05, 0.88), (1.2, 0.86)),
                    B((1.2, 0.86), (1.7, 0.75), (1.55, -0.05), (0.75, -0.02)),
                    B((0.75, -0.02), (0.05, 0.0), (-0.2, 0.35), (0.0, 0.6)),
                    B((0.0, 0.6), (0.15, 0.78), (0.55, 0.75), (0.75, 0.62)))]
    L["4"] = [chain(B((0.55 + K * 1.25, 1.25), (0.5 + K * 0.8, 0.8), (0.42 + K * 0.45, 0.45), (0.4 + K * 0.3, 0.3)),
                    B((0.4 + K * 0.3, 0.3), (0.9, 0.36), (1.5, 0.4), (1.95, 0.33))),
              B((1.4 + K * h, h), (1.32 + K * 1.0, 1.0), (1.22 + K * 0.5, 0.5), (1.2, 0.0))]
    L["5"] = [chain(B((0.55 + K * h, h), (0.6 + K * 1.25, 1.25), (0.62 + K * 1.1, 1.1), (0.6 + K * 1.0, 1.0)),
                    B((0.6 + K * 1.0, 1.0), (1.65, 0.85), (1.55, -0.05), (0.75, -0.02)),
                    B((0.75, -0.02), (0.05, 0.0), (-0.2, 0.35), (0.0, 0.6)),
                    B((0.0, 0.6), (0.15, 0.78), (0.55, 0.75), (0.75, 0.62))),
              S_((0.55 + K * h + 0.08, h), (0.55 + K * h + 0.75, h))]
    L["6"] = [chain(B((K * 2.0 + 0.3, 2.0), (K * 1.0 - 0.05, 1.0), (0.0, 0.3), (0.3, 0.05)),
                    B((0.3, 0.05), (0.6, -0.15), (1.3, 0.0), (1.4, 0.55)),
                    B((1.4, 0.55), (1.45, 0.95), (1.05, 1.05), (0.85, 0.9)),
                    B((0.85, 0.9), (0.65, 0.75), (0.5, 0.5), (0.45, 0.35)))]
    L["7"] = [chain(S_((0.2 + K * h, h), (0.2 + K * 1.25, 1.25)),
                    B((0.2 + K * 1.25, 1.25), (1.45, 1.45), (1.75, 1.3), (2.25, h)),
                    B((2.25, h), (1.9, 1.0), (1.05, 0.0), (K * -0.5 + 0.95, -0.5)))]
    L["8"] = [chain(B((0.95 + K * 1.0, 1.0), (1.85, 1.25), (1.95, h + 0.02), (1.65, h)),
                    B((1.65, h), (1.2, h - 0.02), (1.0, 1.2), (1.05, 0.95)),
                    B((1.05, 0.95), (1.1, 0.6), (1.4, 0.35), (1.1, 0.08)),
                    B((1.1, 0.08), (0.75, -0.15), (0.25, 0.0), (0.4, 0.35)),
                    B((0.4, 0.35), (0.55, 0.65), (1.2, 0.85), (1.45, 1.1)),
                    B((1.45, 1.1), (1.6, 1.25), (1.6, 1.4), (1.55, h)))]
    oval9 = [(u, 0.75 + 0.75 * v) for u, v in pointed_oval(0.0, entry=False)]
    oval9 = [(u + 0.55, v) for u, v in oval9]
    t9 = oval9[-1]
    L["9"] = [chain(oval9, line(t9, (t9[0], -0.5)))]
    # the plate's figures are narrow, a space wide: 2, 3, 5 drawn from their curves are a little wide, so narrowed
    for ch, f in (("2", 0.78), ("3", 0.72), ("5", 0.75), ("0", 0.9), ("8", 0.9)):
        L[ch] = [[(f * u, v) for u, v in st] for st in L[ch]]
    return L


def letters():
    L = _small()
    L.update(_caps())
    L.update(_figures())
    return L


HAND = dict(
    id="spencerian", name="Spencerian", family="spencerian", variant=None, pen="pointed", S=17.5, base=57, slant_deg=38,
    ext=(3.0, 2.0), start="iunmwoaelt", sample="Spencer", keys="ilo", hair=1.0, shade=2.5, dot_w=2.6, cap=3.0,
    about={
        "tool": "A fine, flexible pointed steel pen.",
        "slant": "52 degrees from the horizontal for the main strokes; 30 degrees for the connecting curves.",
        "proportions": "1 : 2 : 3 in spaces (the height of small i): short letters 1 space, t d p 2, loops and capitals 3; lower loops 2 below.",
        "features": "Built from seven principles: straight line, right curve, left curve, extended loop, direct oval, reversed oval and capital stem. Small letters are light and semi-angular: short turns at the top, angular joins at the base, long connecting curves. Capitals are built on ovals and the capital stem with its base oval. Simplified here: the standard capitals without flourishes, M, H, K, T and F a few per cent narrower to fit, and every downstroke swells slightly (the pen rule), where Spencerian shades only a few strokes and each capital once.",
        "history": "Platt Rogers Spencer's American hand, taught from the 1850s in the Spencerian copybooks and business colleges, and the standard American business and correspondence hand until the Palmer method replaced it around 1900."})
