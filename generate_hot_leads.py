#!/usr/bin/env python3
"""
Hot Leads Weekly — Generate curated executive job leads for recruiting firms.

Queries a job scraping database for high-signal VP+ postings that indicate
executive search opportunities: growth hires, team builders, CEO/CRO reports,
and first-hire roles with real salary budgets.

Usage:
    python generate_hot_leads.py
    python generate_hot_leads.py --days 14 --min-seniority director
    python generate_hot_leads.py --db /path/to/jobs.db --output-dir ./output
"""

import argparse
import csv
import html
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Default database path
DEFAULT_DB = "/Users/rome/Documents/projects/scrapers/master/data/jobs.db"

# Seniority tiers in order of rank (highest first)
SENIORITY_RANK = {
    "c_level": 7,
    "evp": 6,
    "svp": 5,
    "vp": 4,
    "head_of": 3.5,
    "head": 3.5,
    "senior_director": 3,
    "director": 2,
    "senior_manager": 1,
    "manager": 0,
}

# Signals that qualify a job as a "hot lead"
HOT_HIRING_SIGNALS = {"growth_hire", "build_team"}
HOT_TEAM_SIGNALS = {"reports_ceo", "reports_cro", "first_hire", "build_team"}

# Scoring weights
SCORE_BASE = 10
SCORE_SENIORITY_BONUS = {
    "c_level": 15,
    "evp": 12,
    "svp": 10,
    "vp": 5,
    "head_of": 3,
    "head": 3,
    "senior_director": 1,
    "director": 0,
}
SCORE_SIGNAL_BONUS = {
    "reports_ceo": 10,
    "first_hire": 8,
    "reports_cro": 6,
    "build_team": 5,
    "growth_hire": 4,
    "immediate": 2,
    "turnaround": 1,
}
SCORE_SALARY_THRESHOLDS = [
    (300000, 10),
    (200000, 7),
    (150000, 4),
    (100000, 2),
]


def get_seniority_tiers_at_or_above(min_seniority: str) -> list[str]:
    """Return all seniority tiers at or above the given minimum."""
    min_rank = SENIORITY_RANK.get(min_seniority, 0)
    return [tier for tier, rank in SENIORITY_RANK.items() if rank >= min_rank]


def fetch_hot_leads(db_path: str, days: int, min_seniority: str) -> list[dict]:
    """Query the database for hot lead jobs."""
    tiers = get_seniority_tiers_at_or_above(min_seniority)
    if not tiers:
        print(f"Warning: Unknown seniority tier '{min_seniority}', defaulting to vp+")
        tiers = get_seniority_tiers_at_or_above("vp")

    placeholders = ",".join("?" for _ in tiers)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Find jobs that match hot lead criteria:
    # VP+ seniority, has salary, posted within date range,
    # AND has at least one hot hiring signal or hot team structure signal
    query = f"""
        SELECT DISTINCT j.id, j.title, j.company_name, j.company_name_normalized,
               j.location_raw, j.location_metro, j.location_state, j.location_type,
               j.is_remote, j.annual_salary_min, j.annual_salary_max,
               j.seniority_tier, j.function_category, j.source_url,
               j.date_posted, j.description_snippet, j.company_industry,
               j.company_num_employees, j.company_stage, j.company_url
        FROM jobs j
        JOIN job_signals js ON j.id = js.job_id
        WHERE j.seniority_tier IN ({placeholders})
          AND j.has_salary = 1
          AND j.date_posted >= ?
          AND (
              (js.signal_type = 'hiring_signals' AND js.signal_id IN ('growth_hire'))
              OR (js.signal_type = 'team_structure' AND js.signal_id IN ('build_team', 'reports_ceo', 'reports_cro', 'first_hire'))
          )
        ORDER BY j.date_posted DESC
    """

    params = tiers + [cutoff_date]
    jobs = conn.execute(query, params).fetchall()

    # Now enrich each job with all its signals and tools
    leads = []
    for job in jobs:
        job_id = job["id"]
        job_dict = dict(job)

        # Fetch all signals for this job
        signals = conn.execute(
            "SELECT signal_type, signal_id, signal_value FROM job_signals WHERE job_id = ?",
            (job_id,),
        ).fetchall()
        job_dict["signals"] = [dict(s) for s in signals]

        # Fetch tools
        tools = conn.execute(
            "SELECT tool_name, tool_category FROM job_tools WHERE job_id = ?",
            (job_id,),
        ).fetchall()
        job_dict["tools"] = [dict(t) for t in tools]

        leads.append(job_dict)

    conn.close()
    return leads


