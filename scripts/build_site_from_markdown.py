#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MD = ROOT / "SITE_CONTENT.md"
START_MARKER = "<!-- SITE_DATA:BEGIN -->"
END_MARKER = "<!-- SITE_DATA:END -->"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_static_site


def load_site_content(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if START_MARKER not in text or END_MARKER not in text:
        raise ValueError(f"Missing data markers in {path}")

    segment = text.split(START_MARKER, 1)[1].split(END_MARKER, 1)[0]
    match = re.search(r"```json\n(.*?)\n```", segment, re.DOTALL)
    if not match:
        raise ValueError(f"Missing JSON code block between markers in {path}")
    return json.loads(match.group(1))


def main() -> None:
    content = load_site_content(SOURCE_MD)
    build_static_site.build_from_content_data(content, copy_assets=False)


if __name__ == "__main__":
    main()
