#!/usr/bin/env python3
"""Standard report generator for a *-research corpus.

Writes:
  - docs/research/literature_review.md   (synthesis + top papers per category)
  - docs/research/trends.md              (12-month trend / burst report)

Self-contained taxonomy discovery; reads momentum/gaps/bursts from the
standard statistics.json if present.

Standard pipeline mimic shared across all research repos.

Usage:
    python3 scripts/analysis/generate_reports.py
    python3 scripts/analysis/generate_reports.py --check   # CI: fail if stale
"""

import argparse
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent  # repo root (3 up from scripts/analysis)
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO / "scripts"))

from trend_scanner import scan as scan_trends  # noqa: E402
import research_config  # noqa: E402
import standard_stats  # noqa: E402  (deterministic stats fallback for --check)

_CFG = research_config.require_valid_config()

# ``**Generated:** YYYY-MM-DD`` line — doubles as the time anchor that --check
# reuses so the freshness gate is timestamp-agnostic (a pure wall-clock day
# rollover never counts as "stale"; only corpus/config drift does).
_GENERATED_RE = re.compile(r"\*\*Generated:\*\*\s*(\d{4}-\d{2}-\d{2})")


def _parse_generated_anchor(text):
    """Return the datetime of the committed report's ``**Generated:**`` line,
    or None when unparseable."""
    m = _GENERATED_RE.search(text or "")
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y-%m-%d")
    except ValueError:
        return None


def _display(kebab):
    # Prefer config display names, fall back to title-casing the id.
    # Shared helper lives in research_config so all generators agree.
    return research_config.display_name(_CFG, kebab)


def load_papers():
    data = yaml.safe_load((REPO / "papers.yaml").read_text(encoding="utf-8"))
    return data.get("papers", [])


