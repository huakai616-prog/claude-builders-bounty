"""S07 · bars 58-65 · Bridge 桥段 -> climax.

58-61  Vn I = RH melody, upper octave (C7 / B-flat6 / A6, under an 8va
       line), Vn II = the RH lower octave; both f, cantabile, the 16th
       leading into each syncopation slurred (58/60) or portato on the
       repeated A (59/61).  Va = the LH's treble-clef 16th figure at pitch
       (treble clef), legato two beats per bow; the LH's bass note on beat 1
       goes to the cello, the viola starts its bar on the figure's upper
       note.  Vc = the LH root of each bar (Eb, G, F, G) held as a whole
       note, the piano's pedal.  Crescendo in 61 into the climax.
62-64  ff.  Violins = the RH chords: first half loco (Vn I G5+C6 / C6 with
       Vn II C5+Eb5 / C5+F5), then Vn I leaps an octave as the piano's 8va
       does (B-flat6, C7) while Vn II stays in 3rd position (Eb5+C6 /
       F5+C6), octave B-flats between them.  Va = the LH 16th pattern at
       pitch, reshaped for adjacent strings (open G bariolage), détaché.
       Vc = the LH low notes as marcato quarters, octave leaps (Eb3 Eb2 ...).
65     Held C7 -> B-flat6, then the three accented Gm(add9) hits, tutti,
       rolled triple stops on open strings, marcato, down-bows; the last
       hit is not tied over (S08 restrikes the chord on 66).
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
    65: "F5+C6/8 Bb5/24 D4+A4+G5/12!db D4+A4+G5/12!db D4+A4+G5/8!db",
}

VA = {
    58: "(Eb4/4 F4/4 Eb4/4 F4/4 Bb3/4 G4/4 A4/4 Bb4/4) "
        "(F5/4 D5/4 C5/4 D5/4 Eb4/4 Bb4/4 A4/4 Bb4/4)",
    59: "(G3/4 F4/4 D4/4 F4/4 Bb3/4 G4/4 A4/4 Bb4/4) "
        "(F5/4 D5/4 C5/4 D5/4 G4/4 Bb4/4 A4/4 Bb4/4)",
    60: "(C4/4 F4/4 C4/4 F4/4 Bb3/4 F4/4 Bb4/4 C5/4) "
        "(F5/4 C5/4 Bb4/4 C5/4 F4/4 Bb4/4 A4/4 Bb4/4)",
    61: "(G3/4 F4/4 D4/4 F4/4 Bb3/4 G4/4 A4/4 Bb4/4) "
        "(F5/4 D5/4 C5/4 D5/4 G4/4 Bb4/4 A4/4 Bb4/4)",
    62: "Bb3/4 Eb4/4 G3/4 Eb3/4 G3/4 Eb3/4 G3/4 Eb4/4 "
        "Bb3/4 Eb4/4 G3/4 Eb3/4 G3/4 Eb3/4 G3/4 Eb4/4",
    63: "G3/4 G4/4 Bb3/4 G3/4 G4/4 G3/4 Bb3/4 G4/4 "
        "G3/4 G4/4 Bb3/4 G3/4 G4/4 G3/4 Bb3/4 G4/4",
    64: "C4/4 F4/4 A3/4 F3/4 C4/4 F3/4 A3/4 F4/4 "
        "C4/4 F4/4 A3/4 F3/4 Bb3/4 F3/4 A3/4 F4/4",
    65: "G3/4 G4/4 Bb3/4 G3/4 r/16 "
        "G3+D4+Bb4/12!db G3+D4+Bb4/12!db G3+D4+Bb4/8!db",
}

VC = {
    58: "Eb2/64",
    59: "G2/64",
    60: "F2/64",
    61: "G2/64",
    62: "Eb3/16 Eb2/16 Eb3/16 Eb2/16",
    63: "G3/16 G2/16 G3/16 G2/16",
    64: "F3/16 F2/16 F3/16 F2/16",
    65: "G3/16 G2/16 G2+D3+Bb3/12!db G2+D3+Bb3/12!db G2+D3+Bb3/8!db",
}

DYN = {
    "vn1": [(58, 0, "f"), (62, 0, "ff")],
    "vn2": [(58, 0, "f"), (62, 0, "ff")],
    "va": [(58, 0, "mf"), (62, 0, "ff")],
    "vc": [(58, 0, "mf"), (62, 0, "ff")],
}

HAIR = {
    "vn1": [(61, 0, 61, 56, "cresc"), (65, 8, 65, 32, "cresc")],
    "vn2": [(61, 0, 61, 48, "cresc"), (65, 8, 65, 32, "cresc")],
    "va": [(61, 0, 61, 60, "cresc")],
    "vc": [(61, 0, 61, 60, "cresc"), (65, 16, 65, 32, "cresc")],
}

TEXT = {
    "vn1": [(58, 0, "cantabile")],
    "vn2": [],
    "va": [(58, 0, "legato"), (62, 0, "détaché")],
    "vc": [(58, 0, "sostenuto"), (62, 0, "marcato")],
}

CLEFS = {
    "va": [(58, 0, "treble"), (62, 0, "alto")],
}

OTTAVA = [("vn1", 58, 65)]

# The cello holds each bar's LH root (Eb2, G2, F2, G2) as a whole note:
# that is the piano's pedal (the LH strikes Eb3 / G3 / F3 once and lets it
# ring under the treble-clef 16th arpeggio).  The source data has no pedal,
# so the held root reads as FOREIGN in the beats where the LH figure has
# moved to other chord tones.  Checked: without these entries the only
# FOREIGN items in 58-61 are exactly those roots (Eb / G / F / G); melody,
# bass and every other part are clean.
ALLOW = set()  # the pedal model covers the held cello roots
