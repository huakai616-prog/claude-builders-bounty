#!/usr/bin/env python3
"""Merge the reconciled transcription chunks into piano.json and make the
proof copies: 钢琴原谱_转写校对.pdf (engraved like the chart, same system
breaks) and 钢琴原谱_转写.mid (sounding pitch, 8va applied, ♩ = 112).

Usage: python3 merge.py            (reads work/c*_final.json)
       python3 merge.py --proof    (only re-render the proofs from piano.json)
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "source"))
import piano_tools as PT  # noqa: E402

OUT_JSON = os.path.join(HERE, "piano.json")
PDF = os.path.join(HERE, "钢琴原谱_转写校对.pdf")
MID = os.path.join(HERE, "钢琴原谱_转写.mid")
NBARS = 52


def merge():
    bars = {}
    for f in sorted(glob.glob(os.path.join(HERE, "work", "c*_final.json"))):
        for b in PT.load(f):
            if b["bar"] in bars:
                raise SystemExit(f"bar {b['bar']} twice ({f})")
            bars[b["bar"]] = b
    missing = [n for n in range(1, NBARS + 1) if n not in bars]
    if missing:
        raise SystemExit(f"missing bars: {missing}")
    out = [bars[n] for n in range(1, NBARS + 1)]
    errs = PT.check(out)
    if errs:
        raise SystemExit("\n".join(errs))
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        fh.write('{"bars": [\n')
        fh.write(",\n".join(json.dumps(b, ensure_ascii=False) for b in out))
        fh.write("\n]}\n")
    return out


def proof_pdf(bars):
    src = PT.build_ly(bars, 1, NBARS)
    src = src.replace(
        "\\header { tagline = ##f }",
        "\\header { tagline = ##f title = \\markup \\override "
        "#'(font-name . \"Noto Serif CJK SC Bold\") \"诀别书 · 钢琴原谱转写\" "
        "subtitle = \\markup \\override #'(font-name . \"Noto Serif CJK SC\") "
        "\"校对用：换行与原谱一致（作曲 邓垚 · 钢琴谱 张科桔）\" }")
    with tempfile.TemporaryDirectory() as d:
        ly = os.path.join(d, "p.ly")
        with open(ly, "w", encoding="utf-8") as fh:
            fh.write(src)
        r = subprocess.run(["lilypond", "-o", os.path.join(d, "p"), ly],
                           capture_output=True, text=True)
        if r.returncode:
            print(r.stderr[-3000:])
            raise SystemExit("lilypond failed")
        with open(os.path.join(d, "p.pdf"), "rb") as a, open(PDF, "wb") as b:
            b.write(a.read())


def proof_midi(bars):
    import mido
    sys.path.insert(0, os.path.join(HERE, ".."))
    from build import midi_of
    tpq, t16 = 480, 120
    mf = mido.MidiFile(type=1, ticks_per_beat=tpq)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("track_name", name="Piano chart", time=0))
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(112)))
    meta.append(mido.MetaMessage("time_signature", numerator=4,
                                 denominator=4))
    mf.tracks.append(meta)
    for ch, staff in enumerate(("rh", "lh")):
        ev = []
        for b in bars:
            base = (b["bar"] - 1) * 16
            for v in b[staff]:
                for e in PT.parse_voice(v):
                    if e["pitches"] is None:
                        continue
                    octv = PT.ottava_shift(b, e["pos"]) if staff == "rh" \
                        else 0
                    for p in e["pitches"]:
                        n = midi_of(p) + octv
                        on = (base + e["pos"]) * t16
                        ev.append((on, 1, n, 80))
                        ev.append((on + e["dur"] * t16 - 10, 0, n, 0))
        ev.sort()
        tr = mido.MidiTrack()
        tr.append(mido.MetaMessage("track_name", name=staff.upper()))
        tr.append(mido.Message("program_change", channel=ch, program=0))
        last = 0
        for t, kind, n, v in ev:
            tr.append(mido.Message("note_on" if kind else "note_off",
                                   channel=ch, note=n, velocity=v,
                                   time=t - last))
            last = t
        mf.tracks.append(tr)
    mf.save(MID)


if __name__ == "__main__":
    bars = PT.load(OUT_JSON) if "--proof" in sys.argv else merge()
    proof_pdf(bars)
    proof_midi(bars)
    print("written", OUT_JSON, PDF, MID)
