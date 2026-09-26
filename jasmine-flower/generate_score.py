#!/usr/bin/env python3
"""茉莉花 · F调迪士尼风格管弦乐伴奏 —— 生成 MusicXML 总谱（Sibelius：文件 > 打开 即可）。

记谱（全部按实际音高书写，移调乐器导出时自动转为记谱音高）：
  音名+八度+时值  时值 w h q e s t（全/二/四/八/十六/三十二分），后加 '.' 为附点；r 休止；x 无音高打击乐
  A3+C4q 和弦   ~ 连音线  > 重音  ! 跳音  - 保持音  * 震音  % 颤音  & 琶音   ( ) 圆滑线
  @p @mf … 力度   @< @> 渐强/渐弱（至下一个力度记号）   @t:文字   | 小节线
用法：python3 generate_score.py [输出文件]
"""
import itertools
import xml.etree.ElementTree as ET
import re
import sys

from music21 import (articulations, chord, clef, dynamics, expressions, harmony, instrument, interval, key,
                     layout, metadata, meter, note, spanner, stream, tempo, tie)

PC = dict(C=0, D=2, E=4, F=5, G=7, A=9, B=11)
pcn = lambda s: (PC[s[0]] + s[1:].count('#') - s[1:].count('b')) % 12
m21 = lambda s: re.sub(r'([A-G])b', r'\1-', s)

CH = {k: v.split() for k, v in (x.split(':') for x in (  # 和弦 = 低音 + 和弦音（根 三 五 色彩音）
    "F:F F A C|Fadd9:F F A C G|Bbmaj7:Bb Bb D F A|C7sus4:C C F G Bb|Dbmaj7:Db Db F Ab C|"
    "Ebadd9:Eb Eb G Bb F|Gm7/C:C G Bb D F|C7:C C E G Bb|Bb/D:D Bb D F|Gm7:G G Bb D F|Dm7:D D F A C|"
    "Gm9:G G Bb D F A|Am7:A A C E G|Bbmaj9:Bb Bb D F A C|F/A:A F A C|Eb6:Eb Eb G Bb C|"
    "C9sus4:C C F G Bb D|F7/Eb:Eb F A C Eb|Bbadd9:Bb Bb D F C|Abmaj7:Ab Ab C Eb G|Bbm6:Bb Bb Db F G"
).split('|'))}
PROG = [b.split() for b in (  # 每小节和声：1-4 前奏｜5-18 人声｜19-22 尾声
    "Fadd9|Bbmaj7 C7sus4|Dbmaj7 Ebadd9|Gm7/C C7|F Bb/D|Gm7 C7sus4|Dm7 Bbmaj7|Gm9 Am7|Bbmaj9 F/A|Gm7 Eb6|"
    "Dm7 C9sus4|Fadd9 F7/Eb|Dm7 C9sus4|Bbadd9 Abmaj7|Gm9 C9sus4|F/A Dm7|Gm9 C9sus4|Dbmaj7 Ebadd9|"
    "Fadd9|Bbmaj7 Bbm6|Fadd9|Fadd9").split('|')]
N = len(PROG)
DL = {4: 'w', 2: 'h', 1: 'q', .5: 'e', .25: 's', .125: 't'}
W = [0, 1, 2, 3, 4, 3, 2, 1]  # 波浪型琶音
SW = [0, 1, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 1]  # 竖琴大跨度琶音


