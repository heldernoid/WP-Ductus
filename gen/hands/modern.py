"""Modern calligraphy (pointed pen or brush pen), after a modern calligraphy alphabet (a-z) and its
basic-strokes sheet.

Modern calligraphy is not one fixed script; this hand follows one exemplar: a modern a-z written with
a brush pen, a strongly slanted, compressed hand with a small x-height, long narrow loops and a bouncing baseline.
Measured on that sheet (x-height about 55 px):

  x-height       53-60 px; the letters bounce (r, s and o stand taller, to 1.4-1.6)
  ascenders      h k l d 1.9-2.0, f 2.35, b 2.6, t 1.8 x-heights; the basic-strokes sheet 2.5
  descenders     p 1.2, y 1.35, g z 1.6, q 1.85 x-heights
  slant          stems of m and n 22 degrees from upright (20-26 elsewhere, b's loop 37)
  widths         m and n stems 0.47 x-height apart; a's bowl 0.6 wide, c 0.6, o about 0.65; loops 0.4-0.5 wide
  weight         downstrokes about 0.09 x-height, hairlines about 0.03
  capitals       (the same writer's "Modern Calligraphy" and "Guides" titles) about the ascender height

Set from these: x-height 22.5 px (the tallest-to-lowest span, 2.15 up to 1.55 down, fills the canvas), slant 25 degrees,
ascender loops 2.1, descender loops 1.5, capitals 2.1, figures 1.6. The shade is a little heavier than the sheet's
(2.6 px, 0.12 x-height) so that the pressure strokes read on the canvas.

Every small letter is built from the eight basic strokes (entry upstroke, downstroke, underturn, overturn, compound
curve, oval, ascending and descending loop) in the sheet's order: an entry hairline from the baseline, the body, an
exit hairline; the pen lifts between basic strokes where the sheet's ductus arrows show a new stroke. Upright frame,
unit = x-height (the hand shears it to the slant).
"""
from gen.pen import arc, bez, chain, dot, line  # noqa: F401

CAP = 2.1      # capital height
FIG = 1.6      # figure height
ASC = 2.1      # top of the ascender loops
DSC = -1.5     # bottom of the descender loops
W = 0.47       # stem to stem in m, n, u (the sheet's 0.47)
WO = 0.54      # the oval of a, d, g, q


# ---- the basic strokes ---------------------------------------------------------------------------------------------
def entry(u, top=1.0):
    """entry upstroke: a hairline from the baseline on the left, rising into the head of a downstroke at u"""
    return bez((u - 0.5, 0.0), (u - 0.3, 0.22), (u - 0.14, top + 0.02), (u, top))


def entry_o(u):
    """entry upstroke of an oval letter: a hairline from the baseline on the left up to the oval's left side"""
    return bez((u - 0.5, 0.0), (u - 0.32, 0.08), (u - 0.14, 0.26), (u - 0.05, 0.46))


def down(u, v0, v1):
    """downstroke (shaded)"""
    return line((u, v0), (u, v1))


def underturn(u, w=0.38, top=0.6):
    """from the foot of a downstroke at u: round the baseline, rising as a hairline to (u + w, top)"""
    return chain(bez((u, 0.3), (u, -0.06), (u + 0.62 * w, -0.07), (u + 0.82 * w, 0.24)),
                 bez((u + 0.82 * w, 0.24), (u + 0.9 * w, 0.4), (u + 0.96 * w, 0.62 * top + 0.08), (u + w, top)))


def overturn(u0, u1, v0=0.32):
    """branching from a downstroke at u0 (height v0): a hairline rising over a narrow round arch into the head of the
    downstroke at u1"""
    return chain(bez((u0, v0), (u0 + 0.06, 0.88), (u1 - 0.14, 1.08), (u1 - 0.03, 0.95)),
                 bez((u1 - 0.03, 0.95), (u1, 0.9), (u1, 0.84), (u1, 0.74)))


def oval(u=0.0, w=WO, start=None):
    """counter-clockwise oval, from its top right: over the top, down the left (shaded), round the bottom, up the
    right as a hairline, back to the start"""
    s = start or (u + 0.88 * w, 0.86)
    return chain(bez(s, (u + 0.72 * w, 1.06), (u + 0.02 * w, 1.06), (u, 0.5)),
                 bez((u, 0.5), (u - 0.02 * w, -0.05), (u + 0.82 * w, -0.08), (u + w, 0.36)),
                 bez((u + w, 0.36), (u + 1.05 * w, 0.56), (u + 1.02 * w, 0.74), s))


