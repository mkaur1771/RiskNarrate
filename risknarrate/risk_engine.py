import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def simulate_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Core risk scoring engine
    Adds:
    - risk_score (0–100)
    - risk_level (Low / Medium / High)
    - anomaly (boolean)
    """
    df = df.copy()
    spend_ratio = df["spend"] / df["income"]
    credit_util = df["credit_utilization"]
    missed = df["missed_payments"]

#------------Risk score calculation (0-100)----------
    df["risk_score"] = (
        (spend_ratio * 40) +
        (credit_util * 40) +
        (missed * 20)
    ).clip(0, 100)
    df["risk_level"] = np.select(
        [
            df["risk_score"] < 35,
            df["risk_score"].between(35, 66),
            df["risk_score"] > 65
        ],
        ["Low Risk", "Medium Risk", "High Risk"],
        default="Unknown"
    ).astype(str)

#---------- Simple anomaly detection -----------
    df["anomaly"] = (
        (df["credit_utilization"] > 0.8) &
        (df["missed_payments"].diff().fillna(0) >= 1))
    return df

def forecast_risk(cust_df: pd.DataFrame, future_months: int = 6) -> pd.DataFrame:
    """Predict future risk_score using time-series regression"""
    df = cust_df.copy()
    X = df["month_index"].values.reshape(-1, 1)
    y = df["risk_score"].values
    model = LinearRegression()
    model.fit(X, y)
    last_month = df["month_index"].max()
    future_index = np.array([last_month + i for i in range(1, future_months + 1)]).reshape(-1, 1)

    future_risk = model.predict(future_index)
    forecast_df = pd.DataFrame({
        "month_index": future_index.flatten(),
        "risk_score": future_risk})
    return forecast_df

def calculate_cibil(latest_row: pd.Series) -> int:
    """Simple CIBIL-like score estimation (300–900)"""
    score = 900
    utilization = latest_row["credit_utilization"]
    if utilization > 0.9:
        score -= 200
    elif utilization > 0.75:
        score -= 150
    elif utilization > 0.5:
        score -= 100
    elif utilization > 0.3:
        score -= 50

    missed = int(latest_row["missed_payments"])
    score -= missed * 40
    risk_score = float(latest_row["risk_score"])
    score -= int(risk_score * 2)

    return int(max(300, min(900, score)))