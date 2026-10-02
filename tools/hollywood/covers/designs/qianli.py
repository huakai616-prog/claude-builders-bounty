"""qianli -- homage to 王希孟《千里江山图》 (1113): Song-dynasty blue-green
landscape re-drawn as modern graphic art, mounted as a hanging scroll.

The page is the mount (deep azurite silk; the 天杆 and two slim 惊燕 on the
天头; the credits on the 地头).  The 画心 is aged silk with a 青绿 landscape
built like the handscroll's: tall steep peaks in crag clusters, flat-topped
terraces and stepped shoulders, long ridges sloping into the river, valleys
full of mist; 石青 summits over 石绿 slopes over 赭石 feet, short 披麻皴
bundles that run down the slopes, 泥金 contours, a hamlet on a terrace with
one thread of smoke, a sail, and rippled water (碧浪清波) whose ripples come
in groups of three (6/8).  One small gold spray in the water is the 「我」 of
the song; the thousand li of mountains and rivers is the 祖国.
"""
import math
import random

import lib

# ---- palette ---------------------------------------------------------------
MOUNT = "#1C3046"      # 天头/地头: deep azurite-indigo silk
MOUNT_HI = "#233C56"   # damask highlight
ROD = "#132232"        # 天杆
GESHUI = "#CDB98A"     # 隔水 band: pale gold silk
GESHUI_D = "#B19B69"
SILK_TOP = "#D9C59C"   # 绢色 (aged silk), top of the 画心
SILK_MID = "#E7D9BA"
MIST = "#F0E7D1"       # 留白 mist
AZ_D = "#163D63"       # 石青 deep (azurite)
AZ_M = "#285F88"       # 石青 mid
AZ_DD = "#0F2C49"      # 皴 ink on the blue
MAL_D = "#2B7564"      # 石绿 deep (malachite)
MAL_M = "#4E977F"      # 石绿 mid
MAL_L = "#93BE9F"      # 三绿
MAL_DD = "#1B4E42"     # 皴 ink on the green
OCHRE = "#B3844F"      # 赭石
OCHRE_L = "#D3B37F"    # 赭石 wash
OCHRE_DD = "#7A5530"
WALL = "#EFE6D2"
AGED = "#7A5A2E"       # age-darkening of the silk at the edges
GOLD = "#C9A04A"       # 泥金
GOLD_D = "#A9853A"
INK = "#1A2E44"        # title ink (azurite black)
CINNABAR = lib.CINNABAR
PALE = "#EDE2C8"       # light text on the mount

# ---- geometry (SVG units: 0.01 in) -------------------------------------------
PW, PH = 1100, 1700
SIDE = 80              # mount (边) at the sides
SG_TOP = 212           # 天头 ends, 上隔水 begins
X0, Y0 = SIDE, 232     # 画心 origin
W = PW - 2 * SIDE      # 画心 width
H = 990                # 画心 height
XG_BOT = Y0 + H + 14   # 下隔水 ends, 地头 begins
JINGYAN = "#253F5A"    # 惊燕 silk (a shade off the mount)


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def f1(v):
    return f"{v:.1f}"


def path(pts):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y, *_ in pts)


# ---- drawing the ridges --------------------------------------------------------
def _cr(p0, p1, p2, p3, t):
    """centripetal Catmull-Rom between p1 and p2"""
    def tj(ti, a, b):
        return ti + max(math.dist(a, b), 1e-3) ** 0.5
    t0 = 0.0
    t1 = tj(t0, p0, p1)
    t2 = tj(t1, p1, p2)
    t3 = tj(t2, p2, p3)
    tt = t1 + (t2 - t1) * t

    def lerp(a, b, ta, tb):
        k = (tt - ta) / (tb - ta)
        return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
    a1, a2, a3 = lerp(p0, p1, t0, t1), lerp(p1, p2, t1, t2), lerp(p2, p3, t2, t3)
    b1, b2 = lerp(a1, a2, t0, t2), lerp(a2, a3, t1, t3)
    return lerp(b1, b2, t1, t2)


def spline(keys, step=2.0):
    P = [(2 * keys[0][0] - keys[1][0], 2 * keys[0][1] - keys[1][1])] + list(keys) \
        + [(2 * keys[-1][0] - keys[-2][0], 2 * keys[-1][1] - keys[-2][1])]
    out = []
    for i in range(1, len(P) - 2):
        n = max(2, int(math.dist(P[i], P[i + 1]) / step))
        out += [_cr(P[i - 1], P[i], P[i + 1], P[i + 2], k / n) for k in range(n)]
    out.append(keys[-1])
    return out


