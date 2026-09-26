/*
 * 小 Claude 弹钢琴 —— 5 秒无缝循环的 Canvas 动画
 *
 * 每一帧只由循环时间 t ∈ [0, 5) 计算得出：琴键、手、身体、飘起的音符、节拍器
 * 都是 t 的函数，所以第 5 秒和第 0 秒的画面完全一致，循环没有接缝。
 * 乐谱：96 BPM，4/4 拍，2 小节 = 8 拍 = 5 秒，和弦 C - Am - F - G。
 */
(() => {
  'use strict';

  // ---------- 时间与乐谱 ----------
  const LOOP = 5;                  // 循环长度（秒）
  const BPM = 96;
  const BEAT = 60 / BPM;           // 0.625 秒
  const EIGHTH = BEAT / 2;
  const TAU = Math.PI * 2;

  const mod = (a, n) => ((a % n) + n) % n;
  const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
  const lerp = (a, b, k) => a + (b - a) * k;
  const easeOut = k => 1 - Math.pow(1 - k, 3);
  const easeInOut = k => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2);
  // 距离某个事件过去了多久；跨过循环边界时依然连续
  const since = (t, t0) => mod(t - t0, LOOP);

  // 右手：每个和弦 4 个八分音符的琶音
  const MELODY = [64, 67, 72, 67, 69, 72, 76, 72, 65, 69, 72, 69, 67, 71, 74, 71]
    .map((midi, i) => ({ midi, i, t: i * EIGHTH, vel: i % 4 === 0 ? 0.9 : 0.7, ring: 0.8, hand: 'R' }));
  // 左手：每拍一个低音（根音、五度）
  const BASS = [48, 55, 45, 52, 41, 48, 43, 50]
    .map((midi, i) => ({ midi, i, t: i * BEAT, vel: i % 2 === 0 ? 1 : 0.75, ring: 1.3, hand: 'L' }));
  const EVENTS = MELODY.concat(BASS);

  // 飘起来的音符：右手隔一个音飘一个，左手每个低音都飘
  const SPRITES = EVENTS
    .filter(e => e.hand === 'L' || e.i % 2 === 0)
    .map((e, n) => ({
      ...e,
      seed: n * 2.39,
      dir: e.hand === 'L' ? -1 : 1,
      kind: e.hand === 'L' && e.i % 2 === 0 ? 'beamed' : 'eighth',
      color: n % 3,
    }));

  // ---------- 场景尺寸（逻辑坐标 800 × 450） ----------
  const W = 800, H = 450;
  const HORIZON = 300;             // 墙和地板的交界
  const PET_FEET = 404;
  const PIANO_FEET = 419;
  const KB = { x0: 190, top: 334, whiteW: 20, whiteH: 38, blackW: 12, blackH: 23, lip: 5 };
  const CASE = { top: 326, bottom: 386, pad: 18 };
  const HAND_Y = KB.top + KB.whiteH - 11;

  // 琴键：F2 (41) 到 E5 (76)，共 21 个白键
  const keys = [];
  let whiteCount = 0;
  for (let m = 41; m <= 76; m++) {
    const black = [1, 3, 6, 8, 10].includes(m % 12);
    if (black) {
      keys.push({ midi: m, black, x: KB.x0 + whiteCount * KB.whiteW - KB.blackW / 2, w: KB.blackW });
    } else {
      keys.push({ midi: m, black, x: KB.x0 + whiteCount * KB.whiteW, w: KB.whiteW });
      whiteCount++;
    }
  }
  KB.x1 = KB.x0 + whiteCount * KB.whiteW;
  const whiteKeys = keys.filter(k => !k.black);
  const blackKeys = keys.filter(k => k.black);
  const keyByMidi = new Map(keys.map(k => [k.midi, k]));
  const keyCenter = midi => { const k = keyByMidi.get(midi); return k.x + k.w / 2; };

  // 小宠物自己的颜色不随主题变化
  const PET = {
    body: '#D97757',
    shade: '#BD5F3F',
    light: '#EC9B7C',
    eye: '#2A1A13',
    cheek: 'rgba(255, 146, 146, 0.5)',
    rgb: '217, 119, 87',
  };

  const STARS = [[14, 20, 1.3, 1], [40, 70, 1, 2], [58, 22, 1.6, 3], [104, 92, 1.1, 1], [22, 118, 1.2, 2], [76, 132, 1, 3], [110, 128, 1.4, 1]];

  // ---------- 画布 ----------
  const canvas = document.getElementById('stage');
  const ctx = canvas.getContext('2d');
  let scale = 1;
  let dirty = true;

  function resize() {
    const cssW = canvas.getBoundingClientRect().width || W;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(cssW * dpr);
    canvas.height = Math.round(cssW * dpr * H / W);
    scale = canvas.width / W;
    dirty = true;
  }
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(canvas);
  else window.addEventListener('resize', resize);
  resize();

  // 场景颜色来自 CSS 变量，切换深浅色主题时重新读取
  const TOKENS = ['wall', 'wallStripe', 'baseboard', 'floor', 'floorLine', 'rug', 'rugEdge', 'glowRgb', 'glowA',
    'skyTop', 'skyBottom', 'frame', 'night', 'piano', 'pianoHi', 'keyWhite', 'keyShade', 'keyBlack', 'brass',
    'wood', 'woodDark', 'leaf', 'leafDark', 'pot', 'noteA', 'noteB', 'noteC', 'floorShadow'];
  const C = {};
  function readPalette() {
    const cs = getComputedStyle(document.documentElement);
    for (const k of TOKENS) {
      C[k] = cs.getPropertyValue('--' + k.replace(/[A-Z]/g, m => '-' + m.toLowerCase())).trim();
    }
    C.night = parseFloat(C.night) || 0;
    C.glowA = parseFloat(C.glowA) || 0;
    dirty = true;
  }
  readPalette();
  const darkQuery = window.matchMedia('(prefers-color-scheme: dark)');
  if (darkQuery.addEventListener) darkQuery.addEventListener('change', readPalette);
  else darkQuery.addListener(readPalette);
  new MutationObserver(readPalette).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme', 'class', 'style'] });

  // ---------- 绘图小工具 ----------
  function rr(x, y, w, h, r) {
    r = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function blob(cx, cy, rx, ry) {
    ctx.beginPath();
    ctx.ellipse(cx, cy, rx, ry, 0, 0, TAU);
    ctx.fill();
  }

  function noteHead(x, y) {
    ctx.beginPath();
    ctx.ellipse(x, y, 5.4, 4, -0.4, 0, TAU);
    ctx.fill();
  }

  // 以符头为原点画一个八分音符或一对连尾八分音符
  function noteGlyph(kind) {
    if (kind === 'beamed') {
      noteHead(0, 0);
      noteHead(14, -3);
      ctx.fillRect(3.4, -20, 2.2, 19);
      ctx.fillRect(17.4, -23, 2.2, 19);
      ctx.beginPath();
      ctx.moveTo(3.4, -20);
      ctx.lineTo(19.6, -23);
      ctx.lineTo(19.6, -18.5);
      ctx.lineTo(3.4, -15.5);
      ctx.closePath();
      ctx.fill();
    } else {
      noteHead(0, 0);
      ctx.fillRect(3.4, -20, 2.2, 19);
      ctx.beginPath();
      ctx.moveTo(5.6, -20);
      ctx.bezierCurveTo(7.5, -15, 13.5, -14, 11.5, -6);
      ctx.bezierCurveTo(11.5, -11, 8.5, -13, 5.6, -14);
      ctx.closePath();
      ctx.fill();
    }
  }

  // ---------- 房间 ----------
  function drawRoom() {
    ctx.fillStyle = C.wall;
    ctx.fillRect(0, 0, W, HORIZON);
    ctx.fillStyle = C.wallStripe;
    for (let x = 12; x < W; x += 56) ctx.fillRect(x, 0, 22, HORIZON);
    ctx.fillStyle = C.baseboard;
    ctx.fillRect(0, HORIZON - 12, W, 12);

    ctx.fillStyle = C.floor;
    ctx.fillRect(0, HORIZON, W, H - HORIZON);
    ctx.strokeStyle = C.floorLine;
    ctx.lineWidth = 1.5;
    let y = HORIZON, gap = 12, row = 0;
    while (y < H) {
      const prevY = y;
      y += gap;
      gap *= 1.35;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(W, y);
      for (let x = (row % 2) * 70 + 40; x < W; x += 140) {
        ctx.moveTo(x, prevY);
        ctx.lineTo(x, y);
      }
      ctx.stroke();
      row++;
    }
  }

  function cloud(cx, cy, s) {
    blob(cx, cy, 20 * s, 9 * s);
    blob(cx - 13 * s, cy + 3 * s, 12 * s, 7 * s);
    blob(cx + 14 * s, cy + 3 * s, 13 * s, 7 * s);
  }

  function drawWindow(t) {
    const x = 66, y = 50, w = 126, h = 150;
    ctx.fillStyle = C.frame;
    rr(x - 8, y - 8, w + 16, h + 16, 6);
    ctx.fill();
    const sky = ctx.createLinearGradient(0, y, 0, y + h);
    sky.addColorStop(0, C.skyTop);
    sky.addColorStop(1, C.skyBottom);
    ctx.fillStyle = sky;
    ctx.fillRect(x, y, w, h);

    ctx.save();
    ctx.beginPath();
    ctx.rect(x, y, w, h);
    ctx.clip();
    if (C.night > 0) {
      ctx.fillStyle = '#FFF4D6';
      for (const [dx, dy, r, k] of STARS) {
        ctx.globalAlpha = C.night * (0.35 + 0.65 * (0.5 + 0.5 * Math.sin(TAU * k * t / LOOP + dx)));
        blob(x + dx, y + dy, r, r);
      }
      ctx.globalAlpha = C.night * 0.25;
      blob(x + 90, y + 40, 24, 24);
      ctx.globalAlpha = C.night;
      ctx.fillStyle = '#F2E6C2';
      blob(x + 90, y + 40, 14, 14);
    }
    if (C.night < 1) {
      ctx.globalAlpha = 1 - C.night;
      ctx.fillStyle = 'rgba(255, 255, 255, 0.92)';
      cloud(x + 40 + 4 * Math.sin(TAU * t / LOOP), y + 46, 1);
      cloud(x + 92 - 3 * Math.sin(TAU * t / LOOP), y + 104, 0.8);
    }
    ctx.restore();

    ctx.fillStyle = C.frame;
    ctx.fillRect(x + w / 2 - 3, y, 6, h);
    ctx.fillRect(x, y + h / 2 - 3, w, 6);
    rr(x - 14, y + h + 6, w + 28, 8, 3);
    ctx.fill();
  }

  // 墙上裱起来的一小段乐谱
  function drawSheetFrame() {
    const x = 640, y = 64, w = 116, h = 78;
    ctx.fillStyle = C.brass;
    rr(x - 6, y - 6, w + 12, h + 12, 4);
    ctx.fill();
    ctx.fillStyle = C.keyWhite;
    ctx.fillRect(x, y, w, h);
    ctx.strokeStyle = C.keyBlack;
    ctx.globalAlpha = 0.35;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < 5; i++) {
      const ly = y + 24 + i * 7;
      ctx.moveTo(x + 10, ly);
      ctx.lineTo(x + w - 10, ly);
    }
    ctx.stroke();
    ctx.globalAlpha = 0.85;
    ctx.fillStyle = C.keyBlack;
    ctx.save();
    ctx.translate(x + 30, y + 49);
    ctx.scale(0.8, 0.8);
    noteGlyph('eighth');
    ctx.restore();
    ctx.save();
    ctx.translate(x + 64, y + 45.5);
    ctx.scale(0.8, 0.8);
    noteGlyph('beamed');
    ctx.restore();
    ctx.globalAlpha = 1;
  }

  function drawRug() {
    ctx.fillStyle = C.rugEdge;
    blob(400, 408, 272, 30);
    ctx.fillStyle = C.rug;
    blob(400, 408, 258, 25);
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.16)';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 6]);
    ctx.beginPath();
    ctx.ellipse(400, 408, 236, 20, 0, 0, TAU);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // 聚光灯：每个和弦开头轻轻亮一下
  function drawGlow(t) {
    const frac = mod(t / (BEAT * 2), 1);
    const a = C.glowA * (1 + 0.1 * Math.exp(-frac * 6));
    const g = ctx.createRadialGradient(400, 250, 10, 400, 250, 340);
    g.addColorStop(0, `rgba(${C.glowRgb}, ${a})`);
    g.addColorStop(1, `rgba(${C.glowRgb}, 0)`);
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  }

  function drawShadows(p) {
    ctx.fillStyle = C.floorShadow;
    blob(400 + (p.cx - 400) * 0.5, PET_FEET + 1, 86, 6);
    blob(KB.x0 + 13, PIANO_FEET + 1, 20, 4);
    blob(KB.x1 - 13, PIANO_FEET + 1, 20, 4);
    blob(700, 405, 48, 5);
    blob(96, 400, 30, 4);
  }

  function drawPlant(t) {
    const px = 96, top = 354, bottom = 398;
    const leaves = [[-0.95, 62], [-0.58, 82], [-0.22, 94], [0.16, 88], [0.52, 74], [0.9, 58]];
    leaves.forEach(([a, len], i) => {
      ctx.save();
      ctx.translate(px, top + 4);
      ctx.rotate(a + 0.05 * Math.sin(TAU * t / LOOP + i * 0.8));
      ctx.fillStyle = i % 2 ? C.leafDark : C.leaf;
      blob(0, -len / 2, 11, len / 2);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.18)';
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.moveTo(0, -4);
      ctx.lineTo(0, -len + 8);
      ctx.stroke();
      ctx.restore();
    });
    ctx.fillStyle = C.pot;
    ctx.beginPath();
    ctx.moveTo(px - 26, top);
    ctx.lineTo(px + 26, top);
    ctx.lineTo(px + 19, bottom);
    ctx.lineTo(px - 19, bottom);
    ctx.closePath();
    ctx.fill();
    rr(px - 30, top - 4, 60, 10, 3);
    ctx.fill();
    ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
    ctx.fillRect(px - 26, top + 6, 52, 3);
  }

  // 边桌上的节拍器：摆锤在每一拍摆到最边上
  function drawMetronome(t) {
    const tx = 700;
    ctx.fillStyle = C.woodDark;
    ctx.fillRect(tx - 34, 344, 6, 60);
    ctx.fillRect(tx + 28, 344, 6, 60);
    ctx.fillStyle = C.wood;
    rr(tx - 44, 336, 88, 10, 3);
    ctx.fill();

    ctx.fillStyle = C.wood;
    ctx.beginPath();
    ctx.moveTo(tx - 24, 336);
    ctx.lineTo(tx + 24, 336);
    ctx.lineTo(tx + 8, 270);
    ctx.lineTo(tx - 8, 270);
    ctx.closePath();
    ctx.fill();
    ctx.fillStyle = C.keyWhite;
    ctx.globalAlpha = 0.9;
    ctx.beginPath();
    ctx.moveTo(tx - 14, 328);
    ctx.lineTo(tx + 14, 328);
    ctx.lineTo(tx + 5, 282);
    ctx.lineTo(tx - 5, 282);
    ctx.closePath();
    ctx.fill();
    ctx.globalAlpha = 1;
    ctx.strokeStyle = C.woodDark;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
      const ly = 290 + i * 6;
      ctx.moveTo(tx - 3, ly);
      ctx.lineTo(tx + 3, ly);
    }
    ctx.stroke();

    const swing = Math.cos(Math.PI * t / BEAT);
    ctx.save();
    ctx.translate(tx, 322);
    ctx.rotate(0.42 * swing);
    ctx.strokeStyle = C.keyBlack;
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, -52);
    ctx.stroke();
    ctx.fillStyle = C.brass;
    rr(-5.5, -38, 11, 8, 2);
    ctx.fill();
    ctx.restore();
    ctx.fillStyle = C.brass;
    blob(tx, 322, 3, 3);

    // “嗒”的一下：摆到最边上时的小闪光
    const tick = Math.pow(Math.abs(swing), 60);
    if (tick > 0.02) {
      const side = Math.sign(swing);
      const tipX = tx + Math.sin(0.42 * side) * 52, tipY = 322 - Math.cos(0.42) * 52;
      ctx.strokeStyle = PET.body;
      ctx.globalAlpha = tick;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(tipX + side * 6, tipY - 2);
      ctx.lineTo(tipX + side * 12, tipY - 6);
      ctx.moveTo(tipX + side * 7, tipY + 5);
      ctx.lineTo(tipX + side * 14, tipY + 5);
      ctx.stroke();
      ctx.globalAlpha = 1;
    }
  }

  // ---------- 小宠物 ----------
  function petPose(t) {
    const frac = mod(t / BEAT, 1);
    const bounce = Math.sin(Math.PI * frac);                          // 拍点上为 0，拍子中间最高
    const squash = 0.045 * Math.exp(-frac * 7) * Math.min(1, frac * 30); // 拍点上被压扁一下
    const w = 176 * (1 + squash * 0.6);
    const h = 134 * (1 - squash);
    const cx = 400 + 5 * Math.sin(TAU * t / (LOOP / 2));
    const bottom = CASE.bottom - 4 * bounce;
    return { cx, w, h, bottom, top: bottom - h, frac };
  }

  // 眨眼一次；弹到 G 和弦时眯起眼睛陶醉一下
  function eyeState(t) {
    const blink = t - 1.62;
    if (blink >= 0 && blink < 0.16) return { open: Math.abs(Math.cos(Math.PI * blink / 0.16)), happy: false };
    if (t >= 3.62 && t < 3.75) return { open: 1 - (t - 3.62) / 0.13, happy: false };
    if (t >= 3.75 && t < 4.4) return { open: 0, happy: true };
    if (t >= 4.4 && t < 4.53) return { open: (t - 4.4) / 0.13, happy: false };
    return { open: 1, happy: false };
  }

  function drawLegs(p) {
    const tap = 6 * Math.sin(Math.PI * p.frac);   // 最右边那条腿跟着拍子点地
    ctx.fillStyle = PET.shade;
    [-62, -24, 24, 62].forEach((o, i) => {
      const lift = i === 3 ? tap : 0;
      const topX = p.cx + o, botX = 400 + o;
      ctx.beginPath();
      ctx.moveTo(topX - 8, p.bottom - 8);
      ctx.lineTo(topX + 8, p.bottom - 8);
      ctx.lineTo(botX + 8, PET_FEET - lift);
      ctx.lineTo(botX - 8, PET_FEET - lift);
      ctx.closePath();
      ctx.fill();
    });
  }

  function drawBody(p, t) {
    const g = ctx.createLinearGradient(0, p.top, 0, p.bottom);
    g.addColorStop(0, PET.light);
    g.addColorStop(0.3, PET.body);
    g.addColorStop(1, PET.shade);
    ctx.fillStyle = g;
    rr(p.cx - p.w / 2, p.top, p.w, p.h, 14);
    ctx.fill();
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    rr(p.cx - p.w / 2 + 16, p.top + 6, p.w * 0.34, 5, 2.5);
    ctx.fill();

    const eyes = eyeState(t);
    const look = 3 * Math.sin(TAU * t / (LOOP / 2) + 0.6);
    const ey = p.top + 34;
    for (const side of [-1, 1]) {
      const ex = p.cx + side * 36 + look;
      if (eyes.happy) {
        ctx.strokeStyle = PET.eye;
        ctx.lineWidth = 4;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(ex - 8, ey + 4);
        ctx.quadraticCurveTo(ex, ey - 9, ex + 8, ey + 4);
        ctx.stroke();
      } else {
        const h = Math.max(2.5, 24 * eyes.open);
        ctx.fillStyle = PET.eye;
        rr(ex - 6.5, ey - h / 2, 13, h, Math.min(4, h / 2));
        ctx.fill();
        if (eyes.open > 0.6) {
          ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
          rr(ex - 4, ey - h / 2 + 3, 4, 5, 1.5);
          ctx.fill();
        }
      }
      ctx.fillStyle = PET.cheek;
      blob(p.cx + side * 60 + look * 0.5, p.top + 54, 10, 5.5);
    }
  }

  // 一只手在两个音之间：按下、抬起、划一道弧落到下一个键上
  function handPose(events, t, liftMax) {
    let i = events.length - 1;
    for (let j = 0; j < events.length; j++) if (events[j].t <= t) i = j;
    const cur = events[i], next = events[(i + 1) % events.length];
    const gap = mod(next.t - cur.t, LOOP) || LOOP;
    const u = since(t, cur.t) / gap;
    const x0 = keyCenter(cur.midi), x1 = keyCenter(next.midi);
    const HOLD = 0.18;
    if (u < HOLD) return { x: x0, y: HAND_Y + 2 * Math.sin(Math.PI * u / HOLD), tilt: 0 };
    const p = (u - HOLD) / (1 - HOLD);
    const lift = liftMax * next.vel * Math.sin(Math.PI * Math.pow(p, 1.25));
    const tilt = clamp((x1 - x0) / 200, -0.3, 0.3) * Math.sin(Math.PI * p);
    return { x: lerp(x0, x1, easeInOut(p)), y: HAND_Y - lift, tilt };
  }

  function drawArms(p, t) {
    const hands = [
      { side: -1, ...handPose(BASS, t, 30) },
      { side: 1, ...handPose(MELODY, t, 16) },
    ];
    for (const hand of hands) {
      const near = Math.max(0, 1 - (HAND_Y - hand.y) / 30);
      ctx.fillStyle = `rgba(0, 0, 0, ${0.18 * near})`;
      blob(hand.x, HAND_Y + 8, 11, 3);
    }
    ctx.lineCap = 'round';
    ctx.lineWidth = 15;
    for (const hand of hands) {
      const sx = p.cx + hand.side * (p.w / 2 - 8), sy = p.top + 58;
      const qx = lerp(sx, hand.x, 0.72) + hand.side * 6, qy = Math.min(sy, hand.y) - 8;
      ctx.strokeStyle = PET.shade;
      ctx.beginPath();
      ctx.moveTo(sx, sy + 2);
      ctx.quadraticCurveTo(qx, qy + 2, hand.x, hand.y + 2);
      ctx.stroke();
      ctx.strokeStyle = PET.body;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.quadraticCurveTo(qx, qy, hand.x, hand.y);
      ctx.stroke();

      ctx.save();
      ctx.translate(hand.x, hand.y);
      ctx.rotate(hand.tilt);
      ctx.fillStyle = PET.body;
      rr(-10, -6, 20, 13, 6);
      ctx.fill();
      ctx.strokeStyle = PET.shade;
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.moveTo(-3.5, 1);
      ctx.lineTo(-3.5, 6);
      ctx.moveTo(3.5, 1);
      ctx.lineTo(3.5, 6);
      ctx.stroke();
      ctx.restore();
      ctx.lineWidth = 15;
    }
  }

  // ---------- 钢琴 ----------
  function keyStates(t) {
    const states = new Map();
    for (const e of EVENTS) {
      const age = since(t, e.t);
      const dur = e.hand === 'L' ? 0.24 : 0.15;
      const press = age < dur ? 1 - Math.pow(age / dur, 3) : 0;
      const glow = age < 1 ? Math.exp(-age * 4) * e.vel : 0;
      if (press === 0 && glow < 0.01) continue;
      const s = states.get(e.midi) || { press: 0, glow: 0 };
      s.press = Math.max(s.press, press);
      s.glow = Math.max(s.glow, glow);
      states.set(e.midi, s);
    }
    return states;
  }

  function drawPiano(t) {
    const states = keyStates(t);
    const left = KB.x0 - CASE.pad, right = KB.x1 + CASE.pad;

    ctx.fillStyle = C.piano;
    for (const lx of [KB.x0 + 6, KB.x1 - 20]) {
      ctx.fillRect(lx, CASE.bottom - 2, 14, PIANO_FEET - CASE.bottom);
      rr(lx - 5, PIANO_FEET - 4, 24, 5, 2);
      ctx.fill();
    }

    rr(left, CASE.top, right - left, CASE.bottom - CASE.top, 8);
    ctx.fill();
    ctx.fillStyle = C.pianoHi;
    ctx.fillRect(left + 8, CASE.top + 1, right - left - 16, 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.45)';
    ctx.fillRect(KB.x0 - 2, KB.top - 2, KB.x1 - KB.x0 + 4, KB.whiteH + KB.lip + 3);

    for (const k of whiteKeys) {
      const s = states.get(k.midi);
      const dy = s ? s.press * 2.5 : 0;
      ctx.fillStyle = C.keyShade;
      ctx.fillRect(k.x + 0.5, KB.top + KB.whiteH + dy, k.w - 1, KB.lip - dy);
      ctx.fillStyle = C.keyWhite;
      ctx.fillRect(k.x + 0.5, KB.top + dy, k.w - 1, KB.whiteH);
      if (s && s.glow > 0.01) {
        ctx.fillStyle = `rgba(${PET.rgb}, ${0.55 * s.glow})`;
        ctx.fillRect(k.x + 0.5, KB.top + dy, k.w - 1, KB.whiteH);
      }
    }
    for (const k of blackKeys) {
      const s = states.get(k.midi);
      const dy = s ? s.press * 2 : 0;
      ctx.fillStyle = C.keyBlack;
      rr(k.x, KB.top - 1 + dy, k.w, KB.blackH, 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(255, 255, 255, 0.13)';
      ctx.fillRect(k.x + 2, KB.top + dy, k.w - 4, KB.blackH - 6);
    }

    // 按下的键向上透出一点暖光
    for (const [midi, s] of states) {
      if (s.glow < 0.05) continue;
      const x = keyCenter(midi);
      const g = ctx.createRadialGradient(x, KB.top, 0, x, KB.top, 24);
      g.addColorStop(0, `rgba(${PET.rgb}, ${0.4 * s.glow})`);
      g.addColorStop(1, `rgba(${PET.rgb}, 0)`);
      ctx.fillStyle = g;
      ctx.fillRect(x - 24, KB.top - 24, 48, 48);
    }

    ctx.fillStyle = C.brass;
    rr(400 - 18, 379.5, 36, 4, 2);
    ctx.fill();
  }

  // ---------- 飘起来的音符 ----------
  function drawNotes(t) {
    const LIFE = 1.9;
    const colors = [C.noteA, C.noteB, C.noteC];
    for (const s of SPRITES) {
      const age = since(t, s.t);
      if (age > LIFE) continue;
      const p = age / LIFE;
      const x = keyCenter(s.midi) + s.dir * (10 + 46 * easeOut(p)) + 7 * Math.sin(p * TAU * 1.3 + s.seed);
      const y = KB.top - 18 - 150 * easeOut(p);
      const alpha = Math.min(1, age / 0.08) * (1 - Math.pow(p, 2.2));
      const size = 1.15 * (0.6 + 0.4 * easeOut(Math.min(1, age / 0.2)));
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.translate(x, y);
      ctx.rotate(0.22 * Math.sin(p * TAU + s.seed));
      ctx.scale(size, size);
      ctx.fillStyle = colors[s.color];
      noteGlyph(s.kind);
      ctx.restore();
    }
  }

  function draw(t) {
    ctx.setTransform(scale, 0, 0, scale, 0, 0);
    ctx.clearRect(0, 0, W, H);
    const pose = petPose(t);
    drawRoom();
    drawWindow(t);
    drawSheetFrame();
    drawRug();
    drawGlow(t);
    drawShadows(pose);
    drawPlant(t);
    drawMetronome(t);
    drawLegs(pose);
    drawBody(pose, t);
    drawPiano(t);
    drawArms(pose, t);
    drawNotes(t);
  }

  // ---------- 声音（Web Audio 实时合成，需要点击后才能开启） ----------
  let audio = null;
  function ensureAudio() {
    const AC = window.AudioContext || window.webkitAudioContext;
    if (!AC) return null;
    if (!audio) {
      const actx = new AC();
      const master = actx.createGain();
      master.gain.value = 0.32;
      const comp = actx.createDynamicsCompressor();
      master.connect(comp);
      comp.connect(actx.destination);
      audio = { ctx: actx, master };
    }
    if (audio.ctx.state === 'suspended') audio.ctx.resume();
    return audio;
  }

  function playNote(midi, dur, vel) {
    const actx = audio.ctx;
    const t0 = actx.currentTime + 0.005;
    const f = 440 * Math.pow(2, (midi - 69) / 12);
    const amp = actx.createGain();
    amp.gain.setValueAtTime(0.0001, t0);
    amp.gain.exponentialRampToValueAtTime(vel, t0 + 0.006);
    amp.gain.exponentialRampToValueAtTime(vel * 0.3, t0 + 0.18);
    amp.gain.exponentialRampToValueAtTime(0.0001, t0 + dur);
    const tone = actx.createBiquadFilter();
    tone.type = 'lowpass';
    tone.frequency.setValueAtTime(Math.min(9000, f * 10), t0);
    tone.frequency.exponentialRampToValueAtTime(Math.max(500, f * 2.5), t0 + dur);
    const o1 = actx.createOscillator();
    o1.type = 'triangle';
    o1.frequency.value = f;
    const o2 = actx.createOscillator();
    o2.type = 'sine';
    o2.frequency.value = f * 2;
    o2.detune.value = 3;
    const o2Gain = actx.createGain();
    o2Gain.gain.value = 0.25;
    o1.connect(tone);
    o2.connect(o2Gain);
    o2Gain.connect(tone);
    tone.connect(amp);
    amp.connect(audio.master);
    o1.start(t0);
    o2.start(t0);
    o1.stop(t0 + dur + 0.05);
    o2.stop(t0 + dur + 0.05);
  }

  // 事件时间是否落在 (from, to] 里；to < from 表示刚好跨过了循环边界
  function crossed(from, to, et) {
    if (from === to) return false;
    return from < to ? et > from && et <= to : et > from || et <= to;
  }

  function triggerSounds(from, to) {
    for (const e of EVENTS) {
      if (crossed(from, to, e.t)) playNote(e.midi, e.ring, e.vel * (e.hand === 'L' ? 0.55 : 0.4));
    }
  }

  // ---------- 界面 ----------
  const playBtn = document.getElementById('play-toggle');
  const soundBtn = document.getElementById('sound-toggle');
  const playhead = document.getElementById('playhead');
  const clockEl = document.getElementById('clock');
  const positionEl = document.getElementById('position');
  const motionNote = document.getElementById('motion-note');
  const chordCells = [...document.querySelectorAll('[data-chord]')];
  const beatCells = [...document.querySelectorAll('[data-beat]')];

  const ICON = {
    pause: '<svg viewBox="0 0 16 16" aria-hidden="true"><rect x="3.5" y="3" width="3" height="10" rx="1"/><rect x="9.5" y="3" width="3" height="10" rx="1"/></svg>',
    play: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.2v9.6a.6.6 0 0 0 .9.5l7.6-4.8a.6.6 0 0 0 0-1L5.9 2.7a.6.6 0 0 0-.9.5z"/></svg>',
    soundOn: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 6h2.5L8 3v10L4.5 10H2z"/><path d="M10.5 5.5a3.5 3.5 0 0 1 0 5M12.5 3.5a6.3 6.3 0 0 1 0 9" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
    soundOff: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M2 6h2.5L8 3v10L4.5 10H2z"/><path d="M10.5 6l4 4M14.5 6l-4 4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>',
  };

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let playing = !reduceMotion;
  let clock = reduceMotion ? 4 : 0;   // 减少动态效果时停在陶醉的那一帧
  let soundOn = false;
  let last = performance.now();
  let activeBeat = -1;
  if (reduceMotion) motionNote.hidden = false;

  function renderButtons() {
    playBtn.innerHTML = (playing ? ICON.pause : ICON.play) + `<span>${playing ? '暂停' : '播放'}</span>`;
    soundBtn.innerHTML = (soundOn ? ICON.soundOn : ICON.soundOff) + `<span>${soundOn ? '关闭声音' : '开启声音'}</span>`;
  }

  function renderUI(t) {
    playhead.style.left = (t / LOOP * 100).toFixed(3) + '%';
    clockEl.textContent = t.toFixed(2);
    const beat = Math.min(7, Math.floor(t / BEAT));
    if (beat !== activeBeat) {
      activeBeat = beat;
      positionEl.textContent = `第 ${Math.floor(beat / 4) + 1} 小节 · 第 ${beat % 4 + 1} 拍`;
      chordCells.forEach((c, i) => c.classList.toggle('is-active', i === Math.floor(beat / 2)));
      beatCells.forEach((c, i) => c.classList.toggle('is-active', i === beat));
    }
  }

  function setPlaying(v) {
    playing = v;
    last = performance.now();
    if (v) motionNote.hidden = true;
    renderButtons();
    dirty = true;
  }

  playBtn.addEventListener('click', () => setPlaying(!playing));
  canvas.addEventListener('click', () => setPlaying(!playing));
  soundBtn.addEventListener('click', () => {
    if (!soundOn && !ensureAudio()) {
      soundBtn.disabled = true;
      soundBtn.textContent = '这个浏览器不支持声音';
      return;
    }
    soundOn = !soundOn;
    if (soundOn && !playing) setPlaying(true);
    renderButtons();
  });

  function frame(now) {
    const dt = (now - last) / 1000;
    last = now;
    if (playing) {
      const prev = clock;
      clock = mod(clock + Math.min(Math.max(dt, 0), 0.1), LOOP);
      // 切回标签页时 dt 很大，这一帧不补发声音，避免一下子响一串
      if (soundOn && audio && dt < 0.25) triggerSounds(prev, clock);
      dirty = true;
    }
    if (dirty) {
      draw(clock);
      renderUI(clock);
      dirty = false;
    }
    requestAnimationFrame(frame);
  }

  renderButtons();
  requestAnimationFrame(frame);
})();
