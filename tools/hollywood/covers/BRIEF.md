# Cover studies for 《我和我的祖国》 full score — design brief

The brief the eight studies were made from (2026-10-02).  Working dir
`tools/hollywood/covers` (below: `$C`); renders go to `/tmp/covers-out/<id>/`
(`$COVERS_OUT`).  Fonts first: `python3 $C/fonts.py`.  Read `lib.py` and
`render.py` (both short).

## Why we are doing this

The user (Chinese; arranger signing as 花开当富贵) looked at the current
cover (`previews/00_classic.jpg`: white page, double-rule frame, centred
black serif type) and said: 「这个封面缺少更多的审美和艺术感，请你结合标题以及我喜欢的
感觉多给我几版参考，是否可以丰富颜色以及排版？参照世界的大师的风格给我设计几版好看的封面。」
So: more aesthetic and artistic feeling, richer colour and layout, inspired by
world-class master designers, rooted in the title and in what the user likes.
Each study is an **homage to one master's visual language**, re-imagined for
this song: not a copy of a specific poster, and never signed as that master.

## What the user likes (evidence, use it)

- Standing words: 「精益求精」「要看精致」「好莱坞标准」; about music: 「简单而高级」
  (simple bones, sophistication from colour). Expect the same from a cover:
  refined, premium, nothing cheap, nothing cluttered or clip-art.
- For this song's National Day video the user chose, out of several, a layout
  they called 「排版和字体都不错」: warm paper `#F6EFE4`, warm ink `#3E372F`,
  vermilion/cinnabar `#B7472A` accents, a big bold Noto Serif CJK title, wide
  letter-spaced small credits, and a **small standard national flag as a
  header ornament (「题头小旗」)**. (`lib.PAPER/INK/CINNABAR`, `lib.flag_svg`.)
  They also had a red-and-gold variant offered. They like the 「编曲手记」look:
  ink + cinnabar only.
- The interior pages are black-on-white Hollywood engraving with EB Garamond +
  Noto Serif CJK headers/footers. A cover that shares some typographic DNA
  with that is a plus, but the cover may be far bolder.

## The song (use its meaning; 「结合标题」)

- 《我和我的祖国》, 1985, music 秦咏诚, lyrics 张藜, first sung by 李谷一.
  This arrangement: complete song for vocal quartet (S.A.T.B. soli, one singer
  each) and string quartet, E♭ major, 6/8 (two 9/8 bars), dotted-crotchet = 56,
  ca. 2'51", 73 bars; lilting, rocking like a boat / like waves.
