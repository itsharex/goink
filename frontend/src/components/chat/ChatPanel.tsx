import { useState, useCallback, useRef, useEffect } from 'react'
import { MessageSquare, Loader2 } from 'lucide-react'
import { useApp } from '@/hooks/useApp'
import ChatInput from './ChatInput'
import MessageBubble from './MessageBubble'

interface Props {
  novelId: number
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
}

const MIN_WIDTH = 280
const MAX_WIDTH = 600
const DEFAULT_WIDTH = 360

export default function ChatPanel({ novelId }: Props) {
  const app = useApp()
  const [width, setWidth] = useState(DEFAULT_WIDTH)
  const [isDragging, setIsDragging] = useState(false)
  const startXRef = useRef(0)
  const startWidthRef = useRef(DEFAULT_WIDTH)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sessionId, setSessionId] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [provider, setProvider] = useState('')
  const [model, setModel] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const counterRef = useRef(0)

  // 加载默认模型
  useEffect(() => {
    app.GetModels().then(models => {
      if (models && models.length > 0) {
        const m = models[0]
        const [p, id] = m.Key.split('/')
        setProvider(p)
        setModel(id)
      }
    }).catch(() => {})
  }, [])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    startXRef.current = e.clientX
    startWidthRef.current = width
  }, [width])

  useEffect(() => {
    if (!isDragging) return
    const handleMouseMove = (e: MouseEvent) => {
      const delta = e.clientX - startXRef.current
      const newWidth = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, startWidthRef.current - delta))
      setWidth(newWidth)
    }
    const handleMouseUp = () => setIsDragging(false)
    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = useCallback(async (content: string) => {
    if (!provider || !model) return

    const userMsg: ChatMessage = {
      id: `msg_${++counterRef.current}`,
      role: 'user',
      content,
    }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    try {
      const result = await app.Chat(null as any, {
        session_id: sessionId,
        novel_id: novelId,
        message: content,
        provider_name: provider,
        model_id: model,
        reasoning_effort: '',
      })

      if (result.session_id) {
        setSessionId(result.session_id)
      }

      if (result.final_text) {
        const assistantMsg: ChatMessage = {
          id: `msg_${++counterRef.current}`,
          role: 'assistant',
          content: result.final_text,
        }
        setMessages(prev => [...prev, assistantMsg])
      }
    } catch (err) {
      const errMsg: ChatMessage = {
        id: `msg_${++counterRef.current}`,
        role: 'assistant',
        content: `错误: ${String(err)}`,
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }, [sessionId, novelId, provider, model, app])

  const hasNovel = novelId > 0
  const hasMessages = messages.length > 0

  const inputPlaceholder = !hasNovel
    ? '请先选择作品'
    : !provider
      ? '请先配置模型'
      : isLoading
        ? 'AI 回复中...'
        : '输入消息...'

  return (
    <aside className="shrink-0 flex flex-col bg-background border-l relative" style={{ width }}>
      <div
        className="absolute left-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-primary/30 transition-colors z-10"
        style={{ marginLeft: -2 }}
        onMouseDown={handleMouseDown}
      />

      <div className="px-4 py-2.5 border-b shrink-0">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">AI 对话</span>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-3">
        {!hasNovel ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <MessageSquare className="w-10 h-10 text-muted-foreground/20 mx-auto mb-3" />
              <p className="text-sm text-muted-foreground">选择作品开始对话</p>
            </div>
          </div>
        ) : !hasMessages && !isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <MessageSquare className="w-10 h-10 text-muted-foreground/20 mx-auto mb-3" />
              <p className="text-sm text-muted-foreground">输入消息开始对话</p>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {messages.map(msg => (
              <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
            ))}
          </div>
        )}

        {isLoading && (
          <div className="flex justify-start mt-3">
            <div className="bg-muted rounded-lg rounded-bl-sm px-3 py-2">
              <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        disabled={!hasNovel || isLoading || !provider}
        placeholder={inputPlaceholder}
        onSend={handleSend}
      />

      {isDragging && (
        <div className="fixed inset-0 z-50 cursor-col-resize select-none" />
      )}
    </aside>
  )
}
