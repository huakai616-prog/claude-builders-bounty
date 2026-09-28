# 交接说明（写给接手的 AI：GPT / Codex / Claude）

先读完这一页再动手。用户说中文，回复用中文，简洁直接。

## 这个仓库现在做什么

仓库名叫 claude-builders-bounty。根目录的 `README.md`（悬赏板）和 `LICENSE` 是早期留下的，跟现在的工作无关，不要改。

现在的实际用途是**把流行歌的副歌编成「人声 + 弦乐」**。流程是：用户发一张简谱截图，AI 转写旋律和歌词，写弦乐伴奏，然后交付：

1. 西贝柳斯能打开的总谱（MusicXML）；
2. 带逐字歌词的人声 MIDI，给 ACE Studio 合成人声用；
3. 配套文件：全轨 MIDI、弦乐 MIDI、PDF 预览、试听 mp3、歌词字幕。

用户在自己的 Mac 上用西贝柳斯看谱，用 ACE Studio 做 demo（AI 人声 + AI 弦乐）。

## 项目地图

| 歌 | 编制 · 调 · 速度 | 分支 | 目录 | 状态 |
|---|---|---|---|---|
| 泪海（副歌，许茹芸） | 人声 + 弦乐四重奏 · F 大调 · ♩=59 | `claude/elegant-pascal-83rncr`（已合并进 `main`） | `leihai/` | 已完成。待确认副歌唱一遍还是两遍，待在 ACE Studio 渲染 |
| 情歌（最后一遍副歌，梁静茹） | 人声 + 弦乐四重奏 · F 大调 · ♩=70 | `claude/serene-darwin-2l4jy4` | `qingge/` | 已完成。只唱一遍（用户图 3 那段），加了前奏和尾奏。2026-09-28 按用户发回的 MIDI 修订：弦乐照用户版，人声带 3 个 br 气口。待在 ACE Studio 渲染 |
| 甲乙丙丁（副歌，李佳薇） | 人声 + 弦乐五重奏 · F 大调 · ♩=65 | `claude/loving-bell-wsnmgy` | `jiayibingding/` | 已完成，另有字幕和 Clawd 动画视频片段 |
| 茉莉花 | 人声 + 弦乐五重奏 · F 大调 | `claude/sleepy-wozniak-g09dmt` | `jasmine-flower/` | 已完成，交付的是单个 `.mxl` |
| Clawd 弹钢琴动画 | — | `claude/focused-volta-ve5ka6` | `claude-piano-pet/` | 5 秒循环动画 |

- `codex/issue-2-…` 和 `codex/issue-3-…` 两个分支是悬赏板的任务，跟音乐无关。
- 除泪海外，以上分支都还**没有合并进 `main`**。合并以后记得更新这张表。
- 每首歌的目录里都有自己的 `README.md`，写了结构、编配思路、时间轴和导入步骤。改哪首歌就先读哪首的。
- 仓库是公开的，谁都能看到这些文件。

## 交付硬性要求（用户明确要求，每次都必须做到）

1. **西贝柳斯工程**：交 MusicXML（`.sib` 只能在西贝柳斯里另存，外部生成不了，回复里要说明「打开后另存为 .sib」）。
2. **PDF 总谱按好莱坞标准制作，要有封面**，排版要精益求精、看起来精致：
   - 封面：曲名、副标题、Full Score / Score in C、词曲原唱、改编、制谱、编制、调和速度、时长。
   - 正文：首页标题区和「Score in C」，每小节都有小节号，排练号加框并在人声和弦乐上方各出现一次，速度和表情记号清楚，从第 2 页起每页有页眉（曲名 + 页码），首页页脚写署名。
   - 用 LilyPond 排版（`engrave.py`），不用 MuseScore 的预览 PDF。交付前逐页出 PNG 自己看一遍，有碰撞、挤压、空白过多就改。
3. **改编和制谱一律署名「花开当富贵」**：PDF 封面和首页、MusicXML 的 arranger 和制谱信息都要写。
4. **MIDI 至少两份**：一份弦乐总的（所有弦乐声部在一个文件里），一份人声带逐字歌词的。其他 MIDI（全轨、GBK 备用、不带歌词的人声）可以额外附上。

## 用户怎么提需求

