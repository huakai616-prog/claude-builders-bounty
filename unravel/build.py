#!/usr/bin/env python3
"""Unravel（全曲）— 东京喰种 OP · 弦乐四重奏 编配生成器

Generates, from one source of truth (this file + arrangement.py):
  * MusicXML full score for Sibelius (MusicXML 4.0, schema-valid)
  * Strings MIDI (four tracks, for ACE Studio String Section)
  * Hollywood-standard PDF with cover (tools/hollywood, `--pdf`)

Based on the Animenz piano arrangement the user sent (4/4, two flats,
♩ = 134, bars 0..132 where bar 0 is the one-eighth pickup).  The bar
numbers here are the score's own.  `--check` checks ranges, string double
stops, and fidelity to the piano original (piano_source.json, kept out of
the public repo): every melody and bass attack of the piano must be there
and no pitch class may sound that the piano does not have at that time.

Token syntax (durations in 64th notes: 16th = 4, 8th = 8, quarter = 16,
half = 32, whole = 64; one string per bar; " | " separates two voices):
  C5/8          note C5, an eighth
  D4+Bb4/16     double stop (low -> high)
  r/16          rest
  A4/8~         tie into the next note
  suffixes      . staccato  > accent  ! marcato  - tenuto  ^ fermata
                arp arpeggiated chord  trem1..trem3 tremolo slashes
                db down-bow  ub up-bow
  (G4/4 A4/4)   slur start / slur end
  g:A5          grace note(s) before the next note (gs: = slashed)
  {5:4 ... }    tuplet: five written values in the time of four
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction as Fr
from math import ceil, floor

import mido
from music21 import (articulations, bar, clef, duration, dynamics,
                     expressions, instrument, key, layout, metadata, meter,
                     note, chord, spanner, stream, tempo, tie)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hollywood"))
import hollywood  # noqa: E402  (shared Hollywood score template)

NAME = "Unravel"
BASE = f"{NAME}_全曲_弦乐四重奏"
TPQ = 480
T64 = TPQ // 16
BPM = 134
FULL = 64                      # a 4/4 bar in 64ths
MEASURES = list(range(0, 133))
PICKUPS = {0}


def blen(b):
    return 8 if b == 0 else FULL


def score_offsets():
    out, t = {}, 0
    for b in MEASURES:
        out[b] = t
        t += blen(b)
    return out, t


OFFS, SCORE_LEN = score_offsets()

# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------
_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ACC = {"#": 1, "##": 2, "b": -1, "bb": -2, None: 0}


def midi_of(p):
    m = re.fullmatch(r"([A-G])(##|#|bb|b)?(-?\d)", p)
    if not m:
        raise ValueError(p)
    s, acc, octv = m.groups()
    return 12 * (int(octv) + 1) + _STEP[s] + _ACC[acc]


def m21_name(p):
    s, acc, octv = re.fullmatch(r"([A-G])(##|#|bb|b)?(-?\d)", p).groups()
    return s + {"#": "#", "##": "##", "b": "-", "bb": "--", None: ""}[acc] \
        + octv


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
PIT = r"[A-G](?:##|#|bb|b)?-?\d"
TOK = re.compile(rf"^(\()?((?:{PIT})(?:\+{PIT})*|r)/(\d+)"
                 r"((?:\.|>|!|-|~|\^|arp|trem[123]|db|ub)*)(\))?$")
SUFFIX = re.compile(r"\.|>|!|-|~|\^|arp|trem[123]|db|ub")


def parse_voice(s, length):
    evs, pos, grace, tup = [], Fr(0), None, None
    for t in s.split():
        if t.startswith(("g:", "gs:")):
            kind, _, notes = t.partition(":")
            grace = dict(slash=kind == "gs", pitches=notes.split(","))
            continue
        mt = re.fullmatch(r"\{(\d+):(\d+)", t)
        if mt:
            tup = dict(n=int(mt.group(1)), m=int(mt.group(2)), evs=[])
            continue
        if t == "}":
            if not tup or not tup["evs"]:
                raise ValueError(f"empty or stray tuplet in {s!r}")
            tup["evs"][0]["tup_start"] = True
            tup["evs"][-1]["tup_stop"] = True
            # the unit the bracket counts in: written total / n (a group
            # may start with a longer rest, e.g. {5:4 r/8 X/4 X/4 X/4 })
            base = Fr(sum(e["wdur"] for e in tup["evs"]), tup["n"])
            for e in tup["evs"]:
                e["tup_base"] = base
            tup = None
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r} in {s!r}")
        sl, pit, dur, suf, sr = m.groups()
        marks = SUFFIX.findall(suf or "")
        wd = int(dur)
        d = Fr(wd) * tup["m"] / tup["n"] if tup else Fr(wd)
        trem = next((int(x[-1]) for x in marks if x.startswith("trem")), 0)
        e = dict(pos=pos, dur=d, wdur=wd,
                 tup=(tup["n"], tup["m"]) if tup else None,
                 tup_start=False, tup_stop=False,
                 pitches=None if pit == "r" else pit.split("+"),
                 tie="~" in marks, slur_start=bool(sl), slur_end=bool(sr),
                 staccato="." in marks, accent=">" in marks,
                 marcato="!" in marks, tenuto="-" in marks,
                 fermata="^" in marks, arp="arp" in marks, trem=trem,
                 downbow="db" in marks, upbow="ub" in marks, grace=grace)
        evs.append(e)
        if tup:
            tup["evs"].append(e)
        grace = None
        pos += d
    if tup:
        raise ValueError(f"unclosed tuplet in {s!r}")
    if pos != length:
        raise ValueError(f"voice sums to {pos}, expected {length}: {s!r}")
    return evs


def parse_part(data):
    """-> list of events with bar, voice, abs (Fractions of 64ths)."""
    out = []
    for b in MEASURES:
        s = data.get(b) or f"r/{blen(b)}"
        for v, vs in enumerate(s.split(" | ")):
            try:
                evs = parse_voice(vs, blen(b))
            except ValueError as e:
                raise ValueError(f"m{b}: {e}") from None
            for e in evs:
                e["bar"], e["voice"] = b, v
                e["abs"] = OFFS[b] + e["pos"]
                out.append(e)
    return out


# ---------------------------------------------------------------------------
# The arrangement
# ---------------------------------------------------------------------------
from arrangement import (VN1, VN2, VA, VC, DYN, HAIR, TEXT,  # noqa: E402
                         CLEFS, OTTAVA, SECTIONS, TEMPI, TEMPO_TEXT,
                         SYSTEM_BREAKS, PAGE_BREAKS, ALLOW)

PARTS = [
    dict(id="vn1", name="Violin I", abbr="Vln. I", data=VN1,
         inst=instrument.Violin, clef="treble", program=40),
    dict(id="vn2", name="Violin II", abbr="Vln. II", data=VN2,
         inst=instrument.Violin, clef="treble", program=40),
    dict(id="va", name="Viola", abbr="Vla.", data=VA,
         inst=instrument.Viola, clef="alto", program=41),
    dict(id="vc", name="Violoncello", abbr="Vc.", data=VC,
         inst=instrument.Violoncello, clef="bass", program=42),
]
for _p in PARTS:
    _p["dyn"] = DYN[_p["id"]]
    _p["hair"] = HAIR[_p["id"]]
    _p["text"] = TEXT[_p["id"]]
    _p["clefs"] = CLEFS.get(_p["id"], [])

CLEF = {"treble": clef.TrebleClef, "alto": clef.AltoClef,
        "tenor": clef.TenorClef, "bass": clef.BassClef}

VEL = {"ppp": 26, "pp": 34, "p": 46, "mp": 60, "mf": 74, "f": 90, "ff": 104,
       "fff": 116}
ACCENT = 12
MARCATO = 18
SFZ = 22

META = dict(
    title="Unravel", title_latin="东京喰种 OP",
    subtitle="全曲 · 弦乐四重奏",
    subtitle_en="Complete — for String Quartet",
    composer="TK from 凛として時雨",
    artist="TK from 凛として時雨",
    source="Animenz 钢琴改编版",
    instrumentation=[("Violin I", "第一小提琴"), ("Violin II", "第二小提琴"),
                     ("Viola", "中提琴"), ("Violoncello", "大提琴")],
    key="G Minor · g小调", tempo="♩ = 134",
    duration="ca. 4′00″", year="2026", tempo_text="Allegro misterioso")


# ---------------------------------------------------------------------------
# Notation splitting (keep the beats of 4/4 visible)
# ---------------------------------------------------------------------------
def _fits(pos, d):
    if d == 64:
        return pos == 0
    if d == 48:
        return pos == 0
    if d == 32:
        return pos % 32 == 0
    if d == 24:
        return pos in (0, 8, 32, 40)
    if d == 16:
        return pos % 16 == 0 or pos in (8, 40)
    if d == 12:          # also the 3+3+2 dotted 8th on the "e" of 1 / 3
        return pos % 16 in (0, 4) or pos % 32 == 12
    if d == 8:           # also the syncopated 16th-8th-16th eighth
        return pos % 8 == 0 or (pos % 4 == 0 and pos // 32 == (pos + 7) // 32)
    if d == 6:
        return pos % 8 in (0, 2)
    if d == 4:
        return pos % 4 == 0
    if d == 3:
        return pos % 4 in (0, 1)
    if d == 2:
        return pos % 2 == 0
    return True


def split_dur(pos, dur):
    pieces = []
    pos, dur = int(pos), int(dur)
    while dur > 0:
        d = next(x for x in (64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1)
                 if x <= dur and _fits(pos, x))
        pieces.append(d)
        pos += d
        dur -= d
    return pieces


def _ql(units):
    return Fr(units, 16)


def _grace_notes(g):
    out = []
    for p in g["pitches"]:
        n = note.Note(m21_name(p),
                      type="16th" if len(g["pitches"]) <= 2 else "32nd")
        n = n.getGrace()
        n.duration.slash = g["slash"]
        out.append(n)
    return out


def _decorate(n, e, first, last):
    if first:
        if e["accent"]:
            n.articulations.append(articulations.Accent())
        if e["marcato"]:
            n.articulations.append(articulations.StrongAccent())
        if e["staccato"]:
            n.articulations.append(articulations.Staccato())
        if e["tenuto"]:
            n.articulations.append(articulations.Tenuto())
        if e["downbow"]:
            n.articulations.append(articulations.DownBow())
        if e["upbow"]:
            n.articulations.append(articulations.UpBow())
        if e["arp"]:
            n.expressions.append(expressions.ArpeggioMark())
    if e["trem"]:
        t = expressions.Tremolo()
        t.numberOfMarks = e["trem"]
        n.expressions.append(t)
    if e["fermata"] and last:
        f = expressions.Fermata()
        f.type = "upright"
        n.expressions.append(f)


def make_m21(p, events):
    part = stream.Part(id=p["id"])
    ins = p["inst"]()
    ins.partName = p["name"]
    ins.partAbbreviation = p["abbr"]
    part.insert(0, ins)
    notes_at = {}
    measures = {}
    by_bar = {}
    for e in events:
        by_bar.setdefault(e["bar"], {}).setdefault(e["voice"], []).append(e)
    tied_prev = {}
    slur_open = {}
    for b in MEASURES:
        m = stream.Measure(number=b)
        if b == 0:
            m.insert(0, CLEF[p["clef"]]())
            m.insert(0, key.KeySignature(-2))
            m.insert(0, meter.TimeSignature("4/4"))
            if p["id"] == "vn1":
                mm = tempo.MetronomeMark(number=BPM, referent=1.0)
                mm.placement = "above"
                m.insert(0, mm)
        voices = by_bar[b]
        containers = []
        for v in sorted(voices):
            if len(voices) > 1:
                vc = stream.Voice(id=str(v + 1))
                containers.append((v, vc))
            else:
                containers.append((v, m))
        for v, cont in containers:
            for e in voices[v]:
                if e["grace"]:
                    for g in _grace_notes(e["grace"]):
                        cont.append(g)
                if e["tup"]:
                    pieces = [None]
                else:
                    pieces = split_dur(e["pos"], e["dur"])
                objs = []
                for i, d in enumerate(pieces):
                    if d is None:
                        dd = duration.Duration(quarterLength=_ql(e["wdur"]))
                        unit = duration.Duration(
                            quarterLength=_ql(e["tup_base"]))
                        tp = duration.Tuplet(e["tup"][0], e["tup"][1])
                        tp.setDurationType(unit.type, unit.dots)
                        if e["tup_start"]:
                            tp.type = "start"
                        elif e["tup_stop"]:
                            tp.type = "stop"
                        dd.appendTuplet(tp)
                    else:
                        dd = duration.Duration(quarterLength=_ql(d))
                    if e["pitches"] is None:
                        n = note.Rest(duration=dd)
                    else:
                        names = [m21_name(x) for x in e["pitches"]]
                        n = (note.Note(names[0], duration=dd)
                             if len(names) == 1 else
                             chord.Chord(names, duration=dd))
                        first = i == 0
                        last = i == len(pieces) - 1
                        starts = (not first) or tied_prev.get(v)
                        cont_ = (not last) or e["tie"]
                        if starts and cont_:
                            n.tie = tie.Tie("continue")
                        elif starts:
                            n.tie = tie.Tie("stop")
                        elif cont_:
                            n.tie = tie.Tie("start")
                        _decorate(n, e, first, last)
                    cont.append(n)
                    objs.append(n)
                if v == 0:
                    notes_at.setdefault(e["abs"], objs[0])
                e["m21"] = objs
                tied_prev[v] = e["tie"] and e["pitches"] is not None
                if e["slur_start"]:
                    slur_open[v] = objs[0]
                if e["slur_end"] and slur_open.get(v) is not None:
                    part.insert(0, spanner.Slur(slur_open[v], objs[-1]))
                    slur_open[v] = None
            if cont is not m:
                m.insert(0, cont)
        # zero-length items after the notes (or append() would shift them)
        for cb, cpos, cname in p["clefs"]:
            if cb == b:
                m.insert(_ql(cpos), CLEF[cname]())
        if p["id"] == "vn1":
            for sb, letter, title in SECTIONS:
                if sb == b:
                    if letter:
                        rm = expressions.RehearsalMark(letter)
                        rm.placement = "above"
                        m.insert(0, rm)
                    if title:
                        te = expressions.TextExpression(title)
                        te.style.fontWeight = "bold"
                        te.placement = "above"
                        m.insert(0, te)
            for tb, ts, txt in TEMPO_TEXT:
                if tb == b:
                    m.insert(_ql(ts), tempo.TempoText(txt))
        if blen(b) < FULL:          # pickup: incomplete, not padded
            m.paddingLeft = _ql(FULL - blen(b))
        if b == MEASURES[-1]:
            m.rightBarline = bar.Barline("final")
        measures[b] = m
        part.append(m)

    def obj_at(a, forward=True):
        ks = sorted(notes_at)
        if forward:
            k = next((k for k in ks if k >= a), None)
        else:
            k = next((k for k in reversed(ks) if k <= a), None)
        return notes_at.get(k) if k is not None else None

    for bb, s, mark in p["dyn"]:
        d = dynamics.Dynamic(mark)
        d.placement = "below"
        measures[bb].insert(_ql(s), d)
    for bb, s, bb2, s2, kind in p["hair"]:
        cls = dynamics.Crescendo if kind == "cresc" else dynamics.Diminuendo
        n1 = notes_at.get(OFFS[bb] + s)
        n2 = obj_at(OFFS[bb2] + s2, forward=False)
        if n1 is None or n2 is None or n1 is n2:
            n1, n2 = spanner.SpannerAnchor(), spanner.SpannerAnchor()
            measures[bb].insert(_ql(s), n1)
            measures[bb2].insert(_ql(min(s2 + 1, blen(bb2))), n2)
        part.insert(0, cls(n1, n2))
    for bb, s, txt in p["text"]:
        te = expressions.TextExpression(txt)
        te.style.fontStyle = "italic"
        te.placement = "above"
        measures[bb].insert(_ql(s), te)
    return part


def build_score(parsed):
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = META["title"]
    md.movementName = f"{META['title']}（{META['subtitle']}）"
    md.composer = META["composer"]
    sc.insert(0, md)
    for p in PARTS:
        sc.insert(0, make_m21(p, parsed[p["id"]]))
    sc.insert(0, layout.StaffGroup(list(sc.parts), name="String Quartet",
                                   symbol="bracket"))
    return sc


# ---------------------------------------------------------------------------
# MusicXML polish for Sibelius
# ---------------------------------------------------------------------------
SOUNDS = {"Violin I": ("Violin", "strings.violin"),
          "Violin II": ("Violin", "strings.violin"),
          "Viola": ("Viola", "strings.viola"),
          "Violoncello": ("Violoncello", "strings.cello")}


def polish(path):
    """Implicit pickup, one <instrument-sound> per part, system / page
    breaks, placements, 8va lines (display only: pitches stay as they
    sound)."""
    tree = ET.parse(path)
    r = tree.getroot()
    for sp in r.iter("score-part"):
        iname, snd = SOUNDS[sp.findtext("part-name")]
        si = sp.find("score-instrument")
        if si is not None:
            si.find("instrument-name").text = iname
            for x in si.findall("instrument-sound"):
                si.remove(x)
            el = ET.Element("instrument-sound")
            el.text = snd
            ab = si.find("instrument-abbreviation")
            si.insert(list(si).index(ab) + 1 if ab is not None else 1, el)
    for n in r.iter("note"):
        for x in n.findall("instrument"):
            n.remove(x)
    names = {s.get("id"): s.findtext("part-name")
             for s in r.iter("score-part")}
    ids = {p["name"]: p["id"] for p in PARTS}
    divs = int(r.find("part/measure/attributes/divisions").text)
    for part in r.findall("part"):
        pid = ids[names[part.get("id")]]
        ms = {int(m.get("number")): m for m in part.findall("measure")}
        for num, m in ms.items():
            if num in PICKUPS:
                m.set("implicit", "yes")
            if num in SYSTEM_BREAKS or num in PAGE_BREAKS:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                pr.set("new-page" if num in PAGE_BREAKS else "new-system",
                       "yes")
            for el in m.findall("direction"):
                if el.find("direction-type/dynamics") is not None or \
                        el.find("direction-type/wedge") is not None:
                    el.set("placement", "below")
                elif el.find("direction-type/words") is not None or \
                        el.find("direction-type/rehearsal") is not None:
                    el.set("placement", "above")
        for ot in OTTAVA:
            # (part, first bar, last bar) or
            # (part, bar1, pos1, bar2, pos2): notes starting at/after pos1
            # in bar1 up to (not including) pos2 in bar2
            if ot[0] != pid:
                continue
            if len(ot) == 3:
                b1, p1, b2, p2 = ot[1], 0, ot[2], blen(ot[2])
            else:
                b1, p1, b2, p2 = ot[1:]
            first = _voice1_notes(ms[b1], divs)
            last = _voice1_notes(ms[b2], divs)
            a = next(el for pos, el in first if pos >= p1)
            z = [el for pos, el in last if pos < p2][-1]
            start = ET.fromstring(
                '<direction placement="above"><direction-type>'
                '<octave-shift type="down" size="8"/></direction-type>'
                '</direction>')
            ms[b1].insert(list(ms[b1]).index(a), start)
            stop = ET.fromstring(
                '<direction><direction-type><octave-shift type="stop" '
                'size="8"/></direction-type></direction>')
            kids = list(ms[b2])
            i = kids.index(z) + 1
            while i < len(kids) and kids[i].tag == "note" and \
                    kids[i].find("chord") is not None:
                i += 1          # after the whole chord
            ms[b2].insert(i, stop)
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


def _voice1_notes(measure, divs):
    """[(pos in 64ths, <note>)] for the non-chord, non-grace notes and
    rests of voice 1 in a MusicXML measure."""
    out, t, last = [], 0, 0
    for el in measure:
        if el.tag == "backup":
            t -= int(el.findtext("duration"))
        elif el.tag == "forward":
            t += int(el.findtext("duration"))
        elif el.tag == "note":
            if el.find("grace") is not None:
                continue
            if el.find("chord") is not None:
                continue
            d = int(el.findtext("duration"))
            if (el.findtext("voice") or "1") == "1":
                out.append((Fr(t * 16, divs), el))
            t += d
    return out


def verify_bars(path):
    """Every bar of every part in the written file holds its length."""
    from music21 import converter
    for p in converter.parse(path).parts:
        ms = list(p.getElementsByClass("Measure"))
        assert len(ms) == len(MEASURES), (p.partName, len(ms))
        for m, b in zip(ms, MEASURES):
            got = m.duration.quarterLength
            assert abs(got - blen(b) / 16) < 1e-6, \
                (p.partName, b, m.duration.quarterLength, m.paddingLeft)


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
GRACE_T = TPQ // 12      # ~37 ms at ♩ = 134
ARP_T = TPQ // 24        # roll of an arpeggiated chord, per note
STACC = 0.5


def tick(abs64):
    return round(abs64 * T64)


def dyn_curve(p):
    """velocity at each 64th of the score."""
    pts = sorted((OFFS[b] + s, m) for b, s, m in p["dyn"])
    level = [VEL["p"]] * (SCORE_LEN + 1)
    lv = [(a, m) for a, m in pts if m in VEL]
    for i, (a, m) in enumerate(lv):
        end = lv[i + 1][0] if i + 1 < len(lv) else SCORE_LEN + 1
        for t in range(a, end):
            level[t] = VEL[m]
    for b, s, b2, s2, kind in p["hair"]:
        a, z = OFFS[b] + s, OFFS[b2] + s2
        v0 = level[a]
        nxt = [VEL[m] for t, m in lv if t > z]
        v1 = nxt[0] if nxt else v0 + (-12 if kind == "dim" else 12)
        if kind == "cresc" and v1 <= v0:
            v1 = v0 + 10
        if kind == "dim" and v1 >= v0:
            v1 = v0 - 10
        for t in range(a, min(z + 1, SCORE_LEN)):
            level[t] = round(v0 + (v1 - v0) * (t - a) / max(1, z - a))
    sfz = {OFFS[b] + s for b, s, m in p["dyn"] if m in ("sfz", "sf", "fp")}
    return level, sfz


def tech_map(p):
    """64th -> 'pizz' / 'arco' state from the part's texts."""
    marks = sorted((OFFS[b] + s, t.strip().rstrip(".").lower())
                   for b, s, t in p["text"]
                   if t.strip().rstrip(".").lower() in ("pizz", "arco"))
    state = [False] * (SCORE_LEN + 1)
    for i, (a, t) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else SCORE_LEN + 1
        for x in range(a, end):
            state[x] = t == "pizz"
    return state


