#!/usr/bin/env node
// pbi-html-content-agent - set the kit up next to a Power BI project (PBIP), or check the machine.
//   npx pbi-html-content-agent init [folder] [--table T] [--page P] [--style S] [--yes] [--force]
//   npx pbi-html-content-agent doctor
// No dependencies: Node's own fs / path / readline / child_process only.
import { cpSync, existsSync, mkdirSync, readdirSync, readFileSync, statSync, writeFileSync } from 'node:fs';
import { basename, dirname, join, resolve } from 'node:path';
import { createInterface } from 'node:readline/promises';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const KIT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const PKG = JSON.parse(readFileSync(join(KIT, 'package.json'), 'utf8'));
const PIPE = join(KIT, 'tools', 'pbip-html-pipeline');
const KIT_PARTS = ['AGENTS.md', 'CONTRIBUTING.md', 'LICENSE', 'README.md', 'ROADMAP.md', 'SOURCES.md',
  'checklists', 'examples', 'library', 'reference', 'research', 'skills', 'tools'];
const STYLES = ['accent', 'tonal', 'midnight', 'sand', 'ocean', 'duotone', 'sunset', 'mint'];

const VALUE_FLAGS = ['table', 'page', 'style', 'project'];
const opts = {}, positional = [];
for (let a = process.argv.slice(2), i = 0; i < a.length; i++) {
  if (a[i].startsWith('--')) {
    const k = a[i].slice(2);
    if (VALUE_FLAGS.includes(k)) { if (a[i + 1] === undefined) { process.stderr.write(`error: --${k} needs a value\n`); process.exit(1); } opts[k] = a[++i]; }
    else opts[k] = true;
  } else positional.push(a[i]);
}
const flag = (name) => opts[name];
const has = (name) => opts[name] === true;
const say = (s = '') => process.stdout.write(s + '\n');
const fail = (s) => { process.stderr.write(`error: ${s}\n`); process.exit(1); };

function help() {
  say(`${PKG.name} ${PKG.version} - Power BI dashboards on the HTML Content visual

Usage
  npx ${PKG.name} init [folder]   set the kit up next to the .pbip in [folder] (default: current folder)
      --table <name>     host table for the generated measures (default: ask)
      --page <id|name>   report page to build on (default: ask)
      --style <preset>   ${STYLES.join(' | ')} (default: accent)
      --yes              take the defaults / the only choice without asking
      --force            overwrite an existing _build/ and kit copy
  npx ${PKG.name} doctor          check Python, Node, Edge and Power BI Desktop

After init, open the folder in your agent (Claude Code, Cursor, Codex, ...) and ask for the dashboard.
Docs: ${PKG.homepage}`);
}

function run(cmd, a) {
  const r = spawnSync(cmd, a, { encoding: 'utf8', shell: false });
  return r.status === 0 ? (r.stdout || r.stderr || '').trim() : null;
}

function doctor() {
  const py = run('python', ['--version']) || run('py', ['-3', '--version']);
  const edgePaths = [process.env.EDGE_PATH, 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    'C:/Program Files/Microsoft/Edge/Application/msedge.exe'].filter(Boolean);
  const edge = edgePaths.find((p) => existsSync(p));
  const major = Number(process.versions.node.split('.')[0]);
  const desktop = process.platform === 'win32' ? (run('tasklist', ['/FI', 'IMAGENAME eq PBIDesktop.exe']) || '') : '';
  const rows = [
    ['Windows', process.platform === 'win32', process.platform],
    ['Node 22+', major >= 22, process.versions.node],
    ['Python 3', !!py && /Python 3/.test(py), py || 'not found (install from python.org)'],
    ['Microsoft Edge', !!edge, edge || 'not found (set EDGE_PATH)'],
    ['Power BI Desktop running', /PBIDesktop/i.test(desktop), /PBIDesktop/i.test(desktop) ? 'yes' : 'not running (open your .pbip before the live DAX test)'],
  ];
  for (const [n, ok, v] of rows) say(`  ${ok ? 'OK ' : '-- '} ${n.padEnd(26)} ${v}`);
  return rows.slice(0, 4).every((r) => r[1]);
}

