"""S09 · bars 74-77 · Arpeggios 琶音 (melody over 16ths).

Harmony (one chord per bar, pedalled in the piano):
  74 E-flat maj9 · 75 F(add9) · 76 Gm(add9) · 77 Dm7  -> 78 E-flat (S10).

Texture
- Vn I: the RH upper voice, the 3+3+2 dotted-8th melody (D6. B-flat5. G5,
  C6. A5. F5, ...), at the piano's sounding pitch (the 8va of 76 gives
  B-flat6 A6 F6, still <= C7).  74-75 legato, one slur per half bar with
  portato (tenuto under the slur) on the dotted notes, no accents (the
  piano has no marks here); 76-77 (the lift) separate bows, the dotted
  notes accented, the repeated B-flats / Ds sung out.  The accents are
  kept for the lift so the 8va step is marked by articulation as well as
  by bowing.
- Vn II: the RH 16th arpeggio figure, one player, one slur per beat
  (string crossings; the slurs say legato, so no text), at pitch in
  74/75/77 so its top notes meet the melody in unison (the piano's shared
  noteheads); in 76 an octave below the piano's 8va (B-flat6 is above
  Vn II's range), so the violins open up to two octaves while Vn I climbs.
- Va: the pedal, sustained chord tones as half notes in the empty middle
  register between the cello's arpeggio and Vn II's figure: the LH top
  notes D4 C4 D4 D4 as the lower voice, under a rising upper voice G4 F4
  B-flat4 D5 (double stops: fourths, then a sixth and the octave over the
  open D string in 76-77, growing into the breakdown).  Only the tones
  the piano keeps re-striking through each bar are held (G/D, C/F,
  B-flat/D, D), so nothing sustains a note the piano has let go of.
- Vc: the LH ascending 16th arpeggio exactly at pitch (E-flat2 B-flat2 F3
  G3 ...), slurred per beat across the strings.
Dynamics: the piano has none here; the passage breathes after the runs and
then builds into the breakdown: melody mf, accompaniment mp (cello mf, the
bass arpeggio must speak), crescendo through 75 to f at the 8va lift (76),
and a further crescendo through 77 into 78.
"""

VN1 = {
    74: "(D6/12- Bb5/12- G5/8) (D6/12- Bb5/12- G5/8)",
    75: "(C6/12- A5/12- F5/8) (C6/12- A5/12- F5/8)",
    76: "Bb6/12> Bb6/12> Bb6/8 Bb6/12> A6/12> F6/8",
    77: "D6/12> D6/12> D6/8 D6/12> C6/12> D6/8",
}

VN2 = {
    74: "(D6/4 G5/4 D5/4 Bb5/4) (G5/4 D5/4 G5/4 D5/4) "
        "(D6/4 G5/4 D5/4 Bb5/4) (G5/4 D5/4 G5/4 D5/4)",
    75: "(C6/4 F5/4 C5/4 A5/4) (F5/4 C5/4 F5/4 C5/4) "
        "(C6/4 F5/4 C5/4 A5/4) (F5/4 C5/4 F5/4 C5/4)",
    76: "(Bb5/4 D5/4 Bb4/4 Bb5/4) (D5/4 Bb4/4 Bb5/4 Bb4/4) "
        "(Bb5/4 D5/4 Bb4/4 A5/4) (D5/4 Bb4/4 F5/4 Bb4/4)",
    77: "(D6/4 F5/4 D5/4 D6/4) (F5/4 D5/4 D6/4 D5/4) "
        "(D6/4 F5/4 D5/4 C6/4) (F5/4 D5/4 D6/8)",
}

VA = {
    74: "D4+G4/32 D4+G4/32",
    75: "C4+F4/32 C4+F4/32",
    76: "D4+Bb4/32 D4+Bb4/32",
    77: "D4+D5/32 D4+D5/32",
}

VC = {
    74: "(Eb2/4 Bb2/4 F3/4 G3/4) (Eb3/4 G3/4 Bb3/4 D4/4) "
        "(Eb2/4 Bb2/4 F3/4 G3/4) (Eb3/4 G3/4 Bb3/4 D4/4)",
    75: "(F2/4 C3/4 G3/4 A3/4) (F3/4 A3/4 Bb3/4 C4/4) "
        "(F2/4 C3/4 G3/4 A3/4) (F3/4 A3/4 Bb3/4 C4/4)",
    76: "(G2/4 D3/4 G3/4 A3/4) (G3/4 Bb3/4 C4/4 D4/4) "
        "(G2/4 D3/4 G3/4 A3/4) (G3/4 Bb3/4 C4/4 D4/4)",
    77: "(D2/4 A2/4 D3/4 F3/4) (D3/4 F3/4 A3/4 D4/4) "
        "(D2/4 A2/4 D3/4 F3/4) (D3/4 A3/4 D4/8)",
}

DYN = {
    "vn1": [(74, 0, "mf"), (76, 0, "f")],
    "vn2": [(74, 0, "mp"), (76, 0, "mf")],
    "va": [(74, 0, "mp"), (76, 0, "mf")],
    "vc": [(74, 0, "mf"), (76, 0, "f")],
}

HAIR = {
    # grow into the 8va lift (76), then into the breakdown (78)
    "vn1": [(75, 32, 75, 63, "cresc"), (77, 0, 77, 63, "cresc")],
    "vn2": [(75, 32, 75, 63, "cresc"), (77, 0, 77, 63, "cresc")],
    "va": [(75, 32, 75, 63, "cresc"), (77, 0, 77, 63, "cresc")],
    "vc": [(75, 32, 75, 63, "cresc"), (77, 0, 77, 63, "cresc")],
}

TEXT = {
    "vn1": [(74, 0, "espressivo")],
    "va": [(74, 0, "sostenuto")],
    "vc": [(74, 0, "legato")],
}

CLEFS = {}
OTTAVA = []
ALLOW = set()
