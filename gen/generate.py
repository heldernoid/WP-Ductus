"""Write the WP-Ductus network: arch.json and weights/ductus.edits (trace mode).

Every value below is typed by hand with a reason; nothing is fitted. Inputs come from ductus/render.py:
m_* = the model letter's maps, a_* = the attempt's maps, has_pressure = 1 when the pen reports pressure.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
lines = []
DIRS = ["dn", "up", "lf", "rt"]
OPPOSITE = {"dn": "up", "up": "dn", "lf": "rt", "rt": "lf"}
# tolerance band: 1 px from B1, then `widen` more steps from B2 (an input: 1 for tracing -> 2 px, 3 for copying -> 4 px;
# ductus/render.py sets it). Ink within the band of the model counts as on it.


def emit(s, why=None):
    lines.append(s + (f"   # {why}" if why else ""))


def section(title):
    lines.append("")
    lines.append(f"# ---- {title} " + "-" * max(0, 100 - len(title)))


def fmt(v):
    return f"{v:.6g}"


# ---- layers ---------------------------------------------------------------------------------------
E1 = {"id": "E1", "op": "conv", "k": 1, "act": "clip01", "in": ["m_ink", "m_wid", "a_ink", "a_wid"],
      "out": ["m_on", "a_on", "m_shade", "a_shade"]}
E2 = {"id": "E2", "op": "conv", "k": 1, "act": "clip01", "in": ["m_on", "m_shade", "m_t"], "out": ["m_hair", "m_tinv"]}
# the tolerance band: ink, shaded ink and the model's writing time (latest t, and 1 - earliest t) widened into the band
BAND_SRC = ["m_on", "a_on", "a_shade", "m_t", "m_tinv"]
BAND_OUT = [f"{n}_b" for n in BAND_SRC]
B1 = {"id": "B1", "op": "max3", "in": BAND_SRC + [f"m_{d}" for d in DIRS] + ["m_shade"],
      "out": BAND_OUT + [f"m_{d}_n" for d in DIRS] + ["m_shade_n"]}
B2 = {"id": "B2", "op": "loop", "n_from": "widen", "body": [{"id": "B2a", "op": "max3", "in": BAND_OUT, "out": BAND_OUT}]}
C1_OUT = (["on_track", "off_track", "covered", "missed"] + [f"same_{d}" for d in DIRS] + [f"opp_{d}" for d in DIRS]
          + ["shade_hit", "shade_miss", "hair_cov", "hair_thick"])
C1 = {"id": "C1", "op": "conv", "k": 1, "act": "clip01",
      "in": ["a_on", "m_on_b", "m_on", "a_on_b", "m_shade", "m_shade_n", "m_hair", "a_shade", "a_shade_b"] + [f"a_{d}" for d in DIRS]
            + [f"m_{d}_n" for d in DIRS], "out": C1_OUT}
C2 = {"id": "C2", "op": "conv", "k": 1, "act": "clip01", "in": ["a_t", "m_t_b", "m_tinv_b", "on_track"], "out": ["late", "early"]}
COUNTS = ["n_on", "n_off", "n_cov", "n_miss", "n_same", "n_opp", "n_late", "n_early", "n_shade_hit", "n_shade_miss",
          "n_hair_cov", "n_hair_thick"]
Z = {"id": "Z", "op": "zone", "act": "none", "in": C1_OUT + ["late", "early"], "out": COUNTS}
R = {"id": "R", "op": "ratio", "parts": {
    "stay": (["n_on"], ["n_on", "n_off"]),
    "cover": (["n_cov"], ["n_cov", "n_miss"]),
    "direction": (["n_same"], ["n_same", "n_opp"]),
    "order_slip": (["n_late", "n_early"], ["n_on"]),
    # a letter with no shades (a light hand's 0) has none to miss: empty counts as all hit
    "shade_hit": (["n_shade_hit"], ["n_shade_hit", "n_shade_miss"], 1.0),
    "hair_slip": (["n_hair_thick"], ["n_hair_cov"]),
}}
QUAL = {"id": "Q", "op": "linear", "act": "clip01", "in": list(R["parts"]), "out": ["shape", "ductus", "shading"]}
OVERALL = {"id": "O", "op": "linear", "act": "clip01", "in": ["shape", "ductus", "shading"],
           "out": ["overall_pressure", "overall_no_pressure"]}
# copy mode: slant = the slope of x on y over the thin-pen path (shear changes it, size and position do not);
# size = the variance of y (size changes it, slant and position do not); each compared with the model's
FORM_SUMS = [f"{p}_{k}" for p in ("a", "m") for k in ("n", "sx", "sy", "sxy", "syy")]
Z2 = {"id": "Z2", "op": "zone", "act": "none", "in": ["a_form", "m_form"], "out": FORM_SUMS}
R2 = {"id": "R2", "op": "moments", "parts": {p: [f"{p}_{k}" for k in ("n", "sx", "sy", "sxy", "syy")] for p in ("a", "m")}}
R3 = {"id": "R3", "op": "ratio", "parts": {"size2": (["a_vy"], ["m_vy"])}}
SLANT = {"id": "S", "op": "linear", "act": "none", "in": ["a_slope", "m_slope"], "out": ["lean_gap"]}
FAULTS = ["f_off", "f_miss", "f_back", "f_order", "f_thin", "f_thick", "f_upright", "f_slanted", "f_big", "f_small"]
FAULT = {"id": "F", "op": "linear", "act": "clip01",
         "in": list(R["parts"]) + ["has_pressure", "copy", "lean_gap", "size2"], "out": FAULTS}
FORM = {"id": "Q2", "op": "linear", "act": "clip01", "in": ["f_upright", "f_slanted", "f_big", "f_small"], "out": ["form"]}
OVERALL_COPY = {"id": "O2", "op": "linear", "act": "clip01", "in": ["shape", "ductus", "shading", "form"],
                "out": ["overall_copy_pressure", "overall_copy_no_pressure"]}
LAYERS = [E1, E2, B1, B2, C1, C2, Z, R, Z2, R2, R3, SLANT, QUAL, OVERALL, FAULT, FORM, OVERALL_COPY]


def gen_encoder():
    section("E1 encoder (same weights for the model and the attempt)")
    for p in ("m", "a"):
        emit(f"TAP E1 {p}_on {p}_ink 0 0 3")
        emit(f"BIAS E1 {p}_on -1", "solid ink: 1 from two-thirds coverage up (the anti-aliased fringe does not count)")
        emit(f"TAP E1 {p}_shade {p}_wid 0 0 0.8")
        emit(f"BIAS E1 {p}_shade -1.8", "shaded ink: pen wider than 2.25 px counts, 3.5 px and wider fully (hairline 1.3, full shade 4)")
    section("E2 hairline ink of the model; 1 - writing time on the model's ink (to carry the earliest time nearby)")
    emit("TAP E2 m_hair m_on 0 0 1")
    emit("TAP E2 m_hair m_shade 0 0 -1")
    emit("BIAS E2 m_hair 0", "model ink that is not shaded")
    emit("TAP E2 m_tinv m_on 0 0 1")
    emit("TAP E2 m_tinv m_t 0 0 -1")
    emit("BIAS E2 m_tinv 0", "1 - t on the model's ink, 0 elsewhere: widened by max, it gives 1 - the EARLIEST time nearby")


def gen_compare():
    section("B1-B2 tolerance band: widen by 1 px (B1), then `widen` more times (B2; 2 px tracing, 4 px copying); the model's direction and shaded "
            "ink by 1 px only (wider, a stem's neighbouring upstroke leaks into its direction, and the hairlines "
            "next to it vanish from the hairline check)")
    section("C1 comparison maps (AND of two maps = clip(a + b - 1))")
    pairs = [("on_track", [("a_on", 1), ("m_on_b", 1)], -1, "your ink inside the model's band"),
             ("off_track", [("a_on", 1), ("m_on_b", -1)], 0, "your ink outside the model's band"),
             ("covered", [("m_on", 1), ("a_on_b", 1)], -1, "model ink with your ink near it"),
             ("missed", [("m_on", 1), ("a_on_b", -1)], 0, "model ink with none of yours near it")]
    for d in DIRS:
        pairs.append((f"same_{d}", [(f"a_{d}", 1), (f"m_{d}_n", 1)], -1, f"you move {d} where the model moves {d}"))
        pairs.append((f"opp_{d}", [(f"a_{d}", 1), (f"m_{OPPOSITE[d]}_n", 1), (f"m_{d}_n", -1)], -1,
                      f"you move {d} where the model only moves {OPPOSITE[d]}: the stroke runs backwards"))
    pairs += [("shade_hit", [("m_shade", 1), ("a_shade_b", 1), ("covered", 0)], -1, "the model is shaded here and so are you"),
              ("shade_miss", [("m_shade", 1), ("a_shade_b", -1), ("a_on_b", 1)], -1, "the model is shaded here, you wrote a thin line"),
              ("hair_cov", [("m_hair", 1), ("m_shade_n", -1), ("a_on_b", 1)], -1,
               "a model hairline (not touching a shaded stroke) that you covered"),
              ("hair_thick", [("m_hair", 1), ("m_shade_n", -1), ("a_shade", 1)], -1,
               "a model hairline (not touching a shaded stroke) that you wrote thick: right beside a stem, a slightly shifted stem is not a thick hairline")]
    for name, terms, bias, why in pairs:
        for src, w in terms:
            if w:
                emit(f"TAP C1 {name} {src} 0 0 {fmt(w)}")
        emit(f"BIAS C1 {name} {fmt(bias)}", why)
    section("C2 stroke order on shared ink: written much later / earlier than the model (time is 0 to 1 over the letter)")
    emit("TAP C2 late a_t 0 0 4")
    emit("TAP C2 late m_t_b 0 0 -4")
    emit("TAP C2 late on_track 0 0 4")
    emit("BIAS C2 late -5", "your ink is a quarter of the letter or more later than the latest model ink near it; only on your ink inside the band")
    emit("TAP C2 early a_t 0 0 -4")
    emit("TAP C2 early m_tinv_b 0 0 -4")
    emit("TAP C2 early on_track 0 0 4")
    emit("BIAS C2 early -1", "your ink is a quarter of the letter or more earlier than the earliest model ink near it "
         "(4 (1 - tinv) - 4 t - 1 + 4 (on_track - 1))")


def gen_scores():
    section("Z counts over the whole canvas")
    for out, ins in (("n_on", ["on_track"]), ("n_off", ["off_track"]), ("n_cov", ["covered"]), ("n_miss", ["missed"]),
                     ("n_same", [f"same_{d}" for d in DIRS]), ("n_opp", [f"opp_{d}" for d in DIRS]),
                     ("n_late", ["late"]), ("n_early", ["early"]), ("n_shade_hit", ["shade_hit"]),
                     ("n_shade_miss", ["shade_miss"]), ("n_hair_cov", ["hair_cov"]), ("n_hair_thick", ["hair_thick"])):
        for i in ins:
            emit(f"ZONE Z {out} {i} 0:96 0:96 1")
        emit(f"BIAS Z {out} 0", f"how many pixels: {', '.join(ins)}")
    section("Q quality scores from the ratios (R: stay, cover, direction, order_slip, shade_hit, hair_slip)")
    emit("LINK Q shape stay 1")
    emit("LINK Q shape cover 1")
    emit("BIAS Q shape -1", "shape = 1 when you stay on the model and cover all of it; 0.9 of each gives 0.8, 0.8 gives 0.6, half gives 0")
    emit("LINK Q ductus direction 1.5")
    emit("LINK Q ductus order_slip -1.5")
    emit("BIAS Q ductus -0.5", "ductus = 1 when every stroke runs the model's way in the model's order; a third backwards gives 0.5; order slips cost as much")
    emit("LINK Q shading shade_hit 0.7")
    emit("LINK Q shading hair_slip -0.7")
    emit("BIAS Q shading 0.3", "shading = 1 when every shaded part is thick and every hairline thin")
    section("O overall, with and without pressure (a mouse or a finger has none: shading is not judged)")
    for out, ws, why in (("overall_pressure", (0.5, 0.3, 0.2), "half shape, 30% ductus, 20% shading"),
                         ("overall_no_pressure", (0.6, 0.4, 0.0), "60% shape, 40% ductus")):
        for q, w in zip(("shape", "ductus", "shading"), ws):
            if w:
                emit(f"LINK O {out} {q} {fmt(w)}")
        emit(f"BIAS O {out} 0", why)


def gen_faults():
    section("F faults: how many score points each fault costs (its quality's slope); the page's tip is the largest one")
    for out, src, w, b, why in (
            ("f_off", "stay", -1, 1, "ink off the model: 1 - stay (shape slope 1)"),
            ("f_miss", "cover", -1, 1, "model not covered: 1 - cover (shape slope 1)"),
            ("f_back", "direction", -1.5, 1.5, "strokes written backwards: 1.5 (1 - direction) (ductus slope 1.5), less "
             "1 - cover below: with little of the letter written, direction means little and the tip should say so"),
            ("f_order", "order_slip", 1.5, 0, "strokes in the wrong order: 1.5 order_slip (ductus slope 1.5)")):
        emit(f"LINK F {out} {src} {fmt(w)}")
        if out == "f_back":
            emit("LINK F f_back cover 1")
            b -= 1                          # - (1 - cover) = cover - 1
        emit(f"BIAS F {out} {fmt(b)}", why)
    emit("LINK F f_thin shade_hit -0.7")
    emit("LINK F f_thin has_pressure 1")
    emit("BIAS F f_thin -0.3", "downstrokes not pressed: 0.7 (1 - shade_hit), only with pressure (without it the sum is below 0)")
    emit("LINK F f_thick hair_slip 0.7")
    emit("LINK F f_thick has_pressure 1")
    emit("BIAS F f_thick -1", "hairlines pressed: 0.7 hair_slip, only with pressure")
    # copy mode only (the `copy` input is 1): in trace mode the dots already hold slant and size
    emit("LINK F f_upright lean_gap 2.5")
    emit("LINK F f_upright copy 1")
    emit("LINK F f_upright cover 2")
    emit("BIAS F f_upright -3.25", "too upright: lean_gap is how much less x moves per px of height than in the model; "
         "0.1 (about 4 degrees) free, each 0.1 more costs a quarter; copy mode only; and silenced by 2 x the share of "
         "the model you missed (-2 here, + 2 cover): a letter with a part missing has no slant or size of its own")
    emit("LINK F f_slanted lean_gap -2.5")
    emit("LINK F f_slanted copy 1")
    emit("LINK F f_slanted cover 2")
    emit("BIAS F f_slanted -3.25", "too slanted: the same, the other way (and the same 2 x cover)")
    emit("LINK F f_big size2 1.33333")
    emit("LINK F f_big copy 1")
    emit("LINK F f_big cover 2")
    emit("BIAS F f_big -4.61333", "too big: size2 is your height variance over the model's (size squared); "
         "1.1 times the size (1.21) free, 1.4 times (1.96) = 1 (and the same 2 x cover)")
    emit("LINK F f_small size2 -2.22222")
    emit("LINK F f_small copy 1")
    emit("LINK F f_small cover 2")
    emit("BIAS F f_small -1.2", "too small: 0.9 times the size (0.81) free, 0.6 times (0.36) = 1 (and the same 2 x cover)")


def gen_form():
    section("Z2 sums for slant and size (copy mode), on the thin-pen path so that pressure does not move them; "
            "R2 turns them into mean y, variance of y and slope of x on y (fixed op)")
    for p, src, who in (("a", "a_form", "your (where it lies on the fitted model)"), ("m", "m_form", "the model's (where your path covers it)")):
        for k, scale, what in (("n", "1", "amount of path"), ("sx", "x", "sum of x"), ("sy", "y", "sum of y"),
                               ("sxy", "xy", "sum of x * y"), ("syy", "yy", "sum of y * y")):
            emit(f"ZONE Z2 {p}_{k} {src} 0:96 0:96 {scale}")
            emit(f"BIAS Z2 {p}_{k} 0", f"{what} over {who} path")
    section("S lean gap: your slope minus the model's (x per px down; copperplate leans right going up, so about -0.7)")
    emit("LINK S lean_gap a_slope 1")
    emit("LINK S lean_gap m_slope -1")
    emit("BIAS S lean_gap 0", "positive: you lean less than the model (more upright); negative: more")


def gen_form_marks():
    section("Q2 form (copy mode): slant and size; O2 the copy-mode overall")
    for f in ("f_upright", "f_slanted", "f_big", "f_small"):
        emit(f"LINK Q2 form {f} -1")
    emit("BIAS Q2 form 1", "form = 1 minus the slant and size faults")
    for out, ws, why in (("overall_copy_pressure", (0.4, 0.3, 0.15, 0.15), "40% shape, 30% ductus, 15% shading, 15% form"),
                         ("overall_copy_no_pressure", (0.45, 0.35, 0.0, 0.2), "45% shape, 35% ductus, 20% form")):
        for q, w in zip(("shape", "ductus", "shading", "form"), ws):
            if w:
                emit(f"LINK O2 {out} {q} {fmt(w)}")
        emit(f"BIAS O2 {out} 0", why)


def build():
    lines.clear()
    lines.append("# WP-Ductus weights: every nonzero parameter comes from a line below; nothing was trained or fitted.")
    gen_encoder()
    gen_compare()
    gen_scores()
    gen_form()
    gen_faults()
    gen_form_marks()
    arch = {"name": "WP-Ductus", "input": [96, 96], "layers": LAYERS,
            "inputs": [f"{p}_{k}" for p in ("m", "a") for k in ("ink", "path", "wid", "t", "dn", "up", "lf", "rt")] + ["has_pressure", "copy", "widen"]}
    return arch, "\n".join(lines) + "\n"


if __name__ == "__main__":
    arch, edits = build()
    os.makedirs(os.path.join(ROOT, "weights"), exist_ok=True)
    with open(os.path.join(ROOT, "arch.json"), "w") as f:
        json.dump(arch, f, indent=1)
    with open(os.path.join(ROOT, "weights", "ductus.edits"), "w") as f:
        f.write(edits)
    n = sum(1 for l in edits.splitlines() if l.strip() and not l.startswith("#"))
    print(f"wrote arch.json and weights/ductus.edits ({n} edit lines)")
    # the demo page reads the same files, plus the model letters of each hand as canvas strokes (one file a hand, loaded
    # when it is chosen) and an index with a sample of each for the picker
    from gen.styles import HANDS
    web = os.path.join(ROOT, "web", "model")
    os.makedirs(os.path.join(web, "styles"), exist_ok=True)
    with open(os.path.join(web, "arch.json"), "w") as f:
        json.dump(arch, f, indent=1)
    with open(os.path.join(web, "ductus.edits"), "w") as f:
        f.write(edits)
    index = []
    for h in HANDS:
        data = h.export()
        with open(os.path.join(web, "styles", f"{h.id}.json"), "w") as f:
            json.dump(data, f, separators=(",", ":"))
        index.append({k: data[k] for k in ("id", "name", "family", "variant", "pen", "slant", "slant_deg", "nib_angle", "nib", "mono", "square", "caps_only", "unicase")}
                     | {"letters": len(data["letters"]), "sample": h.sample_strokes(), "tool": h.about["tool"]})
    with open(os.path.join(web, "styles.json"), "w") as f:
        json.dump(index, f, separators=(",", ":"))
    old = os.path.join(web, "copperplate.json")
    if os.path.exists(old):
        os.remove(old)                          # now web/model/styles/copperplate.json
    print("wrote web/model/ (arch.json, ductus.edits, styles.json, styles/: " + ", ".join(f"{h.id} {len(h.letters)}" for h in HANDS) + ")")
