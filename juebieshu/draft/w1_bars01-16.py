"""诀别书 · 弦乐五重奏 — W1 draft: Intro · 前奏 (bars 1-8) and A · Theme · 主题 (9-16)

What is written here (PLAN.md §3 "Intro" and "A", §4, §5, §6):

* Pitches, voicing and harmony are the skeleton's (plan/00_skeleton.py);
  the seams 8->9 and 16->17 are kept exactly (Vln I D6 dh ten. p -> D5 mp;
  Vln II F5 -> C5 p; Vla F4 h -> F3; Vc/Cb C3/C2 -> Bb2/Bb1; 16: Vln I/II
  D6 E6 / D5 E5, Vla run ... G4 A4, Vc/Cb walk ... Bb2 A2 / Bb1 A1).
* Intro 1-4: Vln I states the motto, slurred over its first three notes,
  tenuto on the fourth, then lifted (plan note).  The pad (Vln II, Vla, Vc)
  fades in dal niente (ppp < pp) and breathes only in the motto's gaps:
  a < p > swell from the motto's release (2&) through beats 3-4 of bars
  2 and 3 carries the Vla's slurred sus4->3 sighs (F4-E4, D4-E4); common
  tones are tied over the barline (Vla F4 1->2, Vc Bb3 1->2, Vln II G4
  2->3) so the pad never re-attacks under the melody.  Bar 4 poco < into the pulse.
* Intro 5-7: the chart's off-beat pulse in Vln II + Vla, p leggiero
  (quarter on the "and", staccato 8th); Vc Bb2/A2 tenuto quarters on 1 and
  3 with the chart's A2 pickup on 4& of bar 7.  Bar 7 < for everyone.
* Bar 8: violins in the chart's sixths, one slur F6-E6-D6 / A5-G5-F5;
  their bar-7 < runs on through the two 8ths to mf on the D6 / F5 (beat
  2), then > to p by beat 4, D6/F5 tenuto to the barline; Vla sigh
  G4-F4 slurred; Vc tenuto quarters; Cb enters pp < mp > p.
* A 9-12: Vln I theme mp espr.; bowing: the motto gesture (the first beam
  group, 8-16-16-8-8) in one slur, 8ths in pairs on beats 3-4, 16th turns
  slurred in fours, the half notes C5 / F5 tenuto at full value; one
  phrase arc (< to mf at the C6s of 11, > to p on the F5 of 12, so the
  Vln II answer is heard; 13 then steps up to mf).  Vln II
  colour pad (C5 = the 9th, E5 -> G4, A4 -> E5), then in 12 the motto
  answer F4 C5 Bb4 C5 under the held F5, p dolce, articulated like the
  intro motto.  Vla broken 8ths in 4-note slurs; the chart's staccato fill
  Bb3 G4 E4 C4 (10) under the held C5.  Vc / Cb whole-note roots (a new
  bow each bar), tenuto cadence quarters in 12; < into 13.
* A 13-16: violins in octaves (Vln II copies Vln I's slurs), mf; Vla broken
  8ths one register lower (mp); Vc/Cb 3+3+2 tenuto (the ★ re-rhythm of
  PLAN §6.8), mp.  One long < from 15 beat 1 to the barline of 16 in all
  five parts; its MIDI target is W2's f at 17.0.  Bar 16: Vla run slurred
  in two groups of four; Vc/Cb launch walk marcato; violins' last two 8ths
  (D6 E6) on separate bows into the f downbeat.

Departures from the plan / skeleton:
* Vln II plays the pad A4 / G4 / G4 / A4 in bars 1-4 as the plan's bar
  table (§3), layer ladder (bar 1 "pad (Vln II, Vla, Vc)"), §4.1 and §6.8
  specify; the skeleton had rests there.  Checked: no clash, no parallel.
* Theme bowing: the plan's "8ths in pairs, 16th turns in fours" is kept,
  except that the 8th after the motto turn (G5 on 2& of 9/13, F5 of
  11/15) joins the turn's slur, so each first beam group is one bow
  instead of leaving a lone détaché 8th.
* "poco cresc." (7), "cresc. poco a poco" (15) and "cresc. molto" (16) are
  written as hairpins only, not words (the words are not in the allowed
  expression list, and the hairpins drive the MIDI curve).  "n<" at bar 1
  is spelled ppp < pp so the fade-in has a printed MIDI target.
* Hairpin peaks are printed (mf in 8, p in the pad swells of 2-3, mf/p
  in the 11-12 arc) because every hairpin needs a printed target.  In 8
  the violins print no mp on the downbeat: their bar-7 < runs through it
  (the MIDI passes mp there) to the mf on the D6 / F5; Vla/Vc print mp.
  The Cb's "pp < mp" entry is completed with > p into 9 (the section's
  accompaniment level).
"""

