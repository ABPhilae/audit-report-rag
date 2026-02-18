"""Audit Report Intelligence Hub — FastAPI Backend."""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.models import (
    ReportUploadResponse, AuditSearchRequest, AuditAnswer,
    ReportsListResponse, ReportRecord
)
from src.vector_store import audit_vector_store
from src.rag_service import audit_rag_service
from src.document_processor import process_audit_report
from src.config import settings
from datetime import datetime
import logging
 
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)
 
app = FastAPI(
    title="Audit Report Intelligence Hub API",
    description="Semantic search and Q&A across audit reports.",
    version="1.0.0"
)
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])
 
@app.get("/health")
async def health_check():
    reports = audit_vector_store.list_reports()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "reports_indexed": len(reports),
        "chunks_indexed": audit_vector_store.total_chunks,
        "regions": audit_vector_store.get_regions()
    }
 
@app.post("/reports/upload", response_model=ReportUploadResponse)
async def upload_report(file: UploadFile = File(...)):
    """Upload and ingest an audit report with automatic metadata extraction."""
    if not file.filename.endswith((".txt", ".pdf")):
        raise HTTPException(400, "Only .txt and .pdf files are supported")
    try:
        content = await file.read()
        chunks, metadata = process_audit_report(file.filename, content)
        report_id = audit_vector_store.add_report(
            title=file.filename, chunks=chunks,
            region=metadata.get("region"),
            severity=metadata.get("severity"),
            audit_type=metadata.get("audit_type"),
            year=metadata.get("year")
        )
        return ReportUploadResponse(
            report_id=report_id, title=file.filename,
            chunks_created=len(chunks), extracted_metadata=metadata
        )
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(500, "Report processing failed")
 
@app.get("/reports", response_model=ReportsListResponse)
async def list_reports():
    reports = audit_vector_store.list_reports()
    return ReportsListResponse(
        reports=[ReportRecord(**r) for r in reports],
        total_reports=len(reports),
        total_chunks=audit_vector_store.total_chunks,
        regions=audit_vector_store.get_regions()
    )
 
@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    if not audit_vector_store.delete_report(report_id):
        raise HTTPException(404, "Report not found")
    return {"message": f"Report {report_id} deleted"}
 
@app.post("/intelligence/ask", response_model=AuditAnswer)
async def ask_audit_question(request: AuditSearchRequest):
    """Ask a natural language question across all indexed audit reports."""
    logger.info(f"Audit question: {request.question[:80]}")
    try:
        return audit_rag_service.answer_question(
            question=request.question,
            n_results=request.n_results,
            filter_region=request.filter_region,
            filter_severity=request.filter_severity,
            filter_year=request.filter_year
        )
    except Exception as e:
        logger.error(f"Question failed: {e}")
        raise HTTPException(500, "Failed to generate answer")
