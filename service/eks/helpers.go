package eks

import (
	"encoding/json"
	"strings"
)

// MatchMessage ...
func MatchMessage(group, msg string) (map[string]interface{}, string) {
	// FIXME: replace with regex
	split := strings.Split(group, "-")
	subService := group
	if len(split) > 1 {
		subService = strings.Join(split[:len(split)-1], "-")
	}
	dict := map[string]interface{}{}
	typ := "eks_info"

	if err := json.Unmarshal([]byte(msg), &dict); err != nil {
		dict["raw_message"] = msg
		typ = "unknown"
	}

	dict["app"] = subService
	return dict, typ
}
