import streamlit as st
import pandas as pd
from firebase_admin import firestore
from datetime import datetime, date
from styles import apply_zenith_theme, zenith_card

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login at the main page first.")
    st.stop()

apply_zenith_theme()
db = firestore.client()
user_id = st.session_state.user

st.title("Velocity")

with st.sidebar:
    st.subheader("Key Deadlines")
    deadline_name = st.text_input("Event Name")
    deadline_date = st.date_input("Date", min_value=date.today())
    if st.button("Set Reminder"):
        if deadline_name:
            db.collection("users").document(user_id).collection("deadlines").add({
                "event": deadline_name,
                "date": deadline_date.isoformat()
            })
            st.rerun()

    deadlines = db.collection("users").document(user_id).collection("deadlines").stream()
    for d in deadlines:
        data = d.to_dict()
        days_left = (date.fromisoformat(data['date']) - date.today()).days
        if days_left >= 0:
            st.warning(f"**{data['event']}** is in **{days_left} days**")

st.divider()

def render_tasks(status, column):
    tasks = db.collection("users").document(user_id).collection("tasks").where("status", "==", status).stream()
    with column:
        st.subheader(f"{status}")
        for task in tasks:
            t_data = task.to_dict()
            with st.container(border=True):
                st.write(t_data['task'])
                if status != "Done":
                    if st.button("Move →", key=f"btn_{task.id}"):
                        next_status = "To Do" if status == "Remind" else "Done"
                        db.collection("users").document(user_id).collection("tasks").document(task.id).update({"status": next_status})
                        st.rerun()

col_remind, col_todo, col_done = st.columns(3)

new_task = st.text_input("New Task Name", placeholder="e.g., Study Cloud Computing")
if st.button("Add to Engine"):
    if new_task:
        db.collection("users").document(user_id).collection("tasks").add({
            "task": new_task,
            "status": "Remind",
            "created_at": firestore.SERVER_TIMESTAMP
        })
        st.rerun()

render_tasks("Remind", col_remind)
render_tasks("To Do", col_todo)
render_tasks("Done", col_done)

if st.sidebar.button("LOGOUT"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.switch_page("main.py")
