"""诀别书 · 弦乐五重奏 — W2 draft: B · Chorus I · 副歌 · 一 (bars 17-24)

What is written here (PLAN.md §3 "B", §4, §5, §6):

* Pitches, voicing and rhythm are exactly the skeleton's (plan/00_skeleton.py);
  the seams 16->17 and 24->25 are untouched (Vln I F6 / A5, Vln II F5+Bb5 /
  F#5, Vla Bb3+F4 / C4+A4, Vc G2 / walk ... A2, Cb G1 / walk ... A1).
* Violin choir (Vln I melody, Vln II the chart's inner RH voice) in the
  chart's 3+(3~2): one merged note for every tie, separate bows at f
  (largamente, full bows); Vln I's D6-E6-F6 pickup in 17 slurred into the
  new bow on A6; the Em7b5 bar (21) sung on one held note with the chart's
  A-Bb octaves slurred in both violins.
* Vln II: div. on the sustained dyads (17, 21 beats 1-3), unis. elsewhere;
  bar 18's borrowed Db6 marked espr. with tenuto on both attacks, the
  loudest inner note, inside a < > swell shared with Vln I.
* Vla: the guide-tone lament F4-E4-E4-D4-D4-C#4-C4-C4 as div. whole-note
  dyads, one bow per bar (partial ties are impossible in the token syntax,
  and a fresh bow per bar keeps the falling line audible), kept at mf.
* Vc: the chart's LH arpeggios at pitch, cantabile, one slur over each
  arc; the big leaps back to the bass (17, 19, 20) and the bass quarters
  are taken on a new bow; blocked chords in 21/23 as in the chart; launch
  walk D3-C3-Bb2-A2 accented.
* Cb: roots as whole notes, the 21 pickup E2, the walk D2-C2-Bb1-A1
  accented, in octaves with the Vc.

Dynamics: everyone lands f at 17 (the target of W1's cresc. molto in 16);
Vla, Vc and Cb settle to mf over bar 17 so that the melody sits one level
above the accompaniment; 18 violins f < > (the signature swell) back to f;
20 poco dim. -> 21 mf (violins, Vla) / mp (Vc, Cb), the saddest bar;
22 cresc. -> f on beat 4; 23 mf in the upper three / mp in Vc and Cb
(the plan's "subito mf": no hairpin, so the drop is immediate); 24
cresc. molto into W3's ff at 25.

Departures from the plan (none in pitch or rhythm):
* "subito" and "poco meno" are not printed as words (neither is in the
  allowed expression list; "poco meno" also reads as a tempo change and
  the body stays in tempo). The subito is carried by the notation itself
  (f on 22 beat 4, mf/mp at 23 with no hairpin); the "poco meno" by mf.
* The < > swell in 18 is written as cresc (18.0-18.7) + dim (18.8-18.15)
  with f printed at 19 (the only spelling engrave.py prints without
  cutting the dim short). In MIDI this gives 92->104, a step to 92 at
  beat 3, ->80, then f at 19: the syncopated attacks on 2& get ~102.
"""

VN1 = {
    17: "F6/10 (D6/2 E6/2 F6/2)",
    18: "A6/6 G6/10",
    19: "E6/6 C6/10",
    20: "A5/6 G5/10",
    21: "Bb5/12 (A5/2 Bb5/2)",
    22: "C6/6 Bb5/6 A5/4",
    23: "G5/6 F5/6 G5/4",
    24: "A5/4 F#5/4 G5/4 A5/4",
}

VN2 = {
    17: "F5+Bb5/16",
    18: "Db6/6_ Db6/10_",
    19: "C6/6 A5/10",
    20: "D5/6 D5/10",
    21: "D5+G5/12 (A4/2 Bb4/2)",
    22: "C#5+E5/6 C#5+E5/6 C#5+E5/4",
    23: "C5/6 C5/6 C5/4",
    24: "Eb5/4 Eb5/4 Eb5/4 F#5/4",
}

VA = {
    17: "Bb3+F4/16",
    18: "Bb3+E4/16",
    19: "A3+E4/16",
    20: "D4+A4/16",
    21: "D4+G4/16",
    22: "C#4+G4/16",
    23: "C4+F4/16",
    24: "C4+F#4/8 C4+A4/8",
}

