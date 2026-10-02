"""kandinsky: homage to Wassily Kandinsky (Composition VIII, 1923; Several
Circles, 1926) - painting as visual music.

One idea: 「我的祖国和我，像海和浪花一朵」 as Kandinsky's two poles.  Upper left,
where Composition VIII keeps its great dark circle, the sea: one deep-blue
circle (the cello, the motherland) in a violet corona.  Upper right, one small
bright yellow circle (the soprano, 我, the spray) in its own glow, tied to the
sea by one taut line (一刻也不能分割).  Everything else is the score sounding
as colour, after Kandinsky's colour-sound correspondences ("Concerning the
Spiritual in Art", 1911):

  S  soprano   lemon yellow   yellow = the high, bright, ringing tone
  A  alto      light blue     light blue = the flute
  T  tenor     vermilion      warm red = strength, the trumpet's ring
  B  bass      violet         violet = the deep woodwinds (bassoon)
  Vn I         green          green = the calm middle of the violin
  Vn II        yellow-green   (the second violin, a lighter green)
  Va  viola    orange         orange = "a viola singing a largo"
  Vc  cello    deep blue      deep blue = the cello

Only the eight performers carry colour; every other mark is ink or a pale
neutral plane, so the colour key stays legible.  Women = small light circles
around the spray; men = deep forms below (the bass's bowl, the tenor's
square); the viola's long wedge rises toward the spray (the viola sings the
theme first); the violins' whirl (漩涡) is a nest of eccentric rings crossed
by four strings, Vn II's circle slipping out of Vn I's; the 6/8 is a
checkerboard of strong and weak quavers and one wave line of two swells (one
6/8 bar) with the cello's pizzicato heartbeat (脉搏) riding it as points,
strong-weak-weak.  All glows are vector radial gradients (no raster
blur).  Type: Noto Sans CJK SC + Jost (Futura-like); the pinyin is in Inter
because Jost lacks the tone marks.
"""
import math

import lib

# ------------------------------------------------------------------ palette
GROUND = "#F4ECDE"
LIGHT = "#FBF7EF"
BLACK = "#1C1916"
INK = "#3E372F"
MUTED = "#887D6E"
HAIR = "#CDBFAA"
COL = {
    "S": "#EEC23A",
    "A": "#86B1D6",
    "T": "#BE3F27",
    "B": "#5B4689",
    "Vn I": "#2D7A57",
    "Vn II": "#A9B94C",
    "Va": "#E2832E",
    "Vc": "#1F3B78",
}


def f(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")


def circle(cx, cy, r, fill="none", stroke=None, sw=0, extra=""):
    s = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ""
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"{s} {extra}/>'


def line(x0, y0, x1, y1, sw, col=BLACK, extra=""):
    return (f'<line x1="{f(x0)}" y1="{f(y0)}" x2="{f(x1)}" y2="{f(y1)}" '
            f'stroke="{col}" stroke-width="{f(sw)}" stroke-linecap="butt" {extra}/>')


def pt(cx, cy, r, a):
    return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))


def arc(cx, cy, r, a0, a1, sw, col=BLACK, extra=""):
    """Arc from angle a0 to a1 (degrees, 0 = east, clockwise on screen)."""
    p0, p1 = pt(cx, cy, r, a0), pt(cx, cy, r, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'<path d="M{f(p0[0])},{f(p0[1])} A{f(r)},{f(r)} 0 {large} 1 '
            f'{f(p1[0])},{f(p1[1])}" fill="none" stroke="{col}" '
            f'stroke-width="{f(sw)}" stroke-linecap="butt" {extra}/>')


def crescent(cx, cy, r, a0, a1, thick, fill=BLACK, extra=""):
    """A moon-sliver hugging the circle (cx, cy, r) from angle a0 to a1:
    the outer edge is the circle, the inner edge a flatter arc; `thick` is the
    width at the middle."""
    p0, p1 = pt(cx, cy, r, a0), pt(cx, cy, r, a1)
    half = math.radians((a1 - a0) / 2)
    h = r * math.sin(half)
    s1 = r - r * math.cos(half)
    s2 = max(s1 - thick, 0.5)
    r2 = (h * h + s2 * s2) / (2 * s2)
    return (f'<path d="M{f(p0[0])},{f(p0[1])} A{f(r)},{f(r)} 0 0 1 {f(p1[0])},{f(p1[1])} '
            f'A{f(r2)},{f(r2)} 0 0 0 {f(p0[0])},{f(p0[1])} Z" fill="{fill}" {extra}/>')


