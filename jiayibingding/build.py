#!/usr/bin/env python3
"""甲乙丙丁（副歌）— 人声 + 弦乐五重奏 编配生成器

Generates, from one source of truth:
  * MusicXML full score (for Sibelius / MuseScore / ACE Studio)
  * Full multitrack MIDI (for ACE Studio: Vocal Synth + String Section)
  * Vocal-only MIDI with lyrics, and a plain vocal MIDI without lyrics

Key: F major (1=F), 4/4, quarter = 65.
Form: Intro (m1-8, pickup "你我" in m8) | Chorus (m9-16) | Coda (m16 b3 - m21)

Token syntax (durations in 16th notes, one string per bar):
  C5/2        note C5, an eighth
  D4+F4/8     double stop
  r/4         rest
  A4/1~       tie into the next note
  (G4/1 A4/1) slur start / slur end
  G4/1=怎     lyric
  g:G4        grace note before the next note
"""
import os
import re
import sys

import mido
from music21 import (bar, clef, duration, dynamics, expressions, instrument,
                     key, layout, metadata, meter, note, chord, spanner, stream,
                     tempo, tie)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
NBARS = 21
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


# ---------------------------------------------------------------------------
# Ripple texture (Va + Vn II interlocking 16ths, each holding its 4th note)
# ---------------------------------------------------------------------------
R = {
    (1, "a"): "F3 Bb3 C4 D4 | F4 A4 C5 A4",
    (1, "b"): "F3 C4 D4 F4 | G4 A4 D5 C5",
    (2, "a"): "E3 G3 A3 C4 | E4 G4 A4 G4",
    (2, "b"): "F3 A3 C4 F4 | F4 A4 C5 D5",
    (3, "a"): "G3 Bb3 D4 F4 | G4 D5 F5 D5",
    (3, "b"): "G3 C4 D4 F4 | G4 Bb4 C5 A4",
    (4, "a"): "D3 F3 A3 C4 | E4 F4 A4 C5",
    (4, "b"): "F3 A3 C4 D4 | F4 A4 G4 F4",
    (5, "a"): "F3 Bb3 C4 D4 | F4 A4 C5 A4",
    (5, "b"): "F3 C4 D4 F4 | G4 A4 D5 C5",
    (6, "a"): "E3 G3 A3 C4 | E4 G4 A4 G4",
    (6, "b"): "F3 A3 C4 F4 | F4 A4 C5 D5",
    (7, "a"): "G3 Bb3 D4 F4 | A4 Bb4 D5 C5",
    (7, "b"): "E3 G3 C4 E4 | G4 A4 C5 D5",
    (8, "a"): "F3 Bb3 D4 F4 | G4 A4 C5 D5",
    (16, "b"): "F3 G3 A3 C4 | F4 A4 C5 A4",
    (17, "a"): "F3 Bb3 C4 D4 | F4 A4 C5 A4",
    (17, "b"): "F3 C4 D4 F4 | G4 A4 D5 C5",
    (18, "a"): "E3 G3 A3 C4 | E4 G4 A4 G4",
    (18, "b"): "F3 A3 C4 F4 | F4 A4 C5 D5",
    (19, "a"): "G3 Bb3 D4 F4 | F4 G4 D5 C5",
    (19, "b"): "G3 C4 D4 F4 | G4 Bb4 C5 A4",
    (20, "a"): "F3 Bb3 D4 F4 | Bb4 A4 G4 F4",
}


def rs(b, h):
    lo, hi = R[(b, h)].split("|")
    return lo.split(), hi.split()


def va_half(b, h):
    c = rs(b, h)[0]
    return f"({c[0]}/1 {c[1]}/1 {c[2]}/1 {c[3]}/5)"


def vn2_ripple_bar(b, incoming):
    """Vn II: held note from before (4) + [3x16th + held 5] + [3x16th + 1~]."""
    a = rs(b, "a")[1]
    z = rs(b, "b")[1]
    head = "r/4" if incoming is None else f"{incoming}/4"
    return (f"{head} ({a[0]}/1 {a[1]}/1 {a[2]}/1 {a[3]}/5) "
            f"({z[0]}/1 {z[1]}/1 {z[2]}/1 {z[3]}/1~)")


# ---------------------------------------------------------------------------
# The parts
# ---------------------------------------------------------------------------
REST = "r/16"

