import streamlit as st
import pandas as pd
import io
import time
from PIL import Image
import os
import google.generativeai as genai

# --- PAGE CONFIG ---
st.set_page_config(page_title="MSME Sahayak | Agentathon 2025", page_icon="🏭")

# --- SIDEBAR: SETUP ---
# --- SIDEBAR: SETUP ---
st.sidebar.header("⚙️ Configuration")
# Get API key from user input OR Streamlit secrets (secrets are for production)
api_key = st.sidebar.text_input("Enter Google Gemini API Key", type="password") or st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    
    # Add to your app.py sidebar
  # Sidebar Chat
st.sidebar.header("💬 Vernacular Text Chat")

language = st.sidebar.selectbox("Choose Language", ["Telugu", "Hindi", "English"])
user_query = st.sidebar.text_area("Type your query")

if user_query:
    if not api_key:
        st.error("Please enter API Key")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("models/gemini-1.5-flash")

            prompt = f"""
You are an MSME financial helper in Telangana.

Respond in {language} to: {user_query}

Mention relevant schemes:
- T-TAP for textiles
- Mudra Loan for general business
- Rythu Bandhu for agriculture
"""

            response = model.generate_content(prompt)
            st.write(response.text)

        except Exception as e:
            st.error(f"Error: {str(e)}")

else:
    st.warning("Please enter your query")
    
      

st.sidebar.divider()
st.sidebar.info(
    "**Project:** Hyderabadi MSME Reviver\n"
    "**Goal:** Save sick units using AI.\n"
    "**Stack:** LangChain + Gemini + Streamlit"
)

# --- TOOLS (Windows Compatible) ---

def analyze_cash_flow(file_path: str):
    """
    Reads the bank statement CSV. Calculates 'Runway' (days of cash left).
    Returns a CRITICAL ALERT if the business is running out of money.
    """
    try:
        df = pd.read_csv(file_path)
        start_bal = df.iloc[0]['Balance']
        end_bal = df.iloc[-1]['Balance']
        days = len(df)
        net_change = end_bal - start_bal
        
        if net_change >= 0:
            return f"Financial Health: STABLE. Balance increased by ₹{net_change}. No subsidy needed."
        
        # Calculate Burn Rate
        daily_burn = abs(net_change) / days
        if daily_burn == 0: daily_burn = 1
        days_left = end_bal / daily_burn
        
        return (f"⚠️ FINANCIAL CRISIS DETECTED.\n"
                f"Current Balance: ₹{end_bal:.2f}\n"
                f"Daily Burn Rate: ₹{daily_burn:.2f}\n"
                f"ESTIMATED RUNWAY: {int(days_left)} DAYS.\n"
                f"Action Required: Immediate intervention needed.")
    except Exception as e:
        return f"Error reading file: {str(e)}"

def search_telangana_schemes(business_category: str):
    """
    Finds Telangana Govt subsidies based on the business type (Textile, Agri, Tech).
    """
    # Simulated Knowledge Base (In real life, this would scrape a website)
    schemes = {
        "Textile": "T-TAP (Telangana Textile and Apparel Policy): 25% Capital Subsidy + Power Tariff Reimbursement.",
        "Agriculture": "Rythu Bandhu & Rythu Bima: Investment support and insurance for farmers.",
        "Tech/Startup": "T-IDEA (Telangana Innovation Fund): Seed funding and R&D grants.",
        "General": "Mudra Loan (Tarun Category): Loans up to ₹10 Lakhs for expansion."
    }
    # Simple keyword matching
    for key, value in schemes.items():
        if key.lower() in business_category.lower():
            return value
    return schemes["General"]

def generate_application_draft(details: str):
    """
    Takes the scheme details and financial status to draft a final letter.
    Returns the letter text.
    """
    # This tool is a placeholder to ensure the Agent knows it's the final step.
    # The actual writing happens in the LLM's final answer, but this tool 
    # reinforces the action.
    return "Drafting letter based on provided details..."

def extract_data_from_image(image_bytes, api_key_val):
    """
    Uses Gemini Vision to read a handwritten ledger and return a CSV string.
    """
    try:
        # Configure API key
        genai.configure(api_key=api_key_val)
        
        # Load image for processing
        image = Image.open(io.BytesIO(image_bytes))
        
        # Setup Gemini Vision model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the message with image
        import base64
        img_str = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = """
        You are an expert Data Entry Operator. 
        Analyze this image of a handwritten bank ledger or statement.
        Extract the transaction data into a strictly formatted CSV string.
        
        The CSV must have these headers: Date,Description,Withdrawal,Deposit,Balance
        
        Rules:
        1. Ignore any header rows in the image, just output the data.
        2. Ensure 'Balance' is the running balance. If not visible, calculate it based on the first visible balance.
        3. If Withdrawal/Deposit are mixed, separate them.
        4. Date should be in YYYY-MM-DD format. 
        5. Return ONLY the CSV string. No markdown code blocks (```csv). No other text.
        """
        
        # Generate content with image
        response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": img_str}])
        csv_string = response.text.strip()
        
        # Clean potential markdown
        if csv_string.startswith("```csv"):
            csv_string = csv_string.replace("```csv", "").replace("```", "")
            
        return csv_string
    except Exception as e:
        return None

