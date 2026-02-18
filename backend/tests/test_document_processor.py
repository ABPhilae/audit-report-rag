"""Tests for the document processor."""
import pytest
from src.document_processor import chunk_text, extract_audit_metadata
 
def test_chunk_text_basic():
    """Text should be split into multiple chunks."""
    text = "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3."
    chunks = chunk_text(text)
    assert len(chunks) >= 1
 
def test_chunk_text_merges_short():
    """Very short paragraphs should be merged."""
    text = "Short.\n\n" * 10 + "A longer paragraph with more content."
    chunks = chunk_text(text, min_size=50)
    # Should have fewer chunks than input paragraphs
    assert len(chunks) < 11
 
def test_extract_metadata_region():
    """Should extract region from well-formed audit report text."""
    text = "Report Reference: IA-001\nRegion: APAC\nAudit Type: Trade Reconciliation"
    metadata = extract_audit_metadata(text)
    assert metadata["region"] == "APAC"
 
def test_extract_metadata_severity():
    """Should extract severity level."""
    text = "Severity Classification: Critical"
    metadata = extract_audit_metadata(text)
    assert metadata["severity"] == "critical"
 
def test_extract_metadata_defaults():
    """Should return defaults when no patterns found."""
    metadata = extract_audit_metadata("No structured data here.")
    assert metadata["region"] is None
    assert metadata["severity"] is None
