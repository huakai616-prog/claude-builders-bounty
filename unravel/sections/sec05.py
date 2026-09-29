"""S05 · bars 36–49 · Chorus 副歌 (ff).

Piano: RH = four-note chords in the 3+3+2 dotted-8th rhythm, melody on top
(octave-framed voicings: the tied syncopations are X4+..+X5 chords); LH =
whole-note low octave (X1+X2), 8th-rest + 16th/8th stabs (X2, X2+X3 dyads),
then a descending 16th arpeggio from X4 ending on the low X1 8th.  From 44
the LH becomes a rocking 16th figure with accented low notes on every beat;
48 = the LH's up/down sweep, 49 = the closing chord (tied into 50).

Quartet:
- Vn I: the RH top line at pitch (all ≤ G6).  Octave double stops only on
  the long notes where the RH voicing itself is octave-framed and the leap
  is easy: A4+A5 (36–37), C5+C6 (38), G4+G5 (41, 49), Bb4+Bb5 (41–42,
  48), F4+F5 (45).  43 = the low melody (A4 Bb4 A4 F4) on the D string.
- Vn II: the two inner notes of each RH chord as double stops in the same
  dotted rhythm (sixths/thirds/fourths across A/E strings), marcato;
  single lower octave where the RH has only an octave (C5, Bb4, A4).  43 =
  the RH's inner 16ths (A4 F4 D4 / Bb4 F4 D4 / A4 F4), slurred.
- Va: the LH middle layer, one player: the stabs an octave up (Eb3,
  Bb3+Eb4 …; 43 at pitch like 39) and the descending arpeggio an octave up
  (Eb5 Bb4 G4 Eb4 Bb3 Eb3), détaché.  43: the arpeggio at pitch too
  (D4 A3 F3 D3, the last two A2 F2 folded up to A3 F3) so the viola stays
  under the low melody (A4/F4).  44–47: the LH's three off-beat 16ths
  of every beat (+8ve), the cello taking the accented beat.  48: doubles
  the cello's sweep an octave higher from beat 2.  49: the LH chord
  (A3+F4) held under the sus chord.
- Vc: the LH low whole notes as sustained single low notes (Eb2, F2, D2 on
  the C string; an Eb2+Eb3-type octave across C/G strings needs thumb
  position) = the piano pedal; G2+G3 octaves on the open G (38, 42).  Plus
  the low 8th that ends each LH arpeggio.  44–47: the LH's accented low
  notes, marcato 8ths.  48: the whole up/down sweep (Eb2 Eb3 … G4 … Eb3,
  Eb2).  49: low F held, re-struck (unaccented) on beat 4.
Dynamics: ff tutti; the held chord of 42 relaxes in all four parts, 43 f
with a crescendo into the second half (44 ff); swell on the up-sweep (48,
the level then held through the climax); only 49 dies away toward the mp
interlude.
"""

VN1 = {
    36: "D6/12 C6/12 C6/8 C6/12 Bb5/12 A4+A5/8>~",
    37: "A4+A5/8 Bb5/16 A5/8>~ A5/8 F5/24",
    38: "D6/12 C6/12 C5+C6/8>~ C5+C6/8 Bb5/16 Bb5/8",
    39: "A5/12 Bb5/12 F6/8>~ F6/8 A5/16 Bb5/8",
    40: "G6/12 F6/12 D6/8>~ D6/8 Bb5/16 Bb5/8",
    41: "Bb5/16 A5/8 G4+G5/8>~ G4+G5/8 A5/16 Bb4+Bb5/8>~",
    42: "Bb4+Bb5/48 r/8 Bb4/8",
    43: "A4/12 Bb4/12 A4/8>~ A4/8 F4/16 D5/8",
    44: "D6/8 C6/4 C6/4>~ C6/8 C6/8 C6/8 Bb5/4 Bb5/4>~ Bb5/8 Bb5/8",
    45: "A5/12 Bb5/12 A5/8>~ A5/8 F4+F5/16 D5/8",
    46: "D6/8 C6/4 C6/4>~ C6/8 C6/8 C6/8 Bb5/4 Bb5/4>~ Bb5/8 Bb5/8",
    47: "A5/12 Bb5/12 F6/8>~ F6/8 A5/16 Bb5/8",
    48: "G6/12 F6/12 D6/8 Bb4+Bb5/24 Bb5/8",
    49: "Bb5/16 A5/8 G4+G5/8>~ G4+G5/8 A5/16 Bb5/8",
}

