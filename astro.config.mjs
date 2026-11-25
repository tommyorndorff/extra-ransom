import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';
import fs from 'node:fs';
import redirects from './src/redirects.json' with { type: 'json' };

// Starlight's autogenerate also emits subdirectories as groups labelled by folder name, so a group's own pages
// are listed here explicitly (ordered by sidebar.order, then filename) and each subdirectory becomes a labelled group.
const DOCS = new URL('./src/content/docs/docs/', import.meta.url);
function pages(dir) {
  const base = new URL(dir + '/', DOCS);
  return fs.readdirSync(base, { withFileTypes: true })
    .filter((d) => d.isFile() && d.name.endsWith('.md') && !fs.readFileSync(new URL(d.name, base), 'utf8').match(/^draft:\s*true/m))
    .map((d) => {
      const order = fs.readFileSync(new URL(d.name, base), 'utf8').match(/^\s*order:\s*(-?\d+)/m);
      return { slug: `docs/${dir}/${d.name === 'index.md' ? '' : d.name.replace(/\.md$/, '')}`.replace(/\/$/, ''), order: order ? +order[1] : 1e6, name: d.name };
    })
    .sort((a, b) => a.order - b.order || a.name.localeCompare(b.name))
    .map((p) => p.slug);
}
const sub = (label, dir) => ({ label, collapsed: true, items: [{ autogenerate: { directory: `docs/${dir}` } }] });
const section = (label, dir, subs = []) => ({ label, collapsed: true, items: [...pages(dir), ...subs] });

export default defineConfig({
  site: 'https://www.extra-ransom.net',
  trailingSlash: 'always',
  redirects,
  integrations: [
    starlight({
      title: 'extra-ransom',
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/tommyorndorff/extra-ransom' },
      ],
      editLink: {
        baseUrl: 'https://github.com/tommyorndorff/extra-ransom/edit/main/',
      },
      customCss: ['./src/styles/custom.css'],
      plugins: [starlightLinksValidator({
        // standalone pages and assets served verbatim from public/ (not Starlight content)
        exclude: ['/warbirds/**', '/salamanders/**', '/couch-to-5k/**', '/norway/**', '/frame-calc/**', '/static/**', '/goat/**'],
      })],
      sidebar: [
        // Equipment (docs/equipment) is draft: true, so it is left out of the sidebar and the build; add it back when un-drafted.
        {
          label: 'Rods & fishing',
          collapsed: true,
          items: [
            'docs/rods-and-fishing',
            section('Making rods', 'rods-and-fishing/making', [
              sub('Binders', 'rods-and-fishing/making/binders'),
              sub('Builds', 'rods-and-fishing/making/builds'),
            ]),
            section('Trips', 'rods-and-fishing/trips'),
          ],
        },
        section('Woodworking', 'woodworking', [sub('Furniture plans', 'woodworking/furniture-plans')]),
        section('Coffee roasting', 'coffee-roasting'),
        section('Hydroponics', 'hydroponics'),
        section('Miscellany', 'miscellany'),
      ],
    }),
  ],
});