def poly(pts, fill, extra=""):
    return (f'<polygon points="{" ".join(f"{f(x)},{f(y)}" for x, y in pts)}" '
            f'fill="{fill}" {extra}/>')


# ------------------------------------------------------------- composition
# SVG units: 1 = 0.01 in; the SVG covers the whole page (1100 x 1700)
C, R = (300, 372), 188      # the sea (cello, deep blue)
S, RS = (812, 170), 37      # the spray (soprano, yellow)
W = (868, 640)              # the violins' whirl


def composition():
    d = []  # defs
    g = []  # drawing, back to front

    def glow(gid, cx, cy, r0, r1, col, op, k=3.4):
        """Radial glow from the edge r0 out to r1, gaussian-like fall-off,
        many stops so it never bands (it stays a vector shading)."""
        stops = [f'<stop offset="0" stop-color="{col}" stop-opacity="{op:.3f}"/>']
        for i in range(0, 25):
            t = i / 24
            o = op * (math.exp(-k * t * t) - math.exp(-k) * t)
            stops.append(f'<stop offset="{(r0 + t * (r1 - r0)) / r1:.4f}" '
                         f'stop-color="{col}" stop-opacity="{max(o, 0):.4f}"/>')
        d.append(f'<radialGradient id="{gid}" cx="{f(cx)}" cy="{f(cy)}" r="{f(r1)}" '
                 f'gradientUnits="userSpaceOnUse">{"".join(stops)}</radialGradient>')
        return circle(cx, cy, r1, f"url(#{gid})")

    # ---- ground: warm paper, a little lighter where the music floats
    g.append(f'<rect width="1100" height="1700" fill="{GROUND}"/>')
    g.append(glow("gl", 560, 470, 0, 820, LIGHT, .85, k=2.2))
    g.append(glow("gw", 1060, 980, 0, 520, "#EAD2AC", .32, k=2.6))

    # pale neutral planes (Composition VIII's floating planes) for depth
    g.append(poly([(632, -14), (1110, -14), (1110, 336), (708, 312)], LIGHT,
                  'opacity=".9"'))
    g.append(poly([(-10, 752), (418, 714), (446, 936), (-10, 968)], "#EEE3D1",
                  'opacity=".7"'))

    # ---- long lines of Composition VIII, different weights
    LINES = [((514, -10), (346, 948), 1.6), ((533, -10), (359, 984), .55)]
    for (x0, y0), (x1, y1), w in LINES:
        g.append(line(x0, y0, x1, y1, w))
    g.append(line(-10, 214, 1110, 766, .5, extra='opacity=".55"'))
    g.append(line(1110, 446, 560, 990, .5, extra='opacity=".55"'))

    # ---- 6/8 as a small checkerboard (2 bars x 6 quavers; the strong
    # quavers dark), top left, turned; a second, tinier one by the whirl
    def board(x, y, rot, cell, cols, rows):
        cb = [f'<rect width="{cols * cell}" height="{rows * cell}" fill="{BLACK}"/>']
        for row in range(rows):
            for col in range(cols):
                strong = col % 3 == 0
                if strong ^ (row % 2 == 1):
                    continue
                ov = .6 if col < cols - 1 else 0
                cb.append(f'<rect x="{col * cell}" y="{row * cell}" width="{f(cell + ov)}" '
                          f'height="{cell}" fill="{LIGHT}"/>')
        return (f'<g transform="translate({x},{y}) rotate({rot})">{"".join(cb)}'
                f'<rect width="{cols * cell}" height="{rows * cell}" fill="none" '
                f'stroke="{BLACK}" stroke-width="1.2"/></g>')
    g.append(board(64, 74, -12, 15, 6, 2))
    g.append(board(1004, 470, 21, 9, 3, 2))

    # ---- a fragment of a five-line staff, top centre, turned
    st = "".join(line(0, k * 7.5, 190, k * 7.5, 1.3 if k in (0, 4) else .6) for k in range(5))
    g.append(f'<g transform="translate(540,46) rotate(13)">{st}</g>')

    # ---- a small hairline grid (the bar lines of the score), lower left
    gr = []
    for k in range(5):
        gr.append(line(k * 15, 0, k * 15, 45, .7))
    for k in range(4):
        gr.append(line(0, k * 15, 60, k * 15, .7))
    gr.append(f'<rect x="15" y="15" width="15" height="15" fill="{BLACK}"/>')
    g.append(f'<g transform="translate(402,664) rotate(9)">{"".join(gr)}</g>')

    # ================================================== the sea (cello)
    g.append(glow("aura", C[0], C[1], R, R + 150, "#9A6A9C", .56, k=3.0))
    # eclipse depth: a black disc, the blue disc shifted toward the light
    d.append(f'<clipPath id="seaclip">{circle(C[0], C[1], R)}</clipPath>')
    d.append(f'<linearGradient id="sea" x1="0" y1="{C[1] - R}" x2="0" y2="{C[1] + R}" '
             f'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#244A90"/>'
             f'<stop offset="1" stop-color="{COL["Vc"]}"/></linearGradient>')
    g.append(circle(C[0], C[1], R, BLACK))
    g.append(f'<g clip-path="url(#seaclip)">'
             f'{circle(C[0] + 13, C[1] - 11, R, "url(#sea)")}</g>')
    # long lines pass THROUGH the sea in paper colour (Kandinsky's inversions)
    inner = [line(x0, y0, x1, y1, w, "#EADFCB") for (x0, y0), (x1, y1), w in LINES]
    g.append(f'<g clip-path="url(#seaclip)">{"".join(inner)}</g>')
    # rings around the sea, eccentric, of different weights
    g.append(circle(C[0] + 8, C[1] - 5, R + 20, "none", BLACK, .8))
    g.append(arc(C[0] - 6, C[1] + 4, R + 44, 128, 222, 2.2))
    # a black crescent swelling from the sea toward the spray
    g.append(crescent(C[0], C[1], R + 108, -62, -24, 7))
    g.append(arc(C[0], C[1], R + 132, -58, -28, .6))

    # ================================================== the spray
    g.append(glow("sh", S[0], S[1], RS, RS + 96, "#F4CC4C", .70, k=3.2))

    # the viola's orange wedge: the theme, rising from below toward the
    # spray; it brightens where it enters the spray's light
    wedge = [(574, 976), (632, 964), (780, 236)]
    d.append(f'<clipPath id="sprayclip">{circle(S[0], S[1], RS + 80)}</clipPath>')
    g.append(poly(wedge, COL["Va"]))
    g.append(f'<g clip-path="url(#sprayclip)">{poly(wedge, "#F3B762")}</g>')
    # three short strokes across it (Composition VIII's hatchings)
    hx, hy, ha = 694, 592, math.radians(-26)
    for i, w in enumerate((1.3, .6, .6)):
        ox, oy = -math.sin(ha) * i * 9, math.cos(ha) * i * 9
        g.append(line(hx + ox - 58 * math.cos(ha), hy + oy - 58 * math.sin(ha),
                      hx + ox + 58 * math.cos(ha), hy + oy + 58 * math.sin(ha), w))

    # the bond: one taut line from the sea's centre through the spray
    ux, uy = S[0] - C[0], S[1] - C[1]
    n = math.hypot(ux, uy)
    ux, uy = ux / n, uy / n
    a = (C[0] - ux * 390, C[1] - uy * 390)
    b = (S[0] + ux * 132, S[1] + uy * 132)
    g.append(line(*a, *b, 3.0))
    g.append(f'<g clip-path="url(#seaclip)">{line(*a, *b, 3.0, "#EADFCB")}</g>')

    # soprano: the one bright circle, its ring, a tiny crescent of shadow
    g.append(circle(S[0], S[1], RS, COL["S"]))
    g.append(circle(S[0] + 7, S[1] - 6, RS + 15, "none", BLACK, 1.2))
    g.append(crescent(S[0], S[1], RS + 26, 112, 172, 4.5))
    # alto: light-blue circles drifting round it, transparent
    for (x, y, r, op) in [(884, 250, 21, .88), (742, 108, 12, .92), (934, 94, 7, .95)]:
        g.append(circle(x, y, r, COL["A"], extra=f'opacity="{op}"'))
    g.append(circle(884, 250, 31, "none", BLACK, .5))
    # precise little points
    for (x, y, r) in [(716, 168, 3.2), (962, 206, 2.4), (852, 300, 2.0),
                      (690, 62, 1.8), (1000, 150, 1.6), (486, 612, 2.6),
                      (128, 600, 1.9), (560, 720, 1.6)]:
        g.append(circle(x, y, r, BLACK))

    # ================================================== the violins' whirl
    g.append(glow("wh", W[0], W[1], 92, 156, "#D3E0A8", .55, k=3.0))
    # Vn II's lighter circle slips out of Vn I's: where they overlap, a
    # mixed green (transparency drawn as a clip, so it stays vector)
    c2, r2 = (W[0] - 50, W[1] - 44), 56
    d.append(f'<clipPath id="vn1clip">{circle(*W, 92)}</clipPath>')
    g.append(circle(*W, 92, COL["Vn I"]))
    g.append(circle(*c2, r2, COL["Vn II"]))
    g.append(f'<g clip-path="url(#vn1clip)">{circle(*c2, r2, "#71A050")}</g>')
    # eccentric rings turning inward
    for (cx, cy, r, w) in [(W[0] + 10, W[1] + 8, 112, 1.2), (W[0] - 6, W[1] - 4, 124, .5),
                           (c2[0] + 6, c2[1] + 5, 27, 1.4), (c2[0] + 2, c2[1] + 1, 12, .8)]:
        g.append(circle(cx, cy, r, "none", BLACK, w))
    # four strings crossing it
    ang = math.radians(-62)
    dx, dy = math.cos(ang), math.sin(ang)
    px, py = -dy, dx
    for i in range(4):
        o = (i - 1.5) * 8.5
        cx, cy = W[0] - 46 + px * o, W[1] + 44 + py * o
        g.append(line(cx - dx * 190, cy - dy * 190, cx + dx * 118, cy + dy * 118,
                      1.6 if i == 0 else .7 + .15 * i))

    # ================================================== men below
    bx, by, br = 182, 850, 112
    bowl_d = f'M{bx - br},{by} A{br},{br} 0 0 0 {bx + br},{by} Z'
    sq = ('<rect x="-32" y="-32" width="64" height="64" fill="{}" '
          'transform="translate(262,822) rotate(16)"/>')
    d.append(f'<clipPath id="bowlclip"><path d="{bowl_d}"/></clipPath>')
    g.append(f'<path d="{bowl_d}" fill="{COL["B"]}"/>')
    g.append(sq.format(COL["T"]))
    g.append(f'<g clip-path="url(#bowlclip)">{sq.format("#5A2743")}</g>')
    g.append(line(-10, by, bx + br + 80, by, 2.2))
    g.append(arc(bx, by, br + 16, 18, 92, .6))

    # ---- lower middle: a point in a thin circle, and an acute angle opening
    # toward the viola's wedge (Kandinsky's "point - line - plane")
    g.append(circle(468, 836, 30, "none", BLACK, .9))
    g.append(circle(474, 830, 4.2, BLACK))
    g.append(line(404, 932, 548, 862, 1.1) + line(404, 932, 540, 898, .5))

    # ---- the 6/8 swell and the heartbeat as one figure: a wave line of two
    # swells of three crests (strong, weak, weak) - the boat's rocking - with
    # the cello's pizzicato pulse (脉搏) as points riding on the crests
    x0, y0, P, A = 700, 902, 186, 18      # P = one dotted crotchet (3 quavers)
    pts = []
    for i in range(241):
        t = i / 120                          # 0..2 periods = one 6/8 bar
        pts.append(f"{f(x0 + t * P)},{f(y0 - A * math.sin(2 * math.pi * t))}")
    g.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{BLACK}" '
             f'stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>')
    for grp in range(2):
        for j in range(3):
            ph = .25 + j / 3
            r = 6.5 if j == 0 else 3.6
            g.append(circle(x0 + (grp + ph) * P, y0 - A * math.sin(2 * math.pi * ph), r, BLACK))

    return (f'<svg class="art" viewBox="0 0 1100 1700" width="11in" height="17in">'
            f'<defs>{"".join(d)}</defs>{"".join(g)}</svg>')


