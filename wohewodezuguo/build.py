#!/usr/bin/env python3
"""我和我的祖国（全曲）— 四声部独唱（S.A.T.B.）+ 弦乐四重奏 编配生成器

One source of truth for:
  * MusicXML full score (Sibelius; Hollywood layout via tools/hollywood)
  * full 8-track MIDI for ACE Studio (four singers + four strings)
  * four-part vocal MIDI with lyrics and "br" breath blocks (UTF-8, GBK),
    a plain vocal MIDI, and the strings-only MIDI
  * lyric subtitles (SRT) and per-voice lyric paste texts

Key: E-flat major (1=bE, as printed; 1 = Eb4), 6/8 with 9/8 bars in the
chorus, dotted quarter = 56 (Moderato).  Written out in full, no repeats:
  Intro 1-8 | A Verse 1 9-24 | B Chorus 1 25-32 | C Interlude 33-40 |
  D Verse 2 41-56 | E Chorus 2 57-64 | F La-la 65-68 | G Coda 69-73
Token syntax and the engine: see engine.py.

    python3 build.py --check   # ranges, lyrics, clashes, parallels, crossings
    python3 build.py           # MusicXML, MIDI, SRT, lyric texts
    python3 build.py --pdf     # ... plus the Hollywood score PDF
    python3 build.py --mp3     # ... plus the GM preview mp3
"""
import os
import re
import subprocess
import sys
import tempfile

from music21 import clef, instrument

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine as E  # noqa: E402

OUT = os.path.join(HERE, "output")
NAME = "我和我的祖国"
NBARS = 73
NINE_EIGHT = {2, 4, 26, 28, 34, 36, 58, 60, 66, 68}
KEY_M21 = "E-"
KEY_MIDI = "Eb"
DOTTED_BPM = 56          # printed tempo: dotted quarter = 56
TOP = "sop"              # the staff that carries tempo and section marks


def R(n=12):
    return f"r/{n}"


# ---------------------------------------------------------------------------
# Harmony (dotted-quarter beats)
#   Intro     Eb Cm7 | Gm7 Abmaj9 Bb7sus4 | Eb/G Ab(add9) | Gm Cm7 F7 |
#             Bb7 | Ebmaj7 Cm7 | Ab Bb7sus4 | Eb
#   Verse     Eb Ab/Eb | Eb | Abmaj7 F/A | Bbsus4 Bb | Ab | F7/A |
#             Bb7 Bb7sus4 | Eb G7/B | Cm7 Fm7 | Abmaj7 Bbsus4 |
#             Eb Gm7 | Abmaj7 | Cm7 Gm7 | Ab(add9) Eb/Bb | Bb7 | Eb
#             (bass A-flat, A, B-flat twice; the second half climbs
#              C-F-Ab-Bb-Eb-G-Ab like the mountain it sings about)
#   Chorus    Eb Cm7 | Gm7 Abmaj9 Bb7sus4 | Eb/G Ab(add9) | Gm Cm7 F7 |
#             Bb7 | Ebmaj7 Cm7 | Ab Bb7sus4 | Eb   (iii-vi-II-V-I at the end)
#   Coda      Bb7 | Ebmaj7 Abmaj7 | Eb/Bb Bb7(fermata) | Eb
# ---------------------------------------------------------------------------

# ============================== VOICES ======================================
SOP = {
    25: "Eb5/2=我 (F5/2=最 G5/2) F5/2=亲 Eb5/2=爱 C5/2=的",
    26: "(D5/2=祖 C5/3 G4/1) Bb4/12=国",
    27: "Eb5/2=我 F5/2=永 G5/2=远 F5/2=紧 Eb5/2=贴 C5/2=着",
    28: "D5/2=你 Bb4/3=的 G4/1=心 C5/12=窝",
    29: "D5/2=你 C5/2=用 Bb4/2=你 Ab4/6=那",
    30: "Bb4/1=母 Bb4/1=亲 Ab4/2=的 G4/2=脉 Eb5/6=搏",
    31: "C5/6=和 Ab4/4=我 G4/2=诉",
    32: "G4/6~=说 G4/4 r/2",
    41: "(Bb4/2=我 C5/2) Bb4/2=的 (Ab4/2=祖 G4/2) F4/2=国",
    42: "Eb4/6=和 Eb4/6=我",
    43: "Eb4/2=像 G4/2=海 Eb5/2=和 D5/2=浪 C5/3=花 G4/1=一",
    44: "Bb4/12=朵",
    45: "C5/2=浪 D5/2=是 C5/2=那 (Bb4/2=海 Ab4/2) G4/2=的",
    46: "F4/6=赤 C4/6=子",
    49: "D5/2=每 (Eb5/2=当 D5/2) C5/2=大 Bb4/2=海 Ab4/2=在",
    50: "G4/6=微 F4/6=笑",
    51: "Eb4/2=我 G4/2=就 Eb5/2=是 D5/2=笑 F5/3=的 Eb5/1=漩",
    52: "C5/12=涡",
    53: "Eb5/2=我 D5/2=分 C5/2=担 Bb4/6=着",
    54: "C5/2=海 Bb4/2=的 Ab4/2=忧 G4/6=愁",
    55: "Bb4/4=分 Ab4/2=享 G4/2=海 G4/2=的 (Ab4/1=欢 G4/1)",
    56: "Bb4/12=乐",
    59: "(Eb5/2=你 F5/2) G5/2=是 (F5/2=大 Eb5/2) C5/2=海",
    60: "D5/2=永 Bb4/3=不 G4/1=干 C5/12=涸",
    61: "D5/2=永 C5/2=远 Bb4/2=给 Ab4/6=我",
    62: "Bb4/2=碧 Ab4/2=浪 G4/2=清 Eb5/6=波",
    63: "C5/6=心 Ab4/4=中 G4/2=的",
    64: "Bb4/12=歌",
    65: "Eb5/2=啦 F5/2=啦 G5/2=啦 F5/2=啦 Eb5/2=啦 C5/2=啦",
    66: "D5/2=啦 C5/3=啦 G4/1=啦 Bb4/12=啦",
    67: "Eb5/2=啦 F5/2=啦 G5/2=啦 F5/2=啦 Eb5/2=啦 C5/2=啦",
    68: "D5/2=啦 Bb4/3=啦 G4/1=啦 C5/12=啦",
    69: "G5/2=永 F5/2=远 Eb5/2=给 D5/6=我",
    70: "D5/2=碧 C5/2=浪 Bb4/2=清 G5/6=波",
    71: "Bb4/6=心 F5/4^=中 Eb5/2=的",
    72: "Eb5/12~=歌",
    73: "Eb5/6^ r/6",
}
SOP[57], SOP[58] = SOP[25], SOP[26]

