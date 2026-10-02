"""brockmann: homage to Josef Mueller-Brockmann (Swiss International Style,
the Tonhalle Zuerich "musica viva" / Beethoven concert posters).

One idea: 「像海和浪花一朵」 drawn as ripples spreading from one spray.
The rings are the score itself, read like a clock face:
  * 8 concentric rings = the 8 performers, from the centre outward
    S, A (women = the spray, vermilion), T, B (men = the sea), Vn I, Vn II,
    Va, Vc (white); ring widths and gaps grow outward by 1 : 1.22.
  * angle = time: the 73 bars (468 quavers) run clockwise from twelve
    o'clock; an arc is drawn where that performer sounds, a gap where they
    rest.
  * two weights, so the image stays calm: a held or bowed line is a full
    arc; a run of three or more short notes (the pizzicato "harp" of the
    intro and first verse, the viola's off-beats) is ONE thin line across
    the run instead of a comb of dashes; rests of up to one beat (a dotted
    crotchet) inside a line are closed.  The only short strokes left are
    the two cello pizzicati on 「母亲的脉搏」 (bar 30): the mother's pulse,
    in vermilion.
  * fine radii mark bar 1 and the rehearsal letters A-G; the letters sit,
    boxed as in the score, on the seam between the singers and the strings.
Colours: deep jade-ink ground (碧, the sea at night), warm white, vermilion
(朱) - three flat colours, as in the master's posters.
Data: wohewodezuguo/output/*.musicxml (sounding spans per part, in quavers).
All type is SVG text on one baseline grid, four columns.
"""
import math

import lib

U = 100  # SVG units per inch

BLACK = "#0D2E2B"
WHITE = "#F3EFE7"
VERMILION = "#D4472B"
GREY = "#9DAAA6"     # secondary text
HAIR = "#4F706A"     # construction lines

SANS = "'Inter','Noto Sans CJK SC',sans-serif"
CJK = "'Noto Sans CJK SC',sans-serif"

TOTAL = 468  # quavers in the 73 bars (63 x 6/8 + 10 x 9/8)
SECTIONS = [("A", 54), ("B", 150), ("C", 204), ("D", 258), ("E", 354),
            ("F", 408), ("G", 438)]

# sounding spans per part, in quavers from bar 1 (consecutive notes merged)
_VN2_PIZZ = [(x, x + 2) for x in range(1, 28, 3)] + [(28, 29)]
PARTS = [
    ("S", [(150, 203), (258, 294), (306, 465)]),
    ("A", [(54, 203), (258, 294), (306, 465)]),
    ("T", [(126, 138), (150, 203), (258, 293), (294, 303), (306, 465)]),
    ("B", [(126, 138), (150, 203), (258, 293), (294, 465)]),
    ("Vn I", [(15, 48), (75, 78), (122, 126), (159, 165), (174, 200),
              (201, 258), (294, 306), (315, 348), (353, 404), (405, 465)]),
    ("Vn II", _VN2_PIZZ + [(30, 48)] + [(x, x + 2) for x in range(49, 74, 3)]
     + [(x, x + 2) for x in range(79, 119, 3)]
     + [(138, 144), (147.5, 156), (159, 200), (201, 258), (294, 306),
        (318, 348), (351.5, 404), (405, 456), (457.5, 465)]),
    ("Va", [(0, 48)] + [(x, x + 1) for x in range(51, 97, 3)]
     + [(99, 126), (138, 144), (146, 258)]
     + [(x, x + 2) for x in range(307, 320, 3)]
     + [(322, 348), (350, 456), (457.5, 465)]),
    ("Vc", [(x, x + 1) for x in range(0, 28, 3)]
     + [(30, 126), (138, 185), (186, 187), (189, 190), (192, 465)]),
]
VOICE_COLOURS = {"S": VERMILION, "A": VERMILION}

# ring geometry (inches): inner edge of the first ring, widths and gaps grow
# by the same ratio outward, like a ripple
R0, W0, G0, Q = 0.70, 0.10, 0.22, 1.22
THIN = 0.17      # a pulse line is this fraction of its ring's width
SHORT = 2        # a note of <= 2 quavers is short
BREATH = 3       # rests up to one beat (a dotted crotchet) are not drawn
# centre: the outer ring is tangent to the right margin; the left and top
# trim edges fall in the middle of ring gaps (clean crops, no near-touches)
CX, CY = 4.75, 3.75


def strokes(spans):
    """[(kind, a, b)]: 'arc' a held/bowed line, 'pulse' a run of >= 3 short
    notes drawn as one thin line, 'beat' an isolated short note."""
    items, i = [], 0
    while i < len(spans):
        j = i
        if spans[i][1] - spans[i][0] <= SHORT:
            while (j + 1 < len(spans) and spans[j + 1][1] - spans[j + 1][0] <= SHORT
                   and spans[j + 1][0] - spans[j][1] <= SHORT):
                j += 1
            if j - i >= 2:
                items.append(["pulse", spans[i][0], spans[j][1]])
            else:
                items += [["beat", a, b] for a, b in spans[i:j + 1]]
        else:
            items.append(["arc", *spans[i]])
        i = j + 1
    out = [items[0]]
    for it in items[1:]:
        p = out[-1]
        gap = it[1] - p[2]
        if gap <= BREATH and p[0] == it[0] == "arc":
            p[2] = it[2]                       # a breath inside a line
        elif gap <= BREATH and "beat" not in (p[0], it[0]):
            if p[0] == "pulse":                # the thin line runs into the arc
                p[2] = it[1]
            else:
                it[1] = p[2]
            out.append(it)
        else:
            out.append(it)
    return out


