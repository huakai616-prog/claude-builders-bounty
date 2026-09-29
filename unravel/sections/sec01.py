"""S01 · bars 0-15 · Intro 前奏 (music box, then chorale).

0-4 (pp, sul tasto): violin duet.  Vn I = the RH melody an octave below
the piano's sounding 8va (the written notes), phrase slurs.  Vn II = the
LH's sustained notes (G dotted half + Bb quarter ...), also an octave down
so the spacing of the piano is kept and the melody stays on top (at pitch
the LH's G5 would sit above Vn I's D5 in bar 4).

5-15 (p): chorale, RH an octave below sounding throughout.
  Vn I  = top note of the RH chords / the melody (9-12).
  Vn II = RH inner note, held through the octave-only hits; the tied
          peak chord (5->6, 13->14) as a D5+Bb5 double stop so the
          violins keep the RH's D-Bb-D; on the RH's held chords (6, 8,
          14) it takes the LH's upper-voice sigh (C5-D5 / A4-Bb4) around
          the held chord tone, the tied note and the first sigh in one
          bow (so the pickups at 6/56 and 14/56 are up-bows with Vn I);
          9-12 the RH counter-line.
          Chord hits (5, 7, 13, 15) tenuto in both violins: separate
          bows, but full value, ringing like the piano's pedalled chords.
  Va    = the LH broken chord (3+3+2 eighths) at pitch, 2-bar slurs in
          5-12, one slur per bar under the crescendo 13-15 (the last F3
          of 15 separate, an up-bow pickup like the LH's plain eighth);
          in 14 the LH's F4 as open-G double stops (G3+F4).
  Vc    = the pedal: the lowest LH note of each bar an octave down,
          whole notes, long bows (8 and 12 release on beat 4 where the
          RH breathes before the melody's pickup); 15 re-strikes F2 on
          the last eighth with the LH's F3 (up-bow into 16's subito f).
No hairpins in the music-box duet (the piano has none); small swells with
the chorale hits 5-8, crescendo 13-14 into 15.
"""

VN1 = {
    0: "(Bb5/8",
    1: "C6/16 Bb5/16 A5/8 G5/16) (C6/8~",
    2: "C6/8 Bb5/16 A5/16 G5/16) (G5/8",
    3: "F5/24 Eb5/8) (Eb5/12 F5/12 D5/8~",
    4: "D5/48) r/8 D5/8",
    5: "D5/16- D5/8- D5/8-~ D5/8 D6/8- D6/16~",
    6: "D6/48 r/8 Bb5/8",
    7: "A5/16- A5/8- A5/8-~ A5/8 Bb5/8- Bb5/16~",
    8: "Bb5/48 r/8 (Bb5/8",
    9: "C6/16 Bb5/16 A5/8 G5/16) (C6/8~",
    10: "C6/8 Bb5/16 A5/16 G5/16) (G5/8",
    11: "F5/24 Eb5/8) (Eb5/12 F5/12 D5/8~",
    12: "D5/48) r/8 D5/8",
    13: "D5/16- D5/8- D5/8-~ D5/8 D6/8- D6/16~",
    14: "D6/48 r/8 Bb5/8",
    15: "A5/16- A5/8- A5/8-~ A5/8 Bb5/8- Bb5/16",
}

VN2 = {
    1: "(G4/48 Bb4/16)",
    2: "(Eb4/48 G4/16)",
    3: "(F4/48 A4/16)",
    4: "G4/48 r/8 D4/8",
    5: "Bb4/24- Bb4/8-~ Bb4/8 D5/8- (D5+Bb5/16~",
    6: "D5+Bb5/8 C5/8 D5/16) (C5/8 D5/16) Bb4/8",
    7: "C5/24- C5/8-~ C5/8 Bb4/8- Bb4/16~",
    8: "Bb4/8 (A4/8 Bb4/16) (A4/8 Bb4/8) r/16",
    9: "r/8 (C5/8 D5/8 Bb4/8 A4/8 Bb4/8 G4/16)",
    10: "(C5/8 D5/8 Bb4/8 A4/8 Bb4/8 G4/16) r/8",
    11: "(A4/8 Bb4/8 F4/8) r/8 (A4/12 Bb4/12 F4/8)",
    12: "r/8 (A4/8 Bb4/8) r/8 (A4/8 Bb4/8) r/8 D4/8",
    13: "Bb4/24- Bb4/8-~ Bb4/8 D5/8- (D5+Bb5/16~",
    14: "D5+Bb5/8 C5/8 D5/16) (C5/8 D5/16) Bb4/8",
    15: "C5/24- C5/8-~ C5/8 Bb4/8- Bb4/16",
}

