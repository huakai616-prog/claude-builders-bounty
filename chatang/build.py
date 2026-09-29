#!/usr/bin/env python3
"""茶汤（副歌）— 人声 + 弦乐四重奏 编配生成器

Generates, from one source of truth:
  * MusicXML full score (for Sibelius / MuseScore / ACE Studio)
  * Full multitrack MIDI (for ACE Studio: Vocal Synth + String Section)
  * Vocal-only MIDI with lyrics (UTF-8 and GBK), and a plain vocal MIDI
  * Strings-only MIDI and lyric subtitles (SRT)

Key: A major (1=A, as in the source jianpu; 1 = A3 so the voice sits at
C#4-E5), 4/4, quarter = 112.
Form: Intro (m1-9, Violin I plays the song's own intro hook) |
      Chorus A, light (m10-17, strings stop on m17 beat 4, voice alone) |
      Chorus B, tutti (m18-25) | Outro (m26-30, the hook again, rit.)

Token syntax (durations in 16th notes, one string per bar):
  C5/2        note C5, an eighth
  D4+F4/8     double stop
  r/4         rest
  A4/1~       tie into the next note
  F5/1>       accent
  B4/4*       mordent (upper, "prall"; notation only, not played in MIDI)
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
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hollywood"))
import hollywood  # noqa: E402  (shared Hollywood score template)

NAME = "茶汤"
NBARS = 30
BAR16 = 16
TPQ = 480
T16 = TPQ // 4
KEY_M21 = "A"    # music21 key name
KEY_MIDI = "A"   # mido key_signature
BPM = 112

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


def drive8(a, b):
    """A bar of repeated eighths, a for beats 1-2 and b for beats 3-4,
    accented 3+3+2 across the bar."""
    return " ".join(f"{p}/2" + (">" if i in (0, 3, 6) else "")
                    for i, p in enumerate([a] * 4 + [b] * 4))


def drive16(a, b):
    """A bar of repeated sixteenths, 3+3+2 accents in each half bar."""
    return rep(a, 8, acc=(0, 3, 6)) + " " + rep(b, 8, acc=(0, 3, 6))


def octs(lo, hi, acc=False):
    """Half a bar of cello octave eighths: lo hi lo hi (accent on the
    first one if acc)."""
    return f"{lo}/2{'>' if acc else ''} {hi}/2 {lo}/2 {hi}/2"


# ---------------------------------------------------------------------------
# Harmony (half bars)
#   Intro   Dmaj9 | A(add9) | F#m7 F#m7/E | Dmaj9 | Esus4 E |
#           A A/C# | Dmaj7 | C#m7 Bm7 | Esus4 E7
#   A       A  E/G# | F#m7  F#m7/E | Dmaj7  A/C# | Bm7  E7sus4 |
#           (bass 1-7-6-5-4-3-2-5)
#           Dmaj7  C#m7 | Bm7  C#m7 | Dmaj7  Esus4 | A  A7 (stop on 4)
#   B       Dmaj7  E | C#m7  F#m7 | Bm7  E7sus4 | Dmaj7  E |
#           C#m7  F#m7 | Bm7  E7sus4 | C#m7  F#m7 | Dmaj7  E   (IV-V-iii-vi)
#   Outro   A(add9) | Dmaj7 | C#m7  F#m7 | Bm7  Dm6 (borrowed iv) | A
# ---------------------------------------------------------------------------
REST = "r/16"

VOCAL = {b: REST for b in range(1, NBARS + 1)}
VOCAL.update({
    10: "r/2 E4/2=我 E4/2=说 E4/2=再 F#4/2=喝 E4/2=一 F#4/2=碗 C#5/2=我",
    11: "B4/2=熬 B4/4*=的 F#4/4=茶 B4/6=汤",
    12: "r/2 B4/2=你 B4/2=说 B4/2=你 B4/2=现 A4/2=在 F#4/2=马 E4/2=上",
    13: "F#4/6=要 C#4/2=渡 E4/8=江",
    14: "r/2 E4/2=渡 E4/2=江 E4/2=到 F#4/2=那 E4/2=遥 F#4/2=远 C#5/2=的",
    15: "B4/2=寒 B4/4*=冷 F#4/4=北 B4/6=方",
    16: "r/2 B4/2=就 B4/2=怕 B4/2=你 B4/2=的 A4/2=手 B4/2=会 (E5/2=冻",
    17: "C#5/2) C#5/2~=僵 C#5/12",
    18: "r/2 E4/2=你 E4/2=何 E4/2=时 F#4/2=回 E4/2=来 F#4/2=喝 C#5/2=我",
    19: "B4/2=熬 B4/4*=的 F#4/4=茶 B4/6=汤",
    20: "r/2 B4/2=这 B4/2=次 B4/2=我 B4/2=会 A4/2=多 F#4/2=放 E4/2=一",
    21: "F#4/6=些 C#4/2=老 E4/8=姜",
    22: "r/2 E4/2=你 E4/2=寄 E4/2=来 F#4/2=的 E4/2=信 F#4/2=一 C#5/2=直",
    23: "B4/3=搁 B4/3*=在 A4/4=桌 B4/6=上",
    24: "r/2 B4/2=不 B4/2=知 B4/2=要 B4/2=寄 A4/2=还 F#4/2=哪 A4/2~=地",
    25: "A4/4 F#4/12=方",
})

VN1 = {
    # intro: the song's own hook (5 | 1 3 2 5 0 0 6 1 | 6 - - 3 | 5 - - - |)
    1: "r/12 (E4/4",
    2: "A4/2 C#5/2 B4/2 E5/2) r/6 (F#5/1 A5/1",
    3: "F#5/12 C#5/4",
    4: "E5/16~",
    5: "E5/12) (E5/4",
    6: "A5/2 C#6/2 B5/2 E6/2) r/6 (F#6/1 A6/1",
    7: "F#6/12 C#6/4)",
    8: "(B5/16~",
    9: "B5/8) r/8",
    10: REST,
    11: REST,
    12: REST,
    13: "r/8 (A4/2 C#5/2 B4/2 E5/2~",
    14: "E5/16)",
    15: "F#5/8 (G#5/2 B5/2 C#6/2 E6/2",
    16: "C#6/8 B5/8)",
    17: "A5/4 (E5/1 F#5/1 A5/1 B5/1 C#6/1 E6/1 F#6/1 A6/1) r/4",
    18: "(F#6/8 E6/6 B5/2",
    19: "C#6/6 B5/2 A5/2 B5/2 C#6/2 E6/2)",
    20: "(D6/8 B5/4 A5/4",
    21: "F#5/8) (G#5/2 B5/2 C#6/2 E6/2",
    22: "E6/8 C#6/4 E6/4)",
    23: "(D6/8 B5/2 C#6/2 E6/2 F#6/2",
    24: "G#6/8 A6/8~",
    25: "A6/8 G#6/8)",
    26: "(A5/2 C#6/2 B5/2 E6/2) r/6 (F#6/1 A6/1",
    27: "F#6/12 C#6/4",
    28: "E6/16)",
    29: "(B5/16",
    30: "A5/16)",
}

VN2 = {
    1: "C#4/16~",
    2: "C#4/16~",
    3: "C#4/16~",
    4: "C#4/16",
    5: "(A4/8 G#4/4) (E4/4",
    6: "A4/2 C#5/2 B4/2 E5/2) r/6 (F#5/1 A5/1",
    7: "F#5/12 C#5/4)",
    8: "(E5/8 F#5/8",
    9: "E5/8 D5/8)",
    10: "(C#5/8 B4/8",
    11: "A4/16",
    12: "C#5/16",
    13: "A4/8 B4/8)",
    14: "(A4/8 G#4/8",
    15: "A4/8 B4/8",
    16: "A4/16)",
    17: "A4/4 (B4/1 C#5/1 E5/1 F#5/1 A5/1 B5/1 C#6/1 E6/1) r/4",
    18: drive8("C#5", "B4"),
    19: drive8("E5", "C#5"),
    20: drive8("D5", "D5"),
    21: drive8("C#5", "B4"),
    22: drive16("E5", "A4"),
    23: drive16("D5", "E5"),
    24: drive16("E5", "F#5"),
    25: drive16("F#5", "G#5"),
    26: "(A4/2 C#5/2 B4/2 E5/2) r/6 (F#5/1 A5/1",
    27: "F#5/12 C#5/4)",
    28: "(B4/8 A4/8",
    29: "D5/16",
    30: "C#5/16)",
}

VA = {
    1: "F#3/16",
    2: "E3/16",
    3: "A3/16",
    4: "F#3/16",
    5: "B3/16",
    6: "(A3/2 E4/2 C#4/2 E4/2) (A3/2 E4/2 C#4/2 E4/2)",
    7: "(D3/2 A3/2 C#4/2 A3/2) (F#3/2 A3/2 C#4/2 A3/2)",
    8: "(E3/2 G#3/2 C#4/2 G#3/2) (D3/2 F#3/2 B3/2 F#3/2)",
    9: "(A3/2 B3/2 E4/2 B3/2) (E3/2 G#3/2 D4/2 G#3/2)",
    10: "(A3/2 C#4/2 E4/2 C#4/2) (G#3/2 B3/2 E4/2 B3/2)",
    11: "(F#3/2 A3/2 C#4/2 A3/2) (E3/2 A3/2 C#4/2 A3/2)",
    12: "(D3/2 F#3/2 A3/2 F#3/2) (C#3/2 E3/2 A3/2 E3/2)",
    13: "(D3/2 F#3/2 A3/2 F#3/2) (E3/2 A3/2 D4/2 A3/2)",
    14: "(F#3/2 A3/2 C#4/2 A3/2) (E3/2 G#3/2 B3/2 G#3/2)",
    15: "(D3/2 F#3/2 A3/2 F#3/2) (E3/2 G#3/2 B3/2 G#3/2)",
    16: "(F#3/2 A3/2 C#4/2 A3/2) (E3/2 A3/2 D4/2 A3/2)",
    17: "C#4/4 " + rep("E4", 4) + " " + rep("G4", 4) + " r/4",
    18: "(D3/2 A3/2 C#4/2 A3/2) (E3/2 B3/2 G#3/2 B3/2)",
    19: "(C#3/2 G#3/2 C#4/2 G#3/2) (F#3/2 C#4/2 E4/2 C#4/2)",
    20: "(D3/2 F#3/2 B3/2 F#3/2) (A3/2 D4/2 E4/2 D4/2)",
    21: "(D3/2 A3/2 C#4/2 A3/2) (E3/2 B3/2 E4/2 G#4/2)",
    22: "(C#4/2 G#3/2 E4/2 G#3/2) (F#3/2 C#4/2 A3/2 C#4/2)",
    23: "(D3/2 F#3/2 B3/2 F#3/2) (A3/2 D4/2 E4/2 D4/2)",
    24: "(C#4/1 G#3/1 E4/1 G#3/1 C#4/1 G#3/1 E4/1 G#3/1) "
        "(F#3/1 C#4/1 A3/1 C#4/1 F#3/1 C#4/1 A3/1 C#4/1)",
    25: "(D4/1 A3/1 F#4/1 A3/1 D4/1 A3/1 F#4/1 A3/1) "
        "(E4/1 B3/1 G#4/1 B3/1 E4/1 B3/1 G#4/1 B3/1)",
    26: "(A3/2 E4/2 C#4/2 E4/2) (A3/2 E4/2 C#4/2 E4/2)",
    27: "(D3/2 A3/2 C#4/2 A3/2) (F#3/2 A3/2 C#4/2 A3/2)",
    28: "G#3/8 C#4/8",
    29: "(F#3/8 F3/8",
    30: "E3/16)",
}

VC = {
    1: "D3/16",
    2: "A2/8 C#3/8",
    3: "F#2/8 E2/8",
    4: "D2/16",
    5: "E2/12 E3/4",
    6: "A2/8 C#3/8",
    7: "D3/16",
    8: "C#3/8 B2/8",
    9: "E2/16",
    10: "A2/8 G#2/8",
    11: "F#2/8 E2/8",
    12: "D3/8 C#3/8",
    13: "B2/8 E2/8",
    14: "D3/6 A2/2 C#3/6 G#2/2",
    15: "B2/6 D3/2 C#3/6 G#2/2",
    16: "D3/6 A2/2 E3/6 E2/2",
    17: "A2/4 " + " ".join(["A2/1 A3/1"] * 2) + " "
        + " ".join(["G2/1 G3/1"] * 2) + " r/4",
    18: octs("D2", "D3", True) + " " + octs("E2", "E3"),
    19: octs("C#2", "C#3") + " " + octs("F#2", "F#3"),
    20: octs("B2", "F#3") + " " + octs("E2", "E3"),
    21: octs("D2", "D3") + " " + octs("E2", "E3"),
    22: octs("C#2", "C#3", True) + " " + octs("F#2", "F#3"),
    23: octs("B2", "F#3") + " " + octs("E2", "E3"),
    24: octs("C#2", "C#3") + " " + octs("F#2", "F#3"),
    25: octs("D2", "D3") + " " + octs("E2", "E3"),
    26: "A2/2 A3/2 A2/2 A3/2 A2/8",
    27: "D2/16",
    28: "C#3/8 F#2/8",
    29: "B2/8 D3/8",
    30: "A2/16",
}

# Dynamics: (bar, 16th, mark). Hairpins: (bar, 16th, bar2, 16th2, kind).
# Text: (bar, 16th, text)
PARTS = [
    dict(id="vox", name="Voice", abbr="V.", data=VOCAL,
         inst=instrument.Soprano, clef=clef.TrebleClef, program=52,
         dyn=[(10, 2, "mp"), (18, 0, "f"), (24, 0, "ff")],
         hair=[(16, 0, 17, 15, "cresc"), (22, 0, 23, 15, "cresc"),
               (25, 4, 25, 15, "dim")],
         text=[(17, 12, "a cappella")]),
    dict(id="vn1", name="Violin I", abbr="Vln. I", data=VN1,
         inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(1, 12, "mp"), (6, 0, "mf"), (8, 0, "f"), (9, 8, "p"),
              (13, 8, "mp"), (17, 0, "mf"), (18, 0, "f"), (22, 0, "ff"),
              (26, 0, "f"), (28, 0, "mp"), (29, 0, "p"), (30, 0, "pp")],
         hair=[(5, 12, 5, 15, "cresc"), (7, 0, 7, 15, "cresc"),
               (8, 8, 9, 7, "dim"), (15, 8, 16, 15, "cresc"),
               (17, 4, 17, 11, "cresc"), (20, 0, 21, 15, "cresc"),
               (26, 8, 27, 15, "dim")],
         text=[(1, 12, "dolce"), (6, 0, "cantabile"), (13, 8, "espr."),
               (18, 0, "con passione"), (29, 0, "eco")]),
    dict(id="vn2", name="Violin II", abbr="Vln. II", data=VN2,
         inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(1, 0, "pp"), (2, 0, "p"), (6, 0, "mf"),
              (8, 0, "f"), (10, 0, "p"), (14, 0, "mp"), (17, 0, "mf"),
              (18, 0, "f"), (22, 0, "ff"), (26, 0, "f"), (28, 0, "mp"),
              (29, 0, "p"), (30, 0, "pp")],
         hair=[(1, 0, 1, 15, "cresc"), (7, 0, 7, 15, "cresc"),
               (8, 8, 9, 15, "dim"), (16, 0, 16, 15, "cresc"),
               (17, 4, 17, 11, "cresc"), (21, 0, 21, 15, "cresc"),
               (26, 8, 27, 15, "dim")],
         text=[(18, 0, "marcato"), (22, 0, "marc., on the string")]),
    dict(id="va", name="Viola", abbr="Vla.", data=VA,
         inst=instrument.Viola, clef=clef.AltoClef, program=41,
         dyn=[(1, 0, "pp"), (2, 0, "p"), (6, 0, "mf"), (8, 0, "f"),
              (10, 0, "p"), (14, 0, "mp"), (17, 0, "mf"), (18, 0, "f"),
              (22, 0, "ff"), (26, 0, "f"), (28, 0, "mp"), (29, 0, "p"),
              (30, 0, "pp")],
         hair=[(1, 0, 1, 15, "cresc"), (7, 0, 7, 15, "cresc"),
               (8, 8, 9, 15, "dim"), (16, 0, 16, 15, "cresc"),
               (17, 4, 17, 11, "cresc"), (21, 0, 21, 15, "cresc"),
               (26, 8, 27, 15, "dim")],
         text=[(6, 0, "legato, come onde")]),
    dict(id="vc", name="Violoncello", abbr="Vc.", data=VC,
         inst=instrument.Violoncello, clef=clef.BassClef, program=42,
         dyn=[(1, 0, "pp"), (2, 0, "p"), (6, 0, "mf"), (8, 0, "f"),
              (10, 0, "p"), (14, 0, "mp"), (17, 0, "mf"), (18, 0, "f"),
              (22, 0, "ff"), (26, 0, "f"), (28, 0, "mp"), (29, 0, "p"),
              (30, 0, "pp")],
         hair=[(1, 0, 1, 15, "cresc"), (7, 0, 7, 15, "cresc"),
               (8, 8, 9, 15, "dim"), (16, 0, 16, 15, "cresc"),
               (17, 4, 17, 11, "cresc"), (21, 0, 21, 15, "cresc"),
               (26, 8, 27, 15, "dim")],
         text=[(18, 0, "marcato")]),
]

VEL = {"pp": 36, "p": 48, "mp": 62, "mf": 76, "f": 92, "ff": 106}
ACCENT = 14

# Tempo map: (bar, 16th, bpm)
TEMPI = [(1, 0, BPM), (28, 0, 106), (29, 0, 98), (29, 8, 90), (30, 0, 80)]
# Section starts: (bar, rehearsal letter or None, section title)
SECTIONS = [(1, None, "Intro 前奏"), (10, "A", "Chorus 副歌"),
            (18, "B", "Climax 高潮"), (26, "C", "Coda 尾奏")]
TEMPO_TEXT = [(28, 0, "rit.")]
SYSTEM_BREAKS = (6, 10, 14, 18, 22, 24, 26, 28)
# 8va lines (notation only; the MusicXML pitches stay at concert pitch):
# (part name, first bar, last bar)
OTTAVA = [("Violin I", 24, 25)]

# Cover, title block and running header / footer (tools/hollywood)
META = dict(
    title="茶汤", title_latin="Chá Tāng",
    subtitle="副歌 · 人声与弦乐四重奏",
    subtitle_en="Chorus — for Voice and String Quartet",
    composer="陈杰汉", lyricist="方文山", artist="郁可唯",
    instrumentation=[("Voice", "人声"), ("Violin I", "第一小提琴"),
                     ("Violin II", "第二小提琴"), ("Viola", "中提琴"),
                     ("Violoncello", "大提琴")],
    key="A Major · A大调", tempo="♩ = 112", duration="ca. 1′06″",
    year="2026", tempo_text="Moderato")

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(\()?((?:[A-G][#b]?\d)(?:\+[A-G][#b]?\d)*|r)/(\d+)(>)?(\*)?(~)?(\))?"
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
        sl, pit, dur, acc, mord, ti, sr, lyr = m.groups()
        dur = int(dur)
        evs.append(dict(
            pos=pos, dur=dur,
            pitches=None if pit == "r" else pit.split("+"),
            tie=bool(ti), slur_start=bool(sl), slur_end=bool(sr),
            accent=bool(acc), mordent=bool(mord), lyric=lyr,
            grace=pending_grace))
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
                       4: [12, 4, 3, 2, 1],
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
            m.insert(0, key.Key(KEY_M21))
            m.insert(0, meter.TimeSignature("4/4"))
            if p["id"] == "vox":
                # the text is joined to it by hollywood.polish_musicxml
                mm = tempo.MetronomeMark(number=BPM, referent=1.0)
                mm.placement = "above"
                m.insert(0, mm)
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
                    if first and e["mordent"]:
                        n.expressions.append(expressions.InvertedMordent())
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
            for sb, letter, title in SECTIONS:
                if sb == b:
                    if letter:
                        rm = expressions.RehearsalMark(letter)
                        rm.placement = "above"
                        m.insert(0, rm)
                    te = expressions.TextExpression(title)
                    te.style.fontWeight = "bold"
                    te.placement = "above"
                    m.insert(0, te)
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
    md.title = META["title"]
    md.movementName = f"{META['title']}（{META['subtitle']}）"
    md.composer = META["composer"]
    md.lyricist = META["lyricist"]
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
    """Tidy the MusicXML for Sibelius: system breaks at phrase starts, one
    <instrument-sound> per part so the staves map to the right instruments,
    no per-note instrument changes, voice dynamics above the staff (lyrics
    are below), words and rehearsal marks above.  Page layout, credits and
    creators come from tools/hollywood (Hollywood house style)."""
    tree = ET.parse(path)
    r = tree.getroot()
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
        for pname, b1, b2 in OTTAVA:
            if names[part.get("id")] != pname:
                continue
            ms = {int(m.get("number")): m for m in part.findall("measure")}
            first, last = ms[b1], ms[b2]
            # pitches stay as they sound; the line shifts only the display
            start = ET.fromstring(
                '<direction placement="above"><direction-type>'
                '<octave-shift type="down" size="8"/></direction-type>'
                '</direction>')
            first.insert(list(first).index(first.find("note")), start)
            stop = ET.fromstring(
                '<direction><direction-type><octave-shift type="stop" '
                'size="8"/></direction-type></direction>')
            last.insert(list(last).index(last.findall("note")[-1]) + 1, stop)
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
            if e["slur_start"]:  # a slur may start on a tied-into note
                in_slur = True
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
          (0, mido.MetaMessage("key_signature", key=KEY_MIDI))]
    for b, s, bpm in TEMPI:
        t = ((b - 1) * BAR16 + s) * T16
        ab.append((t, mido.MetaMessage("set_tempo",
                                       tempo=mido.bpm2tempo(bpm))))
    for b, _, name in SECTIONS:
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
RANGES = {"vox": ("C#4", "E5"), "vn1": ("G3", "A6"), "vn2": ("G3", "E6"),
          "va": ("C3", "C5"), "vc": ("C2", "A3")}


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
    # intentional: the violins play the hook in octaves (intro and outro)
    allow = {("vn1", "vn2", b) for b in (5, 6, 7, 26, 27)}
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
SUB_LINES = ["我说再喝一碗我熬的茶汤", "你说你现在马上要渡江",
             "渡江到那遥远的寒冷北方", "就怕你的手会冻僵",
             "你何时回来喝我熬的茶汤", "这次我会多放一些老姜",
             "你寄来的信一直搁在桌上", "不知要寄还哪地方"]
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
    hollywood.polish_musicxml(base + ".musicxml", META)
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
    if "--pdf" in sys.argv:
        write_pdf()


def write_pdf(png_dir=None):
    """Hollywood-standard full score PDF (cover + score + header/footer)."""
    src = os.path.join(OUT, f"{NAME}_副歌_人声弦乐四重奏.musicxml")
    dst = os.path.join(OUT, f"{NAME}_副歌_总谱.pdf")
    n = hollywood.render_pdf(src, dst, META, png_dir=png_dir)
    print(f"PDF: {dst} ({n} pages)")


if __name__ == "__main__":
    main()
