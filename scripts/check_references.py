# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""Check that author-year citations resolve to references.bib and that every bib entry is cited (M6).

The documents cite in author-year form ("Su, Bayoumi and Joachims 2021", "Ashlagi et al. (2017)").
A citation resolves when its surname is an author of a bib entry with the same year. Every bib
entry must be cited at least once in the manuscript. Capitalised words followed by a year that are
not citations (for example a dated label) are listed in NOT_CITATIONS.

Usage: python scripts/check_references.py   (exit 0 and a PASS line when everything resolves)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BIB = REPO / "research" / "paper" / "references.bib"
MANUSCRIPT = "research/paper/manuscript.md"
DOCUMENTS = [
    MANUSCRIPT,
    "research/paper/supplementary.md",
    "research/experiments/EXP-001/report.md",
    "research/experiments/EXP-002/report.md",
    "research/experiments/EXP-003/report.md",
    "README.md",
    "articles/medium.md",
    "articles/linkedin.md",
]
NOT_CITATIONS = {"EXPLORATORY", "Start", "RecSys"}
CITATION = re.compile(
    r"\b([A-Z][a-zA-Z-]+)(?:,? [A-Z]\. ?[A-Z]?\.?)?(?: et al\.?|(?:, [A-Z][a-zA-Z-]+)*,? and "
    r"[A-Z][a-zA-Z-]+)?,? \(?((?:19|20)\d{2})\b")


def _ascii(name: str) -> str:
    return re.sub(r"\{\\[^{}]*\{(\w)\}\}|\\.\{?(\w)\}?", lambda m: m.group(1) or m.group(2), name)


def parse_bib(text: str) -> dict[str, dict]:
    entries = {}
    for m in re.finditer(r"@\w+\{([^,]+),(.*?)\n\}", text, re.S):
        key, body = m.group(1).strip(), m.group(2)
        fields = dict(re.findall(r"(\w+)\s*=\s*\{(.*)\},?\s*$", body, re.M))
        authors = [_ascii(a.split(",")[0].strip()) for a in fields.get("author", "").split(" and ")]
        entries[key] = {"surnames": set(authors), "year": fields.get("year", "")}
    return entries


def check(repo: Path = REPO) -> dict:
    bib = parse_bib((repo / BIB.relative_to(REPO)).read_text(encoding="utf-8"))
    unresolved, cited_in_manuscript, n_citations = [], set(), 0
    for doc in DOCUMENTS:
        path = repo / doc
        if not path.exists():
            continue
        for m in CITATION.finditer(path.read_text(encoding="utf-8")):
            surname, year = m.group(1), m.group(2)
            if surname in NOT_CITATIONS:
                continue
            keys = [k for k, e in bib.items() if surname in e["surnames"] and e["year"] == year]
            n_citations += 1
            if not keys:
                unresolved.append(f"{doc}: {m.group(0)!r}")
            elif doc == MANUSCRIPT:
                cited_in_manuscript.update(keys)
    uncited = sorted(set(bib) - cited_in_manuscript)
    return {"bib_entries": len(bib), "citations": n_citations, "unresolved": unresolved,
            "uncited": uncited}


def main() -> int:
    res = check()
    for u in res["unresolved"]:
        print(f"UNRESOLVED {u}")
    for k in res["uncited"]:
        print(f"UNCITED {k}")
    ok = not res["unresolved"] and not res["uncited"]
    print(f"{'PASS' if ok else 'FAIL'} references: {res['citations']} author-year citations, "
          f"{res['bib_entries']} bib entries, {len(res['unresolved'])} unresolved, "
          f"{len(res['uncited'])} uncited")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