- 典型原话：「给图二副歌像之前一样写弦乐伴奏，这次要弦乐四重奏，1小提，2小提，中提，大提，和弦简单而高级，综艺编曲抒情高燃风格，我需要西贝柳斯工程，带歌词的人声midi」。中途追加过：「最终呈现改成F大调」。
- 「像之前一样」：沿用上面这些项目的套路，即 `build.py` 单一数据源、同一组输出文件、中文 README。
- 调：用户指定最终调就整体移过去（泪海原谱 1=D，交付 F）。目前所有歌都是 F 大调（情歌的简谱本身就标了「女调 F」）。
- 「和弦简单而高级」：骨架用常见进行，例如下行低音 1–7–6–5–4–3–2–5。高级感靠色彩和弦：add9、maj7、sus4、转位（slash chord）、借用的小四级（iv / m6），以及 ♭VI–♭VII–I。
- 「综艺抒情高燃」：
  - 织体层层加码：长音 → 八分分解和弦 → 十六分律动。
  - 高潮前留一拍弦乐全停让人声清唱，下一拍全奏落地。
  - 结尾渐宽、渐慢。
- 用户说「图二」但只传了一张图时，就用那张图，并在回复里说明。
- **用户嫌每次从聊天里下载文件麻烦**。生成的文件一律提交进仓库的 `output/` 目录，不要只作为聊天附件发。

## 从简谱图到交付

1. **转写**。放大截图逐小节读，规则如下：
   - 下划线数定时值：一条线是八分音符，两条线是十六分音符。
   - 数字下方有点是低八度，上方有点是高八度。中音区的 1 记在第 4 八度，例如 1=D 时 1 是 D4。
   - 弧线连同音是连音线，连不同音是圆滑线（拖腔，一个字唱多个音）。
   - 数字左上角的小字是倚音。
   - 歌词对齐到音符。
   - 每小节加起来必须正好 4 拍。
2. 移到用户要的调，检查人声音区。
3. 先定和声骨架（每半小节一个和弦），再写声部。弦乐的旋律只在人声的长音和气口里动，不抢词。
4. 把数据写进 `build.py`，运行 `--check` 直到没有任何输出，再生成文件。
5. 渲染 PDF 和 PNG，自己看一遍排版。
6. 写目录 README，提交并推送。

## 交付物（每首歌一个目录，以泪海为例）

| 文件 | 用途 |
|---|---|
| `leihai/output/泪海_副歌_人声弦乐四重奏.musicxml` | 西贝柳斯用。`.sib` 只能在西贝柳斯里另存，外部生成不了，所以交 MusicXML，并用 MusicXML 4.0 schema 校验 |
| `…_人声_带歌词.mid` | 人声 MIDI，UTF-8 歌词，拖腔音符写 `-` |
| `…_人声_带歌词_GBK编码备用.mid` | 有些软件读 UTF-8 歌词会乱码，给一份 GBK 编码的备用 |
| `…_人声_素.mid` | 不带歌词的人声 MIDI |
| `…_全轨.mid` | 给 ACE 用。音轨名为 `Vocal 人声` / `Violin I` / `Violin II` / `Viola` / `Violoncello` |
| `…_弦乐四重奏_伴奏.mid` | 只有弦乐声部 |
| `…_总谱.pdf` | **好莱坞标准总谱，带封面**，LilyPond 排版（`engrave.py` 生成），署名「花开当富贵」 |
| `粗略试听_GM音色_非ACE效果.mp3` | FluidSynth + GM 音色渲染，只用来核对音符 |
| `…_歌词字幕.srt` | 歌词字幕，时间从第 1 小节算起 |

## 怎么改、怎么验证

```bash
pip install music21 mido
python3 leihai/build.py --check   # 只检查：音域、小二度/小九度冲突（含人声）、平行五八度
python3 leihai/build.py           # 生成 output/ 下的 MusicXML / MIDI / SRT，并回读核对每小节 4 拍
```

- 乐谱数据全写在 `build.py` 里：每个声部一个 dict，每小节一个字符串，时值以十六分音符为单位。
- token 语法见文件开头的 docstring：
  - `C5/2` 八分音符，`D4+F4/8` 双音，`r/4` 休止；
  - `~` 连音线，`>` 重音，`( )` 圆滑线；
  - `=字` 歌词，`g:G4` 倚音。
