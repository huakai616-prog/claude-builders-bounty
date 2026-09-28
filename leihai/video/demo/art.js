// Refined character art: the girl (《半把伞》) and the dog (《等潮》). Canvas 2D, any size.
const cv = document.getElementById('c'), ctx = cv.getContext('2d'), W = cv.width, H = cv.height;
let _s = 3; const seed = s => { _s = s; };
const rnd = () => (_s = (_s * 1664525 + 1013904223) % 4294967296) / 4294967296;
const gauss = () => { let u = 0; while (!u) u = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rnd()); };
const OUT = '#3b2a22';
function layer(w = W, h = H) { const c = document.createElement('canvas'); c.width = w; c.height = h; return [c, c.getContext('2d')]; }
function vg(g, y0, y1, stops) { const l = g.createLinearGradient(0, y0, 0, y1); stops.forEach(([t, c]) => l.addColorStop(t, c)); return l; }
function lg(g, x0, y0, x1, y1, stops) { const l = g.createLinearGradient(x0, y0, x1, y1); stops.forEach(([t, c]) => l.addColorStop(t, c)); return l; }
function rg(g, x, y, r0, r1, stops) { const l = g.createRadialGradient(x, y, r0, x, y, r1); stops.forEach(([t, c]) => l.addColorStop(t, c)); return l; }
function blurDraw(dst, src, px, op = 'source-over', a = 1) { dst.save(); dst.filter = `blur(${px}px)`; dst.globalCompositeOperation = op; dst.globalAlpha = a; dst.drawImage(src, 0, 0); dst.restore(); }
function ink(w) { ctx.strokeStyle = OUT; ctx.lineWidth = w; ctx.lineJoin = 'round'; ctx.lineCap = 'round'; ctx.stroke(); }
function E(x, y, rx, ry, r = 0) { ctx.beginPath(); ctx.ellipse(x, y, rx, ry, r, 0, Math.PI * 2); }
function P(pts, close = true) { ctx.beginPath(); ctx.moveTo(...pts[0]); for (let i = 1; i < pts.length; i++) { const p = pts[i]; if (p.length === 2) ctx.lineTo(...p); else if (p.length === 4) ctx.quadraticCurveTo(...p); else ctx.bezierCurveTo(...p); } if (close) ctx.closePath(); }
function glow(x, y, r, col, a = 0.5, op = 'screen') { ctx.save(); ctx.globalCompositeOperation = op; ctx.fillStyle = rg(ctx, x, y, 0, r, [[0, `rgba(${col},${a})`], [1, `rgba(${col},0)`]]); ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore(); }
function groundShadow(x, y, rx, a = 0.35) { ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.2); ctx.fillStyle = rg(ctx, 0, 0, 0, rx, [[0, `rgba(50,35,30,${a})`], [1, 'rgba(50,35,30,0)']]); ctx.fillRect(-rx, -rx, 2 * rx, 2 * rx); ctx.restore(); }
function finish({ bloom = 0.22, vignette = 0.3, grain = 8 } = {}) {
  const [c, g] = layer(); g.drawImage(cv, 0, 0);
  ctx.save(); ctx.filter = 'blur(16px) brightness(1.12)'; ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = bloom; ctx.drawImage(c, 0, 0); ctx.restore();
  ctx.fillStyle = rg(ctx, W / 2, H / 2, Math.min(W, H) * 0.45, Math.max(W, H) * 0.75, [[0, 'rgba(30,20,40,0)'], [1, `rgba(30,20,40,${vignette})`]]); ctx.fillRect(0, 0, W, H);
  const img = ctx.getImageData(0, 0, W, H), d = img.data; for (let i = 0; i < d.length; i += 4) { const n = (rnd() - 0.5) * grain; d[i] += n; d[i + 1] += n; d[i + 2] += n; } ctx.putImageData(img, 0, 0);
}
function rain(n, a = 0.35, len = 26, angle = 0.22, x0 = 0, y0 = 0, x1 = W, y1 = H) {
  ctx.save(); ctx.lineCap = 'round';
  for (let i = 0; i < n; i++) { const x = x0 + rnd() * (x1 - x0), y = y0 + rnd() * (y1 - y0), l = len * (0.5 + rnd()), near = rnd();
    ctx.strokeStyle = `rgba(235,242,248,${a * (0.4 + near * 0.8)})`; ctx.lineWidth = 0.8 + near * 1.4;
    ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - l * Math.sin(angle), y + l * Math.cos(angle)); ctx.stroke(); }
  ctx.restore();
}

