"""S08 · bars 66–73 · Solo 华彩 (the runs), f.

Piano: two identical 2-bar waves (66–67 = 70–71, 68–69 = 72–73).  Even
bars: the RH holds a whole-note chord (Eb: G A Bb D G / Gm: D G Bb D)
while its second voice runs up from D3 to A6 in 16th quintuplets (beats
1–2) and sextuplets (beats 3–4).  Odd bars: the RH falls back down in four
accented 16th quintuplets (Bb6/C7 ... A3/C4).  LH: a low whole-note octave
plus the 3+3+2 bass rhythm with a mid-register chord stab on beat 3.

Quartet:
- The upward run is a RELAY, bottom to top, each hand-off on a beat with
  the hand-off note played by both players (one-note overlap):
  Va beats 1–2 (D3 G3 A3 | Bb3 ... Bb4) -> D5 on beat 3, which it then
  holds (the pedal's maj7 / fifth); Vn II beat 3 (D5 D4 G4 A4 Bb4 D5, 3rd
  position around the open D) -> G5 on beat 4, held; Vn I beat 4 (G5 ...
  A6) and the descending quintuplets of the next bar at pitch (C7/D7 as in
  the piano's 8va, accents on the group heads).  The last, low descending
  group goes back down to the Va (overlap on the beat-4 downbeat: both
  play F4 / Bb4), so the viola closes the wave where it starts the next one
  (A3 -> D3) and Vn I has time to prepare the next high chord.
- The RH's held chord = Vn I + Vn II double stops on beat 1, held until
  they enter the relay (Vn II a half note, Vn I a dotted half), dim. so
  the run comes through (the piano chord decays).  66/70: Vn I Bb5+G6,
  Vn II A5+D6 (keeps the A–Bb crunch of the piano's cluster); 68/72:
  Vn I Bb5+D6, Vn II D5+G5.  Vn II rests in the odd bars (breath).
- Vc = the LH: the low octave as an accented boom on beat 1 (open-string
  fifth / octave where it lies well: Eb2+Bb2, F2+C3, G2+G3, D2), then the
  3+3+2 rhythm, and the beat-3 stab as a double stop of the piano's two
  lowest stab notes (Bb2+Eb3, F3+A3, D3+G3, F3+A3), so the root sounds on
  beat 3 (Eb2 / G2 are stopped or gone by then).  In the odd bars the Va
  joins the stab (C4, tenuto like the cello) before its descending group.
- Dynamics: f, restated at every wave and every relay entry so each hairpin
  has an anchor (held chord f >, run entry f <; Vn II's hand-off G5 recedes
  under Vn I; Va f at the odd-bar stab, mf for the last falling group, which
  continues Vn I's diminuendo).  The even-bar chords are down-bow (the
  dotted-8th rest at the end of each odd bar gives time to retake), so the
  sextuplet rises up-bow and the accented apex falls on a down-bow.
"""

_BOOM = "{b}/12> {n}/12- {n}/8 {s}/12- {n}/12- {n}/8"

_UP_VN1 = "{c}/48db {{6:4 (G5/4 A5/4 Bb5/4 D6/4 G6/4 A6/4) }}"
_UP_VN2 = "{c}/32db {{6:4 (D5/4 D4/4 G4/4 A4/4 Bb4/4 D5/4 }} G5/16)"
_UP_VA = ("{5:4 r/8 (D3/4 G3/4 A3/4) } "
          "{5:4 (Bb3/4 D4/4 G4/4 A4/4 Bb4/4 } D5/32)")

_DOWN_F = ("{5:4 (Bb6/4> C7/4 Bb6/4 F6/4 C6/4) } "
           "{5:4 (Bb5/4> C6/4 Bb5/4 F5/4 C5/4) } "
           "{5:4 (A5/4> F5/4 C5/4 Bb4/4 A4/4 } F4/4) r/4 r/8")
