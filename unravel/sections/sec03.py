"""S03 · bars 24–31 · Verse 主歌 (p).

Texture
- Vn I = the RH melody at the piano's pitch (B-flat5 … D6 on the E string),
  p cantabile.  Bowing by phrase: the repeated syllable notes are slurred
  with tenuto dashes (louré), so the line stays one breath but every
  syllable speaks.  Bows: 24 down (3 beats) / up (B-flat5 D6); 25 down
  (3.5 beats) / up from the B-flat5 pickup through C6 B-flat5 A5 of 26;
  down F5 D5 with the dim; the A5 pickup of 27 on its own up-bow (as the
  A5 of 23), so 28 starts down-bow like 24 and each bar of 28–31 starts
  on a down-bow.
  In 31 the melody's tail drops to D4 C4 (G/D strings), a sighing two-note
  slur; Vn I then rests.
- Vn II = the sustained upper inner voice of the RH chords (the piano's
  repeated chords tied into long notes): D5 over Gm(add9), D5 → B-flat4 over
  E-flat maj7 (the major seventh held as long as the piano holds it),
  C5 over F, A4 over B-flat maj7, D5 → C5 over F6.  In 31 it holds D5 of
  the B-flat chord, rests under the melody's low tail and takes the RH's
  F4 pickup (+56) into its own pre-chorus line (S04 Vn II starts on F4).
- Va = the lower inner voice in the piano's rhythm, the repeated chord
  note on +24 held through (half ⌒ 8th, then the 8th "dip" to the root and
  the quarter): A4 G4 B-flat4 / G4 E-flat4 G4 / F4 B-flat4 F4 B-flat4 …,
  two bows per bar (the chord, then dip + dyad).  27: held F4 of
  the B-flat maj7 chord.  31: the LH's F (the upper LH note, Va is free)
  — F4, dropping to F3 under the melody's low D4 C4, then a rest before the
  pre-chorus ostinato.
- Vc = the lower LH note of each whole-note dyad an octave down (G2 open
  string, E-flat2, F2, B-flat2 → A2), one long warm bow per bar; the upper
  LH notes are in the violins / viola chords.
- Dynamics: melody p (set by S02 on the A5 pickup), accompaniment pp;
  one set of hairpins for all four: swells to the top of each phrase
  (25, 29), a taper at the phrase ends (26–27, 30–31).  Vn II and Vc lean
  into the p of the pre-chorus on their last notes.
"""

VN1 = {
    24: "(Bb5/12- Bb5/12- Bb5/8-~ Bb5/16) (Bb5/8 D6/8)",
    25: "(D6/12- C6/12- C6/8-~ C6/24) (Bb5/8",
    26: "C6/12 Bb5/12 A5/8~ A5/8) (F5/16 D5/8~",
    27: "D5/48) r/8 A5/8",
    28: "(Bb5/8- Bb5/4- Bb5/4-~ Bb5/16~ Bb5/8) (Bb5/16 D6/8)",
    29: "(D6/12- C6/12- C6/8-~ C6/8) Bb5/24",
    30: "(D6/16 C6/8- C6/8-~ C6/16) (A5/8 Bb5/8~",
    31: "Bb5/24) (D4/8 C4/16) r/16",
}

VN2 = {
    24: "D5/64",
    25: "(D5/40 Bb4/24)",
    26: "C5/64",
    27: "A4/48 r/16",
    28: "D5/64",
    29: "(D5/40 Bb4/24)",
    30: "(D5/40 C5/24)",
    31: "D5/24 r/8 r/16 r/8 F4/8",
}

VA = {
    24: "A4/40 (G4/8 Bb4/16)",
    25: "G4/40 (Eb4/8 G4/16)",
    26: "(F4/24 Bb4/16) (F4/8 Bb4/16)",
    27: "F4/48 r/16",
    28: "A4/40 (G4/8 Bb4/16)",
    29: "G4/40 (Eb4/8 G4/16)",
    30: "(Bb4/24 A4/16) (F4/8 A4/16)",
    31: "F4/24 F3/24 r/16",
}

VC = {
    24: "G2/64",
    25: "Eb2/64",
    26: "F2/64",
    27: "(Bb2/48 A2/16)",
    28: "G2/64",
    29: "Eb2/64",
    30: "F2/64",
    31: "(Bb2/48 A2/16)",
}

DYN = {
    # the melody p (as the piano), the accompaniment a step below it.
    # Vn I: no mark on 24 — S02 already gives p on its A5 pickup (23/+56),
    # a second p one 8th later would print "p p".
    "vn1": [],
    "vn2": [(24, 0, "pp")],
    "va": [(24, 0, "pp")],
    "vc": [(24, 0, "pp")],
}

# one phrase shape for the whole ensemble (homophonic verse): swell to the
# top of each phrase (25, 29), taper through the falling line to the phrase
# end (27, 31)
_ACC_HAIR = [(24, 24, 24, 63, "cresc"), (26, 0, 27, 40, "dim"),
             (28, 32, 28, 63, "cresc"), (30, 24, 31, 24, "dim")]

HAIR = {
    # same spans as the accompaniment; the swells reach the D6 on the next
    # downbeat, and the last dim runs on into the D4 C4 sigh of 31
    "vn1": [(24, 24, 25, 0, "cresc"), (26, 0, 27, 40, "dim"),
            (28, 32, 29, 0, "cresc"), (30, 24, 31, 32, "dim")],
    # Vn II's F4 pickup and the cello's A2 lean into the p of the
    # pre-chorus (bar 32)
    "vn2": _ACC_HAIR + [(31, 56, 31, 63, "cresc")],
    "va": list(_ACC_HAIR),
    "vc": _ACC_HAIR + [(31, 48, 31, 63, "cresc")],
}

TEXT = {
    "vn1": [(24, 0, "cantabile")],
    # one word for the three accompaniment parts; it also cancels the
    # spicc. of bar 23 in Va and Vc
    "vn2": [(24, 0, "legato")],
    "va": [(24, 0, "legato")],
    "vc": [(24, 0, "legato")],
}

CLEFS = {}
OTTAVA = []
ALLOW = set()
