"""S12 · bars 90–96 · Music Box 八音盒 (p, the piano plays the RH 8va).

Texture
- Vn I: the RH top-note melody (dotted-8th rhythm), one octave below the
  piano's 8va throughout (its peak F7/G7 in 93–94 is out of range, and one
  octave for the whole section keeps the contour: D6 ... G6).  Dolce, phrase
  slurs; the repeated B-flats of 94 as louré.  96: holds B-flat5, then the
  pickup B-flat5 into the chorus at the piano's own pitch.
- Vn II: the RH 16th music-box figure, the same octave as Vn I (so its top
  notes meet the melody in unison, like the piano's shared noteheads),
  leggiero spiccato, one player.  95/96: the syncopated B-flat4+D5 chord
  (the piano's written Bb4+D5 under the 8va) tied into 96.
- Va: the LH middle layer at pitch: the dotted-8th pickups and the chord
  bottom as a half note (the chord's third and fifth are in Vn II's
  figure), sul tasto.  96: the LH 16th arpeggio (G4 B-flat4 D4 ...), ord.,
  crescendo into the chorus.
- Vc: the LH lowest notes as whole notes at pitch (E-flat3 F3 G3 D3 ...),
  sul tasto; 96: open G2+D3 (the piano's G3+D4 an octave down, open-string
  resonance), ord., crescendo.
Dynamics: melody p, accompaniment pp; a small swell to the phrase peak (94)
and back, then p/pp < into the chorus at 97.
"""

VN1 = {
    90: "(D6/12 C6/12) C6/8 (C6/12 Bb5/12) Bb5/8",
    91: "(A5/12 Bb5/12 A5/8~ A5/8 F5/24)",
    92: "(D6/12 C6/12) C6/8 (C6/12 Bb5/12) Bb5/8",
    93: "(A5/12 Bb5/12 F6/8~ F6/8 A5/24)",
    94: "(G6/12 F6/12 D6/8~ D6/8) (Bb5/16- Bb5/8-)",
    95: "(Bb5/16 A5/8 G5/8~ G5/8 A5/16 Bb5/8~",
    96: "Bb5/48) r/8 Bb5/8-",
}

VN2 = {
    90: "D6/4 G5/4 Eb5/4 C6/4 G5/4 Eb5/4 C6/4 Eb5/4 "
        "C6/4 G5/4 Eb5/4 Bb5/4 G5/4 Eb5/4 Bb5/4 Eb5/4",
    91: "A5/4 F5/4 C5/4 Bb5/4 F5/4 C5/4 A5/4 C5/4 "
        "C5/4 C5/4 F5/4 C5/4 C5/4 C5/4 F5/4 A5/4",
    92: "D6/4 G5/4 D5/4 C6/4 G5/4 D5/4 C6/4 D5/4 "
        "C6/4 G5/4 D5/4 Bb5/4 G5/4 D5/4 Bb5/4 D5/4",
    93: "A5/4 F5/4 D5/4 Bb5/4 F5/4 D5/4 F6/4 D5/4 "
        "D5/4 D5/4 A5/4 D5/4 D5/4 D5/4 F5/4 Bb5/4",
    94: "G6/4 Bb5/4 G5/4 F6/4 Bb5/4 G5/4 D6/4 Eb5/4 "
        "Eb5/4 Eb5/4 Bb5/4 Eb5/4 Eb5/4 Eb5/4 Bb5/4 Eb5/4",
    95: "Bb5/4 F5/4 C5/4 C5/4 A5/4 C5/4 G5/4 C5/4 "
        "C5/4 C5/4 A5/4 C5/4 C5/4 C5/4 Bb4+D5/8~",
    96: "Bb4+D5/48 r/16",
}

VA = {
    90: "r/12 Eb4/12 (Eb4/8 Bb4/32)",
    91: "r/12 F4/12 (F4/8 C5/32)",
    92: "r/12 G4/12 (G4/8 D5/32)",
    93: "r/12 D4/12 (D4/8 D5/32)",
    94: "r/12 Eb4/12 (Eb4/8 Bb4/32)",
    95: "r/12 F4/12 (F4/8 C5/32)",
    96: "r/4 G4/4 Bb4/4 D4/4 G4/4 Bb4/4 D4/4 G4/4 "
        "D5/4 D4/4 G4/4 Bb4/4 D4/4 G4/4 Bb4/4 D4/4",
}

VC = {
    90: "Eb3/64",
    91: "F3/64",
    92: "G3/64",
    93: "D3/64",
    94: "Eb3/64",
    95: "F3/64",
    96: "G2+D3/64",
}

DYN = {
    "vn1": [(90, 0, "p"), (94, 0, "mp"), (96, 0, "p")],
    "vn2": [(90, 0, "pp"), (94, 0, "p"), (95, 56, "pp")],
    "va": [(90, 12, "pp"), (94, 12, "p"), (96, 4, "pp")],
    "vc": [(90, 0, "pp"), (94, 0, "p"), (96, 0, "pp")],
}

HAIR = {
    # swell to the phrase peak (F7/G7 in the piano) and back
    "vn1": [(93, 0, 93, 63, "cresc"), (94, 16, 95, 56, "dim"),
            (96, 0, 96, 63, "cresc")],
    "vn2": [(93, 0, 93, 63, "cresc"), (94, 16, 95, 48, "dim"),
            (95, 56, 96, 47, "cresc")],
    "va": [(93, 12, 93, 63, "cresc"), (94, 32, 95, 60, "dim"),
           (96, 4, 96, 63, "cresc")],
    "vc": [(93, 0, 93, 63, "cresc"), (94, 16, 95, 60, "dim"),
           (96, 0, 96, 63, "cresc")],
}

TEXT = {
    "vn1": [(90, 0, "dolce, cantabile")],
    "vn2": [(90, 0, "leggiero, spicc.")],
    "va": [(90, 12, "sul tasto"), (96, 4, "ord.")],
    "vc": [(90, 0, "sul tasto"), (96, 0, "ord.")],
}

CLEFS = {}
OTTAVA = []
ALLOW = set()
