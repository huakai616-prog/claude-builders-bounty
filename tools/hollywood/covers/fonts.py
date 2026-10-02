#!/usr/bin/env python3
"""Fetch the open-licence (SIL OFL) fonts the cover studies use.

    python3 tools/hollywood/covers/fonts.py      # idempotent, quiet

Downloads into ~/.cache/hollywood-fonts (or $HOLLYWOOD_FONTS): Chinese
calligraphy and display faces, and Latin display families from the
google/fonts repository, plus LXGW WenKai.  Variable fonts are cut into
static weights (Chromium prints a variable font as Type 3 outlines), and
fonts.css is written next to them with one @font-face per file.
Noto Serif CJK SC / Noto Sans CJK SC come from the system (tools/setup.sh
installs fonts-noto-cjk; the extra weights are in fonts-noto-cjk-extra).
"""
import os
import sys
import urllib.parse
import urllib.request

CACHE = os.environ.get("HOLLYWOOD_FONTS",
                       os.path.expanduser("~/.cache/hollywood-fonts"))
GF = "https://raw.githubusercontent.com/google/fonts/main/ofl/"
LXGW = "https://github.com/lxgw/LxgwWenKai/releases/latest/download/"

# family -> files under google/fonts ofl/<dir>/
FILES = {
    "Ma Shan Zheng": ["mashanzheng/MaShanZheng-Regular.ttf"],
    "Zhi Mang Xing": ["zhimangxing/ZhiMangXing-Regular.ttf"],
    "Liu Jian Mao Cao": ["liujianmaocao/LiuJianMaoCao-Regular.ttf"],
    "Long Cang": ["longcang/LongCang-Regular.ttf"],
    "ZCOOL XiaoWei": ["zcoolxiaowei/ZCOOLXiaoWei-Regular.ttf"],
    "ZCOOL QingKe HuangYou": ["zcoolqingkehuangyou/ZCOOLQingKeHuangYou-Regular.ttf"],
    "EB Garamond": ["ebgaramond/EBGaramond[wght].ttf", "ebgaramond/EBGaramond-Italic[wght].ttf"],
    "Cormorant Garamond": ["cormorantgaramond/CormorantGaramond[wght].ttf",
                           "cormorantgaramond/CormorantGaramond-Italic[wght].ttf"],
    "Cormorant": ["cormorant/Cormorant[wght].ttf", "cormorant/Cormorant-Italic[wght].ttf"],
    "Playfair Display": ["playfairdisplay/PlayfairDisplay[wght].ttf",
                         "playfairdisplay/PlayfairDisplay-Italic[wght].ttf"],
    "Bodoni Moda": ["bodonimoda/BodoniModa[opsz,wght].ttf", "bodonimoda/BodoniModa-Italic[opsz,wght].ttf"],
    "GFS Didot": ["gfsdidot/GFSDidot-Regular.ttf"],
    "Libre Baskerville": ["librebaskerville/LibreBaskerville[wght].ttf",
                          "librebaskerville/LibreBaskerville-Italic[wght].ttf"],
    "Noto Serif Display": ["notoserifdisplay/NotoSerifDisplay[wdth,wght].ttf",
                           "notoserifdisplay/NotoSerifDisplay-Italic[wdth,wght].ttf"],
    "DM Serif Display": ["dmserifdisplay/DMSerifDisplay-Regular.ttf", "dmserifdisplay/DMSerifDisplay-Italic.ttf"],
    "Instrument Serif": ["instrumentserif/InstrumentSerif-Regular.ttf",
                         "instrumentserif/InstrumentSerif-Italic.ttf"],
    "Fraunces": ["fraunces/Fraunces[SOFT,WONK,opsz,wght].ttf", "fraunces/Fraunces-Italic[SOFT,WONK,opsz,wght].ttf"],
    "Abril Fatface": ["abrilfatface/AbrilFatface-Regular.ttf"],
    "Cinzel": ["cinzel/Cinzel[wght].ttf"],
    "Cinzel Decorative": ["cinzeldecorative/CinzelDecorative-Regular.ttf",
                          "cinzeldecorative/CinzelDecorative-Bold.ttf",
                          "cinzeldecorative/CinzelDecorative-Black.ttf"],
    "Marcellus": ["marcellus/Marcellus-Regular.ttf"],
    "Italiana": ["italiana/Italiana-Regular.ttf"],
    "Poiret One": ["poiretone/PoiretOne-Regular.ttf"],
    "Josefin Sans": ["josefinsans/JosefinSans[wght].ttf", "josefinsans/JosefinSans-Italic[wght].ttf"],
    "Jost": ["jost/Jost[wght].ttf", "jost/Jost-Italic[wght].ttf"],
    "Inter": ["inter/Inter[opsz,wght].ttf", "inter/Inter-Italic[opsz,wght].ttf"],
    "Archivo": ["archivo/Archivo[wdth,wght].ttf", "archivo/Archivo-Italic[wdth,wght].ttf"],
    "Archivo Black": ["archivoblack/ArchivoBlack-Regular.ttf"],
    "Space Grotesk": ["spacegrotesk/SpaceGrotesk[wght].ttf"],
    "Syne": ["syne/Syne[wght].ttf"],
    "Unbounded": ["unbounded/Unbounded[wght].ttf"],
    "Oswald": ["oswald/Oswald[wght].ttf"],
    "Bebas Neue": ["bebasneue/BebasNeue-Regular.ttf"],
    "Big Shoulders Display": ["bigshouldersdisplay/BigShouldersDisplay[wght].ttf"],
}
STATIC_WEIGHT = {"Regular": 400, "Medium": 500, "Bold": 700, "Black": 900}
# optical size for the static cuts: display sizes for the display faces
OPSZ_MAX = {"Bodoni Moda", "Fraunces"}


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        return dest
    tmp = dest + ".part"
    with urllib.request.urlopen(url, timeout=300) as r, open(tmp, "wb") as fh:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            fh.write(b)
    os.replace(tmp, dest)
    return dest


