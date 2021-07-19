module github.com/axiomhq/axiom-cloudwatch-lambda

go 1.16

require (
	github.com/Djarvur/go-err113 v0.1.0 // indirect
	github.com/aws/aws-lambda-go v1.25.0
	github.com/axiomhq/axiom-go v0.2.2
	github.com/axiomhq/pkg v0.0.0-20210318171555-dc26762456be
	github.com/golangci/golangci-lint v1.41.1
	github.com/goreleaser/goreleaser v0.173.2
	github.com/gostaticanalysis/analysisutil v0.6.1 // indirect
	github.com/quasilyte/regex/syntax v0.0.0-20200805063351-8f842688393c // indirect
	github.com/stretchr/objx v0.3.0 // indirect
	github.com/stretchr/testify v1.7.0
	gotest.tools/gotestsum v1.6.4
)

replace github.com/json-iterator/go => github.com/mhr3/jsoniter v1.1.11-0.20200909125010-fb9b85012bdc
