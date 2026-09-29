#!/usr/bin/env python3
"""冬风（肖邦 练习曲 Op. 25 No. 11）— 弦乐四重奏 编配生成器

Generates, from one source of truth:
  * MusicXML full score (for Sibelius / MuseScore / ACE Studio)
  * Full-quartet MIDI (for ACE Studio: String Section x 4) and one MIDI per
    instrument
  * the Hollywood-standard full score PDF (tools/hollywood)

Key: A minor (Chopin's key), cut time.  Lento (bars 1-4), then Allegro con
brio, half = 69.  96 bars, ca. 3'05".

Idea: Chopin's right hand is the "wind" (24 sextuplet 16ths a bar), his left
hand a march theme (E E. E | E F | E C E).  On four strings the wind cannot
stay in one instrument, so it is handed on at the barline: in the falling
four-bar gusts (bars 5-8, 13-16, 23-26, 31-34, 69-72, 77-80, 89-92) it drops
Violin I -> Violin II -> Viola -> Cello, one octave a bar, while the theme
moves up through whoever is free.  Where the wind climbs, the relay runs the
other way.  Everything is Chopin's own notes; only octaves move (see
README.md, "编配说明", for every place a note was changed and why).

The music lives in this file: RH / LH hold Chopin's figuration exactly as
transcribed (sounding pitch), the quartet parts are built bar by bar in
arrange().  Token syntax and the engine are documented in engine.py
(durations in ticks: 48 a bar, 2 = sextuplet 16th, 3 = 16th, 12 = quarter).

    python3 build.py --check   # range / double stops / clashes / parallels
    python3 build.py           # MusicXML + MIDI
    python3 build.py --pdf     # ... + the Hollywood full score PDF
"""
import os
import sys

from music21 import instrument

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hollywood"))
import engine  # noqa: E402
from engine import BAR, octave  # noqa: E402
import hollywood  # noqa: E402  (shared Hollywood score template)

NAME = "冬风"
NBARS = 96
KEY_M21 = "a"
KEY_MIDI = "Am"
MIDI_TITLE = "Winter Wind - Chopin Op.25 No.11 (string quartet)"

