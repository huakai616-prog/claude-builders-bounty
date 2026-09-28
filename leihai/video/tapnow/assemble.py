#!/usr/bin/env python3
"""《泪海》×《等潮》：把 TapNow 生成的镜头按 MP3 的时间拼成抖音竖屏成片（A2 版式）。

    python3 assemble.py --check                              # 看 clips/ 里有哪些镜头、缺哪些
    python3 assemble.py --audio 泪海.mp3                      # 出全片 → out/泪海_等潮_竖屏.mp4
    python3 assemble.py --audio 泪海.mp3 --from 55 --to 70    # 只出一段，快速检查

画面从上到下：
    0–930    镜头（TapNow 生成的视频，裁成 1080×930，最下面 140 像素淡进纸色）
    880      歌词，唱到的字变成赭红色
    1000–1480 四行弦乐谱，跟着音乐滚动（纸色底、手绘抖动）
    1482–1570 署名，编配者一行突出
镜头文件放在 clips/，文件名以镜头号开头：S01.mp4、S07_第二版.mov、S20.png 都可以。
缺的镜头：可省镜头借用 shots.py 里指定的镜头，其余显示占位卡（写着镜头号和画面），所以随时都能出一版看节奏。
需要 python3（numpy、Pillow）和 ffmpeg。镜头自带的声音一律不用，只用 --audio 给的 MP3。
"""
import argparse
import json
import math
import pathlib
import re
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import shots as SH

HERE = SH.HERE
ASSETS = HERE / 'assets'
W, H, FPS = 1080, 1920, 24
ART_H, FADE_FROM, FADE_TO = 930, 790, 930
PAPER = (246, 239, 227)
INK = (70, 60, 52)
TERRA = (200, 100, 63)
GREY = (138, 129, 119)
LIGHT = (214, 205, 193)
TIMING = SH.TIMING
END = SH.END
NFRAMES = TIMING['video']['frames']
VIDEO_EXT = {'.mp4', '.mov', '.m4v', '.webm', '.mkv'}
IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp'}

# 画面上所有固定文字（make_fonts.py 按这些字裁字库）
CAPTION = '他走的那天，把围巾留给了它'
CAPTION_UNTIL = 5.2
CREDITS = [('泪海 · 弦乐四重奏版', 21, 'Regular', GREY, 1482),
           ('弦乐编配　花开当富贵', 32, 'Bold', INK, 1507),
           ('原唱 许茹芸 · 翻唱 小梅 · 词 许常德、李忠屏 · 曲 李忠屏', 18, 'Regular', GREY, 1550)]
LABELS = ['小提琴 I', '小提琴 II', '中提琴', '大提琴']
CARD_TEXT = '★必做☆可省借用音乐占位画面用生成后放进文件名秒'


# ---------------------------------------------------------------- 字体
def font(size, weight='Regular'):
    return ImageFont.truetype(str(ASSETS / f'NotoSerifSC-{weight}-subset.otf'), size)


def card_font(size, bold=False):
    """占位卡用系统里的完整中文字体（改了 shots.py 的文字也不会缺字），没有就用仓库里的子集字库。"""
    cands = [('/usr/share/fonts/opentype/noto/NotoSerifCJK-%s.ttc' % ('Bold' if bold else 'Regular'), 2),
             ('/System/Library/Fonts/PingFang.ttc', 0),
             ('/System/Library/Fonts/STHeiti Medium.ttc', 0),
             ('/System/Library/Fonts/Supplemental/Songti.ttc', 0)]
    for path, idx in cands:
        if pathlib.Path(path).exists():
            return ImageFont.truetype(path, size, index=idx)
    return font(size, 'Bold' if bold else 'Regular')


# ---------------------------------------------------------------- 纸、谱、歌词
def paper():
    rng = np.random.default_rng(7)
    noise = np.clip(rng.normal(128, 12, (H, W)), 0, 255)
    p = np.array(PAPER, np.float32) * (1 - 0.035) + noise[..., None] * 0.035
    return p.astype(np.uint8)