VOCAL = {b: REST for b in range(1, NBARS + 1)}
VOCAL.update({
    8: "r/12 C5/2=你 (G4/1=我 A4/1)",
    9: "G4/1=怎 A4/1=么 D4/1=两 A4/1~=清 A4/2 G4/1=怎 A4/1=么 "
       "D4/1=忍 A4/2=心 C5/1~=怎 C5/1 G4/1=么 G4/1=做 F4/1=回",
    10: "(F4/1=甲 G4/2) F4/1~=乙 F4/1 D4/2=丙 (A4/1=丁 g:G4 A4/4) "
        "C5/2=难 G4/2=道",
    11: "G4/1=非 F4/1=要 D4/1=耗 G4/1~=尽 G4/2 G4/1=所 F4/1=有 "
        "D4/1=委 G4/2=屈 D4/1=再 (C5/1=赔 D5/1) C5/2=上",
    12: "(C5/1=这 G4/1) G4/1=一 G4/1~=条 G4/1 (C5/1=烂 A4/1) A4/1~=命 "
        "A4/4 C5/2=爱 (G4/1=情 A4/1)",
    13: "G4/1=这 F4/1=场 D4/1=酷 A4/1~=刑 A4/2 G4/1=教 F4/1=人 "
        "D4/1=看 A4/2=清 A4/1=爱 F5/2=与 g:D5 E5/2=不",
    14: "G4/2=爱 G4/1=之 F4/1=间 G4/2=的 A4/1=差 (D5/1~=距 D5/1 C5/1 "
        "G4/1 A4/1~ A4/2) C5/1=若 g:G4 A4/1=我",
    15: "G4/1=落 F4/1=下 D4/1=泪 G4/1~=滴 G4/2 G4/1=能 F4/1=否 "
        "D4/1=换 G4/3=来 A4/2=一 G4/2=点",
    16: "F4/2=同 F4/6=情 r/8",
})

VN1 = {b: REST for b in range(1, NBARS + 1)}
VN1.update({
    5: "(D5/2 F5/2 A5/6 G5/1 F5/1 G5/4)",
    6: "(A5/2 C6/2 E6/6 D6/1 C6/1 D6/4)",
    7: "(D6/3 C6/1 A5/4) (E6/3 D6/1 C6/2 A5/2)",
    8: "(G5/6 A5/1 G5/1 F5/8~",
    9: "F5/4) r/12",
    10: "r/8 A5/8",
    11: "(G5/8 F5/8~",
    12: "F5/6 E5/2 D5/4) r/1 (A5/1 Bb5/1 C6/1",
    13: "D6/8) (C6/8",
    14: "Bb5/6 A5/10",
    15: "G5/8 F5/4 E5/4",
    16: "F5/8) (D5/1 G5/3 A5/2 G5/2",
    17: "F5/16)",
    18: "(E5/10 F5/6)",
    19: "(D5/8 C5/8)",
    20: "(D5/8 Db5/8",
    21: "C5/16)",
})

VN2 = {}
VN2[1] = vn2_ripple_bar(1, None)
prev = rs(1, "b")[1][3]
for b in range(2, 8):
    VN2[b] = vn2_ripple_bar(b, prev)
    prev = rs(b, "b")[1][3]
a8 = rs(8, "a")[1]
VN2[8] = f"{prev}/4 ({a8[0]}/1 {a8[1]}/1 {a8[2]}/1 {a8[3]}/5) r/4"
VN2.update({
    9: "r/4 (D5/4 C5/8~",
    10: "C5/16",
    11: "D5/8 G4/8",
    12: "C5/8 F4/4) r/1 (C5/1 D5/1 E5/1",
    13: "F5/8) (A5/8",
    14: "G5/6 F5/2 E5/8",
    15: "D5/12 C5/4~",
})
z16 = rs(16, "b")[1]
VN2[16] = f"C5/12) ({z16[0]}/1 {z16[1]}/1 {z16[2]}/1 {z16[3]}/1~)"
prev = z16[3]
for b in (17, 18, 19):
    VN2[b] = vn2_ripple_bar(b, prev)
    prev = rs(b, "b")[1][3]
a20 = rs(20, "a")[1]
VN2[20] = (f"{prev}/4 ({a20[0]}/1 {a20[1]}/1 {a20[2]}/1 {a20[3]}/5) "
           f"G4/4~")
VN2[21] = "G4/16"

VA = {}
for b in range(1, 8):
    VA[b] = va_half(b, "a") + " " + va_half(b, "b")
