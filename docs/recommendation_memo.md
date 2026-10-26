# Recommendation Memo: Customer Retention Prioritization

**To:** Head of Customer Success  **Re:** Who to contact first, and what to do
**Data:** synthetic SaaS dataset, 4,994 customers after cleaning, 24.1% churn overall

## Recommendation
Run retention outreach from the **High risk tier first (476 customers, 70% churned)**, using the segment playbooks below. This tier churns at about 7x the Low tier (9.7%), while being just 9.5% of customers. Do not spend retention budget on the Low tier.

## What the score shows
A transparent 0-100 points score (monthly contract, login decline, low feature adoption, support tickets, late payments, inactivity, NPS detractor, new customer). It is a ranking tool, not a probability.

| Risk tier | Score | Customers | Observed churn |
|---|---|---|---|
| High | 50+ | 476 | 70.2% |
| Medium | 25-49 | 1,950 | 31.7% |
| Low | 0-24 | 2,568 | 9.7% |

Validation: AUC 0.78 (0.5 = chance). The top 20% of customers by score contain 46% of all churners, and the top decile churns at 69% vs 2% in the bottom decile. All 10 edge cases pass (missing NPS, zero prior logins, threshold boundaries, annual-but-disengaged).

## Segments and actions
| Segment | Customers | Churn | Revenue at risk / month | Action |
|---|---|---|---|---|
| 2 Disengaging | 796 | 40.2% | $23.1k | **Top intensive target.** Outreach within 7 days of a 30%+ login drop; usage review call. 269 of these are already High tier. |
| 3 Friction & Billing Risk | 574 | 33.8% | $16.2k | Named owner for open tickets; billing support and auto-pay. Highest average MRR ($84), so worth personal attention. |
| 1 New & Unproven | 609 | 30.2% | $13.3k | Structured 30/60-day onboarding; activate 3 core features. |
| 4 Stable Monthly | 2,068 | 22.9% | $30.3k | Largest dollar exposure, but churn is below average. Use a **cheap** nudge: annual-plan offer. No personal outreach. |
| 5 Committed Core | 947 | 3.4% | $3.4k | Protect, do not discount. Referral and expansion only. |

*Revenue at risk = segment monthly revenue x segment churn rate.* Stable Monthly ranks first on dollars only because it is big; the Disengaging group is where each hour of staff time is best spent.

## Caveats
- The data is **synthetic**: it demonstrates the method, not real-world rates. Re-run on real data before acting.
- Signals are associations. Test each playbook against a holdout group before assuming it reduces churn.
- Thresholds (30% login drop, 21 days inactive, tier cut-offs) are judgement calls; review quarterly.
- Features must be measured before the churn window in production to avoid leakage.

## Next steps
1. Pilot the Disengaging + High tier playbook for one month with a 50/50 holdout.
2. Compare churn between treated and held-out customers; keep what works.
3. Recalibrate weights on real outcomes (e.g. logistic regression) and compare against this rule-based baseline.
