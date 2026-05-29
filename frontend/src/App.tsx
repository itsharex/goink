import { useState, useEffect } from 'react'
import { useApp } from '@/hooks/useApp'
import type { novel } from '@/hooks/useApp'
import InitView from '@/views/InitView'
import NovelListView from '@/views/NovelListView'
import EditorView from '@/views/EditorView'

type View = 'loading' | 'init' | 'novel-list' | 'editor'

export default function App() {
  const [view, setView] = useState<View>('loading')
  const [selectedNovel, setSelectedNovel] = useState<novel.Novel | null>(null)
  const app = useApp()

  useEffect(() => {
    app.IsInitialized().then((ok) => setView(ok ? 'novel-list' : 'init'))
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
      {view === 'init' && <InitView onInitialized={() => setView('novel-list')} />}
      {view === 'novel-list' && (
        <NovelListView
          onNovelClick={(n) => {
            setSelectedNovel(n)
            setView('editor')
          }}
        />
      )}
      {view === 'editor' && selectedNovel && (
        <EditorView
          novel={selectedNovel}
          onBack={() => setView('novel-list')}
        />
      )}
    </div>
  )
}