def rings():
    out, r = [], R0
    for i, (name, spans) in enumerate(PARTS):
        w = W0 * Q ** i
        out.append((name, strokes(spans), r + w / 2, w))
        r += w + G0 * Q ** i
    return out


def pt(r, deg):
    a = math.radians(deg)
    return CX + r * math.sin(a), CY - r * math.cos(a)


def arc(r, t0, t1):
    a0, a1 = 360 * t0 / TOTAL, 360 * t1 / TOTAL
    x0, y0 = pt(r, a0)
    x1, y1 = pt(r, a1)
    large = 1 if a1 - a0 > 180 else 0
    return (f"M{x0 * U:.2f},{y0 * U:.2f} "
            f"A{r * U:.2f},{r * U:.2f} 0 {large} 1 {x1 * U:.2f},{y1 * U:.2f}")


def art():
    parts = []
    rs = rings()
    r_out = rs[-1][2] + rs[-1][3] / 2
    # the rehearsal dial sits in the gap between the bass and Vn I rings
    b_out = rs[3][2] + rs[3][3] / 2
    v_in = rs[4][2] - rs[4][3] / 2
    rd = (b_out + v_in) / 2
    marks = [("1", 0)] + SECTIONS        # bar 1 = twelve o'clock
    for _, t in marks:                   # construction radii, seen in the gaps
        x0, y0 = pt(0.20, 360 * t / TOTAL)
        x1, y1 = pt(r_out, 360 * t / TOTAL)
        parts.append(f'<line x1="{x0 * U:.2f}" y1="{y0 * U:.2f}" x2="{x1 * U:.2f}" '
                     f'y2="{y1 * U:.2f}" stroke="{HAIR}" stroke-width="0.75"/>')
    for name, items, r, w in rs:
        col = VOICE_COLOURS.get(name, WHITE)
        full = " ".join(arc(r, a, b) for k, a, b in items if k == "arc")
        thin = " ".join(arc(r, a, b) for k, a, b in items if k == "pulse")
        beat = " ".join(arc(r, a, b) for k, a, b in items if k == "beat")
        if full:
            parts.append(f'<path d="{full}" fill="none" stroke="{col}" '
                         f'stroke-width="{w * U:.2f}"/>')
        if thin:
            parts.append(f'<path d="{thin}" fill="none" stroke="{col}" '
                         f'stroke-width="{max(w * THIN, 0.03) * U:.2f}"/>')
        if beat:   # the mother's pulse
            parts.append(f'<path d="{beat}" fill="none" stroke="{VERMILION}" '
                         f'stroke-width="{w * U:.2f}"/>')
    # the spray
    parts.append(f'<circle cx="{CX * U}" cy="{CY * U}" r="{0.09 * U}" fill="{WHITE}"/>')
    # bar 1 and the rehearsal letters, boxed as in the score
    h = 0.20
    for letter, t in marks:
        x, y = pt(rd, 360 * t / TOTAL)
        parts.append(f'<rect x="{(x - h / 2) * U:.2f}" y="{(y - h / 2) * U:.2f}" '
                     f'width="{h * U:.2f}" height="{h * U:.2f}" fill="{BLACK}" '
                     f'stroke="{GREY}" stroke-width="0.8"/>'
                     + txt(x, y + 0.042, letter, 8.5, SANS, 600, WHITE, anchor="middle"))
    return "".join(parts)


def txt(x, y, s, size, fam=SANS, w=400, fill=WHITE, ls=0, anchor="start", extra=""):
    """SVG text, (x, y) = start of the BASELINE in inches, size in points."""
    return (f'<text x="{x * U:.2f}" y="{y * U:.2f}" text-anchor="{anchor}" '
            f'style="font-family:{fam};font-weight:{w};font-size:{size * U / 72:.3f}px;'
            f'letter-spacing:{ls}em;fill:{fill};{extra}">{s}</text>')


def ssym(s):
    """lib.sym for SVG: the music glyphs in the fallback font."""
    return "".join(f"<tspan style=\"font-family:'DejaVu Sans';font-size:.92em\">{ch}</tspan>"
                   if ch in "♩♪♭♯♮" else ch for ch in lib.e(s))


QUOTE = "我的祖国和我，像海和浪花一朵"  # 张藜's lyric: the image of the rings

