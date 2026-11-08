// WP-Ductus, the page: practise calligraphy (ten hands) one letter at a time or as text in a notebook, get marked by the
// hand-written network (ductus.js), read the report for a whole text, and take a template home as a PDF.
import { Net, inputs, fit as fitLetter, samples, H, W, strokeLength } from "./ductus.js";
import { layout, paginate, sheetModel, segment, copySlots, longestWord, pickLetter, PITCH } from "./lines.js";
import { summarize, FAULTS as FAULT_NAMES, starsFor } from "./report.js";
import { templatePdf, dotsAlong, nibSweep, squareSweep } from "./pdf.js";

const $ = id => document.getElementById(id);
const HAIR = 1.3, SHADE = 4.0, NO_PRESSURE_WIDTH = 2.0;
const SIZES = [1.8, 2.4, 3.2, 4.2];   // writing size for text: screen pixels per canvas pixel (an x-height of 20 canvas px is
                                    // 36, 48, 64 or 84 screen pixels); bigger letters, fewer to a row
const EDGE = 12;                    // the notebook's left margin (its red line) in canvas pixels
const MAX_TEXT = 4000;              // characters of text kept from a paste or an upload

const ALL_GROUPS = [
  ["Small", "abcdefghijklmnopqrstuvwxyz"],
  ["Capitals", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"],
  ["Digits", "0123456789"],
  ["Accents", "áàâãäåçéèêëíìîïñóòôõöőúùûüůűýÿčšžřěąęń"],
  ["Accented capitals", "ÁÀÂÃÄÅÇÉÈÊËÍÎÏÑÓÒÔÕÖŐÚÙÛÜŮŰÝČŠŽŘĚ"],
];
// the groups of the chosen hand: the same groups in the same order for every hand (its first letters to learn are
// marked on the keys, not moved to the front), so a letter is always in the same place
let GROUPS = [], SEQ = "", STARRED = "";
function setGroups() {
  GROUPS = ALL_GROUPS.map(([name, chars]) => [name, [...chars].filter(ch => style.letters[ch]).join("")]).filter(g => g[1]);
  SEQ = GROUPS.map(g => g[1]).join("");
  // star totals: the plain letters and digits of the hand (its capitals, for a unicase hand)
  STARRED = [...SEQ].filter(ch => (style.unicase ? /^[A-Z0-9]$/ : /^[a-z0-9]$/).test(ch)).join("");
}
const starKey = k => (style.id === "copperplate" ? k : `${style.id}:${k}`);   // copperplate keeps its earlier stars
// phrases: the minim words first (stems and turns only), then a pangram (every letter), then longer pieces
const PHRASES = [
  ["minimum", "minimum"],
  ["nun mum inn", "nun mum inn"],
  ["a calm ocean", "a calm ocean"],
  ["Pangram", "The quick brown fox jumps over the lazy dog"],
  ["Bickham", "The Universal Penman 1733"],
  ["A letter", "Dear friend,\nI write to you in a slow and careful hand, as the old masters taught.\nYours faithfully"],
];

// ---- state ----------------------------------------------------------------------------------------------------------
let net, style, hands = [], handId = "copperplate";
const handCache = {};
let mode = "trace", unit = "letter", cur = "i", group = 0, text = PHRASES[0][1];
let book = null;                    // text: { lay, pages, words }; a letter: one page of its own
let pageNo = 0, SW = W, SH = H;
let inkByPage = [[]], resultByPage = [];
let live = null, livePointer = null, anim = null, pick = null, pickedByHand = false, checking = false;
let pressureSeen = false, penSeen = false, penOnly = null;

const store = {
  get(k, d) { try { const v = localStorage.getItem("wp-ductus-" + k); return v == null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem("wp-ductus-" + k, JSON.stringify(v)); } catch {} },
};
let best = store.get("best", {});
mode = ["trace", "copy"].includes(store.get("mode")) ? store.get("mode") : mode;
unit = ["letter", "text"].includes(store.get("unit")) ? store.get("unit") : unit;
text = typeof store.get("text") === "string" && store.get("text") ? store.get("text") : text;
cur = typeof store.get("letter") === "string" ? store.get("letter") : cur;
handId = typeof store.get("hand") === "string" ? store.get("hand") : handId;
let size = [0, 1, 2, 3].includes(store.get("size")) ? store.get("size") : 1;

const strokes = () => inkByPage[pageNo];
const result = () => resultByPage[pageNo] ?? null;
const pages = () => book.pages;
const page = () => book.pages[pageNo];

// ---- load ----------------------------------------------------------------------------------------------------------
async function load() {
  try {
    const [arch, edits, index] = await Promise.all([
      fetch("model/arch.json").then(r => r.json()),
      fetch("model/ductus.edits").then(r => r.text()),
      fetch("model/styles.json").then(r => r.json()),
    ]);
    net = new Net(arch, edits);
    hands = index;
    if (!hands.some(h => h.id === handId)) handId = "copperplate";
    const n = edits.split("\n").filter(l => l.trim() && !l.startsWith("#")).length;
    for (const el of document.querySelectorAll(".n-lines")) el.textContent = n;
    for (const el of document.querySelectorAll(".n-letters")) el.textContent = hands.reduce((a, h) => a + h.letters, 0);
    for (const el of document.querySelectorAll(".n-hands")) el.textContent = families().length;
    $("text-in").value = text;
    buildHands();
    await setHand(handId, false);
    $("status").hidden = true;
    buildPhrases();
    setMode(mode, false); setUnit(unit);
  } catch (e) {
    $("status").hidden = false;
    $("status").textContent = "The network could not be loaded: " + e.message + ". Reload the page to try again.";
  }
}

// ---- the hands ---------------------------------------------------------------------------------------------------
async function loadHand(id) {
  if (!handCache[id]) {
    const h = await fetch(`model/styles/${id}.json`).then(r => r.json());
    // a unicase hand (one set of forms) writes a small letter with its capital's form
    for (const [k, v] of Object.entries(h.alias || {})) if (h.letters[v]) h.letters[k] = h.letters[v];
    handCache[id] = h;
  }
  return handCache[id];
}
async function setHand(id, reset = true) {
  try { style = await loadHand(id); }
  catch { flash("That hand could not be loaded. Check your connection and choose it again."); return; }
  handId = id; store.set("hand", id);
  document.body.dataset.pen = style.pen;
  setGroups();
  if (!style.letters[cur]) cur = (style.start.match(/./u) ?? [SEQ[0]])[0];
  group = Math.max(0, GROUPS.findIndex(g => g[1].includes(cur)));
  const fam = hands.find(h => h.id === id)?.family || id;
  store.set("variant-" + fam, id);
  for (const b of document.querySelectorAll(".hand")) {
    const on = b.dataset.family === fam;
    b.setAttribute("aria-pressed", String(on));
    if (on && b.dataset.hand !== id) { b.dataset.hand = id; requestAnimationFrame(drawHandSamples); }
  }
  buildVariants();
  for (const el of document.querySelectorAll(".hand-name")) el.textContent = style.name;
  buildPalette();
  const un = $("unicase-note");
  un.hidden = !style.unicase;
  un.textContent = style.unicase ? `${style.name} is unicase: it has one set of letterforms, so a small letter is written with the same form as its capital.` : "";
  inputNote(); emptyText();
  if (reset) { restart(); }
  drawGuide();
}
// one card per family (Copperplate, Blackletter, ...); a family with more than one form shows its variants under the
// cards (Blackletter: Textura or Bâtarde). A card draws the family's chosen variant.
const families = () => [...new Set(hands.map(h => h.family || h.id))];
const variantOf = fam => { const vs = hands.filter(h => (h.family || h.id) === fam); return vs.find(h => h.id === handId) || vs.find(h => h.id === store.get("variant-" + fam)) || vs[0]; };
function buildHands() {
  const box = $("hands");
  box.innerHTML = "";
  for (const fam of families()) {
    const h = variantOf(fam);
    const b = document.createElement("button");
    b.type = "button"; b.className = "hand"; b.dataset.hand = h.id; b.dataset.family = fam;
    const tool = h.pen === "pointed" ? "pointed pen" : h.pen === "mono" ? (h.square ? "square-cut pen" : "heavy pen") : `broad nib ${h.nib_angle}°`;
    const lean = h.slant_deg ? `${Math.round(90 - h.slant_deg)}°` : "upright";
    const n = hands.filter(x => (x.family || x.id) === fam).length;
    b.innerHTML = `<canvas aria-hidden="true"></canvas><b>${fam === h.id || !h.variant ? h.name : hands.find(x => x.id === fam)?.name ?? h.name}</b><span>${n > 1 ? `${n} styles · ` : ""}${tool} · ${lean}</span>`;
    b.onclick = () => setHand(variantOf(fam).id);
    box.appendChild(b);
  }
  buildVariants();
  requestAnimationFrame(drawHandSamples);
}
function buildVariants() {
  const box = $("variants"), cur_ = hands.find(h => h.id === handId);
  const fam = cur_?.family || handId, vs = hands.filter(h => (h.family || h.id) === fam);
  box.hidden = vs.length < 2;
  box.innerHTML = vs.length < 2 ? "" : `<span class="label">${hands.find(h => h.id === fam)?.name ?? ""} style</span>`;
  for (const v of vs.length < 2 ? [] : vs) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "variant"; b.textContent = v.variant || v.name;
    b.setAttribute("aria-pressed", String(v.id === handId));
    b.onclick = () => setHand(v.id);
    box.appendChild(b);
  }
}
function drawHandSamples() {
  for (const b of document.querySelectorAll(".hand")) {
    const h = hands.find(x => x.id === b.dataset.hand), cvs = b.querySelector("canvas"), c = cvs.getContext("2d");
    const r = cvs.getBoundingClientRect(), dpr = devicePixelRatio || 1;
    if (!r.width) continue;
    cvs.width = Math.round(r.width * dpr); cvs.height = Math.round(r.height * dpr);
    const pts = h.sample.flat(), pad_ = 4;
    const x0 = Math.min(...pts.map(p => p[0] - p[2])), x1 = Math.max(...pts.map(p => p[0] + p[2]));
    const y0 = Math.min(...pts.map(p => p[1] - p[2])), y1 = Math.max(...pts.map(p => p[1] + p[2]));
    const s = Math.min((r.width - 2 * pad_) / (x1 - x0), (r.height - 2 * pad_) / (y1 - y0));
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    c.clearRect(0, 0, r.width, r.height);
    c.translate((r.width - (x1 - x0) * s) / 2 - x0 * s, (r.height - (y1 - y0) * s) / 2 - y0 * s);
    inkStrokes(c, s, h.sample, css("--ink"), 0, 0, h);
  }
}
new ResizeObserver(() => drawHandSamples()).observe($("hands"));

