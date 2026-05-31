import { useEffect, useRef, useState, useCallback } from 'react'
import { X, MessageSquare, Loader2 } from 'lucide-react'
import type { app } from '@/hooks/useApp'
import { useApp } from '@/hooks/useApp'

interface Props {
  open: boolean
  novelId: number
  onClose: () => void
  onSelectSession: (sessionId: string) => void
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const min = Math.floor(diff / 60000)
  if (min < 1) return '刚刚'
  if (min < 60) return `${min} 分钟前`
  const hour = Math.floor(min / 60)
  if (hour < 24) return `${hour} 小时前`
  const day = Math.floor(hour / 24)
  if (day < 30) return `${day} 天前`
  return `${Math.floor(day / 30)} 个月前`
}

export default function SessionHistory({ open, novelId, onClose, onSelectSession }: Props) {
  const app = useApp()
  const [sessions, setSessions] = useState<app.SessionMeta[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [hasMore, setHasMore] = useState(true)
  const listRef = useRef<HTMLDivElement>(null)
  const loadingRef = useRef(false)

  const loadPageRef = useRef<(p: number) => void>(null as any)

  loadPageRef.current = async (p: number) => {
    if (loadingRef.current) return
    loadingRef.current = true
    setIsLoading(true)
    try {
      const result = await app.GetSessions(novelId, p, 20)
      if (result?.items) {
        setSessions(prev => p === 1 ? result.items : [...prev, ...result.items])
        setTotal(result.total)
        setHasMore(result.page < result.total_pages)
      }
    } catch {
      // ignore
    } finally {
      setIsLoading(false)
      loadingRef.current = false
    }
  }

  useEffect(() => {
    if (!open) return
    setSessions([])
    setPage(1)
    setHasMore(true)
    loadPageRef.current?.(1)
  }, [open, novelId])

  const handleScroll = useCallback(() => {
    if (!listRef.current || !hasMore || isLoading) return
    const { scrollTop, scrollHeight, clientHeight } = listRef.current
    if (scrollHeight - scrollTop - clientHeight < 80) {
      const next = page + 1
      setPage(next)
      loadPageRef.current?.(next)
    }
  }, [hasMore, isLoading, page])

  if (!open) return null

  return (
    <div className="absolute inset-x-0 z-40 flex flex-col bg-background border-b shadow-lg"
      style={{ height: '35%', top: '33px' }}>
      {/* 面板头部 */}
      <div className="flex items-center justify-between px-4 py-2 border-b shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium">历史会话</span>
          {total > 0 && (
            <span className="text-[10px] text-muted-foreground">共 {total} 个</span>
          )}
        </div>
        <button
          onClick={onClose}
          className="w-6 h-6 flex items-center justify-center rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 搜索框（占位） */}
      <div className="px-4 py-2 shrink-0">
        <input
          disabled
          placeholder="搜索会话..."
          className="w-full h-7 rounded-md border bg-muted/30 px-2.5 text-xs text-muted-foreground"
        />
      </div>

      {/* 会话列表 */}
      <div
        ref={listRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto px-3 pb-2"
      >
        {sessions.length === 0 && isLoading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="space-y-0.5">
            {sessions.map(s => (
              <button
                key={s.session_id}
                onClick={() => { onSelectSession(s.session_id); onClose() }}
                className="w-full flex items-center gap-2.5 px-2.5 py-2.5 rounded-lg text-left hover:bg-muted/50 transition-colors"
              >
                <MessageSquare className="w-4 h-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <div className="text-xs truncate">{s.title || '新对话'}</div>
                  <div className="text-[10px] text-muted-foreground mt-0.5">{timeAgo(s.updated_at)}</div>
                </div>
              </button>
            ))}
            {isLoading && (
              <div className="flex justify-center py-3">
                <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
              </div>
            )}
            {!hasMore && sessions.length > 0 && (
              <div className="text-center text-[10px] text-muted-foreground py-2">已显示全部会话</div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
