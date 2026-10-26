import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader

M = json.load(open("capstone/metrics.json"))
BLUE, ORANGE, INK, GREY, LIGHT, GREEN = "#4C6EF5", "#E8590C", "#1F2937", "#6B7280", "#EEF2FF", "#2F9E44"
base = M["churn_rate"] * 100
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})

def bar(fn, labels, vals, colors, title, ylabel="Churn rate (%)", ref=True, fmt="{:.1f}%", size=(5.2, 3.2)):
    fig, ax = plt.subplots(figsize=size)
    b = ax.bar(labels, vals, color=colors, width=0.6)
    for r, v in zip(b, vals):
        txt = fmt(v) if callable(fmt) else fmt.format(v)
        ax.text(r.get_x() + r.get_width() / 2, (v if v >= 0 else 0) + max(vals) * .02, txt, ha="center", fontsize=11, fontweight="bold", color=INK)
    if ref: ax.axhline(base, color=ORANGE, ls="--", lw=1.4); ax.text(-0.45, base + max(vals) * .025, f"Overall {base:.1f}%", color=ORANGE, ha="left", fontsize=9)
    ax.set_title(title, loc="left", fontsize=12, color=INK, fontweight="bold"); ax.set_ylabel(ylabel)
    ax.set_ylim(min(0, min(vals) * 1.3), max(vals) * 1.18)
    plt.tight_layout(); fig.savefig(fn, dpi=170); plt.close(fig)

t = M["tier"]
bar("capstone/c1.png", ["Low", "Medium", "High"], [t[k]["churn"] * 100 for k in ("Low", "Medium", "High")], [BLUE, BLUE, ORANGE], "Churn by risk tier")
c = M["contract"]
bar("capstone/c2.png", ["Annual", "Monthly"], [c["Annual"]["mean"] * 100, c["Monthly"]["mean"] * 100], [BLUE, ORANGE], "Churn by contract type")
l = M["login_drop"]
bar("capstone/c3.png", ["Logins steady", "Logins down 30%+"], [l["0"]["mean"] * 100, l["1"]["mean"] * 100], [BLUE, ORANGE], "Churn by recent login trend")
a = M["adoption"]
bar("capstone/c4.png", ["3+ features used", "0-2 features used"], [a["0"]["mean"] * 100, a["1"]["mean"] * 100], [BLUE, ORANGE], "Churn by feature adoption")
s = M["scenarios"]
vals = [s[k]["net_year1"] / 1000 for k in ("low", "base", "high")]
bar("capstone/c5.png", ["Low\n5% saved", "Base\n10% saved", "High\n20% saved"], vals, [ORANGE, BLUE, GREEN],
    "Year-1 net impact of High-tier outreach ($k)", ylabel="$ thousands", ref=False, fmt=lambda v: ("-" if v < 0 else "+") + f"${abs(v):.1f}k", size=(5.6, 3.4))

W, H = 960, 540
pdf = canvas.Canvas("capstone/Executive_Churn_Briefing.pdf", pagesize=(W, H))
pdf.setTitle("Executive Churn Briefing"); pdf.setAuthor("Analytics")
body = ParagraphStyle("b", fontName="Helvetica", fontSize=15, leading=21, textColor=HexColor(INK))
small = ParagraphStyle("s", parent=body, fontSize=12, leading=16, textColor=HexColor(GREY))
bul = ParagraphStyle("bu", parent=body, fontSize=15, leading=21, leftIndent=16, bulletIndent=0, spaceAfter=7)
page = [0]

def slide(title, sub=None):
    pdf.showPage()
    page[0] += 1
    pdf.setFillColor(white); pdf.rect(0, 0, W, H, fill=1, stroke=0)
    pdf.setFillColor(HexColor(BLUE)); pdf.rect(0, H - 8, W, 8, fill=1, stroke=0)
    pdf.setFillColor(HexColor(INK)); pdf.setFont("Helvetica-Bold", 27)
    y = H - 62
    for line in title.split("\n"):
        pdf.drawString(48, y, line); y -= 32
    if sub:
        p = Paragraph(sub, small); w, h = p.wrap(W - 96, 60); p.drawOn(pdf, 48, y - h + 6)
    pdf.setFont("Helvetica", 9); pdf.setFillColor(HexColor(GREY))
    pdf.drawString(48, 20, "Synthetic data. Illustrative figures, not real customers.")
    pdf.drawRightString(W - 48, 20, str(page[0]))

def para(text, x, y, w, h, style=body):
    Frame(x, y, w, h, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, showBoundary=0).addFromList([Paragraph(text, style)], pdf)

def bullets(items, x, y, w, h, style=bul):
    Frame(x, y, w, h, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0).addFromList(
        [Paragraph(i, style, bulletText="•") for i in items], pdf)

