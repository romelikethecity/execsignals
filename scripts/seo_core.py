#!/usr/bin/env python3
"""ExecSignals — SEO Core Module.

Centralized SEO logic adapted from CRO Report's seo_core.py:
- Schema.org JSON-LD generators (BreadcrumbList, FAQPage, Dataset)
- Data-driven FAQ generators for role/city/industry/comparison pages
- Internal linking helpers
"""

import json
from datetime import datetime

DOMAIN = "execsignals.com"
SITE_NAME = "ExecSignals"


def generate_breadcrumb_schema(breadcrumbs):
    """Generate BreadcrumbList schema markup.

    Args:
        breadcrumbs: list of {"name": "Roles", "url": "/roles/"}
    """
    items = []
    for i, crumb in enumerate(breadcrumbs, 1):
        items.append({
            "@type": "ListItem",
            "position": i,
            "name": crumb["name"],
            "item": f"https://{DOMAIN}{crumb['url']}",
        })

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def generate_faq_schema(faqs):
    """Generate FAQPage schema markup.

    Args:
        faqs: list of {"question": "...", "answer": "..."}
    """
    if not faqs:
        return None

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq["answer"],
                },
            }
            for faq in faqs
        ],
    }


def generate_dataset_schema(title, description, record_count, url):
    """Generate Dataset schema for salary/hiring data pages."""
    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": title,
        "description": description,
        "url": f"https://{DOMAIN}{url}",
        "keywords": [
            "executive hiring data",
            "VP salary data",
            "executive search intelligence",
        ],
        "creator": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": f"https://{DOMAIN}",
        },
        "dateModified": datetime.now().strftime("%Y-%m-%d"),
        "temporalCoverage": str(datetime.now().year),
        "spatialCoverage": "United States",
    }


def generate_role_faqs(role):
    """Generate data-driven FAQs for a role page.

    Args:
        role: dict with name, salary_p25, salary_median, salary_p75,
              lead_count, top_signal, top_industry, reports_to
    """
    name = role["name"]
    return [
        {
            "question": f"What is the average {name} salary in 2026?",
            "answer": (
                f"Based on VP+ roles with posted compensation, the median {name} "
                f"salary is {role['salary_median']}. The 25th percentile is "
                f"{role['salary_p25']} and the 75th percentile is {role['salary_p75']}. "
                f"These figures come from active job postings, not survey estimates."
            ),
        },
        {
            "question": f"How many {name} positions are open right now?",
            "answer": (
                f"This week, ExecSignals tracked {role['lead_count']} scored {name} "
                f"openings with posted compensation. The most common hiring signal "
                f"is \"{role['top_signal']}\" and the top hiring industry is "
                f"{role['top_industry']}."
            ),
        },
        {
            "question": f"What hiring signals matter most for {name} roles?",
            "answer": (
                f"The top signal for {name} roles is \"{role['top_signal']}.\" "
                f"Other common signals include reporting structure (typically reports "
                f"to {role['reports_to']}), team-building mandates, and urgency "
                f"indicators like \"immediate start.\" ExecSignals extracts these "
                f"signals automatically from every job description."
            ),
        },
        {
            "question": f"Is {name} a good retained search opportunity?",
            "answer": (
                f"With a median salary of {role['salary_median']}, {name} roles "
                f"typically fall within retained search territory. Roles with "
                f"\"Build Team\" or \"Reports to CEO\" signals are especially strong "
                f"candidates for retained engagements, as they indicate strategic "
                f"hires with board-level visibility."
            ),
        },
    ]


def generate_city_faqs(city):
    """Generate data-driven FAQs for a city page.

    Args:
        city: dict with name, lead_count, avg_salary, remote_pct,
              top_roles, top_companies
    """
    name = city["name"]
    top_roles_str = ", ".join(city["top_roles"][:3])
    top_companies_str = ", ".join(city["top_companies"][:3])

    faqs = [
        {
            "question": f"How many VP+ executive roles are open in {name}?",
            "answer": (
                f"This week, ExecSignals tracked {city['lead_count']} scored VP+ "
                f"openings in {name} with posted compensation. The average salary "
                f"is {city['avg_salary']}. Top roles hiring: {top_roles_str}."
            ),
        },
        {
            "question": f"What companies are hiring executives in {name}?",
            "answer": (
                f"Top companies posting VP+ roles in {name} this week include "
                f"{top_companies_str}. These are active postings with confirmed "
                f"salary budgets, not evergreen listings."
            ),
        },
        {
            "question": f"What is the average executive salary in {name}?",
            "answer": (
                f"The average VP+ salary in {name} is {city['avg_salary']}, based "
                f"on {city['lead_count']} active postings with posted compensation. "
                f"This is real-time market data, updated weekly."
            ),
        },
    ]

    if name != "Remote":
        faqs.append({
            "question": f"What percentage of {name} executive roles are remote?",
            "answer": (
                f"Currently, {city['remote_pct']} of VP+ roles based in {name} "
                f"offer remote or hybrid work arrangements. This varies by role "
                f"and industry."
            ),
        })

    return faqs