// =====================================================================
// The girl: bob hair, mustard raincoat, red boots, clear umbrella
// (x, y) = point between her feet on the ground; s = scale (1 => ~430 px tall)
// opts: view 'front' | 'back'; arm 'down' | 'umbrella'; face 'neutral'|'up'|'closed'|'smile'|'sad'
//       wet: darken her left shoulder; umb: {tilt} umbrella tilt in radians (+ = to her right)
// =====================================================================
const G = { skin: '#f7dccb', skinS: '#e9bda6', hair: '#3f2a24', hairL: '#6a4638', coat: '#efbd4d', coatS: '#cf9630', coatL: '#fbe09a', boot: '#c0463a', bootS: '#8f2e27', sock: '#f4f1ea' };
function girlUmbrella(hx, hy, s, tilt) {
  ctx.save(); ctx.translate(hx, hy); ctx.rotate(tilt); ctx.scale(s, s); ctx.translate(0, -170);
  // shaft + J handle
  ctx.strokeStyle = '#5b4a40'; ctx.lineWidth = 4; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(0, -8); ctx.lineTo(0, 196); ctx.arc(-9, 196, 9, 0, Math.PI * 0.9); ctx.stroke();
  // canopy: clear dome with ribs, lit from the upper left
  const R = 175, Hc = 120;
  ctx.beginPath(); ctx.moveTo(-R, 26); ctx.bezierCurveTo(-R, -Hc * 0.7, -R * 0.45, -Hc, 0, -Hc); ctx.bezierCurveTo(R * 0.45, -Hc, R, -Hc * 0.7, R, 26);
  for (let k = 5; k >= 0; k--) { const x1 = -R + (2 * R) * k / 6, x0 = -R + (2 * R) * (k + 1) / 6; ctx.quadraticCurveTo((x0 + x1) / 2, 12, x1, 26); }
  ctx.closePath();
  ctx.fillStyle = lg(ctx, -R, -Hc, R, 30, [[0, 'rgba(245,250,255,0.55)'], [0.5, 'rgba(200,220,235,0.32)'], [1, 'rgba(160,190,210,0.4)']]); ctx.fill();
  ctx.strokeStyle = 'rgba(70,90,110,0.85)'; ctx.lineWidth = 2.4; ctx.stroke();
  ctx.strokeStyle = 'rgba(90,110,130,0.55)'; ctx.lineWidth = 1.4;
  for (let k = 0; k <= 6; k++) { const xe = -R + (2 * R) * k / 6; ctx.beginPath(); ctx.moveTo(0, -Hc); ctx.quadraticCurveTo(xe * 0.75, -Hc * 0.55, xe, 26); ctx.stroke(); }
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.strokeStyle = 'rgba(255,255,255,0.8)'; ctx.lineWidth = 6; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(-R * 0.72, -Hc * 0.35); ctx.quadraticCurveTo(-R * 0.55, -Hc * 0.85, -R * 0.15, -Hc * 0.97); ctx.stroke(); ctx.restore();
  // raindrops beading on the canopy
  for (let i = 0; i < 26; i++) { const t = rnd() * 2 - 1, xx = t * R * 0.9, yy = -Hc * (1 - t * t) * 0.9 + rnd() * 30; ctx.fillStyle = 'rgba(255,255,255,0.8)'; E(xx, yy, 2.2, 3); ctx.fill(); ctx.fillStyle = 'rgba(80,100,120,0.35)'; E(xx + 0.8, yy + 1.2, 1.4, 1.8); ctx.fill(); }
  ctx.fillStyle = '#5b4a40'; E(0, -Hc - 6, 5, 7); ctx.fill();
  ctx.restore();
}
function girlFace(face, s) {
  // eyes
  const ey = -324, ex = 23;
  if (face === 'closed' || face === 'smile') {
    ctx.strokeStyle = '#2d1c18'; ctx.lineWidth = 3.2; ctx.lineCap = 'round';
    for (const sx of [-1, 1]) { ctx.beginPath(); if (face === 'closed') ctx.arc(sx * ex, ey - 4, 10, 0.15 * Math.PI, 0.85 * Math.PI); else ctx.arc(sx * ex, ey + 8, 10, 1.15 * Math.PI, 1.85 * Math.PI); ctx.stroke(); }
  } else {
    const up = face === 'up' ? -5 : 0;
    for (const sx of [-1, 1]) {
      ctx.fillStyle = '#fffaf6'; E(sx * ex, ey, 11, 13); ctx.fill();
      ctx.fillStyle = rg(ctx, sx * ex, ey + 2 + up, 1, 12, [[0, '#6b3f2c'], [0.6, '#3a2119'], [1, '#1f120e']]); E(sx * ex, ey + 2 + up, 9, 11.5); ctx.fill();
      ctx.fillStyle = '#fff'; E(sx * ex - 3, ey - 3 + up, 3.2, 3.8); ctx.fill(); E(sx * ex + 3.5, ey + 6 + up, 1.5, 1.6); ctx.fill();
      ctx.strokeStyle = '#2d1c18'; ctx.lineWidth = 3.4; ctx.beginPath(); ctx.arc(sx * ex, ey + 4, 13, 1.12 * Math.PI, 1.88 * Math.PI); ctx.stroke();
      if (face === 'sad') { ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(sx * (ex - 9), ey - 28); ctx.lineTo(sx * (ex + 9), ey - 23); ctx.stroke(); }
    }
  }
  // blush, nose, mouth
  ctx.fillStyle = 'rgba(236,128,118,0.30)'; E(-38, -300, 13, 7); ctx.fill(); E(38, -300, 13, 7); ctx.fill();
  ctx.fillStyle = 'rgba(190,120,100,0.6)'; E(0, -305, 2, 1.5); ctx.fill();
  ctx.strokeStyle = '#9a4c3f'; ctx.lineWidth = 2.2; ctx.beginPath();
  if (face === 'smile') { ctx.moveTo(-8, -292); ctx.quadraticCurveTo(0, -284, 8, -292); }
  else if (face === 'sad') { ctx.moveTo(-7, -288); ctx.quadraticCurveTo(0, -293, 7, -288); }
  else if (face === 'up') { E(0, -290, 4, 3); ctx.stroke(); ctx.beginPath(); }
  else { ctx.moveTo(-6, -290); ctx.lineTo(6, -290); }
  ctx.stroke();
  if (face === 'up') { for (const [dx, dy] of [[-30, -312], [34, -300], [10, -340]]) { ctx.fillStyle = 'rgba(210,235,250,0.95)'; E(dx, dy, 2.5, 3.5); ctx.fill(); } }
}
function girl(x, y, s, opts = {}) {
  const { view = 'front', arm = 'down', face = 'neutral', wet = false, umb = null } = opts;
  const side = view === 'back' ? 1 : -1;   // umbrella hand: her right hand (viewer's left from the front, right from behind)
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  groundShadow(0, 2, 120, 0.3);
  // legs, socks, boots
  for (const sx of [-1, 1]) {
    ctx.fillStyle = vg(ctx, -130, -50, [[0, G.skin], [1, G.skinS]]); P([[sx * 14 - 11, -135], [sx * 14 + 11, -135], [sx * 14 + 10, -58], [sx * 14 - 10, -58]]); ctx.fill(); ink(2.6);
    ctx.fillStyle = G.sock; P([[sx * 14 - 11, -80], [sx * 14 + 11, -80], [sx * 14 + 11, -56], [sx * 14 - 11, -56]]); ctx.fill(); ink(2.2);
    ctx.fillStyle = vg(ctx, -62, 0, [[0, G.boot], [1, G.bootS]]); P([[sx * 14 - 15, -62], [sx * 14 + 15, -62], [sx * 14 + 17, -8, sx * 14 + 17, -2], [sx * 14 - 19 + (sx > 0 ? 0 : -2), -2], [sx * 14 - 17, -8, sx * 14 - 15, -62]]); ctx.fill(); ink(2.6);
    ctx.fillStyle = 'rgba(255,255,255,0.35)'; P([[sx * 14 - 11, -56], [sx * 14 - 7, -56], [sx * 14 - 8, -14], [sx * 14 - 12, -14]]); ctx.fill();
    ctx.fillStyle = '#5a1f1a'; ctx.fillRect(sx * 14 - 19, -8, 36, 6);
  }
  // raincoat body (A-line), light from the upper left
  const coat = [[-52, -268], [52, -268], [96, -128], [60, -118, 0, -116], [-60, -118, -96, -128]];
  ctx.fillStyle = lg(ctx, -96, -268, 96, -118, [[0, G.coatL], [0.35, G.coat], [1, G.coatS]]); P(coat); ctx.fill();
  if (wet) { const ws = -side; ctx.save(); P(coat); ctx.clip(); ctx.fillStyle = 'rgba(120,80,20,0.33)'; P([[ws * 56, -270], [ws * 12, -270], [ws * 26, -196], [ws * 82, -176]]); ctx.fill();
    for (let i = 0; i < 14; i++) { ctx.fillStyle = 'rgba(255,255,255,0.7)'; E(ws * (20 + rnd() * 40), -262 + rnd() * 70, 1.6, 2.4); ctx.fill(); } ctx.restore(); }
  P(coat); ink(3);
  // hem shadow, center placket, toggles, pockets
  ctx.fillStyle = 'rgba(140,90,20,0.25)'; P([[-94, -132], [60 * 0 - 94, -132], [-60, -120, 0, -118], [60, -120, 94, -132], [94, -124], [60, -112, 0, -110], [-60, -112, -94, -124]]); ctx.fill();
  ctx.strokeStyle = 'rgba(130,85,20,0.7)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(4, -262); ctx.lineTo(6, -118); ctx.stroke();
  for (const ty of [-236, -204, -172]) { ctx.fillStyle = '#7b5530'; ctx.fillRect(10, ty, 14, 5); ctx.strokeStyle = '#4a3020'; ctx.lineWidth = 1.2; ctx.strokeRect(10, ty, 14, 5); }
  for (const sx of [-1, 1]) { ctx.strokeStyle = 'rgba(130,85,20,0.75)'; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(sx * 30, -164); ctx.lineTo(sx * 64, -164); ctx.lineTo(sx * 68, -140); ctx.lineTo(sx * 34, -140); ctx.closePath(); ctx.stroke(); }
  // hood lying on the shoulders
  ctx.fillStyle = lg(ctx, -70, -290, 70, -250, [[0, G.coatL], [1, G.coatS]]); P([[-64, -262], [-40, -300, 0, -298], [40, -300, 64, -262], [30, -250, 0, -252], [-30, -250, -64, -262]]); ctx.fill(); ink(2.6);
  // arms
  const sleeve = (x0, y0, ang, len) => { ctx.save(); ctx.translate(x0, y0); ctx.rotate(ang);
    ctx.fillStyle = lg(ctx, -14, 0, 14, 0, [[0, G.coatL], [1, G.coatS]]); P([[-15, 0], [15, 0], [13, len], [-13, len]]); ctx.fill(); ink(2.6);
    ctx.fillStyle = G.skin; E(0, len + 9, 11, 12); ctx.fill(); ink(2.2); ctx.restore(); };
  if (arm === 'umbrella') { sleeve(-side * 58, -252, side * 0.12, 110); }
  else { sleeve(-58, -252, 0.12, 110); sleeve(58, -252, -0.12, 110); }
  // head: back hair, face, bangs
  ctx.fillStyle = lg(ctx, -80, -410, 80, -270, [[0, G.hairL], [0.45, G.hair], [1, '#2a1b17']]);
  P([[-78, -330], [-80, -420, 0, -416], [80, -420, 78, -330], [80, -290, 60, -272], [40, -282, 28, -272], [0, -300, -28, -272], [-40, -282, -60, -272], [-80, -290, -78, -330]]); ctx.fill(); ink(3);
  if (view === 'back') {
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.strokeStyle = 'rgba(255,220,200,0.35)'; ctx.lineWidth = 7; ctx.beginPath(); ctx.arc(0, -350, 52, 1.15 * Math.PI, 1.6 * Math.PI); ctx.stroke(); ctx.restore();
    ctx.strokeStyle = 'rgba(20,10,8,0.45)'; ctx.lineWidth = 1.6; for (let k = -3; k <= 3; k++) { ctx.beginPath(); ctx.moveTo(k * 16, -400); ctx.quadraticCurveTo(k * 22, -320, k * 20, -280); ctx.stroke(); }
  } else {
    ctx.fillStyle = vg(ctx, -380, -270, [[0, G.skin], [1, G.skinS]]);
    P([[-58, -340], [-60, -395, 0, -392], [60, -395, 58, -340], [57, -300, 22, -272], [0, -266, -22, -272], [-57, -300, -58, -340]]); ctx.fill(); ink(2.6);
    girlFace(face, s);
    // bangs with separated strands
    ctx.fillStyle = lg(ctx, -70, -410, 60, -330, [[0, G.hairL], [0.6, G.hair], [1, '#2a1b17']]);
    P([[-64, -352], [-66, -412, 0, -414], [66, -412, 64, -352], [53, -334, 42, -356], [31, -333, 20, -355], [10, -331, 0, -357], [-11, -332, -22, -355], [-33, -333, -44, -356], [-54, -336, -64, -352]]); ctx.fill(); ink(2.6);
    ctx.strokeStyle = 'rgba(20,10,8,0.35)'; ctx.lineWidth = 1.4; for (const bx of [-44, -22, 0, 20, 42]) { ctx.beginPath(); ctx.moveTo(bx * 0.6, -400); ctx.quadraticCurveTo(bx * 0.9, -375, bx, -358); ctx.stroke(); }
    ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.strokeStyle = 'rgba(255,215,190,0.4)'; ctx.lineWidth = 6; ctx.lineCap = 'round'; ctx.beginPath(); ctx.arc(-6, -360, 50, 1.18 * Math.PI, 1.52 * Math.PI); ctx.stroke(); ctx.restore();
  }
  if (arm === 'umbrella') sleeve(side * 52, -250, side * -2.64, 62);
  ctx.restore();
  if (umb) girlUmbrella(x + side * 86 * s, y - 312 * s, s, side * umb.tilt);
}

