"""诀别书 · 弦乐五重奏 — W5 draft: E · Reprise · 再现 (bars 41-48, the biggest
climax) and F · Coda · 尾声 (bars 49-52)

What is written here (PLAN.md §3 "E" and "F", §4, §5, §6, and the NO-PIZZ
override at the top of the plan):

* Pitches, voicing, harmony and attack rhythms are the skeleton's
  (plan/00_skeleton.py), with one optional note the plan offers (45, below).
  Seams kept: 40->41 (every part attacks together at ff after W4's G.P.:
  Vln I A5 8th, Vln II A4 8th, Vla bariolage D4-F4 D4 first, Vc Bb2 8th
  accented, Cb Bb1 dq accented), 44->45 (F5 h / F4 h / bariolage ending
  D4 -> C6 / C5 / C4 fff; walk ... A2 / A1 -> G2 8th / G1) and 48->49
  (Vln I D5 w -> D6 q pp; Vln II A4 w / Vla F4 w -> rest h, then F5+A5 /
  Bb4+D5; Vc C3 h ten. -> Bb2 h; Cb C2 h -> Bb1 h).
* 41-44, the landing.  ff tutti on the downbeat.  Violins in octaves (Vln II
  copies Vln I's accents and slurs exactly): the chart's 8-16-16 gallop on
  separate bows, the 8ths on the beat accented, the 16ths plain (lighter);
  the chromatic neighbour F#5 -> G5 (42) and E5 -> F5 (44) slurred into the
  held half note.  Vla: two-string bariolage in plain separate 16ths
  (PLAN §4.2: the cleanest drive in ACE; it also continues W4's 37-40
  articulation across the G.P.), accented with the Cb's 3+3+2 (0, 6, 12)
  in 41-43 and on every beat in 44 (the launch).  Vc: the chart's LH
  strokes, accents on the downbeat and on the syncopated chords; the 42
  fill Bb3 G4 E4 C4 accent + staccato (the chart's staccato fill, played
  marcato as the plan asks) inside the held G5.  Cb: 3+3+2 accented.  44:
  launch walk #3 (★) D-C-Bb-A accented in Vc / Cb octaves, one
  crescendo (hairpins) in all five parts into fff.
* 45-46, the crest.  fff, allargando.  The melody in three octaves (Vln I,
  Vln II 8vb, Vla 15mb), "largamente", separate bows: the downbeat C (the
  sus4 cry) and the syncopated C accented, the rest tenuto.  Vc: the
  chart's sweep, G2 on its own accented bow, D3-G3-Bb3-F4 slurred up to
  the apex, Bb3 tenuto, E2 accented (G -> E -> A in the bass).  Cb G1 held
  to 4&, E1 (open string) on 4&.  46: the A7(b9) hammer, marcato on every
  dq attack in all five parts; beat 4 thins: Vln II / Vla rest, Vln I
  holds E5 (tenuto), Vc / Cb catch a breath and take the pickup A mf.
* 47-48, the release.  Largamente: Vln I f, the others mf (melody one
  level above), everyone > .  Vln I's repeated E5 on beat 4 is slurred
  into the D5 of 48 (the 9-8 sigh); Vc: D3-A3-E4 in one slur; Vla div.
  F3+C4, unis. F4.  48: Dm7 -> Dm7/C with the third kept; Vc / Cb tenuto
  halves (the chart's ten. C3); the violins' and viola's > runs over
  47-48 to the pp of the coda.
* 49-52, the coda.  Vln I plays the motto an octave above the intro (the
  chart's 8va; build.py's OTTAVA prints the 8va line), pp, "lontano"
  ("dolce" is in the global tempo text "Meno mosso, dolce"), one slur per
  bar; the line swells from beat 3 of 49 to the D7 (50: p, no accent)
  and falls back to pp at 51; the last G6 is slurred into the C7 under the
  fermata.  Vln II div. F5+A5 -> E5+G5, Vla Bb4+D5
  -> Bb4 D5 Bb4 (Bb4 on beat 4 of 50: no fifths into 51) -> div. Bb4+C5;
  both pp in 49-50 with a > into ppp at 51, so the pp melody sits one
  level above.  Vc / Cb Bb h pp (49), tacet (50), Bb ppp from 51 under the
  chart's C/Bb (★ pedal, PLAN §6.8).  Everything ends ppp: Vln I's last >
  runs from its G6 (51 beat 4) through the arrival of C7 to ppp on beat 4
  of 52, so the C7 fades after the chord below it (the "releases last").

Dynamics (DYN / HAIR below):
  41  ff tutti; Vla > to f at 42 (the drive settles under the melody)
  42  violins < from the F#5 through the held G5, ff again at 43
  44  < in all five parts (cresc. molto) -> 45 fff
  46  fff hammer; Vc / Cb pickup on 4& mf (beat 4 thins)
  47  Vln I f, Vln II / Vla / Vc / Cb mf, all >; Vc / Cb p at 48 > pp at 49;
      Vln I / Vln II / Vla one > over 47-48 into the coda's pp
  49  pp (Vln II / Vla at their entry on beat 3)
  49-50  Vln I < from 49 beat 3 to p on the D7, > pp at 51 (a < inside
      the single A6 quarter of 50 beat 1 could not be exported)
  50  Vln II (re-entry) pp and Vla > ppp at 51
  51  Vln I pp; chord, Vc, Cb ppp;  52  Vln I > ppp (beat 4), fermata

Departures from the plan (with reasons):
* 45, beat 1: Vln II plays F4+C5 (the plan's optional added F, §3 E note),
  so the fff cry has the chart's 7th (the RH's F5) under the C octaves.
  A short 8th double stop (one finger across D and A), no "div.".
* 46: Vln I's Bb5 / A5 are marcato (^), not accent (>), like every other
  part: the plan's vocabulary (§4.2) names 46 as a hammer bar, and one
  sign for the whole tutti reads cleaner.  MIDI is identical (+12).
* 47 -> 48: the common tones A4 (Vln II) and F4 (Vla) of beat 4 are tied
  into 48 (the chart re-strikes the chord), and Vln I's E5 of beat 4 is
  slurred into D5, so that at the rit. only the melody (the 9-8 sigh) and
  the bass move.  This mirrors W3's treatment of the parallel bars 31-32.
* 48: the plan's "p -> pp" is one > from 47.0 to the end of 48 (Vln I
  f -> pp at 49; Vln II / Vla mf -> pp at their 49 entry), because a
  hairpin inside one held note (the D5 w) cannot be exported to MusicXML
  (build.py drops a wedge that starts and ends on the same note).  The
  MIDI curve passes mp at 48.0 and p on beat 3.  Vc / Cb, which rest on
  beat 4 of 47, print p at 48 and > to pp.
* The 42 "swell" on the held G5 is written as one < from the F#5 (42 beat
  2&) to the barline with ff reprinted at 43 (its target), for the same
  MusicXML reason; W3 did the same at 26-27.
* "cresc. molto" (44), "dal niente" (Vc / Cb 51) and "al niente" (52)
  are not printed as words (not in the allowed list): 44 is a hairpin in
  every part, 51 enters ppp, and 52 fades Vln I to ppp (the dynamics
  vocabulary has no "niente").
* The Vc / Cb pickup A on 4& of 46 gets its own "mf" (a re-entry after the
  8th rest, and the level at which the Largamente bass begins).
* The Vla bariolage 41-44 is not slurred (see above: PLAN §4.2 plain
  16ths); the Vla's 49 Bb4+D5 half note stays a double stop (§4.6 lists
  the Vla's div. only at 47 and 51-52).
"""