# grid
L, RM = 0.75, 10.25
COLS = [0.75, 3.1875, 5.625, 8.0625]
YT = 11.30          # title baseline
TITLE_PT = 87.6     # the title's ink spans columns 1-3 exactly
PITCH = 0.62        # row pitch of the information block
NAME_X = 0.40       # credit names sit on a tab after the two-character label


def render(m):
    e = lib.e
    b = []
    # legend, in the free corner right of the rings
    lx, ly = COLS[3], 8.60
    b.append(txt(lx, ly, "EIGHT RINGS · EIGHT PERFORMERS", 7, SANS, 600, WHITE, .16))
    b.append(txt(lx, ly + 0.19, "S A T B · Vn I Vn II Va Vc", 7.5, SANS, 400, GREY))
    for k, ln in enumerate(["由内向外，八个声部，朱红为女声；",
                            "自十二点起顺时针，第 1–73 小节；",
                            "有声为弧，休止为空（一拍以内不留空）；",
                            "粗弧为长音，细线为拨弦与短音律动；",
                            "朱红两拍：大提琴拨弦，「母亲的脉搏」。"]):
        b.append(txt(lx, ly + 0.40 + k * 0.16, ln.replace(
            "朱红", f'<tspan style="fill:{VERMILION}">朱红</tspan>'), 7, SANS, 400, GREY))
    # headline block
    b.append(txt(L - 0.035, YT, e(m["title"]), TITLE_PT, CJK, 900, WHITE, -.02))
    b.append(txt(COLS[3], YT - 0.872, "FULL SCORE", 12, SANS, 700, WHITE, .16))
    b.append(txt(COLS[3], YT - 0.632, "Score in C · Concert Pitch", 8.5, SANS, 400, GREY))
    ys = YT + 0.44
    b.append(txt(L, ys, e(m["title_latin"]), 15, SANS, 500, WHITE, .02))
    b.append(txt(COLS[2], ys, e(m["subtitle"]), 11, SANS, 400, WHITE))
    b.append(txt(COLS[2], ys + 0.22, e(m["subtitle_en"]), 8, SANS, 400, GREY))
    # the lyric the rings draw
    b.append(txt(L - 0.02, 12.85, e(m.get("quote") or QUOTE), 21, CJK, 350, VERMILION, .04))
    # rule + four columns on one baseline grid
    ry = 13.50
    b.append(f'<line x1="{L * U}" x2="{RM * U}" y1="{ry * U}" y2="{ry * U}" '
             f'stroke="{WHITE}" stroke-width="1.04"/>')
    yl = ry + 0.25           # label baselines; values 0.22 below

    def cell(x, k, label, *lines):
        y = yl + k * PITCH
        out = [txt(x, y, e(label).upper(), 7, SANS, 600, GREY, .16)] if label else []
        for j, ln in enumerate(lines):
            out.append(ln(x, y + 0.22 + j * 0.20))
        return "".join(out)

    def credit(zh, name):
        return lambda x, y: (txt(x, y, e(zh), 10, CJK, 400, GREY)
                             + txt(x + NAME_X, y, e(name), 10, CJK, 500, WHITE))

    def plain(s, fill=WHITE, fam=SANS):
        return lambda x, y: txt(x, y, s, 10, fam, 400, fill)

    credits = lib.credit_rows(m)
    groups = [[c for c in credits if c[0] not in ("改编", "制谱")],
              [c for c in credits if c[0] in ("改编", "制谱")]]
    for col, rows in zip(COLS[:2], groups):
        for k, (zh, en, name) in enumerate(rows):
            b.append(cell(col, k, en, credit(zh, name)))
    tempo = ssym(m["tempo"]) + (f'<tspan dx="0.4em" style="fill:{GREY}">'
                                f'{e(m["tempo_text"])}</tspan>' if m.get("tempo_text") else "")
    for k, (lab, val) in enumerate([("Key", ssym(m["key"])), ("Tempo", tempo),
                                    ("Duration", ssym(m["duration"]))]):
        b.append(cell(COLS[2], k, lab, plain(val)))
    for k, (en, zh) in enumerate(m["instrumentation"]):
        b.append(cell(COLS[3], k, "Instrumentation" if k == 0 else "",
                      plain(e(en)), plain(e(zh), GREY, CJK)))
    # foot
    fy = 15.85
    b.append(f'<line x1="{L * U}" x2="{RM * U}" y1="{fy * U}" y2="{fy * U}" '
             f'stroke="{WHITE}" stroke-width="1.04"/>')
    yf = fy + 0.36
    b.append(txt(L, yf, e(m["arranger"]), 13, CJK, 700, WHITE, .12))
    b.append(txt(COLS[1], yf - 0.005, "ARRANGEMENT &amp; MUSIC PREPARATION · " + e(m["year"]),
                 8, SANS, 400, GREY, .14))
    svg = ('<svg class="art" viewBox="0 0 1100 1700" width="11in" height="17in">'
           + art() + "".join(b) + "</svg>")
    css = (f".page {{ background: {BLACK}; }} .art {{ position:absolute; left:0; top:0; }}"
           " text { font-kerning: normal; }")
    return lib.page(css, svg, "brockmann")
