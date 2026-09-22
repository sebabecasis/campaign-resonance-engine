# Campaign Resonance Engine

For agent-assisted operation, start with [AGENTS.md](AGENTS.md). Claude Code loads the same guide through [CLAUDE.md](CLAUDE.md).

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

The bundled encoder is a deterministic demonstration adapter. [Live collection and embeddings](docs/live-workflow.md) are available through --source-plan and --encoder openai. The default ranking is strongest vector similarity, then average similarity; --ranking breadth retains the original breadth-first policy. Inputs and provider settings are snapshotted in run.json. Tests mock provider calls; no real account acceptance run is implied.

## Test

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

See [`docs/architecture.md`](docs/architecture.md) for the recovered system loop and provider boundary.
