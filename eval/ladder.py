"""Distortion ladders: a perfect copy of each model letter, damaged in known ways, must lose points in the right
quality. Usage: ladder.py [letters]"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ductus.engine import load  # noqa: E402
from ductus.render import inputs  # noqa: E402
from gen.copperplate import BASE_Y, HAIR, LETTERS, model  # noqa: E402

NET = None


def net():
    global NET
    if NET is None:
        NET = load(os.path.join(ROOT, "arch.json"), os.path.join(ROOT, "weights", "ductus.edits"))
    return NET


# ---- distortions of a stroke list [[(x, y, w), ...], ...] ----------------------------------------
def shift(s, dx, dy=0.0):
    return [[(x + dx, y + dy, w) for x, y, w in st] for st in s]


def wobble(s, amp, seed=0):
    rng = random.Random(seed)
    out = []
    for st in s:
        ph, f = rng.uniform(0, 6.3), rng.uniform(0.25, 0.45)
        out.append([(x + amp * math.sin(f * k + ph), y + amp * math.cos(0.8 * f * k + ph), w) for k, (x, y, w) in enumerate(st)])
    return out


def reverse_stroke(s, i=0):
    return [st[::-1] if k == i else st for k, st in enumerate(s)]


def swap_order(s):
    return s[::-1]


def constant_width(s, w=1.8):
    return [[(x, y, w) for x, y, _ in st] for st in s]


def all_thick(s, w=4.0):
    return constant_width(s, w)


def drop_stroke(s, i=-1):
    return [st for k, st in enumerate(s) if k != (i % len(s))] if len(s) > 1 else [s[0][: len(s[0]) // 2]]


def stray(s, length=20):
    """an extra hairline in the empty top-left corner, 20 px long (or `length`)"""
    n = max(2, int(length // 2))
    return s + [[(4 + 2 * j * length / (2 * n), 12 - 2 * j * length / (2 * n) * 0.3, HAIR) for j in range(n + 1)]]


def slant(s, k):
    """lean k px further right per px of height (negative: more upright), about the baseline"""
    return [[(x + k * (BASE_Y - y), y, w) for x, y, w in st] for st in s]


def scale(s, f):
    """f times the size, about the middle of the baseline"""
    return [[(48 + f * (x - 48), BASE_Y + f * (y - BASE_Y), w) for x, y, w in st] for st in s]


def score(model_s, attempt_s, pressure=True, copy=False):
    T = net().forward(inputs(model_s, attempt_s, pressure, copy))
    if copy:
        T["overall_pressure"], T["overall_no_pressure"] = T["overall_copy_pressure"], T["overall_copy_no_pressure"]
    return {k: round(100 * T[k]) for k in ("shape", "ductus", "shading", "form", "overall_pressure", "overall_no_pressure")} | \
        {k: round(T[k], 2) for k in ("stay", "cover", "direction", "order_slip", "shade_hit", "hair_slip", "lean_gap", "size2")}


LADDERS = [
    ("perfect copy", lambda s: s),
    ("shift 2 px", lambda s: shift(s, 2)),
    ("shift 4 px", lambda s: shift(s, 4)),
    ("shift 6 px", lambda s: shift(s, 6)),
    ("wobble 1 px", lambda s: wobble(s, 1)),
    ("wobble 3 px", lambda s: wobble(s, 3)),
    ("first stroke reversed", reverse_stroke),
    ("stroke order swapped", swap_order),
    ("no shading (1.8 px)", constant_width),
    ("all thick (4 px)", all_thick),
    ("last stroke missing", drop_stroke),
    ("stray stroke", stray),
]

if __name__ == "__main__":
    letters = sys.argv[1] if len(sys.argv) > 1 else "".join(LETTERS)
    for ch in letters:
        m = model(ch)
        print(f"\n{ch}   {'':24s} shape ductus shading | overall(pen) overall(mouse) | stay cover dir order_slip shade_hit hair_slip")
        for name, f in LADDERS:
            r = score(m, f(m))
            print(f"    {name:26s} {r['shape']:5d} {r['ductus']:6d} {r['shading']:7d} | {r['overall_pressure']:12d} {r['overall_no_pressure']:14d} | "
                  f"{r['stay']:4} {r['cover']:5} {r['direction']:3} {r['order_slip']:10} {r['shade_hit']:9} {r['hair_slip']:9}")
