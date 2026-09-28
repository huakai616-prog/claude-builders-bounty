"""诀别书 · 弦乐五重奏 — PLAN SKELETON (the pitch / voicing contract of PLAN.md)

This is NOT the finished arrangement. It is the plan's harmony and voicing,
bar by bar, in build.py token syntax, with bare rhythms and no phrasing,
articulation or dynamics. It exists so that
  * every pitch PLAN.md names has been run through build.py --check, and
  * each section writer can test their draft against the neighbours' seams.

Status: with this file as the only draft,
  JUEBIESHU_DRAFTS=<dir holding this file> python3 juebieshu/build.py --check
prints nothing (0 RANGE / STOP / CLASH / PARALLEL / MELODY / BASS findings).

How writers use it (see PLAN.md §7):
  mkdir -p /tmp/jbs && cp juebieshu/plan/00_skeleton.py /tmp/jbs/
  cp juebieshu/draft/<your file>.py /tmp/jbs/     # sorts after 00_, overrides
  JUEBIESHU_DRAFTS=/tmp/jbs python3 juebieshu/build.py --check --bars A-B
Do NOT put this file into juebieshu/draft/ (the merge refuses bars defined
twice).  Writers keep the seam pitches (PLAN.md §5) and the harmony, and are
expected to replace the bare rhythms here with the figures PLAN.md describes
(slurs, articulation, dynamics, idiomatic detail).
"""


def rep(a, b, n=8):
    return " ".join(f"{a}/1 {b}/1" for _ in range(n))

