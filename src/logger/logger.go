package logger

import (
	"fmt"
	"time"
)

func Info(message string) {
	currentTime := time.Now().Format("2006-01-02 15:04:05")
	fmt.Printf("[%s] INFO: %s\n", currentTime, message)
}

func Warn(message string) {
	currentTime := time.Now().Format("2006-01-02 15:04:05")
	fmt.Printf("[%s] WARN: %s\n", currentTime, message)
}

func Debug(message string) {
	currentTime := time.Now().Format("2006-01-02 15:04:05")
	fmt.Printf("[%s] DEBUG: %s\n", currentTime, message)
}
