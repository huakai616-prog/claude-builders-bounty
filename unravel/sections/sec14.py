"""S14 · bars 108–117 · Final Chorus 终副歌 (ff, fullest).

Texture
- 108–111 (the RH chord melody over the 16th "echo" line, LH bass octave +
  3+3+2 pulse + chord stab + falling arpeggio):
  - Vn I: the melody at the piano's pitch (G6 F6 D6 B-flat5 B-flat5, the
    3+3+2 hits accented), the two long notes as the RH chord's own top
    pair (B-flat5+D6, a third in 6th position with the G6/F6; D5+B-flat5, a
    1-2 sixth in 3rd position) — not octaves, which would sit in unison on
    Vn II's D5/B-flat4 echo, drop the chord's B-flat/D and cost three
    shifts a bar.  Bowing as from 112: db db (up) db ub, so each bar ends
    up-bow into the down-bow G6.  Appassionato.
  - Vn II: the RH second voice (the 16th echo pairs G5 G5 / F5 F5 / D5 D5 D5
    / B-flat4 ...) at pitch, detache; the 16th rest at the head of each
    group is filled with the RH chord's middle note (B-flat5, the common
    tone of the first three chords, then F5), accented, so the 3+3+2 hit
    has its inner harmony; the last 8th = the RH chord's D5+F5.  111 ends
    with the RH's D4+D5 octave pickup (open D).
  - Va: the LH upper voice at pitch: the E-flat3 / F3 / G3 / D3 pulse
    (dotted 8th + 8th), the chord stab as a sixth that keeps the stab's
    bottom note (B-flat3+G4, C4+A4, D4+B-flat4; in 111 the full rolled
    triple stop F3+A3+D4, so the D chord keeps its A), then the falling
    16th arpeggio (E-flat4 B-flat3 G3 E-flat3 ...), first position with the
    open strings, detache.
  - Vc: the LH low octave (lh2) as a sustained note at the cello octave
    (E-flat2, F2, G2, D2 — pedal -> sustain); the arpeggio's last two notes,
    below the viola's C string, fall into the cello as its pickup to the
    next bass note (B-flat2 E-flat2 -> F2, C3 F2 -> G2, D3 G2 -> D2 ...).
- 112–117 (the big chords, 3+3+2 over the LH's 8th oom-pah):
  - Vn I + Vn II together play the RH's four-note chords at pitch: the RH
    chords are octave-framed, so Vn I takes the outer octave (melody + its
    lower octave, D5+D6 C5+C6 B-flat4+B-flat5 ... G5+G6 at the 116 peak)
    and Vn II the two inner notes (G5+B-flat5, E-flat5+G5 ...).  Marcato,
    down-bow on the dotted-8th hits, up-bow on the 8th before the next group
    (db db ub | db db ub).  Where the RH has only the melody octave (the
    passing B-flats/As), Vn II rests.  115's D minor middle is D5+A5 (one
    finger across, 1st position all bar) instead of A5+D6 in 6th position.
    The ub on the tied quarter at pos 24 (113, 115) is left implied after
    db db: with the marcato it engraves as one 'X' glyph.
  - Va: the LH off-beat chords (the "pah") as double stops keeping the
    chord's bottom note (B-flat3+G4, A3+F4), marcato; in 116 the LH's low
    E-flat fifths (an octave above the cello's) and the beat-3 chord.
  - Vc: the LH low notes on the beats: beat 1 a one-finger open fifth
    across the C and G strings (E-flat2+B-flat2, F2+C3, D2+A2; stopped
    octaves on C+G strings need a 5-semitone stretch, unplayable in the
    neck — only 114's G2+G3 over the open G stays an octave), the low note
    on beats 2–4 as marcato quarters (sustaining under the viola's
    off-beats); 116 the LH's E-flat fifths, the beat-4 upper E-flat3 in the
    viola.
  - 117 closes with weight, in time: the held chords tenuto, the cello's F2
    sustained (the viola has the F3/F4 above), the last chord (the
    anticipation of bar 118's G minor) down-bow, accented, not tied over the
    double bar.
Dynamics: ff tutti throughout (everybody at the same level); a small
crescendo (all four parts to the end of 111) arriving on ff at 112 (the
^ marks carry the marcato, no text).
"""

_M1 = "G6/12>db F6/12>db Bb5+D6/16> D5+Bb5/16db Bb5/8ub"
_E2 = ("Bb5/4> G5/4 G5/4 Bb5/4> F5/4 F5/4 Bb5/4> D5/4 D5/4 D5/4 "
       "F5/4> Bb4/4 Bb4/4 Bb4/4")

