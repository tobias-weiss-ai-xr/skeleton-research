<h1 align="center">
  <strong>Lie Groups: Theory & Applications</strong>
</h1>
<h3 align="center">Data-driven literature review corpus — from classical structure theory and representation theory to equivariant/geometric machine learning and gauge-theoretic physics</h3>

### 🔗 Links

- **License**: https://github.com/tobias-weiss-ai-xr/skeleton-research/blob/main/LICENSE
- **CI**: https://github.com/<YOUR_ORG>/<YOUR_REPO>/actions/workflows/validate.yml
- **GitHub Pages**: https://<YOUR_ORG>.github.io/<YOUR_REPO>/


> 📚 **Corpus:** 37 curated, auto-validated papers on Lie groups — every entry
> carries a real, verifiable arXiv URL and is fetched from the arXiv API.
> `papers.yaml` is the source of truth; `make all` regenerates everything.

## What you get

| Capability | How |
|------------|-----|
| 📄 **Curated corpus** | `papers.yaml` is the source of truth — one structured entry per paper |
| ✅ **Auto-validation** | `scripts/validate_papers.py` checks schema, duplicates, URL normalization, LaTeX artifacts |
| 🧾 **Auto-generated README** | `scripts/generate_readme.py` renders the paper list grouped by your taxonomy |
| 📊 **Statistics & trends** | `scripts/standard_stats.py` → `statistics.json` (momentum, gaps, bursts, venues, authors) |
| 🔍 **Literature review report** | `scripts/analysis/generate_reports.py` → `docs/research/literature_review.md` + `trends.md` |
| 🧭 **Topic planning** | `tools/topic_planner.py`, `tools/trend_scanner.py`, `tools/landscape_analyzer.py`, `tools/brief_generator.py` |
| 🔎 **New paper discovery** | `scripts/fetch/fetch_new_papers.py` (arXiv), `fetch_other_sources.py` (dblp/crossref/europepmc), `fetch_openalex_bulk.py` |
| 🐙 **GitHub repos discovery** | `scripts/fetch/fetch_github_repos.py` (optional, config-driven via `github_queries` in taxonomy.yaml) |
| 🦊 **GitLab projects discovery** | `scripts/fetch/fetch_gitlab_repos.py` (optional, config-driven via `gitlab_queries` in taxonomy.yaml) |
| 🏠 **Codeberg repos discovery** | `scripts/fetch/fetch_codeberg_repos.py` (optional, config-driven via `codeberg_queries` in taxonomy.yaml) |
| 📰 **News / intelligence digest** | `run_pipeline.py` — RSS/Atom + arXiv + GitHub releases + catalogs (e.g. CISA KEV) → scored, de-duplicated daily digest (`data/latest.md`/`.html`/`.json`) |
| 🖥️ **GitHub Pages site** | `docs/index.html` — searchable, filterable paper browser |
| 🤖 **Agentic workflow** | `AGENTS.md` + `config/taxonomy.yaml` make this repo agent-friendly by design |

## 🚀 Jump-start (5 steps)

```bash
# 1. Clone and rename
git clone https://github.com/tobias-weiss-ai-xr/skeleton-research.git my-topic-research
cd my-topic-research
git remote set-url origin https://github.com/<YOUR_ORG>/my-topic-research.git  # repoint to your fork
cd my-topic-research

# 2. Define your topic & taxonomy
#    Edit config/taxonomy.yaml: topic name, categories, subcategories, queries
vim config/taxonomy.yaml
make bootstrap   # rewrite README/HTML/CITATION identity tokens from the topic

# 3. Seed your corpus (start small — 5-10 papers is fine)
#    Either hand-curate papers.yaml, or auto-discover:
python3 scripts/fetch/fetch_new_papers.py --months 12 --dry-run   # preview arXiv hits
python3 scripts/fetch/fetch_new_papers.py --local                 # append to papers.yaml

# 4. Validate + generate
python3 scripts/validate_papers.py
python3 scripts/generate_readme.py
python3 scripts/standard_stats.py
python3 scripts/analysis/generate_reports.py

# 5. Commit & let CI keep it healthy
git add -A && git commit -m "bootstrap corpus for <YOUR TOPIC>"
git push
```