ALT = {
    9: "(Bb4/2=我 C5/2) Bb4/2=和 (Ab4/2=我 G4/2) F4/2=的",
    10: "Eb4/6=祖 Bb3/6=国",
    11: "Eb4/2=一 G4/2=刻 Eb5/2=也 D5/2=不 C5/3=能 G4/1=分",
    12: "Bb4/12=隔",
    13: "C5/2=无 D5/2=论 C5/2=我 (Bb4/2=走 Ab4/2) G4/2=到",
    14: "F4/6=哪 C4/6=里",
    15: "D4/2=都 C4/2=流 Bb3/2=出 Bb4/2=一 Eb4/3=首 F4/1=赞",
    16: "G4/12=歌",
    17: "Bb4/2=我 C5/2=歌 Bb4/2=唱 Ab4/2=每 G4/2=一 F4/2=座",
    18: "Eb4/6=高 Bb3/6=山",
    19: "Eb4/2=我 G4/2=歌 Eb5/2=唱 D5/2=每 F5/3=一 Eb5/1=条",
    20: "C5/12=河",
    21: "Eb5/2=袅 D5/2=袅 C5/2=炊 Bb4/6=烟",
    22: "C5/2=小 Bb4/2=小 Ab4/2=村 G4/6=落",
    23: "D4/4=路 C4/2=上 Bb3/4=一 (F4/1=道 Eb4/1)",
    24: "Eb4/12=辙",
    25: "G4/2=我 (Ab4/2=最 Bb4/2) Ab4/2=亲 G4/2=爱 Eb4/2=的",
    26: "(Bb4/2=祖 G4/3 Eb4/1) Eb4/12=国",
    27: "Bb4/2=我 Bb4/2=永 Bb4/2=远 C5/2=紧 Ab4/2=贴 Ab4/2=着",
    28: "Bb4/2=你 G4/3=的 D4/1=心 Eb4/12=窝",
    29: "Bb4/2=你 Ab4/2=用 G4/2=你 F4/6=那",
    30: "D4/1=母 D4/1=亲 C4/2=的 Bb3/2=脉 G4/6=搏",
    31: "Ab4/6=和 F4/4=我 Eb4/2=诉",
    32: "Eb4/6~=说 Eb4/4 r/2",
    41: "(Bb4/2=我 C5/2) Bb4/2=的 (Ab4/2=祖 G4/2) F4/2=国",
    42: "Eb4/6=和 Bb3/6=我",
    43: "C4/2=像 Eb4/2=海 C5/2=和 A4/2=浪 A4/3=花 F4/1=一",
    44: "(Eb4/6=朵 D4/6)",
    45: "Ab4/2=浪 Bb4/2=是 Ab4/2=那 (G4/2=海 F4/2) Eb4/2=的",
    46: "C4/6=赤 A3/6=子",
    49: "Bb4/2=每 (C5/2=当 Bb4/2) Ab4/2=大 G4/2=海 F4/2=在",
    50: "Eb4/6=微 Bb3/6=笑",
    51: "Bb3/2=我 Eb4/2=就 G4/2=是 Bb4/2=笑 D5/3=的 Bb4/1=漩",
    52: "Ab4/12=涡",
    53: "G4/2=我 F4/2=分 Eb4/2=担 D4/6=着",
    54: "Ab4/2=海 G4/2=的 F4/2=忧 Eb4/6=愁",
    55: "D4/4=分 C4/2=享 Bb3/2=海 Bb3/2=的 (F4/1=欢 Eb4/1)",
    56: "Eb4/12=乐",
    59: "G4/4=你 Bb4/2=是 (C5/2=大 Ab4/2) Ab4/2=海",
    60: "Bb4/2=永 G4/3=不 D4/1=干 Eb4/12=涸",
    61: "Bb4/2=永 Ab4/2=远 G4/2=给 F4/6=我",
    62: "D4/2=碧 C4/2=浪 Bb3/2=清 G4/6=波",
    63: "Ab4/6=心 F4/4=中 Eb4/2=的",
    64: "Eb4/12=歌",
    65: "G4/2=啦 Ab4/2=啦 Bb4/2=啦 Ab4/2=啦 G4/2=啦 Eb4/2=啦",
    66: "Bb4/2=啦 G4/3=啦 Eb4/1=啦 Eb4/12=啦",
    67: "Bb4/2=啦 Bb4/2=啦 Bb4/2=啦 C5/2=啦 Ab4/2=啦 Ab4/2=啦",
    68: "Bb4/2=啦 G4/3=啦 D4/1=啦 Eb4/12=啦",
    69: "Bb4/2=永 Ab4/2=远 G4/2=给 F4/6=我",
    70: "D4/2=碧 C4/2=浪 Bb3/2=清 G4/6=波",
    71: "Ab4/6=心 Ab4/4^=中 G4/2=的",
    72: "G4/12~=歌",
    73: "G4/6^ r/6",
}
ALT[57], ALT[58] = ALT[25], ALT[26]

TEN = {
    21: "(G4/6=呜 F4/6)",
    22: "Eb4/12=呜",
    25: "Bb3/2=我 C4/4=最 C4/2=亲 G3/2=爱 Ab3/2=的",
    26: "(Bb3/2=祖 C4/3 Bb3/1) (C4/6=国 Ab3/6)",
    27: "Bb3/2=我 Bb3/2=永 Bb3/2=远 Eb4/2=紧 Eb4/2=贴 Eb4/2=着",
    28: "Bb3/2=你 Bb3/3=的 Bb3/1=心 (G3/6=窝 A3/6)",
    29: "F4/2=你 F4/2=用 F4/2=你 D4/6=那",
    30: "G3/1=母 G3/1=亲 Ab3/2=的 Bb3/2=脉 Eb4/6=搏",
    31: "Eb4/6=和 D4/4=我 Bb3/2=诉",
    32: "Bb3/6~=说 Bb3/4 r/2",
    41: "(G3/6=呜 Ab3/6)",
    42: "G3/12=呜",
    43: "(C4/6=呜 F3/6)",
    44: "F3/12=呜",
    45: "C4/12=呜",
    46: "F3/10=呜 r/2",
    47: "(Bb3/6=呜 Eb4/6~)",
    48: "Eb4/6 r/6",
    49: "(G3/6=呜 Ab3/6)",
    50: "(Eb3/6=呜 Bb3/6)",
    51: "G3/2=我 Bb3/2=就 Eb4/2=是 Bb3/2=笑 G3/3=的 G3/1=漩",
    52: "C4/12=涡",
    53: "C4/2=我 C4/2=分 C4/2=担 D4/6=着",
    54: "C4/2=海 Eb4/2=的 C4/2=忧 Bb3/6=愁",
    55: "F3/4=分 Ab3/2=享 Eb3/2=海 Eb3/2=的 (D3/1=欢 Eb3/1)",
    56: "G3/12=乐",
    59: "Eb4/4=你 Eb4/2=是 (Eb4/2=大 C4/2) C4/2=海",
    60: "G3/2=永 D4/3=不 Bb3/1=干 (G3/6=涸 A3/6)",
    61: "F4/2=永 F4/2=远 F4/2=给 D4/6=我",
    62: "G3/2=碧 Ab3/2=浪 Bb3/2=清 Eb4/6=波",
    63: "Eb4/6=心 D4/4=中 Bb3/2=的",
    64: "G3/12=歌",
    # la-la: the men row the boat (long-short, long-short)
    65: "Bb3/4=啦 G3/2=啦 Eb4/4=啦 G3/2=啦",
    66: "Bb3/4=啦 Bb3/2=啦 C4/4=啦 Eb4/2=啦 Ab3/4=啦 Bb3/2=啦",
    67: "G3/4=啦 Bb3/2=啦 Ab3/4=啦 C4/2=啦",
    68: "Bb3/4=啦 Bb3/2=啦 G3/4=啦 C4/2=啦 A3/4=啦 C4/2=啦",
    69: "D4/2=永 D4/2=远 Bb3/2=给 F3/6=我",
    70: "G3/2=碧 Bb3/2=浪 Bb3/2=清 C4/6=波",
    71: "Eb4/6=心 D4/4^=中 Eb4/2=的",
    72: "Bb3/12~=歌",
    73: "Bb3/6^ r/6",
}
TEN[57], TEN[58] = TEN[25], TEN[26]

