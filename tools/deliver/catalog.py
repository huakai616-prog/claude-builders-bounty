"""Catalog of everything shown in 编曲交付中心 (the pinned delivery page).

One entry per work. `ref` is the git ref the files come from (None = the
current working tree, i.e. the song you just built in this session).
`src` is the folder whose files go into the download zip.

Standard songs (layout="standard") get a zip laid out as
    <title>_编曲交付/说明.txt
    <title>_编曲交付/1_四样主文件/   the four must-have files
    <title>_编曲交付/2_其他文件/     everything else from src
Works with their own folder structure (layout="keep") are zipped as-is,
plus 说明.txt; `extra` adds files from elsewhere into a subfolder.

`main` maps the four deliverables to file names inside src (None = missing):
    musicxml  西贝柳斯工程      pdf    总谱 PDF
    strings   弦乐总 MIDI       vocal  人声带歌词 MIDI
To add a new song: append an entry here (newest work at the top is fine,
the page sorts by `updated`), then run tools/deliver/package.py <slug>.
"""

WORKS = [
    dict(
        slug="wobunanguo", section="song", ref=None,
        title="我不难过", subtitle="副歌 · 人声与弦乐四重奏",
        artist="孙燕姿", key="♭E 大调", tempo="♩=68",
        instrumentation="人声 + 弦乐四重奏",
        src="wobunanguo/output", layout="standard",
        main=dict(musicxml="我不难过_副歌_人声弦乐四重奏.musicxml",
                  pdf="我不难过_副歌_总谱.pdf",
                  strings="我不难过_弦乐四重奏_伴奏.mid",
                  vocal="我不难过_人声_带歌词.mid"),
        pdf_kind="hollywood", audio="粗略试听_GM音色_非ACE效果.mp3",
        questions=[
            "谱上几处低八度请核对：「陪」「寞」「看」（以及后半段同位置的「你」「我」「不」）照谱写成了低八度，旋律会在高音之间突然掉下去。原唱不是这样的话告诉我，我改成高八度。",
        ]),
    dict(
        slug="qingge", section="song", ref="origin/claude/serene-darwin-2l4jy4",
        title="情歌", subtitle="最后一遍副歌 · 人声与弦乐四重奏",
        artist="梁静茹", key="F 大调", tempo="♩=70",
        instrumentation="人声 + 弦乐四重奏",
        src="qingge/output", layout="standard",
        main=dict(musicxml="情歌_副歌_人声弦乐四重奏.musicxml",
                  pdf="情歌_总谱.pdf",
                  strings="情歌_弦乐四重奏_伴奏.mid",
                  vocal="情歌_人声_带歌词.mid"),
        pdf_kind="hollywood", audio="粗略试听_GM音色_非ACE效果.mp3",
        note="总谱 PDF 带封面和「花开当富贵」署名，是 A4 版式（LilyPond 排的），还不是统一的 11×17 好莱坞模板。",
        questions=[
            "简谱整段写在高音点上，这里按实际演唱放到 C4–C5 八度，请核对。",
            "「可是」写成 C4→D4 再接「那」F4，请核对。",
            "「久」按原谱只唱 2 拍，弦乐第 3 拍接尾奏，请确认。",
        ]),
    dict(
        slug="chatang", section="song", ref="origin/claude/magical-meitner-wj6g5j",
        title="茶汤", subtitle="副歌 · 人声与弦乐四重奏",
        artist="郁可唯", key="A 大调（原调）", tempo="♩=112",
        instrumentation="人声 + 弦乐四重奏",
        src="chatang/output", layout="standard",
        main=dict(musicxml="茶汤_副歌_人声弦乐四重奏.musicxml",
                  pdf="茶汤_副歌_总谱预览.pdf",
                  strings="茶汤_弦乐四重奏_伴奏.mid",
                  vocal="茶汤_人声_带歌词.mid"),
        pdf_kind="preview", audio="粗略试听_GM音色_非ACE效果.mp3",
        questions=[
            "调没指定，这版保留原调 A 大调（人声 C#4–E5）。要换调告诉我。",
            "转写时中音区 1 记作 A3，请核对八度。",
            "「的」「冷」「在」上的波音只记在谱上，MIDI 里没展开，需要的话在 ACE 里画音高曲线。",
        ]),
    dict(
        slug="dadongbei", section="song", ref="origin/claude/determined-archimedes-93zrgx",
        title="大东北我的家乡", subtitle="全曲 · 迪士尼风格交响乐 + SATB 合唱",
        artist="何玉", key="F 大调 → G 大调", tempo="♩=72 / ♩=128",
        instrumentation="交响乐队（Instrument X）+ 四声部合唱",
        src="干活/大东北我的家乡", layout="keep",
        extra={"4_试听与字幕": [
            "dadongbei/output/粗略试听_GM音色_非最终效果.mp3",
            "dadongbei/output/大东北我的家乡_歌词字幕.srt",
            "dadongbei/output/大东北我的家乡_交响合唱_全轨.mid"]},
        main=dict(musicxml="3_西贝柳斯总谱_好莱坞C调格式/大东北我的家乡_好莱坞总谱_西贝柳斯用.musicxml",
                  pdf="3_西贝柳斯总谱_好莱坞C调格式/大东北我的家乡_好莱坞C调总谱_预览.pdf",
                  strings="1_InstrumentX乐队MIDI/00_全乐队15轨_InstrumentX.mid",
                  vocal="2_合唱四声部合并_带歌词MIDI/大东北我的家乡_合唱四声部合并_带歌词.mid"),
        labels=dict(strings="乐队总 MIDI", vocal="合唱带歌词 MIDI"),
        pdf_kind="preview", audio="4_试听与字幕/粗略试听_GM音色_非最终效果.mp3",
        note="压缩包就是按用途分好的成品文件夹，先看里面的「使用说明.md」。",
        questions=[
            "Instrument X 导入 MIDI 时读不读速度变化（看第 5 小节是不是 ♩=128）？不读就用「按秒对齐_固定120BPM_备用」那套。",
            "西贝柳斯打开后，A 调单簧管、F 调圆号、降 B 调小号等移调乐器显示是否正常？",
            "现在唱一遍主歌、两遍副歌（第二遍转 G），要不要照原谱整首唱两遍？",
            "ACE 里多音字要核对：长、模、呐、血、着、地、这。",
        ]),
    dict(
        slug="leihai", section="song", ref="origin/main",
        title="泪海", subtitle="副歌 · 人声与弦乐四重奏",
        artist="许茹芸", key="F 大调", tempo="♩=59",
        instrumentation="人声 + 弦乐四重奏",
        src="leihai/output", layout="standard",
        main=dict(musicxml="泪海_副歌_人声弦乐四重奏.musicxml",
                  pdf="泪海_副歌_总谱预览.pdf",
                  strings="泪海_弦乐四重奏_伴奏.mid",
                  vocal="泪海_人声_带歌词.mid"),
        pdf_kind="preview", audio="粗略试听_GM音色_非ACE效果.mp3",
        questions=[]),
    dict(
        slug="jiayibingding", section="song", ref="origin/claude/loving-bell-wsnmgy",
        title="甲乙丙丁", subtitle="副歌 · 人声与弦乐五重奏",
        artist="李佳薇", key="F 大调", tempo="♩=65",
        instrumentation="人声 + 弦乐五重奏",
        src="jiayibingding/output", layout="standard",
        main=dict(musicxml="甲乙丙丁_副歌_人声弦乐五重奏.musicxml",
                  pdf="甲乙丙丁_副歌_总谱预览.pdf",
                  strings="甲乙丙丁_弦乐五重奏_伴奏.mid",
                  vocal="甲乙丙丁_人声_带歌词.mid"),
        pdf_kind="preview", audio="粗略试听_MuseScore音色_非ACE效果.mp3",
        questions=[
            "副歌暂取「你我怎么两清」到「能否换来一点同情」。如果你要的范围不同（比如还包括「是你教我勇敢……」），告诉我补进去。",
        ]),
    dict(
        slug="jasmine", section="song", ref="origin/claude/sleepy-wozniak-g09dmt",
        title="茉莉花", subtitle="全曲 · 人声与弦乐五重奏",
        artist="江苏民歌", key="F 大调", tempo="♩=76",
        instrumentation="人声 + 弦乐五重奏",
        src="jasmine-flower", layout="keep", include=["茉莉花_人声与弦乐五重奏.mxl"],
        main=dict(musicxml="茉莉花_人声与弦乐五重奏.mxl", pdf=None,
                  strings=None, vocal=None),
        pdf_kind=None, audio=None,
        note="只有一个西贝柳斯能直接打开的 .mxl 总谱，还没有 PDF 和 MIDI。",
        questions=[]),
    # ---- 视频与动画 --------------------------------------------------------
    dict(
        slug="dengchao", section="media", ref="origin/claude/elegant-pascal-83rncr",
        title="《等潮》视频制作包", subtitle="泪海 · 抖音竖屏 · TapNow 分镜与提示词",
        artist="", key="", tempo="", instrumentation="",
        src="leihai/video/tapnow", layout="keep",
        main={}, pdf_kind=None, audio=None,
        note="先打开「分镜与提示词.md」：照着在 TapNow 里生成 28 个镜头，放进 clips 文件夹，再运行 assemble.py 合成。",
        questions=[]),
    dict(
        slug="clawd", section="media", ref="origin/claude/loving-bell-wsnmgy",
        title="甲乙丙丁 · Clawd 动画样片", subtitle="10 秒样片（歌曲 0:28–0:38）",
        artist="", key="", tempo="", instrumentation="",
        src="jiayibingding/video/clawd", layout="keep",
        main={}, pdf_kind=None, audio=None, video="样片_Clawd_0m28-0m38.mp4",
        questions=["要不要把这 10 秒样片扩展成完整视频、用哪种画风，还在等你定。"]),
    dict(
        slug="pianopet", section="media", ref="origin/claude/focused-volta-ve5ka6",
        title="小 Claude 弹钢琴", subtitle="5 秒循环动画",
        artist="", key="", tempo="", instrumentation="",
        src="claude-piano-pet", layout="keep",
        main={}, pdf_kind=None, audio=None,
        note="解压后双击 index.html，用浏览器打开就能播放。",
        questions=[]),
]
