-- Where the ad impressions went (ad group only), by the same exposure tiers.
WITH t AS (
    SELECT CASE WHEN total_ads <= 10  THEN 1 WHEN total_ads <= 25 THEN 2
                WHEN total_ads <= 50  THEN 3 WHEN total_ads <= 100 THEN 4 ELSE 5 END AS tier_order,
           total_ads
    FROM marketing_ab WHERE test_group = 'ad'
)
SELECT CASE tier_order WHEN 1 THEN '1-10' WHEN 2 THEN '11-25' WHEN 3 THEN '26-50'
                       WHEN 4 THEN '51-100' ELSE '101+' END AS tier,
       COUNT(*)                                             AS users,
       SUM(total_ads)                                       AS impressions,
       ROUND(100.0 * SUM(total_ads) / SUM(SUM(total_ads)) OVER (), 1) AS impressions_share_pct
FROM t GROUP BY tier_order ORDER BY tier_order;