def asc_loop(u, start=(-0.4, 0.25), top=ASC, w=0.46):
    """ascending loop: a hairline rising to the right of a stem at u, over the narrow top to the left into the stem
    head (the downstroke follows)"""
    s0 = (u + start[0], start[1])
    return chain(bez(s0, (u + 0.08, 0.75), (u + w + 0.06, top - 0.9), (u + 0.8 * w, top - 0.2)),
                 bez((u + 0.8 * w, top - 0.2), (u + 0.6 * w, top + 0.07), (u, top + 0.02), (u, top - 0.42)))


def desc_loop(u, w=0.46):
    """descending loop on the left of a stem at u that has come down to -0.6: round the narrow bottom to the left, then
    a hairline rising to the right, crossing the stem near the baseline"""
    return chain(bez((u, -0.6), (u, DSC - 0.05), (u - w, DSC - 0.05), (u - 0.85 * w, -0.72)),
                 bez((u - 0.85 * w, -0.72), (u - 0.7 * w, -0.3), (u + 0.1, -0.06), (u + 0.42, 0.38)))


def desc_loop_right(u, w=0.42):
    """descending loop on the right of a stem at u (f, q): round the bottom to the right, back up to the stem at the
    baseline, then the exit"""
    return chain(bez((u, -0.6), (u, DSC - 0.05), (u + w, DSC - 0.05), (u + 0.9 * w, -0.6)),
                 bez((u + 0.9 * w, -0.6), (u + 0.8 * w, -0.25), (u + 0.25 * w, -0.06), (u + 0.07, 0.04)),
                 bez((u + 0.07, 0.04), (u + 0.24, 0.1), (u + 0.38, 0.3), (u + 0.46, 0.55)))


def tick(u, top=0.9):
    """the small loop that closes b, v and w at the x-height (u = where the rising hairline ends), then the exit"""
    return chain(bez((u, top), (u + 0.02, top + 0.16), (u - 0.18, top + 0.15), (u - 0.17, top + 0.02)),
                 bez((u - 0.17, top + 0.02), (u - 0.07, top - 0.07), (u + 0.1, top - 0.07), (u + 0.28, top)))


