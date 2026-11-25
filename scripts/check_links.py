# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Check that every relative link in the repository's Markdown files resolves (M6).

Scans every Markdown file tracked by git (or, outside a git checkout, every *.md file outside
node_modules, .venv and dist). For each inline link or image ``[text](target)`` whose target is
not an absolute URL (http, https, mailto) the target file must exist, relative to the linking
file; a ``#anchor`` must match a heading slug (GitHub style) in the target file.

Usage: python scripts/check_links.py   (exit 0 and a PASS line when every link resolves)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"node_modules", ".venv", "dist", ".git"}
LINK = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def markdown_files(repo: Path) -> list[Path]:
    try:
        out = subprocess.run(["git", "-C", str(repo), "ls-files", "*.md", "**/*.md"], check=True,
                             capture_output=True, text=True).stdout.split()
        files = sorted({repo / p for p in out})
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = []
    if not files:
        files = sorted(p for p in repo.rglob("*.md") if not SKIP_DIRS & set(p.parts))
    return [p for p in files if p.exists() and not SKIP_DIRS & set(p.relative_to(repo).parts)]


def slug(heading: str) -> str:
    s = heading.strip().lower()
    s = re.sub(r"[`*_]", "", s) if not re.search(r"\w_\w", s) else re.sub(r"[`*]", "", s)
    s = re.sub(r"[^\w\- ]", "", s)
    return s.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    text = CODE.sub("", path.read_text(encoding="utf-8"))
    out, seen = set(), {}
    for m in re.finditer(r"^#{1,6}\s+(.*?)\s*#*\s*$", text, re.M):
        base = slug(m.group(1))
        n = seen.get(base, 0)
        out.add(base if n == 0 else f"{base}-{n}")
        seen[base] = n + 1
    out.update(re.findall(r"<a\s+(?:name|id)=\"([^\"]+)\"", text))
    return out


def check(repo: Path = REPO) -> dict:
    files = markdown_files(repo)
    broken, n_links = [], 0
    for md in files:
        text = CODE.sub("", md.read_text(encoding="utf-8"))
        text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
        for m in LINK.finditer(text):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            n_links += 1
            path_part, _, anchor = target.partition("#")
            dest = md if not path_part else (md.parent / path_part).resolve()
            rel = md.relative_to(repo)
            if not dest.exists():
                broken.append(f"{rel}: {target} (missing file)")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                broken.append(f"{rel}: {target} (missing anchor)")
    return {"files": len(files), "links": n_links, "broken": broken}


def main() -> int:
    res = check()
    for b in res["broken"]:
        print(f"BROKEN {b}")
    ok = not res["broken"]
    print(f"{'PASS' if ok else 'FAIL'} links: {res['links']} relative links in {res['files']} "
          f"Markdown files, {len(res['broken'])} broken")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