def knobby(pts, rng, base, knobs, amp=(1.2, 3.4)):
    """Small rounded knobs (矾头) along the upper ridge, and a faint tremor of
    the brush, pushed outward along the normal."""
    top = min(y for _, y in pts)
    s = [0.0]
    for a, b in zip(pts, pts[1:]):
        s.append(s[-1] + math.dist(a, b))
    S = s[-1]
    ks = [(rng.uniform(0.06, 0.94) * S, rng.uniform(*amp), rng.uniform(3, 7.5)) for _ in range(knobs)]
    ph1, ph2 = rng.uniform(0, 6.3), rng.uniform(0, 6.3)
    out = []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tx, ty) or 1
        nx, ny = ty / ln, -tx / ln
        hw = max(0.0, min(1.0, (base - y) / max(1, base - top) * 1.7 - 0.25))
        d = sum(A * math.exp(-((s[i] - c) / sg) ** 2) for c, A, sg in ks)
        d += 0.45 * math.sin(s[i] / 9 + ph1) + 0.3 * math.sin(s[i] / 4.3 + ph2)
        out.append((x + nx * d * hw, y + ny * d * hw))
    return out


def ribbon(pts, widths):
    """A filled, tapering brush ribbon along a centre line."""
    left, right = [], []
    for i, ((x, y), w) in enumerate(zip(pts, widths)):
        x0, y0 = pts[max(i - 1, 0)]
        x1, y1 = pts[min(i + 1, len(pts) - 1)]
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        left.append((x + nx * w / 2, y + ny * w / 2))
        right.append((x - nx * w / 2, y - ny * w / 2))
    poly = left + right[::-1]
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in poly) + "Z"


def stroke_shape(x, y, dx, dy, L, w, bend):
    """One 皴 stroke: a short, slightly bowed line, pressed at the start and
    trailing off (钉头鼠尾)."""
    nx, ny = -dy, dx
    pts, ws = [], []
    n = 9
    for k in range(n + 1):
        t = k / n
        b = bend * math.sin(math.pi * t)
        pts.append((x + dx * L * t + nx * b, y + dy * L * t + ny * b))
        ws.append(w * (min(1.0, t * 5 + 0.25) * (1 - t) ** 0.7) + 0.08)
    return ribbon(pts, ws)


