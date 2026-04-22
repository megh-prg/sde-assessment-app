import streamlit as st
import requests
import uuid
import pandas as pd
from datetime import date as dt_date, timedelta
import os

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

st.markdown("""
<style>
    .main { padding: 2rem; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-card h2 { font-size: 2rem; margin: 0; }
    .metric-card p { margin: 0; opacity: 0.8; }
    .stDataFrame { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("💰 Expense Tracker")
st.markdown("---")

# Initialize session state for idempotency
if 'pending_client_id' not in st.session_state:
    st.session_state.pending_client_id = None

# ---- LAYOUT: two columns ----
left, right = st.columns([1, 2])

with left:
    st.subheader("➕ Add New Expense")
    with st.form("expense_form", clear_on_submit=True):
        amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
        category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Health", "Other"])
        description = st.text_input("Description", placeholder="What did you spend on?")
        date = st.date_input("Date", value=dt_date.today(), min_value=dt_date(2000, 1, 1), max_value=dt_date.today())
        submitted = st.form_submit_button("Add Expense", use_container_width=True)

        if submitted:
            if not description.strip():
                st.error("⚠️ Please enter a description")
            elif amount <= 0:
                st.error("⚠️ Amount must be greater than 0")
            else:
                # Generate client_id on first submit, reuse on retries (idempotency)
                if st.session_state.pending_client_id is None:
                    st.session_state.pending_client_id = str(uuid.uuid4())
                
                client_id = st.session_state.pending_client_id
                
                payload = {
                    "amount": amount,
                    "category": category,
                    "description": description,
                    "date": str(date),
                    "client_id": client_id
                }
                try:
                    with st.spinner("Saving..."):
                        res = requests.post(f"{API}/expenses", json=payload, timeout=5)
                    if res.status_code == 200:
                        st.success("✅ Expense added!")
                        st.session_state.pending_client_id = None  # Clear for next expense
                        st.rerun()
                    else:
                        st.error("❌ Failed to add expense. Try again.")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timed out. Please try again.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

with right:
    st.subheader("📊 My Expenses")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All", "Food", "Transport", "Shopping", "Bills", "Health", "Other"])
    with col2:
        sort = st.selectbox("Sort by Date", ["Newest First", "No Sort"])

    # Fetch
    params = {}
    if filter_category != "All":
        params["category"] = filter_category
    if sort == "Newest First":
        params["sort"] = "date_desc"

    try:
        with st.spinner("Loading expenses..."):
            res = requests.get(f"{API}/expenses", params=params, timeout=5)

        if res.status_code == 200:
            expenses = res.json()

            if expenses:
                # Total metric
                total = sum(e["amount"] for e in expenses)
                st.markdown(f"""
                <div class="metric-card">
                    <p>Total Expenses ({filter_category})</p>
                    <h2>₹{total:,.2f}</h2>
                    <p>{len(expenses)} transaction(s)</p>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Table
                df = pd.DataFrame(expenses)
                df = df[["date", "category", "description", "amount"]]
                df["amount"] = df["amount"].apply(lambda x: f"₹{x:,.2f}")
                df.columns = ["Date", "Category", "Description", "Amount"]
                st.dataframe(df, use_container_width=True, hide_index=True)

                # Per category summary
                st.markdown("#### 📂 Spending by Category")
                raw_df = pd.DataFrame(expenses)
                summary = raw_df.groupby("category")["amount"].sum().reset_index()
                summary.columns = ["Category", "Total (₹)"]
                summary["Total (₹)"] = summary["Total (₹)"].apply(lambda x: f"₹{x:,.2f}")
                st.dataframe(summary, use_container_width=True, hide_index=True)

            else:
                st.info("📭 No expenses found. Add your first one!")

        else:
            st.error("❌ Could not fetch expenses from server.")

    except requests.exceptions.Timeout:
        st.error("⏱️ Server is taking too long. Please refresh.")
    except Exception as e:
        st.error(f"❌ Could not load expenses: {e}")