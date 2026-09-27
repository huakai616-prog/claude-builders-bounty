// jiayi_clip.js: a 10-second test clip for 甲乙丙丁, song time 28.0–38.0 (the DEMO's chorus entry).
// Storyboard: jiayibingding/video/clawd/STORYBOARD_28-38.md. Needs lite.js loaded first.
// World: five power lines across the sky are the staff; Clawd sitting on them is a note. Memory is warm dusk, the
// present is rainy indigo. Clawd (clay) and TA (ink-blue) hold hands like a beam between two notes, until the rain.
(() => {
  const SKY_WARM = ['#E9A15E', '#F0C68A', '#F7E3BE'], SKY_RAIN = ['#3B4570', '#56608C', '#7A7FA6'];
  const YOU = { col: '#4A5A8C', dk: '#34406A', lt: '#7F90C2' }, GREY = { col: '#A29EAB', dk: '#7C788D', lt: '#C8C4D0' };
  const GAP = 38, P0 = 250, TOP = 430, SAG = 70, WIRE = 2;
  const wireY = (i, x) => { const k = (x - P0) / (W + 600 - P0); return TOP + i * GAP + SAG * Math.sin(Math.PI * clamp(k)) - 60 * k; };
  const sitY = (i, x, u) => wireY(i, x) + 2 * u;   // body rests on the wire, legs dangle below
  // song times (seconds), from the score: 你 我 | 怎么两清 | 怎么忍心 | 怎么做回 | 甲 乙 丙 丁 | 难道
  const T_YOU = 28.615, T_ME = 29.077, T_HIT = 30.231, T_TURN = 30.923, T_UP = 31.35, T_WALK = 31.6,
        T_JIA = 33.231, T_YI = 33.923, T_BING = 34.385, T_DING = 34.846, T_ANS = 35.077, T_NAN = 36.0, T_OUT = 37.45, T_END = 38.0;
  const U = 26, XA = 790, XB = 1160;

  // ---------- set pieces ----------
  function skyPaint(cols, warm) {   // painted once per shot and reused (see cachedBackground in lite.js)
    boilSeed('sky' + (warm ? 'w' : 'r'));
    paint(rectPts(-200, -200, W + 400, H + 400), { wash: cols[1], ink: null });
    paint(ellPts(W * .25, H * .1, W * .7, H * .5, 30, 12), { fill: cols[0], fillOp: 120, bleed: .3, tex: .7, ink: null });
    paint(ellPts(W * .8, H * .95, W * .8, H * .45, 30, 12), { fill: cols[2], fillOp: 110, bleed: .3, tex: .6, ink: null });
    paint(ellPts(W * .65, H * .3, W * .35, H * .18, 24, 10), { fill: cols[2], fillOp: 70, bleed: .35, tex: .5, ink: null });
    if (warm) glow(1500, 300, 520, '#FFD28A', .9);
    boilSeed('city' + (warm ? 'w' : 'r'));
    const pts = [[-100, H + 50], [-100, 820]];
    for (let i = 0; i < 26; i++) { const x = i * 85 - 60, h = 760 + 90 * hash(i + 7); pts.push([x, h], [x + 70, h]); }
    pts.push([W + 100, 800], [W + 100, H + 50]);
    paint(pts, { fill: warm ? mixCol(cols[0], PAL.clayDk, .25) : mixCol(cols[0], PAL.night, .3), fillOp: 150, bleed: .08, tex: .6, ink: null });
  }
  function poleWires(key, inkCol) {
    boilSeed('pole' + key);
    paint(rectPts(P0 - 22, 300, 44, 900, 2), { wash: '#6B4E3D', ink: PAL.ink, sw: 1.1 });
    boilSeed('arm' + key);
    paint(rectPts(P0 - 120, TOP - 22, 240, 22, 2), { wash: '#7A5A45', ink: PAL.ink, sw: 1 });
    for (let i = 0; i < 5; i++) { boilSeed('ins' + key + i); paint(ellPts(P0 + 6, TOP + i * GAP + 2, 9, 8, 12), { wash: PAL.cream, ink: PAL.ink, sw: .7 }); }
    for (let i = 0; i < 5; i++) {
      boilSeed('wire' + key + i);
      const P = []; for (let x = P0; x <= W + 400; x += 120) P.push([x, wireY(i, x)]);
      inkLine(P, 1.1, inkCol, 'inkfine', .6);
    }
  }
  function rain(t, n, col, len = 70) {   // screen space, nearer than everything
    for (let i = 0; i < n; i++) {
      boilSeed('rain' + i);
      const x = hash(i) * (W + 300) - 150, y = frac(hash(i + 50) + t * (1.1 + .4 * hash(i + 90))) * (H + 200) - 100;
      inkLine([[x, y], [x - len * .18, y + len]], .45, col, 'inkfine', 0);
    }
  }
  const dropPts = (x, y, r) => { const P = [[x, y - 2.2 * r]]; for (let a = -25; a <= 205; a += 15) P.push([x + r * Math.cos(a * Math.PI / 180), y + r * Math.sin(a * Math.PI / 180)]); return P; };
  // world position of an arm tip, following clawd()'s own transform (translate, rotate, flip/squash scale)
  function armTip(x, y, u, o, which) {
    const VV = { front: { R: [4.9, 1], L: [-4.9, -1] }, q: { R: [5, 1], L: [-4.7, -1] } }, V = VV[o.view || 'front'] || VV.q;
    const [px, dir] = V[which], a = which === 'L' ? (o.aL ?? .2) : (o.aR ?? .2);
    const slide = dir * .55 * clamp((Math.abs(a) - .7) / .9), sq = (o.sq || 0) + (o.take || 0);
    let lx = (px + slide) * u + dir * 2.2 * u * Math.cos(a), ly = -4.5 * u - 2.2 * u * Math.sin(a);
    lx *= (o.flip ? -1 : 1) * (o.sx ?? 1) * (1 + sq * .6); ly *= (o.sy ?? 1) * (1 - sq);
    const r = o.rot || 0, c = Math.cos(r), s = Math.sin(r);
    return [x + (o.dx || 0) * u + lx * c - ly * s, y + (o.dy || 0) * u + lx * s + ly * c];
  }
  const link = (a, b, key, w = .7 * U) => { boilSeed(key); paint(ribbon([a, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 5], b], w, w), { wash: mixCol(PAL.clay, YOU.col, .5), ink: PAL.ink, sw: .9 }); };

  // ---------- A 28.00–30.23  the memory: warm dusk, holding hands ----------
  function shotA(t, lt, dur) {
    if (!BG_CACHE.rain) cachedBackground('rain', () => skyPaint(SKY_RAIN, false));   // first frame is under the closed iris
    cachedBackground('warm', () => skyPaint(SKY_WARM, true));
    camBegin(960 + 10 * Math.sin(lt * .5), 505, 1.04 + .012 * lt);
    poleWires('w', mixCol(PAL.ink, PAL.clayDk, .3));
    const ya = sitY(WIRE, XA, U), yb = sitY(WIRE, XB, U);
    const me = emotions(t, [[27, 'happy', { lookX: -.3 }], [T_ME, 'love', { lookX: 1 }]], { take: .6 });
    const you = emotions(t, [[27, 'happy', { lookX: -.3 }], [T_YOU, 'happy', { eyes: 'normal', mouth: 'cat', lookX: 1, blush: .6 }]], { take: .5 });
    const oa = { ...me, view: 'q', aR: .28 + .04 * Math.sin(t * 2.1), boilKey: 'me', noShadow: true };
    const ob = { ...you, view: 'q', flip: true, ...YOU, aR: .28 + .04 * Math.sin(t * 2.1 + 1), seed: 3, boilKey: 'you', noShadow: true };
    clawd(XA, ya, U, oa); clawd(XB, yb, U, ob);
    const ta = armTip(XA, ya, U, oa, 'R'), tb = armTip(XB, yb, U, ob, 'R');
    link(ta, tb, 'link');
    const mid = [(ta[0] + tb[0]) / 2, (ta[1] + tb[1]) / 2 - 8];
    if (t > 29.35) {   // one bright drop falls straight onto the joined hands: the eye follows it down
      const fall = x => Math.pow(seg(x, 29.35, T_HIT), 1.8), y = lerp(40, mid[1] - 22, fall(t)), yPrev = lerp(40, mid[1] - 22, fall(t - .08));
      glow(mid[0], y, 110, '#FFFFFF', .8);
      if (y - yPrev > 4) { boilSeed('streak'); inkLine([[mid[0], yPrev - 30], [mid[0], y - 40]], .7, '#EAF3FA', 'inkfine', 0); }
      boilSeed('drop'); paint(dropPts(mid[0], y, 20), { wash: '#DCEBF7', ink: PAL.ink, sw: 1 });
    }
    const at = toScreen(960, 380);
    camEnd();
    boilSeed('transition');
    if (lt < .55) iris(...at, lerp(0, 1700, easeIn(lt / .55)));
  }

  // ---------- B 30.23–38.00  the present: the rain breaks it, TA leaves, strangers fill the staff ----------
  function shotB(t, lt, dur) {
    cachedBackground('rain', () => skyPaint(SKY_RAIN, false));
    const push = ease(seg(t, T_NAN, T_OUT + .3));
    camBegin(lerp(960, 820, push) + 8 * Math.sin(lt * .5), lerp(505, 470, push), lerp(1.07, 1.3, push));
    poleWires('r', PAL.ink);

    // strangers: one per syllable of 甲乙丙丁, dropping in from the upper right like birds, squashing as they land
    [[T_JIA, 1360, 1, 20], [T_YI, 1570, 3, 20], [T_BING, 1770, 0, 20], [T_DING, XB, WIRE, U]].forEach(([tl, x, wi, us], k) => {
      if (t < tl - .45) return;
      const gy = sitY(wi, x, us), j = jump(t, tl - .45, tl, 0);
      const p = t < tl ? arcPt([x + 300, -160], [x, gy], 110, easeIn(seg(t, tl - .45, tl))) : [x, gy];
      clawd(p[0], p[1], us, { ...feel('neutral', t + k * .37), ...GREY, view: 'front', sq: j.sq, dy: 0, seed: k + 5, boilKey: 'st' + k, noShadow: true });
    });

    // TA: blank, arm drops, turns away through its back, stands up and walks off along the wire
    const youMood = { ...feel('neutral', t), ...YOU, seed: 3, boilKey: 'you', noShadow: true };
    let xb = XB, yb = sitY(WIRE, XB, U), ob;
    if (t < T_TURN) ob = { ...youMood, view: 'q', flip: true, aR: lerp(.28, -.45, ease(seg(t, T_HIT, T_HIT + .35))) + .5 * spring(t, T_HIT, 5, 16) };
    else if (t < T_UP) ob = { ...youMood, ...turn(t, T_TURN, T_TURN + .35, -.125, -.75) };
    else {
      const w = stroll(t, T_WALK, 34.7, XB, XB + 960, U), rise = ease(seg(t, T_UP, T_WALK));
      xb = w.x; yb = lerp(sitY(WIRE, XB, U), wireY(WIRE, xb), rise);
      ob = { ...youMood, view: 'side', walk: w.walk, dy: (w.dy || 0) + jump(t, T_UP, T_WALK, .6).dy, sq: jump(t, T_UP, T_WALK, .6).sq };
    }
    if (xb < 2150) clawd(xb, yb, U, ob);

    // Clawd: startled, then hurt; reaches after TA, lets the arm fall; looks for TA among strangers; rain cloud
    const ya = sitY(WIRE, XA, U);
    const me = emotions(t, [[29, 'love'], [T_HIT + .03, 'surprised', { lookX: 1 }], [31.4, 'sad', { lookX: 1, emote: null }],
                            [T_ANS, 'confused'], [T_NAN, 'sad', { lookX: .2 }]]);
    const oa = { ...me, view: 'q', boilKey: 'me', noShadow: true };
    const reach = ease(seg(t, 31.6, 31.95)) * (1 - ease(seg(t, 33.0, 33.5)));
    if (t > 31.45 && t < 33.6) {
      Object.assign(oa, t < 33.4 ? turn(t, 31.45, 31.6, .125, .25) : turn(t, 33.4, 33.55, .25, .125));
      oa.aL = lerp(-.4, .75, reach); oa.dx = (oa.dx || 0) + .4 * reach; oa.rot = (oa.rot || 0) + .04 * reach;
    }
    if (t > T_ANS && t < T_NAN) oa.lookX = Math.cos((t - T_ANS) * 7.5);
    clawd(XA, ya, U, oa);

    // the broken link: two stubs spring back with the arms, and a splash where the drop hit
    const snap = ease(seg(t, T_HIT, T_HIT + .4));
    if (snap < 1) {
      const ta = armTip(XA, ya, U, oa, 'R'), tbx = armTip(XB, sitY(WIRE, XB, U), U, { ...ob, view: 'q', flip: true }, 'R');
      const mid = [(ta[0] + tbx[0]) / 2, (ta[1] + tbx[1]) / 2 - 8];
      link(ta, [lerp(mid[0] - 6, ta[0], snap), lerp(mid[1], ta[1], snap)], 'stubA', .6 * U * (1 - snap * .5));
      if (t < T_TURN) link(tbx, [lerp(mid[0] + 6, tbx[0], snap), lerp(mid[1], tbx[1], snap)], 'stubB', .6 * U * (1 - snap * .5));
      for (let k = 0; k < 7; k++) {
        const ang = -Math.PI * (.15 + .7 * k / 6), q = seg(t, T_HIT, T_HIT + .5);
        const p = arcPt(mid, [mid[0] + Math.cos(ang) * 150, mid[1] + 90], 110 * (.6 + .4 * hash(k)), q);
        boilSeed('splash' + k); paint(dropPts(p[0], p[1], 6 * (1 - q * .6)), { wash: '#DCEBF7', ink: PAL.ink, sw: .5 });
      }
    }
    const at = toScreen(XA, ya - 4 * U);
    camEnd();
    rain(t, 90, mixCol(PAL.cream, SKY_RAIN[1], .45));
    flash(1 - seg(t, T_HIT, T_HIT + .14), '#FFF6E6');
    boilSeed('transition');
    if (t > T_OUT) iris(...at, lt >= dur - .06 ? 0 : lerp(1700, 0, easeIn(seg(t, T_OUT, T_END - .06))));
  }

  const blank = () => paint(rectPts(-10, -10, W + 20, H + 20), { wash: PAL.paper, ink: null });   // cheap t=0 frame
  shots([[0, blank], [28.0, shotA], [T_HIT, shotB], [T_END, blank]]);
})();