// ---- views (tabs) ------------------------------------------------------------------------------------------------
const VIEWS = ["practice", "hand", "network", "made"];
function route() {
  const v = VIEWS.includes(location.hash.slice(1)) ? location.hash.slice(1) : "practice";
  for (const s of document.querySelectorAll("[data-view]")) s.hidden = s.dataset.view !== v;
  for (const a of document.querySelectorAll(".tabs a")) a.setAttribute("aria-current", a.getAttribute("href") === "#" + v ? "page" : "false");
  if (v === "hand") requestAnimationFrame(drawGuide);
  if (v === "network") requestAnimationFrame(showNetwork);
  if (v === "practice") requestAnimationFrame(() => { refit(); });
}
addEventListener("hashchange", route);

// ---- game and unit -------------------------------------------------------------------------------------------------
// the buttons only: <body> carries data-mode and data-unit too (for the layout), and must not become a button
for (const b of document.querySelectorAll("button[data-mode]")) b.onclick = () => setMode(b.dataset.mode);
for (const b of document.querySelectorAll("button[data-unit]")) b.onclick = () => setUnit(b.dataset.unit);

function setMode(m, reset = true) {
  mode = m; store.set("mode", m);
  for (const b of document.querySelectorAll("button[data-mode]")) b.setAttribute("aria-pressed", String(b.dataset.mode === m));
  document.body.dataset.mode = m;
  $("model-sheet").hidden = m !== "copy";
  $("legend-ghost").hidden = m !== "copy";
  if (reset) restart();
}

function setUnit(u) {
  unit = u; store.set("unit", u);
  for (const b of document.querySelectorAll("button[data-unit]")) b.setAttribute("aria-pressed", String(b.dataset.unit === u));
  document.body.dataset.unit = u;
  $("letters-panel").hidden = u !== "letter";
  $("text-panel").hidden = u !== "text";
  restart();
}

// ---- the letter palette ----------------------------------------------------------------------------------------------
function buildPalette() {
  const tabs = $("palette-tabs");
  tabs.innerHTML = "";
  GROUPS.forEach(([name], i) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "ptab"; b.textContent = name; b.setAttribute("role", "tab");
    b.onclick = () => { group = i; drawPalette(); };
    tabs.appendChild(b);
  });
  drawPalette();
}
function drawPalette() {
  [...$("palette-tabs").children].forEach((b, i) => b.setAttribute("aria-selected", String(i === group)));
  const keys = $("palette-keys");
  keys.innerHTML = "";
  for (const ch of GROUPS[group][1]) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "key"; b.dataset.ch = ch;
    if (style.start.includes(ch)) b.classList.add("first");
    b.setAttribute("aria-label", `Letter ${ch}`);
    b.innerHTML = `<span class="glyph">${ch}</span><span class="stars"></span>`;
    b.onclick = () => chooseLetter(ch);
    keys.appendChild(b);
  }
  updateStars();
}
function chooseLetter(ch) {
  cur = ch; store.set("letter", ch);
  group = Math.max(0, GROUPS.findIndex(g => g[1].includes(ch)));
  if (unit !== "letter") setUnit("letter"); else { drawPalette(); restart(); }
}

// ---- text: phrases, your own text, upload, templates ----------------------------------------------------------------
function buildPhrases() {
  const box = $("phrases");
  box.innerHTML = "";
  for (const [label, t] of PHRASES) {
    const b = document.createElement("button");
    b.type = "button"; b.className = "phrase"; b.dataset.text = t;
    b.innerHTML = `<span>${label === t ? t : `<b>${label}</b> ${t.split("\n")[0].slice(0, 28)}${t.length > 28 ? "…" : ""}`}</span><span class="stars"></span>`;
    b.onclick = () => { $("text-in").value = t; setText(t); };
    box.appendChild(b);
  }
}
$("text-form").onsubmit = e => { e.preventDefault(); setText($("text-in").value); };
$("upload").onchange = async e => {
  const f = e.target.files?.[0];
  if (!f) return;
  try {
    const t = (await f.text()).slice(0, MAX_TEXT);
    $("text-in").value = t; setText(t);
    note(`Loaded ${f.name}.`);
  } catch { note("That file could not be read. Choose a plain-text file (.txt)."); }
  e.target.value = "";
};

function cleanText(t) {
  const pickCh = ch => pickLetter(style, ch);
  const chars = [...t.normalize("NFC").slice(0, MAX_TEXT)];
  const small = [...new Set(chars.filter(ch => !style.letters[ch] && pickCh(ch)))];
  const left = [...new Set(chars.filter(ch => !/\s/.test(ch) && !pickCh(ch)))];
  const kept = t.normalize("NFC").slice(0, MAX_TEXT).split(/\r?\n/)
    .map(line => [...line].map(ch => (/\s/.test(ch) ? " " : pickCh(ch) ?? "")).join("").replace(/\s+/g, " ").trim())
    .filter(Boolean).join("\n");
  const notes = [];
  if (left.length) notes.push(`No model yet, left out: ${left.slice(0, 24).join(" ")}`);
  if (small.length) notes.push(`${style.name} has no ${small.some(ch => ch === ch.toLowerCase()) ? "small letters for" : "capitals for"} ${small.join(" ")}: written as ${style.caps_only ? "capitals" : "small letters"}`);
  return { kept, notes };
}
function setText(t) {
  const { kept, notes } = cleanText(t);
  note(notes.join(". "));
  if (!kept) { note("There is nothing to write: type some letters first."); return; }
  text = kept; store.set("text", text);
  restart();
}
function note(msg) { $("text-note").textContent = msg; }