class Art:
    def __init__(self, seed):
        self.defs = []
        self.body = []
        self.n = 0
        self.rng = random.Random(seed)

    def uid(self, p):
        self.n += 1
        return f"{p}{self.n}"

    def grad(self, stops, y1=0, y2=1, units=None, x=False):
        gid = self.uid("g")
        st = "".join(f'<stop offset="{o:.3f}" stop-color="{c}" stop-opacity="{a}"/>'
                     for o, c, a in stops)
        if units:
            u = (f' gradientUnits="userSpaceOnUse" x1="{y1:.1f}" x2="{y2:.1f}" y1="0" y2="0"' if x else
                 f' gradientUnits="userSpaceOnUse" x1="0" x2="0" y1="{y1:.1f}" y2="{y2:.1f}"')
        else:
            u = ' x1="0" y1="0" x2="1" y2="0"' if x else ' x1="0" y1="0" x2="0" y2="1"'
        self.defs.append(f'<linearGradient id="{gid}"{u}>{st}</linearGradient>')
        return gid

    def mist(self, cx, cy, rx, ry, op=0.95, color=MIST):
        """a soft cloud of mist (radial gradient, stays vector)"""
        gid = self.uid("m")
        self.defs.append(f'<radialGradient id="{gid}">'
                         f'<stop offset="0" stop-color="{color}" stop-opacity="{op}"/>'
                         f'<stop offset="0.55" stop-color="{color}" stop-opacity="{op * 0.7:.2f}"/>'
                         f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient>')
        self.body.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{gid})"/>')

    def rgrad(self, cx, cy, rx, ry, stops):
        gid = self.uid("r")
        st = "".join(f'<stop offset="{o:.3f}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
        self.defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="{cx:.1f}" '
                         f'cy="{cy:.1f}" r="{ry:.1f}" gradientTransform="translate({cx:.1f},{cy:.1f}) '
                         f'scale({rx / ry:.3f},1) translate({-cx:.1f},{-cy:.1f})">{st}</radialGradient>')
        return gid

    # ---- one mountain form ----------------------------------------------------
    def form(self, keys, base, kind="peak", fade=0.0, knobs=None, amp=(1.2, 3.4), cun=1.0,
             gold=1.0, drop=6, aspect=None, shade=1.0, spline_it=True):
        """A 青绿 form through hand-placed key points (left foot -> ridge ->
        right foot).  Colour grades outward from the summit (石青 -> 石绿 ->
        赭石 -> mist), so every crest is blue and every foot dissolves; 披麻皴
        strokes run down from the ridges; 泥金 contour."""
        rng = self.rng
        pts = spline(keys) if spline_it else list(keys)
        top = min(y for _, y in pts)
        h = base - top
        pts = knobby(pts, rng, base, knobs if knobs is not None else max(2, int(h / 45)), amp)
        top = min(y for _, y in pts)
        h = base - top
        sx = next(x for x, y in pts if y == top)
        body = path(pts) + f" L{f1(pts[-1][0])},{f1(base + drop)} L{f1(pts[0][0])},{f1(base + drop)} Z"
        m = lambda c: mix(c, MIST, fade)  # noqa: E731
        if kind == "peak":      # 石青 summit, 石绿 slopes, 赭石 foot
            stops = [(0, AZ_D), (.16, AZ_D), (.3, AZ_M), (.45, MAL_D), (.6, MAL_M),
                     (.7, mix(MAL_M, OCHRE_L, .55)), (.77, mix(OCHRE_L, OCHRE, .2)), (.86, mix(OCHRE_L, MIST, .5)),
                     (.94, MIST), (1, MIST)]
            asp = aspect or 0.85
        elif kind == "hill":    # 石绿 with a cap of 石青
            stops = [(0, AZ_M), (.14, mix(AZ_M, MAL_D, .5)), (.3, MAL_D), (.5, MAL_M),
                     (.62, mix(MAL_M, OCHRE_L, .55)), (.72, mix(OCHRE_L, OCHRE, .2)), (.84, mix(OCHRE_L, MIST, .5)),
                     (.94, MIST), (1, MIST)]
            asp = aspect or 1.2
        else:                   # bank: green crown on a broad 赭石 body
            stops = [(0, AZ_D), (.1, AZ_M), (.24, MAL_D), (.42, MAL_M), (.56, mix(MAL_M, OCHRE_L, .55)),
                     (.68, OCHRE_L), (.84, mix(OCHRE, OCHRE_L, .55)), (.95, mix(OCHRE_L, MIST, .3)),
                     (1, mix(OCHRE_L, MIST, .6))]
            asp = aspect or 2.6
        cy = top - 0.05 * h
        ry = base - cy
        if kind == "bank":      # a long low bank: plain vertical grading, 赭石 at the shore
            gid = self.grad([(o, m(c), 1) for o, c in stops], top, base, units=True)
        else:
            # the outermost ring melts away, so a foot dissolves into whatever
            # lies behind it (water, sky, a farther range)
            rs = [(o, m(c), 1) for o, c in stops if o < 0.94] + [(0.94, MIST, 1), (1, MIST, 0)]
            gid = self.rgrad(sx, cy, ry * asp, ry, rs)
        out = [f'<path d="{body}" fill="url(#{gid})"/>']
        cid = self.uid("c")
        self.defs.append(f'<clipPath id="{cid}"><path d="{body}"/></clipPath>')
        if cun:
            strokes = {AZ_DD: [], MAL_DD: [], OCHRE_DD: [], GOLD: []}
            s_next, s_acc = rng.uniform(3, 9), 0.0
            for i in range(1, len(pts) - 1):
                s_acc += math.dist(pts[i - 1], pts[i])
                if s_acc < s_next:
                    continue
                s_acc, s_next = 0.0, rng.uniform(6, 13) / cun
                x, y = pts[i]
                tt = (y - top) / h
                if tt > 0.6:
                    continue
                lit = x < sx
                if rng.random() < ((0.6 if lit else 0.22) / shade):
                    continue
                a, b = pts[max(i - 3, 0)], pts[min(i + 3, len(pts) - 1)]
                tx, ty = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(tx, ty) or 1
                tx, ty = tx / ln, ty / ln
                nx, ny = -ty, tx           # inward normal (left->right ridge, y down)
                if ty < 0:
                    tx, ty = -tx, -ty
                if ty < 0.35:              # flat ridge or summit: fall straight down
                    dx, dy = rng.uniform(-.22, .22), 1.0
                else:
                    dx, dy = tx * 0.62, ty * 0.62 + 0.38
                ln = math.hypot(dx, dy)
                dx, dy = dx / ln, dy / ln
                L = min(58, rng.uniform(0.05, 0.15) * h + 6)
                d0 = rng.uniform(2.5, 6.5)
                col = (GOLD if rng.random() < 0.24 else
                       AZ_DD if tt < 0.28 else MAL_DD if tt < 0.5 else OCHRE_DD)
                strokes[col].append(stroke_shape(x + nx * d0, y + ny * d0, dx, dy, L,
                                                 rng.uniform(.6, .85), rng.uniform(-1.2, 1.2)))
                if rng.random() < 0.45:
                    d1 = d0 + rng.uniform(2.6, 4)
                    strokes[col].append(stroke_shape(x + nx * d1 + dx * 3, y + ny * d1 + dy * 3, dx, dy,
                                                     L * rng.uniform(.45, .75), rng.uniform(.5, .7),
                                                     rng.uniform(-1, 1)))
            ops = {AZ_DD: .5, MAL_DD: .45, OCHRE_DD: .4, GOLD: .85}
            g = "".join(f'<path d="{" ".join(v)}" fill="{c}" fill-opacity="{ops[c] * (1 - fade):.2f}"/>'
                        for c, v in strokes.items() if v)
            out.append(f'<g clip-path="url(#{cid})">{g}</g>')
        if gold:
            fl = self.grad([(0, GOLD, gold), (0.5, GOLD, gold), (0.82, GOLD, 0), (1, GOLD, 0)],
                           top, base, units=True)
            edge = [(x, y) for x, y in pts if y < base - 0.1 * h]
            out.append(f'<path d="{path(edge)}" fill="none" stroke="url(#{fl})" stroke-width="1.05" '
                       f'stroke-linecap="round" stroke-linejoin="round"/>')
        self.body.append("".join(out))


