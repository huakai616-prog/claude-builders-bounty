#!/usr/bin/env python3
"""大东北我的家乡 — 迪士尼风格交响乐 + 传统四声部合唱 编配生成器

Generates, from one source of truth:
  * MusicXML full score (Sibelius), transposing, with SATB lyrics
  * Full multitrack MIDI (orchestra + SATB with lyrics) for ACE Studio / a DAW
  * One MIDI + one concert-pitch MusicXML per orchestral track for
    Dreamtonics Instrument X (and the three optional non-Instrument-X tracks)
  * SATB MIDI with lyrics (UTF-8 / GBK), one file per voice, melody guide
  * Lyric subtitles (SRT)

Key: F major (1=F, as the source jianpu), last chorus and coda in G major.
Tempo: Maestoso 72 (prologue), Allegro giocoso 128.
Form (78 bars):
  Prologue  m1-4    horn call on the chorus hook, choir "啊", A7 fermata
  Intro     m5-13   the jianpu intro, oboe/flute over pizzicato strings
  Verse     m14-30  women (m14-21), men + women's "啊" (m22-25), tutti
  Chorus I  m31-47  SATB, violin countermelody, horns countermelody (m39-)
  Interlude m48-57  brass fanfare on the intro theme, choir "啊",
                    Am7 - B7 lift into G with a general pause on m57 beat 4
  Chorus II m58-73  in G, violins in octaves on the tune, horns counter
  Coda      m74-78  subito p, allargando, fermata on the high A, G6/9 end

Token syntax (durations in 16th notes, one string per bar):
  C5/2        note C5, an eighth
  D4+F4/8     chord / double stop
  r/4         rest
  A4/1~       tie into the next note
  flags after the duration: > accent  . staccato  % tremolo (roll)  t trill
  (G4/1 A4/1) slur start / slur end
  G4/1=家     lyric
  g:G4        grace note before the next note
All pitches are concert (sounding) pitch.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import mido
from music21 import (articulations, bar, clef, dynamics, expressions,
                     instrument, interval, key, layout, metadata, meter, note,
                     chord as m21chord, spanner, stream, tempo, tie)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
NAME = "大东北我的家乡"
NBARS = 78
BAR16 = 16
TPQ = 480
T16 = TPQ // 4
KEYS = {1: "F", 58: "G"}
REST = "r/16"

# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------
_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ACC = {"": 0, "#": 1, "b": -1}
LET = "CDEFGAB"
PIT = re.compile(r"([A-G])([#b]?)(-?\d)")


def midi_of(p):
    m = PIT.fullmatch(p)
    if not m:
        raise ValueError(p)
    s, acc, octv = m.groups()
    return 12 * (int(octv) + 1) + _STEP[s] + _ACC[acc]


def m21_name(p):
    return p.replace("b", "-") if len(p) > 1 and p[1] == "b" else p


def tr_pitch(p, steps=1, semis=2):
    """Diatonic transposition (default: up a major second, F -> G)."""
    s, acc, octv = PIT.fullmatch(p).groups()
    target = midi_of(p) + semis
    li = LET.index(s) + steps
    o2 = int(octv) + li // 7
    s2 = LET[li % 7]
    d = target - (12 * (o2 + 1) + _STEP[s2])
    return f"{s2}{ {0: '', 1: '#', -1: 'b'}[d] }{o2}".replace(" ", "")


def shift(p, semis):
    """Shift by whole octaves (semis must be a multiple of 12)."""
    s, acc, octv = PIT.fullmatch(p).groups()
    return f"{s}{acc}{int(octv) + semis // 12}"


# ---------------------------------------------------------------------------
# Tokens: parse / serialise / transform one bar string
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(\()?((?:[A-G][#b]?\d)(?:\+[A-G][#b]?\d)*|r)/(\d+)([>.%t]*)(~)?(\))?"
    r"(?:=(.+))?$")


def toks(s):
    out, grace = [], None
    for t in s.split():
        if t.startswith("g:"):
            grace = t[2:]
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r} in {s!r}")
        sl, pit, dur, fl, ti, sr, lyr = m.groups()
        out.append(dict(sl=bool(sl), pit=None if pit == "r" else pit.split("+"),
                        dur=int(dur), fl=fl, tie=bool(ti), sr=bool(sr), lyr=lyr,
                        grace=grace))
        grace = None
    return out


def untoks(lst):
    parts = []
    for t in lst:
        s = ""
        if t["grace"]:
            parts.append("g:" + t["grace"])
        if t["sl"]:
            s += "("
        s += "r" if t["pit"] is None else "+".join(t["pit"])
        s += f"/{t['dur']}{t['fl']}"
        if t["tie"]:
            s += "~"
        if t["sr"]:
            s += ")"
        if t["lyr"]:
            s += "=" + t["lyr"]
        parts.append(s)
    return " ".join(parts)


def _map(s, fn):
    lst = toks(s)
    for t in lst:
        if t["pit"]:
            t["pit"] = [fn(p) for p in t["pit"]]
        if t["grace"]:
            t["grace"] = fn(t["grace"])
    return untoks(lst)


def up2(s):
    """F major -> G major."""
    return _map(s, tr_pitch)


def octv(s, n):
    return _map(s, lambda p: shift(p, 12 * n))


def strip(s, slurs=True):
    """Instrumental copy of a sung line: no lyrics (and optionally no
    slurs); melismatic slurs are kept as phrasing."""
    lst = toks(s)
    for t in lst:
        t["lyr"] = None
        if not slurs:
            t["sl"] = t["sr"] = False
    return untoks(lst)


def merge(s, keep_tie=True):
    """Join repeated pitches into one sustained note (colla-parte pads)."""
    out = []
    for t in toks(s):
        t = dict(t, lyr=None, sl=False, sr=False, grace=None)
        t["fl"] = t["fl"].replace(">", "")
        if out and t["pit"] and out[-1]["pit"] == t["pit"]:
            out[-1]["dur"] += t["dur"]
            out[-1]["tie"] = t["tie"]
        elif out and t["pit"] is None and out[-1]["pit"] is None:
            out[-1]["dur"] += t["dur"]
        else:
            out.append(t)
    if not keep_tie and out:
        out[-1]["tie"] = False
    return untoks(out)


def auto_tie(part, bars):
    """Tie a sustained pitch over the barline when the next bar starts on it."""
    for b in bars:
        if b + 1 > NBARS:
            continue
        a, c = toks(part[b]), toks(part[b + 1])
        if a and c and a[-1]["pit"] and a[-1]["pit"] == c[0]["pit"] \
                and not c[0]["grace"]:
            a[-1]["tie"] = True
            part[b] = untoks(a)


# ---------------------------------------------------------------------------
# Chords and accompaniment generators
# ---------------------------------------------------------------------------
IV = {"1": (0, 0), "b3": (2, 3), "3": (2, 4), "4": (3, 5), "5": (4, 7),
      "6": (5, 9), "b7": (6, 10), "7": (6, 11), "9": (1, 2)}
QUAL = {"": "1 3 5", "m": "1 b3 5", "7": "1 3 5 b7", "maj7": "1 3 5 7",
        "m7": "1 b3 5 b7", "9": "1 3 5 b7 9", "maj9": "1 3 5 7 9",
        "add9": "1 3 5 9", "sus4": "1 4 5", "7sus4": "1 4 5 b7",
        "9sus4": "1 4 5 b7 9", "11": "1 4 5 b7 9", "69": "1 3 5 6 9",
        "6": "1 3 5 6"}
POOL = {"triad": ("1", "b3", "3", "4", "5"),
        "seventh": ("1", "b3", "3", "4", "5", "6", "b7", "7"),
        "all": tuple(IV)}


def spell(root, ivn):
    steps, semis = IV[ivn]
    li = LET.index(root[0]) + steps
    s2 = LET[li % 7]
    pc = (_STEP[root[0]] + _ACC[root[1:]] + semis) % 12
    d = (pc - _STEP[s2] + 6) % 12 - 6
    return s2 + {0: "", 1: "#", -1: "b"}[d]


def chord_tones(sym, pool="all", upper=False):
    """Chord tones and bass.  `upper`: a voice above the bass does not take
    the root of a major-seventh chord, which would sit a semitone above the
    seventh in the tune (A under B-flat in B-flat maj7)."""
    m = re.fullmatch(r"([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?", sym)
    root, q, bass = m.groups()
    ivs = QUAL[q].split()
    if upper and "7" in ivs:
        ivs = [x for x in ivs if x != "1"]
    tones = [spell(root, x) for x in ivs if x in POOL[pool]]
    return tones, bass or root


def cands(names, lo, hi):
    out = []
    for n in names:
        for o in range(0, 9):
            p = f"{n}{o}"
            if lo <= midi_of(p) <= hi:
                out.append((midi_of(p), p))
    return sorted(out)


def place(name, lo):
    return min(cands([name], lo, lo + 11))[1]


def segs(b):
    return CHART[b]


def sym_at(b, pos):
    t = 0
    for sym, d in CHART[b]:
        if t <= pos < t + d:
            return sym
        t += d
    raise ValueError((b, pos))


class Line:
    """A voice that moves to the nearest chord tone, pulled toward a
    home register (keeps common tones, avoids drifting)."""

    def __init__(self, target, lo, hi, pool="triad"):
        self.target, self.lo, self.hi, self.pool = \
            midi_of(target), midi_of(lo), midi_of(hi), pool
        self.prev = None

    def pick(self, sym):
        names, _ = chord_tones(sym, self.pool, upper=True)
        cs = cands(names, self.lo, self.hi)
        ref = self.prev if self.prev is not None else self.target
        m, p = min(cs, key=lambda x: (abs(x[0] - ref)
                                      + 0.35 * abs(x[0] - self.target), x[0]))
        self.prev = m
        return p


def _bar(items):
    """items: list of (pos, dur, pitch-string or None, flags) -> bar string."""
    out, t = [], 0
    for pos, d, p, fl in sorted(items, key=lambda x: x[0]):
        if pos > t:
            out.append(f"r/{pos - t}")
        out.append(f"{p}/{d}{fl}" if p else f"r/{d}")
        t = pos + d
    if t < BAR16:
        out.append(f"r/{BAR16 - t}")
    return " ".join(out)


def g_hold(b, lo, octave=False):
    """Bass (slash bass or root) held for each chord."""
    items, t = [], 0
    for sym, d in segs(b):
        p = place(chord_tones(sym)[1], midi_of(lo))
        if octave:
            p = p + "+" + shift(p, 12)
        items.append((t, d, p, ""))
        t += d
    return merge(_bar(items))


def g_pizz(b, lo, fl=""):
    """Bass on beats 1 and 3 (oom-pah)."""
    return _bar([(pos, 4, place(chord_tones(sym_at(b, pos))[1], midi_of(lo)),
                  fl) for pos in (0, 8)])


def g_q(b, lo, fl=""):
    return _bar([(pos, 4, place(chord_tones(sym_at(b, pos))[1], midi_of(lo)),
                  fl) for pos in (0, 4, 8, 12)])


def g_oct8(b, lo):
    items = []
    for pos in range(0, 16, 2):
        p = place(chord_tones(sym_at(b, pos))[1], midi_of(lo))
        items.append((pos, 2, p if pos % 4 == 0 else shift(p, 12), ""))
    return _bar(items)


def g_off(b, line, fl=""):
    """Off-beat chord tones on beats 2 and 4 (the 'pah')."""
    return _bar([(pos, 4, line.pick(sym_at(b, pos)), fl) for pos in (4, 12)])


def g_rep(b, line, d=2, fl=""):
    items, t = [], 0
    for sym, sd in segs(b):
        p = line.pick(sym)
        for k in range(sd // d):
            items.append((t + k * d, d, p, fl))
        t += sd
    return _bar(items)


def g_pad(b, line):
    items, t = [], 0
    for sym, sd in segs(b):
        items.append((t, sd, line.pick(sym), ""))
        t += sd
    return merge(_bar(items))


def g_arp(b, lo, d=2, shape="up", pool="triad", slur=False):
    """Broken chord for each chord of the bar, starting at the first chord
    tone at or above `lo`."""
    items, t = [], 0
    for sym, sd in segs(b):
        names, _ = chord_tones(sym, pool, upper=True)
        cs = [p for _, p in cands(names, midi_of(lo), midi_of(lo) + 30)]
        n = sd // d
        if shape == "up":
            seq = [cs[i % len(cs)] for i in range(n)]
        else:  # up and back down
            k = n // 2 + 1
            seq = cs[:k] + cs[1:k - 1][::-1]
            seq = seq[:n]
        for i, p in enumerate(seq):
            items.append((t + i * d, d, p, ""))
        t += sd
    s = _bar(items)
    if slur:  # one slur per chord
        lst, t, starts = toks(s), 0, set()
        acc = 0
        for sym, sd in segs(b):
            starts.add(acc)
            acc += sd
        pos = 0
        for i, x in enumerate(lst):
            if pos in starts:
                x["sl"] = True
                if i > 0:
                    lst[i - 1]["sr"] = True
            pos += x["dur"]
        lst[-1]["sr"] = True
        for x in lst:  # a one-note slur is meaningless
            if x["sl"] and x["sr"]:
                x["sl"] = x["sr"] = False
        s = untoks(lst)
    return s


def run_bars(bars, fn):
    return {b: fn(b) for b in bars}


# ---------------------------------------------------------------------------
# Harmony (chord per half bar unless noted)
# ---------------------------------------------------------------------------
H = lambda *x: [(s, 8) for s in x]
CHART = {
    # Prologue (Maestoso)
    1: H("Bbadd9", "F/A"), 2: H("G11", "Dm7"), 3: H("Bbmaj7", "Gm7"),
    4: [("Gm7", 8), ("A7sus4", 4), ("A7", 4)],
    # Intro (source m1-4, m13-17)
    5: H("Dm", "F/C"), 6: H("Am", "Dm"), 7: H("Bb", "Gm7"),
    8: [("C9sus4", 4), ("C", 4), ("F", 8)],
    9: H("Dm", "Bbadd9"), 10: H("F", "C"), 11: H("F", "Am"),
    12: H("Bbmaj7", "Dm"), 13: H("Gm7", "C9"),
    # Verse
    14: H("F", "Am7"), 15: H("A7", "Dm"), 16: H("Bb", "Gm7"),
    17: H("C7", "F"), 18: H("Dm", "Bbmaj7"), 19: H("F/A", "C"),
    20: H("F", "Am7"), 21: H("A7", "Dm"), 22: H("Bbmaj7", "F/A"),
    23: H("C", "Dm"), 24: H("Bb", "Gm7"), 25: H("C", "F"),
    26: H("Dm", "Dm/C"), 27: H("Bbmaj7", "C"), 28: H("F", "Am7"),
    29: H("Bbmaj7", "Dm"), 30: H("Gm7", "A7sus4"),
}
CHORUS_CHART = {
    1: H("Bbadd9", "F/A"), 2: H("G11", "Dm"), 3: H("Bbmaj7", "Gm7"),
    4: [("C9sus4", 4), ("C", 4), ("Fadd9", 8)],
    5: H("Dm", "Dm/C"), 6: H("G7/B", "C"), 7: H("Am7", "Dm7"),
    8: [("Gm7", 8), ("C9sus4", 4), ("C9", 4)],
    9: H("Bbadd9", "F/A"), 10: H("G11", "Dm"), 11: H("Bbmaj7", "Cadd9"),
    12: H("Am7", "Dm7"), 13: H("Bbmaj7", "Gm7"), 14: H("F/A", "C"),
    15: H("Bbadd9", "C"), 16: H("F", "Dm"), 17: H("Bbadd9", "C"),
}


def up2_sym(sym):
    m = re.fullmatch(r"([A-G][#b]?)([^/]*)(?:/([A-G][#b]?))?", sym)
    root, q, bass = m.groups()
    t = lambda n: tr_pitch(n + "4")[:-1]
    return t(root) + q + ("/" + t(bass) if bass else "")


for i in range(1, 18):
    CHART[30 + i] = CHORUS_CHART[i]
CHART.update({
    # Interlude (source m1-8) and the lift into G
    48: H("Dm", "F/C"), 49: H("Am", "Dm"), 50: H("Bb", "Gm7"),
    51: [("C9sus4", 4), ("C", 4), ("F", 8)],
    52: H("Dm", "Bbadd9"), 53: H("F", "C"), 54: H("F", "Dm7"),
    55: H("Bbadd9", "C"), 56: H("Am7", "Am7/G"),
    57: [("B7sus4", 8), ("B7", 8)],
})
for i in range(1, 17):
    CHART[57 + i] = [(up2_sym(s), d) for s, d in CHORUS_CHART[i]]
CHART.update({
    # Coda (G)
    74: H("Cmaj7", "Am7/C"), 75: H("Bm7", "Cmaj9"),
    76: [("G/D", 4), ("D", 8), ("D7", 4)],
    77: [("G69", 16)], 78: [("G69", 16)],
})
assert all(sum(d for _, d in CHART[b]) == 16 for b in range(1, NBARS + 1))

# ---------------------------------------------------------------------------
# The tune (jianpu 1=F: 1=F4 ... 6=D5, 6. below = D4)
# ---------------------------------------------------------------------------
# Instrumental intro of the jianpu (source bars 1-8 and 13-17)
THEME = {
    1: "D5/4 D5/3 C5/1 D5/2 A4/2 C5/4",
    2: "A4/3 C5/1 A4/2 E5/2 D5/8",
    3: "D5/4 F5/3 D5/1 G5/2 F5/2 F5/2 D5/2",
    4: "D5/3 C5/1 G4/2 C5/2 A4/8",
    5: "D5/3 D5/1 D5/2 C5/2 D5/2 D5/1 F5/1 D5/2 C5/2",
    6: "A4/2 A4/1 G4/1 F4/2 C5/1 A4/1 G4/8",
    7: "C5/3 A4/1 C5/2 A4/2 C5/2 C5/2 A4/2 F5/2",
    8: "D5/16",
    14: "A4/2 A4/1 C5/1 F4/2 C5/1 A4/1 G4/8",
    15: "C5/3 A4/1 C5/2 A4/2 C5/2 A4/2 C5/4",
    16: "C5/2 C5/2 A4/2 F5/2 D5/8~",
    17: "D5/8 D5/2 C5/2 D5/4",
}

# Verse (v1-v17 -> bars 14-30)
VMEL = {
    1: "A4/4=风 A4/4=吹 A4/2=麦 A4/6=浪",
    2: "A4/2=稻 G4/4=花 E4/2=儿 D4/8=香",
    3: "F4/2=黑 D4/2=土 F4/4=地 D4/2=养 F4/4=育 D4/2=着",
    4: "C5/4=咱 G4/2=的 C5/2=爹 A4/8=娘",
    5: "A4/2=每 D5/4=年 C5/2=的 D5/2=冬 D5/4=天 A4/2=都",
    6: "A4/4=大 F4/2=雪 A4/2=飞 G4/8=扬",
    7: "C5/4=热 C5/2=热 A4/2=的 C5/2=炕 A4/4=头 C5/2=上",
    8: "A4/4=唠 G4/2=唠 E4/2=家 D4/8=常",
    9: "A4/4=蓝 A4/3=蓝 G4/1=的 A4/2=天 A4/6=上",
    10: "G4/2=白 G4/4=云 E4/2=飘 D4/8=荡",
    11: "F4/4=清 F4/3=澈 F4/1=的 D4/2=小 F4/4=河 D4/2=在",
    12: "C5/4=潺 G4/2=潺 C5/2=流 A4/8=淌",
    13: "D5/2=东 A4/2=北 D5/4=人 D5/2=爱 C5/4=吃 A4/2=那",
    14: "A4/4=酸 A4/2=菜 F4/2=血 G4/8=肠",
    15: "C5/4=秧 C5/4=歌 C5/2=扭 A4/2=起 C5/4=来",
    16: "C5/2=人 C5/2=们 A4/2=喜 F5/2=洋 D5/8~=洋",
    17: "D5/14 r/2",
}

# ---------------------------------------------------------------------------
# Choir (SATB).  Chorus in F; the last chorus is the same voicing up a tone.
# ---------------------------------------------------------------------------
CS = {
    1: "D5/4=大 D5/4=东 (A4/2=北 C5/4) C5/2=是",
    2: "A4/4=我 C5/2=的 F5/2=家 D5/8=乡",
    3: "D5/4=唢 F5/4=呐 G5/2=吹 F5/4=出 D5/2=了",
    4: "D5/2=美 C5/2=美 G4/2=的 C5/2=模 A4/8=样",
    5: "D5/4=哥 D5/4=们 D5/2=相 D5/6=聚",
    6: "A4/2=必 A4/2=须 F4/2=整 A4/2=二 G4/8=两",
    7: "C5/3=醉 A4/1=了 C5/3=月 A4/1=亮 C5/2=暖 C5/2=了 A4/2=我 F5/2=心",
    8: "D5/14=肠 r/2",
    10: "A4/2=我 C5/4=的 F5/2=家 D5/8=乡",
    11: "D5/2=我 F5/4=就 D5/2=在 G5/2=这 D5/4=嘎 C5/2=达",
    12: "G4/2=土 A4/2=生 (C5/2=土 D5/1 C5/1) A4/8=长",
    13: "D5/2=东 A4/2=北 D5/2=人 D5/2=的 D5/8=情",
    14: "A4/2=东 G4/2=北 A4/2=人 F4/2=的 G4/8=爱",
    15: "C5/2=贼 C5/2=拉 C5/2=拉 C5/2=的 C5/2=爱 A4/4=你 C5/2=呀",
    16: "A4/2=我 C5/4=的 F5/2=家 D5/8~=乡",
    17: "D5/14 r/2",
}
CA = {
    1: "F4/4=大 F4/4=东 F4/6=北 F4/2=是",
    2: "F4/4=我 F4/2=的 A4/2=家 F4/8=乡",
    3: "F4/4=唢 A4/4=呐 Bb4/2=吹 Bb4/4=出 Bb4/2=了",
    4: "F4/2=美 F4/2=美 E4/2=的 E4/2=模 F4/8=样",
    5: "F4/4=哥 F4/4=们 F4/2=相 F4/6=聚",
    6: "F4/2=必 F4/2=须 F4/2=整 F4/2=二 E4/8=两",
    7: "E4/3=醉 E4/1=了 E4/3=月 E4/1=亮 F4/2=暖 F4/2=了 F4/2=我 A4/2=心",
    8: "(F4/12=肠 E4/2) r/2",
    10: "F4/2=我 F4/4=的 A4/2=家 F4/8=乡",
    11: "F4/2=我 A4/4=就 F4/2=在 E4/2=这 E4/4=嘎 E4/2=达",
    12: "E4/2=土 E4/2=生 E4/4=土 F4/8=长",
    13: "F4/2=东 F4/2=北 F4/2=人 F4/2=的 Bb4/8=情",
    14: "F4/2=东 F4/2=北 F4/2=人 C4/2=的 E4/8=爱",
    15: "F4/2=贼 F4/2=拉 F4/2=拉 F4/2=的 E4/2=爱 E4/4=你 E4/2=呀",
    16: "F4/2=我 F4/4=的 A4/2=家 (F4/8~=乡",
    17: "F4/8 E4/6) r/2",
}
CT = {
    1: "D4/4=大 D4/4=东 C4/6=北 C4/2=是",
    2: "C4/4=我 C4/2=的 C4/2=家 A3/8=乡",
    3: "D4/4=唢 D4/4=呐 D4/2=吹 D4/4=出 D4/2=了",
    4: "Bb3/2=美 Bb3/2=美 C4/2=的 C4/2=模 C4/8=样",
    5: "A3/4=哥 A3/4=们 A3/2=相 A3/6=聚",
    6: "G3/2=必 G3/2=须 G3/2=整 G3/2=二 G3/8=两",
    7: "G3/3=醉 G3/1=了 G3/3=月 G3/1=亮 A3/2=暖 A3/2=了 A3/2=我 A3/2=心",
    8: "Bb3/14=肠 r/2",
    10: "C4/2=我 C4/4=的 C4/2=家 A3/8=乡",
    11: "D4/2=我 D4/4=就 D4/2=在 C4/2=这 C4/4=嘎 C4/2=达",
    12: "C4/2=土 C4/2=生 C4/4=土 C4/8=长",
    13: "D4/2=东 D4/2=北 D4/2=人 D4/2=的 D4/8=情",
    14: "C4/2=东 C4/2=北 C4/2=人 A3/2=的 G3/8=爱",
    15: "D4/2=贼 D4/2=拉 D4/2=拉 D4/2=的 C4/2=爱 C4/4=你 C4/2=呀",
    16: "C4/2=我 C4/4=的 C4/2=家 (A3/8=乡",
    17: "Bb3/8 G3/6) r/2",
}
CB = {
    1: "Bb2/4=大 Bb2/4=东 A2/6=北 A2/2=是",
    2: "G2/4=我 G2/2=的 G2/2=家 D3/8=乡",
    3: "Bb2/4=唢 Bb2/4=呐 G2/2=吹 G2/4=出 G2/2=了",
    4: "C3/2=美 C3/2=美 C3/2=的 C3/2=模 F2/8=样",
    5: "D3/4=哥 D3/4=们 C3/2=相 C3/6=聚",
    6: "B2/2=必 B2/2=须 B2/2=整 B2/2=二 C3/8=两",
    7: "A2/3=醉 A2/1=了 A2/3=月 A2/1=亮 D3/2=暖 D3/2=了 D3/2=我 D3/2=心",
    8: "(G2/8=肠 C3/6) r/2",
    10: "G2/2=我 G2/4=的 G2/2=家 D3/8=乡",
    11: "Bb2/2=我 Bb2/4=就 Bb2/2=在 C3/2=这 C3/4=嘎 C3/2=达",
    12: "A2/2=土 A2/2=生 A2/4=土 D3/8=长",
    13: "Bb2/2=东 Bb2/2=北 Bb2/2=人 Bb2/2=的 G2/8=情",
    14: "A2/2=东 A2/2=北 A2/2=人 A2/2=的 C3/8=爱",
    15: "Bb2/2=贼 Bb2/2=拉 Bb2/2=拉 Bb2/2=的 C3/2=爱 C3/4=你 C3/2=呀",
    16: "F2/2=我 F2/4=的 F2/2=家 (D3/8=乡",
    17: "Bb2/8 C3/6) r/2",
}
for d in (CS, CA, CT, CB):
    d[9] = d[1]
# last chorus: c16 ends the phrase (no tie into c17)
C16_END = {"s": "A4/2=我 C5/4=的 F5/2=家 D5/8=乡",
           "a": "F4/2=我 F4/4=的 A4/2=家 F4/8=乡",
           "t": "C4/2=我 C4/4=的 C4/2=家 A3/8=乡",
           "b": "F2/2=我 F2/4=的 F2/2=家 D3/8=乡"}


def blank():
    return {b: REST for b in range(1, NBARS + 1)}


SOP, ALT, TEN, BAS = blank(), blank(), blank(), blank()

# Prologue: "啊" from bar 3, A7 fermata
SOP.update({3: "(D5/16=啊", 4: "D5/12 C#5/4)"})
ALT.update({3: "(A4/8=啊 Bb4/8", 4: "Bb4/8 A4/4 G4/4)"})
TEN.update({3: "(F4/16=啊", 4: "F4/8 E4/8)"})
BAS.update({3: "(Bb2/8=啊 G2/8", 4: "G2/8 A2/8)"})

# Verse: women in unison, then two parts
for i in range(1, 9):
    SOP[13 + i] = VMEL[i]
    ALT[13 + i] = VMEL[i]
ALT.update({
    18: "F4/2=每 A4/4=年 A4/2=的 Bb4/2=冬 Bb4/4=天 F4/2=都",
    19: "F4/4=大 C4/2=雪 F4/2=飞 E4/8=扬",
    20: "A4/4=热 A4/2=热 F4/2=的 A4/2=炕 E4/4=头 A4/2=上",
    21: "E4/4=唠 E4/2=唠 C#4/2=家 A3/8=常",
})
# men sing "蓝蓝的天上" in thirds; women hold a "啊" halo above
SOP.update({22: "(F5/16=啊", 23: "G5/8 F5/8)", 24: "(F5/16=啊",
            25: "E5/8 C5/8)"})
ALT.update({22: "(D5/8=啊 C5/8", 23: "C5/8 D5/8)", 24: "(Bb4/16=啊",
            25: "G4/8 A4/8)"})
for i in range(9, 13):
    TEN[13 + i] = octv(VMEL[i], -1)
BAS.update({
    22: "F3/4=蓝 F3/3=蓝 E3/1=的 F3/2=天 F3/6=上",
    23: "E3/2=白 E3/4=云 C3/2=飘 F2/8=荡",
    24: "D3/4=清 D3/3=澈 D3/1=的 Bb2/2=小 D3/4=河 Bb2/2=在",
    25: "E3/4=潺 E3/2=潺 E3/2=流 F3/8=淌",
})
# tutti
for i in range(13, 18):
    SOP[13 + i] = VMEL[i]
ALT.update({
    26: "F4/2=东 F4/2=北 F4/4=人 F4/2=爱 F4/4=吃 F4/2=那",
    27: "F4/4=酸 F4/2=菜 D4/2=血 E4/8=肠",
    28: "A4/4=秧 A4/4=歌 A4/2=扭 E4/2=起 G4/4=来",
    29: "F4/2=人 F4/2=们 F4/2=喜 A4/2=洋 (A4/8~=洋",
    30: "A4/8 G4/6) r/2",
})
TEN.update({
    26: "A3/2=东 A3/2=北 A3/4=人 A3/2=爱 A3/4=吃 A3/2=那",
    27: "D4/4=酸 D4/2=菜 D4/2=血 G3/8=肠",
    28: "A3/4=秧 A3/4=歌 A3/2=扭 A3/2=起 A3/4=来",
    29: "D4/2=人 D4/2=们 D4/2=喜 D4/2=洋 (F4/8~=洋",
    30: "F4/8 E4/6) r/2",
})
BAS.update({
    26: "D3/2=东 D3/2=北 D3/4=人 C3/2=爱 C3/4=吃 C3/2=那",
    27: "Bb2/4=酸 Bb2/2=菜 D3/2=血 C3/8=肠",
    28: "F2/4=秧 F2/4=歌 A2/2=扭 A2/2=起 A2/4=来",
    29: "Bb2/2=人 Bb2/2=们 Bb2/2=喜 Bb2/2=洋 (D3/8=洋",
    30: "G2/8 A2/6) r/2",
})
# Chorus I (F) and Chorus II (G)
for i in range(1, 18):
    SOP[30 + i], ALT[30 + i], TEN[30 + i], BAS[30 + i] = \
        CS[i], CA[i], CT[i], CB[i]
for i in range(1, 17):
    s, a, t, bb = CS[i], CA[i], CT[i], CB[i]
    if i == 16:
        s, a, t, bb = C16_END["s"], C16_END["a"], C16_END["t"], C16_END["b"]
    SOP[57 + i], ALT[57 + i], TEN[57 + i], BAS[57 + i] = \
        up2(s), up2(a), up2(t), up2(bb)
# Interlude "啊" and the lift (general pause on m57 beat 4)
SOP.update({54: "(C5/16=啊", 55: "D5/8 E5/8)", 56: "(E5/16=啊",
            57: "E5/8 D#5/4) r/4"})
ALT.update({54: "(A4/16=啊", 55: "Bb4/8 G4/8)", 56: "(G4/8=啊 A4/8",
            57: "A4/12) r/4"})
TEN.update({54: "(F4/16=啊", 55: "F4/8 E4/8)", 56: "(C4/16=啊",
            57: "B3/12) r/4"})
BAS.update({54: "(F3/8=啊 D3/8", 55: "Bb2/8 C3/8)", 56: "(A2/8=啊 G2/8",
            57: "B2/12) r/4"})
# Coda (G): subito p, allargando to the high A, G6/9
SOP.update({
    74: "B4/2=我 D5/4=的 G5/2=家 E5/8=乡",
    75: "D5/2=贼 D5/2=拉 D5/2=拉 D5/2=的 D5/2=爱 B4/4=你 D5/2=呀",
    76: "B4/4=我 D5/8=的 (A5/2=家 F#5/2)",
    77: "E5/16~=乡", 78: "E5/16",
})
ALT.update({
    74: "G4/2=我 G4/4=的 B4/2=家 C5/8=乡",
    75: "A4/2=贼 A4/2=拉 A4/2=拉 A4/2=的 B4/2=爱 G4/4=你 B4/2=呀",
    76: "G4/4=我 A4/8=的 C5/4=家",
    77: "B4/16~=乡", 78: "B4/16",
})
TEN.update({
    74: "E4/2=我 E4/4=的 E4/2=家 A3/8=乡",
    75: "D4/2=贼 D4/2=拉 D4/2=拉 D4/2=的 G3/2=爱 G3/4=你 G3/2=呀",
    76: "D4/4=我 F#4/8=的 F#4/4=家",
    77: "D4/16~=乡", 78: "D4/16",
})
BAS.update({
    74: "C3/2=我 C3/4=的 C3/2=家 C3/8=乡",
    75: "B2/2=贼 B2/2=拉 B2/2=拉 B2/2=的 C3/2=爱 C3/4=你 C3/2=呀",
    76: "D3/4=我 D3/8=的 D3/4=家",
    77: "G2/16~=乡", 78: "G2/16",
})



def tie_held(part):
    """A sung note continued (no new syllable) on the same pitch after the
    barline is one held note: tie it."""
    for b in range(1, NBARS):
        a, c = toks(part[b]), toks(part[b + 1])
        if a and c and a[-1]["pit"] and a[-1]["pit"] == c[0]["pit"] \
                and not c[0]["lyr"] and not a[-1]["tie"]:
            a[-1]["tie"] = True
            part[b] = untoks(a)


for _p in (SOP, ALT, TEN, BAS):
    tie_held(_p)

# Melody guide (the tune with its words, original octave) for SRT / guide MIDI
MEL = blank()
for i in range(1, 18):
    MEL[13 + i] = VMEL[i]
for b in range(31, 48):
    MEL[b] = SOP[b]
for b in range(58, 79):
    MEL[b] = SOP[b]

# ---------------------------------------------------------------------------
# Orchestra
# ---------------------------------------------------------------------------
PRO, INTRO = range(1, 5), range(5, 14)
VA, VB, VC = range(14, 22), range(22, 26), range(26, 31)
CH1, IL, MOD = range(31, 48), range(48, 56), range(56, 58)
CH2, CODA = range(58, 74), range(74, 79)


def c1(i):  # bar of chorus I line i
    return 30 + i


def c2(i):  # bar of chorus II line i
    return 57 + i


def mel8(b):
    """The sung tune an octave up, as an instrumental line."""
    return octv(strip(MEL[b]), 1)


def colla(src, bars, n=0, fn=merge):
    return {b: octv(fn(src[b]), n) for b in bars}


PICC, FL, OB, CL, BSN = blank(), blank(), blank(), blank(), blank()
HN1, HN2, TPT, TBN, TBA = blank(), blank(), blank(), blank(), blank()
TIMP, GLK, HPR, HPL = blank(), blank(), blank(), blank()
VN1, VN2, VLA, VC_, CBS = blank(), blank(), blank(), blank(), blank()

# ---- Prologue ------------------------------------------------------------
FL.update({1: "r/8 (A5/2 C6/2 F6/4)", 2: "r/8 (F6/1 E6/1 D6/1 C6/1 A5/2 C6/2)",
           3: "D6/16", 4: "D6/12 C#6/4"})
CL.update({3: "A4/8 Bb4/8", 4: "Bb4/8 A4/4 G4/4"})
BSN.update({3: "Bb2/8 G2/8", 4: "G2/8 A2/8"})
for b in PRO:
    HN1[b] = octv(strip(CS[b]), -1)
HN2.update({3: "Bb3/4 D4/4 D4/2 D4/4 Bb3/2", 4: "Bb3/4 G3/4 E3/8"})
TBN.update({4: "D3/8 E3/8"})
TBA.update({4: "G1/8 A1/8"})
TIMP.update({4: "r/8 A2/8%"})
GLK.update({1: "r/8 A6/2 C7/2 F7/4"})
HPR.update({1: g_arp(1, "D4", 1, "updown"), 2: g_arp(2, "D4", 1, "updown"),
            3: g_arp(3, "F4", 1, "updown"),
            4: "Bb4+D5+F5/8 r/4 C#5+E5+G5+A5/4"})
HPL.update({1: "Bb1+Bb2/8 A1+A2/8", 2: "G1+G2/8 D2+D3/8",
            3: "Bb1+Bb2/8 G1+G2/8", 4: "G1+G2/8 r/4 A1+A2/4"})
VN1.update({1: "C6/16%", 2: "D6/8% A5/8%", 3: "A5/8% Bb5/8%", 4: "A5/16%"})
VN2.update({1: "F5/16%", 2: "F5/16%", 3: "F5/16%", 4: "F5/8% E5/8%"})
VLA.update({1: "D4/8 C4/8", 2: "D4/16", 3: "D4/16", 4: "D4/12 C#4/4"})
VC_.update({1: "Bb2/8 A2/8", 2: "G2/8 D3/8", 3: "Bb2/8 G2/8", 4: "G2/8 A2/8"})
CBS.update({1: "Bb1/8 A1/8", 2: "G1/8 D2/8", 3: "Bb1/8 G1/8", 4: "G1/8 A1/8"})

# ---- Intro: oboe + flute (8va) over pizzicato; violins take the answer ------
for i, b in enumerate(range(5, 9), 1):
    OB[b] = THEME[i]
    FL[b] = octv(THEME[i], 1)
for i, b in zip((5, 14, 15, 16, 17), range(9, 14)):
    VN1[b] = THEME[i]
    CL[b] = octv(THEME[i], -1)
GLK[7] = octv(THEME[3], 1)
FL.update({12: "r/8 (A5/1 Bb5/1 C6/1 D6/1 F6/4)",
           13: "(G6/4 F6/2 D6/2 E6/2 D6/2 C6/2 Bb5/2)"})
TIMP.update({5: "D3/4 r/12", 8: "r/8 F2/4 r/4"})
_vn2, _va = Line("A4", "E4", "C5"), Line("D4", "A3", "F4")
for b in list(INTRO) + list(VA):
    VN2[b] = g_off(b, _vn2)
    VLA[b] = g_off(b, _va)
    VC_[b] = g_pizz(b, "F2")
    CBS[b] = g_pizz(b, "F1")
for b in range(5, 9):
    CL[b] = g_arp(b, "A3", 2, "up")
for b in INTRO:
    BSN[b] = g_pizz(b, "F2", ".")
_h1, _h2 = Line("D4", "G3", "G4"), Line("A3", "D3", "D4")
for b in range(9, 14):
    HN1[b] = g_pad(b, _h1)
    HN2[b] = g_pad(b, _h2)
    HPR[b] = g_arp(b, "F3", 2, "up")
    HPL[b] = g_hold(b, "F1", octave=True)

# ---- Verse a (women): pizzicato village, woodwind answers ----------------
FL.update({15: "r/8 (F5/1 G5/1 A5/2 C6/2 D6/2)",
           21: "r/8 (D6/2 C6/2 A5/2 F5/2)"})
OB.update({17: "r/8 g:D6 (C6/2 A5/2 G5/2 A5/2)"})
CL.update({19: "r/8 (E5/1 F5/1 G5/2 E5/2 C5/2)",
           21: "r/8 (F5/2 E5/2 C5/2 A4/2)"})
for b in range(18, 22):
    BSN[b] = g_pizz(b, "F2", ".")
    HN1[b] = merge(ALT[b])
    HPR[b] = g_arp(b, "F3", 2, "up")
    HPL[b] = g_hold(b, "F1", octave=True)

# ---- Verse b (men, "蓝蓝的天上"): legato strings, harp water --------------
for b in VB:
    VN1[b] = octv(strip(SOP[b]), 1)
    VN2[b] = strip(ALT[b])
    VLA[b] = strip(TEN[b], slurs=False)
    VC_[b] = g_hold(b, "F2")
    CBS[b] = g_hold(b, "F1")
    BSN[b] = strip(BAS[b], slurs=False)
    HPL[b] = g_hold(b, "F1", octave=True)
HPR.update({22: g_arp(22, "F4", 2, "updown"), 23: g_arp(23, "F4", 2, "updown"),
            24: g_arp(24, "F4", 1, "updown"),
            25: "(C5/1 E5/1 G5/1 C6/1 G5/1 E5/1 C5/1 G4/1) "
                "(A4/1 C5/1 F5/1 A5/1 C6/1 A5/1 F5/1 C5/1)"})
FL.update({23: "r/8 (A5/2 D6/2 C6/2 A5/2)",
           25: "r/8 (C6/1 A5/1 F5/1 A5/1 C6/1 A5/1 F5/1 C5/1)"})
GLK.update({25: "r/8 C7/2 A6/2 F6/4"})

# ---- Verse c (tutti build) -----------------------------------------------
for b in range(26, 30):
    FL[b] = octv(strip(SOP[b]), 1)
    OB[b] = strip(SOP[b])
    VN1[b] = octv(strip(SOP[b]), 1)
FL[30], OB[30] = "D6/14 r/2", "D5/14 r/2"
VN1[30] = "D6/8 (A4/1 Bb4/1 C5/1 D5/1 E5/1 F5/1 G5/1 A5/1)"
_vn2, _va = Line("A4", "F4", "D5"), Line("D4", "A3", "F4")
for b in VC:
    CL[b] = merge(ALT[b])
    BSN[b] = merge(BAS[b])
    HN1[b] = merge(ALT[b])
    HN2[b] = merge(TEN[b])
    VN2[b] = g_rep(b, _vn2, 2)
    VLA[b] = g_arp(b, "D3", 2, "up")
    VC_[b] = g_q(b, "F2")
    CBS[b] = g_hold(b, "F1")
for b in range(26, 30):
    HPR[b] = g_arp(b, "D4", 2, "up")
    HPL[b] = g_hold(b, "F1", octave=True)
HPR[30] = "D4+G4/8 (A4/1 D5/1 E5/1 G5/1 A5/1 D6/1 E6/1 G6/1)"
HPL[30] = "G1+G2/8 A1+A2/8"
TBN.update({28: "F2/8 A2/8", 29: "Bb2/8 D3/8", 30: "G2/8 A2/6 r/2"})
TBA.update({29: "Bb1/8 D2/8", 30: "G1/8 A1/6 r/2"})
TPT.update({30: "r/8 A4/2 D5/2 E5/2 G5/2"})
TIMP.update({29: "r/8 D3/8%~", 30: "D3/8% A2/6% r/2"})
for p in (CL, BSN, HN1, HN2, TBN):
    auto_tie(p, range(26, 30))

# ---- Chorus I --------------------------------------------------------------
VN1_COUNTER = {
    1: "D6/8 C6/8",
    2: "C6/8 (A5/2 C6/2 D6/2 F6/2)",
    3: "F6/8 D6/8",
    4: "D6/4 E6/4 (F6/2 E6/2 D6/2 C6/2)",
    5: "A5/16",
    6: "B5/8 (C6/2 E6/2 G6/2 E6/2)",
    7: "E6/8 D6/8",
    8: "D6/8 C6/8",
}
HN_COUNTER = {
    9: "D4/8 C4/8",
    10: "Bb3/8 (A3/2 C4/2 D4/2 F4/2)",
    11: "F4/8 D4/8",
    12: "C4/4 E4/4 F4/4 (D4/2 C4/2)",
    13: "F4/8 D4/8",
    14: "C4/8 (C4/2 E4/2 G4/2 E4/2)",
    15: "D4/8 E4/8",
    16: "C4/8 D4/8",
    17: "D4/8 E4/6 r/2",
}
_vn2, _cl = Line("A4", "F4", "D5"), None
for i in range(1, 18):
    b = c1(i)
    FL[b] = mel8(b)
    OB[b] = strip(SOP[b])
    CL[b] = g_arp(b, "Bb3", 2, "up")
    BSN[b] = g_hold(b, "F2")
    TBN[b] = merge(TEN[b])
    VN2[b] = g_rep(b, _vn2, 2)
    VLA[b] = g_arp(b, "D3", 2, "up")
    VC_[b] = g_hold(b, "F2") if i < 9 or i == 17 else g_oct8(b, "F2")
    CBS[b] = g_hold(b, "F1")
    HPR[b] = g_arp(b, "F4", 2, "up")
    HPL[b] = g_hold(b, "F1", octave=True)
    if i <= 8:
        VN1[b] = FL[b] = VN1_COUNTER[i]
        CL[b] = merge(ALT[b])
        HN1[b] = merge(ALT[b])
        HN2[b] = merge(TEN[b])
    else:
        VN1[b] = mel8(b)
        PICC[b] = mel8(b)
        HN1[b] = HN2[b] = HN_COUNTER[i]
        TBA[b] = g_hold(b, "F1")
OB[c1(4)] = "D5/2 C5/2 G4/2 C5/2 r/2 g:D6 (C6/2 A5/1 G5/1 A5/2)"
OB[c1(12)] = "G4/2 A4/2 (C5/2 D5/1 C5/1) r/2 g:E6 (D6/2 C6/1 A5/1 C6/2)"
FL[c1(17)] = VN1[c1(17)] = "D6/8 E6/8"
PICC[c1(17)] = REST
TPT.update({c1(8): "r/4 G4/2 Bb4/2 D5/4 C5/4",
            c1(14): "r/8 C5/2 E5/2 G5/4",
            c1(16): "r/8 A4/2 D5/2 F5/4",
            c1(17): "F5/8 E5/6 r/2"})
for i in (3, 7, 11, 15):
    GLK[c1(i)] = mel8(c1(i))
TIMP.update({
    c1(1): "r/8 A2/4 r/4", c1(2): "r/8 D3/4 r/4", c1(4): "C3/4 C3/4 F2/4 r/4",
    c1(5): "D3/4 r/12", c1(8): "r/8 C3/6% r/2", c1(9): "r/8 A2/4 r/4",
    c1(10): "r/8 D3/4 r/4", c1(11): "r/8 C3/4 r/4", c1(12): "A2/4 r/4 D3/4 r/4",
    c1(14): "A2/4 r/4 C3/4 r/4", c1(15): "r/8 C3/4 r/4",
    c1(16): "A2/4 r/4 D3/4 r/4", c1(17): "r/8 C3/8%",
})
for p in (HN1, HN2, TBN, BSN, CBS, TBA, CL):
    auto_tie(p, range(31, 47))

# ---- Interlude: brass fanfare on the intro theme -------------------------
for i, b in enumerate(range(48, 52), 1):
    TPT[b] = THEME[i]
    OB[b] = THEME[i]
    HN1[b] = HN2[b] = octv(THEME[i], -1)
for i, b in zip(range(5, 9), range(52, 56)):
    VN1[b] = octv(THEME[i], 1)
    FL[b] = octv(THEME[i], 1)
    PICC[b] = octv(THEME[i], 1)
GLK[50] = octv(THEME[3], 1)
GLK[54] = octv(THEME[7], 1)
_vn2, _va, _tb = Line("A4", "F4", "D5"), Line("D4", "A3", "F4"), \
    Line("D3", "A2", "A3")
_h1, _h2 = Line("D4", "A3", "F4"), Line("A3", "E3", "C4")
for b in IL:
    TBN[b] = g_pad(b, _tb)
    TBA[b] = g_hold(b, "F1")
    BSN[b] = g_q(b, "F2")
    VC_[b] = g_q(b, "F2")
    CBS[b] = g_hold(b, "F1")
    HPL[b] = g_hold(b, "F1", octave=True)
    VN2[b] = g_rep(b, _vn2, 2)
    if b < 52:
        VN1[b] = g_arp(b, "A4", 1, "updown")
        FL[b] = g_arp(b, "F5", 1, "updown")
        CL[b] = g_arp(b, "F4", 2, "up")
        VLA[b] = g_rep(b, _va, 2)
        HPR[b] = g_arp(b, "D4", 2, "up")
    else:
        CL[b] = g_arp(b, "A3", 2, "up")
        VLA[b] = g_arp(b, "D3", 2, "up")
        HPR[b] = g_arp(b, "F4", 2, "up")
        HN1[b] = g_pad(b, _h1)
        HN2[b] = g_pad(b, _h2)
TIMP.update({48: "D3/4 r/4 C3/4 r/4", 49: "A2/4 r/4 D3/4 r/4",
             51: "C3/4 C3/4 F2/4 r/4"})
for p in (TBN, HN1, HN2, TBA, CBS):
    auto_tie(p, range(52, 55))

# ---- Lift into G: Am7 -> B7, general pause on beat 4 ---------------------
PICC.update({57: "r/12 (A5/1 B5/1 C6/1 D#6/1)"})
FL.update({56: "E6/16t", 57: "E6/8 D#6/4 (A5/1 B5/1 C6/1 D#6/1)"})
OB.update({56: "E5/16", 57: "E5/8 D#5/4 r/4"})
CL.update({56: "G4/8 A4/8", 57: "A4/12 r/4"})
BSN.update({56: "A2/8 G2/8", 57: "B2/12 r/4"})
HN1.update({56: "G4/8 A4/8", 57: "A4/12 r/4"})
HN2.update({56: "C4/16", 57: "B3/12 r/4"})
TPT.update({56: "E5/16", 57: "E5/8 D#5/4 r/4"})
TBN.update({56: "E3/16", 57: "F#3/12 r/4"})
TBA.update({56: "A1/8 G1/8", 57: "B1/12 r/4"})
TIMP.update({56: "r/8 E3/8%", 57: "B2/12% r/4"})
HPR.update({56: g_arp(56, "E4", 2, "up"),
            57: "B3+E4+A4/8 B3+D#4+A4/4 (D#5/1 F#5/1 A5/1 B5/1)"})
HPL.update({56: "A1+A2/8 G1+G2/8", 57: "B1+B2/12 r/4"})
VN1.update({56: "E6/16%", 57: "E6/8% D#6/4% r/4"})
VN2.update({56: "C5/16%", 57: "B4/8% A4/4% r/4"})
VLA.update({56: "E4/16%", 57: "E4/8% D#4/4% r/4"})
VC_.update({56: "A2/8 G2/8", 57: "B2/12 r/4"})
CBS.update({56: "A1/8 G1/8", 57: "B1/12 r/4"})
for p in (CL, HN1, OB, TPT):
    auto_tie(p, (56,))

# ---- Chorus II (G) -------------------------------------------------------
HN_COUNTER2 = {
    1: "E4/8 D4/8", 2: "C4/8 (B3/2 D4/2 E4/2 G4/2)", 3: "G4/8 E4/8",
    4: "E4/4 F#4/4 G4/4 (E4/2 D4/2)", 5: "B3/16",
    6: "C#4/8 (D4/2 F#4/2 A4/2 F#4/2)", 7: "F#4/8 E4/8", 8: "E4/8 D4/8",
    9: "E4/8 D4/8", 10: "C4/8 (B3/2 D4/2 E4/2 G4/2)", 11: "G4/8 E4/8",
    12: "D4/4 F#4/4 G4/4 (E4/2 D4/2)", 13: "G4/8 E4/8",
    14: "D4/8 (D4/2 F#4/2 A4/2 F#4/2)", 15: "E4/8 F#4/8", 16: "D4/8 E4/6 r/2",
}
_va = Line("E4", "B3", "G4")
for i in range(1, 17):
    b = c2(i)
    PICC[b] = FL[b] = VN1[b] = mel8(b)
    OB[b] = VN2[b] = strip(SOP[b])
    CL[b] = g_arp(b, "C4", 2, "up")
    BSN[b] = g_hold(b, "G2")
    HN1[b] = HN2[b] = HN_COUNTER2[i]
    TBN[b] = merge(TEN[b])
    TBA[b] = g_hold(b, "G1")
    VLA[b] = g_rep(b, _va, 2)
    VC_[b] = g_oct8(b, "E2")
    CBS[b] = g_hold(b, "E1")
    HPR[b] = g_arp(b, "G4", 2 if i <= 8 else 1, "up" if i <= 8 else "updown")
    HPL[b] = g_hold(b, "E1", octave=True)
    if i >= 9:
        TPT[b] = strip(SOP[b])
OB[c2(4)] = "E5/2 D5/2 A4/2 D5/2 r/2 g:E6 (D6/2 B5/1 A5/1 B5/2)"
TPT.update({c2(2): "r/8 B4/2 E5/2 G5/4", c2(4): "r/8 B4/2 D5/2 G5/4",
            c2(6): "r/8 D5/2 F#5/2 A5/4", c2(8): "r/4 A4/2 C5/2 E5/4 D5/4"})
for i in (3, 7, 11, 13, 14, 15, 16):
    GLK[c2(i)] = mel8(c2(i))
TIMP.update({
    c2(1): "r/8 B2/4 r/4", c2(2): "r/8 E3/4 r/4", c2(4): "D3/4 D3/4 G2/4 r/4",
    c2(5): "E3/4 r/12", c2(8): "r/8 D3/6% r/2", c2(9): "r/8 B2/4 r/4",
    c2(10): "r/8 E3/4 r/4", c2(11): "r/8 D3/4 r/4", c2(12): "B2/4 r/4 E3/4 r/4",
    c2(14): "B2/4 r/4 D3/4 r/4", c2(15): "r/8 D3/4 r/4",
    c2(16): "B2/4 r/4 E3/4 r/4",
})
for p in (TBN, BSN, CBS, TBA):
    auto_tie(p, range(58, 73))

# ---- Coda (G) -------------------------------------------------------------
VN1.update({74: "(B5/2 D6/4 G6/2 E6/8)", 75: "(D6/10 B5/4 D6/2)",
            76: "B5/4 D6/8 (A6/2 F#6/2)", 77: "E6/16%~", 78: "E6/16%"})
for b in (74, 75, 76):
    VN2[b] = merge(ALT[b])
    VLA[b] = merge(TEN[b])
VN2.update({77: "B4/16~", 78: "B4/16"})
VLA.update({77: "D4/16~", 78: "D4/16"})
VC_.update({74: "C3/16", 75: "B2/8 C3/8", 76: "D3/16", 77: "G2/16~",
            78: "G2/16"})
CBS.update({74: "C2/16", 75: "B1/8 C2/8", 76: "D2/16", 77: "G1/16~",
            78: "G1/16"})
HPR.update({74: g_arp(74, "G3", 2, "up"), 75: g_arp(75, "G3", 2, "up"),
            76: "B3+D4+G4/4 D4+F#4+A4/8 C4+D4+F#4+A4/4",
            77: "(G3/1 A3/1 B3/1 D4/1 E4/1 G4/1 A4/1 B4/1) "
                "(D5/1 E5/1 G5/1 A5/1 B5/1 D6/1 E6/1 G6/1)",
            78: "G3+B3+D4+E4+A4+B4+D5+E5+G5/16"})
HPL.update({74: "C2+C3/16", 75: "B1+B2/8 C2+C3/8", 76: "D2+D3/16",
            77: "G1+G2/16~", 78: "G1+D2+G2/16"})
FL.update({75: "D6/16", 76: "B5/4 D6/8 (A6/2 F#6/2)", 77: "E6/16~",
           78: "E6/16"})
PICC.update({76: "B5/4 D6/8 (A6/2 F#6/2)", 77: "E6/16~", 78: "E6/16"})
OB.update({75: merge(SOP[75]), 76: strip(SOP[76]), 77: "B5/16~",
           78: "B5/16"})
CL.update({75: merge(ALT[75]), 76: merge(ALT[76]), 77: "G4/16", 78: "A4/16"})
BSN.update({75: "B2/8 C3/8", 76: "D3/16", 77: "G2/16~", 78: "G2/16"})
HN1.update({75: merge(ALT[75]), 76: merge(ALT[76]),
            77: "E4/4 E4/4 (B3/2 D4/4) D4/2~", 78: "D4/16"})
HN2.update({75: merge(TEN[75]), 76: merge(TEN[76]), 77: "B3/16~",
            78: "B3/16"})
TPT.update({76: strip(SOP[76]), 77: "E5/4 E5/4 (B4/2 D5/4) D5/2~",
            78: "D5/16"})
TBN.update({76: merge(TEN[76]), 77: "G3/16~", 78: "G3/16"})
TBA.update({75: "B1/8 C2/8", 76: "D2/16", 77: "G1/16~", 78: "G1/16"})
TIMP.update({75: "B2/8% E3/8%", 76: "D3/16%", 77: "G2/16%~",
             78: "G2/16%"})
GLK.update({76: octv(strip(SOP[76]), 1), 77: "E6/4 E6/4 B5/2 D6/4 D6/2",
            78: "E7/4 r/12"})
for p in (VN2, VLA, CL, HN1, HN2):
    auto_tie(p, (74, 75))


def fix_ties(part):
    """Drop a tie that does not land on the same pitch in the next bar."""
    for b in range(1, NBARS + 1):
        a = toks(part[b])
        if not a or not a[-1]["tie"]:
            continue
        nxt = toks(part[b + 1]) if b < NBARS else []
        if not nxt or nxt[0]["pit"] != a[-1]["pit"]:
            a[-1]["tie"] = False
            part[b] = untoks(a)


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------
def _ins(cls, name, abbr, transp=None):
    """mode: 'trans' (transposing score), 'cscore' (score in C: only
    octave transpositions such as piccolo / contrabass / glockenspiel
    remain), 'concert' (everything at sounding pitch)."""
    def make(concert=False, mode=None, names=None):
        mode = mode or ("concert" if concert else "trans")
        i = cls()
        nm, ab = names or (name, abbr)
        i.partName, i.partAbbreviation = nm, ab
        i.instrumentName, i.instrumentAbbreviation = nm, ab
        if transp:
            i.transposition = interval.Interval(transp)
        if mode == "concert" or (
                mode == "cscore" and i.transposition is not None
                and i.transposition.semitones % 12 != 0):
            i.transposition = None
        return i
    return make


def D(s):
    """'3:0:p 5:0:mf' -> [(3, 0, 'p'), (5, 0, 'mf')]"""
    return [tuple(int(x) if x.isdigit() else x for x in t.split(":"))
            for t in s.split()]


def HP(s):
    """'3:0-4:11:c' -> [(3, 0, 4, 11, 'cresc')]"""
    out = []
    for t in s.split():
        a, b = t.split("-")
        b1, s1 = map(int, a.split(":"))
        b2, s2, k = b.split(":")
        out.append((b1, s1, int(b2), int(s2),
                    "cresc" if k == "c" else "dim"))
    return out


def TX(s):
    """'1:8:dolce|5:0:giocoso' -> [(1, 8, 'dolce'), (5, 0, 'giocoso')]"""
    out = []
    for t in s.split("|"):
        if t.strip():
            b, pos, txt = t.split(":", 2)
            out.append((int(b), int(pos), txt.strip()))
    return out


VOX_DYN = ("3:0:pp 4:8:mf 14:0:mp 22:0:pp 26:0:mf 31:0:f 39:0:f 54:0:p "
           "58:0:ff 74:0:p 76:0:ff")
VOX_HAIR = "3:0-4:7:c 29:0-30:13:c 54:0-57:11:c 75:0-75:15:c"
MEN_DYN = "3:0:pp 4:8:mf 22:0:mp 26:0:mf 31:0:f 54:0:p 58:0:ff 74:0:p 76:0:ff"
STR_DYN = "1:0:pp 5:0:mp 22:0:p 26:0:mf 31:0:f 48:0:f 56:0:mf 58:0:ff 74:0:p " \
          "76:0:ff"
STR_HAIR = "3:0-4:11:c 29:0-30:15:c 56:0-57:11:c 75:0-75:15:c"
WW_HAIR = "3:0-4:11:c 29:0-30:13:c 56:0-57:11:c 75:0-75:15:c"
PIZZ = [(5, 21)]

# id, English name, abbr, 中文, data, instrument, clef, GM program, channel,
# Instrument X expansion (None = not in Instrument X), range, dyn, hair, text
PARTS = [
    dict(id="picc", name="Piccolo", abbr="Picc.", cn="短笛", data=PICC,
         inst=_ins(instrument.Piccolo, "Piccolo", "Picc."),
         clef=clef.TrebleClef, program=72, ch=0, ix="Piccolo 1",
         rng=("D5", "C8"), dyn=D("39:0:f 52:0:f 57:12:ff 58:0:ff 76:0:ff"),
         hair=[], text=[]),
    dict(id="fl", name="Flute", abbr="Fl.", cn="长笛", data=FL,
         inst=_ins(instrument.Flute, "Flute", "Fl."),
         clef=clef.TrebleClef, program=73, ch=1, ix="Flute 1",
         rng=("C4", "C7"),
         dyn=D("1:8:p 5:0:mf 12:8:mp 15:8:mp 21:8:mp 23:8:p 25:8:p 26:0:mf "
               "31:0:f 48:0:f 56:0:f 58:0:ff 75:0:mp 76:0:ff"),
         hair=HP("29:0-30:13:c 56:0-57:11:c 75:0-75:15:c"),
         text=TX("1:8:dolce|5:0:giocoso|25:8:潺潺 (rippling)")),
    dict(id="ob", name="Oboe", abbr="Ob.", cn="双簧管", data=OB,
         inst=_ins(instrument.Oboe, "Oboe", "Ob."),
         clef=clef.TrebleClef, program=68, ch=2, ix="Oboe 1",
         rng=("Bb3", "F6"),
         dyn=D("5:0:mf 17:8:mp 26:0:mf 31:0:f 48:0:f 56:0:f 58:0:ff 75:0:mp "
               "76:0:ff"),
         hair=HP("29:0-30:13:c 56:0-57:11:c 75:0-75:15:c"),
         text=TX("5:0:giocoso|17:8:唢呐风 (suona-like)|34:8:唢呐风|"
                 "42:8:唢呐风|61:8:唢呐风")),
    dict(id="cl", name="Clarinet in A", abbr="Cl.", cn="单簧管（A调）",
         data=CL, inst=_ins(instrument.Clarinet, "Clarinet in A", "Cl.",
                            "m-3"),
         clef=clef.TrebleClef, program=71, ch=3, ix="Clarinet in A 1",
         rng=("E3", "F6"),
         dyn=D("3:0:p 5:0:p 9:0:mp 19:8:mp 21:8:mp 26:0:mf 31:0:mf 48:0:f "
               "52:0:mf 56:0:f 58:0:f 75:0:mp 76:0:ff"),
         hair=HP(WW_HAIR), text=[]),
    dict(id="bsn", name="Bassoon", abbr="Bsn.", cn="大管", data=BSN,
         inst=_ins(instrument.Bassoon, "Bassoon", "Bsn."),
         clef=clef.BassClef, program=70, ch=4, ix="Bassoon 1",
         rng=("Bb1", "Bb4"),
         dyn=D("3:0:p 5:0:mp 18:0:p 22:0:p 26:0:mf 31:0:f 48:0:f 56:0:f "
               "58:0:ff 75:0:mp 76:0:ff"),
         hair=HP(WW_HAIR), text=[]),
    dict(id="hn1", name="Horn I", abbr="Hn. I", cn="圆号 I", data=HN1,
         inst=_ins(instrument.Horn, "Horn in F I", "Hn. I"),
         clef=clef.TrebleClef, program=60, ch=5, ix="Horn 1",
         rng=("F2", "F5"),
         dyn=D("1:0:p 9:0:p 18:0:p 26:0:mf 31:0:mf 39:0:f 48:0:ff 52:0:mf "
               "56:0:f 58:0:ff 75:0:mp 76:0:ff"),
         hair=HP(WW_HAIR),
         text=TX("1:0:solo, espr.|9:0:dolce|39:0:a2, cantabile|"
                 "48:0:a2, marcato|58:0:a2, eroico|77:0:大东北 motif")),
    dict(id="hn2", name="Horn II", abbr="Hn. II", cn="圆号 II", data=HN2,
         inst=_ins(instrument.Horn, "Horn in F II", "Hn. II"),
         clef=clef.TrebleClef, program=60, ch=5, ix="Horn 1",
         rng=("F2", "F5"),
         dyn=D("3:0:p 9:0:p 26:0:mf 31:0:mf 39:0:f 48:0:ff 52:0:mf 56:0:f "
               "58:0:ff 75:0:mp 76:0:ff"),
         hair=HP(WW_HAIR), text=[]),
    dict(id="tpt", name="Trumpet", abbr="Tpt.", cn="小号", data=TPT,
         inst=_ins(instrument.Trumpet, "Trumpet in Bb", "Tpt."),
         clef=clef.TrebleClef, program=56, ch=6, ix="Trumpet 1",
         rng=("F#3", "Bb5"),
         dyn=D("30:8:mf 38:4:f 44:8:f 46:8:f 48:0:ff 56:0:mf 58:0:ff 76:0:ff"),
         hair=HP("30:8-30:15:c 56:0-57:11:c"),
         text=TX("48:0:marcato|66:0:con tutta forza")),
    dict(id="tbn", name="Trombone", abbr="Tbn.", cn="长号", data=TBN,
         inst=_ins(instrument.Trombone, "Trombone", "Tbn."),
         clef=clef.BassClef, program=57, ch=7, ix="Trombone 1",
         rng=("E2", "C5"),
         dyn=D("4:0:p 28:0:mf 31:0:mf 48:0:f 56:0:mf 58:0:ff 76:0:ff"),
         hair=HP("4:0-4:11:c 28:0-30:13:c 56:0-57:11:c"), text=[]),
    dict(id="tba", name="Tuba", abbr="Tba.", cn="大号", data=TBA,
         inst=_ins(instrument.Tuba, "Tuba", "Tba."),
         clef=clef.BassClef, program=58, ch=8, ix="Tuba 1",
         rng=("D1", "F4"),
         dyn=D("4:0:p 29:0:mf 39:0:f 48:0:f 56:0:mf 58:0:ff 75:0:mp 76:0:ff"),
         hair=HP("4:0-4:11:c 29:0-30:13:c 56:0-57:11:c 75:0-75:15:c"),
         text=[]),
    dict(id="timp", name="Timpani", abbr="Timp.", cn="定音鼓", data=TIMP,
         inst=_ins(instrument.Timpani, "Timpani", "Timp."),
         clef=clef.BassClef, program=47, ch=10, ix=None,
         rng=("D2", "A3"),
         dyn=D("4:8:pp 5:0:mf 29:8:p 31:0:f 48:0:f 56:8:p 58:0:ff 75:0:p "
               "76:0:f 77:0:ff"),
         hair=HP("4:8-4:15:c 29:8-30:13:c 56:8-57:11:c 75:0-75:15:c"),
         text=TX("1:0:F A C D|52:0:muta in G B D E")),
    dict(id="glk", name="Glockenspiel", abbr="Glk.", cn="钟琴", data=GLK,
         inst=_ins(instrument.Glockenspiel, "Glockenspiel", "Glk.", "P15"),
         clef=clef.TrebleClef, program=9, ch=11, ix=None,
         rng=("G5", "C8"),
         dyn=D("1:8:p 7:0:mf 25:8:p 33:0:mf 50:0:mf 58:0:f 76:0:f"),
         hair=[], text=[]),
    dict(id="hpr", name="Harp", abbr="Hp.", cn="竖琴", data=HPR,
         inst=_ins(instrument.Harp, "Harp", "Hp."),
         clef=clef.TrebleClef, program=46, ch=12, ix=None,
         rng=("C1", "G7"),
         dyn=D("1:0:p 9:0:mp 18:0:p 22:0:mp 26:0:mf 31:0:mf 48:0:f 56:0:mf "
               "58:0:f 74:0:p 76:0:f"),
         hair=HP("56:0-57:11:c"), text=TX("25:0:潺潺流淌 (ripples)")),
    dict(id="hpl", name="Harp", abbr="Hp.", cn="竖琴", data=HPL,
         inst=_ins(instrument.Harp, "Harp", "Hp."),
         clef=clef.BassClef, program=46, ch=12, ix=None,
         rng=("C1", "G7"),
         dyn=D("1:0:p 9:0:mp 18:0:p 22:0:mp 26:0:mf 31:0:mf 48:0:f 56:0:mf "
               "58:0:f 74:0:p 76:0:f"),
         hair=[], text=[]),
    dict(id="sop", name="Soprano", abbr="S.", cn="女高音", data=SOP,
         inst=_ins(instrument.Soprano, "Soprano", "S."),
         clef=clef.TrebleClef, program=52, ch=13, ix=None,
         rng=("C4", "A5"), dyn=D(VOX_DYN), hair=HP(VOX_HAIR),
         text=TX("14:0:女声齐唱|22:0:哼鸣“啊”|26:0:tutti|74:0:subito p")),
    dict(id="alt", name="Alto", abbr="A.", cn="女低音", data=ALT,
         inst=_ins(instrument.Alto, "Alto", "A."),
         clef=clef.TrebleClef, program=52, ch=13, ix=None,
         rng=("G3", "D5"), dyn=D(VOX_DYN), hair=HP(VOX_HAIR), text=[]),
    dict(id="ten", name="Tenor", abbr="T.", cn="男高音", data=TEN,
         inst=_ins(instrument.Tenor, "Tenor", "T."),
         clef=clef.Treble8vbClef, program=52, ch=13, ix=None,
         rng=("C3", "A4"), dyn=D(MEN_DYN), hair=HP(VOX_HAIR),
         text=TX("22:0:男声领唱")),
    dict(id="bas", name="Bass", abbr="B.", cn="男低音", data=BAS,
         inst=_ins(instrument.Bass, "Bass", "B."),
         clef=clef.BassClef, program=52, ch=13, ix=None,
         rng=("E2", "D4"), dyn=D(MEN_DYN), hair=HP(VOX_HAIR), text=[]),
    dict(id="vn1", name="Violin I", abbr="Vln. I", cn="第一小提琴",
         data=VN1, inst=_ins(instrument.Violin, "Violin I", "Vln. I"),
         clef=clef.TrebleClef, program=48, ch=14, ix="Violin 1",
         rng=("G3", "C7"), dyn=D(STR_DYN.replace("5:0:mp ", "9:0:mf ")),
         hair=HP(STR_HAIR),
         text=TX("1:0:sul tasto|9:0:ord., dolce|22:0:espr.|31:0:cantabile|"
                 "58:0:appassionato")),
    dict(id="vn2", name="Violin II", abbr="Vln. II", cn="第二小提琴",
         data=VN2, inst=_ins(instrument.Violin, "Violin II", "Vln. II"),
         clef=clef.TrebleClef, program=48, ch=14, ix="Violin 1",
         rng=("G3", "A6"), dyn=D(STR_DYN), hair=HP(STR_HAIR), text=[],
         pizz=PIZZ),
    dict(id="va", name="Viola", abbr="Vla.", cn="中提琴", data=VLA,
         inst=_ins(instrument.Viola, "Viola", "Vla."),
         clef=clef.AltoClef, program=48, ch=15, ix="Viola 1",
         rng=("C3", "E6"), dyn=D(STR_DYN), hair=HP(STR_HAIR), text=[],
         pizz=PIZZ),
    dict(id="vc", name="Violoncello", abbr="Vc.", cn="大提琴", data=VC_,
         inst=_ins(instrument.Violoncello, "Violoncello", "Vc."),
         clef=clef.BassClef, program=48, ch=15, ix="Violoncello 1",
         rng=("C2", "A5"), dyn=D(STR_DYN), hair=HP(STR_HAIR), text=[],
         pizz=PIZZ),
    dict(id="cb", name="Contrabass", abbr="Cb.", cn="低音提琴", data=CBS,
         inst=_ins(instrument.Contrabass, "Contrabass", "Cb."),
         clef=clef.BassClef, program=43, ch=15, ix="Contrabass 1",
         rng=("E1", "G3"), dyn=D(STR_DYN), hair=HP(STR_HAIR), text=[],
         pizz=PIZZ),
]
PBY = {p["id"]: p for p in PARTS}
CHOIR = ("sop", "alt", "ten", "bas")
for p in PARTS:
    p.setdefault("pizz", [])
    fix_ties(p["data"])

VEL = {"pp": 36, "p": 50, "mp": 62, "mf": 76, "f": 92, "ff": 106}
ACCENT = 14

# Tempo map (bar, 16th, bpm); fermatas are realised here
TEMPI = [(1, 0, 72), (4, 8, 64), (4, 12, 34), (5, 0, 128), (57, 12, 112),
         (58, 0, 128), (74, 0, 118), (75, 8, 122), (76, 0, 112), (76, 4, 100),
         (76, 8, 88), (76, 12, 34), (77, 0, 96), (78, 0, 86), (78, 8, 66),
         (78, 12, 40)]
TEMPO_MARKS = [(1, 0, "Maestoso", 72), (5, 0, "Allegro giocoso", 128),
               (74, 0, "Poco meno mosso", 118), (77, 0, "Maestoso", 96)]
TEMPO_TEXT = [(4, 8, "rit."), (57, 12, "G.P. (bar runs)"), (76, 0, "allarg."),
              (78, 8, "rit.")]
REHEARSAL = {1: "Prologue 序", 5: "A 前奏", 14: "B 主歌", 31: "C 副歌",
             48: "D 间奏", 58: "E 副歌·G调", 74: "Coda 尾声"}
FERMATAS = {4: 12, 76: 12, 78: 0}
SYSTEM_BREAKS = ()  # the full score is one system per page; let it flow

# ---------------------------------------------------------------------------
# Parsing to events
# ---------------------------------------------------------------------------


def parse_bar(s):
    evs, pos = [], 0
    for t in toks(s):
        evs.append(dict(
            pos=pos, dur=t["dur"], pitches=t["pit"], tie=t["tie"],
            slur_start=t["sl"], slur_end=t["sr"], accent=">" in t["fl"],
            stacc="." in t["fl"], trem="%" in t["fl"], trill="t" in t["fl"],
            fermata=False, lyric=t["lyr"], grace=t["grace"]))
        pos += t["dur"]
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
        # fermata: split the event that covers the fermata beat
        if b in FERMATAS:
            fp = FERMATAS[b]
            new = []
            for e in evs:
                if e["pos"] < fp < e["pos"] + e["dur"]:
                    a = dict(e, dur=fp - e["pos"], slur_end=False,
                             tie=e["pitches"] is not None)
                    z = dict(e, pos=fp, dur=e["pos"] + e["dur"] - fp,
                             slur_start=False, lyric=None, grace=None,
                             accent=False)
                    new += [a, z]
                else:
                    new.append(e)
            evs = new
            for e in evs:
                if e["pos"] == fp:
                    e["fermata"] = True
        for e in evs:
            e["bar"] = b
            e["abs"] = (b - 1) * BAR16 + e["pos"]
            out.append(e)
    return out


def in_pizz(p, b):
    return any(a <= b <= z for a, z in p["pizz"])


# ---------------------------------------------------------------------------
# music21 score
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


def make_m21(p, events, top=False, concert=False, staff_cls=stream.Part,
             mode=None, names=None, rehearsal=None, timings=False, hw=False,
             sections=None):
    """hw: conductor-score conventions (English technique words, click
    notes above the top staff)."""
    rehearsal = REHEARSAL if rehearsal is None else rehearsal
    word = (lambda t: HW_WORDS.get(t, t)) if hw else (lambda t: t)
    part = staff_cls(id=p["id"])
    part.insert(0, p["inst"](concert=concert, mode=mode, names=names))
    notes_at, slur_open, measures, by_bar = {}, None, {}, {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    tied_prev, prev_pizz = False, False
    for b in range(1, NBARS + 1):
        m = stream.Measure(number=b)
        if b == 1:
            m.insert(0, p["clef"]())
            m.insert(0, meter.TimeSignature("4/4"))
        if b in KEYS:
            m.insert(0, key.Key(KEYS[b]))
        if top and b == 1:
            pass
        for e in by_bar[b]:
            if e["grace"]:
                g = note.Note(m21_name(e["grace"]), type="16th").getGrace()
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
                         m21chord.Chord(names, quarterLength=QL[d]))
                    first, last = i == 0, i == len(pieces) - 1
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
                    if first and e["stacc"]:
                        n.articulations.append(articulations.Staccato())
                    if e["trem"]:
                        tr = expressions.Tremolo()
                        tr.numberOfMarks = 3
                        n.expressions.append(tr)
                    if first and e["trill"]:
                        n.expressions.append(expressions.Trill())
                if i == 0 and e["fermata"]:
                    f = expressions.Fermata()
                    f.type = "upright"
                    n.expressions.append(f)
                m.append(n)
                objs.append(n)
            notes_at.setdefault(e["abs"], objs[0])
            tied_prev = e["tie"] and e["pitches"] is not None
            if e["slur_start"]:
                slur_open = objs[0]
            if e["slur_end"] and slur_open is not None:
                part.insert(0, spanner.Slur(slur_open, objs[-1]))
                slur_open = None
        # words and marks go in after the notes, or append() shifts them
        if top:
            if b in rehearsal:
                rm = expressions.RehearsalMark(rehearsal[b])
                rm.placement = "above"
                m.insert(0, rm)
            if sections and b in sections:
                te = expressions.TextExpression(sections[b])
                te.style.fontWeight = "bold"
                te.style.fontSize = 12
                te.placement = "above"
                m.insert(0, te)
            if timings:
                t = sec_at((b - 1) * BAR16)
                te = expressions.TextExpression(
                    f"{int(t // 60)}:{t % 60:04.1f}")
                te.style.fontSize = 7
                te.placement = "above"
                m.insert(0, te)
            for tb, ts, txt, bpm in TEMPO_MARKS:
                if tb == b:
                    mm = tempo.MetronomeMark(text=txt, number=bpm,
                                             referent=1.0)
                    mm.placement = "above"
                    m.insert(ts / 4, mm)
            for tb, ts, txt in TEMPO_TEXT:
                if tb == b:
                    m.insert(ts / 4, tempo.TempoText(word(txt)))
            for tb, ts, txt in (HW_CLICK if hw else ()):
                if tb == b:
                    te = expressions.TextExpression(txt)
                    te.style.fontSize = 8
                    te.style.fontStyle = "italic"
                    te.placement = "above"
                    m.insert(ts / 4, te)
        if p["pizz"]:
            now = in_pizz(p, b)
            if now != prev_pizz:
                first_note = next((e for e in by_bar[b] if e["pitches"]),
                                  None)
                at = first_note["pos"] if first_note else 0
                te = expressions.TextExpression("pizz." if now else "arco")
                te.placement = "above"
                m.insert(at / 4, te)
                prev_pizz = now
        if b == NBARS:
            m.rightBarline = bar.Barline("final")
        measures[b] = m
        part.append(m)

    def obj_at(bb, s, forward=True):
        a = (bb - 1) * BAR16 + s
        ks = sorted(notes_at)
        seq = ks if forward else list(reversed(ks))
        for k in seq:
            if (k >= a) if forward else (k <= a):
                return notes_at[k]
        return None

    vocal = p["id"] in CHOIR
    for bb, s, mark in p["dyn"]:
        d = dynamics.Dynamic(mark)
        d.placement = "above" if vocal else "below"
        measures[bb].insert(s / 4, d)
    for bb, s, bb2, s2, kind in p["hair"]:
        n1, n2 = obj_at(bb, s), obj_at(bb2, s2, forward=False)
        if n1 is n2:     # one held note: run the wedge to the next event
            n2 = obj_at(bb2, s2 + 1)
        if n1 is not None and n2 is not None and n1 is not n2:
            part.insert(0, (dynamics.Crescendo if kind == "cresc"
                            else dynamics.Diminuendo)(n1, n2))
    for bb, s, txt in p["text"]:
        te = expressions.TextExpression(word(txt))
        te.style.fontStyle = "italic"
        te.placement = "above"
        measures[bb].insert(s / 4, te)
    part.atSoundingPitch = True
    return part


def score_meta(sc, subtitle):
    md = metadata.Metadata()
    md.title = "大东北我的家乡"
    md.movementName = "大东北我的家乡 · " + subtitle
    md.composer = "刘旗 词曲"
    md.add("arranger", "迪士尼风格交响乐与四声部合唱 · F → G")
    sc.insert(0, md)


GROUPS = [("Woodwinds", ["picc", "fl", "ob", "cl", "bsn"], "bracket"),
          ("Brass", ["hn1", "hn2", "tpt", "tbn", "tba"], "bracket"),
          ("Choir", list(CHOIR), "bracket"),
          ("Strings", ["vn1", "vn2", "va", "vc", "cb"], "bracket")]


def build_score(parsed):
    sc = stream.Score()
    score_meta(sc, "交响乐与四声部合唱")
    objs = {}
    for p in PARTS:
        cls = stream.PartStaff if p["id"] in ("hpr", "hpl") else stream.Part
        objs[p["id"]] = make_m21(p, parsed[p["id"]], top=p["id"] == "picc",
                                 staff_cls=cls)
        sc.insert(0, objs[p["id"]])
    for name, ids, sym in GROUPS:
        sc.insert(0, layout.StaffGroup([objs[i] for i in ids], name=name,
                                       symbol=sym))
    sc.insert(0, layout.StaffGroup([objs["hpr"], objs["hpl"]], name="Harp",
                                   symbol="brace"))
    return sc


def single_part_score(p, events, concert=True, subtitle=None):
    sc = stream.Score()
    score_meta(sc, subtitle or p["name"])
    sc.insert(0, make_m21(p, events, top=True, concert=concert))
    return sc


# ---------------------------------------------------------------------------
# MusicXML polish (Sibelius)
# ---------------------------------------------------------------------------
SOUNDS = {"picc": "wind.flutes.flute.piccolo", "fl": "wind.flutes.flute",
          "ob": "wind.reed.oboe", "cl": "wind.reed.clarinet.a",
          "bsn": "wind.reed.bassoon", "hn1": "brass.french-horn",
          "hn2": "brass.french-horn", "tpt": "brass.trumpet.bflat",
          "tbn": "brass.trombone", "tba": "brass.tuba",
          "timp": "drum.timpani", "glk": "pitched-percussion.glockenspiel",
          "hpr": "pluck.harp", "sop": "voice.soprano", "alt": "voice.alto",
          "ten": "voice.tenor", "bas": "voice.bass", "vn1": "strings.violin",
          "vn2": "strings.violin", "va": "strings.viola",
          "vc": "strings.cello", "cb": "strings.contrabass"}


def polish(path, ids, big=True, breaks=SYSTEM_BREAKS, page=None,
           top_gap=None, margin=None, page_breaks=(), tempo_sounds=True,
           fermata_steps=False):
    """Page layout, one <instrument-sound> per part so Sibelius maps the
    right instrument, no per-note instrument changes, vocal dynamics above
    the staff (lyrics are below), words and rehearsal marks above."""
    tree = ET.parse(path)
    r = tree.getroot()
    d = r.find("defaults")
    if d is None:
        d = ET.Element("defaults")
        r.insert(list(r).index(r.find("part-list")), d)
    for t in ("scaling", "page-layout", "system-layout", "staff-layout"):
        for x in d.findall(t):
            d.remove(x)
    if big:   # A3 portrait, 3.7 mm staves
        mm, pw, ph, sd, st = "3.7", 3211, 4541, 80, 42
    else:     # A4 portrait, 6 mm staves
        mm, pw, ph, sd, st = "6", 1400, 1980, 110, 75
    if page:
        mm, pw, ph = page
    new = ET.fromstring(
        f"<defaults><scaling><millimeters>{mm}</millimeters><tenths>40"
        f"</tenths></scaling><page-layout><page-height>{ph}</page-height>"
        f"<page-width>{pw}</page-width><page-margins type=\"both\">"
        f"<left-margin>{margin or 80}</left-margin>"
        f"<right-margin>{margin or 60}</right-margin>"
        f"<top-margin>{margin or 70}</top-margin>"
        f"<bottom-margin>{margin or 70}</bottom-margin>"
        "</page-margins></page-layout><system-layout><system-margins>"
        "<left-margin>90</left-margin><right-margin>0</right-margin>"
        f"</system-margins><system-distance>{sd}</system-distance>"
        f"<top-system-distance>{top_gap or (110 if big else 170)}"
        "</top-system-distance>"
        "</system-layout>"
        f"<staff-layout><staff-distance>{st}</staff-distance></staff-layout>"
        "</defaults>")
    for i, x in enumerate(new):
        d.insert(i, x)
    sps = list(r.iter("score-part"))
    pid_of = {}
    for sp, pid in zip(sps, ids):
        pid_of[sp.get("id")] = pid
        si = sp.find("score-instrument")
        if si is not None:
            for x in si.findall("instrument-sound"):
                si.remove(x)
            el = ET.Element("instrument-sound")
            el.text = SOUNDS[pid]
            ab = si.find("instrument-abbreviation")
            si.insert(list(si).index(ab) + 1 if ab is not None else 1, el)
        mi = sp.find("midi-instrument")
        if mi is not None and pid in PBY:
            for tag, val in (("midi-channel", PBY[pid]["ch"] + 1),
                             ("midi-program", PBY[pid]["program"] + 1)):
                el = mi.find(tag)
                if el is not None:
                    el.text = str(val)
    for n in r.iter("note"):
        for x in n.findall("instrument"):
            n.remove(x)
    parts = r.findall("part")
    if parts and tempo_sounds:
        add_tempo_sounds(parts[0], fermata_steps)
    for part in r.findall("part"):
        if pid_of.get(part.get("id")) not in CHOIR:
            continue
        last = None   # the lyric of the syllable being held
        for n in part.iter("note"):
            if n.find("rest") is not None:
                last = None
            elif n.find("grace") is not None:
                continue
            elif n.find("lyric") is not None:
                last = n.find("lyric")
            elif last is not None and last.find("extend") is None:
                ET.SubElement(last, "extend")
    for part in r.findall("part"):
        vocal = pid_of.get(part.get("id")) in CHOIR
        for m in part.findall("measure"):
            num = int(m.get("number"))
            if num in breaks or num in page_breaks:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                pr.set("new-page" if num in page_breaks else "new-system",
                       "yes")
            for el in m.findall("direction"):
                if el.find("direction-type/dynamics") is not None or \
                        el.find("direction-type/wedge") is not None:
                    el.set("placement", "above" if vocal else "below")
                elif el.find("direction-type/words") is not None or \
                        el.find("direction-type/rehearsal") is not None:
                    el.set("placement", "above")
    for part in parts:     # pedal changes sit between the harp staves
        if pid_of.get(part.get("id")) == "hpr":
            add_harp_pedals(part)
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
# MusicXML additions: every tempo step for playback, harp pedalling
# ---------------------------------------------------------------------------
def _insert_at(measure, target, el, offset_ok=False):
    """Insert `el` before the note/rest of the first voice that covers
    `target` (divisions).  If that note starts earlier and `offset_ok`,
    an <offset> child places `el` exactly at the target."""
    t = 0
    for i, ch in enumerate(list(measure)):
        if ch.tag == "note":
            if ch.find("chord") is not None or ch.find("grace") is not None:
                continue
            dur = int(ch.findtext("duration"))
            if t <= target < t + dur:
                if target > t:
                    if not offset_ok:
                        raise ValueError("target inside a note")
                    ET.SubElement(el, "offset").text = str(target - t)
                measure.insert(i, el)
                return
            t += dur
        elif ch.tag == "backup":
            break          # only the first voice / staff is walked
        elif ch.tag == "forward":
            t += int(ch.findtext("duration"))
    raise ValueError(f"no note covers {target} in bar {measure.get('number')}")


# TEMPI steps that only stretch a fermata (notation programs hold fermatas
# themselves; ACE / Instrument X do not)
FERMATA_STEPS = {(4, 12), (76, 12)}


def add_tempo_sounds(part, fermata_steps=False):
    """Hidden <sound tempo> for every step of TEMPI (the visible metronome
    marks carry their own), placed exactly with <offset> where the step
    falls inside a held note, so playback and Sibelius' timecode follow the
    same rit./accel. as the MIDI.  fermata_steps: also write the steps that
    stretch the fermatas (for importers that don't play fermatas)."""
    div = int(part.find("measure/attributes/divisions").text)
    shown = {(b, s) for b, s, _, _ in TEMPO_MARKS}
    by_num = {int(m.get("number")): m for m in part.findall("measure")}
    for b, s, bpm in TEMPI:
        if (b, s) in shown or ((b, s) in FERMATA_STEPS and not fermata_steps):
            continue
        _insert_at(by_num[b], s * div // 4,
                   ET.Element("sound", tempo=str(bpm)), offset_ok=True)


def sound_positions(part):
    """[(bar, 16th, bpm)] of every <sound tempo> in a part (read-back)."""
    div = int(part.find("measure/attributes/divisions").text)
    out = []
    for m in part.findall("measure"):
        t = 0
        for ch in m:
            if ch.tag == "note":
                if ch.find("chord") is None and ch.find("grace") is None:
                    t += int(ch.findtext("duration"))
            elif ch.tag == "backup":
                t -= int(ch.findtext("duration"))
            elif ch.tag == "forward":
                t += int(ch.findtext("duration"))
            snds = [ch] if ch.tag == "sound" else ch.findall("sound")
            for sd in snds:
                if sd.get("tempo"):
                    off = int(sd.findtext("offset") or 0)
                    out.append((int(m.get("number")), (t + off) * 4 // div,
                                round(float(sd.get("tempo")))))
    return out


PEDAL_ORDER = "DCBEFGA"
ACC_TXT = {-1: "♭", 0: "♮", 1: "♯"}


def harp_pedal_changes():
    state = {"D": 0, "C": 0, "B": -1, "E": 0, "F": 0, "G": 0, "A": 0}
    first = dict(state)
    evs = sorted(parse_part(HPR) + parse_part(HPL), key=lambda e: e["abs"])
    changes = {}
    for e in evs:
        for p in e["pitches"] or []:
            step, acc, _ = PIT.fullmatch(p).groups()
            a = _ACC[acc]
            if state[step] != a:
                state[step] = a
                changes.setdefault(e["bar"], []).append(step + ACC_TXT[a])
    return first, changes


def add_harp_pedals(part):
    """Pedal diagram at bar 1 and the pedal changes (as text between the
    staves) at the start of each bar that needs them."""
    first, changes = harp_pedal_changes()
    by_num = {int(m.get("number")): m for m in part.findall("measure")}
    d = ET.Element("direction", placement="below")
    hp = ET.SubElement(ET.SubElement(d, "direction-type"), "harp-pedals")
    for step in PEDAL_ORDER:
        pt = ET.SubElement(hp, "pedal-tuning")
        ET.SubElement(pt, "pedal-step").text = step
        ET.SubElement(pt, "pedal-alter").text = str(first[step])
    ET.SubElement(d, "staff").text = "1"
    _insert_at(by_num[1], 0, d)
    by_num[1].remove(d)
    by_num[1].insert(list(by_num[1]).index(by_num[1].find("note")), d)
    for b, ch in changes.items():
        d = ET.Element("direction", placement="below")
        w = ET.SubElement(ET.SubElement(d, "direction-type"), "words",
                          {"font-size": "9"})
        w.text = " ".join(ch)
        ET.SubElement(d, "staff").text = "1"
        _insert_at(by_num[b], 0, d)


def check_xml_extras(path, ids, fermata_steps=False, tempo=True):
    """Read back: every tempo step sits where TEMPI puts it, and every
    part has as many hairpins as its data asks for."""
    r = ET.parse(path).getroot()
    parts = r.findall("part")
    got = sorted(sound_positions(parts[0]))
    want = sorted((b, s, bpm) for b, s, bpm in TEMPI
                  if tempo and (fermata_steps or (b, s) not in FERMATA_STEPS))
    if not tempo:
        want = sorted((b, s, bpm) for b, s, _, bpm in TEMPO_MARKS)
    assert got == want, (path, sorted(set(got) ^ set(want)))
    staff_ids = [i for i in ids if i != "hpl"]
    for part, pid in zip(parts, staff_ids):
        n = sum(1 for w in part.iter("wedge")
                if w.get("type") in ("crescendo", "diminuendo"))
        want_n = len(PBY[pid]["hair"]) + (len(PBY["hpl"]["hair"])
                                          if pid == "hpr" else 0)
        assert n == want_n, (path, pid, n, want_n)


def verify(path, parsed, ids):
    """Read the written file back: every bar holds 4/4, and every note sounds
    at the pitch the data asks for (catches transposition mistakes)."""
    from music21 import converter
    sc = converter.parse(path)
    staves = list(sc.parts)
    assert len(staves) == len(ids), (len(staves), len(ids))
    for st, pid in zip(staves, ids):
        ms = st.getElementsByClass("Measure")
        assert len(ms) == NBARS, (pid, len(ms))
        for m in ms:
            assert abs(m.duration.quarterLength - 4) < 1e-6, \
                (pid, m.number, m.duration.quarterLength)
        got = []
        snd = st.toSoundingPitch() if not st.atSoundingPitch else st
        for m in snd.getElementsByClass("Measure"):
            for n in m.notes:
                if n.duration.isGrace or (n.tie and n.tie.type != "start"):
                    continue
                for pp in n.pitches:
                    got.append((m.number, round(float(n.offset) * 4),
                                int(round(pp.ps))))
        want, held = [], False
        for e in parsed[pid]:
            if e["pitches"] and not held:
                for x in e["pitches"]:
                    want.append((e["bar"], e["pos"], midi_of(x)))
            held = e["tie"] and e["pitches"] is not None
        assert sorted(got) == sorted(want), \
            (pid, sorted(set(got) ^ set(want))[:6])


# ---------------------------------------------------------------------------
# Hollywood-style conductor score (score in C) for Sibelius
# ---------------------------------------------------------------------------
HW_NAMES = {
    "picc": ("Piccolo", "Picc."), "fl": ("Flute", "Fl."),
    "ob": ("Oboe", "Ob."), "cl": ("Clarinet in A", "Cl."),
    "bsn": ("Bassoon", "Bsn."), "hn1": ("Horns 1.3", "Hns. 1.3"),
    "hn2": ("Horns 2.4", "Hns. 2.4"), "tpt": ("Trumpet in B♭", "Tpt."),
    "tbn": ("Trombone", "Tbn."), "tba": ("Tuba", "Tba."),
    "timp": ("Timpani", "Timp."), "glk": ("Glockenspiel", "Glock."),
    "hpr": ("Harp", "Hp."), "hpl": ("Harp", "Hp."),
    "sop": ("Sopranos", "S."), "alt": ("Altos", "A."),
    "ten": ("Tenors", "T."), "bas": ("Basses", "B."),
    "vn1": ("Violins I", "Vlns. I"), "vn2": ("Violins II", "Vlns. II"),
    "va": ("Violas", "Vlas."), "vc": ("Celli", "Vc."),
    "cb": ("Contrabasses", "Cb."),
}
# film sessions navigate by bar numbers: section words, no letters
HW_SECTIONS = {1: "PROLOGUE", 5: "INTRO", 14: "VERSE", 31: "CHORUS 1",
               48: "INTERLUDE", 58: "CHORUS 2 (in G)", 74: "CODA"}
# technique words in English / Italian in the conductor score
HW_WORDS = {"唢呐风 (suona-like)": "suona-like", "唢呐风": "suona-like",
            "潺潺 (rippling)": "rippling", "潺潺流淌 (ripples)": "ripples",
            "女声齐唱": "women unis.", "哼鸣“啊”": "“ah”",
            "男声领唱": "men", "大东北 motif": "motif (bars 31–32)",
            "G.P. (bar runs)": "G.P. (runs only)"}
HW_CLICK = [(1, 0, "click ♩ = 72"), (4, 8, "click follows rit."),
            (4, 12, "free — fermata"), (5, 0, "click ♩ = 128"),
            (74, 0, "click ♩ = 118"), (76, 0, "click follows allarg."),
            (76, 12, "free — fermata"), (77, 0, "click ♩ = 96"),
            (78, 8, "free — rit. to end")]
# one system per page, 4-5 bars, breaks at phrase starts
HW_PAGES = (5, 9, 14, 18, 22, 26, 31, 35, 39, 43, 48, 50, 52, 56, 58, 62, 66,
            70, 74)
# group name, parts, symbol, barlines through the group
HW_GROUPS = [("Woodwinds", ["picc", "fl", "ob", "cl", "bsn"], "bracket", True),
             ("Brass", ["hn1", "hn2", "tpt", "tbn", "tba"], "bracket", True),
             ("Percussion", ["timp", "glk"], "bracket", True),
             ("Choir", list(CHOIR), "bracket", False),
             ("Strings", ["vn1", "vn2", "va", "vc", "cb"], "bracket", True)]
# written-to-sounding transposition of the parts extracted from the C score
HW_FOR_PART = {"cl": (-2, -3), "hn1": (-4, -7), "hn2": (-4, -7),
               "tpt": (-1, -2)}
# Sibelius maps instruments by name: keep its stock names in <part-name>
# and show the session names through <part-name-display>
HW_STOCK = {"picc": "Piccolo", "fl": "Flute", "ob": "Oboe",
            "cl": "Clarinet in A", "bsn": "Bassoon", "hn1": "Horn in F",
            "hn2": "Horn in F", "tpt": "Trumpet in B♭", "tbn": "Trombone",
            "tba": "Tuba", "timp": "Timpani", "glk": "Glockenspiel",
            "hpr": "Harp", "sop": "Soprano", "alt": "Alto", "ten": "Tenor",
            "bas": "Bass", "vn1": "Violin I", "vn2": "Violin II",
            "va": "Viola", "vc": "Violoncello", "cb": "Contrabass"}
HW_CUE = "1M1"
# 11 x 17 in (tabloid) portrait, 5 mm staves (MOLA minimum is 4 mm):
# tenths = mm / 5 * 40; 0.5 in margins
HW_PAGE = ("5", 2235, 3454)
HW_MARGIN = 102


def hollywood_score(parsed, cscore=True):
    """cscore=True: notes at concert pitch (MusicXML 4.0 concert score).
    cscore=False: the same layout written for transposing instruments with
    <transpose>, the encoding every Sibelius version imports reliably; the
    user switches Sibelius to concert pitch after opening."""
    sc = stream.Score()
    score_meta(sc, "Score in C")
    objs = {}
    for p in PARTS:
        cls = stream.PartStaff if p["id"] in ("hpr", "hpl") else stream.Part
        objs[p["id"]] = make_m21(p, parsed[p["id"]], top=p["id"] == "picc",
                                 staff_cls=cls,
                                 mode="cscore" if cscore else "trans",
                                 names=HW_NAMES[p["id"]],
                                 rehearsal={}, sections=HW_SECTIONS,
                                 timings=cscore, hw=True)
        sc.insert(0, objs[p["id"]])
    for name, ids, sym, through in HW_GROUPS:
        g = layout.StaffGroup([objs[i] for i in ids], name=name, symbol=sym)
        g.barTogether = through
        sc.insert(0, g)
    g = layout.StaffGroup([objs["hpr"], objs["hpl"]], name="Harp",
                          symbol="brace")
    g.barTogether = True
    sc.insert(0, g)
    return sc


def _credit(words, x, y, size, justify="left", valign="top", ctype=None,
            weight=None):
    c = ET.Element("credit", page="1")
    if ctype:
        ET.SubElement(c, "credit-type").text = ctype
    w = ET.SubElement(c, "credit-words", {
        "default-x": str(x), "default-y": str(y), "font-size": str(size),
        "justify": justify, "valign": valign})
    if weight:
        w.set("font-weight", weight)
    w.text = words
    return c


def polish_hollywood(path, ids, cscore=True):
    """Score in C on 11x17 paper: title block with cue number, bar numbers
    on every bar, MusicXML 4.0 concert-score with the parts' transpositions,
    B-flat in the trumpet name."""
    # the reading copy / PDF shows the click changes as text instead of a
    # stack of metronome marks
    polish(path, ids, breaks=(), page=HW_PAGE, top_gap=300, margin=HW_MARGIN,
           page_breaks=HW_PAGES, tempo_sounds=not cscore)
    tree = ET.parse(path)
    r = tree.getroot()
    for c in r.findall("credit"):
        r.remove(c)
    for g in r.iter("part-group"):
        for x in g.findall("group-name"):
            g.remove(x)
    _, W, Hh = HW_PAGE
    dur = sec_at(NBARS * BAR16)
    credits = [
        _credit(f"{HW_CUE}\nSCORE IN C", HW_MARGIN, Hh - HW_MARGIN, 16,
                weight="bold"),
        _credit("大东北我的家乡", W // 2, Hh - HW_MARGIN, 24, "center",
                ctype="title"),
        _credit("Da Dongbei, Wo De Jiaxiang · Symphonic Orchestra & SATB "
                "Choir", W // 2, Hh - HW_MARGIN - 105, 12, "center",
                ctype="subtitle"),
        _credit(f"Music & Lyrics: 刘旗\n"
                f"Orchestra: Instrument X · Choir: ACE Studio\n"
                f"♩ = 72 / 128 · F → G · {int(dur // 60)}:{dur % 60:04.1f}",
                W - HW_MARGIN, Hh - HW_MARGIN, 9, "right", ctype="composer"),
    ]
    at = list(r).index(r.find("part-list"))
    for i, c in enumerate(credits):
        r.insert(at + i, c)
    d = r.find("defaults")
    if cscore and d.find("concert-score") is None:
        d.insert(list(d).index(d.find("scaling")) + 1,
                 ET.Element("concert-score"))
    pid_of = dict(zip([sp.get("id") for sp in r.iter("score-part")], ids))
    for sp in r.iter("score-part"):
        pid = pid_of[sp.get("id")]
        show, show_ab = HW_NAMES[pid]
        pn, pa = sp.find("part-name"), sp.find("part-abbreviation")
        if not cscore:   # Sibelius copy: stock name for instrument mapping
            pn.text = HW_STOCK[pid]
        if pn.text == show and "♭" not in show:
            continue
        for tag, ref, text in (("part-name-display", pn, show),
                               ("part-abbreviation-display", pa, show_ab)):
            disp = ET.Element(tag)
            if text.endswith(" in B♭"):
                ET.SubElement(disp, "display-text").text = text[:-1]
                ET.SubElement(disp, "accidental-text").text = "flat"
            else:
                ET.SubElement(disp, "display-text").text = text
            sp.insert(list(sp).index(ref) + 1, disp)
    # Chinese lyrics need a CJK font in Sibelius' Lyrics text style
    lf = ET.Element("lyric-font", {"font-family": "PingFang SC",
                                   "font-size": "10"})
    last = max(i for i, x in enumerate(d)
               if x.tag in ("scaling", "concert-score", "page-layout",
                            "system-layout", "staff-layout", "appearance",
                            "music-font", "word-font"))
    d.insert(last + 1, lf)
    for k, part in enumerate(r.findall("part")):
        pid = pid_of[part.get("id")]
        m1 = part.find("measure")
        if k == 0:
            pr = m1.find("print")
            if pr is None:
                pr = ET.Element("print")
                m1.insert(0, pr)
            mn = ET.SubElement(pr, "measure-numbering")
            mn.text = "measure"
        if cscore and pid in HW_FOR_PART:
            at_ = m1.find("attributes")
            fp = ET.SubElement(at_, "for-part")
            pt = ET.SubElement(fp, "part-transpose")
            dia, chrom = HW_FOR_PART[pid]
            ET.SubElement(pt, "diatonic").text = str(dia)
            ET.SubElement(pt, "chromatic").text = str(chrom)
    # the Sibelius copy uses nothing from 4.0, so it is labelled 3.1 and
    # Sibelius opens it without the "newer MusicXML version" warning
    version = "4.0" if cscore else "3.1"
    r.set("version", version)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    xml = open(path, encoding="utf-8").read()
    xml = re.sub(r"<!DOCTYPE[^>]*>\n?", "", xml)
    xml = xml.replace(
        "?>\n",
        "?>\n<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD "
        f"MusicXML {version} Partwise//EN\" "
        "\"http://www.musicxml.org/dtds/partwise.dtd\">\n", 1)
    open(path, "w", encoding="utf-8").write(xml)


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
def merged_notes(events):
    """Merge tied notes: list of dict(start, dur, pitches, lyric, melisma,
    legato, grace, accent, stacc, trem, bar).  A tie continues only into
    the same pitches starting where the note ends, so the two harp staves
    can be merged into one event list.  legato: slurred into the next
    note."""
    out, open_, in_slur = [], {}, False
    for e in events:
        if e["pitches"] is None:
            in_slur = False
            continue
        key = tuple(e["pitches"])
        cur = open_.pop(key, None)
        if cur is not None and cur["start"] + cur["dur"] == e["abs"]:
            cur["dur"] += e["dur"]
            cur["tie"] = e["tie"]
            if e["tie"]:
                open_[key] = cur
            if e["slur_end"]:
                in_slur = False
                cur["legato"] = False
            continue
        cur = dict(start=e["abs"], dur=e["dur"], pitches=e["pitches"],
                   lyric=e["lyric"], tie=e["tie"], grace=e["grace"],
                   accent=e["accent"], stacc=e["stacc"], trem=e["trem"],
                   bar=e["bar"], melisma=(e["lyric"] is None and in_slur),
                   legato=(in_slur or e["slur_start"]) and not e["slur_end"])
        out.append(cur)
        if e["tie"]:
            open_[key] = cur
        if e["slur_start"]:
            in_slur = True
        if e["slur_end"]:
            in_slur = False
    return out


def dyn_curve(p):
    total = NBARS * BAR16
    pts = sorted(((b - 1) * BAR16 + s, VEL[m]) for b, s, m in p["dyn"])
    if not pts:
        pts = [(0, VEL["mf"])]
    v = [pts[0][1]] * total
    for i, (a, val) in enumerate(pts):
        end = pts[i + 1][0] if i + 1 < len(pts) else total
        for t in range(a, end):
            v[t] = val
    for b, s, b2, s2, kind in p["hair"]:
        a, z = (b - 1) * BAR16 + s, (b2 - 1) * BAR16 + s2
        v0 = v[a]
        nxt = [val for t, val in pts if t > z]
        v1 = nxt[0] if nxt else v0 + (-14 if kind == "dim" else 14)
        if kind == "cresc" and v1 <= v0:
            v1 = v0 + 14
        if kind == "dim" and v1 >= v0:
            v1 = v0 - 12
        for t in range(a, z + 1):
            v[t] = round(v0 + (v1 - v0) * (t - a) / max(1, z - a))
    return v


REHEARSAL_ASCII = {1: "Prologue", 5: "A Intro", 14: "B Verse",
                   31: "C Chorus 1", 48: "D Interlude", 58: "E Chorus 2 (G)",
                   74: "Coda"}


def tempo_track(title, ascii_meta=False):
    marks = REHEARSAL_ASCII if ascii_meta else REHEARSAL
    ab = [(0, mido.MetaMessage("track_name", name=title)),
          (0, mido.MetaMessage("time_signature", numerator=4, denominator=4))]
    for b, k in KEYS.items():
        ab.append(((b - 1) * BAR16 * T16,
                   mido.MetaMessage("key_signature", key=k)))
    for b, s, bpm in TEMPI:
        ab.append((((b - 1) * BAR16 + s) * T16,
                   mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))))
    for b, name in marks.items():
        ab.append(((b - 1) * BAR16 * T16,
                   mido.MetaMessage("marker", text=name)))
    ab.sort(key=lambda x: x[0])
    tr, last = mido.MidiTrack(), 0
    for t, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


