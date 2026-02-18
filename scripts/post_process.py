#!/usr/bin/env python3
"""ExecSignals — Post-Processing Script.

Runs after page generation to add cross-cutting concerns:
- Contextual internal links between pages
- AEO/GEO answer blocks for AI search engines
- Page validation (missing meta, schema, etc.)

Pattern: CRO Report's post-processing pipeline
(add_contextual_links.py, add_aeo_geo_patterns.py, fix_missing_meta_tags.py)

Usage: python scripts/post_process.py
"""

import os
import re
import sys
import json
from glob import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nav_config import DOMAIN


def find_html_files(root="."):
    """Find all generated HTML files."""
    patterns = [
        "roles/*/index.html",
        "cities/*/index.html",
        "industries/*/index.html",
        "vs/*/index.html",
        "roles/index.html",
        "cities/index.html",
        "industries/index.html",
    ]
    files = []
    for pattern in patterns:
        files.extend(glob(os.path.join(root, pattern)))
    return sorted(files)


# ─── Contextual Internal Links ───


def build_link_map(root="."):
    """Build a map of keywords → internal links."""
    dim_path = os.path.join(root, "data", "seo_dimensions.json")
    if not os.path.exists(dim_path):
        return {}

    with open(dim_path) as f:
        dims = json.load(f)

    link_map = {}
    for role in dims.get("roles", []):
        link_map[role["name"]] = f"/roles/{role['slug']}/"

    for city in dims.get("cities", []):
        link_map[city["name"]] = f"/cities/{city['slug']}/"

    for ind in dims.get("industries", []):
        link_map[ind["name"]] = f"/industries/{ind['slug']}/"

    return link_map


def add_contextual_links(root="."):
    """Add internal links where dimension names appear in page text."""
    link_map = build_link_map(root)
    if not link_map:
        print("  No link map built, skipping contextual links")
        return

    files = find_html_files(root)
    total_links = 0

    for filepath in files:
        with open(filepath) as f:
            content = f.read()

        # Determine current page's own link to avoid self-linking
        rel_path = os.path.relpath(filepath, root)
        current_url = "/" + os.path.dirname(rel_path).replace("\\", "/") + "/"

        modified = False
        for term, url in link_map.items():
            if url == current_url:
                continue  # don't self-link

            # Only link in paragraph text, not headings or existing links
            # Match term that's not already inside an <a> tag
            pattern = rf'(?<=>)([^<]*?)(?<!</a>)\b({re.escape(term)})\b'

            def replace_first(match):
                prefix = match.group(1)
                word = match.group(2)
                return f'{prefix}<a href="{url}">{word}</a>'

            # Only replace first occurrence per page
            new_content, count = re.subn(pattern, replace_first, content, count=1)
            if count > 0:
                content = new_content
                modified = True
                total_links += count

        if modified:
            with open(filepath, "w") as f:
                f.write(content)

    print(f"  Added {total_links} contextual links across {len(files)} pages")


# ─── AEO/GEO Answer Blocks ───


def add_aeo_patterns(root="."):
    """Add structured answer blocks for AI search engines.

    Inserts a concise, schema-friendly answer block after the <h1> on each page.
    This helps Perplexity, ChatGPT, and Google SGE extract direct answers.
    """
    dim_path = os.path.join(root, "data", "seo_dimensions.json")
    if not os.path.exists(dim_path):
        print("  No dimensions data, skipping AEO patterns")
        return

    with open(dim_path) as f:
        dims = json.load(f)

    # Build quick lookup
    role_map = {r["slug"]: r for r in dims.get("roles", [])}
    city_map = {c["slug"]: c for c in dims.get("cities", [])}
    ind_map = {i["slug"]: i for i in dims.get("industries", [])}

    files = find_html_files(root)
    count = 0

    for filepath in files:
        with open(filepath) as f:
            content = f.read()

        if "aeo-answer" in content:
            continue  # already has AEO block

        rel_path = os.path.relpath(filepath, root).replace("\\", "/")
        parts = rel_path.split("/")

        answer = None
        if parts[0] == "roles" and len(parts) == 3:
            slug = parts[1]
            if slug in role_map:
                r = role_map[slug]
                answer = (
                    f"The median {r['name']} salary is {r['salary_median']} "
                    f"(P25: {r['salary_p25']}, P75: {r['salary_p75']}). "
                    f"There are {r['lead_count']} open {r['name']} roles this week. "
                    f"The top hiring signal is \"{r['top_signal']}\" and the top "
                    f"industry is {r['top_industry']}."
                )
        elif parts[0] == "cities" and len(parts) == 3:
            slug = parts[1]
            if slug in city_map:
                c = city_map[slug]
                answer = (
                    f"{c['name']} has {c['lead_count']} VP+ executive openings "
                    f"this week with an average salary of {c['avg_salary']}. "
                    f"{c['remote_pct']} of roles are remote-eligible."
                )
        elif parts[0] == "industries" and len(parts) == 3:
            slug = parts[1]
            if slug in ind_map:
                ind = ind_map[slug]
                answer = (
                    f"{ind['name']} has {ind['lead_count']} VP+ openings this week "
                    f"({ind['velocity_wow']} WoW). Average salary: {ind['avg_salary']}. "
                    f"Hiring trend: {ind['hiring_trend'].lower()}."
                )

        if answer:
            aeo_block = (
                f'\n        <div class="aeo-answer" role="doc-abstract">'
                f"<p>{answer}</p></div>"
            )
            # Insert after the subtitle paragraph
            content = content.replace(
                '</p>\n\n            <div class="dimension-stats">',
                f"</p>{aeo_block}\n\n"
                '            <div class="dimension-stats">',
            )
            with open(filepath, "w") as f:
                f.write(content)
            count += 1

    print(f"  Added AEO answer blocks to {count} pages")


# ─── Validation ───


def validate_pages(root="."):
    """Check all SEO pages for required elements."""
    files = find_html_files(root)
    issues = []

    for filepath in files:
        with open(filepath) as f:
            content = f.read()

        rel_path = os.path.relpath(filepath, root)
        page_issues = []

        if "<title>" not in content:
            page_issues.append("missing <title>")
        if 'rel="canonical"' not in content:
            page_issues.append("missing canonical")
        if 'property="og:title"' not in content:
            page_issues.append("missing OG title")
        if 'property="og:description"' not in content:
            page_issues.append("missing OG description")
        if "application/ld+json" not in content:
            page_issues.append("missing JSON-LD schema")
        if "<h1>" not in content and "<h1 " not in content:
            page_issues.append("missing h1")
        if 'class="breadcrumb"' not in content:
            page_issues.append("missing breadcrumb")

        if page_issues:
            issues.append(f"  {rel_path}: {', '.join(page_issues)}")

    if issues:
        print(f"  Validation issues found ({len(issues)} pages):")
        for issue in issues:
            print(issue)
    else:
        print(f"  All {len(files)} pages passed validation")


# ─── Main ───


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    print("Post-processing SEO pages...")
    add_contextual_links()
    add_aeo_patterns()
    validate_pages()
    print("Post-processing complete.")


if __name__ == "__main__":
    main()