# ---- small letters ------------------------------------------------------------------------------------------------
def _small():
    L = {}
    L["a"] = [entry_o(0), oval(0), chain(down(WO, 1.0, 0.3), underturn(WO))]
    L["b"] = [chain(asc_loop(0), down(0, ASC - 0.42, 0.02)),
              chain(bez((0, 0.36), (0.05, 0.86), (0.4, 1.08), (0.48, 0.8)), bez((0.48, 0.8), (0.55, 0.42), (0.38, -0.05), (0.2, -0.02)),
                    bez((0.2, -0.02), (0.1, 0.0), (0.07, 0.06), (0.08, 0.13)))]
    L["c"] = [entry_o(-0.04),
              chain(bez((0.44, 0.76), (0.54, 0.92), (0.44, 1.04), (0.3, 1.02)), bez((0.3, 1.02), (0.06, 0.98), (-0.04, 0.72), (-0.04, 0.5)),
                    bez((-0.04, 0.5), (-0.05, 0.02), (0.36, -0.08), (0.6, 0.34)))]
    L["d"] = [entry_o(0), oval(0), chain(asc_loop(WO, start=(-0.06, 0.95), top=1.95), down(WO, 1.95 - 0.42, 0.3), underturn(WO))]
    L["e"] = [chain(bez((-0.48, 0.0), (-0.12, 0.22), (0.46, 0.5), (0.46, 0.8)), bez((0.46, 0.8), (0.46, 1.05), (0.08, 1.06), (-0.02, 0.7)),
                    bez((-0.02, 0.7), (-0.1, 0.2), (0.3, -0.1), (0.58, 0.32)))]
    L["f"] = [chain(asc_loop(0, top=2.25), down(0, 2.25 - 0.42, -0.6), desc_loop_right(0))]
    L["g"] = [entry_o(0), oval(0), chain(down(WO, 1.0, -0.6), desc_loop(WO))]
    L["h"] = [chain(asc_loop(0), down(0, ASC - 0.42, 0.0)), chain(overturn(0, W), down(W, 0.74, 0.3), underturn(W))]
    L["i"] = [chain(entry(0), down(0, 1.0, 0.3), underturn(0)), dot(0.06, 1.45)]
    L["j"] = [chain(entry(0), down(0, 1.0, -0.6), desc_loop(0)), dot(0.06, 1.45)]
    L["k"] = [chain(asc_loop(0), down(0, ASC - 0.42, 0.0)),
              chain(bez((0, 0.34), (0.06, 0.88), (0.5, 1.1), (0.5, 0.82)), bez((0.5, 0.82), (0.5, 0.56), (0.26, 0.5), (0.1, 0.5)),
                    bez((0.1, 0.5), (0.32, 0.48), (0.42, 0.42), (0.42, 0.3)), underturn(0.42, 0.34, 0.55))]
    L["l"] = [chain(asc_loop(0), down(0, ASC - 0.42, 0.3), underturn(0))]
    L["m"] = [chain(entry(0), down(0, 1.0, 0.0)), chain(overturn(0, W), down(W, 0.74, 0.0)),
              chain(overturn(W, 2 * W), down(2 * W, 0.74, 0.3), underturn(2 * W))]
    L["n"] = [chain(entry(0), down(0, 1.0, 0.0)), chain(overturn(0, W), down(W, 0.74, 0.3), underturn(W))]
    # o stands a little taller than the x-height on the sheet; it closes at the top and leaves with a hairline
    L["o"] = [entry_o(0), chain(oval(0, 0.64, start=(0.46, 1.08)), bez((0.46, 1.08), (0.6, 0.98), (0.76, 0.94), (0.92, 0.98)))]
    L["p"] = [chain(entry(0), down(0, 1.0, -1.2)),
              chain(overturn(0, 0.54), down(0.54, 0.74, 0.36), bez((0.54, 0.36), (0.54, -0.07), (0.16, -0.08), (0.06, 0.12)))]
    L["q"] = [entry_o(0), oval(0), chain(down(WO, 1.0, -0.6), desc_loop_right(WO))]
    # r rises to a small loop above the x-height (the sheet's looped r), then the downstroke and a turn at the base
    L["r"] = [chain(entry(0.16, 1.36), bez((0.16, 1.36), (0.14, 1.5), (-0.1, 1.5), (-0.1, 1.32)),
                    bez((-0.1, 1.32), (-0.1, 1.12), (0.16, 1.08), (0.34, 1.0)), down(0.34, 1.0, 0.3), underturn(0.34))]
    # s: a tall entry to its point (1.45), then the compound curve down and a small closing curl on the base
    L["s"] = [chain(bez((-0.5, 0.0), (-0.2, 0.3), (0.06, 1.0), (0.12, 1.45)),
                    bez((0.12, 1.45), (0.5, 0.95), (0.66, 0.5), (0.52, 0.18)),
                    bez((0.52, 0.18), (0.38, -0.08), (0.0, -0.06), (-0.08, 0.14)),
                    bez((-0.08, 0.14), (-0.06, 0.3), (0.12, 0.3), (0.2, 0.2)))]
    L["t"] = [chain(down(0, 1.8, 0.3), underturn(0)), bez((-0.3, 1.0), (-0.05, 1.06), (0.25, 0.98), (0.5, 1.05))]
    L["u"] = [chain(entry(0), down(0, 1.0, 0.3), underturn(0, W, 1.0)), chain(down(W, 1.0, 0.3), underturn(W))]
    L["v"] = [chain(entry(0), down(0, 1.0, 0.3), underturn(0, 0.5, 0.92), tick(0.5, 0.92))]
    L["w"] = [chain(entry(0), down(0, 1.0, 0.3), underturn(0, W, 1.0), down(W, 1.0, 0.3), underturn(W, 0.46, 0.92),
                    tick(W + 0.46, 0.92))]
    L["x"] = [chain(overturn(-0.36, 0.06, 0.1), down(0.06, 0.74, 0.3), underturn(0.06, 0.42, 0.55)),
              line((-0.3, 0.04), (0.5, 0.96))]
    L["y"] = [chain(entry(0), down(0, 1.0, 0.3), underturn(0, W, 1.0)), chain(down(W, 1.0, -0.6), desc_loop(W))]
    # z: a hooked top, the diagonal, then a descending loop (the sheet's looped z)
    L["z"] = [chain(bez((-0.16, 0.76), (-0.08, 1.0), (0.06, 1.02), (0.16, 0.98)), bez((0.16, 0.98), (0.3, 0.94), (0.44, 1.04), (0.56, 1.0)),
                    bez((0.56, 1.0), (0.4, 0.6), (0.2, 0.3), (0.06, 0.1)), bez((0.06, 0.1), (0.3, 0.2), (0.5, 0.1), (0.5, -0.3)),
                    bez((0.5, -0.3), (0.5, -0.9), (0.4, DSC - 0.04), (0.2, DSC + 0.02)),
                    bez((0.2, DSC + 0.02), (-0.02, DSC + 0.1), (0.0, -0.6), (0.3, -0.2)),
                    bez((0.3, -0.2), (0.45, 0.0), (0.6, 0.2), (0.78, 0.5)))]
    return L


