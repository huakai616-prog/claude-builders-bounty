"""S02 · bars 16–23 · Riff 主题动机.

Texture
- 16 (subito f) and 18 (f): the piano's 3+3+2 chord hits (dotted 8th,
  dotted 8th, 8th | dotted 8th, 16th, quarter) spread over Vn I / Vn II /
  Va as double stops, marcato, bowed down-down-up | down-up-down (group
  heads on down-bows, one retake fewer than all down-bows).  16 is the
  bare open fifth G–D: Vn I D5+G5, Vn II D4+G4, Va G3+D4 on its open
  strings.  18 adds the A3/B-flat3 cluster, split
  between Va (A3+D4) and Vn II (B-flat3+G4).  Vc = the LH's G 16th figure
  on the open G string, interlocking with the hits.
- 17 (mp / p): Vn I = the RH high 16ths at pitch (3rd position, string
  crossings, one slur per 3+3+2 group, tenuto on the group heads); Va = the
  LH 16ths at pitch (B-flat4 G4 A4, first position around the open A);
  Vn II holds the RH's D4+G4 and Vc the G (octave down) — both tied over
  from the last hit of 16, as in the piano, fading to p (the pedal tail,
  one step under the moving mp 16ths).
- 19–22 (ff): the riff.  Vn I = the RH top line (tenuto B-flat6 / G6 as in
  the piano), then the top of the RH chords (D5 C5 D5 / D5 B-flat5 A5);
  Vn II = the RH's lower octave (D5 B-flat5 D5 G5, then D5 B-flat4 G4) and
  the inner notes of the RH chords as double stops (D4+B-flat4 …, the F#
  of the D chord in 20/22).  Va = the LH mid layer: the octave of the bass
  on the downbeat, the G3 pickup and the B-flat3+D4 / B-flat3+E-flat4 stab
  (the D→E-flat motion of the piano's inner voice), then the lh3 F3/D3 and
  the off-beat F3+C4 / A3+D4 16th stabs.  Vc = the LH bass G2 / E-flat2 with
  the low 16th pickup (G2 D3 / E-flat2 B-flat2) and the F2 / D2 rhythm
  (16th, held, 16th).
- 23: the transition.  Vn I rests and only gives the A5 pickup into the
  verse (p); Vn II = the RH's syncopated G4+B-flat4 / G4 / C5; Vc keeps the
  LH 16ths on the open G string; Va plays the D in the LH rhythm for half
  a bar, then just holds it (thinning out).  Va and Vc both spicc. for the
  16ths.  Everybody dim. to p, arriving together on beat 4.
"""

_HIT16 = ("{c}/12!db {c}/12!db {c}/8!ub {c}/12!db {c}/4!ub {c}/16!db{t}")
_G16 = ("G2/4 G2/4 G2/4 r/4 G2/4 G2/4 r/4 G2/4 "
        "r/4 G2/4 G2/4 r/4 r/4 G2/4 G2/8{t}")

VN1 = {
    16: _HIT16.format(c="D5+G5", t=""),
    17: "(D6/4- D5/4 G5/4) (C6/4- D5/4 G5/4) (Bb5/4- D5/4) "
        "(D6/4- D5/4 G5/4) (C6/4- D5/4 G5/4) Bb5/8-",
    18: _HIT16.format(c="D5+G5", t=""),
    19: "D6/4 Bb6/8- D6/4 G6/4- D6/4 Bb5/4 G5/4 r/8 D5/8 C5/8 D5/8",
    20: "D6/4 Bb6/8- D6/4 G6/4- D6/4 Bb5/4 G5/4 r/8 D5/8 Bb5/8 A5/8",
    21: "D6/4 Bb6/8- D6/4 G6/4- D6/4 Bb5/4 G5/4 r/8 D5/8 C5/8 D5/8",
    22: "D6/4 Bb6/8- D6/4 G6/4- D6/4 Bb5/4 G5/4 r/8 D5/8 Bb5/8 A5/8",
    23: "r/32 r/16 r/8 A5/8",
}

