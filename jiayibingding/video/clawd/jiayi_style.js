// jiayi_style.js: style frames for 甲乙丙丁 (the chorus), not a finished video.
// World: the five staff lines are five power lines across the sky; Clawd sits on them like a bird, which makes
// Clawd a note on the staff. Rainy indigo dusk for the present, warm ochre dusk for the memory.
(() => {
  const SKY_RAIN = ['#3B4570', '#56608C', '#7A7FA6'], SKY_WARM = ['#E9A15E', '#F0C68A', '#F7E3BE'];
  const YOU = '#4A5A8C', YOU_DK = '#34406A', YOU_LT = '#7F90C2';     // the one who leaves: ink-blue Clawd
  const GAP = 38;                                                       // staff-line spacing

  // five sagging wires from a pole on the left; y of wire i at x
  const P0 = 250, TOP = 430, SAG = 70;
  const wireY = (i, x) => { const k = (x - P0) / (W + 600 - P0); return TOP + i * GAP + SAG * Math.sin(Math.PI * clamp(k)) * 1.0 - 60 * k; };

  function sky(cols, t, key) {
    boilSeed('sky' + key);
    paint(rectPts(-200, -200, W + 400, H + 400), { wash: cols[1], ink: null });
    paint(ellPts(W * .25, H * .1, W * .7, H * .5, 30, 12), { fill: cols[0], fillOp: 120, bleed: .3, tex: .7, ink: null });
    paint(ellPts(W * .8, H * .95, W * .8, H * .45, 30, 12), { fill: cols[2], fillOp: 110, bleed: .3, tex: .6, ink: null });
    paint(ellPts(W * .65, H * .3, W * .35, H * .18, 24, 10), { fill: cols[2], fillOp: 70, bleed: .35, tex: .5, ink: null });
  }
  function city(col, key) {       // far rooftops, pale: depth from colour, not projection
    boilSeed('city' + key);
    const pts = [[-100, H + 50], [-100, 820]];
    for (let i = 0; i < 26; i++) { const x = i * 85 - 60, h = 760 + 90 * hash(i + 7); pts.push([x, h], [x + 70, h]); }
    pts.push([W + 100, 800], [W + 100, H + 50]);
    paint(pts, { fill: col, fillOp: 150, bleed: .08, tex: .6, ink: null });
  }
  function pole(key) {
    boilSeed('pole' + key);
    paint(rectPts(P0 - 22, 300, 44, 900, 2), { wash: '#6B4E3D', ink: PAL.ink, sw: 1.1 });
    paint(rectPts(P0 - 120, TOP - 22, 240, 22, 2), { wash: '#7A5A45', ink: PAL.ink, sw: 1 });
    for (let i = 0; i < 5; i++) paint(ellPts(P0 + 6, TOP + i * GAP + 2, 9, 8, 12), { wash: PAL.cream, ink: PAL.ink, sw: .7 });
  }
  function wires(col, key) {
    for (let i = 0; i < 5; i++) {
      boilSeed('wire' + key + i);
      const P = []; for (let x = P0; x <= W + 200; x += 120) P.push([x, wireY(i, x)]);
      inkLine(P, 1.1, col, 'inkfine', .6);
    }
  }
  function noteBird(x, i, s, col, key, flip = false) {   // a notehead resting on wire i: a note on the staff
    boilSeed('nb' + key);
    const y = wireY(i, x) - s * .55;
    paint(ellPts(x, y, s * 1.25, s * .85, 14, 0, -.35), { wash: col, ink: PAL.ink, sw: .6 });
    inkLine([[x + (flip ? -1 : 1) * s * 1.1, y], [x + (flip ? -1 : 1) * s * 1.1, y - s * 3.4]], .9, PAL.ink, 'ink', 0);
  }
  function rain(t, n, key, col, len = 60) {
    for (let i = 0; i < n; i++) {
      boilSeed('rain' + key + i);
      const x = hash(i) * (W + 300) - 150, y = frac(hash(i + 50) + t * (1.1 + .4 * hash(i + 90))) * (H + 200) - 100;
      inkLine([[x, y], [x - len * .18, y + len]], .45, col, 'inkfine', 0);
    }
  }
  function spark5(x, y, R, col) {   // the five-line spark: five pen strokes crossing, drawn as ten rays
    const L = [1, .74, .9, .7, .95, .78, .97, .72, .87, .76];
    for (let k = 0; k < 10; k++) {
      boilSeed('spark' + k);
      const a = -Math.PI / 2 + k * Math.PI / 5;
      paint(ribbon([[x, y], [x + Math.cos(a) * R * L[k] * .5, y + Math.sin(a) * R * L[k] * .5], [x + Math.cos(a) * R * L[k], y + Math.sin(a) * R * L[k]]], R * .09, R * .05),
        { wash: col, ink: PAL.ink, sw: .7 });
    }
  }
  const sitY = (i, x, u) => wireY(i, x) + 2 * u;   // body rests on the wire, legs dangle below

  // ---------- F1 0:05  intro: alone on the wire in the rain ----------
  function f1(t, lt) {
    camBegin(960, 540, 1.0);
    sky(SKY_RAIN, t, 'r'); city(mixCol(SKY_RAIN[0], PAL.night, .3), 'r'); pole('r'); wires(PAL.ink, 'r');
    [[1420, 1], [1500, 1], [1720, 0], [1650, 3]].forEach(([x, i], k) => noteBird(x, i, 11, PAL.ink, 'f1' + k, k % 2 === 1));
    const u = 26, x = 860, i = 2;
    clawd(x, sitY(i, x, u), u, feel('sad', t, { view: 'q', lookX: .8, lookY: .3, boilKey: 'me' }));
    rain(t, 110, 'f1', mixCol(PAL.cream, SKY_RAIN[1], .45));
    camEnd();
  }
  // ---------- F2 0:29  你我: the memory, warm, side by side, arms linked like a beam ----------
  function f2(t, lt) {
    camBegin(960, 520, 1.08);
    sky(SKY_WARM, t, 'w'); glow(1500, 300, 520, '#FFD28A', .9); city(mixCol(SKY_WARM[0], PAL.clayDk, .25), 'w'); pole('w'); wires(mixCol(PAL.ink, PAL.clayDk, .3), 'w');
    const u = 26, i = 2, xa = 740, xb = 1220;
    clawd(xa, sitY(i, xa, u), u, feel('love', t, { view: 'q', aL: .35, aR: .35, lookX: 1, boilKey: 'me' }));
    clawd(xb, sitY(i, xb, u), u, feel('happy', t + .4, { view: 'q', flip: true, col: YOU, dk: YOU_DK, lt: YOU_LT, aL: .35, aR: .35, lookX: 1, seed: 3, boilKey: 'you' }));
    boilSeed('beam');   // the linked arms read as one beam between two notes
    const ya = sitY(i, xa, u) - 5.2 * u, yb = sitY(i, xb, u) - 5.2 * u;
    paint(ribbon([[xa + 6.2 * u, ya - 14], [(xa + xb) / 2, (ya + yb) / 2 - 34], [xb - 6.2 * u, yb - 14]], 16, 16), { wash: mixCol(PAL.clay, YOU, .5), ink: PAL.ink, sw: 1 });
    camEnd();
  }
  // ---------- F3 0:34  甲乙丙丁: TA hops off along the wire; strangers fill the staff ----------
  function f3(t, lt) {
    camBegin(960, 540, 1.0);
    sky(SKY_RAIN, t, 'r3'); city(mixCol(SKY_RAIN[0], PAL.night, .3), 'r3'); pole('r3'); wires(PAL.ink, 'r3');
    const GREY = '#9C98A6', GDK = '#77738A', GLT = '#C3BFCB';
    [[1010, 1], [1140, 3], [1260, 0], [1370, 2], [1480, 4], [700, 4], [560, 0]].forEach(([x, i], k) =>
      clawd(x, sitY(i, x, 11), 11, { ...feel('neutral', t + k * .37), col: GREY, dk: GDK, lt: GLT, view: 'q', flip: k % 2 === 0, seed: k + 5, boilKey: 'st' + k }));
    const u = 24, x = 820, i = 2;
    clawd(x, sitY(i, x, u), u, feel('confused', t, { view: 'q', lookX: 1, aR: 1.2, boilKey: 'me' }));
    const xb = 1650, ub = 14;   // TA, small and far, walking away, back view
    clawd(xb, sitY(1, xb, ub), ub, { ...feel('neutral', t), view: 'qback', col: YOU, dk: YOU_DK, lt: YOU_LT, walk: t * 3, boilKey: 'you' });
    rain(t, 90, 'f3', mixCol(PAL.cream, SKY_RAIN[1], .45));
    camEnd();
  }
  // ---------- F4 0:47  the highest note: close-up, crying, the spark flares behind ----------
  function f4(t, lt) {
    camBegin(900, 560, 1.55);
    sky(SKY_RAIN, t, 'r4');
    glow(1250, 330, 360, '#FFC98A', .95);
    spark5(1250, 330, 150, PAL.clayLt);
    wires(PAL.ink, 'r4');
    const u = 30, x = 820, i = 2;
    clawd(x, sitY(i, x, u), u, feel('cry', t, { view: 'front', boilKey: 'me' }));
    rain(t, 130, 'f4', mixCol(PAL.cream, SKY_RAIN[1], .35), 80);
    camEnd();
  }
  // ---------- F5 1:14  the last chord: dawn after the rain, alone, and a little hope ----------
  function f5(t, lt) {
    camBegin(960, 540, 1.0);
    sky(['#8E9CC8', '#E8C9A8', '#F6E4C8'], t, 'd'); glow(1560, 700, 600, '#FFD9A0', .8);
    city(mixCol('#8E9CC8', PAL.clayDk, .2), 'd'); pole('d'); wires(mixCol(PAL.ink, PAL.clayDk, .2), 'd');
    const u = 26, i = 2, x = 820;
    clawd(x, sitY(i, x, u), u, feel('hopeful', t, { view: 'q', lookX: .7, lookY: -.3, boilKey: 'me' }));
    boilSeed('rest');   // where TA used to sit: a painted quarter rest, the only trace
    const rx = 1130, ry = wireY(i, rx) - 70, r = 1.3;
    paint(ribbon([[rx - 10 * r, ry - 46 * r], [rx + 12 * r, ry - 20 * r], [rx - 8 * r, ry + 2 * r], [rx + 12 * r, ry + 24 * r]], 11 * r, 11 * r), { wash: YOU, ink: PAL.ink, sw: .9 });
    paint(ribbon([[rx + 12 * r, ry + 24 * r], [rx - 6 * r, ry + 22 * r], [rx - 10 * r, ry + 34 * r], [rx - 2 * r, ry + 46 * r]], 9 * r, 5 * r), { wash: YOU, ink: PAL.ink, sw: .9 });
    camEnd();
  }

  // ================= Dot and the Line (1965) style: flat modernist colour fields =================
  // A note is literally a dot and a line. 你 = the clay dot, 我 = the black line. Together they make a note.
  const TEAL = '#2E8C87', MUST = '#E3A83D', OFFW = '#F2E8D2', DEEP = '#2B3350', MAG = '#B8466B';
  function dlStaff(x0, x1, y0, gap, col, key) { for (let i = 0; i < 5; i++) { boilSeed('dls' + key + i); inkLine([[x0, y0 + i * gap], [x1, y0 + i * gap]], 1.6, col, 'rotring', 0); } }
  function dl1(t, lt) {
    camBegin(960, 540, 1);
    boilSeed('dl1bg');
    paint(rectPts(-20, -20, W + 40, H + 40), { wash: TEAL, fill: mixCol(TEAL, DEEP, .3), fillOp: 60, bleed: .05, tex: .9, ink: null });
    paint(rectPts(1180, 120, 560, 840, 2), { wash: MUST, fill: mixCol(MUST, PAL.clayDk, .3), fillOp: 50, bleed: .05, tex: .8, ink: null });
    paint(ellPts(360, 250, 120, 120, 30, 1), { wash: OFFW, ink: null });
    dlStaff(-40, W + 40, 560, 46, OFFW, 'a');
    boilSeed('dl1dot');   // the dot (你): a notehead
    paint(ellPts(900, 698, 62, 44, 30, 1, -.35), { wash: PAL.clay, fill: PAL.clayDk, fillOp: 40, bleed: .04, tex: .6, ink: null });
    boilSeed('dl1line');  // the line (我): stands beside the dot, leaning in, one pixel from becoming a stem
    paint(ribbon([[962, 690], [966, 480], [968, 300]], 11, 11), { wash: PAL.ink, ink: null });
    boilSeed('dl1flag'); paint(ribbon([[968, 300], [1010, 360], [1040, 430], [1020, 500]], 16, 6), { wash: PAL.ink, ink: null });
    camEnd();
  }
  function dl2(t, lt) {
    camBegin(960, 540, 1);
    boilSeed('dl2bg');
    paint(rectPts(-20, -20, W + 40, H + 40), { wash: DEEP, fill: mixCol(DEEP, MAG, .25), fillOp: 70, bleed: .05, tex: .9, ink: null });
    paint(rectPts(-20, 760, W + 40, 360, 2), { wash: MAG, fill: mixCol(MAG, DEEP, .4), fillOp: 60, bleed: .04, tex: .8, ink: null });
    // the line, alone, folds itself into a whole staff and a cage of angles: exhausting every shape it knows
    const P = [[180, 820]]; let x = 240;
    for (let k = 0; k < 7; k++) { P.push([x, 330], [x + 70, 330], [x + 70, 760], [x + 140, 760]); x += 140; }
    P.push([x + 60, 540], [x + 360, 540]);
    boilSeed('dl2line'); inkLine(P, 2.2, OFFW, 'rotring', 0);
    for (let i = 0; i < 5; i++) { boilSeed('dl2s' + i); inkLine([[240, 420 + i * 60], [1230, 420 + i * 60]], .9, OFFW, 'rotring', 0); }
    boilSeed('dl2dot');   // the dot, small and far, rolling away off the right edge
    paint(ellPts(1760, 520, 40, 28, 26, 1, -.35), { wash: PAL.clay, fill: PAL.clayDk, fillOp: 40, bleed: .04, tex: .6, ink: null });
    for (let k = 1; k < 5; k++) { boilSeed('dl2trail' + k); paint(ellPts(1760 - k * 58, 526 + k * 2, 6 - k, 5 - k * .8, 10), { wash: mixCol(PAL.clay, DEEP, k * .18), ink: null }); }
    camEnd();
  }

  // ================= Father and Daughter (2000) style: sepia washes, charcoal, long shadows =================
  const SEP = ['#E9DCC0', '#CDB892', '#9E875F', '#5E4B33', '#3A2E22'];
  function fdGround(key, dry = false) {
    boilSeed('fdsky' + key);
    paint(rectPts(-20, -20, W + 40, 700, 0), { wash: SEP[0], fill: SEP[1], fillOp: 60, bleed: .2, tex: .7, ink: null,
      hatch: { d: 14, a: .15, o: { rand: .5, gradient: .5 }, b: 'charcoal', c: SEP[1], w: .5 } });
    boilSeed('fdland' + key);
    paint(rectPts(-20, 640, W + 40, 480, 0), { wash: dry ? SEP[1] : SEP[2], fill: SEP[3], fillOp: 50, bleed: .08, tex: .8, ink: null });
    for (let i = 0; i < 5; i++) { boilSeed('fdfur' + key + i); inkLine([[-40, 700 + i * 34 + i * i * 6], [W + 40, 690 + i * 34 + i * i * 6]], .6, SEP[3], 'charcoal', .2); }
  }
  function poplars(key) {
    for (let k = 0; k < 9; k++) {
      boilSeed('pop' + key + k);
      const x = 980 + k * 95 + 20 * hash(k), h = 210 + 60 * hash(k + 9);
      paint(ellPts(x, 640 - h / 2, 20, h / 2, 16, 2), { wash: SEP[3], fill: SEP[4], fillOp: 60, bleed: .06, tex: .7, ink: null });
      inkLine([[x, 640 - 30], [x, 648]], .7, SEP[4], 'charcoal', 0);
    }
  }
  function figure(x, y, s, key) {   // a small silhouette, and a long evening shadow
    boilSeed('fig' + key);
    paint([[x + 4, y], [x - 380 * s, y + 70 * s], [x - 390 * s, y + 84 * s], [x - 4, y + 6]], { wash: SEP[3], washOp: 120, ink: null });
    paint([[x - 12 * s, y], [x + 12 * s, y], [x + 16 * s, y - 60 * s], [x + 10 * s, y - 92 * s], [x - 10 * s, y - 92 * s], [x - 16 * s, y - 60 * s]], { wash: SEP[4], ink: null });
    paint(ellPts(x, y - 104 * s, 11 * s, 12 * s, 14), { wash: SEP[4], ink: null });
  }
  function fd1(t, lt) {
    camBegin(960, 540, 1);
    fdGround('a'); poplars('a');
    glow(420, 520, 260, '#FFE6B0', .35);
    figure(700, 700, 1, 'a');
    for (let k = 0; k < 6; k++) { boilSeed('fdbird' + k); const x = 520 + k * 60 + 30 * hash(k), y = 260 + 40 * hash(k + 3) - k * 14;
      inkLine([[x - 12, y + 4], [x, y], [x + 12, y + 4]], .7, SEP[4], 'charcoal', .6); }
    camEnd();
  }
  function fd2(t, lt) {   // sunset behind the poplars: five long tree shadows lie across the field like a staff
    camBegin(960, 540, 1);
    fdGround('b', true);
    glow(1480, 600, 420, '#FFD9A0', .75);
    poplars('b');
    const bases = [1075, 1265, 1455, 1645, 1835];
    bases.forEach((bx, k) => { boilSeed('fdsh' + k);
      paint([[bx - 14, 646], [bx + 14, 646], [bx - 1300, 900 + k * 40], [bx - 1340, 918 + k * 40]], { wash: SEP[3], washOp: 150, ink: null }); });
    // the figure stands on the middle shadow line, a note on a staff made of light
    const k = 2, fx = 820, fy = 646 + (900 + k * 40 - 646) * ((bases[k] - fx) / 1300) + 4;
    figure(fx, fy, .9, 'b');
    camEnd();
  }

  const blank = () => paint(rectPts(-10, -10, W + 20, H + 20), { wash: PAL.paper, ink: null });   // cheap first frame: the page draws t=0 on load
  shots([[0, blank], [1, f1], [11, f2], [21, f3], [31, f4], [41, f5], [51, dl1], [61, dl2], [71, fd1], [81, fd2]]);
})();
