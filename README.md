# Campaign Resonance Engine

Find companies whose own language provides evidence that a campaign premise will resonate.

## Repository status

The first clean working slice is implemented. Historical Sentvia data and indexes are not carried into this repository.

The first working slice demonstrates:

```text
campaign brief
→ prospect-language query set
→ semantic search over a fixture corpus
→ evidence-backed company ranking
→ operator refinement
```

See [`MIGRATION.md`](MIGRATION.md) for the recovered modules and extraction plan.

## Run the example

Requires Python 3.11+. The fixture runner has no external model or API dependency.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

campaign-resonance \
  --corpus examples/sample-campaign/corpus.json \
  --queries examples/sample-campaign/queries.csv \
  --out .demo/sample-run
```

The run writes:

- `index.jsonl` — labelled passages and vectors;
- `hits.csv` — the best evidence per query and company;
- `rollup.csv` — the company ranking;
- `run.json` — the reproducibility manifest.

The bundled encoder is a deterministic demonstration adapter. The retrieval and evidence contracts are designed so it can be replaced by a production embedding provider.

## Test

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

See [`docs/architecture.md`](docs/architecture.md) for the recovered system loop and provider boundary.
