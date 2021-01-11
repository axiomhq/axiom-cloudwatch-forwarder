module github.com/axiomhq/axiom-cloudwatch-lambda

go 1.15

require (
	github.com/aws/aws-lambda-go v1.22.0
	github.com/axiomhq/axiom-go v0.0.0-20201215212509-678033418d51
	github.com/golangci/golangci-lint v1.35.2
	github.com/goreleaser/goreleaser v0.154.0
	github.com/stretchr/testify v1.6.1
	gotest.tools/gotestsum v0.6.0
)

replace github.com/json-iterator/go => github.com/mhr3/jsoniter v1.1.11-0.20200909125010-fb9b85012bdc
