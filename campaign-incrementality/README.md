# Campaign Incrementality Readout: What Did the Campaign Actually Cause?

Independent portfolio project. Not affiliated with or endorsed by Crunchyroll, Sony, or Aniplex.
This is a **method demonstration** on a public advertising dataset. It is not Crunchyroll data.

**Live dashboard:** [Crunchyroll campaign incrementality on Tableau Public](https://public.tableau.com/app/profile/enrique.hernandez2674/viz/CrunchyRoll/Dashboard1)

## Business question

When a lifecycle campaign is shown to users, how many of the conversions credited to it were actually *caused* by it, and where should it be focused? (A streaming engagement team asks the same question about re-engagement messages and recommendations.)

## Headline findings

1. **About 3 in 10 credited conversions were caused by the campaign.** The ad group converted 2.555% vs. 1.785% for the holdout, a lift of +0.77 points (95% CI +0.60 to +0.94). Of 14,423 conversions in the ad group, about 4,343 (30%, range 23% to 37%) were incremental. The rest would have happened anyway.
2. **The effect is concentrated.** Users with more than 50 impressions are 11.7% of users but produce about 86% of the incremental conversions. Users with 25 or fewer impressions (73% of users, 27.5% of impressions) show no measurable lift.
3. **Looking only at the ad group misleads.** Heavy users convert a lot with or without the campaign. At 101+ impressions, about 69% of conversions would have happened anyway.
4. **The holdout is too small to read segments.** At 4% of users, an 80,000-user segment can only detect lifts of about 0.67 points or more; at 10% it is about 0.44. Day-of-week results are exploratory (seven unadjusted cuts) and are not reported as findings.

## Data

| Data | Source | License | Used for |
|---|---|---|---|
| Marketing A/B testing (588,101 users) | Kaggle, faviovaz | CC0 (public domain) | Incrementality readout |

## Method

- **Design:** 564,577 users saw the campaign; 23,524 were held out and saw a public-service announcement. The roughly 96/4 split looks deliberate, so the usual 50/50 sample-ratio check does not apply. Instead I checked that the arms look alike on day, hour, and impressions.
- **Lift:** difference in conversion rate with a 95% confidence interval (normal approximation).
- **Incremental conversions:** conversions in the ad group minus the holdout rate times the ad-group size.
- **Robustness:** the arms differ slightly in day, hour, and impression mix (Cramer's V about 0.02, statistically detectable at this size). Re-weighting the holdout to the ad group's mix gives a lift of 0.762 points vs. 0.769 unadjusted, so the result does not depend on the imbalance.
- **Tiers:** users are grouped by impressions seen (1-10, 11-25, 26-50, 51-100, 101+).

## Limitations

- Impressions are measured after assignment, so the tier results are descriptive, not a randomized comparison.
- Day and hour are also recorded after exposure, so differences between arms may partly be an effect of the campaign.
- One outcome (conversion), no dates, no revenue, no cost. No dollar figure is claimed. The calculator on the dashboard uses user-entered, illustrative inputs.
- This is an advertising dataset, not streaming engagement data. It shows the method, not Crunchyroll's results.
- Segment cuts beyond the tiers are underpowered at a 4% holdout.

## What I did

I built this project to answer a question that conversion rates alone can't: how many conversions did the advertising campaign actually cause? The ad group converted at 2.56% compared with 1.79% for the holdout, meaning only about 3 in 10 conversions credited to the campaign were incremental. Before trusting that result, I investigated the uneven 96/4 group split and checked whether the groups were reasonably balanced. Just 11.7% of users, those with 51 or more impressions, accounted for about 86% of estimated incremental conversions. Among the heaviest users (101+ impressions), about 69% of conversions would have happened anyway. This stood out to me because looking only at ad-group conversions would have overstated the campaign's impact.

I built the interactive Tableau dashboard and its parameter-driven value calculator to explore the business implications without making unsupported claims about actual dollar savings or day-of-week effects. I used Claude to help develop the Python and SQL analysis, ran the analysis and checked the outputs myself. With actual campaign revenue and cost data, I would calculate incremental profitability to determine whether the campaign was worth the investment.

## Repo contents

```
campaign-incrementality/
├── README.md
├── analysis/07_marketing_ab_readout.py   # lift, CI, incremental conversions, balance checks
├── sql/                                  # three queries, same results as the script
│   ├── 01_overall_incrementality.sql
│   ├── 02_exposure_tier_lift.sql
│   └── 03_impressions_by_tier.sql
└── outputs/                              # aggregate tables behind the dashboard
    ├── kpis.csv
    ├── attribution_split.csv
    ├── tier_lift.csv
    ├── day_lift.csv
    ├── balance_checks.csv
    └── holdout_planning.csv
```

The raw dataset is not included. Download it from the Kaggle listing above.

## Reproduce

1. Download the dataset from the Kaggle listing named above.
2. From this folder: `python -I analysis/07_marketing_ab_readout.py --data marketing_AB.csv --out outputs` (on Windows, `py -I ...`). Needs pandas, numpy and scipy.
3. Run the SQL files against a table `marketing_ab(user_id, test_group, converted, total_ads, most_ads_day, most_ads_hour)`. Load `converted` as 1/0.

## Disclaimer

Crunchyroll is a trademark of Crunchyroll, LLC. This project is independent and uses only public data.
