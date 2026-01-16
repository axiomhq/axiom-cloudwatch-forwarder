# Axiom CloudWatch Forwarder

<a href="https://axiom.co">
<picture>
  <source media="(prefers-color-scheme: dark) and (min-width: 600px)" srcset="https://axiom.co/assets/github/axiom-github-banner-light-vertical.svg">
  <source media="(prefers-color-scheme: light) and (min-width: 600px)" srcset="https://axiom.co/assets/github/axiom-github-banner-dark-vertical.svg">
  <source media="(prefers-color-scheme: dark) and (max-width: 599px)" srcset="https://axiom.co/assets/github/axiom-github-banner-light-horizontal.svg">
  <img alt="Axiom.co banner" src="https://axiom.co/assets/github/axiom-github-banner-dark-horizontal.svg" align="right">
</picture>
</a>
&nbsp;

[![CI](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml/badge.svg)](https://github.com/axiomhq/axiom-cloudwatch-forwarder/actions/workflows/ci.yaml)

Axiom CloudWatch Forwarder is a set of easy-to-use AWS CloudFormation stacks designed to forward logs from Amazon CloudWatch to [Axiom](https://axiom.co). It includes a Lambda function to handle the forwarding and stacks to create CloudWatch log group subscription filters for both existing and future log groups.

## Documentation

For more information about how to set up and use the Axiom CloudWatch Forwarder, see the [Axiom documentation](https://axiom.co/docs/send-data/cloudwatch).

## Edge Ingestion

The forwarder supports edge-based regional ingestion for improved data locality. When configured, ingest operations are routed to regional edge endpoints while maintaining full backwards compatibility.

### Configuration

| Environment Variable | Description |
|---------------------|-------------|
| `AXIOM_EDGE_URL` | Explicit edge URL (e.g., `https://custom-edge.example.com`). Takes precedence over `AXIOM_EDGE_REGION`. |
| `AXIOM_EDGE_REGION` | Regional edge domain (e.g., `eu-central-1.aws.edge.axiom.co`). |

**Priority:** `AXIOM_EDGE_URL` > `AXIOM_EDGE_REGION` > `AXIOM_URL` (default)

### Edge Endpoint

When edge ingestion is configured, data is sent to:
```
https://{edge}/v1/ingest/{dataset}
```

### CloudFormation Parameters

The forwarder stack accepts optional `AxiomEdgeURL` and `AxiomEdgeRegion` parameters for edge configuration. Existing deployments work unchanged—edge routing only activates when explicitly configured.
