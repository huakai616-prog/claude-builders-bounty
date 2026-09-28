"""诀别书 · 弦乐五重奏 — W4 draft: D · Interlude · 间奏 (bars 33-40), with the
one-beat G.P. on bar 40, beat 4

What is written here (PLAN.md §3 "D", §4.2-4.6, §5, §6 and the NO-PIZZ
override at the top of the plan):

* Pitches, voicing, harmony and attack rhythms are exactly the skeleton's
  (plan/00_skeleton.py).  Seams kept: 32->33 (Vln II E5 8th, Vla F3+A3 dq,
  Vc Bb2 short 8th, Cb Bb1 short, Vln I resting in 33-34) and 40->41 (every
  part silent from 40.12; Vln I D6 / Vln II A5 / Vla bariolage ending D5 at
  pos 11 / Vc and Cb D on beat 3, marcato).
* 33-35, the heartbeat.  Vln II carries the chart's ostinato as the tune,
  mp leggiero: separate spiccato 8ths (staccato dots, so ACE hears short
  strokes) with accents on the 3+3+2 notes (1, 2&, 4); the rising top
  E5 -> F5 -> G5 is carried by those accents.  Vla: low div. dyads in
  tenuto 3+3+2 (dq, dq, q), p.  Vc: short arco 8ths on 1, 2&, 4, p.  Cb:
  the same strokes arco secco (the override: no pizz., text "secco" only).
* 35-36, the sky pedal.  Vln I enters on A5 pp and holds it (one tied note)
  through 36 beat 3 while everybody grows; the pickup A5 Bb5 C6 D6 is one
  slurred up-bow into the new down-bow E6 of 37.  Vln II F5 and the Vla's
  A4+C5 (still div.) are tenuto dotted halves and stop on beat 4, so the
  pickup's Bb5 rubs against nothing.  Vc: the chart's cadence quarters,
  tenuto; Cb: the same, secco (short quarters).
* 37-39, the rebuild.  Violins in octaves (Vln I = the chart's 8va, Vln II
  at the chart's pitch), détaché 8ths, never slurred, accents on the 3+3+2
  notes, Vln II copying Vln I exactly.  Vla unis.: two-string bariolage
  16ths on separate bows (PLAN §4.2 "plain 16ths": the cleanest drive in
  ACE), accents on the same 3+3+2 positions; its upper notes climb
  D4 -> F4 -> A4 -> D5 (37 -> 40).  Vc / Cb arco "marcato" 3+3+2 with
  accents; in 39 the Vc switches to the 8th chug (accents 1, 2&, 4).
* 40, the hammer and the G.P.  ff tutti, one < through beats 1-3 in all
  five parts (ends at 40.11; its MIDI target is W5's ff at 41.0).  Violins
  hold D6 / A5 (accented), the Vla bariolage is accented on the downbeat
  only (accents on beats 2-3 collided with the D5 ledger notes in the
  engraving; the hammer beats are the Vc / Cb's), Vc and Cb hammer D-D-D
  with marcato.  Every note ends at 40.12; nothing
  is tied or slurred into beat 4; "G.P." is printed over the quarter rest
  in all five parts.  The chart's passing C bass on beat 4 is dropped
  (PLAN ★).

Dynamics (melody one level above the accompaniment):
  33  Vln II mp (leggiero); Vla, Vc, Cb p
  35  Vln I pp; one hairpin per part over 35-36 (Vln I pp -> mf, Vln II
      mp -> mf, Vla / Vc / Cb p -> mp), ending on the printed 37 marks
  37  violins mf; Vla, Vc, Cb mp        38  violins f; Vla, Vc, Cb mf
  39  cresc. molto (hairpins) into      40  ff tutti, < to 40.11, G.P.

Departures from the plan (with reasons):
* Vln II's optional open-A4 double stop under the accented ostinato notes
  (33) is not used: a single clean line keeps the leggiero light and keeps
  ACE's smart mode from switching between single notes and chords inside
  one phrase.
* 36 is not printed "mp < mf" as two marks: each part has one continuous
  hairpin over 35-36 ending on the 37 mark, which passes mp at 36.0 in the
  MIDI curve.  Printing mp at 36.0 would have put a waypoint on the middle
  of Vln I's tied A5, and for Vln II (already mp) it would have been a
  hairpin pointing at its own level.  The accompaniment reaches mp at 37,
  one level under the violins' mf, as the balance rule asks; the plan's
  single-level column (37 mf, 38 f) is read as the violins' level.
* "poco cresc." (35) and "cresc. molto" (39) are written as hairpins only
  (the words are not in the allowed expression list, and the hairpins drive
  the MIDI curve).  "from niente" (35) is written as pp < ("niente" is not
  an allowed mark).
* The Vla bariolage is not slurred: PLAN §4.2 specifies plain 16ths for the
  16th drive (separate notes are the cleanest option in ACE), and separate
  bows let the 3+3+2 accents sit where the violins' accents are.
* Engraving note for the integrator (build.py FORM, not a draft key): PLAN
  §4.7 allows an 8va line for Vln I in 37-40; build.py's OTTAVA does not
  list it yet.  Suggested entry: OTTAVA["vn1"] += [(37, 0, 40, 11)].
"""

