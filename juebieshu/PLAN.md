# 诀别书 · 弦乐五重奏 编配总方案
## A Letter of Farewell, for String Quintet: the lead arranger's plan

Scope: all 52 bars, the original key (one flat: F major / D minor), 4/4, ♩ = 112. Strings only: Violin I, Violin II, Viola, Violoncello, Contrabass. The deliverable is a film-score / Juilliard-standard score plus MIDI that is rendered in ACE Studio (String Section; speakers Violins I / Violins II / Violas / Celli / Basses).

**Base and grafts.** The base is the concept "film". Grafted onto it:
- from "variety": clash hygiene, the Vln I sky pedal and pickup, the launch-walk cue, and the check setup;
- from "chamber": the viola guide-tone lament, two-string bariolage for every 16th drive, and the chart's own block left hand in b.28–30 and b.41–43.

The fixes both judges asked for are applied. Section 8 records every decision.

**Checked in code.** Every pitch this plan names is written out bar by bar in **`juebieshu/plan/00_skeleton.py`**. Run through `build.py --check` with the verified transcription (`transcription/piano.json`, all eight `cN_final.json` chunks merged), that skeleton gives **zero** RANGE / STOP / CLASH / PARALLEL / MELODY / BASS findings. It is the pitch contract. The writers turn it into music: phrasing, articulation, dynamics and the figures described below.

> **OVERRIDE from the lead (after the panel) — NO PIZZICATO.** The user imports the MIDI into ACE Studio, where pizzicato must be switched by hand. So the Contrabass in b.33–36 plays the same rhythm **arco, short** (`*` staccato tokens, text *secco* at 33, no "pizz."/"arco" words). Everywhere below where the plan says "pizz." for the Cb, read "arco secco". The only manual ACE step left is none.

Notation used in this plan:
- Pitches are **sounding** pitches. The Cb is written an octave higher in the score; build.py does this.
- Durations: w = whole, dh = dotted half, h = half, dq = dotted quarter, q = quarter, 8 = eighth, 16 = sixteenth. "pos" is the 16th position in the bar, from 0 to 15.
- **3+3+2** means attacks on beat 1, the "and" of 2, and beat 4 (dq, dq, q). **3+(3~2)** means a dq, then a dq tied into a q, so the attacks fall on 1 and 2& only.
- **Pulse** is the chart's off-beat left-hand figure: 8th rest, q, 8th, 8th rest, q, 8th, with attacks on 1&, 2&, 3& and 4&.
- **Bariolage X–Y** means 16ths alternating X and Y on two adjacent strings, X first.
- ★ marks a deliberate departure from the chart; all of them are listed in §6.8.

---

## 1. 全曲弧线与排练号 · Arc and rehearsal letters

**The arc.** A farewell letter that begins with one voice writing alone and ends on a chord that is never answered.

The piece opens with Vln I stating the chart's two-beat motto (D–A–G–A) over a hushed pad with no bass. The pad moves only in the motto's rests, each time with a small sus4→3 sigh. The strings then add layers one at a time:
- the chart's off-beat pulse (b.5);
- the Contrabass, at the first cadence (b.8);
- flowing 8th broken chords under the continuous theme (b.9);
- violins in octaves (b.13).

A walking launch figure (D–C–B♭–A in bass octaves) throws the music into Chorus I (b.17). There a three-voice string choir sings the chart's syncopated block chords over the chart's own cello arpeggios, and a hidden viola lament (F–E–E–D–D–C♯–C–C) sinks through the circle of fifths.

Chorus II (b.25) doubles the tune in octaves. A 16th-note viola riser (b.26, beats 3–4) lifts it to the summit of the body of the piece: B♭6 falling to A6 over C–E (b.27). Then everything drains to one bare D.

Section D (b.33) resets to a heartbeat: pizzicato basses, a light 3+3+2 tresillo, and the chart's ostinato in Vln II. It rebuilds bar by bar: a sky pedal, then arco and 8va octaves, then a climbing viola bariolage, then the cello chug. At bar 40 the whole ensemble hammers three beats and then **stops for one beat**.

The biggest climax, E (b.41), lands on the next downbeat with the fullest texture of the piece, and **an octave higher** than the chart (Vln I at 8va, Vln II at pitch, as in 37–39), so it opens above Chorus II's summit. A third launch walk (b.44) pushes it to its crest (b.45–46, fff, allargando): the melody in three octaves over the chart's G-minor sweep, then an A7(♭9) hammered in 3+3+2. It then releases into Dm9 (Largamente) and the chart's rit.

In the coda the motto returns **one octave above** the intro, pp. The piece ends on bar 2's Lydian C/B♭ with C7 alone on top: IV with its 9th, never resolved to F.

**Threads that hold the piece together**
1. The bass sinks an octave per phrase in the intro: B♭3 (b.1) → B♭2 (b.5) → B♭1 (b.9). This is in the chart.
2. The chart's 3+3+2 rhythm: b.13–15 bass, the chorus choir b.17–30, the heartbeat b.33–40, the reprise bass b.41–43, and the hammer at b.46.
3. The launch walk D–C–B♭–A → G in bass octaves: b.16 and b.24 (both in the chart) and b.44 (★ added).
4. The sus4→3 sigh placed in a gap: b.2, 3, 6, 7 and 8 (pad), then b.27 (the summit appoggiatura).
5. The chromatic inner line D→D♭→C in the viola (b.25→26→27), which carries on the lament of b.17–24.

**Layer ladder (长音 → 八分 → 十六分, then reset and rebuild)**

| Bar | What is added |
|---|---|
| 1 | Vln I motto over a pp pad (Vln II, Vla, Vc); long notes only |
| 5 | Chart's off-beat pulse (Vln II + Vla); Vc drops to B♭2 |
| 8 | Contrabass enters (first cadence) |
| 9 | Continuous theme; Vla 8th broken chords; Cb floor on B♭1 |
| 13 | Violins in octaves; bass in 3+3+2 |
| 16 | Launch walk #1 + Vla 16th run |
| 17 | Chorus choir 3+(3~2) + Vc arpeggio + Vla lament |
| 25 | Chorus in octaves |
| 26, beat 3 | 16th drive begins (Vla bariolage): riser to the summit at 27 |
| 33 | Reset: Vln I out, Cb pizz, light tresillo |
| 35 | Vln I sky pedal (from niente) |
| 37 | Arco, octaves at the chart's 8va, 16th drive returns (Vla climbing bariolage) |
| 39 | Vc 8th chug (last layer) |
| 40, beat 4 | **G.P.**: one beat of silence |
| 41 | Fullest tutti (the biggest climax lands) |
| 44, beats 3–4 | Launch walk #3 |
| 45–46 | Crest: melody in three octaves, fff, allargando; A7(♭9) hammer |
| 47–48 | Release: Largamente, rit. |
| 49 | Coda: high line, sparse chord, the floor falls away |

**Rehearsal letters.** Letters are boxed. The score prints the letter plus the English and Chinese names. The subtitle is for the README and the writers.

| Bar | Letter | English (score) | 中文（总谱） | Subtitle |
|---|---|---|---|---|
| 1 | — | Intro | 前奏 | the letter opens · 信笺展开 |
| 9 | **A** | Theme | 主题 | the letter is read · 读信 |
| 17 | **B** | Chorus I | 副歌 · 一 | circle of fifths · 五度循环 |
| 25 | **C** | Chorus II | 副歌 · 二 | the summit · 顶点 |
| 33 | **D** | Interlude | 间奏 | heartbeat · 心跳 |
| 41 | **E** | Reprise | 再现 | grandioso, the biggest climax · 全曲高潮 |
| 49 | **F** | Coda | 尾声 | the unanswered letter · 未寄出的回信 |

