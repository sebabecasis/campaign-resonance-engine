"""Aggregate passage matches into an explainable company ranking."""

from __future__ import annotations

from collections import defaultdict

from .models import DomainRollup, QueryHit


def rollup_hits(hits: list[QueryHit], *, ranking="similarity") -> list[DomainRollup]:
    if ranking not in {"similarity", "breadth"}:
        raise ValueError("Ranking must be similarity or breadth")
    by_domain: dict[str, list[QueryHit]] = defaultdict(list)
    for hit in hits:
        by_domain[hit.domain].append(hit)

    rows = []
    for domain, domain_hits in by_domain.items():
        ordered = sorted(domain_hits, key=lambda hit: (-hit.score, hit.query))
        scores = [hit.score for hit in ordered]
        top = ordered[0]
        rows.append(
            DomainRollup(
                domain=domain,
                n_queries_matched=len(ordered),
                max_score=max(scores),
                sum_score=sum(scores),
                avg_score=sum(scores) / len(scores),
                top_query=top.query,
                top_matched_phrase=top.matched_phrase,
                matched_queries=[hit.query for hit in ordered],
                matched_labels=[hit.matched_label for hit in ordered],
                matched_phrases=[hit.matched_phrase for hit in ordered],
                source_urls=[hit.source_url for hit in ordered],
            )
        )
    if ranking == "breadth":
        rows.sort(key=lambda row: (-row.n_queries_matched, -row.sum_score, row.domain))
    else:
        rows.sort(key=lambda row: (-row.max_score, -row.avg_score, row.domain))
    return rows