def crag(cx, top, base, wt, wb, rng, lean=0.0, steps=2, p=1.8, skirt=1.0, hu=0.1):
    """Key points of a tall 千里江山 peak: a pointed-dome head, steep flanks
    with a step or two (shoulders), a concave skirt that flares at the foot;
    the two flanks differ and the head may lean."""
    h = base - top
    st = [(rng.uniform(0.2, 0.6), rng.uniform(6, 14) * (wb / 180 + 0.5), rng.choice((-1, 1)))
          for _ in range(steps)]
    pl, pr = p * rng.uniform(0.85, 1.15), p * rng.uniform(0.85, 1.15)
    wl, wr = wb * rng.uniform(0.85, 1.1), wb * rng.uniform(0.85, 1.1)

    def half(u, side):
        pp, ww = (pl, wl) if side < 0 else (pr, wr)
        if u < hu:
            w = wt / 2 * (max(u, 0) / hu) ** 0.62
        else:
            w = wt / 2 + (ww / 2 - wt / 2) * ((u - hu) / (1 - hu)) ** pp
        for us, ds, sd in st:          # a shoulder: a short outward step
            if sd == side:
                w += ds * (1 / (1 + math.exp(-(u - us) * 55)))
        return w * (skirt if u > 0.8 else 1)

    us = [0, .01, .03, .06, .1, .15, .21, .28, .35, .42, .5, .58, .66, .74, .82, .9, .96, 1.0]
    left = [(cx - half(u, -1) + lean * (1 - u) ** 1.5 * h * 0.12, top + u * h) for u in reversed(us)]
    right = [(cx + half(u, 1) + lean * (1 - u) ** 1.5 * h * 0.12, top + u * h) for u in us]
    return left[:-1] + [(cx + lean * h * 0.12, top - 1.0)] + right[1:]


# ---- the river ----------------------------------------------------------------------
class Water:
    """One gradient, one set of ripple rows (groups of three: 6/8); drawn in
    strips so nearer land can stand in it (碧浪清波)."""

    def __init__(self, art, rng, top):
        self.art = art
        self.top = top
        self.gid = art.grad([(0, MIST, 1), (0.22, "#DFE1CD", 1), (1, "#A9C4B9", 1)], top, H, units=True)
        self.rows = []
        y, i = top + 3, 0
        while y < H + 12:
            depth = (y - top) / (H - top)
            L = 7 + 25 * depth ** 1.15          # wavelength grows toward the viewer
            A = 0.5 + 2.8 * depth ** 1.2
            x = -L * 2 + (L / 2) * (i % 2) + rng.uniform(0, L)
            d = []
            while x < W + L:
                if rng.random() > 0.07:
                    a = A * rng.uniform(.75, 1.15)
                    d.append(f"M{x:.1f},{y:.1f} Q{x + L / 2:.1f},{y - 2 * a:.1f} {x + L:.1f},{y:.1f}")
                x += L
            gold = i % 3 == 0
            op = (0.18 + 0.45 * depth) * (1.15 if gold else 1)
            self.rows.append((y, f'<path d="{"".join(d)}" fill="none" stroke="{GOLD_D if gold else AZ_M}" '
                                 f'stroke-width="{0.42 + 0.38 * depth:.2f}" stroke-opacity="{op:.2f}" '
                                 f'stroke-linecap="round"/>'))
            y += (1.6 + 8.6 * depth ** 1.3) * (1.0 if i % 3 != 2 else 2.0)
            i += 1

    def strip(self, y0, x0=-20, x1=W + 20, fade=0, shore=None):
        cid = self.art.uid("w")
        if shore:       # an irregular shoreline: [(x, y), ...] left to right
            pts = [(x0, shore[0][1])] + shore + [(x1, shore[-1][1]), (x1, H + 20), (x0, H + 20)]
            self.art.defs.append(f'<clipPath id="{cid}"><path d="{path(pts)} Z"/></clipPath>')
        else:
            self.art.defs.append(f'<clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{x1 - x0}" '
                                 f'height="{H - y0 + 20}"/></clipPath>')
        self.art.body.append(
            f'<g clip-path="url(#{cid})"><rect x="-20" y="{self.top}" width="{W + 40}" '
            f'height="{H - self.top + 20}" fill="url(#{self.gid})"/>'
            + "".join(r for y, r in self.rows if y > y0 + 2) + "</g>")
        if fade:
            g = self.art.grad([(0, MIST, 0.96), (0.45, MIST, 0.6), (1, MIST, 0)], y0, y0 + fade, units=True)
            self.art.body.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{fade}" fill="url(#{g})"/>')


# ---- small things ----------------------------------------------------------------------
def spray(cx, cy, s=1.0):
    """The single spray (浪花一朵, the 「我」 of the song): a gold crest that
    rises out of the ripples and curls over into a round eddy (「笑的漩涡」),
    flinging three drops."""
    pts, ws = [], []
    n1 = 40
    for i in range(n1):                       # the rising swell
        t = i / n1
        pts.append((-50 + 54 * t, 10 - 32 * math.sin(t * math.pi / 2) ** 1.3))
        ws.append(0.3 + 5.6 * t ** 1.6)
    c = (15.5, -10.5)
    r0 = math.hypot(4 - c[0], -22 - c[1])
    a0 = math.atan2(-22 - c[1], 4 - c[0])
    n2 = 80
    for i in range(1, n2 + 1):                # the curl, winding into an eddy
        t = i / n2
        a = a0 + t * 1.9 * math.pi
        r = r0 * (1 - 0.74 * t ** 0.9)
        pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a)))
        ws.append(5.9 * (1 - t) ** 1.25 + 0.35)
    parts = [ribbon(pts, ws)]
    foam = []
    for (x0, y0, x1, y1, w) in [(-42, 13, 38, 10.5, 1.7), (-22, 17.5, 48, 16, 1.1)]:
        fp = [(x0 + (x1 - x0) * k / 30, y0 + (y1 - y0) * k / 30 - 1.6 * math.sin(k / 30 * math.pi))
              for k in range(31)]
        foam.append(ribbon(fp, [w * math.sin(k / 30 * math.pi) + 0.2 for k in range(31)]))
    drops = "".join(f'<circle cx="{x}" cy="{y}" r="{r}"/>'
                    for x, y, r in [(31, -30, 1.7), (37.5, -22, 1.25), (24, -37, 1.05)])
    return (f'<g transform="translate({cx:.1f},{cy:.1f}) scale({s})" fill="{GOLD}">'
            f'<path d="{" ".join(parts)}"/><path d="{" ".join(foam)}" opacity=".85"/>{drops}</g>')