- 改完必须先 `--check` 干净（没有 RANGE / CLASH / PARALLEL 输出），再生成。
- **PDF 总谱用 `engrave.py`（LilyPond）生成**，它读同一份 `build.py` 数据，排出带封面的好莱坞标准总谱（模板见 `qingge/engrave.py`，新歌复制过去改顶部的换行、排练号和时长设置）。Ubuntu 上先装 `apt-get install lilypond fonts-noto-cjk fonts-texgyre` 和 `pip install fonttools`，然后 `python3 qingge/engrave.py --png /tmp/pg`，逐页看 PNG，确认没有碰撞、超出页边、单独一行被拉满整页。
- 署名（改编、制谱：花开当富贵）写在 `build.py` 顶部的 `ARRANGER` / `ENGRAVER`，MusicXML 首页的 credit 和 PDF 都从这里取。MusicXML 首页的 credit 每个位置只放一个多行文字块，分开写会被导入软件叠在一起。
- mp3 不在 `build.py` 里，需要另外渲染。泪海的 PDF 还是旧的 MuseScore 预览（下面的命令），以后重做时换成 `engrave.py`。Ubuntu 上先装 `apt-get install musescore3 fluidsynth fluid-soundfont-gm ffmpeg`，然后：

  ```bash
  cd leihai/output
  QT_QPA_PLATFORM=offscreen mscore3 -o 泪海_副歌_总谱预览.pdf 泪海_副歌_人声弦乐四重奏.musicxml
  fluidsynth -ni -g 0.6 -F /tmp/p.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 泪海_副歌_人声弦乐四重奏_全轨.mid
  ffmpeg -y -i /tmp/p.wav -af loudnorm=I=-16:TP=-1.5 -b:a 160k 粗略试听_GM音色_非ACE效果.mp3
  ```

- 看排版：`mscore3 -o page.png …` 按页出 PNG。PNG 是透明底，看之前先铺白底。
- MusicXML 合法性以 `xmllint --noout --schema musicxml.xsd …` 为准：
  - schema 取 w3c/musicxml 仓库的 `schema/musicxml.xsd`；
  - 它 import 的 `xml.xsd` / `xlink.xsd` 要在本地放一份，或者写最小的桩；
  - MuseScore 3 的「not a valid MusicXML file」提示不可靠，不要以它为准。

## 踩过的坑

