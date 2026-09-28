// Shared helpers for the refined stills (lighting, glass, drops, finishing).
const W = 1080, H = 840, cv = document.getElementById('c'), ctx = cv.getContext('2d');
let _s = 1; const seed = s => { _s = s; };
const rnd = () => (_s = (_s * 1664525 + 1013904223) % 4294967296) / 4294967296;
const gauss = () => { let u = 0; while (!u) u = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rnd()); };
function layer() { const c = document.createElement('canvas'); c.width = W; c.height = H; return [c, c.getContext('2d')]; }
function vg(g, y0, y1, stops) { const l = g.createLinearGradient(0, y0, 0, y1); stops.forEach(([t, c]) => l.addColorStop(t, c)); return l; }
function hg(g, x0, x1, stops) { const l = g.createLinearGradient(x0, 0, x1, 0); stops.forEach(([t, c]) => l.addColorStop(t, c)); return l; }
function rg(g, x, y, r0, r1, stops) { const l = g.createRadialGradient(x, y, r0, x, y, r1); stops.forEach(([t, c]) => l.addColorStop(t, c)); return l; }
function blurDraw(dst, src, px, op = 'source-over', a = 1) { dst.save(); dst.filter = `blur(${px}px)`; dst.globalCompositeOperation = op; dst.globalAlpha = a; dst.drawImage(src, 0, 0); dst.restore(); }
const OUT = '#3b2a22';