VN1 = {
    41: "A5/2> D6/1 D6/1 D6/2> A5/1 A5/1 A5/2> F5/1 F5/1 F5/2> A5/2",
    42: "A5/2> G5/1 G5/1 G5/2> (F#5/2 G5/8)",
    43: "G5/2> C6/1 C6/1 C6/2> G5/1 G5/1 G5/2> E5/1 E5/1 E5/2> G5/2",
    44: "G5/2> F5/1 F5/1 F5/2> (E5/2 F5/8)",
    45: "C6/2> Bb5/2_ F5/2_ C6/4> Bb5/6_",
    46: "Bb5/6^ A5/6^ E5/4_",
    47: "E5/12_ (E5/4",
    48: "D5/16)",
    49: "(D6/4 A6/2 G6/2 A6/4 G6/4)",
    50: "(A6/4 D7/4 A6/4 G6/4)",
    51: "(A6/2 G6/2 A6/2 G6/2) (A6/4 G6/4",
    52: "C7/16!)",
}

VN2 = {
    41: "A4/2> D5/1 D5/1 D5/2> A4/1 A4/1 A4/2> F4/1 F4/1 F4/2> A4/2",
    42: "A4/2> G4/1 G4/1 G4/2> (F#4/2 G4/8)",
    43: "G4/2> C5/1 C5/1 C5/2> G4/1 G4/1 G4/2> E4/1 E4/1 E4/2> G4/2",
    44: "G4/2> F4/1 F4/1 F4/2> (E4/2 F4/8)",
    45: "F4+C5/2> Bb4/2_ F4/2_ C5/4> Bb4/6_",
    46: "C#5+E5/6^ C#5+E5/6^ r/4",
    47: "C5/12_ A4/4~",
    48: "A4/16",
    49: "r/8 F5+A5/8",
    50: "r/4 F5+A5/8 F5+A5/4",
    51: "E5+G5/16~",
    52: "E5+G5/16!",
}