- **music21 插入顺序**：往 Measure 里先 `insert` 零时值元素（TempoText 等），再 `append` 音符，音符会从那个偏移之后开始排，整小节错位。文字、力度、速度字一律在音符之后插入。泪海第 24 小节出过这个 bug，现在 `verify_bars()` 会拦住。
- **MusicXML 元素顺序**：`<score-instrument>` 里的 `<instrument-sound>` 必须放在 `<instrument-abbreviation>` 之后，否则不合法。
- **延长记号**：`<fermata>` 不能带 `placement` 属性，4.0 schema 不允许。
- **排版**：A4、6 mm 谱表时，含十六分音符的段落一行放 3 小节。强行放 4 小节，会有一小节被挤到下一行单独一行。换行由 `polish()` 里的 `SYSTEM_BREAKS` 控制。
- **人声长音附近的弦乐**：弦乐和人声的长音不要构成小九度。例如人声 C4 持续时，B♭m6 的 D♭ 只能放在 C4 下面，放在上面就成了小九度。`--check` 会抓出来。
- **歌词 MIDI**：每个字一个 lyrics meta 事件；拖腔音符写 `-`；倚音带那个字，主音写 `-`。
- **简谱的高音点不一定是实际八度**：情歌的简谱把副歌整段写在高音点上，照字面是 F5–C6，女声唱不了。按实际演唱音高放（女声副歌大致在 C4–D5），同时保留谱里点与点之间的相对高低。
- **原曲自带的不协和**：前奏钩子里的倚音这类原曲本来就有的小九度，写进 `CLASH_ALLOW` 白名单并在 README 说明，不要为了过检查去改原曲旋律。
- **LilyPond 的中文字形**：LilyPond 2.24 读 `.ttc` 字体集合时忽略字形编号，永远用第 0 个。Noto CJK 的第 0 个是日文，「直」「骨」等字会变成日文写法。`engrave.py` 用 fontTools 把简体中文那一个抽成独立字体（`QG Serif SC` / `QG Sans SC`，缓存在 `~/.cache/qingge-fonts`）。字体设置要用 2.24 的 `set-global-fonts`，`property-defaults.fonts` 是 2.25 的写法，2.24 会静默忽略。交付前用 `grep -a -o "/FontName */[A-Za-z+_-]*" 总谱.pdf` 确认没有 `jp` 字体。
- **MusicXML 给西贝柳斯的细节**：music21 写出的十六分音符符杠会在拍中间断开，八分音符按拍分组，和 PDF 不一样；起止落在同一个音上的渐强渐弱线会被丢掉。`build.py` 的 `finish_parts()` 负责重算符杠、按准确位置写渐强渐弱线、拖腔加延长线、渐慢写成 `<sound tempo>`。
- **MusicXML 的记号只挂在音符起点**：力度、渐强渐弱线、文字如果落在持续音中间，就得用 `<backup>/<forward>` 或 `<offset>` 定位，西贝柳斯会因此生成隐藏休止符、另开第二声部或截断音符，看起来像「节奏出错」，MuseScore 则直接丢掉这些记号。`build.py` 的 `_insert_at()` 遇到这种位置会直接报错，这时应在数据里把长音拆成用连音线连起来的几个音。
- **用户发回的 MIDI 优先**：用户在 ACE Studio 里改过的 MIDI 是弦乐的最终版本，照它逐音改 `build.py`，不要自作主张再改回去。人声里 `br` 是用户加的气口，保留并在谱上显示；其余节奏按原谱校准。
- **平行五八度检查**：只比较各声部的最高音。高潮处两把小提琴有意八度齐奏的地方，写进 `check()` 的 `allow` 白名单。

## 待办 / 待确认

- **泪海唱几遍**：副歌目前唱两遍，第一遍抒情，第二遍高燃。用户还没确认要不要只唱一遍。如果只要一遍，把第 14–24 小节换成直接进尾奏的结尾（见 `leihai/README.md` 末尾）。
- **泪海 ACE Studio 渲染**：只能在用户的 Mac 上做（见下一节）。
- **合并分支**：上面的分支是否合并进 `main`，由用户决定。

## ACE Studio（在用户的 Mac 上）

- ACE Studio 和操作它的 AI 必须在同一台机器上，云端环境连不上。
- **命令行（优先用）**：`"/Applications/ACE Studio.app/Contents/Helpers/acestudio-cli"`。路径里有空格，要加引号。用 `help` 参数列出所有命令。
- **MCP server**：命令行被沙盒或权限挡住时才用。可执行文件是 `"/Applications/ACE Studio.app/Contents/Helpers/ace-mcp-server"`，按你自己的 agent 的方式注册。
- **操作知识**：见 https://github.com/BeatMagic/acestudio_agent_plugin 。
- **泪海的渲染步骤**：
  1. 在第 1 小节导入 `leihai/output/泪海_副歌_人声弦乐四重奏_全轨.mid`，保留速度信息（第 24 小节起渐宽、渐慢）。
  2. 「Vocal 人声」轨加载 Vocal Synth，选中文流行女声（抒情、气声多一点）。歌词已经在音符上。如果乱码，改用 `泪海_人声_带歌词_GBK编码备用.mid`。
  3. Violin I / Violin II / Viola / Violoncello 四轨加载 AI 乐器 **String Section**，speaker 分别选 Violins I / Violins II / Violas / Celli。演奏法保持智能模式，这版没有拨弦，也没有弱音器。
  4. 第 15 小节第 4 拍弦乐是故意空着的（人声清唱），不要补。
  5. 确认没有轨被静音或独奏，然后从头播放一遍，让所有轨都渲染。

## Git 约定

- 新工作开新分支提交，提交信息写清楚。不改写别人分支的历史，不 force push。
- 生成的文件（`output/`）要提交进仓库。用户直接从 GitHub 或本地同步的文件夹打开，不想每次从聊天里下载。
- `__pycache__` 已经在 `.gitignore` 里，不要提交。