VN1 = {
    1: "(D5/2 A5/1 G5/1) A5/2_ r/2 r/8",
    2: "(C5/2 G5/1 F5/1) G5/2_ r/2 r/8",
    3: "(C5/2 G5/1 F5/1) G5/2_ r/2 r/8",
    4: "(C6/2 F5/1 E5/1) F5/2_ r/2 r/8",
    5: "(D5/2 A5/1 G5/1) A5/2_ r/2 r/8",
    6: "(D6/2 G5/1 F5/1) G5/2_ r/2 r/8",
    7: "(E6/2 G5/1 F5/1) G5/2_ r/2 r/8",
    8: "(F6/2 E6/2 D6/12_)",
    9: "(D5/2 A5/1 G5/1 A5/2 G5/2) (A5/2 D6/2) (A5/2 G5/2)",
    10: "(A5/1 G5/1 A5/1 G5/1) (A5/2 G5/2) C5/8_",
    11: "(C5/2 G5/1 F5/1 G5/2 F5/2) (G5/2 C6/2) (C6/2 G5/2)",
    12: "(G5/1 A5/1 G5/1 A5/1) (G5/2 E5/2) F5/8_",
    13: "(D5/2 A5/1 G5/1 A5/2 G5/2) (A5/2 D6/2) (A5/2 G5/2)",
    14: "(A5/1 G5/1 A5/1 G5/1) (A5/2 G5/2) C5/8_",
    15: "(C5/2 G5/1 F5/1 G5/2 F5/2) (G5/2 C6/2) (C6/2 E6/2)",
    16: "(D6/1 E6/1 D6/1 E6/1) (D6/2 C6/2) (D6/2 A5/2) D6/2 E6/2",
}

VN2 = {
    1: "A4/16",
    2: "G4/16~",
    3: "G4/16",
    4: "A4/16",
    5: "r/2 A4/4 A4/2* r/2 A4/4 A4/2*",
    6: "r/2 G4/4 G4/2* r/2 G4/4 G4/2*",
    7: "r/2 G4/4 G4/2* r/2 G4/4 r/2",
    8: "(A5/2 G5/2 F5/12_)",
    9: "C5/16",
    10: "E5/8 G4/8",
    11: "A4/8 E5/8",
    12: "D5/8 (F4/2 C5/1 Bb4/1) C5/2_ r/2",
    13: "(D4/2 A4/1 G4/1 A4/2 G4/2) (A4/2 D5/2) (A4/2 G4/2)",
    14: "(A4/1 G4/1 A4/1 G4/1) (A4/2 G4/2) C4/8_",
    15: "(C4/2 G4/1 F4/1 G4/2 F4/2) (G4/2 C5/2) (C5/2 E5/2)",
    16: "(D5/1 E5/1 D5/1 E5/1) (D5/2 C5/2) (D5/2 A4/2) D5/2 E5/2",
}

VA = {
    1: "(F4/16~",
    2: "F4/8 E4/8)",
    3: "(D4/8 E4/8)",
    4: "F4/16",
    5: "r/2 F4/4 F4/2* r/2 F4/4 F4/2*",
    6: "r/2 F4/4 F4/2* r/2 E4/4 E4/2*",
    7: "r/2 D4/4 D4/2* r/2 E4/4 r/2",
    8: "(G4/8 F4/8)",
    9: "(F3/2 Bb3/2 D4/2 A4/2) (F3/2 Bb3/2 D4/2 A4/2)",
    10: "(G3/2 C4/2 E4/2 G4/2) Bb3/2* G4/2* E4/2* C4/2*",
    11: "(A3/2 C4/2 G4/2 C4/2) (A3/2 E4/2 G4/2 C4/2)",
    12: "(D4/2 F4/2 A4/2 F4/2) (D4/4 F4/4)",
    13: "(F3/2 Bb3/2 D4/2 Bb3/2) (D3/2 F3/2 A3/2 D4/2)",
    14: "(C3/2 E3/2 G3/2 C4/2) Bb3/2* G4/2* E4/2* C4/2*",
    15: "(A3/2 C4/2 G3/2 C4/2) (A3/2 E3/2 G3/2 C4/2)",
    16: "(D3/2 F3/2 A3/2 F3/2) (A3/1 Bb3/1 C4/1 D4/1) (E4/1 F4/1 G4/1 A4/1)",
}

VC = {
    1: "Bb3/16~",
    2: "Bb3/16",
    3: "A3/16",
    4: "(D3/12 C3/4)",
    5: "Bb2/4_ r/4 Bb2/4_ r/4",
    6: "Bb2/4_ r/4 Bb2/4_ r/4",
    7: "A2/4_ r/4 A2/4_ r/2 A2/2",
    8: "D3/4_ D3+A3/4_ D3/4_ C3/4_",
    9: "Bb2/16",
    10: "Bb2/16",
    11: "A2/16",
    12: "D3/4_ D3+A3/4_ D3/4_ C3/4_",
    13: "Bb2/6_ Bb2/6_ Bb2/4_",
    14: "Bb2/6_ Bb2/6_ Bb2/4_",
    15: "A2/6_ A2/6_ A2/4_",
    16: "D3/4_ D3+A3/4_ D3/2^ C3/2^ Bb2/2^ A2/2^",
}

