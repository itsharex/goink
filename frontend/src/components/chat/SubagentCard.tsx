import { useState, useEffect, useRef, memo } from 'react'
import { Loader2, CheckCircle2, XCircle, ChevronDown } from 'lucide-react'
import type { TurnSegment } from './types'
import ThinkingBlock from './ThinkingBlock'
import MessageBubble from './MessageBubble'
import ToolCallCard from './ToolCallCard'

interface Props {
  agentType: 'memory' | 'review'
  segments: TurnSegment[]
  status: 'streaming' | 'done' | 'failed'
}

const labelMap: Record<string, string> = { memory: '记忆分析师', review: '审核编辑' }

export default memo(function SubagentCard({ agentType, segments, status }: Props) {
  const [collapsed, setCollapsed] = useState(false)
  const autoExpanded = useRef(false)
  const isReview = agentType === 'review'
  const isStreaming = status === 'streaming'
  const isDone = status === 'done'
  const isFailed = status === 'failed'

  const accentBorder = isReview ? 'border-l-emerald-500/60' : 'border-l-primary/60'
  const accentBg = isReview ? 'bg-emerald-50/30' : 'bg-primary/5'

  // streaming 开始时自动展开一次；完成后 1 秒自动折叠一次
  useEffect(() => {
    if (isStreaming && !autoExpanded.current) {
      setCollapsed(false)
      autoExpanded.current = true
    }
    if (!isStreaming) {
      autoExpanded.current = false
    }
    if (isDone) {
      const t = setTimeout(() => setCollapsed(true), 1000)
      return () => clearTimeout(t)
    }
  }, [status])

  const canToggle = !isStreaming

  return (
    <div className={`my-1.5 ml-3 rounded-lg border-l-[3px] ${accentBorder} ${accentBg}`}>
      {/* Header */}
      <button
        onClick={() => canToggle && setCollapsed(!collapsed)}
        className="w-full flex items-center gap-2 px-3 py-2 text-xs hover:bg-muted/30 transition-colors cursor-pointer"
      >
        <span className={`shrink-0 transition-transform duration-200 ${collapsed ? '' : 'rotate-180'}`}>
          <ChevronDown className="w-3 h-3 text-muted-foreground" />
        </span>
        <span className={`font-semibold ${isReview ? 'text-emerald-700' : 'text-primary'}`}>
          {labelMap[agentType]}
        </span>

        <span className="flex-1" />

        {isStreaming && (
          <span className="inline-flex items-center gap-1 rounded-full px-1.5 py-px text-[10px] font-medium text-primary bg-primary/10">
            <Loader2 className="w-2.5 h-2.5 animate-spin" /> 执行中
          </span>
        )}
        {isDone && (
          <span className="inline-flex items-center gap-1 rounded-full px-1.5 py-px text-[10px] font-medium text-emerald-700 bg-emerald-100">
            <CheckCircle2 className="w-2.5 h-2.5" /> 完成
          </span>
        )}
        {isFailed && (
          <span className="inline-flex items-center gap-1 rounded-full px-1.5 py-px text-[10px] font-medium text-destructive bg-destructive/10">
            <XCircle className="w-2.5 h-2.5" /> 失败
          </span>
        )}
      </button>

      {/* Body — grid 折叠，不裁剪内容 */}
      <div
        className={`grid transition-all duration-300 ease-out ${
          collapsed ? 'grid-rows-[0fr] opacity-0' : 'grid-rows-[1fr] opacity-100'
        }`}
      >
        <div className="overflow-hidden">
          <div className="px-3 pb-3 space-y-2 border-t border-border/30 pt-2">
            {segments.length === 0 && isStreaming && (
              <div className="flex items-center gap-2 text-xs text-muted-foreground py-2">
                <Loader2 className="w-3 h-3 animate-spin" /> 正在分析…
              </div>
            )}
            {segments.length === 0 && !isStreaming && (
              <div className="text-xs text-muted-foreground py-2">暂无内容</div>
            )}

            {segments.map(seg => {
              if (seg.type === 'text') {
                return (
                  <div key={seg.id} className="space-y-1">
                    {seg.thinkingContent && (
                      <ThinkingBlock content={seg.thinkingContent} isStreaming={isStreaming && !seg.thinkingDone} />
                    )}
                    {seg.content && (
                      <div className="text-xs">
                        <MessageBubble role="assistant" content={seg.content} />
                      </div>
                    )}
                  </div>
                )
              }
              if (seg.type === 'tool') {
                return (
                  <ToolCallCard
                    key={seg.id}
                    toolName={seg.toolName}
                    displayText={seg.displayText}
                    status={seg.toolStatus}
                    activityKind={seg.activityKind}
                    error={seg.error}
                    compact
                  />
                )
              }
              return null
            })}
          </div>
        </div>
      </div>
    </div>
  )
})
