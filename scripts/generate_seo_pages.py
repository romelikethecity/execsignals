#!/usr/bin/env python3
"""ExecSignals — Programmatic SEO Page Generator.

Generates role, city, industry, comparison, and hub pages.
Pattern: Verum generate_pages.py + CRO Report generate_salary_pages.py
Framework: marketingskills programmatic-seo playbooks (Personas, Locations, Comparisons)

Usage: python scripts/generate_seo_pages.py [--data path/to/seo_dimensions.json]
"""

import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nav_config import DOMAIN, SITE_NAME
from templates import get_page_wrapper
from seo_core import (
    generate_breadcrumb_schema,
    generate_faq_schema,
    generate_dataset_schema,
    generate_role_faqs,
    generate_city_faqs,
    generate_industry_faqs,
    generate_comparison_faqs,
    get_related_pages,
)

YEAR = str(datetime.now().year)
MIN_LEADS_FOR_INDEX = 3  # noindex pages with fewer leads (thin page guard)


def load_dimensions(data_path):
    """Load SEO dimensions from JSON file."""
    with open(data_path) as f:
        return json.load(f)


# ─── Shared HTML Components ───


def breadcrumb_html(crumbs):
    """Generate breadcrumb navigation HTML."""
    parts = ['<nav class="breadcrumb" aria-label="Breadcrumb">']
    for i, crumb in enumerate(crumbs):
        if i > 0:
            parts.append('<span class="breadcrumb-sep">&rsaquo;</span>')
        if crumb.get("url"):
            parts.append(f'<a href="{crumb["url"]}">{crumb["name"]}</a>')
        else:
            parts.append(f'<span class="breadcrumb-current">{crumb["name"]}</span>')
    parts.append("</nav>")
    return "\n".join(parts)


def related_pages_html(pages, title="Related Pages"):
    """Generate related pages grid."""
    if not pages:
        return ""
    cards = ""
    for page in pages:
        cards += f"""
            <a href="{page['url']}" class="related-card">
                <span class="related-card-name">{page['name']}</span>
                <span class="related-card-arrow">&rarr;</span>
            </a>"""
    return f"""
    <section class="related-pages">
        <h3>{title}</h3>
        <div class="related-grid">{cards}
        </div>
    </section>"""


def cta_inline_html():
    """Inline CTA block for SEO pages."""
    return """
    <section class="seo-cta">
        <div class="seo-cta-box">
            <h3>Get scored VP+ leads every Monday</h3>
            <p>Your first week is free. No credit card, no call.</p>
            <a href="/#cta-section" class="cta-btn">Send Me the Brief</a>
        </div>
    </section>"""


def faq_section_html(faqs):
    """Generate FAQ section HTML from FAQ list."""
    if not faqs:
        return ""
    items = ""
    for faq in faqs:
        items += f"""
            <div class="faq-item">
                <div class="faq-question">{faq['question']}</div>
                <div class="faq-answer">{faq['answer']}</div>
            </div>"""
    return f"""
    <section class="faq-section seo-faq">
        <h2>Frequently Asked Questions</h2>
        <div class="faq-list">{items}
        </div>
    </section>"""


# ─── Role Pages (Personas playbook) ───


