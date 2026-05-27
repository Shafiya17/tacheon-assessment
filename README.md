# Task 2: Data Pipeline — Weather Data → BigQuery

## What This Does

A fully automated Python pipeline that:
1. Fetches daily weather data for 4 Indian cities from the Open-Meteo API
2. Cleans and transforms the raw response into a structured tabular format
3. Adds derived analytical fields
4. Loads the data into Google BigQuery

---

## Why Open-Meteo?

- **Free** — no API key, no credit card, no rate limit issues
- **Structured** — returns clean JSON with consistent field names
- **Relevant** — weather data is genuinely useful for marketing (campaign timing, regional targeting)
- **Reliable** — well-maintained public API with good uptime

---

## Project Structure

```
task2/
├── pipeline.py        # Main pipeline script
├── summary_query.sql  # SQL analytics queries
└── README.md          # This file
```

---

## How to Run

### Prerequisites
```bash
pip install requests pandas google-cloud-bigquery db-dtypes
```

### Run the pipeline
```bash
python pipeline.py
```

### With custom parameters
```bash
# Fetch 14 days of data
python pipeline.py --days 14

# Custom key path
python pipeline.py --key "C:\path\to\bq-key.json"
```

---

## BigQuery Setup

1. Go to [console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)
2. Sign in with Google account (free Sandbox — no credit card needed)
3. Note your Project ID: `prismatic-smoke-480516-k4`
4. Create a Service Account with BigQuery Admin role
5. Download the JSON key file
6. The pipeline auto-creates the dataset and table on first run

**Dataset:** `weather_pipeline`  
**Table:** `daily_weather`

---

## Schema

| Field | Type | Description |
|-------|------|-------------|
| date | DATE | Forecast date |
| city | STRING | City name |
| temp_max_c | FLOAT | Max temperature (°C) |
| temp_min_c | FLOAT | Min temperature (°C) |
| precipitation_mm | FLOAT | Total rainfall (mm) |
| windspeed_max_kmh | FLOAT | Max wind speed (km/h) |
| weathercode | INTEGER | WMO weather code |
| temp_avg_c | FLOAT | **Derived** — average temp |
| temp_range_c | FLOAT | **Derived** — temp swing (max - min) |
| weather_condition | STRING | **Derived** — human-readable condition |
| is_rainy | BOOLEAN | **Derived** — TRUE if rainfall > 1mm |
| ingested_at | TIMESTAMP | When pipeline ran |

---

## SQL Summary Query & Sample Output

```sql
SELECT
    city,
    ROUND(AVG(temp_avg_c), 2)        AS avg_temp_c,
    ROUND(MAX(temp_max_c), 2)        AS peak_temp_c,
    ROUND(SUM(precipitation_mm), 2)  AS total_rainfall_mm,
    COUNTIF(is_rainy = TRUE)         AS rainy_days,
    COUNT(*)                         AS total_days
FROM `prismatic-smoke-480516-k4.weather_pipeline.daily_weather`
GROUP BY city
ORDER BY avg_temp_c DESC;
```

**Actual Output (from live BigQuery run — 27 May 2026):**
| city | avg_temp_c | peak_temp_c | total_rainfall_mm | rainy_days | total_days |
|------|-----------|-------------|-------------------|------------|------------|
| Chennai | 32.94 | 40.2 | 8.0 | 3 | 7 |
| Delhi | 32.19 | 42.5 | 5.2 | 3 | 7 |
| Mumbai | 31.21 | 34.4 | 5.7 | 3 | 7 |
| Bangalore | 25.75 | 31.1 | 31.1 | 6 | 7 |

---

## Production Thinking (Step 5)

### How would you schedule this pipeline?
Use **Google Cloud Scheduler** to trigger a **Cloud Run Job** or **Cloud Function** daily at 6 AM IST. Alternatively, use **Apache Airflow** (Cloud Composer) for more complex orchestration with dependencies.

```
Cloud Scheduler (cron: 0 6 * * *)
    → triggers Cloud Run Job
        → runs pipeline.py
            → loads to BigQuery
```

### How would you know if it failed?
- **Logging:** All steps log to stdout; in production, pipe to **Google Cloud Logging**
- **Alerting:** Set up a **Cloud Monitoring alert** on job failure
- **Dead letter:** If load fails, write raw JSON to a **GCS bucket** for replay
- **Slack/email notification:** Use Cloud Functions to send alerts on failure

### What would you change for 10x data volume?
- Switch from `load_table_from_dataframe` to **streaming inserts** or **GCS-staged loads** for larger batches
- Add **partitioning** on the `date` column and **clustering** on `city` for query performance
- Use **pagination** on API calls if fetching longer date ranges
- Consider **Dataflow** (Apache Beam) for parallel city fetching instead of sequential
- Add **incremental loading** — only fetch and append new dates instead of full reload (WRITE_TRUNCATE → WRITE_APPEND with deduplication)