VN2 = {
    36: "G5+Bb5/12 Eb5+G5/12 Eb5+G5/8 Eb5+G5/12 Eb5+G5/12 C5+F5/8>~",
    37: "C5+F5/8 D5+F5/16 C5+F5/8>~ C5+F5/8 A4+C5/24",
    38: "G5+Bb5/12 F5+A5/12 F5+A5/8>~ F5+A5/8 D5+G5/16 Bb4/8",
    39: "D5+F5/12 D5+F5/12 A5+D6/8>~ A5+D6/8 D5+F5/16 Bb4/8",
    40: "Bb5+Eb6/12 Bb5+D6/12 F5+Bb5/8>~ F5+Bb5/8 D5+F5/16 Bb4/8",
    41: "C5+F5/16 A4/8 C5+F5/8>~ C5+F5/8 A4/16 D5+G5/8>~",
    42: "D5+G5/48 r/16",
    43: "(A4/4 F4/4 D4/4) (Bb4/4 F4/4 D4/4) (A4/4 F4/4) r/16 r/8 D4/8",
    44: "G5+Bb5/8 C5/4 Eb5+G5/4>~ Eb5+G5/8 C5/8 Eb5+G5/8 Bb4/4 "
        "Eb5+G5/4>~ Eb5+G5/8 Bb4/8",
    45: "C5+F5/12 Bb4/12 C5+F5/8>~ C5+F5/8 A4+C5/16 D4/8",
    46: "G5+Bb5/8 C5/4 F5+A5/4>~ F5+A5/8 C5/8 F5+A5/8 Bb4/4 "
        "D5+G5/4>~ D5+G5/8 Bb4/8",
    47: "D5+F5/12 Bb4/12 A5+D6/8>~ A5+D6/8 D5+F5/16 Bb4/8",
    48: "Bb5+Eb6/12 Bb5+D6/12 D5/8 D5+F5/24 Bb4/8",
    49: "C5+F5/16 A4/8 C5+F5/8>~ C5+F5/8 A4/16 D5+G5/8",
}


def _stab_arp(r, fifth_root, top, a1, a2, a3, a4, a5):
    """LH middle layer of 36-43: 8th rest, R 16th, (5th+R) 8th, R, (5th+R),
    then the descending 16th arpeggio (six notes); the low 8th = Vc."""
    return (f"r/8 {r}/4 {fifth_root}/8 {r}/4 {fifth_root}/8 "
            f"{top}/4 {a1}/4 {a2}/4 {a3}/4 {a4}/4 {a5}/4 r/8")


def _rock(hi, mid, lo):
    """44-47: the three off-beat 16ths of the LH's rocking figure."""
    beat = f"r/4 {hi}/4 {mid}/4 {lo}/4 r/4 {lo}/4 {mid}/4 {hi}/4"
    return beat + " " + beat


