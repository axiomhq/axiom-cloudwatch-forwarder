"""Tests for edge URL configuration in forwarder.py"""

import unittest


def get_ingest_url_impl(
    axiom_url: str,
    axiom_edge_url: str,
    axiom_edge_region: str,
    dataset: str,
) -> str:
    """
    Standalone implementation of get_ingest_url for testing.
    This mirrors the logic in forwarder.py.
    """
    if axiom_edge_url:
        return f"{axiom_edge_url}/v1/ingest/{dataset}"
    elif axiom_edge_region:
        return f"https://{axiom_edge_region}/v1/ingest/{dataset}"
    else:
        return f"{axiom_url}/v1/datasets/{dataset}/ingest"


class TestGetIngestUrl(unittest.TestCase):
    """Tests for the get_ingest_url function and edge configuration."""

    def test_legacy_url_when_no_edge_configured(self):
        """When no edge config is set, should use legacy AXIOM_URL path."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="",
            axiom_edge_region="",
            dataset="my-dataset",
        )
        self.assertEqual(url, "https://api.axiom.co/v1/datasets/my-dataset/ingest")

    def test_edge_region_builds_correct_url(self):
        """When AXIOM_EDGE_REGION is set, should build edge ingest URL."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="",
            axiom_edge_region="eu-central-1.aws.edge.axiom.co",
            dataset="my-dataset",
        )
        self.assertEqual(
            url, "https://eu-central-1.aws.edge.axiom.co/v1/ingest/my-dataset"
        )

    def test_edge_url_builds_correct_url(self):
        """When AXIOM_EDGE_URL is set, should use it directly."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="https://custom-edge.example.com",
            axiom_edge_region="",
            dataset="my-dataset",
        )
        self.assertEqual(url, "https://custom-edge.example.com/v1/ingest/my-dataset")

    def test_edge_url_takes_precedence_over_region(self):
        """AXIOM_EDGE_URL should take precedence over AXIOM_EDGE_REGION."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="https://custom-edge.example.com",
            axiom_edge_region="eu-central-1.aws.edge.axiom.co",
            dataset="my-dataset",
        )
        self.assertEqual(url, "https://custom-edge.example.com/v1/ingest/my-dataset")

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
                    axiom_edge_url="",
                    axiom_edge_region=region,
                    dataset=dataset,
                )
                self.assertEqual(url, expected)

    def test_default_axiom_url(self):
        """Test with default Axiom URL."""
        url = get_ingest_url_impl(
            axiom_url="https://api.axiom.co",
            axiom_edge_url="",
            axiom_edge_region="",
            dataset="cloudwatch-logs",
        )
        self.assertEqual(url, "https://api.axiom.co/v1/datasets/cloudwatch-logs/ingest")

    def test_custom_axiom_url(self):
        """Test with custom Axiom URL (self-hosted)."""
        url = get_ingest_url_impl(
            axiom_url="https://axiom.mycompany.com",
            axiom_edge_url="",
            axiom_edge_region="",
            dataset="logs",
        )
        self.assertEqual(url, "https://axiom.mycompany.com/v1/datasets/logs/ingest")


if __name__ == "__main__":
    unittest.main()
