# exec'd inside make.py: cover(), chars(), variant, e, INK, RED, META, math
PAPER = "#fff"
RED_LIGHT = "#D9876F"   # the reverse side of a cinnabar ribbon / feather
BASE = 982.5            # baseline in the 1000-unit em box (line top = 0)


def _f(*xs):
    return ",".join(f"{x:.2f}" for x in xs)


def goose(x, y, s, color=INK):
    """A wild goose flying up the page, seen from below: crescent wings
    swept back, a short body with the head forward.  s = wingspan."""
    w = s / 2
    wing = (f"M{_f(-w, .30 * s)} Q{_f(-.45 * w, -.24 * s)} {_f(0, -.06 * s)} "
            f"Q{_f(.45 * w, -.24 * s)} {_f(w, .30 * s)} "
            f"Q{_f(.48 * w, -.04 * s)} {_f(0, .10 * s)} "
            f"Q{_f(-.48 * w, -.04 * s)} {_f(-w, .30 * s)} Z")
    body = (f"M{_f(0, -.30 * s)} C{_f(.07 * s, -.22 * s)} {_f(.06 * s, .16 * s)} {_f(0, .30 * s)} "
            f"C{_f(-.06 * s, .16 * s)} {_f(-.07 * s, -.22 * s)} {_f(0, -.30 * s)} Z")
    return (f"<g transform='translate({_f(x, y)})' fill='{color}'>"
            f"<path d='{wing}'/><path d='{body}'/></g>")


def feather(L, wu, wl, color, shaft=PAPER, notches=(), barbs=0):
    """A feather along +x: quill at (0,0), tip at (L,0); upper vane wu wide,
    lower vane wl wide.  notches: positions (0..1) of splits in the upper
    vane.  barbs: number of fine paper-coloured barb lines."""
    a = .14 * L
    vane = (f"M{_f(a, 0)} C{_f(.30 * L, -wu)} {_f(.78 * L, -.95 * wu)} {_f(L, 0)} "
            f"C{_f(.80 * L, .95 * wl)} {_f(.32 * L, wl)} {_f(a, 0)} Z")
    out = [f"<path d='{vane}' fill='{color}'/>",
           f"<path d='M{_f(0, 0)} L{_f(.97 * L, 0)}' stroke='{shaft}' "
           f"stroke-width='{max(.6, .045 * wu):.2f}' stroke-linecap='round'/>",
           f"<path d='M{_f(0, 0)} L{_f(a * 1.05, 0)}' stroke='{color}' "
           f"stroke-width='{max(.8, .09 * wu):.2f}' stroke-linecap='round'/>"]
    for t in notches:   # a split in the vane, angled toward the tip
        x0 = t * L
        out.append(f"<path d='M{_f(x0, -.05 * wu)} L{_f(x0 + .10 * L, -1.1 * wu)}' "
                   f"stroke='{shaft}' stroke-width='{max(.6, .05 * wu):.2f}'/>")
    for k in range(barbs):
        x0 = a + (k + .5) * (.86 * L - a) / barbs
        for sgn, ww in ((-1, wu), (1, wl)):
            out.append(f"<path d='M{_f(x0, 0)} L{_f(x0 + .07 * L, sgn * ww)}' stroke='{shaft}' "
                       f"stroke-width='{max(.25, .012 * ww):.2f}' opacity='.55'/>")
    return "".join(out)


