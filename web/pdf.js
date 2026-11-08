// Practice templates as PDF: the text on copperplate guidelines, A4, ready to print. A tracing sheet (the model in
// dots, as on the screen) or a copybook (a model row in ink, then an empty row to copy it into). The PDF is written
// here by hand (lines, dots and text in the 14 standard fonts), so no library is needed.
import { layout, sheetModel, PITCH } from "./lines.js";

// ---- a minimal PDF writer -------------------------------------------------------------------------------------------
const A4 = [595.28, 841.89];
const num = v => (Math.abs(v) < 1e-4 ? "0" : v.toFixed(2).replace(/\.?0+$/, ""));
// text in WinAnsi: Latin-1 characters as octal escapes, anything else as "?"
const pdfString = s => "(" + [...s].map(ch => {
  const c = ch.codePointAt(0);
  if (ch === "\\" || ch === "(" || ch === ")") return "\\" + ch;
  if (c >= 32 && c < 127) return ch;
  if (c >= 160 && c < 256) return "\\" + c.toString(8).padStart(3, "0");
  return "?";
}).join("") + ")";

class Page {
  constructor(h) { this.h = h; this.ops = ["1 J 1 j"]; }   // round caps and joins: strokes look like ink
  color(r, g, b) { this.ops.push(`${num(r)} ${num(g)} ${num(b)} RG ${num(r)} ${num(g)} ${num(b)} rg`); return this; }
  width(w) { this.ops.push(`${num(w)} w`); return this; }
  line(x0, y0, x1, y1) { this.ops.push(`${num(x0)} ${num(this.h - y0)} m ${num(x1)} ${num(this.h - y1)} l S`); return this; }
  dot(x, y, d) { this.width(d); return this.line(x, y, x, y); }        // a round cap on a zero-length line
  // a filled polygon (a broad nib's sweep)
  poly(pts) { this.ops.push(pts.map(([x, y], i) => `${num(x)} ${num(this.h - y)} ${i ? "l" : "m"}`).join(" ") + " h f"); return this; }
  text(x, y, size, s, font = "F1") { this.ops.push(`BT /${font} ${num(size)} Tf ${num(x)} ${num(this.h - y)} Td ${pdfString(s)} Tj ET`); return this; }
}

export class Pdf {
  constructor() { this.pages = []; }
  page() { const p = new Page(A4[1]); this.pages.push(p); return p; }
  blob() {
    const objs = [];                                   // object bodies, numbered from 1
    const add = body => { objs.push(body); return objs.length; };
    const catalog = add(""), pages = add("");
    const f1 = add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>");
    const f2 = add("<< /Type /Font /Subtype /Type1 /BaseFont /Times-Italic /Encoding /WinAnsiEncoding >>");
    const kids = this.pages.map(p => {
      const stream = p.ops.join("\n");
      const content = add(`<< /Length ${stream.length} >>\nstream\n${stream}\nendstream`);
      return add(`<< /Type /Page /Parent ${pages} 0 R /MediaBox [0 0 ${A4[0]} ${A4[1]}] ` +
        `/Resources << /Font << /F1 ${f1} 0 R /F2 ${f2} 0 R >> >> /Contents ${content} 0 R >>`);
    });
    objs[catalog - 1] = `<< /Type /Catalog /Pages ${pages} 0 R >>`;
    objs[pages - 1] = `<< /Type /Pages /Kids [${kids.map(k => `${k} 0 R`).join(" ")}] /Count ${kids.length} >>`;
    let out = "%PDF-1.4\n", offsets = [];
    objs.forEach((body, i) => { offsets.push(out.length); out += `${i + 1} 0 obj\n${body}\nendobj\n`; });
    const xref = out.length;
    out += `xref\n0 ${objs.length + 1}\n0000000000 65535 f \n` + offsets.map(o => `${String(o).padStart(10, "0")} 00000 n \n`).join("");
    out += `trailer\n<< /Size ${objs.length + 1} /Root ${catalog} 0 R >>\nstartxref\n${xref}\n%%EOF\n`;
    return new Blob([out], { type: "application/pdf" });     // ASCII only, so string length = byte length
  }
}

