# AGENTS.md

Guidance for AI agents (and people) improving WP-Ductus. Read `README.md` for what it is and `LOG.md` for how the
weights were written; this file is about how to work on it.

## What this project is

A calligraphy teacher: a small Siamese network that compares a written attempt with an authored model letter and
marks shape, ductus (stroke direction and order), shading and, in the copy game, form (slant and size). Two games:
trace the dots (2 px band) and copy by eye (attempt fitted onto the model: place, size, slant; 4 px band), each with one letter
or lines of text (`web/lines.js` lays the text out and cuts the writing into letters; each letter is marked alone). Its weights are **written by hand**: the generator
(`gen/generate.py`) emits a plain-text edit list (`weights/ductus.edits`); the engine (`ductus/engine.py`, mirrored in
`web/ductus.js`) starts every parameter at zero and applies it. Model letters are pen strokes authored in
`gen/copperplate.py` and `gen/hands/`. Sister project of WP-CharNet, same method.

## House rules

1. **No training, ever.** No gradient descent, no fitting, no automatic search over weights or thresholds. Type
   values by hand, each with a reason. A sweep of a constant is allowed only as a few hand-picked settings, each
   logged.
2. **Every value has a reason.** Every `BIAS` line carries its reason after `#` (a test checks this). If you change
   the terms of a neuron, rewrite its reason.
3. **A perfect copy scores 100.** Every model letter, copied exactly, must score 100 in every mark with no fault
   above zero. If a new letter or a new neuron breaks this, fix the cause, do not lower the bar.
4. **Damage lowers the right mark.** Each distortion in `eval/ladder.py` must lower the quality it damages and the
   tip must name it. Add a ladder step when you add a kind of fault.
5. **Model letters are authored strokes,** in writing order, with the pen's direction. Never trace or import a font
   (fonts have no stroke order or direction) and never copy an exemplar sheet point by point.
6. **Shading comes from the rule, not by hand.** For pointed-pen hands, width follows the direction of travel
   (`_width`); for broad-nib hands, the nib angle (`Hand.width`). Do not paint thickness per letter.
7. **Log everything** in `LOG.md`: what you changed, the numbers before and after, and what did not work.
8. **One set of weights.** No version names in files or docs; the repository holds the current network only.
9. **Keep the browser engine identical.** If you change `ductus/engine.py` or `ductus/render.py`, change
   `web/ductus.js` the same way; `tests/test_parity.py` must pass.
10. **Privacy.** No personal names, emails or local paths in files or commits.
11. **No assistant-specific files.** This file is the shared guide; do not add `CLAUDE.md` or other agent files
    (they are in `.gitignore`).

## How the network is built (short)

| Layer | Op | What it makes |
|---|---|---|
| E1 | 1 × 1 conv | `on` (solid ink), `shade` (pen wider than 2.25 px), for model and attempt with the same weights |
| E2 | 1 × 1 conv | `m_hair` (model ink not shaded), `m_tinv` (1 − time on model ink) |
| B1, B2 | max 3 × 3 | `*_b`: ink, shade, time widened into the tolerance band (1 + `widen` px: 2 tracing, 4 copying); `m_*_n`: direction and shade widened 1 px |
| C1 | 1 × 1 conv | comparison maps: `on_track`, `off_track`, `covered`, `missed`, `same_*`, `opp_*`, `shade_hit`, `shade_miss`, `hair_cov`, `hair_thick` |
| C2 | 1 × 1 conv | `late`, `early`: written a quarter of the letter or more after / before the model nearby |
| Z | zone | pixel counts over the canvas |
| R | ratio (fixed) | `stay`, `cover`, `direction`, `order_slip`, `shade_hit`, `hair_slip` |
| Q, O | linear | marks `shape`, `ductus`, `shading`; `overall_pressure`, `overall_no_pressure` |
| Z2, R2, R3, S | zone, moments (fixed), ratio, linear | copy game: sums over `a_form` / `m_form` (the thin-pen paths before the fit, where they lie within 3 px of each other once fitted); slope of x on y and variance of y; `lean_gap`, `size2` |
| F | linear | faults in score points: `f_off`, `f_miss`, `f_back`, `f_order`, `f_thin`, `f_thick`; copy game `f_upright`, `f_slanted`, `f_big`, `f_small`, silenced by 2 × (1 − cover) (the tip is the largest) |
| Q2, O2 | linear | `form` (copy game); `overall_copy_pressure`, `overall_copy_no_pressure` |

AND of two maps is `clip(a + b − 1)`; AND-NOT is `clip(a − b)`. Everything is in [0, 1] except counts.

## Decisions to keep (and why)

- **Direction and shade compared within 1 px, ink within 2 px.** Wider, a stem's neighbour leaks in and perfect
  copies lose points (`LOG.md`, decisions 1 and 3).
- **Opposite direction only where the model moves only the other way** (`opp_d = a_d AND m_opp AND NOT m_d`): at
  turns and retraced strokes the model moves both ways.
- **Two time maps** (latest and earliest model time nearby): needed at crossings.
- **Copy game: fit, then mark precision; form apart.** Your letter is fitted onto the model (place, size, slant) so
  shape and ductus mark the strokes themselves; slant and size are marked only in form, from the paths before the fit
  (`LOG.md`, decision 12). The fit matches both ways and trims both ways; keep `ductus/render.py` and `web/ductus.js`
  identical (same sums in the same order: the parity test checks the result to 1e-9).
- **Accents are authored strokes after the letter** (`ACCENTS`, `ANCHOR` in `gen/copperplate.py`), only on letters
  without ascenders; the order test skips one-stroke letters with an accent (the accent's place in the order counts
  for little).