def build_role_page(role, dimensions):
    """Generate a role-specific page (e.g., /roles/vp-sales/)."""
    name = role["name"]
    slug = role["slug"]
    lead_count = role["lead_count"]
    noindex = lead_count < MIN_LEADS_FOR_INDEX

    crumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Roles", "url": "/roles/"},
        {"name": name, "url": None},
    ]

    faqs = generate_role_faqs(role)
    related = get_related_pages(slug, "roles", dimensions)

    # Cross-dimension links
    cross_industry = [
        {"name": ind["name"], "url": f"/industries/{ind['slug']}/"}
        for ind in dimensions.get("industries", [])[:3]
    ]

    body = f"""
<div class="seo-page">
    <div class="container">
        {breadcrumb_html(crumbs)}

        <section class="dimension-hero">
            <div class="dimension-hero-label">Role Intelligence</div>
            <h1>{name} Hiring Data &mdash; {YEAR}</h1>
            <p class="dimension-hero-subtitle">Real-time VP+ hiring intelligence for executive recruiters placing {name} roles.</p>

            <div class="dimension-stats">
                <div class="dimension-stat">
                    <div class="num">{lead_count}</div>
                    <div class="lbl">Open roles this week</div>
                </div>
                <div class="dimension-stat">
                    <div class="num">{role['salary_median']}</div>
                    <div class="lbl">Median salary</div>
                </div>
                <div class="dimension-stat">
                    <div class="num">{role['salary_p75']}</div>
                    <div class="lbl">75th percentile</div>
                </div>
            </div>
        </section>

        <section class="dimension-detail">
            <h2>Salary Benchmarks</h2>
            <p>Based on {lead_count} {name} postings with posted compensation this week.</p>
            <div class="salary-range">
                <div class="salary-bar">
                    <div class="salary-marker p25">
                        <span class="salary-marker-label">P25</span>
                        <span class="salary-marker-value">{role['salary_p25']}</span>
                    </div>
                    <div class="salary-marker median">
                        <span class="salary-marker-label">Median</span>
                        <span class="salary-marker-value">{role['salary_median']}</span>
                    </div>
                    <div class="salary-marker p75">
                        <span class="salary-marker-label">P75</span>
                        <span class="salary-marker-value">{role['salary_p75']}</span>
                    </div>
                </div>
            </div>
        </section>

        <section class="dimension-detail">
            <h2>Hiring Signals</h2>
            <p>The most common signal for {name} roles is <strong>{role['top_signal']}</strong>.
            {name} roles typically report to the <strong>{role['reports_to']}</strong>.
            The top hiring industry is <strong>{role['top_industry']}</strong>.</p>

            <div class="signal-highlights">
                <div class="signal-highlight">
                    <span class="signal-badge growth">{role['top_signal']}</span>
                    <span>Most common signal</span>
                </div>
                <div class="signal-highlight">
                    <span class="signal-badge team">Reports to {role['reports_to']}</span>
                    <span>Typical reporting structure</span>
                </div>
            </div>
        </section>

        {cta_inline_html()}

        {faq_section_html(faqs)}

        {related_pages_html(related, f"Other Executive Roles")}
        {related_pages_html(cross_industry, "Top Industries Hiring")}
    </div>
</div>"""

    title = f"{name} Hiring Data {YEAR} | Salary, Signals & Market Intel — {SITE_NAME}"
    desc = (
        f"{name} hiring intelligence: {role['salary_median']} median salary, "
        f"{lead_count} open roles this week. Scored leads with salary data "
        f"and hiring signals for executive recruiters."
    )

    breadcrumb_schema = generate_breadcrumb_schema(
        [c for c in crumbs if c["url"]] + [{"name": name, "url": f"/roles/{slug}/"}]
    )
    dataset_schema = generate_dataset_schema(
        f"{name} Salary & Hiring Data {YEAR}",
        f"Weekly {name} hiring data including salary benchmarks, hiring signals, and market intelligence.",
        lead_count,
        f"/roles/{slug}/",
    )
    faq_schema = generate_faq_schema(faqs)

    schemas = {"@context": "https://schema.org", "@graph": [breadcrumb_schema, dataset_schema]}
    if faq_schema:
        schemas["@graph"].append(faq_schema)

    return get_page_wrapper(title, desc, f"/roles/{slug}/", body, schemas=schemas, noindex=noindex)


# ─── City Pages (Locations playbook) ───