VN1 = {
    108: _M1,
    109: _M1,
    110: _M1,
    111: "G6/12>db F6/12>db Bb5+D6/16> D5+Bb5/16db r/8",
    112: "D5+D6/12!db C5+C6/12!db C5+C6/8!ub "
         "C5+C6/12!db Bb4+Bb5/12!db Bb4+Bb5/8!ub",
    113: "A4+A5/12!db Bb4+Bb5/12!db A4+A5/16! C5+F5/16!db D5/8>ub",
    114: "D5+D6/12!db C5+C6/12!db C5+C6/8!ub "
         "C5+C6/12!db Bb4+Bb5/12!db Bb4+Bb5/8!ub",
    115: "A4+A5/12!db Bb4+Bb5/12!db F5+F6/16! A4+A5/16!db Bb4+Bb5/8!ub",
    116: "G5+G6/12!db F5+F6/12!db D5+D6/8!ub Bb4+Bb5/24!db Bb4+Bb5/8!ub",
    117: "Bb4+Bb5/16!db A4+A5/8>ub G4+G5/16>-db A4+A5/16-ub "
         "Bb4+Bb5/8>-db",
}

VN2 = {
    108: _E2 + " D5+F5/8",
    109: _E2 + " D5+F5/8",
    110: _E2 + " D5+F5/8",
    111: "Bb5/4> G5/4 G5/4 Bb5/4> F5/4 F5/4 Bb5/4> D5/4 D5/4 D5/4 "
         "F5/16 D4+D5/8>",
    112: "G5+Bb5/12!db Eb5+G5/12!db Eb5+G5/8!ub "
         "Eb5+G5/12!db Eb5+G5/12!db Eb5+G5/8!ub",
    113: "C5+F5/12!db r/12 C5+F5/16! F4+A4/16!db r/8",
    114: "G5+Bb5/12!db F5+A5/12!db F5+A5/8!ub "
         "F5+A5/12!db D5+G5/12!db D5+G5/8!ub",
    115: "D5+F5/12!db r/12 D5+A5/16! D5+F5/16!db r/8",
    116: "Bb5+Eb6/12!db Bb5+D6/12!db r/8 D5+F5/24!db r/8",
    117: "C5+F5/16!db r/8 C5+F5/16>-db r/16 D5+G5/8>-db",
}

VA = {
    108: "r/12 Eb3/12> Eb3/8> Bb3+G4/8! Eb4/4 Bb3/4 G3/4 Eb3/4 r/8",
    109: "r/12 F3/12> F3/8> C4+A4/8! F4/4 C4/4 A3/4 F3/4 r/8",
    110: "r/12 G3/12> G3/8> D4+Bb4/8! G4/4 D4/4 Bb3/4 G3/4 r/8",
    111: "r/12 D3/12> D3/8> F3+A3+D4/8! D4/4 A3/4 D3/4 r/12",
    112: "r/8 Bb3+G4/8! r/8 Bb3+G4/8! r/8 Bb3+G4/8! r/8 Bb3+G4/8!",
    113: "r/8 A3+F4/8! r/8 A3+F4/8! r/8 A3+F4/8! r/8 A3+F4/8!",
    114: "r/8 Bb3+G4/8! r/8 Bb3+G4/8! r/8 Bb3+G4/8! r/8 Bb3+G4/8!",
    115: "r/8 A3+F4/8! r/8 A3+F4/8! r/8 A3+F4/8! r/8 A3+F4/8!",
    116: "r/8 Eb3+Bb3/8! Eb3+Bb3/8! Eb3+Bb3/8! Bb3+G4/16!db Eb3/16!ub",
    117: "F3+C4/16!db r/8 A3+F4/32- G3+D4/8>db",
}

VC = {
    108: "Eb2/56 Bb2/4 Eb2/4",
    109: "F2/56 C3/4 F2/4",
    110: "G2/56 D3/4 G2/4",
    111: "D2/52 A2/4 D2/8",
    112: "Eb2+Bb2/16!db Eb2/16! Eb2/16! Eb2/16!",
    113: "F2+C3/16!db F2/16! F2/16! F2/16!",
    114: "G2+G3/16!db G2/16! G2/16! G2/16!",
    115: "D2+A2/16!db D2/16! D2/16! D2/16!",
    116: "Eb2/8!db Eb2+Bb2/8! Eb2+Bb2/8! Eb2+Bb2/24! Eb2/16!db",
    117: "F2/48!db F2/16>db",
}

DYN = {
    "vn1": [(108, 0, "ff"), (112, 0, "ff")],
    "vn2": [(108, 0, "ff"), (112, 0, "ff")],
    "va": [(108, 12, "ff"), (112, 8, "ff")],
    "vc": [(108, 0, "ff"), (112, 0, "ff")],
}

HAIR = {
    # the last arpeggio of 111 grows into the big chords of 112 (all four
    # hairpins end together at the barline; the ff at 112 is the arrival)
    "vn1": [(111, 40, 111, 63, "cresc")],
    "vn2": [(111, 40, 111, 63, "cresc")],
    "va": [(111, 40, 111, 63, "cresc")],
    "vc": [(111, 40, 111, 63, "cresc")],
}

TEXT = {
    "vn1": [(108, 0, "appassionato")],
    "vn2": [(108, 0, "détaché")],
    "va": [(108, 12, "marcato")],
    "vc": [(108, 0, "sostenuto")],
}

CLEFS = {}
OTTAVA = []
ALLOW = set()
