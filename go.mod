module github.com/axiomhq/axiom-cloudwatch-lambda

go 1.16

require (
	github.com/aws/aws-lambda-go v1.23.0
	github.com/axiomhq/axiom-go v0.0.0-20210312122006-3294c6b958f9
	github.com/axiomhq/pkg v0.0.0-20210318171555-dc26762456be
	github.com/golangci/golangci-lint v1.38.0
	github.com/goreleaser/goreleaser v0.159.0
	github.com/stretchr/testify v1.7.0
	gotest.tools/gotestsum v1.6.2
)

replace github.com/json-iterator/go => github.com/mhr3/jsoniter v1.1.11-0.20200909125010-fb9b85012bdc
