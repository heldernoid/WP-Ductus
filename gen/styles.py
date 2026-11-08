"""The calligraphy hands. Copperplate's letters are in
gen/copperplate.py; every other hand is a module in gen/hands/ with `letters()` (its strokes) and `HAND` (its pen,
guidelines and description). This file turns them into model letters on the 96 x 96 canvas.

Every letter is pen strokes in writing order, in an upright frame: u to the right and v up, in x-heights (for the
capital-only hands, in capital heights). A hand shears the frame to its slant, scales it to the canvas and gives each
point a pen width by its pen:

  pointed   width from pressure, which the pointed-pen rule gives to downstrokes along the slant (as copperplate)
  broad     a broad nib held at a fixed angle: the width is the nib's width times the sine of the angle between the
            stroke and the nib's edge (thick across the nib, thin along it); nothing to press
  mono      one width everywhere (Neuland's heavy, low-contrast strokes); `square` draws it with a square end

Every hand has the same alphabet: a-z, A-Z, 0-9 and the accented letters. A unicase hand (Roman capitals, Uncial,
Neuland: one set of forms) has no separate small letters; a small letter is written with its capital's form (`alias`).
"""
import importlib
import math
import unicodedata

from gen import copperplate as cp

# the hands in the picker's order, families together (a family's first hand is its main form, the rest variants)
ORDER = ["copperplate", "spencerian", "modern", "italic", "foundational", "roman", "rustica", "uncial", "blackletter", "batarde", "fraktur", "rotunda",
         "gothicized", "neuland"]
MODULE = {"blackletter": "textura"}          # module name where it differs from the hand's id
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
ACC_BASES = "aceinorsuyzACEINORSUYZ"


# ---- the hands --------------------------------------------------------------------------------------------------------
class Hand:
    def __init__(self, id, name, pen, S, base, slant_deg, ext, letters, about, start, sample, keys, nib_angle=0.0, nib=0.0,
                 hair=1.0, shade=4.0, dot_w=3.4, mono=0.0, cap=None, bounce=0.0, unicase=False, k=None, family=None,
                 variant=None, square=False):
        self.id, self.name, self.pen, self.S, self.base = id, name, pen, S, base
        self.k = k if k is not None else math.tan(math.radians(slant_deg))   # horizontal shift per unit of height
        self.slant_deg, self.ext, self.letters, self.about = slant_deg, ext, letters, about
        self.start, self.sample, self.keys = start, sample, keys
        self.nib_angle, self.nib, self.hair, self.shade, self.dot_w, self.mono = nib_angle, nib, hair, shade, dot_w, mono
        self.cap, self.bounce, self.unicase = cap, bounce, unicase
        self.caps_only = unicase                      # the guidelines of a hand of capitals
        self.family, self.variant = family or id, variant
        self.alias = {}
        self.square = square                          # a mono pen with a square end (Neuland), not a round one

    def guides(self):
        g = {}
        up, down = self.ext
        if self.caps_only:
            if up > 1.001:
                g["ascender"] = self.base - up * self.S
            g["cap height" if up <= 1.001 else "x-height"] = self.base - self.S
        else:
            g["ascender"] = self.base - up * self.S
            g["x-height"] = self.base - self.S
        g["baseline"] = self.base
        if down > 0.001:
            g["descender"] = self.base + down * self.S
        return {k: round(v, 3) for k, v in g.items()}

    def width(self, dx, dy):
        n = math.hypot(dx, dy) or 1
        if self.pen == "mono":
            return self.mono
        if self.pen == "broad":
            a = math.radians(self.nib_angle)                  # the nib's edge: up to the right at this angle
            return max(self.hair, self.nib * abs(dx * math.sin(a) + dy * math.cos(a)) / n)
        # pointed: pressure only while moving down along the slant
        sx, sy = -self.k / math.hypot(self.k, 1), 1 / math.hypot(self.k, 1)
        p = (dx * sx + dy * sy) / n
        f = min(1.0, max(0.0, (p - 0.55) / 0.4))
        return self.hair + (self.shade - self.hair) * f * f * (3 - 2 * f)

    def to_canvas(self, strokes, centre=48.0):
        xy = [[(self.S * (u + v * self.k), self.base - self.S * v) for u, v in st] for st in strokes]
        xs = [x for st in xy for x, _ in st]
        shift = centre - (min(xs) + max(xs)) / 2
        out = []
        for st in xy:
            st = [(x + shift, y) for x, y in st]
            if len(st) == 1:
                out.append([(st[0][0], st[0][1], self.mono if self.pen == "mono" else self.dot_w)])
                continue
            out.append([(x, y, self.width(st[min(len(st) - 1, k + 1)][0] - st[max(0, k - 1)][0], st[min(len(st) - 1, k + 1)][1] - st[max(0, k - 1)][1]))
                        for k, (x, y) in enumerate(st)])
        return out

    def model(self, ch):
        return self.to_canvas(self.letters[ch])

    def sample_strokes(self):
        """the sample word, letters side by side, for the picker"""
        out, x = [], 0.0
        for ch in self.sample:
            m = self.model(ch)
            xs = [p[0] - p[2] / 2 for st in m for p in st] + [p[0] + p[2] / 2 for st in m for p in st]
            dx = x - min(xs)
            out += [[(round(p[0] + dx, 1), round(p[1], 1), round(p[2], 2)) for p in st] for st in m]
            x = max(xs) + dx + (2 if self.pen != "pointed" else -0.3 * self.S)   # pointed letters overlap: their entry and exit strokes join
        return out

    def export(self):
        return {"id": self.id, "name": self.name, "pen": self.pen, "slant": self.k, "slant_deg": self.slant_deg,
                "guides": self.guides(), "nib_angle": self.nib_angle, "nib": self.nib, "hair": self.hair, "shade": self.shade,
                "dot": self.dot_w, "mono": self.mono, "square": self.square, "bounce": self.bounce, "caps_only": self.caps_only, "unicase": self.unicase,
                "family": self.family, "variant": self.variant, "alias": self.alias,
                "start": self.start, "keys": self.keys, "about": self.about,
                "letters": {ch: [[[round(x, 3), round(y, 3), round(w, 3)] for x, y, w in st] for st in self.model(ch)] for ch in self.letters}}