# ---- capitals -----------------------------------------------------------------------------------------------------
def _capitals():
    """authored 1.8 high and scaled to CAP below"""
    C = 1.8
    L = {}

    def head(u, top=C):
        """a hooked entry into the top of a capital downstroke at u: a hairline from the left, a small loop, down"""
        return bez((u - 0.36, top - 0.42), (u - 0.3, top - 0.04), (u - 0.04, top + 0.08), (u, top - 0.2))

    def foot(u):
        """the foot of a capital downstroke at u: a small turn to the left on the baseline"""
        return bez((u, 0.3), (u, -0.05), (u - 0.3, -0.06), (u - 0.38, 0.14))

    L["A"] = [chain(bez((-0.25, 0.05), (0.1, 0.6), (0.4, 1.3), (0.55, C)), line((0.55, C), (0.9, 0.3)), underturn(0.9, 0.38, 0.55)),
              bez((0.0, 0.8), (0.35, 0.95), (0.75, 0.68), (1.2, 0.86))]
    L["B"] = [chain(head(0.1), down(0.1, C - 0.2, 0.3), foot(0.1)),
              chain(bez((-0.12, 1.55), (0.25, 1.95), (1.05, 1.98), (0.95, 1.4)), bez((0.95, 1.4), (0.88, 1.05), (0.5, 0.98), (0.26, 0.98)),
                    bez((0.26, 0.98), (0.85, 1.0), (1.2, 0.68), (1.06, 0.3)), bez((1.06, 0.3), (0.92, -0.06), (0.36, -0.06), (0.12, 0.08)))]
    L["C"] = [chain(bez((0.98, 1.4), (1.1, 1.78), (0.75, 1.92), (0.48, 1.78)), bez((0.48, 1.78), (-0.02, 1.52), (-0.15, 0.5), (0.18, 0.13)),
                    bez((0.18, 0.13), (0.48, -0.15), (0.95, 0.0), (1.12, 0.36)))]
    L["D"] = [chain(head(0.2), down(0.2, C - 0.2, 0.3), bez((0.2, 0.3), (0.2, -0.04), (-0.2, -0.06), (-0.26, 0.1)),
                    bez((-0.26, 0.1), (-0.2, 0.28), (0.25, 0.0), (0.62, 0.0)), bez((0.62, 0.0), (1.5, 0.02), (1.52, C + 0.02), (0.62, C)),
                    bez((0.62, C), (0.4, C - 0.01), (0.2, C - 0.06), (0.06, C - 0.14)))]
    L["E"] = [chain(bez((0.92, 1.5), (1.0, 1.86), (0.4, 1.94), (0.3, 1.58)), bez((0.3, 1.58), (0.24, 1.25), (0.55, 1.04), (0.72, 1.0)),
                    bez((0.72, 1.0), (0.12, 1.02), (-0.15, 0.68), (0.0, 0.28)), bez((0.0, 0.28), (0.15, -0.08), (0.8, -0.08), (1.06, 0.34)))]
    L["F"] = [bez((-0.2, 1.62), (0.25, 1.9), (0.8, 1.6), (1.35, 1.84)),
              chain(down(0.55, 1.7, 0.3), bez((0.55, 0.3), (0.55, -0.06), (0.12, -0.08), (-0.02, 0.18))),
              bez((0.22, 0.9), (0.45, 1.0), (0.7, 0.88), (0.96, 0.96))]
    L["G"] = [chain(bez((0.98, 1.4), (1.1, 1.78), (0.75, 1.92), (0.48, 1.78)), bez((0.48, 1.78), (-0.02, 1.52), (-0.15, 0.5), (0.18, 0.13)),
                    bez((0.18, 0.13), (0.5, -0.12), (0.95, 0.0), (1.05, 0.45)), line((1.05, 0.45), (1.1, 0.95))),
              chain(down(1.1, 0.95, -0.55), desc_loop(1.1, 0.5))]
    L["H"] = [chain(head(0.1), down(0.1, C - 0.2, 0.3), foot(0.1)),
              chain(bez((0.82, 1.62), (0.88, 1.84), (1.0, 1.88), (1.05, 1.7)), down(1.05, 1.7, 0.32), underturn(1.05, 0.38, 0.55)),
              bez((-0.12, 0.82), (0.3, 1.1), (0.75, 0.78), (1.25, 1.0))]
    L["I"] = [chain(bez((-0.3, 1.25), (-0.15, 1.85), (0.45, 2.0), (0.55, 1.65)), down(0.55, 1.65, 0.3),
                    bez((0.55, 0.3), (0.55, -0.06), (0.12, -0.08), (0.0, 0.15)))]
    L["J"] = [chain(bez((-0.3, 1.25), (-0.15, 1.85), (0.45, 2.0), (0.55, 1.65)), down(0.55, 1.65, -0.55), desc_loop(0.55, 0.5))]
    L["K"] = [chain(head(0.1), down(0.1, C - 0.2, 0.3), foot(0.1)),
              chain(bez((1.15, 1.76), (1.0, 1.9), (0.75, 1.6), (0.36, 1.0)), bez((0.36, 1.0), (0.24, 0.84), (0.48, 0.9), (0.62, 0.74)),
                    line((0.62, 0.74), (0.8, 0.32)), underturn(0.8, 0.38, 0.55))]
    L["L"] = [chain(bez((0.95, 1.6), (0.98, 1.92), (0.5, 1.9), (0.45, 1.55)), down(0.43, 1.55, 0.3),
                    bez((0.43, 0.3), (0.4, -0.06), (-0.12, -0.1), (-0.12, 0.12)), bez((-0.12, 0.12), (0.0, 0.3), (0.4, -0.04), (1.1, 0.1)))]
    # M as on the same writer's "Modern" title: a swash entry over the top into a tall stem, then two arches (a tall m)
    L["M"] = [chain(bez((-0.42, 1.0), (-0.42, 1.6), (0.0, C + 0.04), (0.15, C)), down(0.15, C, 0.0)),
              chain(bez((0.15, 0.6), (0.2, 1.48), (0.6, 1.72), (0.7, 1.5)), bez((0.7, 1.5), (0.72, 1.43), (0.72, 1.36), (0.72, 1.26)),
                    down(0.72, 1.26, 0.0)),
              chain(bez((0.72, 0.6), (0.77, 1.48), (1.17, 1.72), (1.27, 1.5)), bez((1.27, 1.5), (1.29, 1.43), (1.29, 1.36), (1.29, 1.26)),
                    down(1.29, 1.26, 0.3), underturn(1.29, 0.36, 0.55))]
    L["N"] = [chain(bez((-0.2, 0.0), (-0.08, 0.6), (0.02, 1.3), (0.08, C)), line((0.08, C), (0.95, 0.0)),
                    line((0.95, 0.0), (1.02, C)), bez((1.02, C), (1.08, C + 0.06), (1.22, C + 0.06), (1.34, C - 0.02)))]
    L["O"] = [chain(bez((0.62, C), (0.0, C + 0.04), (-0.18, 1.0), (-0.06, 0.55)), bez((-0.06, 0.55), (0.06, -0.06), (1.0, -0.12), (1.14, 0.7)),
                    bez((1.14, 0.7), (1.24, 1.4), (0.95, C + 0.04), (0.52, 1.74)), bez((0.52, 1.74), (0.42, 1.7), (0.32, 1.65), (0.2, 1.58)))]
    L["P"] = [chain(head(0.1), down(0.1, C - 0.2, 0.3), foot(0.1)),
              chain(bez((-0.12, 1.5), (0.25, 1.96), (1.12, 1.94), (1.02, 1.3)), bez((1.02, 1.3), (0.92, 0.82), (0.45, 0.8), (0.22, 0.98)))]
    L["Q"] = [list(L["O"][0]), bez((0.2, 0.08), (0.5, -0.2), (0.85, 0.1), (1.32, -0.14))]
    L["R"] = [chain(head(0.1), down(0.1, C - 0.2, 0.3), foot(0.1)),
              chain(bez((-0.12, 1.5), (0.25, 1.96), (1.12, 1.94), (1.02, 1.3)), bez((1.02, 1.3), (0.92, 0.82), (0.45, 0.8), (0.22, 0.98)),
                    bez((0.22, 0.98), (0.62, 0.92), (0.75, 0.7), (0.78, 0.32)), underturn(0.78, 0.38, 0.55))]
    L["S"] = [chain(bez((1.0, 1.45), (1.08, 1.8), (0.65, 1.92), (0.42, 1.78)), bez((0.42, 1.78), (0.1, 1.6), (0.18, 1.2), (0.48, 1.0)),
                    bez((0.48, 1.0), (0.85, 0.75), (1.0, 0.5), (0.85, 0.2)), bez((0.85, 0.2), (0.65, -0.12), (0.05, -0.08), (-0.05, 0.2)),
                    bez((-0.05, 0.2), (-0.08, 0.38), (0.12, 0.42), (0.22, 0.28)))]
    L["T"] = [bez((-0.2, 1.62), (0.25, 1.9), (0.8, 1.6), (1.35, 1.84)),
              chain(down(0.55, 1.7, 0.3), bez((0.55, 0.3), (0.55, -0.06), (0.12, -0.08), (-0.02, 0.18)))]
    L["U"] = [chain(head(0.1), down(0.1, C - 0.2, 0.36), bez((0.1, 0.36), (0.1, -0.07), (0.82, -0.07), (0.94, 0.4)), line((0.94, 0.4), (1.02, C))),
              chain(down(1.02, C, 0.32), underturn(1.02, 0.38, 0.55))]
    L["V"] = [chain(head(0.1), line((0.1, C - 0.2), (0.5, 0.0)), bez((0.5, 0.0), (0.75, 0.6), (0.95, 1.4), (1.1, C)),
                    bez((1.1, C), (1.16, C + 0.06), (1.3, C + 0.06), (1.42, C - 0.02)))]
    L["W"] = [chain(head(0.1), line((0.1, C - 0.2), (0.42, 0.0)), line((0.42, 0.0), (0.8, 1.55)), line((0.8, 1.55), (1.12, 0.0)),
                    bez((1.12, 0.0), (1.32, 0.6), (1.45, 1.4), (1.58, C)), bez((1.58, C), (1.64, C + 0.06), (1.78, C + 0.06), (1.9, C - 0.02)))]
    L["X"] = [chain(head(0.1), line((0.1, C - 0.2), (0.9, 0.32)), underturn(0.9, 0.38, 0.55)), line((-0.15, 0.02), (1.12, C))]
    L["Y"] = [chain(head(0.1), down(0.1, C - 0.2, 0.62), bez((0.1, 0.62), (0.1, 0.04), (0.84, 0.04), (0.92, 0.62)), line((0.92, 0.62), (1.0, C))),
              chain(down(1.0, C, -0.55), desc_loop(1.0, 0.5))]
    L["Z"] = [chain(bez((-0.05, 1.5), (0.1, 1.86), (0.4, 1.78), (0.65, 1.76)), bez((0.65, 1.76), (0.85, 1.75), (1.0, 1.8), (1.1, C)),
                    line((1.1, C), (-0.05, 0.04)), bez((-0.05, 0.04), (0.35, 0.22), (0.72, -0.1), (1.15, 0.1)))]
    return L


