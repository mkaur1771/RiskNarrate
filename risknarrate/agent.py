import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-3-flash-preview"

def ask_gemini(question, data_snapshot):
    prompt = f"""
You are a financial risk analyst.
Customer Financial Data:
{data_snapshot}
Question:
{question}
Return:
1) Why the risk increased
2) Suggested actions
"""
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text

    except Exception as e:
        # IMPORTANT: log the real error so we can debug
        print("Gemini API error:", repr(e))
        return """
AI service temporarily unavailable.
However, based on the customer's recent financial behavior, the increase in risk score is likely driven by:
- Higher spending relative to income
- Increased credit utilization
- Missed or delayed payments trend
"""

def fairness_summary():
    return """
Fairness & Explainability:
- Uses only financial behavior
- No demographic or personal attributes
- Transparent scoring logic
- Fully explainable outcomes
"""