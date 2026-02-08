import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from db import load_csv
from agent import ask_gemini, fairness_summary
from risk_engine import simulate_risk, forecast_risk
from utils import export_pdf_bytes
from anomaly_engine import detect_anomalies
from scoring import compute_credit_score, recommend_lenders


# =========================================================
# Session State Defaults
# =========================================================
if "response" not in st.session_state:
    st.session_state["response"] = ""
if "show_score" not in st.session_state:
    st.session_state["show_score"] = False
if "credit_score" not in st.session_state:
    st.session_state["credit_score"] = None
if "forecast_df" not in st.session_state:
    st.session_state["forecast_df"] = None
if "selected_customer" not in st.session_state:
    st.session_state["selected_customer"] = None


# =========================================================
# Helper Functions
# =========================================================
def calculate_cibil(latest_row: pd.Series) -> int:
    """Fallback CIBIL-like score (300–900) if compute_credit_score fails."""
    score = 900
    score -= int(latest_row["missed_payments"]) * 40
    score -= int(float(latest_row["credit_utilization"]) * 200)

    if latest_row.get("risk_level") == "High Risk":
        score -= 120
    elif latest_row.get("risk_level") == "Medium Risk":
        score -= 60

    return max(300, min(900, int(score)))


def risk_level_from_score(score: float) -> str:
    if score >= 70:
        return "High Risk"
    elif score >= 40:
        return "Medium Risk"
    return "Low Risk"


def apply_what_if(
    cust_df: pd.DataFrame,
    target_util: float,
    spend_reduction_pct: int,
    missed_payment_reduction: int
):
    """
    Modify ONLY the latest row, recompute risk via simulate_risk, and recompute CIBIL.
    Returns: sim_df, sim_latest, sim_risk_score, sim_cibil
    """
    sim_df = cust_df.copy()
    latest = sim_df.iloc[-1].copy()

    # Apply what-if changes
    latest["credit_utilization"] = float(target_util)

    if "spend" in latest:
        latest["spend"] = max(0, float(latest["spend"]) * (1 - spend_reduction_pct / 100))

    latest["missed_payments"] = max(0, int(latest["missed_payments"]) - int(missed_payment_reduction))

    # Write back
    sim_df.iloc[-1] = latest

    # Recompute risk using your engine
    sim_df = simulate_risk(sim_df)
    sim_latest = sim_df.iloc[-1]
    sim_risk_score = float(sim_latest["risk_score"])

    # Recompute CIBIL using your scoring module if possible; otherwise fallback
    sim_cibil = compute_credit_score(sim_df)
    if sim_cibil is None:
        sim_cibil = calculate_cibil(sim_latest)

    return sim_df, sim_latest, sim_risk_score, int(sim_cibil)


def get_current_cibil(cust_df: pd.DataFrame) -> int:
    """Safely compute current CIBIL for BEFORE values in What-if."""
    latest = cust_df.iloc[-1]
    cibil = compute_credit_score(cust_df)
    if cibil is None:
        cibil = calculate_cibil(latest)
    return int(cibil)


# =========================================================
# Page Config
# =========================================================
st.set_page_config(page_title="RiskNarrate", layout="wide")
st.title("RiskNarrate - AI Financial Risk Copilot")
st.caption("Where financial risk explains itself")


# =========================================================
# Data Loading
# =========================================================
st.subheader("Upload Financial Dataset")
uploaded_file = st.file_uploader(
    "Upload a CSV file with financial data",
    type=["csv"]
)

if not uploaded_file:
    st.info("Please upload a CSV file to continue.")
    st.stop()

try:
    df = load_csv(uploaded_file)
    st.success("Dataset loaded successfully")
except Exception as e:
    st.error(f"Dataset error: {e}")
    st.stop()


# =========================================================
# Data Preview
# =========================================================
st.subheader("Data Preview")
st.dataframe(df.head(20), use_container_width=True)


# =========================================================
# Customer Selection + Reset State
# =========================================================
st.subheader("Select Customer")
customer = st.selectbox("Choose a customer ID", sorted(df["customer_id"].unique()))

# Reset outputs when customer changes
if st.session_state["selected_customer"] != customer:
    st.session_state["selected_customer"] = customer
    st.session_state["response"] = ""
    st.session_state["show_score"] = False
    st.session_state["credit_score"] = None
    st.session_state["forecast_df"] = None

cust_df = df[df["customer_id"] == customer].copy()
cust_df = detect_anomalies(cust_df)


# =========================================================
# Risk Summary + Trend Chart
# =========================================================
st.subheader("Customer Risk Summary")
latest = cust_df.iloc[-1]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current Risk Score", round(float(latest["risk_score"]), 1))
c2.metric("Risk Level", str(latest["risk_level"]))
c3.metric("Missed Payments", int(latest["missed_payments"]))
c4.metric("Credit Utilization", round(float(latest["credit_utilization"]), 2))

plt.rcParams.update({
    "font.size": 6,
    "axes.labelsize": 6,
    "axes.titlesize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 5
})

fig, ax = plt.subplots(figsize=(6.9, 2.2))
ax.plot(cust_df["month_index"], cust_df["risk_score"], label="Risk Score")

# anomaly_flag expected from detect_anomalies()
if "anomaly_flag" in cust_df.columns:
    anoms = cust_df[cust_df["anomaly_flag"] == True]
    ax.scatter(anoms["month_index"], anoms["risk_score"], color="red", s=40, label="Anomaly")

ax.set_xlabel("Month")
ax.set_ylabel("Risk Score")
ax.legend()
st.pyplot(fig, use_container_width=False)


