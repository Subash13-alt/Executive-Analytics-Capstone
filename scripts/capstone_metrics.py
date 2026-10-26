"""Compute every number used in the capstone deck/PDF/dashboard from the analysis namespace."""
import json, io, contextlib, re
src = open("scripts/analysis_cells.py").read()
ns = {"__name__": "x"}
with contextlib.redirect_stdout(io.StringIO()):
    exec(compile(src, "analysis", "exec"), ns)
df, base, lift, seg, band = ns["df"], ns["base"], ns["lift"], ns["seg"], ns["band"]
auc, y = ns["auc"], ns["y"]

M = {}
M["customers"] = len(df); M["churn_rate"] = base; M["total_mrr"] = df.mrr.sum()
M["mrr_churned"] = df.loc[df.churned == 1, "mrr"].sum()
M["auc"] = auc(y, df.risk_score.values)

top = df.sort_values("risk_score", ascending=False)
M["capture"] = {p: top.head(int(len(top) * p / 100)).churned.sum() / df.churned.sum() for p in (10, 20, 30)}

# Insight data
M["tier"] = {t: dict(n=int(r.customers), churn=r.churn_rate, avg_mrr=r.avg_mrr) for t, r in band.iterrows()}
M["contract"] = df.groupby("contract").churned.agg(["count", "mean"]).to_dict("index")
M["login_drop"] = df.groupby("login_drop_30").churned.agg(["count", "mean"]).to_dict("index")
M["adoption"] = df.groupby("low_adoption").churned.agg(["count", "mean"]).to_dict("index")
M["segments"] = {k: dict(n=int(v.customers), churn=v.churn_rate, avg_mrr=v.avg_mrr,
                         mrr=float(df[df.segment == k].mrr.sum())) for k, v in seg.iterrows()}

# Impact scenario: targeted outreach on the High tier
hi = df[df.risk_tier == "High"]
exp_churners = hi.churned.sum(); exp_mrr_lost = hi.loc[hi.churned == 1, "mrr"].sum()
M["high"] = dict(n=len(hi), churners=int(exp_churners), mrr_lost_month=float(exp_mrr_lost),
                 avg_mrr_churner=float(hi.loc[hi.churned == 1, "mrr"].mean()))
COST = 40   # assumed fully-loaded cost per customer contacted (USD)
M["assumed_cost_per_contact"] = COST
sc = {}
for name, save in (("low", 0.05), ("base", 0.10), ("high", 0.20)):
    saved = exp_churners * save
    mrr_saved = exp_mrr_lost * save
    cost = len(hi) * COST
    sc[name] = dict(save_rate=save, customers_saved=saved, mrr_saved_month=mrr_saved,
                    annual_revenue=mrr_saved * 12, cost=cost, net_year1=mrr_saved * 12 - cost)
M["scenarios"] = sc

# Retention of a monthly->annual move on the Stable Monthly group (second lever)
sm = df[(df.segment == "4 Stable Monthly")]
M["stable_monthly"] = dict(n=len(sm), churn=sm.churned.mean(), mrr=float(sm.mrr.sum()))
json.dump(M, open("capstone/metrics.json", "w"), indent=1, default=float)
print(json.dumps(M, indent=1, default=float))
