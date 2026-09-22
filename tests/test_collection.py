import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
from campaign_resonance.collect import collect
from campaign_resonance.providers import digest, OpenAIEncoder
from campaign_resonance.pipeline import run_campaign
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class CollectionTests(unittest.TestCase):
    def test_review_hash_and_source_provenance(self):
        plan = {"objective": "goal", "sources": [{"domain": "example.test", "source_url": "https://example.test", "label": "offering"}]}
        fetch = Mock(return_value={"text": "exact source"})
        with self.assertRaises(PermissionError):
            collect(plan, "wrong", fetch=fetch)
        fetch.assert_not_called()
        result = collect(plan, digest(plan), fetch=fetch)
        passage = result["corpus"][0]["passages"][0]
        self.assertEqual("exact source", passage["text"])
        self.assertEqual("https://example.test", passage["source_url"])

    def test_partial_collection_is_not_silent(self):
        plan = {"sources": [{"domain": "example.test", "source_url": "https://example.test", "label": "offering"}]}
        result = collect(plan, digest(plan), fetch=Mock(side_effect=TimeoutError()))
        self.assertEqual(1, len(result["failures"]))
        self.assertEqual([], result["corpus"][0]["passages"])

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test"})
    def test_real_encoder_contract_used_for_index_and_queries(self):
        transport = Mock(return_value={"data": [{"embedding": [3, 4]}]})
        encoder = OpenAIEncoder(dimensions=2, transport=transport)
        with tempfile.TemporaryDirectory() as directory:
            result = run_campaign(ROOT / "examples/sample-campaign/corpus.json", ROOT / "examples/sample-campaign/queries.csv", directory, encoder=encoder)
            self.assertEqual("openai", result["manifest"]["provider"])
            self.assertEqual("similarity", result["manifest"]["ranking"])
            self.assertGreater(transport.call_count, 1)
            self.assertTrue(result["hits"])
