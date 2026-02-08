def compute_credit_score(cust_df):
    latest = cust_df.iloc[-1]

    income = latest["income"]
    spend = latest["spend"]
    credit_util = latest["credit_utilization"]
    missed = latest["missed_payments"]
    risk = latest["risk_score"] / 100

    base = 500
    score = base
    score += (income / spend) * 100
    score += (1- credit_util) * 200
    score -= missed * 50
    score -= risk * 100
    return int(max(300, min(900, score)))

def recommend_lenders(cibil):
    if cibil >=750:
        return [
            {"name": "HDFC Bank", "type":"Personal/Home", "rate":"8-10%", "chance":"High"},
            {"name": "Axis Bank", "type":"Personal/Home", "rate":"9.5-12%", "chance":"High"},
            {"name": "SBI", "type":"Personal/Home", "rate":"10-12%", "chance":"High"},
            {"name": "ICICI Bank", "type":"Personal/Home", "rate":"8-12%", "chance":"High"},
        ]
    if cibil >=650:
        return[
            {"name": "Bajaj Finance", "type":"Personal/Home", "rate":"13-16%", "chance":"Medium"},
            {"name": "IDFC First Bank", "type":"Personal/Home", "rate":"12-15%", "chance":"Medium"},
            {"name": "Tata Capital", "type":"Personal/Home", "rate":"12-14%", "chance":"Medium"},
        ]
    if cibil >=550:
        return[
            {"name": "Fullerton India", "type":"Personal/Home", "rate":"16-22%", "chance":"Low"},
            {"name": "Muthoot Finance", "type":"Personal/Home", "rate":"18-24%", "chance":"Low"},
        ]
    return [
        {"name": "Other NBFC", "type":"Secured", "rate":"20-30%", "chance":"Low"},
    ]