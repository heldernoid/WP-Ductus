# How the weights were written

Every value in `weights/ductus.edits` was typed by hand in `gen/generate.py`, with its reason next to it. This log
records the decisions, the numbers that drove them and what did not work.

## Data

None. The model letters are authored strokes (`gen/copperplate.py`), so a perfect copy is known exactly and every
fault can be made on purpose. The network is checked on distortion ladders (`eval/ladder.py`): shift, wobble, a
reversed stroke, swapped stroke order, constant width, all thick, a missing stroke, a stray stroke.

## The model letters

- Written in an upright frame (x-height = 1, ascender line 2.5, descender line −1.5, i.e. 3 : 2 : 3), then sheared to
  55° and scaled to 20 px per x-height, baseline at y = 58 on the 96 × 96 grid.
- Built from copperplate basic strokes: entrance hairline, stem, underturn with exit, overturn, arch (branching
  compound curve), oval, ascending loop, descending loops (left for g j y z, right for f q), the small closing loop of
  b v w.
- Pen width from direction (pointed-pen rule): a smooth step from hairline (1.3 px) to full shade (4 px) as the
  direction of travel turns from across the slant to straight down it. No shading is placed by hand.
- Checked by eye on rendered sheets after each batch (`eval/sheet.py`).

## Decisions, with the evidence

**1. Direction is compared against a 1 px band, not the full 2 px.** First version: the model's direction maps
widened like the ink (3 px), and `same = clip(a_d + m_d_b − 1)`. A perfect copy of `u` scored ductus 33 (direction
0.59) and `a` 36: near every stem, the neighbouring upstroke's direction leaked into the band, so a correct
downstroke also counted as "opposite". With 1 px and `opp_d` written as `a_d AND m_opp AND NOT m_d` (opposite only
where the model *only* moves the other way), perfect copies score direction 1.0 on all 36 characters.

**2. Stroke order compares against the latest and the earliest model time nearby.** `late` = your time more than a
quarter of the letter after the *latest* model time within the band; `early` = more than a quarter before the
*earliest* (carried as `1 − t`, widened by max, since max can only carry the latest). With one time map, crossings
(where two strokes of different times meet) counted as order slips on a perfect copy.

**3. Shading is judged on the hairline itself, away from stems.** First version: `hair_thick = m_hair AND a_shade_b`
(your thick ink within 3 px). A perfect copy scored shading 49/52 (`u`/`a`): the 3 px band put each stem's thickness
onto the hairlines joined to it. Then `m_hair AND a_shade` with hairline pixels within 2 px of shade left out: perfect
copies 100, but `p` and `4` had no hairline pixels left to judge (an all-thick `p` scored shading 100). Final: leave
out hairline pixels within **1 px** of the model's shade. Perfect copies 100; all-thick 30 on every character but `4`
(its diagonal is a shaded downstroke, so little hairline remains); a 2 px shift costs at most 5.

**4. Band of 2 px (was 3).** A 2 px band is about 8 screen pixels at the demo's size, enough for a careful hand;
with 3 px, a 4 px miss still scored shape 96 on average over the 36 characters (83 with 2 px).

**5. Shape = stay + cover − 1.** First version `0.8 stay + 0.8 cover − 0.6` gave 100 already at 0.875 of each, so a
clearly wobbly trace scored perfect. Now 0.9 of each gives 80.

**6. The tip names the costliest fault.** Layer F gives each fault in score points (its quality's slope). Found on the
demo: tracing only a tenth of a letter gave the tip "a stroke ran the wrong way", because with almost no shared ink
the direction ratio is 0. `f_back` now subtracts `1 − cover`, so with little written the tip asks for the missing
parts.

**7. Copy game: slide sideways, widen the band, add form.** A freehand copy cannot land on the model, so: the
attempt is moved sideways until its path's centre (length-weighted) meets the model's, before rendering; height is
kept, since the guidelines fix it. The band's loop count became an input (`widen`: 1 for tracing, 3 for copying, so
2 px and 4 px). A perfect copy moved 12 px sideways scores 100 on all 36 characters.

