#!/usr/bin/env python3
"""Quick-start script: bootstrap a new research corpus topic.

Usage:
    python3 scripts/setup_new_topic.py --name "My Research Topic"
    python3 scripts/setup_new_topic.py --name "Kubernetes Security" --short k8s-sec \
        --desc "Container orchestration security research" \
        --email research@example.com

What this script does:
  1. Updates config/taxonomy.yaml with your topic name, short name, description, email
  2. Runs 'make bootstrap' to regenerate identity-dependent files (README, HTML, CITATION)
  3. Prints next steps

Note: 'make bootstrap' must succeed (it reads the taxonomy you just set).
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = REPO_ROOT / "config" / "taxonomy.yaml"


def update_taxonomy(topic_name, short_name, description, email):
    """Update config/taxonomy.yaml with new topic identity."""
    content = CONFIG_FILE.read_text()
    
    old_topic = (
        'topic:\n'
        '  name: "Your Research Topic"          # shown in README header\n'
        '  short: "your-topic"                  # used in URLs, badges, docs paths\n'
        '  description: "Short description of the research field covered by this corpus."\n'
        '  openalex_mailto: "research@your-org.example"'
    )

    new_topic = (
        f'topic:\n'
        f'  name: "{topic_name}"          # shown in README header\n'
        f'  short: "{short_name}"                  # used in URLs, badges, docs paths\n'
        f'  description: "{description}"\n'
        f'  openalex_mailto: "{email}"'
    )
    
    if old_topic in content:
        content = content.replace(old_topic, new_topic)
        CONFIG_FILE.write_text(content)
        print(f"  OK: Updated config/taxonomy.yaml")
        return True
    else:
        print(f"  WARN: Could not find topic block in config/taxonomy.yaml to replace")
        print(f"  Manual setup: edit config/taxonomy.yaml, set:")
        print(f"    name: \"{topic_name}\"")
        print(f"    short: \"{short_name}\"")
        print(f"    description: \"{description}\"")
        print(f"    openalex_mailto: \"{email}\"")
        return True


def run_bootstrap():
    """Run make bootstrap to regenerate identity-dependent files."""
    try:
        result = subprocess.run(
            ["make", "bootstrap"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        lines = (result.stdout + result.stderr).strip().split('\n')
        for line in lines:
            if line.strip() and 'Error' not in line and 'refused' not in line:
                print(f"  {line}")
        if result.returncode != 0:
            if "Bootstrap refused" in result.stdout:
                print("\n  ERROR: Bootstrap refused — config/taxonomy.yaml still has placeholders!")
                print("  Edit config/taxonomy.yaml and set topic.name, topic.short, topic.description")
            return False
        return True
    except FileNotFoundError:
        print(f"  WARN: make not found — run 'python3 tools/bootstrap.py' manually")
        return True
    except subprocess.TimeoutExpired:
        print(f"  WARN: make bootstrap timed out")
        return True


def print_next_steps(topic_name, short_name):
    """Print what the user should do next."""
    dummy_suffix = "research"  # most repos use this; bootstrap.py derives its own from CITATION.cff
    repo_name = f"{short_name}-{dummy_suffix}"
    
    print("\n" + "=" * 70)
    print("SETUP COMPLETE")
    print("=" * 70)
    print(f"""
Your {topic_name} research corpus skeleton is configured!

NEXT STEPS:

 1. Repoint git to your repository:
    git remote set-url origin https://github.com/YOUR_ORG/{repo_name}.git
    git add config/taxonomy.yaml
    git commit -m "bootstrap {short_name} topic config"
    git push

 2. Define your taxonomy and discovery queries in config/taxonomy.yaml:
    - Edit categories and subcategories under taxonomy.categories & subcategories
    - Add arXiv queries under arxiv_queries: (with category: set)
    - Add OpenAlex queries under openalex_queries:
    - Add other source queries under other_sources_queries:

    Example arXiv query:
      - query: 'cat:cs.CF AND (abs:\"Kubernetes\" AND abs:\"security\")'
        category: security

    Example OpenAlex query:
      - category: security
        query: "Kubernetes AND RBAC AND security"

    Example other sources query:
      - source: dblp
        query: "Kubernetes security"
        category: security
        subcategory_hint: systems

 3. Seed your corpus with initial papers:

    Preview arXiv matches:
      python3 scripts/fetch/fetch_new_papers.py --months 24 --dry-run

    Ingest arXiv papers:
      python3 scripts/fetch/fetch_new_papers.py --months 24 --local

    Ingest OpenAlex papers:
      python3 scripts/fetch/fetch_openalex_bulk.py --months 24 --local

    Ingest from other sources:
      python3 scripts/fetch/fetch_other_sources.py --local

 4. Validate and generate all outputs:
    make all
    # or step-by-step:
    python3 scripts/validate_papers.py
    python3 scripts/generate_readme.py
    python3 scripts/standard_stats.py
    python3 scripts/analysis/generate_reports.py

 5. Set up CI:
    - Enable GitHub Actions in your repo Settings > Actions
    - The workflow in .github/workflows/validate.yml will auto-run

 6. Optional: Enable GitHub Pages for docs/ directory
     - Settings > Pages > Source: "/docs" branch: main

 Your config/taxonomy.yaml has been updated with your topic identity.
 Edit it to add proper taxonomy categories and discovery queries.

 DOCUMENTATION:
   Pipeline overview: README.md
   Agent workflow: AGENTS.md  
   Taxonomy reference: config/taxonomy.yaml comments
   Quick start: python3 scripts/setup_new_topic.py --help

 Tips:
   - Use python3.12 (default python3 sometimes broken)
   - Always run 'make validate' before committing
   - Use 'make check' to verify generated files are fresh
   - Use 'make discover' for automated arXiv PRs (set GITHUB_TOKEN)
""")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap a new research corpus topic"
    )
    parser.add_argument("--name", "-n", required=True,
                       help="Full topic name (e.g., 'Kubernetes Security')")
    parser.add_argument("--short", "-s", default=None,
                       help="Short name for URLs/repo (e.g., 'k8s-sec') — "
                            "defaults to lowercase dash-separated name")
    parser.add_argument("--desc", "-d", default="Research corpus for this topic",
                       help="Topic description")
    parser.add_argument("--email", "-e", default="research@your-org.example",
                       help="Email for OpenAlex polite pool (mailto)")
    
    args = parser.parse_args()
    
    if args.short is None:
        args.short = args.name.lower().replace(" ", "-").replace("_", "-")
    
    print(f"\nBootstrapping: {args.name}")
    print(f"  Short name: {args.short}")
    print(f"  Description: {args.desc}")
    print(f"  OpenAlex email: {args.email}")
    print()
    
    update_taxonomy(args.name, args.short, args.desc, args.email)
    success = run_bootstrap()
    
    if not success:
        sys.exit(1)
    
    print_next_steps(args.name, args.short)


if __name__ == "__main__":
    main()
