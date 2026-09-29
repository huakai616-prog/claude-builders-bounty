#!/usr/bin/env python3
"""Hollywood-standard full score: shared by every song's build.py.

Two entry points:

  polish_musicxml(path, meta)
      Page layout (11 x 17 in tabloid, concert pitch), first-page credit block
      and <identification> for the MusicXML that goes to Sibelius.  Arranger
      and engraver are always 花开当富贵 unless meta overrides them.

  render_pdf(musicxml, out_pdf, meta, png_dir=None)
      MuseScore Studio 4 engraves the score with hollywood.mss, headless
      Chromium draws the cover page and the running header / footer, and
      pypdf merges them into one PDF.

`meta` is a plain dict; see DEFAULT_META and the SKILL.md for every key.
Command line (re-render a PDF without rebuilding the song):

  python3 tools/hollywood/hollywood.py <song>/build.py
"""
import glob
import html
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(HERE, "hollywood.mss")

ARRANGER = "花开当富贵"
ENGRAVER = "花开当富贵"

DEFAULT_META = {
    "title": "",            # 我不难过
    "title_latin": "",      # Wǒ Bù Nánguò (cover only)
    "subtitle": "",         # 副歌 · 人声与弦乐四重奏
    "subtitle_en": "",      # Chorus — for Voice and String Quartet
    "composer": "",
    "lyricist": "",
    "artist": "",           # original performer
    "original": "",         # original work, for instrumental arrangements
                            # ("钢琴练习曲 Op. 25 No. 11"): cover row and
                            # first-page left block
    "arranger": ARRANGER,
    "engraver": ENGRAVER,
    "instrumentation": [],  # [("Voice", "人声"), ("Violin I", "第一小提琴"), ...]
    "key": "",              # "E♭ Major · 降E大调"
    "tempo": "",            # "♩ = 68"
    "duration": "",         # "ca. 1′25″"
    "year": "",
    "tempo_text": "",       # "Andante espressivo": joined to the bar-1 metronome
}

# page geometry, must match hollywood.mss (inches)
PAGE_W, PAGE_H = 11.0, 17.0
MARGIN_X, MARGIN_TOP, MARGIN_BOTTOM = 0.6, 1.05, 0.95
SPATIUM_MM = 1.8  # also <Spatium> in hollywood.mss


def _meta(meta):
    m = dict(DEFAULT_META)
    m.update(meta or {})
    return m


# ---------------------------------------------------------------------------
# MusicXML: layout + credits (what Sibelius opens)
# ---------------------------------------------------------------------------
def _tenths(inches):
    return round(inches * 25.4 / SPATIUM_MM * 10, 1)


def _credit(page, ctype, text, x, y, size, justify, valign, weight=None):
    c = ET.Element("credit", page=str(page))
    ET.SubElement(c, "credit-type").text = ctype
    w = ET.SubElement(c, "credit-words", {
        "default-x": str(x), "default-y": str(y), "font-size": str(size),
        "justify": justify, "valign": valign})
    if weight:
        w.set("font-weight", weight)
    w.text = text
    return c


