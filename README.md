# Skeleton Research Repository

Template/structure for research projects with paper ingestion, knowledge base, and analysis workflows.

## Structure

```
.
├── papers.yaml           # Main paper collection
├── config/
│   ├── taxonomy.yaml     # Categories and discovery queries
│   └── other_sources_queries.yaml  # Multi-source queries
├── knowledgebase/
│   ├── papers/           # Organized YAML collections
│   ├── full_texts/       # PDF/MD full texts
│   ├── by_topic/         # Symlinks by category
│   └── by_date/          # Symlinks by date
└── scripts/
    ├── fetch/            # Paper fetching scripts
    └── analysis/         # Analysis notebooks
```
