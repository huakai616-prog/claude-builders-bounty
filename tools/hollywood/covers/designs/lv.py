"""lv — homage to 吕敬人 (Lü Jingren): the poetics of the Chinese book.

The right of the page is one leaf of a Song woodblock book on 朱丝栏 paper:
四周双边 frame and six 界栏 columns ruled in cinnabar (six, like the 6/8
bar), the 版心 on the fold side with a pair of 鱼尾 and, at its foot, the
engraver's name (the 刻工 of a Song print = 制谱).  The title stands in
ink in the centre two columns, the grid giving way to it.  The columns end
on a horizon: below it a jade sea after 马远's 水图, and riding on that
horizon the arranger's 白文 seal: 「像海和浪花一朵」, the sea and the one
spray.  To the left, on the darker board, the Western half of the score's
bilingual life: a precise column whose rules hang on the leaf's own lines
(the title's character grid, then the horizon itself, carried across in
jade) and run on into the frame, so the two halves read as one system.
"""
import math
import re

import lib
from lib import e, sym

# one short lyric line (张藜) — per-song art; meta may override it
LYRIC = "我的祖国和我　像海和浪花一朵"

INK, CIN = lib.INK, lib.CINNABAR
INK2 = "#857A6C"                # secondary ink (warm grey)
LEAF = "#FAF6EE"                # the leaf, a sheet lighter than the board
SEA = "#3F7A7A"                 # 碧: 「永远给我碧浪清波」
WASH, WASH_OP = "#6FA9A0", .20   # the sea's wash: a clearer, lighter 碧


def mix(a, b, t):
    """t of colour a over colour b, as a solid hex (hairlines print evenly)."""
    ca = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x * t + y * (1 - t)):02X}" for x, y in zip(ca, cb))


BOARD = "#F1E8D9"               # the board: lib.PAPER a shade deeper, so the leaf reads as a sheet
RULE = mix(CIN, LEAF, .78)      # 朱丝栏 column rules
HAIR = mix(CIN, BOARD, .55)     # hairlines of the Western column
JADE_RULE = mix(SEA, BOARD, .70)

# ---- grid (inches) --------------------------------------------------------
FX0, FX1 = 4.35, 10.05          # frame, outer rule
FY0, FY1 = 2.15, 15.10          # 天头 2.15 > 地脚 1.90
GAP = 0.08                      # 四周双边: outer thick, inner thin
IX0, IX1, IY0, IY1 = FX0 + GAP, FX1 - GAP, FY0 + GAP, FY1 - GAP
BX = 0.56                       # 版心 width
CX0 = IX0 + BX                  # first text column
CW = (IX1 - CX0) / 6            # six 界栏 columns
TX = CX0 + 3 * CW               # title axis
T_SIZE, T_STEP = 1.40, 1.52     # title glyph, pitch
T_TOP = IY0 + 0.72              # = top of the upper 鱼尾
T_END = T_TOP + 6 * T_STEP - (T_STEP - T_SIZE)
SEAL = 1.08
HORIZON = 13.16                 # where the 界栏 end and the sea begins
SEAL_Y = HORIZON - SEAL * 0.66  # the seal rides on the horizon
YW_H = 0.26                     # 鱼尾 height
YW1 = T_TOP                     # upper 鱼尾: top on the title's first line
YW2 = HORIZON - YW_H            # lower 鱼尾: stands on the horizon
LX = 0.95                       # Western column
LW = FX0 - 0.45 - LX


def char_top(k):
    return T_TOP + k * T_STEP


def U(v):
    return round(v * 100, 2)   # svg units (0.01 in)


def line(x1, y1, x2, y2, col, w, extra=""):
    return (f"<line x1='{U(x1)}' y1='{U(y1)}' x2='{U(x2)}' y2='{U(y2)}' "
            f"stroke='{col}' stroke-width='{w}'{extra}/>")


def vtext(x, y, w, s, cls, h=None, extra=""):
    """A vertical column of text centred on a column of width w."""
    hh = f"height:{h}in;" if h else ""
    return (f"<div class='v {cls}' style='left:{x}in;top:{y}in;width:{w}in;"
            f"line-height:{w}in;{hh}{extra}'>{s}</div>")