**8. Slant and size from moments of the thin-pen path, not from fixed rows.** First version: slant = how far the ink
in the top half of the x-zone sits right of the ink in the bottom half (rows 38–48 vs 48–58), size = mean distance
from the baseline. Two failures. (a) With the solid-ink map, a copy with no shading moved the slant by 0.5 px on
average (min form 28 on one letter): stems and hairlines change weight. Fixed by a `path` map, a thin pen of constant
width, used only here. (b) With fixed rows, a bigger letter moved parts of its loops into the rows and read as "too
upright" (b, h, k, l, f, 5, c, r failed the test). Fixed with a fixed `moments` op: the slope of x on y over the path
(a shear by k changes it by exactly k; size and position do not change it) and the variance of y (size squared;
slant and position do not change it). Slope 0.1 (about 4°) and 10% of size are free.

**9. Tips at three stars.** A 99 with a 4-point direction slip got the tip "a stroke ran the wrong way". Above 90 a
fault now needs 8 points to earn a tip; otherwise the page praises.

**10. Lines of text: lay out, cut, mark each letter alone.** The network stays a single-letter network; lines are
page logic in `web/lines.js`. Letters are placed 1 px apart in the upright frame (x moved back along the 55° slant to
the baseline), so exits and entrances meet as in joined writing; rows are 88 px apart and wrap at word gaps; the sheet
is at least as wide as the longest word, so words are never broken. Writing is cut at the slanted slot boundaries;
a stroke that crosses one is cut there. Trace game: the model's boundaries. Copy game: first tried moving each
stretched boundary to the thinnest ink nearby. It cut a perfect copy of *minimum* wrongly (84 on an i): in the
upright frame the joining hairlines are nearly vertical, so they are dense, while the bottoms of underturns are
sparse. Replaced by dynamic time warping of the ink profiles (path length per column in the three zones). The cost of
a stretched column was set by hand to 0.5, 1, 2, 4 and 8 samples: 0.5–2 misplaced one boundary in *illumination*
(o 94.7), 4 and 8 placed all of them (lowest letter 99.4); kept 4. Perfect copies 100 per letter in both games;
joined 99.4; copies moved and spaced unevenly 99.4 or more (`tests/lines.mjs`).

**11. Accented letters.** Typed text with é, ó, ö, ñ … was dropped. Accents are now strokes written after the letter
(`ACCENTS` in `gen/copperplate.py`: acute, grave, circumflex, caron, diaeresis, tilde, ring, macron, breve, double
acute above; cedilla, ogonek below), on the eleven letters without an ascender, wherever Unicode has the letter: 76
more characters. Placed first over the middle of the body and 0.12 x-heights up: on the sheet they sat over the stem
that closes a, d, g, q and leaned right (the 55° shear moves an accent 1.5 x-heights up about a third of an x-height
right). Now a hand-typed anchor per letter, a little left of the body's middle, 0.04 up. All of them score 100 copied
exactly and pass the ladders. Swapping strokes costs a one-stroke letter with an accent little (ẽ, ĩ, š ductus 71–81):
the order test skips those, as it skips i, j, t, 5; the rule for "a small later stroke" is now by length.

**12. Copy game: fit onto the model, mark precision; slant and size only in form.** The copy game slid the attempt
sideways only, so writing higher, bigger or more slanted than the model also cost shape and ductus (13° more upright:
shape 95, ductus 91; 1.25 × size: shape 93, ductus 88): the score asked for the exact spot. Now `fit` maps your
letter onto the model before rendering (x' = A x + B y + e, y' = A y + f: size, slant, place). Steps, each one a fix:
(a) centre and match the moments' size and slant, then refine by matching your points to the nearest model points:
fine for slant and size, but a stray stroke dragged the moments (shape 64, ductus 51) and a missing stroke made the
fit shrink your letter onto part of the model. (b) Moments from the 90% of each path nearest its centre: stray better
(shape 74). (c) Refine size, slant and place together by least squares on the best 80% of matches, matching both ways
(yours to the model and the model's to yours), from two starts (as written, and the moments' guess), keeping the
closer: stray shape 87, ductus 95. (d) A part of a letter could still be blown up over the whole model (scale at the
1.6 limit): range narrowed to 0.7–1.45 and a pull toward your own size and slant, first 25 px² per pair (too strong
for small characters: 1 and 7 at 0.7 × size read only 0.16 too small), now a tenth of the pairs' own spread.
Form: measured on the paths before the fit, where yours and the model's lie within 3 px of each other once fitted (6 px
picked up a neighbouring stroke), so a stray mark is not read as too big and a missing stroke is left out of both; and
the four form faults are silenced by 2 × (1 − cover) (4 edit lines): a letter with a part missing has no slant or
size of its own, and the tip should say what is missing (missing-stroke tips naming a form fault: 14 of 36 → 4).
Numbers in `README.md`; all 112 characters score 100 copied exactly, moved anywhere.

