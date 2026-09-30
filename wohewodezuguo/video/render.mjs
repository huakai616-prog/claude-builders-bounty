// Capture N frames of a page that defines apply(i), pipe them to ffmpeg.
// usage: node render.mjs page.html N fps out.mp4   (PW_DIR, CHROME in env)
import { createRequire } from 'module';
import { spawn } from 'child_process';

const require = createRequire(process.env.PW_DIR.replace(/\/?$/, '/'));
const { chromium } = require('playwright-core');
const [html, N, fps, out] = process.argv.slice(2);

const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe',
  '-framerate', fps, '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264',
  '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p',
  '-r', fps, out], { stdio: ['pipe', 'inherit', 'inherit'] });

const browser = await chromium.launch({ executablePath: process.env.CHROME,
  args: ['--no-sandbox', '--hide-scrollbars', '--font-render-hinting=none'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 },
  deviceScaleFactor: 1 });
await page.goto('file://' + html);
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(300);
const cdp = await page.context().newCDPSession(page);
const t0 = Date.now();
for (let i = 0; i < +N; i++) {
  await page.evaluate(k => apply(k), i);
  const { data } = await cdp.send('Page.captureScreenshot',
    { format: 'jpeg', quality: 95 });
  if (!ff.stdin.write(Buffer.from(data, 'base64')))
    await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) process.stderr.write(`frame ${i}/${N} ${((Date.now() - t0) / 1000).toFixed(1)}s\n`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