async function choose(rl, label, items, wanted, show = (x) => x) {
  if (wanted !== undefined) {
    const hit = items.find((x) => [x.id, x.name, x].includes(wanted));
    if (!hit) fail(`${label} "${wanted}" not found. Options: ${items.map(show).join(', ')}`);
    return hit;
  }
  if (items.length === 1 || has('yes')) return items[0];
  // no terminal (an agent or a script): never wait on a prompt nobody can answer
  if (!process.stdin.isTTY) fail(`${label}: ${items.length} options and no terminal to ask in - pass it as a flag (or --yes for the first): ${items.map(show).join(', ')}`);
  say(`\n${label}:`);
  items.forEach((x, i) => say(`  ${i + 1}. ${show(x)}`));
  const a = await rl.question(`Choose 1-${items.length} [1]: `);
  const n = Number(a.trim() || '1');
  if (!(n >= 1 && n <= items.length)) fail(`no such choice: ${a}`);
  return items[n - 1];
}

async function init() {
  const dir = resolve(positional[1] || '.');
  if (!existsSync(dir)) fail(`folder not found: ${dir}`);
  const pbips = readdirSync(dir).filter((f) => f.toLowerCase().endsWith('.pbip'));
  if (!pbips.length) fail(`no .pbip in ${dir}. Save the report as a Power BI Project first (File > Save as > .pbip).`);
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  try {
    const project = basename(await choose(rl, 'Project', pbips, flag('project')), '.pbip');
    const model = join(dir, `${project}.SemanticModel`), report = join(dir, `${project}.Report`);
    if (!existsSync(model) || !existsSync(report)) fail(`${project}.SemanticModel / ${project}.Report not found next to ${project}.pbip`);

    const tdir = join(model, 'definition', 'tables');
    const tables = existsSync(tdir) ? readdirSync(tdir).filter((f) => f.endsWith('.tmdl')).map((f) => {
      const text = readFileSync(join(tdir, f), 'utf8');
      const first = text.split(/\r?\n/).find((l) => l.startsWith('table ')) || '';
      const name = first.replace(/^table\s+/, '').replace(/^'(.*)'$/, '$1').trim() || basename(f, '.tmdl');
      // Power BI's own auto date tables and hidden tables never host the dashboard's measures
      const auto = /^(DateTableTemplate_|LocalDateTable_)/.test(name) || /^\s*(isHidden|showAsVariationsOnly)\s*$/m.test(text.split(/\r?\n\s*column /)[0]);
      return { id: f, name, auto };
    }).filter((t) => !t.auto) : [];
    if (!tables.length) fail(`no user tables in ${tdir} (is the model saved in TMDL format?)`);
    if (tables.length > 1 && has('yes') && flag('table') === undefined)
      fail(`the model has ${tables.length} tables - pick the one that hosts the measures with --table: ${tables.map((t) => t.name).join(', ')}`);
    const table = await choose(rl, 'Table that hosts the generated measures', tables, flag('table'), (t) => t.name);

    const pdir = join(report, 'definition', 'pages');
    const pages = existsSync(pdir) ? readdirSync(pdir).filter((d) => existsSync(join(pdir, d, 'page.json'))).map((d) => {
      const pj = JSON.parse(readFileSync(join(pdir, d, 'page.json'), 'utf8'));
      return { id: d, name: pj.displayName || d };
    }) : [];
    if (!pages.length) fail(`no pages in ${pdir} (is the report saved in PBIR format?)`);
    const page = await choose(rl, 'Report page to build on', pages, flag('page'), (p) => `${p.name}  (${p.id})`);

    let style = flag('style');
    if (style === undefined && !has('yes')) {
      say(`\nStyle (see skills/colorful-styles): ${STYLES.join(', ')} - or a brand later, in pipeline.json`);
      style = (await rl.question('Style [accent]: ')).trim() || 'accent';
    }
    style = style || 'accent';
    if (!STYLES.includes(style)) fail(`unknown style "${style}". Use one of: ${STYLES.join(', ')}`);

    // 1. the kit, for the agent to read
    const kitDest = join(dir, PKG.name);
    if (existsSync(kitDest) && !has('force')) say(`\nkit copy exists, kept: ${kitDest} (--force to refresh)`);
    else { for (const p of KIT_PARTS) if (existsSync(join(KIT, p))) cpSync(join(KIT, p), join(kitDest, p), { recursive: true }); say(`\nkit copied:      ${kitDest}`); }

    // 2. the pipeline, next to the PBIP
    const build = join(dir, '_build');
    if (existsSync(build) && !has('force')) fail(`${build} exists - keep it, or rerun with --force to overwrite the pipeline files`);
    cpSync(PIPE, build, { recursive: true });
    say(`pipeline copied: ${build}`);

    // 3. a clean backup copy (the writer rebuilds the model's TMDL from it)
    const backup = join(dir, '_backup');
    if (!existsSync(join(backup, `${project}.SemanticModel`))) {
      for (const p of [`${project}.pbip`, `${project}.Report`, `${project}.SemanticModel`])
        cpSync(join(dir, p), join(backup, p), { recursive: true, filter: (s) => !/[\\/]\.pbi[\\/](cache\.abf|localSettings\.json)$/.test(s) });
      say(`backup made:     ${backup}`);
    } else say(`backup exists, kept: ${backup}`);

    // 4. pipeline.json
    // the dashboard speaks the data's language: Hebrew/Arabic names -> RTL, otherwise LTR English (change in pipeline.json)
    const ttext = readFileSync(join(tdir, table.id), 'utf8');
    const lang = /[֐-׿]/.test(ttext) ? 'he' : /[؀-ۿ]/.test(ttext) ? 'ar' : 'en';
    const cfg = { project, table: table.name, page_id: page.id, page_display_name: page.name, backup_dir: '_backup',
      partition_m: null, lineage_namespace: 'pbi-html-dashboard', style, dir: lang === 'en' ? 'ltr' : 'rtl', lang };
    say(`\nlanguage:        ${lang} (${cfg.dir}) - from the names in ${table.name}; change "lang"/"dir" in pipeline.json if the dashboard should differ`);
    if (table.id !== `${table.name}.tmdl`) cfg.tmdl_file = table.id;
    writeFileSync(join(build, 'pipeline.json'), JSON.stringify(cfg, null, 2) + '\n', 'utf8');
    say(`config written:  ${join(build, 'pipeline.json')}`);

    // 5. tell any agent where to start (never overwrite the user's own files)
    const pointer = `# Power BI dashboards in this folder\n\nBefore building or changing the dashboard, read \`${PKG.name}/AGENTS.md\` and follow it. The pipeline is in \`_build/\` (config: \`_build/pipeline.json\`).\n`;
    for (const f of ['AGENTS.md', 'CLAUDE.md']) {
      if (!existsSync(join(dir, f))) { writeFileSync(join(dir, f), pointer, 'utf8'); say(`agent pointer:   ${join(dir, f)}`); }
      else say(`${f} exists, left as is - add a line pointing to ${PKG.name}/AGENTS.md`);
    }
    say('\nchecks:');
    doctor();
    say(`\nNext: open this folder in your agent and ask, e.g.
  "Build an executive page on ${table.name} with a KPI row, a filter panel and a breakdown, in our brand color."
The agent writes _build/measures.py for your model (examples: _build/measures_example_*.py) and runs the gates
before it writes anything into the report.`);
  } finally { rl.close(); }
}

const cmd = positional[0];
if (!cmd || has('help') || cmd === 'help') help();
else if (cmd === 'init') await init();
else if (cmd === 'doctor') process.exit(doctor() ? 0 : 1);
else if (cmd === '--version' || has('version')) say(PKG.version);
else { help(); process.exit(1); }
