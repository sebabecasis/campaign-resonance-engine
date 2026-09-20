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
company rollup ranked by signal breadth, then cumulative similarity
      │
      ▼
ranked companies + exact evidence + source URLs
```

## Preserved design decisions

- One concept per query.
- Query language should resemble how a target company describes itself.
- Thresholds and label filters are explicit and editable.
- Only the best passage for each query/company pair contributes to ranking.
- Companies matching more distinct campaign signals rank above narrow one-off matches.
- Every match retains the passage and URL that caused it.

## Encoder boundary

The bundled `ConceptHashEncoder` is a deterministic, zero-network demonstration adapter. It makes the fixture reproducible without credentials or model downloads. It is intentionally labelled as such.

A production embedding provider can replace it as long as it returns equal-length normalized vectors. The indexing, evidence retention, query controls and rollup logic do not change.

