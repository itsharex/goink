import type { LucideIcon } from 'lucide-react'
import { PenLine, Users, MapPin, BookOpen } from 'lucide-react'

interface Activity {
  id: string
  icon: LucideIcon
  label: string
  disabled?: boolean
}

const activities: Activity[] = [
  { id: 'editor', icon: PenLine, label: '创作工坊' },
  { id: 'characters', icon: Users, label: '角色管理', disabled: true },
  { id: 'locations', icon: MapPin, label: '地点管理', disabled: true },
  { id: 'toc', icon: BookOpen, label: '章节目录', disabled: true },
]

interface Props {
  activeId: string
  onSelect: (id: string) => void
}

export default function ActivityBar({ activeId, onSelect }: Props) {
  return (
    <nav className="w-12 flex flex-col items-center py-3 gap-1.5 border-r bg-muted/20">
      {activities.map((a) => {
        const isActive = a.id === activeId
        return (
          <button
            key={a.id}
            disabled={a.disabled}
            onClick={() => onSelect(a.id)}
            title={`${a.label}${a.disabled ? '（即将推出）' : ''}`}
            className={`relative w-10 h-10 flex items-center justify-center rounded-lg transition-all duration-200
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
              ${a.disabled
                ? 'text-muted-foreground/40 cursor-not-allowed'
                : isActive
                  ? 'text-foreground bg-muted'
                  : 'text-muted-foreground hover:text-foreground hover:bg-muted/60'
              }`}
          >
            {/* 激活指示条 */}
            {isActive && !a.disabled && (
              <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-primary rounded-r-full" />
            )}
            <a.icon className="w-5 h-5" />
          </button>
        )
      })}
    </nav>
  )
}
