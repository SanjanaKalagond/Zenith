import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_admin import firestore
from styles import apply_zenith_theme, zenith_card
from datetime import date

apply_zenith_theme()
db = firestore.client()

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login at the main page first.")
    st.stop()

user_id = st.session_state.user

st.title("Energy")
tab_log, tab_stats = st.tabs(["Log Activity", "Analysis"])

with tab_log:
    col1, col2 = st.columns(2)
    
    with col1:
        with st.form("workout_form", clear_on_submit=True):
            st.subheader("Log Workout")
            activity = st.selectbox("Activity", ["Gym", "Yoga", "Running", "Swimming"])
            dur = st.number_input("Duration (mins)", min_value=1)
            cal_map = {"Gym": 7, "Yoga": 3, "Running": 10, "Swimming": 8}
            submitted = st.form_submit_button("Save to Zenith")
            
            if submitted:
                calories = dur * cal_map[activity]
                db.collection("users").document(user_id).collection("workouts").add({
                    "activity": activity,
                    "duration": dur,
                    "calories": calories,
                    "timestamp": firestore.SERVER_TIMESTAMP
                })
                st.success(f"Burned {calories} calories!")

    with col2:
        st.subheader("Sleep Entry")
        sleep_h = st.select_slider("Hours Slept", options=range(0, 13), value=8)
        if st.button("Log Sleep"):
            today_str = date.today().isoformat()
            db.collection("users").document(user_id).collection("logs").document(today_str).set({
                "sleep_hours": sleep_h,
                "date": today_str
            }, merge=True)
            st.toast("Rest logged.")

with tab_stats:
    st.subheader("Weekly Momentum")
    
    workouts_ref = db.collection("users").document(user_id).collection("workouts").stream()
    data = [w.to_dict() for w in workouts_ref]
    
    if data:
        df = pd.DataFrame(data)
        fig = px.bar(df, x="activity", y="calories", color_discrete_sequence=['#2DD4BF'],
                     title="Calories by Activity", template="plotly_dark")
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Start logging to see your Zenith energy stats!")

if st.sidebar.button("LOGOUT"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.switch_page("main.py")
