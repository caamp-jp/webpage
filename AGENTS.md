# Repository Guidelines

## Purpose

- This repository migrates `caamp.jp` from WordPress to a static site hosted from GitHub Pages.
- The published site lives in `docs/`.
- After migration, `SITE_CONTENT.md` becomes the content source of truth.
- Migration-only notes live in `MIGRATION.md`.

## Structure

- `docs/`: deployed static site, including Japanese pages, English pages under `docs/en/`, and shared assets.
- `SITE_CONTENT.md`: markdown source for page copy, list data, and major UI labels after migration.
- `MIGRATION.md`: migration-period crawl and bootstrap notes.
- `scripts/build_static_site.py`: migration-time build from a local crawl in `site/caamp.jp`.
- `scripts/build_site_from_markdown.py`: rebuilds `docs/` from `SITE_CONTENT.md`.
- `scripts/serve_static_site.py`: serves `docs/` locally for review.
- `scripts/crawl_source_site.sh`: crawls the original `https://caamp.jp/` into `site/caamp.jp`.
- `site/`: temporary local crawl data. Do not commit it.

## Workflow

1. During migration, crawl the original site into `site/caamp.jp` when needed.
2. Use `scripts/build_static_site.py` only while extracting the original site into a static baseline.
3. Keep migration-specific instructions in `MIGRATION.md`.
4. Consolidate ongoing content into `SITE_CONTENT.md`.
5. Rebuild the site from `SITE_CONTENT.md` with `scripts/build_site_from_markdown.py`.
6. Review locally by serving `docs/`.
7. Commit only the generated site, scripts, and documentation. Never commit `site/`.

## Editing Notes

- Keep asset and page links relative so the site can work under different GitHub Pages paths.
- Treat `docs/` as generated output when changing page structure. Prefer updating the generators and `SITE_CONTENT.md` instead of hand-editing HTML.
- Re-crawling is only expected during the migration period.