def boat(x, y, s):
    """一叶扁舟: a sampan with a mat sail, on the far river."""
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<path d="M-15,-0.6 Q-7,2.6 0,2.8 Q8,2.6 16,-1.6 L13.2,-0.2 Q0,0.6 -12.6,-0.4 Z" fill="{INK}" '
            f'opacity=".85"/>'
            f'<path d="M-3.2,-0.5 Q-1,-3.6 3.4,-3.6 Q6.6,-3.2 7.4,-0.4 Z" fill="{INK}" opacity=".7"/>'
            f'<line x1="0.6" y1="-0.4" x2="0.6" y2="-24" stroke="{INK}" stroke-width="0.55"/>'
            f'<path d="M1.4,-23 L9.8,-21.6 L11.6,-4.8 L1.4,-4.8 Z" fill="{OCHRE}" opacity=".95"/>'
            f'<path d="M1.4,-17.6 L10.7,-16.6 M1.4,-12.6 L11.1,-12 M1.4,-8.4 L11.4,-8.1" '
            f'stroke="{OCHRE_DD}" stroke-width="0.35" opacity=".8"/>'
            f'<path d="M-24,4.6 Q-8,3 0,4.4 Q9,5.8 26,4.2" fill="none" stroke="{AZ_M}" '
            f'stroke-width="0.5" opacity=".5"/></g>')


def hamlet(x, y, s):
    """小小村落, 袅袅炊烟: a few roofs on the terrace, one thread of smoke."""
    def house(dx, dy, w, hh, roof):
        return (f'<g transform="translate({dx},{dy})">'
                f'<rect x="{-w / 2}" y="{-hh}" width="{w}" height="{hh}" fill="{WALL}"/>'
                f'<rect x="{-w / 2 + w * .35}" y="{-hh * .7}" width="{w * .3}" height="{hh * .7}" fill="{INK}" opacity=".55"/>'
                f'<path d="M{-w / 2 - 2.4},{-hh + .4} Q{-w / 2 - .6},{-hh - .6} {-w / 2 + .6},{-hh - roof} '
                f'L{w / 2 - .6},{-hh - roof} Q{w / 2 + .6},{-hh - .6} {w / 2 + 2.4},{-hh + .4} Z" fill="{INK}"/>'
                f'</g>')
    smoke = (f'<path d="M-5,-12 C-9,-20 -1,-26 -5,-34 C-9,-42 -2,-48 -6,-57 C-9,-64 -4,-70 -1,-76" '
             f'fill="none" stroke="{AZ_M}" stroke-width="0.8" stroke-linecap="round" opacity=".5"/>')
    fence = f'<path d="M-22,1 L24,1" stroke="{OCHRE_DD}" stroke-width="0.6" opacity=".5"/>'
    return (f'<g transform="translate({x},{y}) scale({s})">{smoke}{fence}'
            f'{house(-12, 0, 11, 5.2, 4.2)}{house(4, 0.4, 14, 6.2, 5.0)}{house(17, 1, 9, 4.4, 3.6)}</g>')