def quill(L, wo, wi, color, n=36, bend=.05, gaps=(), sw=None, fill=.16):
    """A feather drawn as an engraver would: a tapered, slightly bent shaft,
    a faint vane and dense, gently curved barbs raking toward the tip.
    Quill at (0,0), tip at (L,0); wo / wi: outer (-y) / inner vane width.
    gaps: (t0, t1) ranges where the vane is split."""
    sw = sw or L * .0065

    def sh(t):
        return (t * L, -bend * L * math.sin(math.pi * t))

    def prof(t):  # vane width profile: full in the middle, round tip
        u = min(1, max(0, (t - .13) / .87))
        return (math.sin(math.pi * u) ** .45) * (1 - .22 * u) if u < .5 else \
            (1 - .22 * u) * math.sqrt(max(0, 1 - ((u - .5) / .5) ** 2.4))

    out, edge = [], {-1: [], 1: []}
    barbs = []
    for k in range(n):
        t = .14 + .84 * (k + .5) / n
        x, y = sh(t)
        split = any(a0 <= t <= a1 for a0, a1 in gaps)
        for side, w in ((-1, wo), (1, wi)):
            ln = w * prof(t)
            rake = .62 if side < 0 else .55
            ex, ey = x + ln * rake, y + side * ln
            if split and side < 0:
                ex, ey = ex + ln * .18, ey + ln * .10
            cx, cy = x + ln * rake * .15, y + side * ln * .70
            edge[side].append((ex, ey))
            barbs.append(f"<path d='M{_f(x, y)} Q{_f(cx, cy)} {_f(ex, ey)}' fill='none' "
                         f"stroke='{color}' stroke-width='{sw:.2f}' stroke-linecap='round'/>")
    x0, y0 = sh(.14)
    xt, yt = sh(1)
    poly = [(x0, y0)] + edge[-1] + [(xt, yt)] + edge[1][::-1]
    out.append("<path d='M" + " L".join(_f(*q) for q in poly) + f" Z' fill='{color}' opacity='{fill}'/>")
    out += barbs
    top, bot = [], []
    for k in range(21):
        t = k / 20
        x, y = sh(t)
        w = L * .014 * (1 - t) + sw * .5
        top.append((x, y - w / 2))
        bot.append((x, y + w / 2))
    out.append("<path d='M" + " L".join(_f(*q) for q in top + bot[::-1]) + f" Z' fill='{color}'/>")
    return "".join(out)


def wing_shape(L, color, sep=PAPER, rise=30):
    """A classic wing pointing left (-x), root at (0,0): a gently rising
    leading edge, seven primaries and secondaries hanging from it, and a
    row of coverts over their roots.  Size about L x 0.55L."""
    out = []
    # leading edge from root to tip, rising slightly
    th = math.radians(rise)

    def le(t):  # leading edge: rises at `rise` degrees, arching a little
        return (-L * t * math.cos(th), -L * (t * math.sin(th) + .07 * math.sin(math.pi * t)))
    n = 9
    feathers = []
    for k in range(n):
        t = .10 + .86 * k / (n - 1)
        rx, ry = le(t)
        ang = 118 + 70 * t ** 1.2          # hang down near the root, sweep out at the tip
        ln = L * (.30 + .42 * t ** 1.3)
        w = L * (.08 + .02 * (1 - t))
        feathers.append((rx, ry, ang, ln, w))
    for rx, ry, ang, ln, w in feathers:   # inner first, outer (tip) feathers on top
        d = (f"M0,{-w * .5:.2f} C{ln * .45:.2f},{-w * .62:.2f} {ln * .92:.2f},{-w * .55:.2f} {ln:.2f},0 "
             f"C{ln * .92:.2f},{w * .55:.2f} {ln * .45:.2f},{w * .62:.2f} 0,{w * .5:.2f} Z")
        out.append(f"<g transform='translate({_f(rx, ry)}) rotate({ang:.1f})'>"
                   f"<path d='{d}' fill='{color}' stroke='{sep}' stroke-width='{L * .012:.2f}'/>"
                   f"<path d='M{ln * .05:.2f},0 L{ln * .9:.2f},0' stroke='{sep}' "
                   f"stroke-width='{L * .006:.2f}' opacity='.7'/></g>")
    # coverts: a row of short feathers over the roots
    for k in range(7):
        t = .06 + .62 * k / 6
        rx, ry = le(t)
        ang, ln, w = 128 + 40 * t, L * (.15 + .10 * t), L * .07
        d = (f"M0,{-w * .5:.2f} C{ln * .45:.2f},{-w * .62:.2f} {ln * .92:.2f},{-w * .55:.2f} {ln:.2f},0 "
             f"C{ln * .92:.2f},{w * .55:.2f} {ln * .45:.2f},{w * .62:.2f} 0,{w * .5:.2f} Z")
        out.append(f"<g transform='translate({_f(rx, ry)}) rotate({ang:.1f})'>"
                   f"<path d='{d}' fill='{color}' stroke='{sep}' stroke-width='{L * .012:.2f}'/></g>")
    return "".join(out)


def put(svg_inner, x, y, rot=0, scale=1):
    return (f"<g transform='translate({_f(x, y)}) rotate({rot:.2f}) scale({scale:.3f})'>"
            f"{svg_inner}</g>")


