#!/usr/bin/env python3
"""诀别书（全曲）— 弦乐五重奏 编配生成器

Source: the piano chart of 诀别书 (作曲 邓垚, 钢琴谱 制谱 张科桔), 52 bars,
F major / D minor, 4/4, quarter = 112.  The chart is transcribed in
transcription/piano.json (see transcription/README.md); this file holds the
arrangement for Violin I, Violin II, Viola, Violoncello and Contrabass and
generates, from this one source of truth:

  * output/诀别书_弦乐五重奏.musicxml    Sibelius project (MusicXML 4.0,
                                         Score in C, contrabass written an
                                         octave up with <transpose>)
  * output/诀别书_弦乐五重奏_全轨.mid     all five parts, for ACE Studio
                                         (String Section) with the tempo map
  * output/ACE分轨MIDI/*.mid              one MIDI per part
  * the Hollywood-standard score and parts are engraved by engrave.py

Token syntax (durations in 16th notes, one string per bar, each bar = 16):
  C5/4        note C5, a quarter          D4+A4/8   double stop, a half
  r/4         rest                        A4/2~     tie into the next note
  flags after the duration, any order:
    >  accent     *  staccato / spiccato     _  tenuto     ^  marcato
    %  measured tremolo (16ths)             !  fermata
  (G4/1 A4/1) slur start / slur end        g:G4      grace note before
Pitches are SOUNDING pitches for every part (the contrabass is written an
octave higher only in the notation).

Usage:
  python3 build.py --check            ranges, clashes, parallels, double
                                      stops, melody / bass fidelity
  python3 build.py --check --bars 17-24   the same, only those bars
  python3 build.py                    MusicXML + MIDI
  python3 build.py --pdf              also engrave the score and parts
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
NAME = "诀别书"
NBARS = 52
BAR16 = 16
TPQ = 480
T16 = TPQ // 4

# Credits. Standing rule from the user: 改编 and 制谱 are always 花开当富贵.
TITLE = "诀别书"
TITLE_LATIN = "Jué Bié Shū"
TITLE_EN = "A Letter of Farewell"
SUBTITLE = "弦乐五重奏"
SUBTITLE_EN = "for String Quintet"
COMPOSER = "邓垚"
SOURCE_CHART = "张科桔"          # engraver of the piano chart we arranged from
ARRANGER = "花开当富贵"
ENGRAVER = "花开当富贵"
YEAR = "2026"
KEY_TEXT = "F Major · F 大调（d 小调色彩）"

# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------
_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_NAMES = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]


def midi_of(p):
    m = re.fullmatch(r"([A-G])(#|##|b|bb)?(-?\d)", p)
    if not m:
        raise ValueError(p)
    s, acc, octv = m.groups()
    v = _STEP[s] + {"#": 1, "##": 2, "b": -1, "bb": -2}.get(acc or "", 0)
    return 12 * (int(octv) + 1) + v


def name_of(n):
    return f"{_NAMES[n % 12]}{n // 12 - 1}"


def shift(p, semis):
    """Transpose a pitch name by octaves, keeping its spelling."""
    assert semis % 12 == 0
    s, acc, o = re.fullmatch(r"([A-G])(#|##|b|bb)?(-?\d)", p).groups()
    return f"{s}{acc or ''}{int(o) + semis // 12}"


def m21_name(p):
    s, acc, o = re.fullmatch(r"([A-G])(#|##|b|bb)?(-?\d)", p).groups()
    return s + (acc or "").replace("b", "-") + o


# ---------------------------------------------------------------------------
# Form, tempo and rehearsal marks
# ---------------------------------------------------------------------------
# >>> FORM (filled in by the arrangement plan)
REHEARSAL = {}          # bar -> (letter, "English", "中文"); bar 1 gets only a title
INTRO_TITLE = ("Intro", "前奏")
TEMPO_MARK = ("Moderato con moto", 112)   # printed at bar 1
TEMPI = [(1, 0, 112)]   # MIDI tempo map: (bar, 16th, bpm)
TEMPO_TEXT = []         # printed tempo words: (bar, 16th, text, bpm or None)
SYSTEM_BREAKS = ()      # bars that start a new system in the full score
PAGE_BREAKS = ()        # bars that start a new page in the full score
PART_BREAKS = {}        # part id -> bars that start a new line in the part
CLEFS = {}              # part id -> [(bar, 16th, "tenor" / "treble" / ...)]
# <<< FORM

# ---------------------------------------------------------------------------
# The arrangement
# ---------------------------------------------------------------------------
REST = "r/16"
# >>> DATA (merged from the section drafts; edit here)
VN1 = {}
VN2 = {}
VA = {}
VC = {}
CB = {}
DYN = {"vn1": [], "vn2": [], "va": [], "vc": [], "cb": []}
HAIR = {"vn1": [], "vn2": [], "va": [], "vc": [], "cb": []}
TEXT = {"vn1": [], "vn2": [], "va": [], "vc": [], "cb": []}
# <<< DATA

# >>> CHECK-ALLOW (intentional exceptions, each with a reason)
# (bar, part, part): minor 2nd / minor 9th that is meant
CLASH_ALLOW = {}
# (part, part, first bar, last bar): intentional octave / unison doublings,
# excluded from the parallel-octave check
DOUBLINGS = []
# bar -> [(part, octave shift in semitones)]: who carries the chart's melody
MELODY = {}
# bars where the melody part deliberately departs from the chart: reason
MELODY_FREE = {}
# bars / half bars where the bass deliberately departs from the chart
# ((bar, half) -> reason, half = 0 or 1)
BASS_FREE = {}
# <<< CHECK-ALLOW

# Optional drafts overlay (used while the sections are being written):
# JUEBIESHU_DRAFTS=dir makes every dir/*.py that defines some of VN1 .. CB,
# DYN, HAIR, TEXT, MELODY, CLASH_ALLOW, DOUBLINGS, MELODY_FREE, BASS_FREE
# override / extend the data above.
_DRAFTS = os.environ.get("JUEBIESHU_DRAFTS")
if _DRAFTS:
    import importlib.util
    for _f in sorted(os.listdir(_DRAFTS)):
        if not _f.endswith(".py"):
            continue
        _spec = importlib.util.spec_from_file_location(
            "draft_" + _f[:-3], os.path.join(_DRAFTS, _f))
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        for _k, _tgt in (("VN1", VN1), ("VN2", VN2), ("VA", VA), ("VC", VC),
                         ("CB", CB), ("MELODY", MELODY),
                         ("CLASH_ALLOW", CLASH_ALLOW),
                         ("MELODY_FREE", MELODY_FREE),
                         ("BASS_FREE", BASS_FREE), ("CLEFS", CLEFS)):
            _tgt.update(getattr(_mod, _k, {}))
        for _k, _tgt in (("DYN", DYN), ("HAIR", HAIR), ("TEXT", TEXT)):
            for _pid, _lst in getattr(_mod, _k, {}).items():
                _tgt[_pid].extend(_lst)
        DOUBLINGS.extend(getattr(_mod, "DOUBLINGS", []))

PARTS = [
    dict(id="vn1", name="Violin I", zh="第一小提琴", abbr="Vln. I",
         data=VN1, clef="treble", program=48, ace="Violins I",
         sib="Violin I", sound="strings.violin"),
    dict(id="vn2", name="Violin II", zh="第二小提琴", abbr="Vln. II",
         data=VN2, clef="treble", program=48, ace="Violins II",
         sib="Violin II", sound="strings.violin"),
    dict(id="va", name="Viola", zh="中提琴", abbr="Vla.",
         data=VA, clef="alto", program=48, ace="Violas",
         sib="Viola", sound="strings.viola"),
    dict(id="vc", name="Violoncello", zh="大提琴", abbr="Vc.",
         data=VC, clef="bass", program=48, ace="Celli",
         sib="Violoncello", sound="strings.cello"),
    dict(id="cb", name="Contrabass", zh="低音提琴", abbr="Cb.",
         data=CB, clef="bass", program=48, ace="Basses",
         sib="Contrabass", sound="strings.contrabass", written_octave=12),
]
for _p in PARTS:
    _p["dyn"] = DYN[_p["id"]]
    _p["hair"] = HAIR[_p["id"]]
    _p["text"] = TEXT[_p["id"]]
PART = {p["id"]: p for p in PARTS}

# Sounding ranges (ACE String Section speakers, idiomatic section writing)
RANGES = {"vn1": ("G3", "D7"), "vn2": ("G3", "A6"), "va": ("C3", "E6"),
          "vc": ("C2", "A5"), "cb": ("E1", "G3")}
OPEN_STRINGS = {"vn1": ["G3", "D4", "A4", "E5"], "vn2": ["G3", "D4", "A4", "E5"],
                "va": ["C3", "G3", "D4", "A4"], "vc": ["C2", "G2", "D3", "A3"],
                "cb": ["E1", "A1", "D2", "G2"]}
HAND_SPAN = {"vn1": 7, "vn2": 7, "va": 6, "vc": 4, "cb": 2}

VEL = {"ppp": 26, "pp": 36, "p": 48, "mp": 62, "mf": 76, "f": 92, "ff": 106,
       "fff": 118, "sfz": 110, "fp": 92, "sf": 104}
ACCENT = 12

# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(\()?((?:[A-G](?:#|##|b|bb)?\d)(?:\+[A-G](?:#|##|b|bb)?\d)*|r)"
    r"/(\d+)([~>*_^%!]*)(\))?$")


def parse_bar(s):
    evs, pos, pending_grace = [], 0, None
    for t in s.split():
        if t.startswith("g:"):
            pending_grace = t[2:]
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r} in {s!r}")
        sl, pit, dur, flags, sr = m.groups()
        dur = int(dur)
        if dur <= 0:
            raise ValueError(f"zero duration in {t!r}")
        evs.append(dict(
            pos=pos, dur=dur,
            pitches=None if pit == "r" else pit.split("+"),
            tie="~" in flags, accent=">" in flags, stacc="*" in flags,
            tenuto="_" in flags, marcato="^" in flags, trem="%" in flags,
            fermata="!" in flags,
            slur_start=bool(sl), slur_end=bool(sr), grace=pending_grace))
        pending_grace = None
        pos += dur
    if pos != BAR16:
        raise ValueError(f"bar sums to {pos}: {s!r}")
    return evs


def parse_part(data):
    out = []
    for b in range(1, NBARS + 1):
        try:
            evs = parse_bar(data.get(b, REST))
        except ValueError as e:
            raise ValueError(f"m{b}: {e}") from None
        for e in evs:
            e["bar"] = b
            e["abs"] = (b - 1) * BAR16 + e["pos"]
            out.append(e)
    return out


def parse_all():
    return {p["id"]: parse_part(p["data"]) for p in PARTS}


# ---------------------------------------------------------------------------
# Notation splitting (keep beats 1 and 3 visible)
# ---------------------------------------------------------------------------
def split_dur(pos, dur):
    pieces = []
    while dur > 0:
        if pos % 4 == 0:
            allowed = {0: [16, 12, 8, 6, 4, 3, 2, 1],
                       8: [8, 6, 4, 3, 2, 1]}.get(pos, [4, 3, 2, 1])
            if pos == 4 and dur >= 8:
                allowed = [8, 6, 4, 3, 2, 1] if dur == 8 or dur >= 12 \
                    else [4, 3, 2, 1]
            if pos == 4 and dur >= 12:
                allowed = [12, 8, 6, 4, 3, 2, 1]
        elif pos % 4 == 2:
            allowed = [6, 4, 2, 1] if pos in (2, 10) else [2, 1]
            if pos == 6:
                allowed = [2, 1]
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


# ---------------------------------------------------------------------------
# The piano chart (transcription) — used by the fidelity checks
# ---------------------------------------------------------------------------
TRANSCRIPTION = os.path.join(HERE, "transcription", "piano.json")


def load_piano():
    """The chart as sets of sounding MIDI pitches per absolute 16th:
    rh / lh = sounding, rh_att = newly attacked in the RH (ties are not
    attacks); 8va bars are transposed to sounding pitch."""
    if not os.path.exists(TRANSCRIPTION):
        return None
    sys.path.insert(0, os.path.join(HERE, "source"))
    import piano_tools as PT
    bars = json.load(open(TRANSCRIPTION, encoding="utf-8"))["bars"]
    rh_snd, lh_snd, rh_att = {}, {}, {}
    tied = {}  # (staff, voice) -> set of pitches tied over from before
    for b in sorted(bars, key=lambda x: x["bar"]):
        base = (b["bar"] - 1) * BAR16
        octv = 12 if b.get("rh_ottava") else 0
        for staff, store in (("rh", rh_snd), ("lh", lh_snd)):
            for vi, v in enumerate(b[staff]):
                carry = tied.get((staff, vi), set())
                for e in PT.parse_voice(v):
                    if e["pitches"] is None:
                        carry = set()
                        continue
                    ps = {midi_of(x) + (octv if staff == "rh" else 0)
                          for x in e["pitches"]}
                    for t in range(e["pos"], e["pos"] + e["dur"]):
                        store.setdefault(base + t, set()).update(ps)
                    if staff == "rh":
                        new = ps - carry
                        if new:
                            rh_att.setdefault(base + e["pos"], set()).update(
                                new)
                    carry = ps if e["tie"] else set()
                tied[(staff, vi)] = carry
    return dict(rh=rh_snd, lh=lh_snd, rh_att=rh_att, bars=bars)


def piano_melody(piano):
    """[(abs16, midi)]: the chart's top line — every 16th where the highest
    sounding RH note is freshly attacked."""
    out = []
    for t in sorted(piano["rh_att"]):
        top = max(piano["rh"][t])
        if top in piano["rh_att"][t]:
            out.append((t, top))
    return out


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
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


def attacks(evs):
    """[(abs16, [midi...], dur16 incl. ties)]"""
    out, held = [], False
    for e in evs:
        if e["pitches"] is None:
            held = False
            continue
        ps = sorted(midi_of(x) for x in e["pitches"])
        if held and out:
            out[-1][2] += e["dur"]
        else:
            out.append([e["abs"], ps, e["dur"]])
        held = e["tie"]
    return out


def double_stop_ok(pid, ps):
    """ps: sorted midi list of one chord. True if some pair of adjacent
    strings can take it within the hand span (triple stops: rolled, each
    adjacent pair checked)."""
    opens = [midi_of(x) for x in OPEN_STRINGS[pid]]
    span = HAND_SPAN[pid]
    n = len(ps)
    if n == 1:
        return True
    if n > 4:
        return False
    for s0 in range(0, len(opens) - n + 1):
        strs = opens[s0:s0 + n]
        if all(p >= o for p, o in zip(ps, strs)):
            posns = [p - o for p, o in zip(ps, strs)]
            fingered = [x for x in posns if x > 0]
            if not fingered or max(fingered) - min(fingered) <= span:
                return True
    return False


def in_bars(b, bars):
    return bars is None or bars[0] <= b <= bars[1]


def check(parsed, bars=None):
    problems = []
    for pid, evs in parsed.items():
        lo, hi = (midi_of(x) for x in RANGES[pid])
        for e in evs:
            if not in_bars(e["bar"], bars):
                continue
            ps = sorted(midi_of(x) for x in e["pitches"] or [])
            for pit in e["pitches"] or []:
                if not lo <= midi_of(pit) <= hi:
                    problems.append(f"RANGE: {pid} m{e['bar']} {pit}")
            if len(ps) > 1 and not double_stop_ok(pid, ps):
                problems.append(
                    f"STOP: {pid} m{e['bar']}.{e['pos']:02d} "
                    f"{'+'.join(e['pitches'])} not playable as a "
                    f"{len(ps)}-note stop (write div. or respace)")
    grid = sounding(parsed)
    allow = {(bb, *sorted(pp)) for (bb, *pp) in CLASH_ALLOW}
    for t, snd in sorted(grid.items()):
        if not in_bars(t // 16 + 1, bars):
            continue
        for i in range(len(snd)):
            for j in range(i + 1, len(snd)):
                a, b = snd[i], snd[j]
                if not (a[3] or b[3]):
                    continue
                if (t // 16 + 1, *sorted((a[0], b[0]))) in allow:
                    continue
                iv = abs(a[1] - b[1])
                if iv % 12 == 1:
                    problems.append(
                        f"CLASH: m{t // 16 + 1}.{t % 16:02d} {a[0]}:{a[2]} "
                        f"x {b[0]}:{b[2]} ({'m2' if iv == 1 else 'b9'})")
    lines = {pid: top_line(evs) for pid, evs in parsed.items()}
    ids = list(parsed)

    def doubled(x, y, bar):
        return any({x, y} == {a, b} and f <= bar <= l
                   for a, b, f, l in DOUBLINGS)

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
                bar = t // 16 + 1
                if prev and pa != prev[0] and pb != prev[1] and \
                        in_bars(bar, bars):
                    iv0 = abs(prev[0] - prev[1]) % 12
                    iv1 = abs(pa - pb) % 12
                    same_dir = (pa - prev[0]) * (pb - prev[1]) > 0
                    if same_dir and iv0 == iv1 and iv1 in (0, 7) and \
                            not doubled(ids[i], ids[j], bar):
                        problems.append(
                            f"PARALLEL: m{bar}.{t % 16:02d} "
                            f"{ids[i]}/{ids[j]} "
                            f"{'P8' if iv1 == 0 else 'P5'}")
                prev = (pa, pb)
    problems += check_fidelity(parsed, bars)
    return problems


def check_fidelity(parsed, bars=None):
    """The chart's melody must be in the part(s) MELODY names (same rhythm
    of attacks and same pitches, allowing the listed octave shift); the
    lowest sounding note on beats 1 and 3 must match the chart's bass
    pitch class."""
    piano = load_piano()
    if piano is None:
        return ["FIDELITY: transcription/piano.json missing"]
    out = []
    mel = piano_melody(piano)
    atk = {pid: {a[0]: a for a in attacks(evs)} for pid, evs in parsed.items()}
    for b in range(1, NBARS + 1):
        if not in_bars(b, bars) or b in MELODY_FREE:
            continue
        carriers = MELODY.get(b)
        if carriers is None:
            continue
        want = [(t, m) for t, m in mel if (t // 16) + 1 == b]
        for pid, octv in carriers:
            got = {t: a for t, a in atk[pid].items() if (t // 16) + 1 == b}
            for t, m in want:
                a = got.get(t)
                if a is None:
                    out.append(f"MELODY: {pid} m{b}.{t % 16:02d} missing "
                               f"attack of {name_of(m + octv)}")
                elif (m + octv) not in a[1]:
                    out.append(f"MELODY: {pid} m{b}.{t % 16:02d} has "
                               f"{'+'.join(name_of(x) for x in a[1])}, chart "
                               f"{name_of(m + octv)}")
    grid = sounding(parsed)
    for b in range(1, NBARS + 1):
        if not in_bars(b, bars):
            continue
        for half in (0, 1):
            t = (b - 1) * BAR16 + half * 8
            if (b, half) in BASS_FREE:
                continue
            lh = piano["lh"].get(t)
            snd = grid.get(t)
            if not lh or not snd:
                continue
            want = min(lh) % 12
            have = min(x[1] for x in snd)
            if have % 12 != want:
                out.append(f"BASS: m{b} beat {1 + half * 2}: lowest note "
                           f"{name_of(have)}, chart bass {_NAMES[want]}")
    return out


# ---------------------------------------------------------------------------
# MusicXML (for Sibelius)
# ---------------------------------------------------------------------------
QL = {1: 0.25, 2: 0.5, 3: 0.75, 4: 1.0, 6: 1.5, 8: 2.0, 12: 3.0, 16: 4.0}


def make_m21(p, events):
    from music21 import (articulations, bar, clef, dynamics, expressions,
                         instrument, key, meter, note, chord, spanner,
                         stream, tempo, tie)
    part = stream.Part(id=p["id"])
    ins = {"vn1": instrument.Violin, "vn2": instrument.Violin,
           "va": instrument.Viola, "vc": instrument.Violoncello,
           "cb": instrument.Contrabass}[p["id"]]()
    ins.partName = p["sib"]
    ins.partAbbreviation = p["abbr"]
    part.insert(0, ins)
    woct = p.get("written_octave", 0)
    notes_at = {}
    slur_open = None
    measures = {}
    by_bar = {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    tied_prev = False
    first_part = p["id"] == PARTS[0]["id"]
    for b in range(1, NBARS + 1):
        m = stream.Measure(number=b)
        if b == 1:
            m.insert(0, {"treble": clef.TrebleClef, "alto": clef.AltoClef,
                         "bass": clef.BassClef}[p["clef"]]())
            m.insert(0, key.Key("F"))
            m.insert(0, meter.TimeSignature("4/4"))
        for e in by_bar[b]:
            if e["grace"]:
                g = note.Note(m21_name(shift(e["grace"], woct)),
                              type="16th").getGrace()
                g.duration.slash = True
                m.append(g)
            pieces = (split_rest if e["pitches"] is None else split_dur)(
                e["pos"], e["dur"])
            objs = []
            for i, d in enumerate(pieces):
                if e["pitches"] is None:
                    n = note.Rest(quarterLength=QL[d])
                    if e["dur"] == 16:
                        n.fullMeasure = True
                else:
                    names = [m21_name(shift(x, woct)) for x in e["pitches"]]
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
                    if first:
                        if e["accent"]:
                            n.articulations.append(articulations.Accent())
                        if e["stacc"]:
                            n.articulations.append(articulations.Staccato())
                        if e["tenuto"]:
                            n.articulations.append(articulations.Tenuto())
                        if e["marcato"]:
                            n.articulations.append(
                                articulations.StrongAccent())
                    if e["trem"]:
                        t = expressions.Tremolo()
                        t.numberOfMarks = 2 if d >= 2 else 1
                        n.expressions.append(t)
                    if e["fermata"] and last:
                        f = expressions.Fermata()
                        f.type = "upright"
                        n.expressions.append(f)
                m.append(n)
                objs.append(n)
            notes_at.setdefault(e["abs"], objs[0])
            e["m21"] = objs
            tied_prev = e["tie"] and e["pitches"] is not None
            if e["slur_start"]:
                slur_open = objs[0]
            if e["slur_end"] and slur_open is not None:
                if slur_open is not objs[-1]:
                    part.insert(0, spanner.Slur(slur_open, objs[-1]))
                slur_open = None
        # words after the notes (inserting first would shift the notes)
        for cb_, cs_, cname in CLEFS.get(p["id"], []):
            if cb_ == b:
                m.insert(cs_ / 4, {"treble": clef.TrebleClef,
                                   "alto": clef.AltoClef,
                                   "tenor": clef.TenorClef,
                                   "bass": clef.BassClef}[cname]())
        if first_part:
            if b == 1:
                mm = tempo.MetronomeMark(number=TEMPO_MARK[1],
                                         referent=1.0)
                m.insert(0, mm)
            for tb, ts, txt, bpm in TEMPO_TEXT:
                if tb == b:
                    if bpm:
                        m.insert(ts / 4, tempo.MetronomeMark(
                            text=txt, number=bpm, referent=1.0))
                    else:
                        m.insert(ts / 4, tempo.TempoText(txt))
            if b in REHEARSAL:
                rm = expressions.RehearsalMark(REHEARSAL[b][0])
                m.insert(0, rm)
        if b == NBARS:
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
        measures[bb].insert(s / 4, te)
    return part


def build_score(parsed):
    from music21 import layout, metadata, stream
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = TITLE
    md.movementName = TITLE
    md.composer = COMPOSER
    md.add("arranger", ARRANGER)
    sc.insert(0, md)
    for p in PARTS:
        sc.insert(0, make_m21(p, parsed[p["id"]]))
    sc.insert(0, layout.StaffGroup(list(sc.parts), name="Strings",
                                   symbol="bracket", barTogether=True))
    return sc


# Sibelius page: 11 x 17 in (tabloid), 7.2 mm staves
PAGE_W_IN, PAGE_H_IN = 11.0, 17.0
SPATIUM_MM = 1.8


def _tenths(inches):
    return round(inches * 25.4 / SPATIUM_MM * 10, 1)


def polish(path):
    """Tidy the MusicXML for Sibelius: tabloid page, credits (title block,
    Score in C, composer / arranger / engraver), creators and encoder,
    instrument sounds, Hollywood part names for display, bar numbers on
    every bar, system breaks, placement of dynamics and words."""
    tree = ET.parse(path)
    r = tree.getroot()
    ident = r.find("identification")
    for x in ident.findall("creator"):
        ident.remove(x)
    for i, (t, v) in enumerate((("composer", COMPOSER),
                                ("arranger", ARRANGER))):
        el = ET.Element("creator", type=t)
        el.text = v
        ident.insert(i, el)
    rights = ident.find("rights")
    if rights is None:
        rights = ET.Element("rights")
        ident.insert(2, rights)
    rights.text = (f"作曲 {COMPOSER} · 改编 {ARRANGER} · 制谱 {ENGRAVER}")
    enc = ident.find("encoding")
    for x in enc.findall("encoder"):
        enc.remove(x)
    e = ET.Element("encoder")
    e.text = ENGRAVER
    enc.insert(1, e)

    d = r.find("defaults")
    if d is None:
        d = ET.Element("defaults")
        r.insert(list(r).index(r.find("part-list")), d)
    for t in ("scaling", "page-layout", "system-layout", "staff-layout"):
        for x in d.findall(t):
            d.remove(x)
    W, H = _tenths(PAGE_W_IN), _tenths(PAGE_H_IN)
    mx, mt, mb = _tenths(0.6), _tenths(0.9), _tenths(0.8)
    new = ET.fromstring(
        f"<defaults><scaling><millimeters>{SPATIUM_MM * 4:g}</millimeters>"
        "<tenths>40</tenths></scaling><page-layout>"
        f"<page-height>{H}</page-height><page-width>{W}</page-width>"
        "<page-margins type=\"both\">"
        f"<left-margin>{mx}</left-margin><right-margin>{mx}</right-margin>"
        f"<top-margin>{mt}</top-margin><bottom-margin>{mb}</bottom-margin>"
        "</page-margins></page-layout><system-layout><system-margins>"
        "<left-margin>80</left-margin><right-margin>0</right-margin>"
        "</system-margins><system-distance>130</system-distance>"
        "<top-system-distance>300</top-system-distance></system-layout>"
        "<staff-layout><staff-distance>80</staff-distance></staff-layout>"
        "</defaults>")
    for i, x in enumerate(new):
        d.insert(i, x)

    for x in r.findall("credit"):
        r.remove(x)
    top = round(H - mt, 1)
    credits = [  # (types, runs [(text, size, bold)], x, y, justify, valign)
        (("title",), [(TITLE, 30, True)], W / 2, top, "center", "top"),
        (("subtitle",), [(f"{SUBTITLE}　{SUBTITLE_EN}", 13, False)],
         W / 2, round(top - 75, 1), "center", "top"),
        (("part name",), [("Score in C", 11, True)], mx, round(top - 150, 1),
         "left", "bottom"),
        (("composer",), [(f"作曲：{COMPOSER}\n改编：{ARRANGER}\n"
                          f"制谱：{ENGRAVER}", 10.5, False)],
         W - mx, round(top - 150, 1), "right", "bottom"),
    ]
    at = list(r).index(r.find("part-list"))
    for i, (types, runs, x, y, just, va) in enumerate(credits):
        c = ET.Element("credit", page="1")
        for t in types:
            ET.SubElement(c, "credit-type").text = t
        for k, (text, size, bold) in enumerate(runs):
            w = ET.SubElement(c, "credit-words", {"font-size": f"{size:g}"})
            if k == 0:
                w.attrib = {"default-x": f"{x:g}", "default-y": f"{y:g}",
                            "font-size": f"{size:g}", "justify": just,
                            "valign": va}
            if bold:
                w.set("font-weight", "bold")
            w.text = text
        r.insert(at + i, c)

    by_name = {p["sib"]: p for p in PARTS}
    for sp in r.iter("score-part"):
        pname = sp.findtext("part-name")
        p = by_name[pname]
        # Hollywood display name next to the Sibelius instrument name
        pn = sp.find("part-name")
        idx = list(sp).index(pn)
        for x in sp.findall("part-name-display"):
            sp.remove(x)
        pnd = ET.Element("part-name-display")
        ET.SubElement(pnd, "display-text").text = p["name"]
        sp.insert(idx + 1, pnd)
        si = sp.find("score-instrument")
        if si is not None:
            si.find("instrument-name").text = p["sib"]
            for x in si.findall("instrument-sound"):
                si.remove(x)
            el = ET.Element("instrument-sound")
            el.text = p["sound"]
            ab = si.find("instrument-abbreviation")
            si.insert(list(si).index(ab) + 1 if ab is not None else 1, el)
    for n in r.iter("note"):
        for x in n.findall("instrument"):
            n.remove(x)
    for part in r.findall("part"):
        for m in part.findall("measure"):
            num = int(m.get("number"))
            if num == 1 or num in SYSTEM_BREAKS or num in PAGE_BREAKS:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                if num == 1:
                    for x in list(pr):
                        pr.remove(x)
                    sl = ET.SubElement(pr, "system-layout")
                    ET.SubElement(sl, "top-system-distance").text = "330"
                    ET.SubElement(pr, "measure-numbering").text = "measure"
                elif num in PAGE_BREAKS:
                    pr.set("new-page", "yes")
                else:
                    pr.set("new-system", "yes")
            for el in m.findall("direction"):
                if el.find("direction-type/dynamics") is not None or \
                        el.find("direction-type/wedge") is not None:
                    el.set("placement", "below")
                elif el.find("direction-type/words") is not None or \
                        el.find("direction-type/rehearsal") is not None or \
                        el.find("direction-type/metronome") is not None:
                    el.set("placement", "above")
    # one bold tempo mark: "Moderato con moto ♩ = 112"
    first_measure = r.find("part/measure")
    for dr in first_measure.findall("direction"):
        met = dr.find("direction-type/metronome")
        if met is not None:
            dt = ET.Element("direction-type")
            ET.SubElement(dt, "words", {"font-weight": "bold"}).text = \
                TEMPO_MARK[0] + " "
            dr.insert(0, dt)
            break
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
# MIDI (ACE Studio String Section)
# ---------------------------------------------------------------------------
def merged_notes(events):
    """Tied notes merged: list of dicts (start16, dur16, pitches, accent,
    stacc, tenuto, marcato, trem, grace, slurred = slurred into the next
    note)."""
    out, cur, in_slur = [], None, False
    for e in events:
        if e["pitches"] is None:
            cur = None
            continue
        if cur is not None and cur["tie"]:
            cur["dur"] += e["dur"]
            cur["tie"] = e["tie"]
            if e["slur_end"]:
                in_slur = False
                cur["slurred"] = False
            continue
        if e["slur_start"]:
            in_slur = True
        cur = dict(start=e["abs"], dur=e["dur"], pitches=e["pitches"],
                   tie=e["tie"], grace=e["grace"], accent=e["accent"],
                   stacc=e["stacc"], tenuto=e["tenuto"],
                   marcato=e["marcato"], trem=e["trem"],
                   slurred=in_slur and not e["slur_end"])
        if e["slur_end"]:
            in_slur = False
        out.append(cur)
    return out


def dyn_curve(p):
    total = NBARS * BAR16
    pts = sorted(((b - 1) * BAR16 + s, VEL[m]) for b, s, m in p["dyn"])
    if not pts:
        pts = [(0, VEL["mf"])]
    v = [pts[0][1]] * (total + 1)
    for i, (a, val) in enumerate(pts):
        end = pts[i + 1][0] if i + 1 < len(pts) else total + 1
        for t in range(a, end):
            v[t] = val
    for b, s, b2, s2, kind in p["hair"]:
        a = (b - 1) * BAR16 + s
        z = min(total, (b2 - 1) * BAR16 + s2)
        v0 = v[a]
        nxt = [val for t, val in pts if t > z]
        v1 = nxt[0] if nxt else v0 + (-16 if kind == "dim" else 16)
        if kind == "cresc" and v1 <= v0:
            v1 = v0 + 12
        if kind == "dim" and v1 >= v0:
            v1 = v0 - 12
        for t in range(a, z + 1):
            v[t] = round(v0 + (v1 - v0) * (t - a) / max(1, z - a))
    return [max(1, min(127, x)) for x in v]


def tempo_track(title):
    ab = [(0, mido_msg("track_name", name=title)),
          (0, mido_msg("time_signature", numerator=4, denominator=4)),
          (0, mido_msg("key_signature", key="F"))]
    import mido
    for b, s, bpm in TEMPI:
        t = ((b - 1) * BAR16 + s) * T16
        ab.append((t, mido.MetaMessage("set_tempo",
                                       tempo=mido.bpm2tempo(bpm))))
    # ASCII only: some DAWs show non-Latin marker text as garbage
    marks = {1: INTRO_TITLE[0]}
    marks.update({b: f"{l} {en}" for b, (l, en, zh) in REHEARSAL.items()})
    for b, name in sorted(marks.items()):
        ab.append(((b - 1) * BAR16 * T16,
                   mido.MetaMessage("marker", text=name)))
    ab.sort(key=lambda x: x[0])
    tr, last = mido.MidiTrack(), 0
    for t, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def mido_msg(kind, **kw):
    import mido
    return mido.MetaMessage(kind, **kw)


GRACE_T = T16 // 2          # a 32nd
GAP = 40                    # ticks of air between detached notes


def part_track(p, events, ch, gm=False):
    import mido
    notes = merged_notes(events)
    vel = dyn_curve(p)
    ab = []  # (tick, order, msg)
    ab.append((0, 0, mido.MetaMessage("track_name", name=p["name"])))
    ab.append((0, 0, mido.MetaMessage("instrument_name", name=p["ace"])))
    prog = {"vn1": 48, "vn2": 48, "va": 48, "vc": 48, "cb": 43}[p["id"]] \
        if gm else p["program"]
    ab.append((0, 1, mido.Message("program_change", channel=ch,
                                  program=prog)))
    if gm:  # orchestral seating for the preview only
        pan = {"vn1": 30, "vn2": 48, "va": 78, "vc": 92, "cb": 104}[p["id"]]
        ab.append((0, 1, mido.Message("control_change", channel=ch,
                                      control=10, value=pan)))
        ab.append((0, 1, mido.Message("control_change", channel=ch,
                                      control=91, value=48)))
    last_cc = None
    for t in range(0, NBARS * BAR16, 1):
        val = min(127, 16 + vel[t])
        if val != last_cc:
            ab.append((t * T16, 2, mido.Message(
                "control_change", channel=ch, control=1, value=val)))
            ab.append((t * T16, 2, mido.Message(
                "control_change", channel=ch, control=11, value=val)))
            last_cc = val
    for i, n in enumerate(notes):
        on = n["start"] * T16
        off = (n["start"] + n["dur"]) * T16
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        touching = nxt is not None and nxt["start"] * T16 == off
        if n["stacc"]:
            off = on + max(T16, (off - on) // 2)
        elif touching and set(nxt["pitches"]) & set(n["pitches"]):
            off -= GAP                      # re-articulate the same pitch
        elif touching and n["slurred"]:
            pass                            # legato: note touches the next
        elif touching and not n["tenuto"]:
            off -= GAP // 2                 # détaché
        v = vel[min(n["start"], len(vel) - 1)]
        if n["accent"] or n["marcato"]:
            v += ACCENT
        v = max(1, min(127, v))
        if n["grace"]:
            gp = midi_of(n["grace"])
            ab.append((on - GRACE_T, 5, mido.Message(
                "note_on", channel=ch, note=gp, velocity=v)))
            ab.append((on, 3, mido.Message(
                "note_off", channel=ch, note=gp, velocity=0)))
        if n["trem"]:
            step = T16
            t = on
            while t < off:
                for pit in n["pitches"]:
                    ab.append((t, 5, mido.Message(
                        "note_on", channel=ch, note=midi_of(pit),
                        velocity=v)))
                    ab.append((min(off, t + step) - 20, 3, mido.Message(
                        "note_off", channel=ch, note=midi_of(pit),
                        velocity=0)))
                t += step
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


def write_midi(path, part_ids, parsed, gm=False):
    import mido
    mf = mido.MidiFile(type=1, ticks_per_beat=TPQ)
    mf.tracks.append(tempo_track("Jue Bie Shu - String Quintet"))
    for ch, p in enumerate(PARTS):
        if p["id"] in part_ids:
            mf.tracks.append(part_track(p, parsed[p["id"]], ch, gm=gm))
    mf.save(path)


SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


def render_mp3(mid, mp3):
    """Rough GM preview (FluidSynth + ffmpeg); only for checking notes."""
    import shutil
    import subprocess
    import tempfile
    if not (shutil.which("fluidsynth") and shutil.which("ffmpeg")
            and os.path.exists(SF2)):
        print("mp3 skipped: needs fluidsynth, ffmpeg, fluid-soundfont-gm")
        return
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "p.wav")
        subprocess.run(["fluidsynth", "-ni", "-g", "0.5", "-R", "1",
                        "-F", wav, SF2, mid], check=True,
                       capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-af", "loudnorm=I=-16:TP=-1.5", "-b:a", "192k",
                        mp3], check=True)


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


def duration_text():
    s = sec_at(NBARS * BAR16) + 2.5   # the final fermata
    return f"ca. {int(s // 60)}′{int(round(s % 60)):02d}″"


# ---------------------------------------------------------------------------
def score_basename():
    return os.path.join(OUT, f"{NAME}_弦乐五重奏")


def main():
    bars = None
    if "--bars" in sys.argv:
        a, b = sys.argv[sys.argv.index("--bars") + 1].split("-")
        bars = (int(a), int(b))
    parsed = parse_all()
    for x in check(parsed, bars):
        print(x)
    if "--check" in sys.argv:
        return
    os.makedirs(OUT, exist_ok=True)
    base = score_basename()
    sc = build_score(parsed)
    sc.write("musicxml", fp=base + ".musicxml")
    polish(base + ".musicxml")
    verify_bars(base + ".musicxml")
    ids = [p["id"] for p in PARTS]
    write_midi(base + "_全轨.mid", ids, parsed)
    d = os.path.join(OUT, "ACE分轨MIDI")
    os.makedirs(d, exist_ok=True)
    for i, p in enumerate(PARTS):
        write_midi(os.path.join(
            d, f"{i + 1}_{p['name'].replace(' ', '')}_{p['zh']}.mid"),
            [p["id"]], parsed)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        gm = os.path.join(tmp, "preview_gm.mid")
        write_midi(gm, ids, parsed, gm=True)
        if "--mp3" in sys.argv or "--pdf" in sys.argv:
            render_mp3(gm, os.path.join(OUT, "粗略试听_GM音色_非ACE效果.mp3"))
    print("written to", OUT)
    if "--pdf" in sys.argv:
        import engrave
        engrave.main(png="--png" in sys.argv)


if __name__ == "__main__":
    main()
