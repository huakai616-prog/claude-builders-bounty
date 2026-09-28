#!/usr/bin/env python3
"""情歌 — 好莱坞标准总谱 PDF（LilyPond 排版，带封面）

Reads the score from build.py (single source of truth) and engraves
output/情歌_总谱.pdf with LilyPond:
  * cover page: title, Full Score / Score in C, credits, instrumentation
  * page-1 title block with "Score in C" and the credits
  * a bar number centred under every bar, boxed rehearsal letters and
    tempo marks above both the voice and the strings
  * running header (title + page number) from page 2, credit footer on
    page 1

Needs: apt-get install lilypond fonts-noto-cjk fonts-texgyre
Usage: python3 engrave.py            (writes the PDF)
       python3 engrave.py --png DIR  (also one PNG per page, for proofing)
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

import build as B

LY_DUR = {1: "16", 2: "8", 3: "8.", 4: "4", 6: "4.", 8: "2", 12: "2.",
          16: "1"}
TOTAL = B.NBARS * B.BAR16

# Engraving choices for this score
STAFF_SIZE = 17.5
BREAKS = (5, 8, 11, 13)         # bars that start a new system
PAGE_BREAKS = (8, 13)           # bars that start a new page
SHORT = {"vox": "V.", "vn1": "Vln. I", "vn2": "Vln. II", "va": "Vla.",
         "vc": "Vc."}
MARKS = B.REHEARSAL
DURATION = "0′56″"
COLOPHON_DATE = "2026 年 9 月"
LATIN_SERIF = "TeX Gyre Pagella"
# (part, bar, 16th) -> LilyPond command put before that note
TWEAKS = {
    # Vln II G4 tied into the last bar: bow the tie clear of the bottom line
    ("vn2", 14, 8): "\\shape #'((0 . -0.5) (0 . -1.1) (0 . -1.1) "
                    "(0 . -0.5)) Tie ",
}
# LilyPond 2.24 ignores the face index of a .ttc collection and always
# takes face 0, which for Noto CJK is the JAPANESE face (different glyphs
# for e.g. 直 骨). So the Simplified Chinese faces are extracted into
# standalone fonts under their own family names and loaded from a cache.
CJK_SERIF = "QG Serif SC"
CJK_SANS = "QG Sans SC"
NOTO = "/usr/share/fonts/opentype/noto"
SC_FONTS = {  # (family, style) -> source collection
    (CJK_SERIF, "Regular"): f"{NOTO}/NotoSerifCJK-Regular.ttc",
    (CJK_SERIF, "Bold"): f"{NOTO}/NotoSerifCJK-Bold.ttc",
    (CJK_SANS, "Regular"): f"{NOTO}/NotoSansCJK-Regular.ttc",
    (CJK_SANS, "Light"): f"{NOTO}/NotoSansCJK-Light.ttc",
}
FONT_DIR = os.path.join(os.path.expanduser("~"), ".cache", "qingge-fonts")


def ensure_sc_fonts():
    """Extract the SC face of each Noto CJK collection (needs fonttools)."""
    from fontTools.ttLib import TTCollection
    os.makedirs(FONT_DIR, exist_ok=True)
    for (fam, style), src in SC_FONTS.items():
        ps = f"{fam.replace(' ', '')}-{style}"
        out = os.path.join(FONT_DIR, ps + ".otf")
        if os.path.exists(out):
            continue
        coll = TTCollection(src, lazy=True)
        font = next(f for f in coll.fonts
                    if "CJKsc-" in (f["name"].getDebugName(6) or ""))
        name = font["name"]
        name.names = [n for n in name.names if n.nameID > 6 and
                      n.nameID not in (16, 17)]
        legacy = fam if style in ("Regular", "Bold") else f"{fam} {style}"
        sub = style if style in ("Regular", "Bold") else "Regular"
        for nid, val in ((1, legacy), (2, sub), (3, ps), (4, f"{fam} {style}"),
                         (6, ps), (16, fam), (17, style)):
            name.setName(val, nid, 3, 1, 0x409)
            name.setName(val, nid, 1, 0, 0)
        if "CFF " in font:
            cff = font["CFF "].cff
            cff.fontNames = [ps]
            top = cff.topDictIndex[0]
            for k, v in (("FullName", f"{fam} {style}"), ("FamilyName", fam)):
                if hasattr(top, k):
                    setattr(top, k, v)
        font.save(out)


def pos(bar, s16):
    return (bar - 1) * B.BAR16 + s16


def ly_pitch(p):
    s, acc, o = re.fullmatch(r"([A-G])([#b]?)(-?\d)", p).groups()
    o = int(o)
    return (s.lower() + {"#": "is", "b": "es", "": ""}[acc]
            + ("'" * (o - 3) if o >= 3 else "," * (3 - o)))


def ly_str(t):
    return '"' + t.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
def ly_notes(events, pid=None):
    """One LilyPond line per bar."""
    by_bar = {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    lines = []
    for b in range(1, B.NBARS + 1):
        evs = by_bar[b]
        last_bar = b == B.NBARS
        if len(evs) == 1 and evs[0]["pitches"] is None:
            # the final bar gets a real whole rest so its fermata lines up
            # with the strings' final chord
            lines.append("r1\\fermata |" if last_bar else "R1 |")
            continue
        toks = []
        for e in evs:
            if (pid, b, e["pos"]) in TWEAKS:
                toks.append(TWEAKS[pid, b, e["pos"]])
            if e["grace"]:
                toks.append(f"\\slashedGrace {{ {ly_pitch(e['grace'])}16 }}")
            pieces = (B.split_rest if e["pitches"] is None
                      else B.split_dur)(e["pos"], e["dur"])
            for i, d in enumerate(pieces):
                first, last = i == 0, i == len(pieces) - 1
                if e["pitches"] is None:
                    toks.append("r" + LY_DUR[d])
                    continue
                ps = [ly_pitch(x) for x in e["pitches"]]
                t = (ps[0] if len(ps) == 1 else "<" + " ".join(ps) + ">")
                if e["lyric"] == B.BREATH:
                    t = "\\xNote " + t
                t += LY_DUR[d]
                if not last or e["tie"]:
                    t += "~"
                if first and e["accent"]:
                    t += "->"
                if last_bar and last:
                    t += "\\fermata"
                if first and e["slur_start"]:
                    t += "("
                if last and e["slur_end"]:
                    t += ")"
                toks.append(t)
        lines.append(" ".join(toks) + " |")
    return "\n  ".join(lines)


def ly_lyrics(events):
    out = []
    ext = iter(B.melisma_marks(events))
    for e in events:
        if e["lyric"] == B.BREATH:
            out.append("\\markup \\pad-x #0.7 \\override "
                       "#'(font-name . \"TeX Gyre Pagella Italic\") "
                       "\\fontsize #-0.5 br")
        elif e["lyric"]:
            out.append(e["lyric"] + (" __" if next(ext) else ""))
    return " ".join(out)


# ---------------------------------------------------------------------------
# Spacer voices: dynamics / hairpins / words per part, and the global line
# ---------------------------------------------------------------------------
def spacer_line(att):
    """att: list (len TOTAL+1) of lists of post-events per 16th."""
    out, run = [], 0
    for t in range(TOTAL):
        if att[t]:
            if run:
                out.append(f"s16*{run}")
                run = 0
            out.append("s16" + "".join(att[t]))
        else:
            run += 1
        if (t + 1) % B.BAR16 == 0:
            if run:
                out.append(f"s16*{run}")
                run = 0
            out.append("|\n  ")
    return " ".join(out)


def ly_dynamics(p):
    att = [[] for _ in range(TOTAL + 1)]
    dyn_at = {pos(b, s) for b, s, _ in p["dyn"]}
    starts = {pos(b, s) for b, s, *_ in p["hair"]}
    joined = {(b, s): t for b, s, t in p["text"] if t in B.MOOD_WORDS}
    for b, s, mark in p["dyn"]:
        if (b, s) in joined:
            att[pos(b, s)].append(
                "-\\tweak self-alignment-X #LEFT "
                "#(make-dynamic-script (markup #:dynamic "
                f"\"{mark}\" #:normal-text #:italic \" {joined[b, s]}\"))")
        elif b == B.NBARS and s == 0:
            # final chord: start the dynamic under the notehead, clear of
            # the barline
            att[pos(b, s)].append("-\\tweak self-alignment-X #LEFT \\"
                                  + mark)
        else:
            att[pos(b, s)].append("\\" + mark)
    for b, s, b2, s2, kind in p["hair"]:
        a, z = pos(b, s), pos(b2, s2)
        att[a].append("\\<" if kind == "cresc" else
                      "-\\tweak circled-tip ##t \\>" if kind == "niente"
                      else "\\>")
        end = z + 1
        if end >= TOTAL:
            att[z].append("\\!")
        elif end not in dyn_at and end not in starts:
            att[end].append("\\!")
    for b, s, txt in p["text"]:
        if (b, s) in joined:
            continue
        att[pos(b, s)].append(
            f"^\\markup \\whiteout \\italic {ly_str(txt)}")
    return spacer_line(att)


def tempo_markup(text, bpm=None):
    if bpm is None:
        return f"\\tempo \\markup \\bold {ly_str(text)}"
    return ("\\tempo \\markup { \\bold " + ly_str(text) + " \\hspace #1.2 "
            "\\concat { \\fontsize #-1.5 \\general-align #Y #DOWN "
            "\\note {4} #UP \\normal-text \" = " + str(bpm) + "\" } }")


def ly_global(with_marks, spacer_rests=False):
    att = [[] for _ in range(TOTAL + 1)]
    att[0].append(tempo_markup(B.TEMPO_MARK, B.TEMPI[0][2]))
    for b, s, txt in B.TEMPO_TEXT:
        att[pos(b, s)].append(tempo_markup(txt))
    if with_marks:
        for b, (letter, label) in MARKS.items():
            att[pos(b, 0)].append(
                "\\mark \\markup \\concat { \\box \\pad-markup #0.35 "
                f"\\sans \\bold \\fontsize #3 {ly_str(letter)} "
                "\\hspace #1.2 "
                f"\\sans \\fontsize #-1 {ly_str(label)} }}")
    for b in range(2, B.NBARS + 1):
        if b in PAGE_BREAKS:
            att[pos(b, 0)].insert(0, "\\pageBreak ")
        elif b in BREAKS:
            att[pos(b, 0)].insert(0, "\\break ")
        else:
            att[pos(b, 0)].insert(0, "\\noBreak ")
    # post-events have to follow the spacer; commands go before it
    out, run = [], 0
    for t in range(TOTAL - B.BAR16):
        cmds = [x for x in att[t]]
        if cmds:
            if run:
                out.append(f"s16*{run}")
                run = 0
            out.append(" ".join(cmds) + " s16")
        else:
            run += 1
        if (t + 1) % B.BAR16 == 0:
            if run:
                out.append(f"s16*{run}")
                run = 0
            out.append("|\n  ")
    # last bar: hidden rests give the final chord real spacing columns
    # (spacer rests do not), so it is not squeezed
    last = [x for t in range(TOTAL - B.BAR16, TOTAL) for x in att[t]]
    out.append(" ".join(last) + (" \\hide Rest r2 r2 |" if spacer_rests
                                  else " s1 |"))
    out.append('\\bar "|."')
    return " ".join(out)


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def cover():
    inst = " · ".join(p["name"] for p in B.PARTS)
    credit_rows = [("作词", B.LYRICIST), ("作曲", B.COMPOSER),
                   ("原唱", B.SINGER), ("改编", B.ARRANGER),
                   ("制谱", B.ENGRAVER)]
    labels = " ".join(ly_str(a) for a, _ in credit_rows)
    names = " ".join(ly_str(n) for _, n in credit_rows)
    return f"""\\markup {{
  \\override #'(baseline-skip . 3.2)
  \\column {{
    \\vspace #1
    \\fill-line {{ \\sans \\fontsize #0.5 \\override #'(word-space . 1.6)
      \\line {{ F U L L \\hspace #2 S C O R E }} }}
    \\vspace #0.6
    \\fill-line {{ \\sans \\fontsize #-1 "Score in C" }}
    \\vspace #9
    \\fill-line {{ \\override #'(font-name . "{CJK_SERIF} Bold")
      \\abs-fontsize #60 {ly_str(" ".join(B.TITLE))} }}
    \\vspace #2.2
    \\fill-line {{ \\override #'(font-name . "{CJK_SERIF}")
      \\abs-fontsize #15 {ly_str(B.SUBTITLE)} }}
    \\vspace #0.4
    \\fill-line {{ \\abs-fontsize #12.5 \\italic {ly_str(B.SUBTITLE_EN)} }}
    \\vspace #3.2
    \\fill-line {{ \\draw-line #'(22 . 0) }}
    \\vspace #3.2
    \\fill-line {{ \\override #'(baseline-skip . 3.4)
      \\line {{
        \\override #'(font-name . "{CJK_SANS} Light")
        \\abs-fontsize #11 \\right-column {{ {labels} }}
        \\hspace #3
        \\override #'(font-name . "{CJK_SERIF}")
        \\abs-fontsize #11 \\left-column {{ {names} }}
      }} }}
    \\vspace #15
    \\fill-line {{ \\draw-line #'(60 . 0) }}
    \\vspace #1.2
    \\fill-line {{ \\abs-fontsize #10 {ly_str(inst)} }}
    \\vspace #0.3
    \\fill-line {{ \\abs-fontsize #10 \\concat {{
      "F major · " \\fontsize #-2 \\general-align #Y #DOWN \\note {{4}} #UP
      " = {B.TEMPI[0][2]} · ca. {DURATION}" }} }}
  }}
}}
\\pageBreak
"""


def title_block():
    return f"""\\markup {{
  \\override #'(baseline-skip . 3)
  \\column {{
    \\fill-line {{
      \\sans \\bold \\fontsize #-0.5 "Score in C"
      \\override #'(font-name . "{CJK_SERIF} Bold") \\abs-fontsize #26
        {ly_str(B.TITLE)}
      \\sans \\bold \\fontsize #-0.5 "Full Score"
    }}
    \\vspace #0.9
    \\fill-line {{ \\override #'(font-name . "{CJK_SERIF}")
      \\abs-fontsize #11.5 {ly_str(B.SUBTITLE)} }}
    \\vspace #0.5
    \\fill-line {{
      \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #9.5
        \\left-column {{ {ly_str("作词：" + B.LYRICIST)}
                         {ly_str("原唱：" + B.SINGER)} }}
      \\null
      \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #9.5
        \\right-column {{ {ly_str("作曲：" + B.COMPOSER)}
                          {ly_str("改编：" + B.ARRANGER)}
                          {ly_str("制谱：" + B.ENGRAVER)} }}
    }}
  }}
}}
"""


def paper():
    footer = (f"{B.TITLE} · {B.SUBTITLE}　　原曲：作词 {B.LYRICIST} · "
              f"作曲 {B.COMPOSER} · 原唱 {B.SINGER}　　"
              f"改编 · 制谱：{B.ARRANGER}")
    return f"""
#(define-markup-command (from-page layout props n arg) (number? markup?)
   (if (>= (chain-assoc-get 'page:page-number props 0) n)
       (interpret-markup layout props arg)
       empty-stencil))
#(define-markup-command (on-page layout props n arg) (number? markup?)
   (if (= (chain-assoc-get 'page:page-number props 0) n)
       (interpret-markup layout props arg)
       empty-stencil))

\\paper {{
  #(set-paper-size "a4")
  #(define fonts
     (set-global-fonts
       #:roman "{LATIN_SERIF}, {CJK_SERIF}"
       #:sans "TeX Gyre Heros, {CJK_SANS}"
       #:typewriter "DejaVu Sans Mono"
       #:factor (/ staff-height pt 20)))
  top-margin = 12\\mm
  bottom-margin = 12\\mm
  left-margin = 15\\mm
  right-margin = 13\\mm
  indent = 21\\mm
  short-indent = 11\\mm
  first-page-number = 0
  print-first-page-number = ##f
  bookTitleMarkup = ##f
  scoreTitleMarkup = ##f
  ragged-last = ##f
  ragged-bottom = ##f
  ragged-last-bottom = ##t
  markup-system-spacing = #'((basic-distance . 10) (minimum-distance . 6)
                             (padding . 3) (stretchability . 4))
  system-system-spacing = #'((basic-distance . 16) (minimum-distance . 10)
                             (padding . 5) (stretchability . 40))
  last-bottom-spacing = #'((basic-distance . 10) (minimum-distance . 8)
                           (padding . 6) (stretchability . 30))
  top-system-spacing = #'((basic-distance . 12) (minimum-distance . 8)
                          (padding . 4) (stretchability . 0))
  system-separator-markup = \\slashSeparator
  oddHeaderMarkup = \\markup \\from-page #2 \\fill-line {{
    \\sans \\fontsize #-2 \\concat {{ {ly_str(B.TITLE)} " · Full Score" }}
    \\sans \\bold \\fontsize #1 \\fromproperty #'page:page-number-string
  }}
  evenHeaderMarkup = \\markup \\from-page #2 \\fill-line {{
    \\sans \\bold \\fontsize #1 \\fromproperty #'page:page-number-string
    \\sans \\fontsize #-2 \\concat {{ {ly_str(B.TITLE)} " · Full Score" }}
  }}
  oddFooterMarkup = \\markup \\on-page #1 \\fill-line {{
    \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #7.5
      {ly_str(footer)}
  }}
  evenFooterMarkup = \\markup \\on-page #1 \\fill-line {{ \\null }}
}}
"""


def layout():
    return """
\\layout {
  \\context {
    \\Score
    \\remove Bar_number_engraver
    \\remove Metronome_mark_engraver
    \\remove Mark_engraver
    \\remove Staff_collecting_engraver
    \\override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/32)
    \\override RehearsalMark.self-alignment-X = #LEFT
    \\override RehearsalMark.padding = #1.6
    \\override RehearsalMark.outside-staff-padding = #1.4
    \\override DynamicLineSpanner.padding = #1.1
    \\override DynamicLineSpanner.outside-staff-padding = #0.9
    \\override MetronomeMark.outside-staff-padding = #0.9
    \\override MetronomeMark.padding = #1.8
    \\override Script.padding = #0.45
    \\override RehearsalMark.outside-staff-priority = #1500
    \\override MetronomeMark.outside-staff-priority = #1400
    \\override TextScript.outside-staff-priority = #450
    \\override Hairpin.minimum-length = #4
    \\override Hairpin.to-barline = ##t
    \\override DynamicTextSpanner.style = #'none
    \\override StaffGrouper.staffgroup-staff-spacing =
      #'((basic-distance . 11) (minimum-distance . 8) (padding . 1.6))
    \\override StaffGrouper.staff-staff-spacing =
      #'((basic-distance . 10) (minimum-distance . 7.5) (padding . 1.4))
  }
  \\context {
    \\Staff
    \\override InstrumentName.self-alignment-X = #RIGHT
    \\override InstrumentName.padding = #0.8
  }
  \\context {
    \\Lyrics
    \\override LyricText.font-size = #0.6
    \\override LyricText.font-name = "QG Serif SC"
    \\override LyricExtender.thickness = #1.2
    \\override LyricExtender.right-padding = #0.9
    \\override LyricSpace.minimum-distance = #1.3
    \\override VerticalAxisGroup.nonstaff-relatedstaff-spacing.padding = #1.2
    \\override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing.padding = #3.5
  }
}
"""


def staff(p, parsed, top_marks):
    pid = p["id"]
    clef = {"vox": "treble", "vn1": "treble", "vn2": "treble",
            "va": "alto", "vc": "bass"}[pid]
    extra = []
    if pid == "vc":
        # clear the accents under the low C2 hits
        extra += ["\\override DynamicLineSpanner.padding = #1.7"]
    if pid in ("vox", "vn1"):
        extra += ["\\consists Mark_engraver",
                  "\\consists Staff_collecting_engraver",
                  "\\consists Metronome_mark_engraver"]
    name = p["name"]
    notes = ly_notes(parsed[pid], pid)
    glob = ly_global(with_marks=top_marks, spacer_rests=pid == "vn1") \
        if pid in ("vox", "vn1") \
        else ("s1*%d \\bar \"|.\"" % B.NBARS)
    dyn_up = "\\dynamicUp " if pid == "vox" else ""
    voice_name = f'= "{pid}"'
    return f"""
    \\new Staff = "{pid}" \\with {{
      instrumentName = {ly_str(name)}
      shortInstrumentName = {ly_str(SHORT[pid])}
      {" ".join(extra)}
    }} <<
      \\new Voice {voice_name} {{
        \\clef {clef} \\key f \\major \\numericTimeSignature \\time 4/4
        {notes}
      }}
      \\new Voice {{ {dyn_up}
        {ly_dynamics(p)}
      }}
      \\new Voice {{
        {glob}
      }}
    >>"""


def ly_source():
    parsed = {p["id"]: B.parse_part(p["data"]) for p in B.PARTS}
    parts = {p["id"]: p for p in B.PARTS}
    vox = staff(parts["vox"], parsed, True)
    lyr = ly_lyrics(parsed["vox"])
    strings = "".join(staff(parts[x], parsed, x == "vn1")
                      for x in ("vn1", "vn2", "va", "vc"))
    return f"""\\version "2.24.0"
#(ly:font-config-add-directory "{FONT_DIR}")
#(set-global-staff-size {STAFF_SIZE})
{paper()}
\\book {{
{cover()}
{title_block()}
\\score {{
  <<
{vox}
    \\new Lyrics \\lyricsto "vox" {{ {lyr} }}
    \\new StaffGroup \\with {{ systemStartDelimiter = #'SystemStartBracket }}
    <<{strings}
    >>
    \\new Dynamics \\with {{
      \\consists Measure_counter_engraver
      \\override MeasureCounter.font-encoding = #'latin1
      \\override MeasureCounter.font-series = #'bold
      \\override MeasureCounter.font-family = #'sans
      \\override MeasureCounter.font-size = #0.5
      \\override MeasureCounter.outside-staff-priority = ##f
      \\override MeasureCounter.Y-offset = #0
      \\override MeasureCounter.stencil =
        #(make-stencil-boxer 0.1 0.45 ly:text-interface::print)
      \\override VerticalAxisGroup.nonstaff-relatedstaff-spacing =
        #'((basic-distance . 8.5) (minimum-distance . 6) (padding . 2))
    }} {{ \\startMeasureCount s1*{B.NBARS} \\stopMeasureCount }}
  >>
{layout()}
}}
\\markup {{ \\vspace #3 \\fill-line {{ \\null
  \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #8.5
  \\right-column {{ {ly_str("改编 · 制谱：" + B.ARRANGER)}
                    {ly_str(COLOPHON_DATE)} }} }} }}
}}
"""


def main():
    os.makedirs(B.OUT, exist_ok=True)
    ensure_sc_fonts()
    pdf = os.path.join(B.OUT, f"{B.NAME}_总谱.pdf")
    with tempfile.TemporaryDirectory() as tmp:
        ly = os.path.join(tmp, "score.ly")
        with open(ly, "w", encoding="utf-8") as fh:
            fh.write(ly_source())
        if "--ly" in sys.argv:
            shutil.copy(ly, sys.argv[sys.argv.index("--ly") + 1])
        r = subprocess.run(["lilypond", "-dno-point-and-click", "-o",
                            os.path.join(tmp, "score"), ly],
                           capture_output=True, text=True)
        log = r.stderr
        warn = [x for x in log.splitlines()
                if "warning" in x.lower() or "error" in x.lower()]
        for x in warn:
            print(x)
        if r.returncode != 0:
            print(log)
            sys.exit(1)
        shutil.copy(os.path.join(tmp, "score.pdf"), pdf)
        if "--png" in sys.argv:
            d = sys.argv[sys.argv.index("--png") + 1]
            os.makedirs(d, exist_ok=True)
            subprocess.run(["lilypond", "-dno-point-and-click", "--png",
                            "-dresolution=150", "-o",
                            os.path.join(d, "page"), ly],
                           capture_output=True, text=True, check=True)
    print("written", pdf)


if __name__ == "__main__":
    main()
