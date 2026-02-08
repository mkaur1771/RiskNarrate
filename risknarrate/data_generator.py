import pandas as pd
import numpy as np

def generate_synthetic_data(num_customers=500, months=12, seed=42):
    np.random.seed(seed)
    rows =[]
    for cid in range(num_customers):
        customer_id = f"C{1000 +cid}"
        income = np.random.randint(4000,12000)
        credit_util = np.random.uniform(0.25, 0.45)
        missed = 0
        for month in range(months):
            spend = income * np.random.uniform(0.55, 1.15)
            credit_util = min(1.0, credit_util + np.random.uniform(-0.03, 0.07))
            missed += np.random.choice([0, 1], p=[0.9, 0.1])
            rows.append({
                    "customer_id": customer_id,
                    "month_index": month,
                    "income": income,
                    "spend": round(spend, 2),
                    "credit_utilization": round(credit_util, 2),
                    "missed_payments": missed})
            print("Total Rows Generated:", len(rows))
            return pd.DataFrame(rows)
