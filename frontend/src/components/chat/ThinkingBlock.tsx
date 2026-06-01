import './ThinkingBlock.css'

interface Props {
  content: string
  isStreaming: boolean
}

export default function ThinkingBlock({ content, isStreaming }: Props) {
  if (!content) return null

  return (
    <details className="thinking-block">
      <summary className="thinking-summary">
        <span className="thinking-chevron">▶</span>
        {isStreaming ? (
          <span className="thinking-shimmer">正在思考</span>
        ) : (
          <span>思考过程</span>
        )}
      </summary>
      <div className="thinking-content">
        {content}
      </div>
    </details>
  )
}
