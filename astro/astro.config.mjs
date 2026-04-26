// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { remarkBasePaths } from './src/lib/remark-base-paths.js';

const BASE = '/21cb';

export default defineConfig({
  site: 'https://hohyon-ryu.github.io',
  base: BASE,
  trailingSlash: 'ignore',
  integrations: [sitemap()],
  markdown: {
    smartypants: true,
    remarkPlugins: [remarkBasePaths(BASE)],
  },
});