# ---------------------------------------------------------------------------
@variant
def geese():
    """雁字: the divider's diamond becomes wild geese flying in a 人 —
    「一会儿排成个人字」, every Chinese child's first autumn text."""
    pts = [(50, 6),
           (45.5, 16), (40.5, 25.5), (34.5, 34.5), (27, 43), (18, 50.5), (8, 56.5),
           (55.5, 17.5), (62, 27.5), (69.5, 37), (78.5, 45), (89.5, 51.5)]
    g = "".join(goose(x, y, 7.6) for x, y in pts)
    orn = ("<span></span><i class='flock'><svg viewBox='0 0 100 64' "
           f"width='1.12in' height='0.72in'>{g}</svg></i><span></span>")
    css = """
.orn { top: 6.93in; }
.orn span { width: 1.35in; }
.orn .flock { display: inline-block; margin: 0 16pt; vertical-align: middle;
              position: relative; top: -3pt; }
.orn .flock svg { display: block; overflow: visible; }
"""
    return cover(orn_html=orn, css=css)


# ---------------------------------------------------------------------------
def bracket_wing(mirror=False):
    """《 drawn as feathers: each chevron arm is a feather whose tip reaches
    the vertex, quill at the open end; the outer chevron in ink, the inner
    in cinnabar.  Together the two brackets are a pair of wings around the
    title.  Box 560 x 1000 (em units)."""
    W, H = 560, 1000
    parts = []
    for (vx, ex, col, wo, wi, reach) in ((30, 330, INK, 72, 26, .47),
                                          (240, 540, RED, 62, 22, .43)):
        for sgn in (-1, 1):
            qx, qy = ex, H / 2 + sgn * H * reach
            tx, ty = vx, H / 2 + sgn * 18
            L = math.hypot(tx - qx, ty - qy)
            ang = math.degrees(math.atan2(ty - qy, tx - qx))
            # outer vane faces away from the bracket's interior
            f = quill(L, wo, wi, col, n=40, bend=.035 * -sgn, gaps=((.56, .60),))
            if sgn < 0:
                f = f"<g transform='scale(1,-1)'>{f}</g>"
            parts.append(put(f, qx, qy, ang))
    inner = "".join(parts)
    if mirror:
        inner = f"<g transform='translate({W},0) scale(-1,1)'>{inner}</g>"
    return (f"<span class='br'><svg viewBox='0 0 {W} {H}' width='{W / 1000:.3f}em' "
            f"height='1em'>{inner}</svg></span>")


@variant
def wings():
    """羽书名号: 《 》 drawn as feathers, so the title flies between its own
    brackets."""
    css = """
.title { font-size: 84pt; }
.title .br { display: inline-block; width: .56em; height: 1em; vertical-align: -.12em;
             margin: 0 .10em 0 0; }
.title .br.r { margin: 0 0 0 -.02em; }
.title .br svg { display: block; overflow: visible; }
"""
    t = bracket_wing() + e(META["title"]) + bracket_wing(True).replace("class='br'", "class='br r'")
    return cover(title_html=t, css=css)


# ---------------------------------------------------------------------------
def glyph_path(ch, size=1000):
    """SVG path of a title glyph (Noto Serif CJK SC Bold) in the 1000-unit
    em box used by the character spans (y down, baseline at BASE)."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    f = TTFont("/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc", fontNumber=2)
    gs = f.getGlyphSet()
    pen = SVGPathPen(gs)
    gs[f.getBestCmap()[ord(ch)]].draw(TransformPen(pen, (1, 0, 0, -1, 0, BASE)))
    return pen.getCommands()


@variant
def takeoff():
    """飞字起飞: the last character lifts off the line, a hairline climb
    behind it — the title takes off like the launches the song scored."""
    css = """
