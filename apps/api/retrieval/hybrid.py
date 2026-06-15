"""
BM25-style Hybrid Ranker for retrieval scoring.
Combines semantic (vector) score with keyword (BM25) score.
Pure Python — no external search engine required.
"""
import math
import logging
from collections import Counter
from typing import List, Tuple

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> List[str]:
    """Lightweight whitespace + punctuation tokenizer."""
    import re
    tokens = re.findall(r"\b[a-zA-Z0-9_'-]{2,}\b", text.lower())
    return tokens


class BM25Scorer:
    """
    BM25 scorer for a fixed set of candidate documents.
    k1 and b are standard BM25 parameters (Robertson & Zaragoza, 2009).
    """
    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_count = len(documents)
        self._tokenized: List[List[str]] = [_tokenize(d) for d in documents]
        self._tf: List[Counter] = [Counter(toks) for toks in self._tokenized]
        self._doc_lengths: List[int] = [len(toks) for toks in self._tokenized]
        self._avg_doc_len: float = (
            sum(self._doc_lengths) / max(self.doc_count, 1)
        )

        # Build DF (document frequency) table
        self._df: Counter = Counter()
        for tf in self._tf:
            for term in tf:
                self._df[term] += 1

    def idf(self, term: str) -> float:
        df = self._df.get(term, 0)
        return math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1)

    def score(self, query: str, doc_index: int) -> float:
        tokens = _tokenize(query)
        if not tokens:
            return 0.0

        tf = self._tf[doc_index]
        doc_len = self._doc_lengths[doc_index]
        score = 0.0
        for term in set(tokens):
            freq = tf.get(term, 0)
            if freq == 0:
                continue
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (
                1 - self.b + self.b * doc_len / max(self._avg_doc_len, 1)
            )
            score += self.idf(term) * (numerator / denominator)
        return score

    def score_all(self, query: str) -> List[float]:
        return [self.score(query, i) for i in range(self.doc_count)]


class HybridRanker:
    """
    Hybrid semantic + keyword ranker.
    Final score = (semantic_weight * semantic_score) + (keyword_weight * normalised_bm25_score)
    """

    def __init__(
        self,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
    ):
        assert abs(semantic_weight + keyword_weight - 1.0) < 1e-6, (
            "Weights must sum to 1.0"
        )
        self.semantic_weight = semantic_weight
        self.keyword_weight = keyword_weight

    def rerank(
        self,
        query: str,
        chunk_ids: List[str],
        documents: List[str],
        semantic_scores: List[float],
    ) -> List[Tuple[str, float, float, float]]:
        """
        Re-rank retrieved chunks using hybrid scoring.

        Args:
            query: The original user query
            chunk_ids: List of chunk identifiers
            documents: Corresponding document texts
            semantic_scores: Cosine similarity scores from the vector store

        Returns:
            List of (chunk_id, hybrid_score, semantic_score, keyword_score) tuples,
            sorted by hybrid_score descending.
        """
        if not documents:
            return []

        bm25 = BM25Scorer(documents)
        kw_scores_raw = bm25.score_all(query)

        # Normalise BM25 scores to [0, 1] range
        max_kw = max(kw_scores_raw) if kw_scores_raw else 1.0
        if max_kw == 0:
            kw_scores_norm = [0.0] * len(kw_scores_raw)
        else:
            kw_scores_norm = [s / max_kw for s in kw_scores_raw]

        results: List[Tuple[str, float, float, float]] = []
        for i, (cid, sem_score) in enumerate(zip(chunk_ids, semantic_scores)):
            kw_score = kw_scores_norm[i]
            hybrid = (self.semantic_weight * sem_score) + (self.keyword_weight * kw_score)
            results.append((cid, hybrid, sem_score, kw_score))

        results.sort(key=lambda x: x[1], reverse=True)
        logger.debug(
            f"[HybridRanker] Re-ranked {len(results)} chunk(s) | "
            f"top_hybrid={results[0][1]:.3f} sem={results[0][2]:.3f} kw={results[0][3]:.3f}"
            if results else f"[HybridRanker] No chunks to rank"
        )
        return results
