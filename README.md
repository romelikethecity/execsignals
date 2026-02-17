# Hot Leads Weekly

Weekly curated feed of high-signal VP+ executive job postings for recruiting firms. Surfaces growth hires, team-building mandates, and CEO/CRO direct reports with confirmed salary budgets.

## What This Is

A Python script that queries a job scraping database, identifies the postings most likely to represent retained executive search opportunities, scores them by signal richness, and generates email-ready output (HTML, plain text, and CSV attachment).

The output is a weekly deliverable sent to subscribing recruiting firms every Monday morning.

## Quick Start

```bash
# Generate this week's hot leads (default: last 7 days, VP+ seniority)
python generate_hot_leads.py

# Custom time range
python generate_hot_leads.py --days 14

# Lower seniority threshold
python generate_hot_leads.py --min-seniority director

# Custom DB path and output directory
python generate_hot_leads.py --db /path/to/jobs.db --output-dir ./output

# Only top 25 leads
python generate_hot_leads.py --top 25
```

### Output Files

- `hot_leads.csv` — Full scored list, attach to email
- `hot_leads_email.html` — HTML email body with top 5 highlights and summary stats
- `hot_leads_email.txt` — Plain text fallback

### Requirements

- Python 3.10+
- No external dependencies (uses only `sqlite3`, `csv`, `argparse`, `html` from stdlib)

## How Scoring Works

Each qualifying lead starts with a base score of 10 and accumulates bonuses:

### Seniority Bonus
| Tier | Bonus |
|------|-------|
| C-Level | +15 |
| EVP | +12 |
| SVP | +10 |
| VP | +5 |
| Head/Head Of | +3 |

### Signal Bonus
| Signal | Bonus |
|--------|-------|
| Reports to CEO | +10 |
| First Hire | +8 |
| Reports to CRO | +6 |
| Build Team | +5 |
| Growth Hire | +4 |
| Immediate | +2 |
| Turnaround | +1 |

### Salary Bonus
| Max Salary | Bonus |
|------------|-------|
| $300K+ | +10 |
| $200K+ | +7 |
| $150K+ | +4 |
| $100K+ | +2 |

### Additional Bonuses
- **Multi-signal richness:** +5 if 3 or more qualifying signals are present
- **Growth-stage company:** +2 if company stage indicates Series funding or growth stage

### Score Interpretation
- **40+**: Exceptional — C-level, high salary, multiple strong signals. Reach out immediately.
- **30-39**: Strong — VP+ with good signal combination. Priority outreach.
- **20-29**: Solid — Qualifies on fundamentals but fewer distinguishing signals.
- **10-19**: Baseline — Meets minimum criteria. Worth monitoring.

## What Qualifies as a "Hot Lead"

A job posting must meet ALL of these criteria:

1. **Seniority:** VP, SVP, EVP, or C-Level (configurable with `--min-seniority`)
2. **Hiring signal:** At least one of: Growth Hire (from hiring_signals) or Build Team, Reports to CEO, Reports to CRO, First Hire (from team_structure)
3. **Has salary:** Posted compensation confirms real budget authority
4. **Recency:** Posted within the last 7 days (configurable with `--days`)

### Why These Criteria

- **VP+ seniority** — Below VP, companies rarely engage retained search firms. Director-level and below are typically handled by internal TA or contingency recruiters.
- **Growth/Build signals** — Backfill and replacement hires usually go to internal recruiters or agencies they already work with. Growth hires and first-hire roles are where companies look for outside expertise.
- **CEO/CRO reports** — The higher the reporting line, the higher the stakes and the more likely the company will pay for retained search.
- **Salary posted** — No salary = no confirmed budget = higher chance the role is aspirational, evergreen, or not yet approved. Posted salary means someone signed off on headcount.

## How to Deliver

### MVP: Gmail + Manual Send

1. Run `python generate_hot_leads.py` on Monday morning
2. Open `hot_leads_email.html` in a browser, copy the rendered content
3. Compose a new email in Gmail, paste the HTML content
4. Attach `hot_leads.csv`
5. Send to subscriber list

### Better: Resend or Postmark

For a small subscriber list (under 100), either service works well:

**Resend** (https://resend.com)
- Free tier: 100 emails/day, 3,000/month
- Simple API, good deliverability
- $20/month for 50K emails

**Postmark** (https://postmarkapp.com)
- Best deliverability reputation in the industry
- $15/month for 10K emails
- Transactional email focus (not marketing) — which is exactly what this is

### Automation

Add a cron job or GitHub Action to run the generator every Monday at 6 AM:

```bash
# crontab -e
0 6 * * 1 cd /Users/rome/Documents/projects/products/hot-leads && python generate_hot_leads.py --output-dir ./weekly-output && echo "Hot leads generated" | mail -s "Hot Leads Ready" rome@paritermedia.com
```

## Project Structure

```
hot-leads/
  generate_hot_leads.py      # Main generator script
  email_templates/
    welcome_email.html        # Initial outreach email to prospects
    weekly_delivery.html      # Template for weekly email (with placeholders)
    weekly_delivery.txt        # Plain text version of weekly delivery
  messaging.md                # Product messaging, pricing, objection handling
  README.md                   # This file
```

## Pricing

$297/month per subscriber. See `messaging.md` for full pricing rationale and tier recommendations.

## Database

The generator reads from a SQLite database with these tables:

- `jobs` — Main job postings (title, company, salary, seniority, location, etc.)
- `job_signals` — Extracted signals per job (hiring_signals, team_structure, segment, deal_size, etc.)
- `job_tools` — Tools/tech mentioned per job (CRM, marketing automation, etc.)

Default path: `/Users/rome/Documents/projects/scrapers/master/data/jobs.db`

Override with `--db /your/path/to/jobs.db`.

## Next Steps

1. Run the generator against the live database and review output quality
2. Send a sample report to 3-5 recruiter contacts for feedback
3. Iterate on scoring weights based on feedback
4. Set up Resend or Postmark for automated delivery
5. Build a simple Stripe checkout page for subscriptions
6. Add custom filtering per subscriber (industry, geography, function)
