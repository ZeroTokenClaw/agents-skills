#!/usr/bin/env python3
"""Extract head/tail source pages for China software-copyright identification materials.

Default assumption (verify with current CCPC rules before filing):
  - 30 pages from the start + 30 pages from the end
  - >= 50 lines per page (last page may be shorter)

Usage:
  python extract_source_pages.py --src ./project --out ./软著材料_demo/source_pages \\
      --title "示例管理系统 V1.0" --ext .py,.ts,.js,.go,.java
"""

from __future__ import annotations

import argparse
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "node_modules",
    "dist",
    "build",
    "out",
    "target",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
}


def collect_lines(root: Path, exts: set[str]) -> list[str]:
    lines: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in exts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        lines.append(f"// ===== FILE: {rel} =====")
        lines.extend(text.splitlines())
        lines.append("")
    return lines


def paginate(lines: list[str], lines_per_page: int) -> list[list[str]]:
    pages: list[list[str]] = []
    for i in range(0, len(lines), lines_per_page):
        pages.append(lines[i : i + lines_per_page])
    return pages or [[]]


def select_pages(pages: list[list[str]], head: int, tail: int) -> list[tuple[int, list[str]]]:
    n = len(pages)
    if n <= head + tail:
        return [(i + 1, p) for i, p in enumerate(pages)]
    selected: list[tuple[int, list[str]]] = []
    for i in range(head):
        selected.append((i + 1, pages[i]))
    for i in range(n - tail, n):
        selected.append((i + 1, pages[i]))
    return selected


def write_pages(
    selected: list[tuple[int, list[str]]],
    out_dir: Path,
    title: str,
    lines_per_page: int,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    index_lines = [
        f"# Source extraction for: {title}",
        f"lines_per_page={lines_per_page}",
        f"pages_written={len(selected)}",
        "",
    ]
    for seq, (orig_no, page_lines) in enumerate(selected, start=1):
        name = f"page_{seq:03d}_orig_{orig_no:04d}.txt"
        body = [f"{title}", f"original_page={orig_no}", ""] + page_lines
        (out_dir / name).write_text("\n".join(body) + "\n", encoding="utf-8")
        index_lines.append(f"- {name} (orig page {orig_no}, lines={len(page_lines)})")
    (out_dir / "INDEX.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, required=True, help="Source tree root")
    parser.add_argument("--out", type=Path, required=True, help="Output directory")
    parser.add_argument("--title", required=True, help="Software full name + version for header")
    parser.add_argument("--ext", default=".py,.ts,.tsx,.js,.jsx,.go,.java,.cs", help="Comma-separated suffixes")
    parser.add_argument("--lines-per-page", type=int, default=50)
    parser.add_argument("--head", type=int, default=30)
    parser.add_argument("--tail", type=int, default=30)
    args = parser.parse_args()

    exts = {e if e.startswith(".") else f".{e}" for e in args.ext.split(",") if e.strip()}
    exts = {e.lower().strip() for e in exts}

    lines = collect_lines(args.src.resolve(), exts)
    if not lines:
        raise SystemExit(f"No source lines found under {args.src} with extensions {sorted(exts)}")

    pages = paginate(lines, args.lines_per_page)
    selected = select_pages(pages, args.head, args.tail)
    write_pages(selected, args.out.resolve(), args.title, args.lines_per_page)
    print(f"OK: total_lines={len(lines)} total_pages={len(pages)} written={len(selected)} -> {args.out}")


if __name__ == "__main__":
    main()