# ---- figures ------------------------------------------------------------------------------------------------------
def _figures():
    F = FIG
    L = {}
    L["0"] = [chain(bez((0.45, F), (-0.02, F + 0.02), (-0.08, 0.6), (0.06, 0.25)), bez((0.06, 0.25), (0.2, -0.1), (0.75, -0.08), (0.8, 0.6)),
                    bez((0.8, 0.6), (0.85, 1.2), (0.75, F), (0.45, F)))]
    L["1"] = [chain(bez((-0.05, 1.2), (0.15, 1.3), (0.3, 1.45), (0.4, F)), down(0.4, F, 0.0))]
    L["2"] = [chain(bez((-0.02, 1.15), (0.02, 1.6), (0.72, 1.72), (0.7, 1.2)), bez((0.7, 1.2), (0.68, 0.8), (0.2, 0.42), (-0.02, 0.06)),
                    bez((-0.02, 0.06), (-0.08, -0.04), (0.06, 0.1), (0.2, 0.08)), bez((0.2, 0.08), (0.4, 0.04), (0.6, -0.04), (0.82, 0.08)))]
    L["3"] = [chain(bez((0.0, 1.3), (0.1, 1.68), (0.72, 1.7), (0.66, 1.25)), bez((0.66, 1.25), (0.62, 0.98), (0.4, 0.88), (0.24, 0.86)),
                    bez((0.24, 0.86), (0.66, 0.84), (0.82, 0.55), (0.72, 0.26)), bez((0.72, 0.26), (0.58, -0.08), (0.05, -0.08), (-0.04, 0.24)))]
    L["4"] = [chain(line((0.5, F), (-0.06, 0.5)), line((-0.06, 0.5), (0.86, 0.5))), down(0.58, 1.12, 0.0)]
    L["5"] = [chain(line((0.12, F - 0.04), (0.06, 0.88)), bez((0.06, 0.88), (0.45, 1.08), (0.8, 0.85), (0.74, 0.4)),
                    bez((0.74, 0.4), (0.68, -0.06), (0.08, -0.08), (-0.04, 0.22))),
              bez((0.12, F - 0.04), (0.35, F + 0.02), (0.55, F - 0.04), (0.78, F + 0.02))]
    L["6"] = [chain(bez((0.66, 1.5), (0.5, F + 0.08), (0.05, F), (0.0, 0.8)), bez((0.0, 0.8), (-0.04, 0.0), (0.72, -0.12), (0.76, 0.42)),
                    bez((0.76, 0.42), (0.8, 0.88), (0.2, 0.92), (0.03, 0.55)))]
    L["7"] = [chain(bez((-0.02, 1.52), (0.25, 1.64), (0.5, 1.56), (0.84, F)), bez((0.84, F), (0.6, 1.2), (0.4, 0.6), (0.3, 0.0)))]
    L["8"] = [chain(bez((0.68, 1.3), (0.7, 1.7), (0.02, 1.72), (0.06, 1.28)), bez((0.06, 1.28), (0.1, 0.95), (0.78, 0.75), (0.76, 0.36)),
                    bez((0.76, 0.36), (0.74, -0.08), (-0.04, -0.08), (-0.02, 0.36)), bez((-0.02, 0.36), (0.0, 0.75), (0.66, 0.95), (0.68, 1.3)))]
    L["9"] = [chain(bez((0.72, 1.3), (0.62, 1.66), (0.04, 1.68), (0.04, 1.2)), bez((0.04, 1.2), (0.04, 0.78), (0.6, 0.76), (0.72, 1.18)),
                    bez((0.72, 1.18), (0.74, 0.7), (0.68, 0.3), (0.5, 0.12)), bez((0.5, 0.12), (0.32, -0.06), (0.08, -0.04), (0.0, 0.1)))]
    return L


