import re
from typing import List, Dict, Any

class TextChunker:
    """
    Splits emergency SOP documents into structured, semantically coherent text chunks
    with section headers, word overlap, and metadata preservation.
    """
    def __init__(self, chunk_size: int = 120, overlap: int = 25):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_text = doc.get("content", "").strip()
        doc_id = doc.get("id", "DOC-001")
        title = doc.get("title", "Emergency Guideline")
        category = doc.get("category", "GENERAL")
        source = doc.get("source", "NDMA")

        # Split into sections by numbered headers or paragraph blocks
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
        chunks: List[Dict[str, Any]] = []

        chunk_idx = 0
        for p in paragraphs:
            words = p.split()
            if len(words) <= self.chunk_size:
                chunks.append({
                    "chunk_id": f"{doc_id}-chk-{chunk_idx}",
                    "doc_id": doc_id,
                    "title": title,
                    "category": category,
                    "source": source,
                    "text": p,
                    "word_count": len(words)
                })
                chunk_idx += 1
            else:
                # Sliding window chunking
                start = 0
                while start < len(words):
                    end = min(len(words), start + self.chunk_size)
                    chunk_text = " ".join(words[start:end])
                    chunks.append({
                        "chunk_id": f"{doc_id}-chk-{chunk_idx}",
                        "doc_id": doc_id,
                        "title": title,
                        "category": category,
                        "source": source,
                        "text": chunk_text,
                        "word_count": len(words[start:end])
                    })
                    chunk_idx += 1
                    if end >= len(words):
                        break
                    start += (self.chunk_size - self.overlap)

        return chunks

chunker = TextChunker()