def polish_musicxml(path, meta):
    """Tabloid layout, spacing, credit block and creators for Sibelius."""
    m = _meta(meta)
    tree = ET.parse(path)
    r = tree.getroot()

    # identification: creators + encoder
    ident = r.find("identification")
    if ident is None:
        ident = ET.Element("identification")
        anchor = r.find("defaults")
        if anchor is None:
            anchor = r.find("part-list")
        r.insert(list(r).index(anchor), ident)
    for x in ident.findall("creator"):
        ident.remove(x)
    creators = [("composer", m["composer"]), ("lyricist", m["lyricist"]),
                ("arranger", m["arranger"])]
    for i, (t, v) in enumerate(c for c in creators if c[1]):
        el = ET.Element("creator", type=t)
        el.text = v
        ident.insert(i, el)
    enc = ident.find("encoding")
    if enc is not None:
        for x in enc.findall("encoder"):
            enc.remove(x)
        e = ET.Element("encoder")
        e.text = m["engraver"]
        enc.insert(0, e)

    # defaults: page layout and staff spacing
    d = r.find("defaults")
    for t in ("scaling", "page-layout", "system-layout", "staff-layout"):
        for x in d.findall(t):
            d.remove(x)
    W, H = _tenths(PAGE_W), _tenths(PAGE_H)
    new = ET.fromstring(
        f"<defaults><scaling><millimeters>{SPATIUM_MM * 4}</millimeters>"
        "<tenths>40</tenths></scaling><page-layout>"
        f"<page-height>{H}</page-height><page-width>{W}</page-width>"
        "<page-margins type=\"both\">"
        f"<left-margin>{_tenths(MARGIN_X)}</left-margin>"
        f"<right-margin>{_tenths(MARGIN_X)}</right-margin>"
        f"<top-margin>{_tenths(MARGIN_TOP)}</top-margin>"
        f"<bottom-margin>{_tenths(MARGIN_BOTTOM)}</bottom-margin>"
        "</page-margins></page-layout><system-layout><system-margins>"
        "<left-margin>0</left-margin><right-margin>0</right-margin>"
        "</system-margins><system-distance>100</system-distance>"
        "<top-system-distance>250</top-system-distance></system-layout>"
        "<staff-layout><staff-distance>70</staff-distance></staff-layout>"
        "</defaults>")
    for i, x in enumerate(new):
        d.insert(i, x)

    # credits: replace whatever music21 wrote with the house title block
    for c in r.findall("credit"):
        r.remove(c)
    top = round(H - _tenths(MARGIN_TOP), 1)
    left, right, mid = _tenths(MARGIN_X), W - _tenths(MARGIN_X), W / 2
    lines_l = [f"作词：{m['lyricist']}" if m["lyricist"] else "",
               f"原唱：{m['artist']}" if m["artist"] else "",
               f"原作：{m['original']}" if m["original"] else ""]
    lines_r = [f"作曲：{m['composer']}" if m["composer"] else "",
               f"改编：{m['arranger']}", f"制谱：{m['engraver']}"]
    base = round(top - 150, 1)  # left and right blocks share a baseline
    credits = [
        _credit(1, "title", m["title"], mid, top, 30, "center", "top", "bold"),
        _credit(1, "subtitle", m["subtitle"], mid, round(top - 70, 1), 14,
                "center", "top"),
        _credit(1, "lyricist", "\n".join(x for x in lines_l if x),
                left, base, 10.5, "left", "bottom"),
        _credit(1, "composer", "\n".join(x for x in lines_r if x),
                right, base, 10.5, "right", "bottom"),
    ]
    at = list(r).index(r.find("part-list"))
    for c in reversed(credits):
        r.insert(at, c)

    # tempo: one mark, "Andante espressivo ♩ = 68", not two stacked texts
    if m["tempo_text"]:
        for dr in r.find("part/measure").findall("direction"):
            met = dr.find("direction-type/metronome")
            if met is not None:
                dt = ET.Element("direction-type")
                ET.SubElement(dt, "words", {"font-weight": "bold"}).text = \
                    m["tempo_text"] + " "
                dr.insert(0, dt)
                break

    # 16th runs: music21 breaks the second beam after every eighth, so a beat
    # of four 16ths reads 2+2; engrave each pure 16th group as one unit
    for meas in r.iter("measure"):
        group = []
        for n in meas.findall("note"):
            b1 = n.find("beam[@number='1']")
            if b1 is None:
                continue
            group.append(n)
            if b1.text != "end":
                continue
            b2 = [g.find("beam[@number='2']") for g in group]
            if len(group) > 2 and all(
                    b is not None and b.text in ("begin", "continue", "end")
                    for b in b2):
                for i, b in enumerate(b2):
                    b.text = ("begin" if i == 0 else
                              "end" if i == len(b2) - 1 else "continue")
            group = []

    # rehearsal letters bold (house style; Sibelius and MS4 both read it)
    for rh in r.iter("rehearsal"):
        rh.set("font-weight", "bold")

    # every bar numbered (Sibelius honours <measure-numbering>)
    first = r.find("part/measure")
    if first is not None:
        pr = first.find("print")
        if pr is None:
            pr = ET.Element("print")
            first.insert(0, pr)
        for x in pr.findall("measure-numbering"):
            pr.remove(x)
        mn = ET.Element("measure-numbering")
        mn.text = "measure"
        # schema order inside <print>: layouts first, measure-numbering last
        pr.append(mn)

    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    xml = open(path, encoding="utf-8").read()
    if "<!DOCTYPE" not in xml:
        xml = xml.replace(
            "?>\n",
            "?>\n<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD "
            "MusicXML 4.0 Partwise//EN\" "
            "\"http://www.musicxml.org/dtds/partwise.dtd\">\n", 1)
        open(path, "w", encoding="utf-8").write(xml)


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
MS4_URL = ("https://github.com/musescore/MuseScore/releases/download/v4.4.4/"
           "MuseScore-Studio-4.4.4.243461245-x86_64.AppImage")
