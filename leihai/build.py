#!/usr/bin/env python3
"""泪海（副歌）— 人声 + 弦乐四重奏 编配生成器

Generates, from one source of truth:
  * MusicXML full score (for Sibelius / MuseScore / ACE Studio)
  * Full multitrack MIDI (for ACE Studio: Vocal Synth + String Section)
  * Vocal-only MIDI with lyrics (UTF-8 and GBK), and a plain vocal MIDI
  * Strings-only MIDI and lyric subtitles (SRT)

Key: F major (1=F; the source jianpu is in D), 4/4, quarter = 59.
Form: Intro (m1-5, pickup "你怎么" in m5) | Chorus I, lyrical (m6-14) |
      Lift (m14 b3 - m15, strings stop on beat 4, voice alone) |
      Chorus II, full (m16-24) | Coda (m25-27)

Token syntax (durations in 16th notes, one string per bar):
  C5/2        note C5, an eighth
  D4+F4/8     double stop
  r/4         rest
  A4/1~       tie into the next note
  F5/1>       accent
  (G4/1 A4/1) slur start / slur end
  G4/1=怎     lyric
  g:G4        grace note before the next note
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
NAME = "泪海"
NBARS = 27
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
# Harmony (half bars unless noted)
#   Intro   Fsus2 | F  C/E | Dm7  Dm7/C | Bbmaj7 (C9sus4) | C7sus4  C7
#   Chorus  Fadd9  C/E | Dm7  Dm7/C | Bbmaj7  Am7 | Gm7  C7sus4 C7 |
#           Fadd9  C/E | Dm7  G9/B  | Bbmaj7  Bbm6 F/A | Gm7  C7sus4 C7 |
#   I end   Fadd9  Bbmaj7 Gm7 | C7sus4 (lift, stop on beat 4)
#   II end  Db  Eb(add9) | F   (bVI - bVII - I)
#   Coda    Bbmaj9  Bbm6 | Fadd9
# ---------------------------------------------------------------------------
REST = "r/16"

CHORUS_VOCAL = {
    0: "A4/3=舍 C5/1~=得 C5/2 (A4/1=让 G4/1) G4/2=我 A4/1=的 G4/1~=泪 G4/1 "
       "A4/2=流 C5/1=向",
    1: "g:G4 F4/12=海 A4/2=付 G4/1=出 F4/1=的",
    2: "D4/3=感 F4/1~=情 F4/1 (F4/1=永 G4/1) C4/1~=远 C4/4 A4/2=找 C5/1=不 "
       "(A4/1=回",
    3: "G4/2) G4/2~=来 G4/8 r/1 C5/1=你 D5/1=怎 C5/1=么",
    4: "A4/3=舍 C5/1~=得 C5/2 (D5/1=让 G4/1) G4/2=我 A4/1=的 G4/1~=爱 G4/1 "
       "A4/2=流 C5/1=向",
    5: "g:G4 F4/12=海 A4/2=伤 G4/1=心 F4/1=的",
    6: "D4/2=往 F4/2=事 F4/1=一 G4/2=幕 C4/1~=幕 C4/4 A4/2=就 C5/1=像 "
       "(A4/1=潮",
    7: "G4/2) G4/2~=水 G4/8 A4/2=将 C5/2=我",
}

VOCAL = {b: REST for b in range(1, NBARS + 1)}
VOCAL[5] = "r/13 C5/1=你 D5/1=怎 C5/1=么"
for i in range(8):
    VOCAL[6 + i] = CHORUS_VOCAL[i]
    VOCAL[16 + i] = CHORUS_VOCAL[i]
VOCAL[14] = "(G4/1=淹 F4/2) F4/1~=埋 F4/8 r/4"
VOCAL[15] = "r/13 C5/1=你 D5/1=怎 C5/1=么"
VOCAL[24] = "(G4/1=淹 F4/2) F4/1~=埋 F4/12~"
VOCAL[25] = "F4/8 r/8"

VN1 = {
    1: "r/13 (C5/1 D5/1 C5/1",
    2: "A4/3 C5/1~ C5/8) r/1 (C5/1 D5/1 C5/1",
    3: "A4/3 C5/1~ C5/8) r/1 (F5/1 G5/1 F5/1",
    4: "D5/3 F5/1~ F5/8 D5/3 C5/1~",
    5: "C5/12) r/4",
    6: REST,
    7: "r/5 (C6/1 D6/1 C6/1 A5/3 C6/1~ C6/4~",
    8: "C6/6 Bb5/2 C6/8)",
    9: "(Bb5/6 A5/2 F5/4 E5/4)",
    10: "(F5/4 A5/4 G5/8",
    11: "F5/4 A5/2 G5/2 F5/4 D5/4)",
    12: "(F5/4 C6/4 Bb5/4 C6/4",
    13: "Bb5/6 A5/2 C6/4 G5/4",
    14: "A5/8) (F5/4 G5/4",
    15: "F5/4) (G5/1 A5/1 Bb5/1 C6/1 D6/1 E6/1 F6/1 G6/1) r/4",
    16: "(C6/6 D6/2 C6/4 E6/4",
    17: "F6/4 E6/2 D6/2~ D6/4 C6/2 A5/2)",
    18: "(Bb5/4 D6/4 C6/8",
    19: "Bb5/4 A5/2 Bb5/2 C6/4 Bb5/4)",
    20: "(A5/8 C6/4 E6/4",
    21: "F6/4 E6/2 D6/2~ D6/8)",
    22: "(D6/4 F6/4 G6/4 F6/4~",
    23: "F6/12 E6/4)",
    24: "(F6/8 G6/8",
    25: "F6/12) r/1 (C6/1 D6/1 C6/1",
    26: "A5/3 C6/1~ C6/8) (Db6/4",
    27: "C6/16)",
}

VN2 = {
    1: "G4/16~",
    2: "G4/16",
    3: "F4/8 D4/8",
    4: "F4/12 G4/4",
    5: "F4/8 E4/8",
    6: "(E5/16~",
    7: "E5/8 D5/8~",
    8: "D5/8 C5/8",
    9: "D5/16)",
    10: "(C5/16",
    11: "D5/4 F5/2 E5/2 D5/4 B4/4)",
    12: "(D5/4 A5/4 G5/4 F5/4",
    13: "D5/6 E5/2 F5/4 E5/4",
    14: "F5/8) (D5/8",
    15: "C5/4) (E5/1 F5/1 G5/1 A5/1 Bb5/1 C6/1 D6/1 E6/1) r/4",
    16: rep("F5", 4, 2) + " " + rep("G5", 4, 2),
    17: rep("A5", 4, 2) + " " + rep("F5", 4, 2),
    18: rep("F5", 4, 2) + " " + rep("E5", 4, 2),
    19: rep("G5", 4, 2) + " " + rep("F5", 2, 2) + " " + rep("E5", 2, 2),
    20: rep("F5", 8, acc=DRIVE) + " " + rep("G5", 8, acc=DRIVE),
    21: rep("A5", 8, acc=DRIVE) + " " + rep("F5", 8, acc=DRIVE),
    22: rep("Bb5", 8, acc=DRIVE) + " " + rep("F5", 8, acc=DRIVE),
    23: rep("G5", 8, acc=DRIVE) + " " + rep("F5", 4, acc=(0, 3)) + " "
        + rep("G5", 4, acc=(2,)),
    24: "(F5/8 G5/8)",
    25: "A5/8 C5/8",
    26: "(F4/8 G4/8",
    27: "A4/16)",
}

VA_CHORUS = {
    0: "(A3/2 C4/2 G4/2 C4/2) (G3/2 E4/2 C4/2 G3/2)",
    1: "(F3/2 A3/2 C4/2 A3/2) (C4/2 D4/2 A3/2 D4/2)",
    2: "(D3/2 F3/2 A3/2 F3/2) (G3/2 E3/2 C4/2 A3/2)",
    3: "(Bb3/2 D4/2 F4/2 D4/2) (G3/2 C4/2 E4/2 Bb3/2)",
    # 16th waves for the build / second half of the full chorus
    "12": "(F3/1 Bb3/1 D4/1 F4/1 D4/1 Bb3/1 F3/1 Bb3/1) "
          "(Db3/1 F3/1 G3/1 Bb3/1 F4/1 C4/1 A3/1 C4/1)",
    "13": "(G3/1 Bb3/1 D4/1 F4/1 D4/1 Bb3/1 G3/1 Bb3/1) "
          "(C4/1 F4/1 G4/1 C4/1 E4/1 G4/1 Bb4/1 G4/1)",
}

VA = {
    1: "C4/16~",
    2: "C4/16",
    3: "C4/8 A3/8",
    4: "A3/12 Bb3/4",
    5: "Bb3/16",
    6: VA_CHORUS[0],
    7: VA_CHORUS[1],
    8: VA_CHORUS[2],
    9: VA_CHORUS[3],
    10: "(F3/2 C4/2 G4/2 C4/2) (E3/2 C4/2 G4/2 C4/2)",
    11: "(D3/2 A3/2 C4/2 A3/2) (D3/2 G3/2 F3/2 D4/2)",
    12: VA_CHORUS["12"],
    13: VA_CHORUS["13"],
    14: "(F3/2 C4/2 G4/2 C4/2) (D3/2 F3/2 Bb3/2 G3/2)",
    15: rep("G3", 12) + " r/4",
    16: VA_CHORUS[0],
    17: VA_CHORUS[1],
    18: VA_CHORUS[2],
    19: VA_CHORUS[3],
    20: "(F3/1 C4/1 F4/1 G4/1 F4/1 C4/1 A3/1 C4/1) "
        "(E3/1 G3/1 C4/1 E4/1 G4/1 E4/1 C4/1 G3/1)",
    21: "(D3/1 A3/1 C4/1 D4/1 C4/1 A3/1 F3/1 A3/1) "
        "(D3/1 G3/1 B3/1 D4/1 F4/1 D4/1 B3/1 G3/1)",
    22: VA_CHORUS["12"],
    23: VA_CHORUS["13"],
    24: "(Db3/1 Ab3/1 Db4/1 F4/1 Ab4/1 F4/1 Db4/1 Ab3/1) "
        "(Eb3/1 Bb3/1 Eb4/1 G4/1 Bb4/1 G4/1 Eb4/1 Bb3/1)",
    25: "A3/8 C4/8",
    26: "(D4/8 Db4/8)",
    27: "C4+G4/16",
}

VC = {
    1: "F3/16~",
    2: "F3/8 E3/8",
    3: "D3/8 C3/8",
    4: "Bb2/12 C2/4~",
    5: "C2/16",
    6: "F3/8 E3/8",
    7: "D3/8 C3/8",
    8: "Bb2/8 A2/4 C3/4",
    9: "G2/8 C3/8",
    10: "F2/8 E2/8",
    11: "D2/6 A2/2 B2/8",
    12: "Bb2/8 Bb2/4 A2/2 F2/2",
    13: "G2/8 C3/4 C2/4",
    14: "F2/8 Bb2/4 G2/4",
    15: " ".join(["C2/1 C3/1"] * 6) + " r/4",
    16: "F2/2 F3/2 F2/2 F3/2 E2/2 E3/2 E2/2 E3/2",
    17: "D2/2 D3/2 D2/2 D3/2 C2/2 C3/2 C2/2 C3/2",
    18: "Bb2/2 F3/2 Bb2/2 F3/2 A2/2 E3/2 A2/2 E3/2",
    19: "G2/2 D3/2 G2/2 D3/2 C2/2 C3/2 C2/2 C3/2",
    20: "F2/2 F3/2 F2/2 F3/2 E2/2 E3/2 E2/2 E3/2",
    21: "D2/2 D3/2 D2/2 D3/2 B2/2 G3/2 B2/2 G3/2",
    22: "Bb2/2 F3/2 Bb2/2 F3/2 Bb2/2 F3/2 A2/2 F3/2",
    23: "G2/2 D3/2 G2/2 D3/2 C2/2 C3/2 C2/2 C3/2",
    24: "Db2+Db3/8 Eb2+Eb3/8",
    25: "F2+F3/8 F2/8",
    26: "Bb2/16",
    27: "F2/16",
}

# Dynamics: (bar, 16th, mark). Hairpins: (bar, 16th, bar2, 16th2, kind).
# Text: (bar, 16th, text)
PARTS = [
    dict(id="vox", name="Voice", abbr="V.", data=VOCAL,
         inst=instrument.Soprano, clef=clef.TrebleClef, program=52,
         dyn=[(5, 13, "mp"), (10, 0, "mf"), (15, 13, "f"), (24, 0, "ff"),
              (25, 8, "p")],
         hair=[(12, 0, 13, 15, "cresc"), (20, 0, 23, 15, "cresc"),
               (25, 0, 25, 7, "dim")],
         text=[(15, 13, "a cappella")]),
    dict(id="vn1", name="Violin I", abbr="Vln. I", data=VN1,
         inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(1, 13, "mp"), (5, 0, "p"), (7, 5, "p"), (10, 0, "mp"),
              (14, 0, "mf"), (15, 4, "mp"), (16, 0, "f"), (20, 0, "ff"),
              (25, 13, "pp"), (27, 0, "pp")],
         hair=[(3, 0, 4, 7, "cresc"), (4, 8, 5, 11, "dim"),
               (12, 0, 13, 15, "cresc"), (15, 4, 15, 11, "cresc"),
               (19, 0, 19, 15, "cresc"), (24, 0, 24, 15, "cresc"),
               (25, 0, 25, 11, "dim"), (26, 8, 27, 15, "dim")],
         text=[(1, 13, "dolce"), (7, 5, "espr."), (15, 4, "cresc. molto"),
               (16, 0, "con passione"), (25, 13, "eco")]),
    dict(id="vn2", name="Violin II", abbr="Vln. II", data=VN2,
         inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(1, 0, "pp"), (3, 0, "p"), (6, 0, "p"), (10, 0, "mp"),
              (14, 0, "mf"), (15, 4, "mp"), (16, 0, "f"), (24, 0, "ff"),
              (26, 0, "p"), (27, 0, "pp")],
         hair=[(1, 0, 2, 15, "cresc"), (12, 0, 13, 15, "cresc"),
               (15, 4, 15, 11, "cresc"), (19, 0, 19, 15, "cresc"),
               (25, 0, 25, 15, "dim")],
         text=[(16, 0, "marcato"), (20, 0, "marc., on the string")]),
    dict(id="va", name="Viola", abbr="Vla.", data=VA,
         inst=instrument.Viola, clef=clef.AltoClef, program=41,
         dyn=[(1, 0, "pp"), (3, 0, "p"), (6, 0, "p"), (10, 0, "mp"),
              (14, 0, "mf"), (15, 0, "p"), (16, 0, "f"), (24, 0, "ff"),
              (26, 0, "p"), (27, 0, "pp")],
         hair=[(1, 0, 2, 15, "cresc"), (12, 0, 13, 15, "cresc"),
               (15, 0, 15, 11, "cresc"), (19, 0, 19, 15, "cresc"),
               (25, 0, 25, 15, "dim")],
         text=[(6, 0, "legato, come onde")]),
    dict(id="vc", name="Violoncello", abbr="Vc.", data=VC,
         inst=instrument.Violoncello, clef=clef.BassClef, program=42,
         dyn=[(1, 0, "pp"), (3, 0, "p"), (6, 0, "p"), (10, 0, "mp"),
              (14, 0, "mf"), (15, 0, "p"), (16, 0, "f"), (24, 0, "ff"),
              (26, 0, "p"), (27, 0, "pp")],
         hair=[(1, 0, 2, 15, "cresc"), (12, 0, 13, 15, "cresc"),
               (15, 0, 15, 11, "cresc"), (19, 0, 19, 15, "cresc"),
               (25, 0, 25, 15, "dim")],
         text=[(16, 0, "marcato")]),
]

VEL = {"pp": 36, "p": 48, "mp": 62, "mf": 76, "f": 92, "ff": 106}
ACCENT = 14

# Tempo map: (bar, 16th, bpm)
TEMPI = [(1, 0, 59), (24, 0, 58), (24, 8, 55), (25, 0, 52), (25, 12, 54),
         (26, 8, 50), (27, 0, 44)]
REHEARSAL = {1: "Intro", 6: "A  副歌 I", 16: "B  副歌 II", 25: "Coda"}
TEMPO_TEXT = [(24, 8, "allarg."), (26, 8, "rit.")]
SYSTEM_BREAKS = (6, 9, 12, 14, 16, 19, 22, 24)

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
            if p["id"] == "vox":
                mm = tempo.MetronomeMark(text="Andante espressivo",
                                         number=59, referent=1.0)
                mm.placement = "above"
                m.insert(0, mm)
        if p["id"] == "vox" and b in REHEARSAL:
            rm = expressions.RehearsalMark(REHEARSAL[b])
            rm.placement = "above"
            m.insert(0, rm)
        for e in by_bar[b]:
            if e["grace"]:
                g = note.Note(m21_name(e["grace"]), type="16th")
                g = g.getGrace()
                g.duration.slash = True
                m.append(g)
            pieces = split_dur(e["pos"], e["dur"])
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
        if p["id"] == "vox":  # after the notes, or append() would shift them
            for tb, ts, txt in TEMPO_TEXT:
                if tb == b:
                    m.insert(ts / 4, tempo.TempoText(txt))
        if b == NBARS:
            for n in m.notesAndRests:
                if not n.isRest:
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

    for bb, s, mark in p["dyn"]:
        d = dynamics.Dynamic(mark)
        d.placement = "above" if p["id"] == "vox" else "below"
        measures[bb].insert(s / 4, d)
    for bb, s, bb2, s2, kind in p["hair"]:
        n1, n2 = obj_at(bb, s), obj_at(bb2, s2, forward=False)
        if n1 is not None and n2 is not None and n1 is not n2:
            sp = (dynamics.Crescendo if kind == "cresc"
                  else dynamics.Diminuendo)(n1, n2)
            part.insert(0, sp)
    for bb, s, txt in p["text"]:
        te = expressions.TextExpression(txt)
        te.style.fontStyle = "italic"
        te.placement = "above"
        measures[bb].insert(s / 4, te)
    return part


def build_score(parsed):
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = "泪海（副歌）"
    md.movementName = "泪海（副歌）· 人声与弦乐四重奏"
    md.composer = "李忠屏 曲"
    md.lyricist = "许常德、李忠屏 词"
    md.add("arranger", "人声与弦乐四重奏 · F大调")
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
    for b, name in REHEARSAL.items():
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
          "va": ("C3", "Bb4"), "vc": ("C2", "G3")}


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
                iv = abs(a[1] - b[1])
                if iv % 12 == 1:
                    clashes.append(
                        f"m{t // 16 + 1}.{t % 16:02d} {a[0]}:{a[2]} "
                        f"x {b[0]}:{b[2]} ({'m2' if iv == 1 else 'b9'})")
    # parallel perfect fifths / octaves between the top notes of two parts
    lines = {pid: top_line(evs) for pid, evs in parsed.items()}
    parallels = []
    ids = list(parsed)
    # intentional: the violins double each other in octaves at the climax
    allow = {("vn1", "vn2", 24)}
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
SUB_LINES = ["你怎么舍得让我的泪流向海", "付出的感情永远找不回来",
             "你怎么舍得让我的爱流向海", "伤心的往事一幕幕", "就像潮水将我淹埋"] * 2
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
