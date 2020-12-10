module axicode.axiom.co/watchmakers/axiom-cloudwatch-lambda

go 1.15

require (
	axicode.axiom.co/watchmakers/axiomdb v1.3.0-beta.1.0.20201209171547-bc85be56dbfd
	axicode.axiom.co/watchmakers/go-lambda-proxy v1.1.0
	axicode.axiom.co/watchmakers/logmanager v1.0.4
	github.com/aws/aws-lambda-go v1.20.0
	github.com/stretchr/testify v1.6.1
)

replace github.com/json-iterator/go => github.com/mhr3/jsoniter v1.1.11-0.20200909125010-fb9b85012bdc
