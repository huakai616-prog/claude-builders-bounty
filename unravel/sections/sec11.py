"""S11 · bars 82–89 · Pre-Chorus 导歌 II (like 32–35).

82–85  the S04 texture: Va = LH 16th ostinato (at pitch, détaché),
       Vc = the LH low bass (G2 Eb2 F2 G2) held for the whole bar, as in
       S04 (the piano's pedal made audible),
       Vn I = RH upper voice (A4 Bb4 A4 A4), Vn II = RH lower voice
       (F4 D4 D4 · D4 C4 D4 D4 · F4).  mp/p, small swell in 85.
86–88  four layers: Vn I = RH 16th figure (D5 A4 Bb4 F4, slurred per
       group, 3+3+2), Vn II = LH top syncopated line (same rhythm as
       82–85; from 88 beat 2.5 it takes the RH lower voice's echo of the
       hook, D5 A4 Bb4 F4, holding F4), Va = LH ostinato (G3 Bb3 Bb3 …),
       Vc = LH bass held (F2 through 88 beat 3).  Cresc.
       through to f on the chord at 88 beat 4 (Gm7: Vc G2+G3, Va D4+F4,
       Vn II Bb4, Vn I D5).  In 88 beats 3–4 the LH lower line A3 G3 Bb3
       G2 is shared: Va A3 (G3 Bb3), Vc G3 then G2 (G2+G3).
89     Vn I = the RH's lower octave, Eb5 D5 D6 C6 (no 8va; the upper
       octave would reach D7 and then drop a 7th into S12's D6), tied in
       from the chord's D5; Vn II doubles Eb5 D5 in unison; then the
       "bloom" of the LH triplet:
       Va adds G4 then A4, Vn II adds Bb4 then D5 (held second voices),
       over the cello's held open-G octave.  Dim. to arrive p at 90.
"""

VN1 = {
    82: "r/16 r/8 A4/8 (Bb4/8 A4/4) A4/4 r/16",
    83: "r/16 r/8 A4/8 (Bb4/8 A4/4) A4/4 r/16",
    84: "r/16 r/8 A4/8 (Bb4/8 A4/4) A4/4 r/16",
    85: "r/16 r/8 A4/8 (Bb4/8 A4/4) A4/4 r/16",
    86: "(D5/4 A4/4 Bb4/4 F4/4) r/8 (D5/4 A4/4 Bb4/4 F4/4) r/8 "
        "(D5/4 A4/4 Bb4/8)",
    87: "(D5/4 A4/4 Bb4/4 F4/4) r/8 (D5/4 A4/4 Bb4/4 F4/4) r/8 "
        "(D5/4 A4/4 Bb4/8)",
    88: "(D5/4 A4/4 Bb4/4 F4/4) r/8 D5/8- (C5/12 D5/12) D5/8~",
    # the piano's lower octave (Eb5 D5 D6 C6): leads straight into S12's D6
    89: "D5/8 (Eb5/8 D5/16) D6/16 C6/16",
}

VN2 = {
    82: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    83: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    84: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    85: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    86: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    87: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    # from 2.5: the RH lower voice's echo of the hook, F4 held to the chord
    88: "F4/8 D4/4 D4/4 r/8 (D5/4 A4/4 Bb4/4 F4/4~ F4/16) Bb4/8~",
    # held Bb4 (tie) -> Eb5 D5 doubling Vn I, then the bloom: Bb4, + D5
    89: "Bb4/8 (Eb5/8 D5/8) {3:2 r/8 Bb4/4~ } Bb4/32 | r/32 D5/32",
}

_OST = ("r/4 G3/4 F3/4 G3/4 D3/4 F3/4 G3/4 A3/4 "
        "Bb3/4 G3/4 F3/4 G3/4 D3/4 G3/4 F3/4 G3/4")
VA = {
    82: _OST,
    83: _OST,
    84: _OST,
    85: _OST,
    86: "r/4 G3/4 Bb3/4 Bb3/4 G3/4 A3/4 Bb3/4 G3/4 "
        "A3/4 G3/4 Bb3/4 Bb3/4 G3/4 A3/4 D4/4 G3/4",
    87: "r/4 Eb3/4 Bb3/4 Bb3/4 G3/4 A3/4 Bb3/4 G3/4 "
        "A3/4 G3/4 Bb3/4 Bb3/4 G3/4 A3/4 D4/4 G3/4",
    88: "r/4 F3/4 Bb3/4 Bb3/4 G3/4 A3/4 Bb3/4 G3/4 "
        "A3/8 (G3/4 Bb3/8) r/4 D4+F4/8~",
    # tied D4+F4, then the bloom: G4 at the triplet, + A4 (second voice)
    89: "D4+F4/8 r/16 G4/40 | r/16 r/8 {3:2 r/4 A4/8~ } A4/32",
}

VC = {
    82: "G2/64",                          # the pedal bass held, as in S04
    83: "Eb2/64",
    84: "F2/64",
    85: "G2/64",
    86: "G2/64",
    87: "Eb2/64",
    88: "F2/40 G3/12 (G2/4 G2+G3/8~)",   # F2 carries the beat-3 F chord
    89: "G2+G3/64",                       # open-G octave held under the bloom
}

DYN = {
    "vn1": [(82, 24, "mp"), (86, 0, "mf"), (88, 56, "f")],
    "vn2": [(82, 0, "p"), (86, 0, "mp"), (88, 56, "f"), (89, 24, "mp")],
    "va": [(82, 4, "p"), (86, 4, "mp"), (88, 56, "f"), (89, 24, "mp")],
    "vc": [(82, 0, "p"), (86, 0, "mp"), (88, 56, "f")],
}

HAIR = {
    "vn1": [(85, 24, 85, 47, "cresc"), (86, 0, 88, 52, "cresc"),
            (89, 32, 89, 63, "dim")],
    "vn2": [(85, 0, 85, 63, "cresc"), (86, 0, 88, 52, "cresc"),
            (89, 24, 89, 63, "dim")],
    "va": [(85, 4, 85, 63, "cresc"), (86, 4, 88, 52, "cresc"),
           (89, 24, 89, 63, "dim")],
    "vc": [(85, 0, 85, 63, "cresc"), (86, 0, 88, 52, "cresc"),
           (89, 0, 89, 63, "dim")],
}

TEXT = {
    "vn1": [(82, 24, "espressivo")],
    "vn2": [],
    "va": [(82, 4, "détaché")],
    "vc": [],
}

CLEFS = {}

OTTAVA = []

ALLOW = set()