def render_literature(papers, now, stats):
    now = now or datetime.now()
    total = len(papers)
    cat_counter = Counter(p.get("category", "unknown") for p in papers)
    sub_counter = Counter(p.get("subcategory", "unknown") for p in papers)
    year_counter = Counter(p.get("date", "")[:4] for p in papers if p.get("date"))
    years = sorted(y for y in year_counter if y)
    span = f"{years[0]}–{years[-1]}" if years else "—"
    median = years[len(years) // 2] if years else "—"

    L = ["# Literature Review", "",
         f"**Generated:** {now:%Y-%m-%d}  ",
         f"**Corpus:** {total:,} papers across {len(cat_counter)} categories", "",
         "> Synthesis of the corpus. Category insights are grounded in "
         "title/abstract analysis of the papers themselves.", "", "---", "",
         "## Corpus Overview", "", "| Rank | Category | Papers |",
         "|------|----------|--------|"]
    for i, (c, n) in enumerate(sorted(cat_counter.items(), key=lambda kv: -kv[1])[:8], 1):
        L.append(f"| {i} | {_display(c)} | {n} |")
    dom = ", ".join(f"{_display(s)} ({n})" for s, n in sub_counter.most_common(3)) or "—"
    L += ["", f"**Time span:** {span} (median year {median})",
          f"**Dominant aspects:** {dom}", "", "---", ""]

    if isinstance(stats, dict):
        mom = stats.get("momentum", [])
        if mom:
            L += ["## 📈 Research Momentum (Last 12 Months)", "",
                  "| Category | Total | Last 12m | Prior 12m | Growth | 12-m share | Papers/mo |",
                  "|----------|------:|---------:|----------:|-------:|----------:|----------:|"]
            for m in mom[:12]:
                g = f"{m['growth_pct']:+.0f}%" if m.get('growth_pct') is not None else "—"
                L.append(f"| {m['name']} | {m['total']} | {m['recent']} | {m['prior']} | {g} | "
                         f"{m['recent_share']*100:.0f}% | {m['papers_per_month']} |")
            L += ["", "---", ""]
        gaps = stats.get("gaps", {})
        thinnest = gaps.get("thinnest_cells", [])[:8]
        if thinnest:
            L += ["## 🕳️ Research Gaps (Thinnest Cells)", "", "| Cell | Papers |", "|------|--------:|"]
            for g in thinnest:
                L.append(f"| `{g['cell']}` | {g['papers']} |")
            L += ["", "---", ""]

    L += ["", "## Category Insights", ""]
    for c, n in sorted(cat_counter.items(), key=lambda kv: -kv[1]):
        if n == 0:
            continue
        L += [f"### {_display(c)} (`{c}`)", "", f"**Corpus size:** {n} papers"]
        top3 = sorted((p for p in papers if p.get("category") == c),
                      key=lambda p: p.get("date", ""), reverse=True)[:3]
        if top3:
            L += ["", "**Recent papers:**", ""]
            for p in top3:
                L.append(f"- [{p.get('date', '')}] {p.get('title', '')[:95]} — {p.get('url', '')}")
        L += ["", "---", ""]

    L += ["", "## Methodology",
          "", "1. Papers are discovered via taxonomy-aware arXiv/OpenAlex queries and "
          "auto-classified into the corpus taxonomy.",
          "2. Insights are grounded in `statistics.json` (generated by `scripts/standard_stats.py`).",
          "3. Regenerate with `scripts/analysis/generate_reports.py`.", ""]
    return "\n".join(L)


def render_trends(papers, now):
    now = now or datetime.now()
    res = scan_trends(papers, months=12, top=15, now=now)
    L = ["# Trends (12-Month View)", "",
         f"**Generated:** {now:%Y-%m-%d}  ",
         f"**Window:** since {res['cutoff']} — {res['recent_papers']} of {len(papers)} papers", "",
         "## 🔥 Keyword Bursts", "", "| Keyword | Recent | Total | Burst |",
         "|---------|--------|-------|-------|"]
    for t in res["trends"]:
        L.append(f"| {t['keyword']} | {t['recent_papers']} | {t['total_papers']} | {t['burst_score']}× |")
    L += ["", "## 📈 Fastest-Growing Cells", "",
          "| Cell | Recent | Total | Recent Share |", "|------|--------|-------|--------------|"]
    for g in res["growing_cells"]:
        L.append(f"| `{g['cell']}` | {g['recent']} | {g['total']} | {g['recent_share']*100:.0f}% |")
    L += ["", "Regenerate with `python3 tools/trend_scanner.py --months 12`.", ""]
    return "\n".join(L)


REPORT_FILES = ("literature_review.md", "trends.md")


def reports_for(papers, now=None, stats=None):
    """Render both reports, returning {filename: content}.

    ``now`` (default: real clock) anchors the rolling 12-month window.
    ``--check`` passes the anchor parsed from each committed report so the
    gate is timestamp-agnostic.  ``stats`` defaults to a deterministic
    recomputation from ``papers`` (statistics.json is gitignored and absent in
    a fresh CI checkout, so it must not be a dependency of the gate).
    """
    now = now or datetime.now()
    if stats is None:
        stats, _export, _viz = standard_stats.compute_all(papers, now=now)
    return {
        "literature_review.md": render_literature(papers, now, stats),
        "trends.md": render_trends(papers, now),
    }


def check_reports(papers, out_dir, now=None):
    """Return the list of stale report filenames ([] when fresh).

    Each committed report is regenerated as of its own ``**Generated:**``
    anchor, so wall-clock drift alone never trips the gate.
    """
    now = now or datetime.now()
    stale = []
    for fname in REPORT_FILES:
        path = out_dir / fname
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current is None:
            stale.append(fname)
            continue
        anchor = _parse_generated_anchor(current) or now
        expected = reports_for(papers, now=anchor)[fname]
        if current != expected:
            stale.append(fname)
    return stale


def write_reports(papers, out_dir, now=None):
    """Render and write both reports (docs/research/*)."""
    out_dir = Path(out_dir)
    reports = reports_for(papers, now=now)
    out_dir.mkdir(parents=True, exist_ok=True)
    for fname, content in reports.items():
        (out_dir / fname).write_text(content, encoding="utf-8")
    print("wrote docs/research/literature_review.md & docs/research/trends.md")


def main():
    parser = argparse.ArgumentParser(description="Generate literature/trends reports")
    parser.add_argument(
        "--check", action="store_true",
        help="Verify reports are up-to-date without writing (exit 1 if stale)",
    )
    args = parser.parse_args()

    papers = load_papers()
    out = REPO / "docs" / "research"

    if args.check:
        stale = check_reports(papers, out)
        if not stale:
            print("All reports are up-to-date.")
            sys.exit(0)
        print(
            "Stale reports: " + ", ".join(stale) +
            ". Run scripts/analysis/generate_reports.py to regenerate.",
            file=sys.stderr,
        )
        sys.exit(1)

    write_reports(papers, out)


if __name__ == "__main__":
    main()