def _bar(lo, hi, accents):
    """Two-string bariolage, 16 separate 16ths, lo first, accents at the
    given 16th positions."""
    return " ".join(f"{lo if i % 2 == 0 else hi}/1{'>' if i in accents else ''}"
                    for i in range(16))


_TRESILLO = (0, 6, 12)
VA = {
    41: _bar("D4", "F4", _TRESILLO),
    42: _bar("E4", "C4", _TRESILLO),
    43: _bar("E4", "A3", _TRESILLO),
    44: _bar("A3", "D4", (0, 4, 8, 12)),
    45: "C4/2> Bb3/2_ F3/2_ C4/4> Bb3/6_",
    46: "G4+Bb4/6^ G4+Bb4/6^ r/4",
    47: "F3+C4/12_ F4/4~",
    48: "F4/16",
    49: "r/8 Bb4+D5/8",
    50: "(Bb4/4 D5/8 Bb4/4)",
    51: "Bb4+C5/16~",
    52: "Bb4+C5/16!",
}

VC = {
    41: "Bb2/2> r/4 D3+A3/4> r/2 D3+A3/4>",
    42: "Bb2/2> E3+C4/4> E3+C4/2 Bb3/2>* G4/2>* E4/2>* C4/2>*",
    43: "A2/2> E3+C4/4> E3+C4/2 A2/2 E3+C4/4> A2/2",
    44: "D3/4> F3+C4/4 D3/2> C3/2> Bb2/2> A2/2>",
    45: "G2/2> (D3/2 G3/2 Bb3/2 F4/2) Bb3/4_ E2/2>",
    46: "A2+E3/6^ A2+E3/6^ r/2 A2/2_",
    47: "(D3/4 A3/4 E4/4) r/4",
    48: "D3+C4/8_ C3/8_",
    49: "Bb2/8 r/8",
    50: "r/16",
    51: "Bb2/16~",
    52: "Bb2/16!",
}

CB = {
    41: "Bb1/6> Bb1/6> Bb1/4>",
    42: "Bb1/6> Bb1/6> Bb1/4>",
    43: "A1/6> A1/6> A1/4>",
    44: "D2/8> D2/2> C2/2> Bb1/2> A1/2>",
    45: "G1/14> E1/2>",
    46: "A1/6^ A1/6^ r/2 A1/2_",
    47: "D2/12_ r/4",
    48: "D2/8_ C2/8_",
    49: "Bb1/8 r/8",
    50: "r/16",
    51: "Bb1/16~",
    52: "Bb1/16!",
}

