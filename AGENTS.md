# Repository Guidelines

## Purpose

- This repository migrates `caamp.jp` from WordPress to a static site hosted from GitHub Pages.
- The published site lives in `docs/`.
- After migration, `SITE_CONTENT.json` becomes the content source of truth for structured site content.
- X post embed snippets for the News/SNS section live in `X_EMBED.txt`.
- Migration-only notes live in `MIGRATION.md`.

## Structure

- `docs/`: deployed static site, including Japanese pages, English pages under `docs/en/`, and shared assets.
- `SITE_CONTENT.json`: JSON source for page copy, list data, and major UI labels after migration.
- `X_EMBED.txt`: source for embedded X posts shown in the News/SNS section. Paste official embed snippets here.
- `MIGRATION.md`: migration-period crawl and bootstrap notes.
- `scripts/build_static_site.py`: migration-time build from a local crawl in `site/caamp.jp`.
- `scripts/build_site_from_json.py`: rebuilds `docs/` from `SITE_CONTENT.json`.
- `scripts/serve_static_site.py`: serves `docs/` locally for review.
- `scripts/crawl_source_site.sh`: crawls the original `https://caamp.jp/` into `site/caamp.jp`.
- `site/`: temporary local crawl data. Do not commit it.

## Workflow

1. During migration, crawl the original site into `site/caamp.jp` when needed.
2. Use `scripts/build_static_site.py` only while extracting the original site into a static baseline.
3. Keep migration-specific instructions in `MIGRATION.md`.
4. Consolidate ongoing content into `SITE_CONTENT.json`.
5. Update `X_EMBED.txt` when the News/SNS section should show different X posts.
6. Rebuild the site from `SITE_CONTENT.json` with `scripts/build_site_from_json.py`.
7. Review locally by serving `docs/`.
8. Commit only the generated site, scripts, `X_EMBED.txt`, and documentation. Never commit `site/`.

## Editing Notes

- Keep asset and page links relative so the site can work under different GitHub Pages paths.
- Treat `docs/` as generated output when changing page structure. Prefer updating the generators and `SITE_CONTENT.json` instead of hand-editing HTML.
- For X embeds, update `X_EMBED.txt` instead of hand-editing `docs/news/index.html` or `docs/en/news/index.html`.
- `X_EMBED.txt` may contain multiple official embed snippets. The generator extracts each `blockquote.twitter-tweet` and includes `widgets.js` once.
- Re-crawling is only expected during the migration period.
