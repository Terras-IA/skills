---
name: terras-astro
description: Publica site estático multilíngue de graça no Cloudflare Pages com Astro e conteúdo em markdown. Use para criar site ou blog estático, configurar i18n, converter markdown em site e subir hospedagem gratuita.
keywords: [astro.js, site astro, projeto astro, framework astro, cloudflare pages]
---

# Astro Static Site Generator

Deploy multilingual static websites for free on Cloudflare using Astro framework.

## Prerequisites

- Node.js 20+ installed
- Cloudflare account (free)
- Git repository (GitHub, GitLab, or Bitbucket)

## Quick Start

### 1. Create Project

```bash
npm create astro@latest my-site -- --template minimal
cd my-site
npm install
```

### 2. Configure for Cloudflare

**Static (Recommended for most use cases)** — no adapter:

```javascript
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://your-site.pages.dev',
});
```

**SSR/Edge (Optional):** `npm install @astrojs/cloudflare` and set `output: 'server'` with `adapter: cloudflare()` → `references/cloudflare-pages.md`.

### 3. Deploy to Cloudflare

**Git Integration (Recommended):** push to Git → Cloudflare Dashboard → Pages → Create project → Connect to Git → Build command `npm run build`, Build output `dist`.

**Direct Upload:** `npx wrangler pages deploy dist`

## Reference

- **Multilingual (i18n) setup** — config, routing modes, content structure/schema, language switcher, i18n scripts → `references/i18n-multilingual.md`
- **Content collections / blog** — file structure, `[...slug].astro` dynamic blog pages → `references/content-collections.md`
- **Cloudflare Pages** — deploy (git + direct), SSR/edge adapter, settings, custom domain, redirects, commands, troubleshooting → `references/cloudflare-pages.md`

## Scripts

| Script | Description |
|--------|-------------|
| `astro-new-post.py` | Create multilingual blog posts |
| `astro-i18n-check.py` | Validate translation coverage |

Usage examples → `references/i18n-multilingual.md`. All scripts use only Python standard library (no dependencies).
