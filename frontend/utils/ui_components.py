"""
UI Components & Design System for AI Disease Prediction & Health Assistant
Provides unified aesthetics, typography, color palettes, responsive layouts,
and consistent navigation components across all pages.
"""

import streamlit as st
from datetime import datetime

def inject_custom_css():
    """Injects high-end medical dashboard CSS stylesheet across the Streamlit app."""
    st.markdown("""
    <style>
        /* Google Fonts Import */
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        /* Root CSS Variables */
        :root {
            --bg-main: #F8FAFC;
            --card-bg: #FFFFFF;
            --primary-teal: #0D9488;
            --primary-teal-dark: #0F766E;
            --primary-teal-light: #F0FDFA;
            --medical-blue: #0284C7;
            --medical-blue-dark: #1E3A8A;
            --medical-blue-light: #E0F2FE;
            --clinical-green: #10B981;
            --clinical-green-light: #ECFDF5;
            --danger-red: #EF4444;
            --danger-red-light: #FEF2F2;
            --warning-amber: #F59E0B;
            --warning-amber-light: #FFFBEB;
            --text-primary: #0F172A;
            --text-secondary: #475569;
            --text-muted: #94A3B8;
            --border-subtle: #E2E8F0;
            --border-accent: #99F6E4;
            --radius-md: 12px;
            --radius-lg: 16px;
            --radius-xl: 20px;
        }

        /* Master Page Styling */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0F172A;
        }

        .stApp {
            background-color: #F8FAFC;
        }

        /* Hide unwanted default Streamlit chrome */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header[data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.85);
            backdrop-filter: blur(8px);
        }

        /* Container Padding Adjustments */
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 1320px;
        }

        @media (max-width: 768px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1rem;
            }
        }

        /* Top Bar Styling */
        .top-navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 0.9rem 1.6rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.05);
        }
        .navbar-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .navbar-logo-icon {
            font-size: 1.8rem;
            line-height: 1;
            background: #F0FDFA;
            padding: 6px;
            border-radius: 10px;
            border: 1px solid #CCFBF1;
        }
        .navbar-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #0F172A;
            margin: 0;
            letter-spacing: -0.02em;
        }
        .navbar-sub {
            font-size: 0.8rem;
            color: #64748B;
            margin: 0;
        }
        .navbar-status-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #ECFDF5;
            color: #065F46;
            font-size: 0.8rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
            border: 1px solid #A7F3D0;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            background-color: #10B981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.3);
        }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #0F766E 0%, #0369A1 55%, #1E3A8A 100%);
            border-radius: 20px;
            padding: 2.2rem 2.5rem;
            color: #FFFFFF;
            margin-bottom: 1.8rem;
            box-shadow: 0 12px 30px -8px rgba(15, 118, 110, 0.28);
            position: relative;
            overflow: hidden;
        }
        .hero-banner::after {
            content: '';
            position: absolute;
            top: -50px;
            right: -50px;
            width: 200px;
            height: 200px;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 50%;
            pointer-events: none;
        }
        .hero-tag {
            display: inline-block;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.03em;
            text-transform: uppercase;
            margin-bottom: 0.8rem;
        }
        .hero-title {
            font-size: 2.1rem;
            font-weight: 800;
            line-height: 1.2;
            margin: 0 0 0.6rem 0;
            letter-spacing: -0.03em;
        }
        .hero-description {
            font-size: 1.05rem;
            line-height: 1.5;
            color: #F1F5F9;
            max-width: 800px;
            margin: 0;
            opacity: 0.95;
        }

        /* Glassmorphic Badge Pill inside Hero */
        .hero-stats-row {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 1.4rem;
        }
        .hero-stat-pill {
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.25);
            padding: 6px 14px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* Universal Health Card */
        .health-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            height: 100%;
        }
        .health-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 24px -4px rgba(13, 148, 136, 0.1);
            border-color: #CBD5E1;
        }
        .card-header-icon {
            width: 48px;
            height: 48px;
            border-radius: 12px;
            background: #F0FDFA;
            border: 1px solid #CCFBF1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            margin-bottom: 1rem;
        }
        .card-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #0F172A;
            margin: 0 0 0.4rem 0;
            letter-spacing: -0.01em;
        }
        .card-desc {
            font-size: 0.92rem;
            color: #64748B;
            line-height: 1.5;
            margin: 0 0 1.2rem 0;
        }

        /* Metric Tiles */
        .metric-tile {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            box-shadow: 0 2px 8px -2px rgba(15, 23, 42, 0.04);
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .metric-icon-wrap {
            width: 46px;
            height: 46px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.4rem;
            flex-shrink: 0;
        }
        .metric-val {
            font-size: 1.65rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }
        .metric-lbl {
            font-size: 0.82rem;
            color: #64748B;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 2px;
        }

        /* Selected Symptom Chips */
        .symptom-chip {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: #F0FDFA;
            color: #0F766E;
            border: 1px solid #99F6E4;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.86rem;
            font-weight: 600;
            margin: 3px 4px 3px 0;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
        }

        /* Emergency Urgent Alert Banner */
        .emergency-banner {
            background-color: #FEF2F2;
            border: 1px solid #FECACA;
            border-left: 6px solid #EF4444;
            border-radius: 12px;
            padding: 1.2rem 1.5rem;
            color: #991B1B;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px -2px rgba(239, 68, 68, 0.12);
        }
        .emergency-header {
            font-size: 1.05rem;
            font-weight: 800;
            margin: 0 0 0.4rem 0;
            display: flex;
            align-items: center;
            gap: 8px;
            letter-spacing: -0.01em;
        }
        .emergency-text {
            font-size: 0.9rem;
            line-height: 1.5;
            margin: 0;
            color: #7F1D1D;
        }

        /* Disclaimer Notice Card */
        .disclaimer-card {
            background-color: #FFFBEB;
            border: 1px solid #FDE68A;
            border-left: 5px solid #F59E0B;
            border-radius: 12px;
            padding: 1.1rem 1.4rem;
            color: #92400E;
            font-size: 0.88rem;
            line-height: 1.55;
            margin-top: 1.8rem;
            margin-bottom: 1rem;
        }
        .disclaimer-title {
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 0.3rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Primary Diagnostic Result Card */
        .result-primary-card {
            background: #FFFFFF;
            border: 2px solid #0D9488;
            border-radius: 18px;
            padding: 1.8rem;
            text-align: center;
            box-shadow: 0 8px 25px -4px rgba(13, 148, 136, 0.15);
            position: relative;
        }
        .result-badge {
            display: inline-block;
            background: #CCFBF1;
            color: #0F766E;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 0.6rem;
        }
        .result-condition {
            font-size: 1.9rem;
            font-weight: 800;
            color: #0F172A;
            margin: 0 0 0.5rem 0;
            letter-spacing: -0.02em;
        }
        .result-score {
            font-size: 3rem;
            font-weight: 800;
            color: #0F766E;
            line-height: 1;
            margin: 0.5rem 0 0.3rem 0;
            letter-spacing: -0.03em;
        }
        .result-score-lbl {
            font-size: 0.85rem;
            color: #64748B;
            font-weight: 600;
        }

        /* Empty State Box */
        .empty-state-box {
            background: #FFFFFF;
            border: 2px dashed #CBD5E1;
            border-radius: 18px;
            padding: 3rem 2rem;
            text-align: center;
            margin: 1.5rem 0;
        }
        .empty-state-icon {
            font-size: 3rem;
            margin-bottom: 0.8rem;
            color: #94A3B8;
        }
        .empty-state-title {
            font-size: 1.25rem;
            font-weight: 700;
            color: #1E293B;
            margin: 0 0 0.4rem 0;
        }
        .empty-state-desc {
            font-size: 0.92rem;
            color: #64748B;
            max-width: 480px;
            margin: 0 auto 1.5rem auto;
            line-height: 1.5;
        }

        /* Streamlit Input & Widget Polish */
        .stButton button[kind="primary"] {
            background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%) !important;
            border: none !important;
            border-radius: 10px !important;
            color: white !important;
            font-weight: 600 !important;
            padding: 0.65rem 1.4rem !important;
            font-size: 0.95rem !important;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.25) !important;
            transition: all 0.2s ease !important;
        }
        .stButton button[kind="primary"]:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 18px rgba(13, 148, 136, 0.35) !important;
            opacity: 0.96 !important;
        }
        .stButton button[kind="secondary"] {
            background: #FFFFFF !important;
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            color: #0F172A !important;
            font-weight: 600 !important;
            padding: 0.65rem 1.2rem !important;
            transition: all 0.2s ease !important;
        }
        .stButton button[kind="secondary"]:hover {
            border-color: #0D9488 !important;
            background: #F0FDFA !important;
            color: #0F766E !important;
        }

        /* Streamlit Multiselect & Selectbox styling */
        .stMultiSelect, .stSelectbox {
            font-family: inherit;
        }
        div[data-baseweb="select"] {
            border-radius: 10px !important;
            border-color: #CBD5E1 !important;
        }
        div[data-baseweb="select"]:focus-within {
            border-color: #0D9488 !important;
            box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
        }

        /* Streamlit Expander styling */
        .streamlit-expanderHeader {
            font-weight: 600 !important;
            color: #1E293B !important;
            border-radius: 10px !important;
        }
        div[data-testid="stExpander"] {
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
            background: #FFFFFF !important;
            margin-bottom: 0.8rem !important;
        }

        /* History Table Badge Styles */
        .conf-badge-high {
            background: #ECFDF5;
            color: #065F46;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.8rem;
            border: 1px solid #A7F3D0;
        }
        .conf-badge-med {
            background: #EFF6FF;
            color: #1E40AF;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.8rem;
            border: 1px solid #BFDBFE;
        }
        .conf-badge-low {
            background: #FFFBEB;
            color: #92400E;
            padding: 3px 10px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.8rem;
            border: 1px solid #FDE68A;
        }
    </style>
    """, unsafe_allow_html=True)

