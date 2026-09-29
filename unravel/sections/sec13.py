"""S13 · bars 97–107 · Chorus 副歌 II (97–103) + Interlude 间奏 (104–107).

Texture
- 97–103 (chorus II, f):
  - Vn I: the RH melody (top notes of the chords) at the piano's pitch,
    cantabile, slurred by phrase; the repeated C6/Bb5 of 98/100 detached.
  - Vn II: the RH chord tones under the melody as double stops, in the
    piano's own chord rhythm (the syncopated "chord . chord- ." of the even
    bars; chord on 1 in the odd bars, plus the "and" of 2 in 99 and 101
    where the RH has a chord there), resting where the RH is a single
    melody note (97 beats 2-4).  103: the anticipated G-minor chord
    (D5+G5) on the last eighth, released at the barline.
  - Va: the LH middle layer at pitch.  97: continues its 16th arpeggio from
    96 (D4 F4 A3 ... D3).  98–102: the LH's repeated 16ths (Eb4 Eb4 Eb4 +
    the G4+Bb4 dyad on beats 2 and 4) as driving détaché 16ths; the dyad is
    a two-string double stop with one flat finger, so the figure stays in
    one hand position.  103: the LH 16th run F3 ... F5 ... F3 across all
    four strings.
  - Vc: the LH bass an octave down on beats 1 and 3 as half notes (D2+A2
    in 97, where the piano holds D3+A3 for the whole bar: a stopped fifth,
    one flat first finger across the C and G strings, kept for the weight
    of the chorus downbeat; single roots in 98–103 because the piano's
    fifth is only a 16th).  103: F2 sustained through beat 3 under the
    viola's descending run (the piano's pedal holds the F), re-struck on
    the LH's beat-4 F.
  - Swell through 101, dim. from the chorus peak (G6, 102) through 103
    into the interlude.
- 104–107 (interlude, mp -> cresc. into the final chorus):
  - Vn I: holds the tied Bb5 of the 103 chord through 104 (dim.), rests in
    105, re-enters with the pickup Bb5 and sings the RH melody (C6 Bb5 C6 ...
    D6) espressivo.  Bowing: pickup up, (C6 Bb5 C6) down, (Bb5 C6~C6) up,
    D6 down (its own bow for the cresc.), Bb5 up, so 108 starts down-bow.
  - Vn II: the RH 16th broken figure (104 rh2, 105 rh, 106–107 rh2) at
    pitch, leggiero spiccato, one player; its top notes meet the melody in
    unison where the piano shares noteheads.
  - Va: the LH upper voice at pitch (dotted-8th rest, Eb3 Eb3, half-note
    dyad G3+Bb3 etc.).
  - Vc: the LH whole-note bass (Eb2 F2 G2 D2), sustained.
  - The three lower parts start their cresc. together at 107 (not under the
    melody's re-entry in 106).
"""

VN1 = {
    97: "(A5/12 Bb5/12 A5/16) (F5/16 D5/8)",
    98: "(D6/8 C6/4) C6/12 C6/8 (C6/8 Bb5/4) Bb5/12 Bb5/8",
    99: "(A5/12 Bb5/12 A5/16) (F5/16 D5/8)",
    100: "(D6/8 C6/4) C6/12 C6/8 (C6/8 Bb5/4) Bb5/12 Bb5/8",
    101: "(A5/12 Bb5/12 F6/16) (A5/16 Bb5/8)",
    102: "(G6/12 F6/12 D6/16) Bb5/16 Bb5/8",
    103: "Bb5/16 (A5/8 G5/16) A5/16 Bb5/8~",
    104: "Bb5/64",
    105: "r/56 Bb5/8",
    106: "(C6/12 Bb5/12 C6/16) (Bb5/16 C6/8~",
    107: "C6/8) D6/48 Bb5/8",
}

VN2 = {
    97: "D5+F5/12 r/4 r/16 r/32",
    98: "Eb5+G5/8 r/4 Eb5+G5/12 r/8 Eb5+G5/8 r/4 Eb5+G5/12 r/8",
    99: "C5+F5/12 r/12 C5+F5/16 r/24",
    100: "F5+Bb5/8 r/4 F5+Bb5/12 r/8 F5+Bb5/8 r/4 F5/12 r/8",
    101: "D5+F5/12 r/12 A5+D6/16 r/24",
    102: "Bb5+Eb6/12 r/12 Bb5/16 G5/16 r/8",
    103: "C5+F5/16 r/40 D5+G5/8",
    104: "r/4 D4/4 G4/4 Bb4/4 D4/4 G4/4 Bb4/4 D4/4 "
         "D5/4- D4/4 G4/4 Bb4/4 D4/4 G4/4 Bb4/4 D4/4",
    105: "C5/4- C4/4 F4/4 Bb4/4 C4/4 F4/4 Bb4/4 C4/4 "
         "C5/4- C4/4 F4/4 Bb4/4 C4/4 F4/4 Bb4/8",
    106: "C6/4 F5/4 D5/4 Bb5/4 F5/4 D5/4 C6/4 F5/4 "
         "D5/4 F5/4 Bb5/4 F5/4 D5/4 F5/4 C6/4 F5/4",
    107: "D5/4 F5/4 D6/4 F5/4 D5/4 F5/4 D5/4 F5/4 "
         "D5/4 F5/4 D5/4 F5/4 D5/4 F5/4 r/8",
}

