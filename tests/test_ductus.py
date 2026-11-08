"""Checks of the hand-written network: every model letter copied exactly scores 100 in every quality, and each kind
of damage lowers the quality it should (and the tip names it)."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "eval"))
from ductus.render import stroke_length  # noqa: E402
from gen.copperplate import LETTERS, model  # noqa: E402
from gen.generate import build  # noqa: E402
from ladder import (all_thick, constant_width, drop_stroke, net, reverse_stroke, scale, score, shift, slant,  # noqa: E402
                    stray, swap_order, wobble)

FAULTS = ["f_off", "f_miss", "f_back", "f_order", "f_thin", "f_thick"]


def faults(m, a, pressure=True):
    from ductus.render import inputs
    T = net().forward(inputs(m, a, pressure))
    return {f: T[f] for f in FAULTS}


def test_weights_on_disk_match_the_generator():
    _, edits = build()
    with open(os.path.join(ROOT, "weights", "ductus.edits")) as f:
        assert f.read() == edits, "run gen/generate.py"


def test_every_bias_has_a_reason():
    _, edits = build()
    for line in edits.splitlines():
        if line.startswith("BIAS"):
            assert "#" in line, line


@pytest.mark.parametrize("ch", list(LETTERS))
def test_perfect_copy_scores_100(ch):
    m = model(ch)
    r = score(m, m)
    assert (r["shape"], r["ductus"], r["shading"], r["overall_pressure"], r["overall_no_pressure"]) == (100,) * 5
    assert max(faults(m, m).values()) < 1e-9


@pytest.mark.parametrize("ch", list(LETTERS))
def test_small_slips_are_forgiven(ch):
    m = model(ch)
    for a in (shift(m, 2), wobble(m, 1)):
        assert score(m, a)["overall_no_pressure"] >= 95


@pytest.mark.parametrize("ch", list(LETTERS))
def test_damage_lowers_the_right_quality(ch):
    m = model(ch)
    assert score(m, reverse_stroke(m))["ductus"] <= 80, "a reversed stroke must cost ductus"
    assert score(m, constant_width(m))["shading"] <= 40, "no shading must cost shading"
    assert score(m, all_thick(m))["shading"] <= 40 or ch in "4", "thick hairlines must cost shading"
    # a stray stroke a fifth as long as the letter (at least 20 px): a fixed 20 px is little beside a long capital
    long = max(20.0, 0.2 * sum(stroke_length(st) for st in m))
    assert score(m, stray(m, long))["shape"] <= 95, "a stray stroke must cost shape"
    assert score(m, shift(m, 6))["shape"] <= 75, "a 6 px miss must cost shape"
    if len(m) > 1 and stroke_length(m[-1]) > 0.2 * sum(stroke_length(st) for st in m):
        assert score(m, drop_stroke(m))["shape"] <= 95, "a missing stroke must cost shape"


def _orderly(ch):
    """letters whose order is worth marking: more than one stroke, and the strokes after the first not small (the dot
    of i and j, the bar of t, the flag of 5, the bar of A and the accents count for little in the order)"""
    import unicodedata
    base = unicodedata.normalize("NFD", ch)[0]
    if base != ch and len(model(base)) - (base in "ij") == 1:
        return False        # a one-stroke letter and its accent
    m = model(ch)
    return len(m) > 1 and sum(stroke_length(st) for st in m[1:]) > 0.3 * stroke_length(m[0])


@pytest.mark.parametrize("ch", [c for c in LETTERS if _orderly(c)])
def test_swapped_order_costs_ductus(ch):
    m = model(ch)
    # capitals: 75 (F reversed scores 74: its three strokes each move under a quarter of the letter's time)
    assert score(m, swap_order(m))["ductus"] <= (75 if ch.isupper() else 70)


def test_tips_name_the_fault():
    m = model("n")
    assert max(faults(m, reverse_stroke(m)).items(), key=lambda kv: kv[1])[0] == "f_back"
    assert max(faults(m, swap_order(m)).items(), key=lambda kv: kv[1])[0] == "f_order"
    assert max(faults(m, constant_width(m)).items(), key=lambda kv: kv[1])[0] == "f_thin"
    assert max(faults(m, all_thick(m)).items(), key=lambda kv: kv[1])[0] == "f_thick"
    assert max(faults(m, stray(m)).items(), key=lambda kv: kv[1])[0] == "f_off"
    assert max(faults(m, drop_stroke(m)).items(), key=lambda kv: kv[1])[0] in ("f_miss", "f_order")


def test_no_pressure_means_no_shading_tip():
    m = model("u")
    f = faults(m, constant_width(m), pressure=False)
    assert f["f_thin"] == 0 and f["f_thick"] == 0


# ---- copy mode: the attempt is slid sideways onto the model, the band is 4 px, and slant and size are marked ----------
FORM_FAULTS = ["f_upright", "f_slanted", "f_big", "f_small"]


def copy_trace(m, a, pressure=True):
    from ductus.render import inputs
    return net().forward(inputs(m, a, pressure, copy=True))


@pytest.mark.parametrize("ch", list(LETTERS))
def test_copy_mode_perfect_and_anywhere(ch):
    m = model(ch)
    for a in (m, shift(m, 12), shift(m, -9), shift(m, 5, 7), shift(m, -6, -5)):
        T = copy_trace(m, a)
        for k in ("shape", "ductus", "shading", "form", "overall_copy_pressure", "overall_copy_no_pressure"):
            assert round(100 * T[k]) == 100, (k, T[k])
        assert max(T[f] for f in FAULTS + FORM_FAULTS) < 1e-9


@pytest.mark.parametrize("ch", list(LETTERS))
def test_copy_mode_names_slant_and_size(ch):
    m = model(ch)
    for a, want in ((slant(m, -0.45), "f_upright"), (slant(m, 0.45), "f_slanted"), (scale(m, 1.35), "f_big"), (scale(m, 0.7), "f_small")):
        if min(y for st in a for _, y, _ in st) < 0:
            continue        # ascender letters already reach the top of the sheet: 1.35 times bigger does not fit
        T = copy_trace(m, a)
        got = max(FORM_FAULTS, key=lambda f: T[f])
        # an accented letter: the small accent is matched less surely after the fit, which silences form a little
        assert got == want and T[want] > (0.3 if ch.isascii() else 0.15), (want, {f: round(T[f], 2) for f in FORM_FAULTS})
        assert T["form"] < 0.7


@pytest.mark.parametrize("ch", "anhkgs2")
def test_copy_mode_marks_precision_not_place_size_or_slant(ch):
    # a copy that is only bigger, smaller or slanted keeps its shape and ductus: those mark the strokes themselves
    m = model(ch)
    for a in (scale(m, 1.2), scale(m, 0.85), slant(m, -0.3), slant(m, 0.3)):
        T = copy_trace(m, a)
        assert T["shape"] > 0.95 and T["ductus"] > 0.9, (round(T["shape"], 2), round(T["ductus"], 2))


def test_form_faults_are_silent_in_trace_mode():
    m = model("a")
    T = net().forward(__import__("ductus.render", fromlist=["inputs"]).inputs(m, slant(m, -0.5), True))
    assert max(T[f] for f in FORM_FAULTS) == 0
