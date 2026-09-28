#!/usr/bin/env python3
"""Write leihai/video/timing.json: the song-time map for the 泪海 video.

The user's Logic mixes of 泪海 (both 118.83 s) follow the score's tempo map
exactly (measured within 30 ms, no offset), so every time here comes
straight from ../build.py (TEMPI + sec_at) and applies to the audio as is.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build  # noqa: E402

AUDIO_SECONDS = 118.831036
FPS = 24

EVENTS = [  # (bar, 16th, what)
    (1, 0, "前奏：Fsus2 长音"),
    (1, 13, "前奏：第一小提琴弱起，拉钩子「你怎么舍得」"),
    (5, 0, "前奏最后一小节"),
    (5, 13, "人声弱起「你怎么」"),
    (6, 0, "副歌 I（抒情）"),
    (7, 5, "「海」长音，第一小提琴高八度回声钩子"),
    (10, 0, "副歌 I 后半，两把小提琴双线"),
    (12, 0, "「往事一幕幕」，中提琴改十六分音符"),
    (14, 0, "「淹埋」"),
    (14, 8, "过门：上行音阶，渐强"),
    (15, 12, "弦乐全停"),
    (15, 13, "人声清唱「你怎么」"),
    (16, 0, "副歌 II（高燃）全奏进入"),
    (20, 0, "副歌 II 后半，第二小提琴十六分音符"),
    (22, 8, "第一小提琴最高音 G6"),
    (24, 0, "「淹埋」：D♭，渐宽"),
    (24, 8, "E♭"),
    (25, 0, "落到 F 大调，全曲最大的高潮"),
    (25, 8, "人声结束"),
    (25, 13, "尾奏：第一小提琴弱奏回声钩子"),
    (26, 8, "B♭m6，渐慢"),
    (27, 0, "最后的和弦（延长）"),
    (28, 0, "乐谱结束，之后是混响尾巴"),
]


def t(bar, s16=0):
    return round(build.sec_at((bar - 1) * build.BAR16 + s16), 3)


def main():
    parsed = {p["id"]: build.parse_part(p["data"]) for p in build.PARTS}
    syl = build.syllables(parsed["vox"])
    lines, i = [], 0
    for text in build.SUB_LINES:
        chunk = syl[i:i + len(text)]
        assert "".join(s[0] for s in chunk) == text, text
        lines.append(dict(
            text=text,
            start=round(build.sec_at(chunk[0][1]), 3),
            end=round(build.sec_at(chunk[-1][2]), 3),
            syllables=[dict(char=c, start=round(build.sec_at(a), 3),
                            end=round(build.sec_at(b), 3))
                       for c, a, b in chunk]))
        i += len(text)
    data = dict(
        audio=dict(
            seconds=AUDIO_SECONDS,
            offset=0.0,
            note="Logic 混音与乐谱速度表一致：音频秒数 = 乐谱秒数。"
                 "约 112.5 秒后是混响尾巴，约 115 秒后基本静音。"),
        video=dict(fps=FPS, frames=math.ceil(AUDIO_SECONDS * FPS),
                   note="按整帧收尾，末尾补不到 1 帧的静音"),
        tempo=[dict(bar=b, s16=s, bpm=bpm, t=t(b, s))
               for b, s, bpm in build.TEMPI],
        bars=[dict(bar=b, t=t(b)) for b in range(1, build.NBARS + 2)],
        beats=[dict(bar=b, beat=k + 1, t=t(b, 4 * k))
               for b in range(1, build.NBARS + 1) for k in range(4)],
        events=[dict(bar=b, s16=s, t=t(b, s), what=w) for b, s, w in EVENTS],
        lines=lines,
    )
    out = os.path.join(HERE, "timing.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    print("written", out, "-", len(lines), "lines,",
          sum(len(x["syllables"]) for x in lines), "syllables,",
          data["video"]["frames"], "frames")


if __name__ == "__main__":
    main()
