"""The browser engine (web/ductus.js) must give the same numbers as the Python engine. Needs node; skipped without."""
import json
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "eval"))
from ductus.render import inputs  # noqa: E402
from ladder import LADDERS, net  # noqa: E402


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_js_engine_matches_python(tmp_path):
    with open(os.path.join(ROOT, "web", "model", "styles", "copperplate.json")) as f:
        letters = json.load(f)["letters"]
    cases = []
    for ch in ("a", "k", "y", "4", "i"):
        m = [[tuple(p) for p in st] for st in letters[ch]]
        for k, (_, distort) in enumerate(LADDERS):
            cases.append({"model": m, "attempt": distort(m), "pressure": k % 2 == 0, "copy": k % 3 == 0})
    path = tmp_path / "cases.json"
    path.write_text(json.dumps(cases))
    js = json.loads(subprocess.run(["node", os.path.join(ROOT, "tests", "parity.mjs"), str(path)],
                                   capture_output=True, text=True, check=True).stdout)
    for c, J in zip(cases, js):
        T = net().forward(inputs(c["model"], c["attempt"], c["pressure"], c["copy"]))
        for k, v in J.items():
            assert abs(T[k] - v) < 1e-9, (k, T[k], v)
