#!/usr/bin/env python3
"""土耳其进行曲（莫扎特 K.331 第三乐章 Rondo alla Turca）— 弦乐四重奏 编配生成器

Generates, from one source of truth (the four part dictionaries below):
  * MusicXML full score (Sibelius / MuseScore / ACE Studio)
  * String-quartet MIDI (one track per instrument, for ACE Studio's String
    Section), plus one MIDI per instrument
  * the Hollywood-standard full score PDF (tools/hollywood) and part PDFs

Source: the user's piano edition (4 pages, 虫虫音乐), transcribed bar by bar
into source_piano.py and cross-checked against the DCML Urtext encoding.
Key: A minor / A major as in the original, 2/4, Allegretto quarter = 120.

Form (the piano original's repeats are written out, so the second time
through each strain can be scored differently; bar 0 is the pickup):
  Tema (A minor)          1-48    strains m1-8 and m9-24, each twice
  Alla turca (A major)    49-64   m25-32 twice
  Episodio (F# minor)     65-112  m33-40 and m41-56, each twice
  Alla turca              113-128 m57-64 twice
  Tema (A minor)          129-176 m65-72 and m73-88, each twice
  Alla turca (16ths)      177-192 m89-96 twice (2nd ending leads on)
  Coda (A major)          193-223 m97-127
("m.." numbers are the Urtext / Henle bar numbers of the piano original.)

The part data are written per Urtext bar ("m17") with optional second-time
overrides; FORM unrolls them in performance order and joins the split
half-bars at the repeats into full 2/4 bars.

Token syntax (durations in 16ths, .5 = a 32nd; one string per source bar):
  C5/2        note C5, an eighth           A4+E5/4   double stop
  r/2         rest                         A4/1~     tie into the next note
  marks after the duration: .  staccato   >  accent   _  tenuto
                            ^  marcato    tr trill    arp  arpeggiated chord
  (G4/1 A4/1) slur start / slur end
  g:G5        grace note before the next note (gs:G5 = slashed)
  [p] [sfz]   dynamic under the next note;  [cresc.]  [dim.]  words below
  [<] [>]     hairpin start at the next note;  [<|] [>|] hairpin end after
              the previous note
  {pizz.}     technique / expression text above the next note
              ({pizz.} / {arco} also switch the preview MIDI sound)
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
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hollywood"))
import hollywood  # noqa: E402  (shared Hollywood score template)
import source_piano  # noqa: E402  (the transcribed piano original)

NAME = "土耳其进行曲"
TPQ = 480
T32 = TPQ // 8          # ticks per 32nd
BAR = 16                # a 2/4 bar in 32nds
PICKUP = 8              # bar 0: one beat
BPM = 120


# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------
_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def midi_of(p):
    m = re.fullmatch(r"([A-G])(#|b|##|bb)?(-?\d)", p)
    if not m:
        raise ValueError(p)
    s, acc, octv = m.groups()
    v = _STEP[s] + {"#": 1, "b": -1, "##": 2, "bb": -2, None: 0}[acc]
    return 12 * (int(octv) + 1) + v


def m21_name(p):
    return re.sub(r"^([A-G])(b+)", lambda k: k.group(1) + "-" * len(k.group(2)),
                  p)


# ---------------------------------------------------------------------------
# Form: Urtext bar labels in performance order
# ---------------------------------------------------------------------------
def rng(a, b):
    return [f"m{i}" for i in range(a, b + 1)]


FORM = [  # (strain, labels); each strain is listed once per time through
    ("A1", ["m0"] + rng(1, 7) + ["m8a"]),
    ("A1", ["m0"] + rng(1, 7) + ["m8a"]),
    ("A2", ["m8b"] + rng(9, 23) + ["m24a"]),
    ("A2", ["m8b"] + rng(9, 23) + ["m24a"]),
    ("B1", ["m24b"] + rng(25, 31) + ["m32a"]),
    ("B1", ["m24b"] + rng(25, 31) + ["m32a"]),
    ("C1", ["m32b"] + rng(33, 39) + ["m40a"]),
    ("C1", ["m32b"] + rng(33, 39) + ["m40a"]),
    ("C2", ["m40b"] + rng(41, 55) + ["m56a"]),
    ("C2", ["m40b"] + rng(41, 55) + ["m56a"]),
    ("B2", ["m56b"] + rng(57, 63) + ["m64a"]),
    ("B2", ["m56b"] + rng(57, 63) + ["m64a"]),
    ("A3", ["m64b"] + rng(65, 71) + ["m72a"]),
    ("A3", ["m64b"] + rng(65, 71) + ["m72a"]),
    ("A4", ["m72b"] + rng(73, 87) + ["m88a"]),
    ("A4", ["m72b"] + rng(73, 87) + ["m88a"]),
    ("B3", ["m88b"] + rng(89, 95) + ["m96a"]),
    ("B3", ["m88b"] + rng(89, 95) + ["m96b"]),
    ("CO", rng(97, 127)),
]


def performance():
    """[(label, time-through)] in playing order."""
    seen, out = {}, []
    for strain, labels in FORM:
        seen[strain] = seen.get(strain, 0) + 1
        out += [(lab, seen[strain]) for lab in labels]
    return out


def label_len(lab):
    """Length of a source bar in 32nds (split halves and the pickup are one
    beat, m96b is the 2nd ending plus the coda's upbeat)."""
    if lab == "m0" or (lab.endswith(("a", "b")) and lab != "m96b"):
        return PICKUP
    return BAR


def arrangement_bars():
    """Arrangement bar number -> [(label, time-through), ...]."""
    bars, cur, fill = {0: []}, 0, 0
    for lab, t in performance():
        cap = PICKUP if cur == 0 else BAR
        if fill == cap:
            cur, fill = cur + 1, 0
            bars[cur] = []
        bars[cur].append((lab, t))
        fill += label_len(lab)
        assert fill <= (PICKUP if cur == 0 else BAR), (cur, lab)
    return bars


ARR = arrangement_bars()
NBARS = max(ARR)


def bar_len(b):
    return PICKUP if b == 0 else BAR


def bar_start(b):
    return 0 if b == 0 else PICKUP + (b - 1) * BAR


def bar_of(label, time=1):
    """First arrangement bar holding a source bar."""
    for b, labs in ARR.items():
        if (label, time) in labs:
            return b
    raise KeyError((label, time))


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(\()?((?:[A-G](?:#|b|##|bb)?-?\d)(?:\+[A-G](?:#|b|##|bb)?-?\d)*|r)"
    r"/(\d+(?:\.5)?)((?:\.|>|_|\^|tr|arp|fer)*)(~)?(\))?$")
SPLIT = re.compile(r"\{[^}]*\}|\[[^\]]*\]|[^\s\[\{]+")
DYN_MARKS = {"ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "sfz", "sf",
             "fz", "sfp", "fp", "rfz"}


def parse_voice(s, length=None, where=""):
    """One voice of one source bar -> list of events (pos/dur in 32nds)."""
    evs, pos = [], 0
    graces, pre_dyn, pre_txt, pre_hair = [], [], [], []
    slur_pending = False
    tail_hair = []
    for t in SPLIT.findall(s):
        if t.startswith("{"):
            pre_txt.append(t[1:-1])
            continue
        if t.startswith("["):
            m = t[1:-1]
            if m in ("<|", ">|"):
                if evs:
                    evs[-1]["hair_end"].append(m[0])
                else:
                    tail_hair.append(m[0])   # ends right before this bar
            elif m in ("<", ">"):
                pre_hair.append(m)
            else:
                pre_dyn.append(m)
            continue
        if t in ("(",):
            slur_pending = True
            continue
        gm = re.fullmatch(r"(\()?(gs?):([A-G](?:#|b|##|bb)?-?\d)", t)
        if gm:
            if gm.group(1):
                slur_pending = True
            graces.append((gm.group(3), gm.group(2) == "gs"))
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"{where}: bad token {t!r} in {s!r}")
        sl, pit, dur, marks, ti, sr = m.groups()
        d32 = round(float(dur) * 2)
        mk = set(re.findall(r"tr|arp|fer|\.|>|_|\^", marks or ""))
        evs.append(dict(
            pos=pos, dur=d32,
            pitches=None if pit == "r" else pit.split("+"),
            tie=bool(ti), slur_start=bool(sl) or slur_pending,
            slur_end=bool(sr), marks=mk, graces=graces, dyn=pre_dyn,
            text=pre_txt, hair_start=pre_hair, hair_end=[]))
        graces, pre_dyn, pre_txt, pre_hair = [], [], [], []
        slur_pending = False
        pos += d32
    if pre_dyn or pre_txt or pre_hair or graces:
        raise ValueError(f"{where}: dangling marks at the end of {s!r}")
    if length is not None and pos != length:
        raise ValueError(f"{where}: bar sums to {pos / 2:g} 16ths, "
                         f"expected {length / 2:g}: {s!r}")
    if tail_hair:
        evs[0]["hair_end_before"] = tail_hair
    return evs


# ---------------------------------------------------------------------------
# Part data: filled in below the framework (see "THE ARRANGEMENT")
# ---------------------------------------------------------------------------
def lookup(data, data2, lab, t):
    """A source bar's tokens for one part: second-time data first, then an
    alias (the reprises reuse the first statement), then first-time data."""
    names = [lab] + ([ALIAS[lab]] if lab in ALIAS else [])
    order = ([data2] if t >= 2 else []) + [data]
    for d in order:
        for n in names:
            if n in d:
                return d[n]
    raise KeyError(f"no data for {lab} (time {t})")


def part_bars(data, data2):
    """Arrangement bar -> token string for one part."""
    return {b: " ".join(lookup(data, data2, lab, t) for lab, t in labs)
            for b, labs in ARR.items()}


def parse_part(bars):
    evs = []
    for b in range(NBARS + 1):
        try:
            got = parse_voice(bars[b], bar_len(b), where=f"bar {b}")
        except ValueError as e:
            raise ValueError(f"{e}  (source {ARR[b]})") from None
        # a bar of rests (two joined half bars) -> one whole-bar rest
        if b and len(got) > 1 and all(e["pitches"] is None for e in got):
            got = [dict(got[0], dur=BAR,
                        text=sum((e["text"] for e in got), []),
                        dyn=sum((e["dyn"] for e in got), []),
                        hair_start=sum((e["hair_start"] for e in got), []),
                        hair_end=sum((e["hair_end"] for e in got), []))]
        for e in got:
            e["bar"] = b
            e["abs"] = bar_start(b) + e["pos"]
        evs += got
    return evs


# ---------------------------------------------------------------------------
# Notation splitting (keep the beat visible in 2/4)
# ---------------------------------------------------------------------------
def split_dur(pos, dur):
    """Split a note into tied notated pieces; pos / dur in 32nds within a
    2/4 bar (beats at 0 and 8)."""
    pieces = []
    while dur > 0:
        if pos == 0:
            allowed = [16, 12, 8, 6, 4, 3, 2, 1]
        elif pos == 8:
            allowed = [8, 6, 4, 3, 2, 1]
        elif pos == 4:
            allowed = [8, 4, 2, 1]        # 8th-quarter-8th syncopation
        elif pos == 12:
            allowed = [4, 2, 1]
        elif pos % 8 == 2:
            allowed = [6, 2, 1]
        elif pos % 2 == 0:
            allowed = [2, 1]
        else:
            allowed = [1]
        d = next(x for x in allowed if x <= dur)
        pieces.append(d)
        pos += d
        dur -= d
    return pieces


def ql(d32):
    return d32 / 8


# ---------------------------------------------------------------------------
# music21 score
# ---------------------------------------------------------------------------
def _grace_type(n):
    return "16th" if n <= 2 else "32nd"


def make_m21(p, events, lead=None):
    """One part; `lead` (default: Violin I) carries the tempo mark and the
    rehearsal letters, as the top staff of the score and in every part."""
    lead = p["id"] == "vn1" if lead is None else lead
    part = stream.Part(id=p["id"])
    ins = p["inst"]()
    ins.partName = p["name"]
    ins.partAbbreviation = p["abbr"]
    part.insert(0, ins)
    measures, by_bar = {}, {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    slur_open, tied_prev = None, False
    hair_open = {}          # "<" / ">" -> first note object
    last_obj = None
    spanners = []
    for b in range(NBARS + 1):
        m = stream.Measure(number=b)
        if b == 0:
            m.insert(0, p["clef"]())
            m.insert(0, key.Key(KEYS[0]))
            m.insert(0, meter.TimeSignature("2/4"))
            m.paddingLeft = (BAR - PICKUP) / 8    # an anacrusis, not padded
            if lead:
                # the text is joined to it by hollywood.polish_musicxml
                mm = tempo.MetronomeMark(number=BPM, referent=1.0)
                mm.placement = "above"
                m.insert(0, mm)
        elif b in KEYS:
            m.insert(0, key.Key(KEYS[b]))
        pending = []        # (offset, obj) inserted after the notes
        for e in by_bar[b]:
            for k in e.get("hair_end_before", []):
                if k in hair_open and last_obj is not None:
                    spanners.append((k, hair_open.pop(k), last_obj))
            for i, (gp, slash) in enumerate(e["graces"]):
                g = note.Note(m21_name(gp), type=_grace_type(len(e["graces"])))
                g = g.getGrace()
                g.duration.slash = slash
                m.append(g)
                if i == 0 and e["slur_start"]:
                    slur_open = g
            pieces = split_dur(e["pos"], e["dur"])
            objs = []
            for i, d in enumerate(pieces):
                if e["pitches"] is None:
                    n = note.Rest(quarterLength=ql(d))
                else:
                    names = [m21_name(x) for x in e["pitches"]]
                    n = (note.Note(names[0], quarterLength=ql(d))
                         if len(names) == 1 else
                         chord.Chord(names, quarterLength=ql(d)))
                    first, last = i == 0, i == len(pieces) - 1
                    starts = (not first) or tied_prev
                    cont = (not last) or e["tie"]
                    if starts and cont:
                        n.tie = tie.Tie("continue")
                    elif starts:
                        n.tie = tie.Tie("stop")
                    elif cont:
                        n.tie = tie.Tie("start")
                    if first:
                        mk = e["marks"]
                        if "." in mk:
                            n.articulations.append(articulations.Staccato())
                        if ">" in mk:
                            n.articulations.append(articulations.Accent())
                        if "^" in mk:
                            n.articulations.append(
                                articulations.StrongAccent())
                        if "_" in mk:
                            n.articulations.append(articulations.Tenuto())
                        if "tr" in mk:
                            n.expressions.append(expressions.Trill())
                        if "arp" in mk:
                            n.expressions.append(
                                expressions.ArpeggioMark("normal"))
                        if "fer" in mk:
                            f = expressions.Fermata()
                            f.type = "upright"
                            n.expressions.append(f)
                m.append(n)
                objs.append(n)
            e["m21"] = objs
            off = e["pos"] / 8
            for d in e["dyn"]:
                pending.append((off, "dyn", d))
            for t in e["text"]:
                pending.append((off, "text", t))
            if e["pitches"] is not None:
                if e["slur_start"] and slur_open is None:
                    slur_open = objs[0]
                if e["slur_end"] and slur_open is not None:
                    spanners.append(("slur", slur_open, objs[-1]))
                    slur_open = None
            for k in e["hair_start"]:
                hair_open[k] = objs[0]
            for k in e["hair_end"]:
                if k in hair_open:
                    spanners.append((k, hair_open.pop(k), objs[-1]))
            tied_prev = e["tie"] and e["pitches"] is not None
            last_obj = objs[-1]
        # after the notes, or append() would shift them
        for off, kind, val in pending:
            if kind == "dyn":
                if val in DYN_MARKS:
                    d = dynamics.Dynamic(val)
                    d.placement = "below"
                    m.insert(off, d)
                else:           # cresc. / dim. / poco a poco ...
                    te = expressions.TextExpression(val)
                    te.style.fontStyle = "italic"
                    te.placement = "below"
                    m.insert(off, te)
            else:
                te = expressions.TextExpression(val)
                te.style.fontStyle = "italic"
                te.placement = "above"
                m.insert(off, te)
        if lead:
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
        if b + 1 in KEYS or b + 1 in DOUBLE_BARS:
            m.rightBarline = bar.Barline("light-light")
        if b == NBARS:
            m.rightBarline = bar.Barline("final")
        measures[b] = m
        part.append(m)
    assert slur_open is None, (p["id"], "slur left open")
    assert not hair_open, (p["id"], "hairpin left open", hair_open)
    for kind, a, z in spanners:
        if kind == "slur":
            part.insert(0, spanner.Slur(a, z))
        else:
            cls = dynamics.Crescendo if kind == "<" else dynamics.Diminuendo
            part.insert(0, cls(a, z))
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


def polish(path, breaks=True, part_breaks=(), part_pages=()):
    """Instrument sounds, the pickup bar, system breaks (score only),
    dynamics below and words above the staff.  Page layout, credits and
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
            ab = si.find("instrument-abbreviation")
            si.insert(list(si).index(ab) + 1 if ab is not None else 1, el)
    for n in r.iter("note"):
        for x in n.findall("instrument"):
            n.remove(x)
    for part in r.findall("part"):
        for m in part.findall("measure"):
            num = int(m.get("number"))
            if num == 0:
                m.set("implicit", "yes")     # the pickup: not counted
            if (breaks and num in SYSTEM_BREAKS) or num in part_breaks:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                pr.set("new-system", "yes")
            if (breaks and num in PAGE_BREAKS) or num in part_pages:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                pr.set("new-page", "yes")
            for el in m.findall("direction"):
                if el.find("direction-type/dynamics") is not None or \
                        el.find("direction-type/wedge") is not None:
                    el.set("placement", "below")
                elif el.find("direction-type/rehearsal") is not None:
                    el.set("placement", "above")
                elif el.find("direction-type/words") is not None:
                    w = el.find("direction-type/words").text or ""
                    el.set("placement", "below" if w.strip() in BELOW_WORDS
                           else "above")
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
    """Every bar of every part in the written file has the right length."""
    from music21 import converter
    for p in converter.parse(path).parts:
        ms = p.getElementsByClass("Measure")
        assert len(ms) == NBARS + 1, (p.partName, len(ms))
        for m in ms:
            want = bar_len(m.number) / 8
            got = sum(n.quarterLength for n in m.notesAndRests)
            assert abs(got - want) < 1e-6, (p.partName, m.number, got)


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
VEL = {"ppp": 26, "pp": 36, "p": 48, "mp": 60, "mf": 74, "f": 90, "ff": 104,
       "fff": 116}
ACCENT = 14
SFZ = 26          # sfz / fz / sf: a one-note accent above the running level


def merged_notes(events):
    """Tied notes merged: [dict(start, dur, pitches, marks, graces, dyn,
    legato, pizz)] (32nds)."""
    out, cur, in_slur, pizz = [], None, False, False
    for e in events:
        for t in e["text"]:
            if t.startswith("pizz"):
                pizz = True
            elif t.startswith("arco"):
                pizz = False
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
        starts_slur = e["slur_start"] or bool(e["graces"] and e["slur_start"])
        cur = dict(start=e["abs"], dur=e["dur"], pitches=e["pitches"],
                   tie=e["tie"], marks=e["marks"], graces=e["graces"],
                   dyn=e["dyn"], pizz=pizz,
                   legato=in_slur or (starts_slur and not e["slur_end"]))
        out.append(cur)
        if starts_slur:
            in_slur = True
        if e["slur_end"]:
            in_slur = False
            cur["slur_last"] = True
    return out


RAMP = 12   # how far a hairpin moves when no dynamic mark gives it a target


def dyn_curve(events):
    """Velocity at every absolute 32nd.  Marked dynamics set the level;
    hairpins and cresc./dim. words ramp from the running level, in the
    order they start.  A ramp (with the same-way ramps that follow it
    within a beat) aims at the next marked dynamic when that follows
    within a beat and lies in its direction; otherwise a crescendo rises
    RAMP and a diminuendo returns to the marked level (RAMP below it if
    already there).  A ramp's last level holds until the next mark or
    ramp; a cresc./dim. word runs to the next mark or opposite ramp."""
    total = bar_start(NBARS) + BAR
    pts, ramps, open_ramp = [], [], {}
    for e in events:
        for d in e["dyn"]:
            if d in VEL:
                pts.append((e["abs"], VEL[d]))
            elif d.startswith(("cresc", "dim", "decresc")):
                ramps.append((e["abs"], None, "<" if d.startswith("cresc")
                              else ">"))
        for k in e.get("hair_end_before", []):
            if k in open_ramp:
                ramps.append((open_ramp.pop(k), e["abs"] - 1, k))
        for k in e["hair_start"]:
            open_ramp[k] = e["abs"]
        for k in e["hair_end"]:
            if k in open_ramp:
                ramps.append((open_ramp.pop(k), e["abs"] + e["dur"] - 1, k))
    pts.sort()
    ramps.sort(key=lambda r: r[0])
    marked = [pts[0][1] if pts else VEL["mf"]] * total
    for i, (a, val) in enumerate(pts):
        end = pts[i + 1][0] if i + 1 < len(pts) else total
        for t in range(a, end):
            marked[t] = val
    v = marked[:]
    at_mark = {t for t, _ in pts}
    ends = []
    for i, (a, z, kind) in enumerate(ramps):
        tm = next((t for t, _ in pts if t > a), total)
        opp = next((r[0] for r in ramps[i + 1:] if r[2] != kind and r[0] > a),
                   total)
        ends.append(z if z is not None else min(tm, opp) - 1)
    for i, (a, _, kind) in enumerate(ramps):
        z = ends[i]
        tm, tv = next(((t, val) for t, val in pts if t > a), (total, None))
        chain, j = z, i + 1          # same-way ramps starting within a beat
        while j < len(ramps):
            if ramps[j][0] > chain + 9 or ramps[j][0] >= tm:
                break
            if ramps[j][2] != kind:
                chain = None
                break
            chain = max(chain, ends[j])
            j += 1
        v0 = v[a] if (a == 0 or a in at_mark) else v[a - 1]
        up = kind == "<"
        if (chain is not None and tv is not None and tm - chain - 1 <= 8
                and (tv > v0 if up else tv < v0)):
            v1 = v0 + (tv - v0) * (z + 1 - a) / (chain + 1 - a)
        elif up:
            v1 = v0 + RAMP
        else:
            v1 = marked[a] if v0 > marked[a] else v0 - RAMP
        for t in range(a, z + 1):
            v[t] = round(v0 + (v1 - v0) * (t - a) / max(1, z - a))
        stop = min([t for t, _ in pts if t > z]
                   + [r[0] for r in ramps if r[0] > z] + [total])
        for t in range(z + 1, stop):
            v[t] = round(v1)
    return v


# The MIDI starts with one silent beat, so the pickup falls on beat 2 of
# the file's first 2/4 bar and every barline lines up with the score's:
# bar N of the score is bar N + 1 in ACE Studio or a DAW.
LEAD = TPQ


def tempo_track(title):
    ab = [(0, mido.MetaMessage("track_name", name="Rondo alla Turca")),
          (0, mido.MetaMessage("time_signature", numerator=2, denominator=4))]
    for b, k in KEYS.items():
        ab.append((0 if b == 0 else LEAD + bar_start(b) * T32,
                   mido.MetaMessage("key_signature",
                                    key="Am" if k == "a" else "A")))
    for b, s, bpm in TEMPI:
        ab.append((0 if b == 0 and s == 0 else LEAD + (bar_start(b) + s) * T32,
                   mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))))
    for b, letter, name in SECTIONS:
        ab.append((LEAD + bar_start(b) * T32, mido.MetaMessage(
            "marker", text=(f"{letter} " if letter else "") + name)))
    ab.sort(key=lambda x: x[0])
    tr, last = mido.MidiTrack(), 0
    for t, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


GRACE_T = 50          # ticks per grace note (played on the beat)
ARP_T = 22            # ticks between the notes of a rolled chord

# the diatonic upper neighbour for trills, per key
_SCALES = {"a": ["A", "B", "C", "D", "E", "F", "G#"],
           "A": ["A", "B", "C#", "D", "E", "F#", "G#"]}


def key_at(b):
    return KEYS[max(k for k in KEYS if k <= b)]


def upper_neighbour(pit, b):
    sc = _SCALES[key_at(b)]
    m = midi_of(pit)
    for up in range(1, 3):
        cand = m + up
        name = [n for n in sc if midi_of(n + "4") % 12 == cand % 12]
        if name:
            return cand
    return m + 2


def part_track(p, events, ch, gm_preview=True):
    notes = merged_notes(events)
    vel = dyn_curve(events)
    ab = [(0, 0, mido.MetaMessage("track_name", name=p["name"])),
          (0, 1, mido.Message("program_change", channel=ch,
                              program=p["program"]))]
    for t in range(0, len(vel), 4):
        if t == 0 or vel[t] != vel[t - 4]:
            val = min(127, 20 + vel[t])
            ab.append((t * T32, 2, mido.Message(
                "control_change", channel=ch, control=11, value=val)))
            ab.append((t * T32, 2, mido.Message(
                "control_change", channel=ch, control=1, value=val)))
    prog = p["program"]
    for i, n in enumerate(notes):
        b = next(bb for bb in range(NBARS, -1, -1)
                 if bar_start(bb) <= n["start"])
        if gm_preview:
            want = 45 if n["pizz"] else p["program"]
            if want != prog:
                ab.append((n["start"] * T32, 1, mido.Message(
                    "program_change", channel=ch, program=want)))
                prog = want
        on = n["start"] * T32
        length = n["dur"] * T32
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        mk = n["marks"]
        if n["pizz"]:
            length = min(length, 3 * T32)
        elif "." in mk:
            length = max(T32, int(length * 0.45))
        elif "_" in mk or (n["legato"] and not n.get("slur_last")):
            length = length + 8          # legato overlap
        else:
            length = int(length * 0.9)
        off = on + length
        if nxt and nxt["start"] * T32 < off:
            # what the next note sounds first: its pitches, its grace notes
            # and (for a trill) the upper neighbour it starts on
            nm = {midi_of(x) for x in nxt["pitches"]}
            nm |= {midi_of(gp) for gp, _ in nxt["graces"]}
            if "tr" in nxt["marks"]:
                nb = next(bb for bb in range(NBARS, -1, -1)
                          if bar_start(bb) <= nxt["start"])
                nm.add(upper_neighbour(nxt["pitches"][-1], nb))
            if nm & {midi_of(x) for x in n["pitches"]}:
                off = nxt["start"] * T32 - 10
        v = vel[min(n["start"], len(vel) - 1)]
        if ">" in mk or "^" in mk:
            v += ACCENT + (6 if "^" in mk else 0)
        if any(d in ("sfz", "sf", "fz", "rfz") for d in n["dyn"]):
            v += SFZ
        v = max(1, min(127, v))
        t0 = on
        for gp, _ in n["graces"]:
            ab.append((t0, 5, mido.Message("note_on", channel=ch,
                                           note=midi_of(gp), velocity=v)))
            ab.append((t0 + GRACE_T, 3, mido.Message(
                "note_off", channel=ch, note=midi_of(gp), velocity=0)))
            t0 += GRACE_T
        on = t0
        if "tr" in mk:
            main = midi_of(n["pitches"][-1])
            up = upper_neighbour(n["pitches"][-1], b)
            t, k = on, 0
            while t + T32 <= off:
                pit = up if k % 2 == 0 else main
                ab.append((t, 5, mido.Message("note_on", channel=ch,
                                              note=pit, velocity=v - 6)))
                ab.append((t + T32 - 4, 3, mido.Message(
                    "note_off", channel=ch, note=pit, velocity=0)))
                t += T32
                k += 1
            continue
        pits = sorted(n["pitches"], key=midi_of)
        for j, pit in enumerate(pits):
            dt = j * ARP_T if ("arp" in mk or len(pits) >= 3) else 0
            ab.append((on + dt, 5, mido.Message("note_on", channel=ch,
                                                note=midi_of(pit),
                                                velocity=v)))
            ab.append((max(off, on + dt + 20), 3, mido.Message(
                "note_off", channel=ch, note=midi_of(pit), velocity=0)))
    # everything but the header (track name, first program) moves by LEAD
    ab = [(t if (t == 0 and o < 2) else t + LEAD, o, m) for t, o, m in ab]
    ab.sort(key=lambda x: (x[0], x[1]))
    tr, last = mido.MidiTrack(), 0
    for t, _, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def write_midi(path, part_ids, parsed, gm_preview=False):
    mf = mido.MidiFile(type=1, ticks_per_beat=TPQ, charset="utf-8")
    mf.tracks.append(tempo_track(NAME))
    for ch, p in enumerate(PARTS):
        if p["id"] in part_ids:
            mf.tracks.append(part_track(p, parsed[p["id"]], ch,
                                        gm_preview=gm_preview))
    mf.save(path)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
RANGES = {"vn1": ("G3", "A6"), "vn2": ("G3", "E6"), "va": ("C3", "A5"),
          "vc": ("C2", "E4")}
STRINGS = {"vn1": ("G3", "D4", "A4", "E5"), "vn2": ("G3", "D4", "A4", "E5"),
           "va": ("C3", "G3", "D4", "A4"), "vc": ("C2", "G2", "D3", "A3")}


def source_events():
    """The piano original unrolled in performance order, on the same
    timeline as the arrangement: {"rh": [...], "lh": [...]}."""
    out = {"rh": [], "lh": []}
    t0 = 0
    for lab, _ in performance():
        n = label_len(lab)
        for hand, data in (("rh", source_piano.RH), ("lh", source_piano.LH)):
            for v in data[lab].split("||"):
                for e in parse_voice(v, n, where=f"source {lab} {hand}"):
                    e["abs"] = t0 + e["pos"]
                    e["label"] = lab
                    out[hand].append(e)
        t0 += n
    return out


def sounding(evs_by_part):
    """abs32 -> [(part, midi, name, attacked-here)] (ties = held)."""
    grid = {}
    for pid, evs in evs_by_part.items():
        held = set()
        for e in evs:
            if e["pitches"] is None:
                held = set()
                continue
            for t in range(e["abs"], e["abs"] + e["dur"]):
                for pit in e["pitches"]:
                    grid.setdefault(t, []).append(
                        (pid, midi_of(pit), pit,
                         t == e["abs"] and pit not in held))
            held = set(e["pitches"]) if e["tie"] else set()
    return grid


def playable(pits, pid):
    """Can this double / triple / quadruple stop be fingered?  Notes go on
    adjacent strings, low to high, one per string, all within one hand
    frame (a sixth above the lowest stopped note, open strings free)."""
    opens = [midi_of(x) for x in STRINGS[pid]]
    ms = sorted(midi_of(x) for x in pits)
    k = len(ms)
    for first in range(0, 5 - k):
        strs = list(range(first, first + k))
        stops = []
        ok = True
        for m, s in zip(ms, strs):
            if m < opens[s] or m > opens[s] + 12:
                ok = False
                break
            if m != opens[s]:
                stops.append(m - opens[s])
        if ok and (not stops or max(stops) - min(stops) <= 5):
            return True
    return False


def label_at(abs32):
    """The source bar (Urtext label) sounding at an absolute 32nd."""
    t0 = 0
    for lab, _ in performance():
        if t0 <= abs32 < t0 + label_len(lab):
            return lab
        t0 += label_len(lab)
    return None


def allowed(kind, abs32, pid=None):
    """ALLOW holds (kind, label[, part]) for deliberate departures from the
    piano original; aliases share their source's entries."""
    lab = label_at(abs32)
    names = {lab, ALIAS.get(lab)}
    return any((kind, n) in ALLOW or (kind, n, pid) in ALLOW for n in names)


def where(abs32):
    b = next(bb for bb in range(NBARS, -1, -1) if bar_start(bb) <= abs32)
    pos = abs32 - bar_start(b)
    return f"b{b}.{pos / 2:g}", b


def check(parsed):
    out = []
    # ranges and multiple stops
    for pid, evs in parsed.items():
        lo, hi = (midi_of(x) for x in RANGES[pid])
        for e in evs:
            for pit in (e["pitches"] or []) + [g for g, _ in e["graces"]]:
                if not lo <= midi_of(pit) <= hi:
                    out.append(f"RANGE: {pid} b{e['bar']} {pit}")
            if e["pitches"] and len(e["pitches"]) > 1 and \
                    not playable(e["pitches"], pid):
                out.append(f"STOP: {pid} b{e['bar']} "
                           f"{'+'.join(e['pitches'])} not playable")
    src = source_events()
    sgrid = sounding(src)
    agrid = sounding(parsed)
    # melody: every top note the piano's right hand attacks is attacked by
    # some instrument at the same moment (octave doubling allowed)
    tops, held = {}, False
    for e in src["rh"]:
        if e["pitches"] is None:
            held = False
            continue
        if not held:
            m = max(midi_of(x) for x in e["pitches"])
            tops[e["abs"]] = max(tops.get(e["abs"], 0), m)
        held = e["tie"]
    for t, m in sorted(tops.items()):
        att = [x for x in agrid.get(t, []) if x[3]]
        if not any((x[1] - m) % 12 == 0 and abs(x[1] - m) <= 12
                   for x in att) and not allowed("melody", t):
            w, b = where(t)
            out.append(f"MELODY: {w} ({label_at(t)}) top {m} not attacked")
    # bass on each downbeat of the original
    lab_t, t0 = [], 0
    for lab, _ in performance():
        if label_len(lab) == BAR or lab == "m96b":
            lab_t.append((lab, t0))
        t0 += label_len(lab)
    for lab, t in lab_t:
        low = [x for x in sgrid.get(t, []) if x[0] == "lh"]
        mine = agrid.get(t, [])
        if not low or not mine:
            continue
        want = min(x[1] for x in low) % 12
        got = min(x[1] for x in mine) % 12
        w, b = where(t)
        if want != got and not allowed("bass", t):
            out.append(f"BASS: {w} ({lab}) lowest pc {got}, piano {want}")
    # foreign notes: every attacked pitch class occurs in the original
    # somewhere in the same source bar (or half bar at the repeats)
    segs, t0 = [], 0
    for lab, _ in performance():
        segs.append((t0, t0 + label_len(lab)))
        t0 += label_len(lab)
    seg_of = {}
    for a, z in segs:
        for u in range(a, z):
            seg_of[u] = (a, z)
    seg_pcs = {}
    for t in sorted(agrid):
        a, z = seg_of[t]
        if (a, z) not in seg_pcs:
            pcs = {x[1] % 12 for u in range(a, z)
                   for x in sgrid.get(u, [])}
            pcs |= {midi_of(g) % 12 for h in ("rh", "lh") for e in src[h]
                    if a <= e["abs"] < z for g, _ in e["graces"]}
            seg_pcs[(a, z)] = pcs
        pcs = seg_pcs[(a, z)]
        for pid, m, name, att in agrid[t]:
            if att and m % 12 not in pcs and not allowed("foreign", t, pid):
                w, b = where(t)
                out.append(f"FOREIGN: {w} ({label_at(t)}) {pid}:{name}")
    # clashes (minor 2nd / 9th) that the original does not have
    for t, snd in sorted(agrid.items()):
        spcs = {x[1] % 12 for x in sgrid.get(t, [])}
        for i in range(len(snd)):
            for j in range(i + 1, len(snd)):
                a, b2 = snd[i], snd[j]
                if a[0] == b2[0] or not (a[3] or b2[3]):
                    continue
                if abs(a[1] - b2[1]) % 12 == 1 and \
                        not {a[1] % 12, b2[1] % 12} <= spcs:
                    if not allowed("clash", t):
                        w, b = where(t)
                        out.append(f"CLASH: {w} ({label_at(t)}) {a[0]}:{a[2]}"
                                   f" x {b2[0]}:{b2[2]}")
    out += parallels(parsed)
    return out


def top_line(evs):
    """[(abs32, midi or None)] attacks of the highest note of one part."""
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


def parallels(parsed):
    """Consecutive perfect fifths between two parts, and parallel octaves
    that are not part of a deliberate doubling (a run of 3+ octaves)."""
    lines = {pid: top_line(evs) for pid, evs in parsed.items()}
    ids = list(parsed)
    out = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = dict(lines[ids[i]]), dict(lines[ids[j]])
            ta, tb = sorted(a), sorted(b)
            times = sorted(set(ta) | set(tb))
            cur_a = cur_b = None
            seq = []   # (t, pa, pb) at each change
            for t in times:
                if t in a:
                    cur_a = a[t]
                if t in b:
                    cur_b = b[t]
                seq.append((t, cur_a, cur_b))
            run = []
            for k in range(1, len(seq)):
                t, pa, pb = seq[k]
                _, qa, qb = seq[k - 1]
                if None in (pa, pb, qa, qb) or pa == qa or pb == qb:
                    if len(run) == 1:
                        out.append(run[0])
                    run = []
                    continue
                same = (pa - qa) * (pb - qb) > 0
                iv0, iv1 = abs(qa - qb) % 12, abs(pa - pb) % 12
                w, bb = where(t)
                if same and iv0 == iv1 == 7 and not allowed("p5", t):
                    out.append(f"PARALLEL: {w} ({label_at(t)}) "
                               f"{ids[i]}/{ids[j]} P5")
                if same and iv0 == iv1 == 0:
                    run.append("ok" if allowed("p8", t) else
                               f"PARALLEL: {w} ({label_at(t)}) "
                               f"{ids[i]}/{ids[j]} P8")
                else:
                    if len(run) == 1 and run[0] != "ok":
                        out.append(run[0])
                    run = []
            if len(run) == 1 and run[0] != "ok":
                out.append(run[0])
    return [x for x in out if x != "ok"]


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
def parse_all():
    return {p["id"]: parse_part(part_bars(p["data"], p.get("data2", {})))
            for p in PARTS}


def base_path():
    return os.path.join(OUT, f"{NAME}_弦乐四重奏")


def render_mp3(parsed):
    """GM preview (FluidSynth), only for checking the notes."""
    import subprocess
    import tempfile
    sf2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
    with tempfile.TemporaryDirectory() as t:
        mid = os.path.join(t, "p.mid")
        wav = os.path.join(t, "p.wav")
        write_midi(mid, [p["id"] for p in PARTS], parsed, gm_preview=True)
        subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-r", "44100",
                        "-F", wav, sf2, mid], check=True,
                       capture_output=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-af", "loudnorm=I=-16:TP=-1.5", "-b:a", "160k",
                        os.path.join(OUT, "粗略试听_GM音色_非ACE效果.mp3")],
                       check=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    parsed = parse_all()
    for x in check(parsed):
        print(x)
    if "--check" in sys.argv:
        return
    base = base_path()
    sc = build_score(parsed)
    sc.write("musicxml", fp=base + ".musicxml")
    polish(base + ".musicxml")
    hollywood.polish_musicxml(base + ".musicxml", META)
    verify_bars(base + ".musicxml")
    write_midi(base + ".mid", [p["id"] for p in PARTS], parsed)
    print("written to", OUT)
    if "--mp3" in sys.argv:
        render_mp3(parsed)
    if "--pdf" in sys.argv:
        write_pdf()
        write_parts(parsed)


def write_parts(parsed):
    """Part PDFs (分谱), one bookmark per instrument, 9 x 12 in."""
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        xmls = []
        for p in PARTS:
            sc = stream.Score()
            md = metadata.Metadata()
            md.title = META["title"]
            md.composer = META["composer"]
            sc.insert(0, md)
            sc.insert(0, make_m21(p, parsed[p["id"]], lead=True))
            path = os.path.join(t, f"{p['id']}.musicxml")
            sc.write("musicxml", fp=path)
            polish(path, breaks=False,
                   part_breaks=PART_BREAKS.get(p["id"], ()),
                   part_pages=PART_PAGE_BREAKS.get(p["id"], ()))
            hollywood.polish_musicxml(path, META, part=(p["name"], p["zh"]))
            xmls.append((path, p["name"], p["zh"]))
        dst = os.path.join(OUT, f"{NAME}_分谱.pdf")
        n = hollywood.render_parts_pdf(xmls, dst, META)
    print(f"parts: {dst} ({n} pages)")


def write_pdf(png_dir=None):
    """Hollywood-standard full score PDF (cover + score + header/footer)."""
    dst = os.path.join(OUT, f"{NAME}_总谱.pdf")
    n = hollywood.render_pdf(base_path() + ".musicxml", dst, META,
                             png_dir=png_dir)
    print(f"PDF: {dst} ({n} pages)")


# ===========================================================================
# THE ARRANGEMENT
#
# Voices come from the piano: Violin I the right hand's melody, Violin II
# its second voice (the thirds and sixths) and the upper note of the left
# hand's chords, Viola the lower chord note, Cello the bass.  Registers are
# the piano's own in the quiet theme (a light, tenor-register accompaniment,
# as Mozart wrote it); the cello drops an octave in the episode and the
# forte passages.  Second times through a strain change the colour:
#   Tema          2nd time: viola and cello pizzicato (cello 8vb)
#   Alla turca    2nd time: viola and cello pizzicato "Janissary drum"
#   Episodio      2nd time (F# minor): the viola sings the 16ths an octave
#                 lower, the others accompany pizzicato;
#                 (A major, forte): violins in octaves, viola double stops
#   Alla turca 3  2nd time: the violas' ... see B3 below
# The reprise of the Tema (m64b-88) and the second Alla turca (m56b-64) are
# scored like their first appearance (ALIAS), apart from the arco / pizz.
# changes their neighbours need.
# ===========================================================================
ALIAS = {}
ALIAS.update({f"m{i + 64}": f"m{i}" for i in range(1, 24)})   # m65-87
ALIAS.update({"m64b": "m0", "m72a": "m8a", "m72b": "m8b", "m88a": "m24a"})
ALIAS.update({f"m{i + 32}": f"m{i}" for i in range(25, 32)})  # m57-63
ALIAS.update({"m56b": "m24b", "m64a": "m32a"})


def rep(tok, n):
    return " ".join([tok] * n)


# ---- Tema (A minor): m0-8a, m8b-24a ----------------------------------------
VN1 = {
    "m0": "[p] (B4/1 A4/1 G#4/1 A4/1",
    "m1": "C5/2.) r/2 (D5/1 C5/1 B4/1 C5/1",
    "m2": "E5/2.) r/2 (F5/1 E5/1 D#5/1 E5/1",
    "m3": "B5/1 A5/1 G#5/1 A5/1 B5/1 A5/1 G#5/1 A5/1",
    "m4": "C6/4>) A5/2. C6/2.",
    "m5": "(g:G5 g:A5 [sfz] B5/2) A5/2 G5/2 A5/2",
    "m6": "(g:G5 g:A5 [sfz] B5/2.) A5/2. G5/2. A5/2.",
    "m7": "(g:G5 g:A5 [sfz] B5/2) A5/2 G5/2 F#5/2",
    "m8a": "E5/4_",
    "m8b": "[mp] E5/2. F5/2.",
    "m9": "G5/2. G5/2. (A5/1 G5/1 F5/1 E5/1)",
    "m10": "D5/4> E5/2. F5/2.",
    "m11": "G5/2. G5/2. (A5/1 G5/1 F5/1 E5/1)",
    "m12": "D5/4>_ C5/2. D5/2.",
    "m13": "E5/2. E5/2. (F5/1 E5/1 D5/1 C5/1)",
    "m14": "B4/4> C5/2. D5/2.",
    "m15": "E5/2. E5/2. (F5/1 E5/1 D5/1 C5/1)",
    "m16": "B4/4>_ [p] (B4/1 A4/1 G#4/1 A4/1",
    "m17": "C5/2.) r/2 (D5/1 C5/1 B4/1 C5/1",
    "m18": "E5/2.) r/2 (F5/1 E5/1 D#5/1 E5/1",
    "m19": "[cresc.] B5/1 A5/1 G#5/1 A5/1 [<] B5/1 A5/1 G#5/1 A5/1 [<|]",
    "m20": "C6/4) A5/2. B5/2.",
    "m21": "[>] C6/2.> B5/2. A5/2. G#5/2. [>|]",
    "m22": "[>] A5/2. E5/2. F5/2. D5/2. [>|]",
    "m23": "[p] C5/4_ (B4/3tr A4/0.5 B4/0.5",
    "m24a": "A4/4_)",
}
VN2 = {
    "m0": "r/4",
    "m1": "[p] r/2 E4/2. E4/2. E4/2.",
    "m2": "r/2 E4/2. E4/2. E4/2.",
    "m3": "r/2 E4/2. r/2 E4/2.",
    "m4": "r/2 E4/2. E4/2. E4/2.",
    "m5": "r/2 F#5/2 E5/2 F#5/2",
    "m6": "r/2 F#5/2. E5/2. F#5/2.",
    "m7": "r/2 F#5/2 E5/2 D#5/2",
    "m8a": "r/4",
    "m8b": "[mp] C5/2. D5/2.",
    # sixths under the running 16ths (thirds would put F5 on the beat
    # against the cello's E3)
    "m9": "E5/2. E5/2. (C5/1 B4/1 A4/1 G4/1)",
    "m10": "(B4/2 G4/2) C5/2. D5/2.",
    "m11": "E5/2. E5/2. (C5/1 B4/1 A4/1 G4/1)",
    "m12": "B4/4>_ A4/2. B4/2.",
    "m13": "C5/2. C5/2. (D5/1 C5/1 B4/1 A4/1)",
    "m14": "(G#4/2 E4/2) A4/2. B4/2.",
    "m15": "C5/2. C5/2. (D5/1 C5/1 B4/1 A4/1)",
    "m16": "G#4/4>_ r/4",
    "m17": "[p] r/2 E4/2. E4/2. E4/2.",
    "m18": "r/2 E4/2. E4/2. E4/2.",
    "m19": "[cresc.] r/2 E4/2. [<] r/2 E4/2. [<|]",
    "m20": "r/2 D#4/2. D#4/2. D#4/2.",
    "m21": "r/2 [>] E4/2. r/2 B3/2. [>|]",
    "m22": "r/2 [>] A3/2. r/2 B3/2. [>|]",
    "m23": "[p] E4/8_",
    "m24a": "E4/4_",
}
VA = {
    "m0": "r/4",
    "m1": "r/2 [p] C4/2. C4/2. C4/2.",
    "m2": "r/2 C4/2. C4/2. C4/2.",
    "m3": "r/2 C4/2. r/2 C4/2.",
    "m4": "r/2 C4/2. C4/2. C4/2.",
    "m5": "r/2 B3+E4/2. B3+E4/2. B3+E4/2.",
    "m6": "r/2 B3+E4/2. B3+E4/2. B3+E4/2.",
    "m7": "r/2 B3+E4/2. r/2 B3/2.",
    "m8a": "r/4",
    # m8b-16: a trio of the violins' thirds over the cello's octave leaps
    "m8b": "r/4",
    **{f"m{i}": "r/8" for i in range(9, 16)},
    "m16": "r/4 {arco} r/4",
    "m17": "r/2 [p] C4/2. C4/2. C4/2.",
    "m18": "r/2 C4/2. C4/2. C4/2.",
    "m19": "[cresc.] r/2 C4/2. [<] r/2 C4/2. [<|]",
    "m20": "r/2 A3/2. A3/2. A3/2.",
    "m21": "r/2 [>] A3/2. r/2 F3/2. [>|]",
    "m22": "r/2 [>] E3/2. r/2 F3/2. [>|]",
    "m23": "[p] A3/2. A3/2. G#3/2. G#3/2.",
    "m24a": "A3/4_",
}
VC = {
    "m0": "r/4",
    "m1": "[p] A3/2 r/2 r/4",
    "m2": "A3/2 r/2 r/4",
    "m3": "A3/2. r/2 A3/2. r/2",
    "m4": "A3/2 r/2 r/4",
    "m5": "E3/2. r/2 r/4",
    "m6": "E3/2. r/2 r/4",
    "m7": "E3/2. r/2 B2/2. r/2",
    "m8a": "E3/4_",
    "m8b": "r/4",
    "m9": "{arco} [mp] C3/2. C4/2. E3/2. E4/2.",
    "m10": "G3/4 r/4",
    "m11": "C3/2. C4/2. E3/2. E4/2.",
    "m12": "G3/4 r/4",
    "m13": "A2/2. A3/2. C3/2. C4/2.",
    "m14": "E3/4 r/4",
    "m15": "A2/2. A3/2. C3/2. C4/2.",
    "m16": "E3/4_ r/4",
    "m17": "[p] A3/2 r/2 r/4",
    "m18": "A3/2 r/2 r/4",
    "m19": "[cresc.] A3/2. r/2 [<] A3/2. r/2 [<|]",
    "m20": "F3/2 r/2 r/4",
    "m21": "[>] E3/2. r/2 D3/2. r/2 [>|]",
    "m22": "[>] C3/2. r/2 D3/2. r/2 [>|]",
    "m23": "[p] E3/2. E3/2. E3/2. E3/2.",
    "m24a": "A2/4_",
}
# second time: viola and cello pizzicato, the cello an octave lower; in the
# middle strain the viola answers the cello's octave leaps instead
VA2 = {
    "m0": "{pizz.} r/4",
    "m1": "r/2 C4/2 C4/2 C4/2", "m2": "r/2 C4/2 C4/2 C4/2",
    "m3": "r/2 C4/2 r/2 C4/2", "m4": "r/2 C4/2 C4/2 C4/2",
    "m5": "r/2 B3+E4/2 B3+E4/2 B3+E4/2",
    "m6": "r/2 B3+E4/2 B3+E4/2 B3+E4/2",
    "m7": "r/2 B3+E4/2 r/2 B3/2",
    "m9": "r/2 [mp] C4/2. r/2 E4/2.", "m11": "r/2 C4/2. r/2 E4/2.",
    "m13": "r/2 A3/2. r/2 C4/2.", "m15": "r/2 A3/2. r/2 C4/2.",
    "m16": "r/4 {pizz.} r/4",
    "m17": "r/2 [p] C4/2 C4/2 C4/2", "m18": "r/2 C4/2 C4/2 C4/2",
    "m19": "[cresc.] r/2 C4/2 [<] r/2 C4/2 [<|]", "m20": "r/2 A3/2 A3/2 A3/2",
    "m21": "r/2 [>] A3/2 r/2 F3/2 [>|]", "m22": "r/2 [>] E3/2 r/2 F3/2 [>|]",
    "m23": "[p] A3/2 A3/2 G#3/2 G#3/2", "m24a": "A3/4",
}
VC2 = {
    "m0": "{pizz.} r/4",
    "m1": "A2/2 r/2 r/4", "m2": "A2/2 r/2 r/4", "m3": "A2/2 r/2 A2/2 r/2",
    "m4": "A2/2 r/2 r/4", "m5": "E2/2 r/2 r/4", "m6": "E2/2 r/2 r/4",
    "m7": "E2/2 r/2 B2/2 r/2", "m8a": "E2/4",
    "m9": "[mp] C3/2. r/2 E3/2. r/2", "m11": "C3/2. r/2 E3/2. r/2",
    "m13": "A2/2. r/2 C3/2. r/2", "m15": "A2/2. r/2 C3/2. r/2",
    "m16": "E3/4_ {pizz.} r/4",
    "m17": "[p] A2/2 r/2 r/4", "m18": "A2/2 r/2 r/4",
    "m19": "[cresc.] A2/2 r/2 [<] A2/2 r/2 [<|]", "m20": "F2/2 r/2 r/4",
    "m21": "[>] E2/2 r/2 D2/2 r/2 [>|]", "m22": "[>] C2/2 r/2 D2/2 r/2 [>|]",
    "m23": "[p] E2/2 E2/2 E2/2 E2/2", "m24a": "A2/4",
}
VN12, VN22 = {}, {}

# ---- Alla turca (A major, forte): m24b-32a ---------------------------------
# The piano's grace-note arpeggio before each drum beat becomes a rolled,
# accented triple stop across three strings: the Janissary bass drum as a
# cellist plays it (and narrow enough in print for 8-bar systems).
DRUM_A = "A2+E3+A3/2>arp A3/2. A3/2. A3/2."
DRUM_E = "E2+B2+E3/2>arp E3/2. E3/2. E3/2."
DRUM_D = "D2+A2+D3/2>arp D3/2."
DRUM_D_ = "D#2+A2+D#3/2>arp D#3/2."
DRUM_E_ = "E2+B2+E3/2>arp E3/2."


def pizz(s):
    """The same notes pizzicato: no staccato dots, tenutos or slurs."""
    return re.sub(r"[()_]", "", s.replace("/2.>", "/2>").replace("/2.", "/2")
                  .replace("/4.", "/4"))


VN1.update({
    "m24b": "[f] A5/2. B5/2.",
    "m25": "C#6/4> A5/2. B5/2.",
    "m26": "C#6/2.> B5/2. A5/2. G#5/2.",
    "m27": "F#5/2. G#5/2. A5/2. B5/2.",
    "m28": "(G#5/2 E5/2.) A5/2. B5/2.",
    "m29": "C#6/4> A5/2. B5/2.",
    "m30": "C#6/2.> B5/2. A5/2. G#5/2.",
    "m31": "F#5/2. B5/2. G#5/2. E5/2.",
    "m32a": "A5/4",
})
VN2.update({
    "m24b": "[f] A4/2. B4/2.",
    "m25": "C#5/4> A4/2. B4/2.",
    "m26": "C#5/2.> B4/2. A4/2. G#4/2.",
    "m27": "F#4/2. G#4/2. A4/2. B4/2.",
    "m28": "(G#4/2 E4/2.) A4/2. B4/2.",
    "m29": "C#5/4> A4/2. B4/2.",
    "m30": "C#5/2.> B4/2. A4/2. G#4/2.",
    "m31": "F#4/2. B4/2. G#4/2. E4/2.",
    "m32a": "A4/4",
})
VA.update({
    "m24b": "r/4",
    "m25": "{arco} [f] A3+E4/2.> A3+E4/2. A3+E4/2. A3+E4/2.",
    "m26": "A3+E4/2.> A3+E4/2. A3+E4/2. A3+E4/2.",
    "m27": "A3+F#4/2.> A3+F#4/2. A3+F#4/2.> A3+F#4/2.",
    "m28": "B3+E4/2.> B3+E4/2. B3+E4/2. B3+E4/2.",
    "m29": "A3+E4/2.> A3+E4/2. A3+E4/2. A3+E4/2.",
    "m30": "A3+E4/2.> A3+E4/2. A3+E4/2. A3+E4/2.",
    "m31": "A3+F#4/2.> A3+F#4/2. B3+E4/2.> B3+E4/2.",
    "m32a": "A3+E4/4",
})
VC.update({
    "m24b": "r/4",
    "m25": "{arco} [f] " + DRUM_A,
    "m26": DRUM_A,
    "m27": DRUM_D + " " + DRUM_D_,
    "m28": DRUM_E,
    "m29": DRUM_A, "m30": DRUM_A,
    "m31": DRUM_D + " " + DRUM_E_,
    "m32a": "A2/4",
})
# second time: the lower strings pizzicato, a Janissary band's drums
VA2.update({"m24b": "{pizz.} r/4"})
VC2.update({"m24b": "{pizz.} r/4"})
for lab in ("m25", "m26", "m27", "m28", "m29", "m30", "m31", "m32a"):
    VA2[lab] = pizz(VA[lab].replace("{arco} ", ""))
    VC2[lab] = pizz(VC[lab].replace("{arco} ", ""))

# ---- Episodio (F# minor / A major): m32b-40a, m40b-56a ---------------------
VN1.update({
    "m32b": "[p] (C#6/1 D6/1 C#6/1 B5/1",
    "m33": "A5/1 B5/1 A5/1 G#5/1 F#5/1 A5/1 G#5/1 F#5/1",
    "m34": "E#5/1 F#5/1 G#5/1 E#5/1 C#5/1 D#5/1 E#5/1 C#5/1)",
    "m35": "[<] (F#5/1 E#5/1 F#5/1 G#5/1 A5/1 G#5/1 A5/1 B5/1 [<|]",
    "m36": "[>] C#6/1 B#5/1 C#6/1 B#5/1 C#6/1 D6/1 C#6/1 B5/1) [>|]",
    "m37": "(A5/1 B5/1 A5/1 G#5/1 F#5/1 A5/1 G#5/1 F#5/1",
    "m38": "E5/1 F#5/1 G#5/1 E5/1 C#5/1 D#5/1 E5/1 C#5/1)",
    "m39": "(D#5/1 E5/1 F#5/1 D#5/1 B#4/1 C#5/1 D#5/1 B#4/1",
    "m40a": "C#5/4)",
    # forte: one bow per beat
    "m40b": "{arco} [f] (E5/1 D5/1 C#5/1 B4/1)",
    "m41": "(A4/1 B4/1 C#5/1 D5/1) (E5/1 F#5/1 G#5/1 A5/1)",
    "m42": "(A5/1> G#5/1 F#5/1 E5/1) (E5/1 D5/1 C#5/1 B4/1)",
    "m43": "(A4/1 B4/1 C#5/1 D5/1) (E5/1 F#5/1 G#5/1 A5/1)",
    "m44": "A#5/2> B5/2. (E5/1 D5/1 C#5/1 B4/1)",
    "m45": "(A4/1 B4/1 C#5/1 D5/1) (E5/1 F#5/1 G#5/1 A5/1)",
    "m46": "(A5/1> G#5/1 F#5/1 E5/1) (E5/1 D5/1 C#5/1 B4/1)",
    "m47": "(C#5/1 E5/1 A4/1 C#5/1) (B4/1 D5/1 G#4/1 B4/1)",
    "m48": "A4/4_ [p] (C#6/1 D6/1 C#6/1 B5/1",
    "m49": "A5/1 B5/1 A5/1 G#5/1 F#5/1 A5/1 G#5/1 F#5/1",
    "m50": "E#5/1 F#5/1 G#5/1 E#5/1 C#5/1 D#5/1 E#5/1 C#5/1)",
    "m51": "[<] (F#5/1 E#5/1 F#5/1 G#5/1 A5/1 G#5/1 A5/1 B5/1 [<|]",
    "m52": "C#6/1 B#5/1 C#6/1 B#5/1 [cresc.] C#6/1 B#5/1 C#6/1 A#5/1)",
    "m53": "[>] (D6/1 C#6/1 D6/1 C#6/1 D6/1 C#6/1 D6/1 C#6/1)",
    "m54": "(D6/1 C#6/1 B5/1 A5/1 G#5/1 A5/1 B5/1 G#5/1 [>|]",
    "m55": "[p] A5/1 B5/1 C#6/1 F#5/1 E#5/1 F#5/1 G#5/1 E#5/1",
    "m56a": "F#5/4_)",
})
VN2.update({
    "m32b": "r/4",
    "m33": "[p] r/2 C#4/2. C#4/2. C#4/2.",
    "m34": "r/2 C#4/2. C#4/2. C#4/2.",
    "m35": "r/2 [<] C#4/2. C#4/2. C#4/2. [<|]",
    "m36": "r/2 [>] C#4/2. C#4/2. C#4/2. [>|]",
    "m37": "r/2 C#4/2. C#4/2. C#4/2.",
    "m38": "r/2 E4/2. E4/2. E4/2.",
    "m39": "r/2 F#4/2. F#4/2. F#4/2.",
    "m40a": "E4/4_",
    "m40b": "r/4",
    "m41": "r/2 {arco} [f] E4/2. E4/2. E4/2.",
    "m42": "r/2 E4/2. r/2 E4/2.",
    "m43": "r/2 E4/2. E4/2. E4/2.",
    "m44": "r/2 D4/2. D4/2. D4/2.",
    "m45": "r/2 E4/2. E4/2. E4/2.",
    "m46": "r/2 E4/2. r/2 E4/2.",
    "m47": "E4/2. F#4/2. F#4/2. E4/2.",
    "m48": "E4/4_ r/4",
    "m49": "[p] r/2 C#4/2. C#4/2. C#4/2.",
    "m50": "r/2 C#4/2. C#4/2. C#4/2.",
    "m51": "r/2 [<] C#4/2. C#4/2. C#4/2. [<|]",
    "m52": "r/2 [cresc.] C#4/2. C#4/2. C#4/2.",
    "m53": "r/2 [>] B3/2. B3/2. B3/2.",
    "m54": "r/2 B3/2. B3/2. B3/2. [>|]",
    "m55": "[p] r/2 A3/2. r/2 B3/2.",
    # #9: B3 (the C#7's seventh) resolves down to A3; the viola's G#3 to F#3
    "m56a": "A3/4_",
})
VA.update({
    "m32b": "r/4",
    "m33": "r/2 {arco} [p] A3/2. A3/2. A3/2.",
    "m34": "r/2 B3/2. B3/2. B3/2.",
    "m35": "r/2 [<] A3/2. A3/2. A3/2. [<|]",
    "m36": "r/2 [>] G#3/2. G#3/2. G#3/2. [>|]",
    "m37": "r/2 A3/2. A3/2. A3/2.",
    "m38": "r/2 C#4/2. C#4/2. C#4/2.",
    "m39": "r/2 D#4/2. D#4/2. D#4/2.",
    "m40a": "C#4/4_",
    "m40b": "r/4",
    "m41": "r/2 [f] C#4/2. C#4/2. C#4/2.",
    "m42": "r/2 D4/2. r/2 D4/2.",
    "m43": "r/2 C#4/2. C#4/2. C#4/2.",
    "m44": "r/2 G#3/2. G#3/2. G#3/2.",
    "m45": "r/2 C#4/2. C#4/2. C#4/2.",
    "m46": "r/2 D4/2. r/2 D4/2.",
    "m47": "C#4/2. A3/2. A3/2. G#3/2.",
    "m48": "C#4/4_ r/4",
    "m49": "r/2 [p] A3/2. A3/2. A3/2.",
    "m50": "r/2 B3/2. B3/2. B3/2.",
    "m51": "r/2 [<] A3/2. A3/2. A3/2. [<|]",
    "m52": "r/2 [cresc.] G#3/2. G3/2. F#3/2.",
    "m53": "r/2 [>] F#3/2. F#3/2. F#3/2.",
    "m54": "r/2 G#3/2. G#3/2. G#3/2. [>|]",
    "m55": "r/2 [p] F#3/2. r/2 G#3/2.",
    "m56a": "F#3/4_",
})
VC.update({
    "m32b": "r/4",
    "m33": "{arco} [p] F#2/2 r/2 r/4",
    "m34": "G#2/2 r/2 r/4",
    "m35": "[<] F#2/2 r/2 r/4 [<|]",
    "m36": "[>] E#2/2 r/2 r/4 [>|]",
    "m37": "F#2/2 r/2 r/4",
    "m38": "G#2/2 r/2 r/4",
    "m39": "G#2/2 r/2 r/4",
    "m40a": "C#3/4_",
    "m40b": "r/4",
    # forte: a drum bass (Trommelbass) under the scales
    "m41": "{arco} [f] " + rep("A2/2.", 4),
    "m42": "B2/2. B2/2. G#2/2. G#2/2.",
    "m43": rep("A2/2.", 4),
    "m44": rep("E2/2.", 4),
    "m45": rep("A2/2.", 4),
    "m46": "B2/2. B2/2. G#2/2. G#2/2.",
    "m47": "A2/2. F#2/2. D2/2. E2/2.",
    "m48": "A2/2. A3/2. r/4",
    "m49": "[p] F#2/2 r/2 r/4",
    "m50": "G#2/2 r/2 r/4",
    "m51": "[<] F#2/2 r/2 r/4 [<|]",
    "m52": "[cresc.] C#3/2 r/2 r/4",
    "m53": "[>] B2/2 r/2 r/4",
    "m54": "B2/2 r/2 r/4 [>|]",
    "m55": "[p] C#3/2. r/2 C#3/2. r/2",
    "m56a": "F#2/4_",
})


def down8(s):
    """A line an octave lower (the viola's second-time melody)."""
    return re.sub(r"([A-G](?:#|b)?)(\d)",
                  lambda k: k.group(1) + str(int(k.group(2)) - 1), s)


# second time, F# minor: the viola sings the 16ths an octave lower, the
# violins and cello accompany pizzicato
for lab in ("m32b", "m33", "m34", "m35", "m36", "m37", "m38", "m39",
            "m40a"):
    VA2[lab] = down8(VN1[lab])
VA2["m32b"] = "[p] {dolce} (C#5/1 D5/1 C#5/1 B4/1"
VN12.update({
    "m32b": "{pizz.} r/4",
    "m33": "r/2 [p] A3/2 A3/2 A3/2", "m34": "r/2 B3/2 B3/2 B3/2",
    "m35": "r/2 [<] A3/2 A3/2 A3/2 [<|]", "m36": "r/2 [>] G#3/2 G#3/2 G#3/2 [>|]",
    # m38-39: below the viola's tune, which dips to B#3 here
    "m37": "r/2 A3/2 A3/2 A3/2", "m38": "r/2 G#3/2 G#3/2 G#3/2",
    "m39": "r/2 G#3/2 G#3/2 G#3/2", "m40a": "C#4/4",
})
VN22.update({lab: pizz(VN2[lab]) for lab in
             ("m33", "m34", "m35", "m36", "m37", "m38", "m39", "m40a")})
VN22["m32b"] = "{pizz.} r/4"
VN22.update({"m38": "r/2 C#4/2 C#4/2 C#4/2", "m39": "r/2 B#3/2 r/2 B#3/2"})
VC2.update({lab: pizz(VC[lab].replace("{arco} ", "")) for lab in
            ("m33", "m34", "m35", "m36", "m37", "m38", "m39", "m40a")})
VC2["m32b"] = "{pizz.} r/4"
# second time, A major forte: the violins in unison over the viola's double
# stops (Violin II an octave lower would run through them)
VN22.update({lab: VN1[lab] for lab in
             ("m41", "m42", "m43", "m44", "m45", "m46", "m47")})
VN22["m40b"] = "[f] (E5/1 D5/1 C#5/1 B4/1)"
VN12["m40b"] = "[f] (E5/1 D5/1 C#5/1 B4/1)"
VA2.update({
    "m40b": "r/4",
    "m41": "r/2 [f] C#4+E4/2. C#4+E4/2. C#4+E4/2.",
    "m42": "r/2 D4+E4/2. r/2 D4+E4/2.",
    "m43": "r/2 C#4+E4/2. C#4+E4/2. C#4+E4/2.",
    "m44": "r/2 G#3+D4/2. G#3+D4/2. G#3+D4/2.",
    "m45": "r/2 C#4+E4/2. C#4+E4/2. C#4+E4/2.",
    "m46": "r/2 D4+E4/2. r/2 D4+E4/2.",
    "m47": "C#4+E4/2. A3+F#4/2. A3+F#4/2. G#3+E4/2.",
    # beat 1 closes the forte, beat 2 takes up the 16ths again
    "m48": "C#4+E4/4_ [p] (C#5/1 D5/1 C#5/1 B4/1",
})
for lab in ("m49", "m50", "m51", "m52", "m53", "m54", "m55", "m56a"):
    VA2[lab] = down8(VN1[lab])
VA2["m56a"] = "A3+F#4/4_)"      # the F# minor third, as the first time
# ... and the others pizzicato; from m52 the cello takes the lower chord
# notes too (the violins cannot reach F#3)
VN12.update({
    "m48": "A4/4_ {pizz.} r/4",
    "m49": "r/2 [p] A3/2 A3/2 A3/2", "m50": "r/2 B3/2 B3/2 B3/2",
    "m51": "r/2 [<] A3/2 A3/2 A3/2 [<|]",
    "m52": "r/8", "m53": "r/8", "m54": "r/8", "m55": "r/8", "m56a": "r/4",
})
VN22.update({
    "m48": "A4/4_ {pizz.} r/4",
    "m49": "r/2 [p] C#4/2 C#4/2 C#4/2", "m50": "r/2 C#4/2 C#4/2 C#4/2",
    "m51": "r/2 [<] C#4/2 C#4/2 C#4/2 [<|]",
    "m52": "r/2 [cresc.] C#4/2 C#4/2 C#4/2",
    "m53": "r/2 [>] B3/2 B3/2 B3/2", "m54": "r/2 B3/2 B3/2 B3/2 [>|]",
    "m55": "r/2 [p] A3/2 r/2 B3/2", "m56a": "r/4",
})
VC2.update({
    "m40b": "r/4",
    "m41": VC["m41"].replace("{arco} ", ""),
    "m48": "A2/2. A3/2. {pizz.} r/4",
    "m49": "[p] F#2/2 r/2 r/4", "m50": "G#2/2 r/2 r/4",
    "m51": "[<] F#2/2 r/2 r/4 [<|]",
    "m52": "[cresc.] C#3/2 G#2/2 G2/2 F#2/2",
    "m53": "[>] B2/2 F#3/2 F#3/2 F#3/2", "m54": "B2/2 G#3/2 G#3/2 G#3/2 [>|]",
    "m55": "[p] C#3/2 F#3/2 C#3/2 G#3/2", "m56a": "F#2/4",
})

# ---- the second Alla turca (m56b-64a) and the Tema's reprise (m64b-88a)
# are aliases; only the bows' changes differ
VN1["m56b"] = "{arco} [f] A5/2. B5/2."
VN2["m56b"] = "{arco} [f] A4/2. B4/2."
VN12["m56b"] = "[f] A5/2. B5/2."
VN22["m56b"] = "[f] A4/2. B4/2."
VA["m57"] = "[f] A3+E4/2.> A3+E4/2. A3+E4/2. A3+E4/2."
VN1["m64a"] = "A5/4_"
VN2["m64a"] = "A4/4_"
VA["m64a"] = "A3+E4/4_"
VC["m64a"] = "A2/4_"
VA["m65"] = "r/2 {arco} [p] C4/2. C4/2. C4/2."
# where the edition marks the reprise differently from the first Tema
VN1.update({
    "m69": "(g:G5 g:A5 [sfz] B5/2) A5/2. G5/2. A5/2.",
    "m71": "(g:G5 g:A5 [sfz] B5/2.) A5/2. G5/2. F#5/2.",
    "m72a": "E5/4",
    "m76": "D5/4> C5/2. D5/2.",
    "m80": "B4/4> [p] (B4/1 A4/1 G#4/1 A4/1",
    "m85": "C6/2.> B5/2. A5/2. [>] G#5/2.",
    "m86": "A5/2. E5/2. [>|] F5/2. D5/2.",
    "m87": "[p] C5/4 (B4/3tr A4/0.5 B4/0.5",
    "m88a": "A4/4)",
})
VN2.update({
    "m69": "r/2 F#5/2. E5/2. F#5/2.",
    "m71": "r/2 F#5/2. E5/2. D#5/2.",
    "m76": "B4/4> A4/2. B4/2.",
    "m80": "G#4/4> r/4",
    "m85": "r/2 E4/2. r/2 [>] B3/2.",
    "m86": "r/2 A3/2. [>|] r/2 B3/2.",
})
VN2.update({"m87": "[p] E4/8", "m88a": "E4/4"})
VA["m88a"] = "A3/4"
VC.update({"m80": "E3/4 r/4", "m88a": "A2/4"})
VC2["m80"] = "E3/4 {pizz.} r/4"
VA.update({"m85": "r/2 A3/2. r/2 [>] F3/2.",
           "m86": "r/2 E3/2. [>|] r/2 F3/2."})
VC.update({"m72a": "E3/4",
           "m85": "E3/2. r/2 [>] D3/2. r/2",
           "m86": "C3/2. r/2 [>|] D3/2. r/2"})
VA2.update({"m85": "r/2 A3/2 r/2 [>] F3/2",
            "m86": "r/2 E3/2 [>|] r/2 F3/2"})
VC2.update({"m85": "E2/2 r/2 [>] D2/2 r/2",
            "m86": "C2/2 r/2 [>|] D2/2 r/2"})
VC["m65"] = "{arco} [p] A3/2 r/2 r/4"
# ---- Alla turca in 16ths (A major, forte): m88b-96 -------------------------
# Violin I plays the piano's broken octaves (slurred in pairs across two
# strings), Violin II the tune in plain eighths; the second time Violin II
# moves up to double Violin I's upper notes.
BROKEN = {
    "m88b": "[f] (A4/1 A5/1) (B4/1 B5/1)",
    "m89": "(C#5/1> C#6/1) r/2 (A4/1 A5/1) (B4/1 B5/1)",
    "m90": "(C#5/1 C#6/1) (B4/1 B5/1) (A4/1 A5/1) (G#4/1 G#5/1)",
    "m91": "(F#4/1 F#5/1) (G#4/1 G#5/1) (A4/1 A5/1) (B4/1 B5/1)",
    "m92": "(G#4/1 G#5/1) (E4/1 E5/1) (A4/1 A5/1) (B4/1 B5/1)",
    "m93": "(C#5/1> C#6/1) r/2 (A4/1 A5/1) (B4/1 B5/1)",
    "m94": "(C#5/1> C#6/1) (B4/1 B5/1) (A4/1 A5/1) (G#4/1 G#5/1)",
    "m95": "(F#4/1> F#5/1) (B4/1 B5/1) (G#4/1> G#5/1) (E4/1 E5/1)",
    "m96a": "A5/4",
    "m96b": "A5/4 C#6/3 C#6/1",
}
PLAIN = {
    "m88b": "[f] A4/2. B4/2.",
    "m89": "C#5/2.> r/2 A4/2. B4/2.",
    "m90": "C#5/2. B4/2. A4/2. G#4/2.",
    "m91": "F#4/2. G#4/2. A4/2. B4/2.",
    "m92": "G#4/2. E4/2. A4/2. B4/2.",
    "m93": "C#5/2.> r/2 A4/2. B4/2.",
    "m94": "C#5/2.> B4/2. A4/2. G#4/2.",
    "m95": "F#4/2.> B4/2. G#4/2.> E4/2.",
    "m96a": "A4/4",
    "m96b": "A4/4 C#5/4",
}
VN1.update(BROKEN)
VN2.update(PLAIN)
VN22.update({lab: re.sub(r"([A-G]#?)(\d)",
                          lambda k: k.group(1) + str(int(k.group(2)) + 1), v)
             if lab != "m96b" else v for lab, v in PLAIN.items()})
DRUM_VA_A = "A3+E4/2.> A3+E4/2. A3+E4/2. A3+E4/2."
DRUM_VA_E = "B3+E4/2.> B3+E4/2. B3+E4/2. B3+E4/2."
VA.update({
    "m88b": "r/4",
    "m89": "{arco} [f] " + DRUM_VA_A,
    "m90": DRUM_VA_A,
    "m91": "A3+F#4/2.> A3+F#4/2. A3+F#4/2.> A3+F#4/2.",
    "m92": DRUM_VA_E,
    "m93": DRUM_VA_A, "m94": DRUM_VA_A,
    "m95": "A3+F#4/2.> A3+F#4/2. B3+E4/2.> B3+E4/2.",
    "m96a": "A3+E4/4",
    "m96b": DRUM_VA_A,
})
VC.update({
    "m88b": "r/4",
    "m89": "{arco} [f] " + DRUM_A,
    "m90": DRUM_A,
    "m91": DRUM_D + " " + DRUM_D_,
    "m92": DRUM_E,
    "m93": DRUM_A, "m94": DRUM_A,
    "m95": DRUM_D + " " + DRUM_E_,
    "m96a": "A2/4",
    "m96b": DRUM_A,
})
VA2["m89"] = "[f] " + DRUM_VA_A
VC2["m89"] = "[f] " + DRUM_A
VA2["m88b"] = VC2["m88b"] = "r/4"

# ---- Coda (A major): m97-127 -------------------------------------------------
# The Janissary band: Violin I the tune, Violin II the piano's chords as
# double / triple stops, the viola's double stops and the cello's rolled
# arpeggios keep the drum going; bars 109-115 the viola takes the left
# hand's Alberti 16ths over a cello pedal.
CHORD_A = "E4+C#5+A5/4arp r/4"
VN1.update({
    "m97": "[f] C#6/8>", "m98": "C#6/8>",
    "m99": "(D6/1 C#6/1.) B5/1. C#6/1. (D6/1 C#6/1.) B5/1. C#6/1.",
    "m100": "D6/8>",
    "m101": rep("(gs:D6 C#6/2.)", 4),
    "m102": "(B5/6 E6/2)",
    "m103": "[f] C#6/8>", "m104": "C#6/8>",
    "m105": "(D6/1 C#6/1.) B5/1. C#6/1. (D6/1 C#6/1.) B5/1. C#6/1.",
    "m106": "D6/8>",
    "m107": "(gs:D6 C#6/8)",
    "m108": rep("(gs:C#6 B5/2.)", 4),
    "m109": "A5/4 g:E5 g:A5 C#6/3 C#6/1",
    "m110": "(g:E5 g:A5 C#6/8>)",
    "m111": "(g:E5 g:A5 C#6/8>)",
    "m112": "(D6/1 C#6/1.) B5/1. C#6/1. (D6/1 C#6/1.) B5/1. C#6/1.",
    "m113": "D6/8>",
    "m114": rep("(gs:D6 C#6/2.)", 4),
    "m115": "(B5/6 E6/2.)",
    "m116": "[f] C#6/8>", "m117": "C#6/8>",
    "m118": "(D6/1 C#6/1.) B5/1. C#6/1. (D6/1 C#6/1.) B5/1. C#6/1.",
    "m119": "D6/8>",
    "m120": "(gs:D6 C#6/8)",
    "m121": rep("(gs:C#6 B5/2.)", 4),
    "m122": "[cresc.] A5/6_ C#6/2.",
    "m123": "A5/6_ E6/2.",
    "m124": "A5/6 C#6/2.",
    "m125": "A5/2. C#6/2. A5/2. E6/2.",
    "m126": "A5/4. [ff] A3+E4+C#5+A5/4.arp>",
    "m127": "A3+E4+C#5+A5/4.arp> r/4",
})
VN2.update({
    "m97": "[f] " + CHORD_A, "m98": CHORD_A,
    "m99": rep("E5+A5/2.", 4),
    "m100": "D4+A4+F#5/4arp D5+F#5/4",
    "m101": rep("E5+A5/2.", 4),
    "m102": "E5+G#5/8",
    "m103": "[f] " + CHORD_A, "m104": CHORD_A,
    "m105": rep("E5+A5/2.", 4),
    "m106": "D4+A4+F#5/4arp D5+F#5/4",
    "m107": "E5+A5/8",
    "m108": rep("E5+G#5/2.", 4),
    "m109": "E5/8", "m110": "E5/8", "m111": "E5/8", "m112": "E5/8",
    "m113": "F#5/8", "m114": "E5/8", "m115": "E5/4 D5/4",
    "m116": "[f] " + CHORD_A, "m117": CHORD_A,
    "m118": rep("E5+A5/2.", 4),
    "m119": "D4+A4+F#5/4arp D5+F#5/4",
    "m120": "E5+A5/8",
    "m121": rep("E5+G#5/2.", 4),
    "m122": "[cresc.] C#5+E5/6_ C#5/2.",
    "m123": "A4+E5/6_ E5/2.",
    "m124": "A4+E5/6 C#5/2.",
    "m125": "A4/2. C#5/2. A4/2. E5/2.",
    "m126": "A4/4. [ff] E4+C#5+A5/4.arp>",
    "m127": "E4+C#5+A5/4.arp> r/4",
})
VA.update({
    "m97": "[f] " + DRUM_VA_A, "m98": DRUM_VA_A, "m99": DRUM_VA_A,
    "m100": "A3+F#4/2.> A3+F#4/2. A3+F#4/2. A3+F#4/2.",
    "m101": DRUM_VA_A, "m102": DRUM_VA_E,
    "m103": "[f] " + DRUM_VA_A, "m104": DRUM_VA_A, "m105": DRUM_VA_A,
    "m106": "A3+F#4/2.> A3+F#4/2. A3+F#4/2. A3+F#4/2.",
    "m107": DRUM_VA_A,
    # E3+G#3, not B3+E4: E4-A3 over the cello's E3-A2 would be octaves;
    # the G#3 leads into the Alberti's A3
    "m108": "E3+G#3/2.> E3+G#3/2. E3+G#3/2. E3+G#3/2.",
    "m109": "(A3/1 E4/1 C#4/1 E4/1 A3/1 E4/1 C#4/1 E4/1)",
    "m110": "(A3/1 E4/1 C#4/1 E4/1 A3/1 E4/1 C#4/1 E4/1)",
    "m111": "(A3/1 E4/1 C#4/1 E4/1 A3/1 E4/1 C#4/1 E4/1)",
    "m112": "(A3/1 E4/1 C#4/1 E4/1 A3/1 E4/1 C#4/1 E4/1)",
    "m113": "(A3/1 F#4/1 D4/1 F#4/1 A3/1 F#4/1 D4/1 F#4/1)",
    "m114": "(A3/1 E4/1 C#4/1 E4/1 A3/1 E4/1 C#4/1 E4/1)",
    "m115": "(E3/1 E4/1 G#3/1 E4/1 E3/1 E4/1 G#3/1 E4/1)",
    "m116": "[f] " + DRUM_VA_A, "m117": DRUM_VA_A, "m118": DRUM_VA_A,
    "m119": "A3+F#4/2.> A3+F#4/2. A3+F#4/2. A3+F#4/2.",
    "m120": DRUM_VA_A,
    # G#3+E4, not B3+E4: B3-A3 would double the tune's B5-A5 in octaves
    "m121": "G#3+E4/2.> G#3+E4/2. G#3+E4/2. G#3+E4/2.",
    "m122": "[cresc.] " + DRUM_VA_A, "m123": DRUM_VA_A, "m124": DRUM_VA_A,
    "m125": "A3+E4/2.> A3+E4/2. A3+E4/2.> A3+E4/2.",
    "m126": "A3/4. [ff] A3+E4+C#5/4arp>~",
    "m127": "A3+E4+C#5/4 r/4",
})
VC.update({
    "m97": "[f] " + DRUM_A, "m98": DRUM_A, "m99": DRUM_A,
    "m100": "D2+A2+D3/2>arp D3/2. D3/2. D3/2.",
    "m101": DRUM_A, "m102": DRUM_E,
    "m103": "[f] " + DRUM_A, "m104": DRUM_A, "m105": DRUM_A,
    "m106": "D2+A2+D3/2>arp D3/2. D3/2. D3/2.",
    "m107": DRUM_A, "m108": DRUM_E,
    "m109": "A2/2. r/2 A2/2. r/2", "m110": "A2/2. r/2 A2/2. r/2",
    "m111": "A2/2. r/2 A2/2. r/2", "m112": "A2/2. r/2 A2/2. r/2",
    "m113": "A2/2. r/2 A2/2. r/2", "m114": "A2/2. r/2 A2/2. r/2",
    "m115": "E2/2. r/2 E2/2. r/2",
    "m116": "[f] " + DRUM_A, "m117": DRUM_A, "m118": DRUM_A,
    "m119": "D2+A2+D3/2>arp D3/2. D3/2. D3/2.",
    "m120": DRUM_A, "m121": DRUM_E,
    "m122": "[cresc.] " + DRUM_A, "m123": DRUM_A, "m124": DRUM_A,
    "m125": "A2+E3+A3/2>arp A3/2. A2+E3+A3/2>arp A3/2.",
    "m126": "A2/4. [ff] A2+E3+A3/4arp>~",
    "m127": "A2+E3+A3/4 r/4",
})

PARTS = [
    dict(id="vn1", name="Violin I", abbr="Vln. I", zh="第一小提琴",
         data=VN1, data2=VN12, inst=instrument.Violin, clef=clef.TrebleClef,
         program=40),
    dict(id="vn2", name="Violin II", abbr="Vln. II", zh="第二小提琴",
         data=VN2, data2=VN22, inst=instrument.Violin, clef=clef.TrebleClef,
         program=40),
    dict(id="va", name="Viola", abbr="Vla.", zh="中提琴",
         data=VA, data2=VA2, inst=instrument.Viola, clef=clef.AltoClef,
         program=41),
    dict(id="vc", name="Violoncello", abbr="Vc.", zh="大提琴",
         data=VC, data2=VC2, inst=instrument.Violoncello,
         clef=clef.BassClef, program=42),
]

KEYS = {0: "a", bar_of("m25"): "A", bar_of("m65"): "a", bar_of("m89"): "A"}
DOUBLE_BARS = {bar_of("m33"), bar_of("m57"), bar_of("m97")}
TEMPI = [(0, 0, BPM)]
SECTIONS = [(1, None, "Tema 主题"),
            (bar_of("m9"), "A", "Tema II 主题第二段"),
            (bar_of("m25"), "B", "Alla turca 土耳其进行曲"),
            (bar_of("m33"), "C", "Episodio 插部"),
            (bar_of("m41"), "D", "Episodio II 插部第二段"),
            (bar_of("m57"), "E", "Alla turca 土耳其进行曲"),
            (bar_of("m65"), "F", "Tema 主题再现"),
            (bar_of("m73"), "G", "Tema II 主题第二段"),
            (bar_of("m89"), "H", "Alla turca 土耳其进行曲"),
            (bar_of("m97"), "I", "Coda 尾声")]


def _systems():
    """Phrase-aligned systems (bar numbers where a system starts):
    * the Tema, the marches and the reprise: Mozart's 8-bar phrases (the
      first system, with the full instrument names, holds half of one);
    * the episode and the last march, all 16ths: half phrases of 4 bars;
    * the coda: its own 6-bar phrases (m97-102, 103-108, 109-115 split
      4 + 3, 116-121, 122-127).
    39 systems, 3 per page (the title page included) = 13 pages."""
    b = bar_of
    starts = [0, 5, 9, 17, 25, 33, 41, b("m25"), b("m25", 2)]
    starts += list(range(b("m33"), b("m57"), 4))
    starts += [b("m57"), b("m57", 2)]
    starts += list(range(b("m65"), b("m88a", 2), 8))
    starts += [b("m88a", 2), b("m89") + 4, b("m89", 2), b("m89", 2) + 4]
    starts += [b(m) for m in ("m97", "m103", "m109", "m113", "m116",
                              "m122")]
    return starts


SYSTEM_STARTS = _systems()
SYSTEM_BREAKS = tuple(SYSTEM_STARTS[1:])
PAGE_BREAKS = tuple(SYSTEM_STARTS[3::3])
# Parts (MS4 lays them out itself): turn the page in a rest, and start a
# system at a rehearsal bar whose title would otherwise run off the page
# (bar that opens a new page; the turn from page 2 to 3 lands in a rest,
# and Violin II's pages 3 / 4 face each other, split at H)
PART_PAGE_BREAKS = {"vn1": (bar_of("m56b"),),   # turn in the m52-55 rest
                    "vn2": (137, bar_of("m89")),  # turn in the empty bar 136
                    "va": (153,),                 # turn in the 144-152 rest
                    "vc": (141,)}                 # after bar 140's pizz.
PART_BREAKS = {"vn2": (bar_of("m25"),), "va": (bar_of("m57"),)}
BELOW_WORDS = {"cresc.", "dim.", "decresc.", "cresc", "cresco", "dolce"}
# Deliberate departures from the piano, by Urtext bar (aliases included):
ALLOW = {
    # Violin II's sixths / thirds under the running 16ths (passing notes)
    *{("foreign", f"m{i}", "vn2") for i in (9, 11, 13, 15)},
    # open fifths added at the half cadences
    ("foreign", "m24a", "vn2"), ("foreign", "m32a", "va"),
    ("foreign", "m96a", "va"),
    ("foreign", "m48", "vn2"), ("foreign", "m48", "va"),
    # the coda: a seventh (D5) that leads Violin II to the next C#5
    ("foreign", "m115", "vn2"),
    # misprints in the edition, corrected (see README): m25's third grace
    # note is printed D3 (E3 in m26, m29, m30 and the Urtext); m87's left
    # hand lacks the sharp on G3 (G#3 in m23 and the Urtext)
    ("foreign", "m25", "va"), ("foreign", "m25", "vc"),
    ("foreign", "m87", "va"), ("clash", "m87"),
    # doublings: the tune in octaves / broken octaves, the final chords
    *{("p8", f"m{i}") for i in range(89, 97)}, ("p8", "m88b"),
    ("p8", "m96a"), ("p8", "m96b"), ("p8", "m126"), ("p8", "m127"),
}

META = dict(
    title="土耳其进行曲", title_latin="Rondo alla Turca",
    subtitle="全曲 · 弦乐四重奏",
    subtitle_en="Piano Sonata K. 331, III — arranged for String Quartet",
    composer="W. A. 莫扎特 Mozart", lyricist="", artist="",
    original="A大调钢琴奏鸣曲 K.331 第三乐章",
    instrumentation=[("Violin I", "第一小提琴"), ("Violin II", "第二小提琴"),
                     ("Viola", "中提琴"), ("Violoncello", "大提琴")],
    key="A Minor / A Major · a小调 / A大调", tempo="♩ = 120",
    duration="ca. 3′44″", year="2026", tempo_text="Allegretto",
    )


def _mscx_hook(x):
    """MS4 touch-ups on the imported score (MS4 ignores MusicXML offsets):
    * the bar-1 title "Tema 主题" goes right of the tempo mark, which MS4
      would otherwise stack above it, into the title block's 原曲 line;
    * rehearsal letters and their titles 7 sp up (not 5), so "Episodio"
      clears bar 65's number box;
    * A, F and G start an A-minor system (no key signature): start their
      titles right of the letter box, not under it;
    * H falls mid-system after the key change: pull its title back to the
      gap the other letters have."""
    x, n = re.subn(r'(<text><b>Tema <font face="Noto Serif CJK SC"/>主题'
                   r'<font face="Edwin"/></b></text>)',
                   r'\1\n            <offset x="5" y="0"/>', x, count=1)
    assert n == 1, n
    x, n = re.subn(r'<offset x="0" y="-5"/>', '<offset x="0" y="-7"/>', x)
    assert n == 18, n          # 9 rehearsal letters + 9 section titles
    x, n = re.subn(r'(<text><b>Tema (?:II )?<font face="Noto Serif CJK SC"/>'
                   r'(?:主题第二段|主题再现)<font face="Edwin"/></b></text>\s*)'
                   r'<offset x="0" y="-7"/>', r'\1<offset x="2.6" y="-7"/>', x)
    assert n == 3, n           # A, F, G
    ms = list(re.finditer(r'(<text><b>Alla turca [^\n]*</b></text>\s*)'
                          r'<offset x="0" (y="[-\d.]+")/>', x))
    assert len(ms) == 3, len(ms)          # B, E, H
    h = ms[2]
    return (x[:h.start()] + h.group(1)
            + f'<offset x="-3.4" {h.group(2)}/>' + x[h.end():])


META["mscx_hook"] = _mscx_hook

if __name__ == "__main__":
    main()
