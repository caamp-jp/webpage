# caamp.jp

このリポジトリは、`caamp.jp` の静的サイトを `docs/` 配下で管理するためのものです。通常運用では `SITE_CONTENT.md` を正本として更新し、そこから静的ページを再生成します。

## 構成

- `docs/`
  公開用の静的サイトです。日本語ページ、英語ページ、`assets/`、`.nojekyll` をこの配下で管理します。
- `SITE_CONTENT.md`
  現在の正本となる Markdown ファイルです。ページ本文、一覧データ、主要な UI 文言を保持します。
- `scripts/build_site_from_markdown.py`
  `SITE_CONTENT.md` を元に `docs/` を再生成するスクリプトです。
- `scripts/serve_static_site.py`
  `docs/` をローカル HTTP サーバーで配信するスクリプトです。

## 前提

- Python 3
- `beautifulsoup4`

`beautifulsoup4` が未導入の場合は、以下で追加します。

```bash
python3 -m pip install beautifulsoup4
```

## Markdown からの再生成

移行後は `SITE_CONTENT.md` を編集し、以下で `docs/` を再生成します。

```bash
python3 scripts/build_site_from_markdown.py
```

このコマンドは `SITE_CONTENT.md` の内容を使って HTML を上書きします。アセットは既存の `docs/assets/` をそのまま利用します。

## ローカル確認

以下で `docs/` をローカル配信できます。

```bash
python3 scripts/serve_static_site.py
```

既定では `http://127.0.0.1:8000/` で確認できます。

## 移行について

移行期には、WordPress 管理だった `caamp.jp` を `site/caamp.jp` にクロールし、`scripts/build_static_site.py` で `docs/` とアセットの初期ベースラインを作成しました。以降は `SITE_CONTENT.md` を正本として運用し、移行専用の手順は [MIGRATION.md](/home/cabot/src/webpage/MIGRATION.md) に分離しています。
