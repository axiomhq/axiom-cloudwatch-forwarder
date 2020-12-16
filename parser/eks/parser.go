package eks

import (
	"strings"

	"github.com/axiomhq/axiom-cloudwatch-lambda/parser"
)

// MatchMessage ...
func MatchMessage(group, msg string) (map[string]interface{}, string) {
	// FIXME: replace with regex
	split := strings.Split(group, "-")
	subService := group
	if len(split) > 1 {
		subService = strings.Join(split[:len(split)-1], "-")
	}
	dict, format := parser.MatchUnknownMessage(msg)
	dict["app"] = subService
	return dict, format
}
