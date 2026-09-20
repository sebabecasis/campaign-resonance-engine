"""Command-line interface for a reproducible campaign resonance run."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .pipeline import run_campaign


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="campaign-resonance")
    root.add_argument("--corpus", type=Path, required=True)
    root.add_argument("--queries", type=Path, required=True)
    root.add_argument("--out", type=Path, required=True)
    root.add_argument("--top", type=int, default=10)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    result = run_campaign(args.corpus, args.queries, args.out)
    print(json.dumps({"manifest": result["manifest"], "top_domains": [asdict(row) for row in result["rollup"][: args.top]]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

