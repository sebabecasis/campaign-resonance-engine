"""Replaceable local encoder used by the safe demonstration corpus."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter


TOKEN = re.compile(r"[a-z0-9]+")


class ConceptHashEncoder:
    """Create small, deterministic embeddings with concept canonicalisation.

    This is a zero-network demonstration adapter. It produces real dense vectors
    and cosine-search behaviour, but it is not presented as equivalent to a
    production embedding model. A provider adapter can replace it without changing
    the index, search or rollup contracts.
    """

    ALIASES = {
        "agents": "agent",
        "agentic": "agent",
        "ai": "agent",
        "automating": "automation",
        "automated": "automation",
        "workflows": "workflow",
        "processes": "workflow",
        "operations": "ops",
        "operational": "ops",
        "developers": "technical",
        "developer": "technical",
        "engineers": "technical",
        "engineering": "technical",
        "distributed": "remote",
        "international": "global",
        "overseas": "global",
        "contractors": "workforce",
        "employees": "workforce",
        "teams": "workforce",
        "analytics": "measurement",
        "metrics": "measurement",
        "reporting": "measurement",
        "evidence": "proof",
        "auditable": "governance",
        "governed": "governance",
        "approval": "review",
        "oversight": "review",
    }
    STOP = {"a", "an", "and", "are", "for", "from", "in", "of", "on", "the", "to", "with"}

    def __init__(self, dimensions: int = 256):
        if dimensions < 32:
            raise ValueError("Encoder dimensions must be at least 32")
        self.dimensions = dimensions

    def _concepts(self, text: str) -> list[str]:
        output = []
        for token in TOKEN.findall(text.casefold()):
            if token in self.STOP:
                continue
            output.append(self.ALIASES.get(token, token))
        return output

    def encode(self, text: str) -> list[float]:
        concepts = self._concepts(text)
        features = concepts + [f"{left}:{right}" for left, right in zip(concepts, concepts[1:])]
        counts = Counter(features)
        vector = [0.0] * self.dimensions
        for feature, count in counts.items():
            digest = hashlib.sha256(feature.encode()).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign * float(count)
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Vectors must have equal dimensions")
    return sum(a * b for a, b in zip(left, right))


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]

