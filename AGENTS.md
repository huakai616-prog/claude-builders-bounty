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
| 泪海（副歌，许茹芸） | 人声 + 弦乐四重奏 · F 大调 · ♩=59 | `claude/elegant-pascal-83rncr` | `leihai/` | 已完成。待确认副歌唱一遍还是两遍，待在 ACE Studio 渲染 |
| 甲乙丙丁（副歌，李佳薇） | 人声 + 弦乐五重奏 · F 大调 · ♩=65 | `claude/loving-bell-wsnmgy` | `jiayibingding/` | 已完成，另有字幕和 Clawd 动画视频片段 |
| 茉莉花 | 人声 + 弦乐五重奏 · F 大调 | `claude/sleepy-wozniak-g09dmt` | `jasmine-flower/` | 已完成，交付的是单个 `.mxl` |
| Clawd 弹钢琴动画 | — | `claude/focused-volta-ve5ka6` | `claude-piano-pet/` | 5 秒循环动画 |
| 大东北我的家乡（全曲，何玉） | 迪士尼风格交响乐（Instrument X）+ SATB 合唱 · F 大调，末段副歌转 G · ♩=128 | `claude/determined-archimedes-93zrgx` | `dadongbei/` | 已完成，待在 Instrument X / ACE Studio 渲染 |

- `codex/issue-2-…` 和 `codex/issue-3-…` 两个分支是悬赏板的任务，跟音乐无关。
- 泪海已经合并进 `main`（PR #2），其余分支都还**没有合并**。合并以后记得更新这张表。
- 每首歌的目录里都有自己的 `README.md`，写了结构、编配思路、时间轴和导入步骤。改哪首歌就先读哪首的。
- 仓库是公开的，谁都能看到这些文件。

## 用户怎么提需求

- 典型原话：「给图二副歌像之前一样写弦乐伴奏，这次要弦乐四重奏，1小提，2小提，中提，大提，和弦简单而高级，综艺编曲抒情高燃风格，我需要西贝柳斯工程，带歌词的人声midi」。中途追加过：「最终呈现改成F大调」。
- 「像之前一样」：沿用上面这些项目的套路，即 `build.py` 单一数据源、同一组输出文件、中文 README。
- 调：用户指定最终调就整体移过去（泪海原谱 1=D，交付 F）。目前三首歌都是 F 大调。
- 「和弦简单而高级」：骨架用常见进行，例如下行低音 1–7–6–5–4–3–2–5。高级感靠色彩和弦：add9、maj7、sus4、转位（slash chord）、借用的小四级（iv / m6），以及 ♭VI–♭VII–I。
- 「综艺抒情高燃」：
  - 织体层层加码：长音 → 八分分解和弦 → 十六分律动。
  - 高潮前留一拍弦乐全停让人声清唱，下一拍全奏落地。
  - 结尾渐宽、渐慢。
- 用户说「图二」但只传了一张图时，就用那张图，并在回复里说明。
- 也会要整首歌的大编制，例如：「给这首歌创作一个华丽的适配Instrument X演奏的迪士尼风格的交响乐搭配传统四声部合唱」。
  - **Instrument X** 是 Dreamtonics 的神经网络乐器（不是 ACE Studio 的功能），首发 13 件管弦乐器：Violin 1 / Viola 1 / Violoncello 1 / Contrabass 1、Piccolo 1 / Flute 1 / Oboe 1 / Clarinet in A 1 / Bassoon 1、Horn 1 / Trumpet 1 / Trombone 1 / Tuba 1，另有两支爵士萨克斯。没有竖琴、打击乐、键盘，这些写成可选轨。
  - 每轨一件独奏乐器，用 unison 叠成声部；木管、铜管每轨只写单音。
  - 交付每轨一个 MIDI 加一个 C 调 MusicXML（见 `dadongbei/`）。
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
| `…_总谱预览.pdf` | MuseScore 3 渲染的预览 |
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
- PDF 和 mp3 不在 `build.py` 里，需要另外渲染。Ubuntu 上先装 `apt-get install musescore3 fluidsynth fluid-soundfont-gm ffmpeg`，然后：

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
- **平行五八度检查**：只比较各声部的最高音。高潮处两把小提琴有意八度齐奏的地方，写进 `check()` 的 `allow` 白名单。
- **大编制（`dadongbei/build.py`）**：
  - 伴奏声部由 `CHART` 和声表自动生成。**maj7 和弦的上方声部不能用根音**，否则会在旋律的七音（例如 B♭maj7 里的 A）上方构成小二度。`chord_tones(upper=True)` 已经去掉。
  - 旋律唱 9 音时（例如 Gm7 上的 A），伴奏也不能放三音。那里改用 G11 这类不带三音的和弦。
  - 移调乐器：music21 的 Part 要设 `atSoundingPitch = True`，才会写成记谱音高并带 `<transpose>`。`verify()` 会回读总谱，逐音核对实际音高。
  - 倚音 token 要写在连线括号前面：`g:D6 (C6/2`，不能写 `(g:D6`。
  - 23 行谱表的总谱用 A3、3.7 毫米谱表，不强制换行，MuseScore 第一页才放得下标题和第一行。
  - GM 试听用的 MIDI 不写 CC：几条轨共用一个 GM 通道，CC1、CC11 会互相覆盖。

## 待办 / 待确认

- **泪海唱几遍**：副歌目前唱两遍，第一遍抒情，第二遍高燃。用户还没确认要不要只唱一遍。如果只要一遍，把第 14–24 小节换成直接进尾奏的结尾（见 `leihai/README.md` 末尾）。
- **泪海 ACE Studio 渲染**：只能在用户的 Mac 上做（见下一节）。
- **大东北我的家乡**：在用户的机器上用 Instrument X 渲染乐队、ACE Studio 渲染合唱（步骤见 `dadongbei/README.md`）。目前唱一遍主歌、两遍副歌，要不要照原谱整首唱两遍待确认。
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
