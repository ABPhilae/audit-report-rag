"""Dashboard page — shows overview metrics."""
import streamlit as st
import requests
import os
 
API_URL = os.getenv("API_URL", "http://localhost:8000")
 
st.title("📊 Dashboard")
 
try:
    resp = requests.get(f"{API_URL}/health", timeout=5)
    data = resp.json()
 
    col1, col2, col3 = st.columns(3)
    col1.metric("Reports Indexed", data.get("reports_indexed", 0))
    col2.metric("Total Chunks", data.get("chunks_indexed", 0))
    col3.metric("Regions Covered", len(data.get("regions", [])))
 
    if data.get("regions"):
        st.subheader("Regions in Index")
        st.write(", ".join(data["regions"]))
 
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to the API. Please start the backend first.")
