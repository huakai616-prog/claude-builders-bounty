#!/usr/bin/env python3
"""Layout study frames (1080x1920) for the 抖音 cut that starts at 1:32.

The notation is the real score (strip/strip.svg from score_strip.py,
MuseJazz handwritten font), coloured like the user's earlier video: cream
paper, brown-black ink, grey staff lines, a faint playhead with a warm dot.
Every position comes from timing.json / strip.json, so a frame at time t
is exactly what the video will show at t.

    python3 frames.py            # all layouts -> frames/*.png
"""
import base64
import bisect
import html
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "frames")
SHELL = "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"
LONGCANG = os.environ.get(
    "LONGCANG_PKG", os.path.join(HERE, "proto", "F2_编曲手记", "fontpkg",
                                 "package"))
W, H = 1080, 1920

# colours sampled from the user's reference (甲乙丙丁 video, Inkpen2 score)
PAPER = "#F6EFE4"
INK = "#3E372F"
STAFF = "#ADA698"
BAR = "#736B60"
LABEL = "#847C74"
PLAY = "#E1D4C2"
DOT = "#B7775B"
CINNABAR = "#B3261E"
PENCIL = "#5A534B"

SINGERS = {"sop": ("周雨桐", "女高音"), "alt": ("刘蔓", "女低音"),
           "ten": ("程一帆", "男高音"), "bas": ("秦岳峰", "男低音")}
STRINGS = {"vn1": "小提琴 Ⅰ", "vn2": "小提琴 Ⅱ", "va": "中提琴", "vc": "大提琴"}
ROWS = ["sop", "alt", "ten", "bas", "vn1", "vn2", "va", "vc"]
CLIP_START = 92.273   # bar 41 downbeat, 「我的祖国和我」

T = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
S = json.load(open(os.path.join(HERE, "strip", "strip.json")))
SVG = open(os.path.join(HERE, "strip", "strip.svg"), encoding="utf-8").read()
SVG = SVG[SVG.index("<svg"):]
SVG = re.sub(r'<path class="" fill="#ffffff"[^>]*/>', "", SVG, count=1)
SVG = re.sub(r"<title>.*?</title>|<desc>.*?</desc>", "", SVG, flags=re.S)
HEADER_X0, HEADER_X1 = S["staff_x0"] - 4, 432.0   # clef + key signature

TMAP_T = [a for a, _ in S["tmap"]]
TMAP_X = [b for _, b in S["tmap"]]


def xmap(t):
    """Strip x (SVG px) of song time t: linear between engraved segments."""
    i = bisect.bisect_right(TMAP_T, t)
    if i == 0:
        return TMAP_X[0]
    if i >= len(TMAP_T):
        t0, x0 = TMAP_T[-1], TMAP_X[-1]
        return x0 + (t - t0) / (S["end"]["t"] - t0) * (S["width"] - 40 - x0)
    t0, t1, x0, x1 = TMAP_T[i - 1], TMAP_T[i], TMAP_X[i - 1], TMAP_X[i]
    return x0 + (t - t0) / (t1 - t0) * (x1 - x0)


def sounding(pid, t):
    return any(n["start"] <= t < n["end"] for n in T["parts"][pid]["notes"])


def line_at(t):
    """(text, chars) of the lyric line to show at t (current or next)."""
    ls = T["lines"]
    for k, l in enumerate(ls):
        nxt = ls[k + 1]["start"] if k + 1 < len(ls) else 1e9
        if l["start"] - 0.25 <= t < max(l["end"] + 0.6, min(nxt - 0.25, l["end"] + 3)):
            return l
    return next((l for l in ls if l["start"] > t), ls[-1])


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- fonts
def longcang_css(text):
    css_path = os.path.join(LONGCANG, "index.css")
    if not os.path.exists(css_path):
        return ""
    css = open(css_path, encoding="utf-8").read()
    out = []
    for blk in re.findall(r"@font-face \{(.*?)\}", css, re.S):
        f = re.search(r"url\(\./files/([^)]+\.woff2)\)", blk).group(1)
        rng = re.search(r"unicode-range: ([^;]+);", blk).group(1)
        spans = []
        for r_ in rng.split(","):
            a, _, b = r_.strip()[2:].partition("-")
            spans.append((int(a, 16), int(b or a, 16)))
        if any(any(a <= ord(ch) <= b for a, b in spans) for ch in set(text)):
            data = base64.b64encode(open(os.path.join(
                LONGCANG, "files", f), "rb").read()).decode()
            out.append("@font-face{font-family:'Long Cang';font-display:block;"
                       f"src:url(data:font/woff2;base64,{data}) format('woff2');"
                       f"unicode-range:{rng};}}")
    return "\n".join(out)