# --- MAIN APP LOGIC ---

st.title("🏭 Hyderabadi MSME Reviver")
st.markdown("### Autonomous Financial Rescue Agent for Small Businesses")
st.write("This AI Agent analyzes bank logs, detects bankruptcy risk, and auto-applies for **Telangana State Govt Schemes**.")
st.divider()

if api_key:
    # 1. FILE UPLOAD
    uploaded_file = st.file_uploader("📂 Upload Bank Statement (CSV or Image)", type=["csv", "jpg", "jpeg", "png"])
    business_type = st.selectbox("Select Business Category", ["Textile Shop", "Agriculture / Farm", "Tech Startup", "General Retail"])
    
    if uploaded_file:
        # Determine File Type
        file_type = uploaded_file.name.split('.')[-1].lower()
        
        df = None # persist dataframe
        temp_path = "temp_bank_statement.csv"
        
        if file_type == 'csv':
            # Save temp file for the agent to read
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            df = pd.read_csv(temp_path)
            
        elif file_type in ['jpg', 'jpeg', 'png']:
            st.info("🖼️ Image detected. Analyzing handwritten ledger...")
            with st.spinner("Extracting data from image... (this uses the Vision Agent)"):
                image_bytes = uploaded_file.getvalue()
                extracted_csv = extract_data_from_image(image_bytes, api_key)
                
                if extracted_csv:
                    from io import StringIO
                    try:
                        df = pd.read_csv(StringIO(extracted_csv))
                        # Save to temp csv for the "File Tool" to use later if needed, 
                        # or we just adapt the tool to take a DF. 
                        # For minimal friction, let's save it as the temp CSV the tool expects.
                        temp_path = "temp_bank_statement.csv"
                        df.to_csv(temp_path, index=False)
                        st.success("✅ Handwritten data digitized successfully!")
                    except Exception as e:
                        st.error(f"Failed to parse extracted data: {e}")
                else:
                    st.error("Failed to extract data from image.")

        if df is not None:
            # Show Preview
            st.dataframe(df.tail(3))
            st.caption(f"Loaded {len(df)} days of transactions.")
        
            # 2. RUN AGENT BUTTON
            if st.button("🚀 Activate CFO Agent", type="primary"):
                
                # 3. EXECUTION - Direct Agent Workflow
                st.info("🤖 Agent is analyzing your business...")
                
                try:
                    # Step 1: Analyze cash flow
                    cash_flow_status = analyze_cash_flow(temp_path)
                    st.info(f"**Cash Flow Analysis:** {cash_flow_status}")
                    
                    # Step 2: Search for schemes
                    scheme = search_telangana_schemes(business_type)
                    st.info(f"**Recommended Scheme:** {scheme}")
                    
                    # Step 3: Generate application letter
                    response = f"""District Industries Centre (DIC), Telangana
Telangana, India

Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}

Subject: Application for Subsidy Under {scheme.split(':')[0]}

Dear Sir/Madam,

I am writing to request immediate financial assistance under the {scheme.split(':')[0]} scheme.

FINANCIAL STATUS:
{cash_flow_status}

REQUESTED SCHEME:
{scheme}

This scheme is critical for the survival of our {business_type} business in Telangana. We are experiencing severe financial constraints and urgently need the support provided by this scheme.

I request expedited processing of this application and look forward to your response.

Yours sincerely,
Business Owner
{business_type}
Telangana"""
                except Exception as e:
                    response = f"Error during agent execution: {str(e)}"
                
                # 4. FINAL OUTPUT
                if "Error" not in response:
                    st.success("✅ Analysis & Action Complete!")
                    st.subheader("📝 Drafted Application Letter")
                    st.text_area("Final Letter", value=response, height=400)
                else:
                    st.error(response)
                
                # Download Button
                st.download_button(
                    label="Download Letter (.txt)",
                    data=response,
                    file_name="Subsidy_Application.txt",
                    mime="text/plain"
                )
                
                        # Cleanup
                if os.path.exists(temp_path):
                    os.remove(temp_path)

else:
    st.warning("⚠️ Please enter your API Key in the sidebar.")
