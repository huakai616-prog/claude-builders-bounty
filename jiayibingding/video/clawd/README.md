# 甲乙丙丁 · Clawd 风格（ClaudeAnimationBase）

`jiayi_style.js` 是用 [ClaudeAnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase)（p5.js + p5.brush）画的风格样帧，不是成片。它把 9 张样帧排在一条时间线上：

| 时间 | 画面 |
|---|---|
| 6 s | Clawd 风格 · 前奏：雨夜里独自坐在电线（五线谱）上 |
| 16 s | Clawd 风格 · 你我：回忆里的黄昏，牵着的手像一道符杠 |
| 26 s | Clawd 风格 · 甲乙丙丁：陌生人挤满电线，TA 背身走远 |
| 36 s | Clawd 风格 · 最高音「与」：哭出声，身后五线星亮起 |
| 46 s | Clawd 风格 · 最后的和弦：TA 的位置只剩一个休止符 |
| 56 s | 《点与线》风格 · 你我：点和线合起来就是一个音符 |
| 66 s | 《点与线》风格 · 酷刑：线把自己折成笼子，点滚着离开 |
| 76 s | 《父与女》风格 · 前奏：田野上的小人和长影子 |
| 86 s | 《父与女》风格 · 尾奏：五道树影像一行五线谱 |

## 在自己电脑上渲染

```bash
git clone https://github.com/JohnHeibel/ClaudeAnimationBase && cd ClaudeAnimationBase && npm install
cp <本仓库>/jiayibingding/video/clawd/jiayi_style.js src/scenes/
# studio.html：把 src/scenes/demo.js 那一行换成 src/scenes/jiayi_style.js
# src/config.js：const PROJECT = { duration: 91, bpm: 65, offset: 0 };
node render.mjs --stills=6,16,26,36,46,56,66,76,86 --out=out/stills
```

有显卡的机器（比如 Mac）渲染一帧不到几秒；没有显卡要加 `--soft-gl`，水彩画面一帧要 20–100 秒。

## 10 秒样片（歌曲 0:28–0:38）

- `样片_Clawd_0m28-0m38.mp4`：成品，1920×1080，24 帧，带 DEMO 的声音（和 DEMO 对齐，偏差 0 毫秒）。
- `STORYBOARD_28-38.md`：这一段的分镜和时间表。
- `jiayi_clip.js`：场景代码，时间就是歌曲时间（28.0–38.0 秒）。
- `lite.js`：没有显卡时用的提速方案。角色的水彩晕染改成平涂，背景仍画真水彩，但每个镜头只画一次后反复使用。在我的云端环境里，一帧从 30–100 秒降到 0.1 秒左右（算上编码约 2.4 秒）。有显卡的电脑可以不加载它，画面会多一点水彩质感。

渲染这段样片（在 ClaudeAnimationBase 文件夹里）：

```bash
cp <本仓库>/jiayibingding/video/clawd/{lite.js,jiayi_clip.js} src/scenes/
# studio.html：把 demo.js 那一行换成两行：src/scenes/lite.js 和 src/scenes/jiayi_clip.js
# src/config.js：const PROJECT = { duration: 82, bpm: 65, offset: 0 };
# 把 DEMO.mp3 复制成 assets/demo.mp3
node render.mjs --clip --range=28:38 --audio=assets/demo.mp3 --out=out/jiayi_clip_28-38.mp4
```
