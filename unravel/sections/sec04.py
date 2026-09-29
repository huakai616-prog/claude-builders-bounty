"""S04 · bars 32–35 · Pre-Chorus 导歌 (build).

32–33  Va = the LH 16th ostinato at pitch (G3 F3 G3 D3 …, on the open G
       and C strings), détaché, p.  Vc = the LH's low G2, held for the
       whole bar on the open G string (the piano's pedal made audible).
       Vn I = the RH upper voice (A4 Bb4 A4 A4, syncopated), mp espressivo;
       Vn II = the RH lower voice (F4 D4 D4 · D4 C4 D4 D4 · F4), p.
34     The ostinato runs on in Va to the Bb3 8th, then the RH chords take
       over: each violin keeps its line and adds the chord note above it
       (Vn I A4+D5 / Bb4+C5, Vn II D4+F4 / C4+F4), so the piano's
       four-note RH voicing is in the two violins.  On the syncopated hits
       (+44, +56 tied over) all four play: Vc the LH octave G2+G3, Va the
       open G3+D4, violins as before.  Vc holds G2 for the first half bar
       (the pedal) and rests on the Bb3 chord.
35     Beat 1 = the tied chord, then everybody breathes; the LH triplet
       (G3 D4 F4, rising into Bb4) goes to Va, slurred, over the cello's
       held open-G octave (the piano's tied "bloom"); beats 3–4: the
       Gm7 and F chords spread over four, accented (Vn I Bb5+D6 / A5+C6 =
       the RH top, Vn II D5+F5 / C5+F5, Va Bb4 → A4, Vc on beat 4 the
       rolled triple stop F2+C3+F3 in first position: 4th finger across C
       and G strings, 2nd on D, which keeps the LH F octave; a plain F2+F3
       octave is a 4th stretch and not playable low on the cello).  Both
       chords retaken down-bow, the Va triplet an up-bow lift.
       Cresc. through 34–35 in all parts into the ff of the chorus (36).
"""

_OST = ("r/4 G3/4 F3/4 G3/4 D3/4 F3/4 G3/4 A3/4 "
        "Bb3/4 G3/4 F3/4 G3/4 D3/4 G3/4 F3/4 G3/4")

VN1 = {
    32: "r/16 r/8 A4/8 (Bb4/8 A4/4) A4/4 r/16",
    33: "r/16 r/8 A4/8 (Bb4/8 A4/4) A4/4 r/16",
    34: "r/16 r/8 A4+D5/8 Bb4+C5/8 r/4 A4+D5/8 r/4 A4+D5/8~",
    35: "A4+D5/16 r/16 Bb5+D6/16>db A5+C6/16>db",
}

VN2 = {
    32: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    33: "F4/8 D4/4 D4/4 r/8 D4/8 (C4/8 D4/4) D4/4 r/8 F4/8",
    34: "F4/8 D4/4 D4/4 r/8 D4+F4/8 C4+F4/8 r/4 D4+F4/8 r/4 D4+F4/8~",
    35: "D4+F4/16 r/16 D5+F5/16>db C5+F5/16>db",
}

VA = {
    32: _OST,
    33: _OST,
    34: "r/4 G3/4 F3/4 G3/4 D3/4 F3/4 G3/4 A3/4 "
        "Bb3/8 r/4 G3+D4/8 r/4 G3+D4/8~",
    # tied open-string chord, breath, then the LH triplet rising into Bb4
    35: "G3+D4/16 r/8 {3:2 (G3/4ub D4/4 F4/4) } Bb4/16>db A4/16>db",
}

VC = {
    32: "G2/64",                        # open G, the pedal
    33: "G2/64",
    34: "G2/32 r/8 r/4 G2+G3/8 r/4 G2+G3/8~",
    35: "G2+G3/48 F2+C3+F3/16>db",      # held under the triplet, then rolled F
}

DYN = {
    "vn1": [(32, 24, "mp")],
    "vn2": [(32, 0, "p")],
    "va": [(32, 4, "p")],
    "vc": [(32, 0, "p")],
}

HAIR = {
    "vn1": [(34, 24, 35, 63, "cresc")],
    "vn2": [(34, 0, 35, 63, "cresc")],
    "va": [(34, 4, 35, 63, "cresc")],
    "vc": [(34, 0, 35, 63, "cresc")],
}

TEXT = {
    "vn1": [(32, 24, "espressivo")],
    "vn2": [],
    "va": [(32, 4, "détaché")],
    "vc": [],
}

CLEFS = {}

OTTAVA = []

ALLOW = set()
