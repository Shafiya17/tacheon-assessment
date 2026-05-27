# Product Brief: Marketing Performance Intelligence Tool (MPIT)

## Problem Statement

The marketing technology team constantly faces one recurring question from both internal analysts and clients:

> *"How is our marketing performing across channels right now, and where should we be focusing?"*

Today, answering this takes:
- Manual digging across multiple tools (Google Ads, Meta, email platforms, etc.)
- 30–60 minutes of someone's time per request
- Inconsistent outputs depending on who answers it
- A single point of failure — if that person is unavailable, the question goes unanswered

---

## The Tool: What It Is

**Name:** MPIT — Marketing Performance Intelligence Tool  
**Type:** Internal web dashboard (lightweight, read-only)  
**Format:** A single-page view that loads automatically with pre-aggregated channel data

This is NOT a replacement for any existing tool. It sits on top of the data those tools already produce and presents it in one place, in a consistent format, every time.

---

## Primary User

**Internal Marketing Analyst / Account Manager**

The client is NOT the primary user in v1. Here's why:

- Clients have different contexts, expectations, and levels of data literacy
- Building for two audiences at once in v1 would force compromises on both
- The internal team is the bottleneck right now — fixing their workflow first delivers the most immediate value
- If the internal tool works well, a client-facing version becomes a natural v2

---

## What a Successful Interaction Looks Like

A user opens the tool, selects a client brand and a date range, and within 10 seconds sees:

1. **Channel-level performance summary** — spend, impressions, clicks, conversions per channel (paid social, paid search, email, organic)
2. **A simple highlight** — which channel is over/underperforming against its own recent baseline
3. **A recommended focus area** — one plain-language sentence: *"Paid Search is delivering 2.3x the conversion rate of Paid Social this week. Consider reallocating budget."*

The user walks away knowing:
- What is working and what is not, right now
- Which channel deserves attention
- A consistent answer they can share with a client in under 2 minutes

---

## Data Requirements

| Data Needed | Source | How It Gets There |
|-------------|--------|-------------------|
| Paid Social metrics | Meta Ads Manager | Manual CSV export (v1) or Meta API (v2) |
| Paid Search metrics | Google Ads | Manual CSV export (v1) or Google Ads API (v2) |
| Email metrics | Mailchimp / Klaviyo | Manual CSV export (v1) or API (v2) |
| Organic/SEO | Google Search Console | Manual CSV export (v1) or API (v2) |

**v1 Data Strategy:** Manual CSV upload by the analyst once per week (or as needed). This removes the tool dependency issue and lets us validate the display layer first before automating ingestion.

This is a deliberate trade-off — the team won't change their tools or workflows, so v1 meets them where they are.

---

## v1 Scope: What's In

- [ ] Client brand selector (dropdown)
- [ ] Date range picker (last 7 days, last 30 days, custom)
- [ ] Channel performance table (spend, clicks, conversions, CPA, ROAS)
- [ ] Simple highlight: best and worst performing channel this period
- [ ] One derived insight line (rule-based, not AI in v1)
- [ ] CSV upload interface for data ingestion
- [ ] Data freshness indicator (shows when data was last updated)

---

## v1 Scope: What's Explicitly OUT (and Why)

| Feature | Why It's Out of v1 |
|--------|---------------------|
| Client-facing view | Adds UX complexity, auth, and data sensitivity concerns |
| Automated API ingestion | Requires API credentials, maintenance, and error handling — validate the display layer first |
| AI-generated recommendations | Rule-based insights are faster to build, easier to audit, and sufficient for v1 |
| Historical trend charts | Useful but not essential for answering the core question |
| Alerts / notifications | Nice-to-have, not the bottleneck being solved |
| Multi-user access control | Single internal team, not needed yet |
| Mobile optimisation | This is a desktop analyst tool |

---

## What Makes Users Trust It

1. **Data freshness label** — always show when the data was last uploaded. Never show stale data without warning.
2. **Source transparency** — show which file/source each channel's data came from
3. **No black boxes** — the derived insight line shows the numbers it's based on, not just a conclusion
4. **Consistent layout** — same structure every time, regardless of who opens it

---

## What It Would Need to Work (Technical)

- A simple web frontend (React or plain HTML)
- A lightweight backend or serverless function to process uploaded CSVs
- A small database or file store to persist the processed data between sessions
- No external API integrations in v1 — all data comes in via upload

Hosting: Internal (not public-facing). Could run on a simple cloud VM or even locally on a shared machine to start.

---

## What I Would Revisit With More Time

1. **User interviews first** — I've made assumptions about what "channel performance" means to this team. I'd spend a day talking to 2–3 actual users before finalising the metrics shown.
2. **Automate one channel's ingestion** — after validating the display layer, I'd prioritise automating the highest-volume data source first (likely Google Ads or Meta).
3. **Define "good" per channel** — the highlight logic needs agreed benchmarks. Without those, the tool can show numbers but can't say what they mean.
4. **Consider Looker Studio or Metabase** — if the team already uses these, a custom build may not be the right call. I'd validate that first before writing a line of code.
