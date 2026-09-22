# Operating Lead <> Campaign Hook Matcher

The portfolio name is Lead <> Campaign Hook Matcher; the Python package remains campaign_resonance. Read README.md and docs/live-workflow.md. Python 3.11+, standard library only.

## Agent workflow

1. Understand audience, problem and campaign hook. Form distinct queries in prospects' language; record the assumption each tests.
2. Prepare CSV columns phrase, threshold, only_labels, assumption. Separate multiple labels with semicolons and remove near-duplicate queries.
3. Review exact company passages with real source_url and label, or prepare a source plan of domain/source_url/label records. Agent research supplies the URL inventory; this is not an autonomous discovery crawler.
4. Preview --source-plan without a hash, then obtain operator approval for the displayed plan hash and paid work. Re-review changed plans. Optional extraction_model calls OpenRouter for exact quotes; default collection chunks the source unchanged.
5. Run with the same encoder for passages and queries. --encoder openai uses real normalized vectors; demo uses the limited deterministic concept vocabulary. Recalibrate thresholds when changing model.
6. Inspect strong, borderline and zero-hit companies and exact passages. Similarity suggests relevance, not buying intent. Keep failures separate from absent evidence.
7. Refine with operator feedback and preserve earlier outputs. Deliver ranked evidence, query assumptions, provider and ranking policy.

## Commands

```bash
PYTHONPATH=src python -m campaign_resonance.cli --corpus examples/sample-campaign/corpus.json --queries examples/sample-campaign/queries.csv --out .demo/run
PYTHONPATH=src python -m unittest discover -s tests -v
```

See docs/live-workflow.md for reviewed collection and real embeddings. Source-plan collection stops before ranking if any source fails, retaining collection.json and corpus.json for diagnosis.

## Contracts

Default --ranking similarity sorts maximum cosine score, then average score, then domain. --ranking breadth preserves the earlier policy of number of matched queries, then summed similarity. Explain which policy was used; breadth and vector strength are not interchangeable.

index.jsonl persists exact deduplicated passages and vectors. hits.csv keeps the best passage for each query/company pair. rollup.csv contains the ranked company summary. run.json records the policy, provider/model/dimensions and full input snapshots/hashes. --top only limits printed results.

Production corpora require explicit HTTP(S) source URLs. Labels are operator-supplied, not independently inferred. OpenAI cache files are keyed by model/dimensions/text; rebuild the index when any changes. A new run rebuilds the local index (cached embeddings avoid repeating model calls); no hosted vector database or incremental crawler is provided. Failed collection is not silently treated as zero similarity. Keep secrets and private corpora out of tracked examples. Provider contracts are mock-tested, not verified against a live account.
