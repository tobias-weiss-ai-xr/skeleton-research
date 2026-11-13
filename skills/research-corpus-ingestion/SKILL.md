---
name: research-corpus-ingestion
description: Ingest new papers into the research corpus via arXiv, OpenAlex, and other sources, then validate and regenerate. Use when the user wants to add papers, expand coverage, run "find new papers", or after editing config/taxonomy.yaml discovery queries.
license: MIT
metadata:
  author: skeleton-research
  version: "1.0"
---

# Research Corpus Ingestion

## When to use
- User asks to find/ingest new papers for the corpus
- After editing discovery queries in `config/taxonomy.yaml`
- Expanding an under-covered taxonomy category

## Discovery queries first
Before fetching, make sure queries exist in `config/taxonomy.yaml`:

1. **arXiv** under `arxiv_queries:` — each entry needs a `category` (validate fails otherwise)
2. **OpenAlex** under `openalex_queries:` — per-category search phrases
3. **Other sources** under `other_sources_queries:` — dblp/crossref/europepmc/etc.

```yaml
# Example arXiv entry
- query: 'cat:cs.CF AND (abs:"Kubernetes" AND abs:"security")'
  category: security
```

## Fetch workflow (preview → ingest → validate → regenerate)

```bash
# 1. Preview what each source will find (no writes)
python3 scripts/fetch/fetch_new_papers.py --months 12 --dry-run
python3 scripts/fetch/fetch_openalex_bulk.py --months 12 --dry-run --per-category 20
python3 scripts/fetch/fetch_other_sources.py --dry-run

# 2. Ingest (appends to papers.yaml)
python3 scripts/fetch/fetch_new_papers.py --months 12 --local
python3 scripts/fetch/fetch_openalex_bulk.py --months 12 --local --per-category 200
python3 scripts/fetch/fetch_other_sources.py --local

# 3. Validate — must pass before anything else
python3 scripts/validate_papers.py

# 4. Regenerate all derived outputs
make all
# or:
python3 scripts/generate_readme.py
python3 scripts/standard_stats.py
python3 scripts/analysis/generate_reports.py
```

## Gotchas from production usage

- **Use `python3.12`** — the default `python3` on some hosts is broken (xcode-select issue).
- **Never run `--dry-run` on OpenAlex twice** — it consumes the same polite-pool budget as a real run.
- **TODO/dummy queries** in `other_sources_queries.yaml` (e.g. `your topic a`) pollute the corpus — the script does not filter them.
- **Medical/life-science junk** appears because "container"/"security" collide with unrelated fields. Always junk-scan new intake manually (see *junk-scan* skill).
- **arXiv caps at 100 results per query** with no pagination. To deepen coverage add many specific queries, don't widen one query.
- **DBLP frequently returns 0 results** (API availability) — don't retry in a loop; Crossref carries the round.
- **Wide keyword fetches pull "review"-subcategory junk** — validate_papers will warn; clean manually.
- Always **back up `papers.yaml` before a big fetch** (`cp papers.yaml papers.yaml.bak`) so a failed auto-scan is easy to roll back.

## Verification
- `python3 scripts/validate_papers.py` exits 0 with no new errors
- `make check` passes (generated files fresh)
- `python3 -m pytest` passes

## Commit message convention
```
feat: ingest N papers into <short-topic> corpus

Sources: arXiv +N, OpenAlex +N, other +N
Net new: +N (corpus: N -> N)
```