VA = {
    5: "(Eb3/8 Bb3/8 G4/8 Eb3/8 Bb3/8 F4/8 Bb4/8 D5/8",
    6: "G3/8 D4/8 Bb4/8 G3/8 D4/8 Bb4/8 G3/8 D4/8)",
    7: "(F3/8 C4/8 A4/8 F3/8 C4/8 F4/8 Bb4/8 C5/8",
    8: "G3/8 D4/8 G4/8 G3/8 D4/8 G4/8 G3/8 D4/8)",
    9: "(Eb3/8 Bb3/8 G4/8 Eb3/8 Bb3/8 G4/8 Eb3/8 Bb3/8",
    10: "G3/8 D4/8 Bb4/8 G3/8 D4/8 Bb4/8 G3/8 D4/8)",
    11: "(F3/8 C4/8 A4/8 F3/8 C4/8 A4/8 F3/8 C4/8",
    12: "G3/8 D4/8 Bb4/8 G3/8 D4/8 Bb4/8 G3/8 D4/8)",
    13: "(Eb3/8 Bb3/8 G4/8 Eb3/8 Bb3/8 G4/8 Eb3/8 Bb3/8)",
    14: "(G3+F4/8 D4/8 Bb4/8 G3+F4/8 D4/8 Bb4/8 G3+F4/8 D4/8)",
    15: "(F3/8 C4/8 A4/8 F3/8 C4/8 A4/8 F3/8) F3/8",
}

VC = {
    5: "Eb2/64",
    6: "G2/64",
    7: "F2/64",
    8: "G2/48 r/16",
    9: "Eb2/64",
    10: "G2/64",
    11: "F2/64",
    12: "G2/48 r/16",
    13: "Eb2/64",
    14: "G2/64",
    15: "F2/56 F2/8",
}

DYN = {
    "vn1": [(0, 0, "pp"), (4, 56, "p"), (15, 0, "mp")],
    "vn2": [(1, 0, "pp"), (4, 56, "p"), (15, 0, "mp")],
    "va": [(5, 0, "pp"), (15, 0, "p")],
    "vc": [(5, 0, "pp"), (15, 0, "p")],
}

_SWELLS = [(5, 24, 5, 47, "cresc"), (6, 0, 6, 47, "dim"),
           (7, 24, 7, 47, "cresc"), (8, 0, 8, 47, "dim"),
           (13, 0, 14, 63, "cresc")]
HAIR = {
    "vn1": list(_SWELLS),
    "vn2": list(_SWELLS),
    "va": list(_SWELLS),
    "vc": list(_SWELLS),
}

TEXT = {
    "vn1": [(0, 0, "sul tasto, dolce"), (4, 48, "ord."),
            (8, 56, "cantabile")],
    "vn2": [(1, 0, "sul tasto"), (4, 48, "ord.")],
    "va": [(5, 0, "legato")],
    "vc": [(5, 0, "sost.")],
}

CLEFS = {}
OTTAVA = []

ALLOW = {
    # 10 +40 (Bb4) and 11 +16 (A4): the viola plays these LH notes (top of
    # the broken chord), but the RH counter-line in Vn II (G4 / F4, an
    # octave below sounding like the melody) crosses under it for one
    # eighth, so the "lowest attack" is the counter-line.  The real bass
    # (G2 / F2 in the cello, G3 / F3 in the viola) is intact.
    ("bass", 10), ("bass", 11),
}