def build_city_page(city, dimensions):
    """Generate a city-specific page (e.g., /cities/new-york/)."""
    name = city["name"]
    slug = city["slug"]
    lead_count = city["lead_count"]
    noindex = lead_count < MIN_LEADS_FOR_INDEX

    crumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Cities", "url": "/cities/"},
        {"name": name, "url": None},
    ]

    faqs = generate_city_faqs(city)
    related = get_related_pages(slug, "cities", dimensions)
    top_roles_str = ", ".join(city["top_roles"][:3])
    top_companies_str = ", ".join(city["top_companies"][:3])

    # Cross-dimension: roles most common in this city
    cross_roles = [
        {"name": r, "url": f"/roles/{r.lower().replace(' ', '-')}/"}
        for r in city["top_roles"][:3]
    ]

    body = f"""
<div class="seo-page">
    <div class="container">
        {breadcrumb_html(crumbs)}

        <section class="dimension-hero">
            <div class="dimension-hero-label">Market Intelligence</div>
            <h1>Executive Hiring in {name} &mdash; {YEAR}</h1>
            <p class="dimension-hero-subtitle">VP+ hiring data for executive recruiters placing in the {name} market.</p>

            <div class="dimension-stats">
                <div class="dimension-stat">
                    <div class="num">{lead_count}</div>
                    <div class="lbl">VP+ leads this week</div>
                </div>
                <div class="dimension-stat">
                    <div class="num">{city['avg_salary']}</div>
                    <div class="lbl">Average salary</div>
                </div>
                <div class="dimension-stat">
                    <div class="num">{city['remote_pct']}</div>
                    <div class="lbl">Remote-eligible</div>
                </div>
            </div>
        </section>

        <section class="dimension-detail">
            <h2>Market Overview</h2>
            <p>{name} has {lead_count} scored VP+ openings this week with an average salary of {city['avg_salary']}.
            Top roles hiring: <strong>{top_roles_str}</strong>.
            Top companies: <strong>{top_companies_str}</strong>.</p>
            <p>{city['remote_pct']} of {name}-based executive roles offer remote or hybrid arrangements.</p>
        </section>

        <section class="dimension-detail">
            <h2>Top Hiring Companies</h2>
            <div class="company-list">
                {"".join(f'<div class="company-item">{c}</div>' for c in city['top_companies'])}
            </div>
        </section>

        {cta_inline_html()}

        {faq_section_html(faqs)}

        {related_pages_html(related, "Other Markets")}
        {related_pages_html(cross_roles, f"Top Roles in {name}")}
    </div>
</div>"""

    title = f"Executive Hiring in {name} {YEAR} | VP+ Leads & Salary Data — {SITE_NAME}"
    desc = (
        f"{name} executive hiring: {lead_count} VP+ roles, {city['avg_salary']} average salary. "
        f"Top companies: {top_companies_str}. Weekly scored leads for executive recruiters."
    )

    breadcrumb_schema = generate_breadcrumb_schema(
        [c for c in crumbs if c["url"]] + [{"name": name, "url": f"/cities/{slug}/"}]
    )
    dataset_schema = generate_dataset_schema(
        f"VP+ Hiring Data for {name} {YEAR}",
        f"Weekly executive hiring data for the {name} market including salary benchmarks and company intelligence.",
        lead_count,
        f"/cities/{slug}/",
    )
    faq_schema = generate_faq_schema(faqs)

    schemas = {"@context": "https://schema.org", "@graph": [breadcrumb_schema, dataset_schema]}
    if faq_schema:
        schemas["@graph"].append(faq_schema)

    return get_page_wrapper(title, desc, f"/cities/{slug}/", body, schemas=schemas, noindex=noindex)


# ─── Industry Pages ───