MS4_DIR = "/opt/ms4"


def find_ms4(install=True):
    cands = [os.environ.get("MSCORE4", ""),
             os.path.join(MS4_DIR, "squashfs-root", "AppRun"),
             shutil.which("mscore4portable") or "",
             shutil.which("mscore4") or "",
             "/Applications/MuseScore 4.app/Contents/MacOS/mscore"]
    for c in cands:
        if c and os.path.exists(c):
            return c
    if not install:
        return None
    print("MuseScore 4 not found, downloading the AppImage to", MS4_DIR)
    os.makedirs(MS4_DIR, exist_ok=True)
    img = os.path.join(MS4_DIR, "ms4.AppImage")
    subprocess.run(["curl", "-sSL", "-o", img, MS4_URL], check=True)
    os.chmod(img, 0o755)
    subprocess.run([img, "--appimage-extract"], cwd=MS4_DIR, check=True,
                   stdout=subprocess.DEVNULL)
    return os.path.join(MS4_DIR, "squashfs-root", "AppRun")


def find_chrome():
    cands = [os.environ.get("CHROME", "")]
    cands += sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"))
    cands += [shutil.which(x) or "" for x in
              ("chromium", "chromium-browser", "google-chrome")]
    cands.append("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    for c in cands:
        if c and os.path.exists(c):
            return c
    raise SystemExit("Chromium / Chrome not found (set CHROME=...)")


def _ms4(args):
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    p = subprocess.run([find_ms4()] + args, env=env, capture_output=True,
                       text=True, timeout=600)
    if p.returncode != 0:
        raise RuntimeError(f"MuseScore 4 failed: {args}\n{p.stderr[-2000:]}")


TITLE_FRAME_SP = 21  # height of the first-page title frame, in spaces


def _fix_title_frame(mscz):
    """MS4 imports MusicXML credits with odd offsets (composer drifts to the
    top, lyricist into the music).  Give the title frame a fixed height and
    let the style place each text: title / subtitle centred at the top,
    lyricist bottom-left, composer bottom-right on one shared baseline."""
    with zipfile.ZipFile(mscz) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    out = []
    for info, data in items:
        if info.filename.endswith(".mscx"):
            x = data.decode("utf-8")

            def fix(mo):
                box = mo.group(0)
                box = re.sub(r"<height>[^<]*</height>",
                             f"<height>{TITLE_FRAME_SP}</height>", box, 1)
                box = re.sub(r"\s*<offset [^>]*/>", "", box)
                box = re.sub(r"\s*<align>[^<]*</align>", "", box)
                return box
            x = re.sub(r"<VBox>.*?</VBox>", fix, x, count=1, flags=re.S)
            data = x.encode("utf-8")
        out.append((info, data))
    with zipfile.ZipFile(mscz, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)


SECTION_LIFT_SP = 5  # rehearsal letter + section title sit above bar numbers


def _lift_sections(mscz, lift=SECTION_LIFT_SP):
    """Bar numbers are boxed above every bar, so a rehearsal letter and its
    bold section title ("A  Chorus 副歌") would share their row and run into
    the section's first bar number.  Raise both onto a row of their own."""
    if not lift:
        return
    off = f'\n            <offset x="0" y="{-lift}"/>'
    with zipfile.ZipFile(mscz) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    out = []
    for info, data in items:
        if info.filename.endswith(".mscx"):
            x = data.decode("utf-8")

            def fix(mo):
                meas = mo.group(0)
                if "<RehearsalMark>" not in meas:
                    return meas
                meas = re.sub(r"(<RehearsalMark>\s*<eid>[^<]*</eid>)",
                              lambda k: k.group(1) + off, meas)
                # the section title: a staff text that is bold throughout
                return re.sub(
                    r"(<StaffText>\s*<eid>[^<]*</eid>\s*"
                    r"<text><b>[^<]*</b></text>)",
                    lambda k: k.group(1) + off, meas)
            x = re.sub(r"<Measure>.*?</Measure>", fix, x, flags=re.S)
            data = x.encode("utf-8")
        out.append((info, data))
    with zipfile.ZipFile(mscz, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)


CJK_FONT = "Noto Serif CJK SC"
_CJK = re.compile(r"[\u3000-\u303f\u3400-\u9fff\uff00-\uffef]+")


def _engrave_fixes(mscz):
    """Fixes on the imported .mscz that the MusicXML cannot carry:
    * Chinese in staff / system texts ("Chorus 副歌") in Noto Serif CJK,
      not whatever fallback the text font finds;
    * 8va lines labelled "8va", not a bare "8" (MS4 turns the import's
      ottavaNumbersOnly on, and -S does not reset it)."""
    with zipfile.ZipFile(mscz) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    out = []
    for info, data in items:
        if info.filename.endswith(".mscx"):
            x = data.decode("utf-8")

            def text(mo):
                return _CJK.sub(lambda k: f'<font face="{CJK_FONT}"/>'
                                f'{k.group(0)}<font face="Edwin"/>',
                                mo.group(0))

            def block(mo):
                return re.sub(r"<text>.*?</text>", text, mo.group(0),
                              flags=re.S)
            x = re.sub(r"<(StaffText|SystemText)>.*?</\1>", block, x,
                       flags=re.S)
            data = x.encode("utf-8")
        elif info.filename.endswith(".mss"):
            x = data.decode("utf-8")
            if "<ottavaNumbersOnly>" in x:
                x = re.sub(r"<ottavaNumbersOnly>\d</ottavaNumbersOnly>",
                           "<ottavaNumbersOnly>0</ottavaNumbersOnly>", x)
            else:
                x = x.replace("</Style>",
                              "  <ottavaNumbersOnly>0</ottavaNumbersOnly>\n"
                              "    </Style>", 1)
            data = x.encode("utf-8")
        out.append((info, data))
    with zipfile.ZipFile(mscz, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in out:
            z.writestr(info, data)


def _edit_mscx(mscz, fn):
    """Apply fn(mscx_text) -> mscx_text to the score inside an .mscz."""
    with zipfile.ZipFile(mscz) as z:
        items = [(i, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(mscz, "w", zipfile.ZIP_DEFLATED) as z:
        for info, data in items:
            if info.filename.endswith(".mscx"):
                data = fn(data.decode("utf-8")).encode("utf-8")
            z.writestr(info, data)


# CJK Radicals Supplement code points that share a glyph with an ordinary
# character in Noto Serif CJK SC (derived from the font's cmap).  The
# Kangxi Radicals block (U+2F00-2FDF) is handled by NFKC.
_RADICALS = {
    0x2E82: 0x4E5B, 0x2E83: 0x4E5A, 0x2E85: 0x4EBB, 0x2E89: 0x5202,
    0x2E8E: 0x5140, 0x2E8F: 0x5C23, 0x2E90: 0x5C22, 0x2E92: 0x5DF3,
    0x2E93: 0x5E7A, 0x2E94: 0x5F51, 0x2E95: 0x5F50, 0x2E96: 0x5FC4,
    0x2E98: 0x624C, 0x2E99: 0x6535, 0x2E9B: 0x65E1, 0x2E9E: 0x6B7A,
    0x2EA0: 0x6C11, 0x2EA1: 0x6C35, 0x2EA3: 0x706C, 0x2EA6: 0x4E2C,
    0x2EA8: 0x72AD, 0x2EAB: 0x7F52, 0x2EAD: 0x793B, 0x2EAF: 0x7CF9,
    0x2EB0: 0x7E9F, 0x2EB1: 0x7F53, 0x2EB2: 0x7F52, 0x2EB9: 0x8002,
    0x2EBA: 0x8080, 0x2EBE: 0x8279, 0x2EBF: 0x8279, 0x2EC0: 0x8279,
    0x2EC1: 0x864E, 0x2EC2: 0x8864, 0x2EC3: 0x8980, 0x2EC5: 0x89C1,
    0x2EC6: 0x89D2, 0x2EC8: 0x8BA0, 0x2EC9: 0x8D1D, 0x2ECB: 0x8F66,
    0x2ECC: 0x8FB6, 0x2ED0: 0x9485, 0x2ED1: 0x9577, 0x2ED2: 0x9578,
    0x2ED3: 0x957F, 0x2ED4: 0x95E8, 0x2ED6: 0x961D, 0x2ED8: 0x9752,
    0x2ED9: 0x97E6, 0x2EDA: 0x9875, 0x2EDB: 0x98CE, 0x2EDC: 0x98DE,
    0x2EDD: 0x98DF, 0x2EDF: 0x98E0, 0x2EE0: 0x9963, 0x2EE2: 0x9A6C,
    0x2EE3: 0x9AA8, 0x2EE4: 0x9B3C, 0x2EE5: 0x9C7C, 0x2EE6: 0x9E1F,
    0x2EE7: 0x5364, 0x2EE8: 0x9EA6, 0x2EE9: 0x9EC4, 0x2EEA: 0x9EFE,
    0x2EEB: 0x6589, 0x2EEC: 0x9F50, 0x2EEE: 0x9F7F, 0x2EEF: 0x7ADC,
    0x2EF0: 0x9F99, 0x2EF1: 0x9F9C, 0x2EF2: 0x4E80,
}


def _plain_cjk(cp):
    if cp in _RADICALS:
        return _RADICALS[cp]
    if 0x2F00 <= cp <= 0x2FDF:
        import unicodedata
        n = unicodedata.normalize("NFKC", chr(cp))
        if len(n) == 1:
            return ord(n)
    return cp


def _fix_tounicode(cmap):
    """Rewrite one ToUnicode CMap so glyphs that the font shares between a
    radical and an ordinary character (方 / ⽅) map to the ordinary one.
    MS4's PDF export picks the radical, so copy / search in the PDF fails.
    Returns the new CMap bytes, or None if nothing needed changing."""
    txt = cmap.decode("latin-1")
    table = {}
    for blk in re.findall(r"beginbfchar(.*?)endbfchar", txt, re.S):
        for src, dst in re.findall(r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>",
                                   blk):
            table[src] = dst
    for blk in re.findall(r"beginbfrange(.*?)endbfrange", txt, re.S):
        for lo, hi, rest in re.findall(
                r"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*(\[[^\]]*\]|<[0-9A-Fa-f]+>)",
                blk):
            w = len(lo)
            a, b = int(lo, 16), int(hi, 16)
            if rest.startswith("["):
                for i, d in enumerate(re.findall(r"<([0-9A-Fa-f]+)>", rest)):
                    table[f"{a + i:0{w}X}"] = d
            else:
                d0 = int(rest[1:-1], 16)
                dw = len(rest) - 2
                for i in range(b - a + 1):
                    table[f"{a + i:0{w}X}"] = f"{d0 + i:0{dw}X}"
    changed = False
    for k, d in table.items():
        if len(d) == 4 and 0x2E80 <= int(d, 16) <= 0x2FDF:
            nd = f"{_plain_cjk(int(d, 16)):04X}"
            if nd != d.upper():
                table[k] = nd
                changed = True
    if not changed:
        return None
    head = txt[:txt.index("endcodespacerange") + len("endcodespacerange")]
    items = sorted(table.items(), key=lambda kv: int(kv[0], 16))
    body = []
    for i in range(0, len(items), 100):
        chunk = items[i:i + 100]
        body.append(f"{len(chunk)} beginbfchar")
        body += [f"<{k}> <{v}>" for k, v in chunk]
        body.append("endbfchar")
    tail = "endcmap\nCMapName currentdict /CMap defineresource pop\nend\nend\n"
    return (head + "\n" + "\n".join(body) + "\n" + tail).encode("latin-1")


def _fix_text_layer(writer):
    """Apply _fix_tounicode to every font (Type 0 / 3 / TrueType, also inside
    Type 3 and form-XObject resources) in the finished PDF."""
    from pypdf.generic import NameObject
    seen = set()

    def walk_res(res):
        res = res.get_object() if res is not None else None
        if not res:
            return
        for f in (res.get("/Font") or {}).values():
            f = f.get_object()
            if id(f) in seen:
                continue
            seen.add(id(f))
            tu = f.get("/ToUnicode")
            if tu is not None:
                stream = tu.get_object()
                new = _fix_tounicode(stream.get_data())
                if new is not None:
                    stream.set_data(new)
            walk_res(f.get("/Resources"))
        for x in (res.get("/XObject") or {}).values():
            x = x.get_object()
            if x.get("/Subtype") == NameObject("/Form"):
                walk_res(x.get("/Resources"))
    for page in writer.pages:
        walk_res(page.get("/Resources"))


def _chrome_pdf(html_path, pdf_path):
    subprocess.run([find_chrome(), "--headless", "--no-sandbox", "--disable-gpu",
                    "--no-pdf-header-footer", "--virtual-time-budget=4000",
                    f"--print-to-pdf={pdf_path}", "file://" + html_path],
                   check=True, capture_output=True, timeout=300)


# ---------------------------------------------------------------------------
# Cover and running header / footer (HTML, printed by Chromium)
# ---------------------------------------------------------------------------
CSS = """
@page { size: 11in 17in; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: transparent; }
body { font-family: 'EB Garamond', 'Noto Serif CJK SC', 'Songti SC', serif;
       color: #111; font-variant-numeric: lining-nums; }
.cjk { font-family: 'Noto Serif CJK SC', 'Songti SC', serif; }
.sym { font-family: 'DejaVu Sans', sans-serif; font-size: .95em; }
/* note values (half note for cut-time metronomes): DejaVu has none */
.note { font-family: 'FreeSerif', 'Noto Music', 'Apple Symbols', serif;
        font-size: 1.2em; line-height: 0; }
.page { width: 11in; height: 17in; position: relative; overflow: hidden;
        page-break-after: always; break-after: page; }
.page:last-child { page-break-after: auto; break-after: auto; }
.sc { text-transform: uppercase; letter-spacing: .22em; font-size: .78em; }

/* cover */
.cover { background: #fff; }
.frame { position: absolute; inset: .55in; border: 1.6pt solid #111; }
.frame::after { content: ''; position: absolute; inset: 5pt;
                border: .5pt solid #111; }
.cv { position: absolute; left: 0; right: 0; text-align: center; }
/* letter-spacing trails the last glyph too: pad-left by the same amount
   so every spaced line sits on the page axis */
.kicker { top: 2.05in; font-size: 15pt; letter-spacing: .5em; padding-left: .5em;
          text-transform: uppercase; }
.kicker2 { top: 2.5in; font-size: 11pt; letter-spacing: .3em; padding-left: .3em;
           text-transform: uppercase; color: #444; }
.title { top: 4.1in; font-family: 'Noto Serif CJK SC', serif;
         font-weight: 700; font-size: 92pt; letter-spacing: .12em;
         padding-left: .12em; line-height: 1.1; }
.latin { top: 6.05in; font-size: 17pt; letter-spacing: .45em; padding-left: .45em;
         text-transform: uppercase; color: #333; }
.orn { top: 6.85in; }
.orn span { display: inline-block; width: 1.6in; height: 0;
            border-top: .6pt solid #111; vertical-align: middle; }
.orn b { display: inline-block; width: 7pt; height: 7pt; margin: 0 12pt;
         transform: rotate(45deg); border: .8pt solid #111;
         vertical-align: middle; }
.sub { top: 7.4in; font-family: 'Noto Serif CJK SC', serif; font-size: 22pt;
       padding-left: .12em;
       letter-spacing: .12em; }
.suben { top: 8.05in; font-size: 17pt; font-style: italic; color: #222; }
.credits { position: absolute; top: 9.55in; left: 2.35in; right: 2.35in;
           border-collapse: collapse; width: 6.3in; }
.credits td { padding: 8pt 0; vertical-align: middle;
              border-bottom: .4pt solid #bbb; }
.credits tr:last-child td { border-bottom: none; }
.credits .zh { font-family: 'Noto Serif CJK SC', serif; font-size: 13pt;
               width: .75in; letter-spacing: .15em; }
.credits .en { font-size: 10pt; letter-spacing: .2em; text-transform: uppercase;
               color: #555; width: 2.3in; }
.credits .nm { font-family: 'Noto Serif CJK SC', serif; font-size: 15pt;
               text-align: right; font-weight: 600; }
.info { top: 13.25in; font-size: 12.5pt; letter-spacing: .06em;
        padding-left: .06em; color: #222; }
.inst { top: 13.75in; font-size: 11pt; letter-spacing: .12em;
        padding-left: .12em; color: #444; }
.inst .cjk { font-size: 10pt; letter-spacing: .05em; color: #666; }
.sig { top: 15.1in; font-family: 'Noto Serif CJK SC', serif; font-size: 13pt;
       letter-spacing: .5em; padding-left: .5em; }
.sig2 { top: 15.5in; font-size: 9.5pt; letter-spacing: .35em; padding-left: .35em;
        text-transform: uppercase; color: #555; }

/* running header / footer on the music pages (transparent overlay) */
.hd { position: absolute; top: .42in; left: .6in; right: .6in; height: .42in;
      border-bottom: .45pt solid #888; }
.hd .l { position: absolute; left: 0; bottom: 6pt; font-size: 10.5pt; }
.hd .l .t { font-family: 'Noto Serif CJK SC', serif; font-weight: 600;
            letter-spacing: .08em; }
.hd .l .x { color: #555; margin-left: 10pt; font-size: 8.5pt;
            letter-spacing: .25em; text-transform: uppercase; }
/* page number: a real bold face with lining figures (EB Garamond has no
   bold here, so Chromium would fake one) */
.hd .r { position: absolute; right: 0; bottom: 3pt; font-size: 21pt;
         font-family: 'Noto Serif CJK SC', serif; font-weight: 700; }
/* one flex row, baseline-aligned: the credit line and "PAGE n OF N" have
   different sizes but must share a baseline */
.ft { position: absolute; bottom: .38in; left: .6in; right: .6in;
      height: .36in; border-top: .45pt solid #888; font-size: 9pt;
      padding-top: 7pt; display: flex; justify-content: space-between;
      align-items: baseline; }
.ft .l .cjk { letter-spacing: .08em; }
.ft .l .en { color: #555; margin-left: 8pt; font-style: italic; }
.ft .l .en .nm { font-style: normal; }  /* no fake-italic Chinese */
.ft .r { letter-spacing: .2em; margin-right: -.2em; /* flush with the rule */
         text-transform: uppercase; font-size: 8pt; color: #333; }
"""


def _e(s):
    return html.escape(str(s))


def _sym(s):
    """Wrap music glyphs EB Garamond lacks (♩ ♪ ♭ ♯, and the note values
    𝅝 𝅗𝅥 𝅘𝅥 for a "𝅗𝅥 = 69" in cut time) in a fallback font."""
    out = []
    for ch in _e(s):
        if ch in "♩♪♭♯♮":
            out.append(f"<span class='sym'>{ch}</span>")
        elif 0x1D100 <= ord(ch) <= 0x1D1FF:  # Musical Symbols block
            out.append(f"<span class='note'>{ch}</span>")
        else:
            out.append(ch)
    # a note value and its combining stem go in one span
    return "".join(out).replace("</span><span class='note'>", "")


def cover_html(m):
    rows = [("作曲", "Music", m["composer"]), ("作词", "Lyrics", m["lyricist"]),
            ("原唱", "Original Artist", m["artist"]),
            ("原作", "Original Work", m["original"]),
            ("改编", "Arranged by", m["arranger"]),
            ("制谱", "Music Preparation", m["engraver"])]
    trs = "".join(
        f"<tr><td class='zh'>{_e(a)}</td><td class='en'>{_e(b)}</td>"
        f"<td class='nm'>{_e(c)}</td></tr>" for a, b, c in rows if c)
    info = "　·　".join(_sym(x) for x in (m["key"], m["tempo"], m["duration"])
                       if x)
    inst = "　·　".join(
        f"{_e(en)} <span class='cjk'>{_e(zh)}</span>"
        for en, zh in m["instrumentation"])
    return f"""
<div class='page cover'>
  <div class='frame'></div>
  <div class='cv kicker'>Full Score</div>
  <div class='cv kicker2'>Score in C · Concert Pitch</div>
  <div class='cv title'>{_e(m['title'])}</div>
  <div class='cv latin'>{_e(m['title_latin'])}</div>
  <div class='cv orn'><span></span><b></b><span></span></div>
  <div class='cv sub'>{_e(m['subtitle'])}</div>
  <div class='cv suben'>{_e(m['subtitle_en'])}</div>
  <table class='credits'>{trs}</table>
  <div class='cv info'>{info}</div>
  <div class='cv inst'>{inst}</div>
  <div class='cv sig'>{_e(m['arranger'])}</div>
  <div class='cv sig2'>Arrangement &amp; Music Preparation{
      ' · ' + _e(m['year']) if m['year'] else ''}</div>
</div>"""


def overlay_html(m, page, total):
    same = m["arranger"] == m["engraver"]
    who = (f"<span class='cjk'>改编 · 制谱　{_e(m['arranger'])}</span>"
           "<span class='en'>Arranged &amp; Music Preparation by "
           f"<span class='nm'>{_e(m['arranger'])}</span></span>") if same else (
           f"<span class='cjk'>改编　{_e(m['arranger'])}　·　制谱　"
           f"{_e(m['engraver'])}</span>")
    head = _e(m["title"]) + (f" · {_e(m['subtitle'].split('·')[0].strip())}"
                             if m["subtitle"] else "")
    return f"""
<div class='page'>
  <div class='hd'><div class='l'><span class='t'>{head}</span>
    <span class='x'>Full Score in C</span></div>
    <div class='r'>{page}</div></div>
  <div class='ft'><div class='l'>{who}</div>
    <div class='r'>Page {page} of {total}</div></div>
</div>"""


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------
def _style_file(tmp, overrides):
    """hollywood.mss, or a copy with song-specific values
    (META["style"] = {"measureSpacing": 1.1, ...}) for dense music."""
    if not overrides:
        return STYLE
    x = open(STYLE, encoding="utf-8").read()
    for k, v in overrides.items():
        tag = f"<{k}>{v}</{k}>"
        if re.search(rf"<{k}>[^<]*</{k}>", x):
            x = re.sub(rf"<{k}>[^<]*</{k}>", tag, x)
        else:
            x = x.replace("</Style>", f"  {tag}\n  </Style>", 1)
    path = os.path.join(tmp, "style.mss")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(x)
    return path


def render_pdf(musicxml, out_pdf, meta, png_dir=None):
    from pypdf import PdfReader, PdfWriter
    m = _meta(meta)
    with tempfile.TemporaryDirectory() as tmp:
        mscz = os.path.join(tmp, "score.mscz")
        score_pdf = os.path.join(tmp, "score.pdf")
        _ms4(["-o", mscz, musicxml])            # import MusicXML
        _fix_title_frame(mscz)
        _lift_sections(mscz, m.get("section_lift", SECTION_LIFT_SP))
        _engrave_fixes(mscz)
        if m.get("mscx_hook"):  # song-specific touch-ups, see SKILL.md
            _edit_mscx(mscz, m["mscx_hook"])
        style = _style_file(tmp, m.get("style"))
        _ms4(["-S", style, "-o", score_pdf, mscz])  # engrave with house style
        score = PdfReader(score_pdf)
        n = len(score.pages)
        doc = ("<!doctype html><html><head><meta charset='utf-8'><style>"
               + CSS + "</style></head><body>" + cover_html(m)
               + "".join(overlay_html(m, i + 1, n) for i in range(n))
               + "</body></html>")
        hp = os.path.join(tmp, "pages.html")
        open(hp, "w", encoding="utf-8").write(doc)
        ov_pdf = os.path.join(tmp, "pages.pdf")
        _chrome_pdf(hp, ov_pdf)
        ov = PdfReader(ov_pdf)
        assert len(ov.pages) == n + 1, (len(ov.pages), n)
        w = PdfWriter()
        w.add_page(ov.pages[0])
        for i in range(n):
            pg = score.pages[i]
            pg.merge_page(ov.pages[i + 1])
            w.add_page(pg)
        who = " / ".join(x for x in (
            f"{m['composer']} 曲" if m["composer"] else "",
            f"{m['lyricist']} 词" if m["lyricist"] else "") if x)
        w.add_metadata({
            "/Title": f"{m['title']} — {m['subtitle']} (Full Score)",
            "/Author": (who + " · " if who else "")
                       + f"改编 {m['arranger']} · 制谱 {m['engraver']}",
            "/Subject": m["subtitle_en"],
            "/Creator": "MuseScore Studio 4 + tools/hollywood"})
        _fix_text_layer(w)
        with open(out_pdf, "wb") as fh:
            w.write(fh)
        if png_dir:
            os.makedirs(png_dir, exist_ok=True)
            for f in glob.glob(os.path.join(png_dir, "page-*.png")):
                os.remove(f)
            subprocess.run(["pdftoppm", "-r", "60", "-png", out_pdf,
                            os.path.join(png_dir, "page")], check=True)
    return n + 1


def _load_build(path):
    spec = importlib.util.spec_from_file_location("song_build", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    b = _load_build(sys.argv[1])
    b.write_pdf()