VN1 = {
1: "D5/2 A5/1 G5/1 A5/2 r/2 r/8", 2: "C5/2 G5/1 F5/1 G5/2 r/2 r/8",
3: "C5/2 G5/1 F5/1 G5/2 r/2 r/8", 4: "C6/2 F5/1 E5/1 F5/2 r/2 r/8",
5: "D5/2 A5/1 G5/1 A5/2 r/2 r/8", 6: "D6/2 G5/1 F5/1 G5/2 r/2 r/8",
7: "E6/2 G5/1 F5/1 G5/2 r/2 r/8", 8: "F6/2 E6/2 D6/12",
9: "D5/2 A5/1 G5/1 A5/2 G5/2 A5/2 D6/2 A5/2 G5/2",
10: "A5/1 G5/1 A5/1 G5/1 A5/2 G5/2 C5/8",
11: "C5/2 G5/1 F5/1 G5/2 F5/2 G5/2 C6/2 C6/2 G5/2",
12: "G5/1 A5/1 G5/1 A5/1 G5/2 E5/2 F5/8",
13: "D5/2 A5/1 G5/1 A5/2 G5/2 A5/2 D6/2 A5/2 G5/2",
14: "A5/1 G5/1 A5/1 G5/1 A5/2 G5/2 C5/8",
15: "C5/2 G5/1 F5/1 G5/2 F5/2 G5/2 C6/2 C6/2 E6/2",
16: "D6/1 E6/1 D6/1 E6/1 D6/2 C6/2 D6/2 A5/2 D6/2 E6/2",
17: "F6/10 D6/2 E6/2 F6/2", 18: "A6/6 G6/10", 19: "E6/6 C6/10", 20: "A5/6 G5/10",
21: "Bb5/12 A5/2 Bb5/2", 22: "C6/6 Bb5/6 A5/4", 23: "G5/6 F5/6 G5/4",
24: "A5/4 F#5/4 G5/4 A5/4",
25: "F6/10 D6/2 E6/2 F6/2", 26: "A6/6 G6/10", 27: "Bb6/6 A6/10", 28: "G6/6 F6/10",
29: "A6/2 G6/2 r/2 D6/10", 30: "F6/2 E6/2 r/2 A5/10", 31: "E6/12 E5/4", 32: "D5/16",
33: "r/16", 34: "r/16", 35: "A5/16~", 36: "A5/12 A5/1 Bb5/1 C6/1 D6/1",
37: "E6/2 D6/2 A5/2 E6/2 D6/2 A5/2 D6/2 E6/2",
38: "F6/2 E6/2 A5/2 F6/2 E6/2 A5/2 E6/2 F6/2",
39: "G6/2 F6/2 A5/2 G6/2 F6/2 A5/2 F6/2 E6/2", 40: "D6/12 r/4",
41: "A5/2 D6/1 D6/1 D6/2 A5/1 A5/1 A5/2 F5/1 F5/1 F5/2 A5/2",
42: "A5/2 G5/1 G5/1 G5/2 F#5/2 G5/8",
43: "G5/2 C6/1 C6/1 C6/2 G5/1 G5/1 G5/2 E5/1 E5/1 E5/2 G5/2",
44: "G5/2 F5/1 F5/1 F5/2 E5/2 F5/8",
45: "C6/2 Bb5/2 F5/2 C6/4 Bb5/6", 46: "Bb5/6 A5/6 E5/4", 47: "E5/12 E5/4", 48: "D5/16",
49: "D6/4 A6/2 G6/2 A6/4 G6/4", 50: "A6/4 D7/4 A6/4 G6/4",
51: "A6/2 G6/2 A6/2 G6/2 A6/4 G6/4", 52: "C7/16!",
}
VN2 = {
1: "r/16", 2: "r/16", 3: "r/16", 4: "r/16",
5: "r/2 A4/4 A4/2 r/2 A4/4 A4/2", 6: "r/2 G4/4 G4/2 r/2 G4/4 G4/2",
7: "r/2 G4/4 G4/2 r/2 G4/4 r/2", 8: "A5/2 G5/2 F5/12",
9: "C5/16", 10: "E5/8 G4/8", 11: "A4/8 E5/8", 12: "D5/8 F4/2 C5/1 Bb4/1 C5/2 r/2",
13: "D4/2 A4/1 G4/1 A4/2 G4/2 A4/2 D5/2 A4/2 G4/2",
14: "A4/1 G4/1 A4/1 G4/1 A4/2 G4/2 C4/8",
15: "C4/2 G4/1 F4/1 G4/2 F4/2 G4/2 C5/2 C5/2 E5/2",
16: "D5/1 E5/1 D5/1 E5/1 D5/2 C5/2 D5/2 A4/2 D5/2 E5/2",
17: "F5+Bb5/16", 18: "Db6/6 Db6/10", 19: "C6/6 A5/10", 20: "D5/6 D5/10",
21: "D5+G5/12 A4/2 Bb4/2", 22: "C#5+E5/6 C#5+E5/6 C#5+E5/4", 23: "C5/6 C5/6 C5/4",
24: "Eb5/4 Eb5/4 Eb5/4 F#5/4",
25: "F5/10 D5/2 E5/2 F5/2", 26: "A5/6 G5/10", 27: "Bb5/6 A5/10", 28: "G5/6 F5/10",
29: "A5/2 G5/2 r/2 D5/10", 30: "F5/2 E5/2 r/2 A4/10", 31: "A5+C6/12 A4/4", 32: "A4/16",
33: "E5/2 D5/2 A4/2 E5/2 D5/2 A4/2 D5/2 E5/2",
34: "F5/2 E5/2 A4/2 F5/2 E5/2 A4/2 E5/2 F5/2",
35: "G5/2 F5/2 A4/2 G5/2 F5/2 A4/2 F5/2 G5/2", 36: "F5/12 r/4",
37: "E5/2 D5/2 A4/2 E5/2 D5/2 A4/2 D5/2 E5/2",
38: "F5/2 E5/2 A4/2 F5/2 E5/2 A4/2 E5/2 F5/2",
39: "G5/2 F5/2 A4/2 G5/2 F5/2 A4/2 F5/2 E5/2", 40: "A5/12 r/4",
41: "A4/2 D5/1 D5/1 D5/2 A4/1 A4/1 A4/2 F4/1 F4/1 F4/2 A4/2",
42: "A4/2 G4/1 G4/1 G4/2 F#4/2 G4/8",
43: "G4/2 C5/1 C5/1 C5/2 G4/1 G4/1 G4/2 E4/1 E4/1 E4/2 G4/2",
44: "G4/2 F4/1 F4/1 F4/2 E4/2 F4/8",
45: "C5/2 Bb4/2 F4/2 C5/4 Bb4/6", 46: "C#5+E5/6 C#5+E5/6 r/4", 47: "C5/12 A4/4", 48: "A4/16",
49: "r/8 F5+A5/8", 50: "r/4 F5+A5/8 F5+A5/4", 51: "E5+G5/16~", 52: "E5+G5/16!",
}
VA = {
1: "F4/16", 2: "F4/8 E4/8", 3: "D4/8 E4/8", 4: "F4/16",
5: "r/2 F4/4 F4/2 r/2 F4/4 F4/2", 6: "r/2 F4/4 F4/2 r/2 E4/4 E4/2",
7: "r/2 D4/4 D4/2 r/2 E4/4 r/2", 8: "G4/8 F4/8",
9: "F3/2 Bb3/2 D4/2 A4/2 F3/2 Bb3/2 D4/2 A4/2",
10: "G3/2 C4/2 E4/2 G4/2 Bb3/2* G4/2* E4/2* C4/2*",
11: "A3/2 C4/2 G4/2 C4/2 A3/2 E4/2 G4/2 C4/2",
12: "D4/2 F4/2 A4/2 F4/2 D4/4 F4/4",
13: "F3/2 Bb3/2 D4/2 Bb3/2 D3/2 F3/2 A3/2 D4/2",
14: "C3/2 E3/2 G3/2 C4/2 Bb3/2* G4/2* E4/2* C4/2*",
15: "A3/2 C4/2 G3/2 C4/2 A3/2 E3/2 G3/2 C4/2",
16: "D3/2 F3/2 A3/2 F3/2 A3/1 Bb3/1 C4/1 D4/1 E4/1 F4/1 G4/1 A4/1",
17: "Bb3+F4/16", 18: "Bb3+E4/16", 19: "A3+E4/16", 20: "D4+A4/16", 21: "D4+G4/16",
22: "C#4+G4/16", 23: "C4+F4/16", 24: "C4+F#4/8 C4+A4/8",
25: "Bb4+D5/16", 26: "Bb4+Db5/6 Bb4+Db5/2 " + rep("Bb4", "Db5", 4),
27: rep("G4", "C5", 3) + " " + rep("C5", "A4", 5), 28: rep("A4", "D5"), 29: rep("Bb4", "D5"),
30: rep("C#4", "G4"), 31: "F3+C4/12 F4/4", 32: "F4/16",
33: "F3+A3/6 F3+A3/6 F3+A3/4", 34: "A3+C4/6 A3+C4/6 A3+C4/4",
35: "A3+C4/6 A3+C4/6 A3+C4/4", 36: "A4+C5/12 r/4",
37: rep("Bb3", "D4"), 38: rep("A3", "F4"), 39: rep("D4", "A4"), 40: rep("A4", "D5", 6) + " r/4",
41: rep("D4", "F4"), 42: rep("E4", "C4"), 43: rep("E4", "A3"), 44: rep("A3", "D4"),
45: "C4/2 Bb3/2 F3/2 C4/4 Bb3/6", 46: "G4+Bb4/6 G4+Bb4/6 r/4", 47: "F3+C4/12 F4/4", 48: "F4/16",
49: "r/8 Bb4+D5/8", 50: "Bb4/4 D5/8 Bb4/4", 51: "Bb4+C5/16~", 52: "Bb4+C5/16!",
}
VC = {
1: "Bb3/16", 2: "Bb3/16", 3: "A3/16", 4: "D3/12 C3/4",
5: "Bb2/4 r/4 Bb2/4 r/4", 6: "Bb2/4 r/4 Bb2/4 r/4", 7: "A2/4 r/4 A2/4 r/2 A2/2",
8: "D3/4 D3+A3/4 D3/4 C3/4",
9: "Bb2/16", 10: "Bb2/16", 11: "A2/16", 12: "D3/4 D3+A3/4 D3/4 C3/4",
13: "Bb2/6 Bb2/6 Bb2/4", 14: "Bb2/6 Bb2/6 Bb2/4", 15: "A2/6 A2/6 A2/4",
16: "D3/4 D3+A3/4 D3/2 C3/2 Bb2/2 A2/2",
17: "G2/4 Bb3/2 D4/2 F4/2 Bb3/2 D4/2 G2/2", 18: "C3/4 E3/2 G3/2 Bb3/2 G3/2 E3/2 C3/2",
19: "F2/2 F3/2 A3/2 C4/2 E4/2 C4/2 A3/2 F2/2", 20: "Bb2/2 Bb3/2 D4/2 F4/2 A4/2 F4/2 D4/2 Bb2/2",
21: "E3/6 E3+Bb3/6 r/2 E3/2", 22: "A2/4 C#3/2 E3/2 G3/2 E3/2 C#3/2 A2/2",
23: "D3/6 D3+A3/6 A2/4", 24: "D3/4 F#3+C4/4 D3/2 C3/2 Bb2/2 A2/2",
25: "G2/4 Bb3/2 D4/2 F4/2 Bb3/2 D4/2 G2/2", 26: "C3/4 E3/2 G3/2 Bb3/2 G3/2 E3/2 C3/2",
27: "F2/2 F3/2 A3/2 C4/2 E4/2 C4/2 A3/2 F3/2", 28: "Bb2/6 D3+A3/6 Bb2/4",
29: "E2/6 G3+D4/6 E2/4", 30: "A2/6 E3+C#4/6 A2/4", 31: "D3/4 A3/4 E4/4 r/4", 32: "D3+C4/8 C3/8",
33: "Bb2/2* r/4 Bb2/2* r/4 Bb2/2* r/2", 34: "C3/2* r/4 C3/2* r/4 C3/2* r/2",
35: "D3/2* r/4 D3/2* r/4 D3/2* r/2", 36: "D3/4 D3+A3/4 D3/4 C3/4",
37: "Bb2/6 Bb2/6 Bb2/4", 38: "C3/6 C3/6 C3/4", 39: "D3/2 D3/2 D3/2 D3/2 D3/2 D3/2 D3/2 D3/2",
40: "D3/4 D3+A3/4 D3/4 r/4",
41: "Bb2/2 r/4 D3+A3/4 r/2 D3+A3/4", 42: "Bb2/2 E3+C4/4 E3+C4/2 Bb3/2 G4/2 E4/2 C4/2",
43: "A2/2 E3+C4/4 E3+C4/2 A2/2 E3+C4/4 A2/2", 44: "D3/4 F3+C4/4 D3/2 C3/2 Bb2/2 A2/2",
45: "G2/2 D3/2 G3/2 Bb3/2 F4/2 Bb3/4 E2/2", 46: "A2+E3/6 A2+E3/6 r/2 A2/2",
47: "D3/4 A3/4 E4/4 r/4", 48: "D3+C4/8 C3/8",
49: "Bb2/8 r/8", 50: "r/16", 51: "Bb2/16~", 52: "Bb2/16!",
}
CB = {b: "r/16" for b in range(1, 8)}
CB.update({
8: "D2/4 r/4 D2/4 C2/4", 9: "Bb1/16", 10: "Bb1/16", 11: "A1/16", 12: "D2/4 r/4 D2/4 C2/4",
13: "Bb1/6 Bb1/6 Bb1/4", 14: "Bb1/6 Bb1/6 Bb1/4", 15: "A1/6 A1/6 A1/4",
16: "D2/4 r/4 D2/2 C2/2 Bb1/2 A1/2",
17: "G1/16", 18: "C2/16", 19: "F1/16", 20: "Bb1/16", 21: "E2/12 r/2 E2/2", 22: "A1/16",
23: "D2/12 A1/4", 24: "D2/4 r/4 D2/2 C2/2 Bb1/2 A1/2",
25: "G1/16", 26: "C2/16", 27: "F1/16", 28: "Bb1/12 Bb1/4", 29: "E1/12 E1/4", 30: "A1/12 A1/4",
31: "D2/12 r/4", 32: "D2/8 C2/8",
33: "Bb1/2 r/4 Bb1/2 r/4 Bb1/2 r/2", 34: "C2/2 r/4 C2/2 r/4 C2/2 r/2",
35: "D2/2 r/4 D2/2 r/4 D2/2 r/2", 36: "D2/4 r/4 D2/4 C2/4",
37: "Bb1/6 Bb1/6 Bb1/4", 38: "C2/6 C2/6 C2/4", 39: "D2/6 D2/6 D2/4", 40: "D2/4 D2/4 D2/4 r/4",
41: "Bb1/6 Bb1/6 Bb1/4", 42: "Bb1/6 Bb1/6 Bb1/4", 43: "A1/6 A1/6 A1/4",
44: "D2/8 D2/2 C2/2 Bb1/2 A1/2", 45: "G1/14 E1/2", 46: "A1/6 A1/6 r/2 A1/2",
47: "D2/12 r/4", 48: "D2/8 C2/8", 49: "Bb1/8 r/8", 50: "r/16", 51: "Bb1/16~", 52: "Bb1/16!",
})
MELODY = {}
for b in range(1, 53):
    MELODY[b] = [("vn1", 0)]