VA = {
    36: _stab_arp("Eb3", "Bb3+Eb4", "Eb5", "Bb4", "G4", "Eb4", "Bb3", "Eb3"),
    37: _stab_arp("F3", "C4+F4", "F5", "C5", "A4", "F4", "C4", "F3"),
    38: _stab_arp("G3", "D4+G4", "G5", "D5", "Bb4", "G4", "D4", "G3"),
    39: _stab_arp("D3", "A3+D4", "D5", "A4", "F4", "D4", "A3", "D3"),
    40: _stab_arp("Eb3", "Bb3+Eb4", "Eb5", "Bb4", "G4", "Eb4", "Bb3", "Eb3"),
    41: _stab_arp("F3", "C4+F4", "F5", "C5", "A4", "F4", "C4", "F3"),
    42: _stab_arp("G3", "D4+G4", "G5", "D5", "Bb4", "G4", "D4", "G3"),
    # 43: the LH stabs are single notes (D3, A3) — played at pitch; the
    # arpeggio at pitch as well (A2 F2 folded up) so it stays under the
    # low melody A4/F4 instead of above it
    43: _stab_arp("D3", "A3", "D4", "A3", "F3", "D3", "A3", "F3"),
    44: _rock("Eb4", "Bb3", "Eb3"),
    45: _rock("F4", "C4", "F3"),
    46: _rock("G4", "D4", "G3"),
    47: _rock("D4", "A3", "D3"),
    # 48: joins the cello's sweep an octave higher on beat 2
    48: "r/16 Bb3/4 Eb4/4 Bb4/4 Eb5/4 G5/4 Eb5/4 Bb4/4 Eb4/4 Eb3/16",
    # 49: the LH chord A3 C4 F4 (held), released before the Bb chord
    49: "r/24 A3+F4/24 r/16",
}

VC = {
    # single low notes: octaves from the C string to the G string need
    # thumb position; only the open-G octave (38, 42) is kept
    36: "Eb2/56> Eb2/8",
    37: "F2/56> F2/8",
    38: "G2+G3/56> G2/8",
    39: "D2/56> D2/8",
    40: "Eb2/56> Eb2/8",
    41: "F2/56> F2/8",
    42: "G2+G3/56> G2/8",
    43: "D2/56> D2/8",
    44: "Eb2/8! r/8 Eb2/8! r/8 Eb2/8! r/8 Eb2/8! r/8",
    45: "F2/8! r/8 F2/8! r/8 F2/8! r/8 F2/8! r/8",
    46: "G2/8! r/8 G2/8! r/8 G2/8! r/8 G2/8! r/8",
    47: "D2/8! r/8 D2/8! r/8 D2/8! r/8 D2/8! r/8",
    48: "Eb2/4 Eb3/4 Eb2/4 Eb3/4 Bb2/4 Eb3/4 Bb3/4 Eb4/4 "
        "G4/4 Eb4/4 Bb3/4 Eb3/4 Eb2/16>",
    49: "F2/48> F2/16",
}

DYN = {
    "vn1": [(36, 0, "ff"), (42, 56, "f"), (44, 0, "ff")],
    "vn2": [(36, 0, "ff"), (43, 0, "f"), (44, 0, "ff")],
    "va": [(36, 8, "ff"), (43, 8, "f"), (44, 4, "ff")],
    "vc": [(36, 0, "ff"), (43, 0, "f"), (44, 0, "ff")],
}

HAIR = {
    # 42: all four parts relax to the f of 43 (violins on the held chord,
    # va/vc on the arpeggio); 43 grows into 44; 48: the lower parts swell
    # on the up-sweep and keep the level under the violins' G6 climax;
    # only 49 dies away toward the mp interlude
    "vn1": [(42, 8, 42, 44, "dim"), (43, 24, 43, 60, "cresc"),
            (49, 40, 49, 60, "dim")],
    "vn2": [(42, 8, 42, 44, "dim"), (43, 24, 43, 60, "cresc"),
            (49, 40, 49, 60, "dim")],
    "va": [(42, 32, 42, 56, "dim"), (43, 24, 43, 60, "cresc"),
           (48, 4, 48, 28, "cresc"), (49, 24, 49, 44, "dim")],
    "vc": [(42, 32, 42, 60, "dim"), (43, 24, 43, 60, "cresc"),
           (48, 0, 48, 28, "cresc"), (49, 40, 49, 60, "dim")],
}

TEXT = {
    "vn1": [(36, 0, "con forza")],
    "vn2": [(36, 0, "marcato"), (43, 0, "legato"), (44, 0, "marcato")],
    "va": [(36, 8, "détaché")],
    "vc": [(36, 0, "sostenuto")],
}

CLEFS = {}

OTTAVA = []

ALLOW = set()