# ---------------------------------------------------------------------------
# Chopin's text (sounding pitch).  RH: the right-hand "wind", 24 sextuplet
# 16ths per bar.  LH: bars where the left hand has the same figuration.
# Transcribed from the user's edition (虫虫钢琴, 17 pages) and checked note
# by note against a second edition.
# ---------------------------------------------------------------------------
RH = {
    5: ("F7 C7 E7 A6 D#7 C7  D7 A6 C#7 A6 C7 E6  "
         "B6 E6 Bb6 C6 A6 E6  G#6 C6 G6 C6 F#6 A5"),
    6: ("F6 C6 E6 A5 D#6 C6  D6 A5 C#6 A5 C6 E5  "
         "B5 E5 Bb5 C5 A5 E5  G#5 C5 G5 C5 F#5 A4"),
    7: ("F5 C5 E5 A4 D#5 C5  D5 A4 C#5 A4 C5 E4  "
         "B4 E4 Bb4 C4 A4 E4  G#4 C4 G4 C4 F#4 A3"),
    8: ("F4 C4 E4 A3 D#4 C4  D4 A3 C#4 A3 C4 E3  "
         "B3 E3 Bb3 C3 A3 E3  G#3 C3 A3 E3 C4 F3"),
    9: ("E4 B3 D4 F4 E5 B4  D5 F5 E6 B5 D6 F5  "
         "D6 A5 C6 F5 D5 A4  C5 F4 D4 A3 C4 F3"),
    10: ("E4 B3 D4 F4 E5 B4  D5 F5 E6 B5 D6 F5  "
         "D6 A5 C6 F5 D5 A4  C5 F4 D4 A3 C4 B3"),
    11: ("A4 E4 G#4 B4 A5 E5  G#5 B5 A6 E6 G#6 B5  "
         "G#6 D#6 F#6 B5 G#5 D#5  F#5 B4 G#4 D#4 F#4 B3"),
    13: ("F7 C7 E7 A6 D#7 C7  D7 A6 C#7 A6 C7 E6  "
         "B6 E6 Bb6 C6 A6 E6  G#6 C6 G6 C6 F#6 A5"),
    14: ("F6 C6 E6 A5 D#6 C6  D6 A5 C#6 A5 C6 E5  "
         "B5 E5 Bb5 C5 A5 E5  G#5 C5 G5 C5 F#5 A4"),
    15: ("F5 Bb4 E5 G4 Eb5 Bb4  D5 G4 Db5 Bb4 C5 G4  "
         "B4 G4 Bb4 E4 A4 C4  G#4 Bb3 G4 C4 F#4 Bb3"),
    16: ("F4 C4 E4 Bb3 Eb4 C4  D4 G3 Db4 Bb3 C4 G3  "
         "B3 G3 C4 Bb3 C#4 G3  Db4 Bb3 D#4 G3 E4 Bb3"),
    17: ("A4 E4 G4 Bb4 A5 E5  G5 Bb5 A6 E6 G6 Bb5  "
         "A6 Eb6 G6 Bb5 A5 Eb5  G5 Bb4 A4 Eb4 G4 Bb3"),
    18: ("A4 E4 G4 Bb4 A5 E5  G5 Bb5 A6 E6 G6 Bb5  "
         "A6 Eb6 G6 Bb5 A5 Eb5  G5 Bb4 A4 Eb4 G4 Bb3"),
    19: ("A4 C4 G4 Bb3 C5 A4  Bb4 G4 A5 C5 G5 Bb4  "
         "C6 A5 Bb5 G5 A6 C6  G6 Bb5 C7 A6 Bb6 G6"),
    # beat 3 as the user's edition prints it (another edition has D#6 A5 C6)
    20: ("D7 A6 C7 F6 G#6 F6  A6 C6 E6 C6 F6 A5  "
         "C#6 A5 D6 F5 G#5 F5  A5 C5 E5 C5 F5 A4"),
    21: ("E5 B4 D5 F5 E6 B5  D6 F6 E7 B6 D7 F6  "
         "A6 F6 G6 B5 A5 F5  G5 B4 E6 G5 D6 F5"),
    22: ("B5 G5 C6 E5 D#6 C6  E6 G5 F#6 E6 G6 C6  "
         "A#6 G6 B6 E6 C7 G6  C#7 E6 D7 G6 D#7 E6"),
    23: ("E7 B6 D#7 G6 D7 B6  C#7 G6 C7 G6 B6 E6  "
         "A#6 G6 A6 E6 G#6 E6  G6 C6 F#6 C6 F6 G5"),
    24: ("E6 B5 D#6 G5 D6 B5  C#6 G5 C6 G5 B5 E5  "
         "A#5 G5 A5 E5 G#5 E5  G5 C5 F#5 C5 F5 G4"),
    25: ("E5 B4 D#5 G4 D5 B4  C#5 G4 C5 G4 B4 E4  "
         "A#4 G4 A4 E4 G#4 E4  G4 C4 F#4 C4 F4 G3"),
    26: ("E4 B3 D#4 G3 D4 B3  C#4 G3 C4 G3 B3 E3  "
         "A#3 G3 A3 B2 G#3 E3  G3 B2 F#3 E3 G3 C3"),
    27: ("B3 F#3 A3 C4 B4 F#4  A4 C5 B5 F#5 A5 C5  "
         "A5 E5 G5 C5 A4 E4  G4 C4 A3 E3 G3 C3"),
    28: ("B3 F#3 A3 C4 B4 F#4  A4 C5 B5 F#5 A5 C5  "
         "A5 E5 G5 C5 A4 E4  G4 C4 A3 E3 G3 F#3"),
    29: ("E4 B3 D#4 F#4 E5 B4  D#5 F#5 E6 B5 D#6 F#5  "
         "D#6 A#5 C#6 F#5 D#5 A#4  C#5 F#4 D#4 A#3 C#4 F#3"),
    31: ("C7 G6 B6 E6 A#6 G6  A6 E6 G#6 E6 G6 B5  "
         "F#6 B5 F6 G5 E6 B5  D#6 G5 D6 G5 C#6 E5"),
    32: ("C6 G5 B5 E5 A#5 G5  A5 E5 G#5 E5 G5 B4  "
         "F#5 B4 F5 G4 E5 B4  D#5 G4 D5 G4 C#5 E4"),
    33: ("C5 G4 B4 E4 A#4 G4  A4 E4 G#4 E4 G4 B3  "
         "F#4 B3 F4 G3 E4 B3  Eb4 F#3 D4 G3 C#4 F3"),
    34: ("C4 G3 B3 E3 Bb3 G3  A3 E3 Ab3 E3 G3 B2  "
         "F#3 F3 G3 B2 G#3 F3  A3 D3 A#3 G3 B3 F3"),
    35: ("E4 B3 D4 F4 E5 B4  D5 F5 E6 B5 D6 F5  "
         "E6 Bb5 D6 F5 E5 Bb4  D5 F4 E4 Bb3 D4 F3"),
    36: ("E4 A3 D4 F4 E5 A4  D5 F5 E6 A5 D6 F5  "
         "E6 G#5 D6 F5 E5 G#4  D5 F4 E4 G#3 D4 F3"),
    37: ("E4 G3 D4 F3 G4 E4  F4 D4 E5 G4 D5 F4  "
         "G5 E5 F5 D5 E6 G5  D6 F5 G6 E6 F6 D6"),
    38: ("A6 E6 G6 C6 E7 G6  D7 E6 C7 G#6 B6 E6  "
         "Bb6 F6 Ab6 Db6 Gb6 Db6  F6 Ab5 Eb6 Ab5 Db6 F5"),
    39: ("Db6 F#5 C6 E5 G5 C5  Ab5 E5 F#5 C5 G5 E5  "
         "A5 B4 F#5 F5 G5 B4  B5 F5 E6 G5 D6 F5"),
    40: ("D6 G5 C6 E5 A5 E5  G5 C5 F5 C5 E5 G4  "
         "A5 E5 G5 C5 F5 C5  E5 G4 A5 E5 G5 C5"),
    # the user's edition prints this bar's 8va under the left hand of bar
    # 44 (an engraving slip); beats 1-2 sound an octave up, as here
    45: ("C7 Eb6 Bb6 Db6 Ab6 Eb6  G6 Db6 F6 Db6 Eb6 G5  "
         "F6 C6 Eb6 Ab5 Db6 Ab5  C6 Eb5 Bb5 Eb5 Ab5 C5"),
    46: ("C6 Eb5 Bb5 Db5 A5 Eb5  Bb5 Db5 Db6 Eb5 G5 Db5  "
         "Bb5 Eb5 Ab5 C5 G5 Eb5  Ab5 C5 Bb5 Eb5 Ab5 C5"),
    47: ("G#6 B5 F#6 A5 E6 B5  D#6 A5 C#6 A5 B5 F#5  "
         "E6 G#5 D#6 E5 C#6 G#5  B5 E5 A5 E5 G#5 B4"),
    48: ("G#5 D#5 F#5 A4 E#5 D#5  F#5 A4 A5 B4 D#5 A4  "
         "F#5 B4 F5 G#4 E5 B4  D#5 G#4 D5 B4 C#5 G#4"),
    49: ("C#5 G#4 B4 D4 C#5 G#4  B4 D5 C#6 G#5 B5 D6  "
         "C#7 G#6 B6 D6 C#6 G#5  B5 D5 C#5 G#4 B4 D4"),
    50: ("D5 G4 C5 C4 F5 C5  Eb5 G4 Ab5 Eb5 G5 C5  "
         "C6 G5 B5 Eb5 Bb5 G5  A5 Eb5 Ab5 Eb5 G5 C5"),
    51: ("F5 C5 Eb5 Gb4 F5 C5  Eb5 Gb5 F6 C6 Eb6 Gb6  "
         "F7 C7 Eb7 Gb6 F6 C6  Eb6 Gb5 F5 C5 D#5 F#4"),
    52: ("F#5 B4 E5 E4 A5 E5  G5 B4 C6 G5 B5 E5  "
         "E6 B5 D#6 G5 D6 B5  C#6 G5 C6 G5 B5 E5"),
    53: ("Bb5 E5 A5 Bb4 Ab5 E5  G5 Bb4 A5 E5 G5 Bb4  "
         "G5 C5 F#5 A4 F5 C5  F#5 A4 G5 B4 F#5 A4"),
    54: ("F#5 B4 F5 G4 E5 B4  E5 G4 F5 A4 E5 G4  "
         "E5 A4 C#5 F4 D5 A4  D5 E4 B4 A4 C5 E4"),
    55: ("C5 A4 B4 F4 C5 A4  B4 F5 C6 A5 B5 F6  "
         "C7 A6 B6 F6 C6 A5  B5 F5 C5 A4 B4 F4"),
    56: ("B4 F#4 A4 C4 B4 F#4  A4 C5 B5 F#5 A5 C6  "
         "B6 F#6 A6 C6 B5 F#5  A5 C5 B4 F#4 A4 C4"),
    57: ("A4 E4 G#4 B4 A5 E5  G#5 B5 A6 E6 G#6 B5  "
         "G#6 D6 F#6 B5 G#5 D5  F#5 B4 G#4 D4 F#4 B3"),
    58: ("F#4 C#4 E4 G#4 F#5 C#5  E5 G#5 F#6 C#6 E6 G#5  "
         "E6 B5 D6 F#5 E5 B4  D5 F#4 E4 B3 D4 F#3"),
    59: ("C#4 G#3 B3 F3 E4 B3  D4 G#3 G4 D4 F4 B3  "
         "A4 F4 G#4 D4 C5 G#4  B4 F4 E5 B4 D5 G#4"),
    60: ("G5 D5 F5 B4 A5 F5  G#5 D5 C6 G#5 B5 F5  "
         "E6 B5 D6 G#5 G6 D6  F6 B5 A6 F6 G#6 D6"),
    61: ("F7 B6 E7 G#6 D#7 B6  D7 G#6 C#7 G6 C7 F6  "
         "B6 F6 Bb6 D6 A6 F6  G#6 B5 G6 D6 F#6 G#5"),
    63: ("B6 F6 A#6 D6 A6 F6  G#6 D6 G6 D6 F#6 B5  "
         "F6 B5 E6 G#5 D#6 B5  D6 G#5 C#6 G#5 C6 F5"),
    66: ("F5 D5 E5 G#4 F5 D5  E5 G#4 F5 D5 E5 G#4  "
         "F5 D5 E5 G#4 F5 D5  E5 G#4 F5 D5 E5 G#4"),
    67: ("F5 D5 E5 G#4 F5 D5  E5 G#4 F5 D5 E5 G#4  "
         "F5 D5 E5 G#4 F5 D5  E5 G#4 F5 D5 E5 G#4"),
    68: ("F5 D5 E5 G#4 F5 D5  E5 G#5 F6 D6 E6 G#6  "
         "F7 D7 E7 G#6 F7 D7  E7 G#6 F7 D7 E7 G#6"),
    69: ("F7 C7 E7 A6 D#7 C7  D7 A6 C#7 A6 C7 E6  "
         "B6 E6 Bb6 C6 A6 E6  G#6 C6 G6 C6 F#6 A5"),
    70: ("F6 C6 E6 A5 D#6 C6  D6 A5 C#6 A5 C6 E5  "
         "B5 E5 Bb5 C5 A5 E5  G#5 C5 G5 C5 F#5 A4"),
    71: ("F5 C5 E5 A4 D#5 C5  D5 A4 C#5 A4 C5 E4  "
         "B4 E4 Bb4 C4 A4 E4  G#4 C4 G4 C4 F#4 A3"),
    72: ("F4 C4 E4 A3 D#4 C4  D4 A3 C#4 A3 C4 E3  "
         "B3 E3 Bb3 C3 A3 E3  G#3 C3 A3 E3 C4 F3"),
    73: ("E4 B3 D4 F4 E5 B4  D5 F5 E6 B5 D6 F5  "
         "D6 A5 C6 F5 D5 A4  C5 F4 D4 A3 C4 F3"),
    74: ("E4 B3 D4 F4 E5 B4  D5 F5 E6 B5 D6 F5  "
         "D6 A5 C6 F5 D5 A4  C5 F4 D4 A3 C4 B3"),
    75: ("A4 E4 G#4 B4 A5 E5  G#5 B5 A6 E6 G#6 B5  "
         "G#6 D#6 F#6 B5 G#5 D#5  F#5 B4 G#4 D#4 F#4 B3"),
    77: ("F7 C7 E7 A6 D#7 C7  D7 A6 C#7 A6 C7 E6  "
         "B6 E6 Bb6 C6 A6 E6  G#6 C6 G6 C6 F#6 A5"),
    78: ("F6 C6 E6 A5 D#6 C6  D6 A5 C#6 A5 C6 E5  "
         "B5 E5 Bb5 C5 A5 E5  G#5 C5 G5 C5 F#5 A4"),
    79: ("F5 C5 E5 A4 D#5 C5  D5 A4 C#5 A4 C5 E4  "
         "B4 E4 Bb4 C4 A4 E4  A#4 C4 A4 C4 F#4 A3"),
    80: ("F4 C4 E4 A3 D#4 C4  D4 A3 C#4 A3 C4 E3  "
         "B3 F3 A3 C3 G#3 F3  A3 C3 B3 E3 C4 C3"),
    81: ("C4 F3 B3 B3 C5 F4  B4 B4 C6 F5 B5 B5  "
         "C7 F#6 B6 B5 C6 F#5  B5 B4 C5 F#4 B4 B3"),
    82: ("D5 G4 C#5 C#5 D6 G5  C#6 C#6 D7 G6 C#7 C#6  "
         "Eb7 Bb6 D7 D6 Eb6 Bb5  D6 D5 Eb5 Bb4 D5 D4"),
    83: ("E5 A4 D#5 D#4 E5 A4  D#5 D#5 E6 A5 D#6 D#6  "
         "E7 A6 D#7 D#6 E6 A5  D#6 D#5 E6 A5 D#6 D#6"),
    84: ("E7 A6 D#7 D#6 E6 A5  D#6 D#5 E6 A5 D#6 D#6  "
         "E7 A6 D#7 D#6 E7 A6  D#7 D#6 E7 A6 D#7 D#6"),
    85: ("E7 B6 D#7 A6 E7 B6  D#7 A6 E7 B6 D#7 A6  "
         "E7 B6 D#7 A6 E7 B6  D#7 A6 E7 B6 D#7 A6"),
    86: ("E7 B6 D#7 A6 E7 B6  D#7 A6 E7 B6 D#7 A6  "
         "E7 B6 D#7 A6 E7 B6  D#7 A6 E7 B6 D#7 A6"),
    87: ("F7 C7 E7 A6 D7 A6  C7 E6 B6 E6 A6 C6  "
         "F6 C6 E6 A5 D6 A5  C6 E5 B5 E5 A5 C5"),
    89: ("A6 E6 G#6 C6 G6 E6  F#6 C6 F6 C6 E6 A5  "
         "D#6 C6 D6 A5 C#6 A5  C6 E5 B5 E5 Bb5 C5"),
    90: ("A5 E5 G#5 C5 G5 E5  F#5 C5 F5 C5 E5 A4  "
         "D#5 C5 D5 A4 C#5 A4  C5 E4 B4 E4 Bb4 C4"),
    91: ("A4 E4 G#4 C4 G4 E4  F#4 C4 F4 C4 E4 A3  "
         "D#4 C4 D4 A3 C#4 A3  C4 E3 B3 E3 Bb3 C3"),
    92: ("A3 E3 G#3 C3 G3 E3  F#3 C3 F3 C3 E3 A2  "
         "D#3 C3 D3 A2 C#3 A2  C3 E2 B2 E2 Bb2 E2"),
}