def _accented(hand, bases):
    """accented letters for a hand: copperplate's accent strokes, placed over the body of each base letter (the dot of
    i and j left out), moved up or down so they sit just above it; cedilla and ogonek under the foot. A character
    whose accent would leave the canvas is skipped."""
    out = {}
    for base in bases:
        if base not in hand.letters:
            continue
        strokes = [st for st in hand.letters[base] if not (base in "ij" and len(st) == 1)]
        top = 1.0 if base.islower() else (hand.cap or 1.0)
        body = [p for st in strokes for p in st if 0.1 <= p[1] <= top + 0.05]
        if not body:
            continue
        mid = (min(u for u, _ in body) + max(u for u, _ in body)) / 2
        foot = min(body, key=lambda p: (p[1], -p[0]))[0]
        for mark, draw in cp.ACCENTS.items():
            ch = unicodedata.normalize("NFC", base + mark)
            if len(ch) != 1:
                continue
            if mark in ("̧", "̨"):
                acc = draw(foot)
            else:
                raw = draw(mid)
                lo = min(v for st in raw for _, v in st)
                dv = top + 0.12 - lo                        # the accent's foot just above the letter
                acc = [[(u - hand.k * (top + 0.3 - 0.5 * top), v + dv) for u, v in st] for st in raw]
            letters = strokes + acc
            ys = [hand.base - hand.S * v for st in letters for _, v in st]
            if min(ys) < 2 or max(ys) > 94:
                continue
            out[ch] = letters
    return out



ABOUT_COPPERPLATE = {
    "tool": "A flexible pointed nib, usually in an oblique holder.", "slant": "55°.",
    "proportions": "3 : 2 : 3 (ascender : x-height : descender).",
    "features": "Shaded downstrokes, hairline upstrokes, ovals and loops; every thick and thin comes from pressure. "
                "Capitals 2.5 x-heights tall, as on the exemplar; the exemplar has no figures, so these are in the "
                "copybook style. An accent would leave the page above a capital, so the accented capitals are left out.",
    "history": "The English Roundhand of the writing masters, late 17th and 18th centuries; named after the engraved copper plates of their copybooks."}




def build(id):
    """one hand, from its module (or copperplate's letters)"""
    if id == "copperplate":
        h = Hand("copperplate", "Copperplate", "pointed", cp.S, cp.BASE_Y, 35, (2.5, 1.5), dict(cp.LETTERS), ABOUT_COPPERPLATE,
                 "iunmaocelt", "hand", "", hair=cp.HAIR, shade=cp.SHADE, dot_w=cp.DOT, cap=2.5, k=cp.SLANT)
    else:
        mod = importlib.import_module("gen.hands." + MODULE.get(id, id))
        kw = dict(mod.HAND)
        args = [kw.pop(k) for k in ("id", "name", "pen", "S", "base", "slant_deg", "ext")]
        about, start, sample, keys = kw.pop("about"), kw.pop("start"), kw.pop("sample"), kw.pop("keys")
        h = Hand(args[0], args[1], args[2], args[3], args[4], args[5], args[6], mod.letters(), about, start, sample, keys, **kw)
        h.letters.update({k: v for k, v in _accented(h, ACC_BASES).items() if k not in h.letters})
    if h.unicase:                                   # one set of forms: a small letter is its capital
        h.letters = {k: v for k, v in h.letters.items() if not k.islower()}
        h.alias = {k.lower(): k for k in h.letters if k.isupper() and len(k.lower()) == 1 and k.lower() != k}
    h.letters = {k: h.letters[k] for k in sorted(h.letters)}
    return h


def has(h, ch):
    return ch in h.letters or ch in h.alias


_cache = {}


def __getattr__(name):                              # HANDS and BY_ID are built on first use
    if name in ("HANDS", "BY_ID"):
        if "HANDS" not in _cache:
            _cache["HANDS"] = [build(i) for i in ORDER]
            _cache["BY_ID"] = {h.id: h for h in _cache["HANDS"]}
        return _cache[name]
    raise AttributeError(name)
