"""Load labelled website passages and build a deterministic vector index."""

from __future__ import annotations

import json
from pathlib import Path

from .embedding import ConceptHashEncoder, text_hash
from .models import IndexedPassage, Passage


def load_corpus(path: str | Path) -> list[Passage]:
    payload = json.loads(Path(path).read_text())
    if not isinstance(payload, list):
        raise ValueError("Corpus must be a JSON list")
    passages: list[Passage] = []
    for company in payload:
        domain = str(company.get("domain", "")).strip()
        if not domain:
            raise ValueError("Every corpus company requires a domain")
        for item in company.get("passages", []):
            passages.append(
                Passage(
                    domain=domain,
                    source_url=str(item.get("source_url", f"https://{domain}")),
                    label=str(item.get("label", "misc")),
                    text=str(item["text"]),
                )
            )
    return passages


def build_index(
    passages: list[Passage],
    *,
    encoder: ConceptHashEncoder | None = None,
) -> list[IndexedPassage]:
    active_encoder = encoder or ConceptHashEncoder()
    seen: set[tuple[str, str]] = set()
    indexed: list[IndexedPassage] = []
    for passage in passages:
        identity = (passage.domain, text_hash(passage.text))
        if identity in seen:
            continue
        seen.add(identity)
        indexed.append(
            IndexedPassage(
                **passage.to_dict(),
                text_hash=identity[1],
                vector=active_encoder.encode(passage.text),
            )
        )
    return indexed


def write_index(path: str | Path, rows: list[IndexedPassage]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row.to_dict(), sort_keys=True) + "\n")


def read_index(path: str | Path) -> list[IndexedPassage]:
    return [IndexedPassage.from_dict(json.loads(line)) for line in Path(path).read_text().splitlines() if line.strip()]

