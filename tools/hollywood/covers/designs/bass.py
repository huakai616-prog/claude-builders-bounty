"""bass: homage to Saul Bass - the Hollywood film-title poster in cut paper.

One idea: 「我的祖国和我，像海和浪花一朵」.  The black sea, cut from one sheet
of paper, rises into a single wave whose lip rolls over into a whirl
(「我就是笑的漩涡」, Bass's own Vertigo spiral) above a big open hollow.  Off
the lip flies one burst of cream spray led by a single larger drop - the
small 「我」, the only light shape on the vermilion field.  Three calm,
rocking scissor-cut strips cross the open sea (6/8: three swells to a
strip).  The title is set whole and solid - never cut (「一刻也不能分割」):
「我和我的」 in the cream of the spray, 「祖国」 in the vermilion of the field,
squared into one block.  Every edge of the art is cut with the same
scissors (short facets and the same small hand wobble), never ruled.
"""
import math
import random

import lib

U = 100  # SVG units per inch

VERMILION = "#D2462A"
BLACK = "#16130F"
CREAM = "#F2E8D5"
OCHRE = "#E2A23A"

# one pair of scissors for every edge on the page
FACET = (0.06, 0.16)   # facet length, inches
JIT = 0.0042           # per-vertex jitter, inches
SLOW = 0.0065          # slow hand wobble, inches


# ------------------------------------------------------------------ geometry
def catmull(pts, n=24, closed=False):
    """Dense Catmull-Rom curve through pts."""
    out = []
    P = list(pts)
    P = [P[-1]] + P + [P[0], P[1]] if closed else [P[0]] + P + [P[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                    + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                           for j in range(2)))
    if not closed:
        out.append(tuple(pts[-1]))
    return out


def resample(dense, rng, lo=FACET[0], hi=FACET[1]):
    """Pick vertices at irregular arc-length steps: scissor facets."""
    out = [dense[0]]
    acc, step = 0.0, rng.uniform(lo, hi)
    for a, b in zip(dense, dense[1:]):
        acc += math.dist(a, b)
        if acc >= step:
            out.append(b)
            acc, step = 0.0, rng.uniform(lo, hi)
    if out[-1] != dense[-1]:
        out.append(dense[-1])
    return out


def normals(pts, closed=False):
    n = len(pts)
    out = []
    for i in range(n):
        if closed:
            a, b = pts[i - 1], pts[(i + 1) % n]
        else:
            a, b = pts[max(0, i - 1)], pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1
        out.append((-dy / L, dx / L))
    return out


def wobble(pts, rng, amp=JIT, slow=SLOW, keep_ends=True, closed=False):
    """Offset each vertex along its normal: jitter + a slow hand wobble."""
    n = len(pts)
    ph1, ph2 = rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    out, s = [], 0.0
    for i, (p, (nx, ny)) in enumerate(zip(pts, normals(pts, closed))):
        if i:
            s += math.dist(pts[i - 1], p)
        off = (rng.gauss(0, amp) + slow * math.sin(s * 2.3 + ph1)
               + 0.5 * slow * math.sin(s * 5.9 + ph2))
        if keep_ends and not closed and i in (0, n - 1):
            off = 0
        out.append((p[0] + nx * off, p[1] + ny * off))
    return out


def scissor(dense, rng, scale=1.0, closed=False, keep_ends=True):
    """The one cut used everywhere; `scale` < 1 only for the small drops,
    so their facets and wobble stay in proportion."""
    pts = resample(dense, rng, FACET[0] * scale, FACET[1] * scale)
    if closed and len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
        pts = pts[:-1]
    return wobble(pts, rng, JIT * scale, SLOW * scale, keep_ends, closed)


def d(pts, close=True):
    s = "M" + " L".join(f"{x * U:.1f},{y * U:.1f}" for x, y in pts)
    return s + (" Z" if close else "")


# ------------------------------------------------------------------ the wave
# One flat black shape, no inner strands: the back rises out of the sea,
# the lip is a logarithmic spiral ribbon that rolls over, turns inward and
# tapers to a point inside a clean vermilion eye (the whirl, Bass's Vertigo
# spiral); the face drops steeply under it, leaving a big open hollow.
C = (7.05, 4.0)
TH0 = math.pi                      # start on the west side, roll clockwise
SWEEP = math.radians(408)
R0, W0, R_END = 2.58, 1.62, 0.50
SEA = 7.42                         # the open sea's surface
# the back: points from the open sea up to the west side of the lip
BACK = [(-0.6, 7.46), (0.7, 7.40), (1.85, 7.14), (2.7, 6.6), (3.25, 5.75)]
# the face: offsets from the inner west point of the lip down to the sea
FACE = [(-0.14, 0.88), (-0.08, 1.74), (0.28, 2.56), (1.05, 3.14), (2.30, 3.38)]