VA[8] = va_half(8, "a") + " (G3/1 C4/1 D4/1 F4/5)"
VA.update({
    9: "(D3/2 F3/2 A3/2 C4/2 A3/2 C4/2 D4/2 A3/2)",
    10: "(D3/2 F3/2 A3/2 F3/2) (A3/2 C4/2 F4/2 C4/2)",
    11: "(D3/2 F3/2 G3/2 Bb3/2) (C3/2 G3/2 Bb3/2 D4/2)",
    12: "(F3/2 A3/2 C4/2 A3/2) (D3/2 F3/2 A3/2 C4/2)",
    13: "(D3/1 F3/1 A3/1 D4/1 C4/1 A3/1 F3/1 A3/1) "
        "(C3/1 G3/1 C4/1 F4/1 C4/1 G3/1 E3/1 G3/1)",
    14: "(D3/1 G3/1 Bb3/1 D4/1 F4/1 D4/1 Bb3/1 G3/1) "
        "(C3/1 E3/1 A3/1 C4/1 E4/1 C4/1 A3/1 E3/1)",
    15: "(D3/2 F3/2 A3/2 C4/2) (C3/2 G3/2 Bb3/2 E4/2)",
    16: "(F3/2 A3/2 C4/2 A3/2) " + va_half(16, "b"),
    17: va_half(17, "a") + " " + va_half(17, "b"),
    18: va_half(18, "a") + " " + va_half(18, "b"),
    19: va_half(19, "a") + " " + va_half(19, "b"),
    20: va_half(20, "a") + " Db4/8",
    21: "F3+C4/16",
})

VC = {
    1: "(D3/2 F3/2 A3/6 G3/1 F3/1 G3/4)",
    2: "(A3/2 C4/2 E4/6 D4/1 C4/1 D4/4)",
    3: "(D4/3 C4/1 A3/4) (G3/2 F3/2 G3/2 A3/2",
    4: "A3/6 G3/1 A3/1 F3/8)",
    5: "r/8 (D3/2 F3/2 A3/4",
    6: "C4/4 A3/2 G3/2) (F3/4 G3/2 A3/2",
    7: "D4/4 Bb3/2 G3/2) (A3/4 C4/2 E4/2",
    8: "D4/4 C4/2 A3/2 G3/8)",
    9: "Bb2/8 A2/8",
    10: "D3/8 (F3/2 A3/2 C4/4",
    11: "D4/6 C4/2 Bb3/4 G3/4)",
    12: "(A3/6 G3/1 A3/1) (F3/2 A3/2 C4/2 E4/2",
    13: "D4/8) (C4/8",
    14: "Bb3/8 A3/8",
    15: "G3/8 F3/4 E3/4",
    16: "F3/8) r/8",
    17: "(D3/2 F3/2 A3/6 G3/1 F3/1 G3/4)",
    18: "(A3/2 C4/2 E4/6 D4/1 C4/1 D4/4)",
    19: "(D4/3 C4/1 A3/4) (G3/2 F3/2 G3/2 A3/2)",
    20: "(Bb3/6 A3/1 G3/1 F3/4 G3/4",
    21: "A3/16)",
}

CB = {  # sounding pitch
    1: "Bb1/16", 2: "A1/8 D2/8", 3: "G1/8 C2/8", 4: "D2/8 C2/8",
    5: "Bb1/16", 6: "A1/8 D2/8", 7: "G1/8 A1/8", 8: "Bb1/8 C2/8",
    9: "Bb1/8 A1/8", 10: "D2/8 C2/8", 11: "Bb1/8 C2/8",
    12: "A1/8 D2/4 C2/4", 13: "Bb1/8 C2/8", 14: "G1/8 A1/8",
    15: "Bb1/8 C2/8", 16: "F1/8 A1/8", 17: "Bb1/16", 18: "A1/8 D2/8",
    19: "G1/8 C2/8", 20: "Bb1/16", 21: "F1/16",
}

