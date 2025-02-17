package internal

import (
	"os"
	"strings"
)

// Contains checks is needle exists in elems.
// Yoinked from https://gosamples.dev/generics-slice-contains/.
func Contains[T comparable](elems []T, needle T) bool {
	for _, elem := range elems {
		if needle == elem {
			return true
		}
	}
	return false
}

func ExpandUser(path string) string {
	return strings.Replace(path, "~", os.Getenv("HOME"), 1)
}
