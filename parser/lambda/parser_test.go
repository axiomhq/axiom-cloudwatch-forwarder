package lambda

import (
	"testing"

	"github.com/stretchr/testify/require"
)

type testRegexpMatch struct {
	name     string
	input    string
	expected map[string]interface{}
	format   string
	err      error
}

func TestMatchMessage(t *testing.T) {
	tests := []testRegexpMatch{
		{
			name:  "start",
			input: "START RequestId: c891f2ff-e6ef-4a70-afaf-dea58196b73e Version: $LATEST",
			expected: map[string]interface{}{
				"request_id": "c891f2ff-e6ef-4a70-afaf-dea58196b73e",
				"version":    "$LATEST",
				"type":       "start",
			},
			format: "lambda_info",
		},
		{
			name:  "end",
			input: "END RequestId: b3be449c-8bd7-11e7-bb30-4f271af95c46",
			expected: map[string]interface{}{
				"request_id": "b3be449c-8bd7-11e7-bb30-4f271af95c46",
				"type":       "end",
			},
			format: "lambda_info",
		},
		{
			name: "report",
			input: "REPORT RequestId: c891f2ff-e6ef-4a70-afaf-dea58196b73e	Duration: 549.57 ms	Billed Duration: 550 ms	Memory Size: 512 MB	Max Memory Used: 44 MB	Init Duration: 91.46 ms",
			expected: map[string]interface{}{
				"request_id":         "c891f2ff-e6ef-4a70-afaf-dea58196b73e",
				"duration_ms":        549.57,
				"duration_billed_ms": 550,
				"memory_size_max_mb": 44,
				"memory_size_mb":     512,
				"type":               "report",
			},
			format: "lambda_info",
		},
		{
			name:     "misc",
			input:    `{"hello": "world"}`,
			expected: map[string]interface{}{"hello": "world"},
			format:   "json",
		},
	}

	for _, test := range tests {
		dict, format := MatchMessage(test.input)
		require.Equal(t, test.format, format)
		require.Equal(t, test.expected, dict, test.name)
	}
}