CB = {
    1: "r/16", 2: "r/16", 3: "r/16", 4: "r/16",
    5: "r/16", 6: "r/16", 7: "r/16",
    8: "D2/4_ r/4 D2/4_ C2/4_",
    9: "Bb1/16",
    10: "Bb1/16",
    11: "A1/16",
    12: "D2/4_ r/4 D2/4_ C2/4_",
    13: "Bb1/6_ Bb1/6_ Bb1/4_",
    14: "Bb1/6_ Bb1/6_ Bb1/4_",
    15: "A1/6_ A1/6_ A1/4_",
    16: "D2/4_ r/4 D2/2^ C2/2^ Bb1/2^ A1/2^",
}

# The pad's dynamics in 1-4 (Vln II, Vla, Vc): dal niente, then a swell in
# the motto's gap on beats 3-4 of bars 2 and 3.
_PAD_DYN = [(1, 0, "ppp"), (1, 8, "pp"), (2, 12, "p"), (3, 0, "pp"),
            (3, 12, "p"), (4, 0, "pp")]
_PAD_HAIR = [(1, 0, 1, 7, "cresc"), (2, 6, 2, 11, "cresc"),
             (2, 12, 2, 15, "dim"), (3, 6, 3, 11, "cresc"),
             (3, 12, 3, 15, "dim")]

DYN = {
    "vn1": [(1, 0, "p"), (8, 4, "mf"), (8, 12, "p"),
            (9, 0, "mp"), (11, 12, "mf"), (12, 8, "p"), (13, 0, "mf")],
    "vn2": _PAD_DYN + [(5, 2, "p"), (8, 4, "mf"), (8, 12, "p"),
                       (13, 0, "mf")],
    "va": _PAD_DYN + [(5, 2, "p"), (8, 0, "mp"), (9, 0, "p"),
                      (13, 0, "mp")],
    "vc": _PAD_DYN + [(5, 0, "p"), (8, 0, "mp"), (9, 0, "p"),
                      (13, 0, "mp")],
    "cb": [(8, 0, "pp"), (8, 8, "mp"), (9, 0, "p"), (13, 0, "mp")],
}

# (bar, 16th, bar2, 16th2, kind); every hairpin ends right before a printed
# dynamic.  The 15-16 crescendo targets W2's f at 17.0.
HAIR = {
    "vn1": [(7, 0, 8, 3, "cresc"), (8, 4, 8, 11, "dim"),
            (11, 0, 11, 11, "cresc"),
            (11, 12, 12, 7, "dim"), (15, 0, 16, 15, "cresc")],
    "vn2": _PAD_HAIR + [(4, 8, 5, 1, "cresc"), (7, 0, 8, 3, "cresc"),
                        (8, 4, 8, 11, "dim"),
                        (15, 0, 16, 15, "cresc")],
    "va": _PAD_HAIR + [(4, 8, 5, 1, "cresc"), (7, 0, 7, 15, "cresc"),
                       (8, 8, 8, 15, "dim"), (12, 8, 12, 15, "cresc"),
                       (15, 0, 16, 15, "cresc")],
    "vc": _PAD_HAIR + [(4, 8, 4, 15, "cresc"), (7, 0, 7, 15, "cresc"),
                       (8, 8, 8, 15, "dim"), (12, 8, 12, 15, "cresc"),
                       (15, 0, 16, 15, "cresc")],
    "cb": [(8, 0, 8, 7, "cresc"), (8, 8, 8, 15, "dim"),
           (12, 8, 12, 15, "cresc"), (15, 0, 16, 15, "cresc")],
}

TEXT = {
    "vn1": [(1, 0, "espr."), (9, 0, "espr.")],
    "vn2": [(5, 2, "leggiero"), (12, 8, "dolce")],
    "va": [(5, 2, "leggiero")],
    "vc": [],
    "cb": [],
}

# PLAN §6.1 for bars 1-16
MELODY = {b: [("vn1", 0)] for b in range(1, 17)}
for _b in (13, 14, 15, 16):
    MELODY[_b] = [("vn1", 0), ("vn2", -12)]
MELODY_FREE = {}
# PLAN §6.3: none of the 13 chart b9 colours falls in bars 1-16
CLASH_ALLOW = {}
# PLAN §6.4, clipped to bars 1-16
DOUBLINGS = [("vn1", "vn2", 13, 16), ("vc", "cb", 8, 16)]
# PLAN §4.7: Vla alto, Vc bass throughout; no clef changes in 1-16
CLEFS = {}
