"""haishui -- homage to the 海水江崖 (sea-water-and-cliff) hem of Qing
ceremonial robes, as revived in modern state dress, and to 常沙娜's
decorative design for state ceremony (Dunhuang mineral palette, 退晕 colour
bands, strict bilateral symmetry, fine gold line).

The page is a vermilion robe, its satin woven with a faint 如意-cloud damask
(暗花); its hem is the 海水江崖:
  * 立水 standing water: steep parallel stripes in five-tone 退晕 groups,
    石青 and 石绿 by turns, a gold thread between groups, mirrored about the
    axis and meeting there in nested round arches that echo the peak, so
    the axis is drawn, not stitched;
  * 平水 rolling sea: two rows of curling crests (卷浪), each four strands
    rising up a concave back into one spiral, 月白-to-石青 退晕 between them,
    gold edged; they roll in from both sides, and the central pair meet in
    a clean V trough on the axis;
  * 江崖: a 山-shaped massif of three stepped peaks, the sawtooth outline
    echoed inward in a jade-to-azurite rim and then in fine gold strata on
    the deep core 「我歌唱每一座高山」;
  * 浪花: from the trough at the foot of the cliff one spray of drops is
    thrown up against the dark rock: the 「浪花一朵」 of 「像海和浪花一朵」,
    the small 我 before the vast 祖国;
  * two restrained 如意 clouds in couched gold line, tails streaming out.
Above: a 方胜 (two interlocked lozenges, the old sign of two that cannot be
parted, 「一刻也不能分割」) over the gold title, set in Noto Serif Bold with
a stamped edge and optically spaced; the credits hang on a gold spine on
the same axis as the peak.  Everything is vector.
"""
import math

import lib

e, sym = lib.e, lib.sym

# ---- palette ---------------------------------------------------------------
RED = "#931D1E"       # 朱红 ground
RED_HI = "#A8291F"    # glow behind title and peak
RED_LO = "#6C1316"    # deep edges
RED_DK = "#4E0B0E"    # stamped shadow under the gold
GOLD = "#D6B062"      # 泥金
CREAM = "#F2E7CF"     # 月白 / names
QING_D = "#142D45"    # 石青 deep
QING = "#24507A"      # 石青
QING_M = "#4C7FA6"    # 二青
QING_L = "#9DBCD0"    # 三青
LV_D = "#1A4A44"      # 石绿 deep
LV = "#317A69"        # 石绿
LV_M = "#5E9F88"      # 二绿
LV_L = "#A8CDB6"      # 三绿
MOON = "#E9E3D0"      # 月白
HEM = "#13263A"       # hem border
SPINE = "#B56740"     # gold half-way into the red: the credits' spine

PW, PH = 1100, 1700   # SVG units: 0.01 in
CX = PW / 2


def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def pth(pts, close=False):
    s = "M" + " L".join(f"{f(x)},{f(y)}" for x, y in pts)
    return s + (" Z" if close else "")


def tapered(center, w0, w1=0.0):
    """Filled outline of a stroke along `center` whose width goes w0 -> w1."""
    n = len(center)
    L, R = [], []
    for i in range(n):
        x0, y0 = center[max(i - 1, 0)]
        x2, y2 = center[min(i + 1, n - 1)]
        tx, ty = x2 - x0, y2 - y0
        ln = math.hypot(tx, ty) or 1
        nx, ny = -ty / ln, tx / ln
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * t) / 2
        x, y = center[i]
        L.append((x + nx * w, y + ny * w))
        R.append((x - nx * w, y - ny * w))
    return pth(L + R[::-1], True)


