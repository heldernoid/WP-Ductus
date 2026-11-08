// The report for a long text: what the per-letter marks of the network add up to. Fixed rules, typed by hand like
// the rest (no weights are learned here): means, counts and spreads over the letters you wrote, and which faults cost
// the most points. Pure functions, so tests/report.mjs can run them in node.

// the faults the network's F layer names, in score points (0 to 1 each), with how the report names them
export const FAULTS = {
  f_off: { name: "Off the path", what: "ink outside the model's path" },
  f_miss: { name: "Missed parts", what: "parts of the letter not written" },
  f_back: { name: "Wrong direction", what: "strokes written the wrong way" },
  f_order: { name: "Stroke order", what: "strokes in the wrong order" },
  f_thin: { name: "Shades too light", what: "downstrokes without pressure" },
  f_thick: { name: "Hairlines too heavy", what: "upstrokes with pressure" },
  f_upright: { name: "Too upright", what: "steeper than the hand's slant" },
  f_slanted: { name: "Leaning too far", what: "flatter than the hand's slant" },
  f_big: { name: "Too big", what: "taller than the model" },
  f_small: { name: "Too small", what: "shorter than the model" },
};

// a sentence of advice per fault, for the whole text
export const ADVICE = {
  f_off: "Slow down on the curves: most of the lost points are ink outside the path.",
  f_miss: "Finish every stroke, hairlines included: parts of letters are missing.",
  f_back: "Start each stroke at its number and follow the arrow: some strokes ran the wrong way.",
  f_order: "Write the strokes of each letter in their order: 1, then 2.",
  f_thin: "Press on the downstrokes so they swell; lift the pressure before the turn.",
  f_thick: "Keep the upstrokes light: a hairline wants almost no pressure.",
  f_upright: "Lean more: keep every downstroke parallel to the slanted guidelines ({lean}).",
  f_slanted: "Lean less: your downstrokes lie flatter than the {lean} guidelines.",
  f_big: "Write smaller: the body of a small letter fills only the band between baseline and x-height line.",
  f_small: "Write larger: fill the band from the baseline up to the x-height line.",
};

export const starsFor = s => (s >= 90 ? 3 : s >= 75 ? 2 : s >= 55 ? 1 : 0);

const FORM = ["f_upright", "f_slanted", "f_big", "f_small"];   // the copy game's form faults: not marked when tracing
const mean = a => (a.length ? a.reduce((x, y) => x + y, 0) / a.length : 0);
const spread = a => { const m = mean(a); return a.length > 1 ? Math.sqrt(mean(a.map(v => (v - m) ** 2))) : 0; };
// a downstroke's angle from the horizontal, from the slope of x on y (x per pixel down: copperplate's is about -0.7)
const degrees = k => (Math.atan2(1, -k) * 180) / Math.PI;

// letters: [{ ch, word, overall (0-100), T (the network's outputs, or null when nothing was written there) }]
// words: the text of each word, by its index. Returns the summary the page shows.
// slant: the hand's slant in degrees from the horizontal (90 for an upright hand), for the advice on leaning
export function summarize(letters, words, { copy = false, pressure = false, slant = 55 } = {}) {
  const done = letters.filter(l => l.T);
  const out = { n: letters.length, written: done.length };
  out.overall = Math.round(mean(letters.map(l => l.overall)));
  out.marks = {};
  for (const k of ["shape", "ductus", "shading", "form"]) out.marks[k] = Math.round(100 * mean(letters.map(l => (l.T ? l.T[k] : 0))));
  if (!pressure) delete out.marks.shading;
  if (!copy) delete out.marks.form;

  // each word: the mean of its letters
  const byWord = new Map();
  for (const l of letters) { if (!byWord.has(l.word)) byWord.set(l.word, []); byWord.get(l.word).push(l.overall); }
  out.words = [...byWord.entries()].sort((a, b) => a[0] - b[0]).map(([w, s]) => ({ text: words[w] ?? "", score: Math.round(mean(s)) }));

  // each character you wrote more than once or poorly: its mean, how often, and its costliest fault
  const byChar = new Map();
  for (const l of letters) { if (!byChar.has(l.ch)) byChar.set(l.ch, []); byChar.get(l.ch).push(l); }
  out.chars = [...byChar.entries()].map(([ch, ls]) => {
    const fs = Object.keys(FAULTS).map(f => [f, mean(ls.map(l => (l.T ? l.T[f] : f === "f_miss" ? 1 : 0)))]).sort((a, b) => b[1] - a[1]);
    return { ch, n: ls.length, score: Math.round(mean(ls.map(l => l.overall))), fault: fs[0][1] > 0.03 ? fs[0][0] : null };
  }).sort((a, b) => a.score - b.score || b.n - a.n);
  out.weakest = out.chars.filter(c => c.score < 90).slice(0, 6);

  // points lost to each fault, per letter on average (a letter left out counts as all missed)
  out.faults = Object.keys(FAULTS).map(f => {
    const pts = letters.map(l => (l.T ? l.T[f] : f === "f_miss" ? 1 : 0));
    const worst = [...byChar.entries()]
      .map(([ch, ls]) => [ch, mean(ls.map(l => (l.T ? l.T[f] : f === "f_miss" ? 1 : 0)))])
      .filter(([, v]) => v > 0.05).sort((a, b) => b[1] - a[1]).slice(0, 4).map(([ch]) => ch);
    return { f, points: 100 * mean(pts), letters: pts.filter(v => v > 0.05).length, worst };
  }).filter(x => x.points >= 0.5 && (copy || !FORM.includes(x.f))).sort((a, b) => b.points - a.points);
  const lean = slant >= 89.5 ? "upright" : `${Math.round(slant)}°`;
  const advice = f => (slant >= 89.5 && f === "f_slanted" ? "Stand up straight: this hand is upright, and your downstrokes lean."
    : ADVICE[f].replace("{lean}", lean));
  out.advice = out.faults.slice(0, 3).map(x => ({ ...x, text: advice(x.f) }));

  // copy game: how steady your slant and size are across the text (letters with a slant of their own: path height)
  if (copy) {
    const formed = done.filter(l => l.T.m_vy > 4 && l.T.a_vy > 4);
    if (formed.length >= 3) {
      const you = formed.map(l => degrees(l.T.a_slope)), model = formed.map(l => degrees(l.T.m_slope));
      const gap = you.map((v, i) => v - model[i]);
      const size = formed.map(l => Math.sqrt(Math.max(0, l.T.size2)));
      out.slant = { you: mean(you), model: mean(model), spread: spread(gap) };
      out.size = { ratio: mean(size), spread: spread(size) };
    }
  }
  return out;
}
