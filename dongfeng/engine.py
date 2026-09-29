#!/usr/bin/env python3
"""Score engine for 冬风 (Chopin Op. 25 No. 11) — shared by build.py.

build.py holds the music (Chopin's text and the quartet parts); this module
turns it into MusicXML, MIDI, checks and the Hollywood PDF.  It follows the
house pipeline of chatang/build.py, widened for a piano etude:

  * one bar = 48 ticks (a tick is a twelfth of a quarter), so sextuplet
    16ths (2), 16ths (3), triplet eighths (4), eighths (6), dotted eighths
    (9), quarters (12), halves (24) and wholes (48) share one grid;
  * cut time (2/2) throughout, beamed by the quarter like Chopin's text;
  * sextuplets are written as 6:4 16ths with the "6" shown only where a
    part starts a run of them.

Token syntax (one string per bar and part, durations in ticks):
  F6/2        a sextuplet 16th        E4/9  a dotted eighth
  E4/3        a 16th                  G3/4  a triplet eighth
  A3+E4/12    double stop (quarter)   r/24  half rest
  flags after the duration, in any order:
    >  accent     ^  marcato (strong accent)     .  staccato
    '  staccatissimo    @  fermata    ~  tie into the next note
  (F6/2 ... A4/2)   slur start / slur end
"""
import os
import re
import xml.etree.ElementTree as ET
from fractions import Fraction

import mido
from music21 import (articulations, bar, clef, duration, dynamics,
                     expressions, instrument, key, layout, metadata, meter,
                     note, chord, spanner, stream, tempo, tie)

BAR = 48          # ticks per bar
BEAT = 12         # ticks per quarter
TPQ = 480
TICK = TPQ // BEAT  # MIDI ticks per engine tick

# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------
_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ACC = {"": 0, "#": 1, "##": 2, "b": -1, "bb": -2}
PITCH = r"[A-G](?:##|bb|#|b)?-?\d"


def midi_of(p):
    m = re.fullmatch(r"([A-G])(##|bb|#|b)?(-?\d)", p)
    if not m:
        raise ValueError(p)
    s, acc, octv = m.groups()
    return 12 * (int(octv) + 1) + _STEP[s] + _ACC[acc or ""]


def m21_name(p):
    m = re.fullmatch(r"([A-G])(##|bb|#|b)?(-?\d)", p)
    s, acc, octv = m.groups()
    return s + {"": "", "#": "#", "##": "##", "b": "-", "bb": "--"}[
        acc or ""] + octv


def octave(p, n):
    """Shift a spelled pitch by n octaves, keeping its spelling."""
    m = re.fullmatch(r"([A-G](?:##|bb|#|b)?)(-?\d)", p)
    return f"{m.group(1)}{int(m.group(2)) + n}"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
TOK = re.compile(
    rf"^(\()?((?:{PITCH})(?:\+{PITCH})*|r)/(\d+)([>^.'@]*)(~)?(\))?$")


def parse_bar(s):
    evs, pos = [], 0
    for t in s.split():
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r}")
        sl, pit, dur, flags, ti, sr = m.groups()
        dur = int(dur)
        evs.append(dict(
            pos=pos, dur=dur,
            pitches=None if pit == "r" else pit.split("+"),
            tie=bool(ti), slur_start=bool(sl), slur_end=bool(sr),
            accent=">" in flags, marcato="^" in flags,
            staccato="." in flags, stacc2="'" in flags,
            fermata="@" in flags))
        pos += dur
    if pos != BAR:
        raise ValueError(f"bar sums to {pos} ticks, not {BAR}: {s!r}")
    return evs


def parse_part(data, nbars):
    out = []
    for b in range(1, nbars + 1):
        try:
            evs = parse_bar(data[b])
        except (ValueError, KeyError) as e:
            raise ValueError(f"m{b}: {e}") from None
        for e in evs:
            e["bar"] = b
            e["abs"] = (b - 1) * BAR + e["pos"]
            out.append(e)
    return out


