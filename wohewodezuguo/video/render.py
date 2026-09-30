#!/usr/bin/env python3
"""Render the 抖音 video (final layout, 1080x1920) with the user's mix.

    python3 render.py 92.0 102.0 out.mp4      # the 10-second sample
    python3 render.py 92.0 174.6 out.mp4      # the whole cut

Every frame is the page from frames.final() driven to its time: the score
scrolls so that each note reaches the playhead exactly at its onset (a
monotone cubic through the engraved segments, so the speed changes
smoothly), sung syllables turn red, silent voices fade, the big lyric line
fills in character by character.  Frames are captured with headless
Chromium (render.mjs, playwright-core) and piped to ffmpeg; the audio is
the user's Logic mix, cut and muxed untouched apart from short fades.

Needs: node + playwright-core (PW_DIR=<dir with node_modules>), ffmpeg,
the mix at MIX (or $MIX).
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import frames as F  # noqa: E402

FPS = 30
MIX = os.environ.get("MIX", os.path.join(HERE, "mix", "我和我的祖国_混音.mp3"))
PW_DIR = os.environ.get("PW_DIR", HERE)
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
ROWS = ["sop", "alt", "ten", "bas"]


def pchip(xk, yk, x):
    """Monotone cubic (Fritsch-Carlson) through (xk, yk), evaluated at x."""
    xk, yk = np.asarray(xk, float), np.asarray(yk, float)
    h = np.diff(xk)
    d = np.diff(yk) / h
    m = np.zeros_like(yk)
    for i in range(1, len(xk) - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    m[0], m[-1] = d[0], d[-1]
    i = np.clip(np.searchsorted(xk, x) - 1, 0, len(h) - 1)
    t = (x - xk[i]) / h[i]
    h00, h10 = 2 * t**3 - 3 * t**2 + 1, t**3 - 2 * t**2 + t
    h01, h11 = -2 * t**3 + 3 * t**2, t**3 - t**2
    return h00 * yk[i] + h10 * h[i] * m[i] + h01 * yk[i + 1] + h11 * h[i] * m[i + 1]


def frame_data(t0, t1, sc):
    n = int(round((t1 - t0) * FPS))
    ts = t0 + np.arange(n) / FPS
    # score position: through every engraved segment, extended past the end
    tk = [a for a, _ in F.S["tmap"]] + [F.S["end"]["t"], F.S["end"]["t"] + 10]
    # ...and come to rest on the final barline
    xk = [b for _, b in F.S["tmap"]] + [F.S["width"] - 60, F.S["width"] - 60]
    xs = pchip(tk, xk, ts)
    s = sc.s
    # ending: ease to a stop with the final barline 330 px right of the
    # playhead, so the last chord 「歌」 and its fermata stay on screen
    x_stop = F.S["width"] - 60 - 330 / s
    x_a = x_stop - 500
    over = np.maximum(xs - x_a, 0)
    xs = np.where(xs <= x_a, xs,
                  x_a + (x_stop - x_a) * (1 - np.exp(-over / (x_stop - x_a))))
    body_x = sc.label_w + sc.hdr_w
    tx = (sc.play_x - sc.x - body_x) - xs * s
    # silent voices fade (0.62), eased
    veil = {}
    for pid in ROWS:
        # lift a little before an entry, fade a little after the last note
        notes = F.T["parts"][pid]["notes"]
        end = max(nt["end"] for r in ROWS          # after the last sung
                  for nt in F.T["parts"][r]["notes"]) - .2   # note: all lit
        target = np.array([0 if t >= end or any(
            nt["start"] - .35 <= t < nt["end"] + .3 for nt in notes)
            else .62 for t in ts])
        v = np.empty_like(target)
        v[0] = target[0]
        k = 1 - np.exp(-1 / (FPS * .10))
        for i in range(1, n):
            v[i] = v[i - 1] + (target[i] - v[i - 1]) * k
        veil[pid] = [round(float(a), 3) for a in v]
    on = {pid: [bool(veil[pid][i] < .31) for i in range(n)] for pid in ROWS}
    lines = F.T["lines"]
    line_idx = []
    for t in ts:
        l = F.line_at(t)
        line_idx.append(lines.index(l))
    return dict(
        t=[round(float(a), 4) for a in ts],
        tx=[round(float(a), 2) for a in tx],
        ty=round(-sc.top * s, 2), s=round(s, 5),
        veil=veil, on=on, line=line_idx,
        lines=[dict(chars=[[c["char"], c["start"]] for c in l["chars"]])
               for l in lines],
        lyrics=[l for l in F.S["lyrics"] if l[1] in ROWS],
        colors=dict(ink=F.INK, red=F.CINNABAR, grey=F.LABEL))


JS = r"""
<script>
const D = __DATA__;
const sb = document.getElementById('scorebody');
const big = document.getElementById('bigline');
const lyr = D.lyrics.map(l => [sb.querySelector('#' + l[0]), l[2], l[3], null]);
let cur = -1;
function apply(i) {
  const t = D.t[i];
  sb.style.transform = `translate(${D.tx[i]}px,${D.ty}px) scale(${D.s})`;
  for (const p in D.veil) document.getElementById('veil-' + p).style.opacity = D.veil[p][i];
  for (const p in D.on) document.getElementById('lab-' + p).classList.toggle('on', D.on[p][i]);
  if (D.line[i] !== cur) {
    cur = D.line[i];
    big.innerHTML = D.lines[cur].chars.map(c => `<span>${c[0]}</span>`).join('');
  }
  const sp = big.children;
  D.lines[cur].chars.forEach((c, k) => {
    const done = c[1] <= t;
    sp[k].style.color = done ? D.colors.red : D.colors.ink;
    sp[k].style.opacity = done ? 1 : .28;
  });
  for (const L of lyr) {
    const st = L[2] <= t ? 'p' : (L[1] <= t ? 'n' : 'f');
    if (st === L[3]) continue;
    L[3] = st;
    L[0].style.fill = st === 'n' ? D.colors.red : (st === 'p' ? D.colors.ink : D.colors.grey);
    L[0].style.opacity = st === 'p' ? .8 : 1;
  }
  return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
}
</script>
"""


def main():
    t0, t1, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    deco = os.environ.get("DECO", "banner")
    work = os.path.join(HERE, "frames")
    os.makedirs(work, exist_ok=True)
    sc = F.Score(ROWS, 0, 846, F.W, 8.8, 150, 420, bottom_pad=6.0)
    html = F.final(t0, deco)
    data = frame_data(t0, t1, sc)
    html = html.replace("</body>", JS.replace("__DATA__", json.dumps(
        data, ensure_ascii=False)) + "</body>")
    hp = os.path.join(work, "_render.html")
    open(hp, "w", encoding="utf-8").write(html)
    silent = os.path.join(work, "_silent.mp4")
    env = dict(os.environ, PW_DIR=PW_DIR, CHROME=CHROME)
    subprocess.run(["node", os.path.join(HERE, "render.mjs"), hp,
                    str(len(data["t"])), str(FPS), silent], check=True, env=env)
    dur = len(data["t"]) / FPS
    fade_out = min(1.2, dur / 6)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", silent,
        "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", MIX,
        "-map", "0:v", "-map", "1:a", "-c:v", "copy",
        "-af", f"afade=t=in:d=0.04,afade=t=out:st={dur - fade_out:.3f}:d={fade_out:.3f}",
        "-c:a", "aac", "-b:a", "256k", "-ar", "44100",
        "-movflags", "+faststart", "-shortest", out], check=True)
    print(out, f"{dur:.2f} s")


if __name__ == "__main__":
    main()
