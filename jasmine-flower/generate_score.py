#!/usr/bin/env python3
"""茉莉花 · 人声与弦乐五重奏（F调）—— 生成一个 .mxl 文件（压缩 MusicXML，Sibelius 可直接打开）。

结构：前奏 1-8（大提琴与第一小提琴对答主题）｜A 9-16、B 17-22 人声｜尾声 22-28（主题倒过来再对答一次）
“水”：八分音符波纹在第二小提琴、中提琴、大提琴之间传递；人声长音处由各声部轮流呼应。

记谱（实际音高）：音名+八度+时值 w h q e s（后加 '.' 为附点），r 休止，A3+C4 和弦；
  ~ 连音线  > 重音  - 保持音  ( ) 圆滑线  @p @mf … 力度  @< @> 渐强/渐弱  @t:文字  | 小节线
用法：python3 generate_score.py [输出文件.mxl]
"""
import os
import re
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

from music21 import (articulations, chord, clef, dynamics, expressions, instrument, key, layout, metadata, meter,
                     note, spanner, stream, tempo, tie)

N = 28
m21 = lambda s: re.sub(r'([A-G])b', r'\1-', s)
R = lambda k: ['rw'] * k
LYR = "好一朵美丽的茉莉花好一朵美丽的茉莉花芬芳美丽满枝桠又香又白人人夸让我来将你摘下送给别人家茉莉花呀茉莉花"

