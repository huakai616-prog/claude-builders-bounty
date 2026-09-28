# 交接说明（写给接手的 AI：GPT / Codex / Claude）

先读完这一页再动手。用户说中文，回复用中文，简洁直接。

## 这个仓库现在做什么

仓库名叫 claude-builders-bounty。根目录的 `README.md`（悬赏板）和 `LICENSE` 是早期留下的，跟现在的工作无关，不要改。

现在的实际用途是**把流行歌的副歌编成「人声 + 弦乐」**。流程是：用户发一张简谱截图，AI 转写旋律和歌词，写弦乐伴奏，然后交付：

1. 西贝柳斯能打开的总谱（MusicXML）；
2. 带逐字歌词的人声 MIDI，给 ACE Studio 合成人声用；
3. 配套文件：全轨 MIDI、弦乐 MIDI、PDF 预览、试听 mp3、歌词字幕。

用户在自己的 Mac 上用西贝柳斯看谱，用 ACE Studio 做 demo（AI 人声 + AI 弦乐）。

**用户在「编曲交付中心」找文件**：https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN
- 已经钉在用户 claude.ai 的左侧边栏。
- 每首歌点「下载到电脑」，就得到一个整理好的 zip。
- 用户说过「我不太会用 GitHub」，所以别让用户去 GitHub 或分支里找文件。
- 每次交付都要把作品加进交付中心，回复第一句给这个链接。步骤见 `.claude/skills/hollywood-score/SKILL.md` 的「Delivery center」。
- GPT / Codex 发布不了这个页面，就在回复里写明「请 Claude 把它加进交付中心」。

## 项目地图

| 歌 | 编制 · 调 · 速度 | 分支 | 目录 | 状态 |
|---|---|---|---|---|
| 泪海（副歌，许茹芸） | 人声 + 弦乐四重奏 · F 大调 · ♩=59 | `main` | `leihai/` | 已完成。PDF 是旧版预览，没有花开当富贵署名。副歌唱两遍（用户已在 ACE 渲染、Logic 混音） |
| 甲乙丙丁（副歌，李佳薇） | 人声 + 弦乐五重奏 · F 大调 · ♩=65 | `claude/loving-bell-wsnmgy` | `jiayibingding/` | 已完成，另有字幕和 Clawd 动画视频片段 |
| 茉莉花 | 人声 + 弦乐五重奏 · F 大调 | `claude/sleepy-wozniak-g09dmt` | `jasmine-flower/` | 已完成，交付的是单个 `.mxl` |
| Clawd 弹钢琴动画 | — | `claude/focused-volta-ve5ka6` | `claude-piano-pet/` | 5 秒循环动画 |
| 我不难过（副歌，孙燕姿） | 人声 + 弦乐四重奏 · ♭E 大调（原调） · ♩=68 | `main`（原 `claude/eager-bell-1xpu86`） | `wobunanguo/` | 已完成，副歌唱一遍，带前奏尾奏，好莱坞总谱 PDF（第一首用 `tools/hollywood` 的）。待用户确认谱上几处低八度（见目录 README「转写说明」），待在 ACE Studio 渲染 |
| 情歌（最后一遍副歌，梁静茹） | 人声 + 弦乐四重奏 · F 大调 · ♩=70 | `claude/serene-darwin-2l4jy4` | `qingge/` | 已完成，带封面 PDF（LilyPond 排的 A4，不是 `tools/hollywood` 的 11×17）。有三处八度 / 节奏待用户确认 |
| 茶汤（副歌，郁可唯） | 人声 + 弦乐四重奏 · A 大调（原调） · ♩=112 | `claude/magical-meitner-wj6g5j` | `chatang/` | 已完成，PDF 是旧版预览，没有花开当富贵署名 |
| 大东北我的家乡（全曲，何玉） | 交响乐队（Instrument X）+ SATB 合唱 · F→G · ♩=72/128 | `claude/determined-archimedes-93zrgx` | `dadongbei/`，给用户的成品在 `干活/大东北我的家乡/` | 已完成，待在 Mac 上用 Instrument X 和 ACE 渲染；PDF 没有封面和署名 |
| 泪海 ×《等潮》视频 | 抖音竖屏 · TapNow 分镜与提示词 | `claude/elegant-pascal-83rncr` | `leihai/video/` | 制作包已提交，等用户在 TapNow 里生成镜头 |

- `codex/issue-2-…` 和 `codex/issue-3-…` 两个分支是悬赏板的任务，跟音乐无关。
- 泪海、我不难过、好莱坞模板和交付中心工具在 `main` 上。其他歌还在各自的分支上，但成品都已经放进交付中心（`tools/deliver/catalog.py` 记着每首歌来自哪个分支）。合并以后记得更新这张表。
- 情歌、茶汤、大东北、泪海、甲乙丙丁、茉莉花的 PDF 或署名还没按好莱坞标准重做。用户要的时候，用 `tools/hollywood` 重出，再更新交付中心。
- 每首歌的目录里都有自己的 `README.md`，写了结构、编配思路、时间轴和导入步骤。改哪首歌就先读哪首的。
- 仓库是公开的，谁都能看到这些文件。

## 交付标准（用户的长期要求，每次都照做，不要再问）

