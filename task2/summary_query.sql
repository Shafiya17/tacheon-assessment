-- ============================================================
-- Summary Query: Weather Pipeline Analytics
-- Table: prismatic-smoke-480516-k4.weather_pipeline.daily_weather
-- ============================================================

-- 1. Average temperature and total rainfall per city
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


-- 2. Hottest day per city
SELECT
    city,
    date,
    temp_max_c,
    weather_condition
FROM `prismatic-smoke-480516-k4.weather_pipeline.daily_weather`
WHERE temp_max_c = (
    SELECT MAX(temp_max_c)
    FROM `prismatic-smoke-480516-k4.weather_pipeline.daily_weather` t2
    WHERE t2.city = daily_weather.city
)
ORDER BY temp_max_c DESC;


-- 3. Days with rain by city (useful for campaign timing)
SELECT
    date,
    city,
    precipitation_mm,
    weather_condition
FROM `prismatic-smoke-480516-k4.weather_pipeline.daily_weather`
WHERE is_rainy = TRUE
ORDER BY date, city;