# ---------------------------------------------------------------------------
# Notation splitting: keep the beats visible
# ---------------------------------------------------------------------------
def split_dur(pos, dur):
    """Break a note into notatable pieces that do not hide a beat."""
    pieces = []
    while dur > 0:
        if pos == 0:
            allowed = [48, 36, 24, 18, 12, 9, 6, 4, 3, 2, 1]
        elif pos == 24:
            allowed = [24, 18, 12, 9, 6, 4, 3, 2, 1]
        elif pos % BEAT == 0:
            allowed = [12, 9, 6, 4, 3, 2, 1]
        else:
            r = pos % BEAT
            room = BEAT - r
            # the 16th / eighth grid and the triplet / sextuplet grid
            allowed = sorted({x for x in (6, 4, 3, 2)
                              if x <= room and r % x == 0}, reverse=True)
            allowed += [1]
        d = next((x for x in allowed if x <= dur), None)
        if d is None:
            raise ValueError(f"cannot notate {dur} ticks at {pos}")
        pieces.append(d)
        pos += d
        dur -= d
    return pieces


def _dur(d, full=False):
    """music21 Duration for d ticks.  Sextuplet 16ths (2) are 6:4 when a
    whole beat of them is written, else 16th triplets; 1-tick notes are
    12:8 32nds (or 32nd triplets)."""
    if d == 2:
        du = duration.Duration("16th")
        du.appendTuplet(duration.Tuplet(6, 4, "16th") if full
                        else duration.Tuplet(3, 2, "16th"))
        return du
    if d == 1:
        du = duration.Duration("32nd")
        du.appendTuplet(duration.Tuplet(12, 8, "32nd") if full
                        else duration.Tuplet(3, 2, "32nd"))
        return du
    return duration.Duration(Fraction(d, BEAT))


