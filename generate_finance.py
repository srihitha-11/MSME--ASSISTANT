import pandas as pd
import random
from datetime import datetime, timedelta

# Create a scenario: A textile shop in Sircilla is bleeding money
# Revenue is dropping, Rent/Electricity is constant.

data = []
current_balance = 500000 # Starting with 5 Lakhs
date = datetime.now() - timedelta(days=90) # Start 3 months ago

for i in range(90): # 3 months of daily transactions
    date += timedelta(days=1)
    
    # Random Income (Declining over time to simulate crisis)
    # Month 1: High, Month 3: Low
    decay_factor = (100 - i) / 100 
    daily_sales = random.randint(5000, 15000) * decay_factor
    
    # Expenses (Constant)
    daily_expense = random.randint(4000, 8000) # Raw materials
    if i % 30 == 0: # Monthly Rent & Electricity on 1st of month
        daily_expense += 30000 
    
    current_balance += (daily_sales - daily_expense)
    
    data.append({
        "Date": date.strftime("%Y-%m-%d"),
        "Description": "Daily Sales" if daily_sales > daily_expense else "Vendor Payment/Rent",
        "Credit": round(daily_sales, 2),
        "Debit": round(daily_expense, 2),
        "Balance": round(current_balance, 2)
    })

df = pd.DataFrame(data)
df.to_csv("bank_statement.csv", index=False)

print(f"📉 Generated financial data. Ending Balance: ₹{current_balance:.2f}")
print("⚠️ This business is in trouble. The agents need to save it.")
