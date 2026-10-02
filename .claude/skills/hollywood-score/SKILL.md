---
name: hollywood-score
description: House standard for delivering a song arrangement in this repo (voice + strings from a jianpu screenshot). Use whenever you create or update a song's score, PDF, Sibelius file or MIDI. It fixes the deliverable set (Sibelius MusicXML, Hollywood-standard PDF with cover, full strings MIDI, vocal MIDI with lyrics), the credits (改编 and 制谱 are both 花开当富贵), the Hollywood layout (tools/hollywood), and the hand-off: every finished work goes into the pinned 编曲交付中心 page (tools/deliver) and is merged into main. Follow it without asking the user about layout, credits, deliverables or merging. It fixes the delivery format only; the music (texture, harmony, structure) must be conceived fresh for each song, never copied from an earlier one.
---

# Hollywood score delivery

The user set these rules once and does not want to be asked again.

**This skill is about the delivery format, not the music.** When the user says 「像之前一样」, they mean the same delivery: the files, the PDF, the credits and the delivery center. They do not mean the same arrangement. 我不难过 copied 泪海's textures and chords almost one for one, and the user called it 难听. Conceive each song's texture, harmony, intro and ending from that song itself, and say in the README how it differs from earlier work. The full rule is in `AGENTS.md` under 「用户怎么提需求」.

## Standing rules

1. **Always deliver these four files**, committed to `<song>/output/` (never only as chat attachments):
   - **Sibelius project**: `<歌名>_副歌_<编制>.musicxml`. A `.sib` file cannot be generated outside Sibelius, so the Sibelius project is a MusicXML file that validates against the MusicXML 4.0 schema. Say so in one short line. The user opens it and saves it as `.sib`.
   - **Hollywood-standard full score PDF with a cover**: `<歌名>_副歌_总谱.pdf`.
   - **Full strings MIDI**: all string parts in one file, `<歌名>_弦乐<编制>_伴奏.mid`.
   - **Vocal MIDI with per-syllable lyrics**: `<歌名>_人声_带歌词.mid`, plus the GBK fallback.
   - Also keep the usual extras: full-track MIDI for ACE, plain vocal MIDI, GM preview mp3, SRT.
   - **Instrumental works** (no voice, `alla-turca/`, `unravel/`, `dongfeng/`): four main files with a parts PDF in place of the vocal MIDI, see「Instrumental works and parts」below and `references/instrumental.md`. `META["original"]` prints as 原曲; `META["source"]` prints as 改编自 / Based on (the version an arrangement follows, e.g. "Animenz 钢琴版"). A Latin-script title gets tight tracking on the cover automatically.
2. **Credits**: 改编 (arranger) and 制谱 (engraver / music preparation) are both **花开当富贵**. They appear on the cover, in the first-page title block, in every page footer, in the MusicXML `<creator type="arranger">` and `<encoder>`, and in the PDF metadata. `tools/hollywood` defaults to this; never leave either credit out.
3. **Layout must be refined** (精益求精). Render, look at every page, and fix problems before you deliver (see the QA list below).
4. **The user must be able to find the files without GitHub** (they said 「我不太会用 GitHub」). Every finished work goes into the pinned **编曲交付中心** page, and the first line of your reply is its link: https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN . There, one click saves a zip to the computer's Downloads folder. Never tell the user to look for files on a branch. The publishing steps are in `references/delivery-center.md`.
5. **Merge into main yourself** once the work is checked (the user authorized this once, for good): open a PR from your branch to `main` and merge it. New conversations only read `main`, so the rules, tools and catalog must live there.

## What "Hollywood standard" means here

| Element | Standard |
|---|---|
| Paper | 11 × 17 in (tabloid) portrait, the Hollywood full-score size. Score in C (concert pitch) |
| Cover | Double-rule frame, "FULL SCORE / Score in C · Concert Pitch", large title (Noto Serif CJK), pinyin or English title, subtitle in Chinese and English, credits table (作曲 / 作词 / 原唱 / 改编 / 制谱), key · tempo · duration, instrumentation, and 花开当富贵 at the foot |
| First page | Title block: title and subtitle centred; lyricist and original artist bottom-left; composer, arranger and engraver bottom-right |
| Every page | Running header (title · section, "FULL SCORE IN C", big page number top right, hairline); footer (改编 · 制谱 花开当富贵 / Arranged & Music Preparation by 花开当富贵, "PAGE n OF N") |
| Bar numbers | Every bar, bold, boxed, centred over the bar |
| Rehearsal marks | Letters A, B, C…, boxed, large and bold, at section starts, with a bold section title beside them ("Chorus 副歌", "Climax 高潮", "Coda 尾奏"). The intro gets only its title |
| Tempo | One bold mark: "Andante espressivo ♩ = 68" |
| Fonts | Leland (music), Edwin (text), Noto Serif CJK SC (Chinese lyrics and titles), EB Garamond (cover, header, footer) |
| Staff size | 7.2 mm (spatium 1.8 mm), generous staff spacing, systems spread down the page |
| Systems | Aim for **3 systems per page on every page** and phrase-aligned breaks. Never leave a one-bar system or a near-empty last page |