def handdrawn(a, seed):
    """轻微的手绘抖动（和示意图同一种做法），a 是 0–255 的灰度数组，255 = 纸。"""
    h, w = a.shape
    rng = np.random.default_rng(seed)

    def field():
        f = Image.fromarray((rng.random((h // 24 + 2, w // 24 + 2)) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        return (np.asarray(f, dtype=np.float32) / 255 - 0.5) * 2.4
    dx, dy = field(), field()
    yy, xx = np.mgrid[0:h, 0:w]
    sx = np.clip(np.rint(xx + dx), 0, w - 1).astype(np.int32)
    sy = np.clip(np.rint(yy + dy), 0, h - 1).astype(np.int32)
    out = Image.fromarray(a[sy, sx].astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.55))
    return np.asarray(out, dtype=np.float32)


class Score:
    """四行弦乐谱：MuseScore 排出的一长条谱，按小节时间滚动，播放线固定在 x=play。"""
    STAFF_MID = [75, 187.5, 297.5, 402.5]   # 长条里每行谱第三线的 y
    HEADER_W = 49                            # 谱号 + 调号的宽度
    U_PER_PX, CROP_X, PAD = 32.72, 11, 1400

    def __init__(self, space=12.0, band_px=55, x0=250, x1=885, play=432, fade=70, centers=(1085, 1200, 1315, 1430)):
        self.x0, self.x1, self.play, self.centers = x0, x1, play, centers
        self.sc = sc = space / 8.25
        strip = Image.open(ASSETS / 'score_strip.png').convert('L')
        big0 = strip.resize((int(strip.width * sc), int(strip.height * sc)), Image.LANCZOS)
        big = Image.new('L', (big0.width + 2 * self.PAD, big0.height), 255)
        big.paste(big0, (self.PAD, 0))
        big = np.asarray(big, dtype=np.uint8)
        self.band = band = int(band_px * sc)
        self.rows = []
        for k in range(4):
            sy = int(self.STAFF_MID[k] * sc)
            y0, y1 = max(0, sy - band - 4), min(big.shape[0], sy + band + 4)
            warped = handdrawn(big[y0:y1], seed=11 + k)
            self.rows.append(1.0 - warped[sy - band - y0: sy + band - y0] / 255.0)   # 1 = 墨
        mpos = [(float(a), float(b)) for a, b in re.findall(r'<element id="\d+" x="([\d.]+)" y="[\d.]+" sx="([\d.]+)"',
                                                               (ASSETS / 'score_strip.mpos').read_text())]
        self.bar_x = [x / self.U_PER_PX - self.CROP_X for x, _ in mpos] + [(mpos[-1][0] + mpos[-1][1]) / self.U_PER_PX - self.CROP_X]
        self.bar_t = [b['t'] for b in TIMING['bars']]
        width = x1 - x0
        m = np.ones(width, np.float32)
        m[width - fade:] = 1 - np.arange(fade) / fade
        self.fade = m[None, :]
        self.vfade = []                      # 每行谱上下边缘淡出，不留硬切的边
        for k in range(4):
            v = np.ones(2 * band, np.float32)
            v[:14] = np.linspace(0, 1, 14)
            tail = 44 if k == 3 else 14      # 大提琴下面让出署名的位置
            v[2 * band - tail:] = np.linspace(1, 0, tail)
            self.vfade.append(v[:, None])
        self.top_y, self.bot_y = centers[0] - int(7.2 * space), centers[-1] + int(3.6 * space)

    def strip_x(self, t):
        t = max(0.0, min(t, self.bar_t[-1]))
        for i in range(len(self.bar_t) - 1):
            if self.bar_t[i] <= t <= self.bar_t[i + 1]:
                f = (t - self.bar_t[i]) / (self.bar_t[i + 1] - self.bar_t[i])
                return self.bar_x[i] + f * (self.bar_x[i + 1] - self.bar_x[i])
        return self.bar_x[-1]

    def draw_static(self, img):
        """谱号、调号、声部名：不动的部分画进底图。"""
        hw = int(self.HEADER_W * self.sc)
        for k, cy in enumerate(self.centers):
            ink = self.rows[k][:, self.PAD:self.PAD + hw] * self.vfade[k]
            reg = img[cy - self.band:cy + self.band, self.x0 - hw - 12:self.x0 - 12].astype(np.float32)
            img[cy - self.band:cy + self.band, self.x0 - hw - 12:self.x0 - 12] = (reg * (1 - ink[..., None]) + np.array(INK) * ink[..., None]).astype(np.uint8)
        pil = Image.fromarray(img)
        d = ImageDraw.Draw(pil)
        for cy, name in zip(self.centers, LABELS):
            d.text((self.x0 - hw - 12 - 108, cy - 13), name, font=font(22), fill=GREY)
        img[:] = np.asarray(pil)

    def draw(self, img, t, strength=1.0):
        left = self.strip_x(t) * self.sc + self.PAD - (self.play - self.x0)
        i0 = int(math.floor(left))
        f = left - i0
        width = self.x1 - self.x0
        for k, cy in enumerate(self.centers):
            row = self.rows[k]
            ink = (row[:, i0:i0 + width] * (1 - f) + row[:, i0 + 1:i0 + 1 + width] * f) * self.fade * self.vfade[k] * strength
            reg = img[cy - self.band:cy + self.band, self.x0:self.x1].astype(np.float32)
            img[cy - self.band:cy + self.band, self.x0:self.x1] = (reg * (1 - ink[..., None]) + np.array(INK, np.float32) * ink[..., None]).astype(np.uint8)
        # 播放线和红点
        p = self.play
        col = np.array((200, 100, 63), np.float32)
        reg = img[self.top_y:self.bot_y, p - 1:p + 1].astype(np.float32)
        img[self.top_y:self.bot_y, p - 1:p + 1] = (reg * (1 - 0.43) + col * 0.43).astype(np.uint8)
        yy, xx = np.mgrid[-7:3, -5:6]
        dot = ((xx / 4.5) ** 2 + ((yy + 2) / 4.5) ** 2) <= 1
        sub = img[self.top_y - 7:self.top_y + 3, p - 5:p + 6]
        sub[dot] = (sub[dot] * 0.1 + np.array((205, 70, 55)) * 0.9).astype(np.uint8)


def strings_level(t):
    """弦乐全停（60.0–61.02 秒，只剩清唱）时谱面变淡。"""
    a, b = SH.EV('弦乐全停'), SH.EV('副歌 II')
    if a <= t < b:
        return 0.3 + 0.7 * max(0.0, 1 - (t - a) / 0.12)
    return 1.0


class Lyrics:
    Y, TOP, HGT = 880, 860, 110

    def __init__(self):
        self.lines = TIMING['lines']
        self.f = font(54, 'Medium')
        self.cache = {}
        n = len(self.lines)
        self.win = []   # 每句显示的起止，相邻两句直接换，不重叠
        for i, L in enumerate(self.lines):
            s = L['start'] - 0.35
            nxt = self.lines[i + 1]['start'] - 0.35 if i + 1 < n else None
            e = L['end'] + 0.45
            joined = nxt is not None and nxt <= e
            self.win.append([s, nxt if joined else e, joined])
        for i in range(1, n):
            self.win[i].append(self.win[i - 1][2])   # 前一句是不是直接换过来的

    def patch(self, i, sung):
        key = (i, sung)
        if key not in self.cache:
            text = self.lines[i]['text']
            im = Image.new('RGBA', (W, self.HGT), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            x = (W - d.textlength(text, font=self.f)) / 2
            for j, ch in enumerate(text):
                d.text((x, self.Y - self.TOP), ch, font=self.f, fill=TERRA + (255,) if j < sung else LIGHT + (255,))
                x += d.textlength(ch, font=self.f)
            a = np.asarray(im, dtype=np.float32)
            self.cache[key] = (a[..., :3], a[..., 3:] / 255.0)
        return self.cache[key]

    def draw(self, img, t):
        for i, w in enumerate(self.win):
            s, e, joined_next = w[0], w[1], w[2]
            joined_prev = w[3] if len(w) > 3 else False
            if s <= t < e:
                a_in = 1.0 if joined_prev else min(1.0, (t - s) / 0.25)
                a_out = 1.0 if joined_next else min(1.0, (e - t) / 0.25)
                sung = sum(1 for syl in self.lines[i]['syllables'] if syl['start'] <= t)
                rgb, al = self.patch(i, sung)
                al = al * a_in * a_out
                reg = img[self.TOP:self.TOP + self.HGT].astype(np.float32)
                img[self.TOP:self.TOP + self.HGT] = (reg * (1 - al) + rgb * al).astype(np.uint8)
                return


def caption_patch():
    im = Image.new('RGBA', (W, 170), (0, 0, 0, 0))
    f = font(50, 'Bold')
    d = ImageDraw.Draw(im)
    x = (W - d.textlength(CAPTION, font=f)) / 2
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x, 50), CAPTION, font=f, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    im = Image.alpha_composite(sh, im)
    ImageDraw.Draw(im).text((x, 50), CAPTION, font=f, fill=(251, 246, 238, 255))
    a = np.asarray(im, dtype=np.float32)
    return a[..., :3], a[..., 3:] / 255.0


def douyin_zones(img):
    pil = Image.fromarray(img)
    d = ImageDraw.Draw(pil, 'RGBA')
    for x0, y0, x1, y1 in [(2, 2, W - 3, 170), (905, 880, W - 3, 1545), (2, 1575, W - 3, H - 3)]:
        d.rectangle([x0, y0, x1, y1], outline=(200, 40, 40, 160), width=2)
    img[:] = np.asarray(pil)


# ---------------------------------------------------------------- 镜头
def probe(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height:format=duration',
                          '-of', 'json', str(path)], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    st = j['streams'][0]
    return st['width'], st['height'], float(j['format']['duration'])


def find_file(clips, sid):
    if not clips.exists():
        return None
    for p in sorted(clips.iterdir()):
        if re.match(sid + r'(?!\d)', p.name, re.I) and p.suffix.lower() in VIDEO_EXT | IMAGE_EXT:
            return p
    return None


def plan(clips):
    """每个镜头用什么画面：自己的片段 → 借用的片段 → 占位卡。"""
    ids = {s['id']: s for s in SH.SHOTS}
    out = []
    for s in SH.SHOTS:
        own = find_file(clips, s['id'])
        src = None
        if own:
            src = ('clip' if own.suffix.lower() in VIDEO_EXT else 'still', own, 0.0, s['id'])
        elif s['reuse']:
            rid, _, off = s['reuse'].partition('@')
            other = find_file(clips, rid)
            if other:
                src = ('clip' if other.suffix.lower() in VIDEO_EXT else 'still', other, float(off or 0), rid)
        if src is None:
            src = ('card', None, 0.0, s['id'])
        out.append(src)
    return out


def cover(w, h, focus):
    s = max(W / w, ART_H / h)
    sw, sh = math.ceil(w * s), math.ceil(h * s)
    return sw, sh, int((sw - W) * focus[0]), int((sh - ART_H) * focus[1])


def card(s):
    top, bot = [np.array(Image.new('RGB', (1, 1), c).getpixel((0, 0)), np.float32) for c in s['pal']]
    g = np.linspace(0, 1, ART_H)[:, None, None]
    img = Image.fromarray((top * (1 - g) + bot * g + np.zeros((1, W, 3))).astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle([0, 0, W, ART_H], fill=(10, 10, 20, 70))
    tag = '★ 必做' if s['must'] else ('借用' if s['kind'] == 'reuse' else '☆ 可省')
    d.text((72, 356), s['id'], font=card_font(72, True), fill=(255, 255, 255, 240))
    d.text((250, 382), f"{tag}　{SH.mmss(s['t0'])}–{SH.mmss(s['t1'])}　{s['t1'] - s['t0']:.1f} 秒", font=card_font(32), fill=(255, 255, 255, 235))
    d.text((74, 462), '音乐：' + s['music'], font=card_font(32), fill=(255, 255, 255, 225))
    f = card_font(42, True)
    y, line = 530, ''
    for ch in s['title']:
        if d.textlength(line + ch, font=f) > W - 150:
            d.text((74, y), line, font=f, fill=(255, 255, 255, 255))
            y += 62
            line = ''
        line += ch
    d.text((74, y), line, font=f, fill=(255, 255, 255, 255))
    d.text((74, 150), f"占位画面 · 用 TapNow 生成后放进 clips/，文件名 {s['id']}.mp4", font=card_font(24), fill=(255, 255, 255, 150))
    return np.asarray(img)


class ShotStream:
    """按帧号顺序给出一个镜头的画面（1080×930）。"""

    def __init__(self, s, src, nframes):
        self.s, self.kind, self.path, self.off, self.rid = s, src[0], src[1], src[2], src[3]
        self.n, self.k, self.last, self.proc = nframes, 0, None, None
        if self.kind == 'card':
            self.last = card(s)
        elif self.kind == 'still':
            self.img = Image.open(self.path).convert('RGB')
        else:
            w, h, dur = probe(self.path)
            need = nframes / FPS
            avail = max(0.1, dur - self.off)
            speed = 1.0 if avail >= need else max(0.85, avail / need)
            sw, sh, cx, cy = cover(w, h, s['focus'])
            vf = f'setpts=PTS/{speed:.5f},fps={FPS},scale={sw}:{sh}:flags=lanczos,setsar=1,crop={W}:{ART_H}:{cx}:{cy},format=rgb24'
            self.log = tempfile.TemporaryFile()
            self.proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{self.off:.3f}', '-i', str(self.path), '-an', '-vf', vf,
                                          '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE, stderr=self.log)

    def next(self):
        k = self.k
        self.k += 1
        if self.kind == 'card':
            return self.last
        if self.kind == 'still':
            z = 1.0 + 0.06 * k / max(1, self.n - 1)
            w, h = self.img.size
            s = max(W / w, ART_H / h) * z
            im = self.img.resize((math.ceil(w * s), math.ceil(h * s)), Image.BILINEAR)
            x = int((im.width - W) * self.s['focus'][0])
            y = int((im.height - ART_H) * self.s['focus'][1])
            return np.asarray(im.crop((x, y, x + W, y + ART_H)))
        buf = self.proc.stdout.read(W * ART_H * 3) if self.proc else b''
        if len(buf) == W * ART_H * 3:
            self.last = np.frombuffer(buf, np.uint8).reshape(ART_H, W, 3)
        elif self.last is None:
            self.log.seek(0)
            sys.stderr.write(f"警告：{self.path.name} 读不出画面：{self.log.read().decode(errors='replace')[:300]}\n")
            self.last = card(self.s)
        return self.last

    def at(self, local):
        """跳到镜头内第 local 帧（只会往后跳）。"""
        while self.k < local:
            self.next()
        return self.next()

    def close(self):
        if self.proc:
            self.proc.stdout.close()
            self.proc.terminate()
            self.proc.wait()
            self.proc = None


def fade_mask():
    y = np.arange(ART_H, dtype=np.float32)
    a = np.clip(1 - (y - FADE_FROM) / (FADE_TO - FADE_FROM), 0, 1) ** 1.4
    return a[:, None, None]


# ---------------------------------------------------------------- 主流程
def frames_of(s):
    return round(s['t0'] * FPS), min(NFRAMES, round(s['t1'] * FPS))


def check(clips):
    probs = SH.check()
    for p in probs:
        print('分镜表有问题：', p)
    srcs = plan(clips)
    have = miss = 0
    for s, src in zip(SH.SHOTS, srcs):
        d = s['t1'] - s['t0']
        if src[0] == 'card':
            status = '缺 → 占位卡' if s['must'] else '缺（可省）→ 占位卡'
            miss += s['must']
        elif src[3] != s['id']:
            status = f'借用 {src[3]}（{src[1].name}，从第 {src[2]} 秒起）'
        else:
            have += 1
            status = f'✓ {src[1].name}'
            if src[0] == 'clip':
                _, _, dur = probe(src[1])
                status += f'（{dur:.1f} 秒）'
                if dur < d * 0.85:
                    status += f'  注意：比需要的 {d:.1f} 秒短太多，结尾会停在最后一帧'
        print(f"{s['id']}  {SH.mmss(s['t0'])}  {d:5.2f} 秒  {'必做' if s['must'] else '可省'}  {status}")
    print(f'\n已有 {have} 个镜头，必做镜头还缺 {miss} 个。clips 目录：{clips}')
    return not probs


def render(args):
    clips = pathlib.Path(args.clips)
    srcs = plan(clips)
    f_from = max(0, round(args.t_from * FPS))
    f_to = min(NFRAMES, round(args.t_to * FPS)) if args.t_to else NFRAMES
    base = paper()
    score = Score()
    score.draw_static(base)
    pil = Image.fromarray(base)
    d = ImageDraw.Draw(pil)
    for text, size, weight, col, y in CREDITS:
        d.text((76, y), text, font=font(size, weight), fill=col)
    base = np.asarray(pil).copy()
    lyrics, (cap_rgb, cap_a), mask = Lyrics(), caption_patch(), fade_mask()
    paper_top = base[:ART_H].astype(np.float32)

    spans = [frames_of(s) for s in SH.SHOTS]
    tails = [0] * len(SH.SHOTS)          # 下一个镜头叠化进来时，这个镜头要多给几帧
    for i, s in enumerate(SH.SHOTS[1:], 1):
        if s['enter'] == 'dissolve':
            tails[i - 1] = round(s['enter_len'] * FPS)
    streams = {}

    def stream(i):
        if i not in streams:
            f0, f1 = spans[i]
            streams[i] = ShotStream(SH.SHOTS[i], srcs[i], f1 - f0 + tails[i])
        return streams[i]

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    todo = range(f_from, f_to)
    if args.stills:
        todo = sorted({min(NFRAMES - 1, round(float(x) * FPS)) for x in args.stills.split(',')})
    t0, dur = f_from / FPS, (f_to - f_from) / FPS
    cmd = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
    if args.audio:
        cmd += ['-ss', f'{t0:.3f}', '-t', f'{dur:.3f}', '-i', args.audio, '-map', '0:v', '-map', '1:a', '-af', 'apad', '-shortest',
                '-c:a', 'aac', '-b:a', '256k']
    if args.scale != 1:
        cmd += ['-vf', f'scale={int(W * args.scale) // 2 * 2}:{int(H * args.scale) // 2 * 2}:flags=lanczos']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', str(args.crf), '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)]
    enc = None if args.stills else subprocess.Popen(cmd, stdin=subprocess.PIPE)

    i = 0
    for n in todo:
        t = n / FPS
        while spans[i][1] <= n:
            i += 1
        s = SH.SHOTS[i]
        f0 = spans[i][0]
        art = stream(i).at(n - f0).astype(np.float32)
        k = n - f0
        if s['enter'] == 'dissolve' and i > 0 and k < round(s['enter_len'] * FPS):
            w = (k + 1) / (round(s['enter_len'] * FPS) + 1)
            prev = stream(i - 1).at(n - spans[i - 1][0]).astype(np.float32)
            art = prev * (1 - w) + art * w
        elif s['enter'] == 'flash' and k < round(s['enter_len'] * FPS):
            w = ((k + 1) / (round(s['enter_len'] * FPS) + 1)) ** 0.7
            art = 255 * (1 - w) + art * w
        for j in [j for j in streams if spans[j][1] + tails[j] <= n]:
            streams.pop(j).close()
        fin = min(1.0, max(0.0, (END - t) / 2.5))           # 最后 2.5 秒画面淡出
        a = mask * fin
        img = base.copy()
        top = art * a + paper_top * (1 - a)
        if t < CAPTION_UNTIL:
            ca = cap_a * min(1.0, (CAPTION_UNTIL - t) / 0.6)
            top[170:340] = top[170:340] * (1 - ca) + cap_rgb * ca
        img[:ART_H] = top.astype(np.uint8)
        score.draw(img, t, strings_level(t))
        lyrics.draw(img, t)
        if args.zones:
            douyin_zones(img)
        if args.stills:
            png = out.with_name(f'{out.stem}_{t:06.2f}s.png')
            Image.fromarray(img).save(png)
            print('写入', png)
            continue
        enc.stdin.write(img.tobytes())
        if (n - f_from) % (FPS * 10) == 0:
            print(f'  {SH.mmss(t)}  {s["id"]}', flush=True)
    for st in streams.values():
        st.close()
    if enc:
        enc.stdin.close()
        if enc.wait() != 0:
            sys.exit('ffmpeg 编码失败，看上面的报错')
        print('写入', out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--clips', default=str(HERE / 'clips'), help='TapNow 片段所在的文件夹（默认 clips/）')
    ap.add_argument('--audio', help='你的《泪海》MP3（不给就出无声版）')
    ap.add_argument('--out', default=str(HERE / 'out' / '泪海_等潮_竖屏.mp4'))
    ap.add_argument('--from', dest='t_from', type=float, default=0.0, help='从第几秒开始（默认 0）')
    ap.add_argument('--to', dest='t_to', type=float, default=None, help='到第几秒结束（默认到结尾）')
    ap.add_argument('--scale', type=float, default=1.0, help='输出缩放，0.5 = 540×960 的预览')
    ap.add_argument('--crf', type=int, default=18, help='画质，越小越好（默认 18）')
    ap.add_argument('--zones', action='store_true', help='画出抖音界面会盖住的区域（检查用）')
    ap.add_argument('--stills', help='只导出这几个时间点的静帧（秒，逗号分隔），比如 --stills 23.5,60.5')
    ap.add_argument('--check', action='store_true', help='只检查，不渲染')
    args = ap.parse_args()
    if args.check:
        sys.exit(0 if check(pathlib.Path(args.clips)) else 1)
    probs = SH.check()
    if probs:
        sys.exit('分镜表有问题：\n' + '\n'.join(probs))
    render(args)


if __name__ == '__main__':
    main()