.cover { position: relative; z-index: 0; }
.title .c4 { color: #fff; }
"""
    lifted = (f"<svg viewBox='0 0 1000 1000' width='1em' height='1em'>"
              f"<g transform='translate(20,-200) rotate(-9 100 900)'>"
              f"<path d='{glyph_path('飞')}' fill='{INK}'/></g></svg>")
    # climb path in page inches: along under the line, lifting at 飞
    path = ("M 2.05 5.62 C 4.8 5.64, 7.4 5.62, 8.55 5.30 "
            "S 9.55 4.30, 9.68 3.62")
    dots = "".join(f"<circle cx='{x}' cy='{y}' r='{r}' fill='{RED}' opacity='{o}'/>"
                   for x, y, r, o in ((9.70, 3.45, .035, 1),))
    extra = (f"<svg class='art' style='left:0;top:0;z-index:-1' width='11in' height='17in' "
             f"viewBox='0 0 11 17'><path d='{path}' fill='none' stroke='{RED}' "
             f"stroke-width='.012' stroke-dasharray='.05 .035' stroke-linecap='round'/>"
             f"{dots}</svg>")
    return cover(title_html=chars(META["title"], lambda i, c: lifted if i == 4 else ""),
                 extra=extra, css=css)


# ---------------------------------------------------------------------------
def catmull(pts, n=60):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                                   + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                             for j in range(2)))
    out.append(pts[-1])
    return out


def ribbon(pts, width, twists, front=RED, back=RED_LIGHT, taper=.18):
    """A silk ribbon along a spline: its visible width breathes with
    |cos|, and each zero crossing flips it to the other face."""
    c = catmull(pts)
    # arc length
    s = [0]
    for a, b in zip(c, c[1:]):
        s.append(s[-1] + math.dist(a, b))
    S = s[-1]
    polys, cur, side = [], [], None
    for i, (p, si) in enumerate(zip(c, s)):
        t = si / S
        q = c[min(i + 1, len(c) - 1)] if i < len(c) - 1 else p
        r = c[max(i - 1, 0)]
        dx, dy = q[0] - r[0], q[1] - r[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        ph = math.cos(math.pi * (twists * t + .25))
        env = min(1, t / taper, (1 - t) / (taper * .6))
        hw = width / 2 * max(abs(ph), .08) * max(env, 0)
        sd = ph >= 0
        if side is None:
            side = sd
        if sd != side:
            polys.append((side, cur))
            cur = [cur[-1]]
            side = sd
        cur.append((p[0] + nx * hw, p[1] + ny * hw, p[0] - nx * hw, p[1] - ny * hw))
    polys.append((side, cur))
    out = []
    for sd, seg in polys:
        ring = [(a, b) for a, b, _, _ in seg] + [(c2, d) for _, _, c2, d in reversed(seg)]
        d = "M" + " L".join(_f(x, y) for x, y in ring) + " Z"
        out.append(f"<path d='{d}' fill='{front if sd else back}'/>")
    return "".join(out)


@variant
def ribbon_feitian():
    """飞天飘带: Chinese flight never needed wings — the Dunhuang apsaras fly
    on a ribbon.  One silk ribbon streams back from 飞 behind the title."""
    pts = [(9.0, 4.6), (9.3, 3.98), (8.6, 3.5), (7.2, 3.74), (5.7, 3.42),
           (4.25, 3.70), (2.95, 3.44), (2.05, 3.62), (1.62, 3.98), (1.95, 4.22),
           (2.2, 3.92), (1.85, 3.62), (1.3, 3.55)]
    r = ribbon(pts, .11, 2.6)
    extra = (f"<svg class='art' style='left:0;top:0;z-index:-1' width='11in' height='17in' "
             f"viewBox='0 0 11 17'>{r}</svg>")
    css = ".cover { position: relative; z-index: 0; }"
    return cover(extra=extra, css=css)


# ---------------------------------------------------------------------------
def swallow_kite():
    """A swallow kite (沙燕风筝), box 100 x 100, head up: long crescent wings
    on a straight bamboo spar, slim body, deep forked tail."""
    lw = 1.1
    k = []
    for sgn in (-1, 1):
        x = lambda v: 50 + sgn * v  # noqa: E731
        # tail fork
        k.append(f"<path d='M{_f(x(2.5), 56)} C{_f(x(6), 72)} {_f(x(10), 86)} {_f(x(17), 99)} "
                 f"C{_f(x(11), 90)} {_f(x(5), 78)} {_f(x(0), 66)} Z' fill='{RED}' "
                 f"stroke='{INK}' stroke-width='{lw}' stroke-linejoin='round'/>")
        # wing: crescent, tip swept up and out
        k.append(f"<path d='M{_f(x(3), 31)} C{_f(x(16), 22)} {_f(x(34), 16)} {_f(x(49), 14)} "
                 f"C{_f(x(40), 24)} {_f(x(26), 34)} {_f(x(5), 44)} Z' fill='{PAPER}' "
                 f"stroke='{INK}' stroke-width='{lw}' stroke-linejoin='round'/>")
        k.append(f"<path d='M{_f(x(31), 18.6)} C{_f(x(38), 16)} {_f(x(44), 14.6)} {_f(x(49), 14)} "
                 f"C{_f(x(44), 19)} {_f(x(39), 23.5)} {_f(x(33), 27.6)} "
                 f"C{_f(x(34), 24)} {_f(x(33), 21)} {_f(x(31), 18.6)} Z' fill='{RED}'/>")
        k.append(f"<path d='M{_f(x(12), 31)} C{_f(x(18), 28)} {_f(x(24), 27)} {_f(x(29), 27)}' "
                 f"fill='none' stroke='{INK}' stroke-width='.7'/>")
    # body
    k.append(f"<path d='M50,18 C56,26 56,46 50,64 C44,46 44,26 50,18 Z' fill='{PAPER}' "
             f"stroke='{INK}' stroke-width='{lw}'/>")
    k.append(f"<path d='M50,30 C52.6,36 52.6,46 50,54 C47.4,46 47.4,36 50,30 Z' fill='{INK}'/>")
    k.append(f"<circle cx='50' cy='19' r='5.2' fill='{INK}'/>")
    # bamboo spars
    k.append(f"<path d='M8,29.5 C26,23.5 74,23.5 92,29.5' fill='none' stroke='{INK}' stroke-width='.8'/>")
    k.append(f"<path d='M50,14 L50,62' stroke='{INK}' stroke-width='.6' opacity='.6'/>")
    return "".join(k)


@variant
def kite():
    """纸鸢: the hook of 飞 holds the string of a swallow kite — the kite is a
    Chinese invention of flight (墨子木鸢), the character flies it."""
    # in 飞's em box: hook tip of Noto Serif CJK Bold 飞 at (988, 413) -> y 569.5
    hx, hy = 975, BASE - 430
    kx, ky = 1060, -770          # kite placement (top-left of its 100-unit box)
    ks = 8.2                     # 1 kite unit = 8.2 em units
    bx, by = kx + 47 * ks, ky + 44 * ks          # bridle point (approx, rotated)
    string = (f"<path d='M{_f(hx, hy)} C{_f(hx + 190, hy - 80)} {_f(bx + 40, by + 330)} {_f(bx, by)}' "
              f"fill='none' stroke='{INK}' stroke-width='5' stroke-linecap='round'/>")
    art = (f"<svg viewBox='0 0 1000 1000' width='1em' height='1em'>{string}"
           f"<g transform='translate({_f(kx, ky)}) rotate(16 {50 * ks:.1f} {40 * ks:.1f}) scale({ks})'>"
           f"{swallow_kite()}</g></svg>")
    return cover(title_html=chars(META["title"], lambda i, c: art if i == 4 else ""))


# ---------------------------------------------------------------------------
def wing_fan(n, a0, a1, L0, L1, wo, col):
    """n feathers fanned from angle a0 (shortest) to a1 (longest)."""
    out = []
    for k in range(n):
        t = k / (n - 1)
        L = L0 + (L1 - L0) * t ** .8
        out.append(put(quill(L, wo * (.75 + .25 * t), wo * .35, col, n=16, bend=.04,
                             gaps=((.62, .67),) if k == 2 else ()),
                       0, 0, a0 + (a1 - a0) * t))
    return "".join(out)


@variant
def yuren():
    """羽人: the Han-dynasty 'feathered immortal' — 人 grows a pair of small
    cinnabar wings, as in 羽化登仙."""
    # wing roots just under 人's apex (the apex is at about (470, 150))
    fan = []
    for k in range(6):
        t = k / 5
        ang = 170 + 50 * t                 # from nearly level to up-and-out
        L = 290 + 270 * t ** .9
        fan.append(put(quill(L, 38 + 18 * t, 15, RED, n=32, bend=-.04,
                             gaps=((.58, .62),) if k in (2, 4) else ()), 0, 0, ang))
    w = "".join(fan[::-1])
    left = put(w, 450, 360)
    right = put(f"<g transform='scale(-1,1)'>{w}</g>", 510, 360)
    art = (f"<svg viewBox='0 0 1000 1000' width='1em' height='1em' style='z-index:-1'>"
           f"{left}{right}</svg>")
    return cover(title_html=chars(META["title"], lambda i, c: art if i == 2 else ""))
