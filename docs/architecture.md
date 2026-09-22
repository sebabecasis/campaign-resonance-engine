# Architecture

```text
labelled website passages
          │
          ▼
replaceable encoder → passage index
                           │
campaign brief             │
      │                    │
      ▼                    │
operator-reviewed queries ─┘
      │
      ▼
best passage per query × company
      │
      ▼
company rollup ranked by strongest similarity (or explicit breadth policy)
      │
      ▼
ranked companies + exact evidence + source URLs
```

## Preserved design decisions

- One concept per query.
- Query language should resemble how a target company describes itself.
- Thresholds and label filters are explicit and editable.
- Only the best passage for each query/company pair contributes to ranking.
- Default ranking compares maximum cosine similarity then average score; explicit breadth mode ranks matched-query count then summed similarity.
- Every match retains the passage and URL that caused it.

## Encoder boundary

The bundled `ConceptHashEncoder` is a deterministic, zero-network demonstration adapter. It makes the fixture reproducible without credentials or model downloads. It is intentionally labelled as such.

providers.OpenAIEncoder implements real embeddings with validation, normalization and model/content-addressed caching. collect.py executes an operator-reviewed URL list using Firecrawl and optional verbatim OpenRouter extraction. CLI exposes these providers; run.json retains provider/model/dimensions, ranking and full input snapshots. The local JSONL index is rebuilt per run, using cached vectors when unchanged.
