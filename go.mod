module github.com/axiomhq/axiom-cloudwatch-lambda

go 1.15

require (
	axicode.axiom.co/watchmakers/logmanager v1.0.4
	github.com/aws/aws-lambda-go v1.20.0
	github.com/axiomhq/axiom-go v0.0.0-20201215212509-678033418d51
	github.com/stretchr/testify v1.6.1
)

replace github.com/json-iterator/go => github.com/mhr3/jsoniter v1.1.11-0.20200909125010-fb9b85012bdc
