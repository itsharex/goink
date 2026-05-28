.PHONY: dev build frontend-dev frontend-build clean

# 启动 Wails 开发模式（Go 后端 + Vite HMR 前端）
dev:
	wails dev -tags webkit2_41

# 生产构建（单二进制）
build:
	cd frontend && npm run build
	wails build -tags webkit2_41

# 纯前端开发（浏览器模式，后端不可用）
frontend-dev:
	cd frontend && npm run dev

# 纯前端构建
frontend-build:
	cd frontend && npm run build

# 清理构建产物
clean:
	rm -rf frontend/dist frontend/node_modules
