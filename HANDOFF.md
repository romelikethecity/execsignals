# ExecSignals — Handoff Doc

## What Is This?
ExecSignals (execsignals.com) is a $297/mo B2B product delivering scored VP+ executive job leads and market intelligence to retained search firms and solo executive recruiters every Monday via "The Monday Brief."

**Entity:** Pariter Media Inc.
**Domain:** execsignals.com (live)
**Email:** hello@execsignals.com (placeholder until demand validated — no paritermedia.com email exists)

## Brand (Locked)
- **Name:** ExecSignals
- **Domain:** execsignals.com
- **Weekly delivery:** The Monday Brief
- **Price:** $297/mo
- **Accent:** Warm amber `#D4A054`, background `#0C0F1A`, cards `#111827`
- **Fonts:** DM Serif Display (display) + Plus Jakarta Sans (body) + IBM Plex Mono (data)
- **Signal badges:** green=growth, blue=team, amber=urgency (semantic, not brand)

## Current Status: Mockups Complete, Pending Final Review

All mockups are built and iterated through 2 rounds of user feedback. They need a final visual review in browser before applying to production files.

### Files to Review
| File | What | How to View |
|------|------|-------------|
| `mockups/landing-page.html` | Full landing/sales page | Open in browser |
| `mockups/monday-brief-email.html` | The Monday Brief email | Open in browser |
| `mockups/ExecSignals_Feb17.xlsx` | Excel attachment mockup | Open in Excel/Numbers |
| `mockups/MarketIntel_Feb17.html` | PDF one-pager (print-ready) | Open in browser, Cmd+P to PDF |
| `mockups/generate_execsignals_mockup.py` | Script that generated the .xlsx | Reference only |

### What's in the Landing Page
- Hero with stats: 272 VP+ leads scored, $234K avg salary, 86% growth hires, 1-3 days fresh
- "Built for" badges: Retained search firms, Solo executive recruiters, Boutique search practices
- 4 sample lead cards with: freshness badges (red 1-2d, amber 3-4d), company signals (employee count + public/private), signal one-liners, clickable source URLs
- Blurred geo preview (top 3 metros visible, rest blurred — full data for paid subs only)
- Scoring methodology section
- Value props section
- Market intelligence preview
- Sample email preview section (browser-frame mockup)
- Pricing: $297/mo, "Cancel anytime. No contract, no setup fee."
- CTA sections throughout

### What's in the Email
- Top 10 scored VP+ leads: 5 full cards + 5 compact
- Each lead has: clickable source URL, "Posted X days ago" badge, company signals, signal one-liner, competitive context
- Market intelligence sections: salary benchmarks (P25/median/P75 + trends), hiring velocity (WoW + 4-week), top companies, geo with WoW deltas, company stage, stack trends
- Attachment callout: Excel workbook + PDF one-pager
- ExecSignals branded footer

### What's in the Excel
- Sheet 1 "Top Leads": 20 leads with 15 columns, conditional formatting (score colors, freshness colors), auto-filters, freeze panes, clickable source URLs
- Sheet 2 "Market Intel": Salary benchmarks, velocity, companies, geo, key takeaways

### What's in the PDF One-Pager
- Print-ready US Letter format, one page
- Summary stats, salary benchmarks table, hiring velocity, top 10 companies, geo by metro, company stage bar chart

## User Feedback Already Applied (2 Rounds)

### Round 1 (all implemented):
- Added clickable source URLs to every lead
- Added "Posted X days ago" freshness badges (red 1-2d, amber 3-4d, gray 5+)
- Added company signals (employee count + public/private)
- Added signal one-liners per lead (factual, derived from signals — not AI-generated)
- Added competitive context per lead ("1 of 6 VP+ roles in San Francisco this week")
- Added WoW deltas on velocity, geo, salary sections
- Added 4-week trend arrows
- Added sample email preview section to landing page
- Created Excel (.xlsx) and PDF one-pager attachment mockups
- Updated pricing features: "Excel workbook" and "PDF market intel one-pager"