## 📖 How it works

```
config/taxonomy.yaml ──► papers.yaml ──► validate_papers.py
                          │   ▲              │
                          ▼   └── fetch_* ───┘
                   generate_readme.py ──► README.md paper list (auto)
                          │
                          ▼
                  standard_stats.py ──► statistics.json, docs/papers.json,
                                        README.md corpus statistics (auto)
                          │
                          ▼
              analysis/generate_reports.py ──► docs/research/*.md
```

The generated README sections (paper list + corpus statistics) are
**marker-delimited** (`<!-- BEGIN … -->` … `<!-- END … -->`) and are owned by
the pipeline: `generate_readme.py` and `standard_stats.py` regenerate exactly
their section on every run. Everything else in the README is user-owned prose
and is left untouched. If a repo drops a section entirely (e.g. the paper list
lives on the GitHub Pages site), the owning script skips it gracefully instead
of erroring.

- **Never edit the generated README sections by hand** — run the pipeline.
- The **taxonomy lives in one place** (`config/taxonomy.yaml`); every script reads it via `scripts/research_config.py`, which now validates the config up front so mistakes fail loudly.
- **CI (validate.yml)** runs on every push/PR and weekly to discover new papers. The `validate` job re-checks that all generated outputs are fresh (README, statistics, reports), and a `test` job runs the pytest suite.

## 🧪 Local pipeline (all in one)

```bash
make all          # validate → check freshness → generate → test
# …or run the raw steps:
python3 scripts/validate_papers.py && \
python3 scripts/generate_readme.py && \
python3 scripts/standard_stats.py && \
python3 scripts/analysis/generate_reports.py

# Freshness checks (non-destructive; exit 1 if stale) — used by CI
python3 scripts/generate_readme.py --check
python3 scripts/standard_stats.py --check
python3 scripts/analysis/generate_reports.py --check

# Unit tests
python3 -m pytest
```

## 📰 News / Intelligence Digest (`run_pipeline.py`)

A complementary pipeline that ingests **RSS/Atom feeds**, **arXiv queries**,
**GitHub release feeds**, and **structured catalogs** (e.g. CISA KEV), then
classifies + scores each item, de-duplicates against a seen-history, and renders
a daily digest (`data/latest.md`, `data/latest.html`, `data/raw.json`).

```bash
python3 run_pipeline.py --dry-run   # ingest + score only (no writes)
python3 run_pipeline.py              # full run → writes digest + marks seen
python3 run_pipeline.py --top 30     # smaller digest
```

Sources, weights and keyword classification live in `config/sources.yml`.

### Anti-saturation controls