function sunsetSky(g, x0, y0, w, hor, sunX, opts = {}) {
  g.fillStyle = vg(g, y0, hor, opts.stops || [[0, '#4c5688'], [0.32, '#9a7fa6'], [0.62, '#e59b8a'], [0.86, '#f8c38a'], [1, '#ffe0a6']]);
  g.fillRect(x0, y0, w, hor - y0 + 2);
  const [c, cg] = layer();
  for (const [x, y, rx, ry] of opts.clouds || []) {
    for (let i = 0; i < 16; i++) { cg.fillStyle = `rgba(${226 + rnd() * 20},${150 + rnd() * 30},${150 + rnd() * 20},0.16)`; cg.beginPath(); cg.ellipse(x + gauss() * rx * 0.35, y + gauss() * ry * 0.4, rx * (0.3 + rnd() * 0.4), ry * (0.6 + rnd() * 0.6), 0, 0, Math.PI * 2); cg.fill(); }
    for (let i = 0; i < 8; i++) { cg.fillStyle = 'rgba(255,226,180,0.18)'; cg.beginPath(); cg.ellipse(x - rx * 0.1 + gauss() * rx * 0.25, y + ry * 0.45, rx * (0.25 + rnd() * 0.3), ry * 0.35, 0, 0, Math.PI * 2); cg.fill(); }
  }
  blurDraw(g, c, 7);
  g.fillStyle = rg(g, sunX, hor, 0, 420, [[0, 'rgba(255,240,200,0.95)'], [0.12, 'rgba(255,214,150,0.6)'], [0.45, 'rgba(255,170,120,0.18)'], [1, 'rgba(255,160,120,0)']]);
  g.fillRect(x0, y0, w, hor - y0 + 40);
  g.fillStyle = rg(g, sunX, hor, 0, opts.sunR || 40, [[0, '#fffbe8'], [0.7, '#ffe6a6'], [1, 'rgba(255,214,140,0)']]);
  g.beginPath(); g.arc(sunX, hor, opts.sunR || 40, Math.PI, 0); g.fill();
}
function sea(g, x0, w, hor, bottom, sunX) {
  g.fillStyle = vg(g, hor, bottom, [[0, '#86a9b6'], [0.25, '#5f8ea3'], [1, '#2c5a72']]); g.fillRect(x0, hor, w, bottom - hor);
  const [c, cg] = layer();
  for (let i = 0; i < 220; i++) { const y = hor + 3 + Math.pow(rnd(), 1.3) * (bottom - hor), sc = (y - hor) / (bottom - hor);
    cg.strokeStyle = rnd() < 0.5 ? `rgba(20,55,75,${0.12 + sc * 0.12})` : `rgba(200,225,230,${0.08 + rnd() * 0.08})`;
    cg.lineWidth = 1 + sc * 2.5; const x = x0 + rnd() * w, l = 20 + sc * 90 * rnd(); cg.beginPath(); cg.moveTo(x, y); cg.quadraticCurveTo(x + l / 2, y - 1.5 - sc * 2, x + l, y); cg.stroke(); }
  blurDraw(g, c, 0.8);
  const [c2, g2] = layer();
  for (let i = 0; i < 380; i++) { const y = hor + 2 + Math.pow(rnd(), 1.4) * (bottom - hor), sp = 10 + (y - hor) * 0.55, x = sunX + gauss() * sp, l = 3 + rnd() * (8 + (y - hor) * 0.12);
    g2.fillStyle = `rgba(255,${220 + rnd() * 30},${160 + rnd() * 60},${0.4 + rnd() * 0.6})`; g2.beginPath(); g2.ellipse(x, y, l, 1 + rnd() * 1.4, 0, 0, Math.PI * 2); g2.fill(); }
  blurDraw(g, c2, 4, 'screen', 0.9); g.drawImage(c2, 0, 0);
  g.fillStyle = 'rgba(255,230,190,0.35)'; g.fillRect(x0, hor - 1, w, 2);
}
function drop(g, x, y, r, a = 1) {
  g.fillStyle = rg(g, x - r * 0.3, y - r * 0.3, 0, r, [[0, `rgba(255,255,255,${0.95 * a})`], [0.45, `rgba(225,245,245,${0.55 * a})`], [1, `rgba(190,225,230,${0.08 * a})`]]);
  g.beginPath(); g.arc(x, y, r, 0, Math.PI * 2); g.fill();
}
// Boxy Clawd parts with light from one side (side = -1 light from left, 1 from right)
function litBox(x, y, w, h, base, shade, side = -1, rim = true) {
  ctx.fillStyle = vg(ctx, y, y + h, [[0, base], [1, shade]]); ctx.fillRect(x, y, w, h);
  const g2 = side < 0 ? hg(ctx, x, x + w, [[0, 'rgba(255,214,160,0.45)'], [0.25, 'rgba(255,214,160,0)'], [1, 'rgba(60,40,60,0.18)']])
                      : hg(ctx, x, x + w, [[0, 'rgba(60,40,60,0.18)'], [0.75, 'rgba(255,214,160,0)'], [1, 'rgba(255,214,160,0.45)']]);
  ctx.fillStyle = g2; ctx.fillRect(x, y, w, h);
  if (rim) { ctx.fillStyle = 'rgba(255,226,170,0.9)'; ctx.fillRect(side < 0 ? x + 2 : x + w - 5, y + 3, 3, h - 6); }
  ctx.strokeStyle = OUT; ctx.lineWidth = 3; ctx.lineJoin = 'round'; ctx.strokeRect(x, y, w, h);
}
function clawdEye(x, y, s = 1, tear = false) {
  ctx.fillStyle = '#2a1f1b'; ctx.fillRect(x, y, 8 * s, 20 * s);
  ctx.fillStyle = '#fff'; ctx.fillRect(x + 2 * s, y + 3 * s, 2.5 * s, 3.5 * s);
  if (tear) { ctx.fillStyle = rg(ctx, x + 4 * s, y + 26 * s, 0, 6 * s, [[0, 'rgba(255,255,255,0.95)'], [1, 'rgba(180,225,245,0.2)']]); ctx.beginPath(); ctx.ellipse(x + 4 * s, y + 26 * s, 3.5 * s, 5 * s, 0, 0, Math.PI * 2); ctx.fill(); }
}
function blueFish(x, y, s = 1, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.fillStyle = vg(ctx, -14, 14, [[0, '#7fa6ec'], [0.5, '#4f78c4'], [1, '#2f4f94']]);
  ctx.beginPath(); ctx.ellipse(0, 0, 24, 13, 0, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.moveTo(19, 0); ctx.lineTo(40, -14); ctx.quadraticCurveTo(34, 0, 40, 14); ctx.closePath(); ctx.fill();
  ctx.beginPath(); ctx.moveTo(-2, -11); ctx.quadraticCurveTo(6, -22, 14, -10); ctx.closePath(); ctx.fill();
  ctx.strokeStyle = 'rgba(30,40,70,0.8)'; ctx.lineWidth = 1.6; ctx.beginPath(); ctx.ellipse(0, 0, 24, 13, 0, 0, Math.PI * 2); ctx.stroke();
  ctx.fillStyle = 'rgba(255,255,255,0.55)'; ctx.beginPath(); ctx.ellipse(-4, -6, 10, 3, -0.1, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#1b1b24'; ctx.beginPath(); ctx.arc(-12, -2, 2.8, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-12.8, -2.8, 1, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
// Glass sphere bowl with refraction of whatever is already painted behind it.
function glassBowl(bx, by, R, mouthY, waterY, inside) {
  const snap = document.createElement('canvas'); snap.width = W; snap.height = H; snap.getContext('2d').drawImage(cv, 0, 0);
  const mw = Math.sqrt(R * R - (mouthY - by) ** 2), sw = Math.sqrt(R * R - (waterY - by) ** 2);
  ctx.save(); ctx.beginPath(); ctx.arc(bx, by, R, 0, Math.PI * 2); ctx.clip();
  // refraction: the view behind, flipped and magnified
  ctx.save(); ctx.translate(bx, by); ctx.scale(-1.18, 1.18); ctx.translate(-bx, -by); ctx.globalAlpha = 0.9; ctx.drawImage(snap, 0, 0); ctx.restore();
  ctx.fillStyle = 'rgba(235,245,245,0.12)'; ctx.fillRect(bx - R, by - R, 2 * R, 2 * R);
  // water
  ctx.save(); ctx.beginPath(); ctx.rect(bx - R, waterY, 2 * R, 2 * R); ctx.clip();
  ctx.fillStyle = vg(ctx, waterY, by + R, [[0, 'rgba(140,200,205,0.45)'], [1, 'rgba(60,120,140,0.6)']]); ctx.fillRect(bx - R, waterY, 2 * R, 2 * R);
  if (inside) inside();
  ctx.restore();
  // inner shading at the rim of the sphere
  ctx.fillStyle = rg(ctx, bx, by, R * 0.6, R, [[0, 'rgba(20,50,60,0)'], [1, 'rgba(20,50,60,0.35)']]); ctx.fillRect(bx - R, by - R, 2 * R, 2 * R);
  ctx.restore();
  // water surface
  ctx.fillStyle = 'rgba(210,240,242,0.35)'; ctx.beginPath(); ctx.ellipse(bx, waterY, sw, 9, 0, 0, Math.PI * 2); ctx.fill();
  ctx.strokeStyle = 'rgba(40,80,90,0.5)'; ctx.lineWidth = 1.4; ctx.stroke();
  // glass outline and mouth
  ctx.strokeStyle = 'rgba(40,60,70,0.8)'; ctx.lineWidth = 2.4;
  ctx.beginPath(); ctx.arc(bx, by, R, -Math.PI / 2 + Math.asin(mw / R), 1.5 * Math.PI - Math.asin(mw / R)); ctx.stroke();
  ctx.fillStyle = 'rgba(255,255,255,0.12)'; ctx.beginPath(); ctx.ellipse(bx, mouthY, mw, 10, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  // highlights: window reflection + rim
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.lineCap = 'round';
  ctx.strokeStyle = 'rgba(255,255,255,0.85)'; ctx.lineWidth = 7; ctx.beginPath(); ctx.arc(bx, by, R - 16, Math.PI * 1.02, Math.PI * 1.28); ctx.stroke();
  ctx.lineWidth = 3.5; ctx.beginPath(); ctx.arc(bx, by, R - 16, Math.PI * 1.34, Math.PI * 1.41); ctx.stroke();
  ctx.fillStyle = 'rgba(255,236,200,0.55)'; ctx.beginPath(); ctx.ellipse(bx + R * 0.5, by - R * 0.42, R * 0.13, R * 0.2, 0.5, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = 'rgba(255,245,220,0.35)'; ctx.beginPath(); ctx.ellipse(bx + R * 0.35, by + R * 0.55, R * 0.25, R * 0.07, -0.3, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
function motes(n, x0, y0, x1, y1) {
  const [c, g] = layer();
  for (let i = 0; i < n; i++) { const r = 1 + rnd() * 3; g.fillStyle = `rgba(255,236,200,${0.3 + rnd() * 0.5})`; g.beginPath(); g.arc(x0 + rnd() * (x1 - x0), y0 + rnd() * (y1 - y0), r, 0, Math.PI * 2); g.fill(); }
  blurDraw(ctx, c, 1.2, 'screen');
}
function finish({ bloom = 0.28, sat = 0, vignette = 0.35 } = {}) {
  const [c, g] = layer(); g.drawImage(cv, 0, 0);
  ctx.save(); ctx.filter = 'blur(18px) brightness(1.15)'; ctx.globalCompositeOperation = 'screen'; ctx.globalAlpha = bloom; ctx.drawImage(c, 0, 0); ctx.restore();
  if (sat) { ctx.save(); ctx.globalCompositeOperation = 'saturation'; ctx.fillStyle = `rgba(128,128,128,${sat})`; ctx.fillRect(0, 0, W, H); ctx.restore(); }
  ctx.fillStyle = rg(ctx, W / 2, H / 2, H * 0.45, H * 0.95, [[0, 'rgba(30,20,40,0)'], [1, `rgba(30,20,40,${vignette})`]]); ctx.fillRect(0, 0, W, H);
  const img = ctx.getImageData(0, 0, W, H), d = img.data;
  for (let i = 0; i < d.length; i += 4) { const n = (rnd() - 0.5) * 9; d[i] += n; d[i + 1] += n; d[i + 2] += n; }
  ctx.putImageData(img, 0, 0);
}
