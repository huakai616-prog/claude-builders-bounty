"""Shared helpers for the cover studies.

A design is designs/<id>.py with

    def render(m) -> str      # one complete HTML document, one 11 x 17 in page

`m` is META (meta.json): every text on the cover must come from it, so the
design can later move into tools/hollywood for any song.  Use page() to wrap
your CSS and body: it adds the @page size, the bundled fonts and a reset.
"""
import html
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.environ.get("HOLLYWOOD_FONTS", os.path.expanduser("~/.cache/hollywood-fonts"))
try:
    FONTS_CSS = open(os.path.join(FONTS_DIR, "fonts.css"), encoding="utf-8").read()
except FileNotFoundError:
    raise SystemExit("cover fonts missing: run  python3 tools/hollywood/covers/fonts.py")

# Approved colours from the user's own work (国庆抖音 video, "排版和字体都不错")
PAPER = "#F6EFE4"      # warm paper
INK = "#3E372F"        # warm ink
CINNABAR = "#B7472A"   # 朱砂 (vermilion)
FLAG_RED = "#EE1C25"   # GB 12982 red  - only for the flag itself
FLAG_YELLOW = "#FFFF00"  # GB 12982 yellow - only for the flag itself
GOLD = "#C9A04A"


def meta(path=None):
    """META of a song; default: 我和我的祖国 (meta_wohewodezuguo.json)."""
    path = path or os.path.join(HERE, "meta_wohewodezuguo.json")
    return json.load(open(path, encoding="utf-8"))


def e(s):
    """HTML-escape."""
    return html.escape(str(s))


def sym(s):
    """Escape, and wrap the music glyphs most text fonts lack (♩ ♪ ♭ ♯ ♮ ′ ″)
    in a fallback font so they never render as tofu."""
    out = []
    for ch in e(s):
        out.append(f"<span style=\"font-family:'DejaVu Sans',sans-serif;"
                   f"font-size:.92em\">{ch}</span>" if ch in "♩♪♭♯♮" else ch)
    return "".join(out)


def star(cx, cy, r, toward=None, inner=0.381966):
    """SVG points of a five-pointed star; one point aims at `toward`
    (default: straight up)."""
    a0 = -math.pi / 2
    if toward:
        a0 = math.atan2(toward[1] - cy, toward[0] - cx)
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner
        a = a0 + i * math.pi / 5
        pts.append(f"{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}")
    return " ".join(pts)


def flag_svg(w):
    """The national flag exactly to GB 12982: 3:2, hoist quarter ruled
    15 x 10, big star centre (5,5) r 3, small stars (10,2) (12,4) (12,7)
    (10,9) r 1, each with one point aimed at the big star's centre.
    RED LINES: whole, flat, opaque, upright, nothing drawn over it, never a
    faded or cropped background, never under a texture layer."""
    u = w / 30
    stars = [f'<polygon fill="{FLAG_YELLOW}" points="{star(5 * u, 5 * u, 3 * u)}"/>']
    for x, y in [(10, 2), (12, 4), (12, 7), (10, 9)]:
        stars.append(f'<polygon fill="{FLAG_YELLOW}" points="'
                     f'{star(x * u, y * u, u, toward=(5 * u, 5 * u))}"/>')
    return (f'<svg style="display:block" width="{w:.2f}" height="{w * 2 / 3:.2f}" '
            f'viewBox="0 0 {w} {w * 2 / 3}">'
            f'<rect width="{w}" height="{w * 2 / 3}" fill="{FLAG_RED}"/>'
            f'{"".join(stars)}</svg>')


BASE_CSS = """
@page { size: 11in 17in; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { width: 11in; height: 17in; }
body { -webkit-print-color-adjust: exact; print-color-adjust: exact;
       font-variant-numeric: lining-nums; }
.page { width: 11in; height: 17in; position: relative; overflow: hidden; }
"""


def page(css, body, title="cover"):
    """A complete HTML document: fonts + reset + your CSS, body inside
    <div class='page'>.  Put the page background on .page (or body)."""
    return ("<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>{e(title)}</title><style>{FONTS_CSS}{BASE_CSS}{css}"
            f"</style></head><body><div class='page'>{body}</div></body></html>")


def credit_rows(m):
    """The credit rows the house standard requires, in order, empty ones
    dropped: [(中文, English, name)]."""
    rows = [("作曲", "Music", m.get("composer")),
            ("原曲", "Original", m.get("original")),
            ("作词", "Lyrics", m.get("lyricist")),
            ("原唱", "Original Artist", m.get("artist")),
            ("改编自", "Based on", m.get("source")),
            ("改编", "Arranged by", m.get("arranger")),
            ("制谱", "Music Preparation", m.get("engraver"))]
    return [r for r in rows if r[2]]
