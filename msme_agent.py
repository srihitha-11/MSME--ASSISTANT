import pandas as pd
import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

# 1. SETUP (Use the key you got from Google AI Studio)
os.environ["GEMINI_API_KEY"] = "AIzaSyBjAL97L_8ve3lUJgj-UwelUxVBjAn_HlU"
my_llm = LLM(model="gemini/gemini-1.5-flash", temperature=0.0)

# --- TOOLS ---

class FinanceTools:
    @tool("Analyze Cash Flow")
    def analyze_runway(file_path: str):
        """Reads bank CSV. Calculates monthly burn rate and 'Runway' (days left of money)."""
        try:
            df = pd.read_csv(file_path)
            start_bal = df.iloc[0]['Balance']
            end_bal = df.iloc[-1]['Balance']
            days = len(df)
            
            # Net Loss over the period
            net_change = end_bal - start_bal
            
            if net_change >= 0:
                return "Healthy. Business is profitable."
            
            # Calculate when they hit 0
            daily_burn = abs(net_change) / days
            days_left = end_bal / daily_burn
            
            return f"CRITICAL: Business is bleeding money. Current Balance: ₹{end_bal:.2f}. At this rate, cash runs out in {int(days_left)} days."
        except Exception as e:
            return f"Error: {e}"

    @tool("Search Telangana Schemes")
    def find_scheme(business_type: str):
        """Returns applicable Govt schemes based on business type (Textile/Tech/Agri)."""
        # In a real app, this would scrape 'industries.telangana.gov.in'. 
        # For the hackathon, we simulate the 'Search' success.
        schemes = {
            "Textile": "T-TAP (Telangana Textile and Apparel Policy): Offers 25% capital subsidy and power tariff reimbursement.",
            "Tech": "T-IDEA: Incentives for IT startups including seed funding.",
            "General": "Mudra Loan: Central govt collateral-free loan up to 10 Lakhs."
        }
        return schemes.get(business_type, schemes["General"])

# --- AGENTS ---

# Agent 1: The Virtual CFO
cfo = Agent(
    role='Crisis CFO',
    goal='Monitor bank logs and trigger alerts if runway < 60 days',
    backstory="You are a financial expert. You look at numbers and predict bankruptcy before it happens.",
    tools=[FinanceTools.analyze_runway],
    verbose=True, llm=my_llm
)

# Agent 2: The Govt Liaison
consultant = Agent(
    role='Scheme Expert',
    goal='Find the best Telangana Govt relief package for the client',
    backstory="You know every subsidy in Telangana (T-PRIDE, T-TAP). You match businesses to free money.",
    tools=[FinanceTools.find_scheme],
    verbose=True, llm=my_llm
)

# Agent 3: The Clerk
writer = Agent(
    role='Application Writer',
    goal='Draft a persuasive application letter for the bank/govt',
    backstory="You write formal letters. You take the financial data and the scheme details and write a 'Request for Restructuring' letter.",
    verbose=True, llm=my_llm
)

# --- TASKS ---

task1 = Task(
    description="Analyze 'bank_statement.csv'. Determine if the business is in danger.",
    expected_output="A financial health report with estimated days of cash remaining.",
    agent=cfo
)

task2 = Task(
    description="""
    If the business is in danger (from Task 1), identify the best scheme for a 'Textile Shop' in Sircilla. 
    Use the Search Tool.
    """,
    expected_output="Name and details of the specific subsidy scheme.",
    agent=consultant
)

task3 = Task(
    description="""
    Draft a formal application letter to the 'District Industries Centre (DIC), Sircilla'.
    Subject: Application for [Scheme Name] due to Cash Flow Constraints.
    Content: Mention the current balance, the projected runway (from Task 1), and request immediate enrollment in the scheme (from Task 2).
    """,
    expected_output="A complete, professional application letter text.",
    agent=writer
)

# --- EXECUTION ---

crew = Crew(
    agents=[cfo, consultant, writer],
    tasks=[task1, task2, task3],
    process=Process.sequential
)

print("🚀 CFO Agent Activated...")
result = crew.kickoff()
print("\n################################")
print(result)
