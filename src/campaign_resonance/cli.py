"""Command-line interface for a reproducible campaign resonance run."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .pipeline import run_campaign
from .providers import OpenAIEncoder, digest
from .collect import collect


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="campaign-resonance")
    inputs = root.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--corpus", type=Path)
    inputs.add_argument("--source-plan", type=Path)
    root.add_argument("--approved-plan-hash")
    root.add_argument("--encoder", choices=["demo", "openai"], default="demo")
    root.add_argument("--model", default="text-embedding-3-small")
    root.add_argument("--dimensions", type=int, default=1536)
    root.add_argument("--queries", type=Path, required=True)
    root.add_argument("--out", type=Path, required=True)
    root.add_argument("--top", type=int, default=10)
    root.add_argument("--ranking", choices=["similarity", "breadth"], default="similarity")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    corpus = args.corpus
    if args.source_plan:
        plan = json.loads(args.source_plan.read_text())
        if not args.approved_plan_hash:
            print(json.dumps({"plan_hash": digest(plan), "plan": plan, "status": "awaiting_review"}, indent=2))
            return 0
        collected = collect(plan, args.approved_plan_hash)
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / "collection.json").write_text(json.dumps(collected, indent=2))
        corpus = args.out / "corpus.json"
        corpus.write_text(json.dumps(collected["corpus"], indent=2))
        if collected["failures"]:
            print("Collection incomplete; inspect collection.json before using partial corpus")
            return 1
    encoder = OpenAIEncoder(args.model, args.dimensions, args.out / "embedding-cache") if args.encoder == "openai" else None
    result = run_campaign(corpus, args.queries, args.out, encoder=encoder, ranking=args.ranking)
    print(json.dumps({"manifest": result["manifest"], "top_domains": [asdict(row) for row in result["rollup"][: args.top]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