# ------------------------------------------------------------------ chips
def chip(code, h=18):
    """The performer's shape and colour, as it appears in the composition."""
    c = COL[code]
    m = h / 2
    if code == "T":
        q = h * .62
        body = (f'<rect x="{f(m - q / 2)}" y="{f(m - q / 2)}" width="{f(q)}" height="{f(q)}" '
                f'fill="{c}" transform="rotate(16 {m} {m})"/>')
    elif code == "B":
        r = m - .5
        body = f'<path d="M.5,{f(h * .28)} A{f(r)},{f(r)} 0 0 0 {f(h - .5)},{f(h * .28)} Z" fill="{c}"/>'
    elif code == "Va":
        body = poly([(h * .22, h - .5), (h * .58, h - .5), (h * .84, .5)], c)
    elif code == "Vc":
        r = m - .5
        body = (f'<clipPath id="cv"><circle cx="{m}" cy="{m}" r="{r}"/></clipPath>'
                f'{circle(m, m, r, BLACK)}'
                f'<g clip-path="url(#cv)">{circle(m + 1.1, m - 1, r, c)}</g>')
    else:
        r = {"S": m - 1.5, "A": m - 2.1, "Vn II": m - 1.2}.get(code, m - .8)
        body = circle(m, m, r, c)
    return (f'<svg class="chip" width="{h}" height="{h}" viewBox="0 0 {h} {h}">'
            f'{body}</svg>')


