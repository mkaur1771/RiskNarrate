# RiskNarrate – AI Financial Risk Copilot

RiskNarrate is a Streamlit-based AI copilot that helps explain a customer’s financial risk in plain language.  
It combines **deterministic risk scoring + forecasting** with **Gemini-powered reasoning** to generate actionable insights, lender-fit explanations, and downloadable PDF reports.

---

## 🚀 What RiskNarrate Does

### ✅ Core Features
- **Customer Risk Summary**: Risk score, risk level, missed payments, credit utilization
- **Risk Trend + Anomaly Flags**: Visual trend of risk score with anomaly detection
- **Ask the Risk Copilot (Gemini)**: Ask questions and get reasoning-based explanations
- **Future Risk Forecast (Next 6 months)**: Forecast risk trajectory
- **Estimated Credit Score**: CIBIL-like credit score estimation
- **Loan Match Recommendations**: Recommended lenders based on credit score
- **What‑If Simulator**: Adjust utilization/spend/missed payments and simulate impact
- **PDF Export**:
  - Quick PDF export of Copilot insight
  - Full structured Risk Report PDF (includes summary, trends, what-if, forecast, lenders, fairness)

---

## 🧠 Gemini 3 Integration (Summary)
Gemini is used as the reasoning layer for:
1. Generating **risk explanations** from structured customer history and user questions
2. Explaining **why recommended lenders fit** the customer profile

> The app sends a compact customer context (recent months + key signals) to Gemini to keep responses fast and relevant.

---

## 🗂️ Project Structure

```text
.
├── app.py
├── agent.py                # Gemini calls + fairness_summary
├── db.py                   # CSV loader
├── risk_engine.py          # simulate_risk + forecast_risk
├── anomaly_engine.py       # detect_anomalies
├── scoring.py              # compute_credit_score + recommend_lenders
├── utils.py                # quick insight PDF export (+ optional wrapper for full report)
├── risk_report_generator.py# full structured PDF report generator
├── assets/
│   └── DejaVuSans.ttf      # optional font for unicode-safe PDFs
├── requirements.txt
└── README.md
