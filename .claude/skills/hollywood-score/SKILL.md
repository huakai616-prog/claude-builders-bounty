---
name: hollywood-score
description: House standard for delivering a song arrangement in this repo (voice + strings from a jianpu screenshot). Use whenever you create or update a song's score, PDF, Sibelius file or MIDI. It fixes the deliverable set (Sibelius MusicXML, Hollywood-standard PDF with cover, full strings MIDI, vocal MIDI with lyrics), the credits (改编 and 制谱 are both 花开当富贵), and the Hollywood layout, and says how to render and check it with tools/hollywood. Follow it without asking the user about layout, credits or deliverables.
---

# Hollywood score delivery

The user set these rules once and does not want to be asked again.

## Standing rules

1. **Always deliver these four files**, committed to `<song>/output/` (never only as chat attachments):
   - **Sibelius project**: `<歌名>_副歌_<编制>.musicxml`. A `.sib` file cannot be generated outside Sibelius, so the Sibelius project is a MusicXML file that validates against the MusicXML 4.0 schema. Say so in one short line. The user opens it and saves it as `.sib`.
   - **Hollywood-standard full score PDF with a cover**: `<歌名>_副歌_总谱.pdf`.
   - **Full strings MIDI**: all string parts in one file, `<歌名>_弦乐<编制>_伴奏.mid`.
   - **Vocal MIDI with per-syllable lyrics**: `<歌名>_人声_带歌词.mid`, plus the GBK fallback.
   - Also keep the usual extras: full-track MIDI for ACE, plain vocal MIDI, GM preview mp3, SRT.
2. **Credits**: 改编 (arranger) and 制谱 (engraver / music preparation) are both **花开当富贵**. They appear on the cover, in the first-page title block, in every page footer, in the MusicXML `<creator type="arranger">` and `<encoder>`, and in the PDF metadata. `tools/hollywood` defaults to this; never leave either credit out.
3. **Layout must be refined** (精益求精). Render, look at every page, and fix problems before you deliver (see the QA list below).

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
- `polish()` in `build.py` keeps only the song-specific work: instrument sounds, dynamics placement, `SYSTEM_BREAKS`. Page layout and credits come from `hollywood`.

Then run:

```bash
python3 <song>/build.py --check   # must print nothing
python3 <song>/build.py --pdf     # MusicXML, MIDI, SRT and the Hollywood PDF
```

## Environment setup (a new cloud container has none of this)

```bash
pip install music21 mido pypdf cffi          # cffi: the system cryptography needs it for pypdf
apt-get install -y fonts-noto-cjk fonts-ebgaramond fonts-ebgaramond-extra poppler-utils \
                   fluidsynth fluid-soundfont-gm ffmpeg libxml2-utils
```

- **MuseScore 4**: `hollywood.find_ms4()` downloads the 4.4.4 AppImage to `/opt/ms4` and extracts it if it is missing (about 170 MB, via github.com releases). Override with `MSCORE4=/path`.
- **Chromium**: found under `/opt/pw-browsers/chromium-*/chrome-linux/chrome`, or set `CHROME=/path`.
- On the user's Mac: MuseScore 4 at `/Applications/MuseScore 4.app`, Chrome at `/Applications/Google Chrome.app`. Both are picked up automatically.

## Choosing system breaks (3 systems per page)

On 11 × 17 at 7.2 mm staves:

- **Width**: an intro with long notes fits 4 bars per system. A lyrical passage with some 16ths in the voice fits 3. Passages with 16ths in the voice **and** 16th strings fit 2.
- **Height**: 5 staves + lyrics = one system. The first page holds the title block + 3 systems; the other pages hold 3.
- Count the systems and make the total a multiple of 3 (page 1 counts as 3). Move one break if the last page would get 1–2 lonely systems. Start systems at rehearsal letters where possible.
- Explicit breaks that are too full make MS4 wrap a bar on its own. If you see a one-bar system, take a bar out of that system.

## QA before delivering (look at every page)

```bash
pdftoppm -r 90 -png <song>/output/<歌名>_副歌_总谱.pdf /tmp/pg   # then view each PNG
xmllint --noout --schema musicxml.xsd <song>/output/*.musicxml   # schema from w3c/musicxml
```

- The cover shows the title, credits table (both 花开当富贵 rows), key · tempo · duration, and instrumentation, with nothing clipped.
- Every page has its header and footer and a correct "PAGE n OF N".
- There is a boxed bar number on every bar, and no collisions between dynamics, texts, lyrics or hairpins.
- Each page has 3 systems (the last page may have fewer, but not a lone system with half a page empty), and there is no one-bar system.
- The first-page title block is symmetric: left and right credit blocks share a bottom line and don't touch the music.
- The MusicXML validates against the schema. The MIDI reads back: every vocal note has a lyric or `-`, and the track names are right.

## Known pitfalls

- MS4 **ignores `-S style` when it imports MusicXML directly**. `render_pdf` imports to `.mscz` first, then exports with the style.
- MS4 gives imported MusicXML credits odd offsets: the composer drifts to the top and the lyricist falls into the music. `render_pdf` resets the title frame (`_fix_title_frame`).
- music21 writes the tempo words and the metronome as two directions. Use `tempo_text` so they print as one mark.
- The cover and header are an HTML page printed by headless Chromium on a transparent background and merged onto the MS4 pages. Page size must stay 11 × 17 in on both sides.
- EB Garamond has no ♩ ♭ ♯; `hollywood._sym` wraps them in a fallback font.
- MuseScore 3 (`mscore3`) cannot read this style. The Hollywood PDF needs MuseScore 4.