DYN = {
    "vn1": [(41, 0, "ff"), (43, 0, "ff"), (45, 0, "fff"), (47, 0, "f"),
            (49, 0, "pp"), (50, 4, "p"), (51, 0, "pp"), (52, 12, "ppp")],
    "vn2": [(41, 0, "ff"), (43, 0, "ff"), (45, 0, "fff"), (47, 0, "mf"),
            (49, 8, "pp"), (50, 4, "pp"), (51, 0, "ppp")],
    "va": [(41, 0, "ff"), (42, 0, "f"), (45, 0, "fff"), (47, 0, "mf"),
           (49, 8, "pp"), (51, 0, "ppp")],
    "vc": [(41, 0, "ff"), (45, 0, "fff"), (46, 14, "mf"), (48, 0, "p"),
           (49, 0, "pp"), (51, 0, "ppp")],
    "cb": [(41, 0, "ff"), (45, 0, "fff"), (46, 14, "mf"), (48, 0, "p"),
           (49, 0, "pp"), (51, 0, "ppp")],
}

# (bar, 16th, bar2, 16th2, kind); every hairpin starts and ends on
# different notes (so the MusicXML keeps it) and ends right before a
# printed dynamic (its MIDI target).
HAIR = {
    "vn1": [(42, 6, 42, 15, "cresc"), (44, 0, 44, 15, "cresc"),
            (47, 0, 48, 15, "dim"), (49, 8, 50, 3, "cresc"),
            (50, 4, 50, 15, "dim"), (51, 12, 52, 11, "dim")],
    "vn2": [(42, 6, 42, 15, "cresc"), (44, 0, 44, 15, "cresc"),
            (47, 0, 48, 15, "dim"), (50, 4, 50, 15, "dim")],
    "va": [(41, 2, 41, 15, "dim"), (44, 0, 44, 15, "cresc"),
           (47, 0, 48, 15, "dim"), (50, 4, 50, 15, "dim")],
    "vc": [(44, 0, 44, 15, "cresc"), (47, 0, 47, 11, "dim"),
           (48, 0, 48, 15, "dim")],
    "cb": [(44, 0, 44, 15, "cresc"), (48, 0, 48, 15, "dim")],
}

TEXT = {
    "vn1": [(45, 0, "largamente"), (49, 0, "lontano")],
    "vn2": [(45, 0, "largamente"), (49, 8, "div.")],
    "va": [(45, 0, "largamente"), (47, 0, "div."), (47, 12, "unis."),
           (51, 0, "div.")],
    "vc": [],
    "cb": [],
}

# PLAN §6.1 for bars 41-52
MELODY = {b: [("vn1", 0)] for b in range(41, 53)}
for _b in (41, 42, 43, 44):
    MELODY[_b] = [("vn1", 0), ("vn2", -12)]
MELODY[45] = [("vn1", 0), ("vn2", -12), ("va", -24)]
MELODY_FREE = {}

# the chart's own b9 colours in bars 41-52 (copied from the skeleton)
CLASH_ALLOW = {
    (46, "vn1", "vc"): "melody Bb5 over the A bass: the chart's A7(b9)",
    (46, "vn1", "cb"): "melody Bb5 over the A bass: the chart's A7(b9)",
    (46, "va", "vc"): "Bb4 over the A bass: the chart's A7(b9) (its RH Bb4)",
    (46, "va", "cb"): "Bb4 over the A bass: the chart's A7(b9) (its RH Bb4)",
}

# PLAN §6.4 entries that cover bars 41-52
DOUBLINGS = [("vn1", "vn2", 41, 45), ("vn2", "va", 45, 45),
             ("vn1", "va", 45, 45), ("vc", "cb", 41, 52)]

# PLAN §4.7: Vla alto, Vc bass throughout (no clef changes in 41-52)
CLEFS = {}
