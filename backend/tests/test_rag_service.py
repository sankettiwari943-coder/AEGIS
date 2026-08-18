import pytest
from app.services.rag import rag_service, vector_store, document_loader, chunker

def test_document_loader_and_chunking():
    docs = document_loader.load_all_documents()
    assert len(docs) >= 6
    assert any("SOP-FL-001" in d["id"] for d in docs)

    # Test chunking
    doc = docs[0]
    chunks = chunker.chunk_document(doc)
    assert len(chunks) > 0
    assert chunks[0]["doc_id"] == doc["id"]

def test_rag_service_query():
    # Query for flood evacuation SOP
    res = rag_service.query_knowledge_base("flood emergency evacuation SOP", top_k=3)
    assert res["retrieved_count"] > 0
    assert len(res["guidance_summary"]) > 0
    assert len(res["citations"]) > 0
    assert res["top_match"] is not None

def test_rag_status_and_catalog():
    status = rag_service.get_status()
    assert status["status"] == "OPERATIONAL"
    assert status["total_documents"] >= 6

    catalog = rag_service.get_documents_catalog()
    assert len(catalog) >= 6
