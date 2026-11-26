import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.api_client import APIClient
from frontend.utils.ui_components import (
    inject_custom_css,
    render_top_navbar,
    render_sidebar,
    render_medical_disclaimer,
    get_medical_chart_layout
)

st.set_page_config(
    page_title="Symptom Checker | AI Disease Prediction & Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom medical styling
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

if "selected_symptom_names" not in st.session_state:
    st.session_state.selected_symptom_names = []

# Top Navigation Bar & Sidebar
render_top_navbar(active_page="Symptom Checker")
render_sidebar()

# Page Header
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.85rem; font-weight: 800; color: #0F172A; margin: 0 0 4px 0; letter-spacing: -0.025em;">
        🔎 AI Clinical Symptom Checker & Prediction Engine
    </h1>
    <p style="font-size: 0.98rem; color: #64748B; margin: 0;">
        Select your observed clinical indicators, describe symptoms in natural language, or use demo presets to calculate multi-class disease probability distributions.
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch Symptoms Catalog
symptoms_data = APIClient.get_symptoms()

if not symptoms_data:
    st.error("Unable to load symptoms catalog from database or API. Please verify the system setup.")
    st.stop()

# Build symptom mappings
categories = sorted(list(set([s["category"] for s in symptoms_data if s.get("category")])))
all_symptom_map = {s["display_name"]: s["name"] for s in symptoms_data}
raw_to_display = {s["name"]: s["display_name"] for s in symptoms_data}

# Preset Symptom Bundles for Rapid Testing & Examiner Presentations
st.markdown("""
<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.6rem;">
    <span style="font-size: 0.88rem; font-weight: 700; color: #334155;">⚡ Quick Symptom Presets (Click to Auto-fill):</span>
</div>
""", unsafe_allow_html=True)

col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)

with col_p1:
    if st.button("🦟 Malaria Symptoms", key="preset_malaria", use_container_width=True):
        st.session_state.selected_symptom_names = ["Chills", "High Fever", "Headache", "Nausea", "Muscle Pain"]
        st.rerun()

with col_p2:
    if st.button("🌡️ Dengue Symptoms", key="preset_dengue", use_container_width=True):
        st.session_state.selected_symptom_names = ["High Fever", "Skin Rash", "Chills", "Joint Pain", "Headache", "Loss Of Appetite"]
        st.rerun()

with col_p3:
    if st.button("🧠 Migraine Symptoms", key="preset_migraine", use_container_width=True):
        st.session_state.selected_symptom_names = ["Headache", "Visual Disturbances", "Acidity", "Indigestion", "Stiff Neck"]
        st.rerun()

with col_p4:
    if st.button("🫁 Bronchial Asthma", key="preset_asthma", use_container_width=True):
        st.session_state.selected_symptom_names = ["Fatigue", "Cough", "High Fever", "Breathlessness", "Mucoid Sputum"]
        st.rerun()

with col_p5:
    if st.button("🧹 Clear Selection", key="preset_clear", use_container_width=True):
        st.session_state.selected_symptom_names = []
        if "last_prediction" in st.session_state:
            del st.session_state["last_prediction"]
        st.rerun()

st.markdown("<br/>", unsafe_allow_html=True)

# Step 1: Symptom Selection Interface
st.markdown("""
<div class="health-card" style="margin-bottom: 1.5rem;">
    <h3 style="font-size: 1.2rem; font-weight: 700; color: #0F172A; margin: 0 0 1rem 0;">
        Step 1: Select or Search Observed Symptoms
    </h3>
""", unsafe_allow_html=True)

col_cat, col_search = st.columns([1, 2])

with col_cat:
    selected_category = st.selectbox(
        "Filter by Symptom Category",
        ["All Categories"] + categories,
        index=0,
        help="Filter symptoms by anatomical system"
    )

filtered_symptoms = symptoms_data
if selected_category != "All Categories":
    filtered_symptoms = [s for s in symptoms_data if s.get("category") == selected_category]

category_options = [s["display_name"] for s in filtered_symptoms]