VN1 = {
    33: "r/16",
    34: "r/16",
    35: "A5/16~",
    36: "A5/12 (A5/1 Bb5/1 C6/1 D6/1)",
    37: "E6/2> D6/2 A5/2 E6/2> D6/2 A5/2 D6/2> E6/2",
    38: "F6/2> E6/2 A5/2 F6/2> E6/2 A5/2 E6/2> F6/2",
    39: "G6/2> F6/2 A5/2 G6/2> F6/2 A5/2 F6/2> E6/2",
    40: "D6/12> r/4",
}

VN2 = {
    33: "E5/2>* D5/2* A4/2* E5/2>* D5/2* A4/2* D5/2>* E5/2*",
    34: "F5/2>* E5/2* A4/2* F5/2>* E5/2* A4/2* E5/2>* F5/2*",
    35: "G5/2>* F5/2* A4/2* G5/2>* F5/2* A4/2* F5/2>* G5/2*",
    36: "F5/12_ r/4",
    37: "E5/2> D5/2 A4/2 E5/2> D5/2 A4/2 D5/2> E5/2",
    38: "F5/2> E5/2 A4/2 F5/2> E5/2 A4/2 E5/2> F5/2",
    39: "G5/2> F5/2 A4/2 G5/2> F5/2 A4/2 F5/2> E5/2",
    40: "A5/12> r/4",
}

VA = {
    33: "F3+A3/6_ F3+A3/6_ F3+A3/4_",
    34: "A3+C4/6_ A3+C4/6_ A3+C4/4_",
    35: "A3+C4/6_ A3+C4/6_ A3+C4/4_",
    36: "A4+C5/12_ r/4",
    37: ("Bb3/1> D4/1 Bb3/1 D4/1 Bb3/1 D4/1 Bb3/1> D4/1 "
         "Bb3/1 D4/1 Bb3/1 D4/1 Bb3/1> D4/1 Bb3/1 D4/1"),
    38: ("A3/1> F4/1 A3/1 F4/1 A3/1 F4/1 A3/1> F4/1 "
         "A3/1 F4/1 A3/1 F4/1 A3/1> F4/1 A3/1 F4/1"),
    39: ("D4/1> A4/1 D4/1 A4/1 D4/1 A4/1 D4/1> A4/1 "
         "D4/1 A4/1 D4/1 A4/1 D4/1> A4/1 D4/1 A4/1"),
    40: ("A4/1> D5/1 A4/1 D5/1 A4/1 D5/1 A4/1 D5/1 "
         "A4/1 D5/1 A4/1 D5/1 r/4"),
}

