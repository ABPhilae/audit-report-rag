"""Intelligence page — Q&A with filters and structured results."""
import streamlit as st
import requests
import os
 
API_URL = os.getenv("API_URL", "http://localhost:8000")
 
st.title("💬 Audit Intelligence")
 
# ── FILTERS ──────────────────────────────────────────────
with st.expander("🔧 Search Filters (optional)"):
    col1, col2, col3 = st.columns(3)
    region = col1.text_input("Filter by Region:", placeholder="e.g. APAC")
    severity = col2.selectbox("Filter by Severity:", ["All", "critical", "high", "medium", "low"])
    year = col3.number_input("Filter by Year:", min_value=2020, max_value=2030, value=0)
 
# ── QUESTION INPUT ───────────────────────────────────────
question = st.text_area("Your question:", height=80,
                        placeholder="e.g. What critical findings had deadlines before March 2026?")
 
col_btn, col_n = st.columns([3, 1])
n_results = col_n.number_input("Sources:", 1, 15, 5)
 
if col_btn.button("🔍 Search Reports", type="primary") and question:
    payload = {
        "question": question,
        "n_results": n_results,
        "filter_region": region or None,
        "filter_severity": None if severity == "All" else severity,
        "filter_year": int(year) if year > 0 else None
    }
 
    with st.spinner("Searching reports and generating answer..."):
        resp = requests.post(f"{API_URL}/intelligence/ask",
                             json=payload, timeout=30)
 
    if resp.status_code == 200:
        data = resp.json()
 
        # Confidence badge
        conf_icons = {"high": "🟢", "medium": "🟡", "low": "🔴"}
        st.markdown(f"**Confidence:** {conf_icons.get(data['confidence'], '⚪')} {data['confidence'].capitalize()}")
        st.caption(f"Searched {data['reports_searched']} reports, {data['total_chunks_searched']} total chunks indexed")
 
        # Main answer
        st.markdown("### Answer")
        st.markdown(data["answer"])
 
        # Key findings
        if data.get("key_findings"):
            st.markdown("### Key Findings")
            for finding in data["key_findings"]:
                st.markdown(f"• {finding}")
 
        # Sources
        if data.get("sources"):
            with st.expander(f"📄 View {len(data['sources'])} source excerpts"):
                for i, src in enumerate(data["sources"], 1):
                    st.markdown(f"**{i}. {src['report_title']}** (relevance: {src['relevance_score']:.0%})")
                    if src.get("region"): st.caption(f"Region: {src['region']} | Severity: {src.get('severity', 'N/A')}")
                    st.info(src["chunk_text"])
    else:
        st.error(f"Error: {resp.json().get('detail', 'Unknown error')}")
