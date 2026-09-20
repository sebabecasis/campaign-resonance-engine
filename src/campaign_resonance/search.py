"""Search a passage index while retaining the evidence for every match."""

from __future__ import annotations

from .embedding import ConceptHashEncoder, cosine
from .models import IndexedPassage, QueryHit, QuerySpec


def search_index(
    index: list[IndexedPassage],
    queries: list[QuerySpec],
    *,
    encoder: ConceptHashEncoder | None = None,
) -> list[QueryHit]:
    active_encoder = encoder or ConceptHashEncoder()
    hits: list[QueryHit] = []
    for query in queries:
        query_vector = active_encoder.encode(query.phrase)
        allowed = set(query.only_labels)
        best_by_domain: dict[str, tuple[float, IndexedPassage]] = {}
        for row in index:
            if allowed and row.label not in allowed:
                continue
            score = cosine(query_vector, row.vector)
            if score < query.threshold:
                continue
            previous = best_by_domain.get(row.domain)
            if previous is None or score > previous[0]:
                best_by_domain[row.domain] = (score, row)
        for domain, (score, row) in sorted(best_by_domain.items(), key=lambda item: (-item[1][0], item[0])):
            hits.append(
                QueryHit(
                    query=query.phrase,
                    domain=domain,
                    score=score,
                    matched_label=row.label,
                    matched_phrase=row.text,
                    source_url=row.source_url,
                )
            )
    return hits