# 和声（每半小节）：
#  前奏 F Dm|Bb C|F/A Bb|C F|Am7 Dm7|Bb C|Gm7 Bb|C C7
#  A    F Dm|Bb C|F/A Bb|C F|Am7 Dm7|Bb C|Dm C|F
#  B    Dm Am|Bb F|C Dm|Am Dm|Gm7 C7sus4|F
#  尾声 F Dm|Bb C|F/A Bb|C F|Gm7 C7sus4|Bb Bbm6|F
PARTS = [  # (名称, 缩写, 乐器, 谱号, 各小节)
    ('Voice', 'V.', instrument.Soprano(), clef.TrebleClef(), R(8) + [
        "@mp A4q A4e C5e (D5e F5e) F5e D5e", "C5q (C5e D5e) C5h", "A4q A4e C5e (D5e F5e) F5e D5e", "C5q (C5e D5e) C5h",
        "C5q C5q C5q (A4e C5e)", "D5q D5q C5h", "A4q (G4e A4e) C5q (A4e G4e)", "F4q (F4e G4e) F4h",
        "(A4e G4e) (F4e A4e) G4q. A4e", "C5q (D5e F5e) C5h", "@mf G4q (A4e C5e) (G4e A4e) (F4e D4e)", "C4h D4q F4q",
        "@p G4q. A4e (F4e G4e) (F4e D4e)", "C4w"] + R(6)),
    ('Violin I', 'Vln. I', instrument.Violin(), clef.TrebleClef(), [
        "rw", "rw", "@mp @t:dolce (A5q A5e C6e) (D6e F6e F6e D6e)", "(C6q D6e C6e) A5h",
        "rw", "(D5q D5q C5h)", "@mf @t:espr. (G5q. A5e) (F5e G5e F5e D5e)", "C5h- rh",
        "rw", "@p rh (C6e D6e) C6q", "rw", "rw", "rw", "rh (D6q C6q)", "rw", "rw",
        "@mp (A5h. G5q)", "(Bb5h A5h)", "@mf (G5h F5h)", "(E5q D5e C5e) (D5q F5q)", "@p (G5h. F5q)",
        "@mp (A5q A5e C6e) (D6e F6e F6e D6e)", "(C6q C6e D6e C6h)", "rw", "rw",
        "@p (G5q. A5e) (F5e G5e F5e D5e)", "@pp C5w~", "C5w"]),
    ('Violin II', 'Vln. II', instrument.Violin(), clef.TrebleClef(), [
        "@pp (F4e A4e C5e A4e) (F4e A4e D5e A4e)", "(F4e Bb4e D5e Bb4e) (E4e G4e C5e G4e)", "@p (C5h D5h)",
        "(E5h F5h)", "(E4e A4e C5e A4e) (F4e A4e D5e A4e)", "(F4h E4h)", "@mp (Bb4h D5h)", "@p (F4h E4h)",
        "F4w", "(F4h E4h)", "F4w", "(E4h F4h)", "(G4h F4h)", "(F4h G4h)", "(F4h G4h)", "A4w",
        "@mp (F5h E5h)", "F5w", "@mf (E5h D5h)", "(C5h A4h)", "@p (D5h C5h)",
        "A4w", "(Bb4h G4h)", "(F4e A4e C5e A4e) (F4e Bb4e D5e Bb4e)", "(E4e G4e C5e G4e) (F4e A4e C5e A4e)",
        "(D5h C5h)", "@pp (F4h G4h)", "A4w"]),
    ('Viola', 'Vla.', instrument.Viola(), clef.AltoClef(), [
        "@pp F3w", "(F3h E3h)", "@p (A3e C4e F4e C4e) (Bb3e D4e F4e D4e)", "(G3e C4e E4e C4e) (A3e C4e F4e C4e)",
        "(E3h D3h)", "(D3e F3e Bb3e F3e) (C3e E3e G3e E3e)", "@mp F4w", "@p G3h (E4e C4e Bb3e G3e)",
        "(F3e A3e C4e A3e) (F3e A3e D4e A3e)", "(F3e Bb3e D4e Bb3e) (E3e G3e C4e G3e)",
        "(F3e A3e C4e A3e) (F3e Bb3e D4e Bb3e)", "(E3e G3e C4e G3e) (F3e A3e C4e A3e)",
        "(E4h D4h)", "(D4h E4h)", "(D4h E4h)", "C4w",
        "@mp (D3e F3e A3e F3e) (C3e E3e A3e E3e)", "(D3e F3e Bb3e F3e) (C3e F3e A3e F3e)",
        "(C3e E3e G3e E3e) (D3e F3e A3e F3e)", "(C3e E3e A3e E3e) (D3e F3e A3e F3e)",
        "@p (D3e G3e Bb3e G3e) (C3e F3e Bb3e F3e)",
        "(F3e A3e C4e A3e) (F3e A3e D4e A3e)", "(F3e Bb3e D4e Bb3e) (E3e G3e C4e G3e)", "F3w", "(E3h F3h)",
        "Bb3w", "@pp (D4h Db4h)", "C4w"]),
    ('Violoncello', 'Vc.', instrument.Violoncello(), clef.BassClef(), [
        "@mp @t:cantabile (A3q A3e C4e) (D4e F4e F4e D4e)", "(C4q C4e D4e C4h)", "@p (C3h D3h)", "(E3h F3h)",
        "@mp (C4q C4q C4q A3e C4e)", "@p (F3h G3h)", "@mf (G3q. A3e) (F3e G3e F3e D3e)", "@p (C3h Bb2h)",
        "(A2h D3h)", "(D3h E3h)", "(C3h D3h)", "E3h (C4e D4e) C4q",
        "(A2e E3e C4e E3e) (D3e A3e C4e A3e)", "(Bb2e F3e D4e F3e) (C3e G3e E4e G3e)",
        "(D3e A3e F4e A3e) (C3e G3e E4e G3e)", "(F2e C3e A3e C3e) (F3e G3e) A3q",
        "@mp (A3h C4h)", "D4h (D4e F4e) C4q", "@mf (C4h A3h)", "(A3h F3h)", "@p (D3h C3h)",
        "(C3h D3h)", "(D3h E3h)", "@mp (A3q A3e C4e) (D4e F4e F4e D4e)", "(C4q D4e C4e) A3h",
        "@p (D3h C3h)", "@pp Bb2w", "(C3q C3e D3e C3h)"]),
    ('Contrabass', 'Cb.', instrument.Contrabass(), clef.BassClef(), [
        "@pp F2h D2h", "Bb1h C2h", "A1h Bb1h", "C2h F2h", "A1h D2h", "Bb1h C2h", "@p G1h Bb1h", "C2w",
        "@pp F2h D2h", "Bb1h C2h", "A1h Bb1h", "C2h F1h", "@p A1h D2h", "Bb1h C2h", "D2h C2h", "F1w",
        "@mp D2h A1h", "Bb1h F1h", "C2h D2h", "A1h D2h", "@p G1h C2h",
        "F1h D2h", "Bb1h C2h", "A1h Bb1h", "C2h F1h", "G1h C2h", "@pp Bb1w", "F1w"]),
]
T, X, RM = tempo.MetronomeMark, expressions.TextExpression, expressions.RehearsalMark
MARKS = [(1, 0, T("Andante, come l'acqua (如水)", 76)), (8, 0, X('poco rit.')), (9, 0, RM('A')), (9, 0, X('a tempo')),
         (17, 0, RM('B')), (21, 2, X('poco rit.')), (22, 0, RM('C')), (22, 0, X('a tempo')),
         (27, 0, X('rit. e morendo'))]

FLAG = {'>': articulations.Accent, '-': articulations.Tenuto}
TOK = re.compile(r"(\(?)(r|[A-G][#b]?\d(?:\+[A-G][#b]?\d)*)([whqes])(\.?)([~>-]*)(\)?)$")
QL = dict(w=4, h=2, q=1, e=.5, s=.25)