LAT = "'Jost', 'Inter', 'Noto Sans CJK SC', sans-serif"
PIN = "'Inter', 'Noto Sans CJK SC', sans-serif"
CJK = "'Noto Sans CJK SC', 'Jost', sans-serif"

L, RC, COLW = .75, 5.75, 4.5   # left column x, right column x, column width
ROW = .40                      # table row height (in)
T0 = 12.62                     # top of the two tables

CSS = f"""
.page {{ background: {GROUND}; color: {INK}; }}
.art {{ position: absolute; left: 0; top: 0; }}
.abs {{ position: absolute; }}

.title {{ left: {L - .05}in; top: 10.40in; font: 700 88pt/1 {CJK};
          letter-spacing: .015em; color: {BLACK}; white-space: nowrap; }}
.fs {{ right: .75in; top: 10.455in; text-align: right; }}
.fs .a {{ font: 600 13pt/1 {LAT}; letter-spacing: .36em; margin-right: -.36em;
          color: {BLACK}; }}
.fs .b {{ font: 400 7.6pt/1 {LAT}; letter-spacing: .24em; margin-right: -.24em;
          color: {MUTED}; text-transform: uppercase; margin-top: 8pt; }}
.fs .b2 {{ margin-top: 4pt; }}
.line2 {{ left: {L}in; width: 9.5in; top: 11.80in; display: flex;
          align-items: baseline; justify-content: space-between; }}
.pinyin {{ font: 300 15pt/1 {PIN}; letter-spacing: .24em; color: {INK}; }}
.epi {{ font: 300 10pt/1 {CJK}; letter-spacing: .3em; margin-right: -.3em;
        color: {INK}; font-feature-settings: "halt"; }}
.epi .p {{ letter-spacing: .62em; }}
.rule {{ left: {L}in; width: 9.5in; height: 0; border-top: 2.4pt solid {BLACK}; }}

.tbl {{ top: {T0}in; width: {COLW}in; border-top: .6pt solid {HAIR}; }}
.tbl .r {{ height: {ROW}in; display: flex; align-items: center;
           border-bottom: .6pt solid {HAIR}; }}
.tbl .zh {{ font: 500 10.5pt/1 {CJK}; color: {BLACK}; width: .56in; }}
.tbl .en {{ font: 400 6.8pt/1 {LAT}; letter-spacing: .2em; color: {MUTED};
            text-transform: uppercase; flex: 1; }}
.tbl .nm {{ font: 500 12pt/1 {CJK}; color: {BLACK}; letter-spacing: .04em; }}
.tbl .r.me .nm {{ font-weight: 700; }}
.tbl .v {{ font: 400 11pt/1 {LAT}; color: {BLACK}; }}
.tbl .v .zh2 {{ font: 400 10.5pt/1 {CJK}; }}
.tbl .sub {{ height: {2 * ROW}in; display: flex; flex-direction: column;
             justify-content: center; border-bottom: .6pt solid {HAIR}; }}
.tbl .sub .zh {{ width: auto; font: 500 13.5pt/1 {CJK}; letter-spacing: .05em; }}
.tbl .sub .zh .dot {{ letter-spacing: 0; margin: 0 .18em; }}
.tbl .sub .en2 {{ font: 400 10pt/1 {LAT}; color: {INK}; margin-top: 9pt; }}

.key {{ top: 14.96in; width: {COLW}in; }}
.key .h {{ font: 400 9.5pt/1 {LAT}; color: {BLACK}; letter-spacing: .02em; }}
.key .h .zh {{ font: 400 9.5pt/1 {CJK}; margin-left: 7pt; color: {INK}; }}
.key .chips {{ display: flex; margin-top: 11pt;
               align-items: center; font: 500 8.6pt/1 {LAT}; letter-spacing: .04em;
               color: {BLACK}; }}
.key .chips span {{ display: inline-flex; align-items: center; gap: 6pt;
                    width: {COLW / 4}in; }}
.key .chips i {{ font: 400 8.6pt/1 {CJK}; font-style: normal; color: {MUTED};
                 letter-spacing: 0; }}
.key .chips svg {{ display: block; }}

.foot {{ left: {L}in; top: 15.80in; width: 9.5in; display: flex; align-items: center;
         border-top: .6pt solid {HAIR}; padding-top: .21in; }}
.foot .mark {{ margin-right: 12pt; display: block; }}
.foot .sig {{ font: 700 13pt/1 {CJK}; letter-spacing: .3em; color: {BLACK}; }}
.foot .yr {{ font: 400 7.4pt/1 {LAT}; letter-spacing: .28em; margin-right: -.28em;
             color: {MUTED}; text-transform: uppercase; margin-left: auto; }}
"""