# ---- the landscape ----------------------------------------------------------------------
def landscape(seed=1113):
    art = Art(seed)
    rng = art.rng
    sky = art.grad([(0, SILK_TOP, 1), (0.36, SILK_MID, 1), (0.62, MIST, 1), (1, MIST, 1)])
    art.body.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#{sky})"/>')

    # ---- far ranges on the horizon (千里: the distance)
    for keys, base in [
            ([(430, 712), (470, 650), (512, 618), (540, 570), (558, 540), (572, 532), (586, 548),
              (606, 578), (636, 596), (676, 626), (716, 712)], 712),
            ([(-20, 640), (20, 604), (60, 594), (110, 610), (150, 640)], 650)]:
        art.form(keys, base, "hill", fade=0.7, cun=0, gold=0.35, knobs=4)
    art.mist(560, 700, 240, 34, 0.9)

    # ---- right group, middle distance: a stepped flat-topped mountain with
    # a cluster of crags on its far shoulder (fade: further away)
    art.form(crag(896, 404, 716, 40, 270, rng, lean=0.25, steps=2, p=1.6), 716, "peak", fade=0.2)
    art.form([(560, 720), (578, 676), (596, 650), (614, 640), (630, 618), (646, 600), (664, 594),
              (676, 572), (690, 548), (706, 534), (726, 528), (780, 526), (796, 530), (804, 516),
              (812, 494), (822, 474), (834, 466), (846, 472), (852, 492), (860, 520), (872, 536),
              (890, 560), (910, 600), (936, 660), (960, 720)],
             720, "peak", fade=0.15, knobs=7, amp=(0.8, 2.4), aspect=1.15, cun=1.4)
    art.form(crag(946, 500, 724, 34, 210, rng, lean=-0.2, steps=1, p=1.6), 724, "peak", fade=0.1)
    art.mist(720, 676, 190, 22, 0.7)

    water = Water(art, rng, 712)
    water.strip(712, fade=36)

    # ---- the main massif (高山): one broad range climbing in knobbly steps
    # to the crown, crags clustered on its flank, a terrace, and broad
    # stepped forms in front
    art.form([(-30, 790), (-12, 690), (4, 640), (18, 606), (30, 594), (44, 596), (56, 566),
              (68, 544), (80, 538), (92, 542), (102, 512), (112, 486), (124, 474), (138, 478),
              (148, 450), (160, 414), (172, 392), (186, 382), (198, 386), (208, 360), (220, 326),
              (234, 302), (248, 290), (262, 288), (274, 296), (282, 312), (292, 322), (304, 316),
              (316, 320), (326, 340), (336, 368), (348, 390), (362, 400), (376, 404), (388, 418),
              (398, 444), (410, 466), (426, 476), (442, 484), (456, 504), (476, 536), (502, 572),
              (534, 612), (572, 660), (616, 716), (660, 790)], 790, "peak", knobs=14,
             amp=(1.0, 3.0), aspect=0.95, fade=0.04, cun=1.5)
    art.form(crag(110, 400, 780, 34, 230, rng, lean=-0.3, steps=2, p=1.9), 780, "peak", fade=0.06)
    art.form(crag(374, 372, 780, 36, 250, rng, lean=0.35, steps=2, p=1.7), 780, "peak", fade=0.06)
    art.mist(240, 646, 240, 26, 0.7)
    art.mist(480, 590, 110, 20, 0.6)
    # the terrace: a flat platform on a stepped ridge that runs down into the river
    art.form([(372, 840), (382, 772), (392, 712), (400, 668), (408, 636), (418, 618), (432, 610),
              (492, 608), (504, 611), (510, 624), (516, 632), (540, 636), (556, 640), (568, 656),
              (592, 690), (626, 730), (666, 782), (704, 840)], 840, "hill", knobs=3, amp=(0.6, 1.6),
             aspect=1.05)
    art.body.append(hamlet(462, 609, 1.45))
    art.form([(-30, 846), (-12, 768), (6, 712), (22, 676), (38, 660), (54, 660), (68, 640),
              (82, 612), (96, 598), (112, 600), (126, 578), (142, 544), (158, 518), (174, 504),
              (190, 500), (204, 508), (214, 526), (226, 544), (242, 552), (258, 552), (270, 570),
              (290, 612), (316, 672), (350, 744), (390, 846)], 846, "peak", knobs=9,
             amp=(1.0, 2.8), aspect=0.95)
    art.form(crag(332, 548, 852, 30, 250, rng, lean=0.3, steps=2, p=1.45), 852, "peak")
    art.mist(330, 800, 300, 30, 0.9)

    water.strip(806, fade=46)
    art.body.append(boat(790, 782, 1.55))

    # ---- foreground: a promontory, green crown on an 赭石 bank with two rocky
    # knobs, sloping out into the river (碧浪清波)
    art.form([(-30, 900), (-18, 828), (-4, 790), (10, 764), (24, 746), (38, 740), (50, 746),
              (60, 734), (72, 714), (86, 702), (100, 700), (112, 710), (120, 726), (134, 738),
              (150, 742), (166, 752), (184, 772), (200, 786), (216, 790), (234, 794), (250, 806),
              (276, 830), (310, 852), (348, 868), (382, 880), (404, 900)], 900, "bank", knobs=6,
             amp=(0.8, 2.4), cun=1.3)
    shore = spline([(-20, 900), (40, 897), (90, 902), (150, 896), (220, 899), (280, 893),
                    (340, 896), (400, 892), (470, 897), (520, 890), (560, 880), (620, 870)], 6)
    water.strip(890, shore=shore)
    art.body.append(spray(W * 0.6, 948, 1.3))
    vg = art.uid("v")
    art.defs.append(f'<radialGradient id="{vg}" cx="0.5" cy="0.45" r="0.75">'
                    f'<stop offset="0.55" stop-color="{AGED}" stop-opacity="0"/>'
                    f'<stop offset="1" stop-color="{AGED}" stop-opacity="0.2"/></radialGradient>')
    art.body.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#{vg})"/>')
    return art


