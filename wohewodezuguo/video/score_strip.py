#!/usr/bin/env python3
"""Handwritten score strip for the video: bars B1..73 of the real score in
one endless system, engraved by MuseScore 4 with the MuseJazz font (the
closest free match to Sibelius' Inkpen2, which the user's earlier video
used).  Writes to video/strip/:

  strip.svg     the system (MuseScore SVG, classes kept for CSS colouring)
  strip.json    time -> x map (audio seconds), staff line y's, header width

Lyrics, instrument names, section titles and tempo text are left out of
the engraving; the page layer draws them (Chinese fonts, singer names).
"""
import json
import os
import re
import subprocess
import sys

from music21 import converter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import build  # noqa: E402
import engine as E  # noqa: E402

B1, B2 = 40, 73
SRC = os.path.join(os.path.dirname(HERE), "output",
                   "我和我的祖国_全曲_四声部人声弦乐四重奏.musicxml")
OUT = os.path.join(HERE, "strip")
MS4 = "/opt/ms4/squashfs-root/AppRun"
MUSEJAZZ = ("/opt/ms4/squashfs-root/share/mscore4portable-4.4/styles/"
            "MuseJazz.mss")
KEEP_WORDS = ("dolce", "espr", "cantabile", "leggiero", "dim.", "sul tasto",
              "ord.", "pizz.", "arco", "allargando", "rit.", "poco allarg.",
              "a tempo", "semplice")
# extra space (SVG px, 24.8 = one staff space) added above each staff after
# engraving: room above the strings so the Violin I 8va line clears the bass
# lyrics.  MuseScore ignores per-part staff distances in MusicXML.
EXTRA = [0, 0, 0, 0, 90, 0, 0, 0]
U = 12.0            # MuseScore .spos/.mpos units per SVG px


def excerpt(path):
    sc = converter.parse(SRC)
    sc.measures(B1, B2).write("musicxml", fp=path)
    x = open(path, encoding="utf-8").read()
    x = re.sub(r"<credit.*?</credit>\s*", "", x, flags=re.S)
    x = re.sub(r"<print[^>]*?/>|<print.*?</print>", "", x, flags=re.S)
    x = re.sub(r"<sound[^>]*tempo=\"[^\"]*\"[^>]*/>", "", x)
    x = re.sub(r"<part-group.*?</part-group>|<part-group[^>]*/>", "", x,
               flags=re.S)

    def direction(m):
        d = m.group(0)
        if "<dynamics" in d or "<wedge" in d or "<octave-shift" in d:
            return d
        w = re.findall(r"<words[^>]*>([^<]*)</words>", d)
        if w and all(any(k in s for k in KEEP_WORDS) for s in w) \
                and "<metronome" not in d and "<rehearsal" not in d:
            return d
        return ""
    x = re.sub(r"<direction\b.*?</direction>", direction, x, flags=re.S)
    # vocal dynamics and hairpins go above the staff: the lyrics are below
    chunks = re.split(r'(?=<part id=")', x)
    for k in range(1, 5):
        chunks[k] = re.sub(
            r'<direction placement="below"(?=>(?:(?!</direction>).)*?'
            r'<(?:dynamics|wedge))', '<direction placement="above"',
            chunks[k], flags=re.S)
    x = "".join(chunks)
    x = re.sub(r"<part-name>[^<]*</part-name>",
               '<part-name print-object="no"></part-name>', x)
    x = re.sub(r"<part-abbreviation>[^<]*</part-abbreviation>",
               '<part-abbreviation print-object="no"></part-abbreviation>', x)
    open(path, "w", encoding="utf-8").write(x)


def style(path, width_in):
    s = open(MUSEJAZZ, encoding="utf-8").read()
    over = {
        "pageWidth": width_in, "pageHeight": 12,
        "pagePrintableWidth": width_in - 0.4,
        "pageEvenLeftMargin": 0.2, "pageOddLeftMargin": 0.2,
        "pageEvenTopMargin": 0.4, "pageOddTopMargin": 0.4,
        "pageEvenBottomMargin": 0.2, "pageOddBottomMargin": 0.2,
        "staffDistance": 5.0, "akkoladeDistance": 5.0,
        "minSystemDistance": 8, "maxSystemDistance": 8,
        "showHeader": 0, "showFooter": 0,
        "lastSystemFillLimit": 0,
        "minMeasureWidth": 9.0,
        "enableVerticalSpread": 0, "frameSystemDistance": 7.0,
        "measureSpacing": 1.6,
        "lyricsOddFontFace": "Noto Sans CJK SC",
        "lyricsEvenFontFace": "Noto Sans CJK SC",
        "lyricsOddFontSize": 12, "lyricsEvenFontSize": 12,
        "lyricsPosBelow": None, "lyricsMinTopDistance": 1.4,
    }
    for k, v in over.items():
        if v is None:
            continue
        if re.search(rf"<{k}>", s):
            s = re.sub(rf"<{k}>[^<]*</{k}>", f"<{k}>{v}</{k}>", s)
        else:
            s = s.replace("</Style>", f"  <{k}>{v}</{k}>\n  </Style>")
    open(path, "w", encoding="utf-8").write(s)


