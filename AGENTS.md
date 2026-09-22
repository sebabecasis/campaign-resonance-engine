# Operating Lead <> Campaign Hook Matcher

The portfolio calls this project Lead <> Campaign Hook Matcher; its package and repository remain Campaign Resonance Engine. Read `README.md` and `docs/architecture.md`. Work from the repository root with Python 3.11+.

## Agent workflow

1. Understand the campaign's audience, problem and hook. Convert it into several distinct search ideas phrased as a prospect would describe its own business. Keep one concept per query and explain the assumption behind it.
2. Review the query set and source corpus with the operator. Build query CSV columns `phrase`, `threshold`, `only_labels`, `assumption`; multiple allowed labels are separated with semicolons. Remove duplicate or near-identical queries so breadth is not inflated.
3. Supply a JSON list of companies with `domain` and `passages`. Each passage needs exact `text`, `label` and a real `source_url`. The loader can default URLs; do not treat a default homepage URL as verified passage provenance. Collection and passage labeling happen outside this package, through supplied data or authorized research tools.
4. Run into a fresh output directory. Inspect strong matches, borderline matches and companies with no hits. Review both the evidence and the campaign assumption; similarity alone does not establish demand.
5. Refine queries, labels or thresholds based on observed errors, preserve prior runs, and deliver a ranked shortlist with exact passages, source links and limitations.

## Reproducible fixture

```bash
PYTHONPATH=src python -m campaign_resonance.cli --corpus examples/sample-campaign/corpus.json --queries examples/sample-campaign/queries.csv --out .demo/operator-run
PYTHONPATH=src python -m unittest discover -s tests -v
```

`index.jsonl` holds deduplicated passages and vectors. `hits.csv` retains the best passage for each query/company pair. `rollup.csv` ranks by number of matched queries, then cumulative similarity, then domain. `run.json` contains counts and encoder metadata. `--top` limits printed results, not the saved ranking. Keep the input config/corpus with the run because the manifest does not snapshot them.

## Capability boundaries

The bundled `ConceptHashEncoder` uses deterministic hashing and a small concept vocabulary. It is a demo adapter, not a production embedding model. Website ingestion, model-based extraction and a persistent production index are missing. `run_campaign(..., encoder=...)` accepts an adapter in Python; the CLI has no provider flag. Use the same encoder for indexed passages and queries and rebuild when it changes.

The website's vector-similarity wording needs qualification: current ranking uses breadth first and summed similarity second. Do not silently change ranking or describe it as pure maximum similarity. A production adapter needs normalized equal-length vectors plus the `dimensions` property used in the manifest.

Completion means a reproducible run with inspectable matching evidence and an explanation of the ranking. Keep fixtures synthetic and private corpora/credentials untracked. Propose code changes separately when ingestion, real embeddings or a new ranking policy is needed. Preserve provenance, deduplication and label filters in any implementation change.
