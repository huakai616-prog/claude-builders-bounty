# -*- coding: utf-8 -*-
"""F2《编曲手记》样帧 @ 55.10 s：生成自包含 HTML（纸+谱用 canvas，文字和铅笔用 SVG）。"""
import base64, math, random, os, json, re

HERE = os.path.dirname(os.path.abspath(__file__))
# 谱面图：从总谱 PDF 第 5 页 144dpi 裁出的第 25–28 小节、第 1–2 小节中提琴
FIN = os.path.join(HERE, 'assets')
# 手写字体 Long Cang（OFL）：npm pack @fontsource/long-cang 后解压到 fontpkg/（约 24 MB，不进仓库）
FONTPKG = os.environ.get('LONGCANG_PKG', os.path.join(HERE, 'fontpkg', 'package'))

def b64(p):
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()

SYS = b64(os.path.join(FIN, 'sys25.png'))
VA = b64(os.path.join(FIN, 'va_b1_2.png'))

# ---------- 几何：谱图坐标 -> 画布坐标 ----------
S_ = 0.92; OX = -20; OY = 400
def X(ix): return ix * S_ + OX
def Y(iy): return iy * S_ + OY
PX = 380                      # 播放线
SCORE_BOTTOM = Y(1060)        # ≈1375

INK = '#2A2A28'; RED = '#B3261E'; PENCIL = '#4B4A47'; MUTE = '#6E675B'
SERIF = "'Noto Serif CJK SC'"; SANS = "'Noto Sans CJK SC'"; HAND = "'Long Cang','Noto Serif CJK SC'"

# ---------- 手绘路径 ----------
def catmull(pts):
    d = 'M%.1f,%.1f' % pts[0]
    n = len(pts)
    for i in range(n - 1):
        p0 = pts[i - 1] if i > 0 else pts[i]
        p1 = pts[i]; p2 = pts[i + 1]
        p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += ' C%.1f,%.1f %.1f,%.1f %.1f,%.1f' % (c1 + c2 + p2)
    return d

def wobble_ellipse(cx, cy, rx, ry, start_deg, sweep_deg, jit, seed, step=14):
    r = random.Random(seed)
    pts = []
    n = int(sweep_deg / step) + 1
    ph = r.uniform(0, 6.28)
    for k in range(n + 1):
        t = math.radians(start_deg + sweep_deg * k / n)
        grow = 1 + 0.08 * (k / n)          # 手画的圈越画越外扩，首尾错开
        m = grow * (1 + 0.035 * math.sin(2 * t + ph))
        pts.append((cx + rx * m * math.cos(t) + r.uniform(-jit, jit),
                    cy + ry * m * math.sin(t) + r.uniform(-jit, jit)))
    return catmull(pts)

def wobble_quad(p0, c, p1, jit, seed, n=12):
    r = random.Random(seed)
    pts = []
    for k in range(n + 1):
        t = k / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]
        j = jit if 0 < k < n else 0
        pts.append((x + r.uniform(-j, j), y + r.uniform(-j, j)))
    return catmull(pts), pts

def arrow_head(tip, prev, length=14, spread=27, seed=3):
    r = random.Random(seed)
    ang = math.atan2(tip[1] - prev[1], tip[0] - prev[0])
    out = []
    for s in (-1, 1):
        a = ang + math.pi + s * math.radians(spread + r.uniform(-3, 3))
        L = length * r.uniform(0.9, 1.08)
        e = (tip[0] + L * math.cos(a), tip[1] + L * math.sin(a))
        mid = ((tip[0] + e[0]) / 2 + r.uniform(-.8, .8), (tip[1] + e[1]) / 2 + r.uniform(-.8, .8))
        out.append('M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f' % (e + mid + tip))
    return ' '.join(out)

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;')

# ---------- Long Cang（OFL）离线子集 ----------
def longcang_css(text):
    css = open(os.path.join(FONTPKG, 'index.css'), encoding='utf-8').read()
    out = []
    for blk in re.findall(r'@font-face \{(.*?)\}', css, re.S):
        f = re.search(r'url\(\./files/([^)]+\.woff2)\)', blk).group(1)
        rng = re.search(r'unicode-range: ([^;]+);', blk).group(1)
        spans = []
        for r_ in rng.split(','):
            a, _, b = r_.strip()[2:].partition('-')
            spans.append((int(a, 16), int(b or a, 16)))
        if any(any(a <= ord(ch) <= b for a, b in spans) for ch in set(text)):
            data = base64.b64encode(open(os.path.join(FONTPKG, 'files', f), 'rb').read()).decode()
            out.append("@font-face{font-family:'Long Cang';font-weight:400;font-display:block;"
                       "src:url(data:font/woff2;base64,%s) format('woff2');unicode-range:%s;}" % (data, rng))
    return '\n'.join(out)

