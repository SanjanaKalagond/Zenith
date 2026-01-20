import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_admin import firestore
from styles import apply_zenith_theme, zenith_card

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login at the main page first.")
    st.stop()

apply_zenith_theme()
db = firestore.client()
user_id = st.session_state.user

st.title("Lifestyle & Finance")

col_input, col_graph = st.columns([1, 2])

with col_input:
    with st.form("finance_form"):
        st.subheader("Log Transaction")
        t_type = st.selectbox("Type", ["Saving", "Expense"])
        amount = st.number_input("Amount (₹)", min_value=0)
        note = st.text_input("Note", placeholder="Rent, Coffee, Stocks...")
        if st.form_submit_button("Update Ledger"):
            db.collection("users").document(user_id).collection("finance").add({
                "type": t_type,
                "amount": amount,
                "note": note,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            st.success("Ledger Updated!")

with col_graph:
    st.subheader("Monthly Cashflow")
    f_logs = db.collection("users").document(user_id).collection("finance").order_by("timestamp").stream()
    f_data = [l.to_dict() for l in f_logs]
    
    if f_data:
        df_f = pd.DataFrame(f_data)
        fig_f = px.line(df_f, x="timestamp", y="amount", color="type", 
                        color_discrete_map={"Saving": "#2DD4BF", "Expense": "#FF4B4B"},
                        template="plotly_dark")
        fig_f.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_f, use_container_width=True)
    else:
        st.info("Log your first transaction to see the cashflow chart.")

if st.sidebar.button("LOGOUT"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.switch_page("main.py")