def part_track(p, events, ch):
    level, sfz = dyn_curve(p)
    pizz = tech_map(p)
    ab = [(0, 0, mido.MetaMessage("track_name", name=p["name"])),
          (0, 1, mido.Message("program_change", channel=ch,
                              program=p["program"]))]
    cur_prog = p["program"]
    held = {}
    notes = []
    last_cc = None
    for e in sorted(events, key=lambda e: (e["abs"], e["voice"])):
        if e["pitches"] is None:
            continue
        a = e["abs"]
        ai = int(floor(a))
        t_on = tick(a)
        t_end = tick(a + e["dur"])
        want = 45 if pizz[ai] else p["program"]
        if want != cur_prog:
            ab.append((t_on, 1, mido.Message("program_change", channel=ch,
                                             program=want)))
            cur_prog = want
        v = level[ai]
        cc = min(127, 22 + v)
        if cc != last_cc:
            ab.append((t_on, 2, mido.Message("control_change", channel=ch,
                                             control=11, value=cc)))
            ab.append((t_on, 2, mido.Message("control_change", channel=ch,
                                             control=1, value=cc)))
            last_cc = cc
        if ai in sfz:
            v += SFZ
        if e["accent"]:
            v += ACCENT
        if e["marcato"]:
            v += MARCATO
        v = max(1, min(127, v))
        vk = e["voice"]
        if vk in held:                       # continuation of a tie
            held[vk]["off"] = t_end
            if not e["tie"]:
                notes.extend(held.pop(vk)["emit"]())
            continue
        on = t_on
        if e["grace"]:
            gl = GRACE_T if len(e["grace"]["pitches"]) > 1 else GRACE_T * 2
            for i, gp in enumerate(e["grace"]["pitches"]):
                notes.append((on + i * gl, on + (i + 1) * gl, midi_of(gp), v))
            on += gl * len(e["grace"]["pitches"])
        pits = sorted(midi_of(x) for x in e["pitches"])
        if e["trem"]:
            step = {1: T64 * 8, 2: T64 * 4, 3: T64 * 2}[e["trem"]]
            t = on
            while t < t_end - 5:
                for pm in pits:
                    notes.append((t, min(t + step - 8, t_end), pm, v))
                t += step
            continue
        rec = dict(on=on, off=t_end, pits=pits, v=v, arp=e["arp"])

        def emit(rec=rec):
            out = []
            roll = rec["arp"] or len(rec["pits"]) > 2
            for k, pm in enumerate(rec["pits"]):
                o = rec["on"] + (k * ARP_T if roll else 0)
                out.append((o, max(o + 30, rec["off"]), pm, rec["v"]))
            return out
        rec["emit"] = emit
        if e["tie"]:
            held[vk] = rec
            continue
        if e["staccato"] or pizz[ai]:
            rec["off"] = on + max(40, int((t_end - on) * STACC))
        elif not e["tenuto"] and not e["slur_start"]:
            rec["off"] = t_end - 8
        notes.extend(emit())
    for on, off, pm, v in notes:
        ab.append((on, 5, mido.Message("note_on", channel=ch, note=pm,
                                       velocity=v)))
        ab.append((off, 3, mido.Message("note_off", channel=ch, note=pm,
                                         velocity=0)))
    ab.sort(key=lambda x: (x[0], x[1]))
    tr, last = mido.MidiTrack(), 0
    for t, _, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def tempo_track():
    ab = [(0, mido.MetaMessage("track_name", name=f"{NAME} - String Quartet")),
          (0, mido.MetaMessage("time_signature", numerator=4, denominator=4)),
          (0, mido.MetaMessage("key_signature", key="Gm"))]
    for b, s, bpm in TEMPI:
        ab.append((tick(OFFS[b] + s), mido.MetaMessage(
            "set_tempo", tempo=mido.bpm2tempo(bpm))))
    for b, letter, title in SECTIONS:
        ab.append((tick(OFFS[b]), mido.MetaMessage(
            "marker", text=((letter + " ") if letter else "")
            + (title.split()[0] if title else ""))))
    ab.sort(key=lambda x: x[0])
    tr, last = mido.MidiTrack(), 0
    for t, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def seconds():
    marks = [(OFFS[b] + s, bpm) for b, s, bpm in TEMPI]
    t = 0.0
    for i, (a, bpm) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else SCORE_LEN
        t += (end - a) / 16 * 60 / bpm
    return t


