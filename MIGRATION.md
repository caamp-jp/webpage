# Migration Notes

`caamp.jp` を WordPress 管理から `github.io` 上の静的サイトへ移行する際のメモです。移行期だけ必要な作業をここに分離して管理します。

## 移行期の流れ

1. オリジナルの `caamp.jp` を `site/caamp.jp` にクロールする
2. クロール結果を元に `scripts/build_static_site.py` で `docs/` と必要なアセットを固める
3. 現在の公開内容を `SITE_CONTENT.md` にまとめる
4. 以降は `SITE_CONTENT.md` を正本として `scripts/build_site_from_markdown.py` で `docs/` を再生成する

## クロール

```bash
bash scripts/crawl_source_site.sh
```

- 既定では `site/caamp.jp/` に保存されます
- `site/` は一時データであり、コミットしません

## 静的化

```bash
python3 scripts/build_static_site.py
```

- このスクリプトは移行期のベースライン生成用です
- `docs/` の内容を上書きします

## 移行後

- 継続的な更新は `SITE_CONTENT.md` と `scripts/build_site_from_markdown.py` を使います
- 再クロールは移行期に必要な場合だけ行います