VC = {
    17: "G2/4 (Bb3/2 D4/2 F4/2 Bb3/2 D4/2) G2/2",
    18: "C3/4 (E3/2 G3/2 Bb3/2 G3/2 E3/2 C3/2)",
    19: "F2/2 (F3/2 A3/2 C4/2 E4/2 C4/2 A3/2) F2/2",
    20: "Bb2/2 (Bb3/2 D4/2 F4/2 A4/2 F4/2 D4/2) Bb2/2",
    21: "E3/6 E3+Bb3/6 r/2 E3/2",
    22: "A2/4 (C#3/2 E3/2 G3/2 E3/2 C#3/2 A2/2)",
    23: "D3/6 D3+A3/6 A2/4",
    24: "D3/4 F#3+C4/4 D3/2> C3/2> Bb2/2> A2/2>",
}

CB = {
    17: "G1/16",
    18: "C2/16",
    19: "F1/16",
    20: "Bb1/16",
    21: "E2/12 r/2 E2/2",
    22: "A1/16",
    23: "D2/12 A1/4",
    24: "D2/4 r/4 D2/2> C2/2> Bb1/2> A1/2>",
}

DYN = {
    "vn1": [(17, 0, "f"), (19, 0, "f"), (21, 0, "mf"), (22, 12, "f"),
            (23, 0, "mf")],
    "vn2": [(17, 0, "f"), (19, 0, "f"), (21, 0, "mf"), (22, 12, "f"),
            (23, 0, "mf")],
    "va": [(17, 0, "f"), (18, 0, "mf"), (22, 12, "f"), (23, 0, "mf")],
    "vc": [(17, 0, "f"), (18, 0, "mf"), (21, 0, "mp"), (22, 12, "f"),
           (23, 0, "mp")],
    "cb": [(17, 0, "f"), (18, 0, "mf"), (21, 0, "mp"), (22, 12, "f"),
           (23, 0, "mp")],
}

HAIR = {
    "vn1": [(18, 0, 18, 7, "cresc"), (18, 8, 18, 15, "dim"),
            (20, 8, 20, 15, "dim"), (22, 0, 22, 11, "cresc"),
            (24, 0, 24, 15, "cresc")],
    "vn2": [(18, 0, 18, 7, "cresc"), (18, 8, 18, 15, "dim"),
            (20, 8, 20, 15, "dim"), (22, 0, 22, 11, "cresc"),
            (24, 0, 24, 15, "cresc")],
    "va": [(17, 4, 17, 15, "dim"), (22, 0, 22, 11, "cresc"),
           (24, 0, 24, 15, "cresc")],
    "vc": [(17, 4, 17, 15, "dim"), (20, 8, 20, 15, "dim"),
           (22, 0, 22, 11, "cresc"), (24, 0, 24, 15, "cresc")],
    "cb": [(17, 4, 17, 15, "dim"), (20, 8, 20, 15, "dim"),
           (22, 0, 22, 11, "cresc"), (24, 0, 24, 15, "cresc")],
}

TEXT = {
    "vn1": [(17, 0, "largamente"), (21, 0, "espr.")],
    "vn2": [(17, 0, "div."), (18, 0, "unis. espr."),
            (21, 0, "div."), (21, 12, "unis.")],
    "va": [(17, 0, "div.")],
    "vc": [(17, 4, "cantabile")],
    "cb": [],
}

MELODY = {b: [("vn1", 0)] for b in range(17, 25)}
MELODY_FREE = {}

# the chart's own b9 colours in bars 17-24 (copied from the skeleton)
CLASH_ALLOW = {
    (18, "vn2", "vc"): "Db6 over the C bass: the chart's C7(b9) / borrowed Bbm6 over C",
    (18, "vn2", "cb"): "Db6 over the C bass: the chart's C7(b9) / borrowed Bbm6 over C",
    (22, "vn1", "cb"): "melody Bb5 over the A bass: the chart's A7(b9)",
    (24, "vn2", "vc"): "Eb5 over the D bass: the chart's D7(b9)",
    (24, "vn2", "cb"): "Eb5 over the D bass: the chart's D7(b9)",
}

# PLAN §6.4 entries that cover bars 17-24
DOUBLINGS = [("vn1", "vn2", 21, 21), ("vc", "cb", 8, 52)]

CLEFS = {}
