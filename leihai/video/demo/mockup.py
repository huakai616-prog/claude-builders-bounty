"""Vertical 1080x1920 layout mockups in the style of the previous (GPT-made) video."""
import json
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1080, 1920
PAPER = (246, 239, 227)
INK = (70, 60, 52)
TERRA = (200, 100, 63)
GREY = (138, 129, 119)
LIGHT = (214, 205, 193)
SERIF = '/usr/share/fonts/opentype/noto/NotoSerifCJK-{}.ttc'
TIMING = json.load(open('/home/user/claude-builders-bounty/leihai/video/timing.json', encoding='utf-8'))


def font(size, weight='Regular'):
    return ImageFont.truetype(SERIF.format(weight), size, index=2)


# ---- score strip: positions from MuseScore's measure map ----
STRIP = Image.open('full_strip.png').convert('L')
U_PER_PX, CROP_X = 32.72, 11
_mpos = [(float(a), float(b)) for a, b in re.findall(r'<element id="\d+" x="([\d.]+)" y="[\d.]+" sx="([\d.]+)"', open('full.mpos').read())]
BAR_X = [x / U_PER_PX - CROP_X for x, _ in _mpos] + [(_mpos[-1][0] + _mpos[-1][1]) / U_PER_PX - CROP_X]
BAR_T = [b['t'] for b in TIMING['bars']]
STAFF_MID = [75, 187.5, 297.5, 402.5]   # middle staff line of each staff in the strip
HEADER_W = 49                            # clef + key signature


def strip_x(t):
    t = max(0.0, min(t, BAR_T[-1]))
    for i in range(len(BAR_T) - 1):
        if BAR_T[i] <= t <= BAR_T[i + 1]:
            f = (t - BAR_T[i]) / (BAR_T[i + 1] - BAR_T[i])
            return BAR_X[i] + f * (BAR_X[i + 1] - BAR_X[i])
    return BAR_X[-1]


def handdrawn(ink):
    """Soft wobble + warm ink so the printed placeholder reads closer to the handwritten score."""
    a = np.asarray(ink, dtype=np.float32)
    h, w = a.shape
    rng = np.random.default_rng(4)
    def field():
        f = Image.fromarray((rng.random((h // 24 + 2, w // 24 + 2)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        return (np.asarray(f, dtype=np.float32) / 255 - 0.5) * 2.4
    dx, dy = field(), field()
    yy, xx = np.mgrid[0:h, 0:w]
    sx = np.clip(np.rint(xx + dx), 0, w - 1).astype(int); sy = np.clip(np.rint(yy + dy), 0, h - 1).astype(int)
    out = Image.fromarray(a[sy, sx].astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.55))
    return out


def score(cv, t, centers, labels=True, x0=250, x1=1010, play=432, alpha=1.0):
    sc = 14.0 / 8.25
    big0 = STRIP.resize((int(STRIP.width * sc), int(STRIP.height * sc)), Image.LANCZOS)
    PAD = 1400  # white margin so the scroll can run past either end of the strip
    big = Image.new('L', (big0.width + 2 * PAD, big0.height), 255); big.paste(big0, (PAD, 0))
    ink = Image.new('L', (W, H), 255)
    band = int(50 * sc)
    px = strip_x(t) * sc + PAD
    for k, cy in enumerate(centers):
        sy = int(STAFF_MID[k] * sc)
        row = big.crop((0, sy - band, big.width, sy + band))
        body = row.crop((int(px - (play - x0)), 0, int(px - (play - x0)) + (x1 - x0), row.height))
        # soft fade at the right end of the scrolling body
        m = Image.new('L', body.size, 255); d = ImageDraw.Draw(m)
        for i in range(60): d.line([(body.width - 60 + i, 0), (body.width - 60 + i, body.height)], fill=int(255 * (1 - i / 60)))
        ink.paste(Image.composite(body, Image.new('L', body.size, 255), m), (x0, cy - band))
        ink.paste(row.crop((PAD, 0, PAD + int(HEADER_W * sc), row.height)), (x0 - int(HEADER_W * sc) - 12, cy - band))
    ink = handdrawn(ink)
    if alpha < 1:
        ink = Image.eval(ink, lambda v: int(255 - (255 - v) * alpha))
    col = Image.new('RGB', (W, H), INK)
    cv.paste(col, (0, 0), Image.eval(ink, lambda v: 255 - v))
    d = ImageDraw.Draw(cv, 'RGBA')
    if labels:
        for (cy, name) in zip(centers, ['小提琴 I', '小提琴 II', '中提琴', '大提琴']):
            d.text((64, cy - 13), name, font=font(22), fill=GREY)
    d.line([(play, centers[0] - 70), (play, centers[-1] + 60)], fill=(200, 100, 63, 110), width=2)
    d.ellipse([play - 4, centers[0] - 76, play + 4, centers[0] - 68], fill=(205, 70, 55, 230))


def base(top_png, fade_from=790, fade_to=930):
    cv = Image.new('RGB', (W, H), PAPER)
    g = Image.effect_noise((W, H), 12).convert('L')
    cv = Image.blend(cv, Image.merge('RGB', [g, g, g]), 0.035)
    top = Image.open(top_png).convert('RGB')
    band = top.crop((0, 810, W, 840)).resize((W, 1)).resize((W, fade_to - 840)).filter(ImageFilter.GaussianBlur(6))
    ext = Image.new('RGB', (W, fade_to)); ext.paste(top, (0, 0)); ext.paste(band, (0, 840))
    mask = Image.new('L', (W, fade_to), 255); md = ImageDraw.Draw(mask)
    for y in range(fade_from, fade_to): md.line([(0, y), (W, y)], fill=int(255 * (1 - (y - fade_from) / (fade_to - fade_from)) ** 1.4))
    cv.paste(ext, (0, 0), mask)
    return cv


def lyric_at(t):
    for L in TIMING['lines']:
        if L['start'] - 0.2 <= t <= L['end'] + 0.3:
            return L['text'], sum(1 for s in L['syllables'] if s['start'] <= t)
    return None, 0


def lyric(cv, t, y=900, size=54):
    text, sung = lyric_at(t)
    if not text:
        return
    d = ImageDraw.Draw(cv); f = font(size, 'Medium')
    x = (W - d.textlength(text, font=f)) / 2
    for i, ch in enumerate(text):
        d.text((x, y), ch, font=f, fill=TERRA if i < sung else LIGHT); x += d.textlength(ch, font=f)


def douyin_zones(cv):
    d = ImageDraw.Draw(cv, 'RGBA')
    def dashed(box):
        x0, y0, x1, y1 = box
        for x in range(x0, x1, 18): d.line([(x, y0), (min(x + 9, x1), y0)], fill=(200, 40, 40, 150), width=2); d.line([(x, y1), (min(x + 9, x1), y1)], fill=(200, 40, 40, 150), width=2)
        for y in range(y0, y1, 18): d.line([(x0, y), (x0, min(y + 9, y1))], fill=(200, 40, 40, 150), width=2); d.line([(x1, y), (x1, min(y + 9, y1))], fill=(200, 40, 40, 150), width=2)
    for b in [(2, 2, W - 3, 170), (905, 880, W - 3, 1545), (2, 1575, W - 3, H - 3)]:
        dashed(b)
    d.text((14, 1582), '红虚线内：抖音界面大约会盖住', font=font(22), fill=(190, 40, 40, 200))