def at(x, y, s, cls, extra=""):
    return f"<div class='a {cls}' style='left:{x}in;top:{y}in;{extra}'>{s}</div>"


def yuwei(cx, y, w, h, down=True, col=CIN, inlay=None):
    """鱼尾: a bar with a swallow-tail notch (down: the upper one); `inlay`
    draws a fine paper line inside it, as cut in the block."""
    x0, x1 = cx - w / 2, cx + w / 2
    if down:
        pts = [(x0, y), (x1, y), (x1, y + h), (cx, y + h * .38), (x0, y + h)]
    else:
        pts = [(x0, y + h), (x1, y + h), (x1, y), (cx, y + h * .62), (x0, y)]
    p = " ".join(f"{U(a)},{U(b)}" for a, b in pts)
    out = f"<polygon points='{p}' fill='{col}'/>"
    if inlay:
        # the notch echoed by a paper hairline a little inside the bar
        k = 0.30 * h
        if down:
            q = [(x0 + .05, y + h - .035), (cx, y + h * .38 - k * .55), (x1 - .05, y + h - .035)]
        else:
            q = [(x0 + .05, y + .035), (cx, y + h * .62 + k * .55), (x1 - .05, y + .035)]
        out += (f"<polyline points='{' '.join(f'{U(a)},{U(b)}' for a, b in q)}' "
                f"fill='none' stroke='{inlay}' stroke-width='.55'/>")
    return out


def rnd_gen(seed):
    s = [seed]

    def rnd():
        s[0] = (s[0] * 1103515245 + 12345) % 2147483648
        return s[0] / 2147483648
    return rnd


def sea(x0, x1, y0, y1, n, hole):
    """Water after 马远's 水图, in jade hairline: swells seen in depth (lines
    crowd towards the horizon, grow, slow and darken towards us); every
    third line a little stronger (6/8: one strong, two light); each line
    fades in and out at its own place, so the field breathes.  A faint
    jade wash deepens towards the foot, so the band reads as sea from far
    off.  `hole` (x0, y0, x1, y1) is kept clear round the seal."""
    rnd = rnd_gen(7)
    defs, out = [], []
    # wash: nothing at the horizon, a breath of jade at the foot
    defs.append(f"<linearGradient id='wash' x1='0' y1='0' x2='0' y2='1'>"
                f"<stop offset='0' stop-color='{WASH}' stop-opacity='0'/>"
                f"<stop offset='.35' stop-color='{WASH}' stop-opacity='{WASH_OP * .3:.3f}'/>"
                f"<stop offset='1' stop-color='{WASH}' stop-opacity='{WASH_OP:.3f}'/>"
                f"</linearGradient>")
    hx0, hy0, hx1, hy1 = hole
    defs.append(f"<mask id='seal-hole' maskUnits='userSpaceOnUse' x='0' y='0' "
                f"width='1100' height='1700'><rect width='1100' height='1700' fill='#fff'/>"
                f"<rect x='{U(hx0)}' y='{U(hy0)}' width='{U(hx1 - hx0)}' "
                f"height='{U(hy1 - hy0)}' rx='3' fill='#000'/></mask>")
    wash = (f"<rect x='{U(x0)}' y='{U(y0)}' width='{U(x1 - x0)}' "
            f"height='{U(y1 - y0)}' fill='url(#wash)'/>")
    for i in range(n):
        t = i / (n - 1)
        yb = y0 + 0.005 + (y1 - y0 - 0.13) * t ** 1.5
        amp = 0.004 + 0.032 * t ** 1.1
        lam = 0.15 + 0.38 * t
        ph = rnd() * 6.28
        strong = i % 3 == 0
        pts = []
        x = x0
        while x <= x1 + 1e-6:
            u = 2 * math.pi * (x - x0) / lam + ph
            a = amp * (0.58 + 0.42 * math.cos(u / 3))
            pts.append((x, yb - a * math.sin(u)))
            x += 0.01
        d = "M" + " L".join(f"{U(a)},{U(b)}" for a, b in pts)
        s0 = 0.00 + rnd() * 0.20
        s1 = 1.00 - rnd() * 0.20
        if i == 0:                                   # the horizon: whole
            s0, s1 = 0.0, 1.0
        op = (0.78 + 0.22 * t) if strong else (0.55 + 0.30 * t)
        gid = f"sw{i}"
        defs.append(
            f"<linearGradient id='{gid}' gradientUnits='userSpaceOnUse' "
            f"x1='{U(x0)}' x2='{U(x1)}' y1='0' y2='0'>"
            f"<stop offset='{max(s0 - .02, 0):.3f}' stop-color='{SEA}' stop-opacity='{0 if i else op:.2f}'/>"
            f"<stop offset='{s0 + .12:.3f}' stop-color='{SEA}' stop-opacity='{op:.2f}'/>"
            f"<stop offset='{s1 - .12:.3f}' stop-color='{SEA}' stop-opacity='{op:.2f}'/>"
            f"<stop offset='{min(s1 + .02, 1):.3f}' stop-color='{SEA}' stop-opacity='{0 if i else op:.2f}'/>"
            f"</linearGradient>")
        sw = (.75 + .75 * t) if strong else (.45 + .45 * t)
        out.append(f"<path d='{d}' fill='none' stroke='url(#{gid})' "
                   f"stroke-width='{sw:.2f}' stroke-linecap='round'/>")
    return (f"<defs>{''.join(defs)}</defs>{wash}"
            f"<g mask='url(#seal-hole)'>{''.join(out)}</g>")