# =========================================================
# Gemini Copilot (Analyze)
# =========================================================
st.subheader("Ask the Risk Copilot")
question = st.text_input(
    "Ask a question about customer risk",
    placeholder="Type your question here..."
)

if st.button("Analyze", type="primary", key="btn_analyze"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        context = cust_df.to_string(index=False)
        with st.spinner("Analyzing..."):
            st.session_state["response"] = ask_gemini(question, context)


# =========================================================
# Show Copilot Insight + PDF Export
# =========================================================
if st.session_state["response"]:
    st.success("Copilot Insight")
    st.markdown(st.session_state["response"])

    pdf_data = export_pdf_bytes(st.session_state["response"], title="RiskNarrate Report")
    st.download_button(
        label="Export Insight as PDF",
        data=pdf_data,
        file_name="RiskNarrate_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )


# =========================================================
# Gate: Show Credit Score & Forecast only if user wants
# =========================================================
if st.session_state["response"]:
    st.divider()
    st.subheader("Want to see Credit Score & Future Forecast?")

    if st.button("Show Credit Score & Forecast", key="btn_show_score"):
        st.session_state["show_score"] = True


# =========================================================
# Credit Score + Forecast + Lenders + What-If (only if opted in)
# =========================================================
if st.session_state["show_score"]:

    # ---------- Forecast (cached in session_state) ----------
    st.subheader("Future Risk Forecast (Next 6 Months)")
    if st.session_state["forecast_df"] is None:
        st.session_state["forecast_df"] = forecast_risk(cust_df)

    forecast_df = st.session_state["forecast_df"]
    combined = pd.concat([cust_df[["month_index", "risk_score"]], forecast_df], ignore_index=True)
    st.line_chart(combined.set_index("month_index"), height=300)

    # ---------- Credit Score (cached in session_state) ----------
    st.subheader("Estimated Credit Score")
    if st.session_state["credit_score"] is None:
        st.session_state["credit_score"] = compute_credit_score(cust_df)

    cibil = st.session_state["credit_score"]
    if cibil is None:
        cibil = calculate_cibil(latest)

    cibil = int(cibil)
    st.metric("Estimated CIBIL Score", cibil)

    # ---------- Lenders ----------
    st.subheader("Loan Match Recommendations")
    lenders = recommend_lenders(cibil)
    for loan in lenders:
        st.write(
            f"**{loan['name']}** | {loan['type']} loan | Interest: {loan['rate']} | Acceptance Chance: {loan['chance']}"
        )

    # ---------- Gemini explanation ----------
    st.subheader("Why these lenders fit this customer")
    explain_prompt = f"""
The customer has an estimated credit score of {cibil}.
Explain why the above banks/NBFCs are suitable for this customer
based on income, spending, utilization, missed payments, and overall risk profile.
"""
    st.write(ask_gemini(explain_prompt, cust_df.to_string(index=False)))

    # =========================================================
    # What‑If Simulator (ONLY HERE — after score/forecast)
    # =========================================================
    st.divider()
    st.subheader("🔮 What‑If Simulator (Mini)")
    st.caption("Now try improvements and see predicted impact on risk and credit score.")

    with st.expander("Open What‑If Simulator", expanded=False):
        latest = cust_df.iloc[-1]

        col1, col2, col3 = st.columns(3)

        with col1:
            target_util = st.slider(
                "Target Credit Utilization",
                min_value=0.00,
                max_value=1.00,
                value=float(latest["credit_utilization"]),
                step=0.01,
                key="sim_target_util"
            )

        with col2:
            spend_reduction = st.slider(
                "Reduce Spending (%)",
                min_value=0,
                max_value=50,
                value=10,
                step=1,
                key="sim_spend_reduction"
            )

        with col3:
            max_missed = max(0, int(latest["missed_payments"]))
            missed_reduce = st.slider(
                "Reduce Missed Payments By",
                min_value=0,
                max_value=max(3, max_missed),
                value=0,
                step=1,
                key="sim_missed_reduce"
            )

        if st.button("Simulate What‑If", use_container_width=True, key="btn_simulate"):
            sim_df, sim_latest, sim_risk, sim_cibil = apply_what_if(
                cust_df,
                target_util=target_util,
                spend_reduction_pct=spend_reduction,
                missed_payment_reduction=missed_reduce
            )

            before_risk = float(latest["risk_score"])
            before_cibil = get_current_cibil(cust_df)

            st.markdown("### 📌 Before vs After")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Risk Score (Before)", f"{before_risk:.1f}")
            m2.metric("Risk Score (After)", f"{sim_risk:.1f}", delta=f"{sim_risk - before_risk:+.1f}")

            m3.metric("CIBIL (Before)", f"{before_cibil}")
            m4.metric("CIBIL (After)", f"{sim_cibil}", delta=f"{sim_cibil - before_cibil:+d}")

            sim_level = sim_latest.get("risk_level", risk_level_from_score(sim_risk))
            st.info(f"✅ Simulated Risk Level: **{sim_level}**")

            st.markdown("### 📈 Risk Trend (Simulated last month)")
            trend_sim = cust_df[["month_index", "risk_score"]].copy()
            trend_sim.iloc[-1, trend_sim.columns.get_loc("risk_score")] = sim_risk
            st.line_chart(trend_sim.set_index("month_index"), height=220)

            with st.expander("See simulated latest-month snapshot", expanded=False):
                st.dataframe(pd.DataFrame([sim_latest]), width="stretch")


# =========================================================
# Fairness (show after analysis to keep UI clean)
# =========================================================
if st.session_state["response"]:
    st.subheader("Fairness & Explainability")
    st.info(fairness_summary())