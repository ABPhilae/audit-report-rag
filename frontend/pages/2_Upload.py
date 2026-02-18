"""Upload page — ingest audit reports."""
import streamlit as st
import requests
import os
 
API_URL = os.getenv("API_URL", "http://localhost:8000")
 
st.title("📤 Upload Audit Reports")
st.markdown("Upload audit reports (PDF or TXT). Metadata is extracted automatically.")
 
uploaded = st.file_uploader("Choose audit report", type=["pdf", "txt"])
 
if uploaded and st.button("📤 Ingest Report", type="primary"):
    with st.spinner("Processing and embedding report..."):
        resp = requests.post(
            f"{API_URL}/reports/upload",
            files={"file": (uploaded.name, uploaded.getvalue(), "application/octet-stream")},
            timeout=120
        )
        if resp.status_code == 200:
            data = resp.json()
            st.success(f"✅ Ingested: {data['title']} | {data['chunks_created']} chunks")
            meta = data.get("extracted_metadata", {})
            if any(meta.values()):
                st.info(
                    f"Auto-detected: Region={meta.get('region','N/A')} | "
                    f"Severity={meta.get('severity','N/A')} | "
                    f"Type={meta.get('audit_type','N/A')}"
                )
        else:
            st.error(f"Upload failed: {resp.json().get('detail', 'Error')}")

