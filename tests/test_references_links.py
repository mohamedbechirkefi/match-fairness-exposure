# SPDX-License-Identifier: LicenseRef-MATCH-NC-Research-1.0
"""M6 checks: citations resolve to references.bib, every bib entry is cited, relative links resolve."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


refs = _load("check_references")
links = _load("check_links")


def test_every_citation_resolves_and_every_bib_entry_is_cited() -> None:
    res = refs.check()
    assert res["bib_entries"] == 8
    assert res["citations"] > 0
    assert res["unresolved"] == []
    assert res["uncited"] == []


def test_reference_check_flags_unknown_and_uncited(tmp_path: Path) -> None:
    (tmp_path / "research" / "paper").mkdir(parents=True)
    (tmp_path / "research" / "paper" / "references.bib").write_text(
        "@article{a2000,\n  author = {Alpha, A. and Beta, B.},\n  year = {2000}\n}\n"
        "@article{c2001,\n  author = {Gamma, C.},\n  year = {2001}\n}\n", encoding="utf-8")
    (tmp_path / "research" / "paper" / "manuscript.md").write_text(
        "As shown (Alpha and Beta 2000) and by Delta et al. (1999).\n", encoding="utf-8")
    res = refs.check(tmp_path)
    assert len(res["unresolved"]) == 1 and "Delta" in res["unresolved"][0]
    assert res["uncited"] == ["c2001"]


def test_every_relative_markdown_link_resolves() -> None:
    res = links.check()
    assert res["links"] > 0
    assert res["broken"] == []


def test_link_check_flags_missing_files_and_anchors(tmp_path: Path) -> None:
    (tmp_path / "a.md").write_text("# Title\n\n## Part two\n\n[ok](#part-two) [x](b.md) [y](#nope)\n"
                                   "`[not a link](c.md)` [web](https://example.org)\n", encoding="utf-8")
    res = links.check(tmp_path)
    assert res["links"] == 3
    assert sorted(res["broken"]) == ["a.md: #nope (missing anchor)", "a.md: b.md (missing file)"]
