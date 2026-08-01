// @ts-check
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  // 部署到自定义域名（EdgeOne Pages）
  site: 'https://hwj123hwj.asia',

  integrations: [
    react(),
    sitemap({
      i18n: {
        defaultLocale: 'zh',
        locales: { zh: 'zh', en: 'en' },
      },
    }),
  ],

  vite: {
    plugins: [tailwindcss()],
  },

  // 构建产物输出到 dist/
  output: 'static',
});
