package parser

import (
	"encoding/json"
)

// Formats ...
const (
	FormatUnknown = "unknown"
	FormatJSON    = "json"
)

// MatchUnknownMessage ...
func MatchUnknownMessage(msg string) (map[string]interface{}, string) {
	dict := map[string]interface{}{}
	if err := json.Unmarshal([]byte(msg), &dict); err != nil {
		return NewRawMessage(msg)
	}
	data := shrinkJSON(dict, 3)
	return data, FormatJSON
}

// NewRawMessage ...
func NewRawMessage(msg string) (map[string]interface{}, string) {
	return map[string]interface{}{"message": msg}, FormatUnknown
}

// TrimJSON ...
func shrinkJSON(data map[string]interface{}, depth uint8) map[string]interface{} {
	newData := make(map[string]interface{})
	for k, v := range data {
		if depth <= 1 {
			p, _ := json.Marshal(v)
			newData[k] = string(p)
			continue
		}

		subData, ok := v.(map[string]interface{})
		if !ok {
			newData[k] = v
		} else {
			newData[k] = shrinkJSON(subData, depth-1)
		}
	}
	return newData
}
