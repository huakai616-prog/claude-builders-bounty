"""诀别书 · 弦乐五重奏 — W3 draft: C · Chorus II · 副歌 · 二 (bars 25-32)

What is written here (PLAN.md §3 "C", §4, §5, §6):

* Pitches, harmony and voicing are the skeleton's (plan/00_skeleton.py).
  Seams kept: 24->25 Vln I F6 ff / Vln II F5 (the chromatic F#5->F5) /
  Vla Bb4+D5 / Vc G2 / Cb G1; 32->33 Vln I D5 w p / Vln II A4 / Vla F4 /
  Vc C3 h / Cb C2 h (poco rit. on beats 3-4 comes from the global
  TEMPO_TEXT).
* Violins in octaves 25-30 (the lift). Vln II copies Vln I's slurs, ties
  and accents exactly. Both land with an accent on the downbeat of 25. Bars
  26-28 are the chart's 3+(3~2): one merged note per tie and a separate
  full bow on each attack at ff (bars 17-20 are bowed the same way). The
  summit Bb6/Bb5 (27) is accented and marked con tutta forza; its
  resolution to A6/A5 takes the next bow. The chart's pickup D-E-F (25)
  and the sigh pairs A-G / F-E (29-30) are slurred. The 8th rests in
  29-30 are real breaths. Bar 31: E6 on its own bow, then E5 slurred into
  the dolce D5 of 32 (A string), so the phrase ends legato.
* Vla: div. dyads Bb4+D5 (25) and Bb4+Db5 (26, tenuto, the borrowed-iv
  colour). The chromatic thread D5 -> Db5 -> C5 falls on the downbeats of
  25, 26 and 27. unis. at 26 beat 3: the riser, Bb4-Db5 bariolage in
  one-beat slurs, cresc. molto into the summit, then bariolage through
  27-30 in one-beat slurs (it keeps moving through the violins' breaths
  in 29-30). Bar 31 div. F3+C4, then unis. F4.
* Vc: the chart's LH arpeggios 25-27, bowed single note + short slurs so
  each downbeat can take a down-bow. Bars 28-30 are the chart's block LH
  in 3+3+2, accented on 1 and 2&. Bar 31: the rising D3-A3-E4 in one
  slur. Bar 32: halves D3+C4 -> C3, plain (not tenuto), so that the MIDI
  keeps a little air before W4's secco Bb2 at 33.
* Cb: roots. G1 / C2 / F1 are whole notes; the 3+3+2 bars re-strike the
  root on beat 4 with the Vc; 31 D2 dh; 32 D2 -> C2 halves.

Dynamics: everyone lands ff at 25 (the target of W2's cresc. molto in 24).
Vla, Vc and Cb settle to f over bar 25, so the octave melody sits one
level above them, as W2 did in bar 17. Bar 26: Vc and Cb < across the bar;
the Vla < on beats 3-4 (the riser) and the violins < on their tied G6/G5
from 2& (no subito p). All five are ff con tutta forza at 27 and ff in 28.
From 2& of 28, > to f (violins) / mf (Vla, Vc, Cb) at 29. From 2& of 30,
> to mf (Vln I) / mp (the others). Bar 31 is "mf dim." -> 32 p dolce
(Vln I) / pp (all others).
Hairpins start on a note onset (25.0, 26.0/26.6/26.8, 28.6, 30.6, 31.0).
build.py's MusicXML export anchors a wedge on the notes that start at or
after its first position and at or before its last one. A wedge that
starts inside a held note would come out reversed in the Sibelius file.

Departures from the plan / skeleton (no pitch or harmony changes):
* Vla bariolage phase. In 27, pos 0-5 run C5-G4 (upper note first), not
  G4-C5. The Db5 of 26 then resolves straight to C5 on the summit
  downbeat (thread 5 of PLAN §1: D -> Db -> C), and the plan's phase would
  have repeated C5 at pos 5/6 inside a slurred group. For the same
  reason (a continuous rocking figure with no repeated note at the
  barlines), 28-30 are also upper note first: D5-A4, D5-Bb4, G4-C#4.
  Bar 30 then ends on C#4, which moves to the C4 of 31 (C# -> C, as in the
  lament of 22 -> 23). --check is clean with these phases (no Vla/Vc
  parallels).
* Common tones tied into 32: Vln II A4 and Vla F4 from beat 4 of 31
  (the chart re-strikes the chord). At the dolce arrival only the melody
  (E5 -> D5) and the bass move, so the texture "drains to one bare D".
  The seam pitches at 32 (A4 w, F4 w) are unchanged.
* "cresc. molto" (26) and "dim." (30, 31) are written as hairpins only,
  as W1 and W2 did. The violins' < in 26 needs a printed
  target, so ff is printed again at 27, together with con tutta forza.
  In MIDI this gives a real swell on the tied G6/G5 into the accented
  Bb6/Bb5. fff stays reserved for 45-46.
* The plan's single marking per bar is applied with the balance rule: the
  accompaniment is one level under the melody in 25 (after the landing),
  26 and 29-32.
"""