def K():
    return math.log(R0 / R_END) / SWEEP


def spiral_pt(th, f):
    """Point on the lip ribbon at angle th, fraction f from outer (0) to inner (1)."""
    t = min(1.0, max(0.0, (th - TH0) / SWEEP))
    r = R0 * math.exp(-K() * (th - TH0))
    w = W0 * (1 - t) ** 0.95
    rr = r + w / 2 - f * w
    return (C[0] + math.cos(th) * rr, C[1] + math.sin(th) * rr)


def wave_top(rng):
    """One continuous cut: the sea -> up the back -> over the lip -> into
    the whirl -> back out under the lip -> down the face -> the sea."""
    n = 96
    ths = [TH0 + SWEEP * i / n for i in range(n + 1)]
    outer = [spiral_pt(t, 0) for t in ths]
    inner = [spiral_pt(t, 1) for t in ths]
    i0 = inner[0]
    face = [(i0[0] + dx, i0[1] + dy) for dx, dy in FACE]
    face += [(face[-1][0] + 1.5, SEA - 0.02), (11.6, SEA + 0.02)]
    up = catmull(BACK + outer[:3], 16)[:-2 * 16] + outer
    down = list(reversed(inner)) + catmull(inner[1::-1] + face, 16)[16:]
    return scissor(up, rng) + scissor(down, rng)


def ellipse(cx, cy, r, ang, aspect=1.0, n=48):
    """A drop in flight: a circle stretched a little along its motion."""
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for k in range(n):
        t = 2 * math.pi * k / n
        x, y = r * aspect * math.cos(t), r / aspect ** 0.5 * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


# The burst: a cloud of spray thrown forward off the lip - dense and coarse
# at the lip, thinning and finer as it flies out in a widening cone.  One
# drop, clearly the largest, leads it: 「我」.  Drops never touch.
SPRAY_FROM = 298          # point on the lip (deg on the spiral)
SPRAY_DIR = -34           # centre of the cone (deg)
SPRAY_SEED = 3
SPRAY_N = 13
SPRAY_R = 0.105
LEAD = (-34, 1.05, 0.20)


def spray_drops():
    """(x, y, r, direction) of every drop, deterministic."""
    rs = random.Random(SPRAY_SEED)
    ox, oy = spiral_pt(math.radians(SPRAY_FROM), 0.0)

    def place(deg, dist):
        a = math.radians(deg)
        return ox + dist * math.cos(a), oy + dist * math.sin(a) + 0.07 * dist * dist
    deg, dist, r = LEAD
    lx, ly = place(deg, dist)
    drops = [(lx, ly, r)]
    tries = 0
    while len(drops) < SPRAY_N + 1 and tries < 5000:
        tries += 1
        u = rs.random()
        dist = 0.18 + 1.75 * u ** 1.25
        spread = 16 + 16 * dist
        deg = SPRAY_DIR + rs.uniform(-spread, spread)
        r = SPRAY_R * (1 - 0.62 * min(1, dist / 2.2)) * rs.uniform(0.6, 1.25)
        x, y = place(deg, dist)
        if all(math.dist((x, y), (a, b)) > r + rb + 0.07 for a, b, rb in drops):
            drops.append((x, y, r))
    return [(x, y, r, math.atan2(y - oy, x - ox)) for x, y, r in drops]


def spray(rng):
    shapes = []
    for x, y, r, dirn in spray_drops():
        q = ellipse(x, y, r, dirn, 1.12)
        q = scissor(q + [q[0]], rng, scale=min(1.0, r / 0.3), closed=True)
        shapes.append(f'<path d="{d(q)}" fill="{CREAM}"/>')
    return "".join(shapes)


# Three rocking cuts across the open sea (6/8: three swells to a strip).
# y, amplitude, phase, thickness, x from, x to, colour
PERIOD = 11.0 / 3
SEA_CUTS = [(8.28, 0.10, 0.6, 0.070, -0.6, 11.6, VERMILION),
            (8.92, 0.12, 2.2, 0.080, -0.6, 7.8, OCHRE),
            (9.52, 0.11, 4.1, 0.070, 3.6, 11.6, VERMILION)]