# Dynamics: (bar, 16th, mark). Hairpins: (bar, 16th, bar2, 16th2, kind).
# Text: (bar, 16th, text)
PARTS = [
    dict(id="vox", name="Voice", abbr="V.", zh="人声", data=VOCAL,
         inst=instrument.Soprano, clef=clef.TrebleClef, program=52,
         dyn=[(8, 12, "mp"), (13, 0, "f"), (15, 0, "mf"), (16, 0, "mp")],
         hair=[(12, 0, 12, 15, "cresc"), (15, 8, 15, 15, "dim")],
         text=[]),
    dict(id="vn1", name="Violin I", abbr="Vln. I", zh="第一小提琴",
         data=VN1, inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(5, 0, "mp"), (7, 0, "mf"), (8, 8, "p"), (10, 8, "p"),
              (13, 0, "f"), (15, 8, "mp"), (16, 8, "p"), (21, 0, "pp")],
         hair=[(6, 0, 6, 15, "cresc"), (8, 0, 8, 7, "dim"),
               (11, 0, 12, 15, "cresc"), (14, 8, 15, 7, "dim"),
               (20, 0, 20, 15, "dim")],
         text=[(5, 0, "dolce, espressivo"), (16, 8, "eco")]),
    dict(id="vn2", name="Violin II", abbr="Vln. II", zh="第二小提琴",
         data=VN2, inst=instrument.Violin, clef=clef.TrebleClef, program=40,
         dyn=[(1, 4, "pp"), (7, 0, "p"), (9, 4, "p"), (13, 0, "f"),
              (15, 8, "mp"), (16, 12, "pp"), (21, 0, "pp")],
         hair=[(3, 0, 3, 11, "cresc"), (4, 0, 4, 15, "dim"),
               (6, 0, 6, 15, "cresc"), (8, 0, 8, 11, "dim"),
               (11, 0, 12, 15, "cresc"), (14, 8, 15, 7, "dim")],
         text=[(1, 4, "legato, come acqua")]),
    dict(id="va", name="Viola", abbr="Vla.", zh="中提琴", data=VA,
         inst=instrument.Viola, clef=clef.AltoClef, program=41,
         dyn=[(1, 0, "pp"), (7, 0, "p"), (8, 8, "pp"), (9, 0, "p"),
              (13, 0, "mf"), (15, 0, "mp"), (16, 0, "p"), (17, 0, "pp"),
              (21, 0, "pp")],
         hair=[(3, 0, 3, 11, "cresc"), (4, 0, 4, 15, "dim"),
               (6, 0, 6, 15, "cresc"), (11, 0, 12, 15, "cresc")],
         text=[(1, 0, "legato, come acqua")]),
    dict(id="vc", name="Violoncello", abbr="Vc.", zh="大提琴", data=VC,
         inst=instrument.Violoncello, clef=clef.BassClef, program=42,
         dyn=[(1, 0, "mp"), (4, 8, "p"), (5, 8, "p"), (7, 0, "mp"),
              (9, 0, "mp"), (13, 0, "f"), (15, 8, "mp"), (16, 0, "p"),
              (17, 0, "mp"), (21, 0, "pp")],
         hair=[(3, 0, 3, 11, "cresc"), (4, 0, 4, 7, "dim"),
               (6, 0, 6, 15, "cresc"), (8, 0, 8, 15, "dim"),
               (11, 0, 12, 15, "cresc"), (14, 8, 15, 7, "dim"),
               (20, 0, 20, 15, "dim")],
         text=[(1, 0, "cantabile, espressivo"), (10, 8, "espr."),
               (17, 0, "cantabile")]),
    dict(id="cb", name="Contrabass", abbr="Cb.", zh="低音提琴", data=CB,
         inst=instrument.Contrabass, clef=clef.BassClef, program=43,
         dyn=[(1, 0, "pp"), (5, 0, "p"), (9, 0, "mp"), (13, 0, "f"),
              (15, 8, "mp"), (16, 0, "p"), (17, 0, "pp")],
         hair=[(11, 0, 12, 15, "cresc"), (20, 0, 21, 15, "dim")],
         text=[]),
]

VEL = {"pp": 36, "p": 48, "mp": 62, "mf": 76, "f": 92, "ff": 106}

