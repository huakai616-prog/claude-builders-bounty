"""S06 · bars 50–57 · Interlude 间奏 (mp -> f).

Piano: RH 16th broken pattern (tenuto top notes = the melody pulse), in
53 a dotted melody on top; LH = low octave whole notes (Eb G F G ...) plus
the 3+3+2 figure (X3 dotted 8th, X3 8th) and a half-note dyad on beat 3.

Quartet:
- Vn II: the whole RH 16th stream, one player, light spiccato, tenuto on
  the piano's tenuto top notes.
- Vn I: 50 holds the top of the RH chord (Bb5, tail of the chorus), rests
  in 51-52, then from the pickup in 52 sings the melody: D6 C6 C6 A5 Bb5 |
  Bb5 D6 | D6 D6 | C6 C6 | A5 Bb5 Bb6 (the tenuto top notes, sustained
  where the pedal holds them; A5 in 57 kept short because nothing in the
  piano sustains an A after it).
- Vc: the LH bass (Eb2 G2 F2 ...) in the LH's 3+3+2 rhythm, last note tied
  through the half = bass sustained all bar.
- Va: the LH half-note dyad on beat 3 (single note in 50-52, double stop
  from 53); from 53 also the X3 rhythm (the piano's octave doubling), as
  the texture builds.
- 57: Vc keeps the open-G2 pedal in the same 3+3+2 rhythm (no re-attack
  on beat 3: the piano's G2+G3 whole note just rings); the LH line
  G3 G3 -> G4 A4 Bb4 D5 G5 is one line in one hand, so it all goes to Va
  (open-string G3s, then the run slurred), which leads into the bridge.
- Va and Vc articulate the 3+3+2 hook alike: tenuto on every attack.
- Vn I bowing: the first slur ends on the first C6 in 53, so the re-struck
  (syncopated) C6 starts a new bow; 55 and 56 portato, one bow per bar.
- Dynamics into S07 (f in all parts at 58): Vn I reaches f at 57 (mf ->
  cresc 55-56) and stays there; Vn II / Va / Vc cresc 55-56 from mp to mf
  at 57, then the second half of 57 (the Va run) crescendos into the f.
"""

VN1 = {
    50: "Bb5/64",
    52: "r/32 r/16 r/8 (Bb5/8",
    53: "D6/12 C6/12) (C6/8~ C6/8 A5/16 Bb5/8~",
    54: "Bb5/32) D6/32-",
    55: "(D6/32- D6/32-)",
    56: "(C6/32- C6/32-)",
    57: "A5/8- r/8 r/16 Bb5/16- r/8 Bb6/8",
}

VN2 = {
    50: "r/4 D4/4 G4/4 D4/4 G4/4 D4/4 G4/4 D4/4 "
        "D5/4- D4/4 G4/4 Bb4/4 D4/4 G4/4 Bb4/4 D4/4",
    51: "D5/4- D4/4 F4/4 Bb4/4 D4/4 F4/4 Bb4/4 D4/4 "
        "D5/4- D4/4 F4/4 Bb4/4 D4/4 F4/4 Bb4/4 D4/4",
    52: "C5/4- C4/4 F4/4 Bb4/4 C4/4 F4/4 Bb4/4 C4/4 "
        "C5/4- C4/4 F4/4 Bb4/4 C4/4 F4/4 Bb4/8",
    53: "D6/4 F5/4 D5/4 C6/4 F5/4 D5/4 C6/4 F5/4 "
        "D5/4 F5/4 A5/4 F5/4 D5/4 F5/4 Bb5/4 G5/4",
    54: "D5/4 G5/4 D5/4 G5/4 D5/4 G5/4 D5/4 G5/4 "
        "D6/4- D5/4 G5/4 Bb5/4 D5/4 G5/4 Bb5/4 D5/4",
    55: "D6/4- D5/4 F5/4 Bb5/4 D5/4 F5/4 Bb5/4 D5/4 "
        "D6/4- D5/4 F5/4 Bb5/4 D5/4 F5/4 Bb5/4 D5/4",
    56: "C6/4- C5/4 F5/4 Bb5/4 C5/4 F5/4 Bb5/4 C5/4 "
        "C6/4- C5/4 F5/4 Bb5/4 C5/4 F5/4 Bb5/4 C5/4",
    57: "A5/4- D5/4 Bb4/4 D5/4 Bb4/4 D5/4 Bb4/4 D5/4 "
        "Bb5/16- r/8 Bb5/8",
}

VA = {
    50: "r/32 G3/32",
    51: "r/32 Bb3/32",
    52: "r/32 A3/32",
    53: "r/12 G3/12- G3/8- Bb3+D4/32",
    54: "r/12 Eb3/12- Eb3/8- Bb3+G4/32",
    55: "r/12 G3/12- G3/8- D4+Bb4/32",
    56: "r/12 F3/12- F3/8- C4+A4/32",
    57: "r/12 G3/12- G3/8- (G4/4 A4/4 Bb4/4 D5/4 G5/16)",
}

VC = {
    50: "Eb2/12- Eb2/12- Eb2/8-~ Eb2/32",
    51: "G2/12- G2/12- G2/8-~ G2/32",
    52: "F2/12- F2/12- F2/8-~ F2/32",
    53: "G2/12- G2/12- G2/8-~ G2/32",
    54: "Eb2/12- Eb2/12- Eb2/8-~ Eb2/32",
    55: "G2/12- G2/12- G2/8-~ G2/32",
    56: "F2/12- F2/12- F2/8-~ F2/32",
    57: "G2/12- G2/12- G2/8-~ G2/32",
}

DYN = {
    "vn1": [(50, 0, "mp"), (52, 56, "mf"), (57, 0, "f")],
    "vn2": [(50, 4, "mp"), (57, 0, "mf")],
    "va": [(50, 32, "p"), (53, 12, "mp"), (57, 12, "mf")],
    "vc": [(50, 0, "p"), (53, 0, "mp"), (57, 0, "mf")],
}

HAIR = {
    "vn1": [(50, 0, 50, 60, "dim"), (55, 0, 56, 60, "cresc")],
    "vn2": [(55, 0, 56, 60, "cresc"), (57, 32, 57, 60, "cresc")],
    "va": [(52, 32, 52, 60, "cresc"), (55, 12, 56, 60, "cresc"),
           (57, 32, 57, 60, "cresc")],
    "vc": [(52, 24, 52, 60, "cresc"), (55, 0, 56, 60, "cresc"),
           (57, 32, 57, 60, "cresc")],
}

TEXT = {
    "vn1": [(52, 56, "cantabile")],
    "vn2": [(50, 4, "spiccato, leggiero")],
    "va": [],
    "vc": [(50, 0, "sostenuto")],
}

CLEFS = {"va": [(57, 32, "treble")]}  # the run into the bridge (S07 returns to alto at 62)

OTTAVA = []

ALLOW = set()
