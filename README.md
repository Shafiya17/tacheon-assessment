# Tacheon Assessment — Data & AI Product Engineer

**Candidate:** Shafiya D  
**Submitted:** May 2026  
**Repo:** github.com/Shafiya17/tacheon-assessment

---

## Repository Structure

```
tacheon-assessment/
├── task1/                  # Product Scoping
│   ├── PRODUCT_BRIEF.md    # Full product scoping document
│   ├── wireframe.html      # Interactive dashboard wireframe
│   └── README.md           # Decision walkthrough
│
└── task2/                  # Pipeline Building
    ├── pipeline.py         # Main Python pipeline script
    ├── summary_query.sql   # BigQuery SQL analytics queries
    └── README.md           # Setup and production thinking
```

---

## Task 1: Product Scoping

Scoped an internal marketing performance tool (MPIT) that answers: *"How is our marketing performing across channels right now, and where should we be focusing?"*

Key decisions:
- Primary user: internal analyst (not client) in v1
- Data ingestion: CSV upload in v1, API automation in v2
- v1 focuses on display and insight layer, not automation

→ See `task1/` for full brief, wireframe, and reasoning

---

## Task 2: Pipeline Building

Built a complete Python data pipeline:
- **API:** Open-Meteo (free, no key required)
- **Data:** 7-day weather forecast for 4 Indian cities
- **Transform:** Derived fields — avg temp, temp range, weather condition, rainy day flag
- **Storage:** Google BigQuery (Sandbox)
- **Result:** 28 rows loaded successfully

→ See `task2/` for code, SQL queries, and production thinking