# Tempo map: (bar, 16th, bpm)
TEMPI = [(1, 0, 65), (20, 0, 63), (20, 8, 59), (20, 12, 55), (21, 0, 48)]

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(\()?((?:[A-G][#b]?\d)(?:\+[A-G][#b]?\d)*|r)/(\d+)(~)?(\))?(?:=(.+))?$")


def parse_bar(s):
    evs, pos, pending_grace = [], 0, None
    for t in s.split():
        if t.startswith("g:"):
            pending_grace = t[2:]
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r} in {s!r}")
        sl, pit, dur, ti, sr, lyr = m.groups()
        dur = int(dur)
        evs.append(dict(
            pos=pos, dur=dur,
            pitches=None if pit == "r" else pit.split("+"),
            tie=bool(ti), slur_start=bool(sl), slur_end=bool(sr),
            lyric=lyr, grace=pending_grace))
        pending_grace = None
        pos += dur
    if pos != BAR16:
        raise ValueError(f"bar sums to {pos}: {s!r}")
    return evs


def parse_part(data):
    out = []
    for b in range(1, NBARS + 1):
        for e in parse_bar(data[b]):
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
    is_cb = p["id"] == "cb"
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
                                         number=65, referent=1.0)
                mm.placement = "above"
                m.insert(0, mm)
        if p["id"] == "vox" and b in (1, 9, 17):
            rm = expressions.RehearsalMark(
                {1: "Intro", 9: "Chorus", 17: "Coda"}[b])
            rm.placement = "above"
            m.insert(0, rm)
        if p["id"] == "vox" and b == 20:
            m.insert(0, tempo.TempoText("rit."))
        for e in by_bar[b]:
            if e["grace"]:
                gp = e["grace"]
                g = note.Note(m21_name(gp), type="16th")
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
                    if is_cb:  # written an octave above sounding
                        names = [re.sub(r"(\d)$",
                                        lambda mm: str(int(mm.group(1)) + 1),
                                        x) for x in names]
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
                if not n.isRest:
                    f = expressions.Fermata()
                    f.type = "upright"
                    f.placement = "above"
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
        if p["id"] == "vox":
            d.placement = "above"
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
    md.title = "甲乙丙丁（副歌）"
    md.movementName = "甲乙丙丁（副歌）· 人声与弦乐五重奏"
    md.composer = "应晓璃 词曲"
    sc.insert(0, md)
    for p in PARTS:
        sc.insert(0, make_m21(p, parsed[p["id"]]))
    sc.insert(0, layout.StaffGroup(
        [x for x in sc.parts][1:], name="Strings", symbol="bracket"))
    return sc


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
def merged_notes(events):
    """Merge tied notes; returns list of dicts (start16, dur16, pitches,
    lyric, slurred-into, grace)."""
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
    tr = mido.MidiTrack()
    tr.append(mido.MetaMessage("track_name", name="甲乙丙丁 副歌", time=0))
    tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4,
                               time=0))
    tr.append(mido.MetaMessage("key_signature", key="F", time=0))
    last = 0
    for b, s, bpm in TEMPI:
        t = ((b - 1) * BAR16 + s) * T16
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm),
                                   time=t - last))
        last = t
    for b, name in ((1, "Intro"), (9, "Chorus"), (17, "Coda")):
        t = (b - 1) * BAR16 * T16
        tr.append(mido.MetaMessage("marker", text=name, time=t - last))
        last = t
    tr.sort(key=lambda m: 0)
    return _absolute_sort(tr)


def _absolute_sort(tr):
    ab, t = [], 0
    for m in tr:
        t += m.time
        ab.append((t, m))
    ab.sort(key=lambda x: x[0])
    out, last = mido.MidiTrack(), 0
    for t, m in ab:
        out.append(m.copy(time=t - last))
        last = t
    out.append(mido.MetaMessage("end_of_track", time=0))
    return out


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
            off -= 12
        v = vel[min(n["start"], len(vel) - 1)]
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
RANGES = {"vox": ("D4", "F5"), "vn1": ("G3", "E6"), "vn2": ("G3", "C6"),
          "va": ("C3", "F4"), "vc": ("C2", "E4"), "cb": ("E1", "D2")}


def check(parsed):
    problems = []
    for pid, evs in parsed.items():
        lo, hi = (midi_of(x) for x in RANGES[pid])
        for e in evs:
            for pit in e["pitches"] or []:
                if not lo <= midi_of(pit) <= hi:
                    problems.append(f"{pid} m{e['bar']} {pit} out of range")
    # sounding pitches per 16th
    grid = {}
    for pid, evs in parsed.items():
        for e in evs:
            if e["pitches"] is None:
                continue
            for t in range(e["abs"], e["abs"] + e["dur"]):
                for pit in e["pitches"]:
                    grid.setdefault(t, []).append((pid, midi_of(pit), pit,
                                                   t == e["abs"]))
    clashes = []
    for t, snd in sorted(grid.items()):
        for i in range(len(snd)):
            for j in range(i + 1, len(snd)):
                a, b = snd[i], snd[j]
                if a[0] == b[0]:
                    continue
                if not (a[3] or b[3]):
                    continue  # only report when something is attacked
                iv = abs(a[1] - b[1])
                if iv % 12 == 1 and iv >= 1:
                    clashes.append(
                        f"m{t // 16 + 1}.{t % 16:02d} {a[0]}:{a[2]} "
                        f"x {b[0]}:{b[2]} ({'m2' if iv == 1 else 'b9'})")
    return problems, clashes


