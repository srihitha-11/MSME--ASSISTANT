import os
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

# 1. SETUP API KEY (Use your actual key)
# Note: In a real terminal, set this via `set GEMINI_API_KEY=...` or paste it below for testing
if "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = "AIzaSyBjAL97L_8ve3lUJgj-UwelUxVBjAn_HlU"  # Replace with your actual key

# Initialize the Gemini Model
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    google_api_key=os.environ["GEMINI_API_KEY"]
)

# --- 2. DEFINE THE TOOLS (The "Arms and Legs") ---

def analyze_cash_flow_runway(file_path: str):
    """
    Reads a bank statement CSV to calculate the 'Runway' (days of cash left).
    Input must be a valid file path string (e.g., 'bank_statement.csv').
    Returns a status string indicating if the business is in danger.
    """
    try:
        # Check if file exists to prevent errors
        if not os.path.exists(file_path):
            return f"Error: File '{file_path}' not found."

        df = pd.read_csv(file_path)
        start_bal = df.iloc[0]['Balance']
        end_bal = df.iloc[-1]['Balance']
        days = len(df)
        
        # Net Loss over the period
        net_change = end_bal - start_bal
        
        if net_change >= 0:
            return f"Healthy Financials. Balance grew by {net_change}. No action needed."
        
        # Calculate burn rate
        daily_burn = abs(net_change) / days
        if daily_burn == 0: daily_burn = 1 # Avoid div by zero
        days_left = end_bal / daily_burn
        
        return (f"CRITICAL ALERT: The business is losing money (Burn Rate: ₹{daily_burn:.2f}/day). "
                f"Current Balance: ₹{end_bal:.2f}. "
                f"Estimated Runway: {int(days_left)} days remaining before bankruptcy.")
    except Exception as e:
        return f"Error analyzing data: {str(e)}"

def search_telangana_schemes(business_category: str):
    """
    Searches for Telangana State Government subsidies based on business category.
    Input should be a category like 'Textile', 'Agriculture', or 'Tech'.
    """
    # Simulated Database of Schemes
    schemes = {
        "textile": "T-TAP (Telangana Textile and Apparel Policy): Provides 25% capital subsidy and 100% stamp duty reimbursement.",
        "agriculture": "Rythu Bandhu: Investment support for agriculture.",
        "tech": "T-IDEA: Incentive scheme for IT startups and expansions.",
        "general": "Mudra Loan (Kishore Category): Loans up to ₹5 Lakhs for existing small businesses."
    }
    
