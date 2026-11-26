import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from frontend.utils.api_client import APIClient
from frontend.utils.ui_components import (
    inject_custom_css,
    render_top_navbar,
    render_sidebar,
    render_medical_disclaimer
)

st.set_page_config(
    page_title="Health Library | AI Disease Prediction & Health Assistant",
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
render_top_navbar(active_page="Health Library")
render_sidebar()

# Page Header
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.85rem; font-weight: 800; color: #0F172A; margin: 0 0 4px 0; letter-spacing: -0.025em;">
        📚 Clinical Health & Disease Knowledge Library
    </h1>
    <p style="font-size: 0.98rem; color: #64748B; margin: 0;">
        Browse curated, verified medical information, clinical symptom associations, preventive precautions, and urgent care protocols across 41 pathological conditions.
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch all diseases from database / API
diseases = APIClient.get_diseases()

if not diseases:
    st.error("Unable to load health library data. Please verify database initialization.")
    st.stop()

# Helper function to categorize diseases based on real clinical taxonomies
def get_disease_category(name):
    name_lower = name.lower()
    if any(k in name_lower for k in ["malaria", "dengue", "typhoid", "tuberculosis", "chicken pox", "impetigo", "aids"]):
        return "Infectious & Vector-Borne", "🦟"
    elif any(k in name_lower for k in ["asthma", "pneumonia", "common cold"]):
        return "Respiratory & Pulmonary", "🫁"
    elif any(k in name_lower for k in ["diabetes", "hypertension", "hypothyroidism", "hyperthyroidism", "hypoglycemia"]):
        return "Chronic & Metabolic", "🩸"
    elif any(k in name_lower for k in ["fungal", "acne", "psoriasis", "allergy", "drug reaction"]):
        return "Dermatological & Allergic", "🧴"
    elif any(k in name_lower for k in ["gerd", "peptic ulcer", "gastroenteritis", "jaundice", "hepatitis", "cholestasis"]):
        return "Gastrointestinal & Hepatic", "🫀"
    elif any(k in name_lower for k in ["arthritis", "spondylosis", "migraine", "vertigo", "paralysis"]):
        return "Neurological & Musculoskeletal", "🧠"
    elif any(k in name_lower for k in ["heart attack", "varicose veins", "hemorrhoids"]):
        return "Cardiovascular & Vascular", "❤️"
    elif any(k in name_lower for k in ["urinary tract infection"]):
        return "Urological & Renal", "💧"
    return "General Medical Conditions", "🏥"

# Attach categories and icons
for d in diseases:
    cat, icon = get_disease_category(d["name"])
    d["clinical_category"] = cat
    d["icon"] = icon

# Metric Overview Cards
all_categories = sorted(list(set([d["clinical_category"] for d in diseases])))
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.markdown("""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #F0FDFA; color: #0D9488;">📚</div>
        <div>
            <div class="metric-val">41</div>
            <div class="metric-lbl">Curated Diseases</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #EFF6FF; color: #0284C7;">🗂️</div>
        <div>
            <div class="metric-val">{len(all_categories)}</div>
            <div class="metric-lbl">Clinical Categories</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown("""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #ECFDF5; color: #059669;">🛡️</div>
        <div>
            <div class="metric-val">100%</div>
            <div class="metric-lbl">Verified Guidelines</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown("""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #FFFBEB; color: #D97706;">🏛️</div>
        <div>
            <div class="metric-val">WHO / CDC</div>
            <div class="metric-lbl">Authoritative Data</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Search & Filter Controls
st.markdown("""
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
""", unsafe_allow_html=True)

col_s1, col_s2 = st.columns([2, 1])

with col_s1:
    search_query = st.text_input("🔍 Search Diseases or Associated Symptoms:", placeholder="e.g. Malaria, Dengue, Fever, Cough, Diabetes, Diet...")

with col_s2:
    selected_cat = st.selectbox("Filter by Clinical Category:", ["All Categories"] + all_categories)

st.markdown("</div>", unsafe_allow_html=True)

# Filter Logic
filtered = diseases

if search_query.strip():
    q = search_query.lower()
    filtered = [
        d for d in filtered
        if q in d["name"].lower()
        or q in d.get("description", "").lower()
        or any(q in sym.lower() for sym in d.get("common_symptoms", []))
        or any(q in p.lower() for p in d.get("precautions", []))
    ]

if selected_cat != "All Categories":
    filtered = [d for d in filtered if d["clinical_category"] == selected_cat]

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
    <span style="font-weight: 700; color: #0F172A; font-size: 1.05rem;">
        Available Clinical Guides ({len(filtered)} Conditions)
    </span>
</div>
""", unsafe_allow_html=True)

if not filtered:
    st.markdown("""
    <div class="empty-state-box">
        <div class="empty-state-icon">🔍</div>
        <h3 class="empty-state-title">No Matching Conditions Found</h3>
        <p class="empty-state-desc">
            No disease matched your search query or category filter. Try clearing your search keyword or selecting "All Categories".
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render Disease Articles in clean, responsive cards
    for d in filtered:
        with st.expander(f"{d.get('icon', '🩺')} **{d['name']}** — *{d['clinical_category']}*"):
            st.markdown(f"""
            <div style="padding: 0.5rem 0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 6px;">
                    <span style="background: #F0FDFA; color: #0F766E; border: 1px solid #99F6E4; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.82rem;">
                        {d['clinical_category']}
                    </span>
                    <span style="font-size: 0.8rem; color: #64748B;">
                        Verified Source: <strong>{d.get('source', 'Clinical Reference Database')}</strong>
                    </span>
                </div>
                <h4 style="font-size: 1.15rem; font-weight: 700; color: #0F172A; margin: 0 0 0.5rem 0;">Clinical Overview</h4>
                <p style="font-size: 0.93rem; color: #334155; line-height: 1.6; margin: 0 0 1rem 0;">
                    {d.get('description', 'Comprehensive clinical overview is maintained in the internal knowledge base.')}
                </p>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 🧬 Common Associated Symptoms")
                sym_list = d.get("common_symptoms", [])
                if sym_list:
                    chips_html = "".join([f'<span class="symptom-chip" style="background:#EFF6FF; color:#1E40AF; border-color:#BFDBFE;">• {s}</span>' for s in sym_list])
                    st.markdown(chips_html, unsafe_allow_html=True)
                else:
                    st.caption("Refer to physician for symptom evaluation.")

                st.markdown("<br/>##### 🛡️ General Precautions & Lifestyle Care", unsafe_allow_html=True)
                prec_list = d.get("precautions", [])
                if prec_list:
                    for p in prec_list:
                        st.markdown(f"- {p}")
                else:
                    st.caption("Standard clinical precautions apply.")

            with col2:
                st.markdown("##### 🚨 When to Seek Immediate Medical Help")
                help_text = d.get("when_to_seek_help", "Seek prompt medical care if experiencing worsening fever or severe debility.")
                st.markdown(f"""
                <div style="background: #FEF2F2; border-left: 4px solid #EF4444; border-radius: 8px; padding: 0.9rem 1.1rem; color: #991B1B; font-size: 0.88rem; line-height: 1.5;">
                    <strong>Emergency Criteria:</strong><br/>
                    {help_text}
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br/>", unsafe_allow_html=True)
                if st.button(f"🩺 Check for {d['name']} in Symptom Checker", key=f"btn_check_{d['name']}", use_container_width=True):
                    # Prepopulate symptom checker with symptoms for this disease if possible
                    st.session_state.selected_symptom_names = [s for s in d.get("common_symptoms", [])]
                    st.switch_page("pages/02_Symptom_Checker.py")

# Quick Navigation Footer
st.markdown("<br/>", unsafe_allow_html=True)
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("🩺 Go to Symptom Checker", type="primary", use_container_width=True):
        st.switch_page("pages/02_Symptom_Checker.py")
with col_nav2:
    if st.button("📋 View Health History", type="secondary", use_container_width=True):
        st.switch_page("pages/03_History.py")

# Mandatory Medical Disclaimer
render_medical_disclaimer()
