SELECT
    target_path,
    tab_url,
    referrer,
    start_time
FROM downloads
WHERE target_path LIKE '%' || :filename
ORDER BY start_time;
