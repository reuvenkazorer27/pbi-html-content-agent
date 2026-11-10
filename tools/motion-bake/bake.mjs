// Bake a motion2code page (inline SVG driven by one GSAP timeline) into pure CSS @keyframes,
// so it can run inside the HTML Content visual - including the Secure edition, which strips <script>.
//
//   node bake.mjs <motion2code index.html> --out <dir> [--fps 30] [--name brand] [--height 100vh]
//                 [--font "'Segoe UI', sans-serif"] [--check 0.5] [--max-diff 0.02]
//
// Writes into <dir>:
//   baked.html          the animation as one self-contained <div> (CSS + SVG, no script, no external URL)
//   preview.html        baked.html on a page, with the source fonts kept (for the fidelity check)
//   measure.dax         a DAX measure that returns baked.html (quotes doubled)
//   report.json         size, keyframe counts, fidelity scores per checked time, what could not be baked
// Then prints BAKE OK / BAKE FAIL with the reasons. Exit code 1 on FAIL.
//
// How it works: motion2code pages honor a contract - window.anim.seek(t) is a pure function of t and
// <html data-ready="1"> marks the first frame drawn. We seek every 1/fps s, read each element's transform and
// animatable CSS/geometry properties, drop samples a straight line already reproduces, and emit one @keyframes
// per element (linear timing between samples). The fidelity gate screenshots the GSAP page and the baked page
// at the same times and compares them pixel by pixel in the browser.
//
// No npm packages: Microsoft Edge headless + the DevTools protocol + Node's WebSocket (same as fitcheck.mjs).
import { spawn, spawnSync } from 'node:child_process';
import { writeFileSync, mkdtempSync, mkdirSync, existsSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const argv = process.argv.slice(2);
const opt = (k, d) => (argv.includes(k) ? argv[argv.indexOf(k) + 1] : d);
if (!argv[0] || argv[0].startsWith('--')) { console.log(readFileSync(new URL(import.meta.url)).toString().split('\n').slice(0, 17).join('\n')); process.exit(2); }
const SRC = resolve(argv[0]);
const OUT = resolve(opt('--out', 'baked'));
const FPS = +opt('--fps', 30);
const NAME = (opt('--name', 'm2c').replace(/[^a-z0-9]/gi, '') || 'm2c').toLowerCase();
const HEIGHT = opt('--height', '100vh');
const FONT = opt('--font', "'Segoe UI', Arial, sans-serif");
const CHECK = +opt('--check', 0.5);          // fidelity check every N seconds
const MAX_DIFF = +opt('--max-diff', 0.02);    // worst allowed mean pixel difference (0..1) on any checked frame
const SIZE_WARN = 30000, SIZE_FAIL = 200000;  // characters; the HTML Content raw view truncates above ~200 KB
mkdirSync(OUT, { recursive: true });

// ---------------------------------------------------------------- browser (copied pattern from fitcheck.mjs)
const EDGE = [process.env.EDGE_PATH, 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  process.env.LOCALAPPDATA && join(process.env.LOCALAPPDATA, 'Microsoft/Edge/Application/msedge.exe')].find(p => p && existsSync(p));
if (!EDGE) { console.log('BAKE DID NOT RUN (Microsoft Edge not found - set EDGE_PATH)'); process.exit(2); }
const port = 9300 + Math.floor(Math.random() * 500);
const prof = mkdtempSync(join(tmpdir(), 'bake-'));
spawn(EDGE, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`,
  '--window-size=1920,1080', '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
function shutdown() {
  const leaf = prof.split(/[\\/]/).pop();
  spawnSync('powershell', ['-NoProfile', '-Command',
    `Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains('${leaf}') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }`],
    { stdio: 'ignore' });
  try { rmSync(prof, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 }); } catch {}
}
process.on('exit', shutdown);
const sleep = ms => new Promise(r => setTimeout(r, ms));
let target;
for (let i = 0; i < 60 && !target; i++) {
  await sleep(250);
  try { target = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(t => t.type === 'page'); } catch {}
}
if (!target) { console.log('BAKE DID NOT RUN (Edge did not start)'); process.exit(2); }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pending = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
  if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description || r.result.exceptionDetails.text);
  return r.result?.result?.value;
};
await send('Page.enable'); await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
async function open(url, ready) {
  await send('Page.navigate', { url });
  for (let i = 0; i < 200; i++) { await sleep(100); try { if (await evaluate(ready)) return true; } catch {} }
  return false;
}

// ---------------------------------------------------------------- 1) sample the GSAP page
const srcUrl = pathToFileURL(SRC).href + '?external=1';
if (!(await open(srcUrl, "document.documentElement.dataset.ready==='1' && !!window.anim"))) {
  console.log('BAKE FAIL\n  the page never set <html data-ready="1"> with window.anim - not a motion2code page?'); process.exit(1);
}
const SAMPLE_JS = `(() => {
  const FPS = ${FPS};
  const stage = document.querySelector('svg#stage') || document.querySelector('svg');
  if (!stage) return { error: 'no <svg> stage found' };
  const dur = window.anim.duration;
  // pre-pass: pages that build shapes lazily inside draw(t) only have every element after a full sweep
  const counts = new Set();
  for (let f = 0; f <= Math.round(dur * FPS); f++) { window.anim.seek(f / FPS); counts.add(stage.querySelectorAll('*').length); }
  window.anim.seek(0);
  const els = [stage, ...stage.querySelectorAll('*')].filter(e => !['defs','clipPath','mask','linearGradient','radialGradient','stop','title','desc','style','script','filter','feGaussianBlur'].includes(e.tagName) || e === stage);
  els.forEach((e, i) => e.classList.add('${NAME}-e' + i));
  const CSSP = ['opacity','fill','stroke','stroke-width','stroke-dashoffset','stroke-dasharray','fill-opacity','stroke-opacity','visibility','display'];
  const GEO = { rect: ['x','y','width','height','rx','ry'], circle: ['cx','cy','r'], ellipse: ['cx','cy','rx','ry'], path: ['d'], image: ['x','y','width','height'], use: ['x','y'] };
  const NONCSS = ['offset','font-size','dx','dy'];   // changes here cannot be baked
  // polygon/polyline/line geometry is not a CSS property, but path 'd' is: sample them as a path
  const asPath = (e) => {
    if (e.tagName === 'line') return 'M' + ['x1','y1'].map(a => e.getAttribute(a) || 0).join(' ') + ' L' + ['x2','y2'].map(a => e.getAttribute(a) || 0).join(' ');
    const pts = (e.getAttribute('points') || '').trim().split(/[\\s,]+/).filter(Boolean);
    let d = ''; for (let i = 0; i + 1 < pts.length; i += 2) d += (i ? ' L' : 'M') + pts[i] + ' ' + pts[i + 1];
    return d + (e.tagName === 'polygon' && d ? ' Z' : '');
  };
  const read = (e) => {
    const cs = getComputedStyle(e), o = {};
    for (const p of CSSP) o[p] = cs.getPropertyValue(p);
    // rendered at all? (self or any ancestor with display:none hides it) - used when display turns into visibility
    let a = e, gone = false;
    while (a && a !== stage.parentNode) { if (getComputedStyle(a).display === 'none') { gone = true; break; } a = a.parentElement; }
    o._gone = gone;
    const m = e.transform && e.transform.baseVal && e.transform.baseVal.consolidate && e.transform.baseVal.consolidate();
    const css = cs.transform && cs.transform !== 'none' ? cs.transform : null;
    // no transform = identity matrix, so 'none' -> zoom stays interpolable instead of a jump
    // a singular matrix (scale 0) makes CSS fall back to a discrete jump at 50%: nudge it to a tiny scale instead
    const fix = (a, b, c, d) => (Math.abs(a * d - b * c) < 1e-8 ? [a || 1e-4, b, c, d || 1e-4] : [a, b, c, d]);
    const mm = m ? [...fix(m.matrix.a, m.matrix.b, m.matrix.c, m.matrix.d), m.matrix.e, m.matrix.f] : null;
    o.transform = css || (mm ? 'matrix(' + mm.map(v => +v.toFixed(5)).join(', ') + ')' : 'matrix(1, 0, 0, 1, 0, 0)');
    for (const g of (GEO[e.tagName] || [])) { const v = e.getAttribute(g); if (v !== null) o['@' + g] = v; }
    if (['polygon','polyline','line'].includes(e.tagName)) o['@d'] = asPath(e);
    for (const g of NONCSS) { const v = e.getAttribute(g); if (v !== null) o['!' + g] = v; }
    if (e.tagName === 'text' || e.tagName === 'tspan') o['!text'] = e.textContent;
    return o;
  };
  const n = Math.round(dur * FPS);
  const series = els.map(() => []);
  for (let f = 0; f <= n; f++) { window.anim.seek(f / FPS); els.forEach((e, i) => series[i].push(read(e))); }
  window.anim.seek(0);
  // CSS keyframes do not toggle 'display' on SVG elements: turn display on/off into visibility (inherited by children)
  const toggled = [];
  series.forEach((ser, i) => {
    if (ser.every(o => o.display === ser[0].display)) return;
    // an explicit 'visible' on a child would override a hidden parent, so use the effective state (self + ancestors)
    ser.forEach(o => { o.visibility = (o._gone || o.visibility === 'hidden') ? 'hidden' : 'visible'; });
    toggled.push(i);
  });
  series.forEach(ser => ser.forEach(o => { delete o.display; delete o._gone; }));
  const clone = stage.cloneNode(true);
  toggled.forEach(i => { const c = clone.querySelector('.${NAME}-e' + i) || (clone.classList.contains('${NAME}-e' + i) ? clone : null);
    if (c) { c.removeAttribute('display'); c.style.removeProperty('display'); } });
  // swap polygon/polyline/line for an equivalent <path> (same attributes, d at frame 0)
  els.forEach((e, i) => {
    if (!['polygon','polyline','line'].includes(e.tagName)) return;
    const c = clone.querySelector('.${NAME}-e' + i); if (!c) return;
    const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    for (const a of c.attributes) if (!['points','x1','y1','x2','y2'].includes(a.name)) p.setAttribute(a.name, a.value);
    p.setAttribute('d', series[i][0]['@d']);
    if (e.tagName !== 'polygon' && !p.getAttribute('fill')) p.setAttribute('fill', 'none');
    c.replaceWith(p);
  });
  clone.querySelectorAll('script').forEach(s => s.remove());
  const styles = [...document.querySelectorAll('style')].map(s => s.textContent).join('\\n');
  const bg = getComputedStyle(document.body).backgroundColor;
  return { dur, n, fps: FPS, tags: els.map(e => e.tagName), series, svg: clone.outerHTML, styles, bg, dynamic: counts.size > 1 };
})()`;
const S = await evaluate(SAMPLE_JS);
if (S.error) { console.log('BAKE FAIL\n  ' + S.error); process.exit(1); }

// ---------------------------------------------------------------- 2) reduce samples to keyframes
const NUM = /-?\d*\.?\d+(?:e[-+]?\d+)?/gi;
const shape = v => String(v).replace(NUM, '#');
const nums = v => (String(v).match(NUM) || []).map(Number);
function keep(vals) {
  // greedy: keep a sample when a straight line from the last kept one misses an intermediate sample by more than tol
  const n = vals.length, k = [0];
  const interp = shape(vals[0]);
  const linear = vals.every(v => shape(v) === interp);
  if (!linear) {  // structure changes (e.g. 'none' -> matrix, hidden -> visible): key every change as a hold
    for (let i = 1; i < n; i++) if (vals[i] !== vals[i - 1]) { if (k[k.length - 1] !== i - 1) k.push(i - 1); k.push(i); }
    if (k[k.length - 1] !== n - 1) k.push(n - 1);
    return { idx: k, hold: true };
  }
  const N = vals.map(nums), span = N[0].map((_, j) => Math.max(...N.map(a => a[j])) - Math.min(...N.map(a => a[j])));
  const tol = span.map(s => (s <= 2 ? 0.004 : 0.3));
  let a = 0;
  for (let b = 2; b < n; b++) {
    let bad = false;
    for (let i = a + 1; i < b && !bad; i++) {
      const t = (i - a) / (b - a);
      for (let j = 0; j < N[i].length; j++) if (Math.abs(N[a][j] + (N[b][j] - N[a][j]) * t - N[i][j]) > tol[j]) { bad = true; break; }
    }
    if (bad) { k.push(b - 1); a = b - 1; }
  }
  k.push(n - 1);
  return { idx: k, hold: false };
}
const css = [], unbaked = new Set();
let keyframeCount = 0;
const GEO_PX = new Set(['x', 'y', 'width', 'height', 'rx', 'ry', 'cx', 'cy', 'r']);
S.series.forEach((ser, ei) => {
  const props = Object.keys(ser[0]);
  const frames = new Map();   // sample index -> [declarations]
  for (const p of props) {
    const vals = ser.map(o => o[p]);
    if (vals.every(v => v === vals[0])) continue;   // constant: already in the frame-0 markup
    if (p.startsWith('!')) { unbaked.add(`${S.tags[ei]} ${p.slice(1)}`); continue; }
    const { idx, hold } = keep(vals);
    const decl = (v) => {
      if (p.startsWith('@')) { const g = p.slice(1); return g === 'd' ? `d: path("${v}")` : `${g}: ${v}${GEO_PX.has(g) && /^-?[\d.]+$/.test(v) ? 'px' : ''}`; }
      return `${p}: ${v}`;
    };
    for (const i of idx) { if (!frames.has(i)) frames.set(i, []); frames.get(i).push(decl(vals[i]) + (hold ? '; animation-timing-function: step-end' : '')); }
  }
  if (!frames.size) return;
  const name = `${NAME}-k${ei}`;
  const body = [...frames.keys()].sort((x, y) => x - y).map(i => {
    keyframeCount++;
    const pct = +(100 * i / S.n).toFixed(3);
    return `${pct}%{${[...new Set(frames.get(i).join('; ').split('; '))].join(';')}}`;
  }).join('');
  css.push(`@keyframes ${name}{${body}}`);
  css.push(`.${NAME} .${NAME}-e${ei}{animation:${name} ${S.dur}s linear infinite;transform-box:view-box;transform-origin:0 0}`);
});

// ---------------------------------------------------------------- 3) assemble outputs
const stripComments = s => s.replace(/\/\*[\s\S]*?\*\//g, '');
const pageCss = stripComments(S.styles)
  .replace(/html\s*,\s*body\s*\{[^}]*\}/g, '')                         // page-level rules do not belong in a visual
  .replace(/(^|\})\s*svg\s*\{/g, `$1 .${NAME} svg{`)                   // scope bare svg/text rules to this visual
  .replace(/(^|\})\s*text\s*\{/g, `$1 .${NAME} text{`);
const fontRule = f => `.${NAME} text,.${NAME} tspan{font-family:${f} !important}`;
const wrap = (fontCss) => `<div class='${NAME}' style='position:relative;width:100%;height:${HEIGHT};overflow:hidden;background:${S.bg}'>` +
  `<style>${pageCss} .${NAME} svg{position:absolute;inset:0;width:100%;height:100%;display:block} ${fontCss} ${css.join('')} ` +
  `@media (prefers-reduced-motion: reduce){.${NAME} *{animation-play-state:paused !important}}</style>` +
  S.svg.replace(/\s+/g, ' ') + `</div>`;
const baked = wrap(fontRule(FONT));
// the preview keeps the source fonts (and their <link>) so the fidelity check compares motion, not typefaces
const srcHtml = readFileSync(SRC, 'utf8');
const fontLinks = (srcHtml.match(/<link[^>]+fonts\.googleapis[^>]*>/g) || []).join('');
const preview = `<!doctype html><html><head><meta charset='utf-8'>${fontLinks}<style>html,body{margin:0;height:100%;background:#fff}</style></head><body>${wrap('')}</body></html>`;
writeFileSync(join(OUT, 'baked.html'), baked);
writeFileSync(join(OUT, 'preview.html'), preview);
const daxName = `HTML Motion ${NAME}`;
writeFileSync(join(OUT, 'measure.dax'), `-- Generated by tools/motion-bake/bake.mjs from ${SRC.split(/[\\/]/).pop()} (${S.dur}s loop, ${keyframeCount} keyframes)\n-- Bind to an HTML Content visual (Values). No script, no external URL: runs in the Secure edition.\n${daxName} =\n"${baked.replace(/"/g, '""')}"\n`);

// ---------------------------------------------------------------- 4) fidelity gate: GSAP page vs baked preview
const times = [];
for (let t = 0; t < S.dur - 1e-6; t += CHECK) times.push(+t.toFixed(3));
async function shoot() { return (await send('Page.captureScreenshot', { format: 'png' })).result.data; }
const srcShots = [];
await open(srcUrl, "document.documentElement.dataset.ready==='1' && !!window.anim");
for (const t of times) { await evaluate(`window.anim.seek(${t})`); await sleep(30); srcShots.push(await shoot()); }
await open(pathToFileURL(join(OUT, 'preview.html')).href, "document.readyState==='complete' && document.fonts.status==='loaded'");
await sleep(300);
const bakedShots = [];
for (const t of times) {
  await evaluate(`document.getAnimations().forEach(a => { a.pause(); a.currentTime = ${t * 1000}; }); true`);
  await sleep(30); bakedShots.push(await shoot());
}
const DIFF_JS = (a, b) => `(async () => {
  const load = s => new Promise(r => { const i = new Image(); i.onload = () => r(i); i.src = 'data:image/png;base64,' + s; });
  const [A, B] = await Promise.all([load(${JSON.stringify(a)}), load(${JSON.stringify(b)})]);
  const w = 480, h = 270, c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d');
  x.drawImage(A, 0, 0, w, h); const da = x.getImageData(0, 0, w, h).data;
  x.drawImage(B, 0, 0, w, h); const db = x.getImageData(0, 0, w, h).data;
  let s = 0; for (let i = 0; i < da.length; i += 4) s += Math.abs(da[i]-db[i]) + Math.abs(da[i+1]-db[i+1]) + Math.abs(da[i+2]-db[i+2]);
  return s / (w * h * 3 * 255);
})()`;
const scores = [];
for (let i = 0; i < times.length; i++) scores.push({ t: times[i], diff: +(await evaluate(DIFF_JS(srcShots[i], bakedShots[i]))).toFixed(4) });
const worst = scores.reduce((a, b) => (b.diff > a.diff ? b : a), scores[0]);
// control: the gate is only meaningful if the source really moves between the checked frames
let motion = 0;
for (let i = 1; i < times.length; i++) motion = Math.max(motion, await evaluate(DIFF_JS(srcShots[0], srcShots[i])));
motion = +motion.toFixed(4);
// write the worst pair so a human can look at it
writeFileSync(join(OUT, `worst_${worst.t}s_source.png`), Buffer.from(srcShots[scores.indexOf(worst)], 'base64'));
writeFileSync(join(OUT, `worst_${worst.t}s_baked.png`), Buffer.from(bakedShots[scores.indexOf(worst)], 'base64'));

// ---------------------------------------------------------------- 5) report + verdict
const size = baked.length;
// url(#id) is an in-document reference (clip-path, mask) and stays; any other url() is external and is stripped
const forbidden = [/<script/i, /\son[a-z]+=/i, /url\((?!\s*['"]?#)/i, /@import/i, /@font-face/i, /https?:\/\//i].filter(r => r.test(baked.replace(/http:\/\/www\.w3\.org\/[^'"]*/g, '')));
const fails = [], warns = [];
if (motion < 0.002 || (worst.diff <= MAX_DIFF && motion < worst.diff * 5)) fails.push(`control: the source barely moves across the checked frames (max change ${motion}) - the fidelity score proves nothing; check --check spacing or the page's anim.seek`);
if (worst.diff > MAX_DIFF) fails.push(`fidelity: worst mean pixel difference ${worst.diff} at ${worst.t}s > ${MAX_DIFF} (see worst_*.png)`);
if (forbidden.length) fails.push('Secure edition would strip: ' + forbidden.map(String).join(', '));
if (size > SIZE_FAIL) fails.push(`size ${size} chars > ${SIZE_FAIL}`);
if (size > SIZE_WARN) warns.push(`size ${size} chars > ${SIZE_WARN}: fine for HTML Content, but keep an eye on refresh time; raise --fps tolerance or simplify`);
if (S.dynamic) warns.push('the page adds or removes elements while it plays; the bake keeps the full set from a complete sweep - check the fidelity pairs around those moments');
if (unbaked.size) warns.push('changes that CSS cannot animate were frozen at frame 0: ' + [...unbaked].join(', '));
if (/<text/i.test(S.svg)) warns.push(`text uses ${FONT} in Power BI (web fonts are blocked); the preview kept the source font`);
const report = { source: SRC, duration: S.dur, fps: FPS, samples: S.n + 1, elements: S.tags.length, keyframes: keyframeCount, size, worst, motion, scores, unbaked: [...unbaked], warnings: warns, failures: fails };
writeFileSync(join(OUT, 'report.json'), JSON.stringify(report, null, 2));
console.log(fails.length ? 'BAKE FAIL' : 'BAKE OK');
console.log(`  ${S.dur}s loop · ${S.tags.length} elements · ${keyframeCount} keyframes · ${size} chars · fidelity worst ${worst.diff} at ${worst.t}s (limit ${MAX_DIFF}) · source motion ${motion}`);
for (const f of fails) console.log('  FAIL ' + f);
for (const w of warns) console.log('  warn ' + w);
ws.close();
process.exit(fails.length ? 1 : 0);
