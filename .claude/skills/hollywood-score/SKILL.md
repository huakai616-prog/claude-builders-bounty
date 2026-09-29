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
2. **Credits**: 改编 (arranger) and 制谱 (engraver / music preparation) are both **花开当富贵**. They appear on the cover, in the first-page title block, in every page footer, in the MusicXML `<creator type="arranger">` and `<encoder>`, and in the PDF metadata. `tools/hollywood` defaults to this; never leave either credit out.
3. **Layout must be refined** (精益求精). Render, look at every page, and fix problems before you deliver (see the QA list below).
4. **The user must be able to find the files without GitHub** (they said 「我不太会用 GitHub」). Every finished work goes into the pinned **编曲交付中心** page, and the first line of your reply is its link: https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN . There, one click saves a zip to the computer's Downloads folder. Never tell the user to look for files on a branch.
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

## Instrumental works and parts

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
- **Repeats**: written out (`FORM`), so the second time can be scored
  differently and the MIDI needs no unrolling; `ALIAS` reuses a strain's
  data for its reprise.

## Song-specific style values

`META["style"] = {"measureSpacing": 1.3}` (and `META["part_style"]` for the
parts) replaces or adds keys of the house style for one piece only;
`render_pdf` writes a temporary copy of `hollywood.mss`.  Use it sparingly:
the house values are the standard.

## Choosing system breaks (3 systems per page)

On 11 × 17 at 7.2 mm staves:

- **Width**: an intro with long notes fits 4 bars per system. A lyrical passage with some 16ths in the voice fits 3. Passages with 16ths in the voice **and** 16th strings fit 2.
- **Height**: 5 staves + lyrics = one system. The first page holds the title block + 3 systems; the other pages hold 3.
- Count the systems and make the total a multiple of 3 (page 1 counts as 3). Move one break if the last page would get 1–2 lonely systems. Start systems at rehearsal letters where possible.
- Explicit breaks that are too full make MS4 wrap a bar on its own. If you see a one-bar system, take a bar out of that system.
- To see the real layout without eyeballing every page, read the boxed bar
  numbers back from the PDF: `pdftotext -bbox <pdf> -` gives each number's
  position; group them by y (systems are 100+ pt apart) to list the bars of
  every system on every page.  A lowered `measureSpacing` does not help when
  the systems are already at their minimum width; take bars out or make
  them narrower.
- Instrumental 2/4 music (the string quartet): Mozart's 8-bar phrases fit one
  system; 16th-note passages 4 bars; the first system (full instrument
  names) holds about 6.

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
- The boxed bar numbers sit above every bar, so a rehearsal letter and its bold section title would share their row and run into the section's first bar number ("A Chorus 副歌 [10]"). `render_pdf` lifts both by 5 spaces onto their own row (`_lift_sections`). MS4 ignores `default-y` from MusicXML, so the offset is written into the imported `.mscz`. Set `META["section_lift"] = 0` to turn it off.
- `render_pdf` also sets the Chinese in staff texts ("Chorus 副歌") in Noto Serif CJK SC (otherwise MS4 falls back to WenQuanYi Zen Hei, a sans) and labels 8va lines "8va" (MS4 imports them as a bare "8" and `-S` does not reset that). `polish_musicxml` makes rehearsal letters bold.
- Letter-spaced cover lines need `padding-left` equal to their `letter-spacing`, or they sit left of the page axis (CSS adds the spacing after the last glyph too).
- music21 writes the tempo words and the metronome as two directions. Use `tempo_text` so they print as one mark.
- The cover and header are an HTML page printed by headless Chromium on a transparent background and merged onto the MS4 pages. Page size must stay 11 × 17 in on both sides.
- EB Garamond has no ♩ ♭ ♯; `hollywood._sym` wraps them in a fallback font.
- MuseScore 3 (`mscore3`) cannot read this style. The Hollywood PDF needs MuseScore 4.

## Delivery center (编曲交付中心)

The page is `tools/deliver/center.html`, published at https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN and pinned in the user's claude.ai sidebar.

- It lists the works from its database: collection `works`, one document per work, sorted newest first.
- It serves each work's files from `files/<slug>/`.
- 「下载到电脑」 builds `<歌名>_编曲交付.zip` in the browser from `bundle.json` and saves it through the `downloads` capability. The zip has `说明.txt`, `1_四样主文件/` and `2_其他文件/`. (The artifact host refuses to serve .zip, .mid or .musicxml files, so small files travel base64 inside `bundle.json`; PDF, mp3, mp4, png and fonts are served as themselves.)
- 「全部歌曲一次下载」 merges every song into one zip.
- 「选择文件」 opens a file browser inside the card. Folders are collapsed; clicking a folder's name opens it. Every folder and file has a checkbox and its own 下载 / 删除; the bar at the bottom downloads or deletes the selection, and 「删除整个…」 deletes the whole work.
  - The save dialog only takes some types (pdf, zip, mp4, txt, json, png, jpg …). A single MIDI / MusicXML / mp3 / srt goes out as `<name>.zip`; several files go out as one zip.
  - Every delete opens an in-page confirmation first (`window.confirm` is blocked in artifacts).
  - Deletes never touch the published files. They go on the work's db row: `removed` holds paths relative to the bundle's top folder, and `deleted: true` hides the whole work. The 「已删除」 section at the bottom restores either.
  - Deleted files are left out of every zip, and the PDF / video buttons hide when those files are removed.

