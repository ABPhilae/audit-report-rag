"""
Audit Intelligence Hub — Main Entry Point.
In multi-page Streamlit apps, app.py is the home page.
Pages in the pages/ folder appear in the sidebar navigation.
"""
import streamlit as st
 
st.set_page_config(
    page_title="Audit Intelligence Hub",
    page_icon="🔍",
    layout="wide"
)
 
st.title("🔍 Audit Report Intelligence Hub")
st.markdown("""
Welcome to the Internal Audit Intelligence Hub.
This system allows you to search across all indexed audit reports
using natural language questions.
 
**Use the navigation on the left to:**
- 📊 **Dashboard** — Overview of indexed reports and metrics
- 📤 **Upload** — Ingest new audit reports
- 💬 **Intelligence** — Ask questions across all reports
- 📂 **Documents** — Manage your report library
""")
