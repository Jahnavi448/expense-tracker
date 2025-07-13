import streamlit as st
import pandas as pd
from datetime import date
import os
import plotly.express as px
from streamlit_lottie import st_lottie
import requests

# ---- Load Lottie Animation ----
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---- Page Config + CSS ----
st.set_page_config(page_title="💰 Expense Tracker", layout="wide")

st.markdown("""
    <style>
    .block-container {
        padding: 1.5rem 2rem 2rem 2rem;
    }
    h1 {
        text-align: center;
        font-size: 3em;
        font-weight: bold;
        color: #00FFDD;
        text-shadow: 2px 2px #444;
    }
    hr {
        border: 1px solid #eee;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Header ----
st.markdown("<h1>💸 Expense Tracker Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ---- Animation ----
with st.container():
    lottie_url = "https://assets2.lottiefiles.com/packages/lf20_jimqos21.json"  # Money flying
    lottie_json = load_lottieurl(lottie_url)
    st_lottie(lottie_json, speed=1, height=250, key="money-lottie")

# ---- Add Record ----
with st.container():
    st.subheader("📥 Add New Record")
    with st.form("entry_form"):
        col1, col2 = st.columns(2)

        with col1:
            entry_type = st.selectbox("Type", ["Expense", "Income"])
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            category = st.selectbox("Category", ["Food", "Transport", "Bills", "Shopping", "Salary", "Other"])

        with col2:
            entry_date = st.date_input("Date", value=date.today())
            description = st.text_input("Description")

        submitted = st.form_submit_button("➕ Add Record")

# ---- Save to CSV ----
def save_data(entry):
    file = "data.csv"
    columns = ["Date", "Type", "Amount", "Category", "Description"]
    df = pd.DataFrame([entry], columns=columns)

    if os.path.exists(file):
        df.to_csv(file, mode='a', header=False, index=False)
    else:
        df.to_csv(file, mode='w', header=True, index=False)

if submitted:
    new_entry = [entry_date, entry_type, amount, category, description]
    save_data(new_entry)
    st.success("✅ Record added successfully!")

# ---- Show Records + Filters ----
file = "data.csv"
if os.path.exists(file):
    df = pd.read_csv(file)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date", ascending=False)

    # ---- Sidebar Filters ----
    st.sidebar.header("🔍 Filters")
    type_filter = st.sidebar.multiselect("Type", options=df["Type"].unique(), default=df["Type"].unique())
    category_filter = st.sidebar.multiselect("Category", options=df["Category"].unique(), default=df["Category"].unique())
    start_date = st.sidebar.date_input("Start Date", value=df["Date"].min().date())
    end_date = st.sidebar.date_input("End Date", value=df["Date"].max().date())

    filtered_df = df[
        (df["Type"].isin(type_filter)) &
        (df["Category"].isin(category_filter)) &
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    ]

    # ---- Display Table ----
    with st.container():
        st.subheader("📋 Filtered Records")
        st.dataframe(filtered_df, use_container_width=True)

    # ---- Summary Cards ----
    with st.container():
        st.markdown("---")
        st.subheader("📊 Summary")
        income = filtered_df[filtered_df["Type"] == "Income"]["Amount"].sum()
        expense = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
        balance = income - expense

        col1, col2, col3 = st.columns(3)
        col1.metric("💸 Total Income", f"₹ {income:,.2f}")
        col2.metric("🧾 Total Expense", f"₹ {expense:,.2f}")
        col3.metric("💰 Balance", f"₹ {balance:,.2f}")

    # ---- Pie Chart (3D-like) ----
    with st.container():
        st.markdown("---")
        st.subheader("🥧 Expense by Category")

        expense_data = filtered_df[filtered_df["Type"] == "Expense"]
        if not expense_data.empty:
            pie_chart = px.pie(
                expense_data,
                names="Category",
                values="Amount",
                title="🧊 3D-Style Expense Chart",
                hole=0.4
            )
            pie_chart.update_traces(
                textinfo='percent+label',
                pull=[0.05] * len(expense_data),
                marker=dict(line=dict(color='white', width=2))
            )
            st.plotly_chart(pie_chart, use_container_width=True)
        else:
            st.info("No expense data to display.")

    # ---- Monthly Bar Chart ----
    with st.container():
        st.markdown("---")
        st.subheader("📅 Monthly Income vs Expense")

        filtered_df["Month"] = filtered_df["Date"].dt.to_period("M").astype(str)
        monthly_summary = (
            filtered_df.groupby(["Month", "Type"])["Amount"]
            .sum()
            .reset_index()
            .sort_values("Month")
        )

        if not monthly_summary.empty:
            bar_chart = px.bar(
                monthly_summary,
                x="Month",
                y="Amount",
                color="Type",
                barmode="group",
                title="Monthly Financial Summary",
                text="Amount"
            )
            bar_chart.update_traces(texttemplate='%{text:.2s}', textposition='outside')
            st.plotly_chart(bar_chart, use_container_width=True)
        else:
            st.info("No data available for monthly trends.")

else:
    st.info("No records found. Add your first entry above to get started!")
