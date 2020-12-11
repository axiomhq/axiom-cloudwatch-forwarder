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
	return dict, FormatJSON
}

// NewRawMessage ...
func NewRawMessage(msg string) (map[string]interface{}, string) {
	return map[string]interface{}{"message": msg}, FormatUnknown
}
