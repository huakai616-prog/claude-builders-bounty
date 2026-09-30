#!/usr/bin/env python3
"""Overlay a rough 抖音 player UI on a frame to check what it covers.
usage: douyin_ui.py in.png out.png"""
import sys
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def main(src, dst):
    im = Image.open(src).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    f = lambda n, b=False: ImageFont.truetype(FB if b else F, n)
    # bottom scrim, caption, music line, nav bar
    for y in range(1380, 1920):
        a = int(min(1, (y - 1380) / 420) * 150)
        d.line([(0, y), (1080, y)], fill=(0, 0, 0, a))
    d.text((36, 1590), "@花开当富贵", font=f(34, True), fill=(255, 255, 255, 235))
    d.text((36, 1640), "《我和我的祖国》四声部独唱 + 弦乐四重奏｜改编", font=f(30), fill=(255, 255, 255, 225))
    d.text((36, 1682), "#我和我的祖国 #国庆节快乐 #弦乐四重奏 …展开", font=f(30), fill=(255, 255, 255, 225))
    d.text((36, 1740), "♪ 作品原声 - 花开当富贵", font=f(28), fill=(255, 255, 255, 215))
    d.text((36, 1776), "ⓘ 作者声明：内容由AI生成", font=f(24), fill=(255, 255, 255, 190))
    d.rectangle([0, 1830, 1080, 1920], fill=(18, 18, 18, 235))
    for i, t in enumerate(["首页", "朋友", "＋", "消息", "我"]):
        d.text((70 + i * 214, 1856), t, font=f(30, i == 0), fill=(255, 255, 255, 230))
    # right rail
    x = 1000
    d.ellipse([x - 44, 1010, x + 44, 1098], fill=(90, 80, 70, 230), outline=(255, 255, 255, 240), width=4)
    for y, lab in [(1180, "♥ 1.2w"), (1320, "… 2386"), (1450, "★ 5021"), (1580, "↗ 3108")]:
        d.ellipse([x - 36, y - 36, x + 36, y + 36], fill=(255, 255, 255, 170))
        d.text((x, y + 58), lab, font=f(24), fill=(255, 255, 255, 240), anchor="mm")
        d.text((x, y + 58), lab, font=f(24), fill=(60, 60, 60, 200), anchor="mm")
    d.ellipse([x - 40, 1700, x + 40, 1780], fill=(30, 30, 30, 230))
    # top tabs
    for y in range(0, 170):
        d.line([(0, y), (1080, y)], fill=(0, 0, 0, int((1 - y / 170) * 110)))
    d.text((40, 20), "9:41", font=f(28, True), fill=(255, 255, 255, 240))
    for i, t in enumerate(["经验", "同城", "关注", "商城", "推荐"]):
        d.text((250 + i * 120, 86), t, font=f(32, i == 4), fill=(255, 255, 255, 240 if i == 4 else 190))
    d.text((1000, 86), "⌕", font=f(40), fill=(255, 255, 255, 230))
    Image.alpha_composite(im, ov).convert("RGB").save(dst)


if __name__ == "__main__":
    main(*sys.argv[1:3])
