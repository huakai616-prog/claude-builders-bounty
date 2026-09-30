#!/usr/bin/env python3
"""Write wohewodezuguo/video/timing.json: the song-time map for the video.

The user's Logic mix (176.8 s, music ends ~171.8 s) follows the score's
tempo map exactly (onset cross-correlation with the GM preview: 0.00 s
offset), so every time here comes straight from ../build.py (TEMPI +
sec_at) and applies to the audio as is.

Contents: bars and dotted-quarter beats, sections, lyric lines with
per-character times (the SRT lines), and every note of all eight parts
(merged ties, lyric or "-" for a melisma, pizz. flag) for visuals that
follow individual voices.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build  # noqa: E402
import engine as E  # noqa: E402

AUDIO_SECONDS = 176.8
MUSIC_END = 171.8   # measured: last sound above -34 dB of peak
FPS = 30

EVENTS = [  # (bar, 16th, what)
    (1, 0, "前奏：中提琴唱主题，第二小提琴、大提琴拨弦"),
    (3, 0, "第一小提琴接主题"),
    (9, 0, "主歌一：女低音独唱「我和我的祖国」"),
    (17, 0, "「我歌唱每一座高山」，低音上行"),
    (21, 0, "「袅袅炊烟」弦乐全停，清唱，男声哼鸣"),
    (24, 0, "接力上行：大提琴 → 中提琴 → 第二小提琴"),
    (25, 0, "副歌一：女高音第一次开口「我最亲爱的祖国」"),
    (29, 0, "「母亲的脉搏」：旋律在女低音"),
    (30, 0, "大提琴拨弦心跳"),
    (32, 6, "poco rit.「和我诉说」"),
    (33, 0, "间奏：第一小提琴 f 唱主题，第二小提琴琶音"),
    (37, 0, "大提琴答句，渐弱"),
    (41, 0, "主歌二：女声（浪花）唱，男声（大海）哼"),
    (47, 0, "男低音独唱「海是那浪的依托」"),
    (49, 0, "「每当大海在微笑」旋律在女低音"),
    (52, 0, "「漩涡」：两把小提琴十六分音符打旋"),
    (56, 0, "接力上行"),
    (57, 0, "副歌二全开"),
    (64, 6, "poco allarg.「心中的歌」"),
    (65, 0, "啦啦段：男声划船节奏"),
    (69, 0, "尾声 allargando「永远给我碧浪清波」ff"),
    (71, 6, "「中」延长"),
    (72, 0, "「歌」渐弱到 p，二对三律动"),
    (73, 6, "最后的和弦"),
]


def main():
    E.configure(build)
    parsed = {p["id"]: E.parse_part(p["data"]) for p in build.PARTS}
    names = {p["id"]: p["name"] for p in build.PARTS}

    def t(bar, s16=0):
        return round(E.sec_at(E.absq(bar, s16)), 3)

    lines = []
    for text, pid, b1, b2 in build.SUB_LINES:
        syl = E.syllables(parsed[pid], b1, b2)
        assert "".join(x[0] for x in syl) == text, (text, pid)
        lines.append(dict(
            text=text, voice=pid,
            start=round(E.sec_at(syl[0][1]), 3),
            end=round(E.sec_at(syl[-1][2]), 3),
            chars=[dict(char=c, start=round(E.sec_at(a), 3),
                        end=round(E.sec_at(b), 3)) for c, a, b in syl]))

    parts = {}
    for pid, evs in parsed.items():
        notes = []
        for n in E.merged_notes(evs):
            b, s = E.bar_of(n["start"])
            notes.append(dict(
                start=round(E.sec_at(n["start"]), 3),
                end=round(E.sec_at(n["start"] + n["dur"]), 3),
                midi=[E.midi_of(p) for p in n["pitches"]],
                lyric=n["lyric"] or ("-" if n["melisma"] else ""),
                bar=b, pizz=E.pizz_state(pid, b, s),
                fermata=bool(n["fermata"])))
        parts[pid] = dict(name=names[pid], notes=notes)

    beats = []
    for b in range(1, build.NBARS + 1):
        for k in range(E.BARLEN[b] // 6):
            beats.append(dict(bar=b, beat=k + 1, t=t(b, 6 * k)))

    sections = [dict(bar=b, letter=l, name=n, t=t(b))
                for b, l, n in build.SECTIONS]
    data = dict(
        audio=dict(seconds=AUDIO_SECONDS, offset=0.0, music_end=MUSIC_END,
                   note="用户 Logic 混音与乐谱速度表一致：音频秒数 = 乐谱秒数。"),
        video=dict(fps=FPS, frames=math.ceil(AUDIO_SECONDS * FPS),
                   size=[1080, 1920]),
        tempo=[dict(bar=b, s16=s, bpm_16th=bpm, t=t(b, s))
               for b, s, bpm in build.TEMPI],
        bars=[dict(bar=b, t=t(b), eighths=E.BARLEN[b] // 2)
              for b in range(1, build.NBARS + 1)]
        + [dict(bar=build.NBARS + 1, t=round(E.sec_at(E.TOTAL), 3),
                eighths=0)],
        beats=beats, sections=sections,
        events=[dict(bar=b, s16=s, t=t(b, s), what=w) for b, s, w in EVENTS],
        lines=lines, parts=parts)
    out = os.path.join(HERE, "timing.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    n = sum(len(p["notes"]) for p in parts.values())
    print(f"{out}: {len(lines)} lines, "
          f"{sum(len(l['chars']) for l in lines)} chars, {n} notes, "
          f"score ends {data['bars'][-1]['t']} s")


if __name__ == "__main__":
    main()