- **Lines: cut first, then mark single letters.** The network never sees a whole line; `web/lines.js` decides which
  ink is which letter's. Copy-game boundaries come from dynamic time warping of the ink profile (`LOG.md`, decision
  10); the "thinnest ink" rule does not work for copperplate.
- **Shading is not marked without pressure,** and the overall falls back to 60 / 40. A mouse or a finger cannot
  shade, so marking it would be unfair.

## The page

`web/index.html` holds the markup and style; `web/app.js` the page. Four views on the URL hash (`#practice`,
`#hand`, `#network`, `#made`). A single letter is a one-page notebook, so letters and text share one path: layout
(`lines.js`), pages, ink per page, `check()` per page, `report.js` over all checked pages, `pdf.js` for templates.
Keep a checked letter slim (numbers and byte maps, `slim()` in `app.js`); never store the network's full output.
Explanations belong in the other views, not on Practice.

## How to add a letter

1. Write it in the hand's `letters()` (`gen/hands/<hand>.py`; copperplate: `_letters()` in `gen/copperplate.py`) from
   the hand's basic strokes, in the exemplar's stroke order and direction, in the upright frame. Strokes that change
   direction sharply should be separate pieces joined with `chain`.
2. `python eval/compare.py out.png <hand> <ch> <exemplar> <crop box> <exemplar x-height px>` and look at it under the
   exemplar. Fix the shape until it reads as the exemplar's letter.
3. `python gen/generate.py` (exports it to the demo), then `HAND=<hand> pytest -q tests/test_styles.py`
   (copperplate: `python eval/ladder.py <ch>` and `pytest -q tests/test_ductus.py`), then `pytest -q tests`.
4. If the perfect copy is below 100, find which measure is below 1 and why (usually overlapping strokes or a hairline
   squeezed between two stems), and fix the letter or the neuron, then log it.
5. Nothing else: the page's palette shows every letter the hand exports.

## How to add a style

Add a module to `gen/hands/` with `letters()` (`{char: [stroke, ...]}` in the upright frame: x-heights, or capital
heights for a unicase hand) and `HAND` (id, name, family, variant, pen: `pointed`, `broad` with its nib angle and
width, or `mono`; x-height in pixels, baseline, slant, extenders, capital height, `unicase`, description `about`,
first letters, sample word, key letters). Add its id to `ORDER` in `gen/styles.py` (a variant goes after its family's
main hand, with the same `family`). Author the hand's **own** letterforms from its exemplars and manuals, in the taught
stroke order; never derive a hand from another hand's letters, never trace. **Measure the exemplar first** (x-height,
extenders and capital height; stem thickness, so the x-height in nib widths; slant; nib angle; widths of n, o, m, H, O)
and set the hand's parameters from it. Every hand has a–z, A–Z, 0–9; accents are added by `gen/styles.py`. Then compare
each row of the sheet with `eval/compare.py out.png <id> <letters> <exemplar> <crop box> <exemplar x-height px>` (the
exemplar above your letters at the same x-height, drawn as the page draws them) and fix every letter until it reads as
the exemplar's; run `HAND=<id> pytest -q tests/test_styles.py`, then `gen/generate.py`. The network does not change: it
compares any two sets of strokes. Fonts (.ttf) are not a source: they have no stroke order and are a typographer's
reading of the hand, not the hand.

## Commands

```bash
.venv/bin/python gen/generate.py          # network + web/model/
.venv/bin/python -m pytest -q tests       # all checks (parity and lines need node)
node tests/lines.mjs                      # lines of text: the per-case report
.venv/bin/python eval/ladder.py [chars]   # distortion table
.venv/bin/python eval/sheet.py out.png [chars] [hand]   # the network's ink
.venv/bin/python eval/compare.py out.png <hand> <chars> [exemplar box x-height]   # as the page draws, beside an exemplar
cd web && python3 -m http.server          # demo
```

## Next steps

1. **Copy-game ductus that follows the stroke, not the pixel:** compare direction only where your stroke and the
   model's are at the same point of the letter in time, so a copy whose strokes cross the model's other strokes is
   not marked backwards there.
2. **Punctuation** (. , ; : ' ! ?) in every hand, and accented capitals for the hands whose capitals fill the page
   (copperplate at 2.5 x-heights, the large broad-nib hands): an accent drawn lower or a page with more room above.
3. **Joins:** authored joining strokes (after o, v, w and b the join leaves from the x-height, not the baseline), and
   marks for a line as a whole: spacing, even slant, a straight baseline.
4. **Truer pens and more variants:** a nib angle that can change within a letter (Roman N, M, Z; Rustica's 70° stems
   and 45° curves; Uncial N), strokes made with the nib's corner (the thin verticals of the Textura and Bâtarde
   capitals: a stroke flag drawn at `hair` whatever its direction, with the attempt's stroke matched to it), a pen
   that is turned in Neuland (thin bowl tops, heavy stems), Spencerian's single shade per capital; and more variants
   (Half-Uncial, Carolingian, flourished Spencerian capitals). Bâtarde's and Rotunda's sheets are low-resolution:
   their capitals would gain from a better exemplar.
5. **Speed:** an even pace on downstrokes is part of good ductus. The renderer's time is position along the letter;
   pace would need the pen's timestamps as a new input map.

## Definition of done for a change

Perfect copies 100 on every character, `pytest -q tests` green (including parity), `LOG.md` updated, the demo checked
in a browser (light and dark, phone width), no version names.
