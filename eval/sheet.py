"""Draw a hand's model letters on its guidelines (ink as rendered for the network).
Usage: sheet.py <out.png> [letters] [hand]   (hand: copperplate, foundational, italic, ...; default copperplate)"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ductus.render import render  # noqa: E402
from gen.styles import build  # noqa: E402

if __name__ == "__main__":
    out = sys.argv[1]
    hand = build(sys.argv[3] if len(sys.argv) > 3 else "copperplate")
    letters = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "all" else "".join(hand.letters)
    letters = [hand.alias.get(ch, ch) for ch in letters if ch in hand.letters or ch in hand.alias]
    Z, per_row = 3, 13
    rows = (len(letters) + per_row - 1) // per_row
    im = Image.new("RGB", (96 * Z * min(per_row, len(letters)), 96 * Z * rows), "white")
    d = ImageDraw.Draw(im)
    for k, ch in enumerate(letters):
        x0, y0 = (k % per_row) * 96 * Z, (k // per_row) * 96 * Z
        M = render(hand.model(ch))
        ink = (255 - M["ink"] * 230).astype(np.uint8)
        im.paste(Image.fromarray(ink).resize((96 * Z, 96 * Z), Image.NEAREST).convert("RGB"), (x0, y0))
        for name, y in hand.guides().items():
            d.line([(x0, y0 + y * Z), (x0 + 96 * Z - 1, y0 + y * Z)], fill=(120, 160, 230) if name in ("baseline", "x-height", "cap height") else (200, 215, 240))
        d.rectangle([x0, y0, x0 + 96 * Z - 1, y0 + 96 * Z - 1], outline=(230, 230, 230))
        d.text((x0 + 6, y0 + 6), ch, fill=(200, 60, 60))
    im.save(out)