def spread(svg, staves):
    """Move every element down by the extra space of its staff band."""
    centers = [(st[0] + st[4]) / 2 for st in staves]
    cuts = [(a + b) / 2 for a, b in zip(centers, centers[1:])]
    off = [sum(EXTRA[:k + 1]) for k in range(len(staves))]

    def band(y):
        return sum(y > c for c in cuts)

    def move(m):
        e = m.group(0)
        t = re.search(r'transform="matrix\(([^)]*)\)"', e)
        if t:
            v = t.group(1).split(",")
            dy = off[band(float(v[5]))]
            v[5] = f"{float(v[5]) + dy:g}"
            return e.replace(t.group(0), f'transform="matrix({",".join(v)})"')
        pts = re.search(r'points="([^"]*)"', e)
        if pts:
            ys = [float(p.split(",")[1]) for p in pts.group(1).split()]
            dy = off[band(sum(ys) / len(ys))]
            new = " ".join(f"{p.split(',')[0]},{float(p.split(',')[1]) + dy:g}"
                           for p in pts.group(1).split())
            return e.replace(pts.group(0), f'points="{new}"')
        d = re.search(r' d="([^"]*)"', e)
        if d:
            nums = re.findall(r"-?[\d.]+,-?[\d.]+", d.group(1))
            ys = [float(n.split(",")[1]) for n in nums]
            if not ys:
                return e
            dy = off[band(sum(ys) / len(ys))]
            if not dy:
                return e
            nd = re.sub(r"(-?[\d.]+),(-?[\d.]+)",
                        lambda q: f"{q.group(1)},{float(q.group(2)) + dy:g}",
                        d.group(1))
            return e.replace(d.group(0), f' d="{nd}"')
        return e
    svg = re.sub(r"<(?:path|polyline)\b[^>]*/>", move, svg)
    return svg, [[y + off[k] for y in st] for k, st in enumerate(staves)]


def tag_lyrics(svg, staves, tmap):
    """Give each engraved syllable an id and find its note, so a frame can
    colour what has been sung.  Returns (svg, [[id, part, start, end]])."""
    tl = json.load(open(os.path.join(HERE, "timing.json"), encoding="utf-8"))
    def seg_x(t):   # timing.json rounds to ms; tmap keeps 0.1 ms
        tt, x = min(tmap, key=lambda p: abs(p[0] - t))
        return x if abs(tt - t) < 0.01 else None
    cands = {}
    for k, pid in enumerate(["sop", "alt", "ten", "bas"]):
        cands[k] = [(seg_x(n["start"]), n) for n in tl["parts"][pid]["notes"]
                    if n["lyric"] not in ("", "-")]
    out, used = [], set()

    def tag(m):
        e = m.group(0)
        pts = [tuple(map(float, q)) for q in
               re.findall(r"(-?[\d.]+),(-?[\d.]+)", e)]
        cx = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
        cy = (min(p[1] for p in pts) + max(p[1] for p in pts)) / 2
        k = max(i for i, st in enumerate(staves) if st[0] < cy)
        best = min((abs(x + 16 - cx), i) for i, (x, n) in enumerate(cands[k])
                   if x is not None)
        assert best[0] < 60, (k, cx, best)
        x, n = cands[k][best[1]]
        key = (k, best[1])
        assert key not in used, key
        used.add(key)
        lid = f"L{len(out)}"
        out.append([lid, ["sop", "alt", "ten", "bas"][k], n["start"], n["end"]])
        return e.replace('<path class="Lyrics"', f'<path id="{lid}" class="Lyrics"')
    svg = re.sub(r'<path class="Lyrics"[^>]*/>', tag, svg)
    return svg, out