### Round 2 (all implemented):
- "Avg Max Salary" → "Avg Salary" everywhere
- Added "Built for" label above audience badges
- Replaced "47 Companies Hiring" stat with "86% Growth Hires"
- Replaced ugly SVG US map with clean blurred geo preview card
- Removed junior researcher pricing comparison ("I always flinch at advertising how they could fire someone")
- Removed "501 search terms across 3 job boards" copy ("it's useless")
- Fixed email footer duplicate "VP+ Hiring Intelligence" text
- Fixed pricing subtitle (removed lingering junior researcher reference)

### User Decisions on Specific Features:
- **"Act Today" callout for recent leads:** REJECTED ("too hokey")
- **AI-generated one-liners:** NEEDS REVIEW (user wants to see examples first — current one-liners are factual/signal-derived, not AI summaries)
- **"Likely retained" indicator:** REJECTED ("too presumptive") — replaced with company size + public/private badges
- **WoW timeframes:** Weekly + 4-week trends (not 90-day or annual)
- **Geo data on landing page:** Blurred preview only (full data for paid subscribers)
- **Social proof:** Methodology-based credibility for now (no fake subscriber counts)

## Landing Page Best Practices Audit

Reference docs from the Verum website project (`/Users/rome/Documents/projects/verum-website/docs/`). These are battle-tested and should guide all ExecSignals copy and layout decisions.

### Source Files
| File | What It Covers |
|------|---------------|
| `docs/LANDING-PAGE-FORMULA.md` | Harry Dry's above/below fold framework — the primary structure reference |
| `docs/WRITING-GUIDELINES.md` | Voice rules, anti-AI-detection patterns, sentence rhythm |
| `docs/CONTENT-STRATEGY.md` | Curiosity hooks, case study structure, AI messaging traps |
| `docs/BRAND.md` | Value CTAs vs generic CTAs, banned marketing words, voice DO/DON'T |
| `CLAUDE.md` | Banned phrases list, blog opening rules, anti-AI-flag words |

### Landing Page Formula Mapping (Harry Dry)

**Above the fold — "earn attention":**

| Element | Formula Says | ExecSignals Current | Gap? |
|---------|-------------|-------------------|------|
| Title | Explain what you do (if unique), OR Value+Objection hook, OR own your niche | "Every VP+ growth hire. Scored. Ranked. Monday morning." | Strong — owns the niche. Works. |
| Subtitle | Introduce WHAT + HOW it delivers the promise | Long methodology explanation — needs rework | YES — currently explains the scoring process instead of the outcome. Should answer "what do I get and why should I care?" not "how does it work internally." Rework in next session. |
| Visual | Show the actual product — no stock photos | 4 real lead cards with scores, signals, salary | Good — the leads ARE the product visual |
| Social proof | Credibility metric above the fold | Stats bar (272 leads, $234K, 86% growth, 1-3 days) | Partial — these are product metrics, not social proof. No testimonials, no subscriber count, no "X firms use this." Acceptable pre-launch but flag for later. |
| CTA | "Call to value" not "Sign Up" — handle objections | "Send Me the Brief" + "Free sample week. No call." | Good — value CTA with objection handling |

**Below the fold — "earn the sale":**

