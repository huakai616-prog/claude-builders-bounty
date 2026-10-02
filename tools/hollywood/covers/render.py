#!/usr/bin/env python3
"""Render cover studies and check them (fonts first: python3 fonts.py).

  python3 tools/hollywood/covers/render.py <id> [<id> ...]
        HTML -> PDF (Chromium) -> PNG, then the content check below
  python3 tools/hollywood/covers/render.py <id> --zoom X0,Y0,X1,Y1 [--dpi 200]
        crop of the rendered PDF (inches from the top-left) -> <out>/<id>/zoom.png
  python3 tools/hollywood/covers/render.py <id> --full
        cover + the real 我和我的祖国 score pages -> <out>/<id>/full.pdf

<out> is  or /tmp/covers-out (never inside the repo).  Per design:
cover.html, cover.pdf (vector), cover.png (72 dpi, 792 x 1224 px, rasterised
FROM the PDF, so it shows what prints), check.txt.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.environ.get("COVERS_OUT", "/tmp/covers-out")
sys.path.insert(0, os.path.join(REPO, "tools", "hollywood"))
import qa  # noqa: E402

SCORE_PDF = os.path.join(REPO, "wohewodezuguo", "output", "我和我的祖国_全曲_总谱.pdf")
import hollywood  # noqa: E402
CHROME = hollywood.find_chrome()


def load(design_id):
    path = os.path.join(HERE, "designs", f"{design_id}.py")
    spec = importlib.util.spec_from_file_location(f"design_{design_id}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def chrome_pdf(html_path, pdf_path):
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--allow-file-access-from-files", "--no-pdf-header-footer",
                    "--virtual-time-budget=6000", "--run-all-compositor-stages-before-draw",
                    f"--print-to-pdf={pdf_path}", "file://" + html_path],
                   check=True, capture_output=True, timeout=300)


def png(pdf, out_base, dpi=72, crop=None):
    args = ["pdftoppm", "-r", str(dpi), "-png", "-singlefile"]
    if crop:
        x0, y0, x1, y1 = crop
        args += ["-x", str(round(x0 * dpi)), "-y", str(round(y0 * dpi)),
                 "-W", str(round((x1 - x0) * dpi)), "-H", str(round((y1 - y0) * dpi))]
    subprocess.run(args + [pdf, out_base], check=True)
    return out_base + ".png"


def check(pdf, m):
    """Content and print checks; returns (problems, notes)."""
    problems, notes = [], []
    title_meta, pages = qa.read_pdf(pdf)
    if len(pages) != 1:
        problems.append(f"{len(pages)} pages, the cover must be exactly 1 page")
    if not pages:
        return problems + ["no pages"], notes
    w, h, words = pages[0]
    if (round(w), round(h)) != (792, 1224):
        problems.append(f"page is {w:.0f} x {h:.0f} pt, must be 792 x 1224 (11 x 17 in)")
    # the real qa.py cover check (positional key/instrumentation lines are
    # specific to the classic layout: reported as notes only)
    qp = []
    qa.check_cover(words, m["title"], qp)
    for p in qp:
        (notes if "line" in p and ("key · tempo" in p or "instrumentation" in p)
         else problems).append(("qa.py: " + p) if p not in notes else p)
    text = qa.norm("".join(t for *_, t in sorted(words, key=lambda x: (round(x[3] / 4), x[0]))))
    allt = qa.norm("".join(t for *_, t in words))

    def has(s):
        s = qa.norm(s)
        return s in text or s in allt
    need = [("FULL SCORE", "Full Score"), ("SCORE IN C", "Score in C"),
            ("CONCERT PITCH", "Concert Pitch"), (m["title"], "title (contiguous text)"),
            (m["title_latin"], "pinyin title"), ("全曲", "subtitle zh"),
            ("四声部独唱", "subtitle/instrumentation zh"), ("弦乐四重奏", "string quartet zh"),
            ("COMPLETE SONG", "subtitle en"), ("STRING QUARTET", "instrumentation en"),
            ("VOCAL QUARTET", "instrumentation en"), ("56", "tempo"),
            ("2′51″", "duration"), ("2026", "year")]
    for s, what in need:
        if not has(s):
            problems.append(f"missing {what}: {s!r}")
    if not (has("E♭ MAJOR") or has("EbMAJOR")) or not has("降E大调"):
        problems.append("missing key: 'E♭ Major' and '降E大调'")
    for zh, en, name in lib.credit_rows(m):
        if not has(zh) or not has(name):
            problems.append(f"missing credit {zh} {name}")
    if allt.count(qa.norm(m["arranger"])) < 3:
        problems.append(f"{m['arranger']} appears {allt.count(qa.norm(m['arranger']))}x; "
                        "need 改编 row + 制谱 row + the signature at the foot")
    # print safety: text closer than 0.35 in to the trim edge
    edge = 0.35 * 72
    for x0, y0, x1, y1, t in words:
        if x0 < edge or y0 < edge or x1 > w - edge or y1 > h - edge:
            problems.append(f"text {t!r} within 0.35 in of the page edge "
                            f"({x0 / 72:.2f},{y0 / 72:.2f})-({x1 / 72:.2f},{y1 / 72:.2f}) in")
    # fonts: Type 3 = outlines without a real font (often a variable-font
    # fallback), and unintended fallbacks
    r = subprocess.run(["pdffonts", pdf], capture_output=True, text=True)
    fonts = [ln for ln in r.stdout.splitlines()[2:] if ln.strip()]
    t3 = sorted({re.sub(r'^[A-Z]{6}\+', '', ln.split()[0]) for ln in fonts if "Type 3" in ln})
    if t3:
        notes.append("Type 3 (outline) fonts, normal for CJK/variable fonts in Chromium, "
                     "text still extracts: " + ", ".join(t3))
    for ln in fonts:
        if re.search(r"WenQuanYi|DejaVuSerif|Liberation|FreeSerif|Unifont|IPA", ln):
            problems.append(f"fallback font used (a glyph is missing in your font?): {ln.split()[0]}")
    notes.append("fonts: " + ", ".join(sorted({re.sub(r'^[A-Z]{6}\+', '', ln.split()[0]) for ln in fonts})))
    size = os.path.getsize(pdf)
    notes.append(f"pdf size {size / 1024:.0f} KB")
    if size > 6 * 1024 * 1024:
        problems.append(f"cover PDF is {size / 1048576:.1f} MB: too heavy (raster effects?)")
    return problems, notes


def render(design_id, full=False):
    out = os.path.join(OUT, design_id)
    os.makedirs(out, exist_ok=True)
    m = lib.meta()
    doc = load(design_id).render(m)
    hp = os.path.join(out, "cover.html")
    open(hp, "w", encoding="utf-8").write(doc)
    pdf = os.path.join(out, "cover.pdf")
    chrome_pdf(hp, pdf)
    # metadata title so qa.read_pdf sees it like the real score
    from pypdf import PdfReader, PdfWriter
    rd = PdfReader(pdf)
    wr = PdfWriter()
    for p in rd.pages:
        wr.add_page(p)
    wr.add_metadata({"/Title": f"{m['title']} — {m['subtitle']} (Full Score)"})
    with open(pdf, "wb") as fh:
        wr.write(fh)
    png(pdf, os.path.join(out, "cover"), 72)
    problems, notes = check(pdf, m)
    rep = "\n".join(["PROBLEM: " + p for p in problems] + ["note: " + n for n in notes])
    open(os.path.join(out, "check.txt"), "w").write(rep + "\n")
    print(f"[{design_id}] {'OK' if not problems else str(len(problems)) + ' problem(s)'}"
          f"  -> {out}/cover.png")
    print(rep)
    if full:
        from pypdf import PdfReader, PdfWriter
        score = PdfReader(SCORE_PDF)
        wr = PdfWriter()
        wr.add_page(PdfReader(pdf).pages[0])
        for p in score.pages[1:]:
            wr.add_page(p)
        wr.add_metadata({"/Title": f"{m['title']} — {m['subtitle']} (Full Score)"})
        fp = os.path.join(out, "full.pdf")
        with open(fp, "wb") as fh:
            wr.write(fh)
        print(f"full score with this cover -> {fp}")
    return problems


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        raise SystemExit(__doc__)
    ids = [a for a in argv if not a.startswith("--") and not re.match(r"^[\d.,]+$", a)]
    if "--zoom" in argv:
        box = tuple(float(x) for x in argv[argv.index("--zoom") + 1].split(","))
        dpi = int(argv[argv.index("--dpi") + 1]) if "--dpi" in argv else 200
        for i in ids:
            out = os.path.join(OUT, i)
            print(png(os.path.join(out, "cover.pdf"), os.path.join(out, "zoom"), dpi, box))
        return 0
    bad = 0
    for i in ids:
        bad += bool(render(i, full="--full" in argv))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
