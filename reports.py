import firebase_admin
from firebase_admin import firestore, credentials
import pandas as pd
import streamlit as st
import smtplib
from email.message import EmailMessage

if not firebase_admin._apps:
    try:
        cred_dict = dict(st.secrets["firebase"])
        cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except:
        pass 

db = firestore.client()

def generate_full_zenith_report(user_id):
    """Aggregates data from all 4 tabs for a single user."""
    user_ref = db.collection("users").document(user_id)
    user_info = user_ref.get().to_dict() or {}
    vibe_type = user_info.get('vibe', 'Ascending')
    email = user_info.get('email', 'Zenith User')

    workouts = list(user_ref.collection("workouts").stream())
    w_data = [w.to_dict() for w in workouts]
    total_cals = sum(d.get('calories', 0) for d in w_data)
    fav_activity = pd.DataFrame(w_data)['activity'].mode()[0] if w_data else "Consistency"

    vibe_logs = list(user_ref.collection("vibe_logs").stream())
    v_data = [v.to_dict() for v in vibe_logs]
    avg_mood = pd.DataFrame(v_data)['mood_val'].mean() if v_data else 0.0

    tasks = list(user_ref.collection("tasks").stream())
    t_data = [t.to_dict() for t in tasks]
    completed = sum(1 for d in t_data if d.get('status') == 'Done')

    finance = list(user_ref.collection("finance").stream())
    f_data = [f.to_dict() for f in finance]
    total_savings = sum(d.get('amount', 0) for d in f_data if d.get('type') == 'Saving')

    report_body = f"""
ZENITH ASCENSION REPORT
-------------------------------
User: {email}
Current Vibe: {vibe_type}

ENERGY:
Total Calories Burned: {total_cals} kcal
Your Power Activity: {fav_activity}

VIBE:
Average Frequency: {avg_mood:.1f} / 5.0

VELOCITY:
Tasks Crushed: {completed}

LIFESTYLE:
Total Capital Growth: ₹{total_savings}

-------------------------------
Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}
KEEP ELEVATING YOUR FREQUENCY.
    """
    return report_body, email

def send_email_report(receiver_email, report_content):
    """Sends the report via Gmail SMTP using Streamlit Secrets."""
    try:
        sender_email = st.secrets["email"]["sender"]
        sender_password = st.secrets["email"]["password"]

        msg = EmailMessage()
        msg.set_content(report_content)
        msg["Subject"] = "Your Zenith Ascension Report"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"Email Error: {e}")
        return False
