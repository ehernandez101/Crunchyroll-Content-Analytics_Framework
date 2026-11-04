-- Lift by exposure tier. NOTE: total_ads is measured after assignment, so tiers are
-- descriptive (who saw how much), not a randomized split.
WITH t AS (
    SELECT CASE WHEN total_ads <= 10  THEN 1
                WHEN total_ads <= 25  THEN 2
                WHEN total_ads <= 50  THEN 3
                WHEN total_ads <= 100 THEN 4
                ELSE 5 END AS tier_order,
           test_group, converted
    FROM marketing_ab
), g AS (
    SELECT tier_order,
           SUM(CASE WHEN test_group = 'ad'  THEN 1 ELSE 0 END)         AS n_ad,
           SUM(CASE WHEN test_group = 'ad'  THEN converted ELSE 0 END) AS x_ad,
           SUM(CASE WHEN test_group = 'psa' THEN 1 ELSE 0 END)         AS n_psa,
           SUM(CASE WHEN test_group = 'psa' THEN converted ELSE 0 END) AS x_psa
    FROM t GROUP BY tier_order
), r AS (
    SELECT tier_order, n_ad, n_psa,
           1.0 * x_ad / n_ad AS p_ad, 1.0 * x_psa / n_psa AS p_psa,
           n_ad * (1.0 * x_ad / n_ad - 1.0 * x_psa / n_psa) AS incremental_conv
    FROM g
)
SELECT CASE tier_order WHEN 1 THEN '1-10' WHEN 2 THEN '11-25' WHEN 3 THEN '26-50'
                       WHEN 4 THEN '51-100' ELSE '101+' END                   AS tier,
       ROUND(100.0 * p_ad, 2)                                                 AS conv_ad_pct,
       ROUND(100.0 * p_psa, 2)                                                AS conv_holdout_pct,
       ROUND(100.0 * (p_ad - p_psa), 2)                                       AS lift_pts,
       ROUND(incremental_conv)                                                AS incremental_conv,
       ROUND(100.0 * incremental_conv / SUM(incremental_conv) OVER (), 1)     AS share_of_incremental_pct,
       ROUND(100.0 * p_psa / p_ad, 1)                                         AS pct_would_have_converted_anyway
FROM r ORDER BY tier_order;
