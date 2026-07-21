# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**D2R Reimagined** — a Diablo II: Resurrected mod (v3.0.10) with a companion data-browsing website, documentation wikis, and a Wiki.js server.

## Repository Structure

| Directory | Purpose |
|-----------|---------|
| `mod/` | Core mod — D2R game data tables (excel .txt files) and processing scripts |
| `mod/data/global/excel/` | Game balance files (armor, skills, cubemain, magicprefix/suffix, sets, uniques, runes, etc.) |
| `mod/scripts/` | Data export/translation utilities (Python, Node.js, batch) |
| `website/` | Aurelia 2 + Vite + Tailwind v4 SPA for browsing mod data |
| `website/src/pages/` | Pages: bases, affixes, uniques, sets, runewords, cube-recipes, grail, home |
| `website/src/utilities/` | Translation store, format-template, damage types, filtering, sorting |
| `website/src/resources/` | Constants, property groups, Aurelia value converters |
| `website/static/data/keyed/` | JSON data files (armors, weapons, uniques, sets, runewords, cube-recipes, magicprefix, magicsuffix) |
| `website/static/data/strings/` | Translation string maps (zhCN, enUS, deDE, frFR, etc.) |
| `wiki/` | English documentation wiki |
| `wiki-zh/` | Chinese documentation wiki |
| `server/` | Wiki.js server instance |
| `docs/website-compact/` | Auto-generated compact Markdown indexes from website data |
| `docs/` | Built website output (vite build target) |

## Key Commands

### Website (in `website/`)

```bash
cd website
pnpm install          # Install dependencies (pnpm 10.33.2)
pnpm start            # Dev server on port 3001
pnpm build            # Build to docs/ + create 404.html
pnpm test             # Run vitest tests
pnpm test:watch       # Watch mode for tests
pnpm lint             # ESLint + HTMLHint
pnpm lint:fix         # ESLint auto-fix
```

### Compact Markdown Generation (root)

```bash
node docs/website-compact/generate.js
```
Generates 6 compact .md files (item-bases, affixes, uniques, sets, runewords, cube-recipes) from website JSON data + zhCN translations, each ≤200KB.

## Data Architecture

### Keyed Line Format

Game data is exported into `static/data/keyed/*.json` using the `d2r-multi-export-tool`. Every property is stored as:

```jsonc
{ "key": "ModStre10d", "args": [3, "FireBolt", 5, 12] }
```

At render time, the website looks up `key` in the active-language string map and applies positional args via `format-template.ts`.

### Translation Flow

1. `website/src/utilities/translation-store.ts` — singleton store with `setLanguage()`, `t(key, args)`, `format(KeyedLine)`
2. String maps at `static/data/strings/{code}.json` — flat key→template maps
3. Fallback chain: active language → enUS → bare key
4. `format-template.ts` handles D2R-style templates (`%d`, `%s`, `%+d`, indexed `%0`-`%9`, range collapsing `[min, max]` → `min-max`)

### Affix Property Groups

`website/src/resources/property_groups.json` maps numeric group IDs to descriptions (e.g., "Damage", "Resistances", "Skill Levels"). Used by the affixes page for filtering and by the compact generator for section grouping.

## Mod Excel Data (in `mod/data/global/excel/`)

These are the authoritative game-balance .txt files:
- `armor.txt`, `weapons.txt` — item bases
- `magicprefix.txt`, `magicsuffix.txt` — affixes
- `sets.txt`, `setitems.txt` — set items
- `uniques.txt` — unique items
- `runes.txt` — runewords
- `cubemain.txt` — cube recipes
- `skills.txt`, `skillcalc.txt` — skills
- `properties.txt` — property definitions
- `itemstatcost.txt` — stat cost definitions
- `itemtypes.txt` — item type hierarchy

## Start Script

`server/start.sh` — one-click startup for the Wiki.js server.
