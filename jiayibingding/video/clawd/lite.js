// lite.js: on machines without a GPU, watercolour fills are what make frames slow (and their cost swings wildly).
// LITE.on turns every fill into a flat translucent wash of the same colour; switch it off to paint real watercolour
// (e.g. inside a cached background).
const LITE = { on: true };
const _paintAtFull = paintAt;
paintAt = function (pts, o) {
  if (!LITE.on || !o.fill) return _paintAtFull(pts, o);
  const q = { ...o };
  if (!q.wash) { q.wash = q.fill; q.washOp = Math.round((q.fillOp ?? 170) * .55); }
  delete q.fill;
  return _paintAtFull(pts, q);
};
// Cache a whole-frame background (painted in screen space, no camera) the first time a key is asked for; later frames
// just draw the image. The background is a still painting, like the painted backgrounds of hand-drawn animation.
const BG_CACHE = {};
function cachedBackground(key, painter) {
  if (!BG_CACHE[key]) {
    const was = LITE.on; LITE.on = false;
    painter(); flushBrush();
    LITE.on = was;
    BG_CACHE[key] = get();
  }
  image(BG_CACHE[key], 0, 0);
}
