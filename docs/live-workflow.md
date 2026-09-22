# From websites to a hook-matched shortlist

Supply an approved source inventory:

```json
{
  "objective": "Find companies whose own language supports the campaign hook",
  "sources": [
    {"domain": "example.com", "source_url": "https://example.com", "label": "offering"}
  ]
}
```

Optionally add extraction_model with an OpenRouter model ID; selected quotes must occur verbatim in the source. Without it, Firecrawl Markdown is split into exact contiguous chunks. Labels come from the plan.

Preview the plan and hash without making requests:

```bash
PYTHONPATH=src python -m campaign_resonance.cli --source-plan /private/plan.json --queries /private/queries.csv --out .demo/live
```

After operator review of sources, queries and paid scope:

```bash
PYTHONPATH=src python -m campaign_resonance.cli --source-plan /private/plan.json --approved-plan-hash <reviewed-hash> --queries /private/queries.csv --out .demo/live --encoder openai --ranking similarity
```

Configure FIRECRAWL_API_KEY, OPENAI_API_KEY and optionally OPENROUTER_API_KEY in the environment. Existing corpora can bypass scraping via --corpus. Production corpora must have explicit HTTP(S) source URLs. Embedding defaults: text-embedding-3-small, 1536 dimensions; --model/--dimensions override them. Use the same model for corpus and queries.

Default similarity ranking compares maximum cosine score, then average score. --ranking breadth retains the earlier matched-query-count/summed-score ordering. The policy is recorded in run.json alongside input hashes, snapshots and embedding metadata.

collection.json retains failed-source diagnostics; failures stop ranking but save successful corpus data for deliberate recovery. An empty company passage list is missing evidence, not proof of a bad fit. Embeddings cache by content/model/dimensions. Source discovery, incremental crawl scheduling and hosted vector databases remain outside this local workflow.

Tests use fixtures and mocked provider calls. Live-account acceptance and threshold calibration are still required before relying on a campaign shortlist.
