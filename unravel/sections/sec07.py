"""S07 · bars 58-65 · Bridge 桥段 -> climax.

58-61  Vn I = RH melody, upper octave (C7 / B-flat6 / A6, under an 8va
       line for 58-61 only, as the piano's), Vn II = the RH lower octave;
       both f, the 16th leading into each syncopation slurred (58/60) or
       portato on the repeated A (59/61).  Va = the LH's treble-clef 16th
       figure at pitch (treble clef), two beats per bow (one beat per bow in
       the crescendo bar 61); the LH's bass note on beat 1 goes to the
       cello, the viola starts its bar on the figure's upper note.  Va and
       Vc at f straight on from S06's crescendo.  Vc = the LH root of each
       bar at the piano's pitch (Eb3, G3, F3, G3: the LH is in treble clef
       here), held as a whole note on the D string, the piano's pedal; the
       low octave is saved for 62.  Crescendo in 61 into the climax.
62-64  ff.  Vn I loco from 62 (whole-bar ottava engine; B-flat6 / C7 on
       ledger lines read at pitch).  Violins = the RH chords: first half
       low (Vn I G5+C6 / C6 with Vn II C5+Eb5 / C5+F5), then Vn I leaps an
       octave as the piano's 8va does (B-flat6, C7) while Vn II stays in
       3rd position (Eb5+C6 / F5+C6), octave B-flats between them.
       Va = the LH 16th pattern at pitch, reshaped for adjacent strings
       (open G bariolage; in 63 the open D gives the Gm11 its fifth),
       détaché.
       Vc = the LH low notes as marcato quarters, octave leaps (Eb3 Eb2 ...).
65     Held C7 -> B-flat6, then the three accented Gm(add9) hits, tutti,
       rolled triple stops on open strings, marcato, down-bows; Vn II's A
       sits at the piano's octave (G5 A5 under Vn I's B-flat5 G6 = the
       piano's G5-A5-B-flat5 cluster under G6); the last hit is not tied
       over (S08 restrikes the chord on 66).
"""

VN1 = {
    58: "C7/8 (Bb6/4 C7/4~ C7/8) Bb6/8 C7/8 (Bb6/4 C7/4~ C7/8) Bb6/8",
    59: "A6/8 (A6/4- A6/4-~ A6/8) A6/8 A6/8 (A6/4- A6/4-~ A6/8) Bb6/8",
    60: "C7/8 (Bb6/4 C7/4~ C7/8) Bb6/8 C7/8 (Bb6/4 C7/4~ C7/8) Bb6/8",
    61: "A6/8 (A6/4- A6/4-~ A6/8) A6/8 A6/8 (A6/4- A6/4-~ A6/8) Bb5/8",
    62: "G5+C6/8 Bb5/4 G5+C6/4-~ G5+C6/8 Bb6/8 "
        "C7/8 Bb6/4 C7/4-~ C7/8 Bb5/8",
    63: "C6/8 Bb5/4 C6/4-~ C6/8 Bb6/8 C7/8 Bb6/4 C7/4-~ C7/8 Bb5/8",
    64: "C6/8 Bb5/4 C6/4-~ C6/8 Bb6/8 C7/12 Bb6/12 C7/8-~",
    65: "C7/8 Bb6/24 Bb5+G6/12!db Bb5+G6/12!db Bb5+G6/8!db",
}

VN2 = {
    58: "C6/8 (Bb5/4 C6/4~ C6/8) Bb5/8 C6/8 (Bb5/4 C6/4~ C6/8) Bb5/8",
    59: "A5/8 (A5/4- A5/4-~ A5/8) A5/8 A5/8 (A5/4- A5/4-~ A5/8) Bb5/8",
    60: "C6/8 (Bb5/4 C6/4~ C6/8) Bb5/8 C6/8 (Bb5/4 C6/4~ C6/8) Bb5/8",
    61: "A5/8 (A5/4- A5/4-~ A5/8) A5/8 A5/8 (A5/4- A5/4-~ A5/8) r/8",
    62: "C5+Eb5/8 Bb4/4 C5+Eb5/4-~ C5+Eb5/8 Bb5/8 "
        "Eb5+C6/8 Bb5/4 Eb5+C6/4-~ Eb5+C6/8 Bb4/8",
    63: "C5+F5/8 Bb4/4 C5+F5/4-~ C5+F5/8 Bb5/8 "
        "F5+C6/8 Bb5/4 F5+C6/4-~ F5+C6/8 Bb4/8",
    64: "C5+F5/8 Bb4/4 C5+F5/4-~ C5+F5/8 Bb5/8 "
        "F5+C6/12 Bb5/12 F5+C6/8-~",
    65: "F5+C6/8 Bb5/24 D4+G5+A5/12!db D4+G5+A5/12!db D4+G5+A5/8!db",
}