def faces(family, path):
    """[(weight, style, file)] for one downloaded file; variable fonts are
    cut into static weights 100..900 within the font's range."""
    name = os.path.basename(path)
    style = "italic" if "Italic" in name else "normal"
    if "[" not in name:
        w = next((v for k, v in STATIC_WEIGHT.items() if name.endswith(f"-{k}.ttf")), 400)
        return [(w, style, path)]
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    axes = {a.axisTag: (a.minValue, a.defaultValue, a.maxValue)
            for a in TTFont(path)["fvar"].axes}
    lo, _, hi = axes["wght"]
    out = []
    for w in range(100, 1000, 100):
        if not lo <= w <= hi:
            continue
        dest = os.path.join(CACHE, "static",
                            f"{family.replace(' ', '')}-{'Italic-' if style == 'italic' else ''}{w}.ttf")
        if not os.path.exists(dest):
            loc = {t: d for t, (_, d, _) in axes.items()}
            loc["wght"] = w
            if "opsz" in axes and family in OPSZ_MAX:
                loc["opsz"] = axes["opsz"][2]
            instancer.instantiateVariableFont(TTFont(path), loc).save(dest)
        out.append((w, style, dest))
    return out


def main():
    os.makedirs(os.path.join(CACHE, "static"), exist_ok=True)
    css = []
    for family, files in FILES.items():
        for rel in files:
            dest = fetch(GF + urllib.parse.quote(rel), os.path.join(CACHE, os.path.basename(rel)))
            for w, st, f in faces(family, dest):
                css.append(f"@font-face {{ font-family: '{family}'; src: url('file://{f}'); "
                           f"font-weight: {w}; font-style: {st}; }}")
    for w, fn in ((400, "LXGWWenKai-Regular.ttf"), (500, "LXGWWenKai-Medium.ttf")):
        f = fetch(LXGW + fn, os.path.join(CACHE, fn))
        css.append(f"@font-face {{ font-family: 'LXGW WenKai'; src: url('file://{f}'); "
                   f"font-weight: {w}; font-style: normal; }}")
    with open(os.path.join(CACHE, "fonts.css"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(css) + "\n")
    print(f"fonts: {len(css)} faces in {CACHE}")


if __name__ == "__main__":
    sys.exit(main())