def write_midi(path, part_ids, parsed):
    mf = mido.MidiFile(type=1, ticks_per_beat=TPQ, charset="utf-8")
    mf.tracks.append(tempo_track())
    for ch, p in enumerate(PARTS):
        if p["id"] in part_ids:
            mf.tracks.append(part_track(p, parsed[p["id"]], ch))
    mf.save(path)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
RANGES = {"vn1": ("G3", "D7"), "vn2": ("G3", "A6"), "va": ("C3", "E6"),
          "vc": ("C2", "A5")}
STRINGS = {"vn1": ["G3", "D4", "A4", "E5"], "vn2": ["G3", "D4", "A4", "E5"],
           "va": ["C3", "G3", "D4", "A4"], "vc": ["C2", "G2", "D3", "A3"]}


def playable(pid, pitches):
    """One note per adjacent string, each within reach above its string,
    and the stopped notes inside one hand frame: a fourth for violin and
    viola (a little more high up), a major third in the cello's neck
    positions, a fourth in thumb position."""
    opens = [midi_of(s) for s in STRINGS[pid]]
    ps = sorted(midi_of(x) for x in pitches)
    n = len(ps)
    if n > 4:
        return False
    for first in range(0, 5 - n):
        strs = opens[first:first + n]
        if not all(p >= s for p, s in zip(ps, strs)):
            continue
        if any(p - s > 17 for p, s in zip(ps, strs)):
            continue
        stopped = [p - s for p, s in zip(ps, strs) if p != s]
        if not stopped:
            return True
        spread = max(stopped) - min(stopped)
        if pid == "vc":
            frame = 5 if min(stopped) >= 10 else 4
        else:
            frame = 6 if min(stopped) >= 7 else 5
        if spread <= frame:
            return True
    return False


