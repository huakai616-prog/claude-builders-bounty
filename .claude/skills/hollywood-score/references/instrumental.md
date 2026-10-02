# Instrumental works and parts

Not every job is a song.  An instrumental piece (the first one: `alla-turca/`,
Mozart's Rondo alla Turca for string quartet, from a piano score PDF) follows
the same standard with these differences:

- **The four main files** are the Sibelius MusicXML, the Hollywood PDF, the
  strings MIDI (one track per instrument, for ACE) and a **parts PDF**
  (`<名>_分谱.pdf`) in place of the vocal MIDI.  In `tools/deliver/catalog.py`
  give the entry `main=dict(musicxml=…, pdf=…, strings=…, parts=…)`, plus
  `other_note` and `howto` for its 说明.txt.  No SRT, no GBK file.
- **Credits**: set `META["original"]` (e.g. "A大调钢琴奏鸣曲 K.331 第三乐章");
  it prints as 原曲 on the cover and in the title block, where a song has
  作词 / 原唱.
- **Parts**: `hollywood.polish_musicxml(path, META, part=("Violin I",
  "第一小提琴"))` lays a one-instrument MusicXML out as a 9 × 12 in part
  (`hollywood_part.mss`: same fonts, boxed bar numbers, multi-rests), and
  `hollywood.render_parts_pdf([(xml, en, zh), …], out, META)` engraves them
  into one PDF with a bookmark per instrument and the instrument named in
  every header and footer.  Give every part the tempo mark and the
  rehearsal letters (`make_m21(…, lead=True)` in `alla-turca/build.py`).
- **Transcribing a printed score** (not jianpu): keep the piano original
  in `<piece>/source_piano.py` and let `--check` compare the arrangement
  with it (melody attacked, bass on every downbeat, no pitch class foreign
  to the bar, no minor 2nd / 9th the original lacks).  Deliberate
  departures go into `ALLOW`, keyed by the original's bar numbers.
  A copyrighted source (Unravel follows Animenz's piano arrangement) stays
  out of the public repo: keep its transcription in the scratchpad and
  point `--check` at it (`UNRAVEL_PIANO=… python3 unravel/build.py
  --check`); without it the check runs ranges and double stops only.
- **The MIDI's barlines** must match the score's: with a pickup, start the
  MIDI with a whole empty bar holding the pickup at its end (ACE bar N =
  score bar N−1) and say so in `howto`.
- **Piano textures that no single string instrument can play** (冬风 /
  `dongfeng/`, Chopin's four-octave sextuplets): `dongfeng/engine.py`
  writes the MusicXML itself (music21 turns 6:4 sextuplets into 3:2 and
  beams per half bar) and prints "6" only on the first group of a run.
  MS4 ignores `show-number="none"`, so `META["mscx_hook"]` and
  `META["mscx_part_hook"]` (`_mscx_hook` in `dongfeng/build.py`) hide
  the bracket and number of every tuplet that arrived without a number.
- **MuseScore-file touch-ups learned on 冬风** (`dongfeng/build.py` hooks): see `ms4-touchups.md`.
- **Parts layout**: read each line's bars back from the PDF (`pdftotext -bbox`, boxed bar numbers are 8.6 pt high) and add explicit line starts wherever a bar stands alone; give each part page starts so page turns fall on rests (plan for page 1 alone, then two-page spreads), and so no last page holds only the final bars. Parts carry the rehearsal letters and tempo marks but not the section titles: a title next to a letter gets pushed around by the first bar-number box and never lines up.
- **Repeats**: written out (`FORM`), so the second time can be scored
  differently and the MIDI needs no unrolling; `ALIAS` reuses a strain's
  data for its reprise.