VA = {
    97: "r/4 D4/4 F4/4 A3/4 D4/4 F4/4 A3/4 D4/4 "
        "D5/4 A4/4 F4/4 D4/4 A3/4 F3/4 D3/8",
    98: "Eb4/4 Eb4/4 Eb4/4 Eb4/4 G4+Bb4/4 Eb4/4 Eb4/4 Eb4/4 "
        "Eb4/4 Eb4/4 Eb4/4 Eb4/4 G4+Bb4/4 Eb4/4 Eb4/4 Eb4/4",
    99: "F4/4 F4/4 F4/4 F4/4 A4+C5/4 F4/4 F4/4 F4/4 "
        "F4/4 F4/4 F4/4 F4/4 A4+C5/4 F4/4 F4/4 F4/4",
    100: "G4/4 G4/4 G4/4 G4/4 Bb4+D5/4 G4/4 G4/4 G4/4 "
         "G4/4 G4/4 G4/4 G4/4 Bb4+D5/4 G4/4 G4/4 G4/4",
    101: "D4/4 D4/4 D4/4 D4/4 F4+A4/4 D4/4 D4/4 D4/4 "
         "D4/4 D4/4 D4/4 D4/4 F4+A4/4 D4/4 D4/4 D4/4",
    102: "Eb4/4 Eb4/4 Eb4/4 Eb4/4 G4+Bb4/4 Eb4/4 Eb4/4 Eb4/4 "
         "Eb4/4 Eb4/4 Eb4/4 Eb4/4 G4+Bb4/4 Eb4/4 Eb4/4 Eb4/4",
    103: "(F3/4 C4/4 F4/4 G4/4 A4/4 C5/4 F5/4 C5/4) "
         "(A4/4 G4/4 F4/4 C4/4) F3/16",
    104: "r/12 Eb3/12- Eb3/8- G3+Bb3/32",
    105: "r/12 F3/12- F3/8- A3+C4/32",
    106: "r/12 G3/12- G3/8- Bb3+D4/32",
    107: "r/12 D3/12- D3/8- F3+A3/32",
}

VC = {
    97: "D2+A2/64",
    98: "Eb2/32 Eb2/32",
    99: "F2/32 F2/32",
    100: "G2/32 G2/32",
    101: "D2/32 D2/32",
    102: "Eb2/32 Eb2/32",
    103: "F2/48 F2/16",
    104: "Eb2/12- Eb2/12- Eb2/8-~ Eb2/32",
    105: "F2/12- F2/12- F2/8-~ F2/32",
    106: "G2/12- G2/12- G2/8-~ G2/32",
    107: "D2/12- D2/12- D2/8-~ D2/32",
}

DYN = {
    "vn1": [(97, 0, "f"), (105, 56, "mf")],
    "vn2": [(97, 0, "f"), (104, 4, "mp")],
    "va": [(97, 4, "mf"), (104, 12, "mp")],
    "vc": [(97, 0, "f"), (104, 0, "mp")],
}

HAIR = {
    # swell through 101 (each cresc. ends on the last note before the
    # barline), dim. from the chorus peak (G6 downbeat of 102) into the
    # interlude; then all four cresc. together in 107 (Vn I from its D6)
    # into the ff of the final chorus
    "vn1": [(101, 0, 101, 63, "cresc"), (102, 0, 104, 63, "dim"),
            (107, 8, 107, 56, "cresc")],
    "vn2": [(101, 0, 101, 63, "cresc"), (102, 0, 103, 56, "dim"),
            (107, 0, 107, 56, "cresc")],
    "va": [(101, 0, 101, 63, "cresc"), (102, 0, 103, 63, "dim"),
           (107, 0, 107, 63, "cresc")],
    "vc": [(101, 0, 101, 63, "cresc"), (102, 0, 103, 63, "dim"),
           (107, 0, 107, 63, "cresc")],
}

TEXT = {
    "vn1": [(97, 0, "cantabile"), (105, 56, "espressivo")],
    "vn2": [(104, 4, "leggiero, spicc.")],
    "va": [(98, 0, "détaché")],
    "vc": [],
}

CLEFS = {}
OTTAVA = []
ALLOW = set()
