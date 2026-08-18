from typing import List, Dict, Any, Optional
from datetime import datetime
from app.services.rag.document_loader import document_loader
from app.services.rag.chunker import chunker
from app.services.rag.vector_store import vector_store
from app.services.rag.retriever import retriever

class RAGService:
    """
    AEGIS Central RAG Service.
    Indexes SOP guidelines, coordinates semantic retrieval, and grounds
    AI decision recommendations in verified emergency doctrine.
    """
    def __init__(self):
        self._is_initialized = False
        self.initialize_index()

    def initialize_index(self):
        """Loads built-in SOP guidelines and constructs vector store index."""
        docs = document_loader.load_all_documents()
        all_chunks: List[Dict[str, Any]] = []
        for d in docs:
            chunks = chunker.chunk_document(d)
            all_chunks.extend(chunks)

        vector_store.index_chunks(all_chunks)
        self._is_initialized = True

    def query_knowledge_base(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes a RAG query and formats structured retrieved guidance with document citations.
        """
        if not self._is_initialized:
            self.initialize_index()

        results = retriever.retrieve(query=query, top_k=top_k, category=category)

        guidance_points = []
        citations = []
        for r in results:
            # Extract key operational takeaway from chunk
            first_line = r["text"].split("\n")[0].strip("- ")
            guidance_points.append(f"[{r['doc_id']}] {r['title']}: {first_line}")
            citations.append({
                "doc_id": r["doc_id"],
                "title": r["title"],
                "source": r["source"],
                "category": r["category"],
                "relevance_score": r["relevance_score"],
                "snippet": r["text"][:220] + "..." if len(r["text"]) > 220 else r["text"]
            })

        return {
            "query": query,
            "retrieved_count": len(results),
            "guidance_summary": guidance_points,
            "citations": citations,
            "top_match": results[0] if results else None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source_type": "RAG (Verified Emergency SOP Documents)"
        }

    def get_documents_catalog(self) -> List[Dict[str, Any]]:
        """Returns metadata for all indexed emergency SOP documents."""
        docs = document_loader.load_all_documents()
        return [
            {
                "id": d["id"],
                "title": d["title"],
                "category": d["category"],
                "source": d["source"],
                "last_revised": d.get("last_revised", "2026-08-15"),
                "summary": d["content"].strip().split("\n")[0]
            }
            for d in docs
        ]

    def get_status(self) -> Dict[str, Any]:
        stats = vector_store.get_stats()
        return {
            "status": "OPERATIONAL",
            "mode": "LOCAL RAG LAYER (Zero External Credential Dependency)",
            "total_documents": len(document_loader.load_all_documents()),
            **stats,
            "embedding_provider": "Deterministic Bag-of-Words TF-IDF Vectorizer",
            "last_reindexed": datetime.utcnow().isoformat() + "Z"
        }

rag_service = RAGService()
