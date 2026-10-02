# 交接说明（写给接手的 AI：GPT / Codex / Claude）

先读完这一页再动手。用户说中文，回复用中文，简洁直接。

这一页每次对话都会整页读进来，所以只放每次都用得上的规则。只在某类活里才用到的细节放在单独的文件里，见下面「什么时候读哪个文件」。**往这页加东西之前先想：是不是每次都用得上？不是，就写进对应的文件，这里最多留一行指引。**

## 这个仓库现在做什么

仓库名叫 claude-builders-bounty。根目录的 `README.md`（悬赏板）和 `LICENSE` 是早期留下的，跟现在的工作无关，不要改。

现在的实际用途是**把流行歌的副歌编成「人声 + 弦乐」**（也做过把整首钢琴改编谱改成纯弦乐，见 `docs/钢琴谱改编.md`）。流程是：用户发一张简谱截图，AI 转写旋律和歌词，写弦乐伴奏，然后交付：

1. 西贝柳斯能打开的总谱（MusicXML）；
2. 带逐字歌词的人声 MIDI，给 ACE Studio 合成人声用；
3. 配套文件：全轨 MIDI、弦乐 MIDI、PDF 预览、试听 mp3、歌词字幕。

用户在自己的 Mac 上用西贝柳斯看谱，用 ACE Studio 做 demo（AI 人声 + AI 弦乐）。

**用户在「编曲交付中心」找文件**：https://claude.ai/artifact/He3NTJ1vbPydtB8fRJJjsN
- 已经钉在用户 claude.ai 的左侧边栏。
- 用户要过把它放进 Mac 程序坞：页面底部（歌曲列表下面）的「放进 Mac 程序坞」卡片给一个安装包和一行终端命令，装好后点程序坞图标就用浏览器打开交付中心。用户问怎么装，就指这张卡片（点击顺序、装不上时怎么办见 `.claude/skills/hollywood-score/references/mac-app.md`）。
- 每首歌点「下载到电脑」，就得到一个整理好的 zip。
- 用户说过「我不太会用 GitHub」，所以别让用户去 GitHub 或分支里找文件。
- 每次交付都要把作品加进交付中心，回复第一句给这个链接。步骤见 `.claude/skills/hollywood-score/references/delivery-center.md`。
- GPT / Codex 发布不了这个页面：照 `.claude/skills/hollywood-score/references/delivery-center.md` 开头「GPT / Codex」那段做能做的几步（catalog 条目、打包检查、提交合并），然后在回复里写明「请 Claude 把它加进交付中心」。

## 什么时候读哪个文件

| 什么时候 | 读 |
|---|---|
| 做新歌，或改哪首歌的总谱、PDF、MIDI | `.claude/skills/hollywood-score/SKILL.md`（交付格式和好莱坞模板。Claude 用 skill 加载，GPT / Codex 直接读） |
| 动笔构思新歌之前、写完对照之前 | `docs/编配手法索引.md`（简表：用过两次以上的手法，和每首歌的织体、和声、前奏、高潮、尾奏）；看着撞了再看 `docs/编配手法索引_详细.md` |
| 用户提到某首旧歌，或要改它、确认它的待确认事项、重出它的 PDF | `docs/项目地图.md` 里那一行（编制、调、分支、待确认的事）和「改旧歌时」一节，再读那首歌目录里的 `README.md` |
| 用户发的是五线谱钢琴谱，或要纯器乐 | `docs/钢琴谱改编.md`，再加 `.claude/skills/hollywood-score/references/instrumental.md` |
| 作品做完，要放进交付中心；或用户问交付中心怎么用（选文件、删除和恢复、单个文件为什么下载成 zip） | `.claude/skills/hollywood-score/references/delivery-center.md` |
| 用户问怎么放进 Mac 程序坞、装不上 | `.claude/skills/hollywood-score/references/mac-app.md` |
| 要驱动 ACE Studio，或用户问怎么在 ACE 里渲染（ACE 和操作它的 AI 必须在用户的 Mac 上，云端连不上） | `docs/ACE-Studio.md`（命令行、MCP、泪海的渲染步骤） |

## 项目地图（精简版）

每首歌的编制、调、速度、状态和待用户确认的事项都在 `docs/项目地图.md`。

