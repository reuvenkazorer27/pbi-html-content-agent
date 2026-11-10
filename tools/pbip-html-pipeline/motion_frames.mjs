// Freeze every CSS animation in the exact-size preview at given times and screenshot a region:
//   node motion_frames.mjs preview_all.html out_prefix 0.15,0.45,0.8,1.5 [x,y,w,h]
// Deterministic: animations are paused and set to currentTime, not caught in real time.
import { spawn, spawnSync } from 'node:child_process';
import { writeFileSync, mkdtempSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const [page, prefix, timesArg, clipArg] = process.argv.slice(2);
const times = (timesArg || '0.15,0.45,0.8,1.5').split(',').map(Number);
const [cx, cy, cw, ch] = (clipArg || '0,130,1920,190').split(',').map(Number);
const EDGE = ['C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe', 'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].find(existsSync);
const port = 9800 + Math.floor(Math.random() * 100);
const prof = mkdtempSync(join(tmpdir(), 'mframes-'));
spawn(EDGE, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, '--window-size=1920,1080', '--hide-scrollbars', pathToFileURL(resolve(page)).href], { stdio: 'ignore' });
process.on('exit', () => {
  const leaf = prof.split(/[\\/]/).pop();
  spawnSync('powershell', ['-NoProfile', '-Command', `Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains('${leaf}') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }`], { stdio: 'ignore' });
  try { rmSync(prof, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch {}
});
const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let i = 0; i < 60 && !target; i++) { await sleep(250); try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page'); } catch {} }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pend = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'no-preference' }] });
await send('Page.reload'); await sleep(1500);
const rm = await send('Runtime.evaluate', { returnByValue: true, expression: "matchMedia('(prefers-reduced-motion: reduce)').matches" }); console.log('reduced motion before override was emulated as:', rm.result.result.value);
const counts = [];
for (const t of times) {
  const r = await send('Runtime.evaluate', { returnByValue: true, expression:
    `[...document.querySelectorAll('iframe')].reduce((n, f) => { const a = f.contentDocument.getAnimations(); a.forEach(x => { x.pause(); x.currentTime = ${t * 1000}; }); return n + a.length; }, 0)` });
  counts.push(r.result.result.value);
  await sleep(80);
  const s = await send('Page.captureScreenshot', { format: 'png', clip: { x: cx, y: cy, width: cw, height: ch, scale: 1 }, captureBeyondViewport: true });
  writeFileSync(`${prefix}_${t}s.png`, Buffer.from(s.result.data, 'base64'));
}
console.log('animations found per frame:', counts.join(','), '-> frames:', times.map(t => `${prefix}_${t}s.png`).join(' '));
ws.close(); process.exit(0);