def build_industry_page(industry, dimensions):
    """Generate an industry-specific page (e.g., /industries/healthcare/)."""
    name = industry["name"]
    slug = industry["slug"]
    lead_count = industry["lead_count"]
    noindex = lead_count < MIN_LEADS_FOR_INDEX

    crumbs = [
        {"name": "Home", "url": "/"},
        {"name": "Industries", "url": "/industries/"},
        {"name": name, "url": None},
    ]

    faqs = generate_industry_faqs(industry)
    related = get_related_pages(slug, "industries", dimensions)
    top_roles_str = ", ".join(industry["top_roles"][:3])

    cross_roles = [
        {"name": r, "url": f"/roles/{r.lower().replace(' ', '-')}/"}
        for r in industry["top_roles"][:3]
    ]

    velocity_class = "up" if industry["velocity_wow"].startswith("+") else "down"

    body = f"""
<div class="seo-page">
    <div class="container">
        {breadcrumb_html(crumbs)}

        <section class="dimension-hero">
            <div class="dimension-hero-label">Industry Intelligence</div>
            <h1>{name} Executive Hiring &mdash; {YEAR}</h1>
            <p class="dimension-hero-subtitle">VP+ hiring velocity, salary data, and market trends for {name}.</p>

            <div class="dimension-stats">
                <div class="dimension-stat">
                    <div class="num">{lead_count}</div>
                    <div class="lbl">VP+ leads this week</div>
                </div>
                <div class="dimension-stat">
                    <div class="num">{industry['avg_salary']}</div>
                    <div class="lbl">Average salary</div>
                </div>
                <div class="dimension-stat">
                    <div class="num {velocity_class}">{industry['velocity_wow']}</div>
                    <div class="lbl">Week-over-week</div>
                </div>
            </div>
        </section>

        <section class="dimension-detail">
            <h2>Hiring Trend</h2>
            <p>{name} executive hiring is currently <strong>{industry['hiring_trend'].lower()}</strong>
            with a <span class="{velocity_class}">{industry['velocity_wow']}</span> change week-over-week.
            The most in-demand roles are <strong>{top_roles_str}</strong>,
            with an average salary of {industry['avg_salary']}.</p>
        </section>

        <section class="dimension-detail">
            <h2>Top Roles in {name}</h2>
            <div class="role-list">
                {"".join(f'<a href="/roles/{r.lower().replace(" ", "-")}/" class="role-item">{r}</a>' for r in industry['top_roles'])}
            </div>
        </section>

        {cta_inline_html()}

        {faq_section_html(faqs)}

        {related_pages_html(related, "Other Industries")}
        {related_pages_html(cross_roles, f"Top Roles in {name}")}
    </div>
</div>"""

    title = f"{name} Executive Hiring {YEAR} | VP+ Salary & Trends — {SITE_NAME}"
    desc = (
        f"{name} executive hiring: {lead_count} VP+ roles, {industry['avg_salary']} avg salary, "
        f"{industry['velocity_wow']} WoW. Scored leads and market intel for executive recruiters."
    )

    breadcrumb_schema = generate_breadcrumb_schema(
        [c for c in crumbs if c["url"]] + [{"name": name, "url": f"/industries/{slug}/"}]
    )
    dataset_schema = generate_dataset_schema(
        f"{name} VP+ Hiring Data {YEAR}",
        f"Weekly executive hiring data for the {name} industry including salary benchmarks and hiring velocity.",
        lead_count,
        f"/industries/{slug}/",
    )
    faq_schema = generate_faq_schema(faqs)

    schemas = {"@context": "https://schema.org", "@graph": [breadcrumb_schema, dataset_schema]}
    if faq_schema:
        schemas["@graph"].append(faq_schema)

    return get_page_wrapper(title, desc, f"/industries/{slug}/", body, schemas=schemas, noindex=noindex)


# ─── Comparison Pages ───