| 歌 | 目录 | 分支 | 状态 |
|---|---|---|---|
| 泪海（副歌） | `leihai/` | `main` | 已完成，用户已在 ACE 渲染、Logic 混音（唱两遍）；旧版 PDF 没有署名 |
| 甲乙丙丁（副歌） | `jiayibingding/` | `claude/loving-bell-wsnmgy` | 已完成；PDF 不是好莱坞模板 |
| 茉莉花 | `jasmine-flower/` | `claude/sleepy-wozniak-g09dmt` | 已完成，单个 `.mxl`；没有好莱坞 PDF |
| 我不难过（副歌） | `wobunanguo/` | `main` | **反面教材**：用户说难听，**不用再重做**，也不要再重出 PDF、再问它的低八度 |
| 情歌（最后一遍副歌） | `qingge/` | `claude/serene-darwin-2l4jy4` | 已完成，有待确认；PDF 是 LilyPond A4 |
| 茶汤（副歌） | `chatang/` | `main` | 已完成，有待确认 |
| 大东北我的家乡（全曲） | `dadongbei/` | `claude/determined-archimedes-93zrgx` | 已完成，PDF 没有封面和署名 |
| 我和我的祖国（全曲，SATB + 弦乐） | `wohewodezuguo/` | `main` | 已完成，有待确认 |
| 土耳其进行曲（纯器乐） | `alla-turca/` | `main` | 已完成，有待确认 |
| Unravel（纯器乐） | `unravel/` | `main` | 已完成，有待确认 |
| 冬风（纯器乐） | `dongfeng/` | `main` | 已完成，有待确认 |
| 诀别书（纯器乐，弦乐五重奏） | `juebieshu/` | `claude/determined-galileo-0epaj3` | 已完成，已进交付中心 |
| 视频：我和我的祖国 × 国庆抖音 / 泪海 ×《等潮》/ Clawd | `wohewodezuguo/video/`、`leihai/video/`、`claude-piano-pet/` | 见 `docs/项目地图.md` | 国庆抖音成片已做完、已进交付中心；《等潮》等用户在 TapNow 生成镜头 |

- `codex/issue-2-…` 和 `codex/issue-3-…` 两个分支是悬赏板的任务，跟音乐无关。
- 不在 `main` 上的歌，成品也都已经放进交付中心（`tools/deliver/catalog.py` 记着每首歌来自哪个分支）。合并或交付以后，这张表和 `docs/项目地图.md` 都要更新。
- 新歌如果是多个人声声部或 6/8、9/8 这类复合拍子，代码从 `wohewodezuguo/`（`build.py` + `engine.py`）接；单人声 4/4 的从 `chatang/build.py` 接（它有长音上的渐强渐弱修复、`print_hair`、`mscx_hook`、8va）。`wohewodezuguo/engine.py` 还支持 MIDI 里的 br 气口、拨弦/拉弦、延长记号，单人声的歌要用这些也从它抄；那首歌的做法经过两轮多视角审稿。
- 每首歌的目录里都有自己的 `README.md`（茉莉花除外，只有 `generate_score.py`），写了结构、编配思路、时间轴和导入步骤。改哪首歌就先读哪首的。
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
4. 交付前先跑 `python3 tools/hollywood/qa.py score <PDF> -v`，把它报的问题改掉；再逐页看 PNG：`qa.py pages <PDF> <草稿目录>` 出图并列出要看的页，看完照它打印的命令（`qa.py seen --round K <草稿目录>`）记下；每个 PDF 用自己的草稿目录。之后每轮只列出还没看过的页（和看过的某一版一模一样的页不用重看；没标记看过的页每轮都会再列出来），所以交付时每一页的最终版都看过。按 SKILL.md 的检查清单查一遍。

## 用户怎么提需求

- 典型原话：「给图二副歌像之前一样写弦乐伴奏，这次要弦乐四重奏，1小提，2小提，中提，大提，和弦简单而高级，综艺编曲抒情高燃风格，我需要西贝柳斯工程，带歌词的人声midi」。中途追加过：「最终呈现改成F大调」。
- **「像之前一样」只指交付方式，不指音乐。** 交付方式是：`build.py` 单一数据源、同一组输出文件、好莱坞 PDF、中文 README、放进交付中心。**音乐（织体、和声、配器、结构、前奏尾奏）每首歌都要从这首歌本身重新构思，不许照搬以前的歌。**
  - 用户原话（我不难过之后）：「我说跟之前一样，是像之前一样的交付方式，没叫你写的也跟泪海一样。你的这个织体和和弦都有很多跟泪海一样的，很奇怪。做得很难听。你一定要在记忆里知道、理解我话的意思。我叫你做一样的，要你自己长脑子，让音乐变得好听。」
  - 用户夸「泪海的弦乐写得很不错」，意思是水准要到那个程度，不是让下一首长得像泪海。
  - 我不难过错在哪（别再犯）：几乎逐项复制了泪海。前奏长音铺底加第一小提琴唱钩子；中提琴八分音符「波浪」分解和弦；两把小提琴三度、六度双线；高潮前一拍弦乐全停；♭VI–♭VII–I「燃点」；尾奏 maj9 → m6 → I(add9) 加半音下行；连「层层加码」的分工表都一样。README 里甚至写了「和泪海结尾同一个燃点进行」。