def strip(y0, amp, ph, th, x0, x1, rng):
    n = int((x1 - x0) / 0.05) + 1
    xs = [x0 + (x1 - x0) * i / (n - 1) for i in range(n)]
    up, lo = [], []
    for x in xs:
        y = (y0 + amp * math.sin(2 * math.pi * x / PERIOD + ph)
             + 0.12 * amp * math.sin(4 * math.pi * x / PERIOD + ph * 1.7))
        taper = min(1.0, (x - x0) / 2.2 if x0 > -0.3 else 1.0,
                    (x1 - x) / 2.2 if x1 < 11.3 else 1.0)
        t = th * (0.7 + 0.3 * math.sin(2 * math.pi * x / PERIOD + ph + 1.2))
        t *= max(0.0, taper) ** 0.8
        up.append((x, y - t / 2))
        lo.append((x, y + t / 2))
    return scissor(up, rng) + list(reversed(scissor(lo, rng)))


def art(rng):
    shapes = []
    sea = wave_top(rng) + [(11.6, 17.4), (-0.6, 17.4)]
    shapes.append(f'<path d="{d(sea)}" fill="{BLACK}"/>')
    for y0, amp, ph, th, x0, x1, fill in SEA_CUTS:
        shapes.append(f'<path d="{d(strip(y0, amp, ph, th, x0, x1, rng))}" fill="{fill}"/>')
    shapes.append(spray(rng))
    # a hand-cut vermilion rule over the specification strip
    y, h = 14.34, 0.03
    top_e = scissor([(0.85 + 9.3 * i / 60, y) for i in range(61)], rng, 0.5)
    bot_e = scissor([(0.85 + 9.3 * i / 60, y + h) for i in range(61)], rng, 0.5)
    shapes.append(f'<path d="{d(top_e + list(reversed(bot_e)))}" fill="{VERMILION}"/>')
    return "".join(shapes)


def tab(w, h, rng, fill):
    """A hand-cut paper label (same scissors)."""
    edge = [(0, 0), (w, 0), (w, h), (0, h), (0, 0)]
    dense = []
    for a, b in zip(edge, edge[1:]):
        for i in range(20):
            dense.append((a[0] + (b[0] - a[0]) * i / 20, a[1] + (b[1] - a[1]) * i / 20))
    dense.append(dense[0])
    pts = scissor(dense, rng, 0.6, closed=True)
    return (f'<svg width="{w}in" height="{h}in" viewBox="0 0 {w * U} {h * U}" '
            f'style="position:absolute;left:0;top:0;overflow:visible">'
            f'<path d="{d(pts)}" fill="{fill}"/></svg>')


# ------------------------------------------------------------------ page
SANS = "'Noto Sans CJK SC', sans-serif"
CR = "rgba(242,232,213,.20)"   # cream hairline on black
CSS = f"""
.page {{ background: {VERMILION}; color: {CREAM}; }}
svg.art {{ position: absolute; left: 0; top: 0; width: 11in; height: 17in; }}
.t {{ position: absolute; white-space: nowrap; }}
.osw {{ font-family: 'Oswald', {SANS}; text-transform: uppercase; }}
.top1 {{ left: .85in; top: .545in; font-size: 17pt; font-weight: 600; letter-spacing: .34em;
        color: {BLACK}; }}
.top2 {{ left: .85in; top: .945in; font-size: 8.6pt; font-weight: 500; letter-spacing: .3em;
        color: {BLACK}; }}
.tag {{ left: .86in; top: 1.72in; writing-mode: vertical-rl; font-family: {SANS};
       font-weight: 700; font-size: 12.5pt; letter-spacing: .42em; color: {BLACK}; }}
.title {{ left: .8in; top: 10.205in; font-family: {SANS}; font-weight: 900; line-height: 1; }}
.title .s {{ font-size: 81.5pt; letter-spacing: .003em; display: block; color: {CREAM}; }}
.title .b {{ font-size: 172pt; letter-spacing: -.035em; display: block; margin-top: -.04in;
            color: {VERMILION}; margin-left: -.03in; }}
.title i {{ font-style: normal; display: inline-block; }}
.side {{ left: 6.4in; top: 10.24in; width: 3.75in; }}
.pin {{ font-family: 'Oswald', {SANS}; font-weight: 600; font-size: 17pt;
       letter-spacing: .16em; color: {OCHRE}; text-transform: uppercase; }}
.sub {{ font-family: {SANS}; font-weight: 500; font-size: 11.8pt; margin-top: .16in;
       letter-spacing: .03em; }}
.suben {{ font-family: 'Oswald', {SANS}; font-weight: 400; font-size: 8pt; margin-top: .09in;
         line-height: 1.6; letter-spacing: .14em; color: #D9CDB8; text-transform: uppercase; }}
.credits {{ left: 6.4in; top: 11.93in; width: 3.75in; }}
.credits .row {{ display: flex; align-items: baseline; justify-content: space-between;
                border-top: 1px solid {CR}; padding: .05in 0 .04in; }}
.credits .row:first-child {{ border-top: 0; }}
.credits .zh {{ font-family: {SANS}; font-weight: 700; font-size: 9.5pt; color: {VERMILION};
               letter-spacing: .1em; }}
.credits .en {{ font-family: 'Oswald', {SANS}; font-weight: 500; font-size: 6.8pt; color: {VERMILION};
               letter-spacing: .2em; text-transform: uppercase; margin-left: .1in; }}
.credits .n {{ font-family: {SANS}; font-weight: 700; font-size: 14pt; letter-spacing: .06em; }}
.spec {{ left: .85in; top: 14.56in; width: 9.3in; display: grid;
        grid-template-columns: 2.0in 1.8in 1.75in 1fr; }}
.spec .k {{ font-family: 'Oswald', {SANS}; font-weight: 500; font-size: 7.2pt; letter-spacing: .24em;
           color: {VERMILION}; text-transform: uppercase; }}
.spec .v {{ font-family: 'Oswald', {SANS}; font-weight: 400; font-size: 11pt; letter-spacing: .05em;
           margin-top: .05in; line-height: 1.35; }}
.spec .v span[style*="DejaVu"] {{ font-size: 1.12em !important; position: relative; top: -.04em; }}
.spec .v .z {{ font-family: {SANS}; font-weight: 500; font-size: 9.6pt; letter-spacing: .06em; }}
.sig {{ left: .85in; top: 15.92in; height: .44in; }}
.sig .tab {{ position: relative; display: inline-block; height: .44in; width: 1.92in; }}
.sig .tab .n {{ position: absolute; left: 0; top: 0; width: 1.92in; line-height: .44in;
              text-align: center; font-family: {SANS}; font-weight: 900; font-size: 14pt;
              letter-spacing: .3em; padding-left: .3em; color: {CREAM}; }}
.sig .e {{ position: absolute; left: 2.18in; top: .13in; font-size: 8.4pt; font-weight: 400;
          letter-spacing: .3em; }}
"""

