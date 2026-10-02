"""deco: homage to A. M. Cassandre and 1930s Shanghai / Hollywood Art Deco.

One idea: 「我的祖国和我，像海和浪花一朵」.  A vast jade sea (the motherland)
drawn as Deco wave rows - stacked scallops inlaid with fine gold arcs that
grow from a hair's breadth at the horizon to broad swells at the viewer's
feet.  In the middle the sea rises into one symmetrical breaking crest: two
waves curl towards each other like a pair of wrought-iron volutes (Bund
ironwork, Brandt's grilles), and from the point where they meet a single
fan of golden spray bursts upwards - 浪花一朵, me - a Chrysler-crown fan of
lancets tipped with drops, pivoting on a small gold shell.  Under it the
swell pulses in nested arcs (母亲的脉搏).  A restrained radiance of fine gold
rays fans out behind it, wide along the horizon and short under the title.  浪是那海的赤子，海是那浪的依托: the spray is made of the sea.
Ink-navy ground, metallic gold, cream, jade and one crimson nameplate: the
palette of the Bund's Deco lobbies.  Title in Republican-era display
lettering (ZCOOL XiaoWei) with a metallic gold gradient.

PDF note: Chromium/Skia leaks a fill alpha into later gradient fills, so
nothing here uses fill-/stroke-opacity next to a gradient: translucent
colours are pre-mixed instead (gradient stop-opacity is fine).
"""
import math

import lib

U = 100  # SVG user units per inch
W, H = 11 * U, 17 * U
CX = W / 2

NAVY = "#0D1828"
NAVY_2 = "#132339"
SKY_LO = "#2A4A6C"
JADE = "#2C6A68"
JADE_DK = "#173C47"
SEA_DEEP = "#0B1A27"
GOLD = lib.GOLD
GOLD_LT = "#F0D896"
GOLD_MD = "#E2C47C"
GOLD_DK = "#8A6828"
CREAM = "#F2E6CC"
CREAM_2 = "#D8CBB0"
CRIMSON = "#7A1D25"

Y_H = 738      # horizon (the crests meet on it)
S = 1.16       # scale of the crest and its spray
Y_B = 1052     # bottom of the sea
IN = 50        # inner frame inset
SPRAY = (CX, Y_H)   # where the two crests meet and the spray springs


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    t = min(max(t, 0), 1)
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def P(pts, close=False):
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in pts) + (" Z" if close else "")


# ------------------------------------------------------------------ defs
def defs():
    return f"""
<defs>
  <linearGradient id="goldV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{GOLD_LT}"/>
    <stop offset=".5" stop-color="{GOLD_MD}"/>
    <stop offset="1" stop-color="{GOLD}"/>
  </linearGradient>
  <linearGradient id="goldH" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{GOLD_DK}"/>
    <stop offset=".3" stop-color="{GOLD}"/>
    <stop offset=".5" stop-color="{GOLD_LT}"/>
    <stop offset=".7" stop-color="{GOLD}"/>
    <stop offset="1" stop-color="{GOLD_DK}"/>
  </linearGradient>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{NAVY}"/>
    <stop offset=".42" stop-color="{NAVY_2}"/>
    <stop offset="1" stop-color="{SKY_LO}"/>
  </linearGradient>
  <radialGradient id="glow" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="{GOLD_LT}" stop-opacity=".2"/>
    <stop offset=".5" stop-color="{GOLD}" stop-opacity=".07"/>
    <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="inner"><path d="{stepped_rect(IN, IN, W - IN, H - IN, 12, 3)}"/></clipPath>
  <clipPath id="skyc"><rect width="{W}" height="{Y_H}"/></clipPath>
</defs>"""


