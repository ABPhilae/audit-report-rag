"""
Extended Vector Store with Metadata Filtering.
 
New capability vs Project 1:
- Store region, severity, audit_type as searchable metadata
- Filter search results by region, severity, or year
- Get statistics about the indexed content
 
ChromaDB's WHERE clause works like SQL WHERE:
  collection.query(query_embeddings=[...], where={"region": "APAC"})
Returns only chunks from APAC reports.
"""
import chromadb
from src.config import settings
from src.embedding_service import embedding_service
import logging
import uuid
from datetime import datetime
 
logger = logging.getLogger(__name__)
 
class AuditVectorStore:
    """ChromaDB store optimised for audit report search with filtering."""
 
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name="audit_reports",
            metadata={"hnsw:space": "cosine"}
        )
        self._report_registry: dict = {}
 
    def add_report(self, title: str, chunks: list[str],
                   region: str = None, severity: str = None,
                   audit_type: str = None, year: int = None) -> str:
        """Ingest an audit report with metadata for filtering."""
        report_id = str(uuid.uuid4())[:8]
        uploaded_at = datetime.utcnow().isoformat()
        year_val = year or datetime.now().year
 
        logger.info(f"Embedding {len(chunks)} chunks for '{title}'")
        embeddings = embedding_service.embed_batch(chunks)
 
        chunk_ids = [f"{report_id}_chunk_{i}" for i in range(len(chunks))]
 
        # Metadata stored with each chunk — enables filtering later
        metadatas = [{
            "report_id": report_id,
            "report_title": title,
            "chunk_index": i,
            "uploaded_at": uploaded_at,
            # These fields enable the WHERE filtering:
            "region": region or "unknown",
            "severity": severity or "unknown",
            "audit_type": audit_type or "unknown",
            "year": year_val
        } for i in range(len(chunks))]
 
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
            ids=chunk_ids
        )
 
        self._report_registry[report_id] = {
            "title": title, "chunks": len(chunks),
            "uploaded_at": uploaded_at, "region": region,
            "severity": severity, "audit_type": audit_type
        }
        return report_id
 
    def search(self, query: str, n_results: int = 5,
               filter_region: str = None,
               filter_severity: str = None,
               filter_year: int = None) -> list[dict]:
        """
        Semantic search with optional metadata filters.
        
        Examples:
            search("access control findings")  # All reports
            search("access control", filter_region="APAC")  # APAC only
            search("critical issues", filter_severity="critical")  # Critical only
        """
        query_embedding = embedding_service.embed_text(query)
 
        # Build ChromaDB WHERE clause from filters
        where = None
        filters = {}
        if filter_region:
            filters["region"] = filter_region
        if filter_severity:
            filters["severity"] = filter_severity
        if filter_year:
            filters["year"] = filter_year
        if len(filters) == 1:
            where = filters  # Single filter
        elif len(filters) > 1:
            where = {"$and": [{k: v} for k, v in filters.items()]}  # Multiple filters
 
        count = self.collection.count()
        if count == 0:
            return []
 
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(n_results, count),
            where=where,
            include=["documents", "metadatas", "distances"]
        )
 
        return [
            {
                "text": doc,
                "report_title": meta.get("report_title", "Unknown"),
                "report_id": meta.get("report_id", ""),
                "region": meta.get("region"),
                "severity": meta.get("severity"),
                "relevance_score": round(1 - dist, 4)
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
 
    def list_reports(self) -> list[dict]:
        return [{"report_id": rid, **meta} for rid, meta in self._report_registry.items()]
 
    def get_regions(self) -> list[str]:
        """Return list of unique regions in the index."""
        return list({
            meta.get("region", "unknown")
            for meta in self._report_registry.values()
            if meta.get("region")
        })
 
    def delete_report(self, report_id: str) -> bool:
        if report_id not in self._report_registry:
            return False
        ids = self.collection.get(where={"report_id": report_id}, include=[])["ids"]
        if ids:
            self.collection.delete(ids=ids)
        del self._report_registry[report_id]
        return True
 
    @property
    def total_chunks(self) -> int:
        return self.collection.count()
 
audit_vector_store = AuditVectorStore()