def kpi(x, y, w, big, label, color=BLUE):
    pdf.setFillColor(HexColor(LIGHT)); pdf.roundRect(x, y, w, 96, 10, fill=1, stroke=0)
    pdf.setFillColor(HexColor(color)); pdf.setFont("Helvetica-Bold", 32); pdf.drawString(x + 16, y + 52, big)
    pdf.setFillColor(HexColor(GREY)); pdf.setFont("Helvetica", 11.5)
    for i, ln in enumerate(label.split("\n")): pdf.drawString(x + 16, y + 34 - i * 14, ln)

def img(fn, x, y, w):
    ir = ImageReader(fn); iw, ih = ir.getSize(); pdf.drawImage(ir, x, y, w, w * ih / iw, mask="auto")

hi = M["high"]
be = s["base"]["cost"] / (hi["mrr_lost_month"] * 12) * 100

# 1 Title
page[0] += 1
pdf.setFillColor(HexColor(BLUE)); pdf.rect(0, 0, W, H, fill=1, stroke=0)
pdf.setFillColor(white); pdf.setFont("Helvetica-Bold", 40); pdf.drawString(60, 330, "Who will we lose next,")
pdf.drawString(60, 280, "and is it worth acting?")
pdf.setFont("Helvetica", 18); pdf.drawString(60, 220, "Executive churn briefing: findings, limitations, recommended action")
pdf.setFont("Helvetica", 12); pdf.drawString(60, 60, "Analysis of 4,994 synthetic SaaS customers | October 2026")

# 2 Bottom line
slide("Bottom line: target the riskiest 10%, but pilot before scaling",
      "We can identify who is likely to leave. Whether outreach pays back depends on a save rate we have not yet measured.")
kpi(48, 300, 205, f"{M['churn_rate']*100:.0f}%", "of customers churned")
kpi(268, 300, 205, f"${M['mrr_churned']/1000:.0f}k", f"monthly revenue lost\n({M['mrr_churned']/M['total_mrr']*100:.0f}% of ${M['total_mrr']/1000:.0f}k)", ORANGE)
kpi(488, 300, 205, f"{t['High']['churn']*100:.0f}%", f"churn in High-risk tier\n({t['High']['n']} customers)", ORANGE)
kpi(708, 300, 205, f"{be:.0f}%", "save rate needed to\nbreak even (assumed)")
bullets([f"<b>Recommendation:</b> run a 1-month outreach pilot on the {hi['n']} High-tier customers with a 50/50 holdout group.",
         f"<b>Expected impact:</b> net year-1 result of about <b>-${abs(s['low']['net_year1'])/1000:.0f}k to +${s['high']['net_year1']/1000:.0f}k</b> (base case +${s['base']['net_year1']/1000:.0f}k), driven mostly by how many customers outreach actually saves.",
         "<b>Decision needed:</b> approve the pilot and agree a go/no-go threshold (save rate above about 8%)."],
        48, 60, 864, 220, ParagraphStyle("b2", parent=bul, fontSize=18, leading=26, spaceAfter=12))

# 3 Insights 1-2
slide("Insights 1 and 2: risk is concentrated, and contract type matters",
      "The score finds a small group that churns far above average. Monthly contracts churn at 3x the annual rate.")
img("capstone/c1.png", 48, 175, 405); img("capstone/c2.png", 507, 175, 405)
para(f"<b>1. Concentrated risk.</b> The High tier is {t['High']['n']/M['customers']*100:.0f}% of customers yet churns at {t['High']['churn']*100:.0f}%. The top 20% by score holds {M['capture']['20']*100:.0f}% of all churners.", 48, 60, 405, 100, small)
para(f"<b>2. Contract type.</b> {c['Monthly']['count']:,} customers are on monthly plans and churn at {c['Monthly']['mean']*100:.0f}%, versus {c['Annual']['mean']*100:.0f}% for annual. Moving customers to annual is the cheapest lever, but this is an association, not proof.", 507, 60, 405, 100, small)

# 4 Insights 3-4
slide("Insights 3 and 4: falling usage and low adoption warn us early",
      "Both signals are visible weeks before cancellation and can be monitored automatically.")
img("capstone/c3.png", 48, 175, 405); img("capstone/c4.png", 507, 175, 405)
para(f"<b>3. Usage decline.</b> {l['1']['count']} customers cut logins by 30% or more and churn at {l['1']['mean']*100:.0f}%, double the {l['0']['mean']*100:.0f}% of steady users.", 48, 60, 405, 100, small)
para(f"<b>4. Low adoption.</b> {a['1']['count']:,} customers use two or fewer features and churn at {a['1']['mean']*100:.0f}% versus {a['0']['mean']*100:.0f}%. This is the largest group we can act on through onboarding.", 507, 60, 405, 100, small)

# 5 Impact
slide("Insight 5: outreach is close to break-even",
      "At-risk customers pay about $56 a month, so each save is worth little. The outcome hinges on the save rate.")