_DOWN_D = ("{5:4 (C7/4> D7/4 C7/4 Bb6/4 F6/4) } "
           "{5:4 (C6/4> D6/4 C6/4 Bb5/4 F5/4) } "
           "{5:4 (C6/4> Bb5/4 A5/4 F5/4 C5/4 } Bb4/4) r/4 r/8")
_VA_F = "r/32 C4/12- r/4 {5:4 (F4/4 C4/4 Bb3/4 A3/4) r/4 }"
_VA_D = "r/32 C4/12- r/4 {5:4 (Bb4/4 A4/4 F4/4 C4/4) r/4 }"

VN1, VN2, VA, VC = {}, {}, {}, {}
for _b in (66, 70):
    VN1[_b] = _UP_VN1.format(c="Bb5+G6")
    VN2[_b] = _UP_VN2.format(c="A5+D6")
    VA[_b] = _UP_VA
    VC[_b] = _BOOM.format(b="Eb2+Bb2", n="Eb2", s="Bb2+Eb3")
for _b in (67, 71):
    VN1[_b] = _DOWN_F
    VA[_b] = _VA_F
    VC[_b] = _BOOM.format(b="F2+C3", n="F2", s="F3+A3")
for _b in (68, 72):
    VN1[_b] = _UP_VN1.format(c="Bb5+D6")
    VN2[_b] = _UP_VN2.format(c="D5+G5")
    VA[_b] = _UP_VA
    VC[_b] = _BOOM.format(b="G2+G3", n="G2", s="D3+G3")
for _b in (69, 73):
    VN1[_b] = _DOWN_D
    VA[_b] = _VA_D
    VC[_b] = _BOOM.format(b="D2", n="D2", s="F3+A3")

DYN = {"vn1": [], "vn2": [], "va": [], "vc": [(66, 0, "f")]}
for _b in (66, 68, 70, 72):
    # restate the level at every wave and every relay entry, so no entry
    # comes out of the previous hairpin (the run must not dip at hand-offs)
    DYN["vn1"] += [(_b, 0, "f"), (_b, 48, "f")]      # chord, run entry
    DYN["vn2"] += [(_b, 0, "f"), (_b, 32, "f")]      # chord, run entry
    DYN["va"] += [(_b, 0, "f"),                      # run
                  (_b + 1, 32, "f"),                 # stab with the Vc
                  (_b + 1, 48, "mf")]                # takes over Vn I's dim.

HAIR = {"vn1": [], "vn2": [], "va": [], "vc": []}
for _b in (66, 68, 70, 72):
    # held chord decays, the run swells to the top; Va swells up its
    # part of the run, then lets the held D5 recede under the violins
    HAIR["vn1"] += [(_b, 0, _b, 44, "dim"), (_b, 48, _b, 63, "cresc")]
    # (Vn II's held hand-off G5 recedes so Vn I's entry on G5 comes through)
    HAIR["vn2"] += [(_b, 0, _b, 28, "dim"), (_b, 32, _b, 48, "cresc"),
                    (_b, 48, _b, 60, "dim")]
    HAIR["va"] += [(_b, 6, _b, 30, "cresc"), (_b, 32, _b, 60, "dim")]
for _b in (67, 69, 71, 73):
    # the falling quintuplets relax, Va lands softly at the bottom
    HAIR["vn1"] += [(_b, 0, _b, 48, "dim")]
    HAIR["va"] += [(_b, 48, _b, 60, "dim")]

TEXT = {
    "vn1": [(66, 48, "brillante")],
    "vn2": [],
    "va": [],
    "vc": [(66, 0, "marcato")],
}

CLEFS = {}

# Vn I's climb and first falling quintuplet (up to D7) read under a short
# 8va: from the beat-4 sextuplet to the end of the next bar's beat 1
OTTAVA = [("vn1", 66, 48, 67, 16), ("vn1", 68, 48, 69, 16),
          ("vn1", 70, 48, 71, 16), ("vn1", 72, 48, 73, 16)]

ALLOW = set()