# ------------------------------------------------------------------ frame
def stepped_rect(x0, y0, x1, y1, s, n=3):
    """Rectangle whose four corners step inwards n times (Deco ziggurat)."""
    p = [(x0 + n * s, y0), (x1 - n * s, y0)]
    for i in range(n):
        p += [(x1 - (n - i) * s, y0 + (i + 1) * s), (x1 - (n - i - 1) * s, y0 + (i + 1) * s)]
    p += [(x1, y1 - n * s)]
    for i in range(n):
        p += [(x1 - (i + 1) * s, y1 - (n - i) * s), (x1 - (i + 1) * s, y1 - (n - i - 1) * s)]
    p += [(x0 + n * s, y1)]
    for i in range(n):
        p += [(x0 + (n - i) * s, y1 - (i + 1) * s), (x0 + (n - i - 1) * s, y1 - (i + 1) * s)]
    p += [(x0, y0 + n * s)]
    for i in range(n):
        p += [(x0 + (i + 1) * s, y0 + (n - i) * s), (x0 + (i + 1) * s, y0 + (n - i - 1) * s)]
    q = [p[0]]
    for pt in p[1:]:
        if pt != q[-1]:
            q.append(pt)
    return P(q, True)


def frame():
    o = 36
    return (f'<rect x="{o}" y="{o}" width="{W - 2 * o}" height="{H - 2 * o}" fill="none" '
            f'stroke="{GOLD}" stroke-width="2.4"/>'
            f'<path d="{stepped_rect(IN, IN, W - IN, H - IN, 12, 3)}" fill="none" '
            f'stroke="{GOLD}" stroke-width=".8"/>')


# ------------------------------------------------------------------ sea rows
def sea_rows(n=16, q=1.15):
    """Rows from the horizon to the foot of the sea, each q times deeper than
    the one behind it: (k, depth 0..1, baseline y, row step, scallop width)."""
    steps = [q ** k for k in range(n)]
    s0 = (Y_B + 18 - Y_H) / sum(steps)
    rows, y = [], Y_H
    for k in range(n):
        s = s0 * steps[k]
        y += s
        rows.append((k, (k + 1) / n, y, s, 3.3 * s))
    return rows


def scallops(y, s, w, odd):
    """x positions of the scallops of one row (one centred on the axis, or a
    cusp on the axis for odd rows)."""
    x = CX - (w / 2 if not odd else 0)
    while x > IN - w:
        x -= w
    xs = []
    while x < W - IN + w:
        xs.append(x)
        x += w
    return xs


def row(k, t, y, s, w):
    """One band of Deco scallops: humps of width w rising 1.15 s above the
    baseline, filled jade-to-deep, edged and inlaid with gold arcs that dim
    with distance and brighten on the light path below the spray."""
    h = .95 * s
    xs = scallops(y, s, w, k % 2)
    top = []
    for x0 in xs:
        for j in range(17):
            a = math.pi * j / 16
            top.append((x0 + w / 2 - w / 2 * math.cos(a), y - h * math.sin(a)))
    fill_top = mix(JADE, "#3C7C78", .35 * (1 - t)) if k % 2 == 0 else mix(JADE, JADE_DK, .25)
    out = [f'<linearGradient id="r{k}" gradientUnits="userSpaceOnUse" x1="0" y1="{y - h:.1f}" '
           f'x2="0" y2="{y + 1.1 * s:.1f}"><stop offset="0" stop-color="{fill_top}"/>'
           f'<stop offset=".55" stop-color="{mix(JADE_DK, SEA_DEEP, .2)}"/>'
           f'<stop offset="1" stop-color="{SEA_DEEP}"/></linearGradient>',
           f'<path d="{P(top + [(W, H), (0, H)], True)}" fill="url(#r{k})"/>']
    base_line = mix(JADE_DK, GOLD, .2 + .34 * t)
    for x0 in xs:
        xc = x0 + w / 2
        d = min(abs(xc - CX) / (150 + 260 * t), 1)   # distance from the light path
        glint = (1 - d) ** 1.4 * (.5 + .5 * t)
        edge = mix(base_line, GOLD_LT, glint)
        sw = .35 + 1.25 * t
        rings = [(1.0, edge, sw)]
        if w > 34:
            rings.append((.68, mix(mix(JADE_DK, GOLD, .15 + .28 * t), GOLD_LT, glint * .8), sw * .7))
        if w > 70:
            rings.append((.38, mix(mix(JADE_DK, GOLD, .1 + .24 * t), GOLD_LT, glint * .6), sw * .6))
        for f, col, wd in rings:
            rx, ry = w / 2 * f, h * f
            out.append(f'<path d="M{xc - rx:.2f},{y:.2f} A{rx:.2f},{ry:.2f} 0 0 1 '
                       f'{xc + rx:.2f},{y:.2f}" fill="none" stroke="{col}" '
                       f'stroke-width="{wd:.2f}"/>')
    return "".join(out)