def piano_events():
    path = os.path.join(HERE, "piano_source.json")
    if not os.path.exists(path):
        path = os.environ.get("UNRAVEL_PIANO", "")
    if not path or not os.path.exists(path):
        return None
    src = json.load(open(path, encoding="utf-8"))
    bars = {b["bar"]: b for b in src["bars"]}
    out = {}
    for b in MEASURES:
        for v in ("rh", "rh2", "rh3", "lh", "lh2", "lh3"):
            s = (bars[b].get(v) or "").strip()
            if s:
                for e in parse_voice(s, blen(b)):
                    e["bar"] = b
                    e["abs"] = OFFS[b] + e["pos"]
                    out.setdefault(v, []).append(e)
    return out


def _grid(events_by_voice):
    grid = {}
    for evs in events_by_voice:
        held = False
        for e in evs:
            if e["pitches"] is None:
                held = False
                continue
            ps = [midi_of(x) for x in e["pitches"]]
            for t in range(int(floor(e["abs"])),
                           int(ceil(e["abs"] + e["dur"]))):
                grid.setdefault(t, set()).update(ps)
            held = e["tie"]
    return grid


def _attacks(evs):
    """(abs, [midi], bar) for every note that is struck, not continued by
    a tie (ties may pass from one voice to another)."""
    tied = {}
    for e in evs:
        if e["pitches"] is not None and e["tie"]:
            end = e["abs"] + e["dur"]
            tied.setdefault(end, set()).update(midi_of(x)
                                               for x in e["pitches"])
    out = []
    for e in sorted(evs, key=lambda e: e["abs"]):
        if e["pitches"] is None:
            continue
        ps = [midi_of(x) for x in e["pitches"]]
        fresh = [x for x in ps if x not in tied.get(e["abs"], ())]
        if fresh:
            out.append((e["abs"], fresh, e["bar"]))
    return out