Without guards, static catalogs (CISA KEV's 1,600+ entry list) and full-archive
feeds (Snyk's 1,600+ post history) recycle old items every run, and one
high-volume feed (e.g. a project blog) can crowd out everything else. Three
config knobs in `config/sources.yml` prevent this:

| Knob | Effect |
|------|--------|
| `recent_days` (per source) / `default_recent_days` | Drop items published/added older than N days. Applied to RSS + catalog sources; **opt in only on archive/catalog feeds** — normal blogs already return recent items, so leave the default at `0` to avoid starving low-frequency, high-signal feeds. |
| `max_items` (per source) | Hard cap on raw items kept from one source (e.g. 15 for an archive feed). |
| `max_source_share` (global) | Hard ceiling on how many digest slots a single source may occupy (default `0.40` → no source takes >40% of the digest). |

> Why `default_recent_days: 0`? Only archive/catalog feeds recycle. A blanket
> window would silently drop infrequent but high-signal feeds (e.g. Project
> Zero, which posts monthly). Set `recent_days` explicitly on the feeds that
> need it.

## 🔎 Discovery & utility scripts

Beyond the core pipeline, several scripts remain available for manual / scheduled use:

| Script | What it does |
|---|---|
| `scripts/fetch/fetch_new_papers.py` | arXiv discovery; `--create-pr` opens a weekly PR (used by CI) |
| `scripts/fetch/fetch_openalex_bulk.py` | OpenAlex bulk discovery per category (`--months`, `--local`) |
| `scripts/fetch/fetch_other_sources.py` | dblp / crossref / Europe PMC / Semantic Scholar discovery |
| `scripts/fetch/fetch_metadata.py` | backfill authors/abstracts/venues for existing arXiv papers |
| `scripts/fetch/saturate_papers.py` | expand queries & loop arXiv until corpus saturates |
| `scripts/fetch/fetch_github_repos.py` / `fetch_gitlab_repos.py` / `fetch_codeberg_repos.py` | discover topic-relevant code repos → `repos.yaml` |
| `scripts/fetch/search_arxiv_html.py` / `search_arxiv_offline.py` | alternate/ad-hoc arXiv search helpers |
| `scripts/export_bibtex.py` | write `paper/references.bib` from `papers.yaml` |
| `scripts/visualize_statistics.py` | visualise `statistics.json` |

The repo-discovery fetchers share rate-limit/backoff + relevance logic in `scripts/fetch/repos_common.py`.

## 🤖 Agentic workflow (AGENTS.md)

This repo is designed to be driven by coding agents (OpenCode, Claude Code, …):

- **Spec-style guardrails** in `AGENTS.md` — agents know the pipeline, never edit README, always re-validate.
- **One config file** to change → one re-run to verify (low context cost for agents).
- **Auto-validation** gives agents an objective pass/fail signal.
- **Weekly discovery** keeps the corpus fresh without human babysitting.

<!-- BEGIN PAPER LIST -->

## 📚 Paper list

- [📚 Surveys & Frameworks](#surveys-&-frameworks)
  - [Classical Theory & Structure](#classical-theory-&-structure)
  - [Equivariant & Geometric ML](#equivariant-&-geometric-ml)
  - [Physics & Geometry](#physics-&-geometry)
- [📚 Theory & Representation](#theory-&-representation)
  - [Classical Theory & Structure](#classical-theory-&-structure)
  - [Representation Theory](#representation-theory)
  - [Equivariant & Geometric ML](#equivariant-&-geometric-ml)
- [📚 Applications](#applications)
  - [Equivariant & Geometric ML](#equivariant-&-geometric-ml)
  - [Physics & Geometry](#physics-&-geometry)
- [📚 Evaluation & Benchmarks](#evaluation-&-benchmarks)
  - [Equivariant & Geometric ML](#equivariant-&-geometric-ml)

### Surveys & Frameworks

#### Classical Theory & Structure

##### 2009

- [2009] **A survey on Weyl calculus for representations of nilpotent Lie groups** [[paper](https://arxiv.org/abs/0910.1994)]

[⬆ Back to top](#paper-list)

#### Equivariant & Geometric ML

##### 2021

- [2021] **Geometric Deep Learning and Equivariant Neural Networks** [[paper](https://arxiv.org/abs/2105.13926)]
- [2021] **Geometric Deep Learning: Grids, Groups, Graphs, Geodesics, and Gauges** *Nature* [[paper](https://arxiv.org/abs/2104.13478)]

[⬆ Back to top](#paper-list)

#### Physics & Geometry

##### 2015

- [2015] **The Higgs boson for mathematicians. Lecture notes on gauge theory and symmetry breaking** *AMS Graduate Studies in Mathematics* [[paper](https://arxiv.org/abs/1512.02632)]

[⬆ Back to top](#paper-list)

### Theory & Representation

#### Classical Theory & Structure

##### 2023

- [2023] **Dirac series for complex E_8** [[paper](https://arxiv.org/abs/2305.03254)]

##### 2015

- [2015] **Towards a Lie theory for locally convex groups** [[paper](https://arxiv.org/abs/1501.06269)]

##### 2002

- [2002] **Abelian ideals in a Borel subalgebra of a complex simple Lie algebra** [[paper](https://arxiv.org/abs/math/0210463)]

[⬆ Back to top](#paper-list)

#### Representation Theory

##### 2026

- [2026] **Characteristic Classes Of Representations Of Lie Groups** [[paper](https://arxiv.org/abs/2602.02145)]

##### 2018

- [2018] **Representations of Compact Lie Groups of Low Cohomogeneity** [[paper](https://arxiv.org/abs/1802.02837)]

##### 2015

- [2015] **Stepwise Square Integrable Representations: the Concept and Some Consequences** [[paper](https://arxiv.org/abs/1511.09064)]

##### 2009

- [2009] **The Orbit Method for Compact Connected Lie Groups** [[paper](https://arxiv.org/abs/0906.4915)]

[⬆ Back to top](#paper-list)

#### Equivariant & Geometric ML

##### 2024

- [2024] **E(n) Equivariant Topological Neural Networks** [[paper](https://arxiv.org/abs/2405.15429)]

##### 2021

- [2021] **Frame Averaging for Invariant and Equivariant Network Design** *NeurIPS 2021* [[paper](https://arxiv.org/abs/2110.03336)]
- [2021] **E(n) Equivariant Graph Neural Networks** *NeurIPS 2021* [[paper](https://arxiv.org/abs/2102.09844)]

##### 2020

- [2020] **LieTransformer: Equivariant self-attention for Lie Groups** *ICML 2021* [[paper](https://arxiv.org/abs/2012.10885)]

##### 2019

- [2019] **General E(2)-Equivariant Steerable CNNs** *NeurIPS 2019* [[paper](https://arxiv.org/abs/1911.08251)]

##### 2018

- [2018] **3D Steerable CNNs: Learning Rotationally Equivariant Features in Volumetric Data** *CVPR 2018* [[paper](https://arxiv.org/abs/1807.02547)]
- [2018] **Clebsch-Gordan Nets: a Fully Fourier Space Spherical Convolutional Neural Network** *ICLR 2018* [[paper](https://arxiv.org/abs/1806.09231)]
- [2018] **CubeNet: Equivariance to 3D Rotation and Translation** *NeurIPS 2018* [[paper](https://arxiv.org/abs/1804.04458)]
- [2018] **Tensor field networks: Rotation- and translation-equivariant neural networks for 3D point clouds** *ICML 2018* [[paper](https://arxiv.org/abs/1802.08219)]

##### 2017

- [2017] **Surface Networks** *CVPR 2018* [[paper](https://arxiv.org/abs/1705.10819)]

##### 2016

- [2016] **Steerable CNNs** *ICLR 2017* [[paper](https://arxiv.org/abs/1612.08498)]
- [2016] **Harmonic Networks: Deep Translation and Rotation Equivariance** *ICLR 2017* [[paper](https://arxiv.org/abs/1612.04642)]
- [2016] **Group Equivariant Convolutional Networks** *ICML 2016* [[paper](https://arxiv.org/abs/1602.07576)]

[⬆ Back to top](#paper-list)

### Applications

#### Equivariant & Geometric ML

##### 2023

- [2023] **Learning Lagrangian Fluid Mechanics with E(3)-Equivariant Graph Neural Networks** [[paper](https://arxiv.org/abs/2305.15603)]
- [2023] **E(3) Equivariant Graph Neural Networks for Particle-Based Fluid Mechanics** [[paper](https://arxiv.org/abs/2304.00150)]

##### 2022

- [2022] **MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields** *NeurIPS 2022* [[paper](https://arxiv.org/abs/2206.07697)]
- [2022] **Equiformer: Equivariant Graph Attention Transformer for 3D Atomistic Graphs** *ICLR 2023* [[paper](https://arxiv.org/abs/2206.11990)]

##### 2021

- [2021] **E(3)-Equivariant Graph Neural Networks for Data-Efficient and Accurate Interatomic Potentials** *Nature Communications 2022* [[paper](https://arxiv.org/abs/2101.03164)]

##### 2020

- [2020] **SE(3)-Transformers: 3D Roto-Translation Equivariant Attention Networks** *ICML 2021* [[paper](https://arxiv.org/abs/2006.10503)]
- [2020] **Roto-Translation Equivariant Convolutional Networks: Application to Histopathology Image Analysis** *CVPR 2020* [[paper](https://arxiv.org/abs/2002.08725)]

[⬆ Back to top](#paper-list)

#### Physics & Geometry

##### 2023

- [2023] **Internal symmetries in Kaluza-Klein models** [[paper](https://arxiv.org/abs/2306.01049)]
- [2023] **Geometrical aspects of lattice gauge equivariant convolutional neural networks** [[paper](https://arxiv.org/abs/2303.11448)]

##### 2022

- [2022] **Gauge Equivariant Neural Networks for 2+1D U(1) Gauge Theory Simulations in Hamiltonian Formulation** [[paper](https://arxiv.org/abs/2211.03198)]

##### 2020

- [2020] **Lattice gauge equivariant convolutional neural networks** *Physical Review Letters 2022* [[paper](https://arxiv.org/abs/2012.12901)]

[⬆ Back to top](#paper-list)

### Evaluation & Benchmarks

#### Equivariant & Geometric ML

##### 2025

- [2025] **Platonic Transformers: A Solid Choice For Equivariance** [[paper](https://arxiv.org/abs/2510.03511)]

##### 2023

- [2023] **Using Multiple Vector Channels Improves E(n)-Equivariant Graph Neural Networks** *ICML 2024* [[paper](https://arxiv.org/abs/2309.03139)]

[⬆ Back to top](#paper-list)

<!-- END PAPER LIST -->

<!-- BEGIN CORPUS STATISTICS -->

## 📊 Corpus Statistics

**37 papers** across **4 categories**.  
Sources: **arXiv** 37 (100%).  
Full paper list: [GitHub Pages site](https://tobias-weiss-ai-xr.github.io/lie-group-research).

### Top categories

| Category | Papers | Recent | |
|----------|--------|--------|-|
| method | **20** | 1 | ████████████ |
| application | **11** | 0 | ███████░░░░░ |
| survey | **4** | 0 | ██░░░░░░░░░░ |
| evaluation | **2** | 1 | █░░░░░░░░░░░ |

### By year

| Year | Papers | |
|------|--------|-|
| 2002 | 1 | ██░░░░░░░░░░ |
| 2009 | 2 | ████░░░░░░░░ |
| 2015 | 3 | ██████░░░░░░ |
| 2016 | 3 | ██████░░░░░░ |
| 2017 | 1 | ██░░░░░░░░░░ |
| 2018 | 5 | ██████████░░ |
| 2019 | 1 | ██░░░░░░░░░░ |
| 2020 | 4 | ████████░░░░ |
| 2021 | 5 | ██████████░░ |
| 2022 | 3 | ██████░░░░░░ |
| 2023 | 6 | ████████████ |
| 2024 | 1 | ██░░░░░░░░░░ |
| 2025 | 1 | ██░░░░░░░░░░ |
| 2026 | 1 | ██░░░░░░░░░░ |

### Momentum (hottest categories)

| Category | Total | Rate | Recent | Score |
|----------|-------|------|--------|-------|
| Evaluation | 2 | 0.1/mo | 50% | 50 |
| Method | 20 | 0.1/mo | 5% | 5 |
| Application | 11 | 0.0/mo | 0% | 0 |
| Survey | 4 | 0.0/mo | 0% | 0 |

### Trending keywords

| Keyword | Papers | Burst |
|---------|--------|-------|
| group convolution | 1 | 4.62 |

### Top venues

| Venue | Papers |
|-------|--------|
| NeurIPS 2021 | 2 |
| ICML 2021 | 2 |
| CVPR 2018 | 2 |
| ICLR 2017 | 2 |
| ICML 2024 | 1 |
| NeurIPS 2022 | 1 |
| ICLR 2023 | 1 |
| Nature | 1 |
| Nature Communications 2022 | 1 |
| Physical Review Letters 2022 | 1 |

### Research gaps (thinnest cells)

| Cell | Papers |
|------|--------|
| `survey/physics` | 1 |
| `survey/classical` | 1 |
| `evaluation/equivariant` | 2 |
| `survey/equivariant` | 2 |
| `method/classical` | 3 |

*Generated 2026-10 by `scripts/standard_stats.py`.*

<!-- END CORPUS STATISTICS -->

## 📖 Citation

If you use this skeleton for a project, please cite:

```bibtex
@misc{skeleton-research,
  author = {Weiß, Tobias},
  title = {Research Corpus Skeleton: Data-Driven Agentic Literature Review},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/tobias-weiss-ai-xr/skeleton-research}
}
```

## 📄 License

MIT — see [LICENSE](LICENSE).