def bez(p0, p1, p2, p3, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


# ---- 立水 standing water ------------------------------------------------------
LS_TOP, LS_BOT = 1372, 1588
LS_K = 0.40          # horizontal run per unit of rise (about 68 deg from horizontal)
LS_P = 6.0           # horizontal pitch of one stripe
LS_A = 20.0          # radius of the arches where the two halves meet
LS_GROUPS = [["#132A40", "#1C3D5C", "#28567A", "#3C6F92", "#5A88A6"],
             ["#132F2E", "#1B4842", "#276257", "#3A7B6A", "#5A9580"]]


def lishui():
    """Nested curves y = T + (g(x) - u)/k with g(x) = hypot(x - CX, a) - a:
    straight slanted stripes on both sides that turn into round arches on
    the axis.  Painted from the outermost in, each over the last."""
    T, B = LS_TOP - 30, LS_BOT + 2
    gmax = math.hypot(CX, LS_A) - LS_A
    umin = -(B - T) * LS_K
    n = int((gmax - umin) / LS_P) + 2
    xs = [i * 2.0 for i in range(int(PW / 2) + 1)]
    gs = [math.hypot(x - CX, LS_A) - LS_A for x in xs]
    out = [f'<clipPath id="lsc"><rect x="0" y="{T + 30}" width="{PW}" height="{B - T - 30}"/></clipPath>',
           '<g clip-path="url(#lsc)">']
    lines = []
    for j in range(n, -1, -1):
        u = umin + j * LS_P
        pts = []
        for x, g in zip(xs, gs):
            y = T + (g - u) / LS_K
            if y < B + 4:
                pts.append((x, max(y, T - 4)))
        if not pts:
            continue
        grp = LS_GROUPS[(j // 5) % 2]
        col = grp[4 - j % 5]
        poly = [(pts[0][0], B + 4)] + pts + [(pts[-1][0], B + 4)]
        out.append(f'<path d="{pth(poly, True)}" fill="{col}"/>')
        if j % 5 == 0:
            lines.append(f'<path d="{pth(pts)}" fill="none" stroke="{GOLD}" stroke-width=".75"/>')
    out.extend(lines)
    out.append('</g>')
    return "".join(out)


# ---- 平水 rolling crests ------------------------------------------------------
CREST_BANDS = [MOON, QING_L, QING_M]   # outer edge -> in; the body is QING
CREST_BANDS_G = [MOON, LV_L, LV_M]


def crest(s, depth, bands, body, line):
    """One 卷浪 rolling to the right, base-left at (0, 0), y up is negative;
    `s` scales it.  Four parallel strands rise along a concave back and curl
    over into one spiral (an Archimedean multi-arm spiral, so the strands
    keep their spacing all the way in); the bands between them are filled
    light-to-dark (退晕) and the outer strand is drawn in gold."""
    N = 4
    R0 = 34 * s
    g = R0 / 8.6
    L = 64 * s
    H = 84 * s
    ex, ey = L + R0, -(H - R0)
    T = 1.15                       # turns of the spiral
    strands = []
    for k in range(N):
        r = R0 - k * g
        sx = k * g * 1.9
        back = bez((sx, 0), (sx + .62 * (ex - r - sx), 0), (ex - r, ey * .42), (ex - r, ey), 26)
        sp = []
        m = 70
        for i in range(1, m + 1):
            th = math.pi + T * 2 * math.pi * i / m
            rr = r - N * g * (th - math.pi) / (2 * math.pi)
            sp.append((ex + rr * math.cos(th), ey + rr * math.sin(th)))
        strands.append(back + sp)
    # silhouette: outer strand to the crest's right-most point, then the
    # front face falls back to the base
    s0 = strands[0]
    i_right = 26 + 35   # theta = 2 pi on the outer strand
    face = bez(s0[i_right], (ex + R0 * 1.02, ey * .45), (ex + R0 * 1.1, -2 * s), (ex + R0 * 1.18, 0), 14)
    sil = s0[:i_right + 1] + face[1:] + [(ex + R0 * 1.18, depth), (0, depth)]
    out = [f'<path d="{pth(sil, True)}" fill="{body}"/>']
    for k in range(N - 1):
        a, b = strands[k], strands[k + 1]
        out.append(f'<path d="{pth(a + b[::-1], True)}" fill="{bands[k]}"/>')
    # 水纹: the body's own current, fine lines running on up the back and
    # into the inner turn of the curl
    for k in range(N, N + 3):
        r = R0 - k * g
        sx = k * g * 1.9
        back = bez((sx, 0), (sx + .62 * (ex - r - sx), 0), (ex - r, ey * .42), (ex - r, ey), 26)
        out.append(f'<path d="{pth(back)}" fill="none" stroke="{line}" stroke-width=".7"/>')
    out.append(f'<path d="{pth(s0)}" fill="none" stroke="{GOLD}" stroke-width="{f(1.0 * max(s, .8))}" '
               f'stroke-linejoin="round"/>')
    out.append(f'<path d="{pth(face)}" fill="none" stroke="{GOLD}" stroke-width=".7"/>')
    return "".join(out), s0[i_right][0]


_ROWS = [0]


def crest_row(y, s, pitch, depth, green=False):
    """A row of crests rolling in from both edges toward the axis.  The two
    central ones come close enough that their faces would cross; each is
    cut at the axis, so their faces meet there in one V, like the trough
    between two waves, and their bodies join without a seam."""
    bands = CREST_BANDS_G if green else CREST_BANDS
    body = LV_D if green else QING
    unit, rp = crest(s, depth, bands, body, LV if green else QING_M)
    _ROWS[0] += 1
    cid = f"axis{_ROWS[0]}"
    x_in = CX - 7 * s - rp          # the innermost crest's curl stops just short of the axis
    xs = []
    x = x_in - pitch
    while x + rp + 60 * s > -20:
        xs.append(x)
        x -= pitch
    xs.reverse()           # outermost first, so each one overlaps the last
    half = [f'<g transform="translate({f(x)},{f(y)})">{unit}</g>' for x in xs]
    half.append(f'<g clip-path="url(#{cid})"><g transform="translate({f(x_in)},{f(y)})">{unit}</g></g>')
    left = "".join(half)
    clip = f'<clipPath id="{cid}"><rect x="-50" y="0" width="{f(CX + 50)}" height="{PH}"/></clipPath>'
    return clip + left + f'<g transform="translate({PW},0) scale(-1,1)">{left}</g>'


# ---- 江崖 the cliff -----------------------------------------------------------
def profile(h, wb, steps, p=.8, ext=50):
    """Half-width of a rock at depth s below its tip (sampled every 0.5
    unit): a flared envelope wb * (s/h)**p cut by ledges -- at each step
    (depth, ledge) the face has drawn in by `ledge` and steps back out to
    the envelope, so the silhouette is a stepped sawtooth along the curve."""
    ws = []
    marks = [0.0] + [d for d, _ in steps] + [h + 60]
    ledges = [l for _, l in steps] + [0.0]
    for i in range(int((h + ext) * 2)):
        s = i / 2
        env = wb * (min(s, h) / h) ** p + (s - h) * .2 * (s > h)
        k = max(j for j in range(len(marks) - 1) if marks[j] <= s)
        t = (s - marks[k]) / (marks[k + 1] - marks[k])
        ws.append(env - ledges[k] * t ** 1.5)
    return ws


def erode(ws, d):
    """Exact erosion of a half-width profile by a disc of radius d."""
    if d <= 0:
        return ws[:]
    k = int(d * 2)
    out = []
    n = len(ws)
    for i in range(n):
        best = 1e9
        for j in range(-k, k + 1):
            ii = i + j
            w = ws[ii] if 0 <= ii < n else (-1e9 if ii < 0 else ws[-1])
            v = w - math.sqrt(max(d * d - (j / 2) ** 2, 0.0))
            if v < best:
                best = v
        out.append(best)
    return out


def pillar_path(cx, yt, ws, lean=0.0):
    left, right = [], []
    n = len(ws)
    for i in range(0, n, 1):
        w = ws[i]
        if w <= 0.05:
            continue
        s = i / 2
        sh = lean * max(0.0, 1 - s / (n / 2)) ** 1.6
        left.append((cx - w + sh, yt + s))
        right.append((cx + w + sh, yt + s))
    if len(left) < 3:
        return None
    # thin the point list on straight runs
    def thin(pts):
        out = [pts[0]]
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = out[-1], pts[i], pts[i + 1]
            if abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)) > .35:
                out.append(pts[i])
        out.append(pts[-1])
        return out
    return pth(thin(left)[::-1] + thin(right), True)


def pillar(cx, yt, ws, bands, lean=0.0):
    """A 江崖 pillar: its stepped outline echoed inward, first in 退晕 colour
    bands from the pale rim to the deep core, then, inside the core, as
    fine gold strata lines (bands with no colour)."""
    out = []
    for i, (d, c) in enumerate(bands):
        dp = pillar_path(cx, yt, erode(ws, d), lean)
        if not dp:
            break
        if c:
            out.append(f'<path d="{dp}" fill="{c}"/>')
            out.append(f'<path d="{dp}" fill="none" stroke="{GOLD}" '
                       f'stroke-width="{".9" if i == 0 else ".5"}" stroke-linejoin="round"/>')
        else:
            out.append(f'<path d="{dp}" fill="none" stroke="{GOLD}" stroke-opacity=".62" '
                       f'stroke-width=".45" stroke-linejoin="round"/>')
    return "".join(out)


def strata(rim, step, upto):
    """退晕 bands: the coloured rim, then gold strata lines every `step`."""
    out = list(rim)
    d = rim[-1][0]
    while d + step < upto:
        d += step
        out.append((d, None))
    return out


BANDS_MAIN = strata([(0, LV_L), (3.5, LV_M), (8, LV), (13.5, QING_M), (20, QING), (28, QING_D)], 8.5, 170)
BANDS_SIDE = strata([(0, LV_L), (3.5, LV_M), (8, LV), (14, LV_D), (20, QING), (27, "#18344C")], 7.5, 110)


def jiangya():
    out = []
    side = profile(290, 118, [(56, 12), (114, 11), (170, 13), (232, 10)], p=.78, ext=34)
    for sg in (-1, 1):
        out.append(pillar(CX + sg * 128, 1052, side, BANDS_SIDE, lean=sg * 8))
    main = profile(444, 166, [(76, 12), (146, 14), (204, 11), (270, 15), (330, 11), (392, 13)], p=.8, ext=34)
    out.append(pillar(CX, 896, main, BANDS_MAIN))
    return "".join(out)


# ---- 浪花 the one spray ----------------------------------------------------------
def spray(x, y, s):
    """The one 浪花 thrown up from the trough where the two central crests
    meet: fine drops flung along three symmetric fountain arcs, shrinking
    as they fly, and a few rising straight up at the crown."""
    out = []
    for sg in (-1, 1):
        for span, hgt, nd, r0, t0 in ((.26, 1.5, 4, .046, .45), (.5, 1.2, 4, .04, .4), (.72, .92, 3, .032, .38)):
            for i in range(nd):
                t = t0 + (.92 - t0) * i / (nd - 1)
                px = x + sg * s * span * t
                py = y - s * hgt * (2.2 * t - 1.6 * t * t)
                rr = s * r0 * (1.15 - .55 * t)
                out.append(f'<circle cx="{f(px)}" cy="{f(py)}" r="{f(rr)}" fill="{CREAM}"/>')
    for dy, r in ((1.32, .05), (1.56, .032), (1.72, .022)):
        out.append(f'<circle cx="{f(x)}" cy="{f(y - s * dy)}" r="{f(s * r)}" fill="{CREAM}"/>')
    return "".join(out)


# ---- 祥云 clouds -----------------------------------------------------------------
def spiral_pts(cx, cy, r, turns, a0, cw, r_in, n=80):
    pts = []
    for i in range(n + 1):
        t = i / n
        a = a0 + (1 if cw else -1) * t * turns * 2 * math.pi
        rr = r * (1 - t * (1 - r_in))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def _meet(c1, c2, upper):
    """The upper (or lower) intersection point of two circles."""
    (x1, y1, r1), (x2, y2, r2) = c1, c2
    d = math.hypot(x2 - x1, y2 - y1)
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(r1 * r1 - a * a, 0))
    mx, my = x1 + a * (x2 - x1) / d, y1 + a * (y2 - y1) / d
    p1 = (mx + h * (y2 - y1) / d, my - h * (x2 - x1) / d)
    p2 = (mx - h * (y2 - y1) / d, my + h * (x2 - x1) / d)
    return min(p1, p2, key=lambda p: p[1]) if upper else max(p1, p2, key=lambda p: p[1])