def nm(m, ch): return next(t for t in CH[ch] if pcn(t) == m % 12) + str(m // 12 - 1)
def root(ch, lo): return next(m for m in range(lo, lo + 12) if m % 12 == pcn(CH[ch][0]))


def cands(ch, lo, hi=108, withbass=False):
    pcs = {pcn(t) for t in CH[ch][1:] + CH[ch][:withbass]}
    return [m for m in range(lo, hi + 1) if m % 12 in pcs]


def pad(n, lo, hi, fl=''):  # 声部进行最平滑的和弦长音
    prev = []

    def f(ch, d):
        ts = [pcn(t) for t in CH[ch][1:]]

        def cost(c):
            pc = [m % 12 for m in c]
            s = sum(abs(a - b) for a, b in zip(c, prev)) if prev else sum(abs(m - (lo + hi) / 2) for m in c)
            return s + (n > 1) * (6 * (ts[1] not in pc) + 3 * (len(ts) > 3 and ts[3] not in pc)
                                  + 4 * sum(b - a < 3 for a, b in zip(c, c[1:])))
        c = min((c for c in itertools.combinations(cands(ch, lo, hi), n) if len({m % 12 for m in c}) == n), key=cost)
        prev[:] = c
        return ['+'.join(nm(m, ch) for m in c) + DL[d] + fl]
    return f


def bass(lo): return lambda ch, d: [nm(root(ch, lo), ch) + DL[d]]
def octv(lo): return lambda ch, d: [nm(root(ch, lo), ch) + '+' + nm(root(ch, lo) + 12, ch) + DL[d]]


def arp(lo, pat, u=.25, withbass=False):  # 分解和弦 / 琶音
    def f(ch, d):
        c = cands(ch, root(ch, lo) if withbass else lo, withbass=withbass)
        return [nm(c[pat[i % len(pat)]], ch) + DL[u] for i in range(int(d / u))]
    return f


def G(a, b, f, pre=''):  # 按和声进行生成第 a..b 小节
    bars = [' '.join(t for ch in PROG[i] for t in f(ch, 4 / len(PROG[i]))) for i in range(a - 1, b)]
    bars[0] = (pre + ' ' + bars[0]).strip()
    return '|'.join(bars)


def P(*xs): return '|'.join(xs)
def R(k): return '|'.join(['rw'] * k)


DYN = {1: '@pp @<', 3: '@mf @<', 4: '@f @>', 5: '@p', 9: '@mp', 13: '@mf @<', 18: '@ff', 20: '@f', 21: '@p @>', 22: '@pp'}


def std(*segs):  # 弦乐：按段落换织体，力度统一
    return P(*(G(b, b, [f for s, f in segs if s <= b][-1], DYN.get(b, '')) for b in range(1, N + 1)))


v2p, vap, hnp = pad(2, 58, 72), pad(2, 50, 62), pad(2, 55, 69)
LYR = "好一朵美丽的茉莉花好一朵美丽的茉莉花芬芳美丽满枝桠又香又白人人夸让我来将你摘下送给别人家茉莉花呀茉莉花"
CYM = getattr(instrument, 'SuspendedCymbal', instrument.Cymbals)()
PT = stream.PartStaff
GLK = instrument.Glockenspiel()
GLK.transposition = interval.Interval('P15')  # 钢片琴实际音高比记谱高两个八度
KIND = {'': ('major', []), 'add9': ('major', [(9, 0)]), 'maj7': ('major-seventh', []), 'maj9': ('major-ninth', []),
        '7': ('dominant', []), '7sus4': ('suspended-fourth', [(7, -1)]), '9sus4': ('suspended-fourth', [(7, -1), (9, 0)]),
        'm7': ('minor-seventh', []), 'm9': ('minor-ninth', []), '6': ('major-sixth', []), 'm6': ('minor-sixth', [])}


def csym(ch):  # 和弦名 -> 合法的 MusicXML 和弦标记
    body, _, b = ch.partition('/')
    r = body[:2] if body[1:2] == 'b' else body[:1]
    kind, adds = KIND[body[len(r):]]
    cs = harmony.ChordSymbol(root=m21(r), kind=kind, **({'bass': m21(b)} if b else {}))
    for d, a in adds:
        cs.addChordStepModification(harmony.ChordStepModification('add', d, a))
    return cs

PARTS = [  # (名称, 缩写, 乐器, 谱号, 谱[, 歌词, 类])
    ('Flute', 'Fl.', instrument.Flute(), clef.TrebleClef(), P(
        "@p (A5q A5e C6e) (D6e F6e F6e D6e)", "(C6q C6e D6e C6q) (A5s C6s D6s F6s)",
        "@mf @< (Ab6s F6s Db6s C6s Ab5s F5s Db5s C5s) (Bb6s G6s F6s Eb6s Bb5s G5s F5s Eb5s)",
        "@f @> G5h% (E5s G5s Bb5s C6s) (D6t E6t F6t G6t A6t Bb6t C7t Bb6t)", "@p A6q rq rh",
        "rh (A5s C6s D6s F6s) (D6e C6e)", "rw", "rh (E6s D6s C6s A5s) (G5e A5e)", "rw",
        "@mp rh (G5s Bb5s C6s Eb6s) (G6e F6e)", "rw", "rh (F5t G5t A5t Bb5t C6t D6t Eb6t F6t) (A6e F6e)", "rw",
        "@mf rh (Eb6s F6s G6s Ab6s) (G6s Eb6s C6s Ab5s)", "rw", "(A5s C6s F6s A6s C7s A6s F6s C6s) rh",
        "@< (D6q. F6e G6q A6q)", "@ff F6h (Eb6s F6s G6s Bb6s) (C7s Bb6s G6s F6s)",
        "(A5q A5e C6e) (D6e F6e F6e D6e)", "(C6q C6e D6e C6h)",
        "@p (C7s A6s G6s F6s D6s C6s A5s G5s) (F5s D5s C5s A4s) G4q", "@pp C6w")),
    ('Oboe', 'Ob.', instrument.Oboe(), clef.TrebleClef(), P(
        R(2), "@mf @< Ab5h G5h", "@f @> F5h E5h", R(8),
        "@mf (D6h C6q Bb5q)", "(D6h C6q Eb6q)", "(D6q. Bb5e C6h)", "rh D6h", "@< (D5q. F5e G5q A5q)",
        "@ff Ab5h Bb5h", "(A4q A4e C5e) (D5e F5e F5e D5e)", "(C5q C5e D5e C5h)", "@mp A5w", "@pp G5w")),
    ('Clarinet in B♭', 'Cl.', instrument.Clarinet(), clef.TrebleClef(), P(
        "@p C5w", "D5h C5h", "@mf @< F5h Eb5h", "@f @> D5h (C4s E4s G4s Bb4s) (C5s E5s G5s Bb5s)", "@p A5q rq rh",
        G(6, 12, pad(1, 55, 67)), G(13, 17, arp(65, [0, 2, 1, 3], .5), '@mf @<'),
        "@ff F5h G5h", "C5w", "@f D5h Db5h", "@p C5w", "@pp A4w")),
    ('Bassoon', 'Bsn.', instrument.Bassoon(), clef.BassClef(), P(
        R(2), G(3, 3, bass(38), '@mf @<'), G(4, 4, bass(38), '@f @>'), R(4), G(9, 12, bass(38), '@mp'),
        G(13, 17, bass(38), '@mf @<'), G(18, 20, bass(38), '@ff'), G(21, 22, bass(38), '@p @>'))),
    ('Horn in F 1.2', 'Hn.', instrument.Horn(), clef.TrebleClef(), P(
        G(1, 2, hnp, '@pp @<'), G(3, 3, hnp, '@mf @<'), G(4, 4, hnp, '@f @>'), R(4), G(9, 12, hnp, '@mp'),
        G(13, 17, hnp, '@mf @<'), G(18, 18, hnp, '@ff'),
        "(A3q> A3e C4e) (D4e F4e F4e D4e)", "(C4q> C4e D4e C4h)",
        G(21, 22, hnp, '@p @>'))),
    ('Trumpet in B♭', 'Tpt.', instrument.Trumpet(), clef.TrebleClef(), P(
        R(2), "@mf @< Ab4+C5h G4+Bb4h", "@f @> F4+Bb4h E4+Bb4h", R(13), "@ff Ab4+C5h G4+Bb4h",
        "(A4q A4e C5e) (D5e F5e F5e D5e)", "(C5q C5e D5e C5h)", R(2))),
    ('Trombone 1.2', 'Tbn.', instrument.Trombone(), clef.BassClef(), P(
        R(2), "@mf @< Db3+Ab3h Eb3+Bb3h", "@f @> C3+G3h C3+Bb3h", R(12), "@mf @< G2+D3h C3+Bb3h",
        "@ff Db3+Ab3h Eb3+Bb3h", "F2+C3w", "Bb2+D3h Bb2+Db3h", "@mp @> F2+C3w", "@pp F2+C3w")),
    ('Timpani', 'Timp.', instrument.Timpani(), clef.BassClef(), P(
        "@pp @< F2w*", "rh C3h*", "@mf @< F2h* Eb3h*", "@f @> C3w*", R(12), "@mp @< C3w*", "@ff F2h* Eb3h*",
        "F2q> rq C3e C3e F2q>", "@f Bb2w*", "@p @> F2w*", "@pp F2w*")),
    ('Suspended Cymbal', 'S.Cym.', CYM, clef.PercussionClef(), P(
        "@pp xw*", "rw", "@p @< xw*", "@f xq rq rh", R(12), "@p @< xw*~", "xw*", "@ff xq> rq rh", R(2), "@pp xw*")),
    ('Glockenspiel', 'Glk.', GLK, clef.TrebleClef(), P(
        "@p A6q rq rh", "rh C7q rq", R(2), "A6q rq rh", "rh rq C7q", "rw", "rh rq A6q", "rw", "rh rq G6q", "rw",
        "rh rq A6q", "rw", "@mf rh C7e G6e Eb7q", "rw", "C7e A6e F6q rh", "rw", "@f F7q C7q G7q Bb6q",
        "@ff A6q C7q F7q rq", "rw", "@p rh C7q A6q", "@pp A6w")),
    ('Harp', 'Hp.', instrument.Harp(), clef.TrebleClef(), P(
        G(1, 1, arp(60, SW), '@p'), G(2, 2, arp(65, W)), G(3, 3, arp(61, range(8)), '@mf @<'),
        "@f @> F4s G4s Bb4s D5s F5s D5s Bb4s G4s Bb6s G6s E6s C6s Bb5s G5s E5s C5s",
        G(5, 8, arp(60, W), '@p'), G(9, 12, arp(60, W), '@mp'), G(13, 17, arp(72, W), '@mf @<'),
        G(18, 18, arp(61, range(8)), '@ff'), G(19, 19, arp(60, SW)), G(20, 20, arp(65, W), '@f'),
        G(21, 21, arp(65, [11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0, 3, 2, 1, 0]), '@p @>'), "@pp F4+A4+C5+G5+A5w&"), None, PT),
    ('Harp', 'Hp.', None, clef.BassClef(), P(
        "F1+F2w", G(2, 4, octv(29)), G(5, 17, arp(36, [0, 2, 3, 4], .5, True)), G(18, 21, octv(29)), "F1+F2w"),
     None, PT),
    ('Soprano', 'S.', instrument.Soprano(), clef.TrebleClef(), P(
        R(4), "@mp A4q A4e C5e (D5e F5e) F5e D5e", "C5q (C5e D5e) C5h", "A4q A4e C5e (D5e F5e) F5e D5e",
        "C5q (C5e D5e) C5h", "@mf C5q C5q C5q (A4e C5e)", "D5q D5q C5h", "A4q (G4e A4e) C5q (A4e G4e)",
        "F4q (F4e G4e) F4h", "(A4e G4e) (F4e A4e) G4q. A4e", "C5q (D5e F5e) C5h",
        "@f G4q (A4e C5e) (G4e A4e) (F4e D4e)", "C4h D4q F4q", "G4q. A4e (F4e G4e) (F4e D4e)", "@f C4w~",
        "C4h rh", R(3)), LYR),
    ('Violin I', 'Vln. I', instrument.Violin(), clef.TrebleClef(), P(
        G(1, 2, pad(2, 67, 81, '*'), '@pp @<'), "@mf @< (F5s G5s Ab5s C6s Db6s Eb6s F6s Ab6s) Bb6h",
        "@f @> A6q G6q (F6s E6s D6s C6s) (Bb5s A5s G5s E5s)", R(4),
        "@mp (F5q. G5e A5h)", "(Bb5h G5q Bb5q)", "(A5q. G5e F5h)", "(A5h C6q Eb6q)",
        "@mf (D6h C6q Bb5q)", "(D6h C6q Eb6q)", "(D6q. Bb5e C6h)", "(A5s C6s F6s A6s C7s A6s F6s C6s) D6h",
        "@< (D6q. F6e G6q A6q)", "@ff F6h (Eb5s F5s G5s Bb5s) (C6s Eb6s F6s G6s)", "A6w", "@f F6h Db6h",
        "@p @> C6w", "@pp A5w")),
    ('Violin II', 'Vln. II', instrument.Violin(), clef.TrebleClef(), std(
        (1, pad(2, 62, 74, '*')), (3, v2p), (13, arp(65, [0, 2, 1, 3, 2, 4, 3, 5])), (18, pad(2, 65, 79, '*')),
        (19, arp(69, W)), (20, v2p))),
    ('Viola', 'Vla.', instrument.Viola(), clef.AltoClef(), std(
        (1, pad(2, 53, 65, '*')), (3, vap), (13, arp(53, [0, 1, 2, 1], .5)), (18, pad(2, 55, 67, '*')),
        (19, arp(60, W)), (20, vap))),
    ('Violoncello', 'Vc.', instrument.Violoncello(), clef.BassClef(), std(
        (1, bass(36)), (13, arp(36, [0, 2, 3, 2], .5, True)), (18, bass(36)),
        (19, arp(36, [0, 2, 3, 4, 5, 4, 3, 2], .25, True)), (20, bass(36)))),
    ('Contrabass', 'Cb.', instrument.Contrabass(), clef.BassClef(), std((1, bass(28)))),
]

FLAG = {'>': articulations.Accent, '!': articulations.Staccato, '-': articulations.Tenuto}
TOK = re.compile(r"(\(?)(r|x|[A-G][#b]?\d(?:\+[A-G][#b]?\d)*)([whqest])(\.?)([~>!*%^&-]*)(\)?)$")
QL = dict(w=4, h=2, q=1, e=.5, s=.25, t=.125)


def build(name, abbr, inst, clf, spec, lyr=None, cls=stream.Part):
    p = cls()
    p.partName, p.partAbbreviation = name, abbr
    if inst:
        inst.partName, inst.partAbbreviation = name, abbr
        p.insert(0, inst)
    p.atSoundingPitch = True
    syl, bars = iter(lyr or ''), spec.split('|')
    assert len(bars) == N, (name, len(bars))
    slur = wedge = last = None
    tied = tstop = False
    wedges = []
    for i, b in enumerate(bars, 1):
        M, off = stream.Measure(number=i), 0
        if i == 1:
            M.append([clf, key.KeySignature(-1), meter.TimeSignature('4/4')])
        for t in b.split():
            if t[0] == '@':
                d = t[1:]
                if wedge:
                    wedge[2], wedge = last, None
                if d in ('<', '>'):
                    wedge = [dynamics.Crescendo if d == '<' else dynamics.Diminuendo, None, None]
                    wedges.append(wedge)
                elif d.startswith('t:'):
                    M.insert(off, expressions.TextExpression(d[2:].replace('_', ' ')))
                elif d != '|':
                    M.insert(off, dynamics.Dynamic(d))
                continue
            g = TOK.match(t)
            assert g, (name, i, t)
            s0, pt, dl, dot, fl, s1 = g.groups()
            ql = QL[dl] * (1.5 if dot else 1)
            if pt == 'r':
                n = note.Rest(quarterLength=ql)
            elif pt == 'x':
                n = note.Unpitched(quarterLength=ql)
                n.displayStep, n.displayOctave = 'C', 5
            elif '+' in pt:
                n = chord.Chord([m21(x) for x in pt.split('+')], quarterLength=ql)
            else:
                n = note.Note(m21(pt), quarterLength=ql)
            if not n.isRest:
                n.tie = tie.Tie('continue' if tied else 'start') if '~' in fl else (tie.Tie('stop') if tied else None)
                tstop, tied = tied, '~' in fl
                for c, A in FLAG.items():
                    if c in fl:
                        n.articulations.append(A())
                if '*' in fl:
                    tr = expressions.Tremolo()
                    tr.numberOfMarks = 3
                    n.expressions.append(tr)
                if '%' in fl:
                    n.expressions.append(expressions.Trill())
                if '&' in fl:
                    n.expressions.append(expressions.ArpeggioMark())
                if wedge and wedge[1] is None:
                    wedge[1] = n
                last = n
            if s0:
                slur = [n]
            elif slur is not None:
                slur.append(n)
            if lyr and not n.isRest and not tstop and (slur is None or slur[0] is n):
                n.lyric = next(syl)
            if s1:
                p.insert(0, spanner.Slur(slur))
                slur = None
            M.insert(off, n)
            off += ql
        assert abs(off - 4) < 1e-9, (name, i, off)
        p.append(M)
    if wedge:
        wedge[2] = last
    for c, a, b in wedges:
        if a is not None and b is not None and a is not b:
            p.insert(0, c(a, b))
    n.expressions.append(expressions.Fermata())  # 终止延长号
    return p




def polish(path):
    """为 Sibelius 整理 MusicXML：A3 页面与 6mm 谱表（避免 18 行谱挤在一页上互相碰撞）、固定分行、
    “力度+发夹”合并为“mf cresc.”一个表情记号、人声力度放在谱表上方（下方是歌词）、文字放在上方。"""
    E = ET.SubElement
    tree = ET.parse(path)
    r = tree.getroot()
    d = r.find('defaults')
    for t in ('scaling', 'page-layout', 'system-layout', 'staff-layout'):
        for x in d.findall(t):
            d.remove(x)
    new = ET.fromstring(
        '<defaults><scaling><millimeters>5</millimeters><tenths>40</tenths></scaling>'
        '<page-layout><page-height>3360</page-height><page-width>2376</page-width><page-margins type="both">'
        '<left-margin>120</left-margin><right-margin>80</right-margin><top-margin>90</top-margin>'
        '<bottom-margin>90</bottom-margin></page-margins></page-layout><system-layout><system-margins>'
        '<left-margin>60</left-margin><right-margin>0</right-margin></system-margins>'
        '<system-distance>120</system-distance><top-system-distance>220</top-system-distance></system-layout>'
        '<staff-layout><staff-distance>70</staff-distance></staff-layout></defaults>')
    for i, x in enumerate(new):
        d.insert(i, x)
    names = {s.get('id'): s.findtext('part-name') for s in r.iter('score-part')}
    for n in r.iter('note'):  # 竖琴左手引用了未声明的乐器 id，会被当成“换乐器”
        for x in n.findall('instrument'):
            n.remove(x)
    for part in r.findall('part'):
        vocal = names[part.get('id')] == 'Soprano'
        merged = set()
        for m in part.findall('measure'):
            if m.get('number') in ('5', '9', '13', '17', '20'):
                m.insert(0, ET.Element('print', {'new-system': 'yes'}))
            kids = list(m)
            for i, el in enumerate(kids):
                if el.tag != 'direction':
                    continue
                mt = el.find('direction-type/metronome/..')
                if mt is not None:  # 速度文字与节拍器记号合成一个速度标记
                    wd = next((k for k in kids[max(i - 1, 0):i + 2] if k.tag == 'direction' and k is not el
                               and k.find('direction-type/words') is not None), None)
                    if wd is not None:
                        wd.insert(len(wd.findall('direction-type')), mt)
                        wd.set('placement', 'above')
                        for x in el.findall('sound'):
                            wd.append(x)
                        m.remove(el)
                    continue
                w = el.find('direction-type/wedge')
                if w is not None and w.get('type') == 'stop':
                    if w.get('number', '1') in merged:
                        merged.discard(w.get('number', '1'))
                        m.remove(el)
                    continue
                if w is not None:  # 同一位置已有力度记号 -> 改成文字 cresc./dim.
                    j = i - 1
                    while j >= 0 and kids[j].tag in ('direction', 'harmony') and kids[j].find('direction-type/dynamics') is None:
                        j -= 1
                    dyn = kids[j] if j >= 0 and kids[j].tag == 'direction' else None
                    if dyn is not None and dyn.find('direction-type/dynamics') is not None \
                            and dyn.findtext('offset') == el.findtext('offset'):
                        dt = ET.Element('direction-type')
                        E(dt, 'words', {'font-style': 'italic'}).text = ' cresc.' if w.get('type') == 'crescendo' else ' dim.'
                        dyn.insert(len(dyn.findall('direction-type')), dt)
                        merged.add(w.get('number', '1'))
                        m.remove(el)
                        continue
                if el.find('direction-type/dynamics') is not None or w is not None:
                    el.set('placement', 'above' if vocal else 'below')
                elif el.find('direction-type/words') is not None:
                    el.set('placement', 'above')
    tree.write(path, encoding='UTF-8', xml_declaration=True)


parts = [build(*x) for x in PARTS]

vo = parts[10]  # 和弦标记写在竖琴上方（人声上方留给力度记号）
for i, bar in enumerate(PROG, 1):
    for j, ch in enumerate(bar):
        vo.measure(i).insert(j * 4 / len(bar), csym(ch))

T, X = tempo.MetronomeMark, expressions.TextExpression
for b, o, e in [(1, 0, T('Andante maestoso', 80)), (4, 2, X('rit.')), (5, 0, expressions.RehearsalMark('A')),
                (5, 0, T('a tempo, dolce', 80)), (9, 0, expressions.RehearsalMark('B')),
                (13, 0, expressions.RehearsalMark('C')), (13, 0, X('con moto')), (18, 0, X('Grandioso')),
                (19, 0, expressions.RehearsalMark('D')), (19, 0, T('Maestoso', 76)), (21, 2, X('rit. e dim.'))]:
    parts[0].measure(b).insert(o, e)

sc = stream.Score()
md = metadata.Metadata(title='茉莉花 Jasmine Flower', composer='江苏民歌 Jiangsu Folk Song')
try:
    md.add('arranger', 'F调 · 迪士尼风格管弦乐伴奏 (Disney-style orchestral arr. in F)')
except Exception:
    pass
sc.insert(0, md)
for p in parts:
    sc.insert(0, p)
for a, b, sym in ((0, 4, 'bracket'), (4, 7, 'bracket'), (7, 10, 'bracket'), (10, 12, 'brace'), (13, 18, 'bracket')):
    sc.insert(0, layout.StaffGroup(parts[a:b], name='Harp' if sym == 'brace' else None, symbol=sym))

for p in parts:  # 实际音高音域检查
    ps = [x.midi for n in p.recurse().notes if not isinstance(n, harmony.ChordSymbol)
          and isinstance(n, (note.Note, chord.Chord)) for x in n.pitches]
    print(f'{p.partName:18s} {min(ps, default=0):3d}-{max(ps, default=0):3d}')

out = sys.argv[1] if len(sys.argv) > 1 else '茉莉花_F调_迪士尼风格管弦乐总谱.musicxml'
sc.write('musicxml', fp=out)
polish(out)
print('written', out)
