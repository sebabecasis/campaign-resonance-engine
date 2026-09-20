"""Data contracts for campaign-to-audience discovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Passage:
    domain: str
    source_url: str
    label: str
    text: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Passage":
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class IndexedPassage(Passage):
    text_hash: str = ""
    vector: list[float] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IndexedPassage":
        return cls(**data)


@dataclass(slots=True)
class QuerySpec:
    phrase: str
    threshold: float = 0.25
    only_labels: list[str] = field(default_factory=list)
    assumption: str = ""


@dataclass(slots=True)
class QueryHit:
    query: str
    domain: str
    score: float
    matched_label: str
    matched_phrase: str
    source_url: str


@dataclass(slots=True)
class DomainRollup:
    domain: str
    n_queries_matched: int
    max_score: float
    sum_score: float
    avg_score: float
    top_query: str
    top_matched_phrase: str
    matched_queries: list[str]
    matched_labels: list[str]
    matched_phrases: list[str]
    source_urls: list[str]