def seal_html(name, x, y, s):
    """白文 seal, real text: the first three characters in the right
    column, the rest in the left (read right to left).  The stone's edge is
    a little uneven and worn, a paper hairline divides the two columns
    (the seal's own 界栏), and the characters fill their cells the way cut
    characters do."""
    right, left = name[:3], name[3:]
    m = 0.085                       # solid border
    g = 0.05                        # gutter (with the dividing hairline)
    cw = (s - 2 * m - g) / 2
    out = []

    def cell(ch, cx, cy, w, h):
        fs = min(w, h)
        sx = w / (fs * .93)
        sy = h / (fs * .93)
        return (f"<span class='sc' style='left:{cx:.3f}in;top:{cy:.3f}in;"
                f"width:{w:.3f}in;height:{h:.3f}in;font-size:{fs:.3f}in'>"
                f"<i style='transform:scale({sx:.3f},{sy:.3f})'>{e(ch)}</i></span>")
    rh = (s - 2 * m) / max(len(right), 1)
    for i, ch in enumerate(right):
        out.append(cell(ch, m + cw + g, m + i * rh, cw, rh))
    lh = (s - 2 * m) / max(len(left), 1)
    for i, ch in enumerate(left):
        out.append(cell(ch, m, m + i * lh, cw, lh))
    # the stone: an uneven edge, slightly worn corners
    rnd = rnd_gen(31)
    pts = []
    S = U(s)
    steps = 9
    for side in range(4):
        for k in range(steps):
            f = k / steps
            j = (rnd() - .5) * 1.1
            if side == 0:
                pts.append((f * S, j))
            elif side == 1:
                pts.append((S + j, f * S))
            elif side == 2:
                pts.append((S - f * S, S + j))
            else:
                pts.append((j, S - f * S))
    # pull the four corners in a touch (a stone is never knife-sharp)
    for idx in (0, steps, 2 * steps, 3 * steps):
        px, py = pts[idx]
        pts[idx] = (px + (1.2 if px < S / 2 else -1.2), py + (1.2 if py < S / 2 else -1.2))
    poly = " ".join(f"{a:.2f},{b:.2f}" for a, b in pts)
    stone = (f"<svg class='stone' width='{s}in' height='{s}in' viewBox='0 0 {S} {S}'>"
             f"<polygon points='{poly}' fill='{CIN}'/></svg>")
    # wear, clipped to the stone: paper nicks on the edge, specks where
    # the ink did not take (paper) or the knife left a crumb (cinnabar),
    # and the dividing hairline
    rnd = rnd_gen(53)
    wear = []
    for (nx, ny, r) in [(.18, 0, .9), (.71, 0, .6), (1, .33, .7), (1, .86, .55),
                        (.42, 1, .8), (.9, 1, .5), (0, .61, .75), (0, .12, .5)]:
        wear.append(f"<circle cx='{nx * S:.2f}' cy='{ny * S:.2f}' r='{r:.2f}' fill='{LEAF}'/>")
    for k in range(44):
        cx, cy = rnd() * S, rnd() * S
        r = .16 + rnd() ** 2 * .34
        col = LEAF if k % 3 else CIN
        wear.append(f"<circle cx='{cx:.2f}' cy='{cy:.2f}' r='{r:.2f}' fill='{col}'/>")
    gx = U(m + cw + g / 2)
    wear.append(f"<line x1='{gx}' y1='{U(m) - 1.5}' x2='{gx}' y2='{S - U(m) + 1.5}' "
                f"stroke='{LEAF}' stroke-width='1.1'/>")
    wear_svg = (f"<svg class='stone' width='{s}in' height='{s}in' viewBox='0 0 {S} {S}'>"
                f"<defs><clipPath id='stone'><polygon points='{poly}'/></clipPath></defs>"
                f"<g clip-path='url(#stone)'>{''.join(wear)}</g></svg>")
    return (f"<div class='seal' style='left:{x}in;top:{y}in;width:{s}in;height:{s}in'>"
            f"{stone}{''.join(out)}{wear_svg}</div>")


