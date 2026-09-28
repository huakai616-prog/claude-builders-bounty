#!/usr/bin/env python3
"""诀别书 — 好莱坞标准总谱与分谱（LilyPond 排版，Chromium 封面）

Reads the arrangement from build.py (single source of truth) and writes:
  * output/诀别书_弦乐五重奏_总谱.pdf   11 x 17 in full score, Score in C:
      cover page; first-page title block; running header (title, page
      number) and footer (credits, "Page n of N") on every music page; a
      boxed bar number under every bar; boxed rehearsal letters with the
      section name; tempo and expression marks
  * output/分谱/诀别书_分谱_<n>_<part>.pdf  9 x 12 in parts with
      multi-bar rests, rehearsal letters and the same header / footer
  * output/诀别书_弦乐五重奏_全部分谱.pdf  all parts in one file

Needs: apt-get install lilypond fonts-noto-cjk fonts-ebgaramond
       fonts-texgyre poppler-utils; pip install pypdf; Chromium (Playwright's
       /opt/pw-browsers, or set CHROME=...) for the cover.
Usage: python3 engrave.py [--png DIR]   (DIR gets one PNG per page)
"""
import glob
import html
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

SCORE_STAFF_SIZE = 19.5
PART_STAFF_SIZE = 21
LATIN_SERIF = "EB Garamond"
CJK_SERIF = "Noto Serif CJK SC"
CJK_SANS = "Noto Sans CJK SC"
LATIN_SANS = "TeX Gyre Heros"


def pos(bar, s16):
    return (bar - 1) * B.BAR16 + s16


def ly_pitch(p, octave=0):
    s, acc, o = re.fullmatch(r"([A-G])(#|##|b|bb)?(-?\d)", p).groups()
    o = int(o) + octave // 12
    accs = {"": "", "#": "is", "##": "isis", "b": "es", "bb": "eses"}
    return (s.lower() + accs[acc or ""]
            + ("'" * (o - 3) if o >= 3 else "," * (3 - o)))


def ly_str(t):
    return '"' + str(t).replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------