def hand_text(txt, x0, y0, fs, rot, seed, fill=PENCIL, track=0.94, jit=1.0):
    """一个字一个字摆，带轻微高低、角度、大小差，像一笔笔写上去的。"""
    r = random.Random(seed)
    out = []
    x = x0
    for ch in txt:
        dy = r.uniform(-jit, jit) * 1.3
        a = r.uniform(-2.0, 2.0) * jit
        sc = r.uniform(0.95, 1.05)
        if ch == '，':
            # 手写逗号：一笔带钩的短撇，单独画，免得粘到下一个字
            bx, by = x + fs * 0.16, y0 - fs * 0.04 + dy
            out.append('<path d="M%.1f,%.1f q%.1f,%.1f %.1f,%.1f q%.1f,%.1f %.1f,%.1f" fill="none" stroke="%s" '
                       'stroke-width="3.4" stroke-linecap="round"/>'
                       % (bx, by - fs * 0.10, fs * 0.07, fs * 0.02, fs * 0.05, fs * 0.13, -fs * 0.02, fs * 0.08, -fs * 0.10, fs * 0.15, fill))
            x += fs * 0.52
            continue
        adv = fs * track
        out.append('<text x="%.1f" y="%.1f" transform="rotate(%.2f %.1f %.1f)" font-size="%.1f">%s</text>'
                   % (x, y0 + dy, a, x + fs * 0.5, y0 - fs * 0.35, fs * sc, esc(ch)))
        x += adv
    return ('<g transform="rotate(%.2f %.1f %.1f)" font-family="%s" fill="%s" filter="url(#graphite)">%s</g>'
            % (rot, x0, y0, HAND, fill, ''.join(out))), x

HAND_TEXTS = []
svg = []
A = svg.append

# ======== 顶部：计数 + 署名 ========
A('<g font-family="%s" font-weight="700" fill="%s">'
  '<text x="58" y="204" font-size="60" letter-spacing="-1">4</text>'
  '<text x="95" y="204" font-size="30" fill-opacity="0.5">/9</text></g>' % (SANS, RED))

A('<text x="900" y="198" text-anchor="end" font-family="%s" font-size="29" fill="%s">'
  '<tspan fill="%s" font-weight="400">弦乐 · 合唱改编：</tspan><tspan font-weight="600">花开当富贵</tspan></text>' % (SERIF, INK, MUTE))

# ======== 歌词大字 ========
sung = 4                      # 55.10 s：我 最 亲 已唱完，爱 正在唱（55.00–55.36）
lyric = '我最亲爱的祖国'
fs = 66; lx0 = 480 - fs * len(lyric) / 2; LY = 292
g = ['<g font-family="%s" font-weight="600" font-size="%d">' % (SERIF, fs)]
for i, ch in enumerate(lyric):
    if i < sung:
        g.append('<text x="%.1f" y="%d" fill="%s">%s</text>' % (lx0 + i * fs, LY, RED, ch))
    else:
        g.append('<text x="%.1f" y="%d" fill="%s" fill-opacity="0.26">%s</text>' % (lx0 + i * fs, LY, INK, ch))
g.append('</g>')
A(''.join(g))

# ======== 批注标题（铅笔手写）========
TITLE = '她开口的第一句，就是前奏中提琴那句'
HAND_TEXTS.append(TITLE)
t_svg, t_end = hand_text(TITLE, 60, 366, 46, -1.5, 31)
A(t_svg)

# ======== 左侧谱头：中文声部名 ========
names = [('女高音', 86, 'S'), ('女低音', 238, 'on'), ('男高音', 377, 'on'), ('男低音', 518, 'on'),
         ('小提琴一', 693, 'rest'), ('小提琴二', 794, 'on'), ('中提琴', 894, 'on'), ('大提琴', 995, 'on')]
g = ['<g font-family="%s" font-size="24" text-anchor="end" dominant-baseline="central">' % SANS]
for n, iy, st in names:
    y = Y(iy)
    if st == 'S':
        g.append('<text x="122" y="%.1f" font-weight="700" fill="%s">%s</text>' % (y, RED, n))
    else:
        op = 0.38 if st == 'rest' else 0.66
        g.append('<text x="122" y="%.1f" font-weight="500" fill="%s" fill-opacity="%.2f">%s</text>' % (y, INK, op, n))
g.append('</g>')
A(''.join(g))

# ======== 女高音歌词：唱过的实心朱砂，没唱到的空心 ========
sop_chars = [('我', 274.5), ('最', 311.5), ('亲', 385.5), ('爱', 423), ('的', 460), ('祖', 534.5), ('国', 658.5)]
sop_next = [('我', 891.5), ('永', 928.5), ('远', 965.5), ('紧', 1003), ('贴', 1040), ('着', 1077), ('你', 1151.5), ('的', 1189)]
SLY = Y(149.5) + 11
g = ['<g font-family="%s" font-weight="600" font-size="30" text-anchor="middle">' % SERIF]
for i, (ch, ix) in enumerate(sop_chars):
    x = X(ix)
    if i < sung:
        g.append('<text x="%.1f" y="%.1f" fill="%s">%s</text>' % (x, SLY, RED, ch))
    else:
        g.append('<text x="%.1f" y="%.1f" fill="#F7F1E6" stroke="%s" stroke-width="1.25" paint-order="fill">%s</text>' % (x, SLY, RED, ch))
