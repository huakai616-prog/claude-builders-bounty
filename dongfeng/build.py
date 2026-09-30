#!/usr/bin/env python3
"""冬风 — 肖邦《a 小调练习曲》Op. 25 No. 11，弦乐四重奏改编（全曲 96 小节）

Generates, from one source of truth:
  * MusicXML full score for Sibelius (MusicXML 4.0, 11 x 17 in house layout)
  * Hollywood-standard full score PDF with cover (tools/hollywood, --pdf)
  * full string-quartet MIDI (four named tracks, tempo map) for ACE Studio
  * GM preview mp3 (--mp3)

Key: A minor (original key), alla breve.  Lento (1-4), then Allegro con
brio, half = 69 (Chopin's own marking).
Chopin's text lives in chopin.py (sounding pitch, bar by bar); the quartet
parts below pull the right-hand "wind" figuration from it with W() and L().

Token syntax (see engine.py): 24 ticks = a quarter, a bar = 96 ticks.
  F6/4 sextuplet 16th, A4/8 triplet 8th, C5/6 16th, E4/18 dotted 8th,
  E4/24 quarter, E4/48 half, E4/96 whole, A2+E3/24 double stop, r/24 rest,
  ( ) slur, ~ tie; marks > ^ . _ % A D U T , ; "||" = second voice.

  python3 dongfeng/build.py --check   # prints nothing when the parts are clean
  python3 dongfeng/build.py --harm    # harmony of every beat vs Chopin (review)
  python3 dongfeng/build.py           # MusicXML + MIDI
  python3 dongfeng/build.py --pdf     # + Hollywood PDF
  python3 dongfeng/build.py --mp3     # + GM preview
  python3 dongfeng/build.py --parts   # + players' parts (A4)
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hollywood"))
import chopin  # noqa: E402
import engine  # noqa: E402
from engine import BAR, fit, shift  # noqa: E402
import hollywood  # noqa: E402

NAME = "冬风"
NBARS = 96

# practical ranges for fast figuration, used by W() / L() to fold notes in
VN = ("G3", "D7")
VA = ("C3", "A5")
VC = ("C2", "A4")


# ---------------------------------------------------------------------------
# Helpers that pull Chopin's figuration from chopin.py
# ---------------------------------------------------------------------------
def fig(b, hand="R"):
    s = (chopin.RH if hand == "R" else chopin.LH)[b]
    assert "@" not in s, f"bar {b} {hand}H is not a figuration bar"
    return s.replace("|", " ").split()


def W(b, g0=0, g1=4, sh=0, rng=None, slur=6, first="", hand="R",
      marks=None, sub=None):
    """Chopin's sextuplet figuration of bar b, beats g0..g1-1, shifted by sh
    octaves; notes outside rng are folded in by octaves; slurred in groups
    of `slur` notes (one bow per beat); `first` = marks on the first note;
    `sub` = {index-in-bar: pitch} replaces single notes."""
    ps = fig(b, hand)[g0 * 6:g1 * 6]
    ps = [shift(p, sh) for p in ps]
    for k, p in (sub or {}).items():
        ps[k - g0 * 6] = p
    if rng:
        ps = [fit(p, *rng) for p in ps]
    out = []
    for i, p in enumerate(ps):
        t = f"{p}/4"
        if i == 0:
            t += first
        if marks and i in marks:
            t += marks[i]
        if slur and i % slur == 0:
            t = "(" + t
        if slur and (i % slur == slur - 1 or i == len(ps) - 1):
            t += ")"
        out.append(t)
    return " ".join(out)


def L(b, g0=0, g1=4, sh=0, rng=None, **kw):
    return W(b, g0, g1, sh, rng, hand="L", **kw)


def R(t):
    """Rest of t ticks, written beat by beat."""
    out = []
    while t > 0:
        d = 48 if t >= 48 else 24 if t >= 24 else t
        out.append(f"r/{d}")
        t -= d
    return " ".join(out)


REST = "r/96"
VN1, VN2, VLA, VLC = {}, {}, {}, {}

# ===========================================================================
# I. Introduction (Lento), bars 1-4
#    The theme alone in the viola (sul G, veiled), then a frozen chorale:
#    all four sul tasto, senza vibrato, pp, the melody in Violin I.
# ===========================================================================
VLA[1] = "(E4/24_ E4/18_ E4/6_ E4/24_ F4/24_)"
VLA[2] = "(E4/24 C4/24 E4/48%)"
for P in (VN1, VN2, VLC):
    P[1] = REST
    P[2] = "r/48 r/48%"
VN1[3] = "(E4/24_ E4/18_ E4/6_ E4/24_ F4/24_)"
VN2[3] = "(C4/24_ C4/18_ C4/6_ C4/24_ C4/24_)"
VLA[3] = "(G3/24_ G3/18_ G3/6_ G3/24_ A3/24_)"
VLC[3] = "(C3/24_ C3/18_ C3/6_ C3/24_ F2/24_)"
VN1[4] = "(E4/24 C4/24 E4/48%)"
VN2[4] = "(C4/24 A3/24 C4/24 D4/24%)"
VLA[4] = "(G3/24 F3/24 G3/24 G#3/24%)"
VLC[4] = "(C2/24 F2/24 C3/24 B2/24%)"

# ===========================================================================
# A. Theme (Allegro con brio), bars 5-22
#    5-8: the wind falls four octaves; the quartet hands it down one bar
#    at a time, an octave under Chopin: Violin I -> Violin II -> Viola ->
#    Cello, while the others play the march.
# ===========================================================================
VN1[5] = W(5, sh=-1, first=">")
VN2[5] = "r/24 C4+E4/18> C4+E4/6. C4+E4/24_ C4+F4/24_"
VLA[5] = "r/24 E3+A3/18> E3+A3/6. E3+A3/24_ F3+A3/24_"
VLC[5] = "A2+E3+A3/24^D A2/72"

VN1[6] = "C4+E4/24_ C4/24_ C4+E4/48_"
VN2[6] = W(6, sh=-1)
VLA[6] = "A3/24_ E3+A3/24_ A3/48_"
VLC[6] = "A2/24_ E2/24_ A2/48_"

VN1[7] = REST
VN2[7] = "r/24 E4/18 E4/6 E4/24 F4/24"
VLA[7] = W(7, sh=-1, rng=VA)
VLC[7] = "A2/24. A2+E3/18 A2+E3/6 A2+E3/24 A2+F3/24"

VN1[8] = REST
VN2[8] = "E4/24 r/24 r/48"
VLA[8] = "E3+A3/48 E3/48"
VLC[8] = W(8, sh=-1)

VN1[9] = W(9, rng=VN, first=">")
VN2[9] = "r/24 D4/18> D4/6 C4/24 r/24"
VLA[9] = "r/24 F3/18> F3/6 F3/24 r/24"
VLC[9] = "G#2/48> r/24 A2/24>"

VN1[10] = W(10, rng=VN, first=">")
VN2[10] = "r/24 D4/8 D4/8 D4/8 C4/24 r/24"
VLA[10] = "r/24 G3/8 F3/8 E3/8 E3/24 r/24"
VLC[10] = "G#2/24> r/48 A2/24>"

VN1[11] = W(11, rng=VN)
VN2[11] = "r/24 (E4/8 G#4/8 C#5/8) D#4+A4/24 B3/24"
VLA[11] = "r/24 G#3/24 B3/48"
VLC[11] = "B2/72 B2/24>"

VN1[12] = W(11, 0, 2) + " E7/24>! r/24"
VN2[12] = "r/24 (B3+G#4/8 A#3+F##4/8 B3+G#4/8) G#4+E5/24. r/24"
VLA[12] = "r/48 B3+E4/24. r/24"
VLC[12] = "E2+B2/24 r/24 E3/24. r/24"

# 13-16 (f): the same fall, now in octaves: (Vln I, Vln II) -> (Vln I, Vla)
#    -> Vla -> Vc, each line keeping Chopin's step from bar to bar; in 15
#    the cello keeps Chopin's C bass and the march, whoever else is free
#    plays the march too.
VN1[13] = W(13, sh=-1, first=">")
VN2[13] = W(13, sh=-2, first=">")
VLA[13] = "r/24 C4+E4/18> C4+E4/6. C4+E4/24_ C4+F4/24_"
VLC[13] = "A2+E3+A3/24^D A2+E3/18> A2+E3/6. A2+E3/24_ A2+F3/24_"

VN1[14] = W(14, sh=-1)
VN2[14] = "C4+E4/24_ C4/24_ C4+E4/48_"
VLA[14] = W(14, sh=-2, rng=VA)
VLC[14] = "A2/24_ E2/24_ A2/48_"

VN1[15] = REST
VN2[15] = "r/24 G3+E4/18 G3+E4/6 G3+E4/24 G3+F4/24"
VLA[15] = W(15, sh=-1, rng=VA)
VLC[15] = "C2/24. G2+E3/18> G2+E3/6 G2+E3/24_ G2+F3/24_"

VN1[16] = REST
VN2[16] = "C4+E4/24 r/24 E4/48"
VLA[16] = "G3+E4/24 C3+C4/24 C3+G3/48"
VLC[16] = W(16, sh=-1)

# 17-22: the sequence climbs; the two violins answer each other (17 / 18),
#    the lower three play Chopin's left hand (bass line, triplet chords,
#    rolled chords), and the wind runs up to bar 23.
VN1[17] = W(17)
VN2[17] = "r/24 Bb3+E4/8. r/16 Bb3+Eb4/24A. r/24"
VLA[17] = "r/24 G3/8. r/16 C#3+G3/24A. r/24"
VLC[17] = "C2/24. r/8 B2/8 C3/8 C#3/24 C#2/24"

VN1[18] = "r/24 D4+G4/8. r/16 Db4+G4/24A. r/24"
VN2[18] = W(18)
VLA[18] = "r/24 Bb3/8. r/16 Eb3+Bb3/24A. r/24"
VLC[18] = "D2/24. r/8 C#3/8 D3/8 Eb3/24 Eb2/24"

VN1[19] = W(19, slur=4)   # a bow per 4-note cell: the ninths fall on bow changes
VN2[19] = "r/24 C5/18> C5/6 C5/24> r/24"
VLA[19] = "r/24 C4/18> C4/6 C4/24> r/24"
VLC[19] = "E2/72 C2/24"

VN1[20] = W(20)
VN2[20] = "r/48 (D4/18 E4/6 F4/24)"
VLA[20] = "r/24 (A4/18 A3/6~ A3/48)"
VLC[20] = "F2/24. r/24 F3/48"

# 21: the peak (E7 in Chopin) comes down an octave from beat 2 on, so the
#     line meets bar 22-23 (written an octave down) without a jump
VN1[21] = W(21, sh=-1, sub={19: "B4"})
VN2[21] = "r/24 (B3/8 F4/8 A4/8) G4/48"
VLA[21] = "r/24 G3/24 r/24 B3+F4/24"
VLC[21] = "G2/72 G2/24"

VN1[22] = W(22, sh=-1)
VN2[22] = "r/24 E4+C5/24A. r/48"
VLA[22] = "r/24 G3+E4/24A. r/48"
VLC[22] = "C2/24 C3+G3/24A. r/48"

# ===========================================================================
# B. The theme in E minor, bars 23-40
# ===========================================================================
# 23-26: the single relay again, a fifth higher
VN1[23] = W(23, sh=-1, first=">")
VN2[23] = "r/24 G4+B4/18> G4+B4/6. G4+B4/24_ G4+C5/24_"
VLA[23] = "r/24 E3+B3/18> E3+B3/6. E3+B3/24_ E3+C4/24_"
VLC[23] = "E2+B2+G3/24^D E2/72"

VN1[24] = "E4+B4/24_ B3+G4/24_ E4+B4/48_"
VN2[24] = W(24, sh=-1)
VLA[24] = "E3+G3/24_ E3+G3/24_ E3+G3/48_"
VLC[24] = "E2/24_ B2/24_ E2/48_"

VN1[25] = REST
VN2[25] = "r/24 B3/18 B3/6 B3/24 C4/24"
VLA[25] = W(25, sh=-1, rng=VA)
VLC[25] = "E2/24. E2+B2/18 E2+B2/6 E2+B2/24 E2+C3/24"

VN1[26] = REST
VN2[26] = "B3/24 r/72"
VLA[26] = "E3+B3/48 B3/48"
VLC[26] = W(26, sh=-1, rng=VC)

# 27-28: the rising arpeggio starts low, so the viola begins and ends each
#    bar and Violin I takes the top
VN1[27] = "r/24 " + W(27, 1, 3) + " r/24"
VN2[27] = "r/24 D#4+C5/18> D#4+C5/6 E4+C5/24 r/24"
VLA[27] = W(27, 0, 1) + " r/48 " + W(27, 3, 4)
VLC[27] = "D#2/48> E3/24 E2/24>"

VN1[28] = "r/24 " + W(28, 1, 3) + " r/24"
VN2[28] = "r/24 D#4+D5/8 D#4+C5/12 D#4+B4/4 E4+B4/24 r/24"
VLA[28] = W(28, 0, 1) + " r/48 " + W(28, 3, 4)
VLC[28] = "D#2/48> E3/24 E2/24>"

VN1[29] = W(29, 0, 3) + " r/24"
VN2[29] = "r/24 (B3/8 D#4/8 G#4/8) A#3+E4/24 r/24"
VLA[29] = "r/24 F#3/24 F#3/24 " + W(29, 3, 4)
VLC[29] = "F#2/72 F#2/24"

VN1[30] = W(29, 0, 2) + " B6/24>! r/24"
VN2[30] = "r/24 (F#4+D#5/8 E#4+C##5/8 F#4+D#5/8) D#4+B4/24. r/24"
VLA[30] = "r/24 (F#3+D#4/8 E#3+C##4/8 F#3+D#4/8) D#3+B3/24. r/24"
VLC[30] = "B2/24 r/24 B2/24. r/24"

# 31-34 (f): octaves in the violins, then the wind sinks into viola and
#    cello (33-34) while Violin II holds its open G as the bass of G major
VN1[31] = W(31, sh=-1, first=">")
VN2[31] = W(31, sh=-2, rng=VN, first=">")
VLA[31] = "r/24 G3+B3/18> G3+B3/6. G3+B3/24_ G3+C4/24_"
VLC[31] = "E2+B2+G3/24^D E2+B2/18> E2+B2/6. E2+B2/24_ E2+C3/24_"

VN1[32] = W(32, sh=-1, rng=VN)
VN2[32] = "E4+B4/24_ B3+G4/24_ E4+B4/48_"
VLA[32] = "E3+G3/24_ E3+G3/24_ E3+G3/48_"
VLC[32] = "E2/24_ B2/24_ E2/48_"

VN1[33] = "r/24 D4+B4/18> D4+B4/6. D4+B4/24_ E4+C5/24_"
VN2[33] = REST
VLA[33] = W(33)
VLC[33] = "G2/24. " + W(33, 1, 4, sh=-1)

VN1[34] = "D4+B4/24 r/24 D4/48"
VN2[34] = REST
VLA[34] = W(34, rng=VA)
VLC[34] = "D2+B2/24> G2/24 G2+D3/48"

# 35-36: the arpeggio figure over a chromatic bass (G F# G Ab-G#, A G# A Bb-A#)
VN1[35] = W(35, 0, 3) + " r/24"
VN2[35] = "r/24 D4+B4/8> r/16 D4+Bb4/24A r/24"
VLA[35] = "r/24 D3+B3/8> r/16 Ab3+D4/24A " + W(35, 3, 4)
VLC[35] = "G2/24. r/8 F#2/8 G2/8 Ab2/24 G#2/24>"

VN1[36] = W(36, 0, 3) + " r/24"
VN2[36] = "r/24 F4+D5/8> r/16 G#4+D5/24A r/24"
VLA[36] = "r/24 F3+D4/8> r/16 F3+D4/24A " + W(36, 3, 4)
VLC[36] = "A2/24. r/8 G#2/8 A2/8 Bb2/24 A#2/24>"

# 37: the wind now climbs through the quartet: viola -> Violin II -> Violin I,
#     over the cello's march on G
VN1[37] = "r/48 " + W(37, 2, 4, slur=4)
VN2[37] = "r/24 (F4/4 D4/4) (E5/4 G4/4 D5/4 F4/4) G4/24> r/24"
VLA[37] = "(E4/4 G3/4 D4/4 F3/4) (G4/4 E4/4) r/24 r/48"
VLC[37] = "B2/24. G3/18> G3/6 G3/24> G2/24"

VN1[38] = W(38, rng=VN)
VN2[38] = "r/24 (E4/8 C5/8 G#5/8) r/24 (Ab4/8 Db5/8 Ab5/8)"
VLA[38] = "r/24 (E3/8 C4/8 G#4/8) r/24 (F3+Ab3/8 Db4/8 Ab4/8)"
VLC[38] = "C2/48 F2/48"

VN1[39] = W(39)
VN2[39] = "r/24 G3/24 r/24 B3+F4/24"
VLA[39] = "r/24 (C4/8 E4/8 G4/8) r/24 G3+D4/24"
VLC[39] = "G2/24. r/24 G2/24. r/24"

VN1[40] = W(40, 0, 3) + " (E5/4 G4/4) (A5/4 E5/4 G5/4 C5/4)"
VN2[40] = "C5+E5/24A r/72"
VLA[40] = "G3+E4/24A r/72"
VLC[40] = "C2+G2+E3/24A r/72"

# ===========================================================================
# C. The theme on top, bars 41-48: the violins sing the march, the wind
#    falls through viola and cello (Chopin's left hand)
# ===========================================================================
VN1[41] = "G5/24 G5/18> G5/6 G5/24_ A5/24_"
VN2[41] = "E5/24 G4+E5/18> G4+E5/6 G4+E5/24_ A4+E5/24_"
VLA[41] = L(41, 0, 3) + " r/24"
VLC[41] = "A2/72 " + L(41, 3, 4)

VN1[42] = "G5/24_ E5/24_ G5/48_"
VN2[42] = "G4+E5/24_ G4+C#5/24_ G4+E5/48_"
VLA[42] = "A3/96"
VLC[42] = L(42, 0, 2) + " " + L(42, 2, 4, sh=1)

VN1[43] = "Bb5/24 Bb5/18> Bb5/6 Bb5/24_ C6/24_"
VN2[43] = "G5/24 Bb4+G5/18> Bb4+G5/6 Bb4+G5/24_ C5+G5/24_"
VLA[43] = L(43)
VLC[43] = "C2/96"

VN1[44] = "Bb5/24_ G5/24_ Bb5/48_"
VN2[44] = "Bb4+G5/24_ Bb4+E5/24_ Bb4+G5/48_"
VLA[44] = "C4/96"
VLC[44] = L(44, 0, 3) + " " + L(44, 3, 4, sh=1)

# 45-48: A-flat, then E major: a quiet interlude, the melody in the viola
VN1[45] = W(45)
VN2[45] = "r/48 C4/48"
VLA[45] = "r/24 (Eb4/18 Eb4/6 Eb4/24 Ab4/18 C4/6"
VLC[45] = "Eb2/48 Eb3/48"

VN1[46] = W(46)
VN2[46] = "r/48 C4/24 r/24"
VLA[46] = "Eb4/24 Bb3/18 Eb4/6 C4/24) r/24"
VLC[46] = "Eb3/48 Ab2+Eb3/24A r/24"

VN1[47] = REST
VN2[47] = W(47)
VLA[47] = "r/24 (B3/18 B3/6 B3/24 E4/12) r/6 G#3/6"
VLC[47] = "B2/48 B2+G#3/24 r/24"

VN1[48] = REST
VN2[48] = W(48)
VLA[48] = "(B3/24 F#3/8 G#3/8 A3/8 G#3/24) r/24"
VLC[48] = "B2/48 E2+B2/24A r/24"

# ===========================================================================
# D. Development, bars 49-60
# ===========================================================================
# 49-52: Chopin's left hand is a bass line in octaves; here it is tripled
#    (cello, viola, Violin II), marcato, under the wind
VN1[49] = W(49)
VN2[49] = REST
VLA[49] = "E4/24> (B3/8 G#3/8 B3/8) E3/12. r/6 E3/6 F#3/18> E3/6"
VLC[49] = "E3/24> (B2/8 G#2/8 B2/8) E2/12. r/6 E2/6 F#2/18> E2/6"

VN1[50] = REST
VN2[50] = "(D5/4 G4/4 C5/4) (C5/4 F5/4 C5/4) " + W(50, 1, 4)  # C4 -> C5: no G-to-E string leap
VLA[50] = "Eb3/24> C3/24 Eb3/24 (F3/8 F#3/8 G3/8)"
VLC[50] = "Eb2/24> C2/24 Eb2/24 (F2/8 F#2/8 G2/8)"

VN1[51] = W(51, rng=("G3", "B6"))
VN2[51] = REST
VLA[51] = "Ab3/24> (Eb3/8 C3/8 Eb3/8) Ab3/12. r/6 Ab3/6 Bb3/18> Ab3/6"
VLC[51] = "Ab2/24> (Eb2/8 C2/8 Eb2/8) Ab2/12. r/6 Ab2/6 Bb2/18> Ab2/6"

VN1[52] = REST
VN2[52] = W(52, sub={3: "E5"})
VLA[52] = "G3/24> E3/24 G3/24 (A3/8 A#3/8 B3/8)"
VLC[52] = "G2/24> E2/24 G2/24 (A2/8 A#2/8 B2/8)"

# 53-54: Chopin's rolled chords round the circle of fifths become
#    strummed triple stops in the lower three
VN1[53] = W(53)
VN2[53] = W(53, first=">")
VLA[53] = "C4/24> G3+E4/24>A F3+C4+A4/24>A A3+F#4/24>A"
VLC[53] = "C3/24> C2+G2+E3/24>A F2+C3+A3/24>A B2+D#3/24>A"

VN1[54] = W(54)
VN2[54] = W(54)
VLA[54] = "G3+E4/24>A C#4+A4/24>A D4+A4/24>A C4+A4/24>A"
VLC[54] = "E2+B2+G3/24>A A2+E3+C#4/24>A D2+A2+D3/24>A A2+E3+C4/24>A"

VN1[55] = W(55)
VN2[55] = "D4/24> (F4/24 A#3/12) r/6 (C4/6 B3/24)"
VLA[55] = "D3/24> (F4/24 A#3/12) r/6 (C4/6 B3/24)"
VLC[55] = "D2/24> (F3/24 A#2/12) r/6 (C3/6 B2/24)"

VN1[56] = W(56)
VN2[56] = "D#4/24> (F#4/24 A3/12) r/6 (D4/6 C4/24)"
VLA[56] = "D#3/24> (F#4/24 A3/12) r/6 (D4/6 C4/24)"
VLC[56] = "D#2/24> (F#3/24 A2/12) r/6 (D3/6 C3/24)"

# 57-60: over a long E pedal the viola sings Chopin's tenor lament, and at
#    59 the theme returns on F, a half step too high, cresc. to the storm
VN1[57] = W(57)
VN2[57] = REST
VLA[57] = "r/24 (B3/18 E4/6 D4/48)"
VLC[57] = "E2/24^ E3/72"

VN1[58] = REST
VN2[58] = W(58, rng=VN)
VLA[58] = "r/24 (G#3/18 C#4/6 B3/48)"
VLC[58] = "E2/96"

VN1[59] = W(59, sh=1, first=">")
VN2[59] = W(59, rng=VN, first=">")
VLA[59] = "r/24 F3/18> F3/6 F3/24> G3/24>"
VLC[59] = "E2/96T~"

VN1[60] = W(60)
VN2[60] = "F4/24> D4/24> F4/48>"
VLA[60] = "F3/24> D3/24> F3/48>"
VLC[60] = "E2/96T"

# ===========================================================================
# E. The storm, bars 61-64: both of Chopin's hands in octaves, the violins
#    falling, viola and cello rising; each wave breaks on a diminished
#    chord and half a bar of silence
# ===========================================================================
VN1[61] = W(61, sh=-1, first=">")
VN2[61] = W(61, sh=-2, first=">")
VLA[61] = L(61, sh=1, first=">")
VLC[61] = L(61, first=">")

VN1[62] = ("(F5/4 B4/4 E5/4 G#4/4 D#5/4 B4/4) (D5/4 G#4/4 C#5/4 G4/4 C5/4 F4/4) "
           "F5+B5/12^ r/12 r/24")
VN2[62] = ("(B3/4 F4/4 D4/4 G#4/4 D4/4 G#4/4) (F4/4 B4/4 F4/4 B4/4 G4/4 D5/4) "
           "D5+G#5/12^ r/12 r/24")
VLA[62] = "D4+G#4/48T D4+G#4/12^ r/12 r/24"
VLC[62] = "B2+F3/48T B2+F3/12^ r/12 r/24"

VN1[63] = W(63, sh=-1, first=">")
VN2[63] = W(63, sh=-2, rng=VN, first=">")
VLA[63] = L(63, sh=1, rng=VA, first=">")
VLC[63] = L(63, rng=VC, first=">")

VN1[64] = ("(B4/4 F4/4 A#4/4 D4/4 A4/4 F4/4) (G#4/4 D4/4 G4/4 D4/4 F#4/4 B3/4) "
           "D5+F5/12^ r/12 r/24")
VN2[64] = ("(F4/4 B4/4 G#4/4 D5/4 G#4/4 D5/4) (B4/4 F5/4 B4/4 F5/4 D5/4 G#5/4) "
           "G#4+D5/12^ r/12 r/24")
VLA[64] = "F4+B4/48T F4+B4/12^ r/12 r/24"
VLC[64] = "B2+G#3/48T B2+G#3/12^ r/12 r/24"

# ===========================================================================
# F. The eye of the storm, bars 65-68: sul ponticello, the four-note cell
#    in both violins, a ghostly E pedal, the chromatic slide, and the
#    wind gathering again (rit.)
# ===========================================================================
VN1[65] = "(F5/4 D5/4 E5/4 G#4/12) r/24 (F5/4 D5/4 E5/4 G#4/12) r/24"
VN2[65] = "(F4/4 D4/4 E4/4 B3/12) r/24 (F4/4 D4/4 E4/4 B3/12) r/24"
VLA[65] = REST
VLC[65] = REST

VN1[66] = W(66, slur=12)
VN2[66] = L(66, slur=12)
VLA[66] = "r/48 B3/48T"
VLC[66] = "E2/96T~"

VN1[67] = W(67, slur=12)
VN2[67] = "B3/96T"
VLA[67] = L(67, 0, 2) + " r/48"
VLC[67] = "E2/48T " + L(67, 2, 4)

VN1[68] = W(68, 0, 2) + " " + W(68, 2, 4, sh=-1)
VN2[68] = "E4+B4/96T"
VLA[68] = "E3+B3/96T"
VLC[68] = L(68)

# ===========================================================================
# G. Reprise, bars 69-80: the fall in sliding octave pairs, as in 13-16
# ===========================================================================
VN1[69] = W(69, sh=-1, first=">")
VN2[69] = W(69, sh=-2, first=">")
VLA[69] = "r/24 C4+E4/18> C4+E4/6. C4+E4/24_ C4+F4/24_"
VLC[69] = "A2+E3+A3/24^D A2+E3/18> A2+E3/6. A2+E3/24_ A2+F3/24_"

VN1[70] = W(70, sh=-1)
VN2[70] = "C4+E4/24_ C4/24_ C4+E4/48_"
VLA[70] = W(70, sh=-2, rng=VA)
VLC[70] = "A2/24_ E2/24_ A2/48_"

VN1[71] = REST
VN2[71] = "r/24 A3+E4/18 A3+E4/6 A3+E4/24 A3+F4/24"
VLA[71] = W(71, sh=-1, rng=VA)
VLC[71] = "A2/24. A2+E3/18 A2+E3/6 A2+E3/24 A2+F3/24"

VN1[72] = REST
VN2[72] = "A3+E4/24 r/72"
VLA[72] = "E3+A3/48 E3/48"
VLC[72] = W(72, sh=-1)

for b in range(73, 77):  # 73-76 as 9-12
    for P in (VN1, VN2, VLA, VLC):
        P[b] = P[b - 64]
VN1[76] = W(75, 0, 2) + " E7/24>! r/24"

VN1[77] = W(77, sh=-1, first=">")
VN2[77] = W(77, sh=-2, first=">")
VLA[77] = "r/24 C4+E4/18> C4+E4/6. C4+E4/24_ C4+F4/24_"
VLC[77] = "A2+E3+A3/24^D A2+E3/18> A2+E3/6. A2+E3/24_ A2+F3/24_"

VN1[78] = W(78, sh=-1)
VN2[78] = "C4+E4/24_ C4/24_ C4+E4/48_"
VLA[78] = W(78, sh=-2, rng=VA)
VLC[78] = "A2/24_ E2/24_ A2/48_"

VN1[79] = REST
VN2[79] = "r/24 G3+E4/18 G3+E4/6 G3+E4/24 G3+F4/24"
VLA[79] = W(79, sh=-1, rng=VA)
VLC[79] = "G2/24. G2+E3/18> G2+E3/6 G2+E3/24_ G2+F3/24_"

VN1[80] = REST
VN2[80] = "C4+E4/24 C4/24 C4+A4/24 A3+E4/24"
VLA[80] = W(80)
VLC[80] = "G2+E3/24 G2/24 F2/24 E2/24"

# ===========================================================================
# H. Coda, bars 81-96
# ===========================================================================
VN1[81] = "r/24 " + W(81, 1, 4, slur=0)
VN2[81] = "r/24 A3+F4/8> r/16 A3+F#4/24A r/24"
VLA[81] = "(C4/4 F3/4 B3/4 B3/4) (C5/4 F4/4) r/24 D#3+A3/24A r/24"
VLC[81] = "D2/24. r/8 C#3/8 D3/8 D#3/24 D#2/24>"

VN1[82] = W(82, 0, 2, slur=0) + " " + W(82, 2, 4, sh=-1, rng=VN, slur=0)
VN2[82] = "r/24 Bb3+G4/8> r/16 D4+Bb4/24A r/24"
VLA[82] = "r/24 Bb3/8 r/16 F3+Bb3/24A r/24"
VLC[82] = "E2/24. r/8 D#3/8 E3/8 F3/24 F2/24>"

# 83-84 (ff): the march on F in three octaves against the wind
VN1[83] = W(83, 0, 2, slur=0) + " " + W(83, 2, 4, sh=-1, slur=0)
VN2[83] = "r/24 F4/18> F4/6. F4/24> G4/24>"
VLA[83] = "r/24 F4/18> F4/6. F4/24> C4+G4/24>"
VLC[83] = "F2/24> F3/18> F3/6. F3/24> F3+C4/24>"

VN1[84] = W(84, sh=-1, slur=0)
VN2[84] = "F4/24> C4/24> F4/48>"
VLA[84] = "F4/24> C4/24> F4/48>"
VLC[84] = "F2/24> C3/24> F2/48>"

# 85-86 (p, cresc.): Violin I whistles; Chopin's rising left hand climbs
#    from the cello through the viola to Violin II; the cello keeps F
VN1[85] = W(85, sh=-1)
VN2[85] = REST
VLA[85] = "r/48 " + L(85, 2, 4)
VLC[85] = L(85, 0, 2) + " F2/48~"

VN1[86] = W(86, sh=-1)
VN2[86] = "r/48 " + L(86, 2, 4)
VLA[86] = L(86, 0, 2) + " r/48"
VLC[86] = "F2/96"

# 87-88 (f): both hands in octaves, falling
VN1[87] = W(87, sh=-1)
VN2[87] = ("C5+E5/12^ r/4 (D5/4 A4/4) (C5/4 E4/4 B4/4 E4/4 A4/4 C4/4) "
           "(F4/4 C4/4 E4/4 A3/4 D4/4 A3/4) r/24")
VLA[87] = "A3+E4/12^ r/12 r/24 r/24 (C4/4 E3/4 B3/4 E3/4 A3/4 C3/4)"
VLC[87] = "E2+A2+E3/12^ E2/84"

VN1[88] = "(F4/4 C4/4 E4/4 A3/4 D4/4 A3/4) r/24 B4+E5/24> G#4+E5/24>"
VN2[88] = "r/48 B3+E4/24> D4+B4/24>"
VLA[88] = "r/24 (C4/4 E3/4 B3/4 E3/4 A3/4 C3/4) E4+A4/24> B3+E4/24>"
VLC[88] = "(F3/4 C3/4 E3/4 A2/4 D3/4 A2/4) (C3/4 E2/4 B2/4 E2/4 A2/4 C2/4) E2+B2/24> E2+D3/24>"

# 89-92 (ff): the last fall, one bar an octave, over the cello's hammered A
HAM = " ".join(["A2/6> E3/6 C4/6 E3/6"] * 4)
HAM_VA = " ".join(["A3/6> E4/6 C5/6 E4/6"] * 4)
VN1[89] = W(89, first=">")
VN2[89] = W(89, sh=-1, first=">")
VLA[89] = HAM_VA
VLC[89] = HAM

VN1[90] = W(90)
VN2[90] = REST
VLA[90] = W(90, sh=-1)
VLC[90] = "A2/6> E3/6 C4/6 E3/6 E2/6> C3/6 E3/6 C3/6 A2/6> E3/6 C4/6 E3/6 C4/6> E3/6 C4/6 E3/6"

VN1[91] = W(91, 0, 3) + " r/24"
VN2[91] = W(91, 0, 3) + " r/24"
VLA[91] = "r/48 r/24 " + W(91, 3, 4, sub={23: "C4"})
VLC[91] = HAM

CHROM = ["A", "G#", "G", "F#", "F", "E", "D#", "D", "C#", "C", "B", "Bb"]


def chrom(o_hi):
    out = []
    for i, n in enumerate(CHROM):
        o = o_hi if i < 10 else o_hi - 1
        o = o if n not in ("B", "Bb") else o_hi - 1
        out.append(f"{n}{o}/8^.")
    return " ".join(out)


VN1[92] = chrom(5)
VN2[92] = chrom(4)
VLA[92] = W(92, sh=1, first=">")
VLC[92] = chrom(3)

# 93-96 (fff): the march one last time in full chords, then the scale
#    from C, in four octaves at once, to the final A
VN1[93] = "A5/24^.D C5+A5/18^ C5+A5/6. C5+A5/24^ D5+A5/24^"
VN2[93] = "A4/24^.D E4+C5/18^ E4+C5/6. E4+C5/24^ F4+D5/24^"
VLA[93] = "A3/24^.D A3+E4+A4/18^ E4+A4/6. A3+E4+A4/24^ A3+F4+A4/24^"
VLC[93] = "A2/24^.D A2+E3+A3/18^ E3+A3/6. A2+E3+A3/24^ A2+D3+A3/24^"

VN1[94] = "C5+A5/48^ B4+A5/48^"
VN2[94] = "E4+C5/48^ F4+D5/48^"
VLA[94] = "A3+E4+A4/48^ A3+D4+A4/48^"
VLC[94] = "A2+E3+A3/48^ A2+F3+A3/48^"

SCALE = ["C", "D", "E", "F#", "G#", "A", "B", "C", "D", "E", "F#", "G#"]


def run_up(o):
    ps = [f"{n}{o + (1 if i >= 7 else 0)}" for i, n in enumerate(SCALE)]
    return "(" + " ".join(f"{p}/4" + ("U" if i == 0 else "")
                          for i, p in enumerate(ps)) + ")"


VN1[95] = "C5+A5/48^ " + run_up(5)
VN2[95] = "E4+C5/48^ " + run_up(4)
VLA[95] = "A3+E4+A4/48^ " + run_up(3)
VLC[95] = "A2+E3+A3/48^ " + run_up(2)

VN1[96] = "A6/24^D r/24 r/48"
VN2[96] = "E5+A5/24^D r/24 r/48"
VLA[96] = "A3+E4+A4/24^D r/24 r/48"
VLC[96] = "A2+E3+A3/24^D r/24 r/48"

# ---------------------------------------------------------------------------
# Dynamics, hairpins, words
#   dynamics: (bar, tick, mark); a mark starting with "=" is MIDI only
#   hairpins: (bar, tick, bar2, tick2, "cresc"|"dim"), a trailing "-" = MIDI only
# ---------------------------------------------------------------------------
IDS = ("vn1", "vn2", "va", "vc")
DYN = {k: [] for k in IDS}
HAIR = {k: [] for k in IDS}
WORDS = {k: [] for k in IDS}


def dyn(bar, tick, mark, *ids):
    for k in ids or IDS:
        DYN[k].append((bar, tick, mark))


def hair(b, t, b2, t2, kind, *ids):
    for k in ids or IDS:
        HAIR[k].append((b, t, b2, t2, kind))


def words(bar, tick, text, *ids):
    for k in ids or IDS:
        WORDS[k].append((bar, tick, text))


# I. Introduction
dyn(1, 0, "p", "va")
words(1, 0, "sul G, poco vibrato", "va")
dyn(3, 0, "p", "vn1")
dyn(3, 0, "pp", "vn2", "va", "vc")
words(3, 0, "sul tasto, senza vibrato")
# A. Theme
dyn(5, 0, "f risoluto", "vn1")
dyn(5, 0, "f", "vc")
dyn(5, 0, "=fz", "vc")
dyn(5, 24, "f", "vn2", "va")
words(5, 0, "ord.")
words(7, 0, "dim.", "va", "vc", "vn2")
hair(7, 0, 7, 72, "dim-", "va", "vc", "vn2")
dyn(8, 0, "mf", "vc", "va", "vn2")
hair(8, 0, 8, 72, "cresc", "vc", "va")
dyn(9, 0, "f", "vn1", "vc")
dyn(9, 24, "f", "vn2", "va")
words(9, 24, "marcato", "vn2", "va")
hair(10, 0, 10, 72, "dim")
dyn(11, 0, "mf")
hair(12, 0, 12, 48, "cresc", "vn1", "vn2", "vc")
dyn(13, 0, "f")
words(15, 0, "dim.", "vn2", "va", "vc")
hair(15, 0, 15, 90, "dim-")
dyn(16, 0, "mf")
hair(16, 48, 16, 90, "cresc", "vn2", "va", "vc")
dyn(17, 0, "f")
dyn(21, 0, "f")
hair(22, 0, 22, 90, "cresc", "vn1")
# B. E minor
dyn(23, 0, "f", "vn1", "vc")
dyn(23, 24, "f", "vn2", "va")
words(25, 0, "dim.", "va", "vc", "vn2")
hair(25, 0, 25, 72, "dim-", "va", "vc", "vn2")
dyn(26, 0, "mf", "vc", "va", "vn2")
dyn(27, 0, "mf")
dyn(29, 0, "mf")
hair(30, 0, 30, 48, "cresc")
dyn(31, 0, "f")
dyn(35, 0, "mf")
hair(37, 0, 37, 90, "cresc", "vn2", "vc")
hair(37, 48, 37, 90, "cresc", "vn1")
dyn(38, 0, "f")
hair(40, 0, 40, 90, "dim", "vn1")
# C. Theme on top
dyn(41, 0, "f cantabile, con forza", "vn1")
dyn(41, 0, "f", "vn2", "va", "vc")
dyn(45, 0, "fp", "vn1")
dyn(45, 0, "p", "vc")
dyn(45, 24, "p", "va")
dyn(45, 48, "pp", "vn2")
words(45, 0, "leggiero", "vn1")
words(45, 24, "dolce, espressivo", "va")
hair(45, 48, 45, 66, "cresc", "va")
hair(45, 72, 45, 90, "dim", "va")
dyn(47, 0, "p")
hair(48, 0, 48, 90, "cresc", "vn2", "va", "vc")
# D. Development
dyn(49, 0, "f")
words(49, 0, "marcato", "va", "vc")
hair(49, 0, 49, 48, "cresc", "vn1", "va", "vc")
dyn(53, 0, "ff")
dyn(55, 0, "f")
dyn(57, 0, "mf")
words(57, 24, "espressivo", "va")
words(57, 0, "poco a poco cresc.", "vn1")
hair(57, 0, 58, 90, "cresc-")
words(58, 0, "cresc.", "va", "vc", "vn2")
dyn(59, 0, "f")
hair(59, 0, 60, 90, "cresc")
# E. Storm
dyn(61, 0, "ff")
words(61, 0, "con fuoco", "vn1")
dyn(62, 48, "fz")
dyn(62, 48, "=ff")
dyn(63, 0, "ff")
dyn(64, 48, "fz")
dyn(64, 48, "=ff")
# F. Eye of the storm
dyn(65, 0, "p", "vn1", "vn2")
words(65, 0, "sul ponticello", "vn1", "vn2")
dyn(66, 0, "pp", "vc")
dyn(66, 48, "pp", "va")
words(66, 0, "sul pont.", "vc")
words(66, 48, "sul pont.", "va")
words(66, 0, "cresc. poco a poco", "vn1", "vn2")
hair(66, 0, 67, 90, "cresc-", "vn1", "vn2")
hair(66, 0, 67, 90, "cresc-", "vc", "va")
dyn(67, 0, "p cresc.", "vc")
dyn(67, 0, "p cresc.", "va")
words(68, 0, "ord.")
dyn(68, 0, "mf")
hair(68, 0, 68, 90, "cresc")
# G. Reprise
dyn(69, 0, "f", "vn1", "vn2")
dyn(69, 0, "f", "vc")
dyn(69, 0, "=fz", "vc")
dyn(69, 24, "f", "va")
words(71, 0, "dim.", "vn2", "va", "vc")
hair(71, 0, 71, 72, "dim-")
dyn(72, 0, "mf")
hair(72, 0, 72, 72, "cresc", "va", "vc")
dyn(73, 0, "f", "vn1", "vc")
dyn(73, 24, "f", "vn2", "va")
words(73, 24, "marcato", "vn2", "va")
hair(74, 0, 74, 72, "dim")
dyn(75, 0, "mf")
hair(76, 0, 76, 48, "cresc", "vn1", "vn2", "vc")
dyn(77, 0, "f")
words(79, 0, "dim.", "vn2", "va", "vc")
hair(79, 0, 79, 90, "dim-")
dyn(80, 0, "mf")
hair(80, 0, 80, 90, "cresc", "vn2", "va", "vc")
# H. Coda
dyn(81, 0, "f")
words(81, 24, "sautillé", "vn1")
words(81, 0, "sautillé", "va")
words(82, 0, "cresc.")
hair(82, 0, 82, 90, "cresc-")
dyn(83, 0, "ff")
words(83, 24, "marcatissimo", "vn2", "va", "vc")
hair(84, 48, 84, 90, "dim")
dyn(85, 0, "p")
words(85, 0, "legato, leggiero", "vn1")
words(85, 0, "cresc. poco a poco", "vn1", "vc")
words(85, 48, "cresc. poco a poco", "va")
words(86, 48, "cresc. poco a poco", "vn2")
hair(85, 0, 86, 90, "cresc-")
dyn(87, 0, "f")
dyn(87, 0, "=fz", "vn2", "va", "vc")
dyn(89, 0, "ff")
words(90, 0, "dim.", "vn1", "va", "vc")
hair(90, 0, 90, 90, "dim-")
dyn(91, 0, "f")
hair(91, 0, 91, 90, "cresc", "vn1", "vn2", "vc")
hair(91, 72, 91, 90, "cresc", "va")
dyn(92, 0, "ff")
words(92, 0, "marcatissimo", "vn1", "vn2", "vc")
dyn(93, 0, "fff")
words(93, 0, "pesante")

# ---------------------------------------------------------------------------
# Form, tempo, layout
# ---------------------------------------------------------------------------
SECTIONS = [(1, None, "Introduction 引子"), (5, "A", "Theme 主题"),
            (23, "B", "E minor e 小调"), (41, "C", "Theme above 主题在上"),
            (49, "D", "Development 展开"), (61, "E", "Storm 风暴"),
            (65, "F", "Eye of the storm 风眼"), (69, "G", "Reprise 再现"),
            (81, "H", "Coda 尾声"), (89, "I", "Last gust 最后一阵风")]
TEMPO_MARKS = [  # (bar, tick, words, beat-unit, number, quarter bpm)
    (1, 0, "Lento", "quarter", 52, 52),
    (5, 0, "Allegro con brio", "half", 69, 138),
    (69, 0, "a tempo", None, None, 138)]
TEMPO_WORDS = [(4, 0, "rit."), (68, 48, "rit."), (95, 0, "allarg.")]
TEMPI = [(1, 0, 52), (2, 48, 34), (3, 0, 50), (4, 0, 46), (4, 48, 40),
         (4, 72, 24), (5, 0, 138),
         (68, 48, 128), (68, 60, 120), (68, 72, 110), (68, 84, 98),
         (69, 0, 138), (93, 0, 132), (95, 0, 122), (95, 48, 118), (96, 0, 104)]
# two bars a system (24 sextuplet 16ths in a bar), the Lento and the last
# four bars (chords and one run) four to a system
SYSTEM_BREAKS = tuple(b for b in range(5, NBARS + 1, 2) if b != 95)
PAGE_BREAKS = ()
DOUBLE_BARS = (4, 22, 40, 48, 60, 64, 68, 80, 88)
PROGRAMS = {}       # part id -> [(bar, tick, GM program)] (pizz. etc.)
PARTS = [
    dict(id="vn1", name="Violin I", abbr="Vln. I", iname="Violin",
         sound="strings.violin", program=40, clef="treble", data=VN1,
         fam="vn", rng=("G3", "E7"), fast="D7", pan=-40),
    dict(id="vn2", name="Violin II", abbr="Vln. II", iname="Violin",
         sound="strings.violin", program=40, clef="treble", data=VN2,
         fam="vn", rng=("G3", "C7"), fast="B6", pan=-15),
    dict(id="va", name="Viola", abbr="Vla.", iname="Viola",
         sound="strings.viola", program=41, clef="alto", data=VLA,
         fam="va", rng=("C3", "E6"), fast="A5", pan=15),
    dict(id="vc", name="Violoncello", abbr="Vc.", iname="Violoncello",
         sound="strings.cello", program=42, clef="bass", data=VLC,
         fam="vc", rng=("C2", "A5"), fast="A4", pan=40),
]

META = dict(
    title="冬风", title_latin="Winter Wind",
    subtitle="肖邦练习曲 Op. 25 No. 11 · 弦乐四重奏",
    subtitle_en="Étude in A minor, Op. 25 No. 11 — for String Quartet",
    composer="肖邦 Frédéric Chopin", lyricist="", artist="",
    original="a 小调练习曲 Op. 25 No. 11",
    instrumentation=[("Violin I", "第一小提琴"), ("Violin II", "第二小提琴"),
                     ("Viola", "中提琴"), ("Violoncello", "大提琴")],
    key="A Minor · a 小调", tempo="Allegro con brio 𝅗𝅥 = 69",
    duration="ca. 3′05″",
    year="2026", tempo_text="",
    title_gap_sp=10)  # room for the Lento mark under the credit lines

def _mscx_hook(x):
    """MS4 touch-ups on the imported score (MS4 ignores these from MusicXML):
    only the tuplets that arrived with a number (the first of each run of
    sextuplets / triplets, and any irregular group) show it; the others get
    neither number nor bracket."""
    def fix(mo):
        t = mo.group(0)
        if "<Number>" in t:  # MS4 brackets it only when it is not beamed
            return t
        extra = ("<bracketType>2</bracketType>\n"
                 "            <numberType>2</numberType>\n")
        return t.replace("<normalNotes>", extra + "            <normalNotes>", 1)
    return re.sub(r"<Tuplet>.*?</Tuplet>", fix, x, flags=re.S)


META["mscx_hook"] = META["mscx_part_hook"] = _mscx_hook
# Parts on a 6.6 mm staff (house parts: 7 mm): Violin I's sextuplet bars
# (24 sixteenths each) then fit two to a line throughout; at 7 mm every
# odd one out ended up alone on a line.
META["part_style"] = {"Spatium": 1.65}
# extra line starts in the parts (besides the sections), read back from
# the engraved PDF, so that no bar stands alone on a line
PART_BREAKS = {"vn1": (37, 53, 55, 57, 59, 67), "va": (53, 57, 63, 95), "vc": (63,)}
# and page starts: the last section on a page of its own (three lines),
# not the last two bars alone on the last page
PART_PAGE_BREAKS = {"vn1": (89,), "va": (89,)}


def auto_marks(parsed):
    """8va lines for the violins (beats that sit above A6, or a held note
    from C7 up) and clef changes for viola (treble when a bar sits from C5
    up) and cello (tenor when a bar sits from D4 up).  Pitches stay at
    concert pitch; only the display changes."""
    ottava, clefs = {}, {}
    mid = engine.midi_of
    for p in PARTS:
        evs = [e for v in parsed[p["id"]].values() for e in v if e["pitches"]]
        if p["fam"] == "vn":
            # count ledger lines, not semitones: a beat reaching B6 (four
            # ledger lines above the staff) or three notes from G6 up
            def dia(x):
                st, _, o = engine.split_pitch(x)
                return 7 * o + "CDEFGAB".index(st)
            g6, b6 = dia("G6"), dia("B6")
            beats = set()
            for k in range(NBARS * BAR // 24):
                a, z = k * 24, k * 24 + 24
                ns = [e for e in evs if a <= e["abs"] < z]
                top = [max(dia(x) for x in e["pitches"]) for e in ns]
                held = [e for e in ns if e["dur"] >= 12 and
                        max(mid(x) for x in e["pitches"]) >= 96]
                if any(t >= b6 for t in top) or \
                        sum(t >= g6 for t in top) >= 3 or held:
                    beats.add(k)
            spans, cur = [], None
            for k in sorted(beats):
                if cur and k - cur[1] <= 1:
                    cur[1] = k + 1
                else:
                    cur = [k, k + 1]
                    spans.append(cur)
            # a line that stops (or starts) mid-bar while the rest of the
            # bar stays high (from C5 up) runs to the barline instead: no
            # choppy one-beat 8va, and no accidental that MS4 drops because
            # the same written line carried it inside the 8va
            def high(a, z):
                ns = [mid(x) for e in evs if a <= e["abs"] < z
                      for x in e["pitches"]]
                return all(x >= 72 for x in ns)
            for sp in spans:
                a, z = sp[0] * 24, sp[1] * 24
                ba, bz = a - a % BAR, z + (-z) % BAR
                if a > ba and high(ba, a):
                    sp[0] = ba // 24
                if z < bz and high(z, bz):
                    sp[1] = bz // 24
            ottava[p["id"]] = [(a * 24 // BAR + 1, a * 24 % BAR,
                                z * 24 // BAR + 1 if z * 24 % BAR else z * 24 // BAR,
                                z * 24 % BAR or BAR) for a, z in spans]
        else:
            thr, alt, base = ((72, "treble", "alto") if p["fam"] == "va"
                              else (62, "tenor", "bass"))
            state, out = base, []
            for b in range(1, NBARS + 1):
                ns = [mid(x) for e in evs if e["bar"] == b for x in e["pitches"]]
                if not ns:
                    continue
                share = sum(1 for x in ns if x >= thr) / len(ns)
                want = alt if share >= 0.6 else base if share < 0.3 else state
                if want != state:
                    out.append((b, 0, want))
                    state = want
            clefs[p["id"]] = out
    return clefs, ottava


def make_spec(parsed):
    clefs, ottava = auto_marks(parsed)
    return engine.Spec(
        nbars=NBARS, title=META["title"],
        movement=f"{META['title']}（{META['subtitle']}）",
        composer=META["composer"], arranger=hollywood.ARRANGER,
        engraver=hollywood.ENGRAVER,
        rights="Music: Chopin (public domain). Arrangement: 花开当富贵",
        group_name="", dyn=DYN, hair=HAIR, words=WORDS, sections=SECTIONS,
        tempo_marks=TEMPO_MARKS, tempo_words=TEMPO_WORDS, tempi=TEMPI,
        system_breaks=SYSTEM_BREAKS, page_breaks=PAGE_BREAKS,
        double_bars=DOUBLE_BARS, clefs=clefs, ottava=ottava,
        programs=PROGRAMS)


def parse_all():
    return {p["id"]: engine.parse_part(p["data"], NBARS) for p in PARTS}


def check(parsed):
    out = []
    for p in PARTS:
        out += engine.check_part(p["id"], p["fam"], p["rng"], parsed[p["id"]],
                                 p.get("fast"))
    return out


def base():
    return os.path.join(OUT, f"{NAME}_弦乐四重奏")


def chopin_events(b):
    """Chopin's notes in bar b: [(tick, dur, midi)] (scale in bar 95 left out)."""
    out = []
    for hand in (chopin.RH, chopin.LH):
        s = hand[b]
        if not s:
            continue
        if "@" not in s:
            for i, p in enumerate(s.replace("|", " ").split()):
                out.append((i * 4, 4, engine.midi_of(p)))
            continue
        for mo in re.finditer(r"@([\d.]+) (\S+)/([\d.]+)", s):
            t, ps, d = float(mo.group(1)), mo.group(2), float(mo.group(3))
            for p in ps.split("+"):
                out.append((t, d, engine.midi_of(p)))
    return out