# ---- the mount -----------------------------------------------------------------------------
def mount_svg():
    art = landscape()
    damask = (f'<pattern id="dam" width="24" height="24" patternUnits="userSpaceOnUse">'
              f'<path d="M12,2 L22,12 L12,22 L2,12 Z" fill="none" stroke="{MOUNT_HI}" '
              f'stroke-width="0.6"/></pattern>'
              f'<pattern id="gsp" width="8" height="8" patternUnits="userSpaceOnUse">'
              f'<path d="M4,0.8 L7.2,4 L4,7.2 L0.8,4 Z" fill="none" stroke="{GESHUI_D}" '
              f'stroke-width="0.35"/></pattern>')
    # 天杆 (the top rod) and the two 惊燕 hanging from it: slim, tone-on-tone
    rod = (f'<linearGradient id="rodg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{ROD}"/>'
           f'<stop offset="0.55" stop-color="{MOUNT_HI}"/><stop offset="1" stop-color="{ROD}"/></linearGradient>'
           f'<rect x="-10" y="-4" width="{PW + 20}" height="20" fill="url(#rodg)"/>'
           f'<line x1="-10" y1="16" x2="{PW + 10}" y2="16" stroke="{GOLD}" stroke-width="0.6" stroke-opacity=".75"/>')
    jy = []
    for cx in (PW * 0.25, PW * 0.75):
        jy.append(f'<rect x="{cx - 7.5}" y="16" width="15" height="{SG_TOP - 16}" fill="{JINGYAN}"/>'
                  f'<line x1="{cx - 7.5}" y1="16" x2="{cx - 7.5}" y2="{SG_TOP}" stroke="{GOLD}" '
                  f'stroke-width="0.5" stroke-opacity=".95"/>'
                  f'<line x1="{cx + 7.5}" y1="16" x2="{cx + 7.5}" y2="{SG_TOP}" stroke="{GOLD}" '
                  f'stroke-width="0.5" stroke-opacity=".95"/>')
    hair = lambda y, op=1: (f'<line x1="{SIDE}" y1="{y}" x2="{PW - SIDE}" y2="{y}" '  # noqa: E731
                            f'stroke="{GOLD}" stroke-width="0.6" stroke-opacity="{op}"/>')
    gs = lambda y, h: (f'<rect x="{SIDE}" y="{y}" width="{W}" height="{h}" fill="{GESHUI}"/>'  # noqa: E731
                       f'<rect x="{SIDE}" y="{y}" width="{W}" height="{h}" fill="url(#gsp)"/>')
    return (f'<svg class="art" viewBox="0 0 {PW} {PH}" width="11in" height="17in">'
            f'<defs>{damask}{"".join(art.defs)}'
            f'<clipPath id="hx"><rect x="0" y="0" width="{W}" height="{H}"/></clipPath></defs>'
            f'<rect width="{PW}" height="{PH}" fill="{MOUNT}"/>'
            f'<rect width="{PW}" height="{PH}" fill="url(#dam)" opacity="0.8"/>'
            f'{"".join(jy)}{rod}'
            f'{gs(SG_TOP, Y0 - SG_TOP)}{gs(Y0 + H, XG_BOT - Y0 - H)}'
            f'<g transform="translate({X0},{Y0})" clip-path="url(#hx)">{"".join(art.body)}</g>'
            f'{hair(SG_TOP)}{hair(Y0, .8)}{hair(Y0 + H, .8)}{hair(XG_BOT)}'
            f'<rect x="{X0 - 5}" y="{SG_TOP - 5}" width="{W + 10}" height="{XG_BOT - SG_TOP + 10}" '
            f'fill="none" stroke="{GOLD}" stroke-width="0.5" stroke-opacity="0.8"/>'
            f'</svg>')


def seal_html(name, x, y, w):
    """A slender cinnabar seal (长方印, 白文): the name in one column inside a
    fine inner border."""
    step = w * 0.86
    h = step * len(name) + w * 0.3
    chars = "".join(f'<span style="display:block;height:{step:.3f}in;line-height:{step:.3f}in">'
                    f'{lib.e(c)}</span>' for c in name)
    return (f'<div class="seal" style="left:{x}in;top:{y}in;width:{w}in;height:{h:.3f}in;'
            f'padding-top:{w * 0.15:.3f}in;font-size:{step * 0.8 * 72:.1f}pt">'
            f'<div class="sealin"></div>{chars}</div>')