用户原话：「给我交付的要西贝柳斯工程，PDF 是要向好莱坞标准来做，要有封面，排版要精益求精、要看精致，改编和制谱都写『花开当富贵』。还要 MIDI 文件，一份弦乐的总的，一份人声带歌词的。」「以后都要像这么做，好莱坞模板你自己总结出一套 skill，下次就不用问我了。」

1. **必交四样**，都提交进 `<歌>/output/`：
   - **西贝柳斯工程**：MusicXML（`.sib` 外部生成不了，要在回复里用一句话说明），通过 MusicXML 4.0 schema 校验；
   - **好莱坞标准总谱 PDF**，要有封面：`<歌名>_副歌_总谱.pdf`；
   - **弦乐总 MIDI**：所有弦乐声部在一个文件里；
   - **人声带歌词 MIDI**，外加 GBK 编码备用版。
   - 其他照旧：全轨 MIDI、人声素 MIDI、试听 mp3、字幕。
2. **署名**：改编、制谱都写**花开当富贵**。封面、首页标题栏、每页页脚、MusicXML 的 arranger / encoder 都要写。
3. **好莱坞模板**：规范和做法都写在 `.claude/skills/hollywood-score/SKILL.md`，工具在 `tools/hollywood/`（`hollywood.py` + `hollywood.mss`）。GPT / Codex 也照这份 SKILL.md 做。要点：
   - 11×17 英寸总谱纸，Score in C；
   - 封面；首页标题栏；每页页眉页脚和「第几页 / 共几页」；
   - 每小节有方框小节号；排练号用字母加框，旁边写段落名；
   - MuseScore 4 排版；尽量每页 3 行，不要单小节一行，最后一页不要只剩孤零零一行。
4. 交付前逐页看 PNG，按 SKILL.md 的检查清单查一遍。

## 用户怎么提需求

- 典型原话：「给图二副歌像之前一样写弦乐伴奏，这次要弦乐四重奏，1小提，2小提，中提，大提，和弦简单而高级，综艺编曲抒情高燃风格，我需要西贝柳斯工程，带歌词的人声midi」。中途追加过：「最终呈现改成F大调」。
- 「像之前一样」：沿用上面这些项目的套路，即 `build.py` 单一数据源、同一组输出文件、中文 README。
- 调：用户指定最终调就整体移过去（泪海原谱 1=D，交付 F）。泪海、甲乙丙丁、茉莉花是 F 大调；我不难过用户没指定，问了之后选的是原调 ♭E。**用户没说调就先问**，别默认 F。
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
| `…_总谱.pdf` | 好莱坞标准总谱：封面 + 总谱，MuseScore 4 排版 + `tools/hollywood` 加封面和页眉页脚（泪海的旧文件还叫 `…_总谱预览.pdf`，是 MuseScore 3 的预览） |
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
- **好莱坞总谱 PDF**：`python3 <歌>/build.py --pdf`（需要 MuseScore 4 和 Chromium，环境准备见 `.claude/skills/hollywood-score/SKILL.md`）。我不难过已经接好，新歌照 `wobunanguo/build.py` 接。
- mp3 不在 `build.py` 里，需要另外渲染。泪海的旧 PDF 预览是 MuseScore 3 出的。Ubuntu 上先装 `apt-get install musescore3 fluidsynth fluid-soundfont-gm ffmpeg`，然后：

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
- **圆滑线从连音线的后半个音开始**（例如 `Bb4/1~=时 (Bb4/1 Ab4/1)`）：泪海版 `merged_notes()` 会漏掉后面拖腔音符的 `-` 歌词。`wobunanguo/build.py` 已修，新歌从它复制。
- **MuseScore 4 排 PDF 的坑**：
  - 直接导入 MusicXML 时 `-S` 样式不生效，要先转成 `.mscz` 再加样式导出；
  - 导入的署名位置会乱（作曲跑到顶上，作词掉进谱里）。
  - 这两个 `tools/hollywood/hollywood.py` 都已经处理了。
  - pypdf 报 `_cffi_backend` 时 `pip install cffi`。
- **转写时注意低八度点**：我不难过的谱上有几处「高音之间突然掉一个八度」的点（「陪」「寞」「看」），照谱写了，但在回复和 README 里单独列出来请用户核对。

## 待办 / 待确认

- **泪海唱几遍**：副歌目前唱两遍，第一遍抒情，第二遍高燃。用户还没确认要不要只唱一遍。如果只要一遍，把第 14–24 小节换成直接进尾奏的结尾（见 `leihai/README.md` 末尾）。
- **泪海 ACE Studio 渲染**：只能在用户的 Mac 上做（见下一节）。
- **合并分支**：用户已经授权：每次交付检查通过后，由 AI 自己开 PR 合并进 `main`，不用再问。别的对话建的旧分支里的歌，合并前要注意 AGENTS.md 冲突，只合并歌曲目录。

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
- **交付完成后自己合并进 `main`**（用户授权过，不用再问）：推送分支，开 PR，合并。新对话只读 `main` 里的规则和工具，不合并的话下次对话就不知道。
- 生成的文件（`output/`）要提交进仓库，同时放进编曲交付中心。用户从交付中心下载，不用 GitHub。
- `tools/deliver/dist/` 是打包中间产物，已经在 `.gitignore` 里，不提交。
- `__pycache__` 已经在 `.gitignore` 里，不要提交。
