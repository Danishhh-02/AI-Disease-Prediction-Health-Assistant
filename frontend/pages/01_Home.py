import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.api_client import APIClient
from frontend.utils.ui_components import (
    inject_custom_css,
    render_top_navbar,
    render_sidebar,
    render_medical_disclaimer
)

st.set_page_config(
    page_title="Home Dashboard | AI Disease Prediction & Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply unified design system styling
inject_custom_css()

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = {
        "id": "guest_user",
        "email": "user@health.ai",
        "full_name": "Guest User",
        "role": "USER",
        "is_authenticated": False
    }

# Top Navigation Bar & Sidebar
render_top_navbar(active_page="Home")
render_sidebar()

user = st.session_state.user
user_name = user.get("full_name", "User")

# Dynamic Time-of-Day Greeting
hour = datetime.now().hour
if hour < 12:
    time_greeting = "Good Morning"
elif hour < 17:
    time_greeting = "Good Afternoon"
else:
    time_greeting = "Good Evening"

# Welcome Section
st.markdown(f"""
<div style="margin-bottom: 1.2rem;">
    <h1 style="font-size: 1.85rem; font-weight: 800; color: #0F172A; margin: 0 0 4px 0; letter-spacing: -0.025em;">
        {time_greeting}, {user_name}! 👋
    </h1>
    <p style="font-size: 0.98rem; color: #64748B; margin: 0;">
        Welcome to your intelligent clinical health assistant & AI disease risk estimation platform.
    </p>
</div>
""", unsafe_allow_html=True)

# Prominent Hero Section
st.markdown("""
<div class="hero-banner">
    <div class="hero-tag">Clinical Decision Support & Predictive AI</div>
    <h2 class="hero-title">AI-Powered Disease Prediction & Health Guidance</h2>
    <p class="hero-description">
        Leverage machine learning algorithms trained on clinical symptom-disease datasets to evaluate health indicators, 
        inspect mathematical feature attribution weights, explore differential conditions, and review verified medical guidance in real time.
    </p>
    <div class="hero-stats-row">
        <div class="hero-stat-pill">🩺 41 Clinical Disease Profiles</div>
        <div class="hero-stat-pill">🧬 131 Validated Symptom Inputs</div>
        <div class="hero-stat-pill">🎯 99.42% ML Model Accuracy</div>
        <div class="hero-stat-pill">💡 Explainable Feature Weights</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Quick Action Cards
st.markdown("""
<h3 style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 0 0 1rem 0; letter-spacing: -0.01em;">
    ⚡ Quick Actions
</h3>
""", unsafe_allow_html=True)

col_act1, col_act2, col_act3 = st.columns(3)

with col_act1:
    st.markdown("""
    <div class="health-card">
        <div class="card-header-icon" style="background:#F0FDFA; color:#0D9488; border-color:#CCFBF1;">🩺</div>
        <h4 class="card-title">Symptom Checker</h4>
        <p class="card-desc">
            Select or describe your symptoms to receive multi-model predicted conditions, probability distributions, and emergency checks.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🩺 Check Symptoms Now", key="btn_home_sym", type="primary", use_container_width=True):
        st.switch_page("pages/02_Symptom_Checker.py")

with col_act2:
    st.markdown("""
    <div class="health-card">
        <div class="card-header-icon" style="background:#EFF6FF; color:#0284C7; border-color:#DBEAFE;">📋</div>
        <h4 class="card-title">Health History</h4>
        <p class="card-desc">
            Review past symptom evaluations, track condition trends over time, compare probability scores, and export records.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📋 View Health History", key="btn_home_hist", type="secondary", use_container_width=True):
        st.switch_page("pages/03_History.py")

with col_act3:
    st.markdown("""
    <div class="health-card">
        <div class="card-header-icon" style="background:#ECFDF5; color:#10B981; border-color:#D1FAE5;">📚</div>
        <h4 class="card-title">Health Library</h4>
        <p class="card-desc">
            Browse verified medical condition summaries, common symptoms, preventive precautions, and when to seek urgent clinical care.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📚 Explore Health Library", key="btn_home_lib", type="secondary", use_container_width=True):
        st.switch_page("pages/04_Health_Library.py")

st.markdown("<br/>", unsafe_allow_html=True)

# Health Overview Cards (Live Database & ML Metrics)
st.markdown("""
<h3 style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 0 0 1rem 0; letter-spacing: -0.01em;">
    📊 Clinical Knowledge & Platform Overview
</h3>
""", unsafe_allow_html=True)

stats = APIClient.get_prediction_stats(user.get("id"))
recent_preds = APIClient.get_recent_predictions(user.get("id"), limit=3)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown("""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #F0FDFA; color: #0D9488;">🏥</div>
        <div>
            <div class="metric-val">41</div>
            <div class="metric-lbl">Trained Conditions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown("""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #EFF6FF; color: #0284C7;">🧬</div>
        <div>
            <div class="metric-val">131</div>
            <div class="metric-lbl">Symptom Features</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown("""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #ECFDF5; color: #059669;">🎯</div>
        <div>
            <div class="metric-val">99.4%</div>
            <div class="metric-lbl">Model Accuracy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    total_count = stats.get("total_predictions", 0)
    st.markdown(f"""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #FFFBEB; color: #D97706;">📈</div>
        <div>
            <div class="metric-val">{total_count}</div>
            <div class="metric-lbl">Evaluations Logged</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Recent Activity and Previous Prediction Summaries
st.markdown("""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.9rem;">
    <h3 style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 0; letter-spacing: -0.01em;">
        🕒 Recent Health Evaluations
    </h3>
</div>
""", unsafe_allow_html=True)

if not recent_preds:
    st.markdown("""
    <div class="empty-state-box">
        <div class="empty-state-icon">📋</div>
        <h4 class="empty-state-title">No Previous Evaluations Recorded</h4>
        <p class="empty-state-desc">
            You haven't run any symptom evaluations yet. Start your first clinical check to see intelligent condition probability rankings, explainable symptom contributions, and personalized guidance.
        </p>
    </div>
    """, unsafe_allow_html=True)
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    with col_cta2:
        if st.button("🩺 Start Your First Symptom Check", key="btn_empty_start", type="primary", use_container_width=True):
            st.switch_page("pages/02_Symptom_Checker.py")
else:
    col_rec = st.columns(len(recent_preds))
    for i, pred in enumerate(recent_preds):
        score_pct = round(pred.get("prediction_score", 0) * 100, 1)
        conf_class = "conf-badge-high" if score_pct >= 70 else ("conf-badge-med" if score_pct >= 40 else "conf-badge-low")
        date_str = pred.get("created_at", "Recent")
        symptoms_list = pred.get("input_symptoms", [])
        
        with col_rec[i]:
            sym_chips = "".join([f'<span class="symptom-chip">✓ {s.replace("_", " ").title()}</span>' for s in symptoms_list[:3]])
            if len(symptoms_list) > 3:
                sym_chips += f'<span class="symptom-chip" style="background:#F1F5F9; color:#64748B; border-color:#E2E8F0;">+{len(symptoms_list)-3} more</span>'

            st.markdown(f"""
            <div class="health-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
                    <span style="font-size: 0.78rem; color: #64748B; font-weight: 600;">🗓️ {date_str}</span>
                    <span class="{conf_class}">{score_pct}% Match</span>
                </div>
                <h4 style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin: 0 0 0.5rem 0;">
                    {pred.get('predicted_condition', 'Unknown Condition')}
                </h4>
                <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.5rem; font-weight: 600;">Evaluated Symptoms:</div>
                <div style="min-height: 48px; margin-bottom: 0.8rem;">
                    {sym_chips}
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"View Details #{i+1}", key=f"rec_btn_{i}", use_container_width=True):
                st.switch_page("pages/03_History.py")

st.markdown("<br/>", unsafe_allow_html=True)

# System Architecture & Academic Project Workflow (B.Tech Presentation Ready!)
with st.expander("🔬 Academic Project Architecture & Machine Learning Pipeline"):
    st.markdown("""
    #### 🏗️ System Workflow & Machine Learning Pipeline
    This system was developed as a final-year B.Tech Computer Science AI & Data Science project. 
    It combines multi-class clinical classification with explainable AI principles:

    1. **Symptom Vectorization**: Maps selected clinical indicators into a 131-dimensional binary feature vector.
    2. **Multi-Algorithm Evaluation**: Evaluated against 5 algorithms: Logistic Regression, Decision Tree, Random Forest, Support Vector Machine, and XGBoost.
    3. **Best Model Selection**: Deploys the best performing classifier with a macro F1-score of **0.9926** and accuracy of **99.42%**.
    4. **Explainable AI (XAI)**: Calculates symptom attribution weights using model coefficients and feature importance distributions.
    5. **Clinical Decision Guidance**: Synthesizes verified medical knowledge (precautions, common symptoms, red flags) for patient decision support.
    """)

# Mandatory Medical Disclaimer
render_medical_disclaimer()