def _arc(c, p, q, key, n=40):
    """Points along circle c from p to q, whichever way round gives the
    smaller key(midpoint)."""
    x, y, r = c
    a1 = math.atan2(p[1] - y, p[0] - x)
    a2 = math.atan2(q[1] - y, q[0] - x)
    best = None
    for sgn in (1, -1):
        span = (a2 - a1) % (2 * math.pi) if sgn > 0 else -((a1 - a2) % (2 * math.pi))
        pts = [(x + r * math.cos(a1 + span * i / n), y + r * math.sin(a1 + span * i / n)) for i in range(n + 1)]
        k = key(pts[n // 2])
        if best is None or k < best[0]:
            best = (k, pts)
    return best[1]


def chain_outline(circ):
    """Outline of a left-to-right chain of overlapping circles: round the
    first, over the tops, round the last, back under the bottoms."""
    n = len(circ)
    T = [_meet(circ[i], circ[i + 1], True) for i in range(n - 1)]
    B = [_meet(circ[i], circ[i + 1], False) for i in range(n - 1)]

    def away(c):        # prefer the way round farther from circle c
        return lambda p: -math.hypot(p[0] - c[0], p[1] - c[1])
    pts = _arc(circ[0], B[0], T[0], away(circ[1]))[:-1]
    for i in range(1, n - 1):
        pts += _arc(circ[i], T[i - 1], T[i], lambda p: p[1])[:-1]
    pts += _arc(circ[-1], T[-1], B[-1], away(circ[-2]))[:-1]
    for i in range(n - 2, 0, -1):
        pts += _arc(circ[i], B[i], B[i - 1], lambda p: -p[1])[:-1]
    return pts


def cloud(cx, cy, s, flip=1):
    """A 如意 cloud in gold line: a chain of four lobes with a double
    contour (as couched gold thread is laid), each lobe holding a curl that
    starts at the notch beside it, and a long tail streaming outward.
    flip=1: head toward the left, tail to the right."""
    u = 22 * s
    spec = [(-.80, .14, .44), (0, -.20, .62), (.80, .16, .42), (1.36, .36, .26)]
    if flip < 0:
        spec = [(-dx, dy, r) for dx, dy, r in spec[::-1]]
    circ = [(cx + dx * u, cy + dy * u, r * u) for dx, dy, r in spec]
    out = []
    tail_x = max(c[0] + c[2] for c in circ) - .3 * u if flip > 0 else min(c[0] - c[2] for c in circ) + .3 * u
    for dy, ln, w0, lift in ((.36, 3.0, .12, .42), (.56, 2.2, .08, .26)):
        tc = []
        for i in range(60):
            t = i / 59
            tc.append((tail_x + flip * ln * u * t,
                       cy + dy * u - lift * u * math.sin(t * math.pi) + .10 * u * t))
        out.append(f'<path d="{tapered(tc, w0 * u, .012 * u)}" fill="{GOLD}"/>')
    outer = chain_outline(circ)
    inner = chain_outline([(x, y, r - 2.8) for x, y, r in circ])
    out.append(f'<path d="{pth(outer, True)}" fill="{RED_HI}" stroke="{GOLD}" stroke-width="1.1" stroke-linejoin="round"/>')
    out.append(f'<path d="{pth(inner, True)}" fill="none" stroke="{GOLD}" stroke-width=".45" stroke-linejoin="round"/>')
    # curls: each starts inside the lobe beside the notch it shares with its
    # bigger neighbour and winds in the other way round
    big = max(range(len(circ)), key=lambda i: circ[i][2])
    for i, (x, y, r) in enumerate(circ):
        j = i + 1 if i < big else i - 1 if i > big else (i - 1 if flip > 0 else i + 1)
        nb = circ[j]
        ang = math.atan2(nb[1] - y, nb[0] - x)
        cw = nb[0] < x            # neighbour on the left: wind clockwise over the top
        sp = spiral_pts(x, y, r * .74, 1.2, ang, cw, .18, 80)
        out.append(f'<path d="{pth(sp)}" fill="none" stroke="{GOLD}" stroke-width="1.0" stroke-linecap="round"/>')
    return "".join(out)


# ---- ornaments ---------------------------------------------------------------
def fangsheng(cx, cy, a, col=GOLD, sw=1.0):
    """方胜: two interlocked lozenges (「一刻也不能分割」)."""
    out = []
    for dx in (-a * .5, a * .5):
        x = cx + dx
        out.append(f'<path d="M{f(x)},{f(cy - a)} L{f(x + a)},{f(cy)} L{f(x)},{f(cy + a)} L{f(x - a)},{f(cy)} Z" '
                   f'fill="none" stroke="{col}" stroke-width="{sw}"/>')
    out.append(f'<path d="M{f(cx)},{f(cy - a * .5)} L{f(cx + a * .5)},{f(cy)} L{f(cx)},{f(cy + a * .5)} '
               f'L{f(cx - a * .5)},{f(cy)} Z" fill="{col}"/>')
    return "".join(out)


def rule_pair(y, x_in, x_out, sw=.8):
    out = []
    for side in (-1, 1):
        x0, x1 = CX + side * x_in, CX + side * x_out
        out.append(f'<line x1="{f(x0)}" y1="{f(y)}" x2="{f(x1)}" y2="{f(y)}" stroke="{GOLD}" stroke-width="{sw}"/>')
        out.append(f'<circle cx="{f(x1 + side * 4)}" cy="{f(y)}" r="1.5" fill="{GOLD}"/>')
    return "".join(out)


# text the damask keeps clear of (x0, y0, x1, y1 in svg units)
KEEP_OUT = [(320, 55, 780, 125), (380, 130, 720, 170), (110, 170, 990, 330), (270, 335, 830, 375),
            (280, 395, 820, 480), (280, 520, 820, 795),
            (60, 935, 370, 1065), (730, 935, 1040, 1065)]          # the two clouds


def damask():
    """暗花: a woven ground of 如意 cloud heads in a half-drop repeat, drawn
    a shade darker than the red, as on the satin of a ceremonial robe."""
    k = 17
    circ = [(-.80 * k, .14 * k, .44 * k), (0, -.20 * k, .62 * k),
            (.80 * k, .16 * k, .42 * k), (1.36 * k, .36 * k, .26 * k)]
    parts = [f'<path d="{pth(chain_outline(circ), True)}"/>']
    for i, (x, y, r) in enumerate(circ):
        nb = circ[i + 1] if i == 0 else circ[i - 1]
        ang = math.atan2(nb[1] - y, nb[0] - x)
        parts.append(f'<path d="{pth(spiral_pts(x, y, r * .7, 1.15, ang, nb[0] < x, .2, 50))}"/>')
    out = [f'<defs><g id="dm">{"".join(parts)}</g></defs>',
           f'<g fill="none" stroke="{RED_DK}" stroke-opacity=".22" stroke-width=".9" stroke-linecap="round">']
    dx, dy = 200, 140
    r = 0
    y = 60
    while y < 1240:
        x = 50 + (dx / 2 if r % 2 else 0)
        while x < PW + 60:
            flip = -1 if r % 2 else 1
            x0, x1 = x - (28 if flip > 0 else 22), x + (22 if flip > 0 else 28)
            if not any(x1 > kx0 and x0 < kx1 and y + 16 > ky0 and y - 16 < ky1
                       for kx0, ky0, kx1, ky1 in KEEP_OUT):
                out.append(f'<use href="#dm" transform="translate({f(x)},{f(y)}) scale({flip},1)"/>')
            x += dx
        y += dy
        r += 1
    out.append('</g>')
    return "".join(out)


def art():
    _ROWS[0] = 0
    defs = f"""
    <defs>
      <radialGradient id="bg" cx="50%" cy="18%" r="80%">
        <stop offset="0" stop-color="{RED_HI}"/>
        <stop offset=".55" stop-color="{RED}"/>
        <stop offset="1" stop-color="{RED_LO}"/>
      </radialGradient>
      <radialGradient id="glow" gradientUnits="userSpaceOnUse" cx="{CX}" cy="1040" r="430">
        <stop offset="0" stop-color="{RED_HI}" stop-opacity=".55"/>
        <stop offset="1" stop-color="{RED_HI}" stop-opacity="0"/>
      </radialGradient>
    </defs>"""
    body = [f'<rect width="{PW}" height="{PH}" fill="url(#bg)"/>',
            f'<rect width="{PW}" height="{PH}" fill="url(#glow)"/>',
            damask(),
            fangsheng(CX, 150, 8),
            rule_pair(150, 20, 150),
            cloud(CX - 300, 1010, 1.8, -1), cloud(CX + 300, 1010, 1.8, 1),
            lishui(),
            jiangya(),
            crest_row(1312, .94, 128, 70, green=True),
            crest_row(1380, 1.1, 148, 0),
            spray(CX, 1268, 70),
            f'<rect x="0" y="1379.2" width="{PW}" height="1.2" fill="{GOLD}"/>',
            f'<rect x="0" y="{LS_BOT}" width="{PW}" height="{PH - LS_BOT}" fill="{HEM}"/>',
            f'<rect x="0" y="{LS_BOT}" width="{PW}" height="2.2" fill="{GOLD}"/>',
            f'<rect x="0" y="{LS_BOT + 6}" width="{PW}" height=".8" fill="{GOLD}"/>',
            rule_pair(1622.5, 90, 230)]
    return (f'<svg class="art" width="11in" height="17in" viewBox="0 0 {PW} {PH}">'
            f'{defs}{"".join(body)}</svg>')


# optical spacing of the big title: per-glyph nudges (inches) that even out
# the ink gaps (measured from the render; 国 is a closed box, 和 opens right)
TITLE_NUDGE = {"我和我的祖国": [0, .032, .034, -.004, .038, 0]}


def title_html(t):
    nudge = TITLE_NUDGE.get(t, [0] * len(t))
    return "".join(f'<span style="position:relative;left:{d:.3f}in">{e(ch)}</span>' if d else e(ch)
                   for ch, d in zip(t, nudge))


def render(m):
    rows = lib.credit_rows(m)
    key_parts = [p.strip() for p in m["key"].split("·")]
    keyline = (f'{sym(key_parts[0])} <span class="cn">{e(" ".join(key_parts[1:]))}</span>'
               f'<span class="dot">·</span>{sym(m["tempo"])}<span class="dot">·</span>{sym(m["duration"])}')
    instr = '<span class="dot">·</span>'.join(
        f'{e(en)} <span class="cn">{e(zh)}</span>' for en, zh in m["instrumentation"])
    cr = "".join(
        f'<div class="cr"><span class="l"><span class="en">{e(en)}</span><span class="zh">{e(zh)}</span></span>'
        f'<span class="mk"><i></i></span><span class="nm">{e(nm)}</span></div>' for zh, en, nm in rows)
    css = f"""
    .page {{ background:{RED}; color:{CREAM}; }}
    .art {{ position:absolute; left:0; top:0; }}
    .t {{ position:absolute; left:0; width:11in; text-align:center; white-space:nowrap; }}
    .fs {{ top:.74in; left:-.02in; font:500 14pt/1 'EB Garamond'; letter-spacing:.6em; padding-left:.6em; color:{GOLD}; }}
    .sic {{ top:1.05in; font:500 7.5pt/1 'EB Garamond'; letter-spacing:.42em; padding-left:.42em;
            color:{GOLD}; text-transform:uppercase; opacity:.85; }}
    .title {{ top:1.86in; left:.015in; font:700 92pt/1 'Noto Serif CJK SC'; letter-spacing:.1em; padding-left:.1em;
              color:{GOLD}; text-shadow:0 1.1pt 0 {RED_DK}; }}
    .py {{ top:3.5in; font:500 12pt/1 'EB Garamond'; letter-spacing:.5em; padding-left:.5em;
           color:{GOLD}; text-transform:uppercase; }}
    .sub {{ top:4.12in; font:500 17pt/1 'Noto Serif CJK SC'; letter-spacing:.14em; padding-left:.14em; }}
    .sube {{ top:4.5in; font:italic 400 12.5pt/1 'EB Garamond'; opacity:.82; }}
    .credits {{ position:absolute; left:0; width:11in; top:5.36in; }}
    .cr {{ display:grid; grid-template-columns:1fr .6in 1fr; align-items:baseline; height:.38in; }}
    .cr .l {{ text-align:right; }}
    .cr .en {{ font:500 7.3pt/1 'EB Garamond'; letter-spacing:.3em; text-transform:uppercase; color:{GOLD};
               opacity:.78; margin-right:.16in; }}
    .cr .zh {{ font:600 11.5pt/1 'Noto Serif CJK SC'; letter-spacing:.12em; color:{GOLD}; }}
    .cr .mk {{ justify-self:center; position:relative; width:3.8pt; height:3.8pt; transform:translateY(-2.9pt); }}
    .cr .mk i {{ position:absolute; left:0; top:0; width:100%; height:100%; background:{GOLD}; transform:rotate(45deg); }}
    .cr .mk::before {{ content:''; position:absolute; left:0; width:100%; top:calc(50% - .19in);
                       height:.38in; background:{SPINE}; transform:scaleX(.1316); }}
    .cr:first-child .mk::before {{ top:50%; height:.19in; }}
    .cr:last-child .mk::before {{ height:.19in; }}
    .cr .nm {{ font:600 12.5pt/1 'Noto Serif CJK SC'; letter-spacing:.1em; color:{CREAM}; text-align:left; }}
    .key {{ top:7.47in; font:400 10.5pt/1 'EB Garamond'; letter-spacing:.06em; }}
    .ins {{ top:7.77in; font:400 9.5pt/1 'EB Garamond'; letter-spacing:.1em; opacity:.85; }}
    .cn {{ font-family:'Noto Serif CJK SC'; font-size:.92em; }}
    .dot {{ margin:0 .7em; color:{GOLD}; }}
    .sig {{ top:16.14in; font:600 12.5pt/1 'Noto Serif CJK SC'; letter-spacing:.5em; padding-left:.5em; color:{GOLD}; }}
    .sige {{ top:16.44in; font:500 7pt/1 'EB Garamond'; letter-spacing:.38em; padding-left:.38em;
             color:{GOLD}; text-transform:uppercase; opacity:.85; }}
    """
    body = f"""
    {art()}
    <div class="t fs">FULL SCORE</div>
    <div class="t sic">Score in C · Concert Pitch</div>
    <div class="t title">{title_html(m['title'])}</div>
    <div class="t py">{e(m['title_latin'])}</div>
    <div class="t sub">{e(m['subtitle'])}</div>
    <div class="t sube">{e(m['subtitle_en'])}</div>
    <div class="credits">{cr}</div>
    <div class="t key">{keyline}</div>
    <div class="t ins">{instr}</div>
    <div class="t sig">{e(m['arranger'])}</div>
    <div class="t sige">Arrangement &amp; Music Preparation · {e(m['year'])}</div>
    """
    return lib.page(css, body, "haishui")
