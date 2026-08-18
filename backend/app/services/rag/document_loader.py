from typing import List, Dict, Any
from app.services.rag.documents.sop_flood_emergency import EMERGENCY_SOP_DOCUMENTS

class DocumentLoader:
    """
    Loads emergency doctrine, disaster SOPs, triage manuals, and operational protocols.
    Supports built-in catalog and dynamic additions.
    """
    def __init__(self):
        self.documents: List[Dict[str, Any]] = list(EMERGENCY_SOP_DOCUMENTS)

    def load_all_documents(self) -> List[Dict[str, Any]]:
        return self.documents

    def add_document(self, doc_id: str, title: str, category: str, content: str, source: str = "Operator Ingested") -> Dict[str, Any]:
        doc = {
            "id": doc_id,
            "title": title,
            "category": category,
            "source": source,
            "last_revised": "2026-08-17",
            "content": content
        }
        self.documents.append(doc)
        return doc

document_loader = DocumentLoader()