def render_top_navbar(active_page="Home"):
    """Renders a polished top navigation bar with live status and user badge."""
    user = st.session_state.get("user", {
        "full_name": "Guest User",
        "role": "USER",
        "is_authenticated": False
    })
    
    role_pill = "🛡️ Admin" if user.get("role") == "ADMIN" else "👤 Patient / User"
    auth_color = "#0284C7" if user.get("role") == "ADMIN" else "#0D9488"
    
    st.markdown(f"""
    <div class="top-navbar">
        <div class="navbar-brand">
            <div class="navbar-logo-icon">🩺</div>
            <div>
                <h2 class="navbar-title">AI Disease Prediction & Health Assistant</h2>
                <p class="navbar-sub">Academic ML Clinical Decision Support Platform </p>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 14px; flex-wrap: wrap;">
            <div class="navbar-status-badge">
                <span class="pulse-dot"></span>
                <span>Active ML Ensemble • 99.4% Acc</span>
            </div>
            <div style="background: #F1F5F9; padding: 4px 12px; border-radius: 20px; font-size: 0.82rem; font-weight: 600; color: #334155; border: 1px solid #E2E8F0;">
                {user.get('full_name', 'Guest User')} ({role_pill})
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renders a unified, modern sidebar with user profile, quick persona switcher, and status."""
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <div style="display: inline-flex; align-items: center; justify-content: center; width: 56px; height: 56px; background: linear-gradient(135deg, #0D9488 0%, #0284C7 100%); border-radius: 16px; font-size: 1.9rem; color: white; box-shadow: 0 6px 16px rgba(13, 148, 136, 0.3); margin-bottom: 0.6rem;">
            🩺
        </div>
        <h3 style="margin: 0; font-size: 1.25rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">HealthAI Studio</h3>
        <p style="margin: 2px 0 0 0; font-size: 0.78rem; color: #64748B; font-weight: 500;">Clinical ML Decision Support v2.4</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize user state if needed
    if "user" not in st.session_state:
        st.session_state.user = {
            "id": "guest_user",
            "email": "user@health.ai",
            "full_name": "Guest User",
            "role": "USER",
            "is_authenticated": False
        }

    user = st.session_state.user
    role_text = "System Administrator" if user.get("role") == "ADMIN" else "Verified User"
    avatar_initials = "".join([part[0] for part in user.get("full_name", "GU").split()[:2]]).upper()

    # User Profile Section
    st.sidebar.markdown(f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1rem; margin-bottom: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #0F766E, #0284C7); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.95rem;">
                {avatar_initials}
            </div>
            <div style="overflow: hidden;">
                <div style="font-weight: 700; font-size: 0.92rem; color: #0F172A; white-space: nowrap; text-overflow: ellipsis;">{user.get('full_name')}</div>
                <div style="font-size: 0.76rem; color: #64748B;">{role_text}</div>
            </div>
        </div>
        <div style="margin-top: 0.7rem; padding-top: 0.6rem; border-top: 1px solid #F1F5F9; display: flex; justify-content: space-between; font-size: 0.76rem; color: #64748B;">
            <span>Mode: <strong>{user.get('role')}</strong></span>
            <span>Status: <strong style="color: #10B981;">● Online</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Demo Persona Switcher (Crucial for final-year project demonstration!)
    st.sidebar.markdown("##### ⚡ Project Demo Switcher")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("👤 User Demo", key="sb_btn_user", use_container_width=True):
            st.session_state.user = {
                "id": "user_demo_id",
                "email": "user@health.ai",
                "full_name": "Demo Health User",
                "role": "USER",
                "is_authenticated": True
            }
            st.rerun()

    with col2:
        if st.button("🛡️ Admin Demo", key="sb_btn_admin", use_container_width=True):
            st.session_state.user = {
                "id": "admin_demo_id",
                "email": "admin@health.ai",
                "full_name": "System Administrator",
                "role": "ADMIN",
                "is_authenticated": True
            }
            st.rerun()

    if user.get("is_authenticated"):
        if st.sidebar.button("↩️ Reset to Guest Session", key="sb_btn_logout", use_container_width=True):
            st.session_state.user = {
                "id": "guest_user",
                "email": "guest@health.ai",
                "full_name": "Guest User",
                "role": "USER",
                "is_authenticated": False
            }
            st.rerun()

    st.sidebar.markdown("---")

    # System Diagnostics Pill
    st.sidebar.markdown("""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 0.8rem 1rem; font-size: 0.8rem; margin-bottom: 1.2rem;">
        <div style="font-weight: 700; color: #334155; margin-bottom: 4px;">🔬 ML Model Architecture</div>
        <div style="color: #64748B; font-size: 0.78rem; line-height: 1.4;">
            • Model: <strong>Logistic Regression Ensemble</strong><br/>
            • Training Accuracy: <strong>99.42%</strong><br/>
            • Classes: <strong>41 Clinical Conditions</strong><br/>
            • Features: <strong>131 Symptom Inputs</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Official Medical Notice
    st.sidebar.markdown("""
    <div style="background-color: #FFFBEB; border: 1px solid #FDE68A; border-radius: 10px; padding: 0.8rem 1rem; font-size: 0.78rem; color: #92400E; line-height: 1.45;">
        <strong>⚠️ Academic Disclaimer:</strong><br/>
        This system is an AI/ML decision-support project for educational evaluation only. It does NOT provide clinical diagnoses.
    </div>
    """, unsafe_allow_html=True)

def render_medical_disclaimer():
    """Renders the standard clinical decision support notice on prediction and home pages."""
    st.markdown("""
    <div class="disclaimer-card">
        <div class="disclaimer-title">⚠️ Mandatory Clinical & Educational Disclaimer</div>
        <div>
            This application is an educational machine-learning demonstration developed for academic decision-support research. 
            Predicted conditions and confidence scores are calculated using statistical pattern recognition on trained symptom datasets 
            and do <strong>NOT</strong> constitute a clinical diagnosis, professional medical judgment, prescription, or therapeutic recommendation. 
            If you or someone around you is experiencing sudden, severe, or life-threatening symptoms (e.g. crushing chest pain, slurred speech, sudden loss of consciousness), 
            immediately contact your local emergency services (112 / 911) or visit the nearest emergency medical department.
        </div>
    </div>
    """, unsafe_allow_html=True)

def get_medical_chart_layout(title="Probability Distribution", height=240):
    """Returns a standardized modern Plotly layout for medical charts."""
    return dict(
        title=dict(text=title, font=dict(family="Plus Jakarta Sans", size=14, color="#0F172A", weight=700)),
        height=height,
        margin=dict(l=10, r=20, t=35, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", color="#475569"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            zeroline=False,
            tickfont=dict(size=11, color="#64748B")
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=12, color="#1E293B", weight=600),
            categoryorder="total ascending"
        )
    )
