"""kan: homage to Kan Tai-keung (靳埭强) - ink spirit x modernist geometry.

A round window (圆窗) onto dawn sky and sea, crossed by one dry-brush
stroke that is the horizon and, where it rises and curls, one breaking
wave-spray: 「我的祖国和我，像海和浪花一朵」 - the sea is 祖国, the spray is 我.

Grid (inches): left margin 0.85 = the window's left edge and the first
info column; the window's centre 3.55 and right edge 6.25 bound the credits
(and the header/foot captions sit on 3.55); the ink of 祖 starts on 6.75,
the third info column; right margin 10.15 = the vertical epigraph's right
edge.  All info lines share one baseline grid (ROW); the seal's foot sits on
the foot of 国, its right edge on 6.75; the epigraph runs from the horizon
down beside the sea.
"""
import math
import random

import lib

U = 100  # SVG user units per inch

# ---------------------------------------------------------------- grid
ML, MR = 0.85, 10.15          # margins
R = 2.70                      # window radius
CX, CY = ML + R, 9.65         # window centre (CY = the horizon)
TCOL = 6.75                   # title column / third info column
ROW = 0.31                    # info row pitch
INFO_TOP = 13.05              # top rule of the information block
HEAD_Y = 0.92                 # header baseline
FOOT_Y = 16.12                # foot baseline
SEAL = 0.86                   # seal size
GUO_FOOT = 6.99               # foot of the calligraphic 国 (measured from the render)
BASE = 14.18                  # baseline offset of a .ln box, pt: (1.007-0.298)/2*40


# ---------------------------------------------------------------- helpers
def sstep(a, b, x):
    if b == a:
        return 0.0 if x < a else 1.0
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


class Noise:
    """Smooth 1-D value noise in [0, 1]."""

    def __init__(self, rng, n=512):
        self.v = [rng.random() for _ in range(n)]
        self.n = n

    def __call__(self, x):
        i = math.floor(x)
        f = x - i
        a, b = self.v[i % self.n], self.v[(i + 1) % self.n]
        return a + (b - a) * f * f * (3 - 2 * f)


class Noise2:
    """Smooth 2-D value noise in [0, 1] (scale the axes to make it
    anisotropic: long along the stroke, short across it = streaks)."""

    def __init__(self, rng, n=97):
        self.n = n
        self.v = [rng.random() for _ in range(n * n)]

    def __call__(self, x, y):
        n = self.n
        xi, yi = math.floor(x), math.floor(y)
        fx, fy = x - xi, y - yi
        sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        x0, x1, y0, y1 = xi % n, (xi + 1) % n, yi % n, (yi + 1) % n
        v = self.v
        a = v[x0 * n + y0] + (v[x1 * n + y0] - v[x0 * n + y0]) * sx
        b = v[x0 * n + y1] + (v[x1 * n + y1] - v[x0 * n + y1]) * sx
        return a + (b - a) * sy


def keys(kf):
    """Smooth piecewise curve through keyframes [(s, value)]."""
    def f(s):
        for (s0, v0), (s1, v1) in zip(kf, kf[1:]):
            if s <= s1:
                return lerp(v0, v1, sstep(s0, s1, s))
        return kf[-1][1]
    return f


def bez(p0, p1, p2, p3, t):
    mt = 1 - t
    return (mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
            mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1])


