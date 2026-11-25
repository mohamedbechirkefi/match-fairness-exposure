# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Build the publication PDFs (M6): manuscript, supplementary file and the three experiment reports.

Uses the repository's builder (``match_lab.report.build_pdf``: pandoc to Typst, compiled by the
``typst`` Python package of the shared tools interpreter). The Typst root is ``research/`` so that
the manuscript can embed the experiment figures it references with ``../experiments/...``.
The PDF title metadata is the document's first level-1 heading (prefixed with "MATCH" for the
supplementary file). With ``--typ-dir`` the intermediate ``.typ`` files are moved there for page
rendering; otherwise they are deleted.

Usage: python scripts/build_pdfs.py [--typ-dir DIR]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from match_lab.report import build_pdf  # noqa: E402

RESEARCH = REPO / "research"
DOCUMENTS = [
    RESEARCH / "paper" / "manuscript.md",
    RESEARCH / "paper" / "supplementary.md",
    RESEARCH / "experiments" / "EXP-001" / "report.md",
    RESEARCH / "experiments" / "EXP-002" / "report.md",
    RESEARCH / "experiments" / "EXP-003" / "report.md",
]
TITLE_PREFIX = {"supplementary.md": "MATCH: "}


def first_heading(md: Path) -> str:
    for line in md.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip().replace("*", "")
    raise ValueError(f"{md} has no level-1 heading")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--typ-dir", type=Path, default=None, help="keep the .typ files in this folder")
    args = ap.parse_args(argv)
    for md in DOCUMENTS:
        title = TITLE_PREFIX.get(md.name, "") + first_heading(md)
        pdf = build_pdf(md, root=RESEARCH, title=title, keep_typ=args.typ_dir is not None)
        if args.typ_dir is not None:
            args.typ_dir.mkdir(parents=True, exist_ok=True)
            name = md.parent.name + "-" + md.stem + ".typ"
            shutil.move(str(md.with_suffix(".typ")), str(args.typ_dir / name))
        print(f"{pdf.relative_to(REPO)} {pdf.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