for b in (13, 14, 15, 16, 25, 26, 27, 28, 29, 30, 37, 38, 39, 41, 42, 43, 44):
    MELODY[b] = [("vn1", 0), ("vn2", -12)]
for b in (33, 34, 35):
    MELODY[b] = [("vn2", 0)]
MELODY[45] = [("vn1", 0), ("vn2", -12), ("va", -24)]
MELODY_FREE = {36: "A5 held over from b.35 in Vln I (sky pedal)"}
# Only the chart's own b9 colours (PLAN.md §6.4). Nothing else may be added.
CLASH_ALLOW = {
    (18, "vn2", "vc"): "Db6 over the C bass: the chart's C7(b9) / borrowed Bbm6 over C",
    (18, "vn2", "cb"): "Db6 over the C bass: the chart's C7(b9) / borrowed Bbm6 over C",
    (22, "vn1", "cb"): "melody Bb5 over the A bass: the chart's A7(b9)",
    (24, "vn2", "vc"): "Eb5 over the D bass: the chart's D7(b9)",
    (24, "vn2", "cb"): "Eb5 over the D bass: the chart's D7(b9)",
    (26, "va", "vc"): "Db5 over the C bass: the chart's C7(b9) (borrowed iv now in the viola)",
    (26, "va", "cb"): "Db5 over the C bass: the chart's C7(b9) (borrowed iv now in the viola)",
    (27, "vn1", "vc"): "Bb6 appoggiatura against the chart's LH arpeggio A3 (pos 4-6)",
    (27, "vn2", "vc"): "Bb5 appoggiatura against the chart's LH arpeggio A3 (pos 4-6)",
    (46, "vn1", "vc"): "melody Bb5 over the A bass: the chart's A7(b9)",
    (46, "vn1", "cb"): "melody Bb5 over the A bass: the chart's A7(b9)",
    (46, "va", "vc"): "Bb4 over the A bass: the chart's A7(b9) (its RH Bb4)",
    (46, "va", "cb"): "Bb4 over the A bass: the chart's A7(b9) (its RH Bb4)",
}
DOUBLINGS = [("vn1", "vn2", 13, 16), ("vn1", "vn2", 21, 21), ("vn1", "vn2", 25, 30),
             ("vn1", "vn2", 37, 39), ("vn1", "vn2", 41, 45), ("vn2", "va", 45, 45),
             ("vn1", "va", 45, 45), ("vc", "cb", 8, 52)]