# ---------------------------------------------------------------------------
# Lyric subtitles (SRT) on the same timeline as the MIDI / ACE render
# ---------------------------------------------------------------------------
SUB_LINES = ["你我怎么两清 怎么忍心", "怎么做回甲乙丙丁", "难道非要耗尽所有委屈",
             "再赔上这一条烂命", "爱情这场酷刑 教人看清", "爱与不爱之间的差距",
             "若我落下泪滴", "能否换来一点同情"]
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
        chars = text.replace(" ", "")
        chunk = syl[i:i + len(chars)]
        assert "".join(s[0] for s in chunk) == chars, text
        lines.append((text, sec_at(chunk[0][1]), sec_at(chunk[-1][2])))
        i += len(chars)
    assert i == len(syl), "subtitle lines do not cover every syllable"

    def ts(t):
        ms = int(round(t * 1000))
        return (f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:"
                f"{ms // 1000 % 60:02d},{ms % 1000:03d}")

    out = []
    for k, (text, s, e) in enumerate(lines):
        start = max(0.0, s - SUB_LEAD)
        end = (lines[k + 1][1] - SUB_LEAD - 0.04 if k + 1 < len(lines)
               else e + SUB_TAIL)
        out.append(f"{k + 1}\n{ts(start)} --> {ts(end)}\n{text}\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


SOUNDS = {"Voice": ("Voice", "voice.vocals"),
          "Violin I": ("Violin", "strings.violin"),
          "Violin II": ("Violin", "strings.violin"),
          "Viola": ("Viola", "strings.viola"),
          "Violoncello": ("Violoncello", "strings.cello"),
          "Contrabass": ("Contrabass", "strings.contrabass")}


def add_instrument_sounds(path):
    """Give each part a MusicXML <instrument-sound> id so Sibelius maps the
    staves to the right instruments on import."""
    xml = open(path, encoding="utf-8").read()

    def fix(m):
        block = m.group(0)
        pname = re.search(r"<part-name>(.*?)</part-name>", block).group(1)
        iname, snd = SOUNDS[pname]
        block = re.sub(r"<instrument-name>.*?</instrument-name>",
                       f"<instrument-name>{iname}</instrument-name>", block)
        block = re.sub(r"(</instrument-abbreviation>)",
                       rf"\1\n        <instrument-sound>{snd}"
                       r"</instrument-sound>", block, count=1)
        return block

    xml = re.sub(r"<score-part .*?</score-part>", fix, xml, flags=re.S)
    open(path, "w", encoding="utf-8").write(xml)


def main():
    os.makedirs(OUT, exist_ok=True)
    parsed = {p["id"]: parse_part(p["data"]) for p in PARTS}
    problems, clashes = check(parsed)
    for x in problems:
        print("RANGE:", x)
    for x in clashes:
        print("CLASH:", x)
    if "--check" in sys.argv:
        return
    base = os.path.join(OUT, "甲乙丙丁_副歌_人声弦乐五重奏")
    sc = build_score(parsed)
    sc.write("musicxml", fp=base + ".musicxml")
    add_instrument_sounds(base + ".musicxml")
    all_ids = [p["id"] for p in PARTS]
    write_midi(base + "_全轨.mid", all_ids, parsed)
    write_midi(os.path.join(OUT, "甲乙丙丁_人声_带歌词.mid"), ["vox"],
               parsed, lyrics=True, with_cc=False)
    write_midi(os.path.join(OUT, "甲乙丙丁_人声_带歌词_GBK编码备用.mid"),
               ["vox"], parsed, lyrics=True, charset="gbk", with_cc=False)
    write_midi(os.path.join(OUT, "甲乙丙丁_人声_素.mid"), ["vox"], parsed,
               lyrics=False, with_cc=False)
    write_midi(os.path.join(OUT, "甲乙丙丁_弦乐五重奏_伴奏.mid"),
               [x for x in all_ids if x != "vox"], parsed)
    write_srt(os.path.join(OUT, "甲乙丙丁_副歌_歌词字幕.srt"), parsed["vox"])
    print("written to", OUT)


if __name__ == "__main__":
    main()