def score_lead(lead: dict) -> int:
    """Score a lead based on signal richness, seniority, and salary."""
    score = SCORE_BASE

    # Seniority bonus
    tier = lead.get("seniority_tier", "")
    score += SCORE_SENIORITY_BONUS.get(tier, 0)

    # Signal bonuses (each unique qualifying signal adds points)
    seen_signals = set()
    for sig in lead.get("signals", []):
        sig_id = sig["signal_id"]
        if sig_id not in seen_signals:
            score += SCORE_SIGNAL_BONUS.get(sig_id, 0)
            seen_signals.add(sig_id)

    # Multiple growth signals bonus
    growth_signals = [s for s in lead.get("signals", [])
                      if s["signal_id"] in HOT_HIRING_SIGNALS | HOT_TEAM_SIGNALS]
    if len(growth_signals) >= 3:
        score += 5  # Multi-signal richness bonus

    # Salary bonus
    max_salary = lead.get("annual_salary_max") or lead.get("annual_salary_min") or 0
    for threshold, bonus in SCORE_SALARY_THRESHOLDS:
        if max_salary >= threshold:
            score += bonus
            break

    # Company info bonuses
    if lead.get("company_stage"):
        stage = lead["company_stage"].lower()
        if "series" in stage or "growth" in stage:
            score += 2

    return score


def format_salary(min_sal, max_sal) -> str:
    """Format salary range as human-readable string."""
    def fmt(val):
        if val is None:
            return None
        if val >= 1_000_000:
            return f"${val / 1_000_000:.1f}M"
        return f"${val / 1_000:,.0f}K"

    min_str = fmt(min_sal)
    max_str = fmt(max_sal)

    if min_str and max_str:
        return f"{min_str} - {max_str}"
    elif max_str:
        return f"Up to {max_str}"
    elif min_str:
        return f"{min_str}+"
    return "Not specified"


def format_location(lead: dict) -> str:
    """Build a readable location string."""
    parts = []
    metro = lead.get("location_metro")
    state = lead.get("location_state")
    loc_type = lead.get("location_type")
    is_remote = lead.get("is_remote")

    if metro:
        parts.append(metro)
    elif state:
        parts.append(state)
    elif lead.get("location_raw"):
        parts.append(lead["location_raw"])

    if is_remote or (loc_type and "remote" in loc_type.lower()):
        if parts:
            parts.append("(Remote)")
        else:
            parts.append("Remote")
    elif loc_type and "hybrid" in loc_type.lower():
        parts.append("(Hybrid)")

    return ", ".join(parts) if parts else "Location not specified"


def extract_hiring_signal(lead: dict) -> str:
    """Get the primary hiring signal for display."""
    signal_priority = ["growth_hire", "turnaround", "immediate"]
    for sig in lead.get("signals", []):
        if sig["signal_type"] == "hiring_signals" and sig["signal_id"] in signal_priority:
            return sig["signal_id"].replace("_", " ").title()
    return ""


def extract_team_structure(lead: dict) -> str:
    """Get team structure signals for display."""
    team_sigs = []
    seen = set()
    for sig in lead.get("signals", []):
        if sig["signal_type"] == "team_structure" and sig["signal_id"] not in seen:
            team_sigs.append(sig["signal_id"].replace("_", " ").title())
            seen.add(sig["signal_id"])
    return ", ".join(team_sigs)


def extract_key_tools(lead: dict, max_tools: int = 5) -> str:
    """Get the most relevant tools for display."""
    tools = []
    seen = set()
    for t in lead.get("tools", []):
        name = t["tool_name"]
        if name not in seen:
            tools.append(name)
            seen.add(name)
        if len(tools) >= max_tools:
            break
    return ", ".join(tools)


def extract_extra_signals(lead: dict) -> dict:
    """Extract additional signal context for rich display."""
    extras = {}
    for sig in lead.get("signals", []):
        st, sid = sig["signal_type"], sig["signal_id"]
        if st == "segment":
            extras.setdefault("segment", []).append(sid.replace("_", " ").title())
        elif st == "deal_size":
            extras.setdefault("deal_size", []).append(sid.replace("_", " ").title())
        elif st == "comp_signals":
            extras.setdefault("comp", []).append(sid.replace("_", " ").title())
        elif st == "motion":
            extras.setdefault("motion", []).append(sid.replace("_", " ").title())
    return extras


