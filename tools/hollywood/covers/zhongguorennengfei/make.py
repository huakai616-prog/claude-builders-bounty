#!/usr/bin/env python3
"""《中国人能飞》 cover drafts: the house cover (tools/hollywood cover_html,
plus the English-title line of the 诀别书 cover) with one small, song-specific
ornament per variant (see README.md).

    python3 tools/hollywood/covers/zhongguorennengfei/make.py [variant ...]
        -> $COVERS_OUT (default /tmp/covers-out/zhongguorennengfei)/<v>.pdf/.png,
           then the qa.py cover check
    python3 .../make.py <variant> --zoom X0,Y0,X1,Y1      crop at 200 dpi (inches)
"""
import math
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "tools", "hollywood"))
import hollywood  # noqa: E402
import qa  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("COVERS_OUT", "/tmp/covers-out/zhongguorennengfei")
INK = "#111"
RED = "#B7472A"          # 朱砂, the user's approved accent

META = dict(
    title="中国人能飞", title_latin="Zhōngguórén Néng Fēi",
    title_en="Chinese Can Fly",
    subtitle="副歌 · 人声与弦乐四重奏",
    subtitle_en="Chorus — for Voice and String Quartet",
    credits=[("词曲", "Words & Music", "揽佬"),
             ("原唱", "Original Artist", "揽佬 SKAI ISYOURGOD"),
             ("改编", "Arranged by", "花开当富贵"),
             ("制谱", "Music Preparation", "花开当富贵")],
    # placeholders until the arrangement exists
    key="A Minor · a 小调", tempo="♩ = 128", duration="ca. 1′30″",
    instrumentation=[("Voice", "人声"), ("Violin I", "第一小提琴"),
                     ("Violin II", "第二小提琴"), ("Viola", "中提琴"),
                     ("Violoncello", "大提琴")],
    arranger="花开当富贵", year="2026")

# the house CSS, with the 诀别书 layout: an English title line under the
# pinyin pushes the ornament and subtitle down
EXTRA_CSS = """
.cover .latin { top: 6.05in; }
.ten { top: 6.55in; font-size: 17pt; font-style: italic; color: #222; }
.credits .en { font-style: italic; }   /* as on the 诀别书 cover */
.orn { top: 7.2in; }
.sub { top: 7.75in; }
.suben { top: 8.4in; }
.credits { top: 9.95in; }
.title { z-index: 0; }
.title .ch { position: relative; display: inline-block; }
/* art inside a character span: 1000 viewBox units = 1 em, y from the line
   top; the baseline is at 982.5 (Noto Serif CJK: ascent 1.151, descent .286,
   line-height 1.1) */
.title .ch svg { position: absolute; left: 0; top: 0; overflow: visible; }
.art { position: absolute; overflow: visible; pointer-events: none; }
"""


def e(s):
    return hollywood._e(s)


def cover(title_html=None, orn_html=None, extra="", css=""):
    m = META
    rows = "".join(
        f"<tr><td class='zh'>{e(a)}</td><td class='en'>{e(b)}</td>"
        f"<td class='nm'>{e(c)}</td></tr>" for a, b, c in m["credits"])
    info = "　·　".join(hollywood._sym(x) for x in (m["key"], m["tempo"], m["duration"]))
    inst = "　·　".join(f"{e(en)} <span class='cjk'>{e(zh)}</span>"
                       for en, zh in m["instrumentation"])
    title_html = title_html or e(m["title"])
    orn_html = orn_html or "<span></span><b></b><span></span>"
    body = f"""
<div class='page cover'>
  <div class='frame'></div>
  <div class='cv kicker'>Full Score</div>
  <div class='cv kicker2'>Score in C · Concert Pitch</div>
  <div class='cv title'>{title_html}</div>
  <div class='cv latin'>{e(m['title_latin'])}</div>
  <div class='cv ten'>{e(m['title_en'])}</div>
  <div class='cv orn'>{orn_html}</div>
  <div class='cv sub'>{e(m['subtitle'])}</div>
  <div class='cv suben'>{e(m['subtitle_en'])}</div>
  <table class='credits'>{rows}</table>
  <div class='cv info'>{info}</div>
  <div class='cv inst'>{inst}</div>
  <div class='cv sig'>{e(m['arranger'])}</div>
  <div class='cv sig2'>Arrangement &amp; Music Preparation · {e(m['year'])}</div>
  {extra}
</div>"""
    return ("<!doctype html><html><head><meta charset='utf-8'><style>"
            + hollywood.CSS + EXTRA_CSS + css + "</style></head><body>"
            + body + "</body></html>")


def chars(title, wrap=None):
    """Title as one span per character; wrap(i, ch) may return extra HTML
    to put inside that character's span (absolutely positioned art)."""
    return "".join(f"<span class='ch c{i}'>{e(ch)}{(wrap or (lambda i, c: ''))(i, ch)}</span>"
                   for i, ch in enumerate(title))


# ---------------------------------------------------------------------------
VARIANTS = {}


def variant(fn):
    VARIANTS[fn.__name__] = fn
    return fn


@variant
def base():
    return cover()


# the ornaments live in variants.py (same namespace)
exec(open(os.path.join(HERE, "variants.py"), encoding="utf-8").read())


# ---------------------------------------------------------------------------
def render(name):
    os.makedirs(OUT, exist_ok=True)
    html_path = os.path.join(OUT, f"{name}.html")
    open(html_path, "w", encoding="utf-8").write(VARIANTS[name]())
    pdf = os.path.join(OUT, f"{name}.pdf")
    hollywood._chrome_pdf(html_path, pdf)
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(pdf)
    w = PdfWriter()
    w.add_page(r.pages[0])
    w.add_metadata({"/Title": f"{META['title']} — {META['subtitle']} (Full Score)",
                    "/Author": "改编 花开当富贵 · 制谱 花开当富贵"})
    with open(pdf, "wb") as fh:
        w.write(fh)
    subprocess.run(["pdftoppm", "-r", "72", "-png", "-singlefile", pdf,
                    os.path.join(OUT, name)], check=True)
    title, pages = qa.read_pdf(pdf)
    probs = []
    if len(pages) != 1:
        probs.append(f"{len(pages)} pages")
    qa.check_cover(pages[0][2], META["title"], probs)
    print(f"[{name}] " + ("qa cover OK" if not probs else "; ".join(probs)))


def zoom(name, box, dpi=200):
    x0, y0, x1, y1 = box
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", "-singlefile",
                    "-x", str(round(x0 * dpi)), "-y", str(round(y0 * dpi)),
                    "-W", str(round((x1 - x0) * dpi)), "-H", str(round((y1 - y0) * dpi)),
                    os.path.join(OUT, f"{name}.pdf"), os.path.join(OUT, f"{name}_zoom")],
                   check=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--zoom" in args:
        i = args.index("--zoom")
        zoom(args[0], [float(x) for x in args[i + 1].split(",")])
    else:
        for n in args or VARIANTS:
            render(n)