for ch, ix in sop_next:
    g.append('<text x="%.1f" y="%.1f" fill="none" stroke="%s" stroke-width="1" stroke-opacity="0.38">%s</text>' % (X(ix), SLY, RED, ch))
g.append('</g>')
A(''.join(g))

# ======== 铅笔：圈住她的第一个音，箭头从「第一句」落下来 ========
note_x, note_y = X(274), Y(71)
circle1 = wobble_ellipse(note_x + 1, note_y - 1, 26, 21, -160, 374, 1.2, 11)
circle2 = wobble_ellipse(note_x + 2, note_y, 27.5, 22, -150, 340, 1.5, 12)
a0 = (300, 382); a1 = (note_x + 21, note_y - 21)
arrow_d, arrow_pts = wobble_quad(a0, (a0[0] - 6, a1[1] - 34), a1, 0.8, 5, n=8)
arrow_tip = arrow_head(arrow_pts[-1], arrow_pts[-3], 13, 28, 9)
A('<g fill="none" stroke="%s" stroke-linecap="round" stroke-linejoin="round" filter="url(#graphite)">'
  '<path d="%s" stroke-width="3"/>'
  '<path d="%s" stroke-width="1.2" stroke-opacity="0.5"/>'
  '<path d="%s" stroke-width="2.6"/>'
  '<path d="%s" stroke-width="2.6"/>'
  '</g>' % (PENCIL, circle1, circle2, arrow_d, arrow_tip))

# ======== 小卡片：第 1 小节中提琴 ========
VA_CROP_W = 500; VA_S = 0.8; VA_TOP = 7
CW = VA_CROP_W * VA_S + 28; CH = 158
cx0 = 900 - CW; cy0 = 944
va_x = cx0 + 14; va_y = cy0 + 38
va_h = (112 - VA_TOP) * VA_S
va_notes = [('我', 137), ('最', 166), ('亲', 232), ('爱', 262), ('的', 296), ('祖', 370), ('国', 470)]
A('<rect x="%.1f" y="%.1f" width="%.1f" height="%d" rx="6" fill="#FFFDF8" filter="url(#shadow)"/>' % (cx0, cy0, CW, CH))
A('<text x="%.1f" y="%.1f" font-family="%s" font-size="19" font-weight="500" fill="%s">前奏 0:00 · 中提琴</text>'
  % (cx0 + 16, cy0 + 28, SANS, PENCIL))
A('<text x="%.1f" y="%.1f" text-anchor="end" font-family="%s" font-size="17" fill="#9A9282">同一串音，低八度</text>'
  % (cx0 + CW - 16, cy0 + 28, SANS))
A('<svg x="%.1f" y="%.1f" width="%.1f" height="%.1f" viewBox="0 7 %d 105" preserveAspectRatio="none" overflow="hidden">'
  '<image href="%s" x="0" y="0" width="635" height="112" style="mix-blend-mode:multiply" opacity="0.9"/></svg>'
  % (va_x, va_y, VA_CROP_W * VA_S, va_h, VA_CROP_W, VA))
g = ['<g font-family="%s" font-weight="600" font-size="20" text-anchor="middle" fill="none" stroke="#8E8676" stroke-width="1.05">' % SERIF]
for ch, ix in va_notes:
    g.append('<text x="%.1f" y="%.1f">%s</text>' % (va_x + ix * VA_S, va_y + va_h + 24, ch))
g.append('</g>')
A(''.join(g))

# ======== 底部署名 ========
A('<g font-family="%s" font-size="25" fill="%s">'
  '<text x="60" y="1424">《我和我的祖国》　词 张藜 · 曲 秦咏诚 · 原唱 李谷一</text>'
  '<text x="60" y="1460">四位 ACE Studio AI 歌手演唱 · 谱面为本版真实总谱</text></g>' % (SANS, MUTE))

SVG = '\n'.join(svg)
cfg = dict(SYS=SYS, S=S_, OX=OX, OY=OY, PX=PX, NOTE=[X(425), Y(71)])

html = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
html = (html.replace('/*CFG*/', 'const CFG=' + json.dumps(cfg) + ';')
            .replace('<!--SVG-->', SVG)
            .replace('/*FONTS*/', longcang_css(''.join(HAND_TEXTS))))
open(os.path.join(HERE, 'frame.html'), 'w', encoding='utf-8').write(html)
print('ok', len(html) // 1024, 'KB')
