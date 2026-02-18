"""
Audit RAG Service — Extended for Structured Audit Intelligence.
 
New vs Project 1:
- Returns structured JSON with key_findings list
- Supports metadata filtering (region, severity, year)
- Detects cross-report patterns and themes
- Confidence scoring with detailed reasoning
"""
import json
from src.vector_store import audit_vector_store
from src.llm_service import llm_service
from src.models import AuditAnswer, SourceChunk, ConfidenceLevel
import logging
 
logger = logging.getLogger(__name__)
 
AUDIT_RAG_SYSTEM_PROMPT = """You are a Senior Internal Audit Intelligence Analyst.
 
You have access to a set of audit report excerpts. Your job: answer audit questions
with precision, citing specific findings, responsible parties, and deadlines.
 
Rules:
1. Answer ONLY from the provided audit context. Never invent findings.
2. Be specific: include finding IDs, deadlines, responsible parties, regions.
3. When multiple reports are relevant, synthesise patterns across them.
4. If the answer is not in the context, state this clearly.
5. Format key findings as a numbered list when appropriate.
 
Return ONLY a JSON object with this exact structure:
{
  "answer": "Your detailed answer text here",
  "key_findings": ["Finding 1", "Finding 2", ...],
  "confidence": "high|medium|low",
  "reasoning": "Why this confidence level"
}"""
 
 
class AuditRAGService:
    """RAG service optimised for audit intelligence queries."""
 
    def answer_question(
        self, question: str, n_results: int = 5,
        filter_region: str = None,
        filter_severity: str = None,
        filter_year: int = None
    ) -> AuditAnswer:
        """Full RAG pipeline for audit questions with optional filters."""
 
        # ── RETRIEVE ──────────────────────────────────────
        chunks = audit_vector_store.search(
            query=question,
            n_results=n_results,
            filter_region=filter_region,
            filter_severity=filter_severity,
            filter_year=filter_year
        )
 
        if not chunks:
            return AuditAnswer(
                question=question,
                answer="No audit reports have been uploaded, or no reports match the filters.",
                confidence=ConfidenceLevel.HIGH,
                key_findings=[],
                sources=[],
                reports_searched=0,
                total_chunks_searched=0
            )
 
        # ── BUILD CONTEXT ──────────────────────────────────
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            meta_str = f"Report: {chunk['report_title']}"
            if chunk.get("region"): meta_str += f" | Region: {chunk['region']}"
            if chunk.get("severity"): meta_str += f" | Severity: {chunk['severity']}"
            context_parts.append(f"[Excerpt {i} — {meta_str}]\n{chunk['text']}")
        context = "\n\n".join(context_parts)
 
        # ── BUILD PROMPT ───────────────────────────────────
        prompt = (
            f"=== AUDIT REPORT EXCERPTS ===\n{context}\n=== END EXCERPTS ===\n\n"
            f"=== AUDITOR'S QUESTION ===\n{question}\n=== END QUESTION ==="
        )
 
        # ── GENERATE (with JSON output) ────────────────────
        raw = llm_service.generate(
            prompt=prompt,
            system_message=AUDIT_RAG_SYSTEM_PROMPT,
            temperature=0.1
        )
 
        # Parse JSON response from LLM
        try:
            clean = raw.strip()
            if clean.startswith("```"): clean = clean.split("\n", 1)[1]
            if clean.endswith("```"): clean = clean.rsplit("\n", 1)[0]
            data = json.loads(clean)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed, using raw text: {e}")
            data = {"answer": raw, "key_findings": [], "confidence": "medium", "reasoning": ""}
 
        # ── BUILD RESPONSE ─────────────────────────────────
        unique_reports = len(set(c["report_title"] for c in chunks))
 
        return AuditAnswer(
            question=question,
            answer=data.get("answer", raw),
            confidence=ConfidenceLevel(data.get("confidence", "medium")),
            key_findings=data.get("key_findings", []),
            sources=[
                SourceChunk(
                    report_title=c["report_title"],
                    chunk_text=c["text"][:250] + "..." if len(c["text"]) > 250 else c["text"],
                    relevance_score=c["relevance_score"],
                    region=c.get("region"),
                    severity=c.get("severity")
                ) for c in chunks
            ],
            reports_searched=unique_reports,
            total_chunks_searched=audit_vector_store.total_chunks
        )
 
 
audit_rag_service = AuditRAGService()
