// Renders index.html frame by frame with headless Chromium and pipes frames to ffmpeg.
// Usage: node render.mjs [out.mp4]   |   node render.mjs --stills 1.5,5,9  (debug PNGs)
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';
const dir = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30, DUR = 30;
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1 });
page.on('pageerror', e => { console.error('PAGE ERROR', e.message); });
await page.goto('file://' + path.join(dir, 'index.html'));
if (process.argv[2] === '--stills') {
  fs.mkdirSync(path.join(dir, 'stills'), { recursive: true });
  for (const t of process.argv[3].split(',').map(Number)) {
    await page.evaluate(t => window.renderFrame(t), t);
    await page.screenshot({ path: path.join(dir, 'stills', `t${t.toFixed(2)}.jpg`), type: 'jpeg', quality: 70 });
  }
} else {
  const out = process.argv[2] || path.join(dir, 'silent.mp4');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < FPS * DUR; i++) {
    await page.evaluate(t => window.renderFrame(t), i / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  console.log('wrote', out);
}
await browser.close();