| Element | Formula Says | ExecSignals Current | Gap? |
|---------|-------------|-------------------|------|
| Features/objections | Make value concrete using customers' words | Scoring methodology, signal distribution, market intel preview | PARTIAL — explains features but doesn't address objections. Missing: "Why not just use LinkedIn Recruiter?" (we have this section but it's far down), "Is this just scraped job boards?" |
| More social proof | Personas + quotes that inspire action | None | YES — no testimonials, no persona quotes. Pre-launch, so expected, but structure the page to drop them in later. |
| FAQ | Tie up loose ends | None on landing page | YES — missing entirely. Should address: data freshness, what "scored" means, cancellation, what's in the Excel, how signals are detected. |
| 2nd CTA | Remind why they're clicking, reinforce value | Bottom CTA box with email capture | Good — has it |
| Founder's note | Problem → ownership → happy ending | None | MAYBE — could add a short "I built this because..." but may not fit the premium intel brand. Discuss. |

### Writing Guidelines Gaps

From `WRITING-GUIDELINES.md` — things to fix in ExecSignals copy:

- **Em-dashes:** Currently used in pricing features ("Excel workbook — color-coded scores"). The Verum writing guide flags em-dashes as AI-detection triggers. Consider replacing with periods or restructuring.
- **Sentence rhythm:** Current subtitle is one long compound sentence. Guide says: vary dramatically (4-word punchy + 25-word flowing). The headline does this well. The subtitle doesn't.
- **"Would this help me sell if I met the customer in person?" test:** Apply this to every section. The scoring methodology section might be too inside-baseball for a first visit.

### Voice DO/DON'T (from `BRAND.md`)

**Applies directly to ExecSignals:**
- Use value CTAs: "Send Me the Brief" (good), NOT "Sign Up" or "Get Started"
- Use specific numbers: "272 VP+ leads" (good), "86% growth hires" (good)
- Problem-focused headlines: "What LinkedIn Recruiter Can't Tell You" (good)
- BANNED words to check for: "Unlock", "Unleash", "Empower", "Supercharge", "Revolutionary", "Game-changing", "Best-in-class", "Book a Demo"

### Content Strategy Patterns (from `CONTENT-STRATEGY.md`)

**Curiosity hook pattern** — useful for the subtitle rework:
- Formula: hint at the value without revealing the mechanism
- Example from Verum: "a single variable predicted a 4x increase in LTV" (not "RevOps team size predicted 4x LTV")
- For ExecSignals: the subtitle should create curiosity about what signals matter, not list them all upfront

**AI messaging trap:** Don't sacrifice authenticity for buzzwords. ExecSignals currently avoids this well — no "AI-powered" claims on the landing page.

### Priority Fixes — COMPLETED (Feb 2026)
1. ~~**Subtitle rework**~~ DONE — "LinkedIn tells you a role was posted. We tell you who it reports to, why it exists, and what it pays."
2. ~~**Add FAQ section**~~ DONE — 6 FAQs (freshness, scoring, data source, Excel contents, scraped boards objection, cancellation). Inserted between pricing and final CTA.
3. **Structure for future testimonials** — NOT DONE. Pre-launch, no real testimonials yet. Add slots later.
4. ~~**Check em-dash usage**~~ DONE — removed from pricing features (4), lead card notes (4), email preview subtitle (1).
5. ~~**Move "What LinkedIn Can't Tell You" higher**~~ DONE — moved from position 6 to position 2 (right after sample leads).
6. ~~**Section order**~~ DONE — new order: Sample Leads → Value Props → Market Intel → Email Preview → Signal Dist → Scoring → Pricing → FAQ → CTA.

### Additional Fixes Applied (Feb 2026)
- **Nav CTA:** "Get Started" → "Send Me the Brief" (value CTA per Harry Dry)
- **Value props subtitle:** Rewrote to avoid duplicating hero subtitle. Now: "Every lead in The Monday Brief comes with four layers of context you won't find in a LinkedIn Recruiter alert."
- **Market intel subtitle:** Rewrote to avoid duplicating value card copy. Now: "Updated weekly from real VP+ postings. Not salary surveys, not estimates."
- **"Signal Distribution" header:** Renamed to "This Week's Breakdown" (less inside-baseball)
- **Pricing button:** "Start with a free sample" → "Send Me a Free Brief" (value CTA)
- **Bottom CTA subtitle:** Feature list → "See what 272 scored VP+ leads look like in your inbox. Your first week is free."
- **Sample leads subtitle:** "Scored by seniority, signals, and salary budget" → "Four real leads from this week. Subscribers see all 272."
- **Scoring subtitle:** "Each qualifying lead starts at 10 points..." → "Transparent scoring across three dimensions. Every lead earns its rank."

### Still Outstanding
- **Testimonial slots** — structure for future social proof (Harry Dry #7)
- **Founder's note** — discuss if it fits the premium intel brand (Harry Dry #10)
- **`messaging.md`** — still references "Hot Leads Weekly", needs ExecSignals rebrand

## What's Next (Implementation Phase)

### Phase 2: Apply Mockups to Production Files
After user approves mockups in browser:

1. **Update production files with approved mockup designs:**
   - `index.html` — apply landing page mockup
   - `email_templates/weekly_delivery.html` — apply email mockup
   - `email_templates/welcome_email.html` — rebrand to ExecSignals
   - `email_templates/weekly_delivery.txt` — rebrand plaintext version
   - `generate_hot_leads.py` — update branding in generated content

2. **Add market analytics generation to `generate_hot_leads.py`:**
   - Salary benchmarks by function + seniority (from compensation_snapshots)
   - Market segment breakdown (from job_signals)
   - Hiring velocity by industry with WoW (from listing_snapshots)
   - Top hiring companies (from companies table)
   - Geo heatmap data (from jobs.location_metro)
   - Company stage analysis (from jobs.company_stage)
   - Stack trends (from job_tools)
   - Salary trend lines over 4-8 weeks (from compensation_snapshots time series)

3. **Add Excel generation** (openpyxl — color-coded scores, clickable URLs, auto-filters)

4. **Add PDF one-pager generation** (weasyprint or reportlab)

5. **Wire up Resend API** with `--send` flag + subscriber management (MVP: subscribers.json)

6. **Set up Stripe checkout** — single tier $297/mo

7. **Set up GitHub repo** for ExecSignals

8. **Deploy to execsignals.com**

9. **Update `messaging.md`** — still references "Hot Leads Weekly"

## Scoring System
- Base score: 10
- **Seniority:** C-Level +15, EVP +12, SVP +10, VP +5
- **Signals:** Reports to CEO +10, First Hire +8, Reports to CRO +6, Build Team +5, Growth Hire +4, Immediate +2
- **Salary:** $300K+ = +10, $200K+ = +7, $150K+ = +4, $100K+ = +2
- **Bonuses:** 3+ signals = +5, Growth-stage company = +2
- **Score tiers:** 40+ Exceptional (amber), 30-39 Strong (blue), 20-29 Solid (light amber), <20 Baseline (gray)

## Database
- **Local:** `/Users/rome/Documents/projects/scrapers/master/data/jobs.db`
- **Server:** `rome@100.91.208.46:~/scrapers/master/data/jobs.db`
- **29,237+ jobs**, 45 signal types, compensation_snapshots (time series), listing_snapshots, companies table
- **Key columns:** `seniority_tier`, `annual_salary_max`, `date_scraped`, `function_category`, `company_industry`, `company_stage`, `location_metro`

## Email Infrastructure
- **Sending:** Resend API (key in `data_prep_app/.env`)
- **Storage MVP:** `subscribers.json` on server
- **Storage later:** Resend Audiences API
- **Payment:** Stripe checkout, $297/mo
- **Delivery:** Cron on server, Monday 6 AM ET
- **Pattern:** Same as `generate_weekly_email.py` in AI Penetration Index project

## Key Files
```
/Users/rome/Documents/projects/products/hot-leads/
├── mockups/
│   ├── landing-page.html              # Landing page mockup (2 rounds of feedback applied)
│   ├── monday-brief-email.html        # Email mockup (2 rounds of feedback applied)
│   ├── ExecSignals_Feb17.xlsx         # Excel attachment mockup
│   ├── MarketIntel_Feb17.html         # PDF one-pager mockup
│   └── generate_execsignals_mockup.py # Excel generator script
├── email_templates/
│   ├── weekly_delivery.html           # Production email (not yet updated)
│   ├── welcome_email.html             # Production welcome email (not yet updated)
│   └── weekly_delivery.txt            # Production plaintext (not yet updated)
├── index.html                         # Production landing page (not yet updated)
├── generate_hot_leads.py              # Lead scoring + generation script (working, needs analytics)
├── messaging.md                       # Cold outreach copy (still says "Hot Leads Weekly")
├── sample-output/                     # Generated sample output from Feb 2026 run
├── subscribers.json                   # Subscriber storage (empty stub)
└── HANDOFF.md                         # This file
```

## Memory Files
- `/Users/rome/.claude/projects/-Users-rome/memory/execsignals.md` — detailed project memory
- `/Users/rome/.claude/plans/crystalline-mapping-sun.md` — original implementation plan