PC = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def harm(parsed):
    """Beat by beat: the lowest sounding pitch class and the pitch classes
    that sound on the beat, quartet against Chopin.  Lists the beats that
    differ, for review (deliberate choices are fine)."""
    lines = []
    q_all = [e for p in PARTS for v in parsed[p["id"]].values() for e in v
             if e["pitches"]]
    for b in range(1, NBARS + 1):
        ch = chopin_events(b)
        if not ch:
            continue
        for k in range(4):
            t0 = k * 24
            c_on = [m for t, d, m in ch if t <= t0 < t + d]
            c_in = {m % 12 for t, d, m in ch if t0 <= t < t0 + 24 or t <= t0 < t + d}
            a0 = (b - 1) * BAR + t0
            q_on = [engine.midi_of(x) for e in q_all
                    if e["abs"] <= a0 < e["abs"] + e["dur"] for x in e["pitches"]]
            q_in = {engine.midi_of(x) % 12 for e in q_all
                    if a0 <= e["abs"] < a0 + 24 or e["abs"] <= a0 < e["abs"] + e["dur"]
                    for x in e["pitches"]}
            msg = []
            if c_on and q_on and min(c_on) % 12 != min(q_on) % 12:
                msg.append(f"bass {PC[min(q_on) % 12]} (Chopin {PC[min(c_on) % 12]})")
            if c_on and not q_on:
                msg.append("quartet silent")
            miss = {m % 12 for m in c_on} - q_in
            if miss:
                msg.append("missing " + " ".join(PC[x] for x in sorted(miss)))
            extra = q_in - c_in
            if extra:
                msg.append("added " + " ".join(PC[x] for x in sorted(extra)))
            if msg:
                lines.append(f"m{b}.{k + 1}: " + "; ".join(msg))
    return lines