## How to build it

The template lives in `tools/hollywood/`:

- `hollywood.mss`: the MuseScore 4 house style (partial style file).
- `hollywood.py`:
  - `polish_musicxml(path, meta)`: tabloid layout, credit block, creators, bar numbers, merged tempo text. This is what Sibelius sees.
  - `render_pdf(musicxml, pdf, meta)`: MuseScore 4 engraving, then the Chromium-drawn cover and header/footer, merged with pypdf.

Wire a song's `build.py` like `wobunanguo/build.py`:

```python
sys.path.insert(0, os.path.join(HERE, "..", "tools", "hollywood"))
import hollywood

SECTIONS = [(1, None, "Intro 前奏"), (5, "A", "Chorus 副歌"), ...]  # rehearsal letters + titles
SYSTEM_BREAKS = (...)            # choose for 3 systems per page (see below)
META = dict(title=..., title_latin=..., subtitle="副歌 · 人声与弦乐四重奏",
            subtitle_en="Chorus — for Voice and String Quartet",
            composer=..., lyricist=..., artist=...,
            instrumentation=[("Voice", "人声"), ("Violin I", "第一小提琴"), ...],
            key="E♭ Major · 降E大调", tempo="♩ = 68", duration="ca. 1′25″",
            year="2026", tempo_text="Andante espressivo")
# arranger / engraver default to 花开当富贵

# in main(): after polish(base + ".musicxml")
hollywood.polish_musicxml(base + ".musicxml", META)
# and a write_pdf() that calls hollywood.render_pdf(...); `--pdf` runs it
```

- Create the `MetronomeMark` **without** text; `META["tempo_text"]` is joined to it.
- **Hairpins on held notes**: the older `make_m21()` (泪海, 我不难过) pins a hairpin to note objects and silently drops it when both ends land on the same held note (a cresc under a whole note, a dim under a tie). `chatang/build.py` falls back to `spanner.SpannerAnchor` offsets in that case; copy its hairpin loop into new songs.
- **Voice hairpins**: printed above the voice staff they push single bar-number boxes up. `print_hair=False` on the voice part keeps them in the MIDI only (`chatang/build.py`).
- **Song-specific engraving touch-ups**: `META["mscx_hook"]` is a function applied to the imported MuseScore file before engraving (for example right-aligning a text at the end of a system, which MS4 ignores from MusicXML `justify`). See `chatang/build.py`.
- **8va lines**: when a violin line sits above about E6 for a bar or more, add `OTTAVA = [("Violin I", first_bar, last_bar)]` and the `<octave-shift>` block in `polish()` (copy it from `chatang/build.py`). The MusicXML keeps the sounding pitches, so the MIDI is unaffected; MS4 and Sibelius only shift the display.
- `polish()` in `build.py` keeps only the song-specific work: instrument sounds, dynamics placement, `SYSTEM_BREAKS`. Page layout and credits come from `hollywood`.
- **Engraving rules learned on Unravel** (`unravel/build.py` has them; copy into new engines):
  - `rebeam()` after `polish_musicxml`: music21 beams across the middle of a 4/4 bar and leaves orphan `end` beams. Rebeam per beat, merge beats only where a note crosses the beat (3+3+2 figures), never across beat 3; secondary beams per beat, a lone 16th hooked toward the note it completes.
  - Rests never hide a beat: dotted rests only on the beat, shorter rests inside their beat (`_fits_rest`).
  - Expressive words (`dolce`, `cantabile`, `espressivo`, `subito`, `morendo`, …) go **below** the staff; when a dynamic sits on the same beat they are merged into its `<direction>` so MS4 and Sibelius print one line ("*f* subito", "*p* dolce"). Techniques (sul tasto, spicc., marcato, legato) stay above. Don't hang an expressive word on a pickup: it runs through the barline (the quartet's barlines are connected); put it on the next downbeat.
  - Ties are per pitch: `Bb4/8~ Bb4+D5/32` ties the Bb4 and strikes the D5 (MusicXML and MIDI), so a chord can grow without a second voice.
  - Per-bar engraving overrides (`STEMS`, `SLURS_BELOW` in `unravel/arrangement.py`) fix a run whose tuplet number pushes a dynamic toward the next staff, or slurs flipping side in repeated cells.
  - Keep a courtesy dynamic right after a rehearsal letter.
