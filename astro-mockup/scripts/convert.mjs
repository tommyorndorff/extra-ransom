// Converts the Hugo source (../content/docs) into Starlight content. Idempotent; never touches ../content.
import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = path.resolve(root, '../content/docs');
const OUT = path.join(root, 'src/content/docs/docs');
const GOAT_DIR = path.join(root, 'public/goat');
const REDIRECTS = path.join(root, 'src/redirects.json');

// goat: PATH first, then the local copy installed by `go install` into node_modules/.goat
const goatCandidates = ['goat', path.join(root, 'node_modules/.goat/goat')];
let goatBin = null;
for (const c of goatCandidates) {
  try { execFileSync(c, ['-h'], { stdio: 'ignore', input: '' }); goatBin = c; break; }
  catch (e) { if (e.code !== 'ENOENT') { goatBin = c; break; } }
}

const stats = { files: 0, drafts: [], aliases: 0, goatRendered: 0, goatUnrendered: 0, warnings: [] };
const redirects = {};
const canonicals = new Set();

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((d) => {
    const p = path.join(dir, d.name);
    return d.isDirectory() ? walk(p) : d.name.endsWith('.md') ? [p] : [];
  });
}

fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });
fs.rmSync(GOAT_DIR, { recursive: true, force: true });

const files = walk(SRC).sort();
for (const file of files) {
  const rel = path.relative(SRC, file);
  const isIndex = path.basename(rel) === '_index.md';
  const noExt = rel.replace(/\.md$/, '');
  const dirPart = isIndex ? path.dirname(rel) : noExt;
  const canonical = '/docs/' + (dirPart === '.' ? '' : dirPart + '/');
  canonicals.add(canonical);
  const outRel = isIndex ? path.join(path.dirname(rel), 'index.md') : rel;
  const slug = (dirPart === '.' ? 'docs' : dirPart).replace(/[\\/]/g, '-');

  const parsed = matter(fs.readFileSync(file, 'utf8'));
  const data = parsed.data;
  let body = parsed.content;

  const fm = {};
  if (data.title !== undefined) fm.title = data.title;
  else { fm.title = path.basename(noExt); stats.warnings.push(`${rel}: no title`); }
  if (data.date !== undefined) fm.date = data.date;
  if (data.draft !== undefined) fm.draft = data.draft;
  if (data.weight !== undefined) { fm.weight = data.weight; fm.sidebar = { order: data.weight }; }
  if (data.draft === true) stats.drafts.push(rel);
  const known = new Set(['title', 'date', 'draft', 'weight', 'aliases']);
  for (const k of Object.keys(data)) if (!known.has(k)) stats.warnings.push(`${rel}: dropped front matter key "${k}"`);

  for (const a of [].concat(data.aliases ?? [])) {
    let alias = a.startsWith('/') ? a : '/' + a;
    if (!alias.endsWith('/')) alias += '/';
    redirects[alias] = canonical;
    stats.aliases++;
  }

  // Strip leading H1 duplicating the title
  body = body.replace(/^\s*# (.+)\n+/, (m, h) => (h.trim() === String(fm.title).trim() ? '' : m));

  if (/\{\{[<%]/.test(body)) stats.warnings.push(`${rel}: Hugo shortcode found`);

  // Relative links: resolve like a browser against the page's own URL, emit absolute /docs/.../ links
  {
    const pageUrl = new URL(canonical, 'http://x');
    const fix = (u) => {
      if (/^\/docs\/[^#?.]*[^/#?](?=[#?]|$)/.test(u)) return u.replace(/^([^#?]*)/, '$1/'); // absolute /docs link missing trailing slash
      if (/^([a-z][a-z0-9+.-]*:|\/\/|#|\/)/i.test(u)) return u;
      const m = u.match(/^([^#?]*)([?#].*)?$/);
      let [, p0, tail = ''] = m;
      if (!p0) return u;
      const r = new URL(p0.replace(/\.md$/, ''), pageUrl);
      let out = r.pathname;
      if (/\.[a-z0-9]+$/i.test(out.split('/').pop())) return u;
      if (!out.endsWith('/')) out += '/';
      return out + r.search + tail;
    };
    body = body.split(/(^```[\s\S]*?^```[ \t]*$)/m).map((chunk) => chunk.startsWith('```') ? chunk
      : chunk.replace(/\]\(([^)\s]+)((?:\s+"[^"]*")?)\)/g, (m, u, t) => `](${fix(u)}${t})`)
            .replace(/(href=")([^"]+)(")/g, (m, a, u, b) => a + fix(u) + b)).join('');
  }

  // GoAT blocks
  let n = 0;
  body = body.replace(/^```goat[^\n]*\n([\s\S]*?)^```[ \t]*$/gm, (m, code) => {
    n++;
    if (goatBin) {
      try {
        const svg = execFileSync(goatBin, [], { input: code, encoding: 'utf8' });
        fs.mkdirSync(GOAT_DIR, { recursive: true });
        fs.writeFileSync(path.join(GOAT_DIR, `${slug}-${n}.svg`), svg);
        stats.goatRendered++;
        return `![diagram](/goat/${slug}-${n}.svg)`;
      } catch (e) { stats.warnings.push(`${rel}: goat failed on block ${n}: ${e.message}`); }
    }
    stats.goatUnrendered++;
    return '```text\n' + code + '```';
  });

  const dest = path.join(OUT, outRel);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.writeFileSync(dest, matter.stringify(body, fm));
  stats.files++;
}

for (const a of Object.keys(redirects)) {
  if (canonicals.has(a)) { stats.warnings.push(`alias ${a} collides with a real page; dropped`); delete redirects[a]; }
}
fs.writeFileSync(REDIRECTS, JSON.stringify(Object.fromEntries(Object.entries(redirects).sort()), null, 2) + '\n');

console.log(`files written: ${stats.files}`);
console.log(`drafts (${stats.drafts.length}): ${stats.drafts.join(', ') || 'none'}`);
console.log(`aliases collected: ${stats.aliases} (${Object.keys(redirects).length} redirects)`);
console.log(`goat: ${goatBin ? 'using ' + goatBin : 'UNAVAILABLE'}; rendered ${stats.goatRendered}, unrendered ${stats.goatUnrendered}`);
console.log(`warnings (${stats.warnings.length}):`);
for (const w of stats.warnings) console.log('  - ' + w);