def ly_notes(p, events, part_mode=False):
    """One LilyPond line per bar."""
    octv = p.get("written_octave", 0)
    by_bar = {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    ott = [((b1 - 1) * B.BAR16 + s1, (b2 - 1) * B.BAR16 + s2)
           for b1, s1, b2, s2 in B.OTTAVA.get(p["id"], [])]
    ott_on = False
    lines = []
    for b in range(1, B.NBARS + 1):
        evs = by_bar[b]
        if len(evs) == 1 and evs[0]["pitches"] is None and not ott_on:
            lines.append("R1" + ("\\fermata" if evs[0]["fermata"] else "")
                         + " |")
            continue
        toks = []
        for e in evs:
            inside = any(a <= e["abs"] <= z for a, z in ott)
            if inside and not ott_on:
                toks.append("\\ottava #1")
                ott_on = True
            elif ott_on and not inside:
                toks.append("\\ottava #0")
                ott_on = False
            if e["grace"]:
                toks.append("\\slashedGrace { "
                            f"{ly_pitch(e['grace'], octv)}8 }}")
            pieces = (B.split_rest if e["pitches"] is None
                      else B.split_dur)(e["pos"], e["dur"])
            for i, d in enumerate(pieces):
                first, last = i == 0, i == len(pieces) - 1
                if e["pitches"] is None:
                    toks.append("r" + LY_DUR[d]
                                + ("\\fermata" if e["fermata"] and last
                                   else ""))
                    continue
                ps = [ly_pitch(x, octv) for x in e["pitches"]]
                t = ps[0] if len(ps) == 1 else "<" + " ".join(ps) + ">"
                t += LY_DUR[d]
                if e["trem"]:
                    t += ":16" if d >= 4 else ":16" if d == 2 else ""
                if not last or e["tie"]:
                    t += "~"
                if first and e["accent"]:
                    t += "->"
                if first and e["marcato"]:
                    t += "-^"
                if first and e["stacc"]:
                    t += "-."
                if first and e["tenuto"]:
                    t += "--"
                if last and e["fermata"]:
                    t += "\\fermata"
                if first and e["slur_start"]:
                    t += "("
                if last and e["slur_end"]:
                    t += ")"
                toks.append(t)
        lines.append(" ".join(toks) + " |")
    if ott_on:
        lines.append("\\ottava #0")
    return "\n    ".join(lines)


# ---------------------------------------------------------------------------
# Spacer voices: dynamics / hairpins / words / clefs per part
# ---------------------------------------------------------------------------
def spacer_line(att, pre=None):
    """att: list (len TOTAL+1) of post-events per 16th; pre: commands that
    go before the spacer (clefs)."""
    pre = pre or [[] for _ in range(TOTAL + 1)]
    out, run = [], 0
    for t in range(TOTAL):
        if att[t] or pre[t]:
            if run:
                out.append(f"s16*{run}")
                run = 0
            out.append(" ".join(pre[t]) + " s16" + "".join(att[t]))
        else:
            run += 1
        if (t + 1) % B.BAR16 == 0:
            if run:
                out.append(f"s16*{run}")
                run = 0
            out.append("|\n    ")
    return " ".join(out)


DYN_WORDS = {"sfz", "fp", "sf", "ppp", "pp", "p", "mp", "mf", "f", "ff",
             "fff"}


def ly_dynamics(p):
    att = [[] for _ in range(TOTAL + 1)]
    pre = [[] for _ in range(TOTAL + 1)]
    dyn_at = {pos(b, s) for b, s, _ in p["dyn"]}
    starts = {pos(b, s) for b, s, *_ in p["hair"]}
    for b, s, mark in p["dyn"]:
        att[pos(b, s)].append("\\" + mark)
    for b, s, b2, s2, kind in p["hair"]:
        a, z = pos(b, s), pos(b2, s2)
        att[a].append("\\<" if kind == "cresc" else "\\>")
        end = z + 1
        if end >= TOTAL:
            att[z].append("\\!")
        elif end not in dyn_at and end not in starts:
            att[end].append("\\!")
    for b, s, txt in p["text"]:
        att[pos(b, s)].append(
            f"^\\markup \\whiteout \\italic {ly_str(txt)}")
    for b, s, c in B.CLEFS.get(p["id"], []):
        pre[pos(b, s)].append(f"\\clef {c}")
    return spacer_line(att, pre)


def tempo_markup(text, bpm=None):
    if bpm is None:
        return f"\\tempo \\markup \\bold {ly_str(text)}"
    return ("\\tempo \\markup { \\bold " + ly_str(text) + " \\hspace #1.2 "
            "\\concat { \\fontsize #-1.5 \\general-align #Y #DOWN "
            "\\note {4} #UP \\normal-text \" = " + str(bpm) + "\" } }")


def mark_markup(letter, en, zh, size=3.2):
    return ("\\mark \\markup \\concat { \\box \\pad-markup #0.45 "
            f"\\sans \\bold \\fontsize #{size} {ly_str(letter)} "
            "\\hspace #1.4 \\general-align #Y #-0.4 \\sans \\bold "
            f"\\fontsize #0.6 {ly_str(en)} \\hspace #0.8 "
            f"\\general-align #Y #-0.4 \\override #'(font-name . \"{CJK_SANS}\") "
            f"\\fontsize #0 {ly_str(zh)} }}")


def ly_global(score=True):
    att = [[] for _ in range(TOTAL + 1)]
    att[0].append(tempo_markup(*B.TEMPO_MARK))
    att[0].append(
        "\\mark \\markup \\concat { \\sans \\bold \\fontsize #0.6 "
        f"{ly_str(B.INTRO_TITLE[0])} \\hspace #0.8 "
        f"\\override #'(font-name . \"{CJK_SANS}\") {ly_str(B.INTRO_TITLE[1])} }}")
    for b, s, txt, bpm in B.TEMPO_TEXT:
        att[pos(b, s)].append(tempo_markup(txt, bpm))
    full = score is True
    for b, (letter, en, zh) in B.REHEARSAL.items():
        att[pos(b, 0)].append(mark_markup(letter, en, zh,
                                          3.2 if full else 2.6))
    if full:
        for b in range(2, B.NBARS + 1):
            if b in B.PAGE_BREAKS:
                att[pos(b, 0)].insert(0, "\\pageBreak")
            elif b in B.SYSTEM_BREAKS:
                att[pos(b, 0)].insert(0, "\\break")
            elif B.SYSTEM_BREAKS:
                att[pos(b, 0)].insert(0, "\\noBreak")
    else:
        for b in B.PART_BREAKS.get(score if isinstance(score, str) else "",
                                   ()):
            att[pos(b, 0)].insert(0, "\\break")
    out, run = [], 0
    for t in range(TOTAL):
        cmds = list(att[t])
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
            out.append("|\n    ")
    out.append('\\bar "|."')
    return " ".join(out)


# ---------------------------------------------------------------------------
# Paper, header, footer
# ---------------------------------------------------------------------------
PAGE_CMDS = """
#(define-markup-command (from-page layout props n arg) (number? markup?)
   (if (>= (chain-assoc-get 'page:page-number props 0) n)
       (interpret-markup layout props arg)
       empty-stencil))
#(define-markup-command (on-page layout props n arg) (number? markup?)
   (if (= (chain-assoc-get 'page:page-number props 0) n)
       (interpret-markup layout props arg)
       empty-stencil))
"""


def footer_markup(total, what):
    who = (f"改编 · 制谱　{B.ARRANGER}")
    return f"""\\markup \\column {{
    \\override #'(thickness . 0.6) \\draw-hline
    \\vspace #0.25
    \\fill-line {{
      \\line {{ \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #8.5
        {ly_str(who)} \\hspace #1.5 \\abs-fontsize #8.5 \\italic
        {ly_str("Arranged & Music Preparation by " + B.ARRANGER)} }}
      \\line {{ \\abs-fontsize #8 \\sans {ly_str(what + "   ·   PAGE")}
        \\abs-fontsize #8 \\sans \\fromproperty #'page:page-number-string
        \\abs-fontsize #8 \\sans {ly_str("OF " + str(total))} }}
    }} }}"""


def header_markup(label):
    return f"""\\markup \\from-page #2 \\column {{
    \\fill-line {{
      \\line {{ \\override #'(font-name . "{CJK_SERIF} Bold")
        \\abs-fontsize #11 {ly_str(B.TITLE)} \\hspace #1.5
        \\general-align #Y #-0.3 \\sans \\abs-fontsize #8
        {ly_str(label)} }}
      \\sans \\bold \\abs-fontsize #20 \\fromproperty #'page:page-number-string
    }}
    \\vspace #0.2
    \\override #'(thickness . 0.6) \\draw-hline
  }}"""


def paper_score(total):
    return f"""
{PAGE_CMDS}
\\paper {{
  #(set-paper-size "tabloid")
  property-defaults.fonts.serif = "{LATIN_SERIF}, {CJK_SERIF}"
  property-defaults.fonts.sans = "{LATIN_SANS}, {CJK_SANS}"
  top-margin = 12\\mm
  bottom-margin = 10\\mm
  left-margin = 16\\mm
  right-margin = 14\\mm
  indent = 27\\mm
  short-indent = 14\\mm
  first-page-number = 1
  print-first-page-number = ##t
  bookTitleMarkup = ##f
  scoreTitleMarkup = ##f
  ragged-last = ##f
  ragged-bottom = ##f
  ragged-last-bottom = ##f
  top-markup-spacing = #'((basic-distance . 2) (padding . 1))
  markup-system-spacing = #'((basic-distance . 14) (minimum-distance . 10)
                             (padding . 4) (stretchability . 6))
  system-system-spacing = #'((basic-distance . 22) (minimum-distance . 14)
                             (padding . 7) (stretchability . 60))
  top-system-spacing = #'((basic-distance . 14) (minimum-distance . 10)
                          (padding . 4) (stretchability . 4))
  last-bottom-spacing = #'((basic-distance . 8) (minimum-distance . 5)
                           (padding . 3) (stretchability . 30))
  oddHeaderMarkup = {header_markup("FULL SCORE IN C")}
  evenHeaderMarkup = \\oddHeaderMarkup
  oddFooterMarkup = {footer_markup(total, "FULL SCORE IN C")}
  evenFooterMarkup = \\oddFooterMarkup
}}
"""


def title_block():
    return f"""\\markup {{
  \\override #'(baseline-skip . 3.2)
  \\column {{
    \\fill-line {{
      \\sans \\bold \\abs-fontsize #12 "SCORE IN C"
      \\override #'(font-name . "{CJK_SERIF} Bold") \\abs-fontsize #34
        {ly_str(B.TITLE)}
      \\sans \\abs-fontsize #10 "FULL SCORE"
    }}
    \\vspace #0.4
    \\fill-line {{ \\abs-fontsize #12 \\italic {ly_str(B.TITLE_LATIN + " · " + B.TITLE_EN)} }}
    \\vspace #0.2
    \\fill-line {{ \\line {{ \\override #'(font-name . "{CJK_SERIF}")
      \\abs-fontsize #13 {ly_str(B.SUBTITLE)} \\hspace #1
      \\abs-fontsize #12.5 \\italic {ly_str(B.SUBTITLE_EN)} }} }}
    \\vspace #1.2
    \\fill-line {{
      \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #10
        \\left-column {{ {ly_str("时长 Duration: " + B.duration_text())}
                         {ly_str("钢琴原谱：" + B.SOURCE_CHART)} }}
      \\null
      \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #10
        \\right-column {{ {ly_str("作曲：" + B.COMPOSER)}
                          {ly_str("改编：" + B.ARRANGER)}
                          {ly_str("制谱：" + B.ENGRAVER)} }}
    }}
  }}
}}
"""


LAYOUT = """
\\layout {
  \\context {
    \\Score
    \\remove Bar_number_engraver
    \\remove Metronome_mark_engraver
    \\remove Mark_engraver
    \\remove Staff_collecting_engraver
    \\override SpacingSpanner.base-shortest-duration = #(ly:make-moment 1/32)
    \\override RehearsalMark.self-alignment-X = #LEFT
    \\override RehearsalMark.padding = #2.2
    \\override MetronomeMark.padding = #1.6
    \\override RehearsalMark.outside-staff-priority = #1500
    \\override MetronomeMark.outside-staff-priority = #1400
    \\override TextScript.outside-staff-priority = #450
    \\override Hairpin.minimum-length = #4
    \\override Hairpin.to-barline = ##t
    \\override DynamicTextSpanner.style = #'none
    \\override StaffGrouper.staffgroup-staff-spacing =
      #'((basic-distance . 12) (minimum-distance . 9) (padding . 2))
    \\override StaffGrouper.staff-staff-spacing =
      #'((basic-distance . 12) (minimum-distance . 9) (padding . 2))
  }
  \\context {
    \\Staff
    ottavationMarkups = #ottavation-ordinals
    \\override OttavaBracket.font-shape = #'italic
    \\override InstrumentName.self-alignment-X = #RIGHT
    \\override InstrumentName.padding = #1.2
    \\override InstrumentName.font-size = #1
  }
}
"""


def staff(p, parsed, top):
    pid = p["id"]
    extra = []
    if top:
        extra += ["\\consists Mark_engraver",
                  "\\consists Staff_collecting_engraver",
                  "\\consists Metronome_mark_engraver"]
    notes = ly_notes(p, parsed[pid])
    glob = ly_global(score=True) if top else \
        ("s1*%d \\bar \"|.\"" % B.NBARS)
    return f"""
    \\new Staff = "{pid}" \\with {{
      instrumentName = {ly_str(p['name'])}
      shortInstrumentName = {ly_str(p['abbr'])}
      {" ".join(extra)}
    }} <<
      \\new Voice = "{pid}" {{
        \\clef {p['clef']} \\key f \\major \\numericTimeSignature \\time 4/4
        {notes}
      }}
      \\new Voice {{
        {ly_dynamics(p)}
      }}
      \\new Voice {{
        {glob}
      }}
    >>"""


BAR_COUNTER = """
    \\new Dynamics \\with {
      \\consists Measure_counter_engraver
      \\override MeasureCounter.font-encoding = #'latin1
      \\override MeasureCounter.font-series = #'bold
      \\override MeasureCounter.font-size = #0.2
      \\override MeasureCounter.outside-staff-priority = ##f
      \\override MeasureCounter.Y-offset = #0
      \\override MeasureCounter.stencil =
        #(make-stencil-boxer 0.12 0.45 ly:text-interface::print)
      \\override VerticalAxisGroup.nonstaff-relatedstaff-spacing =
        #'((basic-distance . 8) (minimum-distance . 6) (padding . 2.5))
    } { \\startMeasureCount s1*%d \\stopMeasureCount }"""


def skip_line(first, last):
    """A voice that hides everything outside bars first..last."""
    out = []
    for b in range(1, B.NBARS + 1):
        cmd = ""
        if b == 1 and first > 1:
            cmd = "\\set Score.skipTypesetting = ##t "
        if b == first and first > 1:
            cmd = "\\set Score.skipTypesetting = ##f "
        if b == last + 1:
            cmd = "\\set Score.skipTypesetting = ##t "
        out.append(cmd + "s1")
    return " ".join(out)


def score_source(total, bars=None):
    parsed = B.parse_all()
    staves = "".join(staff(p, parsed, i == 0) for i, p in enumerate(B.PARTS))
    skip = "" if bars is None else \
        "    \\new Devnull { " + skip_line(*bars) + " }"
    return f"""\\version "2.24.0"
#(set-global-staff-size {SCORE_STAFF_SIZE})
{paper_score(total)}
\\header {{ tagline = ##f }}
\\book {{
{title_block()}
\\score {{
  <<
    \\new StaffGroup \\with {{ systemStartDelimiter = #'SystemStartBracket }}
    <<{staves}
    >>
{BAR_COUNTER % B.NBARS}
{skip}
  >>
{LAYOUT}
}}
}}
"""


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------
def paper_part(p, total):
    return f"""
{PAGE_CMDS}
\\paper {{
  paper-width = 9\\in
  paper-height = 12\\in
  property-defaults.fonts.serif = "{LATIN_SERIF}, {CJK_SERIF}"
  property-defaults.fonts.sans = "{LATIN_SANS}, {CJK_SANS}"
  top-margin = 10\\mm
  bottom-margin = 9\\mm
  left-margin = 14\\mm
  right-margin = 12\\mm
  indent = 0\\mm
  first-page-number = 1
  bookTitleMarkup = ##f
  scoreTitleMarkup = ##f
  ragged-last = ##f
  ragged-bottom = ##t
  ragged-last-bottom = ##t
  markup-system-spacing = #'((basic-distance . 12) (padding . 4))
  system-system-spacing = #'((basic-distance . 15) (minimum-distance . 11)
                             (padding . 3.5) (stretchability . 12))
  oddHeaderMarkup = {header_markup(p['name'].upper())}
  evenHeaderMarkup = \\oddHeaderMarkup
  oddFooterMarkup = {footer_markup(total, p['name'].upper())}
  evenFooterMarkup = \\oddFooterMarkup
}}
"""


def part_title(p):
    return f"""\\markup {{
  \\override #'(baseline-skip . 3)
  \\column {{
    \\fill-line {{
      \\override #'(box-padding . 0.8) \\box \\sans \\bold \\abs-fontsize #13
        {ly_str(p['name'].upper())}
      \\override #'(font-name . "{CJK_SERIF} Bold") \\abs-fontsize #26
        {ly_str(B.TITLE)}
      \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #11 {ly_str(p['zh'])}
    }}
    \\vspace #0.2
    \\fill-line {{ \\line {{ \\override #'(font-name . "{CJK_SERIF}")
      \\abs-fontsize #11 {ly_str(B.SUBTITLE)} \\hspace #1
      \\abs-fontsize #10.5 \\italic {ly_str(B.SUBTITLE_EN)} }} }}
    \\vspace #0.8
    \\fill-line {{
      \\null
      \\null
      \\override #'(font-name . "{CJK_SERIF}") \\abs-fontsize #9
        \\right-column {{ {ly_str("作曲：" + B.COMPOSER)}
                          {ly_str("改编 · 制谱：" + B.ARRANGER)} }}
    }}
  }}
}}
"""


def part_source(p, total):
    parsed = B.parse_all()
    notes = ly_notes(p, parsed[p["id"]], part_mode=True)
    return f"""\\version "2.24.0"
#(set-global-staff-size {PART_STAFF_SIZE})
{paper_part(p, total)}
\\header {{ tagline = ##f }}
\\book {{
{part_title(p)}
\\score {{
  \\new Staff \\with {{
    \\consists Mark_engraver
    \\consists Metronome_mark_engraver
  }} <<
    \\new Voice {{
      \\compressMMRests {{
        \\clef {p['clef']} \\key f \\major \\numericTimeSignature \\time 4/4
        {notes}
      }}
    }}
    \\new Voice {{
      {ly_dynamics(p)}
    }}
    \\new Voice {{
      {ly_global(score=p['id'])}
    }}
  >>
  \\layout {{
    \\context {{
      \\Score
      \\remove Metronome_mark_engraver
      \\remove Mark_engraver
      \\override RehearsalMark.self-alignment-X = #LEFT
      \\override RehearsalMark.padding = #2
      \\override BarNumber.font-size = #0.5
      \\override MultiMeasureRest.expand-limit = #1
      \\override Hairpin.to-barline = ##t
    }}
  }}
}}
}}
"""


# ---------------------------------------------------------------------------
# Cover (HTML printed by Chromium)
# ---------------------------------------------------------------------------
CSS = """
@page { size: 11in 17in; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'EB Garamond', 'Noto Serif CJK SC', serif; color: #111;
       font-variant-numeric: lining-nums; }
.cjk { font-family: 'Noto Serif CJK SC', serif; }
.sym { font-family: 'DejaVu Sans', sans-serif; font-size: .95em; }
.page { width: 11in; height: 17in; position: relative; overflow: hidden;
        background: #fff; }
.frame { position: absolute; inset: .55in; border: 1.6pt solid #111; }
.frame::after { content: ''; position: absolute; inset: 5pt;
                border: .5pt solid #111; }
.cv { position: absolute; left: 0; right: 0; text-align: center; }
.kicker { top: 2.05in; font-size: 15pt; letter-spacing: .5em;
          text-transform: uppercase; padding-left: .5em; }
.kicker2 { top: 2.5in; font-size: 11pt; letter-spacing: .3em;
           text-transform: uppercase; color: #444; padding-left: .3em; }
.title { top: 4.0in; font-family: 'Noto Serif CJK SC', serif;
         font-weight: 700; font-size: 104pt; letter-spacing: .16em;
         padding-left: .16em; line-height: 1.1; }
.latin { top: 6.15in; font-size: 17pt; letter-spacing: .45em;
         text-transform: uppercase; color: #333; padding-left: .45em; }
.en { top: 6.6in; font-size: 15pt; font-style: italic; color: #333; }
.orn { top: 7.25in; }
.orn span { display: inline-block; width: 1.6in; height: 0;
            border-top: .6pt solid #111; vertical-align: middle; }
.orn b { display: inline-block; width: 7pt; height: 7pt; margin: 0 12pt;
         transform: rotate(45deg); border: .8pt solid #111;
         vertical-align: middle; }
.sub { top: 7.75in; font-family: 'Noto Serif CJK SC', serif; font-size: 24pt;
       letter-spacing: .3em; padding-left: .3em; }
.suben { top: 8.4in; font-size: 18pt; font-style: italic; color: #222; }
.credits { position: absolute; top: 9.8in; left: 2.35in;
           border-collapse: collapse; width: 6.3in; }
.credits td { padding: 8pt 0; vertical-align: middle;
              border-bottom: .4pt solid #bbb; }
.credits tr:last-child td { border-bottom: none; }
.credits .zh { font-family: 'Noto Serif CJK SC', serif; font-size: 13pt;
               width: 1.05in; letter-spacing: .15em; }
.credits .en { font-size: 10pt; letter-spacing: .2em; text-transform: uppercase;
               color: #555; width: 2.3in; }
.credits .nm { font-family: 'Noto Serif CJK SC', serif; font-size: 15pt;
               text-align: right; font-weight: 600; }
.info { top: 13.2in; font-size: 12.5pt; letter-spacing: .06em; color: #222; }
.inst { top: 13.7in; font-size: 11pt; letter-spacing: .1em; color: #444; }
.inst .cjk { font-size: 10pt; letter-spacing: .05em; color: #666; }
.sig { top: 15.1in; font-family: 'Noto Serif CJK SC', serif; font-size: 13pt;
       letter-spacing: .5em; padding-left: .5em; }
.sig2 { top: 15.5in; font-size: 9.5pt; letter-spacing: .35em;
        text-transform: uppercase; color: #555; padding-left: .35em; }
"""


def _e(s):
    return html.escape(str(s))


def _sym(s):
    return "".join(f"<span class='sym'>{c}</span>" if c in "♩♪♭♯♮" else c
                   for c in _e(s))


def cover_html():
    rows = [("作曲", "Music", B.COMPOSER),
            ("钢琴原谱", "Piano Score", B.SOURCE_CHART),
            ("改编", "Arranged by", B.ARRANGER),
            ("制谱", "Music Preparation", B.ENGRAVER)]
    trs = "".join(
        f"<tr><td class='zh'>{_e(a)}</td><td class='en'>{_e(b)}</td>"
        f"<td class='nm'>{_e(c)}</td></tr>" for a, b, c in rows if c)
    info = "　·　".join(_sym(x) for x in (
        B.KEY_TEXT, f"♩ = {B.TEMPO_MARK[1]}", B.duration_text()))
    inst = "　·　".join(f"{_e(p['name'])} <span class='cjk'>{_e(p['zh'])}"
                       "</span>" for p in B.PARTS)
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<style>{CSS}</style></head><body><div class='page'>
  <div class='frame'></div>
  <div class='cv kicker'>Full Score</div>
  <div class='cv kicker2'>Score in C · Concert Pitch</div>
  <div class='cv title'>{_e(B.TITLE)}</div>
  <div class='cv latin'>{_e(B.TITLE_LATIN)}</div>
  <div class='cv en'>{_e(B.TITLE_EN)}</div>
  <div class='cv orn'><span></span><b></b><span></span></div>
  <div class='cv sub'>{_e(B.SUBTITLE)}</div>
  <div class='cv suben'>{_e(B.SUBTITLE_EN)}</div>
  <table class='credits'>{trs}</table>
  <div class='cv info'>{info}</div>
  <div class='cv inst'>{inst}</div>
  <div class='cv sig'>{_e(B.ARRANGER)}</div>
  <div class='cv sig2'>Arrangement &amp; Music Preparation · {_e(B.YEAR)}</div>
</div></body></html>"""


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


def render_cover(pdf_path, tmp):
    hp = os.path.join(tmp, "cover.html")
    with open(hp, "w", encoding="utf-8") as fh:
        fh.write(cover_html())
    subprocess.run([find_chrome(), "--headless", "--no-sandbox",
                    "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=4000",
                    f"--print-to-pdf={pdf_path}", "file://" + hp],
                   check=True, capture_output=True, timeout=300)


# ---------------------------------------------------------------------------
def lilypond(src, tmp, name):
    ly = os.path.join(tmp, name + ".ly")
    with open(ly, "w", encoding="utf-8") as fh:
        fh.write(src)
    r = subprocess.run(["lilypond", "-dno-point-and-click", "-o",
                        os.path.join(tmp, name), ly],
                       capture_output=True, text=True)
    warn = [x for x in r.stderr.splitlines()
            if "warning" in x.lower() or "error" in x.lower()]
    if r.returncode != 0:
        print(r.stderr[-4000:])
        raise SystemExit(f"lilypond failed on {name}")
    return os.path.join(tmp, name + ".pdf"), warn


def pages(pdf):
    from pypdf import PdfReader
    return len(PdfReader(pdf).pages)


def two_pass(make_src, tmp, name):
    pdf, _ = lilypond(make_src("?"), tmp, name)
    n = pages(pdf)
    pdf, warn = lilypond(make_src(n), tmp, name)
    assert pages(pdf) == n
    return pdf, warn


def preview(first, last, png):
    """Quick look at bars first..last of the full score (no cover, no
    parts), for checking a section while writing it."""
    with tempfile.TemporaryDirectory() as tmp:
        src = score_source("?", (first, last))
        src = src.replace(title_block(), "")
        ly = os.path.join(tmp, "prev.ly")
        with open(ly, "w", encoding="utf-8") as fh:
            fh.write(src)
        r = subprocess.run(["lilypond", "-dno-point-and-click", "--png",
                            "-dresolution=80", "-o",
                            os.path.join(tmp, "prev"), ly],
                           capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-3000:])
            raise SystemExit("lilypond failed")
        pngs = sorted(glob.glob(os.path.join(tmp, "prev*.png")))
        from PIL import Image
        ims = [Image.open(p).convert("RGB") for p in pngs]
        W = max(i.width for i in ims)
        out = Image.new("RGB", (W, sum(i.height for i in ims)), "white")
        y = 0
        for i in ims:
            out.paste(i, (0, y))
            y += i.height
        out.save(png)
        for x in r.stderr.splitlines():
            if "warning" in x.lower():
                print(x)
    print("written", png)


def main(png=False, png_dir=None):
    from pypdf import PdfReader, PdfWriter
    if png_dir is None and "--png" in sys.argv:
        png_dir = sys.argv[sys.argv.index("--png") + 1]
    os.makedirs(B.OUT, exist_ok=True)
    score_pdf = os.path.join(B.OUT, f"{B.NAME}_弦乐五重奏_总谱.pdf")
    parts_dir = os.path.join(B.OUT, "分谱")
    os.makedirs(parts_dir, exist_ok=True)
    all_warn = []
    with tempfile.TemporaryDirectory() as tmp:
        music, warn = two_pass(score_source, tmp, "score")
        all_warn += [("score", w) for w in warn]
        cover = os.path.join(tmp, "cover.pdf")
        render_cover(cover, tmp)
        w = PdfWriter()
        w.add_page(PdfReader(cover).pages[0])
        for pg in PdfReader(music).pages:
            w.add_page(pg)
        w.add_metadata({
            "/Title": f"{B.TITLE} — {B.SUBTITLE} (Full Score)",
            "/Author": f"{B.COMPOSER} 曲 · 改编 {B.ARRANGER} · "
                       f"制谱 {B.ENGRAVER}",
            "/Subject": f"{B.TITLE_EN} — {B.SUBTITLE_EN}",
            "/Creator": "LilyPond 2.24 + juebieshu/engrave.py"})
        with open(score_pdf, "wb") as fh:
            w.write(fh)
        allp = PdfWriter()
        for i, p in enumerate(B.PARTS):
            pdf, warn = two_pass(lambda n, p=p: part_source(p, n), tmp,
                                 "part_" + p["id"])
            all_warn += [(p["id"], x) for x in warn]
            out = os.path.join(
                parts_dir, f"{B.NAME}_分谱_{i + 1}_{p['name']}_{p['zh']}.pdf")
            shutil.copy(pdf, out)
            for pg in PdfReader(pdf).pages:
                allp.add_page(pg)
        allp.add_metadata({"/Title": f"{B.TITLE} — {B.SUBTITLE} (Parts)",
                           "/Author": f"改编 · 制谱 {B.ARRANGER}"})
        with open(os.path.join(B.OUT, f"{B.NAME}_弦乐五重奏_全部分谱.pdf"),
                  "wb") as fh:
            allp.write(fh)
    for who, x in all_warn:
        print(f"LILYPOND {who}: {x}")
    if png_dir:
        os.makedirs(png_dir, exist_ok=True)
        for f in glob.glob(os.path.join(png_dir, "*.png")):
            os.remove(f)
        subprocess.run(["pdftoppm", "-r", "70", "-png", score_pdf,
                        os.path.join(png_dir, "score")], check=True)
        for f in sorted(glob.glob(os.path.join(parts_dir, "*.pdf"))):
            tag = os.path.basename(f).split("_")[2]
            subprocess.run(["pdftoppm", "-r", "70", "-png", f,
                            os.path.join(png_dir, "part" + tag)], check=True)
    print("written", score_pdf, "and parts in", parts_dir)


if __name__ == "__main__":
    if "--preview" in sys.argv:
        a, b = sys.argv[sys.argv.index("--bars") + 1].split("-")
        preview(int(a), int(b), sys.argv[sys.argv.index("--preview") + 1])
    else:
        main()
