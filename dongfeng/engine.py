"""Engine for dongfeng/build.py: token parser, MusicXML writer, MIDI writer
and the playability checks.  build.py holds the notes; this file holds no
music.  Kept separate because 冬风 needs things the song build.py files do
not: sextuplets, triplets, several voices on one staff, clef changes, 8va
lines, bowing marks, tremolo and rolled chords.

Token syntax (one string per bar and part; 24 ticks = one quarter note, the
bar is alla breve = 96 ticks; "||" separates two voices on one staff):

  F6/4        sextuplet 16th (six to the beat)     C5/6    16th
  A4/8        triplet 8th (three to the beat)      A4/12   8th
  E4/18       dotted 8th                           E4/24   quarter
  E4/48       half                                 E4/96   whole
  A2+E3+A3/24 double / triple stop                 r/24    rest
  (  )        slur start / end (may be doubled)    ~       tie
  marks after the duration, in any order:
    >  accent      ^  marcato      .  staccato     _  tenuto
    %  fermata     A  rolled chord D  down-bow     U  up-bow
    T  tremolo (unmeasured, three strokes)       ,  breath mark (comma)
    !  staccatissimo (wedge)
  g:E1        grace note (acciaccatura) before the next note
"""
import re
import xml.etree.ElementTree as ET
from fractions import Fraction

import mido

Q = 24            # ticks per quarter in the token grammar
BAR = 96          # alla breve
MIDI_TPQ = 480
MT = MIDI_TPQ // Q

# ---------------------------------------------------------------------------
# Pitch helpers
# ---------------------------------------------------------------------------
_STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
_ALT = {"": 0, "#": 1, "##": 2, "b": -1, "bb": -2}
PIT = re.compile(r"^([A-G])(##|#|bb|b)?(-?\d)$")


def split_pitch(p):
    m = PIT.match(p)
    if not m:
        raise ValueError(f"bad pitch {p!r}")
    s, a, o = m.groups()
    return s, _ALT[a or ""], int(o)


def midi_of(p):
    s, a, o = split_pitch(p)
    return 12 * (o + 1) + _STEP[s] + a


def shift(p, octs):
    """Move a pitch name by whole octaves."""
    s, a, o = split_pitch(p)
    acc = {0: "", 1: "#", 2: "##", -1: "b", -2: "bb"}[a]
    return f"{s}{acc}{o + octs}"


def fit(p, lo, hi):
    """Octave-shift p until it lies in [lo, hi] (pitch names)."""
    lo_m, hi_m = midi_of(lo), midi_of(hi)
    while midi_of(p) < lo_m:
        p = shift(p, 1)
    while midi_of(p) > hi_m:
        p = shift(p, -1)
    return p


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
TOK = re.compile(
    r"^(?P<sl>\(*)(?P<p>r|[A-G][#b]*-?\d(?:\+[A-G][#b]*-?\d)*)/(?P<d>\d+)"
    r"(?P<m>[>^._%ADUT,!]*)(?P<tie>~?)(?P<sr>\)*)$")


def parse_voice(s, bar, voice):
    evs, pos, grace = [], 0, None
    for t in s.split():
        if t.startswith("g:"):
            grace = t[2:].split("+")
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"m{bar}: bad token {t!r}")
        d = int(m["d"])
        pit = None if m["p"] == "r" else m["p"].split("+")
        for x in pit or []:
            split_pitch(x)
        evs.append(dict(bar=bar, voice=voice, pos=pos, dur=d, pitches=pit,
                        tie=bool(m["tie"]), sl=len(m["sl"]), sr=len(m["sr"]),
                        marks=m["m"], grace=grace))
        grace = None
        pos += d
    if pos != BAR:
        raise ValueError(f"m{bar} voice {voice}: sums to {pos}, not {BAR}: {s!r}")
    return evs


def parse_part(data, nbars):
    """-> list of voices, each a list of events with absolute positions."""
    voices = {}
    for b in range(1, nbars + 1):
        chunks = data.get(b, f"r/{BAR}").split("||")
        for v, chunk in enumerate(chunks, 1):
            for e in parse_voice(chunk, b, v):
                e["abs"] = (b - 1) * BAR + e["pos"]
                voices.setdefault(v, []).append(e)
        for v in voices:
            if v > len(chunks):  # voice absent in this bar: hidden rest
                voices[v].append(dict(bar=b, voice=v, pos=0, dur=BAR,
                                      pitches=None, tie=False, sl=0, sr=0,
                                      marks="", grace=None, hidden=True,
                                      abs=(b - 1) * BAR))
    return voices


def all_events(voices):
    return sorted((e for v in voices.values() for e in v),
                  key=lambda e: (e["abs"], e["voice"]))


# ---------------------------------------------------------------------------
# Notation: split events into printable pieces
# ---------------------------------------------------------------------------
TYPES = {96: ("whole", 0), 72: ("half", 1), 48: ("half", 0),
         36: ("quarter", 1), 24: ("quarter", 0), 18: ("eighth", 1),
         12: ("eighth", 0), 9: ("16th", 1), 6: ("16th", 0), 3: ("32nd", 0)}
