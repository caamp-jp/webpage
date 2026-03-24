# caamp.jp

このリポジトリは、`caamp.jp` の静的サイトを `docs/` 配下で管理するためのものです。通常運用では `SITE_CONTENT.json` を正本として更新し、`docs/` は生成物として扱います。

## 更新の依頼について

アクセス権のある方は [Issue (private)](https://github.com/caamp-jp/preview/issues) に更新の依頼を投稿してください。

アクセス権については [@daisukes](https://github.com/daisukes) までご連絡ください。

## 通常の更新手順

通常は `docs/` を直接編集しません。更新時は次の流れを前提にします。

1. `SITE_CONTENT.json` を更新する
2. PR を作成する
3. `main` にマージする
4. GitHub Actions が `docs/` を自動再生成し、差分があれば反映する

`main` ブランチでは、`SITE_CONTENT.json`、`scripts/build_site_from_json.py`、`scripts/build_static_site.py` の変更が push されると GitHub Actions が `docs/` を再生成します。PR マージによる `main` 更新も対象です。

## 構成

- `docs/`
  公開用の静的サイトです。日本語ページ、英語ページ、`assets/`、`.nojekyll` をこの配下で管理します。通常は GitHub Actions により更新されます。
- `SITE_CONTENT.json`
  現在の正本となる JSON ファイルです。ページ本文、一覧データ、主要な UI 文言を保持します。
- `scripts/build_site_from_json.py`
  手動で `SITE_CONTENT.json` から `docs/` を再生成するためのスクリプトです。
- `scripts/serve_static_site.py`
  手動で `docs/` をローカル HTTP サーバーで配信するためのスクリプトです。

## 前提

- Python 3

## 手作業で再生成する場合

GitHub Actions を待たずにローカルで確認したい場合だけ、以下のスクリプトを使います。

### `docs/` の再生成

```bash
python3 scripts/build_site_from_json.py
```

このコマンドは `SITE_CONTENT.json` の内容を使って HTML を上書きします。アセットは既存の `docs/assets/` をそのまま利用します。

### ローカル確認

以下で `docs/` をローカル配信できます。これも手動確認用です。

```bash
python3 scripts/serve_static_site.py
```

既定では `http://127.0.0.1:8000/` で確認できます。

## 移行について

移行期には、WordPress 管理だった `caamp.jp` を `site/caamp.jp` にクロールし、`scripts/build_static_site.py` で `docs/` とアセットの初期ベースラインを作成しました。`beautifulsoup4` を含む移行専用依存の扱いは [MIGRATION.md](/home/cabot/src/webpage/MIGRATION.md) に分離しています。以降は `SITE_CONTENT.json` を正本として運用します。
