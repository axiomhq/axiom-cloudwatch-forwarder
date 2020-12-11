package unknown

import (
	"encoding/json"
)

// MatchMessage ...
func MatchMessage(group, msg string) (map[string]interface{}, string) {
	dict := map[string]interface{}{}
	typ := "json"

	if err := json.Unmarshal([]byte(msg), &dict); err != nil {
		dict["raw_message"] = msg
		typ = "unknown"
	}

	return dict, typ
}
