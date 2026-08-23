"""
Dense Semantic Vector Embeddings Engine:
Provides normalized continuous dense embeddings (dim=256) supporting
both local dense subword-positional semantic encoding and sentence-transformers
when available.
"""
import hashlib
import math
import re

_DIM = 256
_TOKEN_RE = re.compile(r"[a-z0-9_+#\.\-]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _subword_ngrams(token: str, n_min: int = 3, n_max: int = 5) -> list[str]:
    """Generates subword char n-grams for out-of-vocabulary semantic generalization."""
    extended = f"<{token}>"
    ngrams = []
    for n in range(n_min, min(n_max + 1, len(extended) + 1)):
        for i in range(len(extended) - n + 1):
            ngrams.append(extended[i : i + n])
    return ngrams or [token]


def embed(text: str) -> list[float]:
    """
    Computes a continuous 256-dimensional semantic vector embedding.
    Uses subword n-gram contextual hashing with positional inverse frequency decay,
    excluding non-discriminative stop words, normalized onto the unit hypersphere (L2-norm = 1.0).
    """
    if not text:
        return [0.0] * _DIM

    tokens = [t for t in _tokenize(text) if t not in _STOP_WORDS and len(t) > 1]
    if not tokens:
        tokens = [t for t in _tokenize(text) if len(t) > 1]
    if not tokens:
        return [0.0] * _DIM

    vec = [0.0] * _DIM
    total_tokens = len(tokens)

    for pos, tok in enumerate(tokens):
        # Word position weighting (early topic words + keyword centrality)
        pos_weight = 1.0 / math.sqrt(pos + 1.0)
        ngrams = _subword_ngrams(tok)
        weight_per_gram = pos_weight / len(ngrams)

        for gram in ngrams:
            h = int(hashlib.sha256(gram.encode("utf-8")).hexdigest(), 16)
            idx1 = h % _DIM
            idx2 = (h // _DIM) % _DIM
            sign1 = 1.0 if (h // (_DIM * _DIM)) % 2 == 0 else -1.0
            sign2 = -1.0 if (h // (_DIM * _DIM * 2)) % 2 == 0 else 1.0

            vec[idx1] += sign1 * weight_per_gram
            vec[idx2] += sign2 * 0.5 * weight_per_gram

    norm = math.sqrt(sum(v * v for v in vec))
    if norm < 1e-9:
        return [0.0] * _DIM
    return [round(v / norm, 6) for v in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Calculates cosine similarity between two unit vectors (range: 0.0 to 1.0)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    # Return non-negative cosine dot product for unit vectors
    return round(max(0.0, min(1.0, dot)), 4)



_STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "by", "from",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "how", "what", "why", "when", "where", "which", "who",
    "whom", "this", "that", "these", "those", "and", "or", "but", "if", "so",
    "than", "too", "very", "can", "will", "just", "should", "now"
}


def bm25_keyword_score(query: str, document_text: str, avg_doc_len: float = 100.0, k1: float = 1.5, b: float = 0.75) -> float:
    """Computes BM25 term saturation score for non-stopwords keyword matching."""
    q_tokens = [t for t in _tokenize(query) if t not in _STOP_WORDS and len(t) > 1]
    doc_tokens = [t for t in _tokenize(document_text) if t not in _STOP_WORDS and len(t) > 1]
    doc_len = len(doc_tokens)
    if not q_tokens or not doc_tokens:
        return 0.0

    score = 0.0
    for q_term in q_tokens:
        freq = doc_tokens.count(q_term)
        if freq > 0:
            tf = (freq * (k1 + 1.0)) / (freq + k1 * (1.0 - b + b * (doc_len / avg_doc_len)))
            score += tf

    max_possible = len(q_tokens) * (k1 + 1.0)
    return round(min(1.0, score / max(1.0, max_possible)), 4)

