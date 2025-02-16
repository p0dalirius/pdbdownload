package utils

import (
	"fmt"
	"time"
)

// ElapsedTime calculates and formats the elapsed time since the provided start time,
// only including non-zero components in the output.
func ElapsedTime(startTime time.Time) string {
	elapsedTime := time.Since(startTime).Round(time.Millisecond)
	hours := int(elapsedTime.Hours())
	minutes := int(elapsedTime.Minutes()) % 60
	seconds := int(elapsedTime.Seconds()) % 60
	milliseconds := int(elapsedTime.Milliseconds()) % 1000

	result := ""
	if hours > 0 {
		result += fmt.Sprintf("%dh ", hours)
	}
	if minutes > 0 {
		result += fmt.Sprintf("%dm ", minutes)
	}
	if seconds > 0 {
		result += fmt.Sprintf("%ds ", seconds)
	}
	if milliseconds > 0 {
		result += fmt.Sprintf("%dms", milliseconds)
	}

	if len(result) == 0 {
		result += "0ms"
	}

	return result
}
