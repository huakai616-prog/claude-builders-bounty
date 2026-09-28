#!/usr/bin/env python3
"""情歌（最后一遍副歌）— 人声 + 弦乐四重奏 编配生成器

Generates, from one source of truth:
  * MusicXML full score (for Sibelius / MuseScore / ACE Studio)
  * Full multitrack MIDI (for ACE Studio: Vocal Synth + String Section)
  * Vocal-only MIDI with lyrics (UTF-8 and GBK), and a plain vocal MIDI
  * Strings-only MIDI and lyric subtitles (SRT)

Key: F major (1=F, the chart's 女调; original F#), 4/4, quarter = 70.
Form: Intro (m1-4, the song's own string hook; pickup "你写" on m4 b4) |
      A, chorus first half (m5-8, strings stop on m8 b4, voice alone) |
      B, chorus second half, tutti (m9-12, "天长地" broadens) |
      Coda (m13-15, "久", then the hook again, Bbmaj7 - Bbm6 - Fadd9)

Token syntax (durations in 16th notes, one string per bar):
  C5/2        note C5, an eighth
  D4+F4/8     double stop
  r/4         rest
  A4/1~       tie into the next note
  F5/1>       accent
  (G4/1 A4/1) slur start / slur end
  G4/1=怎     lyric
  g:G4        grace note before the next note
  C5/2=br     audible breath (ACE Studio "br" note): x notehead, lyric br

Strings and breaths follow the user's corrected MIDI (2026-09-28): no
16th-note bass pushes, no dotted syncopations in Violin I; the voice keeps
the chart's rhythm, with the three "br" breaths the user added.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

import mido
from music21 import (articulations, bar, clef, dynamics, expressions,
                     instrument, key, layout, metadata, meter, note, chord,
                     spanner, stream, tempo, tie)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
NAME = "情歌"
NBARS = 15
BAR16 = 16
TPQ = 480
T16 = TPQ // 4

# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------
_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi_of(p):
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", p)
    if not m:
        raise ValueError(p)
    s, acc, octv = m.groups()
    v = _STEP[s] + (1 if acc == "#" else -1 if acc == "b" else 0)
    return 12 * (int(octv) + 1) + v


def m21_name(p):
    return p.replace("b", "-") if len(p) > 1 and p[1] == "b" else p


def rep(p, n, d=1, acc=()):
    """n repeated notes of pitch p, each d sixteenths; accents at indexes."""
    return " ".join(f"{p}/{d}" + (">" if i in acc else "") for i in range(n))


DRIVE = (0, 3, 6)  # 3+3+2 accents inside a half bar of 16ths

# ---------------------------------------------------------------------------
# Harmony (half bars; chart chords in brackets where they differ)
#   Intro  Bbmaj7  Am7 | Gm7  Bbmaj7/C | Bbmaj7  Am7 | Gm7  C7sus4 C7
#   A      F  C/E | Dm7  Am/C [3m] |
#          Bbmaj7  F/A | Gm7  Bb/C (hit) - (beat 4: strings tacet)
#   B      F  C/E | Dm7  Am/C | Bbmaj7  F/A | Gm7  Bb/C -> C7 (allarg.)
#   Coda   F | Bbmaj7  Bbm6 | Fadd9
# The bass walks down F E D C Bb A G C in both halves of the chorus.
# ---------------------------------------------------------------------------
REST = "r/16"
BREATH = "br"  # lyric of an audible-breath note

# Credits. Standing rule from the user: 改编 and 制谱 are always 花开当富贵.
TITLE = "情歌"
SUBTITLE = "最后一遍副歌 · 人声与弦乐四重奏"
SUBTITLE_EN = "Final Chorus · for Voice and String Quartet"
LYRICIST = "陈没"
COMPOSER = "伍冠谚"
SINGER = "梁静茹"
ARRANGER = "花开当富贵"
ENGRAVER = "花开当富贵"

VOCAL = {b: REST for b in range(1, NBARS + 1)}
VOCAL.update({
    4: "r/12 A4/2=你 (G4/1=写 F4/1)",
    5: "F4/4=给 C5/4=我 Bb4/2=我 A4/1=的 G4/1~=第 G4/1 F4/3=一",
    6: "F4/4=首 C5/2=歌 C5/2=br Bb4/2=你 A4/1=和 G4/1~=我 G4/2 A4/2=十",
    7: "G4/2=指 F4/1=紧 F4/1~=扣 F4/2 A4/2=默 G4/2=写 F4/1=前 F4/1~=奏 "
       "F4/1 F4/2=br C4/1=可",
    8: "D4/2=是 F4/1=那 F4/1~=然 F4/1 (A4/2=后 G4/1) G4/4=呢 A4/2=还 "
       "(G4/1=好 F4/1)",
    9: "F4/4=我 C5/4=有 Bb4/2=我 A4/1=这 G4/1~=一 G4/1 F4/3=首",
    10: "F4/4=情 C5/4=歌 Bb4/2=轻 A4/1=轻 G4/1~=的 G4/2 A4/2=轻",
    11: "G4/2=轻 F4/1=哼 F4/1~=着 F4/1 F4/1=br A4/2=哭 G4/2=着 F4/1=笑 "
        "F4/1~=着 "
        "F4/2 (A4/2=我",
    12: "G4/2) G4/2~=的 G4/4 r/2 A4/2=天 G4/3=长 F4/1=地",
    13: "F4/8=久 r/8",
})

# The hook is the song's own string intro: 3 2 6 3 | 2 5 4 3 | 1 7 1 2 3
HOOK_A = "A5/2 G5/2 D6/2 A5/2"
HOOK_B = "G5/2 C6/2 Bb5/2 A5/2"

VN1 = {
    1: f"({HOOK_A}) ({HOOK_B})",
    2: "(F5/2 E5/2 F5/2 G5/2 A5/8)",
    3: f"({HOOK_A}) ({HOOK_B})",
    4: "(F5/2 E5/2 F5/2 G5/2 A5/4 G5/4)",
    5: "(A5/4 C6/4 G5/8)",
    6: "(F5/4 A5/4 C6/8)",
    7: "(D6/8 C6/8)",
    8: "(Bb5/4 A5/4) D6/4> r/4",
    9: "(C6/4 F6/4) (G6/4 E6/4)",
    10: "(F6/4 D6/4) (E6/6 C6/2)",
    11: "(D6/4 E6/4) F6/8",
    12: "G6/8 F6/4 E6/4",
    13: f"F6/8 ({HOOK_A})",
    14: f"({HOOK_B}) (F5/2 Eb5/2 F5/2 G5/2)",
    15: "A5/16",
}

VN2 = {
    1: "F5/8 C5/8",
    2: "Bb4/8 D5/8",
    3: "(F5/2 D5/2 Bb5/2 D5/2) (E5/2 A5/2 G5/2 C5/2)",
    4: "(D5/2 C5/2 D5/2 E5/2 F5/4 E5/4)",
    5: "(C5/8 E5/8)",
    6: "(D5/8 E5/8)",
    7: "(F5/8 A5/8)",
    8: "D5/8 F5/4> r/4",
    9: rep("A5", 8, acc=DRIVE) + " " + rep("G5", 8, acc=DRIVE),
    10: rep("F5", 8, acc=DRIVE) + " " + rep("E5", 8, acc=DRIVE),
    11: rep("F5", 8, acc=DRIVE) + " " + rep("A5", 8, acc=DRIVE),
    12: rep("Bb5", 8, acc=DRIVE) + " D6/8",
    13: "C6/8 A4/8",
    14: "F4/8 G4/8~",
    15: "G4/16",
}

VA = {
    1: "D4/8 E4/8",
    2: "F4/8 Bb3+F4/8",
    3: "(Bb3/2 F4/2 D4/2 F4/2) (A3/2 E4/2 C4/2 E4/2)",
    4: "(G3/2 D4/2 Bb3/2 D4/2) (Bb3/2 F4/2) Bb3/4",
    5: "(F3/2 C4/2 A3/2 C4/2) (E3/2 C4/2 G3/2 C4/2)",
    6: "(D3/2 A3/2 F3/2 A3/2) (C3/2 E3/2 A3/2 E3/2)",
    7: "(D3/2 F3/2 A3/2 F3/2) (C3/2 F3/2 A3/2 C4/2)",
    8: "(D3/1 G3/1 D4/1 Bb3/1 G3/1 D4/1 Bb3/1 G3/1) Bb3+D4/4> r/4",
    9: "(F3/1 C4/1 F4/1 G4/1 F4/1 C4/1 A3/1 C4/1) "
       "(E3/1 G3/1 C4/1 E4/1 C4/1 A3/1 D4/1 F4/1)",
    10: "(D3/1 A3/1 D4/1 F4/1 C4/1 A3/1 F3/1 A3/1) "
        "(C3/1 E3/1 A3/1 C4/1 E4/1 C4/1 A3/1 E3/1)",
    11: "(D3/1 F3/1 Bb3/1 D4/1 F4/1 D4/1 Bb3/1 F3/1) "
        "(C3/1 F3/1 A3/1 C4/1 F4/1 C4/1 A3/1 F3/1)",
    12: "(D3/1 G3/1 Bb3/1 D4/1 F4/1 D4/1 Bb3/1 G3/1) Bb3+F4/8",
    13: "A3+F4/8~ A3+F4/8",
    14: "D4/8 Db4/8",
    15: "C4/16",
}

VC = {
    1: "Bb2/8 A2/8",
    2: "G2/8 C3/8",
    3: "Bb2/8 A2/8",
    4: "G2/8 C3/4 C2/4",
    # the chart's slow-soul bass figure "1 ~ 1 5 1"
    5: "F3/6 C3/1 F3/1 E3/8",
    6: "D3/6 A2/1 D3/1 C3/6 G2/1 C3/1",
    7: "Bb2/6 F2/1 Bb2/1 A2/6 F2/1 A2/1",
    8: "G2/6 D2/1 G2/1 C2+C3/4> r/4",
    9: "F2/2> F3/2 F2/2 F3/2 E2/2 E3/2 E2/2 E3/2",
    10: "D2/2 D3/2 D2/2 D3/2 C2/2 C3/2 C2/2 C3/2",
    11: "Bb2/2 Bb3/2 Bb2/2 Bb3/2 A2/2 A3/2 A2/2 C3/2",
    12: "G2/2 G3/2 G2/2 G3/2 C2+C3/8",
    13: "F2+C3/8~ F2+C3/8",
    14: "Bb2/8~ Bb2/8",
    15: "F2/16",
}

# Dynamics: (bar, 16th, mark). Hairpins: (bar, 16th, bar2, 16th2, kind).
# Text: (bar, 16th, text)
# Hairpins end on the next dynamic: bars 7-8 build to the f hit on m8
# beat 3; the coda thins from p (m13 b3) to pp on the last chord.
# At the climax the strings hit fp on m12 b3 and swell under the voice's
# "天长地" to mf on "久", so they carry the singer instead of covering her.
STRING_HAIRPINS = [(4, 0, 4, 15, "cresc"), (7, 0, 8, 7, "cresc"),
                   (11, 0, 11, 15, "cresc"), (12, 8, 12, 15, "cresc"),
                   (13, 0, 13, 7, "dim"), (14, 8, 14, 15, "dim")]
# Playing words that start with a dynamic are printed with it, below the
# staff ("mf cantabile"), so each instruction clearly belongs to its staff.
MOOD_WORDS = {"dolce, espr.", "cantabile", "legato, come onde",
              "con passione", "eco", "marcato", "marcato, on the string"}
PARTS = [
    dict(id="vox", name="Voice", abbr="V.", data=VOCAL,
         inst=instrument.Soprano, clef=clef.TrebleClef, program=52,
         dyn=[(4, 12, "mf"), (9, 0, "f"), (12, 0, "ff"), (12, 10, "mf")],
         hair=[(7, 0, 8, 15, "cresc"), (11, 0, 11, 15, "cresc"),
               (13, 0, 13, 7, "niente")],
         text=[(8, 12, "a cappella")]),
    dict(id="vn1", name="Violin I", abbr="Vln. I", data=VN1,
         inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(1, 0, "mp"), (5, 0, "mf"), (8, 8, "f"), (9, 0, "f"),
              (12, 0, "ff"), (12, 8, "fp"), (13, 0, "mf"), (13, 8, "p"),
              (15, 0, "pp")],
         hair=STRING_HAIRPINS,
         text=[(1, 0, "dolce, espr."), (5, 0, "cantabile"),
               (9, 0, "con passione"), (13, 8, "eco")]),
    dict(id="vn2", name="Violin II", abbr="Vln. II", data=VN2,
         inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(1, 0, "p"), (3, 0, "mp"), (5, 0, "mf"), (8, 8, "f"),
              (9, 0, "f"), (12, 0, "ff"), (12, 8, "fp"), (13, 0, "mf"),
              (13, 8, "p"), (15, 0, "pp")],
         hair=STRING_HAIRPINS,
         text=[(9, 0, "marcato, on the string")]),
    dict(id="va", name="Viola", abbr="Vla.", data=VA,
         inst=instrument.Viola, clef=clef.AltoClef, program=41,
         dyn=[(1, 0, "p"), (3, 0, "mp"), (5, 0, "mf"), (8, 8, "f"),
              (9, 0, "f"), (12, 0, "ff"), (12, 8, "fp"), (13, 0, "mf"),
              (13, 8, "p"), (15, 0, "pp")],
         hair=STRING_HAIRPINS,
         text=[(5, 0, "legato, come onde")]),
    dict(id="vc", name="Violoncello", abbr="Vc.", data=VC,
         inst=instrument.Violoncello, clef=clef.BassClef, program=42,
         dyn=[(1, 0, "p"), (3, 0, "mp"), (5, 0, "mf"), (8, 8, "f"),
              (9, 0, "f"), (12, 0, "ff"), (12, 8, "fp"), (13, 0, "mf"),
              (13, 8, "p"), (15, 0, "pp")],
         hair=STRING_HAIRPINS,
         text=[(5, 0, "marcato")]),
]

VEL = {"pp": 36, "p": 48, "mp": 62, "mf": 76, "f": 92, "ff": 106,
       "fp": 70}
ACCENT = 14

# Tempo map: (bar, 16th, bpm)
TEMPI = [(1, 0, 70), (12, 8, 66), (12, 12, 60), (13, 0, 58), (13, 8, 56),
         (14, 0, 54), (14, 8, 50), (15, 0, 44)]
TEMPO_MARK = "Slow soul"
# Rehearsal marks (score) and MIDI markers
REHEARSAL = {5: ("A", "副歌前半"), 9: ("B", "副歌后半 · 全奏"), 13: ("C", "尾奏")}
MIDI_MARKERS = {1: "Intro", 5: "A", 9: "B", 13: "Coda"}
TEMPO_TEXT = [(12, 8, "allarg."), (14, 0, "rit.")]
SYSTEM_BREAKS = (5, 8, 11, 13)

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(\()?((?:[A-G][#b]?\d)(?:\+[A-G][#b]?\d)*|r)/(\d+)(>)?(~)?(\))?"
    r"(?:=(.+))?$")


def parse_bar(s):
    evs, pos, pending_grace = [], 0, None
    for t in s.split():
        if t.startswith("g:"):
            pending_grace = t[2:]
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r} in {s!r}")
        sl, pit, dur, acc, ti, sr, lyr = m.groups()
        dur = int(dur)
        evs.append(dict(
            pos=pos, dur=dur,
            pitches=None if pit == "r" else pit.split("+"),
            tie=bool(ti), slur_start=bool(sl), slur_end=bool(sr),
            accent=bool(acc), lyric=lyr, grace=pending_grace))
        pending_grace = None
        pos += dur
    if pos != BAR16:
        raise ValueError(f"bar sums to {pos}: {s!r}")
    return evs


def parse_part(data):
    out = []
    for b in range(1, NBARS + 1):
        try:
            evs = parse_bar(data[b])
        except ValueError as e:
            raise ValueError(f"m{b}: {e}") from None
        for e in evs:
            e["bar"] = b
            e["abs"] = (b - 1) * BAR16 + e["pos"]
            out.append(e)
    return out


# ---------------------------------------------------------------------------
# Notation splitting (keep beats visible)
# ---------------------------------------------------------------------------
def split_dur(pos, dur):
    pieces = []
    while dur > 0:
        if pos % 4 == 0:
            allowed = {0: [16, 12, 8, 6, 4, 3, 2, 1],
                       8: [8, 6, 4, 3, 2, 1]}.get(pos, [4, 3, 2, 1])
        elif pos % 4 == 2:
            allowed = [4, 2, 1] if pos in (2, 10) else [2, 1]
        elif pos % 4 == 1:
            allowed = [3, 2, 1]
        else:
            allowed = [1]
        d = next(x for x in allowed if x <= dur)
        pieces.append(d)
        pos += d
        dur -= d
    return pieces


def split_rest(pos, dur):
    """Rests: no dotted values, beats 1 and 3 stay visible."""
    pieces = []
    while dur > 0:
        allowed = ([16, 8, 4, 2, 1] if pos == 0 else
                   [8, 4, 2, 1] if pos == 8 else
                   [4, 2, 1] if pos % 4 == 0 else
                   [2, 1] if pos % 2 == 0 else [1])
        d = next(x for x in allowed if x <= dur)
        pieces.append(d)
        pos += d
        dur -= d
    return pieces


QL = {1: 0.25, 2: 0.5, 3: 0.75, 4: 1.0, 6: 1.5, 8: 2.0, 12: 3.0, 16: 4.0}


def make_m21(p, events):
    part = stream.Part(id=p["id"])
    ins = p["inst"]()
    ins.partName = p["name"]
    ins.partAbbreviation = p["abbr"]
    part.insert(0, ins)
    notes_at = {}  # abs16 -> first m21 note/rest object starting there
    slur_open = None
    measures = {}
    by_bar = {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    tied_prev = False
    for b in range(1, NBARS + 1):
        m = stream.Measure(number=b)
        if b == 1:
            m.insert(0, p["clef"]())
            m.insert(0, key.Key("F"))
            m.insert(0, meter.TimeSignature("4/4"))
        for e in by_bar[b]:
            if e["grace"]:
                g = note.Note(m21_name(e["grace"]), type="16th")
                g = g.getGrace()
                g.duration.slash = True
                m.append(g)
            pieces = (split_rest if e["pitches"] is None else split_dur)(
                e["pos"], e["dur"])
            objs = []
            for i, d in enumerate(pieces):
                if e["pitches"] is None:
                    n = note.Rest(quarterLength=QL[d])
                else:
                    names = [m21_name(x) for x in e["pitches"]]
                    n = (note.Note(names[0], quarterLength=QL[d])
                         if len(names) == 1 else
                         chord.Chord(names, quarterLength=QL[d]))
                    first = i == 0
                    last = i == len(pieces) - 1
                    starts = (not first) or tied_prev
                    cont = (not last) or e["tie"]
                    if starts and cont:
                        n.tie = tie.Tie("continue")
                    elif starts:
                        n.tie = tie.Tie("stop")
                    elif cont:
                        n.tie = tie.Tie("start")
                    if first and e["lyric"]:
                        n.lyric = e["lyric"]
                    if e["lyric"] == BREATH:
                        n.notehead = "x"
                    if first and e["accent"]:
                        n.articulations.append(articulations.Accent())
                m.append(n)
                objs.append(n)
            notes_at.setdefault(e["abs"], objs[0])
            e["m21"] = objs
            tied_prev = e["tie"] and e["pitches"] is not None
            if e["slur_start"]:
                slur_open = objs[0]
            if e["slur_end"] and slur_open is not None:
                part.insert(0, spanner.Slur(slur_open, objs[-1]))
                slur_open = None
        if b == NBARS:
            for n in m.notesAndRests:
                f = expressions.Fermata()
                f.type = "upright"
                n.expressions.append(f)
            m.rightBarline = bar.Barline("final")
        measures[b] = m
        part.append(m)

    def obj_at(bb, s, forward=True):
        a = (bb - 1) * BAR16 + s
        cands = sorted(notes_at)
        if forward:
            for k in cands:
                if k >= a:
                    return notes_at[k]
        else:
            for k in reversed(cands):
                if k <= a:
                    return notes_at[k]
        return None

    return part


def build_score(parsed):
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = TITLE
    md.movementName = TITLE
    md.composer = COMPOSER
    md.lyricist = LYRICIST
    md.add("arranger", ARRANGER)
    sc.insert(0, md)
    for p in PARTS:
        sc.insert(0, make_m21(p, parsed[p["id"]]))
    sc.insert(0, layout.StaffGroup(
        [x for x in sc.parts][1:], name="String Quartet", symbol="bracket"))
    return sc


# ---------------------------------------------------------------------------
# MusicXML polish for Sibelius
# ---------------------------------------------------------------------------
SOUNDS = {"Voice": ("Voice", "voice.vocals"),
          "Violin I": ("Violin", "strings.violin"),
          "Violin II": ("Violin", "strings.violin"),
          "Viola": ("Viola", "strings.viola"),
          "Violoncello": ("Violoncello", "strings.cello")}


def polish(path):
    """Tidy the MusicXML for Sibelius: A4 page and 6 mm staves, system
    breaks at phrase starts, one <instrument-sound> per part so the staves
    map to the right instruments, no per-note instrument changes, voice
    dynamics above the staff (lyrics are below), words and rehearsal marks
    above."""
    tree = ET.parse(path)
    r = tree.getroot()
    d = r.find("defaults")
    if d is None:
        d = ET.Element("defaults")
        r.insert(list(r).index(r.find("part-list")), d)
    for t in ("scaling", "page-layout", "system-layout", "staff-layout"):
        for x in d.findall(t):
            d.remove(x)
    new = ET.fromstring(
        "<defaults><scaling><millimeters>6</millimeters><tenths>40</tenths>"
        "</scaling><page-layout><page-height>1980</page-height>"
        "<page-width>1400</page-width><page-margins type=\"both\">"
        "<left-margin>80</left-margin><right-margin>60</right-margin>"
        "<top-margin>70</top-margin><bottom-margin>70</bottom-margin>"
        "</page-margins></page-layout><system-layout><system-margins>"
        "<left-margin>60</left-margin><right-margin>0</right-margin>"
        "</system-margins><system-distance>110</system-distance>"
        "<top-system-distance>170</top-system-distance></system-layout>"
        "<staff-layout><staff-distance>75</staff-distance></staff-layout>"
        "</defaults>")
    for i, x in enumerate(new):
        d.insert(i, x)
    # identification: who engraved it (制谱)
    ident = r.find("identification")
    enc = ident.find("encoding")
    for x in enc.findall("encoder"):
        enc.remove(x)
    e = ET.Element("encoder")
    e.text = ENGRAVER
    enc.insert(1, e)  # after encoding-date
    # page-1 credits, so Sibelius shows title and the credits as page text
    for x in r.findall("credit"):
        r.remove(x)
    W, H, M = 1400, 1980, 70
    # one text block per position: some importers stack separate credits
    # that share a position on top of each other
    credits = [  # (types, runs [(text, size, bold)], x, y, justify)
        (("title", "subtitle"), [(TITLE, 26, True), ("\n" + SUBTITLE, 12,
                                                      False)],
         W / 2, H - M, "center"),
        (("lyricist",), [("Score in C", 10, True),
                         (f"\n\n作词：{LYRICIST}\n原唱：{SINGER}", 10,
                          False)], 80, H - M, "left"),
        (("composer", "arranger"),
         [(f"作曲：{COMPOSER}\n改编：{ARRANGER}\n制谱：{ENGRAVER}", 10,
           False)], W - 60, H - M - 110, "right"),
    ]
    at = list(r).index(r.find("part-list"))
    for i, (types, runs, x, y, just) in enumerate(credits):
        c = ET.Element("credit", page="1")
        for t in types:
            ET.SubElement(c, "credit-type").text = t
        for k, (text, size, bold) in enumerate(runs):
            w = ET.SubElement(c, "credit-words", {"font-size": str(size)})
            if k == 0:
                w.attrib = {"default-x": f"{x:g}", "default-y": f"{y:g}",
                            "font-size": str(size), "justify": just,
                            "valign": "top"}
            if bold:
                w.set("font-weight", "bold")
            w.text = text
        r.insert(at + i, c)
    for sp in r.iter("score-part"):
        pname = sp.findtext("part-name")
        iname, snd = SOUNDS[pname]
        si = sp.find("score-instrument")
        if si is not None:
            si.find("instrument-name").text = iname
            for x in si.findall("instrument-sound"):
                si.remove(x)
            el = ET.Element("instrument-sound")
            el.text = snd
            # schema order: instrument-name, instrument-abbreviation, sound
            ab = si.find("instrument-abbreviation")
            si.insert(list(si).index(ab) + 1 if ab is not None else 1, el)
    for n in r.iter("note"):
        for x in n.findall("instrument"):
            n.remove(x)
    names = {s.get("id"): s.findtext("part-name")
             for s in r.iter("score-part")}
    for part in r.findall("part"):
        vocal = names[part.get("id")] == "Voice"
        for m in part.findall("measure"):
            if m.get("number") == "1":
                # room for the credits; a bar number on every bar
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                for x in list(pr):
                    pr.remove(x)
                sl = ET.SubElement(pr, "system-layout")
                ET.SubElement(sl, "top-system-distance").text = "290"
                ET.SubElement(pr, "measure-numbering").text = "measure"
            if int(m.get("number")) in SYSTEM_BREAKS:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                pr.set("new-system", "yes")
            for el in m.findall("direction"):
                if el.find("direction-type/dynamics") is not None or \
                        el.find("direction-type/wedge") is not None:
                    el.set("placement", "above" if vocal else "below")
                elif el.find("direction-type/words") is not None or \
                        el.find("direction-type/rehearsal") is not None:
                    el.set("placement", "above")
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    # keep the DOCTYPE MusicXML readers expect
    xml = open(path, encoding="utf-8").read()
    if "<!DOCTYPE" not in xml:
        xml = xml.replace(
            "?>\n",
            "?>\n<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD "
            "MusicXML 4.0 Partwise//EN\" "
            "\"http://www.musicxml.org/dtds/partwise.dtd\">\n", 1)
        open(path, "w", encoding="utf-8").write(xml)


TOTAL16 = NBARS * BAR16
BEAMS = {"eighth": 1, "16th": 2, "32nd": 3}


def _timeline(m, div16):
    """[(start16, index, note)] for the time-advancing notes of a measure."""
    out, pos = [], 0.0
    for i, el in enumerate(list(m)):
        if el.tag == "note":
            if el.find("grace") is not None or el.find("chord") is not None:
                continue
            out.append((pos, i, el))
            pos += int(el.findtext("duration")) / div16
        elif el.tag == "backup":
            pos -= int(el.findtext("duration")) / div16
        elif el.tag == "forward":
            pos += int(el.findtext("duration")) / div16
    return out


def _insert_at(m, s16, el, div16):
    """Put el at 16th s16 of measure m, right before the note (or rest)
    that starts there. Directions are only ever placed on onsets: a
    position inside a sustained note would need <backup>/<forward> or
    <offset>, which importers (Sibelius, MuseScore) turn into hidden rests
    or drop. Split the note in the data (tied notes) instead."""
    tl = _timeline(m, div16)
    if s16 >= BAR16 or not tl:
        m.append(el)
        return
    for start, idx, _ in tl:
        if abs(start - s16) < 1e-6:
            m.insert(idx, el)
            return
    raise ValueError(
        f"m{m.get('number')}: no note starts at 16th {s16}; split the "
        "sustained note (tie) so the dynamic/hairpin has an onset")


def melisma_marks(events):
    """For each sung syllable (br excluded): True if its melisma lasts at
    least 3 sixteenths, i.e. long enough for an extender line."""
    out = []
    for i, e in enumerate(events):
        if not e["lyric"] or e["lyric"] == BREATH:
            continue
        if not e["slur_start"]:
            out.append(False)
            continue
        total = 0
        for f in events[i:]:
            total += f["dur"]
            if f["slur_end"]:
                break
        out.append(total >= 3)
    return out


def _fix_beams(m, div16):
    """Beam by beat; two eighth pairs in the same half bar share a beam
    (same as LilyPond's 4/4 default), so Sibelius shows what the PDF shows.
    """
    notes = []
    for start, _, el in _timeline(m, div16):
        for b in el.findall("beam"):
            el.remove(b)
        dur = int(el.findtext("duration")) / div16
        nb = 0 if el.find("rest") is not None else \
            BEAMS.get(el.findtext("type"), 0)
        notes.append((start, dur, el, nb))
    for el in m.findall("note"):
        if el.find("chord") is not None:
            for b in el.findall("beam"):
                el.remove(b)
    runs, cur = [], []
    for n in notes:
        beat = int(n[0] // 4)
        if n[3] and cur and int(cur[-1][0] // 4) == beat:
            cur.append(n)
            continue
        if len(cur) > 1:
            runs.append(cur)
        cur = [n] if n[3] else []
    if len(cur) > 1:
        runs.append(cur)
    merged = []
    for r in runs:
        pair = lambda x: (len(x) == 2 and all(y[3] == 1 for y in x)
                          and x[0][0] % 4 == 0)
        if merged and pair(r) and pair(merged[-1]) and \
                int(r[0][0] // 4) == int(merged[-1][0][0] // 4) + 1 and \
                int(r[0][0] // 8) == int(merged[-1][0][0] // 8):
            merged[-1] = merged[-1] + r
        else:
            merged.append(r)
    for r in merged:
        for i, (_, _, el, nb) in enumerate(r):
            for st in el.findall("stem"):
                el.remove(st)
            beams = []
            for lvl in range(1, nb + 1):
                prev = i > 0 and r[i - 1][3] >= lvl
                nxt = i < len(r) - 1 and r[i + 1][3] >= lvl
                if lvl == 1:
                    v = "begin" if i == 0 else \
                        "end" if i == len(r) - 1 else "continue"
                elif prev and nxt:
                    v = "continue"
                elif prev:
                    v = "end"
                elif nxt:
                    v = "begin"
                else:
                    v = "backward hook" if i == len(r) - 1 else \
                        "forward hook"
                b = ET.Element("beam", number=str(lvl))
                b.text = v
                beams.append(b)
            at = len(el)
            for k, child in enumerate(el):
                if child.tag in ("notations", "lyric", "play", "listen"):
                    at = k
                    break
            for k, b in enumerate(beams):
                el.insert(at + k, b)


def _where(abs16):
    """(bar, 16th) of an absolute 16th; the piece end maps to bar end."""
    if abs16 >= TOTAL16:
        return NBARS, BAR16
    return abs16 // BAR16 + 1, abs16 % BAR16


def _direction(place, *types, sound=None, system=None):
    d = ET.Element("direction", placement=place)
    if system:
        d.set("system", system)
    for t in types:
        dt = ET.SubElement(d, "direction-type")
        dt.append(t)
    if sound is not None:
        ET.SubElement(d, "sound", sound)
    return d


def _words(text, **attrs):
    w = ET.Element("words", attrs)
    w.text = text
    return w


def _metronome(bpm, hidden=False):
    mt = ET.Element("metronome", {"print-object": "no"} if hidden else {})
    ET.SubElement(mt, "beat-unit").text = "quarter"
    ET.SubElement(mt, "per-minute").text = str(bpm)
    return mt


def finish_parts(path):
    """Everything music21 does not write the way Sibelius needs it: beams,
    stems, dynamics with their character words, hairpins, tempo marks and
    the tempo ramp, rehearsal marks and lyric extenders, all at exact
    positions."""
    tree = ET.parse(path)
    r = tree.getroot()
    div = int(next(r.iter("divisions")).text)
    div16 = div / 4
    for p, part in zip(PARTS, r.findall("part")):
        ms = {int(m.get("number")): m for m in part.findall("measure")}
        for m in ms.values():
            _fix_beams(m, div16)
        for n in part.iter("note"):
            if n.find("voice") is None:
                kids = [c.tag for c in n]
                at = max(i for i, t in enumerate(kids)
                         if t in ("duration", "tie", "instrument", "chord",
                                  "pitch", "rest", "unpitched", "grace",
                                  "cue")) + 1
                v = ET.Element("voice")
                v.text = "1"
                n.insert(at, v)
            t = n.find("lyric/text")
            if t is not None and t.text == BREATH:
                t.set("font-style", "italic")
        place = "above" if p["id"] == "vox" else "below"
        mood = {(b, s16): t for b, s16, t in p["text"] if t in MOOD_WORDS}
        for b, s16, mark in p["dyn"]:
            dy = ET.Element("dynamics")
            ET.SubElement(dy, mark)
            types = [dy]
            if (b, s16) in mood:
                types.append(_words(mood[b, s16], **{"font-style": "italic"}))
            _insert_at(ms[b], s16, _direction(
                place, *types,
                sound={"dynamics": str(round(VEL[mark] / 90 * 100))}),
                div16)
        for b, s16, t in p["text"]:
            if t not in MOOD_WORDS:
                _insert_at(ms[b], s16, _direction(
                    "above", _words(t, **{"font-style": "italic"})), div16)
        for b, s16, b2, s2, kind in p["hair"]:
            a = (b - 1) * BAR16 + s16
            z = (b2 - 1) * BAR16 + s2 + 1
            for pos, typ in ((a, "crescendo" if kind == "cresc"
                              else "diminuendo"), (z, "stop")):
                bb, ss = _where(pos)
                w = ET.Element("wedge", type=typ, number="1")
                if kind == "niente" and typ == "diminuendo":
                    w.set("niente", "yes")
                _insert_at(ms[bb], ss, _direction(place, w), div16)
        if p["id"] == "vox":
            # tempo heading, tempo words, hidden ramp, rehearsal marks
            _insert_at(ms[1], 0, _direction(
                "above", _words(TEMPO_MARK + " ", **{"font-weight": "bold"}),
                _metronome(TEMPI[0][2]), sound={"tempo": str(TEMPI[0][2])},
                system="only-top"), div16)
            # The visible tempo words carry the tempo they start; the finer
            # ramp (TEMPI) lives in the MIDI. Hidden metronome marks are
            # shown by some importers, so none are written.
            tempo_at = {(b, s16): bpm for b, s16, bpm in TEMPI}
            for b, s16, txt in TEMPO_TEXT:
                snd = ({"tempo": str(tempo_at[b, s16])}
                       if (b, s16) in tempo_at else None)
                _insert_at(ms[b], s16, _direction(
                    "above", _words(txt, **{"font-weight": "bold"}),
                    sound=snd, system="only-top"), div16)
            for b, (letter, label) in REHEARSAL.items():
                rh = ET.Element("rehearsal", enclosure="square")
                rh.text = letter
                # label first so the mark ends up in front of it
                _insert_at(ms[b], 0, _direction(
                    "above", _words(label), system="only-top"), div16)
                _insert_at(ms[b], 0, _direction(
                    "above", rh, system="only-top"), div16)
            marks = iter(melisma_marks(parse_part(p["data"])))
            for n in part.iter("note"):
                ly = n.find("lyric")
                if ly is None or ly.findtext("text") == BREATH:
                    continue
                if next(marks) and ly.find("extend") is None:
                    ET.SubElement(ly, "extend")
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


def verify_bars(path):
    """Every bar of every part in the written file must hold exactly 4/4."""
    from music21 import converter
    for p in converter.parse(path).parts:
        ms = p.getElementsByClass("Measure")
        assert len(ms) == NBARS, (p.partName, len(ms))
        for m in ms:
            assert abs(m.duration.quarterLength - 4) < 1e-6, \
                (p.partName, m.number, m.duration.quarterLength)


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
def merged_notes(events):
    """Merge tied notes; returns list of dicts (start16, dur16, pitches,
    lyric, slurred-into, grace, accent)."""
    out = []
    cur = None
    in_slur = False
    for e in events:
        if e["pitches"] is None:
            cur = None
            in_slur = False
            continue
        if cur is not None and cur["tie"]:
            cur["dur"] += e["dur"]
            cur["tie"] = e["tie"]
            if e["slur_end"]:
                in_slur = False
            continue
        cur = dict(start=e["abs"], dur=e["dur"], pitches=e["pitches"],
                   lyric=e["lyric"], tie=e["tie"], grace=e["grace"],
                   accent=e["accent"],
                   melisma=(e["lyric"] is None and in_slur))
        out.append(cur)
        if e["slur_start"]:
            in_slur = True
        if e["slur_end"]:
            in_slur = False
    return out


def dyn_curve(p):
    """velocity at each absolute 16th."""
    total = NBARS * BAR16
    pts = sorted(((b - 1) * BAR16 + s, VEL[m]) for b, s, m in p["dyn"])
    v = [pts[0][1]] * total
    for i, (a, val) in enumerate(pts):
        end = pts[i + 1][0] if i + 1 < len(pts) else total
        for t in range(a, end):
            v[t] = val
    for b, s, b2, s2, kind in p["hair"]:
        a = (b - 1) * BAR16 + s
        z = (b2 - 1) * BAR16 + s2
        v0 = v[a]
        nxt = [val for t, val in pts if t > z]
        v1 = nxt[0] if nxt else v0 + (-14 if kind == "dim" else 14)
        if kind == "niente":
            v1 = min(v1, v0 - 24)
        if kind == "cresc" and v1 <= v0:
            v1 = v0 + 12
        if kind == "dim" and v1 >= v0:
            v1 = v0 - 12
        for t in range(a, z + 1):
            v[t] = round(v0 + (v1 - v0) * (t - a) / max(1, z - a))
    return v


def tempo_track():
    ab = [(0, mido.MetaMessage("track_name", name=f"{NAME} 副歌")),
          (0, mido.MetaMessage("time_signature", numerator=4, denominator=4)),
          (0, mido.MetaMessage("key_signature", key="F"))]
    for b, s, bpm in TEMPI:
        t = ((b - 1) * BAR16 + s) * T16
        ab.append((t, mido.MetaMessage("set_tempo",
                                       tempo=mido.bpm2tempo(bpm))))
    for b, name in MIDI_MARKERS.items():
        ab.append(((b - 1) * BAR16 * T16,
                   mido.MetaMessage("marker", text=name.split()[0])))
    ab.sort(key=lambda x: x[0])
    tr, last = mido.MidiTrack(), 0
    for t, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


GRACE_T = T16 // 2  # a 32nd


def part_track(p, events, ch, lyrics=True, with_cc=True):
    notes = merged_notes(events)
    vel = dyn_curve(p)
    ab = []  # (tick, order, msg)
    ab.append((0, 0, mido.MetaMessage("track_name", name=p["name"] if
                                      p["id"] != "vox" else "Vocal 人声")))
    ab.append((0, 1, mido.Message("program_change", channel=ch,
                                  program=p["program"])))
    if with_cc:
        for t in range(0, NBARS * BAR16, 2):
            if t == 0 or vel[t] != vel[t - 2]:
                val = min(127, 20 + vel[t])
                ab.append((t * T16, 2, mido.Message(
                    "control_change", channel=ch, control=11, value=val)))
                ab.append((t * T16, 2, mido.Message(
                    "control_change", channel=ch, control=1, value=val)))
    for i, n in enumerate(notes):
        on = n["start"] * T16
        off = (n["start"] + n["dur"]) * T16
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        # re-articulate repeated pitches with a small gap; otherwise legato
        if nxt and nxt["start"] * T16 == off and \
                set(nxt["pitches"]) & set(n["pitches"]):
            off -= 12 if n["dur"] > 2 else 24
        v = vel[min(n["start"], len(vel) - 1)]
        if n["accent"]:
            v += ACCENT
        v = max(1, min(127, v))
        syl = n["lyric"] if n["lyric"] else ("-" if n["melisma"] else None)
        if n["grace"]:
            gp = midi_of(n["grace"])
            ab.append((on, 5, mido.Message("note_on", channel=ch, note=gp,
                                           velocity=v)))
            if lyrics and p["id"] == "vox":
                ab.append((on, 4, mido.MetaMessage(
                    "lyrics", text=syl if syl else "-")))
            ab.append((on + GRACE_T, 3, mido.Message(
                "note_off", channel=ch, note=gp, velocity=0)))
            on += GRACE_T
            syl = "-"
        if lyrics and p["id"] == "vox" and syl:
            ab.append((on, 4, mido.MetaMessage("lyrics", text=syl)))
        for pit in n["pitches"]:
            ab.append((on, 5, mido.Message("note_on", channel=ch,
                                           note=midi_of(pit), velocity=v)))
            ab.append((off, 3, mido.Message("note_off", channel=ch,
                                            note=midi_of(pit), velocity=0)))
    ab.sort(key=lambda x: (x[0], x[1]))
    tr, last = mido.MidiTrack(), 0
    for t, _, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def write_midi(path, part_ids, parsed, lyrics=True, charset="utf-8",
               with_cc=True):
    mf = mido.MidiFile(type=1, ticks_per_beat=TPQ, charset=charset)
    mf.tracks.append(tempo_track())
    for ch, p in enumerate(PARTS):
        if p["id"] in part_ids:
            mf.tracks.append(part_track(p, parsed[p["id"]], ch,
                                        lyrics=lyrics, with_cc=with_cc))
    mf.save(path)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
RANGES = {"vox": ("C4", "D5"), "vn1": ("G3", "G6"), "vn2": ("G3", "E6"),
          "va": ("C3", "Bb4"), "vc": ("C2", "Bb3")}

# Intentional minor-9ths. (bar, part, part)
#  m1, m3: the intro hook's own B-flat, an appoggiatura on beat 4 over the
#          Am7 root (as in the original record).
#  m5, m9: the user's MIDI keeps the bass on E (C/E) to the end of the bar,
#          under the voice's anticipated F ("一" / "首") and, in m9, the
#          viola's last-16th F4. Passing, kept as the user wrote it.
CLASH_ALLOW = {(1, "vn1", "vc"), (3, "vn1", "vc"), (5, "vox", "vc"),
               (9, "vox", "vc"), (9, "va", "vc")}


def sounding(parsed):
    """abs16 -> list of (part, midi, name, attacked-here)."""
    grid = {}
    for pid, evs in parsed.items():
        held = False
        for e in evs:
            if e["pitches"] is None:
                held = False
                continue
            for t in range(e["abs"], e["abs"] + e["dur"]):
                for pit in e["pitches"]:
                    grid.setdefault(t, []).append(
                        (pid, midi_of(pit), pit, t == e["abs"] and not held))
            held = e["tie"]
    return grid


def top_line(evs):
    """Monophonic (start16, midi) attack list per part (highest note)."""
    out, held = [], False
    for e in evs:
        if e["pitches"] is None:
            out.append((e["abs"], None))
            held = False
            continue
        if not held:
            out.append((e["abs"], max(midi_of(x) for x in e["pitches"])))
        held = e["tie"]
    return out


def check(parsed):
    problems = []
    for pid, evs in parsed.items():
        lo, hi = (midi_of(x) for x in RANGES[pid])
        for e in evs:
            for pit in e["pitches"] or []:
                if not lo <= midi_of(pit) <= hi:
                    problems.append(f"{pid} m{e['bar']} {pit} out of range")
    grid = sounding(parsed)
    clashes = []
    for t, snd in sorted(grid.items()):
        for i in range(len(snd)):
            for j in range(i + 1, len(snd)):
                a, b = snd[i], snd[j]
                if a[0] == b[0] or not (a[3] or b[3]):
                    continue
                if (t // 16 + 1, *sorted((a[0], b[0]))) in {
                        (bb, *sorted(pp)) for bb, *pp in CLASH_ALLOW}:
                    continue
                iv = abs(a[1] - b[1])
                if iv % 12 == 1:
                    clashes.append(
                        f"m{t // 16 + 1}.{t % 16:02d} {a[0]}:{a[2]} "
                        f"x {b[0]}:{b[2]} ({'m2' if iv == 1 else 'b9'})")
    # parallel perfect fifths / octaves between the top notes of two parts
    lines = {pid: top_line(evs) for pid, evs in parsed.items()}
    parallels = []
    ids = list(parsed)
    # (part, part, bar) for intentional doublings. m6: violin II E5-D5 over
    # the bass E3-D3, as in the user's MIDI.
    allow = {("vn2", "vc", 6)}
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = lines[ids[i]], lines[ids[j]]
            times = sorted({t for t, _ in a} | {t for t, _ in b})

            def at(line, t):
                cur = None
                for s, p in line:
                    if s > t:
                        break
                    cur = p
                return cur
            prev = None
            for t in times:
                pa, pb = at(a, t), at(b, t)
                if None in (pa, pb):
                    prev = None
                    continue
                if prev and pa != prev[0] and pb != prev[1]:
                    iv0 = abs(prev[0] - prev[1]) % 12
                    iv1 = abs(pa - pb) % 12
                    same_dir = (pa - prev[0]) * (pb - prev[1]) > 0
                    if (ids[i], ids[j], t // 16 + 1) in allow:
                        pass
                    elif same_dir and iv0 == iv1 and iv1 in (0, 7):
                        parallels.append(
                            f"m{t // 16 + 1}.{t % 16:02d} {ids[i]}/{ids[j]} "
                            f"{'P8' if iv1 == 0 else 'P5'}")
                prev = (pa, pb)
    return problems, clashes, parallels


# ---------------------------------------------------------------------------
# Lyric subtitles (SRT) on the same timeline as the MIDI
# ---------------------------------------------------------------------------
SUB_LINES = ["你写给我我的第一首歌", "你和我十指紧扣默写前奏", "可是那然后呢",
             "还好我有我这一首情歌", "轻轻的轻轻哼着", "哭着笑着我的天长地久"]
SUB_LEAD = 0.2  # show each line slightly before it is sung
SUB_TAIL = 1.5  # keep the last line up after the voice stops


def sec_at(abs16):
    """Seconds from the top of bar 1 to an absolute 16th, via TEMPI."""
    marks = [((b - 1) * BAR16 + s, bpm) for b, s, bpm in TEMPI]
    t = 0.0
    for i, (a, bpm) in enumerate(marks):
        if abs16 <= a:
            break
        end = marks[i + 1][0] if i + 1 < len(marks) else abs16
        t += (min(abs16, end) - a) * 15.0 / bpm
    return t


def syllables(vocal_events):
    """[lyric, start16, end16] per sung syllable (ties/melismas merged)."""
    out = []
    for e in vocal_events:
        if e["pitches"] is None:
            continue
        if e["lyric"] == BREATH:
            continue
        if e["lyric"]:
            out.append([e["lyric"], e["abs"], e["abs"] + e["dur"]])
        elif out:
            out[-1][2] = e["abs"] + e["dur"]
    return out


def write_srt(path, vocal_events):
    syl = syllables(vocal_events)
    lines, i = [], 0
    for text in SUB_LINES:
        chunk = syl[i:i + len(text)]
        assert "".join(s[0] for s in chunk) == text, text
        lines.append((text, sec_at(chunk[0][1]), sec_at(chunk[-1][2])))
        i += len(text)
    assert i == len(syl), "subtitle lines do not cover every syllable"

    def ts(t):
        ms = int(round(t * 1000))
        return (f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:"
                f"{ms // 1000 % 60:02d},{ms % 1000:03d}")

    out = []
    for k, (text, s, e) in enumerate(lines):
        start = max(0.0, s - SUB_LEAD)
        end = (min(e + SUB_TAIL, lines[k + 1][1] - SUB_LEAD - 0.04)
               if k + 1 < len(lines) else e + SUB_TAIL)
        out.append(f"{k + 1}\n{ts(start)} --> {ts(end)}\n{text}\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


def main():
    os.makedirs(OUT, exist_ok=True)
    parsed = {p["id"]: parse_part(p["data"]) for p in PARTS}
    problems, clashes, parallels = check(parsed)
    for x in problems:
        print("RANGE:", x)
    for x in clashes:
        print("CLASH:", x)
    for x in parallels:
        print("PARALLEL:", x)
    if "--check" in sys.argv:
        return
    base = os.path.join(OUT, f"{NAME}_副歌_人声弦乐四重奏")
    sc = build_score(parsed)
    sc.write("musicxml", fp=base + ".musicxml")
    polish(base + ".musicxml")
    finish_parts(base + ".musicxml")
    verify_bars(base + ".musicxml")
    all_ids = [p["id"] for p in PARTS]
    write_midi(base + "_全轨.mid", all_ids, parsed)
    write_midi(os.path.join(OUT, f"{NAME}_人声_带歌词.mid"), ["vox"],
               parsed, lyrics=True, with_cc=False)
    write_midi(os.path.join(OUT, f"{NAME}_人声_带歌词_GBK编码备用.mid"),
               ["vox"], parsed, lyrics=True, charset="gbk", with_cc=False)
    write_midi(os.path.join(OUT, f"{NAME}_人声_素.mid"), ["vox"], parsed,
               lyrics=False, with_cc=False)
    write_midi(os.path.join(OUT, f"{NAME}_弦乐四重奏_伴奏.mid"),
               [x for x in all_ids if x != "vox"], parsed)
    write_srt(os.path.join(OUT, f"{NAME}_副歌_歌词字幕.srt"), parsed["vox"])
    print("written to", OUT)


if __name__ == "__main__":
    main()