// =====================================================================
// The dog: cream shiba-type with a red knitted scarf
// (x, y) = ground point under the chest; s = scale (1 => ~300 px tall sitting); dir -1 faces left
// opts: pose 'sit' | 'back' | 'front'; ears 'up' | 'down'; look 'ahead'|'up'|'closed'|'tilt'; wind: scarf wind strength
// =====================================================================
const D = { fur: '#f2d6ad', furL: '#fcebd0', furS: '#d6ad7a', furD: '#b0855a', white: '#fdf7ec', nose: '#2a1f1b', ear: '#f0ae9c', scarf: '#c8473c', scarfL: '#e2665a', scarfS: '#8f2d27' };
// a knitted scarf tail: the centre line starts hanging down (ang0) and is pulled toward the wind, fluttering on the way
function ribbon(x, y, len, width, wind, phase = 0, ang0 = Math.PI / 2 - 0.1, windAng = 0.12) {
  const N = 30, target = ang0 + (windAng - ang0) * wind, L = [], R = [], C = [];
  let px = x, py = y, a = ang0;
  for (let i = 0; i <= N; i++) {
    const t = i / N, sm = t * t * (3 - 2 * t);
    a = ang0 + (target - ang0) * (0.35 + 0.65 * sm) * (wind > 0 ? 1 : 0) + (0.1 + 0.3 * wind) * t * Math.sin(2 * Math.PI * 1.3 * t + phase);
    if (i) { px += Math.cos(a) * len / N; py += Math.sin(a) * len / N; }
    const w = width * (1 - 0.18 * t) * (0.62 + 0.38 * Math.abs(Math.cos(Math.PI * 1.4 * t + phase * 0.7)));
    const nx = -Math.sin(a), ny = Math.cos(a);
    L.push([px + nx * w / 2, py + ny * w / 2]); R.push([px - nx * w / 2, py - ny * w / 2]); C.push([px, py, a, w]);
  }
  ctx.beginPath(); ctx.moveTo(...L[0]); for (const p of L) ctx.lineTo(...p); for (const p of R.slice().reverse()) ctx.lineTo(...p); ctx.closePath();
  ctx.fillStyle = lg(ctx, x, y, C[N][0], C[N][1], [[0, D.scarf], [0.6, D.scarf], [1, D.scarfS]]); ctx.fill();
  // twist shading where the ribbon narrows
  for (let i = 0; i < N; i++) { const k = 1 - C[i][3] / width; if (k > 0.25) { ctx.fillStyle = `rgba(90,20,15,${(k - 0.25) * 0.9})`; ctx.beginPath(); ctx.moveTo(...L[i]); ctx.lineTo(...L[i + 1]); ctx.lineTo(...R[i + 1]); ctx.lineTo(...R[i]); ctx.fill(); } }
  ctx.beginPath(); ctx.moveTo(...L[0]); for (const p of L) ctx.lineTo(...p); for (const p of R.slice().reverse()) ctx.lineTo(...p); ctx.closePath(); ink(2.2);
  ctx.strokeStyle = 'rgba(90,20,15,0.4)'; ctx.lineWidth = 1.3;
  for (let i = 2; i < N - 1; i += 2) { ctx.beginPath(); ctx.moveTo(...L[i]); ctx.lineTo(...R[i]); ctx.stroke(); }
  const [ex, ey, ea, ew] = C[N]; ctx.strokeStyle = D.scarfS; ctx.lineWidth = 2.2;
  for (let k = 0; k < 5; k++) { const o = (k / 4 - 0.5) * ew * 0.9, bx = ex - Math.sin(ea) * o, by = ey + Math.cos(ea) * o, fl = 10 + 3 * Math.sin(k * 2 + phase);
    ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(bx + Math.cos(ea + 0.15 * (k - 2) * wind) * fl, by + Math.sin(ea + 0.15 * (k - 2) * wind) * fl); ctx.stroke(); }
}
function dogEar(x, y, rot, back, flat) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); if (flat) ctx.scale(1, 0.72);
  ctx.fillStyle = back ? D.furS : lg(ctx, -16, 0, 16, -40, [[0, D.fur], [1, D.furL]]);
  P([[-18, 8], [-18, -18, -2, -44], [4, -46, 8, -40], [20, -16, 18, 8]]); ctx.fill(); ink(2.6);
  if (!back) { ctx.fillStyle = D.ear; P([[-9, 4], [-9, -14, -1, -30], [9, -12, 8, 4]]); ctx.fill(); }
  ctx.restore();
}
function dogHeadSide(ears, look, mouth) {
  // head centred at (0,0), facing left
  const down = ears === 'down';
  dogEar(24, -40, down ? 1.15 : 0.3, true, down);
  ctx.fillStyle = lg(ctx, -50, -50, 50, 50, [[0, D.furL], [0.5, D.fur], [1, D.furS]]); E(0, 0, 54, 50); ctx.fill(); ink(3);
  // cheek fluff at the back of the head
  ctx.fillStyle = D.fur; P([[40, 10], [58, 16], [48, 24], [58, 32], [40, 40], [30, 30, 40, 10]]); ctx.fill();
  ctx.strokeStyle = OUT; ctx.lineWidth = 2.6; ctx.beginPath(); ctx.moveTo(50, 12); ctx.lineTo(58, 16); ctx.lineTo(48, 24); ctx.lineTo(58, 32); ctx.lineTo(44, 40); ctx.stroke();
  dogEar(-4, -44, down ? 1.0 : -0.02, false, down);
  // muzzle (white) and mouth
  if (mouth === 'bark') {
    ctx.fillStyle = '#6e2626'; P([[-22, 14], [-54, 12, -86, 12], [-84, 38, -64, 52], [-38, 48, -22, 24]]); ctx.fill(); ink(2.4);
    ctx.fillStyle = '#e17f7a'; E(-56, 40, 15, 7, -0.15); ctx.fill();
    ctx.fillStyle = D.white; P([[-22, 26], [-44, 44, -70, 48], [-78, 58, -64, 60], [-40, 62, -16, 40]]); ctx.fill(); ink(2.6);
    ctx.fillStyle = D.white; P([[-8, 2], [-40, -12, -80, -4], [-92, 6, -86, 16], [-60, 16, -24, 20], [2, 24, -8, 2]]); ctx.fill(); ink(2.6);
    ctx.fillStyle = rg(ctx, -86, 0, 1, 9, [[0, '#5a4a44'], [1, D.nose]]); E(-84, 1, 9, 7, -0.2); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.6)'; E(-87, -2, 2.5, 1.6); ctx.fill();
  } else {
    ctx.fillStyle = D.white; P([[-10, 4], [-40, -8, -78, 2], [-88, 14, -80, 30], [-62, 44, -20, 36], [4, 30, -10, 4]]); ctx.fill(); ink(2.6);
    ctx.fillStyle = rg(ctx, -84, 4, 1, 9, [[0, '#5a4a44'], [1, D.nose]]); E(-83, 7, 9, 7); ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.6)'; E(-86, 4, 2.5, 1.6); ctx.fill();
    ctx.strokeStyle = OUT; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(-80, 16); ctx.lineTo(-78, 22);
    if (look === 'sad') ctx.quadraticCurveTo(-66, 25, -54, 26); else ctx.quadraticCurveTo(-64, 30, -52, 22); ctx.stroke();
  }
  // eyebrow dot (shiba "maro" brows) and eye
  ctx.fillStyle = '#fff4e2'; E(-24, -30, 7, 4, look === 'sad' ? 0.4 : -0.1); ctx.fill();
  const ey = look === 'up' ? -14 : look === 'sad' ? -7 : -10;
  if (look === 'closed') { ctx.strokeStyle = OUT; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(-26, -14, 9, 0.2 * Math.PI, 0.8 * Math.PI); ctx.stroke(); }
  else {
    const big = look === 'bright' ? 1.2 : 1;
    ctx.fillStyle = rg(ctx, -26, ey, 1, 9 * big, [[0, '#553a2b'], [1, '#1b120e']]); E(-26, ey, 7.5 * big, 9 * big); ctx.fill();
    ctx.fillStyle = '#fff'; E(-28.5, ey - 3.5 * big, 2.8 * big, 3.2 * big); ctx.fill(); E(-23, ey + 4, 1.3, 1.3); ctx.fill();
    if (look === 'bright') { E(-22, ey - 5, 1.4, 1.4); ctx.fill(); }
    ctx.strokeStyle = OUT; ctx.lineWidth = 2;
    if (look === 'sad') { ctx.beginPath(); ctx.moveTo(-37, -14); ctx.quadraticCurveTo(-26, -20, -16, -12); ctx.stroke(); }
    else { ctx.beginPath(); ctx.arc(-26, ey + 2, 11 * big, 1.15 * Math.PI, 1.75 * Math.PI); ctx.stroke(); }
    if (look === 'sad') { ctx.fillStyle = 'rgba(200,230,255,0.85)'; E(-30, ey + 9, 3, 2); ctx.fill(); }
  }
  ctx.fillStyle = 'rgba(236,140,120,0.28)'; E(-16, 16, 11, 6); ctx.fill();
  if (look === 'bright') { ctx.strokeStyle = OUT; ctx.lineWidth = 2.4; ctx.lineCap = 'round'; for (const [a, r0] of [[-2.55, 62], [-2.2, 66], [-1.88, 70]]) { ctx.beginPath(); ctx.moveTo(Math.cos(a) * (r0 + 20) - 10, Math.sin(a) * (r0 + 20) - 10); ctx.lineTo(Math.cos(a) * (r0 + 34) - 10, Math.sin(a) * (r0 + 34) - 10); ctx.stroke(); } }
}
function dogFrontLeg(lx, near) {
  const path = () => P([[lx - 13, -96], [lx - 11, -60, lx - 9, -22], [lx - 11, -12, lx - 22, -8, lx - 22, 0], [lx + 10, 0], [lx + 15, -4, lx + 11, -16], [lx + 12, -60, lx + 14, -96]]);
  ctx.fillStyle = lg(ctx, lx - 14, 0, lx + 14, 0, near ? [[0, D.furL], [1, D.fur]] : [[0, D.fur], [1, D.furS]]); path(); ctx.fill();
  ctx.save(); path(); ctx.clip(); ctx.fillStyle = near ? D.white : '#efe4d3'; P([[lx - 30, -20], [lx - 6, -26, lx + 20, -18], [lx + 20, 4], [lx - 30, 4]]); ctx.fill(); ctx.restore();
  P([[lx - 13, -96], [lx - 11, -60, lx - 9, -22], [lx - 11, -12, lx - 22, -8, lx - 22, 0], [lx + 10, 0], [lx + 15, -4, lx + 11, -16], [lx + 12, -60, lx + 14, -96]], false); ink(2.6);
  ctx.strokeStyle = OUT; ctx.lineWidth = 1.8; for (const tx of [-12, -3]) { ctx.beginPath(); ctx.moveTo(lx + tx, 0); ctx.lineTo(lx + tx + 1, -6); ctx.stroke(); }
}
function dog(x, y, s, opts = {}) {
  const { pose = 'sit', ears = 'up', look = 'ahead', mouth = 'closed', wind = 0.4, dir = -1, head = 0, scarf = true, tailLen = 1 } = opts;
  ctx.save(); ctx.translate(x, y); ctx.scale(-dir * s, s);   // drawn facing left; flip for dir = 1
  groundShadow(30, 2, 140, 0.3);
  if (pose === 'back') {
    // seen from behind, sitting, looking out to sea
    ctx.fillStyle = D.white; E(-62, -6, 24, 10); ctx.fill(); ink(2.4); E(62, -6, 24, 10); ctx.fill(); ink(2.4);
    const body = () => P([[-38, -172], [-58, -140, -58, -100, -74, -60], [-90, -24, -80, -2, -56, -2], [56, -2], [80, -2, 90, -24, 74, -60], [58, -100, 58, -140, 38, -172]]);
    ctx.fillStyle = lg(ctx, -80, -180, 80, 0, [[0, D.furL], [0.5, D.fur], [1, D.furS]]); body(); ctx.fill();
    ctx.save(); body(); ctx.clip();
    ctx.fillStyle = rg(ctx, 0, -96, 4, 70, [[0, 'rgba(150,105,60,0.14)'], [1, 'rgba(150,105,60,0)']]); ctx.fillRect(-80, -180, 160, 180);
    ctx.restore(); body(); ink(3);
    ctx.strokeStyle = 'rgba(80,50,30,0.55)'; ctx.lineWidth = 2.2;
    for (const sx of [-1, 1]) { ctx.beginPath(); ctx.moveTo(sx * 70, -56); ctx.quadraticCurveTo(sx * 44, -46, sx * 38, -6); ctx.stroke(); }
    // tail lying on the ground, curling round to the right
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const tail = () => { ctx.beginPath(); ctx.moveTo(6, -26); ctx.bezierCurveTo(30, -6, 96, 6, 118, -14); ctx.quadraticCurveTo(128, -26, 118, -34); };
    ctx.strokeStyle = OUT; ctx.lineWidth = 28; tail(); ctx.stroke(); ctx.strokeStyle = D.fur; ctx.lineWidth = 22; tail(); ctx.stroke();
    ctx.strokeStyle = D.white; ctx.lineWidth = 16; ctx.beginPath(); ctx.moveTo(112, -8); ctx.quadraticCurveTo(128, -26, 118, -34); ctx.stroke();
    // head from behind
    ctx.save(); ctx.translate(0, -214);
    for (const sx of [-1, 1]) dogEar(sx * 28, -36, sx * 0.22, false, false);
    ctx.fillStyle = lg(ctx, -50, -50, 50, 50, [[0, D.furL], [0.55, D.fur], [1, D.furS]]); E(0, 0, 54, 50); ctx.fill(); ink(3);
    for (const sx of [-1, 1]) { ctx.fillStyle = D.fur; ctx.strokeStyle = OUT; ctx.lineWidth = 2.6; P([[sx * 46, 14], [sx * 60, 22], [sx * 48, 28], [sx * 56, 38], [sx * 36, 42]]); ctx.fill(); ctx.beginPath(); ctx.moveTo(sx * 50, 16); ctx.lineTo(sx * 60, 22); ctx.lineTo(sx * 48, 28); ctx.lineTo(sx * 56, 38); ctx.lineTo(sx * 40, 42); ctx.stroke(); }
    ctx.restore();
    if (scarf) {
      ribbon(44, -170, 110 * tailLen, 26, wind, 0.4, 1.2);
      ribbon(36, -160, 88 * tailLen, 24, wind, 2.0, 1.35);
      ctx.fillStyle = lg(ctx, -60, -180, 60, -150, [[0, D.scarfL], [0.4, D.scarf], [1, D.scarfS]]); P([[-54, -180], [0, -192, 54, -180], [58, -156], [0, -166, -58, -156]]); ctx.fill(); ink(2.4);
      ctx.strokeStyle = 'rgba(90,20,15,0.4)'; ctx.lineWidth = 1.3; for (let k = -4; k <= 4; k++) { ctx.beginPath(); ctx.moveTo(k * 12, -186 + Math.abs(k) * 1.2); ctx.lineTo(k * 12.5, -162 + Math.abs(k) * 0.4); ctx.stroke(); }
    }
    ctx.restore(); return;
  }
  // tail curled over the back (drawn first so its base hides under the body)
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  const tail = () => { ctx.beginPath(); ctx.moveTo(98, -104); ctx.bezierCurveTo(140, -128, 142, -196, 106, -206); ctx.quadraticCurveTo(76, -210, 80, -184); };
  ctx.strokeStyle = OUT; ctx.lineWidth = 32; tail(); ctx.stroke(); ctx.strokeStyle = D.fur; ctx.lineWidth = 26; tail(); ctx.stroke();
  ctx.strokeStyle = D.white; ctx.lineWidth = 18; ctx.beginPath(); ctx.moveTo(98, -206); ctx.quadraticCurveTo(76, -210, 80, -184); ctx.stroke();
  // far front leg, body, haunch, near front leg, hind paw
  dogFrontLeg(-8, false);
  const body = () => P([[-40, -176], [-62, -140, -60, -100, -48, -74], [-40, -48, -20, -20, 4, -10], [22, 0], [96, 0], [126, -2, 130, -46, 114, -86], [98, -132, 52, -172, 0, -186]]);
  ctx.fillStyle = lg(ctx, -40, -200, 120, 0, [[0, D.furL], [0.45, D.fur], [1, D.furS]]); body(); ctx.fill();
  ctx.save(); body(); ctx.clip();
  ctx.fillStyle = 'rgba(150,105,60,0.22)'; E(60, -8, 70, 22); ctx.fill();
  // chest fluff
  ctx.fillStyle = D.white; P([[-66, -160], [-18, -160], [-10, -134], [-20, -124], [-10, -110], [-22, -98], [-12, -84], [-26, -74], [-30, -60, -44, -58], [-70, -90, -66, -160]]); ctx.fill();
  ctx.restore(); body(); ink(3);
  // haunch
  ctx.fillStyle = lg(ctx, 20, -100, 110, 0, [[0, D.fur], [1, D.furS]]); E(66, -48, 48, 44, -0.2); ctx.fill();
  ctx.strokeStyle = OUT; ctx.lineWidth = 2.6; ctx.beginPath(); ctx.ellipse(66, -48, 48, 44, -0.2, 0.92 * Math.PI, 1.72 * Math.PI); ctx.stroke();
  ctx.fillStyle = D.white; P([[18, 0], [14, -16, 36, -18], [66, -18, 78, -8], [80, 0]]); ctx.fill(); ink(2.4);
  ctx.strokeStyle = OUT; ctx.lineWidth = 1.8; for (const tx of [30, 42]) { ctx.beginPath(); ctx.moveTo(tx, 0); ctx.lineTo(tx - 1, -6); ctx.stroke(); }
  dogFrontLeg(-34, true);
  // scarf tails hang behind the head, knot on the neck
  if (scarf) { ribbon(14, -150, 108 * tailLen, 26, wind, 0.3); ribbon(24, -148, 88 * tailLen, 24, wind, 1.9, Math.PI / 2 + 0.05); }
  // head
  ctx.save(); ctx.translate(-34, -206); ctx.rotate(head + (look === 'up' || mouth === 'bark' ? 0.24 : 0) + (ears === 'down' && look !== 'closed' ? -0.1 : 0)); dogHeadSide(ears, look, mouth); ctx.restore();
  if (scarf) {
    ctx.fillStyle = lg(ctx, -60, -180, 40, -140, [[0, D.scarfL], [0.4, D.scarf], [1, D.scarfS]]);
    P([[-64, -170], [-20, -190, 30, -172], [34, -146], [-18, -162, -60, -146]]); ctx.fill(); ink(2.4);
    ctx.strokeStyle = 'rgba(90,20,15,0.4)'; ctx.lineWidth = 1.3; for (let k = 0; k < 9; k++) { const xx = -56 + k * 10.5; ctx.beginPath(); ctx.moveTo(xx, -180 + Math.abs(xx + 14) * 0.12); ctx.lineTo(xx + 2, -154 + Math.abs(xx + 14) * 0.1); ctx.stroke(); }
    ctx.fillStyle = rg(ctx, 14, -162, 2, 14, [[0, D.scarfL], [1, D.scarf]]); E(18, -157, 10, 9); ctx.fill(); ink(2.2);
  }
  ctx.restore();
}