- **动笔前先想这首歌**：
  1. 原曲本来的编曲、律动、速度感、情绪起伏和歌手的气质是什么（孙燕姿不是许茹芸，快歌不是慢歌）。
  2. 这首歌的旋律和歌词里有什么独特的东西，可以让弦乐来放大（节奏型、特别的音程、某个字、某个转折）。
  3. 写下这首的编配构想：织体用什么、和声色彩走什么方向、高潮怎么来、前奏尾奏的点子从哪里来。在回复和 README 里说清楚，这首和以前的作品有什么**不同**。
  4. 下笔后对照已经做过的歌：读 `docs/编配手法索引.md`（用过两次以上的手法，和每首歌的织体、和声、前奏、高潮、尾奏、标志性手法），同一个手法不要连着出现；真用到了常见手法，要能说出为什么这首歌需要它。看着撞了，先看 `docs/编配手法索引_详细.md` 那首歌的一节，还拿不准再读它的 `README.md`「编配思路」（不在 `main` 上的歌用 `git show origin/<分支>:<目录>/README.md`）。
  5. 渲染试听 mp3 自己回头检查，问的是「好不好听、像不像这首歌」，不只是「有没有冲突和平行」。`--check` 干净只说明没有错音，不说明好听。
- 调：用户指定最终调就整体移过去（泪海原谱 1=D，交付 F）。泪海、甲乙丙丁、茉莉花是 F 大调；我不难过用户没指定，问了之后选的是原调 ♭E。**用户没说调就先问**，别默认 F。
- 下面两条是**用户用词的意思**，是方向，不是每首都套的公式：
  - 「和弦简单而高级」：骨架好懂、好唱，高级感来自色彩（add9、maj7、sus4、转位、借用和弦等）。具体用哪些、放在哪，要看这首歌的旋律。泪海用过的那一套（下行低音 1–7–6–5…、借用 iv/m6、♭VI–♭VII–I）别再原样搬。
  - 「综艺抒情高燃」：情绪有明显的起伏和高潮，弦乐有推进感。怎么推进，每首歌自己设计：律动、音区、配器密度、节奏型、对位、转调等都可以用，不一定是「长音 → 八分 → 十六分」，也不一定要「高潮前停一拍」。
- 用户说「图二」但只传了一张图时，就用那张图，并在回复里说明。
- **用户嫌每次从聊天里下载文件麻烦**。生成的文件一律提交进仓库的 `output/` 目录，不要只作为聊天附件发。

## 从简谱图到交付

1. **转写**。放大截图逐小节读，规则如下：
   - 下划线数定时值：一条线是八分音符，两条线是十六分音符。
   - 数字下方有点是低八度，上方有点是高八度。中音区的 1 记在第 4 八度，例如 1=D 时 1 是 D4。调很高时按人声音区选八度，并在回复里说明（茶汤 1=A 记作 A3，待用户确认）。
   - 弧线连同音是连音线，连不同音是圆滑线（拖腔，一个字唱多个音）。
   - 数字左上角的小字是倚音。
   - 歌词对齐到音符。
   - 每小节加起来必须正好 4 拍。