def render(m):
    e, sym = lib.e, lib.sym
    rows = lib.credit_rows(m)

    def row(zh, en, name):
        return (f'<div class="cr"><div class="l"><span class="en">{e(en)}</span>'
                f'<span class="zh">{e(zh)}</span></div><div class="ax"></div>'
                f'<div class="r">{e(name)}</div></div>')

    instr = " &nbsp;·&nbsp; ".join(f'{e(en)} <span class="cn">{e(zh)}</span>'
                                    for en, zh in m["instrumentation"])
    key_parts = [p.strip() for p in m["key"].split("·")]
    key = (f'{sym(key_parts[0])} <span class="cn">{e(" ".join(key_parts[1:]))}</span>'
           f' &nbsp;·&nbsp; {sym(m["tempo"])} &nbsp;·&nbsp; {sym(m["duration"])}')
    ct, rh = 13.62, 0.33
    css = f"""
    .page {{ background: {MOUNT}; color: {PALE}; }}
    .art {{ position:absolute; left:0; top:0; }}
    .t {{ position:absolute; left:0; width:11in; text-align:center; white-space:nowrap; }}
    .fs {{ top:0.78in; font:500 15pt/1 'EB Garamond'; letter-spacing:.62em; padding-left:.62em;
           color:{GOLD}; }}
    .sic {{ top:1.19in; font:500 7.5pt/1 'EB Garamond'; letter-spacing:.42em; padding-left:.42em;
            color:{GOLD}; opacity:.85; text-transform:uppercase; }}
    .title {{ top:2.93in; font:900 86pt/1 'Noto Serif CJK SC'; letter-spacing:.09em;
              padding-left:.09em; color:{INK}; }}
    .py {{ top:4.39in; font:500 13.5pt/1 'EB Garamond'; letter-spacing:.5em; padding-left:.5em;
           color:{AZ_M}; text-transform:uppercase; }}
    .sub {{ top:12.74in; font:500 15.5pt/1 'Noto Serif CJK SC'; letter-spacing:.14em;
            padding-left:.14em; color:{PALE}; }}
    .suben {{ top:13.1in; font:italic 400 12pt/1 'EB Garamond'; color:{PALE}; opacity:.82; }}
    .rule {{ position:absolute; top:13.43in; left:5.1in; width:.8in; border-top:.5pt solid {GOLD}; opacity:.7; }}
    .credits {{ position:absolute; top:{ct}in; left:0; width:11in; }}
    .axis {{ position:absolute; left:5.5in; top:{ct + 0.05:.2f}in; height:{len(rows) * rh - 0.1:.2f}in;
             border-left:.5pt solid {GOLD}; opacity:.55; }}
    .cr {{ display:flex; align-items:baseline; height:{rh}in; }}
    .cr .l {{ width:5.33in; text-align:right; }}
    .cr .ax {{ width:.34in; }}
    .cr .r {{ width:5.33in; font:600 15pt/1 'Noto Serif CJK SC'; color:{PALE}; letter-spacing:.07em; }}
    .cr .en {{ font:500 8pt/1 'EB Garamond'; letter-spacing:.24em; color:{GOLD};
               text-transform:uppercase; margin-right:.13in; }}
    .cr .zh {{ font:500 11pt/1 'Noto Serif CJK SC'; color:{GOLD}; }}
    .key {{ top:15.46in; font:400 11pt/1 'EB Garamond'; letter-spacing:.05em; color:{PALE}; }}
    .key .cn, .ins .cn {{ font-family:'Noto Serif CJK SC'; font-size:.9em; }}
    .ins {{ top:15.74in; font:400 11pt/1 'EB Garamond'; letter-spacing:.05em; color:{PALE}; opacity:.88; }}
    .sig {{ top:16.12in; font:600 13pt/1 'Noto Serif CJK SC'; letter-spacing:.45em;
            padding-left:.45em; color:{PALE}; }}
    .sigen {{ top:16.43in; font:500 7pt/1 'EB Garamond'; letter-spacing:.34em; padding-left:.34em;
              color:{GOLD}; text-transform:uppercase; }}
    .seal {{ position:absolute; background:{CINNABAR}; border-radius:.025in; text-align:center;
             font-family:'Noto Serif CJK SC'; font-weight:700; color:#F7EBDD; }}
    .sealin {{ position:absolute; left:.022in; top:.022in; right:.022in; bottom:.022in;
               border:.6pt solid #F7EBDD; opacity:.75; border-radius:.012in; }}
    """
    body = (mount_svg()
            + f'<div class="t fs">FULL SCORE</div>'
            + f'<div class="t sic">Score in C · Concert Pitch</div>'
            + f'<div class="t title">{e(m["title"])}</div>'
            + f'<div class="t py">{e(m["title_latin"])}</div>'
            + seal_html(m["arranger"], 9.68, 10.66, 0.25)
            + f'<div class="t sub">{e(m["subtitle"])}</div>'
            + f'<div class="t suben">{e(m["subtitle_en"])}</div>'
            + '<div class="rule"></div>'
            + '<div class="credits">' + "".join(row(*r) for r in rows) + '</div>'
            + '<div class="axis"></div>'
            + f'<div class="t key">{key}</div>'
            + f'<div class="t ins">{instr}</div>'
            + f'<div class="t sig">{e(m["arranger"])}</div>'
            + f'<div class="t sigen">Arrangement &amp; Music Preparation · {e(m["year"])}</div>')
    return lib.page(css, body, "qianli")