BAS = {
    21: "(C3/6=呜 G2/6)",
    22: "(Ab2/6=呜 Bb2/6)",
    25: "Eb3/2=我 Eb3/4=最 C3/2=亲 Bb2/2=爱 Ab2/2=的",
    26: "G2/6=祖 (Ab2/6=国 Bb2/6)",
    27: "G2/2=我 G2/2=永 G2/2=远 Ab2/2=紧 Ab2/2=贴 Ab2/2=着",
    28: "G2/2=你 G2/3=的 G2/1=心 (Eb3/6=窝 F3/6)",
    29: "Bb2/2=你 Bb2/2=用 Bb2/2=你 Bb2/6=那",
    30: "Eb3/1=母 Eb3/1=亲 Eb3/2=的 Eb3/2=脉 C3/6=搏",
    31: "Ab2/6=和 Bb2/4=我 Bb2/2=诉",
    32: "Eb3/6~=说 Eb3/4 r/2",
    41: "Eb3/12=呜",
    42: "Eb3/12=呜",
    43: "(Ab2/6=呜 A2/6)",
    44: "Bb2/12=呜",
    45: "Ab2/12=呜",
    46: "A2/10=呜 r/2",
    47: "D3/2=海 C3/2=是 Bb2/2=那 Bb3/2=浪 Eb3/3=的 F3/1=依",
    48: "G3/12=托",
    49: "(C3/6=呜 F2/6)",
    50: "(Ab2/6=呜 Bb2/6)",
    51: "Eb3/2=我 Eb3/2=就 Eb3/2=是 G2/2=笑 G2/3=的 G2/1=漩",
    52: "Ab2/12=涡",
    53: "C3/2=我 C3/2=分 C3/2=担 G2/6=着",
    54: "Ab2/2=海 Ab2/2=的 Ab2/2=忧 Bb2/6=愁",
    55: "Bb2/4=分 Bb2/2=享 Bb2/2=海 Bb2/2=的 Bb2/2=欢",
    56: "Eb3/12=乐",
    59: "G2/4=你 G2/2=是 Ab2/4=大 Ab2/2=海",
    60: "G2/2=永 G2/3=不 G2/1=干 (Eb3/6=涸 F3/6)",
    61: "Bb2/2=永 Bb2/2=远 Bb2/2=给 Bb2/6=我",
    62: "Eb3/2=碧 Eb3/2=浪 Eb3/2=清 C3/6=波",
    63: "Ab2/6=心 Bb2/4=中 Bb2/2=的",
    64: "Eb3/12=歌",
    65: "Eb3/4=啦 Bb2/2=啦 C3/4=啦 G2/2=啦",
    66: "G2/4=啦 Bb2/2=啦 Ab2/4=啦 Eb3/2=啦 Bb2/4=啦 F3/2=啦",
    67: "G2/4=啦 Eb3/2=啦 Ab2/4=啦 Eb3/2=啦",
    68: "G2/4=啦 D3/2=啦 C3/4=啦 G2/2=啦 F2/4=啦 C3/2=啦",
    69: "Bb2/2=永 Bb2/2=远 Bb2/2=给 Bb2/6=我",
    70: "Eb3/2=碧 Eb3/2=浪 Eb3/2=清 Ab2/6=波",
    71: "Bb2/6=心 Bb2/4^=中 Bb2/2=的",
    72: "Eb3/12~=歌",
    73: "Eb3/6^ r/6",
}
BAS[57], BAS[58] = BAS[25], BAS[26]

# ============================== STRINGS =====================================
VN1 = {
    3: "(Eb5/2 F5/2 G5/2 F5/2 Eb5/2 C5/2)",
    4: "(D5/2 Bb4/3 G4/1) C5/12",
    5: "(D5/2 C5/2 Bb4/2 Ab4/6)",
    6: "(Bb4/2 Ab4/2 G4/2 Eb5/6)",
    7: "(C5/6 Ab4/4 G4/2)",
    12: "r/6 (D5/2 C5/3 G4/1)",
    20: "r/4 (C6/1 Bb5/1 Ab5/1 G5/1 Eb5/1 C5/1 Bb4/1 Ab4/1)",
    26: "r/6 (Eb6/2 C6/3 G5/1 Bb5/6)",
    28: "r/6 (D6/2 Bb5/3 G5/1 A5/6)",
    29: "(Bb5/6 Ab5/6)",
    30: "(G5/6 Bb5/6)",
    31: "(Ab5/6 F5/6)",
    32: "G5/4 r/2 (F4/1 G4/1 Ab4/1 Bb4/1 C5/1 D5/1)",
    33: "(Eb5/2 F5/2 G5/2 F5/2 Eb5/2 C5/2)",
    34: "(D5/2 C5/3 G4/1) Bb4/12",
    35: "(Eb5/2 F5/2 G5/2 F5/2 Eb5/2 C5/2)",
    36: "(D5/2 Bb4/3 G4/1) C5/12",
    37: "D5/12",
    38: "(D5/6 Eb5/6)",
    39: "(C5/6 Bb4/6)",
    40: "Bb4/12",
    47: "F5/6 Ab5/6",
    48: "G5/6 F5/6",
    50: "r/6 (D5/2 Eb5/2 F5/2)",
    51: "(G5/6 F5/6)",
    52: "C6/1 Bb5/1 Ab5/1 G5/1 Ab5/1 Bb5/1 C6/1 Bb5/1 Ab5/1 G5/1 Eb5/1 "
        "C5/1",
    53: "(Bb5/4 C6/2 D6/6)",
    54: "(C6/6 Bb5/6)",
    55: "(Ab5/6 G5/6)",
    56: "r/10 Bb5/1 D6/1",
    57: "(Eb6/2 F6/2 G6/2 F6/2 Eb6/2 C6/2)",
    58: "(D6/2 C6/3 G5/1) Bb5/6 (Eb6/2 C6/3 G5/1)",
    59: "(Eb6/2 F6/2 G6/2 F6/2 Eb6/2 C6/2)",
    60: "(D6/2 Bb5/3 G5/1) C6/6 (Eb6/2 C6/3 A5/1)",
    61: "(Bb5/2 Ab5/2 G5/2 F5/6)",
    62: "(D5/2 C5/2 Bb4/2 G5/6)",
    63: "(Ab5/6 F5/4 Eb5/2)",
    64: "Bb5/4 r/2 (F5/1 G5/1 Ab5/1 Bb5/1 C6/1 D6/1)",
    65: "(Eb6/2 F6/2 G6/2) (F6/2 Eb6/2 C6/2)",
    66: "(D6/2 C6/3 G5/1) (Bb5/6 Eb6/6)",
    67: "(Eb6/2 F6/2 G6/2) (F6/2 Eb6/2 C6/2)",
    68: "(D6/2 Bb5/3 G5/1) C6/6 (A5/2 C6/2 Eb6/2)",
    69: "(D6/4 F6/2 Ab6/6)",
    70: "(G6/6 Eb6/6)",
    71: "C6/6 F6/4^ Eb6/2",
    72: "Eb6/12~",
    73: "Eb6/6^ r/6",
}

