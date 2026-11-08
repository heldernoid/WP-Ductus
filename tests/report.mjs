// Checks for the text report (web/report.js) and the PDF templates (web/pdf.js), run by tests/test_lines.py.
import { readFileSync } from "node:fs";
import { Net, inputs } from "../web/ductus.js";
import { layout, paginate, sheetModel } from "../web/lines.js";
import { summarize } from "../web/report.js";
import { templatePdf } from "../web/pdf.js";

const root = new URL("../", import.meta.url);
const net = new Net(JSON.parse(readFileSync(new URL("web/model/arch.json", root))), readFileSync(new URL("web/model/ductus.edits", root), "utf8"));
const st = JSON.parse(readFileSync(new URL("web/model/styles/copperplate.json", root)));
const fails = [];
const ok = (c, what) => { if (!c) fails.push(what); };

// a text with a line break: the break starts a new row, and pages hold every letter once
const lay = layout("Dear friend\nI write slowly and with care", st, 200, { edge: 12 });
ok(lay.items.find(i => i.ch === "I").row > lay.items.find(i => i.ch === "d" && i.word === 1).row, "a line break starts a new row");
const pages = paginate(lay, 2);
ok(pages.flatMap(p => p.index).length === lay.items.length, "pages hold every letter once");
ok(pages.every(p => p.items.every(i => i.row < 2)), "rows counted from each page's top");

// the report: perfect letters score 100 with no advice; one reversed letter shows up as the weakest, under wrong direction
const M = sheetModel(lay, st), words = [];
for (const it of lay.items) words[it.word] = (words[it.word] ?? "") + it.ch;
const mark = (k, s) => { const T = net.forward(inputs(st.letters[lay.items[k].ch], s, true, false)); return { ch: lay.items[k].ch, word: lay.items[k].word, T, overall: Math.round(100 * T.overall_pressure) }; };
const local = k => M[k].map(s => s.map(([x, y, w]) => [x - lay.items[k].ox, y - lay.items[k].oy, w]));
const perfect = lay.items.map((_, k) => mark(k, local(k)));
let S = summarize(perfect, words, { pressure: true });
ok(S.overall === 100 && S.advice.length === 0 && S.weakest.length === 0, `perfect text: ${S.overall}, ${S.advice.length} advice`);
ok(S.words.length === words.length && S.words.every(w => w.score === 100), "every word scored");
const k = lay.items.findIndex(i => i.ch === "y");          // y occurs once in the text
const damaged = perfect.map((l, i) => (i === k ? mark(i, local(i).map((s, j) => (j === 0 ? [...s].reverse() : s))) : l));
S = summarize(damaged, words, { pressure: true });
ok(S.weakest[0]?.ch === "y", `weakest letter ${S.weakest[0]?.ch}`);
// a whole stroke reversed also runs backwards in time: wrong direction or stroke order, both true
ok(["f_back", "f_order"].includes(S.faults[0]?.f) && S.advice[0]?.f === S.faults[0]?.f, `costliest fault ${S.faults[0]?.f}`);
// a letter left out counts as missed
S = summarize(perfect.map((l, i) => (i === 0 ? { ...l, T: null, overall: 0 } : l)), words, { pressure: true });
ok(S.written === S.n - 1 && S.faults[0]?.f === "f_miss", "a letter left out is missed");

// the PDF: a well-formed file, one page per five rows of a tracing sheet, two rows per copybook row
for (const kind of ["trace", "copy"]) {
  const pdf = new TextDecoder().decode(new Uint8Array(await templatePdf("The Universal Penman 1733\nÁgua Köln", st, kind, "test").arrayBuffer()));
  ok(pdf.startsWith("%PDF-1.4") && pdf.trimEnd().endsWith("%%EOF"), `${kind}: PDF header and trailer`);
  const xref = +pdf.match(/startxref\n(\d+)/)[1];
  ok(pdf.slice(xref, xref + 4) === "xref", `${kind}: startxref points at the xref table`);
  ok(/\/Count [1-9]/.test(pdf), `${kind}: has pages`);
}
console.log(JSON.stringify({ fails }));
process.exit(fails.length ? 1 : 0);
