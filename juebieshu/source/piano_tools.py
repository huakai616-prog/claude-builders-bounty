#!/usr/bin/env python3
"""诀别书 钢琴原谱转写工具

The piano chart (三页截图) is transcribed into JSON, one object per bar:

  {"bar": 17,
   "rh": ["F6+D6/8~ D6+F6/2 ...", "optional second voice"],
   "lh": ["G1+G2/4 ...", "optional second voice"],
   "lh_clef": "bass",                 # or "treble", or [["treble",0],["bass",12]]
   "rh_ottava": 0,                    # 1 = the bar is under an 8va bracket
   "marks": ["rit."],                 # tempo / expression words, dynamics
   "harmony": ["Gm7", "Gm7"],         # one chord per half bar
   "doubts": "free text"}

Token syntax (durations in 16th notes, each voice sums to 16):
  C5/2        eighth note        D4+F4/8   chord (half note)
  r/4         quarter rest       A4/1~     tie into the next note
  F5/1>       accent             F5/2*     staccato
  C5+E5/4$    arpeggiated chord  g:G4      grace note before the next note
  (G4/1 A4/1) slur start / end
Pitches are the notated pitch (under 8va: as printed), with the real
accidental (B in F major is Bb).

Usage:
  python3 piano_tools.py check FILE.json            # bar sums, token syntax
  python3 piano_tools.py render FILE.json OUT.png [FIRST LAST]
"""
import json
import os
import re
import subprocess
import sys
import tempfile

BAR16 = 16
# bars that start a system in the original chart
SYSTEM_STARTS = (1, 5, 10, 14, 18, 23, 28, 34, 39, 43, 47)

TOK = re.compile(
    r"^(\()?((?:[A-G][#b]{0,2}\d)(?:\+[A-G][#b]{0,2}\d)*|r)/(\d+)"
    r"([>*$~]*)(\))?$")


def parse_voice(s):
    evs, pos, grace = [], 0, None
    for t in s.split():
        if t.startswith("g:"):
            grace = t[2:]
            continue
        m = TOK.match(t)
        if not m:
            raise ValueError(f"bad token {t!r}")
        sl, pit, dur, flags, sr = m.groups()
        dur = int(dur)
        if dur <= 0:
            raise ValueError(f"bad duration in {t!r}")
        evs.append(dict(pos=pos, dur=dur,
                        pitches=None if pit == "r" else pit.split("+"),
                        tie="~" in flags, accent=">" in flags,
                        stacc="*" in flags, arp="$" in flags,
                        slur_start=bool(sl), slur_end=bool(sr),
                        grace=grace))
        grace = None
        pos += dur
    if pos != BAR16:
        raise ValueError(f"voice sums to {pos} sixteenths, not 16: {s!r}")
    return evs


def ottava_shift(b, pos):
    """Semitones to add to a printed RH pitch at 16th `pos` of bar b to get
    the sounding pitch (8va bracket; it may end inside the bar at
    rh_ottava_until)."""
    if not b.get("rh_ottava"):
        return 0
    return 12 if pos < b.get("rh_ottava_until", 16) else 0


def check(bars):
    errs = []
    seen = set()
    for b in bars:
        n = b.get("bar")
        seen.add(n)
        for staff in ("rh", "lh"):
            vs = b.get(staff) or []
            if not vs:
                errs.append(f"m{n} {staff}: no voices")
            for i, v in enumerate(vs):
                try:
                    parse_voice(v)
                except ValueError as e:
                    errs.append(f"m{n} {staff} v{i + 1}: {e}")
    return errs


# ---------------------------------------------------------------------------
# LilyPond rendering (for comparing a transcription with the chart)
# ---------------------------------------------------------------------------
LY_DUR = {1: "16", 2: "8", 3: "8.", 4: "4", 6: "4.", 8: "2", 12: "2.",
          16: "1"}


