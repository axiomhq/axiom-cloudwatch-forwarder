"""Tests for edge URL configuration in forwarder.py"""

import unittest
from urllib.parse import urlparse


def _url_has_path(url: str) -> bool:
    """Check if URL has a meaningful path (not empty or just '/')."""
    try:
        parsed = urlparse(url)
        return parsed.path not in ("", "/")
    except Exception:
        return False


def get_ingest_url_impl(
    axiom_url: str,
    axiom_edge_url: str,
    axiom_edge: str,
    dataset: str,
) -> str:
    """
    Standalone implementation of get_ingest_url for testing.
    This mirrors the logic in forwarder.py.

    Priority:
    1. AXIOM_EDGE_URL with custom path - Used as-is
    2. AXIOM_EDGE_URL without path - Appends /v1/ingest/{dataset}
    3. AXIOM_EDGE - Regional edge domain, builds https://{edge}/v1/ingest/{dataset}
    4. AXIOM_URL - Legacy path /v1/datasets/{dataset}/ingest
    """
    if axiom_edge_url:
        if _url_has_path(axiom_edge_url):
            return axiom_edge_url
        return f"{axiom_edge_url}/v1/ingest/{dataset}"
    elif axiom_edge:
        return f"https://{axiom_edge}/v1/ingest/{dataset}"
    else:
        return f"{axiom_url}/v1/datasets/{dataset}/ingest"


class TestUrlHasPath(unittest.TestCase):
    """Tests for the _url_has_path helper function."""

    def test_url_without_path(self):
        self.assertFalse(_url_has_path("https://api.axiom.co"))
        self.assertFalse(_url_has_path("https://api.axiom.co/"))
        self.assertFalse(_url_has_path("https://custom-edge.example.com"))
        self.assertFalse(_url_has_path("https://custom-edge.example.com/"))

    def test_url_with_path(self):
        self.assertTrue(_url_has_path("http://localhost:3400/ingest"))
        self.assertTrue(_url_has_path("https://custom.example.com/v1/ingest/dataset"))
        self.assertTrue(_url_has_path("https://edge.example.com/custom/path"))


class TestGetIngestUrl(unittest.TestCase):
    """Tests for the get_ingest_url function."""

    def test_default_no_edge(self):
        """No edge configured → legacy AXIOM_URL path."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="",
            axiom_edge="",
            dataset="foo",
        )
        self.assertEqual(url, "https://api.axiom.co/v1/datasets/foo/ingest")

    def test_edge_domain(self):
        """AXIOM_EDGE set → builds https://{edge}/v1/ingest/{dataset}."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="",
            axiom_edge="eu-central-1.aws.edge.axiom.co",
            dataset="my-dataset",
        )
        self.assertEqual(
            url, "https://eu-central-1.aws.edge.axiom.co/v1/ingest/my-dataset"
        )

    def test_edge_url_without_path(self):
        """AXIOM_EDGE_URL without path → appends /v1/ingest/{dataset}."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="https://custom-edge.example.com",
            axiom_edge="",
            dataset="my-dataset",
        )
        self.assertEqual(url, "https://custom-edge.example.com/v1/ingest/my-dataset")

    def test_edge_url_with_custom_path(self):
        """AXIOM_EDGE_URL with custom path → used as-is."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="http://localhost:3400/ingest",
            axiom_edge="",
            dataset="meh",
        )
        self.assertEqual(url, "http://localhost:3400/ingest")

    def test_edge_url_takes_precedence_over_edge(self):
        """AXIOM_EDGE_URL takes precedence over AXIOM_EDGE."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="https://custom-edge.example.com",
            axiom_edge="mumbai.axiom.co",
            dataset="test",
        )
        self.assertEqual(url, "https://custom-edge.example.com/v1/ingest/test")

    def test_edge_url_with_path_takes_precedence_over_edge(self):
        """AXIOM_EDGE_URL with path takes precedence over AXIOM_EDGE."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="http://localhost:3400/ingest",
            axiom_edge="mumbai.axiom.co",
            dataset="test",
        )
        self.assertEqual(url, "http://localhost:3400/ingest")

    def test_various_edge_domains(self):
        """Test various edge domain formats."""
        test_cases = [
            ("mumbai.axiom.co", "logs", "https://mumbai.axiom.co/v1/ingest/logs"),
            (
                "us-east-1.aws.edge.axiom.co",
                "prod-logs",
                "https://us-east-1.aws.edge.axiom.co/v1/ingest/prod-logs",
            ),
            (
                "eu-west-1.edge.staging.axiom.co",
                "test",
                "https://eu-west-1.edge.staging.axiom.co/v1/ingest/test",
            ),
        ]

        for edge, dataset, expected in test_cases:
            with self.subTest(edge=edge, dataset=dataset):
                url = get_ingest_url_impl(
                    axiom_url="https://api.axiom.co",
                    axiom_edge_url="",
                    axiom_edge=edge,
                    dataset=dataset,
                )
                self.assertEqual(url, expected)

    def test_custom_axiom_url_no_edge(self):
        """Custom AXIOM_URL (self-hosted) with no edge → legacy path."""
        url = get_ingest_url_impl(
            axiom_url="https://axiom.mycompany.com",
            axiom_edge_url="",
            axiom_edge="",
            dataset="logs",
        )
        self.assertEqual(url, "https://axiom.mycompany.com/v1/datasets/logs/ingest")


if __name__ == "__main__":
    unittest.main()
