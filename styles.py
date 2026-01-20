import streamlit as st

def apply_zenith_theme():
    """Injects the global Dark Turquoise, Glassmorphism, and Sidebar Hover effects."""
    st.markdown("""
        <style>
        /* 1. The Main Background Gradient */
        .stApp {
            background: linear-gradient(160deg, #020617 0%, #042f2e 50%, #0d9488 100%);
            color: #E2E8F0;
        }

        /* 2. Custom Sidebar Styling & Visibility */
        [data-testid="stSidebar"] {
            background-color: rgba(2, 6, 23, 0.85);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(45, 212, 191, 0.2);
        }
        
        /* Hide sidebar if not authenticated (Manual Override for main.py) */
        .hide-sidebar [data-testid="stSidebar"] {
            display: none;
        }

        /* 3. Sidebar Font Styling: Bold, Capitalized, and Clean */
        [data-testid="stSidebarNav"] ul li a span {
            text-transform: capitalize !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            color: #E2E8F0;
            transition: all 0.3s ease-in-out;
        }

        /* 4. Sidebar Hover 'Pop' Effect */
        [data-testid="stSidebarNav"] ul li a:hover {
            background-color: rgba(45, 212, 191, 0.1) !important;
            border-radius: 15px;
            margin: 0 10px;
        }

        [data-testid="stSidebarNav"] ul li a:hover span {
            color: #2DD4BF !important;
            transform: translateX(10px) scale(1.05);
            display: inline-block;
        }

        /* 5. Glassmorphism Card Style */
        .zenith-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 25px;
            border: 1px solid rgba(45, 212, 191, 0.15);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        
        .zenith-card:hover {
            transform: translateY(-5px);
            border-color: rgba(45, 212, 191, 0.4);
        }

        /* 6. Turquoise Accents for Headers */
        h1, h2, h3 {
            color: #2DD4BF !important;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }

        /* 7. Chic Button Styling */
        .stButton>button {
            background: linear-gradient(90deg, #0d9488 0%, #2dd4bf 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 10px 24px;
            font-weight: 700;
            transition: all 0.3s ease;
            width: 100%;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .stButton>button:hover {
            box-shadow: 0 0 25px rgba(45, 212, 191, 0.5);
            transform: scale(1.02);
            color: white;
        }
        
        /* 8. Progress Bar Color Override */
        .stProgress > div > div > div > div {
            background-color: #2DD4BF;
        }
        </style>
    """, unsafe_allow_html=True)

def zenith_card(title, content):
    """Renders a styled card with a title and body text."""
    st.markdown(f"""
        <div class="zenith-card">
            <h3 style="margin:0 0 10px 0; font-size:1.1rem; letter-spacing:0.5px;">{title}</h3>
            <div style="font-size:0.95rem; line-height:1.5; opacity:0.9;">
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)