VN2 = {
    16: _HIT16.format(c="D4+G4", t="~"),
    17: "D4+G4/64",
    18: _HIT16.format(c="Bb3+G4", t=""),
    19: "D5/4 Bb5/8- D5/4 G5/4- D5/4 Bb4/4 G4/4 "
        "r/8 D4+Bb4/8 C4+Bb4/8 D4+Bb4/8",
    20: "D5/4 Bb5/8- D5/4 G5/4- D5/4 Bb4/4 G4/4 "
        "r/8 F#4+A4/8 Bb4+D5/8 A4+D5/8",
    21: "D5/4 Bb5/8- D5/4 G5/4- D5/4 Bb4/4 G4/4 "
        "r/8 D4+Bb4/8 C4+Bb4/8 D4+Bb4/8",
    22: "D5/4 Bb5/8- D5/4 G5/4- D5/4 Bb4/4 G4/4 "
        "r/8 F#4+A4/8 Bb4+D5/8 A4+D5/8",
    23: "G4+Bb4/12 G4/8 r/4 C5/8 G4+Bb4/12 G4/8 r/4 C5/8",
}

VA = {
    16: _HIT16.format(c="G3+D4", t=""),
    17: "(Bb4/4 G4/4 A4/4) (Bb4/4 G4/4 A4/4) (Bb4/4 G4/4) "
        "(Bb4/4 G4/4 A4/4) (Bb4/4 G4/4 A4/4) Bb4/8",
    18: _HIT16.format(c="A3+D4", t=""),
    19: "G3/8 G3/4 Bb3+D4/12 r/8 F3/4 F3/8 F3+C4/4 r/4 F3+C4/4 r/4 F3/4",
    20: "Eb3/8 G3/4 Bb3+Eb4/12 r/8 D3/4 D3/8 A3+D4/4 r/4 A3+D4/4 r/4 D3/4",
    21: "G3/8 G3/4 Bb3+D4/12 r/8 F3/4 F3/8 F3+C4/4 r/4 F3+C4/4 r/4 F3/4",
    22: "Eb3/8 G3/4 Bb3+Eb4/12 r/8 D3/4 D3/8 A3+D4/4 r/4 A3+D4/4 r/4 D3/4",
    23: "D4/4 D4/4 r/4 D4/4 D4/4 r/4 D4/4 r/4 D4/32",
}

VC = {
    16: _G16.format(t="~"),
    17: "G2/64",
    18: _G16.format(t=""),
    19: "G2/24 G2/4 D3/4 F2/4 F2/24 F2/4",
    20: "Eb2/24 Eb2/4 Bb2/4 D2/4 D2/24 D2/4",
    21: "G2/24 G2/4 D3/4 F2/4 F2/24 F2/4",
    22: "Eb2/24 Eb2/4 Bb2/4 D2/4 D2/24 D2/4",
    23: "G2/4 G2/4 r/4 G2/4 G2/4 r/4 G2/4 r/4 "
        "G2/4 G2/4 r/4 G2/4 G2/4 r/4 G2/4 r/4",
}

DYN = {
    "vn1": [(16, 0, "f"), (17, 0, "mp"), (18, 0, "f"), (19, 0, "ff"),
            (23, 56, "p")],
    "vn2": [(16, 0, "f"), (17, 0, "p"), (18, 0, "f"), (19, 0, "ff"),
            (23, 56, "p")],
    "va": [(16, 0, "f"), (17, 0, "mp"), (18, 0, "f"), (19, 0, "ff"),
           (23, 56, "p")],
    "vc": [(16, 0, "f"), (17, 0, "p"), (18, 0, "f"), (19, 0, "ff"),
           (23, 56, "p")],
}

HAIR = {
    # 18: no swell under the marcato last hit (piano: f straight to
    # subito ff); only the cello's G pickup drives into 19.
    # 23: the piano's decrescendo across the transition bar, same span in
    # every part that plays.
    "vn1": [],
    # 16: the tied last hit / G fades into the p of 17 (piano: the chord
    # simply decays under the pedal)
    "vn2": [(16, 48, 16, 63, "dim"), (23, 0, 23, 52, "dim")],
    # 23: the viola's 16ths and then its held D thin out with the others
    "va": [(23, 0, 23, 52, "dim")],
    "vc": [(16, 52, 16, 63, "dim"), (18, 52, 18, 63, "cresc"),
           (23, 0, 23, 52, "dim")],
}

TEXT = {
    "vn1": [(16, 0, "subito"), (17, 0, "legato")],
    "vn2": [(16, 0, "subito")],
    "va": [(16, 0, "subito"), (17, 0, "legato"), (23, 0, "spicc.")],
    "vc": [(16, 0, "subito"), (23, 0, "spicc.")],
}

CLEFS = {}
OTTAVA = []
ALLOW = set()