VN1 = {
    25: "F6/10> (D6/2 E6/2 F6/2)",
    26: "A6/6 G6/10",
    27: "Bb6/6> A6/10",
    28: "G6/6 F6/10",
    29: "(A6/2 G6/2) r/2 D6/10",
    30: "(F6/2 E6/2) r/2 A5/10",
    31: "E6/12 (E5/4",
    32: "D5/16)",
}

VN2 = {
    25: "F5/10> (D5/2 E5/2 F5/2)",
    26: "A5/6 G5/10",
    27: "Bb5/6> A5/10",
    28: "G5/6 F5/10",
    29: "(A5/2 G5/2) r/2 D5/10",
    30: "(F5/2 E5/2) r/2 A4/10",
    31: "A5+C6/12 A4/4~",
    32: "A4/16",
}

VA = {
    25: "Bb4+D5/16",
    26: "Bb4+Db5/6_ Bb4+Db5/2_ (Bb4/1 Db5/1 Bb4/1 Db5/1) "
        "(Bb4/1 Db5/1 Bb4/1 Db5/1)",
    27: "(C5/1 G4/1 C5/1 G4/1) (C5/1 G4/1 C5/1 A4/1) "
        "(C5/1 A4/1 C5/1 A4/1) (C5/1 A4/1 C5/1 A4/1)",
    28: "(D5/1 A4/1 D5/1 A4/1) (D5/1 A4/1 D5/1 A4/1) "
        "(D5/1 A4/1 D5/1 A4/1) (D5/1 A4/1 D5/1 A4/1)",
    29: "(D5/1 Bb4/1 D5/1 Bb4/1) (D5/1 Bb4/1 D5/1 Bb4/1) "
        "(D5/1 Bb4/1 D5/1 Bb4/1) (D5/1 Bb4/1 D5/1 Bb4/1)",
    30: "(G4/1 C#4/1 G4/1 C#4/1) (G4/1 C#4/1 G4/1 C#4/1) "
        "(G4/1 C#4/1 G4/1 C#4/1) (G4/1 C#4/1 G4/1 C#4/1)",
    31: "F3+C4/12 F4/4~",
    32: "F4/16",
}

VC = {
    25: "G2/4> (Bb3/2 D4/2 F4/2) (Bb3/2 D4/2) G2/2",
    26: "C3/4 (E3/2 G3/2 Bb3/2) (G3/2 E3/2) C3/2",
    27: "F2/2> (F3/2 A3/2 C4/2 E4/2) (C4/2 A3/2) F3/2",
    28: "Bb2/6> D3+A3/6> Bb2/4",
    29: "E2/6> G3+D4/6> E2/4",
    30: "A2/6> E3+C#4/6> A2/4",
    31: "(D3/4 A3/4 E4/4) r/4",
    32: "D3+C4/8 C3/8",
}