def dump(path):
    """Plain-text view of every bar: Chopin's text and the four parts."""
    with open(path, "w", encoding="utf-8") as fh:
        for b in range(1, NBARS + 1):
            fh.write(f"== bar {b}\n")
            fh.write(f"   Chopin RH: {chopin.RH[b]}\n")
            fh.write(f"   Chopin LH: {chopin.LH[b]}\n")
            for p in PARTS:
                fh.write(f"   {p['abbr']:8s}: {p['data'][b]}\n")


def main():
    if "--dump" in sys.argv:
        dump(sys.argv[sys.argv.index("--dump") + 1])
        return
    parsed = parse_all()
    if "--harm" in sys.argv:
        print("\n".join(harm(parsed)))
        return
    problems = check(parsed)
    for x in problems:
        print(x)
    if "--check" in sys.argv:
        return
    os.makedirs(OUT, exist_ok=True)
    spec = make_spec(parsed)
    xml = base() + ".musicxml"
    engine.write_musicxml(xml, PARTS, parsed, spec)
    hollywood.polish_musicxml(xml, META)
    engine.write_midi(base() + "_全轨.mid", PARTS, parsed, spec,
                      "Winter Wind - String Quartet")
    for i, p in enumerate(PARTS, 1):
        engine.write_midi(os.path.join(OUT, f"{NAME}_分轨{i}_{ZH[p['id']]}.mid"),
                          PARTS, parsed, spec, "Winter Wind - " + p["name"],
                          ids=[p["id"]])
    print("written to", OUT)
    if "--mp3" in sys.argv:
        write_mp3()
    if "--pdf" in sys.argv:
        write_pdf()
    if "--parts" in sys.argv:
        write_parts()