- **Layout options in `META`** (all optional): `title_frame_sp` (title frame height, default 21), `title_gap_sp` (frame to first system; 10 gives the tempo mark room under the credits), `section_lift` (default 5) and `section_pin=True` (title set 1 sp right of the letter so a wide M/N/H doesn't stack them; use with `section_lift=9` when sections open with tall chord stacks or under an 8va).

Then run:

```bash
python3 <song>/build.py --check   # must print nothing
python3 <song>/build.py --pdf     # MusicXML, MIDI, SRT and the Hollywood PDF
```

## Environment setup (a new cloud container has none of this)

```bash
bash tools/setup.sh   # quiet, idempotent; prints one line per component
```

It installs whatever is missing: `pip install music21 mido pypdf cffi` (cffi: the system cryptography needs it for pypdf); `apt-get install --no-install-recommends fonts-noto-cjk fonts-ebgaramond fonts-ebgaramond-extra poppler-utils fluidsynth fluid-soundfont-gm ffmpeg libxml2-utils libegl1 libopengl0` (the MuseScore 4 AppImage needs `libegl1` and `libopengl0` and does not bundle them; the old command only worked because fluidsynth's recommended Qt packages happened to pull them in); MuseScore 4, checked by actually starting it; Chromium is only checked; the MusicXML 4.0 schema for `qa.py xml` (`~/.cache/musicxml/`). All installer output goes to `${TMPDIR:-/tmp}/setup-music.log`; read the log only when a line says FAILED (the script then prints its tail).

- **MuseScore 4**: `hollywood.find_ms4()` downloads the 4.4.4 AppImage to `/opt/ms4` and extracts it if it is missing (about 170 MB, via github.com releases). Override with `MSCORE4=/path`.
- **Chromium**: found under `/opt/pw-browsers/chromium-*/chrome-linux/chrome`, or set `CHROME=/path`.
- On the user's Mac: MuseScore 4 at `/Applications/MuseScore 4.app`, Chrome at `/Applications/Google Chrome.app`. Both are picked up automatically (`tools/setup.sh` is for Linux cloud containers and exits on macOS).

## Instrumental works and parts

An instrumental piece (no voice: `alla-turca/`, `unravel/`, `dongfeng/`) follows the same standard with these differences: a parts PDF replaces the vocal MIDI among the four main files, `META["original"]` / `META["source"]` credits, parts rendering (`polish_musicxml(…, part=…)`, `render_parts_pdf`), `--check` against the piano original, MIDI barlines with a pickup, parts layout, and written-out repeats. **Read `references/instrumental.md` before arranging one**, and `docs/钢琴谱改编.md` for the transcription workflow.

## Song-specific style values

`META["style"] = {"measureSpacing": 1.3}` (and `META["part_style"]` for the
parts) replaces or adds keys of the house style for one piece only;
`render_pdf` writes a temporary copy of `hollywood.mss`.  Use it sparingly:
the house values are the standard.

## Choosing system breaks (3 systems per page)

For a long score, `unravel/layout.py` plans the breaks automatically: it estimates each bar's width from its onsets, starts a system at every rehearsal letter, packs 3 systems per page and prints `SYSTEM_BREAKS` / `PAGE_BREAKS` (budget 74 fits MuseScore 4 on 11×17 with four staves). `build.py` there also supports `PAGE_BREAKS` and positional 8va lines (`(part, bar1, pos1, bar2, pos2)`).

On 11 × 17 at 7.2 mm staves:

- **Width**: an intro with long notes fits 4 bars per system. A lyrical passage with some 16ths in the voice fits 3. Passages with 16ths in the voice **and** 16th strings fit 2.
- **Height**: 5 staves + lyrics = one system. The first page holds the title block + 3 systems; the other pages hold 3.
- Count the systems and make the total a multiple of 3 (page 1 counts as 3). Move one break if the last page would get 1–2 lonely systems. Start systems at rehearsal letters where possible.
- Explicit breaks that are too full make MS4 wrap a bar on its own. If you see a one-bar system, take a bar out of that system.
- To see the real layout without eyeballing every page, run
  `python3 tools/hollywood/qa.py score <pdf> -v`: it reads the boxed bar
  numbers back from the PDF (`pdftotext -bbox`), groups them by y (systems
  are 100+ pt apart) and lists the bars of every system on every page.
  A lowered `measureSpacing` does not help when the systems are already at
  their minimum width; take bars out or make them narrower.
- Instrumental 2/4 music (the string quartet): Mozart's 8-bar phrases fit one
  system; 16th-note passages 4 bars; the first system (full instrument
  names) holds about 6.

## QA before delivering (look at every page)

```bash
python3 tools/hollywood/qa.py score <song>/output/<歌名>_副歌_总谱.pdf -v   # layout report, PROBLEM lines (exit 0 = clean)
python3 tools/hollywood/qa.py pages <song>/output/<歌名>_副歌_总谱.pdf <scratch>/pages   # PNGs; lists pages new or changed
python3 tools/hollywood/qa.py xml <song>/output/<file>.musicxml               # MusicXML 4.0 schema
```

- `qa.py` has its usage in its docstring (`python3 tools/hollywood/qa.py -h`). It also works on a parts PDF (told apart by page size). It takes the bar count and the part list from the one `*.musicxml` next to the PDF (or `--musicxml F`). `--systems N` sets the systems-per-page target when a score has fewer on purpose (我和我的祖国: 8 staves, 2 per page).
- Run `score` after every render and fix what it reports before you look at pages. It reads the boxed bar numbers back from the PDF and lists the bars of every system on every page (`-v`); it flags missing bar numbers, one-bar systems, pages without 3 systems, a lonely last system, and missing headers, footers, page numbers, cover credits and instrumentation.
- Then look at every page that `pages` lists under "look at" (all pages the first time). A page it reports unchanged is pixel-identical to the version you already looked at in an earlier round, so it needs no second look. By delivery, every page must have been looked at in its final form.
- The eye checks the script cannot do:
  - The cover shows the title, credits table (both 花开当富贵 rows), key · tempo · duration, and instrumentation, with nothing clipped.
  - No collisions between dynamics, texts, lyrics or hairpins; bar-number boxes clear of the music.
  - The first-page title block is symmetric: left and right credit blocks share a bottom line and don't touch the music.
  - Systems are spread down the page and breaks fall at phrases.
- The script's checks, for reference: every page has its header and footer and a correct "PAGE n OF N"; there is a boxed bar number on every bar; each page has 3 systems (the last page may have fewer, but not a lone system with half a page empty) and there is no one-bar system; the MusicXML validates against the schema.
- The MIDI reads back: every vocal note has a lyric or `-`, and the track names are right.

## Known pitfalls

`render_pdf` already works around MuseScore 4's quirks: it ignores `-S` style on a direct MusicXML import, gives credits odd offsets, puts rehearsal letters and section titles into the bar-number row, falls back to a sans font for Chinese staff text, and labels 8va lines "8". The template also places ties between noteheads, pads letter-spaced cover lines, and supplies ♩ ♭ ♯ that EB Garamond lacks. **Read `references/template-internals.md` before editing `tools/hollywood/`, or when the PDF shows one of these symptoms.** Two that matter when building a song:

- music21 writes the tempo words and the metronome as two directions. Use `tempo_text` so they print as one mark.
- MuseScore 3 (`mscore3`) cannot read this style. The Hollywood PDF needs MuseScore 4.

## Delivery center (编曲交付中心)

Every finished work goes into the pinned page https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN (`tools/deliver/center.html`; database collection `works`, files under `files/<slug>/`, one zip per work). **When the work is built and checked, read `references/delivery-center.md` and follow its steps**: catalog entry in `tools/deliver/catalog.py`, `package.py`, `Artifact` read then publish, the `ArtifactData` row (keep the user's `removed` / `deleted`), the fallback snapshot, the reply with the link first, then commit, PR and merge. Read it also before editing `center.html`.

The 「放进 Mac 程序坞」 card (Mac Dock app, `tools/deliver/macapp/`) is documented in `references/mac-app.md`.

## Reference files (read when the task needs them)

| File | Read when |
|---|---|
| `references/delivery-center.md` | publishing a finished work, or editing `center.html` / `catalog.py` / `package.py` |
| `references/instrumental.md` | an instrumental piece, a parts PDF, or a printed (staff-notation) score as the source |
| `references/ms4-touchups.md` | the engraved PDF needs a fix MusicXML can't express (title rows, staff spacing, tuplet side, 8va hooks, accidentals after an 8va) |
| `references/template-internals.md` | editing `tools/hollywood/`, or debugging the cover, header/footer, credits or fonts |
| `references/mac-app.md` | the Mac Dock app (「放进 Mac 程序坞」) |
