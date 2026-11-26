import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(
    page_title="AI Disease Prediction & Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    st.switch_page("pages/01_Home.py")
except Exception:
    import importlib
    importlib.import_module("frontend.pages.01_Home")
