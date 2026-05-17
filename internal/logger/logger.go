package logger

import (
	"io"
	"log/slog"
	"os"
)

// New 创建结构化日志器。
//
//	format: "text"（开发环境）或 "json"（生产环境）
//	level:  slog.LevelDebug / Info / Warn / Error
//	out:    os.Stdout、os.Stderr 或文件
func New(level slog.Level, format string, out io.Writer) *slog.Logger {
	var handler slog.Handler

	opts := &slog.HandlerOptions{
		Level:     level,
		AddSource: true,
	}

	switch format {
	case "json":
		handler = slog.NewJSONHandler(out, opts)
	default:
		handler = slog.NewTextHandler(out, opts)
	}

	return slog.New(handler)
}

// Default 返回开发环境默认日志器：文本格式、Debug 级别、输出到 stderr。
func Default() *slog.Logger {
	return New(slog.LevelDebug, "text", os.Stderr)
}