---

## 2. 速度图 · Tempo map

The body of the piece stays strictly in tempo; the momentum is part of the style. There is no rit. at 8, 16 or 24. **The G.P. at 40, beat 4 is in tempo** as well: one silent beat at ♩ = 112 (≈ 0.54 s), with no fermata, no caesura and no tempo trick.

| Where | Printed | MIDI ♩ |
|---|---|---|
| b.1 | **Moderato con moto** ♩ = 112 | 112 |
| b.32, beats 3–4 | *poco rit.* | 108 (b.32 beat 3), 104 (beat 4) |
| b.33 | *a tempo* | 112 |
| b.40, beat 4 | **G.P.** (text over the rest in every part) | 112, unchanged |
| b.41 | **Grandioso** | 112 |
| b.45 | *allargando* | 108, then 104 from beat 3 |
| b.46 | *molto allarg.* | 100, then 96 from beat 3 |
| b.47 | **Largamente** ♩ = 92 | 92 |
| b.48 | *rit.* (the chart's own) | 88 → 82 (beat 3) → 76 (beat 4) |
| b.49 | **Meno mosso, dolce** ♩ = 88 | 88 |
| b.51 | *rit.* | 84 → 78 (beat 3) |
| b.52 | 𝄐 on the final whole note in all five parts | 72 on beats 1–2, 40 on beats 3–4, so the chord lasts ≈ 4.7 s before the ACE release |

The total length is about 1′58″ plus the release, so ≈ 2′00″.

FORM block, ready to paste into `build.py`:

```python
REHEARSAL = {9: ("A", "Theme", "主题"), 17: ("B", "Chorus I", "副歌 · 一"),
             25: ("C", "Chorus II", "副歌 · 二"), 33: ("D", "Interlude", "间奏"),
             41: ("E", "Reprise", "再现"), 49: ("F", "Coda", "尾声")}
INTRO_TITLE = ("Intro", "前奏")
TEMPO_MARK = ("Moderato con moto", 112)
TEMPI = [(1, 0, 112), (32, 8, 108), (32, 12, 104), (33, 0, 112),
         (45, 0, 108), (45, 8, 104), (46, 0, 100), (46, 8, 96), (47, 0, 92),
         (48, 0, 88), (48, 8, 82), (48, 12, 76), (49, 0, 88), (51, 0, 84),
         (51, 8, 78), (52, 0, 72), (52, 8, 40)]
TEMPO_TEXT = [(32, 8, "poco rit.", None), (33, 0, "a tempo", None),
              (41, 0, "Grandioso", None), (45, 0, "allargando", None),
              (46, 0, "molto allarg.", None), (47, 0, "Largamente", 92),
              (48, 0, "rit.", None), (49, 0, "Meno mosso, dolce", 88),
              (51, 0, "rit.", None)]
GP_NOTE = ("第 40 小节第 4 拍五条轨同时休止一拍（G.P. 全体休止），是有意留的呼吸，"
           "下一小节全奏落地，不要补音。")
```

---

## 3. 逐小节总表 · Bar-by-bar table

In each table, **Chart** is the chart's harmony for each half bar, and **Strings** is what the strings actually voice. The melody is at the chart's sounding pitch unless the table says otherwise. The dynamics column gives the main marking; the hairpins are listed per section in the notes below each table.

### Intro · 前奏 (b.1–8)

| Bar | Chart | Strings | Melody | Vln I | Vln II | Vla | Vc | Cb | Dyn |
|---|---|---|---|---|---|---|---|---|---|
| 1 | B♭maj7 · B♭maj7 | B♭maj7 (pad F–A over B♭) | Vln I | motto D5 A5 G5 A5 (8,16,16,8), then rests | pad A4 w | pad F4 w | B♭3 w (chart octave) | tacet | Vln I *p espr.*; pad *pp* (n<) |
| 2 | C/B♭ · C/B♭ | Csus4/B♭ → C/B♭ (F→E on beat 3, in the gap) | Vln I | C5 G5 F5 G5 | G4 h → C5 h~ (into 3) | F4 h → E4 h | B♭3 w | — | pad < > on beats 3–4 |
| 3 | Am7 · Am7 | Am7(11) → Am7 (D→E on beat 3) | Vln I | C5 G5 F5 G5 | C5 w | D4 h → E4 h | A3 w | — | same |
| 4 | Dm7 · Dm7 (C on beat 4) | Dm7 · Dm7/C | Vln I | C6 F5 E5 F5 | A4 w | F4 w | D3 dh, C3 q | — | *poco* < |
| 5 | B♭maj7 | B♭maj7 | Vln I | D5 A5 G5 A5 | **pulse** A4 | **pulse** F4 | B♭2 q on beats 1 and 3 (ten.), octave drop | — | *p*; pulse *p leggiero* |
| 6 | C/B♭ | Csus4/B♭ → C/B♭ | Vln I | D6 G5 F5 G5 | pulse G4+C5 | pulse F4 (1&, 2&) → E4 (3&, 4&) | B♭2 q, beats 1 and 3 | — | |
| 7 | Am7 | Am7(11) → Am7 | Vln I | E6 G5 F5 G5 | pulse G4+C5, no 4& hit | pulse D4 (1&, 2&) → E4 (3&), no 4& | A2 q (beat 1), A2 q (beat 3), A2 8 on 4& (chart pickup) | — | *poco cresc.* |
| 8 | Dm7 · Dm7 (C on 4) | Dm(sus4) → Dm7 · Dm7/C | Vln I top; Vln II the chart's lower sixth | F6 E6 D6 (8, 8, dh) | A5 G5 F5 (8, 8, dh) | G4 h → F4 h (4→3) | D3 q, D3+A3 q, D3 q, C3 q | **enters** D2 q, r, D2 q, C2 q | *mp*; violins < beats 1–2, > to *p* by beat 4; Cb *pp*<*mp* |

Notes:
- The motto is slurred over its first three notes, with tenuto on the fourth, and then lifted.
- The pad only moves (swell, or step 4→3) while the motto rests. **No E may sound on beats 1–2 of bars 2, 3, 6 and 7**, because the motto passes F5 there.
- In 1–4 Vln II and Vla play single long notes only (no double stops). The *rhythmic* layer, the pulse, arrives at b.5 on the same two instruments.

### A · Theme · 主题 (b.9–16)

| Bar | Chart | Strings | Melody | Vln I | Vln II | Vla | Vc | Cb | Dyn |
|---|---|---|---|---|---|---|---|---|---|
| 9 | B♭maj7 | B♭maj9 (C5 in Vln II) | Vln I | theme, legato; 8ths slurred in pairs, 16th turns in fours | C5 w | broken 8ths F3 B♭3 D4 A4 ×2 (4-note slurs) | B♭2 w | B♭1 w (the floor) | Vln I *mp espr.*; accompaniment *p* |
| 10 | C/B♭ | C/B♭ (E5 in Vln II) | Vln I | A5 G5 A5 G5 A5 G5, C5 h at full value | E5 h → G4 h | beats 1–2 G3 C4 E4 G4; beats 3–4 the **chart's staccato fill** B♭3 G4 E4 C4 (spicc.) under the held C5 | B♭2 w | B♭1 w | |
| 11 | Am7 | Am7, **no E on beats 1–2** | Vln I | C5 G5 F5 G5 F5 G5 C6 C6 G5 | A4 h → E5 h | A3 C4 G4 C4 · A3 E4 G4 C4 | A2 w | A1 w | |
| 12 | Dm7 · Dm7/C | Dm7 · Dm7/C | Vln I | G5 A5 G5 A5 G5 E5, F5 h | D5 h → **motto answer** F4 C5 B♭4 C5 (8,16,16,8) + 8 rest, *p*, under the held F5 | D4 F4 A4 F4, D4 q, F4 q (**no A** while Vln II's B♭4 sounds, pos 11) | D3 q, D3+A3 q, D3 q, C3 q | D2 q, r, D2 q, C2 q | |
| 13 | B♭maj7 | B♭maj7 | **Vln I + Vln II 8vb** (first octave doubling) | theme | melody 8vb (D4–D5), same bowing | broken 8ths moved down into C3–D4 (e.g. F3 B♭3 D4 B♭3 D3 F3 A3 D4) | 3+3+2 on B♭2, ten. ★ | 3+3+2 on B♭1 | *mf* |
| 14 | C/B♭ | C/B♭ | 8ves | A5 G5 …, C5 h | … C4 h | G3 C4 E4 C4 + the staccato fill B♭3 G4 E4 C4 (no C3 over the B♭ bass) | 3+3+2 B♭2 | 3+3+2 B♭1 | |
| 15 | Am7 | Am7, **no E on beats 1–2** | 8ves | … C6 C6 E6 | … C5 C5 E5 | A3 C4 G3 C4 · A3 E3 G3 C4 | 3+3+2 A2 (beat 4 = the chart's pickup) | 3+3+2 A1 | *cresc. poco a poco* |
| 16 | Dm7 · walk D–C–B♭–A | Dm7 · Dm – Dm/C – B♭maj7 – Dm/A (passing) → Gm7 | 8ves to the barline | D6 E6 D6 E6 D6 C6 D6 A5 D6 E6 | 8vb D5 E5 D5 E5 D5 C5 D5 A4 D5 E5 | beats 1–2 D3 F3 A3 F3; beats 3–4 16th run **A3 B♭3 C4 D4 E4 F4 G4 A4** → B♭3+F4 at 17 | D3 q, D3+A3 q, **walk** D3 C3 B♭2 A2 (8ths, marcato) | D2 q, r q, **walk** D2 C2 B♭1 A1 | *cresc. molto* → **f**; **LAUNCH CUE 1** |

Notes:
- Counter-lines appear **only** under the melody's half notes: the Vla fill in 10 and 14, and the Vln II answer in 12.
- In 13–16 the Vla must not shadow the melody's contour in octaves. The skeleton orders the notes to avoid this.
- In 16 the Vla run lands on B♭3+F4 while the melody goes E6→F6 (contrary motion). Its last note is A4, not E4.

### B · Chorus I · 副歌 · 一 (b.17–24)

| Bar | Chart | Strings | Melody | Vln I | Vln II | Vla (guide tones, div.) | Vc (chart LH) | Cb | Dyn |
|---|---|---|---|---|---|---|---|---|---|
| 17 | Gm7 | Gm7 | Vln I | F6 held 10 16ths, then D6 E6 F6; *largamente*, full bows | F5+B♭5 w (div.) | B♭3+F4 w | G2 q > (the walk lands, as in 25), B♭3 D4 F4 **B♭3 D4** G2 (★ two notes swapped against a parallel octave with the melody) | G1 w > | **f** |
| 18 | C7(♭9,13) | C7(♭9,13) = B♭m6/C, **no F in the upper strings** | Vln I | A6 dq, G6 dq~q | **D♭6** dq, D♭6 dq~q, *espr.* (the colour note) | B♭3+E4 w | C3 q, E3 G3 B♭3 G3 E3 C3 | C2 w | *f* < > |
| 19 | Fmaj7 | Fmaj7 | Vln I | E6 dq, C6 dq~q | C6 dq, A5 dq~q | A3+E4 w | F2 F3 A3 C4 E4 C4 A3 F2 | F1 w | *f* |
| 20 | B♭maj7 · B♭maj7(13) | B♭maj7(13) | Vln I | A5 dq, G5 dq~q | D5 dq, D5 dq~q | **D4+A4** w (open strings; never A3, which sits a semitone under the Vc's B♭3) | B♭2 B♭3 D4 F4 A4 F4 D4 B♭2 | B♭1 w | *f*, *poco dim.* |
| 21 | Em7♭5 | Em7♭5 (A–B♭ passing octaves on beat 4) | Vln I (+ Vln II 8vb on beat 4) | B♭5 dh, A5 B♭5 (8ths) | D5+G5 dh, A4 B♭4 (8ths) | D4+G4 w | E3 dq, E3+B♭3 dq, r 8, E3 8 | E2 dh, r 8, E2 8 (pickup) | *mf, poco meno* (the saddest bar) |
| 22 | A7(♯9) · A7(♭9) | A7(♯9→♭9) | Vln I | C6 B♭5 A5 (3+3+2) | C♯5+E5 3+3+2 | C♯4+G4 w | A2 q, C♯3 E3 G3 E3 C♯3 A2 | A1 w | *cresc.* → *f* |
| 23 | Dm7(11) · Dm7 | Dm7(11) | Vln I | G5 F5 G5 (3+3+2) | C5 3+3+2 | C4+F4 w | D3 dq, D3+A3 dq, A2 q | D2 dh, A1 q | *subito mf* (a breath) |
| 24 | D7(♭9) | D7(♭9) = V/ii | Vln I | A5 F♯5 G5 A5 (q) | **E♭5** q q q (re-struck with the chart's chords), F♯5 q | C4+A4 w (**no F♯ in the Vla**: the Vc's F♯3 has it, and none may sit under the melody's G5, beat 3) | D3 q, F♯3+C4 q, **walk** D3 C3 B♭2 A2 | D2 h (holds D under beat 2), **walk** D2 C2 B♭1 A1 | *cresc. molto* → **ff**; **LAUNCH CUE 2** |

Notes:
- The violins sing the chart's right hand as a choir, in the chart's rhythm. Ties are one merged note, never re-attacked.
- The viola lament is the textbook guide-tone chain of the circle of fifths. Read as dyads: (B♭3,F4) (B♭3,E4) (A3,E4) (D4,A4) (D4,G4) (C♯4,G4) (C4,F4) (C4,F♯4→A4). The falling line F4–E4–E4–D4–D4–C♯4–C4–C4 must be audible: *mf* legato, one bow per bar.
- The Vc arpeggio is *mf cantabile*. Its apex notes sing inside the melody's tied notes.
- **18 is the signature moment.** Vln II's D♭6 is the loudest inner note, marked *espr.* with tenuto.

### C · Chorus II · 副歌 · 二 (b.25–32)

| Bar | Chart | Strings | Melody | Vln I | Vln II | Vla | Vc | Cb | Dyn |
|---|---|---|---|---|---|---|---|---|---|
| 25 | Gm7 | Gm7 | **Vln I + Vln II 8vb** | as 17 | F5 (10 16ths), D5 E5 F5 | B♭4+D5 w | as 17 (same swap) | G1 w | **ff** |
| 26 | C7(♭9,13) | as 18; the **D♭ moves to the Vla** (D5→D♭5, chromatic) | 8ves | A6 dq, G6 dq~q | A5 dq, G5 dq~q | B♭4+D♭5 dq, B♭4+D♭5 8, then **bariolage B♭4–D♭5** on beats 3–4 (the riser) | as 18, *cresc.* | C2 w, *cresc.* | *ff*; beats 3–4 *cresc. molto* (no subito p) |
| 27 | Fmaj7(11) (= C7/F) → Fmaj7 | 4–3: **B♭6 → A6** over C–E | 8ves; Vln I = the chart's 8va | **B♭6** dq, A6 dq~q: THE SUMMIT, highest note of the body | B♭5 dq, A5 dq~q | bariolage C5–E4 (pos 0–5; E4 is the chart's tritone under the B♭), then **C5–A4** (pos 6–15, upper note first): the A arrives with the resolution | F2 F3 A3 C4 E4 C4 A3 F3 (chart; its A3 at pos 4 is the chart's own rub, allowed) | F1 w | ***ff con tutta forza*** |
| 28 | B♭maj7(13) · B♭maj7 | same (G→F) | 8ves | G6 dq, F6 dq~q | G5, F5 | bariolage A4–D5 | **chart's block LH:** B♭2 dq, D3+A3 dq, B♭2 q | B♭1 dh + B♭1 q | *ff* |
| 29 | Em7♭5 | Em7♭5 | 8ves | A6 G6 (8ths), 8 rest, D6 dq~q | A5 G5, rest, D5 | bariolage B♭4–D5 (keeps moving through the violins' 8th rest) | E2 dq, G3+D4 dq, E2 q | E1 dh + E1 q (open E) | *f* |
| 30 | (chart: A7(♭9)) | **A7(♭13)** (F→E over A) | 8ves | F6 E6, rest, A5 dq~q | F5 E5, rest, A4 | bariolage **C♯4–G4** (no E while F sounds; below Vln II's A4) | A2 dq, E3+C♯4 dq, A2 q | A1 dh + A1 q | *f*, *dim.* from beat 3 |
| 31 | Dm9 | Dm9 | Vln I (the chart's 8va ends before beat 4) | E6 dh → E5 q | A5+C6 dh (div.) → A4 q | F3+C4 dh → F4 q (**no F at F4 or above while the Vc's E4 sounds**, beat 3) | D3 A3 E4 (q), rest | D2 dh, rest | *mf dim.* |
| 32 | Dm7 · Dm7/C | Dm7 → Dm7/C, **third kept** | Vln I | D5 w, A string, *dolce* | A4 w | F4 w | D3 (+C4, the chart's 7th) h → C3 h | D2 h → C2 h | *p*, *poco rit.* beats 3–4 |

Notes:
- The octave doubling is the "lift". Vln II copies Vln I's slurs and ties exactly.
- The 8th rests in 29–30 are real breaths in the violins; only the viola 16ths continue through them.
- The bariolage phase is chosen against the Vc arpeggio (27, upper note first). If `--check` reports a PARALLEL between Vla and Vc, flip the phase; do not add a DOUBLINGS entry.

### D · Interlude · 间奏 (b.33–40)

| Bar | Chart | Strings | Melody | Vln I | Vln II | Vla | Vc | Cb | Dyn |
|---|---|---|---|---|---|---|---|---|---|
| 33 | B♭maj7(♯11) | same | **Vln II**, chart pitch | tacet (its first real rest) | ostinato E5 D5 A4 E5 D5 A4 D5 E5 (8ths, accents on 1, 2&, 4; optional open-string A4 double stop under the accented notes) | F3+A3 3+3+2, ten. | B♭2 short 8ths on 1, 2&, 4 (arco, leggiero, `*`) | **pizz.** B♭1 on 1, 2&, 4 | Vln II *mp leggiero*; others *p* |
| 34 | Fmaj7/C | same | Vln II | tacet | F5 E5 A4 F5 E5 A4 E5 F5 | A3+C4 3+3+2 | C3 as 33 | pizz. C2 | |
| 35 | Dm11 | same | Vln II | **sky pedal** A5 from niente, tied into 36 | G5 F5 A4 G5 F5 A4 F5 G5 | A3+C4 3+3+2 | D3 as 33 | pizz. D2 | Vln I *pp* <; others *poco cresc.* |
| 36 | Dm7 · Dm7 (C on 4) | Dm7 → Dm7/C | Vln I (the held A5; MELODY_FREE) | A5 held to beat 4; beat 4 16th **pickup A5 B♭5 C6 D6** → 37 | F5 dh, **rest on beat 4** | A4+C5 dh, **rest on beat 4** (nothing may rub against the pickup's B♭5) | D3 q, D3+A3 q, D3 q, C3 q | pizz. D2 q, r, D2 q, C2 q | *mp* < *mf* |
| 37 | B♭maj7(♯11) | same | **Vln I (chart's 8va) + Vln II (chart's written pitch)** | ostinato E6 D6 A5 … (détaché 8ths, accents on the 3+3+2 notes) | ostinato E5 D5 A4 … | **bariolage B♭3–D4** (accents on 1, 2&, 4) | **arco**: 3+3+2 marcato B♭2 (dq, dq, q) | **arco**: 3+3+2 marcato B♭1 | *mf* |
| 38 | Fmaj7/C | same | 8ves | F6 E6 A5 … | F5 E5 A4 … | bariolage A3–F4 | 3+3+2 C3 | 3+3+2 C2 | *f* |
| 39 | Dm11 · Dm7 | same | 8ves | G6 F6 A5 G6 F6 A5 F6 E6 | G5 F5 A4 G5 F5 A4 F5 E5 | bariolage D4–C5 (the chart's Dm11 C) | **8th chug** D3 ×8, accents 1, 2&, 4 (the last layer) | 3+3+2 D2 | *cresc. molto* |
| 40 | D5 (no 3rd, as chart) · **G.P.** | same | Vln I | D6 dh, **rest** | A5 dh, **rest** | bariolage A4–D5 on beats 1–3, **rest** | D3 q, D3+A3 q, D3 q (marcato), **rest** | D2 q q q (marcato), **rest** ★ (chart's C on beat 4 dropped) | ***f*** < through beats 1–3 into the G.P., ***ff*** at 41; **beat 4 G.P.** |

Notes:
- The ostinato's top note climbs E5 → F5 → G5 across 33–35 and reaches A5 in 36; phrase it so that this rise is heard. The viola bariolage in 37–40 repeats the climb on its upper notes: D4 → F4 → C5 → D5.
- Vln I's 8ths in 37–39 are *non legato*, never slurred across the 3+3+2 groups, so that ACE picks détaché or spiccato.

### E · Reprise · 再现 (b.41–48): the biggest climax

E is one continuous climax. It **lands** at 41 (ff, fullest texture, straight after the G.P.) and **crests** at 45–46 (fff, allargando). 41 must feel like an arrival and 45 like the last push. 45 does not introduce a new texture; it broadens the one already there.

| Bar | Chart | Strings | Melody | Vln I | Vln II | Vla | Vc | Cb | Dyn |
|---|---|---|---|---|---|---|---|---|---|
| 41 | B♭maj7 | B♭maj7 | **Vln I (chart's 8va) + Vln II (chart's pitch)** | A6 D7 D7 D7 A6 A6 A6 F6 F6 F6 A6 (8, then 16-16-8 ×3, then 8): accented 8ths, lighter 16ths | A5 D6 D6 D6 A5 … (A5–D6) | **bariolage D4–F4** (below Vln II; not B♭3, which would rub against the Vc's A3) | **chart's LH strokes:** B♭2+F3 8 (>), rest, D3+A3 q on 2&, rest, D3+A3 q on 4 | 3+3+2 B♭1, marcato | **ff** tutti (*Grandioso*) |
| 42 | C/B♭ | C9/B♭ (F♯5 = chromatic lower neighbour, melody only) | 8ves | A6 G6 G6 G6 F♯6, G6 h (swell) | A5 G5 G5 G5 F♯5, G5 h | bariolage E4–C4 (E first) on beats 1–2, **rest** on beats 3–4 (the Vc fill) | B♭2 8, E3+C4 q, E3+C4 8, then the **chart's fill** B♭3 G4 E4 C4 (marcato) inside the held G5 | 3+3+2 B♭1 | *ff* |
| 43 | Am7 | Am7 | 8ves | G6 C7 C7 C7 G6 G6 G6 E6 E6 E6 G6 | G5 C6 … (chart pitch) | bariolage E4–A3 (E first) | chart pulse: A2 8, E3+C4 q, E3+C4 8, A2 8, E3+C4 q, A2 8 | 3+3+2 A1 | *ff* |
| 44 | Dm7 · Dm7 | Dm7 · ★ walk Dm – Dm/C – B♭maj7 – Dm/A → Gm | 8ves | G6 F6 F6 F6 E6, F6 h | G5 F5 F5 F5 E5, F5 h | bariolage A3–D4, *cresc. molto* | D3 q, F3+C4 q, **walk** D3 C3 B♭2 A2 | D2 h, **walk** D2 C2 B♭1 A1 | *cresc. molto*; **LAUNCH CUE 3** (★ added) |
| 45 | Gm7(11) · Gm7 (E bass on 4&) | Gm7(11) | **melody in three octaves**: Vln I (chart's 8va), Vln II (chart's pitch), Vla 8vb of Vln II | C7 B♭6 F6 C7 B♭6 (8, 8, 8, q, dq), *largamente* | F5+C6 B♭5 F5 C6 B♭5 | C5 B♭4 F4 C5 B♭4 | **the chart's sweep** G2 D3 G3 B♭3 F4 (8ths), B♭3 q, E2 8 | G1 to 4&, then E1 8 | ***fff***, *allargando* |
| 46 | A7(♭9) | A7(♭9) | Vln I | B♭6 dq ^, A6 dq ^, E6 q (the 8va ends here; 47 *loco*) | E5+C♯6 dq, dq, **rest** | G4+B♭4 dq, dq, **rest** | A2+E3 dq, dq, r 8, A2 8 | A1 dq, dq, r 8, A1 8 | *fff*, *molto allarg.*; beat 4 thins (catch-breath) |
| 47 | Dm9 | Dm9 | Vln I | **E5** dh, E5 q (the chart's octave, not E6) | C5 dh, A4 q | F3+C4 dh, F4 q | D3 A3 E4 (q), rest | D2 dh, rest | **Largamente**; *f* > |
| 48 | Dm7 · Dm7/C | Dm7 → Dm7/C, **third kept** | Vln I | D5 w | A4 w | F4 w | D3 (+C4) h → C3 h, ten. | D2 h → C2 h | *p* → *pp*, *rit.* |

Notes:
- The chart's rolled chords (45, and 51 in the coda) are **not** imitated with grace notes or spreads; they become clean tutti downbeats.
- The unison C on the downbeat of 45 is a sus4 "cry". The Vc sweep supplies the Gm7(11) harmony inside the bar. Vln II adds the F under its downbeat C (F5+C6, *non div.*).

### F · Coda · 尾声 (b.49–52)

| Bar | Chart | Strings | Melody | Vln I | Vln II | Vla | Vc | Cb | Dyn |
|---|---|---|---|---|---|---|---|---|---|
| 49 | B♭maj7 | B♭maj7 (the chart's voicing B♭4 D5 F5 A5) | Vln I, chart's 8va (motto one octave above b.1) | D6 q, A6 8, G6 8, A6 q, G6 q; legato | rest h, F5+A5 h (div.) | rest h, B♭4+D5 h | B♭2 h, rest | B♭1 h, rest | *pp dolce, lontano* |
| 50 | B♭maj7 | B♭maj7 | Vln I | A6 **D7** A6 G6 (q). D7 is the top note of the arrangement: a soft < >, no accent | rest q, F5+A5 h, F5+A5 q | B♭4 q, D5 h, **B♭4** q (not D5, which would make parallel fifths into 51) | tacet | tacet | *pp* |
| 51 | C/B♭ | C/B♭ (bar 2's Lydian chord returns) | Vln I | A6 G6 A6 G6 (8ths), A6 q, G6 q (the rolled chord is not replayed) | E5+G5 w~ (div.) | B♭4+C5 w~ (div.; the chart's own B♭–C rub) | B♭2 w~ *ppp dal niente* | B♭1 w~ *ppp* | *pp*, *rit.* |
| 52 | C/B♭ (C7 on top) | C/B♭ | Vln I | **C7** w 𝄐, *al niente*; releases last | E5+G5 w 𝄐 | B♭4+C5 w 𝄐 | B♭2 w 𝄐 | B♭1 w 𝄐 | → *niente* |

Final spacing: B♭1 · B♭2 · B♭4 C5 E5 G5 · C7. This is IV with its 9th alone on top, an octave and a sixth above the chord: open, and never resolved to F.

---

## 4. 声部分工与演奏法 · Parts, registers, articulation

### 4.1 Register and role per section

| Section | Vln I | Vln II | Vla | Vc | Cb |
|---|---|---|---|---|---|
| Intro 1–8 | motto D5–E6; b.8 F6–D6; alone on top | pad A4, G4→C5, C5, A4 (1–4); pulse A4, G4+C5 (5–7); lower sixth A5–F5 (8) | pad F4/E4/D4 with 4→3 sighs; pulse; G4→F4 (8) | the chart's bass octave B♭3/A3 (1–4), B♭2/A2 (5–7), D3 (8) | tacet → D2 at 8 |
| A 9–16 | theme D5–E6 | colour pad A4–E5 under the melody + b.12 answer; melody 8vb D4–E5 (13–16) | broken 8ths F3–A4 (9–12), C3–D4 (13–16); fills 10/14; run 16 | long roots; cadence quarters (12); 3+3+2 (13–15); walk | B♭1/A1 floor; walk |
| B 17–24 | top of the chart's RH chords, A5–A6 | inner colour voice C5–D♭6 | guide-tone dyads B♭3–A4 (lament) | the chart's LH arpeggio G2–A4 at pitch; dyads in 21/23; walk | roots F1–E2 |
| C 25–32 | as B, then the chart's 8va 27–31 (peak B♭6) | melody 8vb F5–A4 | dyads B♭4–D♭5 → 16th bariolage C♯4–D5 (26–30) | arpeggios 25–27; the chart's 3+3+2 blocks 28–30; D–A–E (31) | roots; E1 at 29 |
| D 33–40 | tacet 33–34; sky pedal A5 + pickup; ostinato 8va E6–G6 (37–39); D6 (40) | ostinato at chart pitch E5–G5 (the tune in 33–35; 8vb double in 37–39) | low tenuto dyads F3–C4 (33–35), A4+C5 (36); climbing bariolage (37–40) | short arco tresillo; chart quarters (36); marcato tresillo; chug (39); hammer (40) | **pizz.** tresillo (33–36); arco marcato; hammer |
| E 41–48 | reprise melody at the chart's 8va F6–D7; the C7 line (45); B♭6–E6 (46); E5 *loco* (47) | melody at the chart's pitch | bariolage A3–F4 (41–44, resting for the Vc fill in 42 beats 3–4), melody 8vb (45), A7(♭9) dyads (46), F3–F4 (47–48) | the chart's LH strokes and fill (41–43), walk (44), sweep (45), hammer (46), D–A–E (47) | tresillo (41–43), walk, G1→E1 (45), hammer (46) |
| F 49–52 | coda line D6–D7, final C7 | chord F5+A5 → E5+G5 | B♭4+D5 → B♭4+C5 | B♭2 (49, 51–52) | B♭1 (49, 51–52) |

Range contract (sounding): Vln I stays at or below A6 except B♭6 (b.27), the reprise 41–46 (D7 in 41, C7 in 43 and 45), D7 (b.50) and C7 (b.52). Vln II goes up to D♭6. Vla C3–D5 (alto clef throughout). Vc C2–A4 (A4 only in the b.20 arpeggio). Cb E1–D2 in this plan; G2 is available if a writer needs it.

### 4.2 Articulation vocabulary (build.py token → score → what ACE's smart mode hears)

| Intention | Token | Score | MIDI / ACE |
|---|---|---|---|
| Legato line | `( … )` slur | slur | notes touch → legato |
| Held or syncopated chord note | `~` tie | tie | **one merged note**, never re-attacked (vital for 3+(3~2)) |
| Détaché | plain token | — | 20-tick gap → détaché |
| Spiccato / leggiero short | `*` | staccato dot | half length → short stroke |
| Tenuto / portato | `_` | tenuto line | full length; connected only to a stepwise next note, else the 20-tick détaché gap |
| Accent | `>` | accent | +12 velocity; inside a crescendo it stays at least 6 below the note the crescendo lands on |
| Hammer (40, 46) | `^` | marcato | +12 velocity (same crescendo cap) |
| Final fermata | `!` | 𝄐 (b.52 only) | the tempo map stretches it |
| 16th drive | written-out 16ths on **two alternating pitches** (bariolage) | plain 16ths | separate notes, which do not merge; the cleanest option in ACE |

Allowed expression text: *espr.*, *dolce*, *cantabile*, *leggiero*, *marcato*, *largamente*, *con tutta forza*, *lontano*, *div.* / *unis.*, **pizz. / arco (Cb, b.33 and b.37 only)**, **G.P. (b.40, all parts)**.

**Not used, because ACE cannot render it from MIDI or because it contradicts the concept:**
- `%` tremolo slashes and unmeasured tremolo;
- grace notes `g:` and imitations of rolled chords;
- trills, glissando / portamento;
- con sordino, sul ponticello, sul tasto / flautando, col legno, harmonics, Bartók or snap pizz.;
- pizzicato anywhere except Cb 33–36;
- fermatas other than b.52.

### 4.3 The one-beat general pause (b.40, beat 4)
- **Where:** bar 40, beat 4 (16th positions 12–15), in all five parts at once. It is the only G.P. and the only full silence in the piece.
- **Notation:** a quarter rest in every staff, with the text **"G.P."** over it in every part: `TEXT[pid] += [(40, 12, "G.P.")]`. No fermata, no caesura, no tempo change.
- **MIDI:** every note ends exactly at 40.12. Nothing is tied or slurred into beat 4. The b.40 crescendo hairpin ends at (40, 11), and the next dynamic mark is *ff* at (41, 0), so that the CC swell does not carry into the gap.
- **What gets dropped:** the chart's passing C on beat 4 (★).
- **Before and after:** beats 1–3 are hammered at *f* with a crescendo into the cut-off: Vc and Cb D–D–D (marcato), violins holding D6/A5, Vla bariolage. On the downbeat of 41 all five attack together at *ff*, the level the crescendo reached: Vln I A6, Vln II A5, Vla D4, Vc B♭2+F3, Cb B♭1. (Round 1: 40 was *ff* < *ff*, which in the MIDI peaked before the G.P. and dropped at the landing; `--check` now reports any hairpin that does not lead to a louder / softer mark.)

### 4.4 Octave doublings and the peaks
- **Vln I / Vln II octaves:**
  - 13–16: warmth, *mf*;
  - 21, beat 4: the chart's own A–B♭ octaves;
  - 25–30: the lift to the summit;
  - 37–39: the drive;
  - 41–45: grandioso, Vln I at the chart's 8va and Vln II at the chart's pitch (round 1).

  Vln II copies Vln I's rhythm, slurs, ties and accents exactly.
- **Three octaves:** only in b.45, where the Vla joins two octaves below Vln I.
- **Register peaks:** B♭6 in b.27 (*ff*, with B♭5 in Vln II) is the summit of Chorus II. The reprise goes above it: D7 in 41, C7 in 43 and at the *fff* crest in 45, so the biggest climax is also the highest. D7 in b.50 is a *soft* peak. C7 in b.52 is the last sound.
- **Bass octaves:** Vc and Cb play in octaves whenever both carry the bass: the walks (16, 24, 44), the tresillos (13–15, 33–43), and the hammers (40, 46).
- **Parallel open fifths:** none are planned. The film concept's Vc "power fifths" were replaced by viola bariolage.

### 4.5 Pizzicato (one spot) — CANCELLED, see the override at the top: Cb 33–36 is arco secco
- **Where:** Cb only, b.33–36. Text **"pizz."** at (33, 0) and **"arco"** at (37, 0) in the Cb part.
- **How it is written:** short 8ths on 1, 2& and 4 (quarters in b.36), so it also works if it stays arco.
- **ACE:** someone has to switch the Basses track to pizzicato by hand for bars 33–36.
- **Delivery:** `usage_md()` step 3 in build.py currently says "no pizz". The delivery step must change it to name this one switch.

### 4.6 Double stops and divisi
- **Sustained dyads are marked *div.* in the score:**
  - Vln II 17, 21, 31, 49–52;
  - Vla 17–24 (the lament), 25–26, 31, 33–36, 47, 51–52.
- **Short rhythmic dyads stay double stops:**
  - Vln II 6–7 (G4+C5 pulse), 22 (C♯5+E5), 45 beat 1 (F5+C6) and 46 (E5+C♯6);
  - Vla 46 (G4+B♭4);
  - Vc D3+A3 (open), E3+B♭3, G3+D4, E3+C4, F♯3+C4, F3+C4, A2+E3, B♭2+F3 (41).
- **Cb:** never.
- **Playability:** every dyad in the skeleton passes build.py's STOP check.

### 4.7 Clefs and engraving
- Vla: alto clef throughout (top note D5).
- Vc: bass clef throughout. Single apex notes (F4, A4, E4, G4) stay in bass clef with ledger lines rather than flickering between clefs. Tenor clef is permitted only for b.20 or b.42, beats 3–4, if the engraver prefers.
- Vln I is printed under an *8va* line in 25–31 (to beat 3 of 31), 36 beat 4 – 46, and 49–52 (`OTTAVA` in build.py); 31 beat 4 and 47 are marked *loco*. The MIDI stays at sounding pitch either way.
- Rehearsal letters are boxed. The G.P., pizz./arco and every tempo word from §2 appear in all parts.

---

## 5. 段落接缝 · Seam contracts

These are the pitches each part has at the last beat of one section and the first beat of the next. Writers may not change these pitches or rhythms without agreeing it with the writer on the other side of the seam. The writer boundaries coincide with the section boundaries (§7).

| Seam | Part | Last beat of the outgoing section | First beat of the incoming section |
|---|---|---|---|
| **8 → 9** | Vln I | D6 (dh from beat 2), tenuto to the barline, *p* | D5 8th: the theme starts, *mp* |
| | Vln II | F5 (dh, the lower sixth) | C5 w, *p* |
| | Vla | F4 h (beats 3–4) | F3 8th: broken chords begin |
| | Vc | C3 q | B♭2 w |
| | Cb | C2 q | B♭1 w |
| **16 → 17** | Vln I | D6 E6 (8ths, beat 4) | F6 tied for 10 16ths, **f** |
| | Vln II | D5 E5 (8ths, 8vb) | F5+B♭5 w |
| | Vla | 16th run ending G4 A4 | B♭3+F4 w |
| | Vc | walk … B♭2 A2 (8ths) | G2 q |
| | Cb | walk … B♭1 A1 | G1 w |
| **24 → 25** | Vln I | A5 q | F6, **ff** |
| | Vln II | F♯5 q | F5 (8vb melody): the chromatic F♯→F |
| | Vla | C4+A4 h | B♭4+D5 w |
| | Vc | walk … B♭2 A2 | G2 q |
| | Cb | walk … B♭1 A1 | G1 w |
| **32 → 33** | Vln I | D5 w, *p*, *poco rit.* | rests (33–34) |
| | Vln II | A4 w | E5 8th (ostinato), *mp*, *a tempo* |
| | Vla | F4 w | F3+A3 dq |
| | Vc | C3 h | B♭2 short 8th |
| | Cb | C2 h | B♭1 short 8th, arco *secco* |
| **40 → 41** | all | **beat 4 silent (G.P.)** | all attack together, **ff** |
| | Vln I | D6 (beats 1–3) | A6 8th |
| | Vln II | A5 (beats 1–3) | A5 8th |
| | Vla | bariolage A4–D5 (last 16th D5 at pos 11) | bariolage D4–F4 (D4 first) |
| | Vc | D3 q (beat 3, marcato) | B♭2+F3 8th > |
| | Cb | D2 q (beat 3, marcato) | B♭1 dq, marcato |
| **44 → 45** (inside E) | Vln I / Vln II / Vla | F6 h / F5 h / bariolage A3–D4 | C7 / F5+C6 / C5, **fff** |
| | Vc / Cb | walk … A2 / … A1 | G2 8th / G1 |
| **48 → 49** | Vln I | D5 w, *pp*, *rit.* | D6 q, *pp dolce*: the octave lift |
| | Vln II | A4 w | rest h, then F5+A5 |
| | Vla | F4 w | rest h, then B♭4+D5 |
| | Vc | C3 h, ten. | B♭2 h |
| | Cb | C2 h | B♭1 h |

---

## 6. 写作规则 · Rules for the section writers

1. **Melody fidelity.** The chart's top line must be present note for note, with the same attack rhythm, in the part(s) listed in `MELODY`, at the listed octave. Ties are kept where the chart ties.
   - No ornaments, passing notes or grace notes in a melody carrier.
   - The only `MELODY_FREE` bar is 36, where the chart's A5 is held over in Vln I from b.35.

   ```python
   MELODY = {b: [("vn1", 0)] for b in range(1, 53)}
   for b in (13, 14, 15, 16, 25, 26, 27, 28, 29, 30, 37, 38, 39):
       MELODY[b] = [("vn1", 0), ("vn2", -12)]
   for b in (33, 34, 35):
       MELODY[b] = [("vn2", 0)]
   for b in (41, 42, 43, 44):                     # round 1: E an octave up
       MELODY[b] = [("vn1", 12), ("vn2", 0)]
   MELODY[45] = [("vn1", 12), ("vn2", 0), ("va", -12)]
   MELODY[46] = [("vn1", 12)]
   MELODY_FREE = {36: "A5 held over from b.35 in Vln I (sky pedal)"}
   ```

   Vln I at "0" means the chart's *sounding* pitch; the check already applies the chart's 8va (27 – 31 beat 3, 37–40, 49–52).
2. **Bass fidelity.** The lowest sounding note on beats 1 and 3 is the chart's bass (build.py checks this). The only deliberate bass departures are those marked ★ in §6.8. **`BASS_FREE` stays empty**; the skeleton passes without it. If a figure trips the BASS check, change the figure.
3. **No minor 2nds or minor 9ths**, in any octave and between any two parts. The only exceptions are the chart's own ♭9 colours, which are the 13 `CLASH_ALLOW` entries in `plan/00_skeleton.py` (bars 18, 22, 24, 26, 27 and 46, each with its reason). Do not add others.

   The traps the skeleton already avoids, which writers must keep avoiding:
   - no E on beats 1–2 of bars 2, 3, 6, 7, 11 and 15 (the motto or theme passes F5);
   - no F in the upper strings in 18 and 26 (the Vc arpeggio has E3);
   - Vla D4+A4, not A3, in 20;
   - no F♯ under G5 in 24, beat 3;
   - no E in 30 at positions 0–2;
   - no F at F4 or above during beat 3 of 31 and 47 (Vc E4);
   - no A in the Vla at 12 pos 11;
   - Vln II and Vla silent on beat 4 of 36;
   - no B♭3 in the Vla in 41 (Vc A3);
   - nothing sounding G against the violins' F♯6 / F♯5 in 42 (pos 6–7).
4. **No parallel 5ths or 8ves**, except the planned doublings:

   ```python
   DOUBLINGS = [("vn1", "vn2", 13, 16), ("vn1", "vn2", 21, 21), ("vn1", "vn2", 25, 30),
                ("vn1", "vn2", 37, 39), ("vn1", "vn2", 41, 45), ("vn2", "va", 45, 45),
                ("vn1", "va", 45, 45), ("vc", "cb", 8, 52)]
   ```

   Typical accidental parallels and their fixes:
   - broken chords shadowing the melody (13, 15): reorder the chord notes;
   - a bariolage in phase with the Vc arpeggio (27, 42, 43): flip the phase;
   - a chart arpeggio against the melody (17/25, pos 10): swap two arpeggio notes;
   - approaching 51 in the Vla: B♭4 on beat 4 of 50.

   Never silence a PARALLEL by widening `DOUBLINGS`.
5. **Counter-lines only in gaps.** The complete list: the Vla fill (10, 14); the Vln II motto answer (12); the walks (16, 24, 44); the Vla run (16); the Vla riser (26, beats 3–4); the bariolage through the rests (29–30); the sky pedal and pickup (35–36); the Vc fill (42). Nothing else moves against a moving melody note.
6. **Harmony.** Keep the chart's harmony. Colour comes only from voicing (maj7 / add9 / sus4→3 / 11 / 13 / ♭9 as listed). The only added harmonic event is the b.44 walk. Keep the third in 32 and 48; b.40 is open (no third) because the chart is.
7. **Engineering for ACE and build.py.**
   - Every bar in your range is defined for all five parts; use `"r/16"` for a silent bar. Every bar sums to 16.
   - At the first bar of your section, give every playing part a `DYN` mark, and give one again at every re-entry after rests. The MIDI curve is a step function.
   - Every hairpin must be followed by a printed dynamic, because that dynamic is the hairpin's MIDI target.
   - Use ties for syncopated chords; never write repeated attacks where the chart ties.
   - Slurred lines must touch; short notes need `*` or real rests.
   - Use Vc / Cb `CLEFS` only as §4.7 allows.
8. **Documented departures (★).** These go in the README section "编配说明":
   - b.13–15: the chart's bass pitches re-rhythmed as 3+3+2.
   - b.17 and b.25: two notes of the Vc arpeggio swapped, to avoid parallel octaves with the melody.
   - b.18 and b.26: the chart's F6 is left out of the strings (it rubs against the arpeggio's E3).
   - b.36, beat 4: the chart's whole-note chord is released in Vln II and Vla for Vln I's pickup; Vln I's sky pedal (35–36) is added.
   - b.40, beat 4: the passing C bass is dropped for the G.P.
   - b.44, beats 3–4: launch walk D–C–B♭–A added (not in the chart).
   - b.45: melody tripled in octaves.
   - b.41–46: the reprise an octave above the chart (Vln I 8va, Vln II at pitch, Vla an octave below Vln II in 45); 47 returns to the chart's E5 (*loco*).
   - b.51–52: Vc and Cb B♭ pedal added under the chart's treble-only C/B♭.
   - Rolled chords (45, 51) are played as plain chords.
   - The chart's LH register in 1–4 is kept, but split between Vln II and Vla as single lines.

---

## 7. Writers, files and testing

| Writer | Bars | Sections | Owns seams |
|---|---|---|---|
| W1 | 1–16 | Intro + A | 8→9 (internal), 16→17 (with W2) |
| W2 | 17–24 | B | 16→17, 24→25 |
| W3 | 25–32 | C | 24→25, 32→33 |
| W4 | 33–40 | D (incl. the G.P.) | 32→33, 40→41 |
| W5 | 41–52 | E + F | 40→41, 44→45 and 48→49 (internal) |

**Delivery.** Each writer delivers `juebieshu/draft/wN_barsAA-BB.py`. The file defines `VN1`, `VN2`, `VA`, `VC` and `CB` for its bars only, plus its `DYN`, `HAIR`, `TEXT`, `MELODY`, `MELODY_FREE`, `CLASH_ALLOW`, `DOUBLINGS` and `CLEFS` entries, copied from §6 for its bars. For formats see the header of `build.py`: DYN is `(bar, 16th, mark)`, HAIR is `(bar, 16th, bar2, 16th2, "cresc" | "dim")`, and TEXT is `(bar, 16th, "text")`.

**Test against the neighbours** by using the skeleton for every bar you do not own:

```bash
mkdir -p /tmp/jbs && cp juebieshu/plan/00_skeleton.py /tmp/jbs/ \
  && cp juebieshu/draft/wN_*.py /tmp/jbs/
JUEBIESHU_DRAFTS=/tmp/jbs python3 juebieshu/build.py --check --bars AA-BB
```

Your draft sorts after `00_` and overrides the skeleton's bars. Check one bar *beyond* each seam as well, for example `--bars 16-25` for W2. Finished means `--check` prints nothing for your range.

**For the build/delivery step, after merging:**
- paste the FORM block from §2;
- set `GP_NOTE`;
- update `usage_md()` step 3 for the Cb pizz. (§4.5);
- list the ★ departures from §6.8 in the README.

---

## 8. Decisions log

| Decision | Source | Why |
|---|---|---|
| Overall shape, the G.P. at 40.4 in tempo, tutti landing at 41, broadening 45–48, tempo map, coda on the chart's C/B♭ with C7 on top | film | Both judges; this is the user's rule about the G.P. landing right before the biggest climax |
| B: the chart's RH chords as a choir in 3+(3~2) with merged ties; Vc plays the chart's LH arpeggio at pitch | film | Most faithful to the chart, and orchestral |
| B: viola guide-tone lament (F–E–E–D–D–C♯–C–C) instead of film's jumpy lowest-RH-voice viola; in 20, D4+A4 | chamber (J1, J2) | "简单而高级"; keeps the viola in a warm register. A3 in 20 is fixed because it clashes with the Vc's B♭3 |
| All 16th drives as two-string bariolage in the Vla (26–30, 37–40, 41–44); no Vc 16th double stops, no repeated-note dyads | chamber (J2) | Cleanest in ACE; removes the low-end mud film had in 37–44; puts the 16th layer at the first summit |
| Keep the borrowed D♭ in 26's riser (Vla B♭4+D♭5, sliding D5→D♭5→C5) | J1 fix | film's G4+B♭4 lost the colour |
| No F in the upper strings in 18 and 26; no E under a passing F; F below the Vc's E4 in Dm9 bars; nothing against F♯4 in 42 | variety (J1, J2) | Clash hygiene, all verified by `--check` |
| Intro pad as single lines in Vln II and Vla with 4→3 sighs in the gaps (no sustained E4+G4) | variety + chamber (J1) | film's whole-note E4 under the passing F5 was a ♭9 |
| 28–30 low strings play the chart's own 3+3+2 block LH | chamber (J2) | Fidelity; strengthens the 3+3+2 thread |
| 41–43 Vc plays the chart's LH strokes and the 42 fill | chamber (J2) | Fidelity; keeps one clear motor per register |
| Sky pedal A5 (35–36) plus the pickup A5–B♭5–C6–D6 into the 8va at 37 | variety (J1, J2) | 综艺 rebuild. Vln II and Vla release on beat 4 of 36 so the B♭5 rubs against nothing |
| Launch walk named as a cue (16, 24) and added at 44 (★) | variety (J1, J2) | "Here it comes" signal into the crest |
| At 45 the Vla joins the melody (three octaves) while the Vc sweep and Cb keep Gm7(11) | variety, softened (J2) | Power without giving up the chart's harmony. variety's five-part unison was rejected (J1) |
| 47 top back to the chart's E5; third kept in 32 and 48; b.41 melody corrected; Vln II E♭5 held in 24; Vln II below the melody in 11 | J1 fixes | Fidelity |
| Only one pizz. spot (Cb 33–36) | film | One manual ACE switch; it still works arco |
| Coda voicing exactly as the chart (Vln II F5+A5 / E5+G5, Vla B♭4+D5 / B♭4+C5), with Vc and Cb B♭ ppp under 51–52 | film (J2) | Rejected: variety's B♭maj9 ending, and chamber's cello quote and reharmonisation under the fermata |
| Rejected: chamber's removal of E3 in 18 and 26, its invented G–F–E bass in 45, its ♩ = 92 coda; variety's misreadings of 29 (E6) and 31 (E5) and its ♩ = 96 G.P. beat; film's Vc tenor counter-melody in 29–30 and its Vc 16th fifths in 37–44 | J1, J2 | Harmony changes, misreadings, or mud |
| Not taken: Vc motto answers in 5–7 | chamber (optional) | Keeps the intro's gaps empty ("the letter's breath"); the answer idea lives in Vln II at b.12 |
| Round 1 (review): E an octave up (41–46); C added to the intro pad (Vln II C5 in 2–3, G4+C5 pulse in 6–7); Cb holds D under 24 beat 2 and the Vla drops its F♯4 there; Vla 14 G3–E4 (not C3 over the B♭ bass); Vla 27 E4 (the chart's B♭–E tritone); Vla 39 D4–C5 (the chart's Dm11 C); Vla rests for the Vc fill in 42 beats 3–4; Vc B♭2+F3 on the 41 landing; 40 *f* < into the G.P.; *sonoro* for *largamente* at 17 | review panel | Fidelity to the chart's chords; the biggest climax must also be the highest and the loudest; "Largamente" is kept for the tempo mark at 47 |
| Round 1, rejected: Vla D4+F4 or Vln II A4 in 23 (the C♯→C octave is Vln II doubling the lament, as in 20–22); Vln II B♭5+D♭6 div. in 18 (halves the unison D♭6 colour note); Cb tenuto in 36 (the secco continues) | lead | Would break the lament or the signature D♭6 |
| Round 2: §3, §4 and §5 brought in line with build.py after round 1 (the tables above now describe the written notes); Cb *dim.* in 47 with the Vc, into the *p* at 48 | lead | build.py is the source of truth; a later writer must not revert round 1 from stale rows |
| Round 2.5 (ACE MIDI): an un-slurred tenuto touches its next note only by step (the leaps at 8→9, 12→13, 15→16, 35→36, 45, 45→46, 46→47, 47, 48 get the détaché gap, so ACE hears no slur the score lacks); an accent inside a crescendo stays at least 6 below the note the crescendo lands on (walks 16/24/44, hammers 40); Vc/Cb accent on the 17 landing, as in 25 | lead | The landings are the loudest attacks in the velocity-only render; the 3+3+2 accents of 39 keep their bite. Reviewer's flat cap at the crescendo's target was not taken: it erased them |

**Fallbacks, to be decided after an ACE test render:**
1. If D7 / C7 in the coda sound thin or whistly, move Vln I in 49–52 down an octave, to the chart's written pitch D5–C6. Vln II and Vla then drop their chords an octave too (Vln II F4+A4 → E4+G4; Vla B♭3+D4 → B♭3+C4).
2. If the 41–44 tutti smears, replace the Vc strokes with 8ths on root–5th–octave–5th (B♭2 F3 B♭3 F3 …), and the Vla bariolage can come down to *mf*.
3. If B♭6 in b.27 is strident, keep it: it is *ff* and doubled at B♭5.
4. If the G.P. is smeared by the release tails, shorten the beat-3 notes of b.40 by a 16th.