def ms4(args):
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen")
    subprocess.run([MS4] + args, env=env, check=True, timeout=600,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    E.configure(build)
    os.makedirs(OUT, exist_ok=True)
    xml = os.path.join(OUT, "excerpt.musicxml")
    mss = os.path.join(OUT, "strip.mss")
    excerpt(xml)
    style(mss, 96)
    for ext in ("svg", "spos", "mpos"):
        ms4(["-S", mss, "-o", os.path.join(OUT, "strip." + ext), xml])
    pages = sorted(f for f in os.listdir(OUT) if re.match(r"strip-\d+\.svg", f))
    assert pages == ["strip-1.svg"], f"strip broke onto pages: {pages}"
    os.replace(os.path.join(OUT, "strip-1.svg"), os.path.join(OUT, "strip.svg"))

    svg = open(os.path.join(OUT, "strip.svg"), encoding="utf-8").read()
    ys = sorted({round(float(m), 2) for m in re.findall(
        r'class="StaffLines"[^>]*points="[\d.]+,([\d.]+)', svg)})
    staves = [ys[i:i + 5] for i in range(0, len(ys), 5)]
    assert len(staves) == 8, len(staves)
    svg, staves = spread(svg, staves)
    w0, h0 = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups()
    h1 = f"{float(h0) + sum(EXTRA):g}"
    svg = svg.replace(f'height="{h0}px"', f'height="{h1}px"').replace(
        f'viewBox="0 0 {w0} {h0}"', f'viewBox="0 0 {w0} {h1}"')
    x0 = min(float(m) for m in re.findall(
        r'class="StaffLines"[^>]*points="([\d.]+),', svg))

    def elems(name):
        el = re.search(r"<elements>(.*?)</elements>", open(
            os.path.join(OUT, name)).read(), re.S).group(1)
        ev = re.search(r"<events>(.*?)</events>", open(
            os.path.join(OUT, name)).read(), re.S).group(1)
        xs = {int(i): float(x) / U for i, x in
              re.findall(r'id="(\d+)" x="([\d.]+)"', el)}
        return [(int(p), xs[int(i)]) for i, p in
                re.findall(r'elid="(\d+)" position="(\d+)"', ev)]
    seg = elems("strip.spos")
    bars = elems("strip.mpos")
    assert len(bars) == B2 - B1 + 1, len(bars)
    # MuseScore stretches fermatas in playback, so its milliseconds drift
    # after bar 71.  Map each bar's segments 1:1 onto the distinct onsets
    # (notes and rests, all parts) of that bar instead.
    parsed = {p["id"]: E.parse_part(p["data"]) for p in build.PARTS}
    tmap = []
    for k, (bms, _) in enumerate(bars):
        b = B1 + k
        nxt = bars[k + 1][0] if k + 1 < len(bars) else float("inf")
        xs = [x for ms, x in seg if bms <= ms < nxt]
        on = sorted({e["abs"] for evs in parsed.values() for e in evs
                     if e["bar"] == b})
        assert len(xs) == len(on), (b, len(xs), len(on))
        tmap += [(round(E.sec_at(a), 4), round(x, 2)) for a, x in zip(on, xs)]
    last = E.absq(B2) + E.BARLEN[B2]
    svg, lyrics = tag_lyrics(svg, staves, tmap)
    open(os.path.join(OUT, "strip.svg"), "w", encoding="utf-8").write(svg)
    end_x = float(re.search(r'width="([\d.]+)px"', svg).group(1))
    data = dict(
        bars=[dict(bar=B1 + i, t=round(E.sec_at(E.absq(B1 + i)), 4),
                   x=round(x, 2)) for i, (_, x) in enumerate(bars)],
        end=dict(t=round(E.sec_at(last), 4)),
        tmap=tmap, lyrics=lyrics, staves=staves, staff_x0=round(x0, 2),
        header_end=round(bars[0][1], 2), width=end_x,
        height=float(re.search(r'height="([\d.]+)px"', svg).group(1)),
        parts=["sop", "alt", "ten", "bas", "vn1", "vn2", "va", "vc"])
    json.dump(data, open(os.path.join(OUT, "strip.json"), "w"), indent=1)
    print(f"strip {data['width']:.0f}x{data['height']:.0f} px, "
          f"{len(tmap)} time points, {len(lyrics)} syllables, bars {B1}-{B2}, "
          f"staves at {[round(s[0]) for s in staves]}")


if __name__ == "__main__":
    main()
