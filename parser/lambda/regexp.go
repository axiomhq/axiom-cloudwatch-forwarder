package lambda

import (
	"fmt"
	"regexp"
)

// RegexpNamedGroupsMatch - returns a map of matched values
// golang will give you an array of values that matches your submatch
// but not a map, you have to manually correlate it over to a map
func RegexpNamedGroupsMatch(pattern *regexp.Regexp, search string) (map[string]interface{}, error) {
	if !pattern.MatchString(search) {
		return nil, fmt.Errorf("could not match string %s", search)
	}
	namedGroupMatch := make(map[string]interface{})
	groups := pattern.SubexpNames()
	for _, group := range groups {
		if group == "" {
			continue
		}
		namedGroupMatch[group] = ""
	}

	for index, submatch := range pattern.FindStringSubmatch(search) {
		// first returned value is just the entire string, which is totally useful. skip it.
		if index < 1 {
			continue
		}
		namedGroupMatch[groups[index]] = submatch
	}

	return namedGroupMatch, nil
}
