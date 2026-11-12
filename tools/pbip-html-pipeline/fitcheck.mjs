// Headless fit + contrast check for preview.html (no npm packages: Edge + DevTools protocol + Node's WebSocket)
//   node fitcheck.mjs preview.html [--shot out.png]
//   node fitcheck.mjs a.html b.html c.html        several pages in ONE browser (stress.py): each block starts "== <file>"
// Prints FIT OK / FIT FAIL lines and CONTRAST OK / CONTRAST FAIL lines; exit code 1 on any failure.
import { spawn, spawnSync } from 'node:child_process';
import { writeFileSync, mkdtempSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';

const args = process.argv.slice(2);
const shot = args.includes('--shot') ? args[args.indexOf('--shot') + 1] : null;
const pages = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--shot').map(a => resolve(a));
if (!pages.length) pages.push(resolve('preview.html'));
const page = pages[0];
// Edge: EDGE_PATH, else the machine-wide and per-user install locations
const EDGE = [process.env.EDGE_PATH,
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  process.env.LOCALAPPDATA && join(process.env.LOCALAPPDATA, 'Microsoft/Edge/Application/msedge.exe')]
  .find(p => p && existsSync(p));
if (!EDGE) { console.log('FIT CHECK DID NOT RUN (Microsoft Edge not found - set EDGE_PATH)'); process.exit(2); }
const port = 9300 + Math.floor(Math.random() * 500);
const prof = mkdtempSync(join(tmpdir(), 'fitck-'));
const edge = spawn(EDGE, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`,
  '--window-size=1920,1080', '--hide-scrollbars', pathToFileURL(page).href], { stdio: 'ignore' });


// Edge forks GPU/renderer/utility children and its launcher exits early, so a tree kill misses them.
// Close the browser over CDP (Browser.close), then kill anything still holding this run's profile.
async function closeBrowser() {
  try {
    const v = await (await fetch(`http://127.0.0.1:${port}/json/version`, { signal: AbortSignal.timeout(2000) })).json();
    const bws = new WebSocket(v.webSocketDebuggerUrl);
    await Promise.race([
      new Promise((r, j) => { bws.addEventListener('open', r, { once: true }); bws.addEventListener('error', j, { once: true }); }),
      new Promise((_, j) => setTimeout(() => j(new Error('timeout')), 2000))]);
    bws.send(JSON.stringify({ id: 1, method: 'Browser.close' }));
    await new Promise(r => setTimeout(r, 700));
  } catch {}
}
function shutdown() {
  const leaf = prof.split(/[\\/]/).pop();   // e.g. fitck-Ab12Cd (mkdtemp suffix: no quotes or wildcards)
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
if (!target) { console.log('FIT CHECK DID NOT RUN (Edge did not start)'); process.exit(2); }

const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise(r => ws.addEventListener('open', r, { once: true }));
let id = 0; const pending = new Map();
ws.addEventListener('message', e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });

// contrast: every text node's color vs. the first opaque background up its ancestors (WCAG 2.x)
const CONTRAST_JS = `
(function(){
  function rgb(s){var m=s.match(/rgba?\\(([^)]+)\\)/); if(!m) return null; var p=m[1].split(',').map(parseFloat); return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};}
  function lum(c){return [c.r,c.g,c.b].map(function(v){v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4)}).reduce(function(a,v,i){return a+v*[0.2126,0.7152,0.0722][i]},0);}
  function bgOf(el,win){for(var e=el;e;e=e.parentElement){var c=rgb(win.getComputedStyle(e).backgroundColor); if(c&&c.a>0.5) return c;} return rgb(getComputedStyle(document.body.firstElementChild).backgroundColor)||{r:255,g:255,b:255,a:1};}
  var out=[];
  document.querySelectorAll('iframe[data-name]').forEach(function(f){
    var d=f.contentDocument, w=f.contentWindow; if(!d) return; var worst=null;
    d.querySelectorAll('body *').forEach(function(el){
      var own=[].some.call(el.childNodes,function(n){return n.nodeType===3&&n.textContent.trim().length>1}); if(!own) return;
      var cs=w.getComputedStyle(el), fg=rgb(cs.color); if(!fg||cs.visibility==='hidden'||parseFloat(cs.opacity)<0.2) return;
      var bg=bgOf(el,w), l1=lum(fg), l2=lum(bg), ratio=(Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05);
      var size=parseFloat(cs.fontSize), bold=parseInt(cs.fontWeight)>=700, large=size>=24||(bold&&size>=18.66), need=large?3:4.5;
      if(ratio<need && (!worst||ratio<worst.r)) worst={r:ratio,need:need,txt:el.textContent.trim().slice(0,30)};
    });
    if(worst) out.push(f.dataset.name+': contrast '+worst.r.toFixed(2)+' < '+worst.need+' at "'+worst.txt+'"');
  });
  return out.length ? 'CONTRAST FAIL\\n'+out.join('\\n') : 'CONTRAST OK';
})()`;

await send('Runtime.enable');
// wait until the page and every card iframe have rendered (fixed sleeps gave false EMPTY results)
const READY = "document.readyState==='complete' && [...document.querySelectorAll('iframe[data-name]')].every(f=>f.contentDocument&&f.contentDocument.readyState==='complete'&&f.contentDocument.body&&f.contentDocument.body.firstElementChild)";
let allOk = true;
for (let p = 0; p < pages.length; p++) {
  if (p > 0) { await send('Page.navigate', { url: pathToFileURL(pages[p]).href }); await sleep(200); }
  for (let i = 0; i < 100; i++) { const r = await send('Runtime.evaluate', { expression: READY, returnByValue: true }); if (r.result?.result?.value) break; await sleep(100); }
  await sleep(300);
  const fit = await send('Runtime.evaluate', { expression: "fitCheck(); document.getElementById('fit').textContent", returnByValue: true });
  const con = await send('Runtime.evaluate', { expression: CONTRAST_JS, returnByValue: true });
  const fitTxt = fit.result?.result?.value ?? ('FIT CHECK ERROR ' + JSON.stringify(fit.result?.exceptionDetails?.text));
  const conTxt = con.result?.result?.value ?? ('CONTRAST CHECK ERROR ' + JSON.stringify(con.result?.exceptionDetails?.text));
  if (pages.length > 1) console.log('== ' + pages[p]);
  console.log(fitTxt); console.log(conTxt);
  allOk = allOk && fitTxt.startsWith('FIT OK') && conTxt.startsWith('CONTRAST OK');
  if (shot && p === 0) {
    await send('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
    // the reference screenshot shows the resting layout (what the gate measured), not a frame mid-animation:
    // entrances at their end, endless loops at their start (motion frames are checked with motion_frames.mjs)
    await send('Runtime.evaluate', { expression: `document.querySelectorAll('iframe').forEach(f => { try {
      (f.contentDocument.getAnimations ? f.contentDocument.getAnimations() : []).forEach(a => { try {
        const t = a.effect.getComputedTiming(); a.pause(); a.currentTime = t.iterations === Infinity ? 0 : t.endTime; } catch (e) {} });
    } catch (e) {} })` });
    await sleep(100);
    const s = await send('Page.captureScreenshot', { format: 'png' });
    writeFileSync(shot, Buffer.from(s.result.data, 'base64')); console.log('screenshot ' + shot);
  }
}
ws.close();
await closeBrowser();
process.exit(allOk ? 0 : 1);
