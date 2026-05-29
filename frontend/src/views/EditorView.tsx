import { useState } from 'react'
import type { novel } from '@/hooks/useApp'
import BackButton from '@/components/shared/BackButton'
import ActivityBar from '@/components/shell/ActivityBar'
import StatusBar from '@/components/shell/StatusBar'
import { FileText, Plus } from 'lucide-react'

interface Props {
  novel: novel.Novel
  onBack: () => void
}

export default function EditorView({ novel: n, onBack }: Props) {
  const [activeId, setActiveId] = useState('editor')

  return (
    <div className="h-screen flex flex-col">
      {/* 工具栏 */}
      <header className="h-11 flex items-center justify-between px-4 border-b bg-muted/10 shrink-0">
        <div className="flex items-center gap-3">
          <BackButton onClick={onBack} />
          <span className="text-sm font-medium text-muted-foreground">{n.title}</span>
        </div>
        <div className="flex items-center gap-2">
          <button className="text-xs text-muted-foreground hover:text-foreground transition-colors px-2 py-1 rounded">
            大纲
          </button>
          <button className="text-xs text-foreground bg-muted px-2 py-1 rounded">
            正文
          </button>
        </div>
      </header>

      {/* 主区域 */}
      <div className="flex-1 flex min-h-0">
        <ActivityBar activeId={activeId} onSelect={setActiveId} />

        {/* 侧面板 — 根据 activeId 切换内容 */}
        <aside className="w-56 border-r bg-background flex flex-col shrink-0">
          {activeId === 'editor' ? (
            <>
              <div className="flex items-center justify-between px-3 py-2.5 border-b">
                <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  章节列表
                </span>
                <button className="w-6 h-6 flex items-center justify-center rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors">
                  <Plus className="w-4 h-4" />
                </button>
              </div>
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <FileText className="w-8 h-8 text-muted-foreground/30 mx-auto mb-2" />
                  <p className="text-xs text-muted-foreground">暂无章节</p>
                  <p className="text-xs text-muted-foreground/60 mt-0.5">点击 + 创建第一章</p>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <p className="text-xs text-muted-foreground">即将推出</p>
            </div>
          )}
        </aside>

        {/* 编辑区 */}
        <main className="flex-1 bg-background flex items-center justify-center border-r">
          <div className="text-center">
            <FileText className="w-12 h-12 text-muted-foreground/20 mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">选择或创建章节开始写作</p>
          </div>
        </main>

        {/* 聊天区 */}
        <aside className="w-80 bg-muted/10 flex flex-col shrink-0">
          <div className="px-4 py-2.5 border-b">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
              AI 对话
            </span>
          </div>
          <div className="flex-1 flex items-center justify-center">
            <p className="text-xs text-muted-foreground">选择章节后开始对话</p>
          </div>
          <div className="p-3 border-t">
            <div className="flex items-center gap-2">
              <input
                type="text"
                placeholder="输入消息..."
                disabled
                className="flex-1 h-8 rounded-md border bg-background px-3 text-xs text-muted-foreground"
              />
              <button
                disabled
                className="w-8 h-8 flex items-center justify-center rounded-md bg-muted text-muted-foreground/50"
              >
                →
              </button>
            </div>
          </div>
        </aside>
      </div>

      <StatusBar />
    </div>
  )
}