img("capstone/c5.png", 40, 100, 450)
rows = [["Assumption", "Value"],
        ["Customers contacted", f"{hi['n']} (High tier)"],
        ["Would-be churners", f"{hi['churners']} (70%)"],
        ["Revenue per churner", f"${hi['avg_mrr_churner']:.0f} / month"],
        ["Cost per contact", f"${M['assumed_cost_per_contact']} (assumed)"],
        ["Value of a save", "12 more months of revenue"],
        ["Save rate range", "5% / 10% / 20% (assumed)"],
        ["Break-even save rate", f"{be:.1f}%"]]
tb = Table(rows, colWidths=[150, 200])
tb.setStyle(TableStyle([("FONT", (0, 0), (-1, -1), "Helvetica", 11), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 11),
    ("BACKGROUND", (0, 0), (-1, 0), HexColor(LIGHT)), ("TEXTCOLOR", (0, 0), (-1, -1), HexColor(INK)),
    ("LINEBELOW", (0, 0), (-1, -1), .4, HexColor("#D1D5DB")), ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6)]))
tb.wrapOn(pdf, 350, 300); tb.drawOn(pdf, 548, 235)
para("None of the save rates above has been measured. They are planning assumptions, which is why we recommend a pilot.", 548, 150, 360, 60, small)
para(f"Customers saved: about {s['low']['customers_saved']:.0f} to {s['high']['customers_saved']:.0f}. Revenue kept per year: ${s['low']['annual_revenue']/1000:.0f}k to ${s['high']['annual_revenue']/1000:.0f}k against ${s['base']['cost']/1000:.0f}k of outreach cost.", 548, 80, 360, 60, small)

# 6 Action
slide("Recommended action: match the play to the reason customers leave")
seg = M["segments"]
rows = [["Segment", "Customers", "Churn", "Play"],
        ["Disengaging", f"{seg['2 Disengaging']['n']}", f"{seg['2 Disengaging']['churn']*100:.0f}%", "Outreach within 7 days of a 30%+ login drop; usage review call"],
        ["Friction & Billing", f"{seg['3 Friction & Billing Risk']['n']}", f"{seg['3 Friction & Billing Risk']['churn']*100:.0f}%", "Named owner for open tickets; billing support, auto-pay"],
        ["New & Unproven", f"{seg['1 New & Unproven']['n']}", f"{seg['1 New & Unproven']['churn']*100:.0f}%", "30/60-day onboarding; activate 3 core features"],
        ["Stable Monthly", f"{seg['4 Stable Monthly']['n']:,}", f"{seg['4 Stable Monthly']['churn']*100:.0f}%", "Low-cost annual-plan offer only; no personal outreach"],
        ["Committed Core", f"{seg['5 Committed Core']['n']}", f"{seg['5 Committed Core']['churn']*100:.0f}%", "Protect; no discounts; referrals and expansion"]]
rows = [[Paragraph(str(x), ParagraphStyle("t", fontName="Helvetica-Bold" if i == 0 else "Helvetica", fontSize=11.5, leading=14, textColor=HexColor(INK))) for x in r] for i, r in enumerate(rows)]
tb = Table(rows, colWidths=[140, 80, 60, 580])
tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), HexColor(LIGHT)), ("LINEBELOW", (0, 0), (-1, -1), .4, HexColor("#D1D5DB")),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
tb.wrapOn(pdf, 860, 300); tb.drawOn(pdf, 48, 250)
bullets(["<b>Pilot design:</b> one month, High tier plus Disengaging, half contacted and half held out.",
         f"<b>Go if</b> the measured save rate is above about {be:.0f}%. <b>Stop or redesign if</b> it is below.",
         "<b>Then:</b> recalibrate the score on real outcomes and revisit thresholds."], 48, 80, 864, 150)

# 7 Limitations
slide("Limitations: what this analysis cannot tell us")
bullets(["<b>Synthetic data.</b> The method is demonstrated; the specific rates are not real-world evidence.",
         "<b>Association, not causation.</b> A monthly contract flags risk; it does not prove switching to annual prevents churn. Only the pilot can show that.",
         "<b>The score ranks, it does not predict.</b> A score of 60 is not a 60% chance of leaving.",
         "<b>Impact figures rest on assumptions</b> (save rate, cost per contact, 12-month value of a save). Treat the range, not the base case, as the message.",
         "<b>Judgement thresholds.</b> The 30% login drop and 21-day inactivity cut-offs were chosen by hand and should be reviewed on real outcomes.",
         "<b>Timing.</b> In production every input must be measured before the churn window, or the score will leak the answer."],
        48, 60, 864, 390, ParagraphStyle("bl", parent=bul, fontSize=17, leading=24, spaceAfter=12))
pdf.save(); print("pdf saved, pages:", page[0])
