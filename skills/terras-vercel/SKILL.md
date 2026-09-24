---
name: terras-vercel
description: Deploy applications and manage projects with complete CLI reference. Commands for deployments, projects, domains, environment variables, and live documentation access.
keywords: [vercel]
metadata: {"clawdbot":{"emoji":"▲","requires":{"bins":["vercel","curl"]}}}
---

# Vercel

Complete Vercel CLI reference and documentation access.

## When to Use
- Deploying applications to Vercel
- Managing projects, domains, and environment variables
- Running local development server
- Viewing deployment logs and status
- Looking up Vercel documentation

---

## Documentation

Fetch any Vercel docs page as markdown:

```bash
curl -s "https://vercel.com/docs/<path>" -H 'accept: text/markdown'
```

**Get the full sitemap to discover all available pages:**
```bash
curl -s "https://vercel.com/docs/sitemap.md" -H 'accept: text/markdown'
```

---

## Core Commands

```bash
vercel                        # deploy current directory
vercel --prod                 # deploy to production
vercel -e NODE_ENV=production # deploy with env var
vercel dev                    # local development server (default 0.0.0.0:3000)
vercel link                   # link local dir to project
vercel ls                     # list deployments
vercel logs <url|id>          # view runtime logs (--json for jq)
vercel env list production    # manage environment variables
vercel rollback               # rollback to previous deployment
```

---

## Reference

- **Full CLI reference** (deployment, projects, env vars, domains/aliases, deployments, auth/teams, other commands, global options, quick reference) → `references/cli-reference.md`
- **Live documentation** → use the `curl` docs fetch above (full sitemap available).
