# Axiom Cloudwatch Lambda

[![Go Workflow][go_workflow_badge]][go_workflow]
[![Coverage Status][coverage_badge]][coverage]
[![Go Report][report_badge]][report]
[![Latest Release][release_badge]][release]
[![License][license_badge]][license]

---

## Table of Contents

1. [Introduction](#introduction)
1. [Usage](#usage)
1. [Contributing](#contributing)
1. [License](#license)

## Introduction

_Axiom Cloudwatch Lambda_ ships logs to Axiom, right within from a lambda
function.

## Installation

### Download the pre-compiled and archived binary manually

Binary releases are available on [GitHub Releases][1].

  [1]: https://github.com/axiomhq/axiom-cloudwatch-lambda/releases/latest

### Install from source

This project uses native [go mod][2] support.

```shell
$ git clone https://github.com/axiomhq/axiom-cloudwatch-lambda.git
$ cd axiom-cloudwatch-lambda
$ make build # Puts archive into ./dist/
```

  [2]: https://golang.org/cmd/go/#hdr-Module_maintenance

## Usage

1. Upload the archive
2. Set the following environment variables on the lambda:
   * `AXIOM_DEPLOYMENT_URL`: URL of the Axiom deployment to use
   * `AXIOM_ACCESS_TOKEN`: **Personal Access** or **Ingest** token. Can be
     created under `Profile` or `Settings > Ingest Tokens`. For security reasons
     it is advised to use an Ingest Token with minimal privileges only.
   * `AXIOM_DATASET`: Dataset to ship the logs to

## Contributing

Feel free to submit PRs or to fill issues. Every kind of help is appreciated.

Before committing, `make` should run without any issues.

## License

&copy; Axiom, Inc., 2021

Distributed under MIT License (`The MIT License`).

See [LICENSE](LICENSE) for more information.

[![License Status][license_status_badge]][license_status]

<!-- Badges -->

[go_workflow]: https://github.com/axiomhq/axiom-cloudwatch-lambda/actions?query=workflow%3Ago
[go_workflow_badge]: https://img.shields.io/github/workflow/status/axiomhq/axiom-cloudwatch-lambda/go?style=flat-square&dummy=unused
[coverage]: https://codecov.io/gh/axiomhq/axiom-cloudwatch-lambda
[coverage_badge]: https://img.shields.io/codecov/c/github/axiomhq/axiom-cloudwatch-lambda.svg?style=flat-square&dummy=unused
[report]: https://goreportcard.com/report/github.com/axiomhq/axiom-cloudwatch-lambda
[report_badge]: https://goreportcard.com/badge/github.com/axiomhq/axiom-cloudwatch-lambda?style=flat-square&dummy=unused
[release]: https://github.com/axiomhq/axiom-cloudwatch-lambda/releases/latest
[release_badge]: https://img.shields.io/github/release/axiomhq/axiom-cloudwatch-lambda.svg?style=flat-square&dummy=unused
[license]: https://opensource.org/licenses/MIT
[license_badge]: https://img.shields.io/github/license/axiomhq/axiom-cloudwatch-lambda.svg?color=blue&style=flat-square&dummy=unused
[license_status]: https://app.fossa.com/projects/git%2Bgithub.com%2Faxiomhq%2Faxiom-cloudwatch-lambda
[license_status_badge]: https://app.fossa.com/api/projects/git%2Bgithub.com%2Faxiomhq%2Faxiom-cloudwatch-lambda.svg?type=large&dummy=unused