2. 移到用户要的调，检查人声音区。
3. 先定和声骨架（每半小节一个和弦），再写声部。弦乐的旋律只在人声的长音和气口里动，不抢词。拨弦、弱音器 ACE 认不出来（见「踩过的坑」）。
4. 把数据写进 `build.py`，运行 `--check` 直到没有任何输出，再生成文件。
5. 渲染 PDF 和 PNG，用 `qa.py` 查过，再自己看一遍排版（见「交付标准」第 4 条）。
6. 写目录 README；在 `docs/编配手法索引.md` 第三节末尾给这首歌加一段（格式照前面几首），用到了第一节的手法就把歌名补进那一条，和某首旧歌撞了、第一节还没有的手法在第一节新加一条；更新上面的精简表和 `docs/项目地图.md`；提交并推送；然后照 `.claude/skills/hollywood-score/references/delivery-center.md` 放进交付中心，开 PR 合并进 `main`。

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
bash tools/setup.sh               # 新的云端容器先跑一次：装依赖、字体、MuseScore 4、MusicXML schema，只打印几行
                                  # 在用户的 Mac 上它什么都不装，只列出缺什么（python3 -m pip install …、brew install poppler fluid-synth ffmpeg、MuseScore 4 和 Chrome）
python3 leihai/build.py --check   # 只检查：音域、小二度/小九度冲突（含人声）、平行五八度
python3 leihai/build.py           # 生成 output/ 下的 MusicXML / MIDI / SRT，并回读核对每小节 4 拍
```

- 乐谱数据全写在 `build.py` 里：每个声部一个 dict，每小节一个字符串，时值以十六分音符为单位。
- token 语法见文件开头的 docstring：
  - `C5/2` 八分音符，`D4+F4/8` 双音，`r/4` 休止；
  - `~` 连音线，`>` 重音，`( )` 圆滑线；
  - `=字` 歌词，`g:G4` 倚音。
- 改完必须先 `--check` 干净（没有 RANGE / CLASH / PARALLEL 输出），再生成。
- **好莱坞总谱 PDF**：`python3 <歌>/build.py --pdf`（需要 MuseScore 4 和 Chromium：MuseScore 4 由 `tools/setup.sh` 装，Chromium 它只检查，云端在 `/opt/pw-browsers`，找不到就设 `CHROME=/path`；细节见 `.claude/skills/hollywood-score/SKILL.md`）。茶汤、我不难过已经接好，新歌照 `chatang/build.py` 接（**只抄代码和流程，不抄里面的音乐数据**）。
- 单人声歌的 mp3 不在 `build.py` 里，需要另外渲染（我和我的祖国、土耳其进行曲、冬风、Unravel 的 `build.py` 加 `--mp3` 就出）：

  ```bash
  cd leihai/output
  fluidsynth -ni -g 0.6 -F /tmp/p.wav /usr/share/sounds/sf2/FluidR3_GM.sf2 泪海_副歌_人声弦乐四重奏_全轨.mid
  ffmpeg -y -i /tmp/p.wav -af loudnorm=I=-16:TP=-1.5 -b:a 160k 粗略试听_GM音色_非ACE效果.mp3
  ```

- 看排版：照「交付标准」第 4 条跑 `qa.py score` / `pages` / `seen`。草稿目录放在仓库外（会话的 scratchpad，或 `/tmp/qa-<歌>`），每个 PDF 一个，绝不要放进 `<歌>/output/`。泪海旧版 MuseScore 3 预览的做法见 `docs/项目地图.md` 末尾。
- MusicXML 合法性以 MusicXML 4.0 schema 为准：`python3 tools/hollywood/qa.py xml <文件>`（用 xmllint；schema 从 w3c/musicxml 仓库下载，缓存在 `~/.cache/musicxml/`；没有网络时照它打印的提示做）。MuseScore 3 的「not a valid MusicXML file」提示不可靠，不要以它为准。
- 人声 MIDI：`python3 tools/hollywood/qa.py midi <歌>/output`（每个音都有歌词或 `-`、GBK 版能读、各文件的音轨名）。

## 踩过的坑

- **music21 插入顺序**：往 Measure 里先 `insert` 零时值元素（TempoText 等），再 `append` 音符，音符会从那个偏移之后开始排，整小节错位。文字、力度、速度字一律在音符之后插入。泪海第 24 小节出过这个 bug，现在 `verify_bars()` 会拦住。
- **MusicXML 元素顺序**：`<score-instrument>` 里的 `<instrument-sound>` 必须放在 `<instrument-abbreviation>` 之后，否则不合法。
- **延长记号**：`<fermata>` 不能带 `placement` 属性，4.0 schema 不允许。
- **排版**：换行由 `polish()` 里的 `SYSTEM_BREAKS` 控制；好莱坞 11×17 每行放几小节见 SKILL.md「Choosing system breaks」（旧 A4 版的经验在 `docs/项目地图.md`「旧做法」）。
- **人声长音附近的弦乐**：弦乐和人声的长音不要构成小九度。例如人声 C4 持续时，B♭m6 的 D♭ 只能放在 C4 下面，放在上面就成了小九度。`--check` 会抓出来。
- **歌词 MIDI**：每个字一个 lyrics meta 事件；拖腔音符写 `-`；倚音带那个字，主音写 `-`。
- **平行五八度检查**：只比较各声部的最高音。高潮处两把小提琴有意八度齐奏的地方，写进 `check()` 的 `allow` 白名单。
- **圆滑线从连音线的后半个音开始**（例如 `Bb4/1~=时 (Bb4/1 Ab4/1)`）：泪海版 `merged_notes()` 会漏掉后面拖腔音符的 `-` 歌词。`wobunanguo/build.py` 和 `chatang/build.py` 都已修，新歌从 `chatang/build.py` 复制。
- **MuseScore 4 排 PDF 的坑**：直接导入 MusicXML 时 `-S` 样式不生效、导入的署名位置会乱，`tools/hollywood/hollywood.py` 都已经处理了（详见 SKILL.md 的 `references/template-internals.md`）。pypdf 报 `_cffi_backend` 时 `pip install cffi`（`tools/setup.sh` 已装）。
- **MS4 一行放不下时**：它会把最后一两小节挤到下一行单独成行，调小 `measureSpacing` 没用（已经是最小宽度）。先用 `qa.py score <PDF> -v` 看实际分行（它从 `pdftotext -bbox` 读方框小节号、按纵坐标分组）。解决办法是每行少放小节，或者去掉占宽的东西（土耳其进行曲把大提琴的三个倚音琶音改成了琶音和弦）。
- **music21 的弱起小节**要设 `m.paddingLeft`，否则导出 MusicXML 时会补一个隐藏休止符，小节变成整小节。弱起开头又没有前奏时，MIDI 怎么对齐小节线见 `.claude/skills/hollywood-score/references/instrumental.md`「The MIDI's barlines」。
- **转写时注意低八度点**：我不难过的谱上有几处「高音之间突然掉一个八度」的点（「陪」「寞」「看」），照谱写了，但在回复和 README 里单独列出来请用户核对。
- **拨弦、弱音器**：ACE 的智能模式不会从 MIDI 推出来，要用户手动改。要导给 ACE 的编配尽量不用；用了就在 README 和 `catalog.py` 的 `howto` 里写明第几小节要在 ACE 里手动改演奏法（照土耳其进行曲）。
- **music21 的六连音**会被写成 3:2、按半小节连梁，MS4 也不认 `show-number="none"`：歌里有六连音、或要藏连音数字时，照 `dongfeng/`（`engine.py`、`build.py` 的 `_mscx_hook`）做，见 `docs/钢琴谱改编.md`「冬风的做法」。
- **给用户 Mac 写 shell 脚本**：macOS 的 bash 3.2 会把紧跟在变量后面的中文字节吞进变量名，变量后面紧跟中文一律写 `${NAME}`（其他坑见 `.claude/skills/hollywood-score/references/mac-app.md`）。
- 纯器乐、钢琴谱转弦乐、LilyPond 排谱的坑见 `docs/钢琴谱改编.md`；ACE 的其他事见 `docs/ACE-Studio.md`。

## 待办 / 待确认

- **泪海唱几遍**：副歌目前唱两遍，第一遍抒情，第二遍高燃。用户还没确认要不要只唱一遍。改之前先看 `docs/项目地图.md`「改旧歌时」（做法，以及已经渲染混音过、视频按它对的时间）。
- **合并分支**：用户已经授权：每次交付检查通过后，由 AI 自己开 PR 合并进 `main`，不用再问。别的对话建的旧分支里的歌，合并前要注意 AGENTS.md 冲突，只合并歌曲目录。
- 其他每首歌待用户确认的事项见 `docs/项目地图.md`。

## Git 约定

- 新工作开新分支提交，提交信息写清楚。不改写别人分支的历史，不 force push。
- **交付完成后自己合并进 `main`**（用户授权过，不用再问）：推送分支，开 PR，合并。新对话只读 `main` 里的规则和工具，不合并的话下次对话就不知道。
- 生成的文件（`output/`）要提交进仓库，同时放进编曲交付中心。用户从交付中心下载，不用 GitHub。
- `tools/deliver/dist/` 是打包中间产物，已经在 `.gitignore` 里，不提交。
- `__pycache__` 已经在 `.gitignore` 里，不要提交。
