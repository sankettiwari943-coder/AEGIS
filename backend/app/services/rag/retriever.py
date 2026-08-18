from typing import List, Dict, Any, Optional
from app.services.rag.vector_store import vector_store

class RAGRetriever:
    """
    RAG Retriever for disaster response protocols and emergency guidelines.
    Extracts high-relevance doctrinal snippets with provenance citations.
    """
    def __init__(self):
        pass

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return vector_store.search(query=query, top_k=top_k, category=category)

retriever = RAGRetriever()
