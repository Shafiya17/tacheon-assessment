"""
Marketing Data Pipeline - Task 2
API: Open-Meteo (free, no API key required)
Fetches weather data, transforms it, and loads to BigQuery.
"""

import requests
import pandas as pd
import logging
import argparse
from datetime import datetime, timedelta
from google.cloud import bigquery
import os
import sys

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
PROJECT_ID  = "prismatic-smoke-480516-k4"
DATASET_ID  = "weather_pipeline"
TABLE_ID    = "daily_weather"

API_URL = "https://api.open-meteo.com/v1/forecast"

# Cities to track (marketing-relevant markets)
CITIES = [
    {"name": "Chennai",   "latitude": 13.08,  "longitude": 80.27},
    {"name": "Mumbai",    "latitude": 19.07,  "longitude": 72.87},
    {"name": "Delhi",     "latitude": 28.61,  "longitude": 77.20},
    {"name": "Bangalore", "latitude": 12.97,  "longitude": 77.59},
]

# ── Step 1: Fetch ───────────────────────────────────────────────────────────────
def fetch_weather(city: dict, days: int = 7) -> dict:
    """Fetch daily weather data for a city from Open-Meteo API."""
    params = {
        "latitude":        city["latitude"],
        "longitude":       city["longitude"],
        "daily":           [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "weathercode"
        ],
        "timezone":        "Asia/Kolkata",
        "forecast_days":   days,
    }
    log.info(f"Fetching weather for {city['name']} ...")
    try:
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        log.info(f"  ✓ Received {len(data['daily']['time'])} days of data for {city['name']}")
        return data
    except requests.exceptions.Timeout:
        log.error(f"  ✗ Timeout fetching data for {city['name']}")
        return None
    except requests.exceptions.HTTPError as e:
        log.error(f"  ✗ HTTP error for {city['name']}: {e}")
        return None
    except Exception as e:
        log.error(f"  ✗ Unexpected error for {city['name']}: {e}")
        return None


# ── Step 2: Transform ───────────────────────────────────────────────────────────
def transform(raw: dict, city_name: str) -> pd.DataFrame:
    """Flatten raw API response into a clean tabular DataFrame."""
    if not raw or "daily" not in raw:
        log.warning(f"No data to transform for {city_name}")
        return pd.DataFrame()

    daily = raw["daily"]

    df = pd.DataFrame({
        "date":         daily.get("time", []),
        "city":         city_name,
        "temp_max_c":   daily.get("temperature_2m_max", []),
        "temp_min_c":   daily.get("temperature_2m_min", []),
        "precipitation_mm": daily.get("precipitation_sum", []),
        "windspeed_max_kmh": daily.get("windspeed_10m_max", []),
        "weathercode":  daily.get("weathercode", []),
    })

    # Handle nulls
    df["temp_max_c"]        = pd.to_numeric(df["temp_max_c"],        errors="coerce")
    df["temp_min_c"]        = pd.to_numeric(df["temp_min_c"],        errors="coerce")
    df["precipitation_mm"]  = pd.to_numeric(df["precipitation_mm"],  errors="coerce").fillna(0)
    df["windspeed_max_kmh"] = pd.to_numeric(df["windspeed_max_kmh"], errors="coerce")
    df["weathercode"]       = pd.to_numeric(df["weathercode"],       errors="coerce").fillna(0).astype(int)

    # ── Derived fields ──────────────────────────────────────────────────────────
    # 1. Average temperature
    df["temp_avg_c"] = ((df["temp_max_c"] + df["temp_min_c"]) / 2).round(2)

    # 2. Temperature range (heat stress indicator)
    df["temp_range_c"] = (df["temp_max_c"] - df["temp_min_c"]).round(2)

    # 3. Human-readable weather condition
    df["weather_condition"] = df["weathercode"].apply(decode_weathercode)

    # 4. Is it a rainy day? (useful for marketing campaign timing)
    df["is_rainy"] = df["precipitation_mm"] > 1.0

    # 5. Ingestion timestamp
    df["ingested_at"] = datetime.utcnow()

    # Date as datetime (BigQuery DATE compatible)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    log.info(f"  ✓ Transformed {len(df)} rows for {city_name}")
    return df


def decode_weathercode(code: int) -> str:
    """Decode WMO weather code to human-readable string."""
    mapping = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
        61: "Light rain", 63: "Rain", 65: "Heavy rain",
        71: "Light snow", 73: "Snow", 75: "Heavy snow",
        80: "Rain showers", 81: "Heavy showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail",
    }
    return mapping.get(code, f"Unknown ({code})")


# ── Step 3: Load to BigQuery ────────────────────────────────────────────────────
def load_to_bigquery(df: pd.DataFrame, key_path: str):
    """Load transformed DataFrame into BigQuery."""
    if df.empty:
        log.warning("Empty DataFrame — nothing to load.")
        return

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path
    client = bigquery.Client(project=PROJECT_ID)

    # Create dataset if it doesn't exist
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    dataset_ref.location = "US"
    try:
        client.create_dataset(dataset_ref, exists_ok=True)
        log.info(f"  ✓ Dataset `{DATASET_ID}` ready")
    except Exception as e:
        log.error(f"  ✗ Could not create dataset: {e}")
        return

    # Define schema
    schema = [
        bigquery.SchemaField("date",               "DATE"),
        bigquery.SchemaField("city",               "STRING"),
        bigquery.SchemaField("temp_max_c",         "FLOAT"),
        bigquery.SchemaField("temp_min_c",         "FLOAT"),
        bigquery.SchemaField("precipitation_mm",   "FLOAT"),
        bigquery.SchemaField("windspeed_max_kmh",  "FLOAT"),
        bigquery.SchemaField("weathercode",        "INTEGER"),
        bigquery.SchemaField("temp_avg_c",         "FLOAT"),
        bigquery.SchemaField("temp_range_c",       "FLOAT"),
        bigquery.SchemaField("weather_condition",  "STRING"),
        bigquery.SchemaField("is_rainy",           "BOOLEAN"),
        bigquery.SchemaField("ingested_at",        "TIMESTAMP"),
    ]

    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    job_config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    log.info(f"Loading {len(df)} rows to BigQuery table `{TABLE_ID}` ...")
    try:
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        job.result()
        log.info(f"  ✓ Successfully loaded {len(df)} rows to {table_ref}")
    except Exception as e:
        log.error(f"  ✗ BigQuery load failed: {e}")
        raise


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Weather Data Pipeline")
    parser.add_argument("--days",    type=int, default=7,    help="Number of forecast days (1-16)")
    parser.add_argument("--key",     type=str, default=r"C:\Users\Shafiya\Downloads\bq-key.json", help="Path to BigQuery service account key")
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("  Weather Data Pipeline — Starting")
    log.info(f"  Fetching {args.days} days of data for {len(CITIES)} cities")
    log.info("=" * 60)

    all_frames = []

    for city in CITIES:
        raw  = fetch_weather(city, days=args.days)
        df   = transform(raw, city["name"])
        if not df.empty:
            all_frames.append(df)

    if not all_frames:
        log.error("No data fetched from any city. Exiting.")
        sys.exit(1)

    combined = pd.concat(all_frames, ignore_index=True)
    log.info(f"\nTotal rows ready to load: {len(combined)}")

    load_to_bigquery(combined, key_path=args.key)

    log.info("\n" + "=" * 60)
    log.info("  Pipeline completed successfully!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
