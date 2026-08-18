import math
import re
from typing import List, Dict, Any, Optional

class EmbeddingService:
    """
    Deterministic hybrid embedding service.
    Generates sparse/dense normalized vector representations of disaster texts
    using vocabulary TF-IDF weighting and term frequencies.
    Zero-dependency, guaranteed offline execution with zero credential requirements.
    """
    def __init__(self, vocab_size: int = 512):
        self.vocab_size = vocab_size
        self.vocab: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}

    def fit_vocabulary(self, texts: List[str]):
        """Builds vocabulary and inverse document frequency statistics from corpus."""
        doc_count = len(texts)
        if doc_count == 0:
            return

        doc_freqs: Dict[str, int] = {}
        all_terms = set()

        for text in texts:
            tokens = self._tokenize(text)
            unique_tokens = set(tokens)
            for t in unique_tokens:
                doc_freqs[t] = doc_freqs.get(t, 0) + 1
                all_terms.add(t)

        # Select top most informative terms
        sorted_terms = sorted(all_terms, key=lambda t: doc_freqs.get(t, 0), reverse=True)
        self.vocab = {term: idx for idx, term in enumerate(sorted_terms[:self.vocab_size])}

        # Compute IDF
        self.idf = {
            term: math.log((doc_count + 1) / (doc_freqs.get(term, 1) + 1)) + 1.0
            for term in self.vocab
        }

    def embed_text(self, text: str) -> List[float]:
        """Generates L2-normalized TF-IDF vector for input text."""
        tokens = self._tokenize(text)
        vec = [0.0] * max(len(self.vocab), 1)

        if not self.vocab:
            # Fallback uniform hash-based vector
            return [1.0]

        # Count term frequencies
        tf: Dict[str, int] = {}
        for t in tokens:
            if t in self.vocab:
                tf[t] = tf.get(t, 0) + 1

        # Populate weighted vector
        for term, count in tf.items():
            idx = self.vocab[term]
            idf_val = self.idf.get(term, 1.0)
            vec[idx] = count * idf_val

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def compute_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates cosine similarity between two normalized vectors."""
        if len(vec_a) != len(vec_b):
            min_len = min(len(vec_a), len(vec_b))
            vec_a = vec_a[:min_len]
            vec_b = vec_b[:min_len]
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(0.0, min(1.0, dot))

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^a-zA-Z0-9\s_-]', ' ', text.lower())
        return [w for w in cleaned.split() if len(w) > 2]

embedding_service = EmbeddingService()