GRACE_T = T16 // 2
TRACK_NAMES = {"sop": "Soprano 女高音", "alt": "Alto 女低音",
               "ten": "Tenor 男高音", "bas": "Bass 男低音",
               "mel": "Melody 主旋律"}


def part_track(p, events, ch, lyrics=True, cc=True, name=None, program=True,
               detache=False):
    """detache: notes outside slurs end a little early (Instrument X reads
    touching notes as legato, overlapping ones as a second voice)."""
    notes = merged_notes(events)
    vel = dyn_curve(p)
    sung = p["id"] in CHOIR or p["id"] == "mel"
    ab = [(0, 0, mido.MetaMessage(
        "track_name", name=name or TRACK_NAMES.get(p["id"], p["name"])))]
    if program:
        ab.append((0, 1, mido.Message("program_change", channel=ch,
                                      program=p["program"])))
    if cc:
        for t in range(0, NBARS * BAR16, 2):
            if t == 0 or vel[t] != vel[t - 2]:
                val = min(127, 20 + vel[t])
                for c in (1, 11):
                    ab.append((t * T16, 2, mido.Message(
                        "control_change", channel=ch, control=c, value=val)))
    for i, n in enumerate(notes):
        on = n["start"] * T16
        off = (n["start"] + n["dur"]) * T16
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        if nxt and nxt["start"] * T16 == off and \
                set(nxt["pitches"]) & set(n["pitches"]):
            off -= 12 if n["dur"] > 2 else 24
        elif detache and nxt and nxt["start"] * T16 == off and \
                not n["legato"]:
            off -= max(20, min(60, (off - on) // 10))
        if in_pizz(p, n["bar"]):
            off = min(off, on + 100)
        elif n["stacc"]:
            off = on + max(40, (off - on) // 2)
        v = vel[min(n["start"], len(vel) - 1)] + (ACCENT if n["accent"] else 0)
        v = max(1, min(127, v))
        syl = n["lyric"] if n["lyric"] else ("-" if n["melisma"] else None)
        if n["grace"]:
            gp = midi_of(n["grace"])
            ab.append((on, 5, mido.Message("note_on", channel=ch, note=gp,
                                           velocity=v)))
            if lyrics and sung:
                ab.append((on, 4, mido.MetaMessage(
                    "lyrics", text=syl if syl else "-")))
            ab.append((on + GRACE_T, 3, mido.Message(
                "note_off", channel=ch, note=gp, velocity=0)))
            on += GRACE_T
            syl = "-"
        if lyrics and sung and syl:
            ab.append((on, 4, mido.MetaMessage("lyrics", text=syl)))
        if n["trem"] and p["id"] == "timp":   # a roll: 32nd strokes
            k, t = 0, on
            while t < off - 10:
                vv = vel[min(n["start"] + (t - on) // T16, len(vel) - 1)]
                vv = max(1, min(127, vv - 10 + (6 if k % 2 == 0 else 0)))
                for pit in n["pitches"]:
                    ab.append((t, 5, mido.Message("note_on", channel=ch,
                                                  note=midi_of(pit),
                                                  velocity=vv)))
                    ab.append((t + GRACE_T - 5, 3, mido.Message(
                        "note_off", channel=ch, note=midi_of(pit),
                        velocity=0)))
                t += GRACE_T
                k += 1
            continue
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


def track_events(parsed, pid):
    """Harp: both staves on one track."""
    if pid == "hp":
        return sorted(parsed["hpr"] + parsed["hpl"],
                      key=lambda e: (e["abs"], e["pitches"] is None))
    return parsed[pid]


MEL_PART = dict(id="mel", name="Melody", program=52, dyn=D(VOX_DYN),
                hair=HP(VOX_HAIR), pizz=[])


def write_midi(path, items, parsed, lyrics=True, charset="utf-8", cc=True,
               title=None, single_channel=False, ascii_meta=False,
               own_channels=False, program=True):
    """items: list of part ids ('hp' = harp, 'mel' = melody guide).
    ascii_meta: English track names and markers only (Instrument X).
    own_channels: every track on its own channel (skipping 10), so hosts
    that route by channel keep each track's CC curves apart."""
    free = iter([c for c in range(16) if c != 9])
    mf = mido.MidiFile(type=1, ticks_per_beat=TPQ, charset=charset)
    mf.tracks.append(tempo_track(
        title or ("Da Dongbei Wo De Jiaxiang" if ascii_meta else NAME),
        ascii_meta))
    for pid in items:
        if pid == "mel":
            p, evs = MEL_PART, parsed["mel"]
            ch = 0 if single_channel else 13
        else:
            p = PBY["hpr" if pid == "hp" else pid]
            evs = track_events(parsed, pid)
            ch = 0 if single_channel else p["ch"]
        if own_channels:
            ch = next(free)
        if pid == "hp":
            p = dict(p, name="Harp")
        name = None
        if ascii_meta and p.get("ix"):
            name = f"{p['name']} (Instrument X: {p['ix']})"
        elif ascii_meta:
            name = "Melody" if pid == "mel" else p["name"]
        mf.tracks.append(part_track(
            p, evs, ch, lyrics=lyrics, cc=cc, name=name, program=program,
            detache=ascii_meta and pid not in CHOIR and pid != "mel"))
    mf.save(path)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def check(parsed):
    problems = []
    for p in PARTS:
        lo, hi = (midi_of(x) for x in p["rng"])
        for e in parsed[p["id"]]:
            for pit in e["pitches"] or []:
                if not lo <= midi_of(pit) <= hi:
                    problems.append(f"{p['id']} m{e['bar']} {pit} out of range")
    # minor 2nds / minor 9ths between parts (runs of 16ths exempt)
    grid = {}
    for pid, evs in parsed.items():
        if pid == "mel":
            continue
        held = False
        for e in evs:
            if e["pitches"] is None:
                held = False
                continue
            for t in range(e["abs"], e["abs"] + e["dur"]):
                for pit in e["pitches"]:
                    grid.setdefault(t, []).append(
                        (pid, midi_of(pit), pit, t == e["abs"] and not held,
                         e["dur"] >= 2 or e["tie"] or held))
            held = e["tie"]
    clashes = set()
    for t, snd in sorted(grid.items()):
        for i in range(len(snd)):
            for j in range(i + 1, len(snd)):
                a, b = snd[i], snd[j]
                if a[0] == b[0] or not (a[3] or b[3]) or not (a[4] and b[4]):
                    continue
                lo_, hi_ = sorted((a, b), key=lambda x: x[1])
                if (hi_[1] - lo_[1]) % 12 == 1:
                    clashes.add(f"m{t // 16 + 1}.{t % 16:02d} "
                                f"{lo_[0]}:{lo_[2]} < {hi_[0]}:{hi_[2]}")
    # parallel fifths / octaves inside the choir
    def line(evs):
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

    def at(ln, t):
        cur = None
        for s, p in ln:
            if s > t:
                break
            cur = p
        return cur
    parallels = []
    lines = {c: line(parsed[c]) for c in CHOIR}
    for i in range(4):
        for j in range(i + 1, 4):
            a, b = lines[CHOIR[i]], lines[CHOIR[j]]
            prev = None
            for t in sorted({t for t, _ in a} | {t for t, _ in b}):
                pa, pb = at(a, t), at(b, t)
                if None in (pa, pb):
                    prev = None
                    continue
                if prev and pa != prev[0] and pb != prev[1]:
                    iv0, iv1 = abs(prev[0] - prev[1]) % 12, abs(pa - pb) % 12
                    unison = pa == pb and prev[0] == prev[1]  # one line
                    if (pa - prev[0]) * (pb - prev[1]) > 0 and iv0 == iv1 \
                            and iv1 in (0, 7) and not unison:
                        parallels.append(
                            f"m{t // 16 + 1}.{t % 16:02d} {CHOIR[i]}/"
                            f"{CHOIR[j]} {'P8' if iv1 == 0 else 'P5'}")
                prev = (pa, pb)
    return problems, sorted(clashes, key=lambda s: (int(s[1:].split(".")[0]),
                                                    s)), parallels


# ---------------------------------------------------------------------------
# Lyric subtitles
# ---------------------------------------------------------------------------
CHORUS_LINES = ["大东北 是我的家乡", "唢呐吹出了 美美的模样",
                "哥们相聚 必须整二两", "醉了月亮 暖了我心肠",
                "大东北 是我的家乡", "我就在这嘎达 土生土长",
                "东北人的情 东北人的爱", "贼拉拉的爱你呀 我的家乡"]
SUB_LINES = (["风吹麦浪 稻花儿香", "黑土地养育着 咱的爹娘",
              "每年的冬天 都大雪飞扬", "热热的炕头上 唠唠家常",
              "蓝蓝的天上 白云飘荡", "清澈的小河在 潺潺流淌",
              "东北人爱吃那 酸菜血肠", "秧歌扭起来 人们喜洋洋"]
             + CHORUS_LINES * 2
             + ["我的家乡", "贼拉拉的爱你呀", "我的家乡"])
SUB_LEAD, SUB_TAIL = 0.2, 1.5


def sec_at(abs16):
    marks = [((b - 1) * BAR16 + s, bpm) for b, s, bpm in TEMPI]
    t = 0.0
    for i, (a, bpm) in enumerate(marks):
        if abs16 <= a:
            break
        end = marks[i + 1][0] if i + 1 < len(marks) else abs16
        t += (min(abs16, end) - a) * 15.0 / bpm
    return t


def syllables(events):
    out = []
    for e in events:
        if e["pitches"] is None:
            continue
        if e["lyric"]:
            out.append([e["lyric"], e["abs"], e["abs"] + e["dur"]])
        elif out:
            out[-1][2] = e["abs"] + e["dur"]
    return out


def write_srt(path, events):
    syl = syllables(events)
    lines, i = [], 0
    for text in SUB_LINES:
        n = len(text.replace(" ", ""))
        chunk = syl[i:i + n]
        assert "".join(s[0] for s in chunk) == text.replace(" ", ""), text
        lines.append((text, sec_at(chunk[0][1]), sec_at(chunk[-1][2])))
        i += n
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


# ---------------------------------------------------------------------------
# Previews (MuseScore 3, FluidSynth, ffmpeg) and the 干活 hand-off folder
# ---------------------------------------------------------------------------
# MuseScore ignores the page size and <measure-numbering> in MusicXML, so the
# Hollywood preview is rendered through a .mscx with these style settings.
MS_STYLE_HOLLYWOOD = {
    "pageWidth": "11", "pageHeight": "17", "pagePrintableWidth": "10",
    "pageEvenLeftMargin": "0.5", "pageOddLeftMargin": "0.5",
    "pageEvenTopMargin": "0.5", "pageEvenBottomMargin": "0.5",
    "pageOddTopMargin": "0.5", "pageOddBottomMargin": "0.5",
    "pageTwosided": "0", "Spatium": "1.4",
    "showMeasureNumber": "1", "showMeasureNumberOne": "1",
    "measureNumberInterval": "1", "measureNumberSystem": "0",
    "measureNumberFontSize": "14", "measureNumberFontStyle": "1",
    "measureNumberFrameType": "0", "measureNumberHPlacement": "1",
    "enableVerticalSpread": "1", "maxSystemSpread": "40",
    "maxStaffSpread": "8",
}


def _mscore(*args):
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    subprocess.run(["mscore3", *args], env=env, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render_pdf(xml, pdf, style=None):
    if not style:
        _mscore("-o", pdf, xml)
        return
    tmp = os.path.join(tempfile.gettempdir(), "dadongbei_style.mscx")
    _mscore("-o", tmp, xml)
    s = open(tmp, encoding="utf-8").read()
    for k in style:
        s = re.sub(rf"\s*<{k}>[^<]*</{k}>", "", s)
    s = s.replace("<Style>", "<Style>" + "".join(
        f"\n      <{k}>{v}</{k}>" for k, v in style.items()), 1)
    open(tmp, "w", encoding="utf-8").write(s)
    _mscore("-o", pdf, tmp)


def render_all():
    base = os.path.join(OUT, f"{NAME}_交响合唱")
    render_pdf(base + "_好莱坞C调总谱_阅读版.musicxml",
               base + "_好莱坞C调总谱_预览.pdf", MS_STYLE_HOLLYWOOD)
    render_pdf(base + "_总谱.musicxml", base + "_总谱预览.pdf")
    render_pdf(base + "_合唱四声部.musicxml",
               os.path.join(OUT, f"{NAME}_合唱四声部_预览.pdf"))
    wav = os.path.join(tempfile.gettempdir(), "dadongbei_preview.wav")
    subprocess.run(["fluidsynth", "-ni", "-g", "0.5", "-F", wav,
                    "/usr/share/sounds/sf2/FluidR3_GM.sf2", PREVIEW],
                   check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af",
                    "loudnorm=I=-16:TP=-1.5", "-b:a", "160k",
                    os.path.join(OUT, "粗略试听_GM音色_非最终效果.mp3")],
                   check=True)


def lyric_text(events):
    """One token per sung note in ACE's lyric-input syntax ('-' continues
    the previous syllable), one line per section, for pasting into ACE if
    the imported lyrics come in garbled."""
    notes = merged_notes(events)
    starts = sorted(REHEARSAL)
    lines, cur, sec = [], [], None
    for n in notes:
        b = n["start"] // BAR16 + 1
        s_ = max(x for x in starts if x <= b)
        if sec is not None and s_ != sec and cur:
            lines.append(f"[{REHEARSAL[sec]}, m{sec}] " + " ".join(cur))
            cur = []
        sec = s_
        if n["grace"]:
            cur.append(n["lyric"] or "-")
            cur.append("-")
        else:
            cur.append(n["lyric"] or "-")
    if cur:
        lines.append(f"[{REHEARSAL[sec]}, m{sec}] " + " ".join(cur))
    return ("# 每个音符一个字，'-' 表示接着唱上一个字（拖腔）。\n"
            "# 粘贴时只复制方括号后面的部分，从该段第一个音符开始粘贴。\n"
            + "\n".join(lines) + "\n")


FLAT_BPM = 120


def flatten_tempo(src, dst, bpm=FLAT_BPM):
    """Re-time a MIDI file to one constant tempo so every event keeps its
    real time in seconds: ritardandos and fermatas are baked into the note
    positions.  For hosts that ignore tempo maps (Instrument X's MIDI
    import): with the project at `bpm`, the audio lines up second for
    second with the choir, but the bar lines no longer match the score."""
    mf = mido.MidiFile(src)
    tempo_map = []   # (tick, microseconds per beat)
    for tr in mf.tracks:
        t = 0
        for m in tr:
            t += m.time
            if m.type == "set_tempo":
                tempo_map.append((t, m.tempo))
    tempo_map.sort()

    def seconds(tick):
        sec, last_t, last_us = 0.0, 0, tempo_map[0][1]
        for t, us in tempo_map:
            if t >= tick:
                break
            sec += (t - last_t) * last_us / 1e6 / mf.ticks_per_beat
            last_t, last_us = t, us
        return sec + (tick - last_t) * last_us / 1e6 / mf.ticks_per_beat

    out = mido.MidiFile(type=mf.type, ticks_per_beat=mf.ticks_per_beat,
                        charset=mf.charset)
    per_sec = bpm / 60 * mf.ticks_per_beat
    for k, tr in enumerate(mf.tracks):
        ab, t = [], 0
        for m in tr:
            t += m.time
            if m.type in ("set_tempo", "end_of_track"):
                continue
            ab.append((round(seconds(t) * per_sec), m))
        if k == 0:
            ab.insert(0, (0, mido.MetaMessage("set_tempo",
                                              tempo=mido.bpm2tempo(bpm))))
        new, last = mido.MidiTrack(), 0
        for tt, m in ab:
            new.append(m.copy(time=tt - last))
            last = tt
        new.append(mido.MetaMessage("end_of_track", time=0))
        out.tracks.append(new)
    out.save(dst)


GANHUO = os.path.join(os.path.dirname(HERE), "干活", NAME)


def export_ganhuo(parsed):
    """The user's hand-off folder: only the finished files, grouped by use."""
    if os.path.isdir(GANHUO):
        shutil.rmtree(GANHUO)
    ix = os.path.join(GANHUO, "1_InstrumentX乐队MIDI")
    opt = os.path.join(ix, "可选_非InstrumentX音源")
    ch = os.path.join(GANHUO, "2_合唱四声部合并_带歌词MIDI")
    sib = os.path.join(GANHUO, "3_西贝柳斯总谱_好莱坞C调格式")
    for d in (ix, opt, ch, sib):
        os.makedirs(d)
    ix_parts = [p for p in PARTS if p["ix"]]
    write_midi(os.path.join(ix, "00_全乐队15轨_InstrumentX.mid"),
               [p["id"] for p in ix_parts], parsed, ascii_meta=True,
               own_channels=True)
    for k, p in enumerate(ix_parts, 1):
        write_midi(os.path.join(
            ix, f"{k:02d}_{p['name'].replace(' ', '')}_"
                f"{p['cn'].replace(' ', '')}_{p['ix'].replace(' ', '')}.mid"),
            [p["id"]], parsed, single_channel=True, ascii_meta=True)
    for pid, cn in (("hp", "竖琴"), ("glk", "钟琴"), ("timp", "定音鼓")):
        p = PBY["hpr" if pid == "hp" else pid]
        write_midi(os.path.join(opt, f"{p['name']}_{cn}.mid"), [pid], parsed,
                   single_channel=True, ascii_meta=True)
    xml_dir = os.path.join(ix, "MusicXML备用_每轨一个")
    os.makedirs(xml_dir)
    src = {f.split("_", 2)[1]: f for f in os.listdir(os.path.join(OUT, IX_DIR))
           if f.endswith(".musicxml")}
    for k, p in enumerate(ix_parts, 1):
        f = src[p["name"].replace(" ", "")]
        shutil.copy(os.path.join(OUT, IX_DIR, f), os.path.join(
            xml_dir, f"{k:02d}_{p['name'].replace(' ', '')}_"
                     f"{p['cn'].replace(' ', '')}.musicxml"))
    # the same files re-timed to a constant 120 BPM (see flatten_tempo)
    flat = os.path.join(ix, f"按秒对齐_固定{FLAT_BPM}BPM_备用")
    for root, _, files in os.walk(ix):
        if root.startswith(flat) or root.startswith(xml_dir):
            continue
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(root, f), ix)
            dst = os.path.join(flat, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            flatten_tempo(os.path.join(root, f), dst)
    for f, cs in ((f"{NAME}_合唱四声部合并_带歌词.mid", "utf-8"),
                  (f"{NAME}_合唱四声部合并_带歌词_GBK编码备用.mid", "gbk")):
        write_midi(os.path.join(ch, f), list(CHOIR), parsed, charset=cs,
                   own_channels=True, cc=False, program=False,
                   ascii_meta=True)
    shutil.copy(os.path.join(OUT, f"{NAME}_交响合唱_合唱四声部.musicxml"),
                os.path.join(ch, f"{NAME}_合唱四声部_MusicXML备用.musicxml"))
    mel = os.path.join(ch, "主旋律单轨_参考")
    os.makedirs(mel)
    for f, cs in ((f"{NAME}_主旋律单轨_带歌词.mid", "utf-8"),
                  (f"{NAME}_主旋律单轨_带歌词_GBK编码备用.mid", "gbk")):
        write_midi(os.path.join(mel, f), ["mel"], parsed, charset=cs,
                   cc=False, program=False, single_channel=True,
                   ascii_meta=True)
    lyr = os.path.join(ch, "歌词粘贴备用")
    os.makedirs(lyr)
    for k, c in enumerate(CHOIR, 1):
        with open(os.path.join(lyr, f"{k}_{PBY[c]['cn']}_歌词.txt"), "w",
                  encoding="utf-8") as fh:
            fh.write(lyric_text(parsed[c]))
    base = os.path.join(OUT, f"{NAME}_交响合唱")
    for src, dst in ((base + "_好莱坞总谱_西贝柳斯用.musicxml",
                      f"{NAME}_好莱坞总谱_西贝柳斯用.musicxml"),
                     (base + "_好莱坞C调总谱_预览.pdf",
                      f"{NAME}_好莱坞C调总谱_预览.pdf")):
        if os.path.exists(src):
            shutil.copy(src, os.path.join(sib, dst))
    readme = os.path.join(HERE, "干活说明.md")
    if os.path.exists(readme):
        shutil.copy(readme, os.path.join(GANHUO, "使用说明.md"))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
PREVIEW = os.path.join(tempfile.gettempdir(), "dadongbei_preview.mid")
IX_DIR = "InstrumentX分轨"
CHOIR_DIR = "合唱分轨"
ORCH = [p["id"] for p in PARTS if p["id"] not in CHOIR and p["id"] != "hpl"]


def orch_items():
    return ["hp" if x == "hpr" else x for x in ORCH]


def fname(p, k):
    tag = "" if p["ix"] else "非IX_"
    return f"{k:02d}_{tag}{p['name'].replace(' ', '')}_" \
        f"{p['cn'].replace(' ', '')}"


def main():
    parsed = {p["id"]: parse_part(p["data"]) for p in PARTS}
    parsed["mel"] = parse_part(MEL)
    problems, clashes, parallels = check(parsed)
    for x in problems:
        print("RANGE:", x)
    for x in clashes:
        print("CLASH:", x)
    for x in parallels:
        print("PARALLEL:", x)
    if "--check" in sys.argv:
        return
    os.makedirs(os.path.join(OUT, IX_DIR), exist_ok=True)
    os.makedirs(os.path.join(OUT, CHOIR_DIR), exist_ok=True)
    base = os.path.join(OUT, f"{NAME}_交响合唱")
    ids = [p["id"] for p in PARTS]
    staff_ids = [i for i in ids if i != "hpl"]

    # full score (transposing) for Sibelius
    sc = build_score(parsed)
    sc.write("musicxml", fp=base + "_总谱.musicxml")
    polish(base + "_总谱.musicxml", staff_ids)
    verify(base + "_总谱.musicxml", parsed, ids)
    check_xml_extras(base + "_总谱.musicxml", ids)

    # choir-only score for singers / checking the vocal lines
    cs = stream.Score()
    score_meta(cs, "四声部合唱")
    ps = [make_m21(PBY[c], parsed[c], top=c == "sop") for c in CHOIR]
    for x in ps:
        cs.insert(0, x)
    cs.insert(0, layout.StaffGroup(ps, name="Choir", symbol="bracket"))
    cs.write("musicxml", fp=base + "_合唱四声部.musicxml")
    polish(base + "_合唱四声部.musicxml", list(CHOIR), big=False,
           breaks=(5, 14, 22, 26, 31, 39, 48, 58, 66, 74), fermata_steps=True)
    check_xml_extras(base + "_合唱四声部.musicxml", list(CHOIR), True)

    # MIDI
    write_midi(base + "_全轨.mid", orch_items() + list(CHOIR), parsed)
    write_midi(base + "_管弦乐伴奏.mid", orch_items(), parsed)
    write_midi(os.path.join(OUT, f"{NAME}_合唱SATB_带歌词.mid"), list(CHOIR),
               parsed, own_channels=True, cc=False, program=False)
    write_midi(os.path.join(OUT, f"{NAME}_合唱SATB_带歌词_GBK编码备用.mid"),
               list(CHOIR), parsed, charset="gbk", own_channels=True,
               cc=False, program=False)
    write_midi(os.path.join(OUT, f"{NAME}_主旋律_带歌词.mid"), ["mel"], parsed,
               cc=False, single_channel=True)
    for k, c in enumerate(CHOIR, 1):
        p = PBY[c]
        stem = os.path.join(OUT, CHOIR_DIR, f"{k}_{p['cn']}_{p['name']}")
        write_midi(stem + "_带歌词.mid", [c], parsed, single_channel=True,
                   cc=False)
        s1 = single_part_score(p, parsed[c], subtitle=p["cn"])
        s1.write("musicxml", fp=stem + ".musicxml")
        polish(stem + ".musicxml", [c], big=False, breaks=(),
               fermata_steps=True)
        check_xml_extras(stem + ".musicxml", [c], True)

    # Instrument X: one MIDI + one concert-pitch MusicXML per track
    k = 0
    for p in PARTS:
        if p["id"] in CHOIR or p["id"] == "hpl":
            continue
        k += 1
        stem = os.path.join(OUT, IX_DIR, fname(p, k))
        item = "hp" if p["id"] == "hpr" else p["id"]
        write_midi(stem + ".mid", [item], parsed, single_channel=True,
                   ascii_meta=True)
        if p["id"] == "hpr":
            s1 = stream.Score()
            score_meta(s1, "Harp")
            a = make_m21(PBY["hpr"], parsed["hpr"], top=True,
                         staff_cls=stream.PartStaff)
            z = make_m21(PBY["hpl"], parsed["hpl"],
                         staff_cls=stream.PartStaff)
            s1.insert(0, a)
            s1.insert(0, z)
            s1.insert(0, layout.StaffGroup([a, z], name="Harp",
                                           symbol="brace"))
            s1.write("musicxml", fp=stem + ".musicxml")
            polish(stem + ".musicxml", ["hpr"], big=False, breaks=(),
                   fermata_steps=True)
            check_xml_extras(stem + ".musicxml", ["hpr", "hpl"], True)
        else:
            s1 = single_part_score(p, parsed[p["id"]], concert=True)
            s1.write("musicxml", fp=stem + ".musicxml")
            polish(stem + ".musicxml", [p["id"]], big=False, breaks=(),
                   fermata_steps=True)
            check_xml_extras(stem + ".musicxml", [p["id"]], True)

    # Hollywood conductor score (score in C) for Sibelius
    for cs_, suffix in ((True, "_好莱坞C调总谱_阅读版.musicxml"),
                        (False, "_好莱坞总谱_西贝柳斯用.musicxml")):
        hw = base + suffix
        hollywood_score(parsed, cs_).write("musicxml", fp=hw)
        polish_hollywood(hw, staff_ids, cs_)
        verify(hw, parsed, ids)
        check_xml_extras(hw, ids, tempo=not cs_)

    write_srt(os.path.join(OUT, f"{NAME}_歌词字幕.srt"), parsed["mel"])
    # preview MIDI for the rough GM render (velocity only, no CC curves,
    # which would fight each other on the shared GM channels)
    write_midi(PREVIEW, orch_items() + list(CHOIR), parsed, cc=False)
    if "--render" in sys.argv:
        render_all()
    export_ganhuo(parsed)
    print("written to", OUT, "and", GANHUO)


if __name__ == "__main__":
    main()