# ---------------------------------------------------------------- score
class Score:
    """A window onto the strip: fixed header (labels, clef, key) on the
    left, the body scrolled so that time t sits under the playhead."""

    def __init__(self, rows, x, y, w, gap, label_w, play_x, lyrics=True,
                 dim_silent=True, label_style="stack", top_pad=5.5,
                 bottom_pad=4.6, highlight=None):
        self.rows, self.x, self.y, self.w = rows, x, y, w
        self.s = gap / 24.8                       # screen px per SVG px
        self.label_w, self.play_x = label_w, play_x
        self.lyrics, self.dim_silent = lyrics, dim_silent
        self.label_style, self.highlight = label_style, highlight
        idx = [ROWS.index(r) for r in rows]
        st = S["staves"]
        self.top = st[idx[0]][0] - top_pad * 24.8
        self.bottom = st[idx[-1]][4] + bottom_pad * 24.8
        self.h = (self.bottom - self.top) * self.s
        self.hdr_w = (HEADER_X1 - HEADER_X0) * self.s

    def Y(self, svg_y):
        return (svg_y - self.top) * self.s

    def html(self, t):
        s, st = self.s, S["staves"]
        body_x = self.label_w + self.hdr_w
        tx = (self.play_x - self.x - body_x) - xmap(t) * s
        ty = -self.top * s
        out = [f'<div class="score" style="left:{self.x}px;top:{self.y}px;'
               f'width:{self.w}px;height:{self.h:.0f}px">']
        # header: clef + key, fixed
        out.append(f'<div class="clip" style="left:{self.label_w}px;top:0;'
                   f'width:{self.hdr_w:.1f}px;height:{self.h:.0f}px">'
                   f'<div class="hdr" style="transform:translate('
                   f'{-HEADER_X0 * s:.2f}px,{ty:.2f}px) scale({s:.5f})">'
                   f'{SVG}</div></div>')
        # body; engraved lyrics coloured by state
        css = []
        if self.lyrics:
            past = [i for i, p, a, e in S["lyrics"] if e <= t and p in self.rows]
            now = [i for i, p, a, e in S["lyrics"] if a <= t < e and p in self.rows]
            if past:
                css.append(",".join(f".body #{i}" for i in past)
                           + f"{{fill:{INK};opacity:.8}}")
            if now:
                css.append(",".join(f".body #{i}" for i in now)
                           + f"{{fill:{CINNABAR}}}")
        out.append(f'<style>{"".join(css)}</style>'
                   f'<div class="clip fade" style="left:{body_x:.1f}px;top:0;'
                   f'width:{self.w - body_x:.1f}px;height:{self.h:.0f}px">'
                   f'<div class="body" style="transform:translate({tx:.2f}px,'
                   f'{ty:.2f}px) scale({s:.5f})">{SVG}</div></div>')
        # silent rows fade (body only)
        if self.dim_silent:
            for pid in self.rows:
                if sounding(pid, t):
                    continue
                k = ROWS.index(pid)
                y0 = self.Y(st[k][0] - 3.2 * 24.8)
                y1 = self.Y(st[k][4] + (4.2 if pid in SINGERS else 2.4) * 24.8)
                out.append(f'<div class="veil" style="left:{body_x:.0f}px;top:{y0:.0f}px;'
                           f'width:{self.w - body_x:.0f}px;height:{y1 - y0:.0f}px"></div>')
        if self.highlight:
            k = ROWS.index(self.highlight)
            y0 = self.Y(st[k][0] - 1.6 * 24.8)
            y1 = self.Y(st[k][4] + 4.0 * 24.8)
            out.append(f'<div class="band" style="left:{body_x:.0f}px;top:{y0:.0f}px;'
                       f'width:{self.w - body_x:.0f}px;height:{y1 - y0:.0f}px"></div>')
        # labels
        for pid in self.rows:
            k = ROWS.index(pid)
            cy = self.Y((st[k][0] + st[k][4]) / 2)
            on = sounding(pid, t)
            if pid in SINGERS:
                name, role = SINGERS[pid]
                if self.label_style == "stack":
                    out.append(f'<div class="lab singer{" on" if on else ""}" '
                               f'style="top:{cy:.0f}px;width:{self.label_w - 10}px">'
                               f'<b>{name}</b><i>{role}</i></div>')
                else:
                    out.append(f'<div class="lab{" on" if on else ""}" '
                               f'style="top:{cy:.0f}px;width:{self.label_w - 10}px">'
                               f'{role}</div>')
            else:
                out.append(f'<div class="lab{" on" if on else ""}" '
                           f'style="top:{cy:.0f}px;width:{self.label_w - 10}px">'
                           f'{STRINGS[pid]}</div>')
        out.append('</div>')
        # playhead
        out.append(f'<div class="play" style="left:{self.play_x - 1.5:.1f}px;'
                   f'top:{self.y - 8}px;height:{self.h + 8:.0f}px"></div>'
                   f'<div class="dot" style="left:{self.play_x - 5:.1f}px;'
                   f'top:{self.y - 14}px"></div>')
        return "".join(out)


