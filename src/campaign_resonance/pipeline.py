"""End-to-end campaign resonance run and reproducible output files."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .embedding import ConceptHashEncoder
from .index import build_index, load_corpus, write_index
from .models import QueryHit, QuerySpec
from .rollup import rollup_hits
from .search import search_index
from .providers import digest


def load_queries(path: str | Path) -> list[QuerySpec]:
    with Path(path).open(newline="") as handle:
        rows = []
        for row in csv.DictReader(handle):
            phrase = (row.get("phrase") or "").strip()
            if not phrase:
                continue
            threshold = float((row.get("threshold") or "0.25").strip())
            labels = [item.strip() for item in (row.get("only_labels") or "").split(";") if item.strip()]
            rows.append(
                QuerySpec(
                    phrase=phrase,
                    threshold=threshold,
                    only_labels=labels,
                    assumption=(row.get("assumption") or "").strip(),
                )
            )
    if not rows:
        raise ValueError("Query CSV contains no usable queries")
    return rows


def _write_hits(path: Path, hits: list[QueryHit]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(hits[0]).keys()) if hits else [
            "query", "domain", "score", "matched_label", "matched_phrase", "source_url"
        ])
        writer.writeheader()
        for hit in hits:
            writer.writerow(asdict(hit))


def _write_rollup(path: Path, rows: list) -> None:
    fields = [
        "domain", "n_queries_matched", "max_score", "sum_score", "avg_score",
        "top_query", "top_matched_phrase", "matched_queries", "matched_labels",
        "matched_phrases", "source_urls",
    ]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            payload = asdict(row)
            for key in ("matched_queries", "matched_labels", "matched_phrases", "source_urls"):
                payload[key] = "|".join(payload[key])
            writer.writerow(payload)


def run_campaign(
    corpus_path: str | Path,
    query_path: str | Path,
    output_dir: str | Path,
    *,
    encoder: ConceptHashEncoder | None = None,
    ranking: str = "similarity",
) -> dict:
    active_encoder = encoder or ConceptHashEncoder()
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    passages = load_corpus(corpus_path)
    if getattr(active_encoder, "provider", "demo") != "demo":
        raw = json.loads(Path(corpus_path).read_text())
        if any(not p.get("source_url", "").startswith(("https://", "http://")) for c in raw for p in c.get("passages", [])):
            raise ValueError("Production corpus requires explicit source URLs")
    index = build_index(passages, encoder=active_encoder)
    queries = load_queries(query_path)
    hits = search_index(index, queries, encoder=active_encoder)
    rollup = rollup_hits(hits, ranking=ranking)

    index_path = output / "index.jsonl"
    hits_path = output / "hits.csv"
    rollup_path = output / "rollup.csv"
    manifest_path = output / "run.json"
    write_index(index_path, index)
    _write_hits(hits_path, hits)
    _write_rollup(rollup_path, rollup)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "encoder": type(active_encoder).__name__,
        "ranking": ranking,
        "dimensions": active_encoder.dimensions,
        "model": getattr(active_encoder, "model", None),
        "provider": getattr(active_encoder, "provider", "demo"),
        "corpus_hash": digest(json.loads(Path(corpus_path).read_text())),
        "queries_hash": digest(Path(query_path).read_text()),
        "corpus_snapshot": json.loads(Path(corpus_path).read_text()),
        "queries_snapshot": Path(query_path).read_text(),
        "passages": len(passages),
        "indexed_passages": len(index),
        "queries": len(queries),
        "hits": len(hits),
        "domains": len(rollup),
        "outputs": {
            "index": str(index_path),
            "hits": str(hits_path),
            "rollup": str(rollup_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return {"manifest": manifest, "hits": hits, "rollup": rollup}