def generate_industry_faqs(industry):
    """Generate data-driven FAQs for an industry page.

    Args:
        industry: dict with name, velocity_wow, lead_count, avg_salary,
                  top_roles, hiring_trend
    """
    name = industry["name"]
    top_roles_str = ", ".join(industry["top_roles"][:3])

    return [
        {
            "question": f"Is {name} hiring executives right now?",
            "answer": (
                f"Yes. {name} posted {industry['lead_count']} VP+ roles with "
                f"salary data this week, with a {industry['velocity_wow']} "
                f"week-over-week change. The hiring trend is: {industry['hiring_trend']}."
            ),
        },
        {
            "question": f"What executive roles are most in demand in {name}?",
            "answer": (
                f"The top VP+ roles in {name} this week are {top_roles_str}. "
                f"Average salary across all {name} executive roles is "
                f"{industry['avg_salary']}."
            ),
        },
        {
            "question": f"What is the average executive salary in {name}?",
            "answer": (
                f"The average VP+ salary in {name} is {industry['avg_salary']}, "
                f"based on {industry['lead_count']} active postings this week. "
                f"This reflects real posted compensation, not survey estimates."
            ),
        },
        {
            "question": f"How is {name} executive hiring trending?",
            "answer": (
                f"{name} VP+ hiring is currently {industry['hiring_trend'].lower()} "
                f"with a {industry['velocity_wow']} change week-over-week. "
                f"ExecSignals tracks these trends every Monday in The Monday Brief."
            ),
        },
    ]


def generate_comparison_faqs(competitor):
    """Generate FAQs for a comparison page.

    Args:
        competitor: dict with name, price, strengths, weaknesses
    """
    name = competitor["name"]
    strengths_str = ", ".join(competitor["strengths"][:3]).lower()
    weaknesses_str = ". ".join(competitor["weaknesses"][:2])

    return [
        {
            "question": f"How does ExecSignals compare to {name}?",
            "answer": (
                f"ExecSignals and {name} serve different needs. {name} excels at "
                f"{strengths_str}. ExecSignals focuses specifically on scored VP+ "
                f"hiring leads with salary data, hiring signal extraction, and "
                f"weekly market intelligence for executive recruiters."
            ),
        },
        {
            "question": f"Is ExecSignals cheaper than {name}?",
            "answer": (
                f"ExecSignals is $297/month with no contract. {name} costs "
                f"{competitor['price']}. The value comparison depends on your "
                f"use case: ExecSignals delivers ready-to-work scored leads, "
                f"while {name} may require more manual effort to achieve "
                f"similar results."
            ),
        },
        {
            "question": f"Can I use ExecSignals alongside {name}?",
            "answer": (
                f"Yes. Many executive recruiters use ExecSignals alongside {name}. "
                f"ExecSignals provides the sourcing intelligence (which roles to "
                f"pursue), while {name} handles other parts of the search workflow."
            ),
        },
    ]


def get_related_pages(current_slug, dimension, all_dimensions, limit=5):
    """Get related page links for internal linking.

    Args:
        current_slug: slug of the current page
        dimension: 'roles', 'cities', or 'industries'
        all_dimensions: the full seo_dimensions dict
        limit: max related pages to return
    """
    items = all_dimensions.get(dimension, [])
    related = [
        {"name": item["name"], "url": f"/{dimension}/{item['slug']}/"}
        for item in items
        if item["slug"] != current_slug
    ]
    return related[:limit]


def slugify(text):
    """Convert text to URL slug."""
    return (
        text.lower()
        .replace(" / ", "-")
        .replace("/", "-")
        .replace(" ", "-")
        .replace("&", "and")
        .replace(",", "")
        .replace(".", "")
        .replace("'", "")
    )
