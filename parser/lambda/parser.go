package lambda

import (
	"regexp"
	"strconv"
	"strings"

	"github.com/axiomhq/axiom-cloudwatch-lambda/parser"
)

var (
	// START RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
	// Version: $LATEST
	rStart = regexp.MustCompile(`START RequestId:\s+(?P<request_id>\S+)\s+Version: (?P<version>\S+)`)

	// Standard out from Lambdas.
	rStd = regexp.MustCompile(`\d\d\d\d-\d\d-\d\d\S+\s+(?P<request_id>\S+)`)

	// END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
	rEnd = regexp.MustCompile(`END RequestId:\s+(?P<request_id>\S+)`)

	// REPORT RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46
	// Duration: 0.47 ms
	// Billed Duration: 100 ms
	// Memory Size: 128 MB
	// Max Memory Used: 20 MB
	rReport = regexp.MustCompile(
		`REPORT RequestId:\s+(?P<request_id>\S+)\s+Duration: (?P<duration_ms>\S+) ms\s+Billed Duration: (?P<duration_billed_ms>\S+) ms\s+Memory Size: (?P<memory_size_mb>\S+) MB\s+Max Memory Used: (?P<memory_size_max_mb>\S+) MB`,
	)

	rServiceGroup = regexp.MustCompile("^/aws/(lambda|apigateway|rds|eks)/(.*)")
)

func cleanupReport(dict map[string]interface{}) (map[string]interface{}, error) {
	var err error
	if dict["duration_ms"], err = strconv.ParseFloat(dict["duration_ms"].(string), 64); err != nil {
		return nil, err
	}
	if dict["duration_billed_ms"], err = strconv.Atoi(dict["duration_billed_ms"].(string)); err != nil {
		return nil, err
	}
	if dict["memory_size_mb"], err = strconv.Atoi(dict["memory_size_mb"].(string)); err != nil {
		return nil, err
	}
	if dict["memory_size_max_mb"], err = strconv.Atoi(dict["memory_size_max_mb"].(string)); err != nil {
		return nil, err
	}
	dict["type"] = "report"
	return dict, nil
}

// MatchMessage ...
func MatchMessage(msg string) (map[string]interface{}, string) {
	var (
		dict map[string]interface{}
		err  error
	)
	switch {
	case strings.HasPrefix(msg, "START"):
		if dict, err = RegexpNamedGroupsMatch(rStart, msg); err != nil {
			return parser.NewRawMessage(msg)
		}
		dict["type"] = "start"
	case strings.HasPrefix(msg, "END"):
		if dict, err = RegexpNamedGroupsMatch(rEnd, msg); err != nil {
			return parser.NewRawMessage(msg)
		}
		dict["type"] = "end"
	case strings.HasPrefix(msg, "REPORT"):
		if dict, err = RegexpNamedGroupsMatch(rReport, msg); err != nil {
			return parser.NewRawMessage(msg)
		}
		if dict, err = cleanupReport(dict); err != nil {
			return parser.NewRawMessage(msg)
		}
	default:
		return parser.MatchUnknownMessage(msg)
	}
	return dict, "lambda_info"
}

// ParseServiceGroup ...
func ParseServiceGroup(msg string) (string, string, bool) {
	parsed := rServiceGroup.FindStringSubmatch(msg)
	if len(parsed) == 0 {
		return "", "", false
	}
	return parsed[1], parsed[2], true
}