# inside a sextuplet beat (6:4) and a triplet beat (3:2)
SEXT = {4: ("16th", 0), 8: ("eighth", 0), 12: ("eighth", 1),
        16: ("quarter", 0), 2: ("32nd", 0)}
TRIP = {8: ("eighth", 0), 16: ("quarter", 0), 4: ("16th", 0)}
LEVELS = {"eighth": 1, "16th": 2, "32nd": 3}


def beat_kinds(events):
    """Tuplet kind of each beat of one voice: 'n', 's' (6:4), 't' (3:2)."""
    kinds = {}
    for e in events:
        for b in (e["pos"], e["pos"] + e["dur"]):
            k, off = divmod(b, Q)
            if off == 0 or k >= BAR // Q:
                continue
            kinds.setdefault(k, set()).add(off)
    out = {}
    for k in range(BAR // Q):
        offs = kinds.get(k, set())
        if offs <= {3, 6, 9, 12, 15, 18, 21}:
            out[k] = "n"
        elif offs <= {8, 16}:
            out[k] = "t"
        elif offs <= {4, 8, 12, 16, 20}:
            out[k] = "s"
        else:
            raise ValueError(f"beat {k + 1}: cannot notate offsets {sorted(offs)}")
    return out


def pieces_of(e, kinds):
    """[(pos, dur, type, dots, tuplet)] for one event."""
    out, pos, left = [], e["pos"], e["dur"]
    while left > 0:
        k, off = divmod(pos, Q)
        kind = kinds.get(k, "n")
        if kind in "st":
            table = SEXT if kind == "s" else TRIP
            room = Q - off
            d = next((x for x in sorted(table, reverse=True)
                      if x <= min(left, room)), None)
            if d is None or (d == Q):
                raise ValueError(f"m{e['bar']}: cannot notate {e}")
            t, dots = table[d]
            out.append((pos, d, t, dots, kind))
        else:
            if off == 0:
                cands = [x for x in (96, 72, 48, 36, 24, 18, 12, 6, 3)
                         if (x <= 24 or pos % 48 == 0) and
                         (x not in (96, 72) or pos == 0) and
                         (x != 36 or pos % 48 == 0) and
                         (x != 72 or e["pitches"] is not None)]
            elif off == 12:
                cands = [12, 6, 3]
            elif off in (6, 18):
                cands = [12, 6, 3] if off == 6 else [6, 3]
            else:
                cands = [3]
            d = next((x for x in cands if x <= left and
                      (x > 24 or off + x <= Q or off == 0)), None)
            if d is None:
                raise ValueError(f"m{e['bar']}: cannot notate {e}")
            t, dots = TYPES[d]
            out.append((pos, d, t, dots, None))
        pos += d
        left -= d
    return out


# ---------------------------------------------------------------------------
# MusicXML writer
# ---------------------------------------------------------------------------
ACC_NAME = {-2: "flat-flat", -1: "flat", 0: "natural", 1: "sharp",
            2: "double-sharp"}
DYN_TAGS = {"ppp", "pp", "p", "mp", "mf", "f", "ff", "fff", "fz", "sfz",
            "sf", "fp", "sfp", "rfz", "sffz"}
CLEFS = {"treble": ("G", 2), "alto": ("C", 3), "tenor": ("C", 4),
         "bass": ("F", 4)}


def _sub(parent, tag, text=None, **attrs):
    el = ET.SubElement(parent, tag, {k.replace("_", "-"): str(v)
                                     for k, v in attrs.items()})
    if text is not None:
        el.text = str(text)
    return el


class Spec:
    """Everything the writer needs beyond the notes."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def _accidentals(events, prev_state):
    """Decide which pitches print an accidental.  Returns
    {(id(event), pitch): alter-or-None} and the state to carry into the
    next bar (for courtesy accidentals)."""
    show = {}
    state = {}          # (step, octave) -> alter in force this bar
    step_alt = {}       # step -> set of alters seen this bar (any octave)
    for e in sorted(events, key=lambda e: e["pos"]):
        if not e["pitches"]:
            continue
        for p in e["pitches"]:
            s, a, o = split_pitch(p)
            if e.get("tied_in"):
                show[(id(e), p)] = None
                continue
            cur = state.get((s, o), 0)
            need = a != cur
            # courtesy: altered last bar in this octave, or another octave
            # of this step carries a different accidental earlier this bar
            if not need and a == 0 and (s, o) not in state:
                if prev_state.get((s, o), 0) != 0 or \
                        any(x != 0 for x in step_alt.get(s, ())):
                    need = True
            show[(id(e), p)] = a if need else None
            state[(s, o)] = a
            step_alt.setdefault(s, set()).add(a)
    return show, state


def _beams(notes):
    """notes: list of (piece-type or None for rest, grace) in one beam group.
    Returns list of {level: value}."""
    lv = [LEVELS.get(t, 0) if t else 0 for t in notes]
    out = [dict() for _ in notes]
    if sum(1 for x in lv if x) < 2:
        return out
    maxl = max(lv)
    for L in range(1, maxl + 1):
        i = 0
        while i < len(lv):
            if lv[i] >= L:
                j = i
                while j + 1 < len(lv) and lv[j + 1] >= L:
                    j += 1
                if j > i:
                    out[i][L] = "begin"
                    for k in range(i + 1, j):
                        out[k][L] = "continue"
                    out[j][L] = "end"
                elif L > 1:
                    # lone note at a deeper level: hook toward its neighbour
                    out[i][L] = "backward hook" if i > 0 and lv[i - 1] >= 1 \
                        and (i == len(lv) - 1 or lv[i + 1] < 1) else \
                        "forward hook"
                i = j + 1
            else:
                i += 1
    # level-1 beam must be continuous across the whole group
    return out


def write_musicxml(path, parts, parsed, spec):
    root = ET.Element("score-partwise", version="4.0")
    work = _sub(root, "work")
    _sub(work, "work-title", spec.title)
    _sub(root, "movement-title", spec.movement)
    ident = _sub(root, "identification")
    _sub(ident, "creator", spec.composer, type="composer")
    _sub(ident, "creator", spec.arranger, type="arranger")
    _sub(ident, "rights", spec.rights)
    enc = _sub(ident, "encoding")
    _sub(enc, "encoder", spec.engraver)
    _sub(enc, "software", "dongfeng/build.py")
    for el, v in (("accidental", "yes"), ("beam", "yes"), ("stem", "no")):
        _sub(enc, "supports", element=el, type=v)
    _sub(enc, "supports", element="print", attribute="new-system",
         type="yes", value="yes")
    defaults = _sub(root, "defaults")
    sc = _sub(defaults, "scaling")
    _sub(sc, "millimeters", "7.2")
    _sub(sc, "tenths", "40")
    pl = _sub(root, "part-list")
    group = len(parts) > 1
    if group:
        _sub(pl, "part-group", type="start", number="1").extend([
            _el("group-name", spec.group_name),
            _el("group-symbol", "bracket"), _el("group-barline", "yes")])
    for i, p in enumerate(parts, 1):
        sp = _sub(pl, "score-part", id=f"P{i}")
        _sub(sp, "part-name", p["name"])
        _sub(sp, "part-abbreviation", p["abbr"])
        si = _sub(sp, "score-instrument", id=f"P{i}-I1")
        _sub(si, "instrument-name", p["iname"])
        _sub(si, "instrument-sound", p["sound"])
        mi = _sub(sp, "midi-instrument", id=f"P{i}-I1")
        _sub(mi, "midi-channel", i)
        _sub(mi, "midi-program", p["program"] + 1)
        _sub(mi, "volume", 80)
        _sub(mi, "pan", p.get("pan", 0))
    if group:
        _sub(pl, "part-group", type="stop", number="1")

    for i, p in enumerate(parts, 1):
        part_el = _sub(root, "part", id=f"P{i}")
        _write_part(part_el, p, parsed[p["id"]], spec, top=(i == 1))
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="UTF-8", xml_declaration=True)
    xml = open(path, encoding="utf-8").read()
    xml = xml.replace(
        "?>\n", "?>\n<!DOCTYPE score-partwise PUBLIC \"-//Recordare//DTD "
        "MusicXML 4.0 Partwise//EN\" "
        "\"http://www.musicxml.org/dtds/partwise.dtd\">\n", 1)
    open(path, "w", encoding="utf-8").write(xml)


def _el(tag, text=None, **attrs):
    el = ET.Element(tag, {k.replace("_", "-"): str(v) for k, v in attrs.items()})
    if text is not None:
        el.text = str(text)
    return el


def _direction(kind, payload, placement=None):
    d = _el("direction")
    if placement:
        d.set("placement", placement)
    if kind == "dyn":
        marks = payload.split()
        dt = _sub(d, "direction-type")
        dy = _sub(dt, "dynamics")
        if marks[0] in DYN_TAGS:
            _sub(dy, marks[0])
            rest = " ".join(marks[1:])
        else:
            _sub(dy, "other-dynamics", marks[0])
            rest = " ".join(marks[1:])
        if rest:
            dt2 = _sub(d, "direction-type")
            _sub(dt2, "words", rest, font_style="italic")
    elif kind == "words":
        dt = _sub(d, "direction-type")
        _sub(dt, "words", payload, font_style="italic")
    elif kind == "title":
        dt = _sub(d, "direction-type")
        _sub(dt, "words", payload, font_weight="bold", font_size="12")
    elif kind == "rehearsal":
        dt = _sub(d, "direction-type")
        _sub(dt, "rehearsal", payload, font_weight="bold")
    elif kind == "tempo":
        words, unit, num, qbpm = payload
        if words:
            dt = _sub(d, "direction-type")
            _sub(dt, "words", words + (" " if unit else ""),
                 font_weight="bold")
        if unit:
            dt = _sub(d, "direction-type")
            mm = _sub(dt, "metronome", parentheses="no")
            _sub(mm, "beat-unit", unit)
            _sub(mm, "per-minute", num)
        if qbpm:
            _sub(d, "sound", tempo=qbpm)
    elif kind == "tempotext":
        dt = _sub(d, "direction-type")
        _sub(dt, "words", payload, font_style="italic", font_weight="bold")
    elif kind == "wedge":
        typ, num = payload
        dt = _sub(d, "direction-type")
        _sub(dt, "wedge", type=typ, number=num)
    elif kind == "ottava":
        typ = payload
        dt = _sub(d, "direction-type")
        if typ == "start":
            _sub(dt, "octave-shift", type="down", size="8", number="1")
        else:
            _sub(dt, "octave-shift", type="stop", size="8", number="1")
    return d


def _with_offset(de, off):
    if off:
        el = _el("offset", off)
        snd = de.find("sound")
        if snd is not None:
            de.insert(list(de).index(snd), el)
        else:
            de.append(el)
    return de


# same tick: a part's own words first, so MS4 sets them nearest the staff,
# under the rehearsal letter, section title and tempo of the top part
ORDER = {"words": -1, "rehearsal": 0, "title": 1, "tempo": 2, "tempotext": 3,
         "ottava": 4, "dyn": 5, "wedge": 7}


def _write_part(part_el, p, voices, spec, top):
    pid = p["id"]
    nb = spec.nbars
    # directions per bar: (tick, kind, payload, placement)
    dirs = {}

    def add(b, t, kind, payload, placement=None):
        dirs.setdefault(b, []).append((t, kind, payload, placement))

    evs_all = all_events(voices)
    starts = sorted({e["abs"] for e in evs_all if e["pitches"]})

    def next_start(a, limit=None):
        for s in starts:
            if s >= a and (limit is None or s < limit):
                return s
        return None

    # dynamics: moved to the part's next entrance if it rests there
    dl = sorted(x for x in spec.dyn.get(pid, []) if not x[2].startswith("="))
    for i, (b, t, mark) in enumerate(dl):
        a = (b - 1) * BAR + t
        lim = ((dl[i + 1][0] - 1) * BAR + dl[i + 1][1]) if i + 1 < len(dl) \
            else None
        s = next_start(a, lim)
        if s is None:
            continue
        add(s // BAR + 1, s % BAR, "dyn", mark, "below")
    for (b, t, b2, t2, kind) in spec.hair.get(pid, []):
        if kind.endswith("-"):  # MIDI only
            continue
        n = 1
        add(b, t, "wedge", ("crescendo" if kind == "cresc" else "diminuendo",
                            n), "below")
        add(b2, t2, "wedge", ("stop", n), "below")
    for (b, t, txt) in spec.words.get(pid, []):
        below = re.match(r"(cresc|dim|decresc|poco|sempre|molto|pi\u00f9|"
                         r"meno|subito|smorz|morendo|calando)", txt)
        if txt.startswith("_"):  # "_text": below the staff
            txt, below = txt[1:], True
        add(b, t, "words", txt, "below" if below else "above")
    # bars where an 8va line starts or stops mid-bar: MS4 decides the
    # accidentals by written position, so it drops one this engine writes
    # for another octave (Ab6 inside the line, Ab5 after it)
    ott_bars = set()
    for (b, t, b2, t2) in spec.ottava.get(pid, []):
        add(b, t, "ottava", "start", "above")
        add(b2, t2, "ottava", "stop", "above")
        if t:
            ott_bars.add(b)
        if t2 < BAR:
            ott_bars.add(b2)
    if top:
        for (b, letter, title) in spec.sections:
            if letter:
                add(b, 0, "rehearsal", letter, "above")
            add(b, 0, "title", title, "above")
        for (b, t, words, unit, num, qbpm) in spec.tempo_marks:
            add(b, t, "tempo", (words, unit, num, qbpm), "above")
        for (b, t, words) in spec.tempo_words:
            add(b, t, "tempotext", words, "above")
    clefs = {}
    for (b, t, c) in spec.clefs.get(pid, []):
        clefs.setdefault(b, []).append((t, c))

    prev_state = {}
    # mark tied-in events (accidental suppression)
    for v in voices.values():
        for a, b in zip(v, v[1:]):
            if a["tie"] and a["pitches"] and b["pitches"]:
                b["tied_in"] = True
    slur_num = {}
    tuplet_run = {}  # voice -> previous beat was the same tuplet kind
    for b in range(1, nb + 1):
        m = _sub(part_el, "measure", number=b)
        if b > 1 and b in spec.page_breaks:
            _sub(m, "print", new_page="yes")
        elif b > 1 and b in spec.system_breaks:
            _sub(m, "print", new_system="yes")
        if b == 1:
            at = _sub(m, "attributes")
            _sub(at, "divisions", Q)
            k = _sub(at, "key")
            _sub(k, "fifths", 0)
            _sub(k, "mode", "minor")
            ti = _sub(at, "time", symbol="cut")
            _sub(ti, "beats", 2)
            _sub(ti, "beat-type", 2)
            cl = _sub(at, "clef")
            sign, line = CLEFS[p["clef"]]
            _sub(cl, "sign", sign)
            _sub(cl, "line", line)
        bar_evs = [e for e in evs_all if e["bar"] == b]
        show, prev_state = _accidentals(bar_evs, prev_state)
        bdirs = sorted(dirs.get(b, []), key=lambda x: (x[0], ORDER[x[1]]))
        bclefs = sorted(clefs.get(b, []))
        vids = sorted(voices)
        for vi, v in enumerate(vids):
            vevs = [e for e in voices[v] if e["bar"] == b]
            if vi > 0:
                bk = _sub(m, "backup")
                _sub(bk, "duration", BAR)
            multi = sum(1 for vv in vids if not all(
                ee.get("hidden") for ee in voices[vv] if ee["bar"] == b)) > 1
            for ee in vevs:
                ee["multi"] = multi
                ee["ott_bar"] = b in ott_bars
            if all(e.get("hidden") for e in vevs):
                fw = _sub(m, "forward")
                _sub(fw, "duration", BAR)
                _sub(fw, "voice", v)
                continue
            kinds = beat_kinds(vevs)
            # pieces
            plist = []
            for e in vevs:
                ps = pieces_of(e, kinds)
                for j, pc in enumerate(ps):
                    plist.append((e, j, len(ps), pc))
            # beam groups: per beat, or per half for plain eighths
            groups = {}
            for idx, (e, j, n, pc) in enumerate(plist):
                pos, d, t, dots, tup = pc
                beamable = t in LEVELS and e["pitches"] is not None
                g = pos // Q
                groups.setdefault(g, []).append((idx, t if beamable else None))
            # plain-eighth halves: join the two beats
            beaminfo = {}
            for half in (0, 1):
                g0, g1 = groups.get(2 * half, []), groups.get(2 * half + 1, [])
                joined = g0 + g1
                if joined and all(t == "eighth" for _, t in joined) and \
                        len(joined) == 4 and kinds.get(2 * half) == "n" and \
                        kinds.get(2 * half + 1) == "n":
                    gl = [joined]
                else:
                    gl = [g0, g1]
                for grp in gl:
                    # split at rests / unbeamable notes
                    run = []
                    for idx, t in grp + [(None, None)]:
                        if t is None:
                            if len(run) > 1:
                                bs = _beams([tt for _, tt in run])
                                for (ii, _), bb in zip(run, bs):
                                    beaminfo[ii] = bb
                            run = []
                        else:
                            run.append((idx, t))
            # tuplet brackets per beat
            tup_first, tup_last = {}, {}
            for idx, (e, j, n, pc) in enumerate(plist):
                pos, d, t, dots, tup = pc
                if tup:
                    g = pos // Q
                    tup_first.setdefault(g, idx)
                    tup_last[g] = idx
            shown = {}
            for g in range(BAR // Q):
                if g in tup_first:
                    unit = 4 if kinds[g] == "s" else 8
                    uniform = all(pc[1] == unit and ee["pitches"]
                                  for ee, _, _, pc in plist if pc[0] // Q == g)
                    shown[g] = tuplet_run.get(v) != kinds[g] or not uniform
                    tuplet_run[v] = kinds[g] if uniform else None
                else:
                    tuplet_run[v] = None
            # emit
            cur = 0
            for idx, (e, j, n, pc) in enumerate(plist):
                pos, d, t, dots, tup = pc
                if vi == 0:
                    for (ct, c) in list(bclefs):
                        if ct <= pos:
                            at = _sub(m, "attributes")
                            cl = _sub(at, "clef")
                            sign, line = CLEFS[c]
                            _sub(cl, "sign", sign)
                            _sub(cl, "line", line)
                            bclefs.remove((ct, c))
                    while bdirs and bdirs[0][0] < pos + d and (
                            bdirs[0][0] <= pos or j == 0 or True):
                        dt, kind, payload, plc = bdirs[0]
                        if dt > pos and idx + 1 < len(plist) and \
                                plist[idx + 1][3][0] <= dt:
                            break
                        bdirs.pop(0)
                        m.append(_with_offset(_direction(kind, payload, plc),
                                              dt - pos))
                _emit_note(m, e, j, n, pc, v, show, beaminfo.get(idx, {}),
                           tup_first, tup_last, idx, shown, kinds, slur_num)
                cur = pos + d
            if vi == 0:
                for dt, kind, payload, plc in bdirs:
                    m.append(_with_offset(_direction(kind, payload, plc),
                                          dt - cur))
                bdirs = []
        if b == nb:
            bl = _sub(m, "barline", location="right")
            _sub(bl, "bar-style", "light-heavy")
        elif b in spec.double_bars:
            bl = _sub(m, "barline", location="right")
            _sub(bl, "bar-style", "light-light")


def _emit_note(m, e, j, n, pc, v, show, beams, tup_first, tup_last, idx,
               shown, kinds, slur_num):
    pos, d, t, dots, tup = pc
    first, last = j == 0, j == n - 1
    pitches = e["pitches"]
    if first and e["grace"] and pitches:
        for gi, gp in enumerate(e["grace"]):
            ne = _sub(m, "note")
            _sub(ne, "grace", slash="yes")
            if gi:
                _sub(ne, "chord")
            s, a, o = split_pitch(gp)
            pe = _sub(ne, "pitch")
            _sub(pe, "step", s)
            if a:
                _sub(pe, "alter", a)
            _sub(pe, "octave", o)
            _sub(ne, "voice", v)
            _sub(ne, "type", "eighth")
            if a:
                _sub(ne, "accidental", ACC_NAME[a])
    if pitches is None:
        ne = _sub(m, "note")
        if d == BAR and pos == 0:
            _sub(ne, "rest", measure="yes")
        else:
            _sub(ne, "rest")
        _sub(ne, "duration", d)
        _sub(ne, "voice", v)
        if not (d == BAR and pos == 0):
            _sub(ne, "type", t)
            for _ in range(dots):
                _sub(ne, "dot")
        _tm(ne, tup, d)
        nots = _el("notations")
        _tuplet_notation(nots, tup, idx, tup_first, tup_last, pos, shown)
        if "%" in e["marks"] and last:
            _sub(nots, "fermata", type="upright")
        if len(nots):
            ne.append(nots)
        return
    tie_in = (not first) or e.get("tied_in")
    tie_out = (not last) or e["tie"]
    for pi, p in enumerate(pitches):
        ne = _sub(m, "note")
        if pi:
            _sub(ne, "chord")
        s, a, o = split_pitch(p)
        pe = _sub(ne, "pitch")
        _sub(pe, "step", s)
        if a:
            _sub(pe, "alter", a)
        _sub(pe, "octave", o)
        _sub(ne, "duration", d)
        if tie_in:
            _sub(ne, "tie", type="stop")
        if tie_out:
            _sub(ne, "tie", type="start")
        _sub(ne, "voice", v)
        _sub(ne, "type", t)
        for _ in range(dots):
            _sub(ne, "dot")
        if first:
            acc = show.get((id(e), p))
            if acc is not None:
                ael = _sub(ne, "accidental", ACC_NAME[acc])
                if e.get("ott_bar"):  # kept as written (see ott_bars);
                    ael.set("cautionary", "yes")  # MS4 keeps it, and without
                    ael.set("parentheses", "no")  # this prints it as (#)
        _tm(ne, tup, d)
        if pi == 0:
            for lvl in sorted(beams):
                _sub(ne, "beam", beams[lvl], number=lvl)
        nots = _el("notations")
        if tie_in:
            _sub(nots, "tied", type="stop")
        if tie_out:
            _sub(nots, "tied", type="start")
        if pi == 0:
            if first:
                for _ in range(e["sl"]):
                    k = 1
                    while slur_num.get((v, k)):
                        k += 1
                    slur_num[(v, k)] = True
                    # two voices: slurs above / below; one voice: let the
                    # notation program put them on the notehead side, clear
                    # of the tuplet numbers on the beam side
                    el = _sub(nots, "slur", type="start", number=k)
                    if e.get("multi"):
                        el.set("placement", "above" if v == 1 else "below")
            if last:
                for _ in range(e["sr"]):
                    open_ = [k for (vv, k), on in slur_num.items()
                             if vv == v and on]
                    if open_:
                        k = max(open_)
                        slur_num[(v, k)] = False
                        _sub(nots, "slur", type="stop", number=k)
            _tuplet_notation(nots, tup, idx, tup_first, tup_last, pos, shown)
            mk = e["marks"]
            arts = _el("articulations")
            if first:
                # MS4 stacks them in this order from the notehead out:
                # staccato / tenuto / wedge inside, accents outside
                for c, tag in ((".", "staccato"), ("_", "tenuto"),
                               ("!", "staccatissimo"), (">", "accent"),
                               ("^", "strong-accent")):
                    if c in mk:
                        el = _sub(arts, tag)
                        if tag == "strong-accent":
                            el.set("type", "up")
            if last and "," in mk:
                _sub(arts, "breath-mark")
            if len(arts):
                nots.append(arts)
            if first:
                tech = _el("technical")
                if "D" in mk:
                    _sub(tech, "down-bow")
                if "U" in mk:
                    _sub(tech, "up-bow")
                if len(tech):
                    nots.append(tech)
            if "T" in mk:
                orn = _sub(nots, "ornaments")
                _sub(orn, "tremolo", "3", type="single")
            if "%" in mk and last:
                _sub(nots, "fermata", type="upright")
        if "A" in e["marks"] and first:
            _sub(nots, "arpeggiate")
        if len(nots):
            ne.append(nots)


def _tm(ne, tup, d):
    if not tup:
        return
    tm = _sub(ne, "time-modification")
    if tup == "s":
        _sub(tm, "actual-notes", 6)
        _sub(tm, "normal-notes", 4)
    else:
        _sub(tm, "actual-notes", 3)
        _sub(tm, "normal-notes", 2)
    # move time-modification before any stem/beam (schema order)


def _tuplet_notation(nots, tup, idx, tup_first, tup_last, pos, shown):
    if not tup:
        return
    g = pos // Q
    if tup_first.get(g) == idx:
        el = _sub(nots, "tuplet", type="start", number=1, bracket="no")
        el.set("show-number", "actual" if shown.get(g) else "none")
    if tup_last.get(g) == idx:
        _sub(nots, "tuplet", type="stop", number=1)


# ---------------------------------------------------------------------------
# MIDI
# ---------------------------------------------------------------------------
VEL = {"ppp": 26, "pp": 36, "p": 48, "mp": 60, "mf": 72, "f": 88, "ff": 102,
       "fff": 114}


def dyn_curve(spec, pid, nticks):
    marks = []
    for b, t, mark in spec.dyn.get(pid, []):
        w = mark.lstrip("=").split()[0]
        if w in VEL:
            marks.append(((b - 1) * BAR + t, VEL[w]))
        elif w in ("fp", "sfp"):
            marks.append(((b - 1) * BAR + t, VEL["p"]))
    marks.sort()
    v = [marks[0][1] if marks else VEL["mf"]] * nticks
    for i, (a, val) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else nticks
        for t in range(a, min(end, nticks)):
            v[t] = val
    for b, t, b2, t2, kind in spec.hair.get(pid, []):
        a = (b - 1) * BAR + t
        z = min((b2 - 1) * BAR + t2, nticks - 1)
        v0 = v[a]
        nxt = [val for tt, val in marks if tt > z]
        kind = kind.rstrip("-")
        v1 = nxt[0] if nxt and nxt[0] != v0 else v0 + (-16 if kind == "dim" else 16)
        if kind == "cresc" and v1 <= v0:
            v1 = v0 + 14
        if kind == "dim" and v1 >= v0:
            v1 = v0 - 14
        for tt in range(a, z + 1):
            v[tt] = round(v0 + (v1 - v0) * (tt - a) / max(1, z - a))
    return v


def merged(voices):
    """Tied notes merged, per voice; each note: start, dur, pitches, marks,
    grace, slurred (inside a slur), first-of-tie event."""
    out = []
    for v, evs in voices.items():
        cur, depth = None, 0
        for e in evs:
            if e["pitches"] is None:
                cur = None
                depth = max(0, depth + e["sl"] - e["sr"])
                continue
            depth = max(0, depth + e["sl"] - e["sr"])
            if cur is not None and cur["tie"] and \
                    cur["pitches"] == e["pitches"]:
                cur["dur"] += e["dur"]
                cur["tie"] = e["tie"]
                cur["marks"] += e["marks"].replace(">", "").replace("^", "")
                continue
            cur = dict(start=e["abs"], dur=e["dur"], pitches=e["pitches"],
                       marks=e["marks"], grace=e["grace"], tie=e["tie"],
                       slurred=depth > 0,
                       voice=v, bar=e["bar"])
            out.append(cur)
    out.sort(key=lambda n: (n["start"], n["voice"]))
    return out


def part_track(p, voices, spec, ch, nticks, with_cc=True):
    notes = merged(voices)
    vel = dyn_curve(spec, p["id"], nticks)
    accents = {}
    for b, t, mark in spec.dyn.get(p["id"], []):
        w = mark.lstrip("=").split()[0]
        if w in ("fz", "sfz", "sf", "rfz", "sffz", "fp", "sfp"):
            accents[(b - 1) * BAR + t] = 22
    ab = [(0, 0, mido.MetaMessage("track_name", name=p["name"])),
          (0, 1, mido.Message("program_change", channel=ch,
                              program=p["program"]))]
    if with_cc:
        last = None
        for t in range(0, nticks, 4):
            val = min(127, 16 + vel[t])
            if val != last:
                ab.append((t * MT, 2, mido.Message("control_change", channel=ch,
                                                   control=11, value=val)))
                ab.append((t * MT, 2, mido.Message("control_change", channel=ch,
                                                   control=1, value=val)))
                last = val
    prog = p["program"]
    for bb, tt, prg in spec.programs.get(p["id"], []):
        ab.append((((bb - 1) * BAR + tt) * MT, 1,
                   mido.Message("program_change", channel=ch, program=prg)))
    by_voice = {}
    for n in notes:
        by_voice.setdefault(n["voice"], []).append(n)
    for vn, vnotes in by_voice.items():
        for i, n in enumerate(vnotes):
            on = n["start"] * MT
            off = (n["start"] + n["dur"]) * MT
            nxt = vnotes[i + 1] if i + 1 < len(vnotes) else None
            mk = n["marks"]
            if "." in mk or "!" in mk:
                off = on + max(3 * MT, (n["dur"] * MT) // (3 if "!" in mk else 2))
            elif nxt and nxt["start"] * MT == off:
                if set(nxt["pitches"]) & set(n["pitches"]):
                    off -= min(24, (n["dur"] * MT) // 4)
                elif not n["slurred"]:
                    off -= min(20, (n["dur"] * MT) // 6)
            else:
                off -= min(30, (n["dur"] * MT) // 8)
            v = vel[min(n["start"], nticks - 1)]
            if ">" in mk:
                v += 12
            if "^" in mk:
                v += 18
            v += accents.get(n["start"], 0)
            v = max(1, min(127, v))
            if n["grace"]:
                g_on = on
                for gp in n["grace"]:
                    ab.append((g_on, 5, mido.Message("note_on", channel=ch,
                                                     note=midi_of(gp), velocity=v)))
                    ab.append((g_on + 2 * MT, 3, mido.Message(
                        "note_off", channel=ch, note=midi_of(gp), velocity=0)))
                on += 2 * MT
            pits = [midi_of(x) for x in n["pitches"]]
            if "T" in mk:  # unmeasured tremolo: repeated 32nds
                t0 = on
                step = 3 * MT
                while t0 < off - 2:
                    t1 = min(off, t0 + step)
                    for pm in pits:
                        ab.append((t0, 5, mido.Message("note_on", channel=ch,
                                                       note=pm, velocity=v)))
                        ab.append((t1 - 4, 3, mido.Message(
                            "note_off", channel=ch, note=pm, velocity=0)))
                    t0 = t1
                continue
            roll = "A" in mk
            for k, pm in enumerate(sorted(pits)):
                o = on + (k * 2 * MT if roll else 0)
                ab.append((o, 5, mido.Message("note_on", channel=ch, note=pm,
                                              velocity=v)))
                ab.append((max(o + 10, off), 3, mido.Message(
                    "note_off", channel=ch, note=pm, velocity=0)))
    ab.sort(key=lambda x: (x[0], x[1]))
    tr, last = mido.MidiTrack(), 0
    for t, _, msg in ab:
        tr.append(msg.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def tempo_track(spec, title):
    ab = [(0, mido.MetaMessage("track_name", name=title)),
          (0, mido.MetaMessage("time_signature", numerator=2, denominator=2)),
          (0, mido.MetaMessage("key_signature", key="Am"))]
    for b, t, bpm in spec.tempi:
        ab.append((((b - 1) * BAR + t) * MT,
                   mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(bpm))))
    for b, letter, title_ in spec.sections:
        ab.append(((b - 1) * BAR * MT, mido.MetaMessage(
            "marker", text=(letter + " " if letter else "") + title_.split()[0])))
    ab.sort(key=lambda x: x[0])
    tr, last = mido.MidiTrack(), 0
    for t, msg in ab:
        tr.append(msg.copy(time=t - last))
        last = t
    tr.append(mido.MetaMessage("end_of_track", time=0))
    return tr


def write_midi(path, parts, parsed, spec, title, ids=None, with_cc=True):
    nticks = spec.nbars * BAR
    mf = mido.MidiFile(type=1, ticks_per_beat=MIDI_TPQ)
    mf.tracks.append(tempo_track(spec, title))
    for ch, p in enumerate(parts):
        if ids and p["id"] not in ids:
            continue
        mf.tracks.append(part_track(p, parsed[p["id"]], spec, ch, nticks,
                                    with_cc))
    mf.save(path)


def seconds(spec, abs_tick):
    marks = [((b - 1) * BAR + t, bpm) for b, t, bpm in spec.tempi]
    tot = 0.0
    for i, (a, bpm) in enumerate(marks):
        if abs_tick <= a:
            break
        end = marks[i + 1][0] if i + 1 < len(marks) else abs_tick
        tot += (min(abs_tick, end) - a) / Q * 60.0 / bpm
    return tot


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
STRINGS = {"vn": ["G3", "D4", "A4", "E5"], "va": ["C3", "G3", "D4", "A4"],
           "vc": ["C2", "G2", "D3", "A3"]}
# widest distance (semitones) the left hand spans between two stopped notes
# on neighbouring strings, measured along the strings
SPAN = {"vn": 5, "va": 4, "vc": 4}


def stop_ok(fam, pitches):
    """Can this double / triple / quadruple stop be played?  Tries every
    assignment of the notes to adjacent strings."""
    ms = sorted(midi_of(x) for x in pitches)
    opens = [midi_of(x) for x in STRINGS[fam]]
    n = len(ms)
    if n == 1:
        return True
    if n > 4:
        return False
    for first in range(0, 5 - n):
        strs = list(range(first, first + n))
        offs = [ms[k] - opens[strs[k]] for k in range(n)]
        if any(o < 0 for o in offs):
            continue
        stopped = [o for o in offs if o > 0]
        if len(stopped) <= 1:
            if not stopped or stopped[0] <= 14:
                return True
            continue
        if max(stopped) - min(stopped) <= SPAN[fam] and max(stopped) <= 14:
            return True
    return False


def check_part(pid, fam, rng, voices, fast_rng=None):
    out = []
    lo, hi = (midi_of(x) for x in rng)
    for v, evs in voices.items():
        for a_, b_ in zip(evs, evs[1:]):
            if a_["tie"] and a_["pitches"] and b_["pitches"] != a_["pitches"]:
                out.append(f"TIE {pid} m{a_['bar']} {'+'.join(a_['pitches'])} "
                           f"-> {'+'.join(b_['pitches'] or ['rest'])}")
        prev = None
        for e in evs:
            if not e["pitches"]:
                prev = None
                continue
            for x in e["pitches"]:
                mm = midi_of(x)
                if not lo <= mm <= hi:
                    out.append(f"RANGE {pid} m{e['bar']} {x}")
                elif fast_rng and e["dur"] <= 4 and mm > midi_of(fast_rng):
                    out.append(f"HIGH {pid} m{e['bar']} {x} in a fast run")
            if len(e["pitches"]) > 1 and not stop_ok(fam, e["pitches"]):
                out.append(f"DSTOP {pid} m{e['bar']} {'+'.join(e['pitches'])}")
            if prev is not None and e["dur"] <= 4 and prev["dur"] <= 4 and \
                    len(e["pitches"]) == 1 and len(prev["pitches"]) == 1:
                iv = abs(midi_of(e["pitches"][0]) - midi_of(prev["pitches"][0]))
                if iv > 16:
                    out.append(f"LEAP {pid} m{e['bar']} "
                               f"{prev['pitches'][0]}->{e['pitches'][0]}")
            prev = e
    return out
