from typing import List, Dict, Any, Optional
from app.services.rag.embedding_service import embedding_service

class VectorStore:
    """
    Lightweight in-memory vector store for emergency SOP chunks.
    Supports cosine similarity retrieval, category filtering, and metadata enrichment.
    """
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vectors: List[List[float]] = []

    def index_chunks(self, chunks: List[Dict[str, Any]]):
        """Fits vocabulary and computes embeddings for all chunks."""
        self.chunks = chunks
        texts = [c["text"] + " " + c["title"] for c in chunks]
        embedding_service.fit_vocabulary(texts)
        self.vectors = [embedding_service.embed_text(t) for t in texts]

    def search(
        self,
        query: str,
        top_k: int = 4,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Searches vector index for top-k matching SOP chunks."""
        if not self.chunks or not self.vectors:
            return []

        query_vec = embedding_service.embed_text(query)
        scores: List[tuple] = []

        for idx, (chunk, vec) in enumerate(zip(self.chunks, self.vectors)):
            if category and chunk.get("category") != category:
                continue

            similarity = embedding_service.compute_similarity(query_vec, vec)
            
            # Boost score if query keywords appear in chunk title
            title_tokens = chunk["title"].lower().split()
            query_tokens = query.lower().split()
            matching_title_words = set(title_tokens).intersection(set(query_tokens))
            if matching_title_words:
                similarity = min(1.0, similarity + 0.15 * len(matching_title_words))

            scores.append((similarity, chunk))

        # Sort by similarity descending
        scores.sort(key=lambda x: x[0], reverse=True)

        results = []
        for sim, chunk in scores[:top_k]:
            results.append({
                **chunk,
                "relevance_score": round(sim, 3),
                "confidence_label": "HIGH" if sim > 0.45 else "MODERATE" if sim > 0.20 else "LOW"
            })
        return results

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_chunks_indexed": len(self.chunks),
            "vector_dimensions": len(self.vectors[0]) if self.vectors else 0,
            "categories": list(set(c.get("category", "") for c in self.chunks)),
            "storage_type": "In-Memory Vector Store (Cosine Similarity)"
        }

vector_store = VectorStore()
