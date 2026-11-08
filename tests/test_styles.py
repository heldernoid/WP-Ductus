"""The other hands (gen/styles.py): every model letter copied exactly scores 100 in both games, and damage costs the
right mark. Broad-nib and even-width hands are marked without shading (the width follows the direction, not the hand)."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "eval"))
from ductus.render import inputs, stroke_length  # noqa: E402
from gen.styles import ALPHABET, ORDER, build  # noqa: E402
from ladder import net, reverse_stroke, shift  # noqa: E402

# HAND=<id> checks one hand only (while writing it); otherwise every hand but copperplate (tests/test_ductus.py)
OTHER = [build(i) for i in (os.environ["HAND"].split(",") if os.environ.get("HAND") else ORDER) if i != "copperplate"]
CASES = [(h.id, ch) for h in OTHER for ch in h.letters]
BY = {h.id: h for h in OTHER}
FAULTS = ["f_off", "f_miss", "f_back", "f_order", "f_thin", "f_thick", "f_upright", "f_slanted", "f_big", "f_small"]


def score(h, m, a, copy):
    T = net().forward(inputs(m, a, h.pen == "pointed", copy))
    key = ("overall_copy" if copy else "overall") + ("_pressure" if h.pen == "pointed" else "_no_pressure")
    return T, T[key]


@pytest.mark.parametrize("hand,ch", CASES)
def test_perfect_copy_scores_100(hand, ch):
    h = BY[hand]
    m = h.model(ch)
    for copy in (False, True):
        T, overall = score(h, m, m, copy)
        assert round(100 * overall) == 100, (copy, overall)
        assert max(T[f] for f in FAULTS) < 1e-9


def _plain(ch):
    import unicodedata
    return unicodedata.normalize("NFD", ch) == ch


@pytest.mark.parametrize("hand,ch", [(h, c) for h, c in CASES if _plain(c) and not c.isdigit()])
def test_damage_costs_the_right_mark(hand, ch):
    h = BY[hand]
    m = h.model(ch)
    # a first stroke written backwards costs ductus (when it is a real stroke, not a dot or a short entry)
    if len(m[0]) > 1 and stroke_length(m[0]) > 0.3 * sum(stroke_length(st) for st in m):
        # at least 15 points (Modern's F and T, whose first stroke is the near-level top bar, lose 19.6)
        T, _ = score(h, m, reverse_stroke(m), False)
        assert T["ductus"] <= 0.85, T["ductus"]
    # a miss of 6 px costs shape in the trace game
    T, _ = score(h, m, shift(m, 6), False)
    assert T["shape"] <= 0.85, T["shape"]


@pytest.mark.parametrize("hand", [h.id for h in OTHER])
def test_every_hand_has_the_whole_alphabet(hand):
    h = BY[hand]
    missing = [ch for ch in ALPHABET if ch not in h.letters and ch not in h.alias]
    assert not missing, "".join(missing)
