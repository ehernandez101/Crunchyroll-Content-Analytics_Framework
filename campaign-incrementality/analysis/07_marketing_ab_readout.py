"""
Campaign-vs-holdout incrementality readout (method demonstration on a public dataset).

Input : marketing_AB.csv  (Kaggle, faviovaz 'Marketing A/B testing', CC0 public domain)
        columns: user id, test group (ad|psa), converted, total ads, most ads day, most ads hour
Output: CSV summary tables only (small, aggregate).

Design notes
  - 'psa' is the holdout: users who saw a public-service announcement instead of the ad.
  - The ~96/4 split looks deliberate, so the usual 50/50 sample-ratio check does not apply.
    We instead check that arms look alike on pre-existing traits (day, hour, impressions).
  - 'total ads' is measured AFTER assignment. Cutting results by it conditions on a
    post-treatment variable, so tier results are descriptive and are labelled as such.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

Z, ZB = 1.96, 0.8416          # 95% two-sided, 80% power

def diff_ci(x1, n1, x0, n0):
    p1, p0 = x1 / n1, x0 / n0
    d = p1 - p0
    se = np.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
    return p1, p0, d, d - Z * se, d + Z * se, 2 * (1 - stats.norm.cdf(abs(d / se)))

def mde(p, n_treat, n_ctrl):
    """Smallest absolute lift detectable with 80% power at 5% significance."""
    return (Z + ZB) * np.sqrt(p * (1 - p) * (1 / n_treat + 1 / n_ctrl))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)

    m = pd.read_csv(a.data).rename(columns={"user id": "user_id", "test group": "grp",
                                            "total ads": "total_ads", "most ads day": "day",
                                            "most ads hour": "hour"})
    m["conv"] = m.converted.astype(int)
    assert m.user_id.is_unique and m.isna().sum().sum() == 0
    ad, ps = m[m.grp == "ad"], m[m.grp == "psa"]
    n1, n0, x1, x0 = len(ad), len(ps), ad.conv.sum(), ps.conv.sum()

    # 1. Headline + how many conversions were actually caused by the campaign
    p1, p0, d, lo, hi, p = diff_ci(x1, n1, x0, n0)
    would_have = p0 * n1                     # conversions expected with no campaign
    inc = x1 - would_have
    kp = pd.DataFrame([
        ("users_ad", n1), ("users_holdout", n0), ("conv_rate_ad_pct", round(100 * p1, 3)),
        ("conv_rate_holdout_pct", round(100 * p0, 3)), ("lift_pts", round(100 * d, 3)),
        ("lift_ci_low_pts", round(100 * lo, 3)), ("lift_ci_high_pts", round(100 * hi, 3)),
        ("relative_lift_pct", round(100 * d / p0, 1)), ("p_value", p),
        ("conversions_in_ad_group", int(x1)), ("conversions_without_campaign_est", round(would_have)),
        ("incremental_conversions_est", round(inc)),
        ("incremental_share_of_conversions_pct", round(100 * inc / x1, 1)),
        ("incremental_share_ci_low_pct", round(100 * n1 * lo / x1, 1)),
        ("incremental_share_ci_high_pct", round(100 * n1 * hi / x1, 1)),
        ("incremental_conv_per_1000_users", round(1000 * d, 2)),
    ], columns=["metric", "value"])
    kp.to_csv(a.out / "kpis.csv", index=False)
    pd.DataFrame({"category": ["Caused by the campaign", "Would have converted anyway"],
                  "conversions": [round(inc), round(would_have)]}).to_csv(a.out / "attribution_split.csv", index=False)

    # 2. Engagement tiers (descriptive; tiers use post-assignment impressions)
    bins = [0, 10, 25, 50, 100, 10**6]
    labels = ["1-10", "11-25", "26-50", "51-100", "101+"]
    m["tier"] = pd.cut(m.total_ads, bins, labels=labels)
    rows = []
    for t, g in m.groupby("tier", observed=True):
        a_, b_ = g[g.grp == "ad"], g[g.grp == "psa"]
        p1t, p0t, dt, lot, hit, pt = diff_ci(a_.conv.sum(), len(a_), b_.conv.sum(), len(b_))
        rows.append(dict(tier=t, users=len(g), pct_of_users=100 * len(g) / len(m),
                         n_ad=len(a_), n_holdout=len(b_), conv_ad_pct=100 * p1t,
                         conv_holdout_pct=100 * p0t, lift_pts=100 * dt,
                         ci_low_pts=100 * lot, ci_high_pts=100 * hit, p_value=pt,
                         incremental_conv=len(a_) * dt,
                         pct_would_have_converted_anyway=100 * p0t / p1t if p1t else np.nan,
                         mde_pts=100 * mde(p0t, len(a_), len(b_))))
    tr = pd.DataFrame(rows)
    tr["share_of_incremental_pct"] = 100 * tr.incremental_conv / tr.incremental_conv.sum()
    imp = ad.assign(tier=pd.cut(ad.total_ads, bins, labels=labels)).groupby("tier", observed=True).total_ads.sum()
    tr["impressions_share_pct"] = (100 * imp / imp.sum()).reindex(tr.tier).values
    tr.round(4).to_csv(a.out / "tier_lift.csv", index=False)

    # 3. Day of week (shows what the holdout is and is not powered to say)
    rows = []
    for dname, g in m.groupby("day"):
        a_, b_ = g[g.grp == "ad"], g[g.grp == "psa"]
        _, p0d, dd, lod, hid, pd_ = diff_ci(a_.conv.sum(), len(a_), b_.conv.sum(), len(b_))
        rows.append(dict(day=dname, n_ad=len(a_), n_holdout=len(b_), lift_pts=100 * dd,
                         ci_low_pts=100 * lod, ci_high_pts=100 * hid,
                         mde_pts=100 * mde(p0d, len(a_), len(b_))))
    pd.DataFrame(rows).round(3).to_csv(a.out / "day_lift.csv", index=False)

    # 4. Balance checks. Statistical tests are overpowered at ~588k users, so report
    #    effect sizes too, and test whether adjusting for any imbalance changes the lift.
    def cramers_v(ct):
        chi2 = stats.chi2_contingency(ct)[0]
        return np.sqrt(chi2 / (ct.values.sum() * (min(ct.shape) - 1)))
    ct_day = pd.crosstab(m.day, m.grp); ct_hr = pd.crosstab(m.hour, m.grp)
    ks = stats.ks_2samp(ad.total_ads, ps.total_ads)
    m["band"] = pd.cut(m.hour, [-1, 5, 11, 17, 23], labels=["0-5", "6-11", "12-17", "18-23"])
    rows = []
    for _, g in m.groupby(["day", "band", "tier"], observed=True):
        a_, b_ = g[g.grp == "ad"], g[g.grp == "psa"]
        if len(a_) >= 5 and len(b_) >= 5:
            rows.append((len(a_), a_.conv.mean() - b_.conv.mean()))
    cell = pd.DataFrame(rows, columns=["n_ad", "diff"])
    adj_lift = (cell.n_ad * cell["diff"]).sum() / cell.n_ad.sum()     # weighted to the ad-arm mix
    chk = pd.DataFrame([
        ("day_mix_chi2_p", stats.chi2_contingency(ct_day)[1]),
        ("day_mix_cramers_v", cramers_v(ct_day)),
        ("hour_mix_chi2_p", stats.chi2_contingency(ct_hr)[1]),
        ("hour_mix_cramers_v", cramers_v(ct_hr)),
        ("impressions_ks_statistic", ks.statistic),
        ("mean_impressions_ad", ad.total_ads.mean()), ("mean_impressions_holdout", ps.total_ads.mean()),
        ("lift_pts_unadjusted", 100 * d),
        ("lift_pts_adjusted_for_day_hour_impressions", 100 * adj_lift),
    ], columns=["check", "value"])
    chk.round(4).to_csv(a.out / "balance_checks.csv", index=False)

    # 5. Holdout planning: how big must the holdout be to read a segment?
    rows = []
    for target in (0.002, 0.003, 0.005):                  # lifts we may want to detect (pts)
        for pct in (0.04, 0.10, 0.20):                    # holdout shares to compare
            n_seg = 80_000                                # a typical segment of ~80k users
            nh, nt = n_seg * pct, n_seg * (1 - pct)
            need_ok = mde(p0, nt, nh) <= target
            rows.append(dict(target_lift_pts=100 * target, holdout_share_pct=100 * pct,
                             segment_users=n_seg, mde_pts=round(100 * mde(p0, nt, nh), 3),
                             detectable="Yes" if need_ok else "No"))
    pd.DataFrame(rows).to_csv(a.out / "holdout_planning.csv", index=False)

if __name__ == "__main__":
    main()
