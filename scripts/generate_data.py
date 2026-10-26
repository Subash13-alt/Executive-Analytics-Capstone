"""Generate a synthetic SaaS customer churn dataset (fully reproducible, seed=42)."""
import numpy as np, pandas as pd, sys
rng = np.random.default_rng(42)
N = 5000
snapshot = pd.Timestamp("2026-09-30")

plan = rng.choice(["Basic", "Pro", "Enterprise"], N, p=[0.50, 0.35, 0.15])
price_map = {"Basic": 29, "Pro": 79, "Enterprise": 249}
monthly_charge = np.array([price_map[p] for p in plan], float) * rng.choice([1, 1, 1, 0.9], N)
monthly_charge = monthly_charge.round(2)
contract = np.where(rng.random(N) < np.where(plan == "Enterprise", 0.7, np.where(plan == "Pro", 0.45, 0.25)),
                    "Annual", "Monthly")
tenure = np.clip(rng.gamma(2.2, 9, N), 1, 72).round().astype(int)
signup_date = [snapshot - pd.DateOffset(months=int(t)) - pd.Timedelta(days=int(rng.integers(0, 28))) for t in tenure]
region = rng.choice(["North America", "Europe", "Asia-Pacific", "Latin America"], N, p=[.4, .3, .2, .1])
payment = rng.choice(["Card", "Invoice", "Bank transfer"], N, p=[.6, .25, .15])
seats = np.where(plan == "Enterprise", rng.integers(20, 200, N), np.where(plan == "Pro", rng.integers(3, 25, N), rng.integers(1, 5, N)))

# latent engagement drives usage behaviour
engage = rng.normal(0, 1, N) + 0.15 * (plan != "Basic")
logins_prev = np.clip(np.exp(2.6 + 0.45 * engage + rng.normal(0, .25, N)), 0, 120).round().astype(int)
trend = rng.normal(0, 1, N) * 0.35 + 0.1 * engage          # recent momentum
logins_30 = np.clip(logins_prev * np.exp(trend) + rng.normal(0, 1.5, N), 0, 150).round().astype(int)
features = np.clip((4 + 2.2 * engage + rng.normal(0, 1.3, N)).round(), 0, 15).astype(int)
tickets = rng.poisson(np.clip(1.2 - 0.3 * engage + 0.15 * (plan == "Enterprise"), 0.1, None))
late = rng.poisson(np.where(payment == "Invoice", 0.5, 0.25) * np.clip(1 - 0.2 * engage, .2, None))
days_since = np.clip(np.where(logins_30 == 0, rng.integers(31, 120, N), rng.exponential(30 / np.maximum(logins_30, 1), N)), 0, 120).round().astype(int)
res_days = np.clip(rng.gamma(2, 1.6, N) + 0.6 * tickets, 0.2, 30).round(1)
nps = np.clip((7 + 1.3 * engage - 0.5 * np.minimum(tickets, 4) + rng.normal(0, 1.6, N)).round(), 0, 10)

z = (-2.55
     - 0.9 * engage
     + 0.9 * (contract == "Monthly") - 0.7 * (contract == "Annual")
     + 0.30 * np.minimum(tickets, 5)
     + 0.35 * late
     + 0.9 * np.clip(-trend, 0, None) * 2
     + 0.012 * np.clip(days_since, 0, 60)
     - 0.025 * np.minimum(tenure, 36)
     + 0.5 * (plan == "Basic") - 0.4 * (plan == "Enterprise")
     - 0.12 * (nps - 7))
p = 1 / (1 + np.exp(-z))
churn = (rng.random(N) < p).astype(int)

df = pd.DataFrame(dict(
    customer_id=[f"C{100000+i}" for i in range(N)],
    signup_date=[d.strftime("%Y-%m-%d") for d in signup_date],
    tenure_months=tenure, plan=plan, contract=contract, payment_method=payment, region=region,
    seats=seats, monthly_charge=monthly_charge, logins_last_30d=logins_30, logins_prev_30d=logins_prev,
    features_used=features, support_tickets_90d=tickets, avg_ticket_resolution_days=res_days,
    late_payments_6m=late, days_since_last_login=days_since, nps_score=nps, churned=churn))

# realistic data-quality issues (documented in the data guide)
df.loc[df.support_tickets_90d == 0, "avg_ticket_resolution_days"] = np.nan          # structural missing
df.loc[rng.random(N) < 0.35, "nps_score"] = np.nan                                  # survey non-response
df.loc[rng.choice(N, 40, replace=False), "monthly_charge"] = np.nan                 # billing gaps
df.loc[rng.choice(N, 6, replace=False), "logins_last_30d"] = -1                     # invalid sentinel
df.loc[rng.choice(N, 5, replace=False), "seats"] *= 20                              # outliers
df = pd.concat([df, df.sample(25, random_state=1)], ignore_index=True)              # exact duplicates
df = df.sample(frac=1, random_state=7).reset_index(drop=True)
df.to_csv(sys.argv[1] if len(sys.argv) > 1 else "customer_churn.csv", index=False)
print(df.shape, "churn rate (raw):", round(df.churned.mean(), 3))