- Lyrics imagery (quote at most one short line, lyrics are by 张藜):
  「我和我的祖国，一刻也不能分割」— I and the motherland, inseparable.
  「我歌唱每一座高山，我歌唱每一条河；袅袅炊烟，小小村落，路上一道辙」— mountains, rivers,
  chimney smoke, villages, a wheel-rut on the road.
  「我的祖国和我，像海和浪花一朵」— the sea and one wave-spray: **I am the spray,
  the motherland is the sea**. 「浪是那海的赤子，海是那浪的依托」. 「我就是笑的漩涡」(a whirl).
  「你用你那母亲的脉搏和我诉说」(the mother's pulse). 「永远给我碧浪清波，心中的歌」.
- The arrangement's own idea: women's voices = the spray, men's voices = the
  sea; the viola sings the theme first; cello pizzicato = the heartbeat on
  「脉搏」; violins whirl in 16ths on 「漩涡」.
- Strong visual seeds: the small 「我」 and the vast 「祖国」; one spray on a vast
  sea; mountains and rivers; 6/8 groups of three like swells; a heartbeat.

## Required content (all text comes from `m`, the META dict; don't hard-code it)

Every item of the house cover standard must be on the page, as **real text**
(HTML/SVG text, never outlined paths or images of text):

1. `FULL SCORE` and `Score in C · Concert Pitch`.
2. The title `m["title"]` (我和我的祖国). You may set the big title creatively
   (vertical, split, different sizes), but the exact string must also appear
   **contiguously on one horizontal line at least once** (a small line is fine).
3. `m["title_latin"]` (pinyin), `m["subtitle"]` and `m["subtitle_en"]`.
4. The credit rows from `lib.credit_rows(m)`: 作曲 / 作词 / 原唱 / 改编 / 制谱 with
   names. **改编 and 制谱 must each sit on one horizontal line with the name
   花开当富贵 to the right of the label** (the repo's `qa.py` checks exactly
   that); the English labels are welcome. Both 花开当富贵 rows are mandatory.
5. `m["key"]`, `m["tempo"]`, `m["duration"]` (wrap with `lib.sym()`: ♭ ♩ need
   a fallback glyph), and the instrumentation `m["instrumentation"]` (English +
   Chinese).
6. 花开当富贵 once more as the signature at the foot, with
   `Arrangement & Music Preparation · 2026` (year from `m["year"]`). A seal
   (印章) style signature is welcome as long as the text is real text.

`render.py` checks all of this and prints PROBLEM lines; fix every one.

## Red lines (non-negotiable)

- No maps, no outline of China, no national emblem, no Tiananmen, no leaders,
  no military/parade imagery, no hammer-and-sickle or propaganda pastiche, no
  photos, no people/figures.
- The national flag may appear ONLY via `lib.flag_svg()`: whole, flat,
  upright, opaque, small, with nothing on top of it, never cropped, never a
  faded background, never under a texture. Only design `lv` may use it.
- Never a red disc on a white/pale field and never red-and-white radiating
  rays (reads as the Japanese flags: offensive in this context). Gold or
  pale rays on a deep ground, kept restrained, are fine.
- No 'AI' / 'ACE' wording. No real brand logos.
- Keep all text ≥ 0.35 in from the trim edges (checked). Backgrounds and art
  may bleed off the edges.

## Technical

- Page: 11 × 17 in portrait. `lib.page(css, body)` gives you the @page size,
  the fonts and a reset; position things absolutely inside `.page` in inches.
- Fonts (all bundled/installed, no network). CJK: `'Noto Serif CJK SC'`
  (weights 200 300 400 500 600 700 900), `'Noto Sans CJK SC'` (100–900),
  calligraphy `'Ma Shan Zheng'` (楷/行), `'Zhi Mang Xing'` (行草),
  `'Liu Jian Mao Cao'` (草), `'Long Cang'` (行), `'LXGW WenKai'` (文楷, 400/500),
  `'ZCOOL XiaoWei'` (elegant display serif), `'ZCOOL QingKe HuangYou'` (bold
  display). Latin: `'EB Garamond'`, `'Cormorant Garamond'`, `'Cormorant'`,
  `'Playfair Display'`, `'Bodoni Moda'`, `'GFS Didot'`, `'Libre Baskerville'`,
  `'Noto Serif Display'`, `'DM Serif Display'`, `'Instrument Serif'`,
  `'Fraunces'`, `'Abril Fatface'`, `'Cinzel'`, `'Cinzel Decorative'`,
  `'Marcellus'`, `'Italiana'`, `'Poiret One'`, `'Josefin Sans'`, `'Jost'`
  (Futura-like), `'Inter'` (Helvetica-like), `'Archivo'`, `'Archivo Black'`,
  `'Space Grotesk'`, `'Syne'`, `'Unbounded'`, `'Oswald'`, `'Bebas Neue'`,
  `'Big Shoulders Display'`; `'DejaVu Sans'` for symbols. Latin fonts have
  static weights 100–900 where the family has them.
- Draw art as inline SVG (paths, gradients, patterns) and CSS. Chromium prints
  vector shapes and gradients as vectors; CSS/SVG filters, blur, blend modes
  and feTurbulence get rasterised: allowed, but zoom in (≥ 150 dpi) and check
  they are not blurry or banded, and keep the PDF < 6 MB (checked).
- Each design is ONE self-contained file `$C/designs/<id>.py` (stdlib +
  `import lib` only) with `def render(m) -> str`. When several designers work
  in parallel, each edits only its own design file (lib.py, render.py and
  fonts.py are shared).

## Process (do all of it)

1. Think like the master: study what makes their language recognisable
   (grid, colour, shape vocabulary, type) and what a cover in that language
   would say about THIS song. Pick one strong idea, not five.
2. Write `designs/<id>.py`, run `python3 $C/render.py <id>`, then LOOK at
   `/tmp/covers-out/<id>/cover.png` with the Read tool (it is rasterised from the PDF).
3. Zoom where detail matters: `python3 $C/render.py <id> --zoom X0,Y0,X1,Y1`
   (inches; e.g. `1,1,10,6` for the title area, `1.5,9,9.5,14.5` credits,
   `2,14,9,16.6` the foot) then Read `/tmp/covers-out/<id>/zoom.png`.
4. Iterate at least three full rounds as a demanding art director: hierarchy,
   alignment to a real grid, optical centring of letter-spaced lines (pad-left
   = letter-spacing), kerning of big CJK type, colour harmony and contrast,
   breathing room, nothing clipped or colliding, Chinese and Latin type
   pairing, does it look *expensive*, does it look like the master, does it
   speak of this song. Fix every PROBLEM line from render.py.
5. Finish only when you would show it to a design director with pride.

## What to return

The structured result: your id, the master, a short 方案名 (4–8 Chinese
characters), a Chinese concept text for the user (3–5 sentences, plain words:
which master, what the image means for this song, colours and type), the
palette (name + hex), the fonts used, your honest self-score (1–10) and the
remaining weaknesses.