async function saveFile(filename, blob) {
  // inside claude.ai the viewer saves files for the page (it asks first); elsewhere an ordinary download
  const downloads = window.claude?.use ? await window.claude.use("downloads").catch(() => null) : null;
  if (downloads) {
    try { await downloads.save({ filename, data: blob }); note(`Saved ${filename}.`); }
    catch (e) { note(e?.code === "declined" ? "The download was cancelled." : "The file could not be saved here."); }
    return;
  }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = filename;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
for (const b of document.querySelectorAll("button[data-template]")) b.onclick = () => {
  if (!style) return;
  const kind = b.dataset.template;
  const t = unit === "letter" ? drill(cur) : text;
  const name = unit === "letter" ? `letter ${cur}` : t.split("\n")[0].slice(0, 40);
  const blob = templatePdf(t, style, kind, name);
  saveFile(`${style.id}-${kind === "copy" ? "copybook" : "tracing"}-${slug(name)}.pdf`, blob);
};
const slug = s => s.normalize("NFKD").replace(/[^\w\s-]/g, "").trim().replace(/\s+/g, "-").toLowerCase().slice(0, 32) || "text";
// a drill sheet for one letter: the letter, a space, again, a whole page of rows
const drill = ch => Array.from({ length: 6 }, () => Array(9).fill(ch).join(" ")).join("\n");

// ---- the notebook: layout and pages ---------------------------------------------------------------------------------
const pad = $("pad"), cv = $("cv"), ctx = cv.getContext("2d");
const mv = $("mv"), mctx = mv.getContext("2d");
let scale = 1, mscale = 1;

function restart() {
  stopAnim();
  pageNo = 0; pick = null;
  relayout();
  inkByPage = book.pages.map(() => []);
  resultByPage = [];
  $("report").hidden = true; $("text-report").hidden = true; $("empty").hidden = false;
  $("legend").hidden = true; $("mini-score").hidden = true;
  $("title").textContent = unit === "letter" ? cur : text.split("\n")[0] + (text.includes("\n") ? " …" : "");
  $("verb").textContent = mode === "copy" ? "Copy" : "Trace";
  $("check").textContent = unit === "letter" ? "Check my letter" : "Check this page";
  emptyText();
  showSize();
  showPage();
  updateStars();
  if (!location.hash.slice(1) || location.hash === "#practice") showNetwork();
}

// the sheet's size: 96 x 96 for a letter; for text, about 2.4 screen pixels per canvas pixel (an x-height near 48
// screen pixels at the default size, A− / A+ for the others), 110 to 360 canvas pixels wide, never narrower than the
// longest word at the two smaller sizes, as many rows a page as fit the screen (rowsPerPage)
function relayout() {
  if (!style) return;
  if (unit === "letter") {
    SW = W; SH = H;
    book = { lay: null, words: [cur], pages: [{ items: [{ ch: cur, ox: 0, oy: 0, row: 0, word: 0 }], index: [0], rows: 1, width: W, height: H }] };
  } else {
    const w = pad.getBoundingClientRect().width || 600;
    // never narrower than the longest word at the usual sizes; at the larger sizes a long word may break over two rows
    const want = Math.min(360, Math.max(110, Math.round(w / SIZES[size])));
    SW = size <= 1 ? Math.max(Math.ceil(longestWord(text, style, EDGE)), want) : want;
    const lay = layout(text, style, SW, { edge: EDGE });
    const words = [];
    for (const it of lay.items) words[it.word] = (words[it.word] ?? "") + it.ch;
    const rows = rowsPerPage(w / SW);
    book = { lay, words, pages: paginate(lay, rows) };
    SH = rows * PITCH + 8;
    if (book.pages.length === 1) SH = book.pages[0].height;
  }
  for (const el of [pad, mv.parentElement]) el.style.aspectRatio = `${SW} / ${SH}`;
}

// as many rows as fit the screen's height beside the notebook's head and toolbar (1 to 8), so the whole page shows
// without scrolling; in focus the notebook has the whole screen
function rowsPerPage(px) {
  const head = document.querySelector(".nb-head")?.offsetHeight ?? 50, bar = document.querySelector(".toolbar")?.offsetHeight ?? 60;
  const room = window.innerHeight - head - bar - 90;
  return Math.max(1, Math.min(8, Math.floor((room / px - 8) / PITCH)));
}
// the writing size: only before anything is written on the text (the letters are laid out again)
function setSize(k) {
  if (k < 0 || k >= SIZES.length || k === size) return;
  if (inkByPage.some(s => s.length) || resultByPage.some(Boolean)) { flash("Clear the pages first: the text is laid out again at the new size."); return; }
  size = k; store.set("size", k);
  relayout(); inkByPage = book.pages.map(() => []); pageNo = 0; showSize(); showPage();
}
function showSize() {
  $("size-row").hidden = unit !== "text";
  $("smaller").disabled = size === 0; $("larger").disabled = size === SIZES.length - 1;
}
$("smaller").onclick = () => setSize(size - 1);
$("larger").onclick = () => setSize(size + 1);

function showPage() {
  const n = pages().length;
  $("pager").hidden = n < 2;
  $("page-label").textContent = `Page ${pageNo + 1} of ${n}`;
  $("prev-page").disabled = pageNo === 0;
  $("next-page").disabled = pageNo === n - 1;
  const r = result();
  $("legend").hidden = !r;
  $("mini-score").hidden = !r;
  if (r) miniScore(r.overall);
  if (unit === "text") { showPageReport(); }
  draw(); drawModel();
}
$("prev-page").onclick = () => { if (pageNo > 0) { pageNo--; pick = null; showPage(); } };
$("next-page").onclick = () => { if (pageNo < pages().length - 1) { pageNo++; pick = null; showPage(); } };

// the model as letters on the current page: [{ ch, ox, oy, row, strokes (on the sheet) }]
function letters() {
  if (!style) return [];
  const pg = page();
  if (unit === "letter") return [{ ch: cur, ox: 0, oy: 0, row: 0, strokes: style.letters[cur] }];
  const M = sheetModel(pg, style);
  return pg.items.map((it, k) => ({ ...it, strokes: M[k] }));
}

// ---- drawing --------------------------------------------------------------------------------------------------------
function css(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }
function fitCanvas(canvas, c, box) {
  const r = box.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
  canvas.width = Math.max(1, Math.round(r.width * dpr)); canvas.height = Math.max(1, Math.round(r.height * dpr));
  c.setTransform(dpr, 0, 0, dpr, 0, 0);
  return r.width / SW;
}
let lastW = 0, lastH = 0;
function refit() {
  const w = pad.getBoundingClientRect().width;
  if (!w) return;
  // a text is laid out again for a new width or screen height, but only before anything is written (never under your ink)
  if (unit === "text" && (Math.abs(w - lastW) > 1 || Math.abs(window.innerHeight - lastH) > 40) && inkByPage.every(s => !s.length) && !resultByPage.length && style) {
    lastW = w; lastH = window.innerHeight; relayout(); inkByPage = book.pages.map(() => []); pageNo = Math.min(pageNo, pages().length - 1); showPage();
  }
  scale = fitCanvas(cv, ctx, pad); draw();
  mscale = fitCanvas(mv, mctx, mv.parentElement); drawModel();
}
new ResizeObserver(refit).observe(pad);
window.addEventListener("resize", refit);
new ResizeObserver(() => { mscale = fitCanvas(mv, mctx, mv.parentElement); drawModel(); }).observe(mv.parentElement);
// a change of theme (the system's, or the viewer's own switch on the root element) redraws every canvas in its colours
const repaint = () => { for (const k in RGB) delete RGB[k]; draw(); drawModel(); drawGuide(); drawHandSamples(); };
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", repaint);
new MutationObserver(repaint).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

// the paper: slant lines every 12 px at the hand's slant, the four guidelines of each row, and (text) the margin line
function guides(c, s, w, h, rows = 1, margin = false) {
  c.fillStyle = css("--paper"); c.fillRect(0, 0, w * s, h * s);
  c.lineWidth = 1; c.strokeStyle = css("--guide");
  for (let x0 = -h * style.slant - 10; style.slant > 0.05 && x0 < w + 10; x0 += 12) {
    c.beginPath(); c.moveTo(x0 * s, h * s); c.lineTo((x0 + h * style.slant) * s, 0); c.stroke();
  }
  for (let r = 0; r < rows; r++) for (const [name, y] of Object.entries(style.guides)) {
    c.strokeStyle = ["baseline", "x-height", "cap height"].includes(name) ? css("--guide-strong") : css("--guide");
    c.lineWidth = name === "baseline" ? 1.6 : 1;
    c.beginPath(); c.moveTo(0, (y + r * PITCH) * s); c.lineTo(w * s, (y + r * PITCH) * s); c.stroke();
  }
  if (margin) {
    c.strokeStyle = css("--margin-line"); c.lineWidth = 1.4;
    c.beginPath(); c.moveTo((EDGE - 5) * s, 0); c.lineTo((EDGE - 5) * s, h * s); c.stroke();
  }
}
const sheetGuides = (c, s) => guides(c, s, SW, SH, unit === "letter" ? 1 : Math.round((SH - 8) / PITCH), unit === "text");

// strokes as ink: a pointed pen at the width of each point; a broad nib as the shape its edge sweeps
function inkStrokes(c, s, list, color, dx = 0, dy = 0, hand = style) {
  c.strokeStyle = c.fillStyle = color;
  c.lineCap = "round"; c.lineJoin = "round";
  if (hand?.pen === "broad") {
    for (const st of list) {
      for (const q of nibSweep(st, hand)) {
        c.beginPath(); q.forEach(([x, y], i) => (i ? c.lineTo : c.moveTo).call(c, (x + dx) * s, (y + dy) * s)); c.closePath(); c.fill();
      }
      c.lineWidth = hand.hair * s;                          // the nib's edge leaves a hairline where it moves sideways
      c.beginPath(); st.forEach(([x, y], i) => (i ? c.lineTo : c.moveTo).call(c, (x + dx) * s, (y + dy) * s)); c.stroke();
    }
    return;
  }
  if (hand?.square) {                                        // a square pen end (Neuland)
    for (const st of list) for (const q of squareSweep(st, hand.mono)) {
      c.beginPath(); q.forEach(([x, y], i) => (i ? c.lineTo : c.moveTo).call(c, (x + dx) * s, (y + dy) * s)); c.closePath(); c.fill();
    }
    return;
  }
  for (const st of list) {
    if (st.length === 1) { c.beginPath(); c.arc((st[0][0] + dx) * s, (st[0][1] + dy) * s, (st[0][2] / 2) * s, 0, Math.PI * 2); c.fill(); continue; }
    for (let k = 1; k < st.length; k++) {
      c.lineWidth = ((st[k - 1][2] + st[k][2]) / 2) * s;
      c.beginPath(); c.moveTo((st[k - 1][0] + dx) * s, (st[k - 1][1] + dy) * s); c.lineTo((st[k][0] + dx) * s, (st[k][1] + dy) * s); c.stroke();
    }
  }
}
function inkUpTo(c, s, list, color, upto) {
  let left = upto;
  const part = [];
  for (const st of list) {
    if (left <= 0) break;
    if (st.length === 1) { part.push(st); continue; }
    const out = [st[0]];
    for (let k = 1; k < st.length && left > 0; k++) {
      const L = Math.hypot(st[k][0] - st[k - 1][0], st[k][1] - st[k - 1][1]);
      if (L <= left) { out.push(st[k]); left -= L; }
      else { const f = left / L; out.push(st[k - 1].map((v, j) => v + f * (st[k][j] - v))); left = 0; }
    }
    part.push(out);
  }
  inkStrokes(c, s, part, color);
}
// stroke numbers beside each start and an arrow along its first few pixels; numbers that meet are pushed apart
function startMarks(c, s, list) {
  const placed = [];
  const accent = css("--accent"), paper = css("--paper");
  const number = (x, y, n) => {
    for (let k = 0; k < 4 && placed.some(([px, py]) => Math.hypot(px - x, py - y) < 4.6); k++) y -= 4.6;
    placed.push([x, y]);
    c.fillStyle = accent; c.beginPath(); c.arc(x * s, y * s, 2.1 * s, 0, Math.PI * 2); c.fill();
    c.fillStyle = paper; c.font = `700 ${2.6 * s}px ${css("--f-mono")}`;
    c.textAlign = "center"; c.textBaseline = "middle"; c.fillText(String(n), x * s, y * s + 0.2 * s);
  };
  list.forEach((st, k) => {
    const [x, y] = st[0];
    if (st.length === 1) { number(x + 3.2, y - 2.4, k + 1); return; }
    let j = 1;
    while (j < st.length - 1 && Math.hypot(st[j][0] - x, st[j][1] - y) < 4) j++;
    const dx = st[j][0] - x, dy = st[j][1] - y, L = Math.hypot(dx, dy) || 1, ux = dx / L, uy = dy / L;
    const ax = x + ux * 6, ay = y + uy * 6;
    c.strokeStyle = c.fillStyle = accent; c.lineWidth = 1.5;
    c.beginPath(); c.moveTo((x + ux * 1.5) * s, (y + uy * 1.5) * s); c.lineTo(ax * s, ay * s); c.stroke();
    c.beginPath();
    c.moveTo((ax + ux * 1.6) * s, (ay + uy * 1.6) * s);
    c.lineTo((ax - uy * 1.1) * s, (ay + ux * 1.1) * s);
    c.lineTo((ax + uy * 1.1) * s, (ay - ux * 1.1) * s);
    c.closePath(); c.fill();
    number(x - ux * 3.2 - uy * 2.2, y - uy * 3.2 + ux * 2.2, k + 1);
  });
}

function draw(progress = null) {
  if (!style || !book) { ctx.fillStyle = css("--paper"); ctx.fillRect(0, 0, SW * scale, SH * scale); return; }
  sheetGuides(ctx, scale);
  const L = letters(), r = result();
  if (mode === "trace") {
    // dots along the model, sized by the pen width there (bigger dots = press harder)
    const all = L.flatMap(l => l.strokes), total = all.reduce((a, st) => a + strokeLength(st), 0);
    let done = 0;
    const accent = css("--accent"), dots = css("--dots");
    for (const st of all) {
      for (const p of dotsAlong(st, 2.4)) {
        ctx.fillStyle = progress != null && done + p.at <= progress * total ? accent : dots;
        ctx.beginPath(); ctx.arc(p.x * scale, p.y * scale, Math.max(0.6, p.w * 0.42) * scale, 0, Math.PI * 2); ctx.fill();
      }
      done += strokeLength(st);
    }
    if (progress == null) for (const l of L) startMarks(ctx, scale, l.strokes);
    inkStrokes(ctx, scale, strokes(), css("--ink"));
  } else {
    // after a check, the model faintly beside your writing (its own size, slant and height), moved sideways to where
    // you wrote, with what you missed of it marked on it
    if (r) for (const x of r.per) if (x.T) besideFit(ctx, scale, x, () => {
      inkStrokes(ctx, scale, style.letters[x.ch], css("--ghost"));
      overlay(ctx, scale, x, "model");
    });
    inkStrokes(ctx, scale, strokes(), css("--ink"));
  }
  // the faults in your ink, on your ink (copy game: taken back through the fit)
  if (r) for (const x of r.per) if (x.T) withFit(ctx, scale, x, () => overlay(ctx, scale, x, mode === "copy" ? "yours" : "all"));
  // the letter you picked in the report, ringed
  if (unit === "text" && r && pick != null && r.per[pick] && (pickedByHand || r.per[pick].overall < 90)) {
    const x = r.per[pick], it = page().items[pick];
    ctx.strokeStyle = css("--accent"); ctx.lineWidth = 2; ctx.setLineDash([4, 4]);
    const x0 = (it ? it.xmin ?? x.ox + 20 : 20) - 3, x1 = (it ? it.xmax ?? x.ox + 76 : 76) + 3;
    ctx.strokeRect(x0 * scale, (x.oy + 6) * scale, (x1 - x0) * scale, 84 * scale);
    ctx.setLineDash([]);
  }
}

function besideYours(M, [a, , c, d, e, f]) {
  // the sideways move that puts the model's centre on the slant line through your letter's centre
  const P = samples(M);
  let mx = 0, my = 0;
  for (const p of P) { mx += p[0]; my += p[1]; }
  mx /= P.length; my /= P.length;
  const Y = (my - f) / d, X = (mx - c * Y - e) / a;
  return X - style.slant * (my - Y) - mx;
}
function besideFit(c, s, r, paint) {
  c.save(); c.translate((r.ox + r.gdx) * s, r.oy * s); paint(); c.restore();
}
function withFit(c, s, r, paint) {
  // a letter's model frame, placed where it was written: its frame on the sheet, then (copy) the inverse of the fit
  c.save();
  c.translate(r.ox * s, r.oy * s);
  if (r.fit) {
    const [a, , cc, d, e, f] = r.fit, ia = 1 / a, ic = -cc / (a * d), id = 1 / d;
    c.transform(ia, 0, ic, id, -(ia * e + ic * f) * s, -id * f * s);
  }
  paint();
  c.restore();
}

// the model sheet in the copy game: ink with stroke numbers (or written out by "Show me")
function drawModel(progress = null) {
  if (!style || !book || mode !== "copy") return;
  guides(mctx, mscale, SW, SH, unit === "letter" ? 1 : Math.round((SH - 8) / PITCH), unit === "text");
  const L = letters(), all = L.flatMap(l => l.strokes), total = all.reduce((a, st) => a + strokeLength(st), 0);
  if (progress == null) { inkStrokes(mctx, mscale, all, css("--ink")); for (const l of L) startMarks(mctx, mscale, l.strokes); }
  else { inkStrokes(mctx, mscale, all, css("--ghost")); inkUpTo(mctx, mscale, all, css("--accent"), progress * total); }
}

// where the faults are: the comparison maps of a letter (kept as bytes), coloured, at the letter's place
// which: "model" (missed: on the model's ink), "yours" (on your ink), or "all" (tracing: one place)
const OVERLAY_MAPS = ["missed", "off_track", "opp_dn", "opp_up", "opp_lf", "opp_rt", "shade_miss", "hair_thick"];
const VIEW_MAPS = ["m_on_b", "m_on", "a_on", "on_track"];
function overlay(c, s, x, which) {
  const m = x.maps, img = new ImageData(W, H), d = img.data;
  const layers = [];
  if (which !== "yours") layers.push([css("--miss"), i => m.missed[i]]);
  if (which !== "model") {
    layers.push([css("--off"), i => m.off_track[i]], [css("--back"), i => Math.max(m.opp_dn[i], m.opp_up[i], m.opp_lf[i], m.opp_rt[i])]);
    if (pressureUsed()) layers.push([css("--press"), i => Math.max(m.shade_miss[i], m.hair_thick[i])]);
  }
  for (const [color, f] of layers) {
    const [r, g, b] = rgb(color);
    for (let i = 0; i < W * H; i++) {
      const a = f(i);
      if (a < 13) continue;
      d[4 * i] = r; d[4 * i + 1] = g; d[4 * i + 2] = b; d[4 * i + 3] = Math.max(d[4 * i + 3], Math.round((150 * a) / 255));
    }
  }
  const off = document.createElement("canvas"); off.width = W; off.height = H;
  off.getContext("2d").putImageData(img, 0, 0);
  c.imageSmoothingEnabled = true;
  c.drawImage(off, 0, 0, W * s, H * s);
}
const RGB = {};
function rgb(color) {
  if (!RGB[color]) { const c = document.createElement("canvas").getContext("2d"); c.fillStyle = color; c.fillRect(0, 0, 1, 1); RGB[color] = c.getImageData(0, 0, 1, 1).data; }
  return RGB[color];
}

// ---- pen input --------------------------------------------------------------------------------------------------------
function widthFor(e) {
  if (e.pointerType === "pen") penSeen = true;
  if (style.pen === "mono") return style.mono;
  if (style.pen === "broad") return style.nib;                // set from the direction as the stroke moves (nibWidth)
  if (e.pointerType !== "pen") return NO_PRESSURE_WIDTH;
  const p = e.pressure;
  if (p > 0 && p !== 0.5) pressureSeen = true;               // 0.5 is what a pen without pressure reports
  if (!pressureSeen) return NO_PRESSURE_WIDTH;
  const f = Math.min(1, Math.max(0, (p - 0.2) / 0.45));     // light touch = hairline, firm press = full shade
  return style.hair + (style.shade - style.hair) * f * f * (3 - 2 * f);
}
// a broad nib: the width from the direction of travel, as the model letters get it (Hand.width in gen/styles.py)
function nibWidth(dx, dy) {
  const n = Math.hypot(dx, dy) || 1, a = (style.nib_angle * Math.PI) / 180;
  return Math.max(style.hair, (style.nib * Math.abs(dx * Math.sin(a) + dy * Math.cos(a))) / n);
}
// shading is marked only with a pointed pen that reports pressure
const pressureUsed = () => style.pen === "pointed" && pressureSeen;
function penGate(e) {
  // the first pen turns "Pen only" on (a palm or finger on the sheet is then ignored); it can be turned off
  if (e.pointerType === "pen" && penOnly == null) { penOnly = true; showPenOnly(); }
  return !(penOnly && e.pointerType === "touch");
}
function showPenOnly() { $("pen-only").hidden = false; $("pen-only").setAttribute("aria-pressed", String(!!penOnly)); }
$("pen-only").onclick = () => { penOnly = !penOnly; showPenOnly(); };
function point(e) {
  const r = pad.getBoundingClientRect();
  return [((e.clientX - r.left) / r.width) * SW, ((e.clientY - r.top) / r.height) * SH, widthFor(e)];
}
pad.addEventListener("pointerdown", e => {
  if (!style || checking) return;
  e.preventDefault();
  if (!penGate(e) || live) return;
  stopAnim();
  try { pad.setPointerCapture(e.pointerId); } catch { /* capture is a nicety: the stroke still works without it */ }
  if (result()) { resultByPage[pageNo] = undefined; $("legend").hidden = true; $("mini-score").hidden = true; }
  live = [point(e)]; livePointer = e.pointerId; strokes().push(live);
  draw(); inputNote();
});
pad.addEventListener("pointermove", e => {
  if (!live || e.pointerId !== livePointer) return;
  const co = e.getCoalescedEvents?.();
  for (const ev of (co && co.length ? co : [e])) {
    const p = point(ev), q = live[live.length - 1];
    if (Math.hypot(p[0] - q[0], p[1] - q[1]) < 0.5) continue;
    if (style.pen === "broad") {                             // the width of each point from its neighbours, as in the model
      const r = live[live.length - 2] ?? q;
      q[2] = nibWidth(p[0] - r[0], p[1] - r[1]);
      p[2] = nibWidth(p[0] - q[0], p[1] - q[1]);
      if (live.length === 1) q[2] = p[2];
    }
    live.push(p);
  }
  draw();
});
const end = e => { if (e.pointerId === livePointer) { live = null; livePointer = null; } };
pad.addEventListener("pointerup", end);
pad.addEventListener("pointercancel", end);
function inputNote() {
  if (!style) return;
  $("input-mode").textContent = style.pen === "broad" ? `Broad nib at ${style.nib_angle}°: the width follows your direction; shading is not marked`
    : style.pen === "mono" ? "Even, heavy strokes: shading is not marked"
    : pressureSeen ? "Pen pressure on: shading is marked"
    : penSeen ? "Pen without pressure: shading is not marked" : "Mouse or finger: shading is not marked";
}

// ---- checking ---------------------------------------------------------------------------------------------------------
const TIPS = {
  f_off: () => mode === "copy" ? "Part of your letter strays from the model's path (red, with the model in grey beside it). Compare the two shapes and try again."
    : "Some of your ink wandered off the dotted path (red). Slow down and keep the pen on the dots.",
  f_miss: () => mode === "copy" ? "Parts of the model are missing from your letter (amber). Check every stroke, hairlines included."
    : "Parts of the letter are missing (amber). Trace the whole path, hairlines included.",
  f_back: () => "A stroke ran the wrong way (violet). Start each stroke at its number and follow the arrow.",
  f_order: () => "The strokes came in the wrong order. Write stroke 1 first, then 2, and so on.",
  f_thin: () => "Press on the downstrokes: they should swell thick (blue marks the thin ones).",
  f_thick: () => "Ease off on the upstrokes: hairlines want almost no pressure (blue marks the heavy ones).",
  f_upright: () => `Your letter stands too upright. ${style.name} leans at ${Math.round(90 - style.slant_deg)}°: keep each downstroke parallel to the slanted guidelines.`,
  f_slanted: () => style.slant_deg ? `Your letter leans too far. ${style.name} leans at ${Math.round(90 - style.slant_deg)}°: keep each downstroke parallel to the slanted guidelines.`
    : `Your letter leans. ${style.name} is upright: keep each downstroke vertical.`,
  f_big: () => "Your letter is too big. The body sits between the baseline and the x-height line; only loops and stems reach the outer lines.",
  f_small: () => "Your letter is too small, or sits low. The body fills the space from the baseline up to the x-height line.",
};
const FAULTS = Object.keys(TIPS);
function tipFor(T, overall) {
  // slant and size are marked only in the copy game (when tracing, the dots set them)
  const [f, v] = FAULTS.filter(f => mode === "copy" || !["f_upright", "f_slanted", "f_big", "f_small"].includes(f))
    .map(f => [f, T[f]]).sort((a, b) => b[1] - a[1])[0];
  return v > (overall >= 90 ? 0.08 : 0.03) ? TIPS[f]() : null;
}
function scoreOf(T, copy) {
  const p = pressureUsed();
  return copy ? (p ? T.overall_copy_pressure : T.overall_copy_no_pressure) : (p ? T.overall_pressure : T.overall_no_pressure);
}
// what a checked letter keeps: the network's numbers, and its comparison maps as bytes (the full set is megabytes)
function slim(T) {
  const scalars = {}, maps = {};
  for (const [k, v] of Object.entries(T)) if (typeof v === "number") scalars[k] = v;
  for (const k of [...OVERLAY_MAPS, ...VIEW_MAPS]) maps[k] = Uint8ClampedArray.from(T[k], v => Math.round(255 * Math.min(1, Math.max(0, v))));
  return { scalars, maps };
}

async function check() {
  if (!net || checking) return;
  const list = strokes().filter(st => st.length);
  if (!list.length) { flash(unit === "text" ? "Write on this page first, then check it." : "Write the letter on the sheet first."); return; }
  checking = true; $("check").disabled = true;
  const copy = mode === "copy", L = letters(), pg = page();
  const pieces = unit === "letter" ? [list] : segment(list, pg, style, copy ? copySlots(list, pg, style) : undefined);
  const per = [];
  for (let k = 0; k < L.length; k++) {
    const l = L[k], M = style.letters[l.ch], P = pieces[k];
    const base = { ch: l.ch, ox: l.ox, oy: l.oy, row: l.row, word: pg.items[k].word, T: null, maps: null, overall: 0, fit: null, gdx: 0 };
    if (P.length) {
      const { scalars, maps } = slim(net.forward(inputs(M, P, pressureUsed(), copy)));
      const F = copy ? fitLetter(M, P) : null;
      Object.assign(base, { T: scalars, maps, overall: Math.round(100 * scoreOf(scalars, copy)), fit: F, gdx: F ? besideYours(M, F) : 0 });
    }
    per.push(base);
    if (L.length > 6 && k % 4 === 3) {                     // a long page: show progress, keep the page responsive
      $("check").textContent = `Checking ${k + 1} of ${L.length}…`;
      await new Promise(r => setTimeout(r));
    }
  }
  const overall = Math.round(per.reduce((a, r) => a + r.overall, 0) / per.length);
  resultByPage[pageNo] = { per, overall, pressure: pressureUsed(), copy };
  checking = false; $("check").disabled = false;
  $("check").textContent = unit === "letter" ? "Check my letter" : "Check this page";
  const key = starKey(unit === "letter" ? `${mode}:${cur}` : `${mode}:text:${text}`);
  const whole = unit === "letter" ? overall : textScore();
  if (whole != null && (best[key] == null || whole > best[key])) { best[key] = whole; store.set("best", best); }
  pick = per.reduce((w, r, k) => (r.overall < per[w].overall ? k : w), 0); pickedByHand = false;
  $("legend").hidden = false; $("legend-press").hidden = !pressureUsed();
  miniScore(overall);
  if (unit === "letter") showLetterReport(); else { showPageReport(); showTextReport(); }
  updateStars(); draw(); showNetwork();
}
// the whole text's score, once every page is checked
function textScore() {
  if (pages().some((_, i) => !resultByPage[i])) return null;
  const all = resultByPage.flatMap(r => r.per);
  return Math.round(all.reduce((a, r) => a + r.overall, 0) / all.length);
}
function miniScore(v) {
  const n = starsFor(v);
  $("mini-score").hidden = false;
  $("mini-score").innerHTML = `${v}<span class="st">${"★".repeat(n)}${"☆".repeat(3 - n)}</span>`;
}
$("mini-score").onclick = () => $("marks").scrollIntoView({ behavior: "smooth", block: "start" });
function flash(msg) { $("hint").textContent = msg; }

// ---- reports -------------------------------------------------------------------------------------------------------
const ordinal = k => ["first", "second", "third"][k] ?? `${k + 1}th`;
function stars(n) { return `<span class="on">${"★".repeat(n)}</span><span class="off">${"★".repeat(3 - n)}</span>`; }
function bars(box, marks, copy, pressure) {
  const rows = [["shape", "Shape", true], ["ductus", "Ductus", true], ["shading", "Shading", pressure], ["form", "Form", copy]];
  box.innerHTML = rows.filter(r => r[0] !== "form" || copy).map(([k, name, on]) => {
    const v = on ? marks[k] : null;
    return `<div class="bar${on ? "" : " na"}"><span class="name">${name}</span><span class="track"><span class="fill" style="width:${on ? v : 0}%"></span></span><span class="val">${on ? v : "–"}</span></div>`;
  }).join("");
}
function emptyText() {
  const copy = mode === "copy", text_ = unit === "text";
  $("empty-text").textContent = copy
    ? (text_ ? "Copy each row of the model into the row level with it on your page. Join the letters or lift between them; your spacing, place, size and slant need not match exactly (size and slant count in form)."
      : "Look at the model, then write it anywhere on your sheet. Your letter is fitted onto the model, so shape and ductus mark how precise your strokes are; slant and size count in form.")
    : (text_ ? "Trace the page, letter by letter. Each letter has its own stroke numbers; join a letter's exit hairline into the next one's entrance as you like. Check each page when it is done."
      : style.pen === "broad" ? `Start at the small number 1 and follow the arrow. Hold the nib at ${style.nib_angle}° and keep it there: the thick and thin come from the direction you move.`
      : style.pen === "mono" ? "Start at the small number 1 and follow the arrow. Heavy, even strokes: keep them steady and square."
      : "Start at the small number 1 and follow the arrow. Downstrokes are thick, upstrokes are hairlines: with a pen, press on the way down and ease off on the way up.");
}
function noPressureNote(copy) {
  const w = copy ? "45% shape, 35% ductus and 20% form" : "60% shape and 40% ductus";
  if (style.pen !== "pointed") return `With a ${style.pen === "broad" ? "broad nib the width comes from the direction" : "heavy even pen there is no thick and thin"}, so shading is not marked: the score is ${w}.`;
  return pressureSeen ? "" : `Shading needs a pen with pressure (a stylus on a tablet). Without it, the score is ${w}.`;
}

function showLetterReport() {
  const r = result(), x = r.per[0];
  $("empty").hidden = true; $("report").hidden = false; $("text-report").hidden = true;
  $("page-head").hidden = true;
  $("overall").textContent = r.overall;
  $("stars").innerHTML = stars(starsFor(r.overall));
  bars($("bars"), Object.fromEntries(["shape", "ductus", "shading", "form"].map(k => [k, Math.round(100 * (x.T?.[k] ?? 0))])), r.copy, r.pressure);
  $("tip").textContent = (x.T && tipFor(x.T, r.overall)) ?? (r.overall >= 90 ? "Lovely: every stroke the right way and in order. On to the next one." : "Close. Try once more, a little slower.");
  $("pressure-note").textContent = noPressureNote(r.copy);
  $("per").hidden = true;
  $("next").textContent = "Next letter →";
}

function showPageReport() {
  const r = result();
  $("report").hidden = !r;
  $("empty").hidden = !!r || resultByPage.some(Boolean);
  if (!r) { if (resultByPage.some(Boolean)) $("empty").hidden = true; return; }
  $("page-head").hidden = pages().length < 2;
  $("page-head").textContent = `Page ${pageNo + 1}`;
  $("overall").textContent = r.overall;
  $("stars").innerHTML = stars(starsFor(r.overall));
  const mean = k => Math.round(100 * r.per.reduce((a, x) => a + (x.T ? x.T[k] : 0), 0) / r.per.length);
  bars($("bars"), { shape: mean("shape"), ductus: mean("ductus"), shading: mean("shading"), form: mean("form") }, r.copy, r.pressure);
  const w = r.per.reduce((w, x, k) => (x.overall < r.per[w].overall ? k : w), 0), x = r.per[w];
  const where = `The ${ordinal(w)} letter on this page, “${x.ch}”`;
  $("tip").textContent = !x.T ? `${where}, is missing: nothing was written in its place.`
    : x.overall < 90 ? `${where}, scored ${x.overall}. ${tipFor(x.T, x.overall) ?? "Try it once more, a little slower."}`
    : "Every letter on this page at three stars.";
  $("pressure-note").textContent = noPressureNote(r.copy);
  // a chip per letter, grouped by words
  const box = $("per"); box.hidden = false; box.innerHTML = "";
  let word = null;
  r.per.forEach((p, k) => {
    if (p.word !== word) {
      word = p.word;
      const g = document.createElement("span"); g.className = "word"; box.appendChild(g);
    }
    const b = document.createElement("button");
    b.type = "button"; b.className = `chip s${starsFor(p.overall)}`;
    b.setAttribute("aria-label", `Letter ${k + 1}, ${p.ch}: ${p.overall}`);
    b.innerHTML = `<b>${p.ch}</b><small>${p.overall}</small>`;
    b.onclick = () => { pick = k; pickedByHand = true; draw(); showNetwork(); markPick(); };
    box.lastChild.appendChild(b);
  });
  markPick();
  const more = pageNo < pages().length - 1;
  $("next").textContent = more ? "Next page →" : "Next phrase →";
}
function markPick() {
  [...$("per").querySelectorAll(".chip")].forEach((b, k) => b.setAttribute("aria-current", String(k === pick)));
}

function showTextReport() {
  const done = resultByPage.map((r, i) => [r, i]).filter(([r]) => r);
  if (!done.length) { $("text-report").hidden = true; return; }
  $("text-report").hidden = false;
  const letters_ = done.flatMap(([r]) => r.per);
  const copy = done[0][0].copy, pressure = done.some(([r]) => r.pressure);
  const S = summarize(letters_, book.words, { copy, pressure, slant: 90 - style.slant_deg });
  const n = pages().length;
  $("tr-progress").textContent = n > 1 ? `${done.length} of ${n} pages checked · ${S.written} of ${S.n} letters written` : `${S.written} of ${S.n} letters written`;
  $("tr-overall").textContent = S.overall;
  $("tr-stars").innerHTML = stars(starsFor(S.overall));
  bars($("tr-bars"), { shape: S.marks.shape, ductus: S.marks.ductus, shading: S.marks.shading ?? 0, form: S.marks.form ?? 0 }, copy, pressure);
  $("tr-words").innerHTML = S.words.map(w => `<span class="wchip s${starsFor(w.score)}" title="${w.score}">${esc(w.text)}<small>${w.score}</small></span>`).join("");
  $("tr-weak").innerHTML = S.weakest.length ? S.weakest.map(c => `
    <li><span class="g">${esc(c.ch)}</span><span class="what"><b>${c.score}</b> · ${c.n === 1 ? "once" : `${c.n} times`}${c.fault ? ` · ${FAULT_NAMES[c.fault].name.toLowerCase()}` : ""}</span>
    <button class="btn small" type="button" data-practise="${esc(c.ch)}">Practise</button></li>`).join("")
    : `<li class="none">Every letter you wrote scored 90 or more.</li>`;
  for (const b of $("tr-weak").querySelectorAll("[data-practise]")) b.onclick = () => { chooseLetter(b.dataset.practise); window.scrollTo({ top: 0, behavior: "smooth" }); };
  const top = Math.max(1, ...S.faults.map(f => f.points));
  $("tr-faults").innerHTML = S.faults.length ? S.faults.slice(0, 6).map(f => `
    <div class="fbar"><span class="name">${FAULT_NAMES[f.f].name}</span><span class="track"><span class="fill" style="width:${(100 * f.points) / top}%"></span></span>
    <span class="val">${f.points.toFixed(1)}</span><span class="ex">${f.worst.length ? "most in " + f.worst.map(esc).join(" ") : ""}</span></div>`).join("")
    : `<p class="muted">No fault cost more than half a point per letter.</p>`;
  $("tr-advice").innerHTML = S.advice.map(a => `<li>${esc(a.text)}</li>`).join("") || "<li>Keep going: try a longer text, or the copy game.</li>";
  const steady = $("tr-steady");
  steady.hidden = !S.slant;
  if (S.slant) {
    const d = S.slant.you - S.slant.model, lean = Math.abs(d) < 1 ? "the model's slant" : `${Math.abs(d).toFixed(0)}° ${d > 0 ? "more upright" : "more slanted"} than the model`;
    steady.innerHTML = `
      <div><span class="k">Slant</span><b>${lean}</b> on average, varying ±${S.slant.spread.toFixed(0)}° from letter to letter</div>
      <div><span class="k">Size</span><b>${S.size.ratio.toFixed(2)}×</b> the model's on average, varying ±${Math.round(100 * S.size.spread)}%</div>`;
  }
}
const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

// ---- inside the network (its own view) -------------------------------------------------------------------------------
const MAPS = [
  ["band", "The model, widened", "the model's ink (dark) and its tolerance band (light)"],
  ["a_on", "Your ink", "your solid ink, through the same encoder"],
  ["on_track", "On the path", "your ink AND the band"],
  ["off_track", "Off the path", "your ink AND NOT the band"],
  ["missed", "Missed", "model ink with none of yours near it"],
  ["backwards", "Backwards", "you move one way where the model moves the other"],
];
function showNetwork() {
  const r = result();
  const x = r && pick != null ? r.per[pick] : null;
  $("net-empty").hidden = !!x?.T;
  $("net").hidden = !x?.T;
  $("net-empty").textContent = x && !x.T ? `The letter “${x.ch}” has no ink of yours, so there is nothing to show.`
    : "Check a letter or a page on the Practice tab; the letter you pick in your report appears here.";
  if (!x?.T) return;
  const T = x.T, m = x.maps;
  $("net-which").textContent = unit === "letter" ? `Your “${x.ch}”, scored ${x.overall}.`
    : `The letter “${x.ch}” on page ${pageNo + 1}, scored ${x.overall}. The network sees it on its own 96 × 96 grid, cut from your writing.`;
  const box = $("maps"); box.innerHTML = "";
  const inkc = rgb(css("--ink")), paper = rgb(css("--paper"));
  for (const [key, title, how] of MAPS) {
    const val = i => key === "backwards" ? Math.max(m.opp_dn[i], m.opp_up[i], m.opp_lf[i], m.opp_rt[i])
      : key === "band" ? Math.max(0.3 * m.m_on_b[i], m.m_on[i]) : m[key][i];
    const c = document.createElement("canvas"); c.width = W; c.height = H;
    const img = new ImageData(W, H);
    for (let i = 0; i < W * H; i++) {
      const a = Math.min(255, val(i)) / 255;
      for (let ch = 0; ch < 3; ch++) img.data[4 * i + ch] = Math.round(paper[ch] + (inkc[ch] - paper[ch]) * a);
      img.data[4 * i + 3] = 255;
    }
    c.getContext("2d").putImageData(img, 0, 0);
    const fig = document.createElement("figure");
    const cap = document.createElement("figcaption");
    cap.innerHTML = `<b>${title}</b><span>${how}</span>`;
    c.setAttribute("aria-label", title);
    fig.append(c, cap); box.appendChild(fig);
  }
  const rows = [
    ["stay", "share of your ink on the path", "n_on / (n_on + n_off)"],
    ["cover", "share of the model you covered", "n_cov / (n_cov + n_miss)"],
    ["direction", "share of shared ink moving the model's way", "n_same / (n_same + n_opp)"],
    ["order_slip", "share of your ink written much earlier or later than the model's", "(n_late + n_early) / n_on"],
    ["shade_hit", "share of the model's shaded strokes you wrote thick", "n_shade_hit / (n_shade_hit + n_shade_miss)"],
    ["hair_slip", "share of the model's hairlines you wrote thick", "n_hair_thick / n_hair_cov"],
    ["shape", "mark", "clip(stay + cover − 1)"],
    ["ductus", "mark", "clip(1.5 direction − 1.5 order_slip − 0.5)"],
    ["shading", "mark", "clip(0.7 shade_hit − 0.7 hair_slip + 0.3)"],
  ];
  if (mode === "copy") rows.push(
    ["lean_gap", "your slope of x on y minus the model's (+ = more upright)", "a_slope − m_slope"],
    ["size2", "your spread in height over the model's, squared", "a_vy / m_vy"],
    ["form", "mark", "clip(1 − f_upright − f_slanted − f_big − f_small)"]);
  $("measures").innerHTML = rows.map(([k, what, how]) =>
    `<tr><td><code>${k}</code><span class="muted">${what}</span></td><td class="num">${T[k].toFixed(2)}</td><td><code>${how}</code></td></tr>`).join("");
}

// ---- stars ----------------------------------------------------------------------------------------------------------
function updateStars() {
  for (const b of document.querySelectorAll(".key")) {
    b.setAttribute("aria-current", String(unit === "letter" && b.dataset.ch === cur));
    const s = best[starKey(`${mode}:${b.dataset.ch}`)];
    b.querySelector(".stars").textContent = s == null ? "" : "★".repeat(starsFor(s)) || "·";
  }
  for (const b of document.querySelectorAll(".phrase")) {
    b.setAttribute("aria-current", String(unit === "text" && b.dataset.text === text));
    const s = best[starKey(`${mode}:text:${b.dataset.text}`)];
    b.querySelector(".stars").textContent = s == null ? "" : "★".repeat(starsFor(s));
  }
  const total = [...STARRED].reduce((a, ch) => { const v = best[starKey(`${mode}:${ch}`)]; return a + (v != null ? starsFor(v) : 0); }, 0);
  $("star-total").textContent = `★ ${total} of ${3 * STARRED.length}`;
}

// ---- show me -----------------------------------------------------------------------------------------------------------
function stopAnim() { if (anim) { cancelAnimationFrame(anim); anim = null; } }
function watch() {
  stopAnim();
  const total = letters().flatMap(l => l.strokes).reduce((a, st) => a + strokeLength(st), 0);
  const ms = 900 + total * (unit === "text" ? 5 : 12), t0 = performance.now();
  const paint = p => (mode === "copy" ? drawModel(p) : draw(p));
  const step = now => {
    const p = Math.min(1, (now - t0) / ms);
    paint(p);
    if (p < 1) anim = requestAnimationFrame(step);
    else { anim = null; setTimeout(() => { if (!anim) { draw(); drawModel(); } }, 700); }
  };
  anim = requestAnimationFrame(step);
}

// ---- focus: the notebook alone, full screen where the browser allows it ------------------------------------------------
async function setFocus(on) {
  document.body.classList.toggle("focus", on);
  $("focus").setAttribute("aria-pressed", String(on));
  $("focus").textContent = on ? "Leave focus" : "Focus";
  $("lock").hidden = !on;
  if (!on && locked) setLock(false);
  try {
    if (on && !document.fullscreenElement) await document.documentElement.requestFullscreen?.();
    if (!on && document.fullscreenElement) await document.exitFullscreen?.();
  } catch { /* full screen is optional: the focus layout works without it */ }
  $("workspace").scrollIntoView({ block: "start" });
}
// lock (in focus): the page does not scroll, zoom or bounce, and only the pen writes, so a hand can rest on the screen
let locked = false;
function setLock(on) {
  locked = on;
  document.documentElement.classList.toggle("locked", on);
  $("lock").setAttribute("aria-pressed", String(on));
  $("lock").querySelector("span").textContent = on ? "Unlock" : "Lock";
  if (on) { penOnly = true; showPenOnly(); $("workspace").scrollIntoView({ block: "start" }); flash("Page locked: only the pen writes, and the page holds still. Unlock to scroll."); }
}
$("lock").onclick = () => setLock(!locked);
const hold = e => { if (locked) e.preventDefault(); };
document.addEventListener("touchmove", hold, { passive: false });              // no scrolling or bounce under the hand
document.addEventListener("touchstart", e => { if (locked && e.touches.length > 1) e.preventDefault(); }, { passive: false });  // no pinch
for (const g of ["gesturestart", "gesturechange"]) document.addEventListener(g, hold, { passive: false });     // Safari's pinch zoom
document.addEventListener("fullscreenchange", () => { if (!document.fullscreenElement && document.body.classList.contains("focus")) setFocus(false); });
$("focus").onclick = () => setFocus(!document.body.classList.contains("focus"));

// ---- controls -----------------------------------------------------------------------------------------------------------
function next() {
  if (unit === "letter") { chooseLetter(SEQ[(SEQ.indexOf(cur) + 1) % SEQ.length]); return; }
  if (pageNo < pages().length - 1) { pageNo++; pick = null; showPage(); $("workspace").scrollIntoView({ block: "start", behavior: "smooth" }); return; }
  const i = PHRASES.findIndex(p => p[1] === text);
  const t = PHRASES[(i + 1) % PHRASES.length][1];
  $("text-in").value = t; setText(t);
}
$("check").onclick = check;
$("watch").onclick = watch;
$("clear").onclick = () => { inkByPage[pageNo] = []; resultByPage[pageNo] = undefined; $("legend").hidden = true; $("mini-score").hidden = true; showPage(); if (unit === "text") showTextReport(); };
$("again").onclick = () => $("clear").click();
$("undo").onclick = () => { strokes().pop(); resultByPage[pageNo] = undefined; $("legend").hidden = true; $("mini-score").hidden = true; draw(); };
$("next").onclick = next;
document.addEventListener("keydown", e => {
  if (e.target.closest("input, textarea, button, a, select")) return;
  if (location.hash && location.hash !== "#practice") return;
  if (e.key === "Enter") { e.preventDefault(); check(); }
  else if ((e.key === "z" && (e.metaKey || e.ctrlKey)) || e.key === "Backspace") { e.preventDefault(); $("undo").click(); }
  else if (e.key === "ArrowRight") next();
  else if (e.key === "Escape" && document.body.classList.contains("focus")) setFocus(false);
});

// ---- the hand: the alphabet, the anatomy and the basic strokes, drawn from the model letters ----------------------------
function drawGuide() {
  if (!style) return;
  // the words about the hand (from its file), then its drawings
  const A = style.about;
  $("hand-intro").textContent = `${A.history} ${A.features}`;
  $("hand-facts").innerHTML = [["Tool", A.tool], ["Slant", A.slant], ["Proportions", A.proportions]]
    .map(([k, v]) => `<dt>${k}</dt><dd>${esc(v)}</dd>`).join("");
  $("strokes-title").textContent = style.id === "copperplate" ? "The basic strokes" : "Key letters";
  $("strokes-note").textContent = style.id === "copperplate" ? "Every letter is built from a handful of strokes. Practise them on their own and the letters follow."
    : `Learn these first: the other letters of ${style.name} are built from their strokes. The numbers show the order.`;
  if ($("anatomy").offsetParent === null) return;
  drawAnatomy(); drawStrokes(); drawSpecimen();
}
function drawSpecimen() {
  // the hand's whole alphabet on guidelines: rows of up to 13 letters, small letters, capitals, digits
  const cvs = $("specimen"), c = cvs.getContext("2d"), r = cvs.getBoundingClientRect(), dpr = devicePixelRatio || 1;
  const rowsTxt = [];
  for (const [name, chars] of GROUPS) {
    if (name.startsWith("Accent")) continue;
    const sorted = [...chars].sort((x, y) => x.localeCompare(y));
    for (let i = 0; i < sorted.length; i += 13) rowsTxt.push(sorted.slice(i, i + 13).join(""));
  }
  const lays = rowsTxt.map(t => layout(t.split("").join(" "), style, 1e6, { edge: 8 }));
  const wide = Math.max(...lays.map(l => Math.max(...l.items.map(i => i.xmax)))) + 8;
  const s = r.width / wide, h = rowsTxt.length * PITCH + 8;
  cvs.style.aspectRatio = `${wide} / ${h}`;
  cvs.width = Math.round(r.width * dpr); cvs.height = Math.round(h * s * dpr);
  c.setTransform(dpr, 0, 0, dpr, 0, 0);
  guides(c, s, wide, h, rowsTxt.length);
  lays.forEach((l, row) => {
    const M = sheetModel(l, style);
    l.items.forEach((it, k) => inkStrokes(c, s, M[k].map(st => st.map(([x, y, w]) => [x, y + row * PITCH, w])), css("--ink")));
  });
  cvs.onclick = e => {
    const b = cvs.getBoundingClientRect(), x = ((e.clientX - b.left) / b.width) * wide, y = ((e.clientY - b.top) / b.height) * h;
    const row = Math.min(rowsTxt.length - 1, Math.floor(y / PITCH));
    const it = lays[row].items.reduce((a, i) => (Math.abs((i.xmin + i.xmax) / 2 - x) < Math.abs((a.xmin + a.xmax) / 2 - x) ? i : a));
    chooseLetter(it.ch); location.hash = "#practice";
  };
}
function drawAnatomy() {
  // the hand's guidelines with three of its letters, the proportions between the lines and, if it leans, its slant
  const cvs = $("anatomy"), c = cvs.getContext("2d"), r = cvs.getBoundingClientRect(), dpr = devicePixelRatio || 1;
  cvs.width = Math.round(r.width * dpr); cvs.height = Math.round(r.height * dpr);
  const s = r.width / 288; c.setTransform(dpr, 0, 0, dpr, 0, 0);
  c.save(); c.translate(0, 8 * s); guides(c, s, 288, 104); c.restore();
  c.fillStyle = css("--paper"); c.fillRect(0, 0, 288 * s, 8 * s);
  const keys = [...(style.keys || (style.caps_only ? "AGM" : "hag"))].filter(ch => style.letters[ch]).slice(0, 3);
  keys.forEach((ch, i) => {
    c.save(); c.translate((16 + i * 72) * s, 8 * s); inkStrokes(c, s, style.letters[ch], css("--ink")); c.restore();
  });
  const G = style.guides, names = Object.keys(G);
  c.fillStyle = css("--muted"); c.font = `600 ${Math.max(9, 4.2 * s)}px ${css("--f-mono")}`; c.textAlign = "right"; c.textBaseline = "bottom";
  for (const n of names) c.fillText(n, 284 * s, (G[n] + 8 - 1) * s);
  // the spaces between the lines, in x-heights (or capital heights)
  const ys = names.map(n => G[n]).sort((a, b) => a - b);
  const unit = G["x-height"] != null ? G.baseline - G["x-height"] : G.baseline - (G["cap height"] ?? G.baseline - 20);
  c.strokeStyle = css("--accent"); c.fillStyle = css("--accent"); c.lineWidth = 1.2;
  c.font = `700 ${Math.max(9, 4.2 * s)}px ${css("--f-mono")}`; c.textAlign = "left"; c.textBaseline = "middle";
  for (let i = 1; i < ys.length; i++) {
    const [y0, y1] = [ys[i - 1], ys[i]], v = Math.round(((y1 - y0) / unit) * 100) / 100;
    c.beginPath(); c.moveTo(6 * s, (y0 + 9) * s); c.lineTo(4 * s, (y0 + 9) * s); c.lineTo(4 * s, (y1 + 7) * s); c.lineTo(6 * s, (y1 + 7) * s); c.stroke();
    c.fillText(String(v), 8 * s, ((y0 + y1) / 2 + 8) * s);
  }
  if (style.slant > 0.05) {
    const ang = 90 - style.slant_deg, bx = 238, by = G.baseline + 8, L = 22;
    c.beginPath(); c.moveTo(bx * s, by * s); c.lineTo((bx + L) * s, by * s); c.stroke();
    c.beginPath(); c.moveTo(bx * s, by * s); c.lineTo((bx + L * Math.cos(ang * Math.PI / 180)) * s, (by - L * Math.sin(ang * Math.PI / 180)) * s); c.stroke();
    c.beginPath(); c.arc(bx * s, by * s, 9 * s, -ang * Math.PI / 180, 0); c.stroke();
    c.fillText(`${Math.round(ang)}°`, (bx + 11) * s, (by - 5) * s);
  }
  $("anatomy-note").textContent = `Guidelines from the top: ${names.join(", ")}. The numbers are the spaces between them, in ${G["x-height"] != null ? "x-heights" : "capital heights"}${style.slant > 0.05 ? `; slant ${Math.round(90 - style.slant_deg)}° from the horizontal` : "; upright"}.`;
}
const BASIC = [
  ["Entrance hairline", "rises from the left into the top of a stroke", "i", 0, [0, 0.18]],
  ["Shaded stem", "straight down the slant with full pressure", "i", 0, [0.18, 0.62]],
  ["Underturn", "shade into a hairline: down, round the bottom, up (u)", "u", 1, [0.25, 1]],
  ["Overturn", "a hairline up and over into a shade (n, m)", "n", 1, [0, 1]],
  ["Oval", "counter-clockwise; shaded down the left side (o, a, d, g)", "o", 0, [0, 0.92]],
  ["Ascending loop", "hairline up to the ascender line, shade back down (b, h, k, l)", "l", 0, [0, 0.75]],
  ["Descending loop", "shade down to the descender line, hairline back up (g, j, y)", "j", 0, [0.2, 1]],
  ["Capital stem", "a long shade curling left on the baseline (B, D, P, R)", "P", 0, [0.1, 1]],
];
function slice(st, a, b) {
  const L = strokeLength(st), out = [];
  let at = 0;
  for (let k = 0; k < st.length; k++) {
    if (k) at += Math.hypot(st[k][0] - st[k - 1][0], st[k][1] - st[k - 1][1]);
    if (at >= a * L && at <= b * L) out.push(st[k]);
  }
  return out;
}
function drawStrokes() {
  // copperplate: its basic strokes, cut from the model letters; the other hands: their key letters, whole
  const cards = style.id === "copperplate"
    ? BASIC.map(([name, what, ch, si, [a, b]]) => ({ name, what, strokes: [slice(style.letters[ch][si], a, b)] }))
    : [...(style.keys || "")].filter(ch => style.letters[ch]).map(ch => ({ name: ch, what: `${style.letters[ch].length} stroke${style.letters[ch].length > 1 ? "s" : ""}`, strokes: style.letters[ch], whole: true }));
  const box = $("strokes");
  box.innerHTML = "";
  for (const card of cards) {
    const d = document.createElement("figure"); d.className = "stroke-card" + (card.whole ? " whole" : "");
    d.innerHTML = `<canvas></canvas><figcaption><b>${esc(card.name)}</b><span>${esc(card.what)}</span></figcaption>`;
    box.appendChild(d);
    const cvs = d.querySelector("canvas"), c = cvs.getContext("2d"), r = cvs.getBoundingClientRect(), dpr = devicePixelRatio || 1;
    cvs.width = Math.round(r.width * dpr); cvs.height = Math.round(r.height * dpr);
    const pts = card.strokes.flat(), xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    const cx = (Math.min(...xs) + Math.max(...xs)) / 2, cy = (Math.min(...ys) + Math.max(...ys)) / 2;
    const span = Math.max(Math.max(...xs) - Math.min(...xs) + 14, (Math.max(...ys) - Math.min(...ys) + 14) * 1.5, 30);
    const s = r.width / span;
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    c.save(); c.translate((span / 2 - cx) * s, (span / 3 - cy) * s); guides(c, s, 200, H); c.restore();
    c.save(); c.translate((span / 2 - cx) * s, (span / 3 - cy) * s);
    inkStrokes(c, s, card.strokes, css("--ink")); startMarks(c, s, card.strokes);
    c.restore();
  }
}
new ResizeObserver(() => drawGuide()).observe($("anatomy"));

route();
load();