LH = {
    41: ("A4 E4 G4 C#4 F4 C#4  E4 Bb3 D4 Bb3 C#4 G3  "
         "C4 G3 Bb3 E3 A3 E3  G3 C#3 F3 C#3 E3 Bb2"),
    42: ("D3 Bb2 C#3 G2 C3 G2  Bb2 E2 A2 E2 G2 C#2  "
         "F2 C#2 E2 Bb1 D2 Bb1  C#2 G1 C2 G1 Bb1 E1"),
    43: ("C5 G4 Bb4 E4 A4 E4  G4 C#4 F4 C#4 E4 Bb3  "
         "D4 Bb3 C#4 G3 C4 G3  Bb3 E3 A3 E3 G3 C#3"),
    44: ("F3 C#3 E3 Bb2 D3 Bb2  C#3 G2 C3 G2 Bb2 E2  "
         "A2 E2 G2 C#2 F2 C#2  E2 Bb1 D2 Bb1 C#2 G1"),
    61: ("E2 B2 G#2 D3 G#2 D3  B2 F3 B2 F3 D3 G#3  "
         "D3 G#3 F3 B3 F3 B3  G#3 D4 G#3 D4 B3 F4"),
    63: ("B1 F2 D2 G#2 D2 G#2  F2 B2 F2 B2 G#2 D3  "
         "G#2 D3 B2 F3 B2 F3  D3 G#3 D3 G#3 F3 B3"),
    66: ("F4 D4 E4 B3 F4 D4  E4 B3 F4 D4 E4 B3  "
         "F4 D4 E4 B3 F4 D4  E4 B3 F4 D4 E4 B3"),
    67: ("F4 E4 D#4 D4 C#4 C4  B3 A#3 A3 G#3 G3 F#3  "
         "F3 E3 D#3 D3 C#3 C3  B2 A#2 A2 G#2 G2 F#2"),
    68: ("F2 E2 D#2 E2 F2 E2  D#2 E2 F2 E2 D#2 E2  "
         "F2 E2 D#2 E2 F2 E2  D#2 E2 F2 E2 D#2 E2"),
    85: ("F2 B2 A2 D#3 A2 D#3  B2 F3 B2 F3 D#3 A3  "
         "D#3 A3 F3 B3 F3 B3  A3 D#4 A3 D#4 B3 F4"),
    86: ("B3 F4 D#4 A4 D#4 A4  F4 B4 F4 B4 A4 D#5  "
         "A4 D#5 B4 F5 B4 F5  D#5 A5 D#5 A5 F5 B5"),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
R = "r/48"


def sx(pitches, slur=12, acc=(), dur=2):
    """Sextuplet 16ths (dur 2) from a pitch list, slurred every `slur`
    notes (0 = no slurs), accents on the indexes in `acc`."""
    ps = pitches.split()
    out = []
    for i, p in enumerate(ps):
        t = f"{p}/{dur}" + (">" if i in acc else "")
        if slur and i % slur == 0 and i < len(ps) - 1:
            t = "(" + t
        if slur and (i % slur == slur - 1 or i == len(ps) - 1) \
                and i % slur != 0:
            t += ")"
        out.append(t)
    return " ".join(out)


def rests(ticks):
    out = []
    for d in (24, 12):
        while ticks >= d:
            out.append(f"r/{d}")
            ticks -= d
    return out


def w(b, sh=0, beats=(1, 4), fix=None, slur=12, src=None, acc=()):
    """Chopin's figuration of bar b (RH, or LH with src=LH) shifted by `sh`
    octaves, played in beats[0]..beats[1] only (rests elsewhere).
    fix = {index: pitch} replaces single notes after the shift."""
    ps = [octave(p, sh) for p in (src or RH)[b].split()]
    assert len(ps) == 24, b
    for i, p in (fix or {}).items():
        ps[i] = p
    b0, b1 = beats
    sel = " ".join(ps[(b0 - 1) * 6:b1 * 6])
    lead = ["r/12"] * (b0 - 1) if b0 != 3 else ["r/24"]
    tail = {4: [], 3: ["r/12"], 2: ["r/24"], 1: ["r/12", "r/24"]}[b1]
    return " ".join(lead + [sx(sel, slur, acc)] + tail)


def lw(b, sh=0, **kw):
    return w(b, sh, src=LH, **kw)


VN1, VN2, VA, VC = {}, {}, {}, {}


def put(b, vn1=R, vn2=R, va=R, vc=R):
    VN1[b], VN2[b], VA[b], VC[b] = vn1, vn2, va, vc


# ---------------------------------------------------------------------------
# The arrangement
# ---------------------------------------------------------------------------
def arrange():
    # ---- Introduction (Lento): the theme alone in the cello, then the
    # quartet as a pp chorale (Chopin's own four-part chords)
    # (repeated notes on separate bows, slurs where Chopin's end)
    put(1, vc="E4/12 E4/9 E4/3 (E4/12 F4/12")
    put(2, vn1="r/48@", vn2="r/48@", va="r/48@", vc="E4/12 C4/12) E4/24@")
    put(3, vn1="E4/12 E4/9 E4/3 (E4/12 F4/12)",
        vn2="C4/12 C4/9 C4/3 C4/12 C4/12",
        va="G3/12 G3/9 G3/3 (G3/12 A3/12)",
        vc="C3/12 C3/9 C3/3 (C3/12 F2/12)")
    put(4, vn1="(E4/12 C4/12) E4/24@",
        vn2="(C4/12 A3/12) (C4/12 D4/12@)",
        va="(G3/12 F3/12) (G3/12 G#3/12@)",
        vc="(C2/12 F2/12) (C3/12 B2/12@)")

    # ---- A: Theme.  The first gust falls Vn1 -> Vn2 -> Va -> Vc (8vb);
    # the theme sits in the viola (E4 on the A string), doubled an octave
    # down in the cello's fifths.
    put(5, vn1=w(5, -1),
        vn2="r/12 C4/9 C4/3 C4/12 C4/12",
        va="r/12 E4/9 E4/3 E4/12 F4/12",
        vc="A2/12^ A2+E3/9 A2+E3/3 A2+E3/12 A2+F3/12")
    put(6, vn1="C4/12 A3/12 C4/24",
        vn2=w(6, -1),
        va="E4/12 C4/12 E4/24",
        vc="A2+E3/12 A2+E3/12 A2+E3/24")
    put(7, va=w(7, -1, fix={23: "A3"}),
        vc="A2/12^ A2+E3/9 A2+E3/3 A2+E3/12 A2+F3/12")
    # Chopin's A bass (held) and E, an octave up, over the cello's wind
    put(8, va="E3+A3/12 A3/12 E3+A3/24",
        vc=w(8, -1, slur=6))
    # arpeggios: Violin I alone; the theme in 6ths/3rds (Vn2 over Va),
    # cello bass on beats 1 and 4
    put(9, vn1=w(9, fix={23: "F4"}),
        vn2="r/12 D4/9 D4/3 C4/12 r/12",
        va="r/12 F3/9 F3/3 F3/12 r/12",
        vc="G#2/24^ r/12 A2/12^")
    put(10, vn1=w(10),
        vn2="r/12 D4/12 C4/12 r/12",
        va="r/12 G3/4 F3/4 E3/4 E3/12 r/12",
        vc="G#2/24^ r/12 A2/12^")
    put(11, vn1=w(11),
        vn2="r/12 E4/4 G#4/4 C#5/4 B4/12 r/12",
        va="r/12 B3/12 D#4+A4/12 B3/12",
        vc="B2/24^ B3/12 B2/12^")
    put(12, vn1=sx("A4 E4 G#4 B4 A5 E5 G#5 B5 A6 E6 G#6 B5") + " E7/12' r/12",
        vn2="r/12 G#4/4 F##4/4 G#4/4 E4/12' r/12",
        va="r/12 B3/4 A#3/4 B3/4 G#3/12' r/12",
        vc="E2/12^ r/12 E3/12' r/12")

    # ---- B: the theme again, stronger: octaves (Vn2 E5 over Va E4)
    put(13, vn1=w(13, -1),
        vn2="r/12 E5/9 E5/3 E5/12 F5/12",
        va="r/12 C4+E4/9 C4+E4/3 C4+E4/12 C4+F4/12",
        vc="A2/12^ A2+E3/9 A2+E3/3 A2+E3/12 A2+F3/12")
    put(14, vn1="E5/12 C5/12 E5/24",
        vn2=w(14, -1),
        va="C4+E4/12 E3+C4/12 C4+E4/24",
        vc="A2+E3/12 A2+E3/12 A2+E3/24")
    # C major: the wind stays in the viola (at pitch), the cello sings
    put(15, va=w(15),
        vc="C2/12^ G2+E3/9 G2+E3/3 G2+E3/12 G2+F3/12")
    put(16, va=w(16),
        vc="G2+E3/12 C2+C3/12 G2+E3/24")
    put(17, vn1=w(17),
        vn2="r/12 Bb3/12 Bb3/12 r/12",
        va="r/12 G3+E4/12 G3+Eb4/12 r/12",
        vc="C2/12^ r/4 B2/4 C3/4 C#3/12 C#2/12^")
    # the same bar answered by Violin II (antiphony across the stage)
    put(18, vn1="r/12 G4/12 Db4+G4/12 r/12",
        vn2=w(18),
        va="r/12 Bb3+D4/12 Bb3/12 r/12",
        vc="D2/12^ r/4 C#3/4 D3/4 Eb3/12 Eb2/12^")
    # rising: Violin II hands the wind up to Violin I at beat 3
    put(19, vn1=w(19, beats=(3, 4)),
        vn2=w(19, beats=(1, 2)),
        va="r/12 C4/9> C4/3 C4/12> r/12",
        vc="E2/12^ C3/9> C3/3 C3/12> C2/12^")
    put(20, vn1=w(20),
        vn2="r/24 D4/9 E4/3 F4/12",
        va="r/12 A4/9 A3/3~ A3/24",
        vc="F2/12^ r/12 F3/24")
    put(21, vn1=w(21),
        vn2="r/12 B3/4 F4/4 A4/4 G4/12 r/12",
        va="r/12 G3/12 r/12 B3+F4/12",
        vc="G2/12^ r/24 G3/12")
    # an octave down, so the rising D#6 lands on bar 23's E6 in one hand
    put(22, vn1=w(22, -1),
        va="r/12 G3+E4/12 r/24",
        vc="C2/12^ C3/12 r/24")

    # ---- C: E minor, the gust again (8vb relay), theme on B3
    put(23, vn1=w(23, -1),
        vn2="r/12 G3/9 G3/3 G3/12 G3/12",
        va="r/12 B3/9 B3/3 B3/12 C4/12",
        vc="E2/12^ E2+B2/9 E2+B2/3 E2+B2/12 E2+C3/12")
    put(24, vn1="B4/12 G4/12 B4/24",
        vn2=w(24, -1),
        va="B3/12 G3/12 B3/24",
        vc="E2+B2/12 E2+B2/12 E2+B2/24")
    put(25, va=w(25, -1, fix={23: "G3"}),
        vc="E2/12^ E2+B2/9 E2+B2/3 E2+B2/12 E2+C3/12")
    put(26, va="E3+B3/12 E3/12 E3+B3/24",
        vc=w(26, -1, fix={15: "B2", 19: "B2"}, slur=6))
    put(27, vn1=w(27, 1),
        vn2="r/12 C4/9> C4/3 C4/12 r/12",
        va="r/12 D#3/9> D#3/3 E3/12 r/12",
        vc="D#2/24^ r/12 E2/12^")
    put(28, vn1=w(28, 1),
        vn2="r/12 (D4/4 C4/6 B3/2) B3/12 r/12",
        va="r/12 D#3/12 E3/12 r/12",
        vc="D#2/24^ r/12 E2/12^")
    put(29, vn1=w(29, fix={23: "F#4"}),
        vn2="r/12 B3/4 D#4/4 G#4/4 F#4/12 r/12",
        va="r/12 F#3/12 A#3+E4/12 F#3/12",
        vc="F#2/24^ F#3/12 F#2/12^")
    put(30, vn1=sx("E4 B3 D#4 F#4 E5 B4 D#5 F#5 E6 B5 D#6 F#5")
        + " B6/12' r/12",
        vn2="r/12 D#4/4 C##4/4 D#4/4 B3/12' r/12",
        va="r/12 F#3/4 E#3/4 F#3/4 D#3/12' r/12",
        vc="B2/12^ r/12 B2/12' r/12")

    # ---- D: the gust at Chopin's own pitch (top C7), theme doubled
    put(31, vn1=w(31),
        vn2="r/12 B4/9 B4/3 B4/12 C5/12",
        va="r/12 G3+E4/9 G3+E4/3 G3+E4/12 G3+E4/12",
        vc="E2/12^ E2+B2/9 E2+B2/3 E2+B2/12 E2+C3/12")
    put(32, vn1="B4/12 G4/12 B4/24",
        vn2=w(32),
        va="G3+E4/12 E3+G3/12 G3+E4/24",
        vc="E2+B2/12 E2+B2/12 E2+B2/24")
    put(33, va=w(33),
        vc="G2/12^ D2+B2/9 D2+B2/3 D2+B2/12 D2+C3/12")
    put(34, va="D3+B3/12 G3/12 D3+G3/24",
        vc=w(34))
    put(35, vn1=w(35, fix={23: "F4"}),
        va="r/12 D3+B3/12> D3+Bb3/12 r/12",
        vc="G2/12^ r/4 F#2/4 G2/4 Ab2/12 G#2/12^")
    put(36, vn1="r/12 D4/12> G#3+D4/12 r/12",
        vn2=w(36, fix={23: "F4"}),
        va="r/12 F3/12> F3/12 r/12",
        vc="A2/12^ r/4 G#2/4 A2/4 Bb2/12 A#2/12^")
    # rising: viola hands the wind up to Violin I
    put(37, vn1=w(37, beats=(3, 4)),
        vn2="r/12 G4/9> G4/3 G4/12> r/12",
        va=w(37, beats=(1, 2)),
        vc="B2/12^ G3/9> G3/3 G3/12> G2/12^")
    put(38, vn1=w(38),
        va="r/12 E3/4 C4/4 G#4/4 r/12 F3+Ab3/4 Db4/4 Ab4/4",
        vc="C2/12^ r/12 F2/12^ r/12")
    put(39, vn2=w(39),
        va="r/12 G3+C4/4 E4/4 G4/4 r/12 D4+F4/12",
        vc="G2/12^ r/12 G2/12^ G2/12")
    put(40, vn1=w(40),
        va="G3+E4/12 r/12 r/24",
        vc="C3/12 r/12 r/24")

    # ---- E: Development.  The theme goes up to the violins in chords,
    # the wind down to the viola and cello (Chopin's left hand)
    put(41, vn1="G5/12 G5/9 G5/3 G5/12 A5/12",
        vn2="E5/12 G4+E5/9 G4+E5/3 G4+E5/12 A4+E5/12",
        va=lw(41, fix={23: "Bb3"}))
    put(42, vn1="G5/12 E5/12 G5/24",
        vn2="G4+E5/12 G4+C#5/12 G4+E5/24",
        vc=lw(42, 1, slur=6))
    put(43, vn1="Bb5/12 Bb5/9 Bb5/3 Bb5/12 C6/12",
        vn2="G5/12 Bb4+G5/9 Bb4+G5/3 Bb4+G5/12 C5+G5/12",
        va=lw(43))
    put(44, vn1="Bb5/12 G5/12 Bb5/24",
        vn2="Bb4+G5/12 Bb4+E5/12 Bb4+G5/24",
        vc=lw(44, 1, slur=6))
    # A-flat: the theme in the viola's tenor voice, Violin I the wind
    put(45, vn1=w(45),
        va="r/12 Eb4/9 Eb4/3 (Eb4/12 Ab4/9 C4/3",
        vc="Eb2/12^ r/12 Eb3+C4/12 r/12")
    put(46, vn1=w(46),
        va="Eb4/12 Bb3/9 Eb4/3 C4/12) r/12",
        vc="Eb3/24 Ab2+Eb3/12 r/12")
    put(47, vn2=w(47),
        va="r/12 B3/9 B3/3 (B3/12 E4/6) r/3 (G#3/3",
        vc="B2/12^ r/12 B2+G#3/12 r/12")
    put(48, vn2=w(48),
        va="B3/12 F#3/4 G#3/4 A3/4 G#3/12) r/12",
        vc="B2/24 E2+B2/12 r/12")

    # ---- F: build-up.  The bass theme in octaves (viola over cello),
    # the wind swapping between the violins
    put(49, vn1=w(49),
        va="E3/12^ B3/4 G#3/4 B3/4 E3/6 r/3 E3/3 F#3/9 E3/3",
        vc="E2/12^ B2/4 G#2/4 B2/4 E2/6 r/3 E2/3 F#2/9 E2/3")
    put(50, vn2=w(50),
        va="Eb3/12 C3/12 Eb3/12 F3/4 F#3/4 G3/4",
        vc="Eb2/12 C2/12 Eb2/12 F2/4 F#2/4 G2/4")
    # the peak (F7) is folded: Violin II climbs to Gb6, Violin I falls
    put(51, vn1=w(51, -1, beats=(3, 4), fix={23: "F#4"}),
        vn2=w(51, beats=(1, 2)),
        va="Ab3/12 Eb3/4 C3/4 Eb3/4 Ab3/6 r/3 Ab3/3 Bb3/9 Ab3/3",
        vc="Ab2/12 Eb2/4 C2/4 Eb2/4 Ab2/6 r/3 Ab2/3 Bb2/9 Ab2/3")
    put(52, vn1=w(52),
        va="G3/12 E3/12 G3/12 A3/4 A#3/4 B3/4",
        vc="G2/12 E2/12 G2/12 A2/4 A#2/4 B2/4")
    put(53, vn2=w(53),
        va="C4/12> E3/12> A3/12> D#3/12>",
        vc="C3/12^ C2+G2/12^ F2+C3/12^ B2/12^")
    put(54, vn1=w(54),
        va="G3/12> C#4/12> D4/12> C4/12>",
        vc="E2+B2/12^ A2+E3/12^ D3+A3/12^ A2+E3/12^")
    put(55, vn1=w(55),
        va="D3/12^ (F4/12^ A#3/6) r/3 (C4/3 B3/12^)",
        vc="D2/12^ (F3/12^ A#2/6) r/3 (C3/3 B2/12^)")
    put(56, vn2=w(56),
        va="D#3/12^ (F#4/12^ A3/6) r/3 (D4/3 C4/12^)",
        vc="D#2/12^ (F#3/12^ A2/6) r/3 (D3/3 C3/12^)")
    # dominant pedal on E: the tenor melody passes Vn2 -> Vn1
    put(57, vn1=w(57),
        vn2="r/12 (B3/9 E4/3 D4/24)",
        va="E3/48",
        vc="E2/48")
    put(58, vn1="r/12 (G#3/9 C#4/3 B3/24)",
        vn2=w(58, fix={23: "F#4"}),
        va="E3/48",
        vc="E2/48~")
    put(59, vn2=w(59, fix={3: "F4"}),
        va="r/12 F3/9> F3/3 F3/12> G3/12>",
        vc="E2/48~")
    put(60, vn1=w(60),
        va="F3/12> D3/12> F3/24>",
        vc="E2/48")

    # ---- G: Climax.  Contrary motion: the violins fall in octaves, the
    # viola and cello climb in octaves
    put(61, vn1=w(61, -1, slur=6), vn2=w(61, -2, slur=6),
        va=lw(61, 1, slur=6), vc=lw(61, slur=6))
    put(62, vn1=sx("F6 B5 E6 G#5 D#6 B5 D6 G#5 C#6 G5 C6 F5", slur=6)
        + " F5+B5/6' r/6 r/12",
        vn2=sx("F5 B4 E5 G#4 D#5 B4 D5 G#4 C#5 G4 C5 F4", slur=6)
        + " F4+B4/6' r/6 r/12",
        va=sx("B3 F4 D4 G#4 D4 G#4 F4 B4 F4 B4 G4 D5", slur=6)
        + " G#4+D5/6' r/6 r/12",
        vc=sx("B2 F3 D3 G#3 D3 G#3 F3 B3 F3 B3 G3 D4", slur=6)
        + " B2+F3/6' r/6 r/12")
    put(63, vn1=w(63, slur=6), vn2=w(63, -1, slur=6),
        va=lw(63, 1, fix={0: "B3"}, slur=6),
        vc=lw(63, fix={0: "B2"}, slur=6))
    put(64, vn1=sx("B5 F5 A#5 D5 A5 F5 G#5 D5 G5 D5 F#5 B4", slur=6)
        + " D5+F5/6' r/6 r/12",
        vn2=sx("B4 F4 A#4 D4 A4 F4 G#4 D4 G4 D4 F#4 B3", slur=6)
        + " G#4+D5/6' r/6 r/12",
        va=sx("F3 B3 G#3 D4 G#3 D4 B3 F4 B3 F4 D4 G#4", slur=6)
        + " F4+B4/6' r/6 r/12",
        vc=sx("F2 B2 G#2 D3 G#2 D3 B2 F3 B2 F3 D3 G#3", slur=6)
        + " B2+F3/6' r/6 r/12")
    # the whisper before the return: F D E G# in both violins, p
    put(65, vn1="(F5/2 D5/2 E5/2 G#4/6) r/12 (F5/2 D5/2 E5/2 G#4/6) r/12",
        vn2="(F4/2 D4/2 E4/2 B3/6) r/12 (F4/2 D4/2 E4/2 B3/6) r/12")
    put(66, vn1=w(66, slur=24), vn2=lw(66, slur=24))
    put(67, vn1=w(67, slur=24), vn2=w(67, -1, slur=24),
        va=lw(67, 1, slur=24), vc=lw(67, slur=24))
    # the climb to F7 folds down at beat 3, so bar 69 starts where it lands
    put(68, vn1=sx("F5 D5 E5 G#4 F5 D5 E5 G#5 F6 D6 E6 G#6") + " "
        + sx("F6 D6 E6 G#5 F6 D6 E6 G#5 F6 D6 E6 G#5"),
        vn2=sx("F4 D4 E4 G#3 F4 D4 E4 G#4 F5 D5 E5 G#5") + " "
        + sx("F5 D5 E5 G#4 F5 D5 E5 G#4 F5 D5 E5 G#4"),
        va=lw(68, 1, slur=24), vc=lw(68, slur=24))

    # ---- H: Reprise (bars 5-16 again, a tempo)
    for b in range(69, 79):
        src = b - 64
        put(b, VN1[src], VN2[src], VA[src], VC[src])
    put(79, va=w(79),
        vc="G2/12^ G2+E3/9 G2+E3/3 G2+E3/12 G2+F3/12")
    put(80, va=w(80),
        vc="G2+E3/12 C3/12 F2/12 E2/12")

    # ---- I: Coda
    # the viola climbs two of Chopin's four-note cells, Violin I the rest
    put(81, vn1="r/12 r/2 r/2 (C6/2 F5/2 B5/2) (B5/2 C7/2 F#6/2 B6/2 B5/2 "
        "C6/2 F#5/2 B5/2 B4/2 C5/2 F#4/2 B4/2 B3/2)",
        vn2="r/12 A3+F4/12> A3+F#4/12 r/12",
        va="(C4/2 F3/2 B3/2) (B3/2 C5/2 F4/2 B4/2) B4/2 r/2 r/2 r/2 r/2 r/24",
        vc="D2/12^ r/4 C#3/4 D3/4 D#3/12 D#2/12^")
    put(82, vn1=w(82),
        vn2="r/24 Bb4/12 r/12",
        va="r/12 Bb3+G4/12> Bb3+D4/12 r/12",
        vc="E2/12^ r/4 D#3/4 E3/4 F3/12 F2/12^")
    put(83, vn1=w(83),
        vn2="r/12 F5/9^ F5/3 F5/12^ G5/12^",
        va="r/12 F4/9^ F4/3 F4/12^ G4/12^",
        vc="F2/12^ F3/9^ F3/3 F3/12^ F3+C4/12^")
    # Violin I carries the wind on (an octave down from beat 3, into bar
    # 85); Violin II ends the theme with the viola and cello
    put(84, vn1=sx("E7 A6 D#7 D#6 E6 A5 D#6 D#5 E6 A5 D#6 D#6") + " "
        + sx("E6 A5 D#6 D#5 E6 A5 D#6 D#5 E6 A5 D#6 D#5"),
        vn2="F5/12> C5/12> F5/24>",
        va="F4/12> C4/12> F4/24>",
        vc="F3/12> C3/12> F3/24>")
    # over the dominant: the wind hovers, the bass climbs
    put(85, vn1=w(85, -1, slur=24),
        vc=lw(85, slur=24))
    # the climb's top half goes to Violin II (1st position), the viola
    # takes over the hover
    put(86, vn1=w(86, -1, slur=24),
        vn2="(E5/2 B4/2 D#5/2 A4/2 E5/2 B4/2 D#5/2 A4/2 E5/2 B4/2 D#5/2 A4/2) "
        "(A4/2 D#5/2 B4/2 F5/2 B4/2 F5/2 D#5/2 A5/2 D#5/2 A5/2 F5/2 B5/2)",
        va="(B3/2 F4/2 D#4/2 A4/2 D#4/2 A4/2 F4/2 B4/2 F4/2 B4/2 A4/2 D#5/2) "
        "(E5/2 B4/2 D#5/2 A4/2 E5/2 B4/2 D#5/2 A4/2 E5/2 B4/2 D#5/2 A4/2)",
        vc="F2/48")
    # the last descent in octaves (Chopin doubles it himself)
    put(87, vn1=w(87, -1),
        vn2="C5+E5/6^ r/6 r/12 r/24",
        va=w(87, -2),
        vc="E2+A2/6^ r/6 r/12 r/24")  # the 6/4: F2 falls to E2
    # the plunge goes on down: viola over cello, one octave a half bar
    put(88, vn1="r/24 B4/12^ E5/12^",
        vn2="r/24 A4/12^ G#4/12^",
        va=sx("F4 C4 E4 A3 D4 A3 C4 E3 B3 E3 A3 C3")
        + " B3+E4/12^ B3+D4/12^",
        vc=sx("F3 C3 E3 A2 D3 A2 C3 E2 B2 E2 A2 C2")
        + " E2+B2/12^ E2+B2/12^")

    # ---- J: Finale.  The wind falls through the quartet one last time
    # A lowest (Chopin's A1 E2 C3 E2; A1 is out of range, so the E goes up)
    bass = " ".join(["A2/3> E3/3 C3/3 E3/3"] * 4)
    bass8 = " ".join(["A3/3> E3/3 C4/3 E3/3"] * 4)
    # bar 90: beat 2 on the low E, beat 4 C-E-C-E (Chopin)
    bass90 = "A2/3> E3/3 C3/3 E3/3 E2/3> E2/3 C3/3 E2/3 " \
             "A2/3> E3/3 C3/3 E3/3 C3/3 E2/3 C3/3 E2/3"
    bass90_8 = "A3/3> E3/3 C4/3 E3/3 E3/3> E3/3 C4/3 E3/3 " \
               "A3/3> E3/3 C4/3 E3/3 C4/3 E3/3 C4/3 E3/3"
    put(89, vn1=w(89), va=bass8, vc=bass)
    put(90, vn2=w(90), va=bass90_8, vc=bass90)
    put(91, va=w(91), vc=bass)
    # the left hand's chromatic fall, two octaves up in the violins,
    # over the wind in the viola and cello
    chrom = "A G# G F# F E D# D C# C B Bb".split()
    # staccato as in the user's edition, an accent on each beat
    put(92, vn1=" ".join(f"{p}{5 if i < 10 else 4}/4." + (">" if i % 3 == 0
                                                          else "")
                         for i, p in enumerate(chrom)),
        vn2=" ".join(f"{p}{4 if i < 10 else 3}/4." + (">" if i % 3 == 0
                                                      else "")
                     for i, p in enumerate(chrom)),
        va=w(92, 1),
        vc=w(92))
    # fff: the theme in full chords, open strings ringing
    put(93, vn1="A4/12' A4+E5/9^ A4+E5/3^ A4+E5/12^ A4+F5/12^",
        vn2="A3/12' C4+E4/9^ C4+E4/3^ C4+E4/12^ D4+A4/12^",
        va="A3/12' A3+E4/9^ A3+E4/3^ A3+E4/12^ A3+F4/12^",
        vc="A2/12' A2+E3/9^ A2+E3/3^ A2+E3/12^ A2+F3/12^")
    put(94, vn1="A4+E5/24^ A4+D5/24^",
        vn2="C4+E4/24^ B3+F4/24^",
        va="A3+E4/24^ A3+D4/24^",
        vc="A2+E3/24^ A2+F3/24^")
    # the last gust: a scale up four octaves, cello and viola first,
    # the violins in 32nds to the top
    # one unbroken scale in octaves, as Chopin's: cello (lower line) and
    # viola (upper) to B, the violins from C to G#, faster and faster
    put(95, vn1="A4+E5/36^ " + sx("C5 D5 E5 F#5 G#5 A5 B5 C6 D6 E6 F#6 G#6",
                                  dur=1),
        vn2="C4+E4/36^ " + sx("C4 D4 E4 F#4 G#4 A4 B4 C5 D5 E5 F#5 G#5",
                              dur=1),
        va="A3+E4/12^ (A3/4 B3/4 C4/4 D4/2 E4/2 F#4/2 G#4/2 A4/2 B4/2) r/12",
        vc="A2+E3/12^ (A2/4 B2/4 C3/4 D3/2 E3/2 F#3/2 G#3/2 A3/2 B3/2) r/12")
    # Chopin ends on the two A's alone
    put(96, vn1="A6/12' r/12 r/24", vn2="A5/12' r/12 r/24")

arrange()

# ---------------------------------------------------------------------------
# Dynamics, hairpins and words: Chopin's (from the user's edition), applied
# to every part that plays there.  (bar, tick, mark)
# ---------------------------------------------------------------------------
DYN = [(1, 0, "p"), (3, 0, "pp"), (5, 0, "f"), (13, 0, "f"), (23, 0, "f"),
       (31, 0, "f"), (41, 0, "f"), (45, 0, "fp"), (49, 0, "f"), (55, 0, "f"),
       (61, 0, "ff"), (63, 0, "ff"), (65, 0, "p"), (69, 0, "f"),
       (77, 0, "f"), (83, 12, "ff"), (85, 0, "p"), (87, 0, "f"),
       (89, 0, "ff"), (92, 0, "ff"), (93, 12, "fff")]
# (bar, tick, bar2, tick2, kind); the user's edition, plus three crescendos
# the quartet needs where the edition jumps a level (bars 66-68 p -> f,
# 82 f -> ff, 86 p -> f; other editions print "cresc." there)
HAIR = [(8, 24, 8, 47, "cresc"), (10, 12, 10, 23, "dim"),
        (12, 12, 12, 24, "cresc"), (16, 24, 16, 47, "cresc"),
        (30, 12, 30, 35, "cresc"), (45, 24, 45, 35, "cresc"),
        (45, 36, 45, 47, "dim"), (49, 6, 49, 30, "cresc"),
        (66, 0, 68, 47, "cresc."), (72, 24, 72, 47, "cresc"),
        (74, 12, 74, 23, "dim"), (76, 12, 76, 24, "cresc"),
        (82, 0, 82, 47, "cresc"), (84, 24, 84, 47, "dim"),
        (86, 0, 86, 47, "cresc")]
# per-part extras: (part, bar, tick, mark)
DYN_EXTRA = [("vc", 5, 0, "fz"), ("vc", 69, 0, "fz"), ("vn1", 62, 24, "fz"),
             ("vn2", 62, 24, "fz"), ("va", 62, 24, "fz"),
             ("vc", 62, 24, "fz"), ("vn2", 87, 0, "fz"), ("vc", 87, 0, "fz"),
             # the level after a fz, and entries that must not inherit fp
             ("vc", 5, 12, "f"), ("vc", 69, 12, "f"), ("vn2", 88, 24, "f"),
             ("vc", 88, 0, "f"), ("va", 45, 12, "p"), ("vn2", 47, 0, "p"),
             ("va", 67, 0, "mp"), ("vc", 67, 0, "mp")]
TEXT = [("vc", 1, 0, "espressivo")]
TEXT += [(pid, 3, 0, "sotto voce") for pid in ("vn1", "vn2", "va", "vc")]
TEXT += [("va", 5, 12, "marcato"), ("va", 69, 12, "marcato"),
         ("vn1", 65, 0, "sotto voce"), ("vn2", 65, 0, "sotto voce"),
         ("vn1", 69, 0, "a tempo")]

# Tempo: quarter-note bpm for the MIDI.  METRONOMES / TEMPO_WORDS /
# TEMPO_TEXT are what the score shows.
TEMPI = [(1, 0, 60), (2, 24, 34), (3, 0, 58), (4, 0, 54), (4, 12, 50),
         (4, 24, 44), (4, 36, 30), (5, 0, 138),
         (68, 0, 132), (68, 12, 124), (68, 24, 114), (68, 36, 100),
         (69, 0, 138)]
METRONOMES = [(1, 0, 60, "quarter"), (5, 0, 69, "half")]
TEMPO_WORDS = {5: ["Allegro con brio"]}
TEMPO_TEXT = [(4, 0, "rit."), (68, 12, "rit.")]
SECTIONS = [(1, None, "Introduction 引子"), (5, "A", "Theme 主题"),
            (13, "B", "Theme 主题 · C 大调"), (23, "C", "Episode 插部 · e 小调"),
            (31, "D", "Episode 插部"), (41, "E", "Development 展开部"),
            (49, "F", "Build-up 推进"), (61, "G", "Climax 高潮"),
            (69, "H", "Reprise 再现"), (81, "I", "Coda 尾声"),
            (89, "J", "Finale 终曲")]
DOUBLE_BARS = {4}
# two bars a system, four systems a page (page 1: the Lento + 3 systems;
# page 9 holds three, bars 67-68 are too tall for a fourth)
SYSTEM_BREAKS = tuple(range(5, 96, 2))
PAGE_BREAKS = (11, 19, 27, 35, 43, 51, 59, 67, 73, 81, 89)
# 8va lines (display only; MusicXML and MIDI keep the sounding pitch):
# (part, bar, bar) for whole bars, (part, bar, tick, bar2, tick2) for spans
OTTAVA = [("Violin I", 19, 21)] + [("Violin I", b, b)
                                   for b in (31, 38, 45, 63, 89)]
OTTAVA += [("Violin I", b, 12, b, 35) for b in (11, 17, 27, 28, 49, 55, 57,
                                               75, 82)]
OTTAVA += [("Violin I", 12, 12, 12, 35), ("Violin I", 76, 12, 76, 35),
           ("Violin I", 30, 24, 30, 35), ("Violin I", 60, 24, 60, 47),
           ("Violin I", 81, 16, 81, 35), ("Violin I", 83, 12, 84, 23),
           ("Violin II", 18, 12, 18, 35), ("Violin II", 47, 0, 47, 23),
           ("Violin II", 56, 12, 56, 35)]
# bar 95: the violin I run's tuplet number above, the cello's below
STEMS = {("Violin I", 95): "up", ("Violoncello", 95): "down"}
# intentional: octave doublings of one line (the theme in octaves, the bass
# theme of bars 49-57 in octaves, the fff chords at the end)
_DOUBLED = {("va", "vc"): (5, 6, 13, 14, 23, 24, 31, 32, 49, 50, 51, 52,
                           53, 54, 55, 56, 57, 69, 70, 77, 78, 84),
            ("vn2", "va"): (13, 31, 77, 83, 84),
            ("vn2", "vc"): (13, 31, 77, 83, 84),
            ("vn1", "va"): (14, 24, 32, 78), ("vn1", "vc"): (14, 32, 78)}
_DOUBLED[("va", "vc")] += (88,)
PARALLEL_OK = {(a, b, bar) for (a, b), bars in _DOUBLED.items()
               for bar in bars}
PARALLEL_OK |= {(a, b, bar) for a in ("vn1", "vn2", "va", "vc")
                for b in ("vn1", "vn2", "va", "vc") for bar in range(93, 97)}
# Chopin's own b9: the theme's F over the E pedal (bars 59-60)
CLASH_OK = {(59, "va", "vc"), (60, "va", "vc")}

RANGES = {"vn1": ("G3", "E7"), "vn2": ("G3", "B6"), "va": ("C3", "C6"),
          "vc": ("C2", "A4")}

PARTS = [
    dict(id="vn1", name="Violin I", abbr="Vln. I", data=VN1,
         inst=instrument.Violin, kind="violin", program=40, clefs=[]),
    dict(id="vn2", name="Violin II", abbr="Vln. II", data=VN2,
         inst=instrument.Violin, kind="violin", program=40, clefs=[]),
    dict(id="va", name="Viola", abbr="Vla.", data=VA,
         inst=instrument.Viola, kind="viola", program=41,
         clefs=[(1, 0, "alto")]),
    dict(id="vc", name="Violoncello", abbr="Vc.", data=VC,
         inst=instrument.Violoncello, kind="cello", program=42,
         clefs=[(1, 0, "tenor"), (3, 0, "bass")]),
]

META = dict(
    title="冬风", title_latin="Winter Wind",
    subtitle="练习曲 Op. 25 No. 11 · 弦乐四重奏",
    subtitle_en="Étude in A minor, Op. 25 No. 11 — for String Quartet",
    composer="肖邦 F. Chopin", lyricist="", artist="",
    original="钢琴练习曲 Op. 25 No. 11",
    instrumentation=[("Violin I", "第一小提琴"), ("Violin II", "第二小提琴"),
                     ("Viola", "中提琴"), ("Violoncello", "大提琴")],
    key="A Minor · a小调", tempo="Lento · Allegro con brio 𝅗𝅥 = 69",
    duration="ca. 3′00″", year="2026", tempo_text="Lento",
    # 24 sextuplets a bar: tighter spacing so two bars fit a system
    # and slightly closer staves so four systems fit every page
    style={"measureSpacing": 1.0, "minNoteDistance": 0.3,
           "staffDistance": 6.5, "akkoladeDistance": 6.5,
           "minSystemDistance": 8.5, "minSystemSpread": 6,
           "minStaffSpread": 5})


def _tuplet_flags(musicxml):
    """Per part, in order: does each tuplet show its number?"""
    import re
    x = open(musicxml, encoding="utf-8").read()
    out = []
    for body in re.findall(r"<part id=[^>]*>(.*?)</part>", x, re.S):
        out.append(['show-number="none"' not in t.group(0) for t in
                    re.finditer(r'<tuplet [^>]*type="start"[^>]*>', body)])
    return out


def _mscx_hook(x):
    """MS4 ignores MusicXML show-number="none": hide the "6" on every
    sextuplet after the first of a run (and on beamed triplets' brackets
    it already follows bracket="no")."""
    import re
    flags = _tuplet_flags(os.path.join(OUT, f"{NAME}_弦乐四重奏.musicxml"))
    staves = [mo for mo in re.finditer(r'<Staff id="(\d+)">.*?</Staff>', x,
                                       re.S) if "<Measure>" in mo.group(0)]
    assert len(staves) == len(flags), (len(staves), len(flags))
    out, last = [], 0
    for mo, fl in zip(staves, flags):
        body = mo.group(0)
        tups = list(re.finditer(r"<Tuplet>.*?</Tuplet>", body, re.S))
        assert len(tups) == len(fl), (mo.group(1), len(tups), len(fl))
        new, k = [], 0
        for t, show in zip(tups, fl):
            new.append(body[k:t.start()])
            tb = t.group(0)
            if not show:
                tb = re.sub(r"\s*<Number>.*?</Number>", "", tb, flags=re.S)
                tb = tb.replace("</Tuplet>", "  <numberType>2</numberType>\n"
                                "            <bracketType>2</bracketType>\n"
                                "            </Tuplet>")
            new.append(tb)
            k = t.end()
        new.append(body[k:])
        out.append(x[last:mo.start()])
        out.append("".join(new))
        last = mo.end()
    out.append(x[last:])
    return "".join(out)


META["mscx_hook"] = _mscx_hook


# ---------------------------------------------------------------------------
# Dynamics placement: a mark goes under a part's first note at or after it
# ---------------------------------------------------------------------------
def distribute(parsed):
    marks = sorted(DYN)
    for p in PARTS:
        evs = parsed[p["id"]]
        onsets = [e["abs"] for e in evs if e["pitches"] is not None]
        dyn = []
        for i, (b, t, mk) in enumerate(marks):
            a = (b - 1) * BAR + t
            z = ((marks[i + 1][0] - 1) * BAR + marks[i + 1][1]
                 if i + 1 < len(marks) else NBARS * BAR)
            hit = next((o for o in onsets if a <= o < z), None)
            if hit is not None:
                dyn.append((hit // BAR + 1, hit % BAR, mk))
        for pid, b, t, mk in DYN_EXTRA:
            if pid == p["id"]:
                dyn = [d for d in dyn if (d[0], d[1]) != (b, t)]
                dyn.append((b, t, mk))
        hair, words, wordy = [], [], []
        for b, t, b2, t2, kind in HAIR:
            a, z = (b - 1) * BAR + t, (b2 - 1) * BAR + t2
            inside = [o for o in onsets if a <= o <= z]
            held = any(e["pitches"] and e["dur"] >= 24 and e["abs"] <= z
                       and e["abs"] + e["dur"] > a for e in evs)
            if kind.endswith("."):  # over several bars: a word, not a wedge
                if inside:
                    words.append((inside[0] // BAR + 1, inside[0] % BAR, kind))
                    wordy.append((b, t, b2, t2, kind.rstrip(".")))
                continue
            if len(inside) >= 2:
                s, e = inside[0], inside[-1]
                hair.append((s // BAR + 1, s % BAR, e // BAR + 1, e % BAR,
                             kind))
            elif held:  # a long note swells or fades too
                hair.append((b, t, b2, t2, kind))
        p["dyn"] = sorted(dyn)
        p["hair"] = hair + wordy   # all of them shape the MIDI
        p["hair_print"] = hair     # the long ones print as "cresc."
        p["words_below"] = words
        p["text"] = [(b, t, x) for pid, b, t, x in TEXT if pid == p["id"]]


def parse_all():
    parsed = {p["id"]: engine.parse_part(p["data"], NBARS) for p in PARTS}
    distribute(parsed)
    return parsed


def main():
    os.makedirs(OUT, exist_ok=True)
    parsed = parse_all()
    problems, stops, clashes, parallels = engine.check(sys.modules[__name__],
                                                       parsed)
    for x in problems:
        print("RANGE:", x)
    for x in stops:
        print("STOP:", x)
    for x in clashes:
        print("CLASH:", x)
    for x in parallels:
        print("PARALLEL:", x)
    if "--check" in sys.argv:
        return
    song = sys.modules[__name__]
    base = os.path.join(OUT, f"{NAME}_弦乐四重奏")
    sc = engine.build_score(song, parsed)
    sc.write("musicxml", fp=base + ".musicxml")
    engine.polish(song, base + ".musicxml")
    hollywood.polish_musicxml(base + ".musicxml", META)
    engine.verify_bars(song, base + ".musicxml")
    ids = [p["id"] for p in PARTS]
    engine.write_midi(song, os.path.join(OUT, f"{NAME}_弦乐四重奏_全轨.mid"),
                      ids, parsed)
    for p in PARTS:
        engine.write_midi(song, os.path.join(
            OUT, f"{NAME}_分轨_{p['name'].replace(' ', '')}.mid"),
            [p["id"]], parsed)
    print(f"written to {OUT} ({engine.seconds(song):.0f} s)")
    if "--pdf" in sys.argv:
        write_pdf()


def write_pdf(png_dir=None):
    """Hollywood-standard full score PDF (cover + score + header/footer)."""
    src = os.path.join(OUT, f"{NAME}_弦乐四重奏.musicxml")
    dst = os.path.join(OUT, f"{NAME}_弦乐四重奏_总谱.pdf")
    n = hollywood.render_pdf(src, dst, META, png_dir=png_dir)
    print(f"PDF: {dst} ({n} pages)")


if __name__ == "__main__":
    main()
