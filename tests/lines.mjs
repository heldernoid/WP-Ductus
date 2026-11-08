// Checks for lines of text (web/lines.js): the layout fits the sheet, and a perfect copy of a whole phrase, cut into
// letters, scores 100 per letter: written letter by letter, joined into words, and (copy game) moved and spaced wider.
// Run by tests/test_lines.py; prints one JSON report and exits 1 on a failure.
import { readFileSync } from "node:fs";
import { Net, inputs } from "../web/ductus.js";
import { layout, sheetModel, segment, copySlots } from "../web/lines.js";

const root = new URL("../", import.meta.url);
const net = new Net(JSON.parse(readFileSync(new URL("web/model/arch.json", root))), readFileSync(new URL("web/model/ductus.edits", root), "utf8"));
const st = JSON.parse(readFileSync(new URL("web/model/styles/copperplate.json", root)));

const TEXTS = ["minimum", "the quick brown fox jumps over the lazy dog", "copperplate 2026", "illumination", "The Universal Penman", "Ánh Öl Señor"];
const fails = [], report = {};
const ok = (cond, what) => { if (!cond) fails.push(what); };

function scores(lay, strokes, copy) {
  const slots = copy ? copySlots(strokes, lay, st) : undefined;
  const pieces = segment(strokes, lay, st, slots);
  return lay.items.map((it, k) => {
    const T = net.forward(inputs(st.letters[it.ch], pieces[k], true, copy));
    return copy ? T.overall_copy_pressure : T.overall_pressure;
  });
}

// joined writing: a letter's last stroke runs on into the next letter's first stroke when they (nearly) meet
function joined(lay, M) {
  const out = [];
  M.forEach((letter, k) => {
    const it = lay.items[k], prev = out[out.length - 1];
    letter.forEach((s, j) => {
      const touch = j === 0 && k && !it.start && lay.items[k - 1].row === it.row && prev && prev.length > 1 && s.length > 1
        && Math.hypot(prev[prev.length - 1][0] - s[0][0], prev[prev.length - 1][1] - s[0][1]) < 4;
      if (touch) prev.push(...s); else out.push(s.map(p => [...p]));
    });
  });
  return out;
}

let t0 = performance.now(), n = 0;
for (const text of TEXTS) for (const width of [168, 300]) {
  const lay = layout(text, st, width), M = sheetModel(lay, st);
  const want = text.replace(/\s/g, "").length;
  ok(lay.items.length === want, `${text}@${width}: ${lay.items.length} letters, want ${want}`);
  for (const s of M.flat()) for (const [x, y] of s) ok(x >= 0 && x <= width && y >= 0 && y <= lay.height, `${text}@${width}: ink off the sheet at ${x.toFixed(1)}, ${y.toFixed(1)}`);
  const J = joined(lay, M);
  const cases = {
    trace: scores(lay, M.flat(), false),
    trace_joined: scores(lay, J, false),
    copy: scores(lay, M.flat(), true),
    copy_joined: scores(lay, J, true),
  };
  // copy game: each row moved 9 px right and written 12% wider apart (the letters themselves unchanged)
  const rowStart = {};
  for (const it of lay.items) rowStart[it.row] = Math.min(rowStart[it.row] ?? Infinity, it.ox);
  const spread = M.map((letter, k) => {
    const it = lay.items[k], dx = 9 + 0.12 * (it.ox - rowStart[it.row]);
    return letter.map(s => s.map(([x, y, w]) => [x + dx, y, w]));
  });
  cases.copy_spread = scores(lay, spread.flat(), true);
  // and uneven: each gap between letters 0, 2.5 or 5 px wider than the model's, in turn
  let acc = 0;
  const uneven = M.map((letter, k) => {
    const it = lay.items[k];
    if (k && lay.items[k - 1].row !== it.row) acc = 0;
    acc += k ? (k % 3) * 2.5 : 0;
    return letter.map(s => s.map(([x, y, w]) => [x + acc - 4, y, w]));
  });
  cases.copy_uneven = scores(lay, joined(lay, uneven), true);
  // damage stays where it was done: the third letter's first stroke written backwards lowers that letter only
  for (const copy of [false, true]) {
    const bad = M.map((letter, k) => letter.map((s, j) => (k === 2 && j === 0 ? [...s].reverse() : s)));
    const sc = scores(lay, bad.flat(), copy);
    ok(sc[2] < 0.9 && sc.every((v, k) => k === 2 || v >= 0.999), `${text}@${width} reversed 3rd letter (${copy ? "copy" : "trace"}): ${sc.map(v => Math.round(100 * v))}`);
  }
  n += 8 * lay.items.length;
  for (const [name, sc] of Object.entries(cases)) {
    const min = Math.min(...sc), worst = lay.items[sc.indexOf(min)].ch;
    report[`${text}@${width} ${name}`] = { min: +(100 * min).toFixed(1), worst, rows: lay.rows };
    const bar = name === "copy_spread" || name === "copy_uneven" ? 0.95 : name.endsWith("joined") ? 0.98 : 0.999;
    ok(min >= bar, `${text}@${width} ${name}: '${worst}' scored ${(100 * min).toFixed(1)}`);
  }
}
report.ms_per_letter = +((performance.now() - t0) / n).toFixed(1);
console.log(JSON.stringify({ fails, report }, null, 1));
process.exit(fails.length ? 1 : 0);