def build_comparison_page(comp, dimensions):
    """Generate a comparison page (e.g., /vs/linkedin-recruiter/)."""
    name = comp["name"]
    slug = comp["slug"]

    crumbs = [
        {"name": "Home", "url": "/"},
        {"name": name, "url": None},
    ]

    faqs = generate_comparison_faqs(comp)

    strengths_html = "".join(f"<li>{s}</li>" for s in comp["strengths"])
    weaknesses_html = "".join(f"<li>{w}</li>" for w in comp["weaknesses"])

    es_strengths = [
        "Scored and ranked VP+ leads",
        "Real salary data from active postings",
        "Hiring signal extraction (growth hire, build team, reports to CEO)",
        "Weekly market intelligence (salary benchmarks, velocity, geo trends)",
        "Excel workbook + PDF one-pager included",
        "$297/mo, no contract",
    ]
    es_strengths_html = "".join(f"<li>{s}</li>" for s in es_strengths)

    body = f"""
<div class="seo-page">
    <div class="container">
        {breadcrumb_html(crumbs)}

        <section class="dimension-hero">
            <div class="dimension-hero-label">Comparison</div>
            <h1>ExecSignals vs {name}</h1>
            <p class="dimension-hero-subtitle">An honest comparison for executive recruiters evaluating their sourcing stack.</p>
        </section>

        <section class="comparison-detail">
            <div class="comparison-grid">
                <div class="comparison-col">
                    <h2>{name}</h2>
                    <div class="comparison-price">{comp['price']}</div>
                    <h3>Strengths</h3>
                    <ul class="comparison-list strengths">{strengths_html}</ul>
                    <h3>Limitations</h3>
                    <ul class="comparison-list weaknesses">{weaknesses_html}</ul>
                </div>
                <div class="comparison-col highlight">
                    <h2>ExecSignals</h2>
                    <div class="comparison-price">$297/mo</div>
                    <h3>What You Get</h3>
                    <ul class="comparison-list strengths">{es_strengths_html}</ul>
                </div>
            </div>
        </section>

        <section class="dimension-detail">
            <h2>When to Use Which</h2>
            <p><strong>{name}</strong> is better if you need {comp['strengths'][0].lower()}.</p>
            <p><strong>ExecSignals</strong> is better if you want scored, ready-to-work VP+ leads
            with salary data and hiring signals delivered every Monday. No searching, no scanning,
            no boolean queries.</p>
            <p>Many recruiters use both. ExecSignals handles the "which roles to pursue" question.
            {name} handles other parts of the workflow.</p>
        </section>

        {cta_inline_html()}

        {faq_section_html(faqs)}
    </div>
</div>"""

    title = f"ExecSignals vs {name} — Comparison for Executive Recruiters"
    desc = (
        f"How does ExecSignals compare to {name}? Honest comparison of features, "
        f"pricing, and use cases for executive search professionals."
    )

    breadcrumb_schema = generate_breadcrumb_schema(
        [{"name": "Home", "url": "/"}, {"name": f"vs {name}", "url": f"/vs/{slug}/"}]
    )
    faq_schema = generate_faq_schema(faqs)

    schemas = {"@context": "https://schema.org", "@graph": [breadcrumb_schema]}
    if faq_schema:
        schemas["@graph"].append(faq_schema)

    return get_page_wrapper(title, desc, f"/vs/{slug}/", body, schemas=schemas)


# ─── Hub Pages ───


def build_hub_page(dimension, items, dimensions):
    """Generate a hub page (e.g., /roles/, /cities/, /industries/)."""
    config = {
        "roles": {
            "title": "Executive Roles",
            "h1": "VP+ Executive Roles — Hiring Data & Salary Benchmarks",
            "subtitle": "Browse hiring intelligence by role. Updated weekly from real job postings.",
            "label": "Role Intelligence",
            "card_stat": lambda item: f"{item['salary_median']} median",
            "card_detail": lambda item: f"{item['lead_count']} leads this week",
        },
        "cities": {
            "title": "Markets",
            "h1": "Executive Hiring by City — VP+ Market Intelligence",
            "subtitle": "Browse VP+ hiring data by metro area. Real salary and demand data, updated weekly.",
            "label": "Market Intelligence",
            "card_stat": lambda item: f"{item['avg_salary']} avg salary",
            "card_detail": lambda item: f"{item['lead_count']} leads this week",
        },
        "industries": {
            "title": "Industries",
            "h1": "Executive Hiring by Industry — Trends & Salary Data",
            "subtitle": "VP+ hiring velocity and salary benchmarks by industry. Updated weekly.",
            "label": "Industry Intelligence",
            "card_stat": lambda item: f"{item['avg_salary']} avg salary",
            "card_detail": lambda item: f"{item['velocity_wow']} WoW",
        },
    }

    cfg = config[dimension]

    crumbs = [
        {"name": "Home", "url": "/"},
        {"name": cfg["title"], "url": None},
    ]

    cards = ""
    for item in items:
        slug = item["slug"]
        cards += f"""
            <a href="/{dimension}/{slug}/" class="hub-card">
                <div class="hub-card-name">{item['name']}</div>
                <div class="hub-card-stat">{cfg['card_stat'](item)}</div>
                <div class="hub-card-detail">{cfg['card_detail'](item)}</div>
            </a>"""

    body = f"""
<div class="seo-page">
    <div class="container">
        {breadcrumb_html(crumbs)}

        <section class="dimension-hero">
            <div class="dimension-hero-label">{cfg['label']}</div>
            <h1>{cfg['h1']}</h1>
            <p class="dimension-hero-subtitle">{cfg['subtitle']}</p>
        </section>

        <div class="hub-grid">{cards}
        </div>

        {cta_inline_html()}
    </div>
</div>"""

    title = f"{cfg['h1']} — {SITE_NAME}"
    desc = cfg["subtitle"]

    breadcrumb_schema = generate_breadcrumb_schema(
        [{"name": "Home", "url": "/"}, {"name": cfg["title"], "url": f"/{dimension}/"}]
    )
    schemas = {"@context": "https://schema.org", "@graph": [breadcrumb_schema]}

    return get_page_wrapper(title, desc, f"/{dimension}/", body, schemas=schemas)