# ------------------------------------------------------------------ the crest
def ribbon(cs, width_at):
    """Outline of a ribbon of variable width around centreline points."""
    n = len(cs) - 1
    left, right = [], []
    for k, (x, y) in enumerate(cs):
        xa, ya = cs[max(k - 1, 0)]
        xb, yb = cs[min(k + 1, n)]
        L = math.hypot(xb - xa, yb - ya) or 1
        nx, ny = -(yb - ya) / L, (xb - xa) / L
        w = width_at(k / n) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left, right


def bez(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        mt = 1 - t
        out.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                    mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
    return out


# the left crest, in page units; the right one is its mirror
EYE = (CX - 96 * S, Y_H - 74 * S)   # eye of the curl
R_A, B_SP = 74 * S, .21         # curl radius where the back joins it, spiral rate
PH_END = 668                # where the curl ends (deg)
FOOT = (CX - 590, Y_H + 108)      # where the back of the wave rises from the sea
TROUGH = (CX, Y_H)          # where the two faces meet (the spray springs here)
N_TAIL, N_CURL = 90, 200


def spiral(ph0, ph1, n, r_a=R_A):
    pts = []
    for i in range(n + 1):
        ph = ph0 + (ph1 - ph0) * i / n
        r = r_a * math.exp(-B_SP * math.radians(ph - 180))
        a = math.radians(ph)
        pts.append((EYE[0] + r * math.cos(a), EYE[1] + r * math.sin(a)))
    return pts


def crest_line():
    """Centreline of the left crest: a long rising back (cubic) flowing
    tangentially into a logarithmic curl round the eye; returns the points
    and the index where the curl begins."""
    A = (EYE[0] - R_A, EYE[1])
    tang = (B_SP, -1)                     # tangent of the spiral at 180 deg
    tail = bez(FOOT, (FOOT[0] + 270, FOOT[1] - 12),
               (A[0] - tang[0] * 95, A[1] - tang[1] * 95), A, N_TAIL)
    curl = spiral(180, PH_END, N_CURL)
    return tail + curl[1:], len(tail) - 1


def crest_width(t):
    return S * (3 + 44 * (1 - t) ** 1.1)


def mirror(pts, side):
    return pts if side < 0 else [(2 * CX - x, y) for x, y in pts]


def crest():
    """浪: two waves rising from the sea and curling towards each other,
    Deco volutes in jade inlaid with gold lines; spray bursts between them."""
    cs, ia = crest_line()
    n = len(cs) - 1
    inner, outer = ribbon(cs, crest_width)     # ribbon's left = inner side here
    k_lip = ia + round(N_CURL * 180 / (PH_END - 180))   # the curl at 360 deg
    lip = outer[k_lip]
    face = bez(lip, (lip[0] + 6 * S, lip[1] + 36 * S), (TROUGH[0] - 26 * S, TROUGH[1] - 4), TROUGH, 30)
    half = outer[:k_lip + 1] + face
    body = half + mirror(half, 1)[::-1]
    out = [f'<linearGradient id="cb" gradientUnits="userSpaceOnUse" x1="0" y1="{EYE[1] - R_A}" '
           f'x2="0" y2="{FOOT[1]}"><stop offset="0" stop-color="#3A7F7A"/>'
           f'<stop offset=".5" stop-color="{JADE}"/><stop offset="1" stop-color="{JADE_DK}"/>'
           f'</linearGradient>',
           f'<linearGradient id="cr" gradientUnits="userSpaceOnUse" x1="0" y1="{EYE[1] - R_A}" '
           f'x2="0" y2="{FOOT[1]}"><stop offset="0" stop-color="#4F968F"/>'
           f'<stop offset=".5" stop-color="#37786F"/><stop offset="1" stop-color="{JADE}"/>'
           f'</linearGradient>',
           f'<path d="{P(body + [(2 * CX - FOOT[0], 900), (FOOT[0], 900)], True)}" fill="url(#cb)"/>',
           f'<clipPath id="bodyc"><path d="{P(body + [(2 * CX - FOOT[0], 900), (FOOT[0], 900)], True)}"/>'
           f'</clipPath>']
    # 你用你那母亲的脉搏: the swell under the spray pulses in nested arcs
    rip = []
    for j in range(7):
        rx, ry = (70 + 52 * j) * S, (26 + 17 * j) * S
        y0 = TROUGH[1] + 62 * S + 6 * j
        rip.append(f'<path d="M{CX - rx:.1f},{y0:.1f} A{rx:.1f},{ry:.1f} 0 0 1 {CX + rx:.1f},{y0:.1f}" '
                   f'fill="none" stroke="{mix(JADE, GOLD, .55 - .05 * j)}" stroke-width=".7"/>')
    out.append(f'<g clip-path="url(#bodyc)">{"".join(rip)}</g>')
    for side in (-1, 1):
        I, O = mirror(inner, side), mirror(outer, side)
        # contour lines in the body, parallel to the back of the wave
        for j, dy in enumerate((14, 27, 39, 50, 60)):
            ln = [(x, y + dy) for x, y in I[int(n * .02):ia + 12]]
            out.append(f'<path d="{P(ln)}" fill="none" stroke="{mix(JADE_DK, GOLD, .62 - .09 * j)}" '
                       f'stroke-width=".6"/>')
        # the scroll itself, a shade lighter than the body
        out.append(f'<path d="{P(O + I[::-1], True)}" fill="url(#cr)"/>')
        # gold inlay lines running its whole length, like Deco ironwork
        for f, sw, c, t1 in ((.0, 1.1, GOLD_LT, .975), (-.3, .6, GOLD, .9), (.3, .6, GOLD, .9)):
            ln = [(I[k][0] + (O[k][0] - I[k][0]) * (.5 + f), I[k][1] + (O[k][1] - I[k][1]) * (.5 + f))
                  for k in range(n + 1) if .01 < k / n < t1]
            out.append(f'<path d="{P(ln)}" fill="none" stroke="{c}" stroke-width="{sw}" '
                       f'stroke-linecap="round"/>')
        out.append(f'<path d="{P(O)}" fill="none" stroke="{GOLD_LT}" stroke-width="1.6"/>')
        out.append(f'<path d="{P(I)}" fill="none" stroke="{GOLD}" stroke-width=".7"/>')
        out.append(f'<path d="{P(mirror(face, side))}" fill="none" stroke="{GOLD}" stroke-width=".8"/>')
    return "".join(out)


def lancet(o, ang, r_in, r_out, wmax):
    """One plume of spray: a pointed lancet radiating from o."""
    a = math.radians(ang)
    ux, uy = math.sin(a), -math.cos(a)
    nx, ny = -uy, ux
    n = 40
    left, right, mid = [], [], []
    for i in range(n + 1):
        t = i / n
        r = r_in + (r_out - r_in) * t
        w = wmax / 2 * math.sin(math.pi * t ** .75) ** .85
        x, y = o[0] + ux * r, o[1] + uy * r
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
        if .12 < t < .8:
            mid.append((x, y))
    return (f'<path d="{P(left + right[::-1], True)}" fill="url(#goldV)"/>'
            f'<path d="{P(mid)}" fill="none" stroke="{GOLD_DK}" stroke-width=".7"/>')


def spray():
    """浪花一朵: a Deco fan of spray - nine lancets (the tallest on the axis),
    fine jets between them, each tipped with drops."""
    o = SPRAY
    out = []
    plumes = [(a, L * S, wd * S) for a, L, wd in
              ((0, 246, 15), (11, 233, 13.5), (22, 214, 12.5), (33, 206, 11.5), (45, 160, 10.5),
               (58, 124, 9.5))]
    jets = [(a, L * S) for a, L in
            ((5.5, 238), (16.5, 222), (27.5, 202))]      # the rest hide behind the crests
    for a, L in jets:
        for sd in (-1, 1):
            ang = math.radians(sd * a)
            ux, uy = math.sin(ang), -math.cos(ang)
            out.append(f'<line x1="{o[0] + ux * 80 * S:.1f}" y1="{o[1] + uy * 80 * S:.1f}" '
                       f'x2="{o[0] + ux * L:.1f}" y2="{o[1] + uy * L:.1f}" stroke="{GOLD}" '
                       f'stroke-width=".7"/>')
            out.append(f'<circle cx="{o[0] + ux * (L + 7 * S):.1f}" cy="{o[1] + uy * (L + 7 * S):.1f}" '
                       f'r="{1.8 * S:.2f}" fill="{GOLD_LT}"/>')
    for a, L, wd in plumes:
        for sd in ((1,) if a == 0 else (-1, 1)):
            out.append(lancet(o, sd * a, 8, L, wd))
            ang = math.radians(sd * a)
            ux, uy = math.sin(ang), -math.cos(ang)
            for d, r in ((12 * S, 3.4 * S), (23 * S, 2.4 * S), (32 * S, 1.6 * S))[:3 if a < 30 else 2 if a < 40 else 0]:
                out.append(f'<circle cx="{o[0] + ux * (L + d):.1f}" '
                           f'cy="{o[1] + uy * (L + d):.1f}" r="{r}" fill="{GOLD_LT}"/>')
    # the fan's pivot, where the two waves meet
    r = 15 * S
    out.append(f'<path d="M{o[0] - r:.1f},{o[1]} A{r:.1f},{r:.1f} 0 0 1 {o[0] + r:.1f},{o[1]} Z" '
               f'fill="{GOLD_MD}" stroke="{GOLD_LT}" stroke-width=".8"/>')
    for i in range(-3, 4):
        a = math.radians(i * 24)
        out.append(f'<line x1="{o[0]}" y1="{o[1]}" x2="{o[0] + math.sin(a) * r * .8:.1f}" '
                   f'y2="{o[1] - math.cos(a) * r * .8:.1f}" stroke="{GOLD_DK}" stroke-width=".6"/>')
    return "".join(out)


def rays():
    """Restrained Deco radiance behind the spray: fine rays, long and short
    alternately, between two ellipses - wide along the horizon, short
    under the title, so the type above stays clean - fading out."""
    cx, cy = SPRAY
    a0, b0 = 330, 300              # start ellipse (clears the fan of spray)
    a1, b1 = 610, 352              # end ellipse (stays under the pinyin)
    k = b1 / a1

    def er(a, ax, by):
        return 1 / math.hypot(math.sin(a) / ax, math.cos(a) / by)
    out = [f'<radialGradient id="rayg" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{a1}" '
           f'gradientTransform="matrix(1 0 0 {k:.4f} 0 {cy * (1 - k):.2f})">'
           f'<stop offset=".5" stop-color="{GOLD}" stop-opacity=".66"/>'
           f'<stop offset=".8" stop-color="{GOLD}" stop-opacity=".3"/>'
           f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></radialGradient>']
    d = []
    for i in range(-24, 25):
        a = math.radians(i * 3.5)
        r0 = er(a, a0, b0)
        r1 = er(a, a1, b1)
        r = r1 if i % 2 == 0 else r0 + (r1 - r0) * .62
        d.append(f"M{cx + math.sin(a) * r0:.1f},{cy - math.cos(a) * r0:.1f} "
                 f"L{cx + math.sin(a) * r:.1f},{cy - math.cos(a) * r:.1f}")
    out.append(f'<path d="{" ".join(d)}" fill="none" stroke="url(#rayg)" stroke-width=".75"/>')
    return "".join(out)


def art():
    rows = sea_rows()
    sky = f'<rect x="0" y="0" width="{W}" height="{Y_H + 1}" fill="url(#sky)"/>'
    glow = f'<ellipse cx="{CX}" cy="{SPRAY[1] - 150}" rx="470" ry="360" fill="url(#glow)"/>'
    horizon = (f'<line x1="0" y1="{Y_H}" x2="{W}" y2="{Y_H}" stroke="{mix(SKY_LO, GOLD_LT, .75)}" '
               f'stroke-width=".7"/>')
    far = "".join(row(*r) for r in rows if r[2] < Y_H + 62)
    near = "".join(row(*r) for r in rows if r[2] >= Y_H + 62)
    y = Y_B + 22
    base = (f'<rect x="0" y="{y}" width="{W}" height="{H - y}" fill="{NAVY}"/>'
            f'<rect x="0" y="{y - 1}" width="{W}" height="2.2" fill="url(#goldH)"/>'
            f'<rect x="0" y="{y + 6}" width="{W}" height=".8" fill="{GOLD}"/>')
    return (f'<svg class="art" viewBox="0 0 {W} {H}" width="11in" height="17in">{defs()}'
            f'<rect width="{W}" height="{H}" fill="{NAVY}"/>'
            f'<g clip-path="url(#inner)">{sky}{glow}'
            f'<g clip-path="url(#skyc)">{rays()}</g>'
            f'<rect x="0" y="{Y_H}" width="{W}" height="{H - Y_H}" fill="{JADE_DK}"/>'
            f'{far}{horizon}{spray()}{crest()}{near}{base}{lower()}</g>'
            f'{frame()}</svg>')


def lower():
    """Deco ornament for the text half: fluted pilasters crowned with small
    fans (the spray again), streamline rules beside FULL SCORE, a stepped
    pendant under the sea, fine dividers and a stepped crimson nameplate."""
    out = []
    y0, y1 = Y_B + 96, 1606
    for x in (112, W - 112):
        for d in (-5, 0, 5):
            out.append(f'<line x1="{x + d}" y1="{y0}" x2="{x + d}" y2="{y1 - 6}" stroke="{GOLD}" '
                       f'stroke-width="{.9 if d == 0 else .5}"/>')
        # fan capital
        for i in range(-3, 4):
            a = math.radians(i * 22)
            out.append(f'<line x1="{x}" y1="{y0}" x2="{x + math.sin(a) * 22:.1f}" '
                       f'y2="{y0 - math.cos(a) * 22:.1f}" stroke="{GOLD}" stroke-width=".6"/>')
        out.append(f'<path d="M{x - 24},{y0} A24,24 0 0 1 {x + 24},{y0}" fill="none" '
                   f'stroke="{GOLD}" stroke-width=".9"/>')
        out.append(f'<rect x="{x - 13}" y="{y0}" width="26" height="2.6" fill="{GOLD}"/>')
        # stepped base
        for k, wd in enumerate((6, 14, 22)):
            out.append(f'<rect x="{x - wd / 2}" y="{y1 - 9 + k * 4.5}" width="{wd}" height="2.6" '
                       f'fill="{GOLD}"/>')
    # streamline rules either side of FULL SCORE (centre line at y=106)
    for sgn in (-1, 1):
        for k, (L, yy) in enumerate(((150, 99), (115, 106), (80, 113))):
            x0 = CX + sgn * 205
            out.append(f'<line x1="{x0:.1f}" y1="{yy}" x2="{x0 + sgn * L:.1f}" y2="{yy}" '
                       f'stroke="{GOLD}" stroke-width="{1.1 if k == 1 else .6}"/>')
    # stepped pendant hanging from the sea's gold rule
    yp = Y_B + 29
    for k, wd in enumerate((64, 40, 18)):
        out.append(f'<rect x="{CX - wd / 2}" y="{yp + k * 5.5}" width="{wd}" height="3" fill="{GOLD}"/>')
    out.append(f'<rect x="{CX - 3.2}" y="{yp + 18.5}" width="6.4" height="6.4" fill="{GOLD_LT}" '
               f'transform="rotate(45 {CX} {yp + 21.7})"/>')
    # dividers: rule - diamond - rule
    for yd in (1212, 1434):
        for sgn in (-1, 1):
            out.append(f'<line x1="{CX + sgn * 10}" y1="{yd}" x2="{CX + sgn * 92}" y2="{yd}" '
                       f'stroke="{GOLD}" stroke-width=".7"/>')
        out.append(f'<rect x="{CX - 2.6}" y="{yd - 2.6}" width="5.2" height="5.2" fill="{GOLD}" '
                   f'transform="rotate(45 {CX} {yd})"/>')
    # nameplate
    pw, ph, py = 312, 52, 1541
    out.append(f'<path d="{stepped_rect(CX - pw / 2, py, CX + pw / 2, py + ph, 5, 2)}" '
               f'fill="{CRIMSON}" stroke="{GOLD}" stroke-width="1.4"/>')
    out.append(f'<path d="{stepped_rect(CX - pw / 2 - 7, py - 7, CX + pw / 2 + 7, py + ph + 7, 6, 2)}" '
               f'fill="none" stroke="{GOLD}" stroke-width=".6"/>')
    return "".join(out)


# ------------------------------------------------------------------ type
CSS = f"""
.page {{ background: {NAVY}; color: {CREAM}; }}
.art {{ position: absolute; left: 0; top: 0; }}
.c {{ position: absolute; left: 0; width: 11in; text-align: center; white-space: nowrap; }}
.fs {{ font-family: 'Cinzel', serif; font-weight: 600; font-size: 16pt; letter-spacing: .6em;
       padding-left: .6em; color: {CREAM}; }}
.sic {{ font-family: 'Josefin Sans', sans-serif; font-weight: 500; font-size: 8pt;
        letter-spacing: .45em; padding-left: .45em; color: {GOLD}; text-transform: uppercase; }}
.ttl {{ position: absolute; left: 0; top: 0; }}
.py {{ font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 14pt;
       letter-spacing: .6em; padding-left: .6em; text-transform: uppercase; color: {CREAM}; }}
.sub {{ font-family: 'Noto Serif CJK SC', serif; font-weight: 500; font-size: 16pt;
        letter-spacing: .22em; padding-left: .22em; color: {CREAM}; }}
.suben {{ font-family: 'Cormorant Garamond', serif; font-style: italic; font-weight: 500;
          font-size: 14pt; color: {GOLD_MD}; letter-spacing: .02em; }}
.cr {{ position: absolute; left: 0; width: 11in; height: .3in; }}
.cr .l {{ position: absolute; right: 5.72in; top: 0; text-align: right; white-space: nowrap; }}
.cr .r {{ position: absolute; left: 5.72in; top: 0; white-space: nowrap; }}
.cr .en {{ font-family: 'Josefin Sans', sans-serif; font-weight: 500; font-size: 7.6pt;
           letter-spacing: .3em; color: {GOLD}; text-transform: uppercase; margin-right: .2in;
           position: relative; top: -2pt; }}
.cr .zh {{ font-family: 'Noto Serif CJK SC', serif; font-weight: 500; font-size: 12pt;
           color: {CREAM_2}; letter-spacing: .1em; }}
.cr .nm {{ font-family: 'Noto Serif CJK SC', serif; font-weight: 600; font-size: 13.5pt;
           color: {GOLD_LT}; letter-spacing: .16em; position: relative; top: -1.6pt; }}
.cr .dm {{ position: absolute; left: 5.5in; top: .085in; width: .06in; height: .06in;
           margin-left: -.03in; background: {GOLD}; transform: rotate(45deg); }}
.info {{ font-family: 'Cormorant Garamond', serif; font-weight: 500; font-size: 14pt;
         color: {CREAM}; letter-spacing: .06em; }}
.info .zh {{ font-family: 'Noto Serif CJK SC', serif; font-size: 10.5pt; letter-spacing: .1em; }}
.dot {{ color: {GOLD}; padding: 0 .6em; }}
.inst {{ font-family: 'Josefin Sans', sans-serif; font-weight: 500; font-size: 8pt;
         letter-spacing: .28em; padding-left: .28em; text-transform: uppercase; color: {GOLD}; }}
.inst .zh {{ font-family: 'Noto Serif CJK SC', serif; font-weight: 500; font-size: 10pt;
             letter-spacing: .14em; color: {CREAM_2}; text-transform: none; }}
.plate {{ font-family: 'ZCOOL XiaoWei', 'Noto Serif CJK SC', serif; font-size: 19pt;
          letter-spacing: .5em; padding-left: .5em; color: {GOLD_LT}; line-height: 1; }}
.arr {{ font-family: 'Josefin Sans', sans-serif; font-weight: 500; font-size: 7.4pt;
        letter-spacing: .42em; padding-left: .42em; color: {GOLD}; text-transform: uppercase; }}
"""


# optical kerning of the display title (em at the title size), measured
# from the rendered ink of ZCOOL XiaoWei; pairs not listed are left alone
KERN = {("我", "和"): -.03, ("我", "的"): -.035, ("的", "祖"): -.048, ("祖", "国"): -.055}
T_SIZE = 145          # title size in SVG units (= 104.4 pt)
T_TRACK = .03         # tracking, em


def title_svg(title):
    """The display title as one SVG text line (real, extractable text) so it
    can carry a metallic gold gradient; per-pair kerning via dx."""
    spans = []
    for i, ch in enumerate(title):
        k = KERN.get((title[i - 1], ch), 0) if i else 0
        dx = f' dx="{k * T_SIZE:.1f}"' if k else ""
        spans.append(f'<tspan{dx}>{lib.e(ch)}</tspan>')
    return (f'<svg class="ttl" viewBox="0 0 {W} 420" width="11in" height="4.2in">'
            f'<defs><linearGradient id="tg" gradientUnits="userSpaceOnUse" x1="0" y1="220" '
            f'x2="0" y2="345"><stop offset="0" stop-color="#F5E3AE"/>'
            f'<stop offset=".5" stop-color="{GOLD_MD}"/><stop offset="1" stop-color="#B98F42"/>'
            f'</linearGradient></defs>'
            f'<text x="{CX + 5.5 + T_SIZE * T_TRACK / 2:.1f}" y="325" text-anchor="middle" '
            f'font-family="ZCOOL XiaoWei" font-size="{T_SIZE}" letter-spacing="{T_SIZE * T_TRACK:.1f}" '
            f'fill="url(#tg)">{"".join(spans)}</text></svg>')


def render(m):
    rows = lib.credit_rows(m)
    b = [art()]
    b.append('<div class="c fs" style="top:.92in">FULL SCORE</div>')
    b.append('<div class="c sic" style="top:1.3in">Score in C · Concert Pitch</div>')
    b.append(title_svg(m["title"]))
    b.append(f'<div class="c py" style="top:3.52in">{lib.e(m["title_latin"])}</div>')
    b.append(f'<div class="c sub" style="top:11.3in">{lib.e(m["subtitle"])}</div>')
    b.append(f'<div class="c suben" style="top:11.68in">{lib.e(m["subtitle_en"])}</div>')
    y = 12.36
    for zh, en, name in rows:
        b.append(f'<div class="cr" style="top:{y:.2f}in"><div class="l"><span class="en">'
                 f'{lib.e(en)}</span><span class="zh">{lib.e(zh)}</span></div>'
                 f'<div class="dm"></div><div class="r"><span class="nm">{lib.e(name)}'
                 f'</span></div></div>')
        y += 0.37
    parts = [p.strip() for p in m["key"].split("·")] + [m["tempo"], m["duration"]]
    info = '<span class="dot">·</span>'.join(
        (f'<span class="zh">{lib.sym(p)}</span>' if any(ord(ch) > 0x2E80 for ch in p)
         else lib.sym(p)) for p in parts)
    b.append(f'<div class="c info" style="top:14.5in">{info}</div>')
    inst = '<span class="dot" style="padding:0 1.2em">·</span>'.join(
        f'{lib.e(en)} <span class="zh">{lib.e(zh)}</span>' for en, zh in m["instrumentation"])
    b.append(f'<div class="c inst" style="top:14.88in">{inst}</div>')
    b.append(f'<div class="c plate" style="top:15.52in">{lib.e(m["arranger"])}</div>')
    b.append(f'<div class="c arr" style="top:16.17in">Arrangement &amp; Music Preparation · '
             f'{lib.e(m["year"])}</div>')
    return lib.page(CSS, "".join(b), "deco")
