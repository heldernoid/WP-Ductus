"""Drawing helpers shared by the hands: every letter is a list of pen strokes in writing order, each stroke a list of
(u, v) points in the upright frame (u to the right, v up, in x-heights; for a hand of capitals only, in capital
heights). The hand shears the frame to its slant and gives each point a width by its pen (gen/styles.py)."""
import math

from gen.copperplate import bez, chain, dot, line  # noqa: F401  (re-exported for the hands)


def arc(cx, cy, rx, ry, a0, a1, n=None):
    """points on an ellipse from angle a0 to a1 (degrees, counter-clockwise with v up)"""
    n = n or max(8, int(abs(a1 - a0) / 7))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def poly(*pts):
    """straight pieces through the points, in order (a broken stroke, as in blackletter)"""
    return chain(*[line(pts[k], pts[k + 1]) for k in range(len(pts) - 1)])


def scaled(letters, s, us=None):
    """letters scaled by s (and u by us, if given)"""
    return {ch: [[((us or s) * u, s * v) for u, v in st] for st in strokes] for ch, strokes in letters.items()}

