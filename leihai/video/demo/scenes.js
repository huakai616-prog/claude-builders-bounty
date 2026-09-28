// Scene helpers for the key frames (load after art.js)
function snap() { const [c, g] = layer(); g.drawImage(cv, 0, 0); return c; }
function grab(draw) { ctx.clearRect(0, 0, W, H); draw(); const c = snap(); ctx.clearRect(0, 0, W, H); return c; }
function poly(q) { ctx.beginPath(); ctx.moveTo(...q[0]); for (const p of q.slice(1)) ctx.lineTo(...p); ctx.closePath(); }
function cloudBank(list, rgb, a = 0.2, blur = 8, n = 18) {
  const [c, g] = layer();
  for (const [x, y, rx, ry] of list) for (let i = 0; i < n; i++) { g.fillStyle = `rgba(${rgb},${a})`; g.beginPath(); g.ellipse(x + gauss() * rx * 0.35, y + gauss() * ry * 0.3, rx * (0.3 + rnd() * 0.4), ry * (0.5 + rnd() * 0.6), 0, 0, Math.PI * 2); g.fill(); }
  blurDraw(ctx, c, blur);
}
function seaSurface(hor, bottom, top, deep, lightX, glint, spread = 0.5, n = 400, x0 = 0, x1 = W) {
  ctx.fillStyle = vg(ctx, hor, bottom, [[0, top], [1, deep]]); ctx.fillRect(x0, hor, x1 - x0, bottom - hor);
  const [c, g] = layer();
  for (let i = 0; i < 300; i++) { const y = hor + 2 + Math.pow(rnd(), 1.4) * (bottom - hor), k = (y - hor) / (bottom - hor), x = x0 + rnd() * (x1 - x0), l = 14 + k * 90 * rnd();
    g.strokeStyle = rnd() < 0.55 ? `rgba(10,20,35,${0.1 + k * 0.14})` : `rgba(220,230,240,${0.05 + rnd() * 0.07})`; g.lineWidth = 1 + k * 2.2; g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + l / 2, y - 1 - k * 2, x + l, y); g.stroke(); }
  blurDraw(ctx, c, 0.8);
  if (lightX != null) { const [c2, g2] = layer();
    for (let i = 0; i < n; i++) { const y = hor + 2 + Math.pow(rnd(), 1.3) * (bottom - hor), sp = 8 + (y - hor) * spread, x = lightX + gauss() * sp, l = 3 + rnd() * (6 + (y - hor) * 0.1);
      g2.fillStyle = `rgba(${glint},${0.35 + rnd() * 0.6})`; g2.beginPath(); g2.ellipse(x, y, l, 0.8 + rnd() * 1.3, 0, 0, Math.PI * 2); g2.fill(); }
    blurDraw(ctx, c2, 4, 'screen', 0.9); ctx.drawImage(c2, 0, 0); }
}
// mirror a layer: (x, y) -> (x, 2(a + b x) - y), i.e. about the line y = a + b x; keep it below that line, fading out
function mirror(src, a, b = 0, alpha = 0.35, blur = 2, fade = 300, smear = 0, clip = null) {
  const [c, g] = layer();
  g.save(); g.setTransform(1, 2 * b, 0, -1, 0, 2 * a); g.filter = `blur(${blur}px)`; g.drawImage(src, 0, 0);
  if (smear) for (let k = 1; k <= 8; k++) { g.globalAlpha = 0.5 * (1 - k / 9); g.drawImage(src, 0, -k * smear); }
  g.restore();
  // fade with distance from the mirror line (approximate: use the line's height at mid-width)
  const ym = a + b * W / 2; g.globalCompositeOperation = 'destination-in';
  g.fillStyle = vg(g, ym - Math.abs(b) * W / 2 - 1, ym + fade, [[0, 'rgba(0,0,0,1)'], [1, 'rgba(0,0,0,0)']]); g.fillRect(0, 0, W, H);
  ctx.save(); if (clip) { clip(); ctx.clip(); } ctx.globalAlpha = alpha; ctx.drawImage(c, 0, 0); ctx.restore();
}
// tint a figure layer (multiply) keeping its alpha
function tint(src, color, amt = 1) {
  const [c, g] = layer(); g.drawImage(src, 0, 0); g.globalAlpha = amt; g.globalCompositeOperation = 'multiply'; g.fillStyle = color; g.fillRect(0, 0, W, H);
  g.globalAlpha = 1; g.globalCompositeOperation = 'destination-in'; g.drawImage(src, 0, 0); return c;
}
// rim light: the figure's edge on the side facing the light (dx, dy = direction away from the light)
function rim(src, dx, dy, color, a = 0.9, blur = 1.5) {
  const [c, g] = layer(); g.drawImage(src, 0, 0); g.globalCompositeOperation = 'source-in'; g.fillStyle = color; g.fillRect(0, 0, W, H);
  g.globalCompositeOperation = 'destination-out'; g.drawImage(src, dx, dy);
  blurDraw(ctx, c, blur * 3, 'screen', a * 0.6); blurDraw(ctx, c, blur, 'screen', a);
}
// light falling on a figure from a point: radial glow clipped to the figure
function litFrom(src, x, y, r, rgb, a = 0.5) {
  const [c, g] = layer(); g.drawImage(src, 0, 0); g.globalCompositeOperation = 'source-in';
  g.fillStyle = rg(g, x, y, 0, r, [[0, `rgba(${rgb},${a})`], [1, `rgba(${rgb},0)`]]); g.fillRect(0, 0, W, H);
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.drawImage(c, 0, 0); ctx.restore();
}
function caption(text, y, size = 44) {
  ctx.save(); ctx.font = `600 ${size}px "Noto Serif CJK SC"`; ctx.textAlign = 'center';
  ctx.shadowColor = 'rgba(0,0,0,0.55)'; ctx.shadowBlur = 14; ctx.fillStyle = '#fbf6ee'; ctx.fillText(text, W / 2, y); ctx.restore();
}
function tag(text) {
  ctx.save(); ctx.font = `20px "Noto Serif CJK SC"`; ctx.fillStyle = 'rgba(255,255,255,0.72)'; ctx.shadowColor = 'rgba(0,0,0,0.5)'; ctx.shadowBlur = 6; ctx.fillText(text, 28, H - 26); ctx.restore();
}
function gull(x, y, s, flap = 0, rot = 0) {
  // facing right; flap 0..1 lifts the wings
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  const wing = (dx, lift, col) => { ctx.fillStyle = lg(ctx, 0, 0, 30, -80, [[0, col], [0.75, '#c4c9d4'], [0.76, '#3a3d48'], [1, '#2a2c35']]);
    P([[dx - 10, -4], [dx - 2, -36 - lift, dx + 22, -66 - lift * 1.4], [dx + 34, -80 - lift * 1.6, dx + 42, -78 - lift * 1.6], [dx + 30, -46 - lift, dx + 14, -2]]); ctx.fill(); ink(2); };
  wing(-16, flap * 10, '#d6dae3');
  ctx.fillStyle = '#f1f0ec'; P([[-58, 2], [-50, -2], [-44, -2], [-30, -10, 0, -10], [16, -10, 24, -16], [32, -22, 42, -16], [48, -12, 42, -5], [30, 4, 10, 10], [-20, 14, -44, 8], [-54, 12], [-58, 2]]); ctx.fill(); ink(2);
  ctx.fillStyle = '#e8b04a'; P([[44, -14], [58, -11], [44, -8]]); ctx.fill(); ctx.strokeStyle = '#9a6a20'; ctx.lineWidth = 1; ctx.stroke();
  ctx.fillStyle = '#222'; E(36, -16, 1.8, 1.8); ctx.fill();
  wing(0, flap * 14, '#e4e7ee');
  ctx.restore();
}
function farGull(x, y, s, a = 0.8, col = '60,50,60') { ctx.save(); ctx.strokeStyle = `rgba(${col},${a})`; ctx.lineWidth = 2.2 * s; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x - 14 * s, y - 2 * s); ctx.quadraticCurveTo(x - 6 * s, y - 9 * s, x, y); ctx.quadraticCurveTo(x + 6 * s, y - 9 * s, x + 14 * s, y - 2 * s); ctx.stroke(); ctx.restore(); }
// cloud masses: soft dark bodies, a silver rim on the side facing the light (lx, ly)
function puffs(list, dark, light, lx, ly, blur = 3, n = 26, mid = '#8a8794', flat = 1) {
  for (const [x, y, rx, ry] of list) {
    const [m, gm] = layer();
    for (let i = 0; i < n; i++) {
      const u = rnd() * 2 - 1, bx = x + u * rx * 0.85, by = y + (rnd() * 2 - 1) * ry * 0.3 - (1 - u * u) * ry * 0.3, r = ry * (0.35 + rnd() * 0.45) * (1 - Math.abs(u) * 0.45);
      gm.fillStyle = '#000'; gm.beginPath(); gm.ellipse(bx, by, r * flat, r / Math.sqrt(flat), 0, 0, Math.PI * 2); gm.fill();
    }
    const dx = lx - x, dy = ly - y, dl = Math.hypot(dx, dy) || 1, near = Math.pow(Math.max(0, 1 - dl / (650 * Math.sqrt(flat))), 1.5);
    // body: dark, lighter toward the light
    const [b, gb] = layer(); gb.drawImage(m, 0, 0); gb.globalCompositeOperation = 'source-in';
    gb.fillStyle = lg(gb, x - dx / dl * rx, y - dy / dl * ry, x + dx / dl * rx, y + dy / dl * ry, [[0, dark], [0.55, dark], [1, mid]]); gb.fillRect(0, 0, W, H);
    gb.fillStyle = vg(gb, y - ry, y + ry, [[0, 'rgba(0,0,0,0)'], [1, 'rgba(10,12,28,0.3)']]); gb.fillRect(0, 0, W, H);
    blurDraw(ctx, b, blur);
    // rim
    const [r, gr] = layer(); gr.drawImage(m, 0, 0); gr.globalCompositeOperation = 'source-in'; gr.fillStyle = light; gr.fillRect(0, 0, W, H);
    const k = ry * 0.32; gr.globalCompositeOperation = 'destination-out'; gr.drawImage(m, -dx / dl * k, -dy / dl * k);
    blurDraw(ctx, r, blur + 4, 'source-over', 0.35 + near * 0.5); blurDraw(ctx, r, blur + 1, 'source-over', 0.25 + near * 0.5);
  }
}
function rays(x, y, a0, a1, n, len, rgb, amax = 0.22, blur = 8) {
  const [c, g] = layer(); g.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) { const a = a0 + (a1 - a0) * rnd(), w = 0.02 + rnd() * 0.05;
    g.fillStyle = lg(g, x, y, x + Math.cos(a) * len, y + Math.sin(a) * len, [[0, `rgba(${rgb},${amax * (0.4 + rnd() * 0.6)})`], [1, `rgba(${rgb},0)`]]);
    g.beginPath(); g.moveTo(x, y); g.lineTo(x + Math.cos(a - w) * len, y + Math.sin(a - w) * len); g.lineTo(x + Math.cos(a + w) * len, y + Math.sin(a + w) * len); g.closePath(); g.fill(); }
  blurDraw(ctx, c, blur, 'screen');
}
function foam(y, a, amp = 6, w = 4) {
  const [c, g] = layer(); g.strokeStyle = `rgba(250,248,240,${a})`; g.lineWidth = w; g.lineCap = 'round';
  let x = -20; while (x < W) { const l = 40 + rnd() * 160; g.beginPath(); g.moveTo(x, y + (rnd() - 0.5) * amp); g.quadraticCurveTo(x + l / 2, y + (rnd() - 0.5) * amp, x + l, y + (rnd() - 0.5) * amp); g.stroke(); x += l + rnd() * 30; }
  blurDraw(ctx, c, 1.4); blurDraw(ctx, c, 5, 'screen', 0.5);
}
