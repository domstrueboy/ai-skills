#!/usr/bin/env python3
"""Assemble an overview from parts/*.md, add a contents list, and check it.

Usage:
  build_overview.py <overview-dir> <Name> [--lang ru --contents-title "Содержание"]

Reads <overview-dir>/parts/*.md (or parts/<lang>/*.md), sorted by file name,
skipping files that start with "_". The first part is the intro; the contents
list of all later "## " headings goes right after it. Writes
<overview-dir>/<Name>-overview.md (or <Name>-overview.<lang>.md), then checks
that every embedded image exists and, for a translation, that headings, images
and table rows match the base file.
"""
import argparse
import re
import sys
from pathlib import Path

IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")


def slug(text, seen):
    s = re.sub(r"[^\w\- ]", "", text.strip().lower(), flags=re.UNICODE)
    s = s.replace(" ", "-")
    n = seen.get(s, 0)
    seen[s] = n + 1
    return s if n == 0 else f"{s}-{n}"


def stats(text):
    return {
        "headings": len(re.findall(r"^#{1,6} ", text, re.M)),
        "images": IMG.findall(text),
        "table_rows": len(re.findall(r"^\|", text, re.M)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("name")
    ap.add_argument("--lang")
    ap.add_argument("--contents-title", default="Contents")
    a = ap.parse_args()

    root = Path(a.dir)
    src = root / "parts" / a.lang if a.lang else root / "parts"
    parts = sorted(p for p in src.glob("*.md") if not p.name.startswith("_"))
    if not parts:
        sys.exit(f"no parts in {src}")
    texts = [p.read_text(encoding="utf-8").strip() for p in parts]

    seen = {}
    all_text = "\n\n".join(texts)
    for line in all_text.splitlines():
        if line.startswith("## "):
            slug(line[3:], seen)
    seen_toc = {}
    for line in texts[0].splitlines():
        if line.startswith("## "):
            slug(line[3:], seen_toc)
    toc = [f"## {a.contents_title}", ""]
    for t in texts[1:]:
        for line in t.splitlines():
            if line.startswith("## "):
                toc.append(f"- [{line[3:].strip()}](#{slug(line[3:], seen_toc)})")
    body = [texts[0], "\n".join(toc), "---", *texts[1:]]
    out_text = "\n\n".join(body) + "\n"

    out = root / (f"{a.name}-overview.{a.lang}.md" if a.lang else f"{a.name}-overview.md")
    out.write_text(out_text, encoding="utf-8")

    st = stats(out_text)
    missing = [i for i in st["images"] if not (root / i).exists()]
    used = {Path(i).name for i in st["images"]}
    unused = sorted(p.name for p in (root / "images").glob("*") if p.name not in used) if (root / "images").exists() else []
    print(f"wrote {out}: {st['headings']} headings, {len(st['images'])} images, {st['table_rows']} table rows")
    ok = True
    if missing:
        ok = False
        print("MISSING images:", *missing, sep="\n  ")
    if unused:
        print("unused images (fine if intentional):", *unused, sep="\n  ")
    if a.lang:
        base = root / f"{a.name}-overview.md"
        if base.exists():
            b = stats(base.read_text(encoding="utf-8"))
            for k in ("headings", "table_rows"):
                if b[k] != st[k]:
                    ok = False
                    print(f"MISMATCH {k}: base {b[k]} vs {a.lang} {st[k]}")
            if b["images"] != st["images"]:
                ok = False
                print("MISMATCH image links (order or paths differ from the base file)")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
