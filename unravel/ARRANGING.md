# Unravel · 弦乐四重奏 编配规范（给写谱的 AI 看的）

Source: Animenz piano arrangement of "Unravel" (TK from 凛として時雨), 4/4, g minor
(two flats), ♩ = 134, bars 0–132 (bar 0 = one-eighth pickup). The piano
transcription is `piano_source.json` (not in the public repo; ask for it or
set `UNRAVEL_PIANO=/path/to/piano_source.json`).

Style (chosen by the user): faithful to the Animenz arrangement — same
melody, harmony, form, dynamics and drama — rewritten so it is idiomatic
for a string quartet. Nothing new is composed: every pitch class the quartet
plays must be in the piano at that moment (`--check` FOREIGN), every melody
attack of the right hand must be there (MELODY), every bass attack of the
left hand must be there (BASS). Octave moves are fine.

## Instruments and ranges (hard limits in `--check`)

| part | id | written range used | clefs |
|---|---|---|---|
| Violin I | vn1 | G3 – C7 (D7 rarely) | treble; `OTTAVA` for long stretches above C7 |
| Violin II | vn2 | G3 – A6 | treble |
| Viola | va | C3 – E6 (comfortable to A5) | alto; `CLEFS` → treble above ~E5 for a phrase |
| Violoncello | vc | C2 – A5 (comfortable to E5) | bass; tenor above ~A3/C4 for a phrase |

The piano's lowest notes (G1, E♭1, C1, …) do not exist on the cello: take
the note an octave up (G2 is the cello's open G string — use it: open-string
resonance is the orchestral substitute for the piano pedal).

## String idiom rules

- **Pedal → sustain.** The piano holds harmony with the pedal; strings must
  actually hold it. Give one or two parts the sustained chord tones.
- **One figuration, one player.** An arpeggio or broken-chord pattern stays
  in one instrument (string crossings), transposed by octave to sit well.
  Don't chop a 16th pattern between players except the deliberate relays
  (runs 66–73 and cascades 78–81).
- **Double stops** only when they add weight (f / ff hits, chorus) and must
  pass `playable()` (adjacent strings, one hand position). Triple/quadruple
  stops only on accented short chords (they are rolled). Never double-stop
  in fast 16ths.
- **Bowing:** slur legato groups (at ♩=134 up to 8 sixteenths or 4 eighths
  per bow), leave driving 16ths/8ths separate (they are played spiccato /
  détaché), mark accents `>` and marcato `!` where the piano accents,
  staccato `.` where the piano has staccato. Tremolo `trem3` where the piano
  writes tremolo. Down-bows `db` on successive ff chord hits.
- **Balance:** the melody is always on top or clearly exposed (Vn I unless
  stated). Don't park an inner part above the melody.
- **Rests are music:** where the piano thins out, let parts rest. Every part
  should have breathing room; avoid 30 bars of non-stop 16ths for one
  player.
- **Registers:** Vn I melody at the piano's sounding octave when it is ≤ C7,
  otherwise an octave lower (and say so in `TEXT` only if it matters).

## Data format (arrangement/secNN.py)

Each section file defines dicts keyed by bar number for its own bars only:

```python
VN1 = {24: "(Bb5/16 A5/8 Bb5/8 ... )", ...}
VN2 = {...}; VA = {...}; VC = {...}
DYN = {"vn1": [(24, 0, "p")], "vn2": [...], "va": [...], "vc": [...]}
HAIR = {"vn1": [(23, 0, 23, 63, "dim")], ...}      # (bar, pos, bar2, pos2, kind)
TEXT = {"vn1": [(24, 0, "espressivo")], ...}        # also "pizz." / "arco"
CLEFS = {"va": [(58, 0, "treble"), (62, 0, "alto")]} # (bar, pos, clef)
OTTAVA = [("vn1", 1, 4),                             # (part, first bar, last bar)
          ("vn1", 62, 24, 62, 48)]                   # or (part, bar1, pos1, bar2, pos2)
```

Expressive words in `TEXT` (dolce, cantabile, espressivo, subito, morendo,
…, see `EXPRESSIVE` in `build.py`) print below the staff, merged with a
dynamic on the same beat ("f subito"); techniques print above.  Don't put
an expressive word on a pickup (it runs through the barline): put it on the
next downbeat.  Engraving-only fixes (stem direction, slurs below) go in
`STEMS` / `SLURS_BELOW` in `arrangement.py`.

Token syntax is in the docstring of `build.py` (64th-note units: 16th = 4,
8th = 8, quarter = 16, half = 32, whole = 64; tuplets `{5:4 … }`; two voices
in one part separated by ` | ` — use sparingly, e.g. a held note under a
moving line). Positions (`pos`) are in 64ths from the bar start. Every bar
string must add up to 64 (bar 0: 8). A bar you don't list is a full-bar
rest.

Check your section: `python3 check_section.py <first> <last>` (prints only
problems in your bars). It must print nothing except allowed items.

## Dynamics

Mirror the piano's dynamics in all parts (each part gets its own marks),
with orchestral sense: accompaniment one step softer than the melody in
p/mp passages; everybody at the same level in ff tutti. Hairpins where the
piano has them, plus small ones where a phrase obviously swells.
