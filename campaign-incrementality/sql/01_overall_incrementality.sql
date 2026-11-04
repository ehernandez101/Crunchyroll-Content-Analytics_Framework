-- Overall campaign-vs-holdout result and how many conversions the campaign actually caused.
-- Table: marketing_ab(user_id, test_group, converted, total_ads, most_ads_day, most_ads_hour)
--   test_group: 'ad' = saw the campaign, 'psa' = holdout (saw a public-service announcement)
--   converted : 1 or 0 (convert 'True'/'False' text to 1/0 when loading)
WITH s AS (
    SELECT SUM(CASE WHEN test_group = 'ad'  THEN 1 ELSE 0 END)         AS n_ad,
           SUM(CASE WHEN test_group = 'ad'  THEN converted ELSE 0 END) AS x_ad,
           SUM(CASE WHEN test_group = 'psa' THEN 1 ELSE 0 END)         AS n_psa,
           SUM(CASE WHEN test_group = 'psa' THEN converted ELSE 0 END) AS x_psa
    FROM marketing_ab
)
SELECT n_ad, n_psa,
       ROUND(100.0 * x_ad  / n_ad,  3)                              AS conv_rate_ad_pct,
       ROUND(100.0 * x_psa / n_psa, 3)                              AS conv_rate_holdout_pct,
       ROUND(100.0 * (1.0 * x_ad / n_ad - 1.0 * x_psa / n_psa), 3)  AS lift_pts,
       x_ad                                                         AS conversions_in_ad_group,
       ROUND(1.0 * x_psa / n_psa * n_ad)                            AS would_have_converted_anyway,
       ROUND(x_ad - 1.0 * x_psa / n_psa * n_ad)                     AS incremental_conversions,
       ROUND(100.0 * (x_ad - 1.0 * x_psa / n_psa * n_ad) / x_ad, 1) AS incremental_share_pct
FROM s;
