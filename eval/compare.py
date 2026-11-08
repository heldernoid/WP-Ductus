"""A hand's letters drawn as the page draws them (a broad nib as the shape its edge sweeps, a square pen as squares), on
the hand's guidelines, with an exemplar crop above them at the same x-height: to check the forms, proportions and
weight against the hand's exemplar sheet letter by letter.

Usage:
  compare.py <out.png> <hand> <letters>
  compare.py <out.png> <hand> <letters> <exemplar.png> <x0,y0,x1,y1> <exemplar x-height in px>

The crop box is in the exemplar's pixels; the crop is scaled so that its x-height (capital height for a unicase hand)
matches the hand's. Only a review aid: never trace an exemplar (AGENTS.md, rule 5).
"""
import math
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from gen.styles import build  # noqa: E402

Z = 4                     # zoom: canvas pixels to image pixels
INK, GUIDE, MAIN = (20, 20, 20), (205, 215, 235), (120, 150, 220)


def nib_quads(st, hand):
    a = math.radians(hand.nib_angle)
    h = hand.nib / 2
    nx, ny = math.cos(a) * h, -math.sin(a) * h
    if len(st) == 1:
        x, y = st[0][:2]
        px, py = -ny * 0.9, nx * 0.9
        return [[(x - nx - px, y - ny - py), (x + nx - px, y + ny - py), (x + nx + px, y + ny + py), (x - nx + px, y - ny + py)]]
    return [[(x0 - nx, y0 - ny), (x0 + nx, y0 + ny), (x1 + nx, y1 + ny), (x1 - nx, y1 - ny)]
            for (x0, y0, _), (x1, y1, _) in zip(st, st[1:])]


def _hull(pts):
    pts = sorted(set(pts))
    if len(pts) < 3:
        return pts

    def half(P):
        out = []
        for p in P:
            while len(out) >= 2 and (out[-1][0] - out[-2][0]) * (p[1] - out[-2][1]) - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0]) <= 0:
                out.pop()
            out.append(p)
        return out
    lo, hi = half(pts), half(pts[::-1])
    return lo[:-1] + hi[:-1]


def square_polys(st, side):
    h = side / 2
    sq = lambda x, y: [(x - h, y - h), (x + h, y - h), (x + h, y + h), (x - h, y + h)]  # noqa: E731
    if len(st) == 1:
        return [sq(*st[0][:2])]
    return [_hull(sq(*a[:2]) + sq(*b[:2])) for a, b in zip(st, st[1:])]


def draw_letter(d, hand, strokes, ox, oy):
    P = lambda x, y: (ox + x * Z, oy + y * Z)  # noqa: E731
    for st in strokes:
        if hand.pen == "broad":
            for q in nib_quads(st, hand):
                d.polygon([P(*p) for p in q], fill=INK)
            if len(st) > 1:
                d.line([P(x, y) for x, y, _ in st], fill=INK, width=max(1, round(hand.hair * Z)))
        elif hand.pen == "mono" and getattr(hand, "square", False):
            for q in square_polys(st, hand.mono):
                d.polygon([P(*p) for p in q], fill=INK)
        else:
            for x, y, w in st:
                r = w * Z / 2
                d.ellipse([ox + x * Z - r, oy + y * Z - r, ox + x * Z + r, oy + y * Z + r], fill=INK)
            for (x0, y0, w0), (x1, y1, w1) in zip(st, st[1:]):
                d.line([P(x0, y0), P(x1, y1)], fill=INK, width=max(1, round((w0 + w1) / 2 * Z)))


def row(hand, letters):
    """the letters set side by side as in a line of writing (a gap of a third of the x-height), on the guidelines"""
    models = [hand.model(hand.alias.get(ch, ch)) for ch in letters]
    spans = []
    for m in models:
        xs = [p[0] - p[2] / 2 for st in m for p in st] + [p[0] + p[2] / 2 for st in m for p in st]
        spans.append((min(xs) - (hand.nib / 2 if hand.pen == "broad" else 0), max(xs) + (hand.nib / 2 if hand.pen == "broad" else 0)))
    gap = hand.S / 3
    width = sum(b - a for a, b in spans) + gap * (len(spans) + 1)
    im = Image.new("RGB", (max(1, round(width * Z)), 96 * Z), "white")
    d = ImageDraw.Draw(im)
    for name, y in hand.guides().items():
        d.line([(0, y * Z), (im.width, y * Z)], fill=MAIN if name in ("baseline", "x-height", "cap height") else GUIDE)
    x = gap
    for ch, m, (a, b) in zip(letters, models, spans):
        draw_letter(d, hand, m, (x - a) * Z, 0)
        d.text((x * Z, 4), ch, fill=(200, 60, 60))
        x += b - a + gap
    return im


if __name__ == "__main__":
    out, hand = sys.argv[1], build(sys.argv[2])
    letters = [ch for ch in sys.argv[3] if ch in hand.letters or ch in hand.alias]
    im = row(hand, letters)
    if len(sys.argv) > 6:
        ex = Image.open(sys.argv[4]).convert("RGB")
        box = tuple(int(v) for v in sys.argv[5].split(","))
        crop = ex.crop(box)
        f = hand.S * Z / float(sys.argv[6])
        crop = crop.resize((max(1, round(crop.width * f)), max(1, round(crop.height * f))), Image.LANCZOS)
        both = Image.new("RGB", (max(im.width, crop.width), im.height + crop.height + 8), "white")
        both.paste(crop, (0, 0))
        both.paste(im, (0, crop.height + 8))
        im = both
    im.save(out)