def split_dur(pos, dur):
    pieces = []
    while dur > 0:
        if pos % 4 == 0:
            allowed = {0: [16, 12, 8, 6, 4, 3, 2, 1],
                       8: [8, 6, 4, 3, 2, 1]}.get(pos, [4, 3, 2, 1])
            if pos == 4:
                allowed = [8, 6, 4, 3, 2, 1] if dur >= 8 else [4, 3, 2, 1]
        elif pos % 4 == 2:
            allowed = [6, 4, 2, 1] if pos in (2, 10) else [2, 1]
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


def ly_pitch(p, shift=0):
    s, acc, o = re.fullmatch(r"([A-G])([#b]{0,2})(-?\d)", p).groups()
    o = int(o) + shift // 12
    accs = {"": "", "#": "is", "##": "isis", "b": "es", "bb": "eses"}[acc]
    return (s.lower() + accs
            + ("'" * (o - 3) if o >= 3 else "," * (3 - o)))


def ly_voice_bar(s, clef_changes=None, bar=None, emit_ottava=True):
    """bar: the transcription bar (for 8va). LilyPond's \\ottava wants the
    sounding pitch, so 8va notes are written an octave up here."""
    toks = []
    clef_changes = dict(clef_changes or {})
    ott_end = bar.get("rh_ottava_until", 16) if bar and \
        bar.get("rh_ottava") else None
    for e in parse_voice(s):
        if e["pos"] in clef_changes:
            toks.append(f"\\clef {clef_changes.pop(e['pos'])}")
        if emit_ottava and ott_end is not None and ott_end < 16 and \
                e["pos"] == ott_end:
            toks.append("\\ottava #0")
        sh = ottava_shift(bar, e["pos"]) if bar else 0
        if e["grace"]:
            toks.append(f"\\slashedGrace {{ {ly_pitch(e['grace'], sh)}16 }}")
        pieces = (split_rest if e["pitches"] is None else split_dur)(
            e["pos"], e["dur"])
        for i, d in enumerate(pieces):
            first, last = i == 0, i == len(pieces) - 1
            if e["pitches"] is None:
                toks.append("r" + LY_DUR[d])
                continue
            ps = [ly_pitch(x, sh) for x in e["pitches"]]
            t = ps[0] if len(ps) == 1 else "<" + " ".join(ps) + ">"
            t += LY_DUR[d]
            if first and e["arp"]:
                t += "\\arpeggio"
            if not last or e["tie"]:
                t += "~"
            if first and e["accent"]:
                t += "->"
            if first and e["stacc"]:
                t += "-."
            if first and e["slur_start"]:
                t += "("
            if last and e["slur_end"]:
                t += ")"
            toks.append(t)
    for pos, c in sorted(clef_changes.items()):
        toks.append(f"\\clef {c}")
    return " ".join(toks)


def clef_list(b):
    c = b.get("lh_clef", "bass")
    if isinstance(c, str):
        return [[c, 0]]
    return c


