"""
Audit Intelligence Hub — Data Models.
 
These models extend Project 1's models with audit-specific fields:
- ReportMetadata: structured audit report information
- AuditFinding: individual finding with severity and deadline
- AdvancedSearchRequest: includes filters for year, region, severity
- AuditAnswer: includes finding list and cross-report analysis
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
 
class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
 
class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
 
# ── REPORT UPLOAD ─────────────────────────────────────────
class ReportUploadResponse(BaseModel):
    report_id: str
    title: str
    chunks_created: int
    extracted_metadata: dict  # Auto-extracted: region, date, severity
    message: str = "Report processed and indexed for search"
 
# ── SEARCH REQUEST (with filters) ─────────────────────────
class AuditSearchRequest(BaseModel):
    """Advanced search with metadata filters."""
    question: str = Field(
        ..., min_length=5, max_length=500,
        description="Natural language question about audit reports"
    )
    n_results: int = Field(default=5, ge=1, le=15)
    # Optional filters — leave None to search across everything
    filter_region: Optional[str] = Field(None, description="Filter by region (e.g. APAC)")
    filter_severity: Optional[str] = Field(None, description="Filter by severity level")
    filter_year: Optional[int] = Field(None, description="Filter by report year")
 
# ── ANSWER MODELS ─────────────────────────────────────────
class SourceChunk(BaseModel):
    """A retrieved document chunk used to generate the answer."""
    report_title: str
    chunk_text: str
    relevance_score: float
    region: Optional[str] = None
    severity: Optional[str] = None
 
class AuditAnswer(BaseModel):
    """Complete structured response to an audit question."""
    question: str
    answer: str
    confidence: ConfidenceLevel
    key_findings: List[str] = []  # Bullet-point findings extracted from answer
    sources: List[SourceChunk] = []
    reports_searched: int
    total_chunks_searched: int
 
# ── DOCUMENT MANAGEMENT ───────────────────────────────────
class ReportRecord(BaseModel):
    report_id: str
    title: str
    chunks: int
    uploaded_at: str
    region: Optional[str] = None
    severity: Optional[str] = None
    audit_type: Optional[str] = None
 
class ReportsListResponse(BaseModel):
    reports: List[ReportRecord]
    total_reports: int
    total_chunks: int
    regions: List[str]  # Unique regions in the index