VA = {
    58: "(Eb4/4 F4/4 Eb4/4 F4/4 Bb3/4 G4/4 A4/4 Bb4/4) "
        "(F5/4 D5/4 C5/4 D5/4 Eb4/4 Bb4/4 A4/4 Bb4/4)",
    59: "(G3/4 F4/4 D4/4 F4/4 Bb3/4 G4/4 A4/4 Bb4/4) "
        "(F5/4 D5/4 C5/4 D5/4 G4/4 Bb4/4 A4/4 Bb4/4)",
    60: "(C4/4 F4/4 C4/4 F4/4 Bb3/4 F4/4 Bb4/4 C5/4) "
        "(F5/4 C5/4 Bb4/4 C5/4 F4/4 Bb4/4 A4/4 Bb4/4)",
    61: "(G3/4 F4/4 D4/4 F4/4) (Bb3/4 G4/4 A4/4 Bb4/4) "
        "(F5/4 D5/4 C5/4 D5/4) (G4/4 Bb4/4 A4/4 Bb4/4)",
    62: "Bb3/4 Eb4/4 G3/4 Eb3/4 G3/4 Eb3/4 G3/4 Eb4/4 "
        "Bb3/4 Eb4/4 G3/4 Eb3/4 G3/4 Eb3/4 G3/4 Eb4/4",
    63: "G3/4 G4/4 D4/4 G3/4 G4/4 G3/4 Bb3/4 G4/4 "
        "G3/4 G4/4 D4/4 G3/4 G4/4 G3/4 Bb3/4 G4/4",
    64: "C4/4 F4/4 A3/4 F3/4 C4/4 F3/4 A3/4 F4/4 "
        "C4/4 F4/4 A3/4 F3/4 Bb3/4 F3/4 A3/4 F4/4",
    65: "G3/4 G4/4 Bb3/4 G3/4 r/16 "
        "G3+D4+Bb4/12!db G3+D4+Bb4/12!db G3+D4+Bb4/8!db",
}

VC = {
    58: "Eb3/64",
    59: "G3/64",
    60: "F3/64",
    61: "G3/64",
    62: "Eb3/16 Eb2/16 Eb3/16 Eb2/16",
    63: "G3/16 G2/16 G3/16 G2/16",
    64: "F3/16 F2/16 F3/16 F2/16",
    65: "G3/16 G2/16 G2+D3+Bb3/12!db G2+D3+Bb3/12!db G2+D3+Bb3/8!db",
}

DYN = {
    "vn1": [(58, 0, "f"), (62, 0, "ff")],
    "vn2": [(58, 0, "f"), (62, 0, "ff")],
    "va": [(58, 0, "f"), (62, 0, "ff")],
    "vc": [(58, 0, "f"), (62, 0, "ff")],
}

HAIR = {
    "vn1": [(61, 0, 61, 56, "cresc"), (65, 8, 65, 32, "cresc")],
    "vn2": [(61, 0, 61, 56, "cresc"), (65, 8, 65, 32, "cresc")],
    "va": [(61, 0, 61, 56, "cresc")],
    "vc": [(61, 0, 61, 56, "cresc"), (65, 16, 65, 32, "cresc")],
}

TEXT = {
    "vn1": [],
    "vn2": [],
    "va": [(62, 0, "détaché")],
    "vc": [(58, 0, "sostenuto"), (62, 0, "marcato")],
}

CLEFS = {
    "va": [(58, 0, "treble"), (62, 0, "alto")],
}

# The piano's 8va covers 58-61 (to pos 48), then only the upper half of
# 62-64 and beats 1-2 of 65.  The engine takes whole bars, so the line
# covers 58-61 (the loco pickup B-flat5 at 61/56 is the one note under it)
# and 62-65 are written at pitch, so the hits and double stops read loco.
OTTAVA = [("vn1", 58, 61)]

# 58-61: the cello holds each bar's LH root (Eb3, G3, F3, G3, the LH's own
# pitch) as a whole note: that is the piano's pedal (the LH strikes Eb3 /
# G3 / F3 once and lets it ring under the treble-clef 16th arpeggio).
# build.check()'s pedal model already covers these held roots, so they
# need no ALLOW entry.
ALLOW = {
    # 63: the piano's LH strikes the dyad Bb3+D4 four times (+8 +24 +40
    # +56) between the G3 / G2 bass notes.  The viola cannot double-stop in
    # fast 16ths, so its bariolage takes the dyad's D4 (open D string) on
    # the 1st and 3rd strikes and Bb3 on the 2nd and 4th: the Gm11 keeps
    # its fifth (without it the quartet had only G Bb C F for the whole
    # bar).  The real bass (G3 / G2 marcato) is in the cello on every
    # beat and Bb sounds throughout in the violins.  Checked: without this
    # entry the only items in 58-65 are BASS Bb3 at 63 +8 and +40.
    ("bass", 63),
}
