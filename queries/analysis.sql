-- Sample analytics queries for the agri-data-pipeline-analytics project.

-- 1. Total fact rows
SELECT
    COUNT(*) AS total_rows
FROM fact_crop_performance;

-- 2. Average yield by region
SELECT
    region,
    AVG(yield_kg_per_hectare) AS average_yield_kg_per_hectare
FROM fact_crop_performance
GROUP BY region
ORDER BY region;

-- 3. Top regions by total estimated yield
SELECT
    region,
    SUM(total_yield_estimate) AS total_estimated_yield
FROM fact_crop_performance
GROUP BY region
ORDER BY total_estimated_yield DESC
LIMIT 5;

-- 4. Yield trend over time
SELECT
    date,
    AVG(yield_kg_per_hectare) AS average_yield_kg_per_hectare
FROM fact_crop_performance
GROUP BY date
ORDER BY date;

-- 5. Crop performance by crop and region
SELECT
    crop_name,
    region,
    AVG(yield_kg_per_hectare) AS average_yield_kg_per_hectare,
    SUM(area_hectares) AS total_area_hectares,
    SUM(total_yield_estimate) AS total_estimated_yield
FROM fact_crop_performance
GROUP BY crop_name, region
ORDER BY crop_name, total_estimated_yield DESC;

-- 6. Weather and yield comparison by region
SELECT
    region,
    AVG(yield_kg_per_hectare) AS average_yield_kg_per_hectare,
    AVG(temperature_2m_max) AS average_max_temperature,
    AVG(temperature_2m_min) AS average_min_temperature,
    AVG(precipitation_sum) AS average_precipitation,
    AVG(rainfall_sum) AS average_rainfall
FROM fact_crop_performance
GROUP BY region
ORDER BY average_yield_kg_per_hectare DESC;