// ---- drawing helpers shared with the page ---------------------------------------------------------------------------
// points every `gap` px along a stroke, with the pen width there and the distance travelled
// a broad nib held at the hand's angle: each piece of a stroke is the quadrilateral the nib's edge sweeps, so thick
// and thin come from the direction, as with a real broad pen (pts: canvas points; returns polygons in canvas units)
export function nibSweep(st, hand) {
  const a = (hand.nib_angle * Math.PI) / 180, h = hand.nib / 2, nx = Math.cos(a) * h, ny = -Math.sin(a) * h;
  if (st.length === 1) {
    const [x, y] = st[0], px = -ny * 0.9, py = nx * 0.9;       // a dot: the nib pressed and turned a little
    return [[[x - nx - px, y - ny - py], [x + nx - px, y + ny - py], [x + nx + px, y + ny + py], [x - nx + px, y - ny + py]]];
  }
  const out = [];
  for (let k = 1; k < st.length; k++) {
    const [x0, y0] = st[k - 1], [x1, y1] = st[k];
    out.push([[x0 - nx, y0 - ny], [x0 + nx, y0 + ny], [x1 + nx, y1 + ny], [x1 - nx, y1 - ny]]);
  }
  return out;
}

// a square pen end (Neuland): each piece of the stroke is the shape a square sweeps from one point to the next
export function squareSweep(st, side) {
  const h = side / 2, sq = (x, y) => [[x - h, y - h], [x + h, y - h], [x + h, y + h], [x - h, y + h]];
  if (st.length === 1) return [sq(st[0][0], st[0][1])];
  const out = [];
  for (let k = 1; k < st.length; k++) out.push(hull([...sq(st[k - 1][0], st[k - 1][1]), ...sq(st[k][0], st[k][1])]));
  return out;
}
function hull(P) {
  P = P.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const half = Q => { const o = []; for (const p of Q) { while (o.length > 1 && (o[o.length - 1][0] - o[o.length - 2][0]) * (p[1] - o[o.length - 2][1]) - (o[o.length - 1][1] - o[o.length - 2][1]) * (p[0] - o[o.length - 2][0]) <= 0) o.pop(); o.push(p); } return o; };
  const lo = half(P), hi = half(P.slice().reverse());
  return lo.slice(0, -1).concat(hi.slice(0, -1));
}

export function dotsAlong(st, gap) {
  if (st.length === 1) return [{ x: st[0][0], y: st[0][1], w: st[0][2], at: 0 }];
  const out = [{ x: st[0][0], y: st[0][1], w: st[0][2], at: 0 }];
  let since = 0, at = 0;
  for (let k = 1; k < st.length; k++) {
    const [x0, y0, w0] = st[k - 1], [x1, y1, w1] = st[k];
    const seg = Math.hypot(x1 - x0, y1 - y0);
    let d = gap - since;
    while (d <= seg) {
      const f = d / seg;
      out.push({ x: x0 + f * (x1 - x0), y: y0 + f * (y1 - y0), w: w0 + f * (w1 - w0), at: at + d });
      d += gap;
    }
    since = seg - (d - gap);
    at += seg;
  }
  return out;
}

// ---- the template ---------------------------------------------------------------------------------------------------
const MARGIN = { left: 40, right: 40, top: 64, bottom: 44 };
const ROW_WIDTH = 440;                 // canvas pixels per row: an x-height of 20 px becomes about 8 mm on paper
const EDGE = 12;                       // the margin line's room, as on the screen
// on paper the template is something to write over: light dots and ruling, so your ink stands out against them
const INK = [0.12, 0.1, 0.18], DOTS = [0.73, 0.7, 0.65], GUIDE = [0.83, 0.87, 0.94], SLANT = [0.89, 0.91, 0.96], STRONG = [0.62, 0.7, 0.86];
const DOT_GAP = 2.8, DOT_SIZE = 0.7;    // dots a little further apart and 0.7 of the screen's size (0.55 lost the hairlines)
const RED = [0.84, 0.42, 0.42], MUTED = [0.4, 0.38, 0.45];