TAGLINE = True


def render(m):
    rng = random.Random(1958)  # Vertigo
    e, sym = lib.e, lib.sym
    svg = (f'<svg class="art" viewBox="0 0 {11 * U} {17 * U}" '
           f'xmlns="http://www.w3.org/2000/svg">{art(rng)}</svg>')
    title = m["title"]
    small, big = title[:-2], title[-2:]
    # 「我和我的」 rocks lightly (6/8); 「祖国」 stands level and whole
    rots = [-0.7, 0.5, -0.5, 0.7]
    dys = [0.012, -0.015, 0.008, -0.01]
    chars = [f'<i style="transform:rotate({r}deg) translateY({dy}in)">{e(ch)}</i>'
             for ch, r, dy in zip(small, rots, dys)]
    credits = "".join(
        f'<div class="row"><span><span class="zh">{e(zh)}</span><span class="en">{e(en)}</span></span>'
        f'<span class="n">{e(n)}</span></div>' for zh, en, n in lib.credit_rows(m))
    sub_en = e(m["subtitle_en"]).replace(" — ", " —<br>", 1)
    inst = "<br>".join(f'{e(en)} <span class="z">{e(zh)}</span>' for en, zh in m["instrumentation"])
    tempo = sym(m["tempo"]) + (f'　{e(m["tempo_text"])}' if m.get("tempo_text") else "")
    tag = (f'<div class="t tag">我的祖国和我　像海和浪花一朵</div>' if TAGLINE else "")
    body = f"""{svg}
<div class="t osw top1">Full Score</div>
<div class="t osw top2">Score in C · Concert Pitch</div>
{tag}
<div class="t title"><span class="s">{"".join(chars)}</span><span class="b">{e(big)}</span></div>
<div class="t side">
  <div class="pin">{e(m['title_latin'])}</div>
  <div class="sub"><span style="margin-left:-.5em">《</span>{e(title)}》{e(m['subtitle'])}</div>
  <div class="suben">{sub_en}</div>
</div>
<div class="t credits">{credits}</div>

<div class="t spec">
  <div><div class="k">Key</div><div class="v">{sym(m['key'])}</div></div>
  <div><div class="k">Tempo</div><div class="v">{tempo}</div></div>
  <div><div class="k">Duration</div><div class="v">{sym(m['duration'])}</div></div>
  <div><div class="k">Instrumentation</div><div class="v">{inst}</div></div>
</div>
<div class="t sig"><span class="tab">{tab(1.92, .44, rng, VERMILION)}<span class="n">{e(m['arranger'])}</span></span><span class="t osw e">Arrangement &amp; Music Preparation · {e(m['year'])}</span></div>
"""
    return lib.page(CSS, body, "bass")