def generate_csv(leads: list[dict], output_path: str):
    """Write leads to CSV file."""
    fieldnames = [
        "Score", "Title", "Company", "Location", "Seniority",
        "Salary Range", "Hiring Signal", "Team Structure", "Segment",
        "Key Tools", "Source URL", "Date Posted",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for lead in leads:
            extras = extract_extra_signals(lead)
            writer.writerow({
                "Score": lead["score"],
                "Title": lead["title"],
                "Company": lead.get("company_name") or "Confidential",
                "Location": format_location(lead),
                "Seniority": (lead.get("seniority_tier") or "").replace("_", " ").title(),
                "Salary Range": format_salary(
                    lead.get("annual_salary_min"),
                    lead.get("annual_salary_max"),
                ),
                "Hiring Signal": extract_hiring_signal(lead),
                "Team Structure": extract_team_structure(lead),
                "Segment": ", ".join(extras.get("segment", [])),
                "Key Tools": extract_key_tools(lead),
                "Source URL": lead.get("source_url") or "",
                "Date Posted": (lead.get("date_posted") or "")[:10],
            })


def generate_html_email(leads: list[dict], days: int) -> str:
    """Generate the HTML email body for weekly delivery."""
    now = datetime.now()
    date_range = f"{(now - timedelta(days=days)).strftime('%b %d')} - {now.strftime('%b %d, %Y')}"

    # Summary stats
    total = len(leads)
    avg_score = sum(l["score"] for l in leads) / total if total else 0

    # Count signals
    signal_counts = {}
    for lead in leads:
        for sig in lead.get("signals", []):
            if sig["signal_type"] in ("hiring_signals", "team_structure"):
                label = sig["signal_id"].replace("_", " ").title()
                signal_counts[label] = signal_counts.get(label, 0) + 1
    top_signal = max(signal_counts, key=signal_counts.get) if signal_counts else "N/A"

    # Seniority breakdown
    seniority_counts = {}
    for lead in leads:
        tier = (lead.get("seniority_tier") or "unknown").replace("_", " ").title()
        seniority_counts[tier] = seniority_counts.get(tier, 0) + 1

    top5 = leads[:5]

    # Build top 5 HTML cards
    top5_html = ""
    for i, lead in enumerate(top5, 1):
        title = html.escape(lead.get("title") or "Untitled")
        company = html.escape(lead.get("company_name") or "Confidential")
        salary = html.escape(format_salary(lead.get("annual_salary_min"), lead.get("annual_salary_max")))
        location = html.escape(format_location(lead))
        hiring_sig = html.escape(extract_hiring_signal(lead))
        team_sig = html.escape(extract_team_structure(lead))
        source = lead.get("source_url") or "#"
        score = lead["score"]

        signal_badges = ""
        if hiring_sig:
            signal_badges += f'<span style="display:inline-block;background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:3px;font-size:12px;margin-right:4px;">{hiring_sig}</span>'
        if team_sig:
            signal_badges += f'<span style="display:inline-block;background:#e3f2fd;color:#1565c0;padding:2px 8px;border-radius:3px;font-size:12px;margin-right:4px;">{team_sig}</span>'

        top5_html += f"""
        <tr>
            <td style="padding:16px 20px;border-bottom:1px solid #eee;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div style="font-size:11px;color:#888;margin-bottom:2px;">#{i} &middot; Score: {score}</div>
                        <a href="{html.escape(source)}" style="color:#1a1a2e;font-size:16px;font-weight:600;text-decoration:none;">{title}</a>
                        <div style="color:#555;font-size:14px;margin-top:4px;">{company}</div>
                        <div style="color:#777;font-size:13px;margin-top:2px;">{location} &middot; {salary}</div>
                        <div style="margin-top:8px;">{signal_badges}</div>
                    </div>
                </div>
            </td>
        </tr>"""

    # Seniority breakdown HTML
    seniority_html = ""
    for tier, count in sorted(seniority_counts.items(), key=lambda x: -x[1]):
        seniority_html += f"<li>{tier}: {count}</li>"

    email_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hot Leads Weekly</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f7;">
        <tr>
            <td align="center" style="padding:24px 16px;">
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background:#1a1a2e;padding:32px 24px;text-align:center;">
                            <h1 style="color:#fff;margin:0;font-size:24px;font-weight:700;letter-spacing:-0.5px;">Hot Leads Weekly</h1>
                            <p style="color:#a0a0c0;margin:8px 0 0;font-size:14px;">{date_range}</p>
                        </td>
                    </tr>

                    <!-- Summary Stats -->
                    <tr>
                        <td style="padding:24px;">
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td width="33%" align="center" style="padding:12px;">
                                        <div style="font-size:28px;font-weight:700;color:#1a1a2e;">{total}</div>
                                        <div style="font-size:12px;color:#888;text-transform:uppercase;letter-spacing:0.5px;">Hot Leads</div>
                                    </td>
                                    <td width="33%" align="center" style="padding:12px;">
                                        <div style="font-size:28px;font-weight:700;color:#1a1a2e;">{avg_score:.0f}</div>
                                        <div style="font-size:12px;color:#888;text-transform:uppercase;letter-spacing:0.5px;">Avg Score</div>
                                    </td>
                                    <td width="33%" align="center" style="padding:12px;">
                                        <div style="font-size:16px;font-weight:700;color:#2e7d32;">{top_signal}</div>
                                        <div style="font-size:12px;color:#888;text-transform:uppercase;letter-spacing:0.5px;">Top Signal</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Seniority Breakdown -->
                    <tr>
                        <td style="padding:0 24px 16px;">
                            <div style="background:#f8f9fa;border-radius:6px;padding:16px;">
                                <div style="font-size:13px;font-weight:600;color:#555;margin-bottom:8px;text-transform:uppercase;letter-spacing:0.5px;">Seniority Breakdown</div>
                                <ul style="margin:0;padding-left:20px;color:#555;font-size:14px;line-height:1.6;">
                                    {seniority_html}
                                </ul>
                            </div>
                        </td>
                    </tr>

                    <!-- Top 5 Divider -->
                    <tr>
                        <td style="padding:8px 24px 0;">
                            <h2 style="font-size:16px;color:#1a1a2e;margin:0;padding-bottom:12px;border-bottom:2px solid #1a1a2e;">Top 5 Leads This Week</h2>
                        </td>
                    </tr>

                    <!-- Top 5 Cards -->
                    <tr>
                        <td style="padding:0 4px;">
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                                {top5_html}
                            </table>
                        </td>
                    </tr>

                    <!-- CSV Note -->
                    <tr>
                        <td style="padding:24px;text-align:center;">
                            <div style="background:#f0f7ff;border-radius:6px;padding:16px;">
                                <p style="margin:0;color:#1565c0;font-size:14px;font-weight:500;">
                                    Full list of {total} leads attached as CSV
                                </p>
                                <p style="margin:4px 0 0;color:#777;font-size:13px;">
                                    Sortable by score, salary, seniority, and signals
                                </p>
                            </div>
                        </td>
                    </tr>

                    <!-- Feedback CTA -->
                    <tr>
                        <td style="padding:0 24px 32px;text-align:center;">
                            <p style="color:#555;font-size:14px;margin:0 0 16px;">
                                How useful were this week's leads?
                            </p>
                            <a href="mailto:rome@paritermedia.com?subject=Hot%20Leads%20Feedback" style="display:inline-block;background:#1a1a2e;color:#fff;padding:12px 32px;border-radius:6px;text-decoration:none;font-size:14px;font-weight:500;">Share Feedback</a>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background:#f8f9fa;padding:20px 24px;border-top:1px solid #eee;">
                            <p style="margin:0;color:#999;font-size:12px;text-align:center;">
                                Hot Leads Weekly by Pariter Media Inc.<br>
                                Curated from {total} qualifying VP+ executive postings.<br>
                                <a href="mailto:rome@paritermedia.com" style="color:#999;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return email_html


def generate_text_email(leads: list[dict], days: int) -> str:
    """Generate the plain text email body for weekly delivery."""
    now = datetime.now()
    date_range = f"{(now - timedelta(days=days)).strftime('%b %d')} - {now.strftime('%b %d, %Y')}"

    total = len(leads)
    avg_score = sum(l["score"] for l in leads) / total if total else 0

    # Count signals
    signal_counts = {}
    for lead in leads:
        for sig in lead.get("signals", []):
            if sig["signal_type"] in ("hiring_signals", "team_structure"):
                label = sig["signal_id"].replace("_", " ").title()
                signal_counts[label] = signal_counts.get(label, 0) + 1
    top_signal = max(signal_counts, key=signal_counts.get) if signal_counts else "N/A"

    # Seniority breakdown
    seniority_counts = {}
    for lead in leads:
        tier = (lead.get("seniority_tier") or "unknown").replace("_", " ").title()
        seniority_counts[tier] = seniority_counts.get(tier, 0) + 1

    lines = []
    lines.append("=" * 60)
    lines.append("HOT LEADS WEEKLY")
    lines.append(date_range)
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  {total} Hot Leads  |  Avg Score: {avg_score:.0f}  |  Top Signal: {top_signal}")
    lines.append("")

    # Seniority breakdown
    lines.append("SENIORITY BREAKDOWN:")
    for tier, count in sorted(seniority_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  {tier}: {count}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("TOP 5 LEADS THIS WEEK")
    lines.append("-" * 60)

    top5 = leads[:5]
    for i, lead in enumerate(top5, 1):
        title = lead.get("title") or "Untitled"
        company = lead.get("company_name") or "Confidential"
        salary = format_salary(lead.get("annual_salary_min"), lead.get("annual_salary_max"))
        location = format_location(lead)
        hiring_sig = extract_hiring_signal(lead)
        team_sig = extract_team_structure(lead)
        source = lead.get("source_url") or "N/A"
        score = lead["score"]

        lines.append("")
        lines.append(f"  #{i} (Score: {score})")
        lines.append(f"  {title}")
        lines.append(f"  {company}")
        lines.append(f"  {location}  |  {salary}")
        signals_str = "  |  ".join(filter(None, [hiring_sig, team_sig]))
        if signals_str:
            lines.append(f"  Signals: {signals_str}")
        lines.append(f"  {source}")
        lines.append("")

    lines.append("-" * 60)
    lines.append("")
    lines.append(f"Full list of {total} leads attached as CSV.")
    lines.append("Sortable by score, salary, seniority, and signals.")
    lines.append("")
    lines.append("How useful were this week's leads?")
    lines.append("Reply to this email with feedback.")
    lines.append("")
    lines.append("-" * 60)
    lines.append("Hot Leads Weekly by Pariter Media Inc.")
    lines.append(f"Curated from {total} qualifying VP+ executive postings.")
    lines.append("Reply with 'unsubscribe' to stop receiving these emails.")
    lines.append("-" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Hot Leads Weekly — curated executive job leads for recruiters"
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"Path to jobs.db (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days back to search (default: 7)",
    )
    parser.add_argument(
        "--min-seniority",
        default="vp",
        choices=list(SENIORITY_RANK.keys()),
        help="Minimum seniority tier (default: vp)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory for output files (default: current directory)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        help="Only include top N leads by score (default: all)",
    )
    args = parser.parse_args()

    # Validate DB exists
    if not os.path.exists(args.db):
        print(f"Error: Database not found at {args.db}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Querying {args.db}...")
    print(f"Parameters: last {args.days} days, min seniority: {args.min_seniority}")
    print()

    # Fetch and score leads
    leads = fetch_hot_leads(args.db, args.days, args.min_seniority)
    print(f"Found {len(leads)} qualifying leads")

    if not leads:
        print("No hot leads found for the given criteria.")
        print("Try increasing --days or lowering --min-seniority.")
        sys.exit(0)

    # Score and sort
    for lead in leads:
        lead["score"] = score_lead(lead)
    leads.sort(key=lambda x: x["score"], reverse=True)

    # Apply top-N filter if specified
    if args.top:
        leads = leads[: args.top]
        print(f"Filtered to top {args.top} leads")

    # Print summary
    scores = [l["score"] for l in leads]
    print(f"Score range: {min(scores)} - {max(scores)} (avg: {sum(scores)/len(scores):.1f})")
    print()

    # Show top 5 in terminal
    print("Top 5 leads:")
    print("-" * 70)
    for i, lead in enumerate(leads[:5], 1):
        title = lead.get("title", "Untitled")
        company = lead.get("company_name") or "Confidential"
        salary = format_salary(lead.get("annual_salary_min"), lead.get("annual_salary_max"))
        score = lead["score"]
        print(f"  {i}. [{score}] {title}")
        print(f"     {company} | {salary}")
        print(f"     {extract_hiring_signal(lead)} | {extract_team_structure(lead)}")
        print()

    # Generate outputs
    csv_path = output_dir / "hot_leads.csv"
    generate_csv(leads, str(csv_path))
    print(f"CSV:        {csv_path} ({len(leads)} rows)")

    html_path = output_dir / "hot_leads_email.html"
    html_content = generate_html_email(leads, args.days)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML email: {html_path}")

    txt_path = output_dir / "hot_leads_email.txt"
    txt_content = generate_text_email(leads, args.days)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt_content)
    print(f"Text email: {txt_path}")

    print()
    print("Done. Attach hot_leads.csv to the email and send hot_leads_email.html as the body.")


if __name__ == "__main__":
    main()
