from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from campaign_resonance.embedding import ConceptHashEncoder
from campaign_resonance.index import build_index, load_corpus, read_index, write_index
from campaign_resonance.models import QueryHit, QuerySpec
from campaign_resonance.pipeline import run_campaign
from campaign_resonance.rollup import rollup_hits
from campaign_resonance.search import search_index


ROOT = Path(__file__).parents[1]
CORPUS = ROOT / "examples" / "sample-campaign" / "corpus.json"
QUERIES = ROOT / "examples" / "sample-campaign" / "queries.csv"


class CampaignResonanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.encoder = ConceptHashEncoder()
        self.index = build_index(load_corpus(CORPUS), encoder=self.encoder)

    def test_index_roundtrip_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.jsonl"
            write_index(path, self.index)
            restored = read_index(path)
        self.assertEqual([row.to_dict() for row in self.index], [row.to_dict() for row in restored])

    def test_search_keeps_best_passage_per_query_and_domain(self) -> None:
        hits = search_index(
            self.index,
            [QuerySpec("human review audit trail", threshold=0.20)],
            encoder=self.encoder,
        )
        domains = [hit.domain for hit in hits]
        self.assertEqual(len(domains), len(set(domains)))
        northstar = next(hit for hit in hits if hit.domain == "northstar.example")
        self.assertIn("audit trail", northstar.matched_phrase)

    def test_label_filter_is_enforced(self) -> None:
        hits = search_index(
            self.index,
            [QuerySpec("global remote workforce", threshold=0.15, only_labels=["audience"])],
            encoder=self.encoder,
        )
        self.assertTrue(hits)
        self.assertTrue(all(hit.matched_label == "audience" for hit in hits))

    def test_rollup_prefers_breadth_before_single_high_score(self) -> None:
        hits = [
            QueryHit("q1", "broad.example", 0.5, "offering", "p1", "https://broad.example/1"),
            QueryHit("q2", "broad.example", 0.4, "audience", "p2", "https://broad.example/2"),
            QueryHit("q1", "narrow.example", 0.99, "offering", "p3", "https://narrow.example"),
        ]
        rows = rollup_hits(hits, ranking="breadth")
        self.assertEqual("broad.example", rows[0].domain)
        self.assertEqual(2, rows[0].n_queries_matched)
        self.assertEqual("narrow.example", rollup_hits(hits)[0].domain)

    def test_pipeline_writes_explainable_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = run_campaign(CORPUS, QUERIES, directory, encoder=self.encoder)
            output = Path(directory)
            self.assertTrue((output / "index.jsonl").exists())
            self.assertTrue((output / "hits.csv").exists())
            self.assertTrue((output / "rollup.csv").exists())
            self.assertTrue((output / "run.json").exists())
            self.assertGreaterEqual(result["rollup"][0].n_queries_matched, 2)
            with (output / "hits.csv").open() as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(all(row["matched_phrase"] and row["source_url"] for row in rows))


if __name__ == "__main__":
    unittest.main()
