---
name: research-corpus-junk-scan
description: Review papers.yaml after a fetch round and remove off-topic, non-research, or spurious entries. Use when corpus was recently grown (arXiv/OpenAlex/other fetch) or the user complains about junk papers.
license: MIT
metadata:
  author: skeleton-research
  version: "1.0"
---

# Research Corpus Junk Scan

## When to use
- After any ingestion round (`fetch_new_papers.py`, `fetch_openalex_bulk.py`, `fetch_other_sources.py`)
- When validation or manual review reveals off-topic entries
- Keyword-based discovery always pulls junk — this is expected, not a bug

## Why junk appears
Discovery queries match **any** paper whose title/abstract contains the query
keywords. Collision classes seen in the wild:

| Query term | Collides with |
|------------|---------------|
| "container" | medical (cell/glass containers), shipping, packaging |
| "security" | any field with a security department (public health, banking) |
| "Kubernetes"/"k8s" | unrelated systems that merely mention it in an abstract |
| "exploit" | economic exploitation, vulnerability studies in other fields |
| "evidence" | medical evidence-based practice |
| "runtime" | any runtime (sports, TV, JVM-only papers) |
| "agentic" | non-AI agent theory |

## Junk categories to look for (typical drop list)

1. **Medical / life sciences** (lung cancer, pregnancy, heart implants, fentanyl epidemiology)
2. **Non-research artifacts** — GitHub release notes, conference announcements, product promos, "interviews", editorials
3. **Off-topic tech** — smartphones, Raspberry Pi I/O, ATMs, health APIs, industrial sensors
4. **Spurious matches** — a "Kubernetes" keyword in the abstract of an unrelated college DB system
5. **Art / literature / culture** — metaphor matches like "Particulates", "Ivory", "Re-thinking ivory"
6. **Duplicate coverage** — same paper ingested from 2 sources

## Junk-scan procedure

```bash
# 1. Identify what was just added (compare with pre-fetch backup)
diff <(python3 -c "import yaml,sys; d=yaml.safe_load(open('papers.bak.yaml')); [print(p['title']) for p in d['papers']]") \
     <(python3 -c "import yaml,sys; d=yaml.safe_load(open('papers.yaml')); [print(p['title']) for p in d['papers']]") | grep '^>' | sed 's/^> //' > /tmp/new_titles.txt

# 2. Grep the new set for suspicious markers
grep -iE "particular|ivory|cuba|particulate|monkeypox|pregnan|lung cancer|heartmate|fentanyl|hippocampus" /tmp/new_titles.txt
```

Review each candidate by reading its title **and** abstract (the abstract usually
settles it). When unsure whether to drop: **check the category**. If a medical
paper somehow landed in `kubernetes-security`, drop it — category mismatch is a
drop signal, not a re-classify signal, unless the paper is genuinely on-topic.

## Apply the drops (safely)

```python
# Remove junk titles from papers.yaml atomically
import yaml, os
from collections import Counter
p = 'papers.yaml'
data = yaml.safe_load(open(p))
drop = set(...)  # confirmed junk titles
kept = [x for x in data['papers'] if x['title'] not in drop]
removed = len(data['papers']) - len(kept)
assert len(data['papers']) == len(kept) + removed
data['papers'] = kept
tmp = p + '.tmp'
with open(tmp, 'w') as f:
    yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
os.replace(tmp, p)
print(f'removed {removed}')  # sanity check before regenerating
```

**Always** print the count and eyeball a few - `assert` before write so a typo
can't wipe the corpus. Then:

```bash
python3 scripts/validate_papers.py && make all
```

## Reject/keep borderline decisions (from production runs)

**Drop** (off-topic despite keyword match):
- Medical papers under `container-security` (e.g. "HeartMate MRI", "Lung cancer review")
- Raspberry Pi embedded I/O isolation (embedded TEE, not containers)
- OT vulnerability-scan datasets (out of corpus scope)
- GitHub release notes / conference announcements / product promos

**Keep** (on-topic even if surprising):
- Tutorial-style **book chapters on the topic** (e.g. "Konfigurationszuordnungen und Secrets")
- Policy/spec papers relevant to the domain, even if they aren't "container" papers
- Foundational old isolation papers (cgroups/namespaces, 2013-2016) — historical value
- A paper mentioning the topic if its contribution is genuinely in-scope

## Verification
- `papers.yaml` still parses and the count matches expectations
- `validate_papers.py` passes
- The dropped papers don't reappear in the next fetch (check `other_sources_queries.yaml` — remove over-broad query terms)

## Commit convention
```
chore: junk-scan — remove N off-topic papers from <source> intake
```