EPIGRAPH = ("我的祖国和我", "像海和浪花一朵")
ZH_NAME = {"S": "女高", "A": "女低", "T": "男高", "B": "男低",
           "Vn I": "小提一", "Vn II": "小提二", "Va": "中提", "Vc": "大提"}


def render(m):
    e, sym = lib.e, lib.sym
    rows = []
    for zh, en, name in lib.credit_rows(m):
        me = " me" if name == m["arranger"] else ""
        rows.append(f'<div class="r{me}"><span class="zh">{e(zh)}</span>'
                    f'<span class="en">{e(en)}</span><span class="nm">{e(name)}</span></div>')
    (v_en, v_zh), (s_en, s_zh) = m["instrumentation"]
    key_en, _, key_zh = m["key"].partition(" · ")
    sub_a, _, sub_b = m["subtitle"].partition(" · ")
    facts = [("调性", "Key", f'{sym(key_en)} · <span class="zh2">{e(key_zh)}</span>'),
             ("速度", "Tempo", sym(m["tempo"])),
             ("时长", "Duration", sym(m["duration"]))]
    fact_rows = "".join(f'<div class="r"><span class="zh">{zh}</span><span class="en">{en}</span>'
                        f'<span class="v">{v}</span></div>' for zh, en, v in facts)

    def chips(codes):
        return "".join(f'<span>{chip(c)}{e(c)}<i>{ZH_NAME[c]}</i></span>' for c in codes)
    # the signature's mark: the cover's idea in miniature - the sea and the
    # spray tied by one line
    mark = ('<svg class="mark" width="46" height="18" viewBox="0 0 46 18">'
            + line(2, 16, 44, 3, 1.1)
            + circle(11, 11, 7, COL["Vc"]) + circle(37, 5.2, 3.6, COL["S"]) + '</svg>')
    body = f"""
{composition()}
<div class="abs title">{e(m["title"])}</div>
<div class="abs fs"><div class="a">FULL SCORE</div>
  <div class="b">Score in C</div><div class="b b2">Concert Pitch</div></div>
<div class="abs line2"><span class="pinyin">{e(m["title_latin"])}</span>
  <span class="epi">{e(EPIGRAPH[0])}<span class="p">，</span>{e(EPIGRAPH[1])}</span></div>
<div class="abs rule" style="top:12.26in"></div>
<div class="abs tbl" style="left:{L}in">
  <div class="sub"><div class="zh">{e(sub_a)}<span class="dot">·</span>{e(sub_b)}</div>
    <div class="en2">{e(m["subtitle_en"])}</div></div>
  {fact_rows}</div>
<div class="abs tbl" style="left:{RC}in">{"".join(rows)}</div>
<div class="abs key" style="left:{L}in">
  <div class="h">{e(v_en)}<span class="zh">{e(v_zh)}</span></div>
  <div class="chips">{chips(("S", "A", "T", "B"))}</div></div>
<div class="abs key" style="left:{RC}in">
  <div class="h">{e(s_en)}<span class="zh">{e(s_zh)}</span></div>
  <div class="chips">{chips(("Vn I", "Vn II", "Va", "Vc"))}</div></div>
<div class="abs foot">{mark}<span class="sig">{e(m["arranger"])}</span>
  <span class="yr">Arrangement &amp; Music Preparation · {e(m["year"])}</span></div>
"""
    return lib.page(CSS, body, "kandinsky")
