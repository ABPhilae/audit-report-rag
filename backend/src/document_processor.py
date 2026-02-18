"""
Audit Document Processor — Extended with Metadata Extraction.
 
New vs Project 1: Automatically extracts structured metadata from
audit reports (region, severity, audit type, year) so they can
be used for metadata filtering in searches.
"""
import io
import re
import logging
from datetime import datetime
 
logger = logging.getLogger(__name__)
 
 
def extract_text_from_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="ignore")
 
 
def extract_text_from_pdf(content: bytes) -> str:
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n\n".join(
            f"[Page {i+1}]\n{page.extract_text()}"
            for i, page in enumerate(reader.pages)
            if page.extract_text()
        )
    except Exception as e:
        raise RuntimeError(f"PDF extraction failed: {e}")
 
 
def extract_audit_metadata(text: str) -> dict:
    """
    Try to extract audit-specific metadata from the report text.
    Uses simple pattern matching — works for well-structured reports.
    Returns defaults if patterns not found (never crashes).
    """
    metadata = {
        "region": None, "severity": None,
        "audit_type": None, "year": datetime.now().year
    }
 
    # Extract region
    region_match = re.search(r'Region:\s*([^\n]+)', text)
    if region_match:
        metadata["region"] = region_match.group(1).strip()[:50]
 
    # Extract severity
    sev_match = re.search(
        r'Severity Classification:\s*(Critical|High|Medium|Low|Info)',
        text, re.IGNORECASE
    )
    if sev_match:
        metadata["severity"] = sev_match.group(1).lower()
 
    # Extract audit type
    type_match = re.search(r'Audit Type:\s*([^\n]+)', text)
    if type_match:
        metadata["audit_type"] = type_match.group(1).strip()[:100]
 
    # Extract year from date
    year_match = re.search(r'Date:.*?(20\d{2})', text)
    if year_match:
        metadata["year"] = int(year_match.group(1))
 
    logger.info(f"Extracted metadata: {metadata}")
    return metadata
 
 
def chunk_text(text: str, min_size: int = 100, max_size: int = 1000) -> list[str]:
    """Same chunking as Project 1 — reused unchanged."""
    raw = [c.strip() for c in text.split("\n\n") if c.strip()]
    sized = []
    for chunk in raw:
        if len(chunk) <= max_size:
            sized.append(chunk)
        else:
            sents = chunk.replace(". ", ".\n").split("\n")
            curr = ""
            for s in sents:
                if len(curr) + len(s) < max_size: curr += (" " + s if curr else s)
                else:
                    if curr: sized.append(curr.strip())
                    curr = s
            if curr: sized.append(curr.strip())
    final, buf = [], ""
    for c in sized:
        if len(buf) + len(c) < min_size: buf += (" " + c if buf else c)
        else:
            if buf: final.append(buf.strip())
            buf = c
    if buf: final.append(buf.strip())
    return final
 
 
def process_audit_report(filename: str, content: bytes) -> tuple[list[str], dict]:
    """
    Process an audit report file.
    Returns (chunks, metadata) where metadata has region, severity, etc.
    """
    if filename.lower().endswith(".txt"):
        text = extract_text_from_txt(content)
    elif filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(content)
    else:
        raise ValueError(f"Unsupported file type: {filename}")
 
    if not text.strip():
        raise ValueError(f"No text extracted from {filename}")
 
    metadata = extract_audit_metadata(text)
    chunks = chunk_text(text)
    return chunks, metadata