def build_ly(bars, first, last):
    bars = [b for b in bars if first <= b["bar"] <= last]
    bars.sort(key=lambda b: b["bar"])
    nrh = max(len(b["rh"]) for b in bars)
    nlh = max(len(b["lh"]) for b in bars)
    rh = [[] for _ in range(nrh)]
    lh = [[] for _ in range(nlh)]
    cur_clef = None
    ott = 0
    for b in bars:
        n = b["bar"]
        brk = "\\break " if n in SYSTEM_STARTS and n != first else ""
        o = b.get("rh_ottava", 0)
        pre = ""
        if o != ott:
            pre = f"\\ottava #{o} "
            ott = o
        if o and b.get("rh_ottava_until", 16) < 16:
            ott = 0          # the bracket ends inside this bar
        for i in range(nrh):
            src = b["rh"][i] if i < len(b["rh"]) else None
            body = ly_voice_bar(src, bar=b, emit_ottava=i == 0) \
                if src else "s1"
            rh[i].append((brk if i == 0 else "") + (pre if i == 0 else "")
                         + body + " |")
        clefs = clef_list(b)
        changes = {}
        for c, pos in clefs:
            if c != cur_clef:
                changes[pos] = c
                cur_clef = c
        for i in range(nlh):
            src = b["lh"][i] if i < len(b["lh"]) else None
            ch = changes if i == 0 else None
            if src:
                body = ly_voice_bar(src, ch)
            else:
                body = "s1"
            lh[i].append(body + " |")
    if ott:
        rh[0].append("\\ottava #0")

    def staff(voices, name):
        if len(voices) == 1:
            return "{ " + "\n".join(voices[0]) + " }"
        cmds = ["\\voiceOne", "\\voiceTwo", "\\voiceThree", "\\voiceFour"]
        parts = [f"\\new Voice {{ {cmds[i]} " + "\n".join(v) + " }"
                 for i, v in enumerate(voices)]
        return "<< " + "\n".join(parts) + " >>"

    first_clef = clef_list(bars[0])[0][0]
    return f"""\\version "2.24.0"
\\header {{ tagline = ##f }}
\\paper {{ #(set-paper-size "a4") indent = 0 top-margin = 8 bottom-margin = 8
  ragged-last = ##f system-system-spacing.basic-distance = #16 }}
\\layout {{ \\context {{ \\Score barNumberVisibility = #all-bar-numbers-visible
  \\override BarNumber.break-visibility = ##(#t #t #t) }} }}
global = {{ \\key f \\major \\numericTimeSignature \\time 4/4 \\set Score.currentBarNumber = #{first} }}
\\score {{
  \\new PianoStaff <<
    \\new Staff = "RH" {{ \\global \\clef treble {staff(rh, 'rh')} }}
    \\new Staff = "LH" {{ \\global \\clef {first_clef} {staff(lh, 'lh')} }}
  >>
}}
"""


def render(bars, out_png, first=None, last=None):
    nums = [b["bar"] for b in bars]
    first = first or min(nums)
    last = last or max(nums)
    src = build_ly(bars, first, last)
    with tempfile.TemporaryDirectory() as d:
        ly = os.path.join(d, "t.ly")
        with open(ly, "w") as f:
            f.write(src)
        r = subprocess.run(["lilypond", "--png", "-dresolution=130",
                            "-o", os.path.join(d, "t"), ly],
                           capture_output=True, text=True)
        pngs = sorted(x for x in os.listdir(d) if x.endswith(".png"))
        if r.returncode != 0 or not pngs:
            sys.stderr.write(r.stderr[-3000:])
            raise SystemExit("lilypond failed")
        from PIL import Image
        ims = [Image.open(os.path.join(d, p)).convert("RGB") for p in pngs]
        # trim white bottoms and stack
        trimmed = []
        for im in ims:
            import numpy as np
            a = np.asarray(im.convert("L"))
            rows = (a < 200).any(axis=1).nonzero()[0]
            if len(rows):
                im = im.crop((0, max(0, rows[0] - 10), im.width,
                              min(im.height, rows[-1] + 10)))
            trimmed.append(im)
        W = max(i.width for i in trimmed)
        H = sum(i.height for i in trimmed)
        out = Image.new("RGB", (W, H), "white")
        y = 0
        for i in trimmed:
            out.paste(i, (0, y))
            y += i.height
        out.save(out_png)
    return out_png


def load(path):
    with open(path) as f:
        data = json.load(f)
    return data["bars"] if isinstance(data, dict) else data


def main():
    cmd = sys.argv[1]
    bars = load(sys.argv[2])
    if cmd == "check":
        errs = check(bars)
        print("\n".join(errs) if errs else "OK")
        sys.exit(1 if errs else 0)
    if cmd == "render":
        a = sys.argv[4:6]
        render(bars, sys.argv[3], *(int(x) for x in a))
        print(sys.argv[3])


if __name__ == "__main__":
    main()
