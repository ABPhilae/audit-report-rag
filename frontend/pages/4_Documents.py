"""Document management page — view and delete indexed reports."""
import streamlit as st
import requests
import os
 
API_URL = os.getenv("API_URL", "http://localhost:8000")
 
st.title("📂 Report Library")
 
if st.button("🔄 Refresh"):
    st.rerun()
 
try:
    resp = requests.get(f"{API_URL}/reports", timeout=5)
    data = resp.json()
 
    st.metric("Total Reports", data["total_reports"])
    st.metric("Total Chunks Indexed", data["total_chunks"])
 
    if not data["reports"]:
        st.info("No reports uploaded yet. Go to the Upload page to add reports.")
    else:
        for report in data["reports"]:
            with st.expander(f"📄 {report['title']}"):
                col1, col2 = st.columns([4, 1])
                col1.write(f"ID: {report['report_id']} | Chunks: {report['chunks']}")
                col1.write(f"Region: {report.get('region', 'N/A')} | Severity: {report.get('severity', 'N/A')}")
                if col2.button("🗑 Delete", key=f"del_{report['report_id']}"):
                    r = requests.delete(f"{API_URL}/reports/{report['report_id']}")
                    if r.status_code == 200: st.success("Deleted"); st.rerun()
 
except requests.exceptions.ConnectionError:
    st.error("Cannot connect to API.")
