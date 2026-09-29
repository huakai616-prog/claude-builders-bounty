"""S10 · bars 78-81 · Breakdown 崩落.

Harmony (one per bar, bass rising then falling to the dominant):
  78 E-flat(maj7, no 3rd) · 79 B-flat/F · 80 Gm · 81 C-F-B-flat over D
  (Dm7 colour) -> 82 Gm (S11, pre-chorus p).

Every bar has the same two halves.
- Beats 1-2, the piano's fingered 32nd tremolo [B-flat5 D6] <-> B-flat6
  (81: [C6 F6] <-> C7) becomes a bowed tremolo that sounds both layers at
  once: Vn I on the top note (B-flat6 / C7, under an 8va line for 78-81 so
  it reads like the piano: written B-flat5 / C6), Vn II on the lower dyad
  as a double stop (a third / a fourth on A+E), Va the same dyad an octave
  lower (B-flat4+D5 thirds; 81 F4+C5 fifth) for body in the empty middle.
- Beats 3-4, the 32nd cascade is an exact four-player relay, one 8th
  each, slurred per group with an accent on each group's first note:
  Vn I B-flat6 E-flat6 D6 B-flat5 -> Vn II B-flat5 E-flat5 D5 B-flat4 ->
  Va B-flat4 E-flat4 D4 B-flat3 -> Vc B-flat3 E-flat3 D3 B-flat2 (the
  piano's LH group).  The cascade repeats the pitch at every joint, so each
  hand-off is a unison: the player who has finished holds that note (tied)
  to the barline and lets it die away (dim.) - the strings' version of the
  pedal that lets the whole cascade ring - while the line falls on below.
  The next bar's tremolo re-enters ff.
- Vc = the LH: the low bass on beat 1 (E-flat2 / F2 / G2 open / D2 - the
  piano's octave an octave up), the octave 8ths on the off-beat pulse
  (octave double stops, marcato), the half note on beat 3 cut to a dotted
  quarter so the cello can play its own cascade group on the last 8th.
- 81 closes the section: dim. from the cascade on (ff -> p) into the
  pre-chorus; Vn II ends with the RH's F4 8th, which leads into its F4 at
  82.  Nothing is tied over the last barline.
Dynamics: the piano has none here; S09 crescendos through 77, so the
breakdown is ff (the piano's climax of the solo) and collapses in 81 to
the p/mp of S11.
"""

VN1 = {
    78: "Bb6/32trem3 (Bb6/2> Eb6/2 D6/2 Bb5/2~) Bb5/24",
    79: "Bb6/32trem3 (Bb6/2> Eb6/2 D6/2 Bb5/2~) Bb5/24",
    80: "Bb6/32trem3 (Bb6/2> Eb6/2 D6/2 Bb5/2~) Bb5/24",
    81: "C7/32trem3 (C7/2> Bb6/2 F6/2 C6/2~) C6/24",
}

VN2 = {
    78: "Bb5+D6/32trem3 r/8 (Bb5/2> Eb5/2 D5/2 Bb4/2~) Bb4/16",
    79: "Bb5+D6/32trem3 r/8 (Bb5/2> Eb5/2 D5/2 Bb4/2~) Bb4/16",
    80: "Bb5+D6/32trem3 r/8 (Bb5/2> Eb5/2 D5/2 Bb4/2~) Bb4/16",
    81: "C6+F6/32trem3 r/8 (C6/2> Bb5/2 F5/2 C5/2~) C5/8 F4/8",
}

VA = {
    78: "Bb4+D5/32trem3 r/16 (Bb4/2> Eb4/2 D4/2 Bb3/2~) Bb3/8",
    79: "Bb4+D5/32trem3 r/16 (Bb4/2> Eb4/2 D4/2 Bb3/2~) Bb3/8",
    80: "Bb4+D5/32trem3 r/16 (Bb4/2> Eb4/2 D4/2 Bb3/2~) Bb3/8",
    81: "F4+C5/32trem3 r/16 (C5/2> Bb4/2 F4/2 C4/2~) C4/8",
}

VC = {
    78: "Eb2/8> Eb2+Eb3/8 Eb2+Eb3/8 Eb2+Eb3/8 Eb2+Eb3/24> "
        "(Bb3/2> Eb3/2 D3/2 Bb2/2)",
    79: "F2/8> F2+F3/8 F2+F3/8 F2+F3/8 F2+F3/24> "
        "(Bb3/2> Eb3/2 D3/2 Bb2/2)",
    80: "G2/8> G2+G3/8 G2+G3/8 G2+G3/8 G2+G3/24> "
        "(Bb3/2> Eb3/2 D3/2 Bb2/2)",
    81: "D2/8> D2+D3/8 D2+D3/8 D2+D3/8 D2+D3/24> "
        "(C4/2> Bb3/2 F3/2 C3/2)",
}

DYN = {
    # the upper parts' held notes die away each bar, so their tremolo
    # re-enters ff; the viola's hold is a single 8th and stays ff
    "vn1": [(78, 0, "ff"), (79, 0, "ff"), (80, 0, "ff"), (81, 0, "ff")],
    "vn2": [(78, 0, "ff"), (79, 0, "ff"), (80, 0, "ff"), (81, 0, "ff")],
    "va": [(78, 0, "ff")],
    "vc": [(78, 0, "ff")],
}

HAIR = {
    # held unison at each hand-off decays under the falling line; 81 dim.
    # into the pre-chorus (p / mp at 82)
    "vn1": [(78, 40, 78, 63, "dim"), (79, 40, 79, 63, "dim"),
            (80, 40, 80, 63, "dim"), (81, 32, 81, 63, "dim")],
    "vn2": [(78, 48, 78, 63, "dim"), (79, 48, 79, 63, "dim"),
            (80, 48, 80, 63, "dim"), (81, 40, 81, 63, "dim")],
    "va": [(81, 48, 81, 63, "dim")],
    "vc": [(81, 32, 81, 63, "dim")],
}

TEXT = {
    "vn1": [(78, 0, "con forza")],
    "vn2": [],
    "va": [],
    "vc": [(78, 0, "marcato")],
}

CLEFS = {}

# Vn I's B-flat6 / C7 tremolo and the top of the cascade read an octave
# lower, as in the piano's own 8va (written B-flat5 / C6)
OTTAVA = [("vn1", 78, 81)]

# The piano's fingered tremolo is encoded in the source as two quarters
# in sequence ([B-flat5 D6] on beat 1, B-flat6 on beat 2; 81: [C6 F6],
# C7), but it sounds as one shimmering chord for the whole half note (32nd
# alternation).  The strings play both layers at once, as the brief asks
# (Vn I bowed tremolo on the top note over Vn II's / the viola's tremolo
# dyad).  The literal check therefore reads: MELODY - D6 (F6) "missing" at
# +0 (it is there, in Vn II, under Vn I's B-flat6 / C7) and B-flat6 (C7)
# at +16 (no re-attack inside the tremolo); FOREIGN - D (F) "extra" at
# +20..+28 (the dyad's top note, which the piano keeps alternating through
# beat 2).  Checked: without these entries these are the only items in
# 78-81; the cascades (beats 3-4), the bass and every other beat are clean.
ALLOW = {
    ("mel", 78), ("mel", 79), ("mel", 80), ("mel", 81),
    ("foreign", 78), ("foreign", 79), ("foreign", 80), ("foreign", 81),
}
