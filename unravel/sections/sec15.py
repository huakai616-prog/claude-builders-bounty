"""S15 · bars 118-132 · Coda 尾声 (p -> pp -> niente).

Texture
- 118-121: Vn II = the RH 8th broken figure (G4 Bb4 D5 ..., the melody of
  these bars), dolce, one slur per half bar.  Vn I holds the RH's long top
  note (Bb5) in 118 and fades out, rests, and returns on the pickup Bb5 of
  121.  S14 closes 117 with every part cut together on beat 4.5 (ff), so
  the Coda's downbeat is a subito pp: Vn I's Bb5 and the cello's new Eb2
  enter together, the pp alone marking it (no Vn I text at 118 pos 0: it
  would push rehearsal box P out of the system).  Va = the LH's syncopated
  dyads (Bb3+D4, A3+C4) as soft double stops in thirds, sul tasto.  Vc =
  the LH whole-note bass (Eb2 G2 F2 G2, the lower note of the piano's
  octaves), sul tasto.
- 122-127 (the intro chorale returns): Vn I = the RH melody (C6 Bb5 A5 /
  D5 D5 D5 D6), cantabile, with the pickups on beat 4.5.  Vn II = the RH's
  lower line: the chord's inner dyad under the melody's first note, the
  8ths on beats 3-4 (G4 Bb4 D5 / A4 Bb4 C5) and the answering 8th figures
  of 123/125/127 (F4 C5 D5 ...), slurred by the 3-note cell (3+3, the
  last F4 on its own bow), like the viola below.
  Va = the LH broken 8ths at pitch (Eb3 Bb3 G4 ...), slurred by the
  piano's 3-note cell (3+3+2), so the bow changes on the string skip back
  to the bottom note instead of skipping a string inside a slur.  Vc = the
  lowest LH note of each bar an octave down, held (the piano's pedal).
- 128: Vn I alone (A5 A5 A5 Bb5 Bb5), louré, dolce; the others rest.  The
  last Bb5 is an 8th with an 8th rest (every piano attack kept): a breath
  before the shift to the exposed pp D7 of 129.
- 129-130: Vn I = the 8va melody at the piano's sounding pitch (D7 C7 Bb6,
  written with an 8va line, dolcissimo; bow near the normal contact point,
  not flautando, which cracks this high on the E string) so the layers keep
  the piano's spacing: Vn II = the RH's 16th second voice an octave lower
  (D6 G5 D5 C6 G5 D5 Bb5), slurred in the piano's 3+3+2; Va = the LH 16th
  run at pitch (D4 ... C6, treble clef) under Vn I's held Bb6, no hairpins
  (the run's contour shapes itself at pp); Vc = open G2 (the piano's G3 an
  octave down), held to the end.  All four re-enter pp after the tacet 128.
- 131-132: the final G/Bb sonority (the piano holds only G3 + Bb5, so no
  D is added): Vc G2 (open), Va G3 (open, back in alto clef), Vn II G4,
  Vn I Bb5 -- the viola's last Bb5 of 130 is taken over by Vn I on the
  downbeat.  The piano strikes nothing on 131 (its G3 and Bb5 are tied
  over), so the chord should arrive as a release: Vc's G2 is tied over,
  Vn II slips in on G4 at 130 beat 3 (under the piano's held G3) and ties
  over, and Vn I and Va enter 'senza accento'.  pp, morendo, fermata on
  132.
Dynamics: the piano prints none here; the brief's p -> pp: Vn II p on the
figure 118-121, accompaniment pp, Vn I pp on its held note and p for the
melody from 121; a small swell to the D6 of 126 in Vn I, Va and Vc, with
the same hairpin spans in all three; dim. in 128, pp in all parts from
129, morendo to the end.
"""

VN1 = {
    118: "Bb5/64",
    121: "r/32 r/16 r/8 (Bb5/8",
    122: "C6/16 Bb5/16 A5/32)",
    123: "r/32 r/16 r/8 (Bb5/8",
    124: "C6/16 Bb5/16 A5/32)",
    125: "r/32 r/16 r/8 D5/8-",
    126: "D5/16- D5/8- D5/16- (D6/8- D6/16~",
    127: "D6/32) r/16 r/8 (Bb5/8",
    128: "A5/16) (A5/8- A5/16-) (Bb5/8- Bb5/8-) r/8",
    129: "(D6/12 C6/12 Bb5/8~ Bb5/32)",
    130: "(D6/12 C6/12 Bb5/8~ Bb5/32~)",
    131: "Bb5/64~",
    132: "Bb5/64^",
}

VN2 = {
    118: "r/8 (G4/8 Bb4/8 D5/8) (G4/8 Bb4/8 D5/8 G4/8)",
    119: "(C5/8 G4/8 Bb4/8 C5/8) (G4/8 Bb4/8 C5/8 G4/8)",
    120: "(C5/8 F4/8 A4/8 Bb4/8) (F4/8 A4/8 Bb4/8 F4/8)",
    121: "(C5/8 G4/8 A4/8 C5/8) (G4/8 Bb4/8 D5/8) r/8",
    122: "D5+F5/16 r/16 r/8 (G4/8 Bb4/8 D5/8)",
    123: "(F4/8 C5/8 D5/8) (F4/8 C5/8 D5/8) F4/8 r/8",
    124: "C5+F5/16 r/16 r/8 (A4/8 Bb4/8 C5/8)",
    125: "(F4/8 A4/8 Bb4/8) (F4/8 A4/8 Bb4/8) F4/8 r/8",
    126: "Bb4/16 r/16 r/32",
    127: "(F4/8 C5/8 D5/8) (F4/8 C5/8 D5/8) F4/8 r/8",
    129: "(D6/4 G5/4 D5/4) (C6/4 G5/4 D5/4 Bb5/8) r/32",
    130: "(D6/4 G5/4 D5/4) (C6/4 G5/4 D5/4 Bb5/8) G4/32~",
    131: "G4/64~",
    132: "G4/64^",
}

