import { useState, useEffect } from 'react'

type View = 'loading' | 'init' | 'novel-list'

export default function App() {
  const [view, setView] = useState<View>('loading')

  useEffect(() => {
    // TODO: 替换为真实的 Wails IPC 调用
    // App.IsInitialized().then(ok => setView(ok ? 'novel-list' : 'init'))
    const timer = setTimeout(() => setView('novel-list'), 500)
    return () => clearTimeout(timer)
  }, [])

  if (view === 'loading') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <p className="text-muted-foreground">加载中...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {view === 'init' && (
        <div className="flex items-center justify-center min-h-screen">
          <p>初始化页面（待实现）</p>
        </div>
      )}
      {view === 'novel-list' && (
        <div className="flex items-center justify-center min-h-screen">
          <p>小说列表（待实现）</p>
        </div>
      )}
    </div>
  )
}
