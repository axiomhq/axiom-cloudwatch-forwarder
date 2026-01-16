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
    axiom_edge_region: str,
    dataset: str,
) -> str:
    """
    Standalone implementation of get_ingest_url for testing.
    This mirrors the logic in forwarder.py.

    Priority:
    1. AXIOM_URL with custom path - Used as-is
    2. AXIOM_URL without path - Appends /v1/datasets/{dataset}/ingest for backwards compat
    3. AXIOM_EDGE_REGION - Regional edge domain, builds https://{region}/v1/ingest/{dataset}
    4. Default cloud endpoint with legacy path
    """
    if axiom_url and _url_has_path(axiom_url):
        return axiom_url
    elif axiom_edge_region:
        return f"https://{axiom_edge_region}/v1/ingest/{dataset}"
    else:
        return f"{axiom_url}/v1/datasets/{dataset}/ingest"


class TestUrlHasPath(unittest.TestCase):
    """Tests for the _url_has_path helper function."""

    def test_url_without_path(self):
        self.assertFalse(_url_has_path("https://api.axiom.co"))
        self.assertFalse(_url_has_path("https://api.axiom.co/"))
        self.assertFalse(_url_has_path("https://api.eu.axiom.co"))
        self.assertFalse(_url_has_path("https://api.eu.axiom.co/"))

    def test_url_with_path(self):
        self.assertTrue(_url_has_path("http://localhost:3400/ingest"))
        self.assertTrue(_url_has_path("https://custom.example.com/v1/ingest/dataset"))
        self.assertTrue(_url_has_path("https://api.axiom.co/custom/path"))


class TestGetIngestUrl(unittest.TestCase):
    """Tests for the get_ingest_url function and edge configuration."""

    def test_legacy_url_when_no_edge_configured(self):
        """When no edge config is set, should use legacy AXIOM_URL path."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_region="",
            dataset="my-dataset",
        )
        self.assertEqual(url, "https://api.axiom.co/v1/datasets/my-dataset/ingest")

    def test_url_without_path_backwards_compat(self):
        """URL without path should append legacy ingest path."""
        url = get_ingest_url_impl(
            axiom_url="https://api.eu.axiom.co",
            axiom_edge_region="",
            dataset="qoo",
        )
        self.assertEqual(url, "https://api.eu.axiom.co/v1/datasets/qoo/ingest")

        # Also with trailing slash
        url = get_ingest_url_impl(
            axiom_url="https://api.eu.axiom.co/",
            axiom_edge_region="",
            dataset="qoo",
        )
        self.assertEqual(url, "https://api.eu.axiom.co//v1/datasets/qoo/ingest")

    def test_url_with_custom_path_used_as_is(self):
        """URL with custom path should be used as-is."""
        url = get_ingest_url_impl(
            axiom_url="http://localhost:3400/ingest",
            axiom_edge_region="",
            dataset="meh",
        )
        self.assertEqual(url, "http://localhost:3400/ingest")

    def test_url_with_path_takes_precedence_over_region(self):
        """URL with custom path takes precedence over edge region."""
        url = get_ingest_url_impl(
            axiom_url="http://localhost:3400/ingest",
            axiom_edge_region="mumbai.axiom.co",
            dataset="test",
        )
        self.assertEqual(url, "http://localhost:3400/ingest")

    def test_edge_region_builds_correct_url(self):
        """When AXIOM_EDGE_REGION is set (and no URL path), should build edge ingest URL."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_region="eu-central-1.aws.edge.axiom.co",
            dataset="my-dataset",
        )
        self.assertEqual(
            url, "https://eu-central-1.aws.edge.axiom.co/v1/ingest/my-dataset"
        )

    def test_region_domain_only(self):
        """Region should be domain only, builds full URL."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_region="mumbai.axiom.co",
            dataset="test-3",
        )
        self.assertEqual(url, "https://mumbai.axiom.co/v1/ingest/test-3")

    def test_various_edge_regions(self):
        """Test various edge region formats."""
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

        for region, dataset, expected in test_cases:
            with self.subTest(region=region, dataset=dataset):
                url = get_ingest_url_impl(
                    axiom_url="https://api.axiom.co",
                    axiom_edge_region=region,
                    dataset=dataset,
                )
                self.assertEqual(url, expected)

    def test_default_no_config(self):
        """No url path, no region → default cloud with legacy path."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_region="",
            dataset="foo",
        )
        self.assertEqual(url, "https://api.axiom.co/v1/datasets/foo/ingest")


if __name__ == "__main__":
    unittest.main()