VN2 = {
    1: "r/2 G4/2 Bb4/2 r/2 G4/2 C5/2",
    2: "r/2 Bb4/2 D5/2 r/2 C5/2 Eb5/2 r/2 Ab4/2 Eb5/2",
    3: "r/2 G4/2 Bb4/2 r/2 Ab4/2 C5/2",
    4: "r/2 Bb4/2 D5/2 r/2 G4/2 Bb4/2 r/2 A4/2 r/2",
    5: "D4/12",
    6: "Bb3/6 Eb4/6",
    7: "Eb4/6 D4/4 Bb3/2",
    8: "r/2 G4/2 Bb4/2 r/2 Eb5/2 Bb4/2",
    9: "r/2 G4/2 Bb4/2 r/2 C5/2 Eb5/2",
    10: "r/2 G4/2 Bb4/2 r/2 G4/2 Eb5/2",
    11: "r/2 C5/2 G4/2 r/2 C5/2 F5/2",
    12: "r/2 F4/2 Bb4/2 r/6",
    13: "r/2 Eb4/2 Ab4/2 r/2 C5/2 Eb5/2",
    14: "r/2 C4/2 F4/2 r/2 A4/2 Eb5/2",
    15: "r/2 D5/2 F5/2 r/2 Ab4/2 Eb5/2",
    16: "r/2 Eb4/2 G4/2 r/2 F4/2 B4/2",
    17: "r/2 G4/2 Eb5/2 r/2 C5/2 Eb5/2",
    18: "r/2 G4/2 C5/2 r/2 F4/2 Bb4/2",
    19: "r/2 Bb4/2 G4/2 r/2 D5/2 Bb4/2",
    23: "F4/12",
    24: "r/7 Eb5/1 G5/1 Bb5/3",
    25: "Bb4/12",
    26: "r/6 G4/12",
    27: "Eb4/12",
    28: "G4/12 F4/6",
    29: "D4/12",
    30: "Bb3/6 Eb4/6",
    31: "Eb4/6 Ab3/4 G3/2",
    32: "Eb4/4 r/2 (Bb3/1 Eb4/1 F4/1 G4/1 Ab4/1 Bb4/1)",
    33: "Bb3/1 Eb4/1 G4/1 Bb4/1 G4/1 Eb4/1 C4/1 Eb4/1 G4/1 C5/1 Eb4/1 G4/1",
    34: "G3/1 Bb3/1 D4/1 F4/1 D4/1 Bb3/1 Ab3/1 C4/1 Eb4/1 G4/1 Eb4/1 C4/1 "
        "Bb3/1 Eb4/1 F4/1 Ab4/1 F4/1 Eb4/1",
    35: "Bb3/1 Eb4/1 G4/1 Bb4/1 G4/1 Eb4/1 C4/1 Eb4/1 Ab4/1 C5/1 Ab4/1 Eb4/1",
    36: "Bb3/1 D4/1 G4/1 D4/1 Bb3/1 D4/1 C4/1 Eb4/1 G4/1 Bb4/1 G4/1 Eb4/1 "
        "A3/1 C4/1 Eb4/1 F4/1 C4/1 A3/1",
    37: "F4/1 Ab4/1 Bb4/1 F4/1 D4/1 F4/1 D4/1 F4/1 Ab4/1 Bb4/1 Ab4/1 F4/1",
    38: "G3/1 Bb3/1 D4/1 Eb4/1 D4/1 Bb3/1 G3/1 C4/1 Eb4/1 G4/1 Eb4/1 C4/1",
    39: "Ab3/1 C4/1 Eb4/1 Ab4/1 Eb4/1 C4/1 D4/1 F4/1 Ab4/1 F4/1 D4/1 Bb3/1",
    40: "G4/12",
    47: "D5/6 Eb5/6",
    48: "Eb5/6 D5/6",
    51: "Eb5/6 Bb4/6",
    52: "Eb5/1 G5/1 Eb5/1 C5/1 Eb5/1 G5/1 Eb5/1 C5/1 Eb5/1 G5/1 Ab5/1 G5/1",
    53: "G4/6 F4/6",
    54: "Eb4/6 G4/6",
    55: "D4/6 Bb3/6",
    56: "r/7 Eb5/1 G5/1 Bb5/3",
    57: "G4/1 Eb4/1 C5/1 Eb5/1 C5/1 G4/1 C4/1 F4/1 G4/1 C5/1 G4/1 Eb4/1",
    58: "G3/1 Bb3/1 C4/1 G4/1 Eb4/1 Bb3/1 Ab3/1 C4/1 Eb4/1 Bb4/1 Eb4/1 C4/1 "
        "Bb3/1 Eb4/1 F4/1 Ab4/1 F4/1 Eb4/1",
    59: "G3/1 Bb3/1 Eb4/1 G4/1 Bb4/1 G4/1 Ab3/1 C4/1 Eb4/1 Ab4/1 C5/1 Ab4/1",
    60: "Bb3/1 D4/1 G4/1 D4/1 Bb3/1 D4/1 Eb4/1 C4/1 G4/1 C5/1 G4/1 Eb4/1 "
        "A3/1 C4/1 Eb4/1 F4/1 Eb4/1 C4/1",
    61: "D4/1 F4/1 Bb4/1 F4/1 D4/1 F4/1 D4/1 F4/1 Ab4/1 Bb4/1 Ab4/1 F4/1",
    62: "G4/1 Bb4/1 Ab4/1 Bb4/1 G4/1 Bb4/1 C4/1 Eb4/1 G4/1 C5/1 G4/1 Eb4/1",
    63: "Ab3/1 C4/1 Eb4/1 Ab4/1 Eb4/1 C4/1 D4/1 F4/1 Ab4/1 Bb4/1 G4/1 Eb4/1",
    64: "Eb4/4 r/2 (D5/1 Eb5/1 F5/1 G5/1 Ab5/1 Bb5/1)",
    65: "(G5/2 Ab5/2 Bb5/2) (Ab5/2 G5/2 Eb5/2)",
    66: "(Bb5/2 G5/3 Eb5/1) Eb5/12",
    67: "Bb5/6 (C6/2 Ab5/4)",
    68: "(Bb5/2 G5/3 D5/1) Eb5/12",
    69: "(Bb5/2 Ab5/2 G5/2 F5/6)",
    70: "(D5/2 C5/2 Bb4/2 G5/6)",
    71: "Ab5/6 Ab5/4^ G5/2",
    72: "r/3 G5/3 G5/3 G5/3",
    73: "G5/6^ r/6",
}