with col_search:
    selected_display_names = st.multiselect(
        "Choose Symptoms from Catalog",
        options=sorted(list(all_symptom_map.keys())),
        default=[s for s in st.session_state.selected_symptom_names if s in all_symptom_map],
        placeholder="Type or select symptoms (e.g., Fever, Cough, Chills, Fatigue)...",
        help="You can select multiple symptoms from across all categories"
    )
    # Sync with session state
    st.session_state.selected_symptom_names = selected_display_names

# Natural Language Free-Text Parser Expander
with st.expander("💬 Optional: Describe Symptoms in Natural Language (AI Text Parser)"):
    st.markdown("""
    <p style="font-size: 0.88rem; color: #64748B; margin-bottom: 0.5rem;">
        Type how you are feeling in plain English, and our clinical keyword parser will automatically match predefined symptoms:
    </p>
    """, unsafe_allow_html=True)
    free_text = st.text_area(
        "Natural language description:",
        placeholder="e.g. I have been having high fever, severe headache, chills and nausea for two days...",
        label_visibility="collapsed"
    )
    if st.button("✨ Parse Text & Add Symptoms", key="btn_parse_text"):
        if free_text.strip():
            matched_disp = []
            text_lower = free_text.lower()
            for disp, raw in all_symptom_map.items():
                clean_raw = raw.replace("_", " ").lower()
                clean_disp = disp.lower()
                if clean_raw in text_lower or clean_disp in text_lower:
                    matched_disp.append(disp)
            if matched_disp:
                new_selection = list(set(st.session_state.selected_symptom_names + matched_disp))
                st.session_state.selected_symptom_names = new_selection
                st.success(f"Recognized {len(matched_disp)} symptoms: {', '.join(matched_disp)}")
                st.rerun()
            else:
                st.warning("No matching predefined medical symptoms were identified. Please select from the dropdown above.")

st.markdown("</div>", unsafe_allow_html=True)

# Convert display names to raw feature names
selected_raw_symptoms = [all_symptom_map[disp] for disp in st.session_state.selected_symptom_names if disp in all_symptom_map]

