import pandas as pd
from risk_engine import simulate_risk
REQUIRED_COLUMNS = [
    "customer_id",
    "month_index",
    "income",
    "spend",
    "credit_utilization",
    "missed_payments"
]

def load_csv(uploaded_file):
    """
    Load and validate uploaded CSV, then apply risk engine.
    """
    df = pd.read_csv(uploaded_file)
    validate_schema(df)
    df = simulate_risk(df)
    return df

def validate_schema(df):
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Uploaded file is missing required columns: {missing}"
        )