VA = {
    1: "(Eb4/2 F4/2 G4/2 F4/2 Eb4/2 C4/2)",
    2: "(D4/2 C4/3 G3/1) Bb3/12",
    3: "Bb3/6 C4/6",
    4: "Bb3/6 Eb4/12",
    5: "(Bb4/2 Ab4/2 G4/2 F4/6)",
    6: "(D4/2 C4/2 Bb3/2 G4/6)",
    7: "(Ab4/6 F4/4 Eb4/2)",
    8: "r/6 Bb3/2 r/4",
    9: "Eb3/2 r/4 Eb3/2 r/4",
    10: "Eb3/2 r/4 G3/2 r/4",
    11: "Ab3/2 r/4 F3/2 r/4",
    12: "Eb3/2 r/4 D3/2 r/4",
    13: "Ab3/2 r/4 Eb3/2 r/4",
    14: "Eb3/2 r/4 F3/2 r/4",
    15: "Ab3/2 r/4 Ab3/2 r/4",
    16: "Bb3/2 r/4 (B3/2 D4/2 F4/2)",
    17: "(G4/4 F4/2 Eb4/6)",
    18: "C4/6 (Eb4/3 D4/3)",
    19: "G3/6 (Bb3/4 F4/2)",
    20: "Eb4/12",
    23: "Ab3/12",
    24: "r/4 Eb4/1 G4/1 Bb4/6",
    25: "Eb4/6 C4/6",
    26: "G3/6 Eb3/12",
    27: "Bb3/6 C4/6",
    28: "D4/6 C4/12",
    29: "Ab3/12",
    30: "Bb3/6 C4/6",
    31: "C4/6 D4/4 Eb4/2",
    32: "G3/6 Bb3/6",
    33: "G3/12",
    34: "Bb3/6 (Eb4/2 C4/3 G3/1 Bb3/6)",
    35: "Bb3/6 C4/6",
    36: "Bb3/6 (Eb4/2 C4/3 G3/1 A3/6)",
    37: "D4/12",
    38: "G3/6 C3/6",
    39: "Eb3/6 (F3/4 G3/2)",
    40: "G3/12",
    49: "r/2 Eb3/2 G3/2 r/2 Ab3/2 C4/2",
    50: "r/2 C4/2 Eb4/2 r/2 Eb4/2 D4/2",
    51: "r/2 G3/2 Bb3/2 r/2 Bb3/2 F4/2",
    52: "C4/12",
    53: "Eb4/6 Bb3/6",
    54: "C4/6 Eb4/6",
    55: "Ab3/6 Bb3/4 Ab3/2",
    56: "r/4 Eb4/1 G4/1 Bb4/6",
    57: "Eb4/6 C4/6",
    58: "Bb3/6 C4/6 Ab3/6",
    59: "Bb3/6 C4/6",
    60: "Bb3/6 Eb4/12",
    61: "Ab3/12",
    62: "Bb3/6 C4/6",
    63: "C4/6 Ab3/4 G3/2",
    64: "G3/6 Bb3/6",
    65: "Bb3+Eb4/4 Bb3+Eb4/2 C4+Eb4/4 C4+Eb4/2",
    66: "Bb3+D4/4 Bb3+Eb4/2 C4+Eb4/4 Ab3+Eb4/2 Ab3+Eb4/4 Ab3+F4/2",
    67: "Bb3+Eb4/4 Bb3+Eb4/2 C4+Eb4/4 C4+Ab4/2",
    68: "Bb3+D4/4 Bb3+D4/2 C4+G4/4 C4+Eb4/2 A3+Eb4/4 A3+F4/2",
    69: "Bb3+F4/12",
    70: "Bb3+F4/6 C4+Eb4/6",
    71: "C4+Eb4/6 D4+F4/4^ Eb4+G4/2",
    72: "r/3 Eb4+Bb4/3 Eb4+Bb4/3 Eb4+Bb4/3",
    73: "Eb4+Bb4/6^ r/6",
}

VC = {
    1: "Eb2/2 r/4 C3/2 r/4",
    2: "G2/2 r/4 Ab2/2 r/4 Bb2/2 r/4",
    3: "G2/2 r/4 Ab2/2 r/4",
    4: "G2/2 r/4 C3/2 r/4 F2/2 r/4",
    5: "Bb2/12",
    6: "Eb3/6 C3/6",
    7: "Ab2/6 Bb2/6",
    8: "Eb2/12",
    9: "Eb2/12",
    10: "Eb2/12",
    11: "Ab2/6 A2/6",
    12: "Bb2/12",
    13: "Ab2/12",
    14: "A2/12",
    15: "Bb2/12",
    16: "Eb3/6 B2/6",
    17: "C3/6 F2/6",
    18: "Ab2/6 Bb2/6",
    19: "Eb2/6 G2/6",
    20: "Ab2/12",
    23: "Bb2/12",
    24: "Eb2/1 Bb2/1 Eb3/1 G3/9",
    25: "Eb2/4 Bb2/2 C3/2 Bb2/2 Ab2/2",
    26: "G2/6 Ab2/6 Bb2/6",
    27: "G2/6 Ab2/6",
    28: "G2/6 C2/6 F2/6",
    29: "Bb2/10 r/2",
    30: "Eb2/2 r/4 C3/2 r/4",
    31: "Ab2/6 Bb2/6",
    32: "Eb2/12",
    33: "Eb2/4 Bb2/2 C3/4 G2/2",
    34: "G2/6 Ab2/6 Bb2/6",
    35: "G2/4 Eb3/2 Ab2/4 Eb3/2",
    36: "G2/6 Eb3/6 F2/6",
    37: "(Bb3/2 Ab3/2 G3/2 F3/6)",
    38: "(D3/2 C3/2 Bb2/2 G3/6)",
    39: "(Ab3/6 F3/4 Eb3/2)",
    40: "Eb2/4 Bb2/2 Eb3/4 Bb2/2",
    41: "Eb2/4 Bb2/2 Eb2/4 C3/2",
    42: "Eb2/4 Bb2/2 Eb2/4 Bb2/2",
    43: "Ab2/4 Eb3/2 A2/4 F3/2",
    44: "Bb2/4 F3/2 Bb2/4 F3/2",
    45: "Ab2/4 Eb3/2 Ab2/4 Eb3/2",
    46: "A2/4 Eb3/2 A2/4 C3/2",
    47: "Bb2/12",
    48: "Eb2/4 Bb2/2 B2/4 D3/2",
    49: "C3/4 Eb3/2 F2/4 C3/2",
    50: "Ab2/4 Eb3/2 Bb2/4 F3/2",
    51: "Eb2/4 Bb2/2 G2/6",
    52: "Ab2/12",
    53: "C3/4 G2/2 G2/4 D3/2",
    54: "Ab2/4 Eb3/2 Bb2/4 F3/2",
    55: "Bb2/4 F3/2 Bb2/4 F3/2",
    56: "Eb2/1 Bb2/1 Eb3/1 G3/9",
    57: "Eb2/4 Bb2/2 C3/2 Bb2/2 Ab2/2",
    58: "G2/6 Ab2/6 Bb2/6",
    59: "G2/6 Ab2/6",
    60: "G2/6 C2/6 F2/6",
    61: "Bb2/12",
    62: "Eb2/6 C2/6",
    63: "Ab2/6 Bb2/6",
    64: "Eb2/12",
    65: "Eb2/1 Bb2/1 Eb3/1 Bb3/1 Eb4/1 G3/1 C3/1 Eb3/1 C4/1 Eb4/1 G3/1 C3/1",
    66: "G2/1 D3/1 G3/1 Bb3/1 Eb4/1 Bb3/1 Ab2/1 Eb3/1 Ab3/1 C4/1 Ab3/1 Eb3/1 "
        "Bb2/1 F3/1 Ab3/1 Bb3/1 Eb4/1 Bb3/1",
    67: "G2/1 Bb2/1 Eb3/1 G3/1 Bb3/1 Eb4/1 Ab2/1 Eb3/1 Ab3/1 C4/1 Eb4/1 C4/1",
    68: "G2/1 D3/1 G3/1 Bb3/1 D4/1 Bb3/1 C3/1 G3/1 C4/1 Eb4/1 C4/1 G3/1 "
        "F2/1 C3/1 F3/1 A3/1 C4/1 Eb4/1",
    69: "Bb2/12",
    70: "Eb2/6 Ab2/6",
    71: "Bb2/6 Bb2/4^ Bb2/2",
    72: "Eb2/12~",
    73: "Eb2/6^ r/6",
}