def render(m):
    title = e(m["title"])
    # ---------------- SVG: frame, 界栏, 版心 ----------------
    sv = []
    sv.append(f"<rect x='{U(FX0)}' y='{U(FY0)}' width='{U(FX1 - FX0)}' "
              f"height='{U(FY1 - FY0)}' fill='{LEAF}' stroke='{CIN}' stroke-width='3.2'/>")
    seal_x = TX - SEAL / 2
    pad = 0.07
    sv.append(sea(CX0, IX1, HORIZON, IY1, 16,
                  (seal_x - pad, SEAL_Y - pad, seal_x + SEAL + pad, SEAL_Y + SEAL + pad)))
    sv.append(f"<rect x='{U(IX0)}' y='{U(IY0)}' width='{U(IX1 - IX0)}' "
              f"height='{U(IY1 - IY0)}' fill='none' stroke='{CIN}' stroke-width='.8'/>")
    sv.append(line(CX0, IY0, CX0, IY1, CIN, .8))            # 版心 rule
    for i in (1, 2, 4, 5):                                     # 界栏
        x = CX0 + i * CW
        sv.append(line(x, IY0, x, HORIZON, RULE, .75))
    bc = IX0 + BX / 2
    sv.append(line(bc, IY0, bc, YW1, CIN, 1.2))               # 细黑口
    sv.append(yuwei(bc, YW1, BX, YW_H, True, inlay=LEAF))
    sv.append(yuwei(bc, YW2, BX, YW_H, False, inlay=LEAF))
    sv.append(line(bc, HORIZON, bc, HORIZON + .32, CIN, 1.2))
    # Western column: hairlines hung on the leaf's lines, run into the frame
    for k in (1, 3, 5):
        y = char_top(k)
        sv.append(line(LX, y, FX0, y, HAIR, .7))
        sv.append(yuwei(LX + 0.09, y, 0.18, 0.085, True))
    # ... and the horizon itself, carried across in jade
    sv.append(line(LX, HORIZON, FX0, HORIZON, JADE_RULE, .75))
    sv.append(yuwei(LX + 0.09, HORIZON, 0.18, 0.085, True, col=SEA))
    svg = (f"<svg class='art' width='11in' height='17in' viewBox='0 0 1100 1700'>"
           f"{''.join(sv)}</svg>")

    # ---------------- the leaf ----------------
    body = [svg]
    body.append(vtext(TX - CW, T_TOP, 2 * CW, title, "title"))
    body.append(seal_html(m["arranger"], seal_x, SEAL_Y, SEAL))
    rows = {zh: name for zh, en, name in lib.credit_rows(m)}
    trad = "".join(f"<span class='it'>{e(rows[k])}<span class='lab'>{e(k)}</span></span>"
                   for k in ("作曲", "作词", "原唱") if k in rows)
    # the credits span the title's first two characters exactly
    body.append(vtext(CX0 + 5 * CW, T_TOP, CW, trad, "trad", h=T_STEP + T_SIZE))
    body.append(vtext(CX0 + 4 * CW, char_top(2), CW,
                      e(m.get("cover_lyric") or LYRIC), "lyric"))
    sub = e(m["subtitle"]).replace(" · ", "<span class='dot'>・</span>")
    body.append(vtext(CX0 + CW, T_TOP, CW, sub, "sub",
                      h=T_END - T_TOP, extra="text-align:end"))
    body.append(vtext(IX0, YW1 + 0.50, BX,
                      f"{title}<span class='bxs'>{e(m.get('score_zh', '总谱'))}</span>", "bx"))
    body.append(vtext(IX0, HORIZON + 0.50, BX, e(m["engraver"]), "bxk"))

    # ---------------- the Western column ----------------
    w = []
    w.append(f"<div class='flag' style='left:{LX}in;top:{FY0}in'>{lib.flag_svg(0.51 * 96)}</div>")
    w.append(at(LX, T_TOP - 0.035, "Full Score", "fs"))
    w.append(at(LX, T_TOP + 0.36, "Score in C · Concert Pitch", "fs2"))
    y1 = char_top(1) + 0.26
    w.append(at(LX, y1, title, "ht"))
    w.append(at(LX, y1 + 0.56, e(m["title_latin"]), "pin"))
    en = m["subtitle_en"]
    en = re.sub(r"\(([^)]*)\)", lambda mo: "(" + mo.group(1).replace(" ", "\u00a0") + ")", en)
    head, _, rest = en.partition(" — ")
    w.append(at(LX, y1 + 1.08, f"<b>{e(head)}</b>{e(rest)}", "suben", f"width:{LW}in"))
    # credits: five rows
    y2 = char_top(3) + 0.14
    cr = lib.credit_rows(m)
    rh = 0.37
    trs = "".join(
        f"<tr style='height:{rh}in'><td class='zh'>{e(zh)}</td><td class='en'>{e(en_)}</td>"
        f"<td class='nm'>{e(name)}</td></tr>" for zh, en_, name in cr)
    w.append(f"<table class='cr' style='left:{LX}in;top:{y2}in;width:{LW}in'>{trs}</table>")
    # key / tempo / duration, then the forces
    y3 = char_top(5) + 0.22
    kz = m["key"].split(" · ")
    cells = [("Key", " · ".join(sym(x) for x in kz)), ("Tempo", sym(m["tempo"])),
             ("Duration", sym(m["duration"]))]
    w.append(f"<div class='kt' style='left:{LX}in;top:{y3}in;width:{LW}in'>" +
             "".join(f"<div><b>{k}</b><span>{v}</span></div>" for k, v in cells) + "</div>")
    inst = "".join(f"<div><span class='en'>{e(a)}</span><span class='zh'>{e(b)}</span></div>"
                   for a, b in m["instrumentation"])
    w.append(f"<div class='inst' style='left:{LX}in;top:{y3 + 0.78}in;width:{LW}in'>"
             f"<b>Forces</b>{inst}</div>")
    yr = f" · {e(m['year'])}" if m.get("year") else ""
    sig = (f"<div class='n'>{e(m['arranger'])}</div>"
           f"<div class='r'>Arrangement &amp; Music Preparation{yr}</div>")
    # the signature rides the horizon, as the seal does on the leaf
    w.append(f"<div class='sig' style='left:{LX}in;top:{HORIZON + 0.22}in'>{sig}</div>")

    css = f"""
.page {{ background:{BOARD}; color:{INK}; }}
.art {{ position:absolute; left:0; top:0; }}
.a, .v, .cr, .kt, .inst, .sig, .flag, .seal {{ position:absolute; }}
.v {{ writing-mode:vertical-rl; text-orientation:upright; white-space:nowrap;
      font-family:'Noto Serif CJK SC'; text-align:center; }}
.title {{ font-size:{T_SIZE}in; font-weight:900; letter-spacing:{T_STEP - T_SIZE}in;
          color:{INK}; text-align:start; }}
.trad {{ font-size:13pt; font-weight:600; letter-spacing:.15em; text-align:start; color:{INK};
         display:flex; flex-direction:row; justify-content:space-between; align-items:center; }}
.trad .it {{ display:block; line-height:{CW}in; }}
.trad .lab {{ font-size:9.5pt; color:{CIN}; letter-spacing:.06em; margin-top:.12em;
              display:inline-block; font-weight:400; }}
.lyric {{ font-family:'LXGW WenKai'; font-size:15pt; letter-spacing:.34em; color:{SEA};
          text-align:start; }}
.sub {{ font-size:12.5pt; font-weight:400; letter-spacing:.22em; color:{INK}; }}
.sub .dot {{ color:{CIN}; }}
.bx {{ font-size:10.5pt; font-weight:600; letter-spacing:.34em; text-align:start; }}
.bxs {{ font-weight:400; color:{INK2}; margin-top:.8em; display:inline-block; }}
.bxk {{ font-size:8.5pt; font-weight:500; letter-spacing:.28em; color:{INK2}; text-align:start; }}
.stone {{ position:absolute; left:0; top:0; display:block; }}
.sc {{ position:absolute; display:flex; align-items:center; justify-content:center;
       font-family:'Noto Sans CJK SC'; font-weight:700; color:{LEAF}; line-height:1; }}
.sc i {{ font-style:normal; display:inline-block; }}

.fs {{ font-family:'EB Garamond'; font-weight:500; font-size:17pt;
       letter-spacing:.36em; text-transform:uppercase; line-height:1; }}
.fs2 {{ font-family:'EB Garamond'; font-size:7.5pt; letter-spacing:.3em;
        text-transform:uppercase; color:{INK2}; }}
.ht {{ font-family:'Noto Serif CJK SC'; font-weight:700; font-size:25pt; letter-spacing:.1em;
       line-height:1; }}
.pin {{ font-family:'EB Garamond'; font-style:italic; font-size:15pt;
        letter-spacing:.03em; color:{CIN}; }}
.suben {{ font-family:'EB Garamond'; font-style:italic; font-size:12pt; line-height:1.45;
          text-wrap:balance; }}
.suben b {{ display:block; font-style:normal; font-weight:400; font-size:7pt; letter-spacing:.28em;
            text-transform:uppercase; color:{INK2}; margin-bottom:.03in; }}
.cr {{ border-collapse:collapse; }}
.cr td {{ border-bottom:.6pt solid {HAIR}; vertical-align:middle; padding:0; }}
.cr .zh {{ font-family:'Noto Serif CJK SC'; font-size:10.5pt; width:.56in; letter-spacing:.08em; }}
.cr .en {{ font-family:'EB Garamond'; font-size:7pt; letter-spacing:.24em; text-transform:uppercase; padding-top:.015in;
           color:{INK2}; }}
.cr .nm {{ font-family:'Noto Serif CJK SC'; font-weight:600; font-size:11.5pt; text-align:right;
           letter-spacing:.06em; }}
.kt {{ display:flex; justify-content:space-between; }}
.kt div {{ display:flex; flex-direction:column; gap:.05in; }}
.kt b, .inst b {{ font-family:'EB Garamond'; font-weight:400; font-size:7pt; letter-spacing:.26em;
         text-transform:uppercase; color:{INK2}; }}
.kt span {{ font-family:'EB Garamond','Noto Serif CJK SC'; font-size:11pt; }}
.inst b {{ display:block; margin-bottom:.05in; }}
.inst div {{ display:flex; justify-content:space-between; align-items:baseline; padding:.02in 0; }}
.inst .en {{ font-family:'EB Garamond'; font-size:11pt; }}
.inst .zh {{ font-family:'Noto Serif CJK SC'; font-size:10pt; color:{INK2}; letter-spacing:.08em; }}
.sig .n {{ font-family:'Noto Serif CJK SC'; font-weight:600; font-size:15pt; letter-spacing:.3em; }}
.sig .r {{ font-family:'EB Garamond'; font-size:7pt; letter-spacing:.2em; text-transform:uppercase;
           color:{INK2}; margin-top:.07in; }}
"""
    return lib.page(css, "".join(body) + "".join(w), "lv")
