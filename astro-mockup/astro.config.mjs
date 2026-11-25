import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightLinksValidator from 'starlight-links-validator';
import redirects from './src/redirects.json' with { type: 'json' };

export default defineConfig({
  site: 'https://www.extra-ransom.net',
  trailingSlash: 'always',
  redirects,
  integrations: [
    starlight({
      title: 'extra-ransom, super-chainsaw',
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/tommyorndorff/extra-ransom' },
      ],
      editLink: {
        baseUrl: 'https://github.com/tommyorndorff/extra-ransom/edit/main/content/',
      },
      customCss: ['./src/styles/custom.css'],
      plugins: [starlightLinksValidator({
        // standalone pages and assets served verbatim from public/ (not Starlight content)
        exclude: ['/warbirds/**', '/salamanders/**', '/couch-to-5k/**', '/norway/**', '/frame-calc/**', '/static/**', '/goat/**'],
      })],
      sidebar: [
        // Equipment (docs/equipment) is draft: true, which Hugo also hides in CI; add back when un-drafted.
        { label: 'Rodmaking', items: [{ autogenerate: { directory: 'docs/rodmaking' } }] },
        { label: 'Woodworking', items: [{ autogenerate: { directory: 'docs/woodworking' } }] },
        { label: 'Coffee Roasting', items: [{ autogenerate: { directory: 'docs/coffee-roasting' } }] },
        { label: 'Hydroponics', items: [{ autogenerate: { directory: 'docs/hydroponics' } }] },
        { label: 'Fishing', items: [{ autogenerate: { directory: 'docs/fishing' } }] },
        { label: 'Miscellany', items: [{ autogenerate: { directory: 'docs/miscellany' } }] },
      ],
    }),
  ],
});
