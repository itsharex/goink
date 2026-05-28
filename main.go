package main

import (
	"embed"
	"log/slog"
	"os"
	"path/filepath"

	ort "github.com/yalue/onnxruntime_go"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"

	"novel/app"
	"novel/internal/logger"
)

//go:embed all:frontend/dist
var assets embed.FS

// findOnnxLib 在常见位置查找 libonnxruntime.so。
func findOnnxLib() string {
	candidates := []string{
		"python-master/backend/.venv/lib/python3.12/site-packages/onnxruntime/capi/libonnxruntime.so",
		"/usr/lib/libonnxruntime.so",
		"/usr/local/lib/libonnxruntime.so",
	}
	for _, p := range candidates {
		if _, err := os.Stat(p); err == nil {
			return p
		}
	}
	return ""
}

func main() {
	log := logger.Default()

	if lib := findOnnxLib(); lib != "" {
		abs, _ := filepath.Abs(lib)
		ort.SetSharedLibraryPath(abs)
		log.Info("ONNX 运行库已设置", "path", abs)
	}

	wapp := app.New(log)

	err := wails.Run(&options.App{
		Title:     "Goink",
		Width:     1400,
		Height:    900,
		MinWidth:  900,
		MinHeight: 600,
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		OnStartup:  wapp.OnStartup,
		OnShutdown: wapp.OnShutdown,
		Bind: []any{
			wapp,
		},
	})
	if err != nil {
		slog.Error("应用退出", "err", err)
		os.Exit(1)
	}
}
