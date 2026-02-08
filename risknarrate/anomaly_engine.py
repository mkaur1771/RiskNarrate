import pandas as pd
import numpy as np
def detect_anomalies(df):
    df = df.copy()

    df["rolling_mean"] = df["risk_score"].rolling(window=3, min_periods=1).mean()

    df["anomaly_flag"] = np.where(
        df["risk_score"] > df["rolling_mean"] * 1.20, True, False
    )
    return df