def build(name, abbr, inst, clf, bars, lyr=None):
    p = stream.Part()
    p.partName, p.partAbbreviation = inst.partName, inst.partAbbreviation = name, abbr
    p.insert(0, inst)
    p.atSoundingPitch = True
    assert len(bars) == N, (name, len(bars))
    syl, slur, wedge, last, tied, tstop, wedges = iter(lyr or ''), None, None, None, False, False, []
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
                    M.insert(off, X(d[2:]))
                else:
                    M.insert(off, dynamics.Dynamic(d))
                continue
            g = TOK.match(t)
            assert g, (name, i, t)
            s0, pt, dl, dot, fl, s1 = g.groups()
            ql = QL[dl] * (1.5 if dot else 1)
            if pt == 'r':
                n = note.Rest(quarterLength=ql)
            elif '+' in pt:
                n = chord.Chord([m21(x) for x in pt.split('+')], quarterLength=ql)
            else:
                n = note.Note(m21(pt), quarterLength=ql)
            if not n.isRest:
                n.tie = tie.Tie('continue' if tied else 'start') if '~' in fl else (tie.Tie('stop') if tied else None)
                tstop, tied = tied, '~' in fl
                n.articulations += [A() for c, A in FLAG.items() if c in fl]
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
    """为 Sibelius 整理：A4 页面、6.5mm 谱表、每 4 小节一行；“力度+发夹”合并成一个表情记号（如 mf cresc.）；
    节拍器记号与速度文字合并；人声力度放在谱表上方（下方是歌词），文字记号放在上方。"""
    tree = ET.parse(path)
    r = tree.getroot()
    d = r.find('defaults')
    for t in ('scaling', 'page-layout', 'system-layout', 'staff-layout'):
        for x in d.findall(t):
            d.remove(x)
    new = ET.fromstring(
        '<defaults><scaling><millimeters>6.5</millimeters><tenths>40</tenths></scaling>'
        '<page-layout><page-height>1828</page-height><page-width>1292</page-width><page-margins type="both">'
        '<left-margin>100</left-margin><right-margin>70</right-margin><top-margin>80</top-margin>'
        '<bottom-margin>80</bottom-margin></page-margins></page-layout><system-layout><system-margins>'
        '<left-margin>50</left-margin><right-margin>0</right-margin></system-margins>'
        '<system-distance>120</system-distance><top-system-distance>180</top-system-distance></system-layout>'
        '<staff-layout><staff-distance>80</staff-distance></staff-layout></defaults>')
    for i, x in enumerate(new):
        d.insert(i, x)
    for n in r.iter('note'):
        for x in n.findall('instrument'):
            n.remove(x)
    names = {s.get('id'): s.findtext('part-name') for s in r.iter('score-part')}
    for part in r.findall('part'):
        vocal, merged = names[part.get('id')] == 'Voice', set()
        for m in part.findall('measure'):
            if m.get('number') in ('5', '9', '13', '17', '21', '25'):
                m.insert(0, ET.Element('print', {'new-system': 'yes'}))
            kids = list(m)
            for i, el in enumerate(kids):
                if el.tag != 'direction':
                    continue
                mt = el.find('direction-type/metronome/..')
                if mt is not None:
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
                if w is not None:
                    j = i - 1
                    while j >= 0 and kids[j].tag == 'direction' and kids[j].find('direction-type/dynamics') is None:
                        j -= 1
                    dyn = kids[j] if j >= 0 and kids[j].tag == 'direction' else None
                    if dyn is not None and dyn.findtext('offset') == el.findtext('offset'):
                        dt = ET.Element('direction-type')
                        ET.SubElement(dt, 'words', {'font-style': 'italic'}).text = \
                            ' cresc.' if w.get('type') == 'crescendo' else ' dim.'
                        dyn.insert(len(dyn.findall('direction-type')), dt)
                        merged.add(w.get('number', '1'))
                        m.remove(el)
                        continue
                if el.find('direction-type/dynamics') is not None or w is not None:
                    el.set('placement', 'above' if vocal else 'below')
                elif el.find('direction-type/words') is not None or el.find('direction-type/rehearsal') is not None:
                    el.set('placement', 'above')
    tree.write(path, encoding='UTF-8', xml_declaration=True)


parts = [build(*x, **({'lyr': LYR} if x[0] == 'Voice' else {})) for x in PARTS]
for b, o, e in MARKS:
    parts[0].measure(b).insert(o, e)
sc = stream.Score()
md = metadata.Metadata(title='茉莉花 Jasmine Flower', composer='江苏民歌 Jiangsu Folk Song')
md.add('arranger', '人声与弦乐五重奏 · F调  (Voice & String Quintet in F)')
sc.insert(0, md)
for p in parts:
    sc.insert(0, p)
sc.insert(0, layout.StaffGroup(parts[1:], symbol='bracket'))

out = sys.argv[1] if len(sys.argv) > 1 else '茉莉花_人声与弦乐五重奏.mxl'
with tempfile.TemporaryDirectory() as tmp:
    xml = os.path.join(tmp, 'score.xml')
    sc.write('musicxml', fp=xml)
    polish(xml)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:  # .mxl = 压缩的 MusicXML，单个文件
        z.writestr(zipfile.ZipInfo('mimetype'), 'application/vnd.recordare.musicxml', zipfile.ZIP_STORED)
        z.writestr('META-INF/container.xml', '<?xml version="1.0" encoding="UTF-8"?><container><rootfiles>'
                   '<rootfile full-path="score.xml" media-type="application/vnd.recordare.musicxml+xml"/>'
                   '</rootfiles></container>')
        z.write(xml, 'score.xml')
print('written', out)
