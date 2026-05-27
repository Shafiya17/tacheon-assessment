# Task 1: Product Scoping — Marketing Performance Intelligence Tool

## What This Folder Contains

| File | Description |
|------|-------------|
| `PRODUCT_BRIEF.md` | Full product scoping document — problem, users, v1 scope, trade-offs |
| `wireframe.html` | Interactive wireframe of the tool's main dashboard view |
| `README.md` | This file — decisions and thinking walkthrough |

---

## My Thinking Process

### The core insight I started with

The problem isn't that data doesn't exist. The data exists — it's sitting in Google Ads, Meta, email platforms. The problem is that pulling it together is manual, slow, and person-dependent.

So the tool doesn't need to collect new data. It needs to **present existing data in one consistent place.**

That reframe changed how I scoped v1 significantly.

---

### The user decision

I chose to scope for **internal analysts only** in v1, not clients.

The instinct might be to build for both — but that's how tools become overcomplicated. The internal team is the actual bottleneck. If they can answer the question in under 2 minutes instead of 45, the client experience improves automatically. Client-facing features are a v2 problem.

---

### The data ingestion decision

The brief says: *"The team is not going to change the tools they use or the way they currently work."*

That constraint actually simplifies v1. I didn't scope automated API integrations — those require credentials, maintenance, and error handling. Instead, v1 uses **CSV uploads**. The analyst already exports CSVs. We just give them a better place to put them.

This lets us validate whether the display and insight layer is actually useful before spending engineering time on automation.

---

### What I deliberately left out

- AI-generated recommendations (rule-based is sufficient and more auditable for v1)
- Client-facing views (separate audience, separate product)
- Automated data ingestion (validate the UI first)
- Alerts and trend charts (not the core question being answered)

---

### Where I had to make calls without full information

- **What metrics matter most?** I assumed standard digital marketing KPIs (spend, clicks, conversions, CPA, ROAS). In reality, I'd validate this with the team first.
- **What counts as "underperforming"?** The highlight logic needs agreed benchmarks per channel. I've scoped the feature but flagged that the thresholds need defining.
- **Does a custom build even make sense?** Tools like Looker Studio or Metabase might already solve this. I'd check before building.

---

### What I would do with more time

1. **Talk to 2–3 actual users** before finalising the scope
2. **Define benchmark logic** for the insight line
3. **Prototype and test the highlight feature** — is "best/worst channel" actually the right framing?
4. **Evaluate off-the-shelf tools** (Looker Studio, Metabase, Notion dashboards) before committing to a custom build
