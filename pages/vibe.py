import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_admin import firestore
from datetime import date
from styles import apply_zenith_theme, zenith_card

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.warning("Please login at the main page first.")
    st.stop()

apply_zenith_theme()
db = firestore.client()
user_id = st.session_state.user

st.title("The Vibe Room")

with st.container():
    zenith_card("How are you today?", "Select an emoji to log your daily frequency.")    
    mood_map = {"😫": 1, "😐": 2, "🙂": 3, "🔥": 4, "✨": 5}
    cols = st.columns(len(mood_map))
    
    for i, (emoji, val) in enumerate(mood_map.items()):
        if cols[i].button(emoji, key=f"mood_{i}", use_container_width=True):
            today = date.today().isoformat()
            db.collection("users").document(user_id).collection("vibe_logs").document(today).set({
                "mood_val": val,
                "mood_emoji": emoji,
                "date": today
            }, merge=True)
            st.success(f"Vibe caught: {emoji}")

st.divider()

st.subheader("Monthly Frequency")
logs = db.collection("users").document(user_id).collection("vibe_logs").stream()
data = [l.to_dict() for l in logs]

if data:
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    fig = px.line(df.sort_values('date'), x="date", y="mood_val", 
                  markers=True, title="Mood Frequency",
                  color_discrete_sequence=['#2DD4BF'], template="plotly_dark")
    fig.update_yaxes(range=[0.5, 5.5], tickvals=[1,2,3,4,5], 
                     ticktext=["😫", "😐", "🙂", "🔥", "✨"])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Log your mood to see your frequency chart.")

st.divider()

tab_f, tab_watch = st.tabs(["🎡 The F-Zone", "🎬 Watchlist Progress"])

with tab_f:
    col_list, col_input = st.columns([2, 1])
    
    with col_input:
        with st.form("f_zone_form", clear_on_submit=True):
            st.subheader("Add New Goal")
            st.caption("Fun • Friends • Food")
            new_f = st.text_input("What's next?", placeholder="Skydiving?")
            if st.form_submit_button("Add to Bucketlist"):
                if new_f:
                    db.collection("users").document(user_id).collection("bucketlist").add({
                        "item": new_f, "done": False, "created_at": firestore.SERVER_TIMESTAMP
                    })
                    st.rerun()

    with col_list:
        st.subheader("Your Bucketlist")
        items = db.collection("users").document(user_id).collection("bucketlist").stream()
        for item in items:
            d = item.to_dict()
            if st.checkbox(d['item'], value=d['done'], key=item.id):
                if not d['done']: 
                    db.collection("users").document(user_id).collection("bucketlist").document(item.id).update({"done": True})
                    st.balloons()
                    st.rerun()

with tab_watch:
    col_w_list, col_w_input = st.columns([2, 1])
    
    with col_w_input:
        with st.expander("Add New Title", expanded=True):
            s_name = st.text_input("Show/Movie Name")
            s_total = st.number_input("Total Episodes", min_value=1)
            if st.button("Add to Watchlist"):
                if s_name:
                    db.collection("users").document(user_id).collection("shows").add({
                        "name": s_name, "total": s_total, "current": 0
                    })
                    st.rerun()

    with col_w_list:
        st.subheader("Currently Watching")
        shows = db.collection("users").document(user_id).collection("shows").stream()
        for s in shows:
            s_data = s.to_dict()
            progress = s_data['current'] / s_data['total']
            
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"**{s_data['name']}**")
                c1.progress(progress, text=f"Progress: {int(progress*100)}%")
                
                if c2.button(f"Ep {s_data['current']} +", key=f"show_{s.id}"):
                    if s_data['current'] < s_data['total']:
                        db.collection("users").document(user_id).collection("shows").document(s.id).update({"current": s_data['current'] + 1})
                        st.rerun()

if st.sidebar.button("LOGOUT"):
    st.session_state.authenticated = False
    st.session_state.user = None
    st.switch_page("main.py")
