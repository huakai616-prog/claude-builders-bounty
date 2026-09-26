# 甲乙丙丁 · 风格样帧（ClaudeAnimationBase）

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