def spine(segs, step):
    """Cubic chain -> points every `step` units of arc length, with unit
    normals; returns [(x, y, nx, ny)], total length."""
    dense = []
    for sg in segs:
        for k in range(500):
            dense.append(bez(*sg, k / 500))
    dense.append(segs[-1][3])
    cum = [0.0]
    for a, b in zip(dense, dense[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    L = cum[-1]
    m = int(L / step) + 1
    out, j = [], 0
    for k in range(m):
        d = L * k / (m - 1)
        while j < len(cum) - 2 and cum[j + 1] < d:
            j += 1
        f = (d - cum[j]) / max(1e-9, cum[j + 1] - cum[j])
        out.append((lerp(dense[j][0], dense[j + 1][0], f), lerp(dense[j][1], dense[j + 1][1], f)))
    pts = []
    for k, (x, y) in enumerate(out):
        a = out[max(0, k - 2)]
        b = out[min(m - 1, k + 2)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, ty) or 1
        pts.append((x, y, -ty / ln, tx / ln))
    return pts, L


def fmt(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def poly(points):
    return "M" + " ".join(f"{fmt(x)},{fmt(y)}" for x, y in points) + "Z"


# ---------------------------------------------------------------- the brush
def brush_stroke(segs, width, dry, seed=7, n=230, step=2.4, ink="#141210",
                 splay=None, tail=(0.95, 1.0), clump=0.6, n_clumps=15, side=0.0):
    """A dry-brush (飞白) stroke as vector bristle ribbons.

    width(s) -> stroke width (units) along arc length s in [0, 1]
    dry(s)   -> dryness 0 (wet, solid ink) .. 1 (almost no ink)
    splay(s) -> how far the bristles fan apart (1 = together)
    tail     -> the bristles run out at staggered points in this range
    side     -> > 0 dries the left-hand side of the stroke first (the
                brush is tilted, its belly holds the ink on the other side)

    Ink is deposited where an anisotropic noise field (long streaks along
    the stroke, narrow across it, plus a fine per-bristle grain) beats the
    dryness: wet passages are solid, dry ones open into streaks of paper
    whose ends break up into dashes, and the outer bristles dry first so
    the contour is ragged.  Every ribbon edge is jittered.
    """
    rng = random.Random(seed)
    pts, L = spine(segs, step)
    m = len(pts)
    splay = splay or (lambda s: 1.0)
    streak = Noise2(rng)        # wide channels
    fine = Noise2(rng)          # narrow streaks
    contour = Noise(rng)
    centres = sorted(-0.5 + (j + 0.5 + rng.uniform(-0.35, 0.35)) / n_clumps
                     for j in range(n_clumps))
    us = [-0.5 + (i + rng.uniform(0.1, 0.9)) / n for i in range(n)]
    paths = []
    for u in us:
        cc = min(centres, key=lambda c: abs(c - u))
        own = Noise(rng)
        wob = Noise(rng)
        half = rng.uniform(0.6, 1.3) / n * 1.2        # cross half-width (norm.)
        s_end = rng.uniform(*tail)
        ph = rng.uniform(0, 400)
        load = rng.uniform(-0.06, 0.06)               # some bristles hold more ink
        edge = abs(u) * 2
        on = []
        for k in range(m):
            s = k / (m - 1)
            if s > s_end:
                on.append(False)
                continue
            d = dry(s)
            dist = s * L
            go = 0.14 + 0.30 * edge ** 2 * min(1.0, d * 2.5)
            v = ((0.50 * streak(u * 11 + 3, dist / 260)
                  + 0.36 * fine(u * 42 + 7, dist / 75)) * (1 - go) / 0.86
                 + go * own(ph + dist / 6))
            thr = d + 0.42 * edge ** 4 * (0.4 + d) - load - side * u * min(1.0, d * 3)
            on.append(v > thr)
        k = 0
        while k < m:
            if not on[k]:
                k += 1
                continue
            k0 = k
            while k < m and on[k]:
                k += 1
            k1 = k - 1
            if k1 - k0 < 2 + int(5 * edge ** 3):
                continue
            left, right = [], []
            nt0 = rng.randint(2, 7)
            nt1 = rng.randint(2, 9)
            if (k1 + 1) / (m - 1) > s_end - 0.004:     # the bristle's last run: 出锋
                nt1 = rng.randint(12, 26)
            for kk in range(k0, k1 + 1):
                s = kk / (m - 1)
                x, y, nx, ny = pts[kk]
                w = width(s) * (0.95 + 0.10 * contour(s * L / 140))
                a = 1.0 if k0 == 0 else min(1.0, (kk - k0 + 0.6) / nt0)
                b = min(1.0, (k1 - kk + 0.6) / nt1) if k1 < m - 1 else 1.0
                tap = min(a, b) ** 0.8
                pull = clump * sstep(0.2, 0.75, dry(s))
                uc = u + (cc - u) * pull
                uu = uc * splay(s) + (wob(ph + s * 9) - 0.5) * (0.02 + 0.05 * dry(s)) * splay(s)
                hh = half * tap
                j1 = (rng.random() - 0.5) * 0.9 * half
                j2 = (rng.random() - 0.5) * 0.9 * half
                left.append((x + nx * w * (uu - hh + j1), y + ny * w * (uu - hh + j1)))
                right.append((x + nx * w * (uu + hh + j2), y + ny * w * (uu + hh + j2)))
            dd = dry((k0 + k1) / 2 / (m - 1))
            op = 1.0 if dd < 0.16 else rng.choice((0.72, 0.82, 0.9, 0.96, 1.0))
            paths.append((poly(left + right[::-1]), op))
    by = {}
    for p, o in paths:
        by.setdefault(o, []).append(p)
    return (f'<g fill="{ink}">'
            + "".join(f'<path fill-opacity="{o}" d="{" ".join(ps)}"/>' for o, ps in by.items())
            + "</g>"), pts


def blob(rng, x, y, r, ang, stretch, n=28):
    """An ink droplet: round-ish with a wobbling rim, a little drawn out
    along its flight `ang` (blunt head leading, the tail side thinner)."""
    ph = [rng.uniform(0, 6.28) for _ in range(5)]
    amp = [0.07, 0.05, 0.035, 0.025, 0.02]
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        rr = r * (1 + sum(am * math.sin((h + 2) * a + p) for h, (am, p) in enumerate(zip(amp, ph))))
        ex = rr * stretch * math.cos(a)
        ey = rr * math.sin(a) * (1 - 0.22 * max(0.0, -math.cos(a)))
        out.append((x + ex * math.cos(ang) - ey * math.sin(ang),
                    y + ex * math.sin(ang) + ey * math.cos(ang)))
    return poly(out)


def spray(seed, tips, mist=7):
    """Droplets flung off the bristle tails, each stream continuing one
    tail's direction (笔断意连) so brush and spray are one gesture:
    tips = [(x, y, angle, gaps, radii)]; the drops fly further apart and
    smaller; big drops shed a satellite or two; plus a mist of specks."""
    rng = random.Random(seed)
    out, placed = [], []
    for x, y, a, gaps, radii in tips:
        for g, rr in zip(gaps, radii):
            g *= rng.uniform(0.85, 1.15)
            a += rng.uniform(-0.03, 0.04)
            x += g * math.cos(a)
            y += g * math.sin(a)
            rr *= rng.uniform(0.85, 1.12)
            out.append(blob(rng, x, y, rr, a, rng.uniform(1.0, 1.18)))
            placed.append((x, y, rr, a))
            for _ in range(int(rr > 3.0) + int(rr > 5.5)):
                sa = a + rng.uniform(-2.2, 2.2)
                sd = rr * rng.uniform(1.5, 2.2)
                out.append(blob(rng, x + sd * math.cos(sa), y + sd * math.sin(sa),
                                rng.uniform(0.35, 0.7), sa, 1.1, 12))
    for _ in range(mist):
        px, py, pr, pa = rng.choice(placed[:-1])
        off = rng.uniform(-1, 1) * 7
        fw = rng.uniform(-3, 9)
        out.append(blob(rng, px + fw * math.cos(pa) - off * math.sin(pa),
                        py + fw * math.sin(pa) + off * math.cos(pa),
                        rng.uniform(0.4, 0.8), pa, rng.uniform(1.0, 1.3), 12))
    return "".join(f'<path d="{p}"/>' for p in out)


# ---------------------------------------------------------------- the seal
def seal(m, size, pad=0.10, gap=0.06, cgap=0.035, fill=1.0):
    """白文 seal, cut in cinnabar: the arranger's name carved out in paper
    colour, read right to left - right column 花开当, left column 富贵
    (the two characters drawn tall to fill their column, as seal cutters
    do), inside a solid red border.  The block has worn edges and nicks."""
    nm = m["arranger"]
    k = (len(nm) + 1) // 2
    cols = [nm[:k], nm[k:]]
    S = size * 72                       # pt
    P, G, CG = S * pad, S * gap, S * cgap
    cw = (S - 2 * P - G) / 2            # column width, pt
    ch_ = S - 2 * P                     # column height, pt
    spans = []
    for ci, txt in enumerate(cols):
        nn = max(1, len(txt))
        cell = (ch_ - CG * (nn - 1)) / nn
        fs = cw * fill
        sy = cell / fs * 1.06
        x = S - P - cw - ci * (cw + G)
        for j, c in enumerate(txt):
            spans.append(
                f"<b style='left:{x:.2f}pt;top:{P + j * (cell + CG):.2f}pt;width:{cw:.2f}pt;"
                f"height:{cell:.2f}pt;font-size:{fs:.2f}pt;line-height:{cell:.2f}pt'>"
                f"<i style='transform:scale(1,{sy:.3f})'>{lib.e(c)}</i></b>")
    rng = random.Random(5)
    pts = []
    for side in range(4):
        for kk in range(18):
            t = kk / 18
            j = rng.uniform(-0.55, 0.55)
            pts.append([(t * 100, j), (100 + j, t * 100), (100 - t * 100, 100 + j),
                        (j, 100 - t * 100)][side])
    nicks = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr:.2f}" fill="{PAPER}"/>'
        for x, y, rr in [(rng.uniform(6, 94), rng.choice((0.2, 99.8)), rng.uniform(0.7, 1.5))
                         for _ in range(3)]
        + [(rng.choice((0.2, 99.8)), rng.uniform(6, 94), rng.uniform(0.6, 1.2))
           for _ in range(2)])
    specks = "".join(
        f'<circle cx="{rng.uniform(4, 96):.1f}" cy="{rng.uniform(4, 96):.1f}" '
        f'r="{rng.uniform(0.25, 0.6):.2f}" fill="{PAPER}" fill-opacity=".8"/>'
        for _ in range(3))
    bg = (f'<svg class="sealbg" viewBox="-1 -1 102 102" preserveAspectRatio="none">'
          f'<path d="{poly(pts)}" fill="{CINNABAR}"/>{nicks}{specks}</svg>')
    return (f"<div class='seal' style='width:{size}in;height:{size}in'>{bg}"
            f"{''.join(spans)}</div>")


# ---------------------------------------------------------------- render
# one short lyric line (张藜) set as a quiet epigraph beside the spray
EPIGRAPH = {"我和我的祖国": "我的祖国和我 像海和浪花一朵"}

PAPER = lib.PAPER
INK = "#141210"
INK2 = "#3E372F"        # warm ink for small type (lib.INK)
GREY = "#8C8378"
RULE = "#D3C9BA"
BLUE = "#2E5B7A"        # mineral blue 石青
CINNABAR = lib.CINNABAR
SERIF = "'EB Garamond', 'Noto Serif CJK SC', serif"
CJK = "'Noto Serif CJK SC', 'EB Garamond', serif"


def music(s):
    """lib.sym() (♭ ♩ from DejaVu Sans), sized and raised to sit with the
    Garamond (see .mus in the CSS)."""
    return f"<span class='mus'>{lib.sym(s)}</span>"


def balanced(s):
    """Two balanced lines, never breaking inside parentheses."""
    words = s.split(" ")
    best, depth = None, 0
    for i in range(1, len(words)):
        depth += words[i - 1].count("(") - words[i - 1].count(")")
        if depth:
            continue
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best[0]:
            best = (score, a, b)
    return [lib.e(best[1]), lib.e(best[2])] if best else [lib.e(s)]


def render(m):
    # ---- the image: the round window (geometry) + one brush stroke (ink)
    cx, cy, r = CX * U, CY * U, R * U
    H = cy
    segs = [
        ((-90, H + 16), (160, H + 10), (400, H + 4), (575, H - 2)),
        ((575, H - 2), (660, H - 5), (716, H - 20), (760, H - 58)),
        ((760, H - 56), (800, H - 88), (818, H - 142), (852, H - 178)),
        ((852, H - 178), (876, H - 218), (938, H - 236), (966, H - 184)),
    ]
    # pressure and dryness along the gesture: a loaded start beyond the
    # page, a fast dry pass across the window (the sky and sea show through
    # the 飞白), a press (顿) before the rise, then the dry, splitting flick
    width = keys([(0, 128), (0.2, 124), (0.4, 112), (0.53, 106), (0.6, 124),
                  (0.68, 112), (0.82, 82), (0.92, 56), (1.0, 30)])
    dry = keys([(0, 0.05), (0.12, 0.06), (0.24, 0.24), (0.33, 0.36), (0.47, 0.38),
                (0.56, 0.18), (0.62, 0.14), (0.72, 0.32), (0.82, 0.40), (0.88, 0.30),
                (1.0, 0.56)])

    def splay(s):
        return 1 + 0.22 * sstep(0.8, 0.95, s)

    stroke, pts = brush_stroke(segs, width, dry, splay=splay, tail=(0.93, 1.0), ink=INK,
                               clump=0.8, n_clumps=13, side=0.32)
    # the spray leaves where the crest turns over (its highest point), flung
    # off the outer edge along the tangent there, while the brush curls on
    ktop = min(range(len(pts) * 3 // 4, len(pts)), key=lambda k: pts[k][1])
    tx, ty, nx, ny = pts[ktop]
    st = ktop / (len(pts) - 1)
    wt = width(st) * splay(st)
    ox, oy = tx - nx * wt * 0.42, ty - ny * wt * 0.42
    ang = math.atan2(-nx, ny)        # tangent at the crest (pointing right)
    tips = [(ox + dx, oy + dy, ang + da, gs, rs)
            for dx, dy, da, gs, rs in [
                (-12, 5, -0.66, [15, 20, 25], [3.6, 2.3, 1.3]),
                (0, 0, -0.36, [17, 22, 27, 32], [6.4, 4.2, 2.6, 1.5]),
                (10, 5, -0.08, [16, 21], [3.3, 1.8])]]
    drops = spray(11, tips, mist=7)

    sea = (f'<linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="#6F98A6"/><stop offset=".22" stop-color="#3F7088"/>'
           f'<stop offset=".7" stop-color="#22506E"/><stop offset="1" stop-color="#163450"/>'
           f'</linearGradient>'
           f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
           f'<stop offset="0" stop-color="#B9CACB"/><stop offset=".45" stop-color="#D9D8C6"/>'
           f'<stop offset=".82" stop-color="#EDD8AE"/><stop offset="1" stop-color="#F1CF97"/>'
           f'</linearGradient>')
    win = (f'<path d="M{cx - r},{cy} A{r},{r} 0 0 1 {cx + r},{cy} Z" fill="url(#sky)"/>'
           f'<path d="M{cx - r},{cy} A{r},{r} 0 0 0 {cx + r},{cy} Z" fill="url(#sea)"/>')
    # 碧浪清波: swells in the window, in groups of three like the 6/8 bars
    clip = f'<clipPath id="win"><circle cx="{cx}" cy="{cy}" r="{r - 0.5}"/></clipPath>'
    rng = random.Random(3)
    sw = []
    for g, (y0, a) in enumerate([(cy + 70, .34), (cy + 122, .27), (cy + 190, .20)]):
        ph = rng.uniform(0, 6.28)            # one swell = three parallel lines
        amp = 1.4 + g * 0.8
        for j in range(3):
            yy = y0 + j * (6 + g * 1.5)
            d = "M" + " ".join(
                f"{fmt(x)},{fmt(yy + amp * math.sin(x / (38 + g * 10) + ph + j * 0.12))}"
                for x in range(int(cx - r), int(cx + r) + 1, 6))
            sw.append(f'<path d="{d}" fill="none" stroke="#CFE0E2" '
                      f'stroke-opacity="{a * (1 - 0.18 * j):.2f}" stroke-width="0.7"/>')
    rim = (f'<circle cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="{INK2}" '
           f'stroke-width="0.45"/>')
    svg = (f'<svg class="art" viewBox="0 0 1100 1700" width="11in" height="17in">'
           f'<defs>{sea}{clip}</defs>{win}<g clip-path="url(#win)">{"".join(sw)}</g>{rim}'
           f'{stroke}<g fill="{INK}">{drops}</g></svg>')

    # ---- type
    t = m["title"]
    lyric = m.get("epigraph") or EPIGRAPH.get(t, "")
    cut = max(0, len(t) - 2)          # the last two characters set monumental
    small = "".join(f"<span>{lib.e(c)}</span>" for c in t[:cut])
    big = "".join(f"<span>{lib.e(c)}</span>" for c in t[cut:])

    # the information block: three columns on one baseline grid (pitch ROW)
    # - col 1 on the window's left edge, col 2 from the window's centre to
    # its right edge, col 3 on the title column, ending on the right margin
    # with the epigraph
    b0 = INFO_TOP + 0.40              # first baseline (in)
    lines = []

    def ln(x, row, html, cls, w=None, right=False):
        y = b0 + row * ROW
        pos = (f"right:{11 - x:.3f}in" if right else f"left:{x:.3f}in")
        ww = f";width:{w:.3f}in" if w else ""
        lines.append(f"<div class='ln' style='{pos};top:calc({y:.3f}in - {BASE}pt){ww}'>"
                     f"<span class='{cls}'>{html}</span></div>")

    ln(ML, 0, lib.e(t), "t")
    ln(ML, 1, lib.e(m["title_latin"]), "py")
    ln(ML, 2, lib.e(m["subtitle"]), "sub")
    for i, part in enumerate(balanced(m["subtitle_en"])):
        ln(ML, 3 + i, part, "suben")
    credits = lib.credit_rows(m)
    for i, (zh, en, nm) in enumerate(credits):
        ln(CX, i, lib.e(zh), "zh")
        ln(CX + 0.44, i, lib.e(en), "en")
        ln(CX + R, i, lib.e(nm), "nm", right=True)
    specs = [("调性", "Key", music(m["key"])),
             ("速度", "Tempo", music(m["tempo"])),
             ("时长", "Duration", music(m["duration"]))]
    for i, (en, zh) in enumerate(m["instrumentation"]):
        specs.append(("编制" if i == 0 else "", "Scoring" if i == 0 else "",
                      f"{lib.e(en)}<i>{lib.e(zh)}</i>"))
    for i, (zh, en, v) in enumerate(specs):
        if zh:
            ln(TCOL, i, zh, "zh")
            ln(TCOL + 0.44, i, lib.e(en), "en")
        ln(MR, i, v, "val", right=True)
    rules = "".join(
        f"<div class='hr' style='left:{x0}in;width:{x1 - x0:.3f}in;"
        f"top:calc({b0 + i * ROW:.3f}in + 7.5pt)'></div>"
        for x0, x1, n in [(CX, CX + R, len(credits)), (TCOL, MR, len(specs))]
        for i in range(n))

    body = f"""
{svg}
<div class='ln' style='left:{ML}in;top:calc({HEAD_Y}in - {BASE}pt)'><span class='fs'>FULL SCORE</span></div>
<div class='ln' style='left:{CX}in;top:calc({HEAD_Y}in - {BASE}pt)'><span class='sic'>Score in C · Concert Pitch</span></div>
<div class='col'>
  <div class='small'>{small}</div>
  <div class='cal'>{big}</div>
</div>
<div class='sealpos'>{seal(m, SEAL, pad=.12, gap=.07, cgap=.05, fill=.96)}</div>
{f"<div class='lyric'>{lib.e(lyric)}</div>" if lyric else ""}
<div class='rule'></div>
{rules}
{"".join(lines)}
<div class='ln' style='left:{ML}in;top:calc({FOOT_Y}in - {BASE}pt)'><span class='signm'>{lib.e(m["arranger"])}</span></div>
<div class='ln' style='left:{CX}in;top:calc({FOOT_Y}in - {BASE}pt)'><span class='sigcap'>Arrangement &amp; Music Preparation · {lib.e(m["year"])}</span></div>
"""
    css = f"""
.page {{ background: {PAPER}; color: {INK2}; font-family: {SERIF}; }}
.art {{ position:absolute; left:0; top:0; }}
/* every text line is anchored by its baseline: a 40pt EB Garamond strut with
   zero line height puts the baseline {BASE}pt below the box top */
.ln {{ position:absolute; font: 400 40pt/0 'EB Garamond'; white-space:nowrap; }}
.ln * , .ln {{ line-height:0 !important; }}
.mus span {{ font-size:1.04em !important; position:relative; top:-.07em; margin-left:.01em; }}
.fs {{ font: 500 11.5pt/0 {SERIF}; letter-spacing:.42em; color:{INK}; }}
.sic {{ font: 500 7pt/0 {SERIF}; letter-spacing:.3em; text-transform:uppercase; color:{INK2}; }}
.col {{ position:absolute; left:{TCOL - 0.19}in; top:0.79in; width:2.55in; display:flex; flex-direction:column; align-items:center; }}
.small {{ display:flex; flex-direction:column; align-items:center; font: 500 21pt {CJK}; color:{INK}; line-height:1; gap:11pt; }}
.cal {{ display:flex; flex-direction:column; align-items:center; font-family:'Ma Shan Zheng'; font-size:2.3in; line-height:1.0; color:{INK}; margin-top:0.10in; }}
.sealpos {{ position:absolute; left:{TCOL - SEAL}in; top:{GUO_FOOT - SEAL}in; }}
.seal {{ position:relative; }}
.sealbg {{ position:absolute; left:0; top:0; width:100%; height:100%; }}
.seal b {{ position:absolute; display:flex; align-items:center; justify-content:center; overflow:visible; }}
.seal i {{ font-style:normal; font-weight:900; font-family:'Noto Serif CJK SC'; color:{PAPER}; display:block; line-height:1; }}
.lyric {{ position:absolute; right:{11 - MR}in; top:{CY}in; writing-mode:vertical-rl; font: 400 9.5pt {CJK}; letter-spacing:.5em; color:{BLUE}; }}
.rule {{ position:absolute; left:{ML}in; width:{MR - ML}in; top:{INFO_TOP}in; border-top:0.6pt solid {INK}; }}
.hr {{ position:absolute; border-top:0.35pt solid {RULE}; }}
.t {{ font: 600 17pt/0 {CJK}; letter-spacing:.16em; color:{INK}; }}
.py {{ font: italic 400 10.5pt/0 {SERIF}; letter-spacing:.03em; color:{INK2}; }}
.sub {{ font: 400 8.6pt/0 {CJK}; letter-spacing:.06em; color:{INK2}; }}
.suben {{ font: italic 400 9.2pt/0 {SERIF}; color:{INK2}; }}
.zh {{ font: 400 8.6pt/0 {CJK}; color:{INK2}; }}
.en {{ font: 500 6.2pt/0 {SERIF}; letter-spacing:.2em; text-transform:uppercase; color:{GREY}; }}
.nm {{ font: 600 10pt/0 {CJK}; color:{INK}; letter-spacing:.08em; margin-right:-.08em; }}
.val {{ font: 400 10pt/0 {SERIF}; color:{INK}; }}
.val i {{ font: normal 400 8.4pt/0 {CJK}; color:{INK2}; margin-left:5pt; }}
.signm {{ font: 600 12pt/0 {CJK}; letter-spacing:.34em; color:{INK}; }}
.sigcap {{ font: 500 6.6pt/0 {SERIF}; letter-spacing:.26em; text-transform:uppercase; color:{GREY}; }}
"""
    return lib.page(css, body, "kan")
