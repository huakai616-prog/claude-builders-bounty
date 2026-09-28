// Tiny watercolor toolkit for demo stills (canvas 2D).
const W = 1080, H = 840;
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');

let _s = 12345;
function seed(s) { _s = s; }
function rnd() { _s = (_s * 1664525 + 1013904223) % 4294967296; return _s / 4294967296; }
function gauss() { let u = 0, v = 0; while (u === 0) u = rnd(); v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
function lerp(a, b, t) { return a + (b - a) * t; }

function hex(c) { const n = parseInt(c.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; }
function rgba(c, a) { const [r, g, b] = hex(c); return `rgba(${r},${g},${b},${a})`; }
function mix(c1, c2, t) { const a = hex(c1), b = hex(c2); return '#' + a.map((v, i) => Math.round(lerp(v, b[i], t)).toString(16).padStart(2, '0')).join(''); }

// Recursive midpoint deformation (watercolor edge)
function deform(pts, depth, varc) {
  if (depth <= 0) return pts;
  const out = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i + 1) % pts.length];
    const len = Math.hypot(b[0] - a[0], b[1] - a[1]);
    out.push(a);
    out.push([(a[0] + b[0]) / 2 + gauss() * len * varc, (a[1] + b[1]) / 2 + gauss() * len * varc]);
  }
  return deform(out, depth - 1, varc * 0.8);
}
function fillPoly(pts) { ctx.beginPath(); ctx.moveTo(pts[0][0], pts[0][1]); for (const p of pts) ctx.lineTo(p[0], p[1]); ctx.closePath(); ctx.fill(); }
function rectPts(x, y, w, h) { return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]; }
function ellipsePts(cx, cy, rx, ry, n = 24) { const p = []; for (let i = 0; i < n; i++) { const t = i / n * Math.PI * 2; p.push([cx + Math.cos(t) * rx, cy + Math.sin(t) * ry]); } return p; }

// Watercolor wash: many faint deformed layers
function wash(pts, color, { layers = 30, alpha = 0.05, spread = 0.12, blend = 'multiply' } = {}) {
  ctx.save(); ctx.globalCompositeOperation = blend;
  const base = deform(pts, 3, spread);
  ctx.fillStyle = rgba(color, alpha);
  for (let i = 0; i < layers; i++) fillPoly(deform(base, 3, spread * 0.6));
  ctx.restore();
}
// Soft vertical gradient band made of washes
function bandGradient(y0, y1, colors, opts = {}) {
  const steps = 14;
  for (let i = 0; i < steps; i++) {
    const t = i / (steps - 1);
    const c = colors.length === 2 ? mix(colors[0], colors[1], t)
      : (t < 0.5 ? mix(colors[0], colors[1], t * 2) : mix(colors[1], colors[2], (t - 0.5) * 2));
    const y = lerp(y0, y1, i / steps), h = (y1 - y0) / steps;
    wash(rectPts(-40, y - h * 0.4, W + 80, h * 1.8), c, { layers: opts.layers || 10, alpha: opts.alpha || 0.09, spread: 0.04 });
  }
}
function paper(base = '#f1e9da') {
  ctx.fillStyle = base; ctx.fillRect(0, 0, W, H);
}
function grain(strength = 14) {
  const img = ctx.getImageData(0, 0, W, H), d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    const n = (rnd() - 0.5) * strength;
    d[i] += n; d[i + 1] += n; d[i + 2] += n;
  }
  ctx.putImageData(img, 0, 0);
  // fibers
  ctx.save(); ctx.globalAlpha = 0.05; ctx.strokeStyle = '#6b5a45'; ctx.lineWidth = 0.6;
  for (let i = 0; i < 700; i++) { const x = rnd() * W, y = rnd() * H, a = rnd() * Math.PI, l = 4 + rnd() * 10; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); ctx.stroke(); }
  ctx.restore();
}
// Wobbly ink line through points
function ink(pts, { w = 3, color = '#2a2320', closed = false, jitter = 0.8 } = {}) {
  ctx.save(); ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  const P = [];
  const src = closed ? [...pts, pts[0]] : pts;
  for (let i = 0; i < src.length - 1; i++) {
    const a = src[i], b = src[i + 1], len = Math.hypot(b[0] - a[0], b[1] - a[1]), n = Math.max(2, Math.floor(len / 14));
    for (let k = 0; k < n; k++) { const t = k / n; P.push([lerp(a[0], b[0], t) + gauss() * jitter, lerp(a[1], b[1], t) + gauss() * jitter]); }
  }
  P.push(src[src.length - 1]);
  ctx.beginPath(); ctx.moveTo(P[0][0], P[0][1]);
  for (let i = 1; i < P.length; i++) ctx.lineTo(P[i][0], P[i][1]);
  ctx.stroke(); ctx.restore();
}
function inkEllipse(cx, cy, rx, ry, opts, a0 = 0, a1 = Math.PI * 2) {
  const pts = []; const n = 64;
  for (let i = 0; i <= n; i++) { const t = lerp(a0, a1, i / n); pts.push([cx + Math.cos(t) * rx, cy + Math.sin(t) * ry]); }
  ink(pts, opts);
}
// Flat textured fill (character bodies)
function flat(pts, color, texture = true) {
  ctx.save(); ctx.fillStyle = color; fillPoly(pts);
  if (texture) {
    ctx.clip(); ctx.globalCompositeOperation = 'multiply';
    for (let i = 0; i < 3; i++) wash(deform(pts, 2, 0.05), mix(color, '#8a5a40', 0.12), { layers: 3, alpha: 0.035, spread: 0.06 });
    ctx.globalAlpha = 0.08; ctx.strokeStyle = '#000';
    const xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
    for (let x = Math.min(...xs); x < Math.max(...xs); x += 26 + rnd() * 20) { ctx.beginPath(); ctx.moveTo(x, Math.min(...ys)); ctx.lineTo(x + gauss() * 3, Math.min(...ys) + 12 + rnd() * 20); ctx.stroke(); }
  }
  ctx.restore();
}
function glow(x, y, r, color, a = 0.5) {
  const g = ctx.createRadialGradient(x, y, 0, x, y, r);
  g.addColorStop(0, rgba(color, a)); g.addColorStop(1, rgba(color, 0));
  ctx.save(); ctx.globalCompositeOperation = 'screen'; ctx.fillStyle = g; ctx.fillRect(x - r, y - r, 2 * r, 2 * r); ctx.restore();
}