# Step 2: Selected Symptoms Review & Emergency Scanner
if selected_raw_symptoms:
    st.markdown(f"""
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem;">
            <span style="font-weight: 700; color: #0F172A; font-size: 0.95rem;">
                Selected Symptoms Review ({len(selected_raw_symptoms)} active):
            </span>
            <span style="font-size: 0.8rem; color: #0D9488; font-weight: 600;">Vector Ready</span>
        </div>
        <div>
            {"".join([f'<span class="symptom-chip">✓ {raw_to_display.get(s, s)}</span>' for s in selected_raw_symptoms])}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Emergency Red-Flag Scanner
CRITICAL_RED_FLAGS = {
    "chest_pain": "Chest Pain may indicate acute coronary syndrome or cardiopulmonary emergency.",
    "slurred_speech": "Slurred speech or facial weakness is a primary symptom of acute stroke.",
    "weakness_of_one_body_side": "Sudden unilateral motor weakness is a clinical stroke red flag.",
    "altered_sensorium": "Altered sensorium or delirium requires urgent neurological evaluation.",
    "coma": "Loss of consciousness is a critical life-threatening emergency.",
    "acute_liver_failure": "Signs of acute hepatic failure require immediate intensive hospital care.",
    "blood_in_sputum": "Hemoptysis (blood in sputum) warrants immediate pulmonology/emergency evaluation."
}

detected_emergency = [s for s in selected_raw_symptoms if s in CRITICAL_RED_FLAGS]

if detected_emergency:
    warning_items = "".join([f"<li><strong>{raw_to_display.get(s, s)}</strong>: {CRITICAL_RED_FLAGS[s]}</li>" for s in detected_emergency])
    st.markdown(f"""
    <div class="emergency-banner">
        <div class="emergency-header">
            <span>🚨</span>
            <span>URGENT CLINICAL ALERT: Critical Red-Flag Symptoms Detected</span>
        </div>
        <p class="emergency-text">
            You have selected one or more symptoms classified as immediate medical red flags:
        </p>
        <ul style="margin: 0.4rem 0 0.6rem 1.2rem; color: #991B1B; font-size: 0.88rem;">
            {warning_items}
        </ul>
        <p class="emergency-text" style="font-weight: 700;">
            ⚠️ Do not delay seeking medical attention. Contact your local emergency services (112 / 911) or proceed immediately to an emergency care department.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Analyze Button Trigger
col_btn1, col_btn2 = st.columns([3, 1])

with col_btn1:
    btn_predict = st.button("🔬 Analyze Symptoms & Run AI Prediction", type="primary", use_container_width=True)

with col_btn2:
    if st.button("🔄 Reset Form", use_container_width=True):
        st.session_state.selected_symptom_names = []
        if "last_prediction" in st.session_state:
            del st.session_state["last_prediction"]
        st.rerun()

if btn_predict:
    if not selected_raw_symptoms:
        st.error("⚠️ Please select at least one symptom to evaluate.")
    else:
        with st.spinner("Processing symptom vector & querying ML ensemble model..."):
            user_id = st.session_state.user.get("id", "guest_user")
            res = APIClient.predict(selected_raw_symptoms, user_id=user_id)

        if res and res.get("status") == "success":
            st.session_state["last_prediction"] = res
            st.success("Analysis complete! Review your clinical model insights below.")
        else:
            msg = res.get("message", "Prediction analysis failed. Please verify your symptom selection.") if res else "Prediction analysis failed."
            st.error(f"Prediction Error: {msg}")

# Step 3: Present Prediction Results
if "last_prediction" in st.session_state:
    res = st.session_state["last_prediction"]
    results = res.get("results", [])
    primary = res.get("primary_prediction", {})
    score_pct = round(primary.get("score", 0) * 100, 1) if primary else 0

    st.markdown("---")
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="font-size: 1.6rem; font-weight: 800; color: #0F172A; margin: 0 0 4px 0; letter-spacing: -0.02em;">
            📊 Clinical Model Assessment Results
        </h2>
        <p style="font-size: 0.92rem; color: #64748B; margin: 0;">
            Estimated probability distribution generated by the multi-class clinical ensemble model.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_res1, col_res2 = st.columns([1, 1])

    with col_res1:
        conf_tier = "High Clinical Correlation" if score_pct >= 70 else ("Moderate Correlation" if score_pct >= 40 else "Low / Inconclusive Correlation")
        tier_color = "#0D9488" if score_pct >= 70 else ("#0284C7" if score_pct >= 40 else "#D97706")

        st.markdown(f"""
        <div class="result-primary-card">
            <span class="result-badge">Primary Model Match</span>
            <h3 class="result-condition">{primary.get('condition', 'N/A')}</h3>
            <div class="result-score" style="color: {tier_color};">{score_pct}%</div>
            <div class="result-score-lbl">Model Confidence Probability</div>
            <div style="margin-top: 1rem; padding-top: 0.8rem; border-top: 1px solid #F1F5F9; font-size: 0.85rem; color: #64748B;">
                Assessment Tier: <strong style="color: {tier_color};">{conf_tier}</strong><br/>
                Engine: <code>{res.get('model_version', 'Logistic Regression')}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_res2:
        # Plotly Horizontal Bar Chart of Ranked Probabilities
        if results:
            chart_data = [{"Condition": r["condition"], "Probability (%)": round(r["score"] * 100, 1)} for r in results]
            fig = px.bar(
                chart_data,
                x="Probability (%)",
                y="Condition",
                orientation="h",
                text="Probability (%)",
                color="Probability (%)",
                color_continuous_scale=[[0, "#E0F2FE"], [0.5, "#0D9488"], [1, "#0F766E"]]
            )
            fig.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside',
                marker=dict(line=dict(width=0))
            )
            layout_dict = get_medical_chart_layout(title="Ranked Differential Probability Distribution", height=250)
            fig.update_layout(**layout_dict)
            st.plotly_chart(fig, use_container_width=True)

    # Explainable AI (XAI) - Symptom Attribution Weights
    st.markdown("""
    <div style="margin-top: 1.5rem; margin-bottom: 0.8rem;">
        <h3 style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 0 0 4px 0;">
            💡 Explainable AI (Feature Attribution Weights)
        </h3>
        <p style="font-size: 0.88rem; color: #64748B; margin: 0;">
            Relative contribution of each evaluated symptom towards the primary predicted condition ({top_cond}).
        </p>
    </div>
    """.format(top_cond=primary.get('condition', 'Condition')), unsafe_allow_html=True)

    explainability = res.get("explainability", {}).get("symptom_contributions", [])
    if explainability:
        exp_data = [{
            "Symptom": raw_to_display.get(e["symptom"], e["symptom"].replace("_", " ").title()),
            "Relative Weight (%)": round(e["importance"] * 100, 1)
        } for e in explainability]
        
        fig_exp = px.bar(
            exp_data,
            x="Symptom",
            y="Relative Weight (%)",
            text="Relative Weight (%)",
            color="Relative Weight (%)",
            color_continuous_scale=[[0, "#EFF6FF"], [0.5, "#0284C7"], [1, "#1E3A8A"]]
        )
        fig_exp.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_exp.update_layout(
            height=240,
            margin=dict(l=10, r=20, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Plus Jakarta Sans", color="#475569"),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
            xaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_exp, use_container_width=True)

    # Structured Disease Knowledge Base & Care Guidelines
    st.markdown("""
    <div style="margin-top: 1.5rem; margin-bottom: 0.8rem;">
        <h3 style="font-size: 1.25rem; font-weight: 700; color: #0F172A; margin: 0 0 4px 0;">
            📚 Clinical Condition Information & Patient Guidance
        </h3>
    </div>
    """, unsafe_allow_html=True)

    diseases = APIClient.get_diseases()
    disease_map = {d["name"]: d for d in diseases}
    top_condition_name = primary.get("condition")
    d_info = disease_map.get(top_condition_name)

    if d_info:
        tab_ov, tab_prec, tab_care = st.tabs(["📖 Overview", "🛡️ General Precautions", "🚨 When to Seek Care"])
        
        with tab_ov:
            st.markdown(f"**Description & Pathological Overview:**")
            st.write(d_info.get("description", "No description available."))
            common_syms = d_info.get("common_symptoms", [])
            if common_syms:
                st.markdown("**Common Associated Symptoms:**")
                sym_chips = "".join([f'<span class="symptom-chip" style="background:#EFF6FF; color:#1E40AF; border-color:#BFDBFE;">• {s}</span>' for s in common_syms])
                st.markdown(sym_chips, unsafe_allow_html=True)

        with tab_prec:
            st.markdown(f"**Recommended Lifestyle, Dietary & Clinical Precautions:**")
            for p in d_info.get("precautions", []):
                st.markdown(f"- {p}")

        with tab_care:
            st.markdown(f"**Clinical Warning Signs & Emergency Consultation:**")
            st.warning(d_info.get("when_to_seek_help", "Consult a licensed healthcare practitioner if symptoms worsen or persist."))
            st.caption(f"Medical Reference: {d_info.get('source', 'Verified Clinical Knowledge Base')}")
    else:
        st.info(f"Detailed health library documentation for {top_condition_name} will be available in future releases.")

    # Interactive Feedback Section
    st.markdown("""
    <div style="margin-top: 1.8rem; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
        <h4 style="font-size: 1rem; font-weight: 700; color: #0F172A; margin: 0 0 0.8rem 0;">
            💬 Was this AI evaluation helpful for your research or demonstration?
        </h4>
    </div>
    """, unsafe_allow_html=True)

    col_fb1, col_fb2, col_fb_txt = st.columns([1, 1, 3])
    fb_submitted = None

    if col_fb1.button("👍 Yes, Helpful", key="fb_yes", use_container_width=True):
        fb_submitted = 1

    if col_fb2.button("👎 Needs Improvement", key="fb_no", use_container_width=True):
        fb_submitted = 0

    comment = col_fb_txt.text_input("Optional feedback comments:", key="fb_txt", placeholder="e.g. Good symptom correlation...")

    if fb_submitted is not None:
        pred_id = res.get("prediction_id", "demo_id")
        user_id = st.session_state.user.get("id", "guest_user")
        APIClient.submit_feedback(pred_id, fb_submitted, comment, user_id)
        st.success("✅ Thank you! Your feedback has been logged to the database.")

    # Action buttons
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("📋 View in Health History", key="btn_goto_hist", use_container_width=True):
            st.switch_page("pages/03_History.py")
    with col_nav2:
        if st.button("📚 Browse Full Health Library", key="btn_goto_lib", use_container_width=True):
            st.switch_page("pages/04_Health_Library.py")

# Mandatory Medical Disclaimer
render_medical_disclaimer()