# ---------------------------------------------------------------- page
BASE_CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden;background:{PAPER}}}
body{{position:relative;font-family:'Noto Sans CJK SC',sans-serif;color:{INK}}}
.paper{{position:absolute;inset:0;background:
 radial-gradient(ellipse 900px 700px at 22% 8%,rgba(255,244,220,.55),transparent 70%),
 radial-gradient(ellipse 140% 110% at 50% 45%,transparent 60%,rgba(120,98,70,.16) 100%);}}
.grain{{position:absolute;inset:0;opacity:.09;mix-blend-mode:multiply}}
.score{{position:absolute}}
.clip{{position:absolute;overflow:hidden}}
.fade{{-webkit-mask-image:linear-gradient(90deg,transparent 0,#000 30px)}}
.hdr,.body{{position:absolute;left:0;top:0;transform-origin:0 0;width:{S['width']}px;height:{S['height']}px}}
.score svg path{{fill:{INK}}}
.score svg polyline{{stroke:{INK}}}
.score svg .StaffLines{{stroke:{STAFF};stroke-width:2.2px}}
.score svg .BarLine{{stroke:{BAR};stroke-width:5.2px}}
.score svg .LedgerLine{{stroke:{STAFF}}}
.score svg .StaffText path,.score svg .Text path{{fill:{PENCIL}}}
.score svg .Lyrics{{fill:{LABEL}}}
.score svg .LyricsLineSegment{{stroke:{STAFF}}}
.hdr svg .TimeSig{{display:none}}
.lyr{{position:absolute;left:0;top:0}}
.ly{{position:absolute;transform:translate(-50%,0);font-size:var(--fs);line-height:1;
 font-family:'Noto Sans CJK SC';font-weight:400;color:{LABEL};white-space:nowrap}}
.ly.past{{color:{INK};opacity:.78}}
.ly.now{{color:{CINNABAR};font-weight:700}}
.ly.next{{opacity:.55}}
.veil{{position:absolute;background:{PAPER};opacity:.62;
 -webkit-mask-image:linear-gradient(180deg,transparent,#000 22px,#000 calc(100% - 22px),transparent)}}
.band{{position:absolute;background:rgba(179,38,30,.07)}}
.lab{{position:absolute;left:0;transform:translateY(-50%);text-align:right;
 font-size:22px;color:{LABEL};letter-spacing:1px;font-weight:350}}
.lab.singer b{{display:block;font-weight:500;font-size:27px;color:{INK};letter-spacing:2px;line-height:1.15}}
.lab.singer i{{display:block;font-style:normal;font-size:18px;color:{LABEL};letter-spacing:2px;margin-top:2px}}
.lab.singer:not(.on) b{{color:{LABEL}}}
.play{{position:absolute;width:3px;background:{PLAY};box-shadow:0 0 8px 1px rgba(255,248,236,.55)}}
.dot{{position:absolute;width:10px;height:10px;border-radius:50%;background:{DOT}}}
.t{{position:absolute;white-space:nowrap}}
.serif{{font-family:'Noto Serif CJK SC',serif}}
.hand{{font-family:'Long Cang','Noto Serif CJK SC',cursive}}
"""

GRAIN = ('<svg class="grain" width="1080" height="1920"><filter id="n">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" '
         'stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 .45  0 0 0 0 .38 '
         ' 0 0 0 0 .3  0 0 0 .9 0"/></filter><rect width="100%" height="100%" '
         'filter="url(#n)"/></svg>')


def lyric_line(t, y, size=64, x=None, gap=0):
    l = line_at(t)
    spans = []
    for c in l["chars"]:
        col = CINNABAR if c["start"] <= t else INK
        op = 1 if c["start"] <= t else .28
        spans.append(f'<span style="color:{col};opacity:{op}">{esc(c["char"])}</span>')
    pos = (f"left:{x}px" if x is not None else
           "left:0;width:1080px;text-align:center")
    return (f'<div class="t serif" style="{pos};top:{y}px;font-size:{size}px;'
            f'font-weight:600;letter-spacing:{gap}px">{"".join(spans)}</div>')


def page(body, text_for_fonts=""):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>'
            f'{longcang_css(text_for_fonts)}{BASE_CSS}</style></head><body>'
            f'<div class="paper"></div>{GRAIN}{body}</body></html>')


CREDIT_TEXT = "改编 · 制作人"
PRODUCER = "花开当富贵"
AI_LINE = "演唱 周雨桐 · 刘蔓 · 程一帆 · 秦岳峰"
WORK_LINE = "《我和我的祖国》 词 张藜 · 曲 秦咏诚 · 原唱 李谷一"


def credits_block(y, center=False):
    al = "left:0;width:1080px;text-align:center" if center else "left:60px"
    return (f'<div class="t" style="{al};top:{y}px;font-size:22px;color:{LABEL};'
            f'letter-spacing:1px">{WORK_LINE}</div>'
            f'<div class="t" style="{al};top:{y + 32}px;font-size:22px;'
            f'color:{LABEL};letter-spacing:1px">{AI_LINE}</div>')


def ai_tag(y=168, size=22):
    return ""


# ---------------------------------------------------------------- layouts
def v1(t):
    """手记·全谱：F2 的版式，换手写谱，声部名写歌手，署名放在右上。"""
    note = "第一小提琴高八度，陪着女高音唱"
    sc = Score(ROWS, 0, 428, W, 7.8, 150, 420)
    body = (ai_tag() +
            f'<div class="t" style="left:60px;top:196px;font-size:56px;'
            f'font-weight:700;color:{CINNABAR}">3<span style="font-size:28px;'
            f'opacity:.7">/5</span></div>'
            f'<div class="t" style="right:180px;top:200px;text-align:right">'
            f'<div style="font-size:21px;color:{LABEL};letter-spacing:3px">{CREDIT_TEXT}</div>'
            f'<div class="serif" style="font-size:40px;font-weight:700;letter-spacing:4px;'
            f'margin-top:2px">{PRODUCER}</div></div>'
            + lyric_line(t, 286, 66, gap=2) +
            f'<div class="t hand" style="left:62px;top:372px;font-size:40px;'
            f'color:{PENCIL};transform:rotate(-1.2deg)">{note}</div>'
            + sc.html(t) + credits_block(1428))
    return page(body, note + "0123456789")


def v2(t):
    """人声四行：只放四位歌手的谱，放大到手机上看得清。"""
    sc = Score(["sop", "alt", "ten", "bas"], 0, 468, W, 13.6, 186, 480,
               top_pad=5.0, bottom_pad=6.2)
    body = (ai_tag() +
            f'<div class="t" style="left:0;width:1080px;top:196px;text-align:center">'
            f'<span style="font-size:22px;color:{LABEL};letter-spacing:4px">{CREDIT_TEXT}　</span>'
            f'<span class="serif" style="font-size:38px;font-weight:700;letter-spacing:4px">{PRODUCER}</span></div>'
            + lyric_line(t, 272, 70, gap=4) +
            f'<div class="t" style="left:0;width:1080px;top:376px;text-align:center;'
            f'font-size:24px;color:{LABEL};letter-spacing:6px">四声部独唱 · 弦乐四重奏</div>'
            + sc.html(t) + credits_block(1426, center=True))
    return page(body)


def v3(t):
    """歌手名牌：上面四张名牌（在唱的亮），下面全谱，品牌放最上面。"""
    cards = []
    for i, pid in enumerate(["sop", "alt", "ten", "bas"]):
        name, role = SINGERS[pid]
        on = sounding(pid, t)
        cx = 60 + i * 210
        cards.append(
            f'<div class="t" style="left:{cx}px;top:318px;width:196px;height:104px;'
            f'border:1.5px solid {INK if on else STAFF};border-radius:4px;'
            f'background:{"rgba(255,251,243,.75)" if on else "transparent"};'
            f'text-align:center;padding-top:14px">'
            f'<div class="serif" style="font-size:34px;font-weight:600;letter-spacing:3px;'
            f'color:{INK if on else LABEL}">{name}</div>'
            f'<div style="font-size:18px;color:{CINNABAR if on else LABEL};letter-spacing:3px;'
            f'margin-top:6px">{role}</div>'
            f'<div style="position:absolute;left:0;right:0;bottom:-1.5px;height:4px;'
            f'background:{CINNABAR if on else "transparent"}"></div></div>')
    sc = Score(ROWS, 0, 540, W, 7.0, 132, 420, label_style="plain")
    body = (ai_tag() +
            f'<div class="t" style="left:60px;top:204px">'
            f'<span class="serif" style="font-size:46px;font-weight:700;letter-spacing:5px">{PRODUCER}</span>'
            f'<span style="font-size:24px;color:{LABEL};letter-spacing:3px;margin-left:16px">'
            f'{CREDIT_TEXT}</span></div>'
            f'<div class="t" style="left:60px;top:270px;font-size:22px;color:{LABEL};'
            f'letter-spacing:2px">《我和我的祖国》四声部独唱 + 弦乐四重奏</div>'
            + "".join(cards) + lyric_line(t, 448, 58, gap=2)
            + sc.html(t) + credits_block(1436))
    return page(body)


def v4(t):
    """片头 / 封面：视频第一帧（歌曲 1:32），先交代「浪花和大海」。"""
    hook = "女声是浪花，男声是大海"
    sc = Score(["sop", "alt", "ten", "bas"], 0, 846, W, 8.8, 150, 420,
               bottom_pad=6.0)
    lineup = "".join(
        f'<div style="display:inline-block;margin:0 18px;text-align:center">'
        f'<div class="serif" style="font-size:32px;font-weight:600;letter-spacing:2px">{SINGERS[p][0]}</div>'
        f'<div style="font-size:18px;color:{LABEL};letter-spacing:3px;margin-top:4px">{SINGERS[p][1]}</div></div>'
        for p in ["sop", "alt", "ten", "bas"])
    body = (
        f'<div class="t" style="left:60px;top:166px;font-size:30px;font-weight:500;'
        f'color:{INK};border:2px solid {INK};padding:6px 14px;border-radius:4px;'
        f'height:66px;line-height:50px">演唱由 AI 生成</div>'
        f'<div class="t serif" style="left:0;width:1080px;top:262px;text-align:center;'
        f'font-size:104px;font-weight:700;letter-spacing:10px">我和我的祖国</div>'
        f'<div class="t hand" style="left:0;width:1080px;top:404px;text-align:center;'
        f'font-size:54px;color:{CINNABAR};transform:rotate(-1deg)">{hook}</div>'
        f'<div class="t" style="left:0;width:1080px;top:506px;text-align:center">'
        f'<span style="font-size:24px;color:{LABEL};letter-spacing:4px">{CREDIT_TEXT}　</span>'
        f'<span class="serif" style="font-size:46px;font-weight:700;letter-spacing:5px">{PRODUCER}</span></div>'
        f'<div class="t" style="left:0;width:1080px;top:600px;text-align:center">{lineup}</div>'
        f'<div class="t" style="left:0;width:1080px;top:716px;text-align:center;font-size:22px;'
        f'color:{LABEL};letter-spacing:5px">四声部独唱 · 弦乐四重奏</div>'
        + lyric_line(t, 758, 44, gap=2)
        + sc.html(t) + credits_block(1440, center=True))
    return page(body, hook)


# ---------------------------------------------------------------- flag
FLAG_RED, FLAG_YELLOW = "#EE1C25", "#FFFF00"


def star(cx, cy, r, toward=None):
    """Five-pointed star; one point straight up, or aimed at `toward`."""
    import math
    a0 = (math.atan2(toward[1] - cy, toward[0] - cx) if toward
          else -math.pi / 2)
    ri = r * math.sin(math.radians(18)) / math.sin(math.radians(54))
    pts = []
    for k in range(10):
        rr = r if k % 2 == 0 else ri
        a = a0 + k * math.pi / 5
        pts.append(f"{cx + rr * math.cos(a):.3f},{cy + rr * math.sin(a):.3f}")
    return " ".join(pts)


def flag_svg(w):
    """The national flag to GB 12982: 3:2, the hoist-side quarter ruled
    15 x 10; big star centre (5,5) radius 3; small stars at (10,2) (12,4)
    (12,7) (10,9) radius 1, each with one point aimed at the big star's
    centre.  Drawn whole, flat, nothing on top of it."""
    u = w / 30
    stars = [f'<polygon fill="{FLAG_YELLOW}" points="{star(5 * u, 5 * u, 3 * u)}"/>']
    for x, y in [(10, 2), (12, 4), (12, 7), (10, 9)]:
        stars.append(f'<polygon fill="{FLAG_YELLOW}" points="'
                     f'{star(x * u, y * u, u, toward=(5 * u, 5 * u))}"/>')
    return (f'<svg style="display:block" width="{w:.0f}" height="{w * 2 / 3:.0f}" '
            f'viewBox="0 0 {w} {w * 2 / 3}">'
            f'<rect width="{w}" height="{w * 2 / 3}" fill="{FLAG_RED}"/>'
            f'{"".join(stars)}</svg>')


GOLD = "#C9A04A"


def final(t, deco="banner", credit="row"):
    """用户定稿的版式（10-01）：只放四个人声声部，不写 AI 标注，
    词曲原唱放大，背景加一点国旗元素。deco: banner 题头小旗 /
    handflag 手持小国旗 / redgold 红金点缀（不用国旗本体）。"""
    sc = Score(["sop", "alt", "ten", "bas"], 0, 846, W, 8.8, 150, 420,
               bottom_pad=6.0)
    lineup = "".join(
        f'<div style="display:inline-block;margin:0 18px;text-align:center">'
        f'<div class="serif" style="font-size:32px;font-weight:600;letter-spacing:2px">{SINGERS[p][0]}</div>'
        f'<div style="font-size:18px;color:{LABEL};letter-spacing:3px;margin-top:4px">{SINGERS[p][1]}</div></div>'
        for p in ["sop", "alt", "ten", "bas"])
    work = "".join(
        f'<span style="font-size:24px;color:{LABEL};letter-spacing:3px">{role}</span>'
        f'<span class="serif" style="font-size:38px;font-weight:600;letter-spacing:3px;'
        f'margin:0 30px 0 12px">{name}</span>'
        for role, name in [("作词", "张藜"), ("作曲", "秦咏诚"), ("原唱", "李谷一")])
    title_y = 262
    top = ""
    if deco == "banner":
        fw = 138
        top = (f'<div class="t" style="left:{(W - fw) / 2:.0f}px;top:152px;'
               f'box-shadow:0 2px 6px rgba(60,40,20,.18)">{flag_svg(fw)}</div>')
        title_y = 266
    elif deco == "handflag":
        fw = 150
        top = (f'<div class="t" style="left:66px;top:150px;width:7px;height:250px;'
               f'border-radius:3px;background:linear-gradient(90deg,#8a6a3c,#c9a26a,#8a6a3c)"></div>'
               f'<div class="t" style="left:62px;top:141px;width:15px;height:15px;'
               f'border-radius:50%;background:radial-gradient(circle at 35% 35%,#f4dc9c,{GOLD} 60%,#8a6a2c)"></div>'
               f'<div class="t" style="left:73px;top:158px;box-shadow:2px 3px 6px rgba(60,40,20,.2)">'
               f'{flag_svg(fw)}</div>')
    elif deco == "redgold":
        orn = (f'<svg width="560" height="60" viewBox="0 0 560 60">'
               f'<line x1="0" y1="30" x2="236" y2="30" stroke="{GOLD}" stroke-width="2"/>'
               f'<line x1="324" y1="30" x2="560" y2="30" stroke="{GOLD}" stroke-width="2"/>'
               f'<polygon fill="{FLAG_RED}" points="{star(280, 32, 26)}"/>'
               f'<polygon fill="{GOLD}" points="{star(248, 30, 7)}"/>'
               f'<polygon fill="{GOLD}" points="{star(312, 30, 7)}"/></svg>')
        sprinkle = "".join(
            f'<polygon fill="{GOLD}" opacity="{o}" points="{star(x, y, r)}"/>'
            for x, y, r, o in [(120, 250, 9, .35), (955, 205, 7, .3), (90, 560, 6, .25),
                               (990, 470, 10, .3), (170, 700, 5, .22), (930, 690, 6, .25)])
        top = (f'<div class="t" style="left:0;top:0;width:1080px;height:900px;'
               f'background:radial-gradient(ellipse 760px 560px at 50% 18%,'
               f'rgba(238,28,37,.10),rgba(238,28,37,.03) 55%,transparent 75%)"></div>'
               f'<svg class="t" style="left:0;top:0" width="1080" height="900">'
               f'<polygon fill="{GOLD}" fill-opacity=".06" stroke="{GOLD}" stroke-opacity=".28" '
               f'stroke-width="3" points="{star(540, 470, 360)}"/>{sprinkle}</svg>'
               f'<div class="t" style="left:260px;top:180px">{orn}</div>')
        title_y = 266
    rule = (f'<div class="t" style="left:340px;top:{title_y + 128}px;width:400px;height:2px;'
            f'background:linear-gradient(90deg,transparent,{FLAG_RED if deco != "banner" else CINNABAR},transparent);opacity:.55"></div>')
    body = (
        top +
        f'<div class="t serif" style="left:0;width:1080px;top:{title_y}px;text-align:center;'
        f'font-size:104px;font-weight:700;letter-spacing:10px">我和我的祖国</div>'
        + rule +
        f'<div class="t" style="left:0;width:1080px;top:{title_y + 146}px;text-align:center;'
        f'padding-left:30px">{work}</div>'
        f'<div class="t" style="left:0;width:1080px;top:{title_y + 240}px;text-align:center">'
        f'<span style="font-size:24px;color:{LABEL};letter-spacing:4px">{CREDIT_TEXT}　</span>'
        f'<span class="serif" style="font-size:46px;font-weight:700;letter-spacing:5px">{PRODUCER}</span></div>'
        f'<div class="t" style="left:0;width:1080px;top:600px;text-align:center">{lineup}</div>'
        f'<div class="t" style="left:0;width:1080px;top:716px;text-align:center;font-size:22px;'
        f'color:{LABEL};letter-spacing:5px">四声部独唱 · 弦乐四重奏</div>'
        + lyric_line(t, 758, 44, gap=2)
        + sc.html(t))
    return page(body)



LAYOUTS = [
    ("E1_题头小旗", lambda t: final(t, "banner"), CLIP_START + 0.35),
    ("E2_手持小国旗", lambda t: final(t, "handflag"), CLIP_START + 0.35),
    ("E3_红金点缀", lambda t: final(t, "redgold"), CLIP_START + 0.35),
    ("E1_题头小旗_2m08副歌", lambda t: final(t, "banner"), 128.2),
    ("A_手记全谱", v1, 128.2), ("B_人声四行", v2, 128.2),
           ("B2_人声四行_1m46男低音", v2, 106.35),
           ("C_歌手名牌", v3, 128.2), ("D_片头封面", v4, CLIP_START + 0.35)]


def shoot(name, html_text):
    os.makedirs(OUT, exist_ok=True)
    hp = os.path.join(OUT, name + ".html")
    open(hp, "w", encoding="utf-8").write(html_text)
    png = os.path.join(OUT, name + ".png")
    subprocess.run([SHELL, "--no-sandbox", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={W},{H}",
                    "--virtual-time-budget=8000", f"--screenshot={png}",
                    "file://" + hp], check=True, timeout=180,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return png


def main():
    only = sys.argv[1:]
    for name, fn, t in LAYOUTS:
        if only and not any(name.startswith(o) for o in only):
            continue
        print(shoot(name, fn(t)))


if __name__ == "__main__":
    main()
