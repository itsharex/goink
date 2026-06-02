import { Loader2, CheckCircle2, XCircle, Eye, Plus, Pencil, Brain, FileText, Wrench } from 'lucide-react'
import { memo } from 'react'

interface Props {
  toolName: string
  displayText: string
  status: 'executing' | 'completed' | 'failed'
  activityKind?: string
  error?: string
  compact?: boolean
}

function activityIcon(kind?: string) {
  switch (kind) {
    case 'view':
    case 'browse':
      return Eye
    case 'create':
      return Plus
    case 'write':
    case 'edit':
      return Pencil
    case 'memory':
      return Brain
    case 'review':
      return CheckCircle2
    case 'plan':
      return FileText
    default:
      return Wrench
  }
}

function activityBadge(kind?: string): string {
  switch (kind) {
    case 'view':
    case 'browse':
      return '查看中'
    case 'create':
      return '创建中'
    case 'write':
      return '写作中'
    case 'edit':
      return '编辑中'
    case 'memory':
      return '检索中'
    case 'review':
      return '审阅中'
    case 'plan':
      return '规划中'
    default:
      return '处理中'
  }
}

export default memo(function ToolCallCard({ displayText, status, activityKind, error, compact }: Props) {
  const Icon = activityIcon(activityKind)
  const isExecuting = status === 'executing'
  const isCompleted = status === 'completed'
  const isFailed = status === 'failed'

  const borderClass = isExecuting
    ? 'border-l-primary bg-primary/5'
    : isCompleted
      ? 'border-l-emerald-500 bg-emerald-50/50'
      : 'border-l-destructive bg-destructive/5'

  const badgeClass = isExecuting
    ? 'text-primary bg-primary/10'
    : isCompleted
      ? 'text-emerald-700 bg-emerald-100'
      : 'text-destructive bg-destructive/10'

  return (
    <div className={`rounded-r-lg border-l-[3px] ${borderClass} transition-colors ${compact ? 'text-[11px]' : 'text-xs'}`}>
      <div className="flex items-center gap-2 py-1.5 pl-2 pr-2.5">
        <span className={`shrink-0 ${isExecuting ? 'text-primary' : isCompleted ? 'text-emerald-600' : 'text-destructive'}`}>
          {isExecuting ? (
            <Loader2 className={`${compact ? 'w-3 h-3' : 'w-3.5 h-3.5'} animate-spin`} />
          ) : isFailed ? (
            <XCircle className={compact ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
          ) : (
            <Icon className={compact ? 'w-3 h-3' : 'w-3.5 h-3.5'} />
          )}
        </span>

        <span className="text-muted-foreground truncate flex-1 min-w-0 leading-[1.35]">
          {displayText}
        </span>

        <span className={`shrink-0 rounded-full px-1.5 py-px font-medium text-[10px] ${badgeClass}`}>
          {isExecuting ? activityBadge(activityKind) : isCompleted ? '完成' : '失败'}
        </span>
      </div>

      {isFailed && error && (
        <div className="px-2 pb-1.5 text-destructive/70 text-[10px] truncate border-t border-destructive/10 pt-1">
          {error.slice(0, 120)}
        </div>
      )}
    </div>
  )
})
