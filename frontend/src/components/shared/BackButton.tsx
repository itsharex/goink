import { ArrowLeft } from 'lucide-react'

interface Props {
  onClick: () => void
  label?: string
}

export default function BackButton({ onClick, label = '返回' }: Props) {
  return (
    <button
      onClick={onClick}
      className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <ArrowLeft className="w-4 h-4" />
      <span>{label}</span>
    </button>
  )
}
