# 封面方案（《我和我的祖国》，等用户选）

2026-10-02 用户看了现在的好莱坞封面（白底、双线框、黑字居中，`previews/00_classic.jpg`），说：「这个封面缺少更多的审美和艺术感，请你结合标题以及我喜欢的感觉多给我几版参考，是否可以丰富颜色以及排版？参照世界的大师的风格给我设计几版好看的封面。」

这里是给这首歌做的 8 版封面，每版致敬一位大师。用户在「封面方案」页面比较：https://claude.ai/artifact/FHTdLNzRRN8gnXpDrtWtfs（图都是从真正的 11×17 英寸 PDF 转出来的）。

**状态：等用户选。** 选定之前 `hollywood.py` 的封面不变，别的歌也照旧。

| 编号 | 文件 | 方案名 | 致敬 |
|---|---|---|---|
| 1 | `designs/lv.py` | 朱丝栏·海与浪花 | 吕敬人的书籍设计：宋版书版式、竖排大标题、白文印浮在海平线上；用户在国庆视频里认可过的暖纸、暖墨、朱砂，加碧色；题头小国旗 |
| 2 | `designs/kan.py` | 一笔海天 | 靳埭强：一笔干笔浓墨横过圆窗（海天之间），笔锋卷成浪花；「我和我的」小、「祖国」大书法 |
| 3 | `designs/qianli.py` | 千里江山图轴 | 王希孟《千里江山图》：青绿山水立轴，靛蓝装裱 |
| 4 | `designs/haishui.py` | 海水江崖 | 海水江崖纹、常沙娜的礼仪装饰：朱红底、泥金、石青石绿 |
| 5 | `designs/deco.py` | 金浪花开 | 卡桑德尔和上海外滩的装饰艺术：墨蓝、金、扇形海浪 |
| 6 | `designs/bass.py` | 剪纸浪花 | 索尔·巴斯的好莱坞电影海报：朱红、暖黑、剪纸大浪 |
| 7 | `designs/brockmann.py` | 海与浪花·同心圆 | 米勒-布罗克曼的瑞士音乐会海报：八个圆环是八个声部，按全曲 73 小节画出有声和休止 |
| 8 | `designs/kandinsky.py` | 海与浪花的色彩乐章 | 康定斯基：八个声部按他的「颜色有声音」各一种颜色和形状 |

`designs/classic.py` 是现在的封面（直接调用 `hollywood.cover_html`），用来对比。

## 出图

```bash
python3 tools/hollywood/covers/fonts.py              # 下载开源字体到 ~/.cache/hollywood-fonts（约 140 MB，只需一次）
python3 tools/hollywood/covers/render.py lv kan      # 出 PDF 和 PNG 到 /tmp/covers-out/<id>/，并检查内容
python3 tools/hollywood/covers/render.py lv --zoom 1,1,10,6   # 局部放大看细节
python3 tools/hollywood/covers/render.py lv --full   # 封面 + 现有总谱内页，看整本的效果
```

- 每版是一个文件，`render(m)` 返回一页 HTML，文字全部从 META（`meta_wohewodezuguo.json`，和 `wohewodezuguo/build.py` 的 META 一样）来。
- `render.py` 的检查：FULL SCORE、标题（至少有一处连成一行）、拼音、中英文副标题、署名表（改编、制谱两行都写花开当富贵，和 `qa.py` 一样的查法）、调、速度、时长、编制、页脚落款；文字离裁切边至少 0.35 英寸；没有掉到备用字体。
- 变量字体在 Chromium 的 PDF 里会变成 Type 3 轮廓，所以 `fonts.py` 把它们切成固定字重。思源宋体、思源黑体用系统的（`fonts-noto-cjk`，细的和特粗的字重在 `fonts-noto-cjk-extra`）。
- 设计要求、用户喜欢什么、红线都在 `BRIEF.md`。红线要点：国旗只能用 `lib.flag_svg()`（GB 12982，完整、平直、不透明、上面不压东西）；不用地图、国徽、天安门、人物；白底上不放红色圆盘、不放红白放射线（像日本国旗）；不把「祖国」两个字切开（「一刻也不能分割」，第一轮的剪纸版就犯过，已改）。

## 用户选定以后要做的

1. `hollywood.render_pdf` 加 `META["cover"]`（选中的设计模块）：封面单独用 Chromium 打印，再和总谱页合并；不设就是现在的封面。
2. `qa.py` 的 `check_cover` 按旧封面的位置找调、编制那两行（`COVER_LINES`），换了版式会误报；改成按内容查（照 `render.py` 的 `check()`）。
3. `tools/setup.sh` 加一步 `fonts.py`（只要选中的那版用到的字体）。在用户的 Mac 上也要能出图。
4. 画面是照这首歌画的（海、浪花、高山、6/8 拍）。别的歌要用同一种版式时，版式和字体可以沿用，画面要照那首歌重新构思（和编曲一样，不照搬）。
5. 重出《我和我的祖国》的 PDF，`qa.py score` 和逐页检查，更新交付中心。