VC = {
    33: "Bb2/2* r/4 Bb2/2* r/4 Bb2/2* r/2",
    34: "C3/2* r/4 C3/2* r/4 C3/2* r/2",
    35: "D3/2* r/4 D3/2* r/4 D3/2* r/2",
    36: "D3/4_ D3+A3/4_ D3/4_ C3/4_",
    37: "Bb2/6> Bb2/6> Bb2/4>",
    38: "C3/6> C3/6> C3/4>",
    39: "D3/2> D3/2 D3/2 D3/2> D3/2 D3/2 D3/2> D3/2",
    40: "D3/4^ D3+A3/4^ D3/4^ r/4",
}

CB = {
    33: "Bb1/2* r/4 Bb1/2* r/4 Bb1/2* r/2",
    34: "C2/2* r/4 C2/2* r/4 C2/2* r/2",
    35: "D2/2* r/4 D2/2* r/4 D2/2* r/2",
    36: "D2/4* r/4 D2/4* C2/4*",
    37: "Bb1/6> Bb1/6> Bb1/4>",
    38: "C2/6> C2/6> C2/4>",
    39: "D2/6> D2/6> D2/4>",
    40: "D2/4^ D2/4^ D2/4^ r/4",
}

DYN = {
    "vn1": [(35, 0, "pp"), (37, 0, "mf"), (38, 0, "f"), (40, 0, "ff")],
    "vn2": [(33, 0, "mp"), (37, 0, "mf"), (38, 0, "f"), (40, 0, "ff")],
    "va": [(33, 0, "p"), (37, 0, "mp"), (38, 0, "mf"), (40, 0, "ff")],
    "vc": [(33, 0, "p"), (37, 0, "mp"), (38, 0, "mf"), (40, 0, "ff")],
    "cb": [(33, 0, "p"), (37, 0, "mp"), (38, 0, "mf"), (40, 0, "ff")],
}

HAIR = {
    "vn1": [(35, 0, 36, 15, "cresc"), (39, 0, 39, 15, "cresc"),
            (40, 0, 40, 11, "cresc")],
    "vn2": [(35, 0, 36, 11, "cresc"), (39, 0, 39, 15, "cresc"),
            (40, 0, 40, 11, "cresc")],
    "va": [(35, 0, 36, 11, "cresc"), (39, 0, 39, 15, "cresc"),
           (40, 0, 40, 11, "cresc")],
    "vc": [(35, 0, 36, 15, "cresc"), (39, 0, 39, 15, "cresc"),
           (40, 0, 40, 11, "cresc")],
    "cb": [(35, 0, 36, 15, "cresc"), (39, 0, 39, 15, "cresc"),
           (40, 0, 40, 11, "cresc")],
}

TEXT = {
    "vn1": [(40, 12, "G.P.")],
    "vn2": [(33, 0, "leggiero"), (40, 12, "G.P.")],
    "va": [(33, 0, "div."), (37, 0, "unis."), (40, 12, "G.P.")],
    "vc": [(37, 0, "marcato"), (40, 12, "G.P.")],
    "cb": [(33, 0, "secco"), (37, 0, "marcato"), (40, 12, "G.P.")],
}

# PLAN §6.1 for bars 33-40
MELODY = {b: [("vn1", 0)] for b in range(33, 41)}
for _b in (33, 34, 35):
    MELODY[_b] = [("vn2", 0)]
for _b in (37, 38, 39):
    MELODY[_b] = [("vn1", 0), ("vn2", -12)]
MELODY_FREE = {36: "A5 held over from b.35 in Vln I (sky pedal)"}

# the skeleton has no b9 exceptions in bars 33-40
CLASH_ALLOW = {}

# PLAN §6.4 entries that cover bars 33-40
DOUBLINGS = [("vn1", "vn2", 37, 39), ("vc", "cb", 8, 52)]

CLEFS = {}
