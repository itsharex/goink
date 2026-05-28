import BookCover from './BookCover'
import type { novel } from '@/hooks/useApp'

interface Props {
  novel: novel.Novel
  onClick: () => void
}

export default function NovelCard({ novel, onClick }: Props) {
  return (
    <button
      onClick={onClick}
      className="group text-left w-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-lg"
    >
      <BookCover title={novel.title} />
      <p className="mt-2 text-sm font-medium truncate group-hover:text-primary transition-colors">
        {novel.title}
      </p>
      {novel.genre && (
        <p className="text-xs text-muted-foreground truncate">{novel.genre}</p>
      )}
    </button>
  )
}
