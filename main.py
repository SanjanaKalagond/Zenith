import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth, firestore
from styles import apply_zenith_theme, zenith_card
from reports import generate_full_zenith_report, send_email_report
import pandas as pd
import time
import re
import requests

# 1. Page Config
st.set_page_config(
    page_title="Zenith", 
    page_icon="", 
    layout="wide" if st.session_state.get("authenticated") else "centered", 
    initial_sidebar_state="expanded"
)

apply_zenith_theme()

if not firebase_admin._apps:
    try:
        cred_dict = dict(st.secrets["firebase"])
        cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")    
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Initialization Error: {e}")

db = firestore.client()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def verify_user_credentials(email, password):
    """Authenticates user via Firebase REST API and checks verification status."""
    try:
        api_key = st.secrets["firebase"]["api_key"]
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}
        response = requests.post(url, json=payload)
        res_data = response.json()

        if "error" in res_data:
            return False, res_data["error"]["message"]

        local_id = res_data["localId"]
        user_info = auth.get_user(local_id)

        # STRICT VERIFICATION CHECK
        if not user_info.email_verified:
            return False, "EMAIL_NOT_VERIFIED"

        return True, local_id
    except Exception as e:
        return False, str(e)

if st.session_state.get("authenticated"):
    if st.sidebar.button("LOGOUT OF ZENITH"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

if not st.session_state.get("authenticated"):
    st.markdown('<style>section[data-testid="stSidebarNav"] {display: none !important;}</style>', unsafe_allow_html=True)
    
    st.title("Zenith")
    st.subheader("Elevate your frequency.")

    mode = st.tabs(["Login", "Sign Up"])

    with mode[1]: 
        with st.form("signup"):
            email = st.text_input("Legit Email ID")
            pwd = st.text_input("Password", type="password")
            vibe = st.selectbox("Choose Monthly Vibe", ["Growth", "Focus", "Zen", "Energy"])
            if st.form_submit_button("CREATE ACCOUNT"):
                if not is_valid_email(email):
                    st.error("Please enter a valid email address.")
                elif len(pwd) < 6:
                    st.error("Password should be at least 6 characters.")
                else:
                    try:
                        user = auth.create_user(email=email, password=pwd)
                        db.collection("users").document(user.uid).set({
                            "email": email, "vibe": vibe, "created_at": firestore.SERVER_TIMESTAMP
                        })
                        
                        link = auth.generate_email_verification_link(email)
                        v_body = f"Welcome to Zenith. Verify your frequency here: {link}"
                        send_email_report(email, v_body)
                        
                        st.success("Account Created! Verify your email link to enter.")
                    except Exception as e:
                        st.error(f"Signup failed: {e}")

    with mode[0]: 
        with st.form("login"):
            l_email = st.text_input("Email")
            l_pwd = st.text_input("Password", type="password")
            if st.form_submit_button("ENTER ZENITH"):
                success, result = verify_user_credentials(l_email, l_pwd)
                if success:
                    st.session_state.user = result
                    st.session_state.authenticated = True
                    st.success("Identity Verified.")
                    time.sleep(0.5)
                    st.rerun()
                elif result == "EMAIL_NOT_VERIFIED":
                    st.warning("Access Denied: Email not verified. Please check your inbox.")
                else:
                    st.error("Invalid credentials.")

else:
    st.markdown('<style>section[data-testid="stSidebarNav"] {display: block !important;}</style>', unsafe_allow_html=True)
    
    user_id = st.session_state.user
    user_ref = db.collection("users").document(user_id)
    user_data = user_ref.get().to_dict()

    st.title("Zenith Hub")
    st.caption(f"Connected: {user_data.get('email', 'User Profile')}")

    col1, col2 = st.columns(2)
    with col1:
        workouts = user_ref.collection("workouts").stream()
        w_list = [w.to_dict() for w in workouts]
        total_cals = sum(d.get('calories', 0) for d in w_list)
        zenith_card("Energy", f"Burned {total_cals} kcal across {len(w_list)} sessions.")

        tasks = user_ref.collection("tasks").stream()
        t_list = [t.to_dict() for t in tasks]
        todo_count = sum(1 for d in t_list if d.get('status') == "To Do")
        zenith_card("Velocity", f"{todo_count} tasks active out of {len(t_list)} total.")

    with col2:
        vibe_logs = user_ref.collection("vibe_logs").order_by("date", direction=firestore.Query.DESCENDING).limit(1).stream()
        latest_mood = next((v.to_dict().get('mood_emoji', "🙂") for v in vibe_logs), "Not logged today")
        zenith_card("Vibe", f"Latest Frequency: {latest_mood}")

        finance = user_ref.collection("finance").stream()
        f_list = [f.to_dict() for f in finance]
        savings = sum(d.get('amount', 0) for d in f_list if d.get('type') == 'Saving')
        zenith_card("Lifestyle", f"Total Savings: ₹{savings}")

    st.divider()
    st.subheader("Quick Actions")
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    if action_col1.button("Log Workout"): st.switch_page("pages/energy.py")
    if action_col2.button("Log Mood"): st.switch_page("pages/vibe.py")
    if action_col3.button("View Tasks"): st.switch_page("pages/velocity.py")
    if action_col4.button("Check Budget"): st.switch_page("pages/lifestyle.py")

    st.divider()
    st.subheader("Your Zenith Analytics")
    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        if st.button("Generate My Ascension Report"):
            report_text, user_email = generate_full_zenith_report(user_id)
            st.text_area("Preview", value=report_text, height=200)
    with col_rep2:
        if st.button("Email Me the Report"):
            report_text, user_email = generate_full_zenith_report(user_id)
            if send_email_report(user_email, report_text):
                st.success("Report Sent!")
                st.balloons()
