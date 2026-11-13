---
name: research-corpus-classify
description: Assign valid category and subcategory to papers in papers.yaml using the corpus taxonomy. Use when categorizing new papers, fixing misclassified papers, or asked "what category does this paper belong to".
license: MIT
metadata:
  author: skeleton-research
  version: "1.0"
---

# Research Corpus Paper Classification

## When to use
- Ingesting manually-curated papers (add to `papers.yaml` directly)
- Fixing misclassified entries after a fetch round
- Explaining the taxonomy to someone adding papers

## Ground truth: config/taxonomy.yaml
The ONLY valid values come from:
- `taxonomy.categories` → `id` values (category field)
- `taxonomy.subcategories` → `id` values (subcategory field)

Never invent a new category/subcategory ID. If no cell fits, note it and ask
the maintainer — do not silently add a new axis.

## Fetching scripts auto-classify
- `fetch_new_papers.py` / `fetch_other_sources.py` use `classify_subcategory(title, abstract)`
- `fetch_openalex_bulk.py` uses the `category` key from `openalex_queries`
- If a query is missing a `category`, discovered papers get `category: ""` and
  validate fails until you fill it in

## Manual classification heuristics

Read title + abstract, then pick:

| Evidence in title/abstract | Category |
|----------------------------|----------|
| "survey", "review", "state of the art", "taxonomy" | survey |
| "application", "case study", "deployed at X", "in practice" | application |
| "method", "novel approach", "algorithm", "framework" | method |
| "benchmark", "evaluation", "comparison", "SOTA vs" | evaluation |
| "architecture", "design", "system", "platform" | architecture/system |
| theory, formal proof, bounds | theory |

Subcategories are typically orthogonal (e.g. agentic / non-agentic / hybrid) —
match by mechanism, not by topic.

## Heuristics for common traps

- **Problem definition papers** ("We identify 12 misconfigurations") → `survey` or `method`, not the topic.
- **Dual-topic papers** → pick the category of the *solved problem*'s domain, keep it consistent with siblings.
- **Evaluation-only papers sharing a benchmark** → `evaluation`.
- **Foundational/system papers** (gVisor, Kata) → `systems` if in subcategory axis, else `architecture`.

## Verification
```bash
python3 scripts/validate_papers.py   # must exit 0
# quick category census
grep -E "^  category:" papers.yaml | sort | uniq -c | sort -rn
```

## Record-keeping
After a batch of classification fixes, run the pipeline and commit:
```
chore: reclassify N papers in <short-topic> corpus
```