// ---- Clawd (boxy, terracotta, ink outline) ----
const ORANGE = '#e5936f', BLUE = '#5f86c0', INK = '#2a2320';
function box(x, y, w, h, color) {
  const pts = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]];
  flat(pts, color); ink(pts, { closed: true, w: 3.2 });
}
function eye(x, y, s = 1) {
  ctx.save(); ctx.fillStyle = INK; ctx.fillRect(x, y, 7 * s, 18 * s);
  ctx.fillStyle = '#fff'; ctx.fillRect(x + 1.5 * s, y + 2.5 * s, 2.2 * s, 3 * s); ctx.restore();
}
// Side view facing left (dir=-1) or right (dir=1). (x,y) = top-left of body.
function clawdSide(x, y, w, h, color, dir = -1, { arm = 'forward', legLen = 26, eyeLook = 0 } = {}) {
  // legs
  const lw = w * 0.13;
  box(x + w * 0.2, y + h - 4, lw, legLen, mix(color, '#5a3a2a', 0.15));
  box(x + w * 0.62, y + h - 4, lw, legLen, mix(color, '#5a3a2a', 0.15));
  box(x, y, w, h, color);
  const ex = dir < 0 ? x + w * 0.12 : x + w * 0.82;
  eye(ex + eyeLook, y + h * 0.18);
}
function arm(x, y, w, h, color, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  box(0, -h / 2, w, h, color); ctx.restore();
}

// Smooth vertical gradient (clean base under watercolor texture)
function vgrad(x, y0, w, y1, stops) {
  const g = ctx.createLinearGradient(0, y0, 0, y1);
  stops.forEach(([t, c]) => g.addColorStop(t, c));
  ctx.fillStyle = g; ctx.fillRect(x, y0, w, y1 - y0);
}
// Light watercolor blooms for texture (normal blend, very faint)
function blooms(x0, y0, x1, y1, color, n = 12, r = 90, a = 0.035) {
  for (let i = 0; i < n; i++) {
    const cx = lerp(x0, x1, rnd()), cy = lerp(y0, y1, rnd());
    wash(ellipsePts(cx, cy, r * (0.6 + rnd()), r * (0.3 + rnd() * 0.4)), color, { layers: 8, alpha: a, blend: 'source-over', spread: 0.15 });
  }
}
function fish(x, y, s = 1, rot = 0, color = '#4f78c4') {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  ctx.fillStyle = color; ctx.beginPath(); ctx.ellipse(0, 0, 22, 12, 0, 0, Math.PI * 2); ctx.fill();
  ctx.beginPath(); ctx.moveTo(18, 0); ctx.lineTo(36, -12); ctx.lineTo(34, 12); ctx.closePath(); ctx.fill();
  ink([[18, 0], [36, -12], [34, 12], [18, 0]], { w: 2 / s, jitter: 0.4 }); inkEllipse(0, 0, 22, 12, { w: 2 / s, jitter: 0.4 });
  ctx.fillStyle = INK; ctx.beginPath(); ctx.arc(-11, -2, 2.6, 0, Math.PI * 2); ctx.fill();
  ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(-11.8, -2.8, 0.9, 0, Math.PI * 2); ctx.fill();
  ctx.restore();
}