# pizzicato ranges: (bar, 16th) from -> (bar, 16th) to (exclusive)
PIZZ = {
    "vn2": [(1, 0, 5, 0), (8, 0, 21, 0)],
    "va": [(8, 0, 16, 6)],
    "vc": [(1, 0, 5, 0), (30, 0, 31, 0)],
}

# ============================== EXPRESSION ==================================
VOCAL_BREATHS = {
    "sop": [(25, 0), (27, 0), (29, 0), (31, 0), (41, 0), (43, 0), (45, 0),
            (49, 0), (51, 0), (53, 0), (54, 0), (55, 0), (57, 0), (59, 0),
            (61, 0), (63, 0), (65, 0), (67, 0), (69, 0), (71, 0)],
    "alt": [(9, 0), (11, 0), (13, 0), (15, 0), (17, 0), (19, 0), (21, 0),
            (22, 0), (23, 0), (25, 0), (27, 0), (29, 0), (31, 0), (41, 0),
            (43, 0), (45, 0), (49, 0), (51, 0), (53, 0), (54, 0), (55, 0),
            (57, 0), (59, 0), (61, 0), (63, 0), (65, 0), (67, 0), (69, 0),
            (71, 0)],
    "ten": [(21, 0), (25, 0), (27, 0), (29, 0), (31, 0), (41, 0), (43, 0),
            (45, 0), (47, 0), (49, 0), (51, 0), (53, 0), (54, 0), (55, 0),
            (57, 0), (59, 0), (61, 0), (63, 0), (65, 0), (67, 0), (69, 0),
            (71, 0)],
    "bas": [(21, 0), (25, 0), (27, 0), (29, 0), (31, 0), (41, 0), (43, 0),
            (45, 0), (47, 0), (49, 0), (51, 0), (53, 0), (54, 0), (55, 0),
            (57, 0), (59, 0), (61, 0), (63, 0), (65, 0), (67, 0), (69, 0),
            (71, 0)],
}

_END_DIM = [(72, 0, 72, 11, "dim")]
VOCAL_DYN = {
    "sop": [(25, 0, "mf"), (29, 0, "p"), (41, 0, "mp"), (49, 0, "p"), (51, 0, "mf"),
            (57, 0, "f"), (61, 0, "mp"), (65, 0, "ff"), (72, 0, "f"),
            (73, 0, "p")],
    "alt": [(9, 0, "mp"), (21, 0, "p"), (23, 0, "mp"), (25, 0, "mf"),
            (29, 0, "mp"), (41, 0, "mp"), (51, 0, "mf"), (57, 0, "f"),
            (61, 0, "mf"), (65, 0, "ff"), (72, 0, "f"), (73, 0, "p")],
    "ten": [(21, 0, "pp"), (25, 0, "mf"), (29, 0, "mp"), (41, 0, "pp"),
            (51, 0, "mf"), (57, 0, "f"),
            (61, 0, "mf"), (65, 0, "f"), (69, 0, "ff"), (72, 0, "f"),
            (73, 0, "p")],
    "bas": [(21, 0, "pp"), (25, 0, "mf"), (29, 0, "mp"), (41, 0, "pp"),
            (47, 0, "mp"), (49, 0, "pp"), (51, 0, "mf"), (57, 0, "f"),
            (61, 0, "mf"), (65, 0, "f"), (69, 0, "ff"), (72, 0, "f"),
            (73, 0, "p")],
}
VOCAL_HAIR = {
    "sop": [(55, 0, 56, 11, "cresc"), (63, 0, 64, 11, "cresc")] + _END_DIM,
    "alt": [(23, 6, 24, 11, "cresc"), (55, 0, 56, 11, "cresc"),
            (63, 0, 64, 11, "cresc")] + _END_DIM,
    "ten": [(55, 0, 56, 11, "cresc"), (63, 0, 64, 11, "cresc")] + _END_DIM,
    "bas": [(55, 0, 56, 11, "cresc"), (63, 0, 64, 11, "cresc")] + _END_DIM,
}
VOCAL_TEXT = {
    "sop": [(72, 3, "dim.")],
    "alt": [(9, 0, "dolce, semplice"), (72, 3, "dim.")],
    "ten": [(21, 0, "呜 = u"), (41, 0, "呜 = u"), (72, 3, "dim.")],
    "bas": [(72, 3, "dim.")],
}