VA = {
    118: "r/24 Bb3+D4/24- Bb3+D4/16-",
    119: "r/24 Bb3+D4/24- Bb3+D4/16-",
    120: "r/24 A3+C4/24- A3+C4/16-",
    121: "r/24 Bb3+D4/24- Bb3+D4/16-",
    122: "(Eb3/8 Bb3/8 G4/8) (Eb3/8 Bb3/8 G4/8) (Eb3/8 Bb3/8)",
    123: "(G3/8 D4/8 Bb4/8) (G3/8 D4/8 Bb4/8) (G3/8 D4/8)",
    124: "(F3/8 C4/8 A4/8) (F3/8 C4/8 A4/8) (F3/8 C4/8)",
    125: "(G3/8 D4/8 G4/8) (G3/8 D4/8 G4/8) (G3/8 D4/8)",
    126: "(Eb3/8 Bb3/8 G4/8) (Eb3/8 Bb3/8 G4/8) (Eb3/8 Bb3/8)",
    127: "(G3/8 D4/8 Bb4/8) (G3/8 D4/8 Bb4/8) (G3/8 D4/8)",
    129: "r/4 (D4/4 G4/4 A4/4 G4/4 A4/4 Bb4/4 D5/4) "
         "(G4/4 Bb4/4 A4/4 Bb4/4 C5/4 Bb4/4 A4/4 Bb4/4)",
    130: "r/4 (D4/4 G4/4 A4/4 G4/4 A4/4 Bb4/4 D5/4) "
         "(G4/4 Bb4/4 A4/4 Bb4/4 C5/4 Bb4/4 A4/4 Bb4/4)",
    131: "G3/64~",
    132: "G3/64^",
}

VC = {
    118: "Eb2/64",
    119: "G2/64",
    120: "F2/64",
    121: "G2/64",
    122: "Eb2/64",
    123: "G2/64",
    124: "F2/64",
    125: "G2/64",
    126: "Eb2/64",
    127: "G2/64",
    129: "G2/64",
    130: "G2/64~",
    131: "G2/64~",
    132: "G2/64^",
}

DYN = {
    "vn1": [(118, 0, "pp"), (121, 56, "p"), (129, 0, "pp")],
    "vn2": [(118, 8, "p"), (122, 0, "pp"), (129, 0, "pp")],
    "va": [(118, 24, "pp"), (129, 4, "pp")],
    "vc": [(118, 32, "pp"), (129, 0, "pp")],
}

HAIR = {
    # 118: the held Bb5 fades under Vn II's figure; one shared swell to the
    # D6 of 126 and back (same spans in Vn I, Va, Vc); 128 the lone line
    # dies away into the 8va pp; morendo.
    "vn1": [(117, 56, 118, 32, "dim"), (125, 56, 126, 40, "cresc"),
            (126, 48, 127, 32, "dim"), (128, 24, 128, 63, "dim"),
            (131, 0, 132, 63, "dim")],
    "vn2": [(121, 0, 121, 55, "dim"), (131, 0, 132, 63, "dim")],
    "va": [(125, 56, 126, 40, "cresc"), (126, 48, 127, 32, "dim"),
           (131, 0, 132, 63, "dim")],
    "vc": [(125, 56, 126, 40, "cresc"), (126, 48, 127, 32, "dim"),
           (131, 0, 132, 63, "dim")],
}

TEXT = {
    "vn1": [(121, 56, "cantabile"), (128, 0, "dolce"),
            (129, 0, "dolcissimo"), (131, 0, "senza accento, morendo")],
    "vn2": [(118, 8, "subito, dolce, legato"), (129, 0, "leggiero"),
            (131, 0, "morendo")],
    "va": [(118, 24, "subito, sul tasto"), (122, 0, "ord., legato"),
           (131, 0, "senza accento, morendo")],
    "vc": [(118, 0, "subito, sul tasto"), (131, 0, "morendo")],
}

CLEFS = {}

OTTAVA = []  # the last music-box statement sits an octave below the piano, like 90-96

# The piano plays 122-127 with the pedal down: each bar's LH root (Eb3 /
# G3 / F3) rings under the broken 8ths.  The cello holds it as a whole note
# an octave down (ARRANGING "pedal -> sustain", brief S15 "Vc = the lowest
# note of each LH group sustained"), which the literal (unpedalled) FOREIGN
# window flags between the LH's re-strikes of the root.  Verified
# separately: without the cello these bars have no FOREIGN item, and every
# cello note is the LH's lowest pitch class of its bar.
ALLOW = set()  # the pedal model covers the held cello roots