CB = {
    25: "G1/16>",
    26: "C2/16",
    27: "F1/16>",
    28: "Bb1/12> Bb1/4",
    29: "E1/12> E1/4",
    30: "A1/12> A1/4",
    31: "D2/12 r/4",
    32: "D2/8 C2/8",
}

DYN = {
    "vn1": [(25, 0, "ff"), (27, 0, "ff"), (29, 0, "f"), (31, 0, "mf"),
            (32, 0, "p")],
    "vn2": [(25, 0, "ff"), (27, 0, "ff"), (29, 0, "f"), (31, 0, "mp"),
            (32, 0, "pp")],
    "va": [(25, 0, "ff"), (26, 0, "f"), (27, 0, "ff"), (29, 0, "mf"),
           (31, 0, "mp"), (32, 0, "pp")],
    "vc": [(25, 0, "ff"), (26, 0, "f"), (27, 0, "ff"), (29, 0, "mf"),
           (31, 0, "mp"), (32, 0, "pp")],
    "cb": [(25, 0, "ff"), (26, 0, "f"), (27, 0, "ff"), (29, 0, "mf"),
           (31, 0, "mp"), (32, 0, "pp")],
}

HAIR = {
    "vn1": [(26, 6, 26, 15, "cresc"), (28, 6, 28, 15, "dim"),
            (30, 6, 30, 15, "dim"), (31, 0, 31, 15, "dim")],
    "vn2": [(26, 6, 26, 15, "cresc"), (28, 6, 28, 15, "dim"),
            (30, 6, 30, 15, "dim"), (31, 0, 31, 15, "dim")],
    "va": [(25, 0, 25, 15, "dim"), (26, 8, 26, 15, "cresc"),
           (28, 6, 28, 15, "dim"), (30, 6, 30, 15, "dim"),
           (31, 0, 31, 15, "dim")],
    "vc": [(25, 0, 25, 15, "dim"), (26, 0, 26, 15, "cresc"),
           (28, 6, 28, 15, "dim"), (30, 6, 30, 15, "dim"),
           (31, 0, 31, 11, "dim")],
    "cb": [(25, 0, 25, 15, "dim"), (26, 0, 26, 15, "cresc"),
           (28, 6, 28, 15, "dim"), (30, 6, 30, 15, "dim"),
           (31, 0, 31, 11, "dim")],
}

TEXT = {
    "vn1": [(27, 0, "con tutta forza"), (32, 0, "dolce")],
    "vn2": [(27, 0, "con tutta forza"), (31, 0, "div."), (31, 12, "unis.")],
    "va": [(25, 0, "div."), (26, 8, "unis."), (27, 0, "con tutta forza"),
           (31, 0, "div."), (31, 12, "unis.")],
    "vc": [(27, 0, "con tutta forza")],
    "cb": [(27, 0, "con tutta forza")],
}

MELODY = {b: [("vn1", 0), ("vn2", -12)] for b in range(25, 31)}
MELODY.update({31: [("vn1", 0)], 32: [("vn1", 0)]})
MELODY_FREE = {}

# the chart's own b9 colours in bars 25-32 (copied from the skeleton)
CLASH_ALLOW = {
    (26, "va", "vc"): "Db5 over the C bass: the chart's C7(b9) (borrowed iv now in the viola)",
    (26, "va", "cb"): "Db5 over the C bass: the chart's C7(b9) (borrowed iv now in the viola)",
    (27, "vn1", "vc"): "Bb6 appoggiatura against the chart's LH arpeggio A3 (pos 4-6)",
    (27, "vn2", "vc"): "Bb5 appoggiatura against the chart's LH arpeggio A3 (pos 4-6)",
}

# PLAN §6.4 entries that cover bars 25-32
DOUBLINGS = [("vn1", "vn2", 25, 30), ("vc", "cb", 8, 52)]

CLEFS = {}