To add or update a work, after its files are built and committed:

1. Add or edit its entry in `tools/deliver/catalog.py`.
   - `ref=None` means "the current working tree", i.e. the song you just built.
   - Fill in `main` (the four files), `pdf_kind` (`"hollywood"` for the tools/hollywood PDF), `audio`, and the open questions for the user.
2. `python3 tools/deliver/package.py <slug> --files`. This prints the `files` map to publish. Output goes to `tools/deliver/dist/`, which is git-ignored.
3. `Artifact` `action: "read"` on the URL. A publish from a new conversation is refused until you have read it.
4. `Artifact` publish:
   - `url` = the page URL;
   - `file_path` = `tools/deliver/center.html`;
   - `files` = the printed map.
   Files you leave out are kept. Omit `capabilities` and `icon` so they stay as they are.
5. `ArtifactData` `set` on collection `works`, doc_id `<slug>`, `file_path` = `tools/deliver/dist/rows/<slug>.json`. If the document already exists, `get` it first and pass its `version` as `if_version`. Also carry over its `removed` and `deleted` fields into the new row, because those are the user's own deletions. Drop them only if the user asked to bring the files back, or if the new bundle no longer has those paths.
6. Refresh the fallback list: `ArtifactData` `list` on collection `works` with `out_dir` = a scratch dir, then `python3 tools/deliver/package.py --snapshot <dir>` and publish the printed `files/works.json`. The page shows this snapshot when its database does not answer.
7. Reply to the user with the page link first, then what changed.
8. Commit (including `catalog.py`), push, open a PR to `main`, and merge it.

Whenever you edit `center.html`, check that its script still parses before publishing. One syntax error and the page shows no songs and no download buttons at all:

```bash
python3 -c "s=open('tools/deliver/center.html',encoding='utf-8').read(); open('/tmp/page.js','w').write(s[s.index('<script>\n')+9:s.rindex('</script>')])" && node --check /tmp/page.js
```

Shell commands inside a JS template literal (`MAC_CMD`) must escape `${` as `\${`; an unescaped `${p%/…}` broke the page once.

### Mac Dock app

The user asked for the delivery center as an app in the Mac Dock. The card below the song list, 「放进 Mac 程序坞」 (collapsed by default so the songs come first), handles it:

- 「下载 Mac 应用」 saves `编曲交付中心_安装包.zip`. It contains a ready-made `编曲交付中心.app` (a shell-script launcher with the icon), `安装.sh`, and `安装说明.txt`.
- 「复制安装命令」 copies a one-line `bash -c '…'` command. The command finds the newest download in `~/Downloads`, which is the zip for Chrome and the unpacked folder for Safari, and runs `安装.sh`.
- `安装.sh` does the rest:
  - builds a native applet with `osacompile` (`open location "<page URL>"`), so there is no Gatekeeper prompt and no Rosetta;
  - swaps in the icon (removes `Assets.car` and `CFBundleIconName`) and re-signs it ad hoc;
  - copies it to `/Applications` (or `~/Applications`);
  - adds it to the Dock unless it is already there, then opens it once.
- Without the Terminal, the user can drag the ready-made app into Applications. It is unsigned, so the first launch needs 「系统设置 → 隐私与安全性 → 仍要打开」. Safari 「文件 → 添加到程序坞…」 is the other fallback.

The source is `tools/deliver/macapp/`: `build.py`, `install.sh`, `安装说明.txt`, `icon.svg`, `AppIcon.png` and `AppIcon.icns`. The app only opens the page URL, so it never needs rebuilding for new songs. Rebuild it only if the page URL, the scripts or the icon change:

```bash
python3 tools/deliver/macapp/build.py          # add --icon to redraw the icon (Playwright + Chromium)
```

Pitfalls, learned on the user's Mac:

- macOS `/bin/bash` is 3.2. In UTF-8 locales it treats bytes 0x80–0xFF as letters, so in `"「$NAME」"` the first byte of 」 becomes part of the variable name, and the output shows 「??. Write `${NAME}` whenever Chinese text follows a variable. To reproduce on Linux, build a Latin-1 locale with `localedef -i en_US -f ISO-8859-1 <dir>/en_US.ISO-8859-1` and run with `LOCPATH=<dir> LC_ALL=en_US.ISO-8859-1`.
- The 'already in the Dock' check reads only `persistent-apps` (via `plutil -extract`). The app also shows up in `recent-apps`, which must not count.
- `MAC_CMD` sorts downloads with `ls -tdc`, because unzipping back-dates mtimes. It accepts only `*.zip` and `*/安装.sh`, skipping partial downloads. It also runs `ls .` first, so a Terminal that is denied the Downloads folder gets a real message and not 「没找到安装包」.

Then publish `center.html` with the printed `files` map (`files/macapp/app.json`, `files/macapp/icon.png`). The install command itself lives in `center.html` as `MAC_CMD`.

Works that live on other branches keep their branch name as `ref`. `package.py` reads them with `git archive`, so fetch first: `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`.
