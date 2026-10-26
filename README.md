# Segmentation and Recommendation Model (churn)

| File | Purpose |
|---|---|
| `churn_segmentation_analysis.ipynb` | Analysis notebook (executed, with outputs and charts) |
| `outputs/segment_table.csv` | Segment table: size, churn, revenue at risk, action |
| `outputs/customer_risk_scores.csv` | Per-customer segment, score, tier |
| `docs/recommendation_memo.md` | One-page recommendation memo |
| `docs/data_guide.md` | Field definitions and data-quality rules |
| `data/customer_churn.csv` | Synthetic dataset |
| `scripts/` | `generate_data.py`, `analysis_cells.py` (notebook source), `build_notebook.py` |

Reproduce: `python3 scripts/generate_data.py data/customer_churn.csv`, then `python3 scripts/build_notebook.py`
(needs pandas, numpy, matplotlib). Or open the notebook in Jupyter and Run All from this folder.

## Task checklist
- [x] Choose useful behavioral and account features
- [x] Create and explain customer segments
- [x] Design a reproducible churn-risk score and validate edge cases
- [ ] Upload this folder to GitHub / Drive and submit the one view-only link

## Executive capstone (`capstone/`)
| File | Purpose |
|---|---|
| `Executive_Churn_Briefing.pdf` | 7-slide executive PDF (16:9, also used as the recording slides) |
| `presentation_script.md` | ~5 minute speaker script, slide by slide |
| `dashboard.html` | Dashboard source (published as an interactive page with an impact calculator) |
| `metrics.json` | Every number used in the PDF and dashboard |

Rebuild: `python3 scripts/capstone_metrics.py && python3 scripts/build_capstone_pdf.py`

- [x] Select the five insights that affect a business decision
- [x] Quantify impact ranges, state assumptions and limitations
- [x] Coherent narrative from problem to recommended action
- [ ] Record the presentation (use `presentation_script.md`) and add it to this folder
- [ ] Submit one view-only link to the folder