_PCN = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def _name(m):
    return f"{_PCN[m % 12]}{m // 12 - 1}"


def check(parsed):
    out = []
    for pid, evs in parsed.items():
        lo, hi = (midi_of(x) for x in RANGES[pid])
        for e in evs:
            for pit in e["pitches"] or []:
                if not lo <= midi_of(pit) <= hi:
                    out.append(f"RANGE: {pid} m{e['bar']} {pit}")
            if e["pitches"] and len(e["pitches"]) > 1 and \
                    not playable(pid, e["pitches"]) and \
                    ("stop", pid, e["bar"]) not in ALLOW:
                out.append(f"STOP: {pid} m{e['bar']} "
                           f"{'+'.join(e['pitches'])} not playable")
    pe = piano_events()
    if pe is None:
        out.append("NOTE: piano_source.json not found, fidelity not checked")
        return out
    q_att = {}
    for pid, evs in parsed.items():
        for a, ps, b in _attacks(evs):
            q_att.setdefault(a, []).extend((pid, x) for x in ps)
    rh = [e for v in ("rh", "rh2", "rh3") for e in pe.get(v, [])]
    lh = [e for v in ("lh", "lh2", "lh3") for e in pe.get(v, [])]
    mel = {}
    for a, ps, b in _attacks(pe.get("rh", [])):
        mel[a] = (max(ps), b)
    for a, (top, b) in sorted(mel.items()):
        att = q_att.get(a, [])
        hi = max((x for _, x in att), default=None)
        v1 = max((x for pid, x in att if pid == "vn1"), default=None)
        got = {x % 12 for x in (hi, v1) if x is not None}
        if top % 12 not in got and ("mel", b) not in ALLOW:
            out.append(f"MELODY: m{b} {_name(top)} at +{a - OFFS[b]} "
                       "missing")
    bass = {}
    for a, ps, b in _attacks(lh):
        if a not in bass or min(ps) < bass[a][0]:
            bass[a] = (min(ps), b)
    for a, (m, b) in sorted(bass.items()):
        att = q_att.get(a, [])
        lo = min((x for _, x in att), default=None)
        c = min((x for pid, x in att if pid == "vc"), default=None)
        got = {x % 12 for x in (lo, c) if x is not None}
        if m % 12 not in got and ("bass", b) not in ALLOW:
            out.append(f"BASS: m{b} {_name(m)} at +{a - OFFS[b]} missing")
    pg = _grid(pe.values())
    # the piano's pedal: a low left-hand note (below C4) keeps sounding
    # until a note at or below it is struck, or the barline — so a cello
    # may hold the root under a broken-chord left hand
    lows = sorted((a, min(ps), b) for a, ps, b in _attacks(lh)
                  if min(ps) < 60)
    for i, (a, m, b) in enumerate(lows):
        end = OFFS[b] + blen(b)
        for a2, m2, b2 in lows[i + 1:]:
            if a2 >= end:
                break
            if m2 <= m:
                end = a2
                break
        for t in range(int(floor(a)), int(ceil(end))):
            pg.setdefault(t, set()).add(m)
    qg = _grid([evs for evs in parsed.values()])
    for t0 in range(0, SCORE_LEN, 4):
        qp = {x % 12 for t in range(t0, t0 + 4) for x in qg.get(t, ())}
        pp = {x % 12 for t in range(t0 - 4, t0 + 8) for x in pg.get(t, ())}
        extra = qp - pp
        if extra:
            b = max(x for x in MEASURES if OFFS[x] <= t0)
            if ("foreign", b) not in ALLOW:
                out.append(f"FOREIGN: m{b} +{t0 - OFFS[b]} "
                           f"{sorted(_PCN[x] for x in extra)}")
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    parsed = {p["id"]: parse_part(p["data"]) for p in PARTS}
    for x in check(parsed):
        print(x)
    if "--check" in sys.argv:
        return
    base = os.path.join(OUT, BASE)
    sc = build_score(parsed)
    sc.write("musicxml", fp=base + ".musicxml")
    polish(base + ".musicxml")
    hollywood.polish_musicxml(base + ".musicxml", META)
    verify_bars(base + ".musicxml")
    write_midi(os.path.join(OUT, f"{NAME}_弦乐四重奏.mid"),
               [p["id"] for p in PARTS], parsed)
    print(f"written to {OUT} ({seconds():.0f} s)")
    if "--mp3" in sys.argv:
        write_mp3()
    if "--pdf" in sys.argv:
        write_pdf()


def write_mp3():
    """Rough GM preview (FluidSynth + FluidR3 GM), for checking notes only."""
    import subprocess
    import tempfile
    sf2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    mid = os.path.join(OUT, f"{NAME}_弦乐四重奏.mid")
    mp3 = os.path.join(OUT, "粗略试听_GM音色_非ACE效果.mp3")
    with tempfile.TemporaryDirectory() as t:
        wav = os.path.join(t, "p.wav")
        subprocess.run(["fluidsynth", "-ni", "-g", "0.7", "-r", "44100",
                        "-F", wav, sf2, mid], check=True,
                       capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-af", "loudnorm=I=-16:TP=-1.5", "-b:a", "160k",
                        mp3], check=True)
    print("mp3:", mp3)


def write_pdf(png_dir=None):
    """Hollywood-standard full score PDF (cover + score + header/footer)."""
    src = os.path.join(OUT, BASE + ".musicxml")
    dst = os.path.join(OUT, f"{NAME}_全曲_总谱.pdf")
    n = hollywood.render_pdf(src, dst, META, png_dir=png_dir)
    print(f"PDF: {dst} ({n} pages)")


if __name__ == "__main__":
    main()
