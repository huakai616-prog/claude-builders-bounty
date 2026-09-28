#!/usr/bin/env python3
"""Print a MIDI file as text for proofreading what ACE Studio will receive:
the tempo map, then per track every note as bar.beat.16th, pitch, length
(in 16ths and ms), velocity, gap to the next note, and the CC11 level.

usage: python3 midi_dump.py FILE.mid [--bars A-B]
"""
import sys

import mido

NAMES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def name(n):
    return f"{NAMES[n % 12]}{n // 12 - 1}"


def main():
    mf = mido.MidiFile(sys.argv[1])
    tpq = mf.ticks_per_beat
    t16 = tpq // 4
    bars = None
    if "--bars" in sys.argv:
        a, b = sys.argv[sys.argv.index("--bars") + 1].split("-")
        bars = (int(a), int(b))
    tempo = []
    for tr in mf.tracks:
        t = 0
        for m in tr:
            t += m.time
            if m.type == "set_tempo":
                tempo.append((t, m.tempo))
    tempo.sort()

    def ms(tick):
        out, last_t, last_tempo = 0.0, 0, 500000
        for tt, tp in tempo:
            if tt >= tick:
                break
            out += (tt - last_t) * last_tempo / tpq / 1000
            last_t, last_tempo = tt, tp
        return out + (tick - last_t) * last_tempo / tpq / 1000

    def pos(tick):
        s = tick // t16
        r = tick % t16
        return f"{s // 16 + 1}.{s % 16 // 4 + 1}.{s % 4}" + (
            f"+{r}t" if r else "")

    print("TEMPO:", ", ".join(f"{pos(t)} {round(mido.tempo2bpm(tp))}"
                               for t, tp in tempo))
    for tr in mf.tracks[1:]:
        t = 0
        on = {}
        notes = []
        cc = []
        for m in tr:
            t += m.time
            if m.type == "note_on" and m.velocity > 0:
                on[m.note] = (t, m.velocity)
            elif m.type in ("note_off", "note_on") and m.note in on:
                s, v = on.pop(m.note)
                notes.append((s, t, m.note, v))
            elif m.type == "control_change" and m.control == 11:
                cc.append((t, m.value))
        notes.sort()
        print(f"\n=== {tr.name}  ({len(notes)} notes)")

        def cc_at(tick):
            v = None
            for tt, val in cc:
                if tt > tick:
                    break
                v = val
            return v
        for i, (s, e, n, v) in enumerate(notes):
            bar = s // (16 * t16) + 1
            if bars and not bars[0] <= bar <= bars[1]:
                continue
            nxt = next((x for x in notes[i + 1:] if x[0] >= s + 1), None)
            gap = (nxt[0] - e) if nxt else None
            print(f"{pos(s):>9} {name(n):>4} len {(e - s) / t16:5.2f}/16 "
                  f"{ms(e) - ms(s):6.0f}ms vel {v:3d} cc11 {cc_at(s)} "
                  f"gap {gap if gap is not None else '-'}t")


if __name__ == "__main__":
    main()
