"""Hermetic tests for the timestamp-agnostic CI freshness gates.

The ``--check`` modes must NOT trip on wall-clock drift (month/day rollover,
rolling 12-month window shift) — only on real corpus/config drift.  These
tests simulate the gate by writing outputs as-of time T0 and re-checking at a
later wall-clock time T1.
"""

import datetime
import sys
from pathlib import Path

import pytest

# generate_reports lives in scripts/analysis/ (not on conftest's sys.path).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts" / "analysis"))

from standard_stats import check_outputs, write_outputs
from generate_reports import check_reports, write_reports
from readme_sections import parse_stats_anchor

T0 = datetime.datetime(2026, 9, 15)
# Later wall clock — different month, day, and 12-month analysis window.
T1 = datetime.datetime(2027, 3, 10)


def _papers(extra=()):
    base = [
        {"title": "Foundational Survey", "date": "2026-01",
         "url": "https://arxiv.org/abs/2601.00001", "category": "method",
         "subcategory": "agentic", "authors": ["Ada"], "abstract": "Survey of agents.",
         "venue": "arXiv"},
        {"title": "Application Study", "date": "2025-06",
         "url": "https://arxiv.org/abs/2506.00002", "category": "application",
         "subcategory": "hybrid", "authors": ["Grace"], "abstract": "Study of tools.",
         "venue": "arXiv"},
    ]
    return base + list(extra)


def _new_paper():
    # In-window paper: changes counts, bursts, and the timeline.
    return {"title": "Fresh Result", "date": "2026-06",
            "url": "https://arxiv.org/abs/2606.00003", "category": "evaluation",
            "subcategory": "non-agentic", "authors": ["Linus"], "abstract": "Benchmark.",
            "venue": "arXiv"}


def _readme(tmp_path):
    p = tmp_path / "README.md"
    p.write_text(
        "<!-- BEGIN CORPUS STATISTICS -->\nplaceholder\n<!-- END CORPUS STATISTICS -->\n",
        encoding="utf-8")
    return p


@pytest.fixture
def cfg():
    # render_stats_section only needs github_pages (optional) from cfg.
    return {"topic": {"github_pages": ""}}


def test_stats_gate_is_timestamp_agnostic(tmp_path, cfg):
    readme = _readme(tmp_path)
    papers = _papers()
    write_outputs(papers, cfg, readme, tmp_path, now=T0)
    # A later wall clock (new month + moved 12m window) must NOT be stale.
    assert check_outputs(papers, cfg, readme, tmp_path, now=T1) == []
    # The committed README documents its own month anchor.
    anchor = parse_stats_anchor(readme.read_text(encoding="utf-8"))
    assert anchor is not None and anchor.year == 2026 and anchor.month == 9


def test_stats_gate_detects_corpus_drift(tmp_path, cfg):
    readme = _readme(tmp_path)
    papers = _papers()
    write_outputs(papers, cfg, readme, tmp_path, now=T0)
    stale = check_outputs(_papers([_new_paper()]), cfg, readme, tmp_path, now=T1)
    assert stale, "a corpus change must be reported stale"
    assert "README.md (corpus statistics)" in stale


def test_reports_gate_is_timestamp_agnostic(tmp_path):
    out = tmp_path / "docs" / "research"
    papers = _papers()
    write_reports(papers, out, now=T0)
    assert check_reports(papers, out, now=T1) == []


def test_reports_gate_detects_corpus_drift(tmp_path):
    out = tmp_path / "docs" / "research"
    papers = _papers()
    write_reports(papers, out, now=T0)
    assert check_reports(_papers([_new_paper()]), out, now=T1) != []


def test_reports_gate_flags_missing_file(tmp_path):
    papers = _papers()
    # Missing report files are stale (drift cannot be ruled out).
    assert check_reports(papers, tmp_path / "nope", now=T1)