def mark_full_groups(evs):
    """Flag events that sit in a beat made only of equal 2- or 1-tick
    notes (6 or 12 of them)."""
    by_beat = {}
    for e in evs:
        by_beat.setdefault(e["pos"] // BEAT, []).append(e)
    for beat, es in by_beat.items():
        durs = {e["dur"] for e in es}
        full = (durs == {2} and len(es) == 6) or (durs == {1} and
                                                   len(es) == 12)
        for e in es:
            e["full"] = full


# ---------------------------------------------------------------------------
# music21 score
# ---------------------------------------------------------------------------
CLEFS = {"treble": clef.TrebleClef, "alto": clef.AltoClef,
         "tenor": clef.TenorClef, "bass": clef.BassClef}


def make_part(song, p, events):
    part = stream.Part(id=p["id"])
    ins = p["inst"]()
    ins.partName = p["name"]
    ins.partAbbreviation = p["abbr"]
    part.insert(0, ins)
    notes_at = {}
    slur_open = None
    by_bar = {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    measures = {}
    tied_prev = False
    first_part = p is song.PARTS[0]
    for b in range(1, song.NBARS + 1):
        m = stream.Measure(number=b)
        if b == 1:
            ts = meter.TimeSignature("2/2")
            ts.symbol = "cut"
            ts.beamSequence = meter.MeterSequence("1/4+1/4+1/4+1/4")
            m.insert(0, key.Key(song.KEY_M21))
            m.insert(0, ts)
        for cb, ct, cname in p.get("clefs", []):
            if cb == b and ct == 0:
                m.insert(0, CLEFS[cname]())
        if first_part:
            for tb, tt, bpm, ref in song.METRONOMES:
                if tb == b:
                    # the words are joined to it in polish (one mark)
                    mm = tempo.MetronomeMark(
                        number=bpm, referent=duration.Duration(ref))
                    mm.placement = "above"
                    m.insert(Fraction(tt, BEAT), mm)
        mark_full_groups(by_bar[b])
        for e in by_bar[b]:
            pieces = split_dur(e["pos"], e["dur"])
            objs = []
            for i, d in enumerate(pieces):
                if e["pitches"] is None:
                    n = note.Rest()
                    n.duration = _dur(d, e["full"])
                else:
                    names = [m21_name(x) for x in e["pitches"]]
                    n = (note.Note(names[0]) if len(names) == 1
                         else chord.Chord(names))
                    n.duration = _dur(d, e["full"])
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
                        if e["marcato"]:
                            n.articulations.append(
                                articulations.StrongAccent())
                        if e["staccato"]:
                            n.articulations.append(articulations.Staccato())
                        if e["stacc2"]:
                            n.articulations.append(
                                articulations.Staccatissimo())
                if e["fermata"] and i == len(pieces) - 1:
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
        # zero-length items after the notes, or append() would shift them
        for cb, ct, cname in p.get("clefs", []):
            if cb == b and ct:
                m.insert(Fraction(ct, BEAT), CLEFS[cname]())
        if first_part:
            for tb, tt, txt in song.TEMPO_TEXT:
                if tb == b:
                    tt_ = tempo.TempoText(txt)
                    m.insert(Fraction(tt, BEAT), tt_)
            for sb, letter, title in song.SECTIONS:
                if sb == b:
                    if letter:
                        rm = expressions.RehearsalMark(letter)
                        rm.placement = "above"
                        m.insert(0, rm)
                    te = expressions.TextExpression(title)
                    te.style.fontWeight = "bold"
                    te.placement = "above"
                    m.insert(0, te)
        if b == song.NBARS:
            m.rightBarline = bar.Barline("final")
        elif b in song.DOUBLE_BARS:
            m.rightBarline = bar.Barline("double")
        measures[b] = m
        part.append(m)

    def obj_at(bb, s, forward=True):
        a = (bb - 1) * BAR + s
        ks = sorted(notes_at)
        if forward:
            for k in ks:
                if k >= a:
                    return notes_at[k]
        else:
            for k in reversed(ks):
                if k <= a:
                    return notes_at[k]
        return None

    for bb, s, mark in p["dyn"]:
        d = dynamics.Dynamic(mark)
        d.placement = "below"
        measures[bb].insert(Fraction(s, BEAT), d)
    for bb, s, bb2, s2, kind in p.get("hair_print", p["hair"]):
        cls = dynamics.Crescendo if kind == "cresc" else dynamics.Diminuendo
        n1 = notes_at.get((bb - 1) * BAR + s)
        n2 = obj_at(bb2, s2, forward=False)
        if n1 is None or n2 is None or n1 is n2:
            n1, n2 = spanner.SpannerAnchor(), spanner.SpannerAnchor()
            measures[bb].insert(Fraction(s, BEAT), n1)
            measures[bb2].insert(Fraction(s2 + 1, BEAT), n2)
        part.insert(0, cls(n1, n2))
    for bb, s, txt in p["text"]:
        te = expressions.TextExpression(txt)
        te.style.fontStyle = "italic"
        te.placement = "above"
        measures[bb].insert(Fraction(s, BEAT), te)
    for bb, s, txt in p.get("words_below", []):  # "cresc." over bars
        te = expressions.TextExpression(txt)
        te.style.fontStyle = "italic"
        te.placement = "below"
        measures[bb].insert(Fraction(s, BEAT), te)
    return part


def build_score(song, parsed):
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = song.META["title"]
    md.movementName = f"{song.META['title']}（{song.META['subtitle']}）"
    md.composer = song.META["composer"]
    sc.insert(0, md)
    for p in song.PARTS:
        sc.insert(0, make_part(song, p, parsed[p["id"]]))
    sc.insert(0, layout.StaffGroup(list(sc.parts), name="String Quartet",
                                   symbol="bracket"))
    return sc


# ---------------------------------------------------------------------------
# MusicXML polish (Sibelius / MS4)
# ---------------------------------------------------------------------------
SOUNDS = {"Violin I": ("Violin", "strings.violin"),
          "Violin II": ("Violin", "strings.violin"),
          "Viola": ("Viola", "strings.viola"),
          "Violoncello": ("Violoncello", "strings.cello")}


def _is_sext(n):
    tm = n.find("time-modification")
    return (tm is not None and tm.findtext("actual-notes") == "6"
            and tm.findtext("normal-notes") == "4")


def polish(song, path):
    """Instrument sounds, placement, system breaks, tuplet display, tempo
    words joined to their metronome, 8va lines.  Page layout, credits and
    creators come from tools/hollywood."""
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
    first_pid = r.find("part").get("id")
    divs = int(r.find("part/measure/attributes/divisions").text)
    for part in r.findall("part"):
        pname = names[part.get("id")]
        prev_sext = False
        for m in part.findall("measure"):
            num = int(m.get("number"))
            if num in song.SYSTEM_BREAKS or num in song.PAGE_BREAKS:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                pr.set("new-page" if num in song.PAGE_BREAKS
                       else "new-system", "yes")
            for el in m.findall("direction"):
                if el.find("direction-type/dynamics") is not None or \
                        el.find("direction-type/wedge") is not None:
                    el.set("placement", "below")
                elif el.find("direction-type/words") is not None or \
                        el.find("direction-type/rehearsal") is not None:
                    el.set("placement", "above")
            # tuplets: no brackets on beamed groups; "6" only where a run
            # of sextuplets starts in this part
            notes = [n for n in m.findall("note") if n.find("chord") is None]
            i = 0
            while i < len(notes):
                n = notes[i]
                if _is_sext(n):
                    grp = notes[i:i + 6]
                    show = not prev_sext
                    for k, g in enumerate(grp):
                        for t in g.findall("notations/tuplet"):
                            if t.get("type") == "start":
                                t.set("bracket", "no")
                                t.set("show-number",
                                      "actual" if show else "none")
                    prev_sext = True
                    i += 6
                    continue
                tm = n.find("time-modification")
                if tm is not None:
                    for t in n.findall("notations/tuplet"):
                        if t.get("type") == "start":
                            beamed = n.find("beam") is not None
                            t.set("bracket", "no" if beamed else "yes")
                    prev_sext = False
                else:  # a plain note or rest ends the run of sextuplets
                    prev_sext = False
                i += 1
            # tempo words joined to the metronome (bar 1 is done by
            # tools/hollywood from META["tempo_text"])
            if part.get("id") == first_pid:
                for words in song.TEMPO_WORDS.get(num, []):
                    for dr in m.findall("direction"):
                        met = dr.find("direction-type/metronome")
                        if met is not None:
                            dt = ET.Element("direction-type")
                            ET.SubElement(dt, "words",
                                          {"font-weight": "bold"}).text = \
                                words + " "
                            dr.insert(0, dt)
                            break
        ms = {int(m.get("number")): m for m in part.findall("measure")}
        for spec in song.OTTAVA:
            if spec[0] != pname:
                continue
            if len(spec) == 3:
                b1, t1, b2, t2 = spec[1], 0, spec[2], BAR - 1
            else:
                b1, t1, b2, t2 = spec[1:]
            first = _note_at(ms[b1], t1, divs, forward=True)
            last = _note_at(ms[b2], t2, divs, forward=False)
            start = ET.fromstring(
                '<direction placement="above"><direction-type>'
                '<octave-shift type="down" size="8"/></direction-type>'
                '</direction>')
            ms[b1].insert(list(ms[b1]).index(first), start)
            stop = ET.fromstring(
                '<direction><direction-type><octave-shift type="stop" '
                'size="8"/></direction-type></direction>')
            ms[b2].insert(list(ms[b2]).index(last) + 1, stop)
        for (pn, b), way in song.STEMS.items():
            if pn != pname:
                continue
            for n in ms[b].findall("note"):
                tm = n.find("time-modification")
                if tm is None:
                    continue
                st = n.find("stem")
                if st is None:  # schema order: right after time-modification
                    st = ET.Element("stem")
                    n.insert(list(n).index(tm) + 1, st)
                st.text = way
                for t in n.findall("notations/tuplet"):
                    if t.get("type") == "start":
                        t.set("placement", "above" if way == "up"
                              else "below")
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


def _note_at(measure, tick, divs, forward=True):
    """The first pitched note starting at or after `tick` (forward), or the
    last one starting at or before it, in a single-voice measure."""
    pos, hits = 0, []
    for n in measure.findall("note"):
        if n.find("chord") is not None:
            continue
        on = pos * BEAT / divs
        if n.find("rest") is None:
            hits.append((on, n))
        pos += int(n.findtext("duration"))
    if forward:
        return next(n for on, n in hits if on >= tick - 1e-6)
    return [n for on, n in hits if on <= tick + 1e-6][-1]


def verify_bars(song, path):
    """Every bar of every part in the written file must hold exactly 2/2."""
    from music21 import converter
    for p in converter.parse(path).parts:
        ms = p.getElementsByClass("Measure")
        assert len(ms) == song.NBARS, (p.partName, len(ms))
        for m in ms:
            assert abs(m.duration.quarterLength - 4) < 1e-6, \
                (p.partName, m.number, m.duration.quarterLength)


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
VEL = {"ppp": 24, "pp": 34, "p": 46, "mp": 60, "mf": 74, "f": 90,
       "ff": 104, "fff": 116, "fp": 90, "fz": 104, "sf": 104, "sfz": 108}
AFTER = {"fp": "p", "fz": None, "sf": None, "sfz": None}
ACCENT = 12


def merged_notes(events):
    out, cur = [], None
    for e in events:
        if e["pitches"] is None:
            cur = None
            continue
        if cur is not None and cur["tie"]:
            cur["dur"] += e["dur"]
            cur["tie"] = e["tie"]
            continue
        cur = dict(start=e["abs"], dur=e["dur"], pitches=e["pitches"],
                   tie=e["tie"], accent=e["accent"] or e["marcato"],
                   marcato=e["marcato"], staccato=e["staccato"],
                   stacc2=e["stacc2"])
        out.append(cur)
    return out


def dyn_curve(song, p):
    total = song.NBARS * BAR
    pts = []
    for b, s, mk in p["dyn"]:
        a = (b - 1) * BAR + s
        pts.append((a, VEL[mk]))
        if mk in AFTER:   # fp / fz: a spike, then the running level
            after = AFTER[mk]
            prev = [v for t, v in pts[:-1]]
            lvl = VEL[after] if after else (prev[-1] if prev else VEL["f"])
            pts.append((a + 3, lvl))
    pts.sort()
    v = [pts[0][1]] * total
    for i, (a, val) in enumerate(pts):
        end = pts[i + 1][0] if i + 1 < len(pts) else total
        for t in range(a, end):
            v[t] = val
    for b, s, b2, s2, kind in p["hair"]:
        a = (b - 1) * BAR + s
        z = (b2 - 1) * BAR + s2
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


def tempo_track(song):
    ab = [(0, mido.MetaMessage("track_name", name=song.MIDI_TITLE)),
          (0, mido.MetaMessage("time_signature", numerator=2,
                               denominator=2)),
          (0, mido.MetaMessage("key_signature", key=song.KEY_MIDI))]
    for b, s, bpm in song.TEMPI:
        t = ((b - 1) * BAR + s) * TICK
        ab.append((t, mido.MetaMessage("set_tempo",
                                       tempo=mido.bpm2tempo(bpm))))
    for b, _, name in song.SECTIONS:
        ab.append(((b - 1) * BAR * TICK,
                   mido.MetaMessage("marker", text=name.split()[0])))
    ab.sort(key=lambda x: x[0])
    tr, last = mido.MidiTrack(), 0
    for t, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def part_track(song, p, events, ch, with_cc=True):
    notes = merged_notes(events)
    vel = dyn_curve(song, p)
    ab = [(0, 0, mido.MetaMessage("track_name", name=p["name"])),
          (0, 1, mido.Message("program_change", channel=ch,
                              program=p["program"]))]
    if with_cc:
        for t in range(0, song.NBARS * BAR, 3):
            if t == 0 or vel[t] != vel[t - 3]:
                val = min(127, 16 + vel[t])
                for cc in (11, 1):
                    ab.append((t * TICK, 2, mido.Message(
                        "control_change", channel=ch, control=cc,
                        value=val)))
    for i, n in enumerate(notes):
        on = n["start"] * TICK
        length = n["dur"] * TICK
        if n["stacc2"]:
            length = int(length * 0.3)
        elif n["staccato"]:
            length = int(length * 0.5)
        off = on + length
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        if nxt and nxt["start"] * TICK <= off and \
                set(nxt["pitches"]) & set(n["pitches"]):
            off = min(off, nxt["start"] * TICK - (12 if n["dur"] > 3
                                                   else 6))
        v = vel[min(n["start"], len(vel) - 1)]
        if n["accent"]:
            v += ACCENT + (6 if n["marcato"] else 0)
        v = max(1, min(127, v))
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


def write_midi(song, path, part_ids, parsed, with_cc=True):
    mf = mido.MidiFile(type=1, ticks_per_beat=TPQ, charset="utf-8")
    mf.tracks.append(tempo_track(song))
    for ch, p in enumerate(song.PARTS):
        if p["id"] in part_ids:
            mf.tracks.append(part_track(song, p, parsed[p["id"]], ch,
                                        with_cc=with_cc))
    mf.save(path)


def seconds(song):
    """Length of the piece in seconds (from the tempo map)."""
    marks = [((b - 1) * BAR + s, bpm) for b, s, bpm in song.TEMPI]
    total = song.NBARS * BAR
    t = 0.0
    for i, (a, bpm) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else total
        t += (end - a) / BEAT * 60.0 / bpm
    return t


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
OPEN = {"violin": ["G3", "D4", "A4", "E5"], "viola": ["C3", "G3", "D4", "A4"],
        "cello": ["C2", "G2", "D3", "A3"]}


def stop_ok(kind, pitches):
    """Can these notes be stopped on adjacent strings in one hand frame?
    (each note on its own string, no more than a fourth between the two
    finger positions, nothing above the 7th position)."""
    opens = [midi_of(x) for x in OPEN[kind]]
    ps = sorted(midi_of(x) for x in pitches)
    k = len(ps)
    for s0 in range(len(opens) - k + 1):
        pos = [ps[i] - opens[s0 + i] for i in range(k)]
        if min(pos) < 0 or max(pos) > 12:
            continue
        fingered = [x for x in pos if x > 0]
        if not fingered or max(fingered) - min(fingered) <= 5:
            return True
    return False


def sounding(parsed, min_dur=0):
    grid = {}
    for pid, evs in parsed.items():
        held = False
        for e in evs:
            if e["pitches"] is None:
                held = False
                continue
            if e["dur"] >= min_dur or held or e["tie"]:
                for t in range(e["abs"], e["abs"] + e["dur"]):
                    for pit in e["pitches"]:
                        grid.setdefault(t, []).append(
                            (pid, midi_of(pit), pit,
                             t == e["abs"] and not held))
            held = e["tie"]
    return grid


def structural_line(evs, min_dur=6):
    """(start, top midi) of every held note (an eighth or longer)."""
    out, held = [], False
    for e in evs:
        if e["pitches"] is None or (e["dur"] < min_dur and not held):
            out.append((e["abs"], None))
            held = False
            continue
        if not held:
            out.append((e["abs"], max(midi_of(x) for x in e["pitches"])))
        held = e["tie"]
    return out


def check(song, parsed):
    problems, clashes, parallels, stops = [], [], [], []
    kinds = {p["id"]: p["kind"] for p in song.PARTS}
    for pid, evs in parsed.items():
        lo, hi = (midi_of(x) for x in song.RANGES[pid])
        for e in evs:
            for pit in e["pitches"] or []:
                if not lo <= midi_of(pit) <= hi:
                    problems.append(f"{pid} m{e['bar']} {pit} out of range")
            if e["pitches"] and len(e["pitches"]) > 1 and \
                    not stop_ok(kinds[pid], e["pitches"]):
                stops.append(f"{pid} m{e['bar']} "
                             f"{'+'.join(e['pitches'])} not playable")
    # m2 / b9 between held notes (the wind's passing notes are Chopin's)
    grid = sounding(parsed, min_dur=6)
    seen = set()
    for t, snd in sorted(grid.items()):
        for i in range(len(snd)):
            for j in range(i + 1, len(snd)):
                a, b = snd[i], snd[j]
                if a[0] == b[0] or not (a[3] or b[3]):
                    continue
                iv = abs(a[1] - b[1])
                key_ = (t // BAR + 1, a[0], a[2], b[0], b[2])
                if iv % 12 == 1 and key_ not in seen and \
                        (t // BAR + 1, a[0], b[0]) not in song.CLASH_OK and \
                        (t // BAR + 1, b[0], a[0]) not in song.CLASH_OK:
                    seen.add(key_)
                    clashes.append(
                        f"m{t // BAR + 1}.{t % BAR:02d} {a[0]}:{a[2]} "
                        f"x {b[0]}:{b[2]} ({'m2' if iv == 1 else 'b9'})")
    lines = {pid: structural_line(evs) for pid, evs in parsed.items()}
    ids = list(parsed)
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
                    bar_ = t // BAR + 1
                    if (ids[i], ids[j], bar_) in song.PARALLEL_OK:
                        pass
                    elif same_dir and iv0 == iv1 and iv1 in (0, 7):
                        parallels.append(
                            f"m{bar_}.{t % BAR:02d} {ids[i]}/{ids[j]} "
                            f"{'P8' if iv1 == 0 else 'P5'}")
                prev = (pa, pb)
    return problems, stops, clashes, parallels
