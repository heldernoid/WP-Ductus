"""Lines of text (web/lines.js, run in node): layout on the sheet, cutting writing into letters, perfect copies 100
per letter (also joined, and in the copy game moved and spaced differently). Needs node; skipped without."""
import json
import os
import shutil
import subprocess

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_lines():
    r = subprocess.run(["node", os.path.join(ROOT, "tests", "lines.mjs")], capture_output=True, text=True)
    out = json.loads(r.stdout)
    assert not out["fails"], out["fails"]


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_text_report_and_templates():
    """the text report (web/report.js) and the PDF templates (web/pdf.js): tests/report.mjs"""
    r = subprocess.run(["node", os.path.join(ROOT, "tests", "report.mjs")], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
