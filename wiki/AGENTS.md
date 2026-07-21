## 中文翻译
AI 自定义说明文件，解释本仓库是 D2R Reimagined 静态 Wiki。

# AGENTS

## Repository overview
- This repository is a local copy of the D2R Reimagined wiki content.
- It is primarily a static site made of HTML and Markdown files, not a traditional application repository.
- The homepage is `home.html`.

## Primary guidance for AI agents
- Treat this repo as a static documentation/wiki site.
- Do not invent a web app build process; there is no `package.json`, no `npm`, and no backend code.
- Use local preview with a static server when possible because many pages use root-relative links (`/en/...`) and external assets.

## How to preview locally
- Recommended: run a static file server from the repo root.
  - Example:
    - `cd d:\Downloads\wiki-content-main\wiki-content-main`
    - `python -m http.server 8000`
    - open `http://127.0.0.1:8000/home.html`
- Direct file open via `file:///.../home.html` may work for many pages, but a local server better preserves relative linking.

## Important files and directories
- `home.html` — local wiki entry point.
- `README.md` — repo description.
- `wiki_formatting.js` — client-side helper for highlighting and formatting wiki content.
- `Builds/`, `Items/`, `Patch_Notes/`, `recipes/`, `installguides/`, `newbieguide/`, `DesktopLauncher/` — major content sections.

## Content conventions
- HTML files often contain metadata frontmatter inside HTML comments at the top.
- Many pages are written as static wiki content and link to the live site (`https://wiki.d2r-reimagined.com/...`).
- Preserve existing page structure and internal links when editing.

## When modifying content
- Prefer editing the existing HTML/MD content in place.
- Keep original navigation and link patterns intact unless fixing broken local links.
- If you add new pages, follow the existing folder structure and naming conventions.

## Notes for AI agents
- This repository is not a source code project in the usual sense.
- Focus on documentation/content editing, local static preview, and preserving wiki formatting.
