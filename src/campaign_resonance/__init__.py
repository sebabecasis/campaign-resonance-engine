"""Campaign Resonance Engine public API."""

from .embedding import ConceptHashEncoder
from .index import build_index, load_corpus
from .pipeline import run_campaign
from .rollup import rollup_hits
from .search import search_index

__all__ = [
    "ConceptHashEncoder",
    "build_index",
    "load_corpus",
    "rollup_hits",
    "run_campaign",
    "search_index",
]