STR_DYN = {
    "vn1": [(3, 0, "mp"), (5, 0, "mf"), (7, 0, "mp"), (12, 6, "p"),
            (20, 4, "pp"), (26, 6, "mp"), (32, 6, "mf"), (33, 0, "f"),
            (37, 0, "mp"), (40, 0, "p"), (47, 0, "pp"), (50, 6, "p"),
            (52, 0, "mp"), (53, 0, "mf"), (56, 10, "f"), (61, 0, "mf"),
            (64, 6, "f"), (65, 0, "ff"), (72, 0, "f"), (73, 0, "p")],
    "vn2": [(1, 0, "p"), (5, 0, "mf"), (7, 0, "mp"), (8, 0, "p"),
            (23, 0, "p"), (24, 7, "p"), (25, 0, "mp"),
            (32, 6, "mf"), (33, 0, "f"), (37, 0, "mp"), (40, 0, "p"),
            (47, 0, "pp"), (51, 0, "mp"), (56, 7, "mp"), (57, 0, "mf"),
            (61, 0, "mp"), (64, 6, "f"), (65, 0, "ff"), (72, 0, "f"),
            (73, 0, "p")],
    "va": [(1, 0, "mp"), (5, 0, "mf"), (7, 0, "mp"), (8, 0, "p"),
           (17, 0, "p"), (23, 0, "p"), (24, 4, "p"), (25, 0, "mp"),
           (32, 0, "mf"), (33, 0, "f"), (37, 0, "mp"),
           (40, 0, "p"), (49, 0, "p"), (51, 0, "mp"), (56, 4, "mp"),
           (57, 0, "mf"),
           (61, 0, "mp"), (64, 0, "mf"), (65, 0, "f"),
           (73, 0, "p")],
    "vc": [(1, 0, "p"), (5, 0, "mf"), (7, 0, "mp"), (8, 0, "p"),
           (17, 0, "p"), (23, 0, "p"), (24, 0, "mp"), (25, 0, "mf"),
           (29, 0, "mp"), (30, 0, "p"), (31, 0, "mp"), (32, 0, "mf"),
           (33, 0, "f"), (37, 0, "mf"), (40, 0, "p"),
           (51, 0, "mp"), (56, 0, "mf"), (57, 0, "f"), (61, 0, "mf"),
           (64, 0, "mf"), (65, 0, "f"), (73, 0, "p")],
}
_SWELLS = [(5, 0, 5, 11, "cresc"), (7, 0, 7, 11, "dim"),
           (37, 0, 39, 11, "dim"), (53, 0, 55, 11, "cresc"),
           (64, 6, 64, 11, "cresc")] + _END_DIM
_INNER = [h for h in _SWELLS if h[:2] != (53, 0)]
STR_HAIR = {
    "vn1": _SWELLS + [(32, 6, 32, 11, "cresc")],
    "vn2": _INNER + [(24, 7, 24, 11, "cresc"), (32, 6, 32, 11, "cresc"),
                      (56, 7, 56, 11, "cresc")],
    "va": _INNER + [(24, 4, 24, 11, "cresc"), (32, 0, 32, 11, "cresc"),
                     (56, 4, 56, 11, "cresc")],
    "vc": _SWELLS + [(24, 0, 24, 11, "cresc"), (32, 0, 32, 11, "cresc"),
                     (56, 0, 56, 11, "cresc")],
}
STR_TEXT = {
    "vn1": [(3, 0, "espr."), (12, 6, "dolce"), (20, 4, "leggiero"),
            (26, 6, "dolce"), (33, 0, "cantabile"), (47, 0, "sul tasto"),
            (50, 6, "ord."), (52, 0, "leggiero")],
    "vn2": [(47, 0, "sul tasto"), (51, 0, "ord."), (52, 0, "leggiero")],
    "va": [(1, 0, "cantabile"), (16, 6, "espr."), (49, 0, "dolce")],
    "vc": [(37, 0, "espr., cantabile")],
}

VEL = {"pp": 34, "p": 46, "mp": 60, "mf": 74, "f": 90, "ff": 104}
ACCENT = 14


def _part(pid, name, abbr, midi_name, inst, cl, program, data, vocal):
    d = dict(id=pid, name=name, abbr=abbr, midi_name=midi_name, inst=inst,
             clef=cl, program=program, data=data, vocal=vocal)
    if vocal:
        d.update(dyn=VOCAL_DYN[pid], hair=VOCAL_HAIR[pid],
                 text=VOCAL_TEXT[pid], breaths=VOCAL_BREATHS[pid],
                 print_hair=False)
    else:
        d.update(dyn=STR_DYN[pid], hair=STR_HAIR[pid], text=STR_TEXT[pid])
    return d


PARTS = [
    _part("sop", "Soprano", "S.", "Soprano 女高音", instrument.Soprano,
          clef.TrebleClef, 52, SOP, True),
    _part("alt", "Alto", "A.", "Alto 女低音", instrument.Alto,
          clef.TrebleClef, 52, ALT, True),
    _part("ten", "Tenor", "T.", "Tenor 男高音", instrument.Tenor,
          clef.Treble8vbClef, 52, TEN, True),
    _part("bas", "Bass", "B.", "Bass 男低音", instrument.Bass,
          clef.BassClef, 52, BAS, True),
    _part("vn1", "Violin I", "Vln. I", "Violin I", instrument.Violin,
          clef.TrebleClef, 40, VN1, False),
    _part("vn2", "Violin II", "Vln. II", "Violin II", instrument.Violin,
          clef.TrebleClef, 40, VN2, False),
    _part("va", "Viola", "Vla.", "Viola", instrument.Viola,
          clef.AltoClef, 41, VA, False),
    _part("vc", "Violoncello", "Vc.", "Violoncello", instrument.Violoncello,
          clef.BassClef, 42, VC, False),
]

SOUNDS = {"Soprano": ("Soprano", "voice.soprano"),
          "Alto": ("Alto", "voice.alto"),
          "Tenor": ("Tenor", "voice.tenor"),
          "Bass": ("Bass", "voice.bass"),
          "Violin I": ("Violin", "strings.violin"),
          "Violin II": ("Violin", "strings.violin"),
          "Viola": ("Viola", "strings.viola"),
          "Violoncello": ("Violoncello", "strings.cello")}

RANGES = {"sop": ("Bb3", "A5"), "alt": ("G3", "F5"), "ten": ("C3", "Bb4"),
          "bas": ("E2", "E4"), "vn1": ("G3", "A6"), "vn2": ("G3", "C6"),
          "va": ("C3", "C5"), "vc": ("C2", "E4")}

# (kind, part, part, bars) — deliberate exceptions to the checks
ALLOW = [
    ("parallel", "sop", "alt", {41, 42, 70}),  # unison / octaves: one line
    ("clash", "sop", "vn1", {32}), ("clash", "sop", "vn2", {32}),  # run
    ("clash", "ten", "vn1", {64}), ("clash", "ten", "vn2", {64}),  # run
]

# Tempo map (quarter-note BPM for MIDI; dotted quarter = 56 -> 84)
TEMPI = [(1, 0, 84), (32, 6, 78), (32, 9, 72), (33, 0, 84),
         (64, 6, 78), (64, 9, 72), (65, 0, 84),
         (69, 0, 80), (70, 0, 74), (71, 0, 68), (71, 6, 28), (71, 10, 62),
         (72, 0, 60), (72, 6, 54), (73, 0, 34), (73, 6, 50)]
TEMPO_TEXT = [(32, 6, "poco rit."), (33, 0, "a tempo"),
              (64, 6, "poco allarg."), (65, 0, "a tempo"),
              (69, 0, "allargando"), (72, 6, "rit.")]
SECTIONS = [(1, None, "Intro 前奏"), (9, "A", "Verse 1 主歌一"),
            (25, "B", "Chorus 1 副歌一"), (33, "C", "Interlude 间奏"),
            (41, "D", "Verse 2 主歌二"), (57, "E", "Chorus 2 副歌二"),
            (65, "F", "La-la 啦啦"), (69, "G", "Coda 尾声")]
SYSTEM_BREAKS = (5, 9, 13, 17, 21, 25, 29, 33, 35, 37, 41, 45, 49, 53, 57,
                 59, 61, 65, 67, 69, 72)   # 22 systems, 2 per page
