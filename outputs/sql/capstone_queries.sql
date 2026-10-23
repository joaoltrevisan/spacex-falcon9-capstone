-- site_success
SELECT LaunchSite, COUNT(*) AS launches, ROUND(AVG(Class), 3) AS success_rate FROM launches GROUP BY LaunchSite ORDER BY success_rate DESC;

-- orbit_success
SELECT Orbit, COUNT(*) AS launches, ROUND(AVG(Class), 3) AS success_rate FROM launches GROUP BY Orbit ORDER BY success_rate DESC;

-- payload_by_success
SELECT Class, COUNT(*) AS launches, ROUND(AVG(PayloadMass), 1) AS mean_payload_kg FROM launches GROUP BY Class ORDER BY Class;

-- year_success
SELECT CAST(strftime('%Y', Date) AS INTEGER) AS year, COUNT(*) AS launches, SUM(Class) AS successful_launches, ROUND(AVG(Class), 3) AS success_rate FROM launches GROUP BY year ORDER BY year;