def letters():
    L = _small()
    L.update({ch: [[(u * CAP / 1.8, v * CAP / 1.8) for u, v in st] for st in sts] for ch, sts in _capitals().items()})
    L.update(_figures())
    return L


HAND = dict(
    id="modern", name="Modern", family="modern", variant=None, pen="pointed", S=22.5, base=54.5, slant_deg=25, ext=(ASC, -DSC),
    start="iunmaoclet", sample="Modern", keys="aglo", hair=1.0, shade=2.6, dot_w=3.0, cap=CAP, bounce=3.0,
    about={
        "tool": "A brush pen or a flexible pointed nib: press on the way down, lift to a hairline on the way up.",
        "slant": "Strongly slanted: about 25° from upright, as on the exemplar a-z (writers range from upright to about 30°).",
        "proportions": "A small x-height with long, narrow loops: ascenders about twice the x-height, descenders about one and a "
                       "half; compressed letters (m and n stems half an x-height apart); capitals as tall as the ascenders.",
        "features": "Small letters are built from eight basic strokes (entry upstroke, downstroke, underturn, overturn, "
                    "compound curve, oval, ascending and descending loop), with an entry hairline from the baseline and an "
                    "exit hairline; long narrow loops; a looped r and z, a tall s; a bouncing baseline, where letters rise "
                    "and dip a little.",
        "history": "A 21st-century practice, not one fixed script: it loosens the rules of copperplate and pointed-pen "
                   "script. This model follows one exemplar, a modern calligraphy alphabet; the bounce of "
                   "the sheet is kept only in r, s and o, joins and flourishes are left out, and the capitals and figures, "
                   "which the sheet does not show, are simple open forms in the same style."})
