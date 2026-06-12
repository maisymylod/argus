"""Text embeddings.

Default is a dependency-free hashed bag-of-words embedder: stable across
processes (uses hashlib, not Python's salted hash), L2-normalized, and good
enough for keyword-grounded retrieval over a small knowledge base with no model
download. Set ARGUS_EMBEDDINGS=st to use sentence-transformers if installed.

To upgrade retrieval quality, swap in a real embedding model (sentence-
transformers, or a hosted embeddings API) behind embed_texts; the rest of the
pipeline is agnostic to how vectors are produced.
"""

from __future__ import annotations

import hashlib
import os
import re

import numpy as np

from . import EMBED_DIM

_TOKEN = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def _hash_bucket(token: str, dim: int) -> int:
    digest = hashlib.md5(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % dim


def _hashed_embed(texts: list[str], dim: int) -> np.ndarray:
    vecs = np.zeros((len(texts), dim), dtype=np.float32)
    for i, text in enumerate(texts):
        for token in _tokenize(text):
            vecs[i, _hash_bucket(token, dim)] += 1.0
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return (vecs / norms).astype(np.float32)


def embed_texts(texts: list[str], dim: int = EMBED_DIM) -> np.ndarray:
    """Embed a list of texts to an (n, dim) float32 matrix of unit vectors."""
    if os.environ.get("ARGUS_EMBEDDINGS") == "st":
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        return np.asarray(model.encode(texts, normalize_embeddings=True), dtype=np.float32)
    return _hashed_embed(texts, dim)


def embed_one(text: str, dim: int = EMBED_DIM) -> np.ndarray:
    return embed_texts([text], dim)[0]
