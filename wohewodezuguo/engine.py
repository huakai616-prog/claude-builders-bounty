#!/usr/bin/env python3
"""Engine for wohewodezuguo/build.py (我和我的祖国, SATB soli + string quartet).

Grown out of chatang/build.py and extended for this song:
  * compound and mixed metre (6/8 and 9/8 bars; bar lengths vary);
  * four sung parts (S, A, T, B), each with its own lyric line;
  * breath blocks: a short note with the lyric "br" before each phrase,
    written only into the lyric MIDIs (never shown in the score);
  * pizzicato / arco ranges (score text, <sound pizzicato>, and a GM
    pizzicato patch in the preview MIDI only);
  * fermatas (token flag "^"), timed through the tempo map.

build.py holds the music (one dict per part, one string per bar, durations
in sixteenths) and calls run(song).  Token syntax:
  C5/2        note C5, an eighth           r/6          rest, a dotted quarter
  D4+F4/6     double stop                   A4/2~        tie into the next note
  F5/1>       accent                        F5/4^        fermata
  (G4/1 A4/1) slur start / end              G4/2=字      lyric
Durations: 1 = 16th, 2 = eighth, 3 = dotted eighth, 4 = quarter,
6 = dotted quarter, 12 = dotted half, 18 = a whole 9/8 bar.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

import mido
from music21 import (articulations, bar, clef, duration, dynamics,
                     expressions, instrument, key, layout, metadata, meter,
                     note, chord, spanner, stream, tempo, tie)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hollywood"))
import hollywood  # noqa: E402  (shared Hollywood score template)

TPQ = 480
T16 = TPQ // 4

_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = "C C# D Eb E F F# G Ab A Bb B".split()


def midi_of(p):
    m = re.fullmatch(r"([A-G])([#b]?)(-?\d)", p)
    if not m:
        raise ValueError(p)
    s, acc, octv = m.groups()
    v = _STEP[s] + (1 if acc == "#" else -1 if acc == "b" else 0)
    return 12 * (int(octv) + 1) + v


def name_of(m):
    return f"{NAMES[m % 12]}{m // 12 - 1}"


def m21_name(p):
    return p.replace("b", "-") if len(p) > 1 and p[1] == "b" else p


# ---------------------------------------------------------------------------
# Song layout (filled by configure())
# ---------------------------------------------------------------------------
S = None           # the song module (build.py)
NBARS = 0
BARLEN = {}        # bar -> length in 16ths (12 for 6/8, 18 for 9/8)
START = {}         # bar -> absolute 16th of its first beat
TOTAL = 0


def configure(song):
    global S, NBARS, TOTAL
    S = song
    NBARS = song.NBARS
    pos = 0
    for b in range(1, NBARS + 1):
        n = 18 if b in song.NINE_EIGHT else 12
        BARLEN[b] = n
        START[b] = pos
        pos += n
    TOTAL = pos


def absq(b, s=0):
    return START[b] + s


def bar_of(t):
    for b in range(NBARS, 0, -1):
        if START[b] <= t:
            return b, t - START[b]
    return 1, t


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(\()?((?:[A-G][#b]?\d)(?:\+[A-G][#b]?\d)*|r)/(\d+)([>*^~]*)(\))?"
    r"(?:=(.+))?$")


def parse_bar(s, b):
    evs, pos = [], 0
    for t in s.split():
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r} in {s!r}")
        sl, pit, dur, flags, sr, lyr = m.groups()
        dur = int(dur)
        evs.append(dict(
            pos=pos, dur=dur,
            pitches=None if pit == "r" else pit.split("+"),
            tie="~" in flags, slur_start=bool(sl), slur_end=bool(sr),
            accent=">" in flags, mordent="*" in flags,
            fermata="^" in flags, lyric=lyr))
        pos += dur
    if pos != BARLEN[b]:
        raise ValueError(f"bar sums to {pos}, not {BARLEN[b]}: {s!r}")
    return evs


def parse_part(data):
    out = []
    for b in range(1, NBARS + 1):
        src = data.get(b, f"r/{BARLEN[b]}")
        try:
            evs = parse_bar(src, b)
        except ValueError as e:
            raise ValueError(f"m{b}: {e}") from None
        for e in evs:
            e["bar"] = b
            e["abs"] = START[b] + e["pos"]
            out.append(e)
    return out


# ---------------------------------------------------------------------------
# Notation splitting (compound metre: the beat is a dotted quarter)
# ---------------------------------------------------------------------------
def split_dur(pos, dur, barlen):
    """Pieces that keep the dotted-quarter beats of 6/8 and 9/8 visible."""
    pieces = []
    while dur > 0:
        r = pos % 6
        if r == 0:
            allowed = [x for x in (12, 6, 4, 3, 2, 1)
                       if x != 12 or pos + 12 <= barlen]
            if pos == 0 and barlen == 18 and dur >= 18:
                allowed = [12] + allowed  # dotted half + dotted quarter
        elif r == 2:
            allowed = [4, 3, 2, 1]
        elif r == 4:
            allowed = [2, 1]
        elif r == 3:
            allowed = [3, 1]  # a dotted eighth on the half beat (2 against 3)
        else:
            allowed = [1]
        d = next(x for x in allowed if x <= dur and pos + x <= barlen)
        pieces.append(d)
        pos += d
        dur -= d
    return pieces


def _slice(e, a, b):
    """Part of event e from absolute a to b (for display splitting)."""
    return a, b


# ---------------------------------------------------------------------------
# music21 score
# ---------------------------------------------------------------------------
def pizz_state(pid, b, s):
    """True if a note starting at bar b, 16th s is pizzicato."""
    t = absq(b, s)
    for (b1, s1, b2, s2) in S.PIZZ.get(pid, []):
        if absq(b1, s1) <= t < absq(b2, s2):
            return True
    return False


def make_m21(p, events):
    part = stream.Part(id=p["id"])
    ins = p["inst"]()
    ins.partName = p["name"]
    ins.partAbbreviation = p["abbr"]
    part.insert(0, ins)
    notes_at = {}
    slur_open = None
    measures = {}
    by_bar = {}
    for e in events:
        by_bar.setdefault(e["bar"], []).append(e)
    tied_prev = False
    prev_pizz = False
    prev_ts = None
    for b in range(1, NBARS + 1):
        m = stream.Measure(number=b)
        ts = "9/8" if BARLEN[b] == 18 else "6/8"
        if b == 1:
            m.insert(0, p["clef"]())
            m.insert(0, key.Key(S.KEY_M21))
        if ts != prev_ts:
            m.insert(0, meter.TimeSignature(ts))
            prev_ts = ts
        if b == 1 and p["id"] == S.TOP:
            mm = tempo.MetronomeMark(number=S.DOTTED_BPM,
                                     referent=duration.Duration(1.5))
            mm.placement = "above"
            m.insert(0, mm)
        full_rest = (len(by_bar[b]) == 1 and by_bar[b][0]["pitches"] is None)
        for e in by_bar[b]:
            if full_rest:
                n = note.Rest(quarterLength=BARLEN[b] / 4)
                n.fullMeasure = True
                m.append(n)
                objs = [n]
                notes_at.setdefault(e["abs"], n)
                e["m21"] = objs
                tied_prev = False
                continue
            pieces = split_dur(e["pos"], e["dur"], BARLEN[b])
            objs = []
            for i, d in enumerate(pieces):
                if e["pitches"] is None:
                    n = note.Rest(quarterLength=d / 4)
                else:
                    names = [m21_name(x) for x in e["pitches"]]
                    n = (note.Note(names[0], quarterLength=d / 4)
                         if len(names) == 1 else
                         chord.Chord(names, quarterLength=d / 4))
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
                    if last and e["fermata"]:
                        f = expressions.Fermata()
                        f.type = "upright"
                        n.expressions.append(f)
                m.append(n)
                objs.append(n)
            if e["pitches"] is None and e["fermata"]:
                f = expressions.Fermata()
                f.type = "upright"
                objs[-1].expressions.append(f)
            notes_at.setdefault(e["abs"], objs[0])
            e["m21"] = objs
            if e["pitches"] is not None and not tied_prev:
                pz = pizz_state(p["id"], b, e["pos"])
                if pz != prev_pizz:
                    te = expressions.TextExpression("pizz." if pz else "arco")
                    te.style.fontStyle = "italic"
                    te.placement = "above"
                    m.insert(e["pos"] / 4, te)
                    e["pizz_mark"] = "pizz" if pz else "arco"
                    prev_pizz = pz
            tied_prev = e["tie"] and e["pitches"] is not None
            if e["slur_start"]:
                slur_open = objs[0]
            if e["slur_end"] and slur_open is not None:
                part.insert(0, spanner.Slur(slur_open, objs[-1]))
                slur_open = None
        if p["id"] == S.TOP:  # after the notes, or append() would shift them
            for tb, tsx, txt in S.TEMPO_TEXT:
                if tb == b:
                    m.insert(tsx / 4, tempo.TempoText(txt))
            for sb, letter, title in S.SECTIONS:
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
            m.rightBarline = bar.Barline("final")
        measures[b] = m
        part.append(m)

    def obj_at(bb, s, forward=True):
        a = absq(bb, s)
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

    vocal = p.get("vocal", False)
    for bb, s, mark in p["dyn"]:
        d = dynamics.Dynamic(mark)
        d.placement = "above" if vocal else "below"
        measures[bb].insert(s / 4, d)
    for bb, s, bb2, s2, kind in (p["hair"] if p.get("print_hair", True)
                                 else []):
        cls = dynamics.Crescendo if kind == "cresc" else dynamics.Diminuendo
        n1 = notes_at.get(absq(bb, s))
        n2 = obj_at(bb2, s2, forward=False)
        if n1 is None or n2 is None or n1 is n2 or \
                not isinstance(n1, note.GeneralNote) or \
                isinstance(n1, note.Rest) or isinstance(n2, note.Rest):
            n1, n2 = spanner.SpannerAnchor(), spanner.SpannerAnchor()
            measures[bb].insert(s / 4, n1)
            measures[bb2].insert((s2 + 1) / 4, n2)
        part.insert(0, cls(n1, n2))
    for bb, s, txt in p["text"]:
        te = expressions.TextExpression(txt)
        te.style.fontStyle = "italic"
        te.placement = "above"
        measures[bb].insert(s / 4, te)
    return part


def build_score(parsed):
    sc = stream.Score()
    md = metadata.Metadata()
    md.title = S.META["title"]
    md.movementName = f"{S.META['title']}（{S.META['subtitle']}）"
    md.composer = S.META["composer"]
    md.lyricist = S.META["lyricist"]
    sc.insert(0, md)
    parts = []
    for p in S.PARTS:
        mp = make_m21(p, parsed[p["id"]])
        sc.insert(0, mp)
        parts.append((p, mp))
    voc = [mp for p, mp in parts if p.get("vocal")]
    strs = [mp for p, mp in parts if not p.get("vocal")]
    sc.insert(0, layout.StaffGroup(voc, name="Soli", symbol="bracket",
                                   barTogether=False))
    sc.insert(0, layout.StaffGroup(strs, name="String Quartet",
                                   symbol="bracket", barTogether=True))
    return sc


# ---------------------------------------------------------------------------
# MusicXML polish for Sibelius
# ---------------------------------------------------------------------------
def polish(path):
    """Instrument sounds, system breaks, placements, pizzicato playback."""
    tree = ET.parse(path)
    r = tree.getroot()
    for sp in r.iter("score-part"):
        pname = sp.findtext("part-name")
        iname, snd = S.SOUNDS[pname]
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
    vocal_names = {p["name"] for p in S.PARTS if p.get("vocal")}
    for part in r.findall("part"):
        vocal = names[part.get("id")] in vocal_names
        for m in part.findall("measure"):
            if int(m.get("number")) in S.SYSTEM_BREAKS:
                pr = m.find("print")
                if pr is None:
                    pr = ET.Element("print")
                    m.insert(0, pr)
                pr.set("new-system", "yes")
            if int(m.get("number")) in getattr(S, "PAGE_BREAKS", ()):
                pr = m.find("print")
                pr.set("new-page", "yes")
                pr.attrib.pop("new-system", None)
            for el in m.findall("direction"):
                w = el.find("direction-type/words")
                if el.find("direction-type/dynamics") is not None or \
                        el.find("direction-type/wedge") is not None:
                    el.set("placement", "above" if vocal else "below")
                elif w is not None or \
                        el.find("direction-type/rehearsal") is not None:
                    el.set("placement", "above")
                if w is not None and (w.text or "").strip() in ("pizz.",
                                                               "arco"):
                    snd = el.find("sound")
                    if snd is None:
                        snd = ET.SubElement(el, "sound")
                    snd.set("pizzicato",
                            "yes" if w.text.strip() == "pizz." else "no")
        for pname, b1, b2 in getattr(S, "OTTAVA", ()):
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
    xml = open(path, encoding="utf-8").read()
    if "<!DOCTYPE" not in xml:
        xml = xml.replace(
            "?>\n",
            "?>\n<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD "
            "MusicXML 4.0 Partwise//EN\" "
            "\"http://www.musicxml.org/dtds/partwise.dtd\">\n", 1)
        open(path, "w", encoding="utf-8").write(xml)


def verify_bars(path):
    """Every bar of every part in the written file holds its time signature."""
    from music21 import converter
    for p in converter.parse(path).parts:
        ms = p.getElementsByClass("Measure")
        assert len(ms) == NBARS, (p.partName, len(ms))
        for m in ms:
            want = BARLEN[m.number] / 4
            assert abs(m.duration.quarterLength - want) < 1e-6, \
                (p.partName, m.number, m.duration.quarterLength, want)


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
def merged_notes(events):
    """Merge tied notes: dicts (start, dur, pitches, lyric, melisma, ...)."""
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
            cur["fermata"] = cur["fermata"] or e["fermata"]
            if e["slur_start"]:
                in_slur = True
            if e["slur_end"]:
                in_slur = False
            continue
        cur = dict(start=e["abs"], dur=e["dur"], pitches=e["pitches"],
                   lyric=e["lyric"], tie=e["tie"], accent=e["accent"],
                   fermata=e["fermata"], bar=e["bar"],
                   melisma=(e["lyric"] is None and in_slur))
        out.append(cur)
        if e["slur_start"]:
            in_slur = True
        if e["slur_end"]:
            in_slur = False
    return out


def dyn_curve(p):
    """velocity at each absolute 16th."""
    pts = sorted((absq(b, s), S.VEL[m]) for b, s, m in p["dyn"])
    v = [pts[0][1] if pts else 64] * TOTAL
    for i, (a, val) in enumerate(pts):
        end = pts[i + 1][0] if i + 1 < len(pts) else TOTAL
        for t in range(a, end):
            v[t] = val
    for b, s, b2, s2, kind in p["hair"]:
        a = absq(b, s)
        z = absq(b2, s2)
        v0 = v[a]
        nxt = [val for t, val in pts if t > z]
        v1 = nxt[0] if nxt else v0 + (-14 if kind == "dim" else 14)
        if kind == "cresc" and v1 <= v0:
            v1 = v0 + 12
        if kind == "dim" and v1 >= v0:
            v1 = v0 - 12
        for t in range(a, min(z + 1, TOTAL)):
            v[t] = max(1, min(127, round(v0 + (v1 - v0) * (t - a)
                                         / max(1, z - a))))
    return v


def tempo_track(title):
    ab = [(0, 0, mido.MetaMessage("track_name", name=title)),
          (0, 0, mido.MetaMessage("key_signature", key=S.KEY_MIDI))]
    prev = None
    for b in range(1, NBARS + 1):
        n = 9 if BARLEN[b] == 18 else 6
        if n != prev:
            ab.append((START[b] * T16, 0, mido.MetaMessage(
                "time_signature", numerator=n, denominator=8,
                clocks_per_click=36, notated_32nd_notes_per_beat=8)))
            prev = n
    for b, s, bpm in S.TEMPI:
        ab.append((absq(b, s) * T16, 1, mido.MetaMessage(
            "set_tempo", tempo=mido.bpm2tempo(bpm))))
    for b, _, name in S.SECTIONS:
        ab.append((START[b] * T16, 2,
                   mido.MetaMessage("marker", text=name)))
    ab.sort(key=lambda x: (x[0], x[1]))
    tr, last = mido.MidiTrack(), 0
    for t, _, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def breath_blocks(p, notes):
    """(start16, dur16, pitch) of the 'br' notes before the phrases listed in
    p['breaths'] ((bar, 16th) of each phrase's first note).  A breath sits in
    the rest before the phrase (up to an eighth); with no rest it takes the
    end of the previous note (an eighth off a long note, a 16th otherwise)
    and returns the shortened end of that note."""
    out, trims = [], {}
    starts = {n["start"]: i for i, n in enumerate(notes)}
    for b, s in p.get("breaths", []):
        t = absq(b, s)
        if t not in starts:
            raise ValueError(f"{p['id']}: no note starts at m{b}.{s} "
                             "for a breath")
        i = starts[t]
        pitch = notes[i]["pitches"][0]
        prev_end = notes[i - 1]["start"] + notes[i - 1]["dur"] if i else -99
        gap = t - prev_end
        if gap >= 1:
            d = min(2, gap)
            out.append((t - d, d, pitch))
        else:
            pd = notes[i - 1]["dur"]
            d = 2 if pd >= 6 else 1
            trims[i - 1] = pd - d
            out.append((t - d, d, pitch))
    return out, trims


GM_PIZZ = 45


def part_track(p, events, ch, lyrics=True, with_cc=True, breaths=False,
               pizz_patch=False):
    notes = merged_notes(events)
    vel = dyn_curve(p)
    vocal = p.get("vocal", False)
    ab = []  # (tick, order, msg)
    ab.append((0, 0, mido.MetaMessage("track_name", name=p["midi_name"])))
    ab.append((0, 1, mido.Message("program_change", channel=ch,
                                  program=p["program"])))
    if with_cc:
        for t in range(0, TOTAL, 2):
            if t == 0 or vel[t] != vel[t - 2]:
                val = min(127, 20 + vel[t])
                ab.append((t * T16, 2, mido.Message(
                    "control_change", channel=ch, control=11, value=val)))
                ab.append((t * T16, 2, mido.Message(
                    "control_change", channel=ch, control=1, value=val)))
    br, trims = ([], {})
    if vocal and lyrics and breaths:
        br, trims = breath_blocks(p, notes)
    cur_patch = p["program"]
    for i, n in enumerate(notes):
        on = n["start"] * T16
        dur = trims.get(i, n["dur"])
        off = (n["start"] + dur) * T16
        nxt = notes[i + 1] if i + 1 < len(notes) else None
        pz = (not vocal) and pizz_state(p["id"], *bar_of(n["start"]))
        if pz:  # plucked: short, whatever the written value
            off = min(off, on + int(T16 * 1.6))
        elif nxt and nxt["start"] * T16 == off and \
                set(nxt["pitches"]) & set(n["pitches"]):
            off -= 12 if dur > 2 else 24
        if pizz_patch and not vocal:
            want = GM_PIZZ if pz else p["program"]
            if want != cur_patch:
                ab.append((on, 1, mido.Message("program_change", channel=ch,
                                               program=want)))
                cur_patch = want
        v = vel[min(n["start"], len(vel) - 1)]
        if n["accent"]:
            v += S.ACCENT
        if pz:
            v += 8
        v = max(1, min(127, v))
        syl = n["lyric"] if n["lyric"] else ("-" if n["melisma"] else None)
        if lyrics and vocal:
            ab.append((on, 4, mido.MetaMessage("lyrics",
                                               text=syl if syl else "-")))
        for pit in n["pitches"]:
            ab.append((on, 5, mido.Message("note_on", channel=ch,
                                           note=midi_of(pit), velocity=v)))
            ab.append((off, 3, mido.Message("note_off", channel=ch,
                                            note=midi_of(pit), velocity=0)))
    for (st, d, pit) in br:
        on, off = st * T16, (st + d) * T16 - 10
        vb = max(1, vel[min(st, len(vel) - 1)] - 30)
        ab.append((on, 4, mido.MetaMessage("lyrics", text="br")))
        ab.append((on, 5, mido.Message("note_on", channel=ch,
                                       note=midi_of(pit), velocity=vb)))
        ab.append((off, 3, mido.Message("note_off", channel=ch,
                                        note=midi_of(pit), velocity=0)))
    ab.sort(key=lambda x: (x[0], x[1]))
    tr, last = mido.MidiTrack(), 0
    for t, _, m in ab:
        tr.append(m.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def write_midi(path, part_ids, parsed, title, lyrics=True, charset="utf-8",
               with_cc=True, breaths=False, pizz_patch=False):
    mf = mido.MidiFile(type=1, ticks_per_beat=TPQ, charset=charset)
    mf.tracks.append(tempo_track(title))
    ch = 0
    for p in S.PARTS:
        if p["id"] in part_ids:
            mf.tracks.append(part_track(p, parsed[p["id"]], ch,
                                        lyrics=lyrics, with_cc=with_cc,
                                        breaths=breaths,
                                        pizz_patch=pizz_patch))
            ch += 1
            if ch == 9:
                ch = 10
    mf.save(path)


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
            pz = pid in S.PIZZ and pizz_state(pid, e["bar"], e["pos"])
            span = min(e["dur"], 2) if pz else e["dur"]
            for t in range(e["abs"], e["abs"] + span):
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


def bottom_line(evs):
    out, held = [], False
    for e in evs:
        if e["pitches"] is None:
            out.append((e["abs"], None))
            held = False
            continue
        if not held:
            out.append((e["abs"], min(midi_of(x) for x in e["pitches"])))
        held = e["tie"]
    return out


def _at(line, t):
    cur = None
    for s_, p_ in line:
        if s_ > t:
            break
        cur = p_
    return cur


def _allowed(kind, a, b, bar):
    for k, x, y, bars in S.ALLOW:
        if k == kind and {x, y} == {a, b} and bar in bars:
            return True
    return False


def check(parsed):
    problems = []
    for pid, evs in parsed.items():
        lo, hi = (midi_of(x) for x in S.RANGES[pid])
        for e in evs:
            for pit in e["pitches"] or []:
                if not lo <= midi_of(pit) <= hi:
                    problems.append(f"{pid} m{e['bar']} {pit} out of range")
    # lyrics: every sung note carries a syllable or continues a slur
    for p in S.PARTS:
        if not p.get("vocal"):
            continue
        for n in merged_notes(parsed[p["id"]]):
            if not n["lyric"] and not n["melisma"]:
                problems.append(f"{p['id']} m{n['bar']} note without lyric")
    grid = sounding(parsed)
    clashes = []
    for t, snd in sorted(grid.items()):
        b, s = bar_of(t)
        for i in range(len(snd)):
            for j in range(i + 1, len(snd)):
                a, c = snd[i], snd[j]
                if a[0] == c[0] or not (a[3] or c[3]):
                    continue
                iv = abs(a[1] - c[1])
                if iv % 12 == 1 and iv < 36 and \
                        not _allowed("clash", a[0], c[0], b):
                    clashes.append(
                        f"m{b}.{s:02d} {a[0]}:{a[2]} x {c[0]}:{c[2]} "
                        f"({'m2' if iv == 1 else 'b9'})")
    parallels = []
    groups = [[p["id"] for p in S.PARTS if p.get("vocal")],
              [p["id"] for p in S.PARTS if not p.get("vocal")]]
    pairs = []
    for g in groups:
        pairs += [(g[i], g[j]) for i in range(len(g))
                  for j in range(i + 1, len(g))]
    for x, y in pairs:
        a, c = top_line(parsed[x]), top_line(parsed[y])
        times = sorted({t for t, _ in a} | {t for t, _ in c})
        prev = None
        for t in times:
            pa, pc = _at(a, t), _at(c, t)
            if None in (pa, pc):
                prev = None
                continue
            if prev and pa != prev[0] and pc != prev[1]:
                iv0 = abs(prev[0] - prev[1]) % 12
                iv1 = abs(pa - pc) % 12
                same = (pa - prev[0]) * (pc - prev[1]) > 0
                b, s = bar_of(t)
                if same and iv0 == iv1 and iv1 in (0, 7) and \
                        not _allowed("parallel", x, y, b):
                    parallels.append(f"m{b}.{s:02d} {x}/{y} "
                                     f"{'P8' if iv1 == 0 else 'P5'}")
            prev = (pa, pc)
    # vocal crossing (adjacent voices, both singing)
    crossings = []
    voc = groups[0]
    for up, lo in zip(voc, voc[1:]):
        a, c = bottom_line(parsed[up]), top_line(parsed[lo])
        times = sorted({t for t, _ in a} | {t for t, _ in c})
        for t in times:
            pa, pc = _at(a, t), _at(c, t)
            if pa is not None and pc is not None and pc > pa:
                b, s = bar_of(t)
                if not _allowed("cross", up, lo, b):
                    crossings.append(f"m{b}.{s:02d} {lo} above {up} "
                                     f"({name_of(pc)} > {name_of(pa)})")
    return problems, clashes, parallels, crossings


# ---------------------------------------------------------------------------
# Lyric subtitles (SRT) and lyric paste text
# ---------------------------------------------------------------------------
def sec_at(a16):
    marks = [(absq(b, s), bpm) for b, s, bpm in S.TEMPI]
    t = 0.0
    for i, (a, bpm) in enumerate(marks):
        if a16 <= a:
            break
        end = marks[i + 1][0] if i + 1 < len(marks) else a16
        t += (min(a16, end) - a) * 15.0 / bpm
    return t


def syllables(events, b1=1, b2=None):
    b2 = b2 or NBARS
    out = []
    for e in events:
        if e["pitches"] is None or not b1 <= e["bar"] <= b2:
            continue
        if e["lyric"]:
            out.append([e["lyric"], e["abs"], e["abs"] + e["dur"]])
        elif out:
            out[-1][2] = e["abs"] + e["dur"]
    return out


def write_srt(path, parsed):
    lines = []
    for text, pid, b1, b2 in S.SUB_LINES:
        syl = syllables(parsed[pid], b1, b2)
        got = "".join(x[0] for x in syl)
        assert got == text, (text, got, pid, b1, b2)
        lines.append((text, sec_at(syl[0][1]), sec_at(syl[-1][2])))

    def ts(t):
        ms = int(round(t * 1000))
        return (f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:"
                f"{ms // 1000 % 60:02d},{ms % 1000:03d}")

    out = []
    for k, (text, s_, e_) in enumerate(lines):
        start = max(0.0, s_ - S.SUB_LEAD)
        end = (min(e_ + S.SUB_TAIL, lines[k + 1][1] - S.SUB_LEAD - 0.04)
               if k + 1 < len(lines) else e_ + S.SUB_TAIL)
        out.append(f"{k + 1}\n{ts(start)} --> {ts(end)}\n{text}\n")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out))


def write_lyric_text(path, p, events):
    """One syllable per note, '-' for a melisma note, grouped by section."""
    notes = merged_notes(events)
    rows = []
    heads = {b: t for b, _, t in S.SECTIONS}
    cur = None
    for n in notes:
        b = n["bar"]
        sec = max(x for x in heads if x <= b)
        if sec != cur:
            rows.append([f"[{heads[sec]}, 第{b}小节]", []])
            cur = sec
        rows[-1][1].append(n["lyric"] or "-")
    body = "\n".join(f"{h} {' '.join(s)}" for h, s in rows)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# 每个音符一个字，'-' 表示接着唱上一个字（拖腔）。\n"
                 "# 粘贴时只复制方括号后面的部分，从该段第一个音符开始粘贴。\n"
                 + body + "\n")