# 8va lines (notation only; the MusicXML pitches stay at concert pitch):
# (part name, first bar, last bar)
OTTAVA = [("Violin I", 57, 60), ("Violin I", 65, 73)]

SUB_LINES = [
    ("我和我的祖国", "alt", 9, 10), ("一刻也不能分隔", "alt", 11, 12),
    ("无论我走到哪里", "alt", 13, 14), ("都流出一首赞歌", "alt", 15, 16),
    ("我歌唱每一座高山", "alt", 17, 18), ("我歌唱每一条河", "alt", 19, 20),
    ("袅袅炊烟", "alt", 21, 21), ("小小村落", "alt", 22, 22),
    ("路上一道辙", "alt", 23, 24),
    ("我最亲爱的祖国", "sop", 25, 26),
    ("我永远紧贴着你的心窝", "sop", 27, 28),
    ("你用你那母亲的脉搏", "alt", 29, 30), ("和我诉说", "alt", 31, 32),
    ("我的祖国和我", "sop", 41, 42), ("像海和浪花一朵", "sop", 43, 44),
    ("浪是那海的赤子", "sop", 45, 46), ("海是那浪的依托", "bas", 47, 48),
    ("每当大海在微笑", "alt", 49, 50), ("我就是笑的漩涡", "sop", 51, 52),
    ("我分担着", "sop", 53, 53), ("海的忧愁", "sop", 54, 54),
    ("分享海的欢乐", "alt", 55, 56),
    ("我最亲爱的祖国", "sop", 57, 58), ("你是大海永不干涸", "sop", 59, 60),
    ("永远给我碧浪清波", "alt", 61, 62), ("心中的歌", "alt", 63, 64),
    ("啦啦啦啦啦啦啦啦啦啦", "sop", 65, 66),
    ("啦啦啦啦啦啦啦啦啦啦", "sop", 67, 68),
    ("永远给我碧浪清波", "alt", 69, 70), ("心中的歌", "sop", 71, 73),
]
SUB_LEAD = 0.2
SUB_TAIL = 1.5

def _mscx_hook(x):
    """MS4 touch-up: bar 69 opens a system with a 6/8 change, so autoplace
    lifts the letter G above its section title.  Nudge it left to sit
    beside "Coda 尾声" like the other letters (PDF only)."""
    return re.sub(r'<offset x="0"( y="-?[\d.]+"/>\s*<text><b>G</b>)',
                  r'<offset x="-2"\1', x)


META = dict(
    title="我和我的祖国", title_latin="Wǒ Hé Wǒ De Zǔguó",
    subtitle="全曲 · 四声部独唱与弦乐四重奏",
    subtitle_en="Complete Song — for Vocal Quartet (S.A.T.B. soli) "
                "and String Quartet",
    composer="秦咏诚", lyricist="张藜", artist="李谷一",
    instrumentation=[("Vocal Quartet S.A.T.B. soli", "四声部独唱"),
                     ("String Quartet", "弦乐四重奏")],
    key="E♭ Major · 降E大调", tempo="♩. = 56", duration="ca. 2′51″",
    year="2026", tempo_text="Moderato", mscx_hook=_mscx_hook)

LYRIC_TXT = {"sop": "1_女高音_歌词.txt", "alt": "2_女低音_歌词.txt",
             "ten": "3_男高音_歌词.txt", "bas": "4_男低音_歌词.txt"}


# ---------------------------------------------------------------------------
def main():
    E.configure(sys.modules[__name__])
    os.makedirs(OUT, exist_ok=True)
    parsed = {p["id"]: E.parse_part(p["data"]) for p in PARTS}
    problems, clashes, parallels, crossings = E.check(parsed)
    for x in problems:
        print("PROBLEM:", x)
    for x in clashes:
        print("CLASH:", x)
    for x in parallels:
        print("PARALLEL:", x)
    for x in crossings:
        print("CROSS:", x)
    if "--check" in sys.argv:
        return
    base = os.path.join(OUT, f"{NAME}_全曲_四声部人声弦乐四重奏")
    sc = E.build_score(parsed)
    sc.write("musicxml", fp=base + ".musicxml")
    E.polish(base + ".musicxml")
    E.hollywood.polish_musicxml(base + ".musicxml", META)
    E.verify_bars(base + ".musicxml")
    voc = [p["id"] for p in PARTS if p["vocal"]]
    strs = [p["id"] for p in PARTS if not p["vocal"]]
    title = f"{NAME}（全曲）"
    E.write_midi(base + "_全轨.mid", voc + strs, parsed, title,
                 breaths=True)
    E.write_midi(os.path.join(OUT, f"{NAME}_四声部人声_带歌词.mid"), voc,
                 parsed, title, with_cc=False, breaths=True)
    E.write_midi(os.path.join(OUT, f"{NAME}_四声部人声_带歌词_GBK编码备用.mid"),
                 voc, parsed, title, charset="gbk", with_cc=False,
                 breaths=True)
    E.write_midi(os.path.join(OUT, f"{NAME}_四声部人声_素.mid"), voc, parsed,
                 title, lyrics=False, with_cc=False)
    E.write_midi(os.path.join(OUT, f"{NAME}_弦乐四重奏_伴奏.mid"), strs,
                 parsed, title)
    E.write_srt(os.path.join(OUT, f"{NAME}_全曲_歌词字幕.srt"), parsed)
    ldir = os.path.join(OUT, "歌词粘贴备用")
    os.makedirs(ldir, exist_ok=True)
    for p in PARTS:
        if p["vocal"]:
            E.write_lyric_text(os.path.join(ldir, LYRIC_TXT[p["id"]]), p,
                               parsed[p["id"]])
    print("written to", OUT)
    if "--pdf" in sys.argv:
        write_pdf()
    if "--mp3" in sys.argv:
        write_mp3(parsed, voc + strs, title)


def write_pdf(png_dir=None):
    E.configure(sys.modules[__name__])
    src = os.path.join(OUT, f"{NAME}_全曲_四声部人声弦乐四重奏.musicxml")
    dst = os.path.join(OUT, f"{NAME}_全曲_总谱.pdf")
    n = E.hollywood.render_pdf(src, dst, META, png_dir=png_dir)
    print(f"PDF: {dst} ({n} pages)")


def write_mp3(parsed, ids, title):
    """GM preview: pizzicato gets the GM pizzicato patch (preview only)."""
    with tempfile.TemporaryDirectory() as t:
        mid = os.path.join(t, "preview.mid")
        wav = os.path.join(t, "preview.wav")
        E.write_midi(mid, ids, parsed, title, lyrics=False,
                     pizz_patch=True)
        subprocess.run(["fluidsynth", "-ni", "-g", "0.6", "-F", wav,
                        "/usr/share/sounds/sf2/FluidR3_GM.sf2", mid],
                       check=True, capture_output=True)
        mp3 = os.path.join(OUT, "粗略试听_GM音色_非ACE效果.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav,
                        "-af", "loudnorm=I=-16:TP=-1.5", "-b:a", "160k", mp3],
                       check=True)
        print("mp3:", mp3)


if __name__ == "__main__":
    main()
