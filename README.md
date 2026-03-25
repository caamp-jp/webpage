# caamp.jp

このリポジトリは、`caamp.jp` の静的サイトを `docs/` 配下で管理するためのものです。運用上の正本は private repo の `caamp-jp/preview` で、公開用の `caamp-jp.github.io` は `preview/main` を mirror します。通常運用では `SITE_CONTENT.json` を正本として更新し、PR には生成済みの `docs/` も含めます。

## 更新の依頼について

アクセス権のある方は [Issue (private)](https://github.com/caamp-jp/preview/issues) に更新の依頼を投稿してください。

アクセス権については [@daisukes](https://github.com/daisukes) までご連絡ください。

## 通常の更新手順

通常は public repo を直接編集しません。更新時は次の流れを前提にします。

1. `caamp-jp/preview` の Issue で更新内容を管理する
2. `preview/main` から作業ブランチを切る
3. `SITE_CONTENT.json`、`X_EMBED.txt`、必要な script を更新する
4. `python3 scripts/build_site_from_json.py` で `docs/` を再生成する
5. PR を `preview/main` に作成する
6. GitHub Actions が `docs/` の整合性を検証する
7. `preview/main` へ merge すると、tracked tree 全体が `caamp-jp.github.io` の `main` に同期される

PR では source だけでなく生成済みの `docs/` も含めてください。CI は PR 上で再生成を実行し、差分が残る場合は fail します。

## GitHub Actions

- `Validate Preview PR`
  `caamp-jp/preview` の `main` 向け PR で `python3 scripts/build_site_from_json.py` を実行し、`docs/` の差分や未追跡生成物が残らないことを確認します。
- `Sync Public Mirror`
  `caamp-jp/preview` の `main` への push で、tracked tree を `caamp-jp.github.io` の `main` に mirror します。同じ workflow が public repo にあっても、repo 条件で no-op になります。

`Sync Public Mirror` を有効にするには、preview repo の Actions secret に `PUBLIC_REPO_SYNC_TOKEN` を追加してください。この token は `caamp-jp/caamp-jp.github.io` に対して `contents:write` が必要です。

## 構成

- `docs/`
  公開用の静的サイトです。日本語ページ、英語ページ、`assets/`、`.nojekyll` をこの配下で管理します。PR には生成済みの内容を含めます。
- `SITE_CONTENT.json`
  現在の正本となる JSON ファイルです。ページ本文、一覧データ、主要な UI 文言を保持します。
- `X_EMBED.txt`
  News/SNS セクションに表示する X 埋め込みの正本です。
- `scripts/build_site_from_json.py`
  `SITE_CONTENT.json` から `docs/` を再生成するスクリプトです。
- `scripts/check_generated_docs.sh`
  `docs/` が source と一致しているかを検証するスクリプトです。
- `scripts/process_issue_with_codex.sh`
  `gh` で Issue を読み込み、Codex CLI で変更を行い、`codex/issue-<number>` ブランチ作成、PR 作成、Issue コメントまで自動化するスクリプトです。
- `scripts/sync_public_repo.sh`
  現在の tracked tree を public repo に mirror するスクリプトです。
- `scripts/serve_static_site.py`
  `docs/` をローカル HTTP サーバーで配信するためのスクリプトです。

## 前提

- Python 3
- preview repo での GitHub Actions 利用
- public repo へ push できる `PUBLIC_REPO_SYNC_TOKEN`

## ローカルで確認する場合

### `docs/` の再生成

```bash
python3 scripts/build_site_from_json.py
```

### 生成物の整合性チェック

```bash
scripts/check_generated_docs.sh
```

### Issue から Codex で更新する

```bash
scripts/process_issue_with_codex.sh ISSUE_NUMBER
```

既定では private repo の `caamp-jp/preview` を対象に、Issue を読んでページ変更か判定し、該当する場合は `codex/issue-<number>` ブランチを `main` から切って更新します。Codex CLI は `gpt-5.4` と `medium` を使い、`danger-full-access` で実行します。PR 本文と Issue コメントの先頭には `Codexが生成したコメントです。` を必ず付けます。

### ローカル配信

```bash
python3 scripts/serve_static_site.py
```

既定では `http://127.0.0.1:8000/` で確認できます。

## 移行について

移行期には、WordPress 管理だった `caamp.jp` を `site/caamp.jp` にクロールし、`scripts/build_static_site.py` で `docs/` とアセットの初期ベースラインを作成しました。`beautifulsoup4` を含む移行専用依存の扱いは [MIGRATION.md](./MIGRATION.md) に分離しています。以降は `SITE_CONTENT.json` を正本として運用します。