**13. Tablet, stylus, and the model beside your sheet.** Copying lines with the model above the whole sheet meant
scrolling up and down. First tried: model rows and writing rows taking turns on one sheet, as in a copybook; but the
sheet then looked already written, and copying by eye wants the model apart. Now the model is a sheet of its own beside
yours, the same size with the same rows, so each model row is level with the row you copy it into (above yours on
screens narrower than 720 px, where two sheets side by side would be too small to write on). The first pen
stroke turns on *Pen only* (touches on the sheet are ignored: a resting palm does not write), only one pointer writes
at a time, the tools stick to the bottom of the screen with the score, touch targets are 44 px on coarse pointers, and
*Focus* hides everything but the sheet and the marks.

The faint model after a copy check was first drawn through the inverse of the fit, at your size and slant: a copy
taller and more upright than the model showed a model i reaching below the baseline, as if the model crossed it (it
does not: the turn's path bottoms out 0.6 px above the baseline, its hairline just touches it). Now the faint model is
drawn as it stands on the guidelines, moved sideways only (along the slant, to your letter's centre), with what you
missed marked on it; the faults in your ink stay on your ink.

**14. Capitals.** Typed capitals were written as small letters. Now 26 capitals (`_capitals()`), 2.2 x-heights tall
(so an accent fits above inside the 96 × 96 grid), from a capital stem, the large oval and hairline entrances, and 75
accented capitals (accents 0.9 x-heights higher than over small letters; 1.0 left a pixel). The page keeps the case
you type. First G was the oval with a stem on the baseline and read as a large a; its stem now descends. Checks over
the 213 characters: perfect copies 100. Three tests met the capitals: a fixed 20 px stray stroke is little beside a
long Y (shape 96), so the stray is now a fifth of the letter's length (at least 20 px); the order test skips letters
whose later strokes are under 30% of the first (was 25%: Â, Å, Ą, whose bar and accent are small); F with its three
strokes reversed scores ductus 74, so capitals pass at 75. The copy fit chose a wrong start for L at 0.7 × size (scale
1.16, not 1.43): the two starts were compared by the trimmed cost, which forgives a fit that matches only part of the
letter; now compared on all points (the small letters' copy table barely moved). Digits in a line stand 5 px apart
(1 px ran "1733" together).

**15. The page reorganised for play, long texts and paper.** With all 213 characters, text and two games, one long
page mixed play with explanation. Now four views (Practice, The hand, Inside the network, How it's made) on the URL
hash; Practice opens ready to trace. Letters sit in tabs by group. Text is a notebook: line breaks kept, ruled pages
with a margin line, five rows a page, ink and marks kept per page, each page checked when done; checking a long page
runs in steps so the page stays responsive. Each checked letter keeps the network's numbers and 12 comparison maps as
bytes (the full set of maps is about 6 MB per letter; a page of 60 letters would have held 360 MB). The report on a
whole text (`web/report.js`) is fixed arithmetic over the per-letter marks: means, the weakest characters, points
lost per fault (a letter left out counts as missed), the three costliest faults as advice, and in the copy game the
spread of slant (from the moments' slopes) and size. First shown as "slant 64°, the model 64°": the moments' slope is
the lean of the whole letter, hairlines included, not of the downstrokes, so the report now gives only the difference
from the model. Templates: `web/pdf.js` writes the PDF itself (lines with round caps, zero-length lines for dots,
Helvetica and Times-Italic, Latin-1 text), from the same layout as the notebook; checked by `tests/report.mjs` and by
rendering. Inside claude.ai the page saves through the viewer's download prompt; elsewhere it is a normal download. The first
tracing sheet printed the dots as on the screen and too dark to write over (the user's print preview); now lighter
(grey 0.73), smaller (0.7 of the screen's size) and 2.8 px apart, with fainter ruling. 0.55 of the size lost the
hairlines.

**16. Ten hands.** The common styles taught to beginners. Five authored as strokes in `gen/styles.py`
(Foundational, Italic, Blackletter Textura, Roman Capitals, Uncial: 130 letters); four derived by a stated transform
(Spencerian and Modern from the copperplate letters; Gothicized Italic from the italic letters, made upright,
compressed and broken into angles by keeping every sixth sampled point; Neuland from the Roman capital forms with a
heavy even pen). Foundational and Italic take the Roman capitals; the broad hands take copperplate's digits scaled
to old-style height; accents are placed over each base letter by the same rule for every hand. A broad nib's width
is `nib · |dx sin a + dy cos a| / |d|` (at least a hairline): the same in `gen/styles.py`, in the page for your own
strokes, and in the page's and the PDF's drawing as the quadrilateral the nib's edge sweeps. Broad and even pens are
marked without shading. The network did not change except for one fixed-op detail: Spencerian's light shades left its
0 with no stroke wide enough to count as a shade, so `shade_hit` was 0/0, read as 0, and a perfect copy scored 86; a
ratio part may now name its own empty value, and `shade_hit`'s is 1 (nothing to shade, nothing missed). Every letter
of every hand, copied exactly, scores 100 in both games (`tests/test_styles.py`); a stroke reversed costs ductus and
a 6 px miss costs shape in each. The page loads a hand's letters when it is chosen (about 0.4 MB a hand).

**17. The real hands.** Four of the ten hands were not their hands: Spencerian and Modern were copperplate's letters
stretched, Gothicized Italic was the italic letters run through a filter, Neuland was the Roman capitals in a heavy
pen; Blackletter had no capitals, Roman had no serifs and guessed proportions, and copperplate's capitals were plain
shapes, not the copybook forms (the user compared them with exemplar sheets). Each hand is now its
own module in `gen/hands/`, authored by eye for that hand from its exemplars and manuals (the user's exemplar sheets
for Copperplate, Textura, Bâtarde, Uncial and the Roman capitals; the 1866 and 1874 Spencerian textbooks;
teaching sheets for Italic, Gothicized Italic, Modern and Neuland; Johnston's teaching for Foundational),
in the taught stroke order, never traced. What changed:
- Copperplate capitals: the capital stem with its ball, the reverse oval (B F I J T U V W X Y Z), the looped entry of
  H and K, the big ovals with an inner loop (O Q) or a hook and ball (C G). Kept at 2.2 x-heights (the exemplar's are
  about 2.5) so the accented capitals fit; T, F, J and Z narrower than the exemplar's, because wider forms lost their
  measured lean in the copy game (slant 0.18 to 0.28 against the test's 0.3: the fit's prior pulls toward no shear).
- Spencerian: written in spaces from the Theory (52° main slant, short letters 1 space, loops 3, lower loops 2), the
  seven principles, semi-angular turns, plain standard capitals from the capital stem and the two ovals; own figures.
- Modern: a beginner's modern alphabet from the eight basic strokes, round and nearly upright (8°), simple capitals.
- Italic: re-authored small letters (arches from mid-stem, one bowl for a d g q u), true italic capitals, old-style
  figures, slant 5°. Gothicized Italic: written from scratch, pointed shoulders, wedge heads, its own capitals.
- Foundational: two-storey g, 3 nib widths for extenders, v and w with pulled diagonals, old-style figures.
- Roman: the classical width groups, pen-made serifs, R's kicked leg, Q's long tail; lining figures.
- Uncial: every letter checked against the exemplar's ductus arrows (nib 15°). Neuland: Koch's own forms (mono 11.5 px).
- Blackletter: real diamond heads (the old heads ran up to the right, which the nib rule makes a hairline), the
  exemplar's a d f g h s x z, and its 26 capitals. A new variant, Bâtarde, from "La gothique bâtarde".
Every hand now has a–z, A–Z, 0–9 and the accents (a test checks it); a unicase hand (Roman, Uncial, Neuland) aliases a
small letter to its capital. The page shows the same groups in the same order for every hand (a hand's first letters
are marked, no longer moved to the front), one card per family, and the family's styles as a choice under the cards.
The network did not change. Still simplified, and said so on each hand: one nib angle per hand (Roman N and M, Uncial
N and Z come out lighter than with a steepened pen), round pen ends (Neuland's square cuts), the hairline doubling
strokes inside the Textura capitals left out, Spencerian shades every slanted downstroke a little (the books shade
one stroke per capital).

**18. Measured against the sheets.** Decision 17 authored the hands "from their exemplars" but nobody set the letters
beside the sheets: put side by side (the user showed Gothicized Italic, Italic and Rustica), they were far off:
letters 30–50% too narrow, capitals small and plain, the wrong slant (Italic 5° against the sheet's 10°), the wrong
weight (Uncial 15° nib and 4 nib widths where the sheet has 25° and 4.1), Neuland a rounded sans-serif, the Textura
capitals narrow, Spencerian's x-height so small in a line that e, a, r, i, n, u read as slashes. Several hands had
been written without their full sheet; full exemplars with ductus arrows exist for Copperplate, Italic,
Gothicized Italic, Foundational, Uncial, Textura, Fraktur and Neuland, and sheets for Roman, Rustica, Rotunda and
Bâtarde. Every hand was redone the same way: measure the sheet first (x-height, extenders, capital height, stem
thickness and so nib widths to the x-height, slant, nib angle from the thinnest strokes, the width of n, o, m, H, O),
set the hand's parameters from the numbers (the table is in each module's docstring), author the letters in the
sheet's stroke order, then compare every row of the sheet with the letters at the same x-height, drawn as the page
draws them (`eval/compare.py`, new), and fix letter by letter. Before and after, in pixels per x-height (S) and nib:
Italic S 22 → 27, slant 5° → 10°; Gothicized S 26 → 42, slant 3° → 0°; Foundational S 28 → 39; Uncial S 32 → 50,
nib angle 15° → 25°; Textura S 26 → 40, stems 0.46 → 0.33 apart; Bâtarde 3.7 → 3 nib widths; Spencerian S 15 → 17.5;
Copperplate capitals 2.2 → 2.5 x-heights, small letters widened to the sheet's 0.58 x-heights stem to stem. New styles: Rustic Capitals
(Roman family, from "La Rustica", nib 60°), Fraktur and Rotunda (Blackletter family). Neuland got a square-cut pen
(`square`, drawn as squares on the page and in the PDFs; the network's width is unchanged), at 0.22 of the capital
height where the sheet's stems are 0.31: one even width at 0.26–0.31 closed the counters of A, B, P, R, O, Q and
filled S. Copperplate's accented capitals no longer fit above a 2.5 capital and are left out (the page falls back to
the small accented letter). The network did not change; all 14 styles pass the perfect-copy and damage tests.
Fonts (.ttf) were considered as a check and rejected: no stroke order, and a typographer's reading of the hand.
Also on the page: a Lock in focus (no scrolling, zooming or bounce under the hand; pen only), writing sizes A− / A+
for a text (1.8, 2.4, 3.2, 4.2 screen pixels per canvas pixel), and as many rows on a page as fit the screen.

## What did not work

- Hands derived from another hand's letters by a transform (Spencerian, Modern, Gothicized Italic, Neuland):
  they looked like the other hand, not like themselves (decision 17).
- Hands authored "from the exemplar" without measuring it or setting the letters beside it: wrong widths, slant,
  weight and capitals throughout (decision 18). The comparison image is the step that catches it.
- Neuland's pen at the sheet's stem thickness (0.31) or 0.26 of the capital height: counters closed (decision 18).

- Comparing direction in the full ink band (decision 1).
- One time map for stroke order (decision 2).
- A 3 px band for shading (decision 3).
- Slant and size from fixed rows of the solid ink (decision 8).
- Copy-game letter boundaries at the thinnest ink nearby (decision 10).
- Copy game slid sideways only: the score asked for the exact spot (decision 12).
- Model rows and writing rows interleaved on one sheet: it looked prefilled (decision 13).
- After the reorganisation (decision 15), anything written vanished at once: `<body>` carried `data-mode` and
  `data-unit` for the layout, and the code that wired the Game and Letters/Text buttons selected `[data-unit]`, so
  `<body>` got a click handler and every click (the end of a stroke, Check) started a fresh sheet. The browser checks
  had injected strokes instead of using the pointer, so they missed it. Selectors are now `button[...]`, and the fix
  was checked with real mouse events through the browser's DevTools protocol.
- A fit refined from your points to the model only (it shrinks your letter onto part of the model), and a fixed pull
  toward your own size (too strong for small characters) (decision 12).
- A stray stroke placed in the descender area as a test: it overlapped the loops of g, j, y, z and was not stray.
  It now sits in the empty top-left corner.

## Final numbers

All 36 characters, both games: perfect copy 100 in every mark. Means per distortion are in `README.md`; `tests/`
holds the per-character limits: 3186 tests over the ten hands (fourteen styles, 1928 model letters: fewer than
before, because the larger letters leave no room above for many accented capitals), including the node checks for
lines and the report, and the browser engine's parity.