ZH = {"vn1": "第一小提琴", "vn2": "第二小提琴", "va": "中提琴",
      "vc": "大提琴"}
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


def write_mp3():
    """GM preview (FluidSynth), only for checking notes: not the ACE sound."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "p.wav")
        subprocess.run(["fluidsynth", "-ni", "-g", "0.7", "-r", "44100",
                        "-F", wav, SF2, base() + "_全轨.mid"], check=True,
                       capture_output=True)
        mp3 = os.path.join(OUT, "粗略试听_GM音色_非ACE效果.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-af", "loudnorm=I=-16:TP=-1.5", "-b:a", "192k", mp3],
                       check=True)
    print("MP3:", mp3)


def write_parts():
    """Players' parts (9 x 12 in, tools/hollywood): one PDF with Violin I,
    Violin II, Viola and Cello, a bookmark per part."""
    import copy
    import tempfile
    parsed = parse_all()
    spec = make_spec(parsed)
    items = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, p in enumerate(PARTS, 1):
            # MS4 fills the lines itself; every section starts a new line,
            # and PART_BREAKS keeps a bar from ending up alone on a line
            pspec = copy.copy(spec)
            pspec.system_breaks = tuple(sorted(
                {s for s, _, _ in SECTIONS if s > 1}
                | set(PART_BREAKS.get(p["id"], ()))))
            pspec.page_breaks = tuple(PART_PAGE_BREAKS.get(p["id"], ()))
            xml = os.path.join(tmp, f"part{i}.musicxml")
            engine.write_musicxml(xml, [p], {p["id"]: parsed[p["id"]]}, pspec)
            hollywood.polish_musicxml(xml, META, part=(p["name"], ZH[p["id"]]))
            items.append((xml, p["name"], ZH[p["id"]]))
        dst = os.path.join(OUT, f"{NAME}_分谱.pdf")
        n = hollywood.render_parts_pdf(items, dst, META)
    print(f"Parts: {dst} ({n} pages)")


def write_pdf(png_dir=None):
    dst = os.path.join(OUT, f"{NAME}_总谱.pdf")
    n = hollywood.render_pdf(base() + ".musicxml", dst, META, png_dir=png_dir)
    print(f"PDF: {dst} ({n} pages)")


if __name__ == "__main__":
    main()
