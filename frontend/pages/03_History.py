import streamlit as st
import pandas as pd
import json
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
    page_title="Health History | AI Disease Prediction & Health Assistant",
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

# Top Navigation Bar & Sidebar
render_top_navbar(active_page="History")
render_sidebar()

user = st.session_state.user
user_id = user.get("id", "guest_user")

# Page Header
st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <h1 style="font-size: 1.85rem; font-weight: 800; color: #0F172A; margin: 0 0 4px 0; letter-spacing: -0.025em;">
        📋 Clinical Prediction History & Tracking Logs
    </h1>
    <p style="font-size: 0.98rem; color: #64748B; margin: 0;">
        Review previous symptom evaluations, compare differential diagnoses, analyze confidence patterns, and export reports.
    </p>
</div>
""", unsafe_allow_html=True)

# Fetch History Records
history = APIClient.get_history(user_id)

if not history:
    st.markdown("""
    <div class="empty-state-box">
        <div class="empty-state-icon">📋</div>
        <h3 class="empty-state-title">No Prediction Records Found</h3>
        <p class="empty-state-desc">
            You currently have no recorded symptom evaluations in this session. Run your first clinical assessment using the Symptom Checker to generate intelligent condition logs here.
        </p>
    </div>
    """, unsafe_allow_html=True)
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("🩺 Go to Symptom Checker", type="primary", use_container_width=True):
            st.switch_page("pages/02_Symptom_Checker.py")
    render_medical_disclaimer()
    st.stop()

# Summary Metric Cards
stats = APIClient.get_prediction_stats(user_id)
col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    st.markdown(f"""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #F0FDFA; color: #0D9488;">📋</div>
        <div>
            <div class="metric-val">{stats.get('total_predictions', len(history))}</div>
            <div class="metric-lbl">Total Records</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_s2:
    st.markdown(f"""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #EFF6FF; color: #0284C7;">🎯</div>
        <div>
            <div class="metric-val">{stats.get('avg_confidence', 0)}%</div>
            <div class="metric-lbl">Avg Confidence</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_s3:
    st.markdown(f"""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #ECFDF5; color: #059669;">🔬</div>
        <div>
            <div class="metric-val">{stats.get('conditions_tested', 0)}</div>
            <div class="metric-lbl">Unique Conditions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_s4:
    top_cond = stats.get('most_frequent_condition', 'N/A')
    st.markdown(f"""
    <div class="metric-tile">
        <div class="metric-icon-wrap" style="background: #FFFBEB; color: #D97706;">🏥</div>
        <div>
            <div class="metric-val" style="font-size: 1.2rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="{top_cond}">{top_cond}</div>
            <div class="metric-lbl">Top Condition</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br/>", unsafe_allow_html=True)

# Search, Filter and Sorting Controls
st.markdown("""
<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 1.2rem; margin-bottom: 1.5rem; box-shadow: 0 2px 6px rgba(0,0,0,0.02);">
""", unsafe_allow_html=True)

col_f1, col_f2, col_f3, col_f4 = st.columns([2, 1.5, 1.5, 1.5])

with col_f1:
    search_query = st.text_input("🔍 Search History:", placeholder="Search by condition or symptom...")

with col_f2:
    all_unique_conds = sorted(list(set([h.get("predicted_condition", "") for h in history if h.get("predicted_condition")])))
    cond_filter = st.selectbox("Filter Condition:", ["All Conditions"] + all_unique_conds)

with col_f3:
    conf_filter = st.selectbox("Confidence Level:", ["All Levels", "High (≥70%)", "Moderate (40-69%)", "Low (<40%)"])

with col_f4:
    sort_option = st.selectbox("Sort By:", ["Newest First", "Oldest First", "Highest Confidence", "Lowest Confidence"])

st.markdown("</div>", unsafe_allow_html=True)

# Apply Filters
filtered_history = history

if search_query.strip():
    q = search_query.lower()
    filtered_history = [
        h for h in filtered_history
        if q in h.get("predicted_condition", "").lower()
        or any(q in s.lower() for s in h.get("input_symptoms", []))
    ]

if cond_filter != "All Conditions":
    filtered_history = [h for h in filtered_history if h.get("predicted_condition") == cond_filter]

if conf_filter == "High (≥70%)":
    filtered_history = [h for h in filtered_history if h.get("prediction_score", 0) >= 0.70]
elif conf_filter == "Moderate (40-69%)":
    filtered_history = [h for h in filtered_history if 0.40 <= h.get("prediction_score", 0) < 0.70]
elif conf_filter == "Low (<40%)":
    filtered_history = [h for h in filtered_history if h.get("prediction_score", 0) < 0.40]

# Apply Sorting
if sort_option == "Newest First":
    filtered_history.sort(key=lambda x: str(x.get("created_at", "")), reverse=True)
elif sort_option == "Oldest First":
    filtered_history.sort(key=lambda x: str(x.get("created_at", "")))
elif sort_option == "Highest Confidence":
    filtered_history.sort(key=lambda x: x.get("prediction_score", 0), reverse=True)
elif sort_option == "Lowest Confidence":
    filtered_history.sort(key=lambda x: x.get("prediction_score", 0))

# Export & Management Toolbar
col_tb1, col_tb2, col_tb3 = st.columns([2, 1, 1])

with col_tb1:
    st.markdown(f"Showing **{len(filtered_history)}** of **{len(history)}** evaluations:")

with col_tb2:
    # CSV Export Button
    if filtered_history:
        export_rows = []
        for h in filtered_history:
            export_rows.append({
                "Date": h.get("created_at"),
                "Condition": h.get("predicted_condition"),
                "Confidence": f"{round(h.get('prediction_score', 0) * 100, 1)}%",
                "Symptoms": ", ".join(h.get("input_symptoms", [])),
                "Model": h.get("model_version")
            })
        df_export = pd.DataFrame(export_rows)
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV Report",
            data=csv_data,
            file_name=f"health_history_{user_id}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col_tb3:
    if st.button("🗑️ Clear Filtered", key="btn_clear_hist", use_container_width=True):
        for item in filtered_history:
            APIClient.delete_history(item.get("id"))
        st.success("Selected records deleted.")
        st.rerun()

# Switchable Views: Cards vs Table
tab_cards, tab_table = st.tabs(["🗂️ Interactive Cards View", "📊 Summary Table View"])

with tab_cards:
    if not filtered_history:
        st.info("No prediction records matched your search filters.")
    else:
        for idx, item in enumerate(filtered_history):
            score_pct = round(item.get("prediction_score", 0) * 100, 1)
            conf_class = "conf-badge-high" if score_pct >= 70 else ("conf-badge-med" if score_pct >= 40 else "conf-badge-low")
            date_str = item.get("created_at", "Date N/A")
            symptoms = item.get("input_symptoms", [])
            top_results = item.get("top_results", [])
            record_id = item.get("id", "N/A")

            st.markdown(f"""
            <div class="health-card" style="margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <span style="font-size: 0.8rem; color: #64748B; font-weight: 600;">🗓️ {date_str}</span>
                        <span style="font-size: 0.78rem; color: #94A3B8; margin-left: 8px;">ID: <code>{record_id[:8]}...</code></span>
                    </div>
                    <span class="{conf_class}">{score_pct}% Match Probability</span>
                </div>
                <h3 style="font-size: 1.3rem; font-weight: 800; color: #0F172A; margin: 0 0 0.6rem 0;">
                    {item.get('predicted_condition', 'Unknown Condition')}
                </h3>
            """, unsafe_allow_html=True)

            col_c1, col_c2 = st.columns([2, 1])

            with col_c1:
                st.markdown("**Evaluated Symptoms:**")
                sym_chips = "".join([f'<span class="symptom-chip">✓ {s.replace("_", " ").title()}</span>' for s in symptoms])
                st.markdown(sym_chips, unsafe_allow_html=True)

                if top_results:
                    st.markdown("<br/>**Differential Candidate Conditions:**", unsafe_allow_html=True)
                    diff_items = []
                    for t in top_results:
                        t_score = round(t.get("score", 0) * 100, 1)
                        diff_items.append(f"• **{t.get('condition')}**: {t_score}%")
                    st.markdown("<br/>".join(diff_items), unsafe_allow_html=True)

            with col_c2:
                st.caption(f"Model Engine: `{item.get('model_version', 'Logistic Regression')}`")
                st.caption(f"Feature Count: {len(symptoms)} inputs")
                
                if st.button("🗑️ Delete Record", key=f"del_card_{record_id}", use_container_width=True):
                    APIClient.delete_history(record_id)
                    st.success("Record deleted successfully.")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

with tab_table:
    if not filtered_history:
        st.info("No records matched your search filters.")
    else:
        table_rows = []
        for h in filtered_history:
            table_rows.append({
                "Date & Time": h.get("created_at"),
                "Primary Condition": h.get("predicted_condition"),
                "Confidence": f"{round(h.get('prediction_score', 0) * 100, 1)}%",
                "Symptoms Count": len(h.get("input_symptoms", [])),
                "Evaluated Symptoms": ", ".join([s.replace("_", " ").title() for s in h.get("input_symptoms", [])]),
                "Model Engine": h.get("model_version")
            })
        df_table = pd.DataFrame(table_rows)
        st.dataframe(df_table, use_container_width=True, hide_index=True)

st.markdown("<br/>", unsafe_allow_html=True)
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("🩺 Start New Symptom Check", type="primary", use_container_width=True):
        st.switch_page("pages/02_Symptom_Checker.py")
with col_nav2:
    if st.button("📚 Browse Medical Knowledge Base", type="secondary", use_container_width=True):
        st.switch_page("pages/04_Health_Library.py")

# Mandatory Medical Disclaimer
render_medical_disclaimer()