# ─── Sitemap entries ───


def get_seo_sitemap_entries(dimensions):
    """Return list of URLs for all SEO pages."""
    entries = []
    today = datetime.now().strftime("%Y-%m-%d")

    for dim in ["roles", "cities", "industries"]:
        entries.append({"loc": f"/{dim}/", "lastmod": today, "changefreq": "weekly", "priority": "0.8"})
        for item in dimensions.get(dim, []):
            entries.append({
                "loc": f"/{dim}/{item['slug']}/",
                "lastmod": today,
                "changefreq": "weekly",
                "priority": "0.7",
            })

    for comp in dimensions.get("comparisons", []):
        entries.append({
            "loc": f"/vs/{comp['slug']}/",
            "lastmod": today,
            "changefreq": "monthly",
            "priority": "0.6",
        })

    return entries


# ─── Main ───


def write_file(path, content):
    """Write content to file, creating directories as needed."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Built: {path}")


def main():
    parser = argparse.ArgumentParser(description="Generate ExecSignals SEO pages")
    parser.add_argument("--data", help="Path to seo_dimensions.json")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    data_path = args.data or "data/seo_dimensions.json"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found")
        sys.exit(1)

    dimensions = load_dimensions(data_path)
    page_count = 0

    # Role pages
    for role in dimensions.get("roles", []):
        write_file(f"roles/{role['slug']}/index.html", build_role_page(role, dimensions))
        page_count += 1

    # City pages
    for city in dimensions.get("cities", []):
        write_file(f"cities/{city['slug']}/index.html", build_city_page(city, dimensions))
        page_count += 1

    # Industry pages
    for industry in dimensions.get("industries", []):
        write_file(
            f"industries/{industry['slug']}/index.html",
            build_industry_page(industry, dimensions),
        )
        page_count += 1

    # Comparison pages
    for comp in dimensions.get("comparisons", []):
        write_file(f"vs/{comp['slug']}/index.html", build_comparison_page(comp, dimensions))
        page_count += 1

    # Hub pages
    for dim in ["roles", "cities", "industries"]:
        items = dimensions.get(dim, [])
        if items:
            write_file(f"{dim}/index.html", build_hub_page(dim, items, dimensions))
            page_count += 1

    # Update sitemap with SEO entries
    update_sitemap(dimensions)

    print(f"Done! {page_count} SEO pages generated.")


def update_sitemap(dimensions):
    """Regenerate sitemap.xml including SEO pages."""
    today = datetime.now().strftime("%Y-%m-%d")

    # Core pages
    urls = [
        {"loc": "/", "lastmod": today, "changefreq": "weekly", "priority": "1.0"},
        {"loc": "/privacy/", "lastmod": today, "changefreq": "yearly", "priority": "0.3"},
        {"loc": "/terms/", "lastmod": today, "changefreq": "yearly", "priority": "0.3"},
    ]

    # SEO pages
    urls.extend(get_seo_sitemap_entries(dimensions))

    xml_urls = ""
    for url in urls:
        xml_urls += f"""    <url>
        <loc>https://{DOMAIN}{url['loc']}</loc>
        <lastmod>{url['lastmod']}</lastmod>
        <changefreq>{url['changefreq']}</changefreq>
        <priority>{url['priority']}</priority>
    </url>\n"""

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{xml_urls}</urlset>"""

    write_file("sitemap.xml", sitemap)
    print(f"  Sitemap updated with {len(urls)} URLs.")


if __name__ == "__main__":
    main()