// kind: "trace" (dotted model letters to write over) or "copy" (a row in ink, then an empty row under it)
export function templatePdf(text, st, kind, title = "") {
  const k = (A4[0] - MARGIN.left - MARGIN.right) / ROW_WIDTH;      // points per canvas pixel
  const lay = layout(text, st, ROW_WIDTH, { edge: EDGE });
  const M = sheetModel(lay, st);
  const usable = A4[1] - MARGIN.top - MARGIN.bottom;
  const slots = Math.max(2, Math.floor((usable / k - 8) / PITCH));  // guideline rows that fit on a page
  const perPage = kind === "copy" ? Math.floor(slots / 2) : slots;  // a copybook row takes two: model and yours
  const pdf = new Pdf(), pages = Math.max(1, Math.ceil(lay.rows / perPage));
  const X = x => MARGIN.left + x * k, Y = y => MARGIN.top + y * k;

  for (let p = 0; p < pages; p++) {
    const pg = pdf.page();
    pg.color(...INK).text(MARGIN.left, 40, 15, "WP-Ductus", "F2");
    pg.color(...MUTED).text(MARGIN.left + 78, 40, 9, `${st.name ?? "Copperplate"} ${kind === "copy" ? "copybook" : "tracing sheet"}${title ? " · " + title : ""}`);
    pg.text(A4[0] - MARGIN.right - 60, 40, 9, `Page ${p + 1} of ${pages}`);
    const r0 = p * perPage, rows = Math.min(perPage, lay.rows - r0);
    const used = kind === "copy" ? 2 * rows : rows;
    const h = used * PITCH + 8;
    // the sheet: slant lines, the four guidelines per row, the margin line
    pg.color(...SLANT).width(0.35);
    for (let x0 = -h * st.slant - 10; st.slant > 0.05 && x0 < ROW_WIDTH + 10; x0 += 12) {
      // clip each slant line to the sheet's left and right edges
      let xa = x0, ya = h, xb = x0 + h * st.slant, yb = 0;
      if (xa < 0) { ya = h - (0 - xa) / st.slant; xa = 0; }
      if (xb > ROW_WIDTH) { yb = (xb - ROW_WIDTH) / st.slant; xb = ROW_WIDTH; }
      if (xa < xb) pg.line(X(xa), Y(ya), X(xb), Y(yb));
    }
    for (let r = 0; r < used; r++) for (const [name, y] of Object.entries(st.guides)) {
      const strong = name === "baseline" || name === "x-height" || name === "cap height";
      pg.color(...(strong ? STRONG : GUIDE)).width(name === "baseline" ? 0.9 : 0.5);
      pg.line(X(0), Y(y + r * PITCH), X(ROW_WIDTH), Y(y + r * PITCH));
    }
    pg.color(...RED).width(0.6).line(X(EDGE - 5), Y(0), X(EDGE - 5), Y(h));
    // the letters of this page's rows
    lay.items.forEach((it, i) => {
      if (it.row < r0 || it.row >= r0 + rows) return;
      const row = it.row - r0, dy = (kind === "copy" ? 2 * row : row) * PITCH - it.oy;
      for (const s of M[i]) {
        if (kind === "trace") {
          pg.color(...DOTS);
          for (const d of dotsAlong(s, DOT_GAP)) pg.dot(X(d.x), Y(d.y + dy), DOT_SIZE * 2 * Math.max(0.6, d.w * 0.42) * k);
        } else if (st.pen === "broad") {
          pg.color(...INK);
          for (const q of nibSweep(s, st)) pg.poly(q.map(([x, y]) => [X(x), Y(y + dy)]));
          pg.width(st.hair * k);                                  // the nib's edge leaves a hairline where it moves sideways
          for (let j = 1; j < s.length; j++) pg.line(X(s[j - 1][0]), Y(s[j - 1][1] + dy), X(s[j][0]), Y(s[j][1] + dy));
        } else if (st.square) {
          pg.color(...INK);
          for (const q of squareSweep(s, st.mono)) pg.poly(q.map(([x, y]) => [X(x), Y(y + dy)]));
        } else {
          pg.color(...INK);
          if (s.length === 1) { pg.dot(X(s[0][0]), Y(s[0][1] + dy), s[0][2] * k); continue; }
          for (let j = 1; j < s.length; j++) {
            pg.width(((s[j - 1][2] + s[j][2]) / 2) * k);
            pg.line(X(s[j - 1][0]), Y(s[j - 1][1] + dy), X(s[j][0]), Y(s[j][1] + dy));
          }
        }
      }
    });
    pg.color(...MUTED).text(MARGIN.left, A4[1] - 24, 7.5,
      kind === "copy" ? `Copy each row into the empty row under it. ${st.about?.slant ?? ""} ${st.about?.proportions ?? ""}`.trim()
        : st.pen === "pointed" ? "Write over the dots, pressing on the downstrokes (bigger dots) and easing off on the hairlines."
        : `Write over the dots. ${st.about?.tool ?? ""}`.trim());
  }
  return pdf.blob();
}
