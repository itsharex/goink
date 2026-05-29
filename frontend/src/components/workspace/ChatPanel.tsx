export default function ChatPanel() {
  return (
    <aside className="w-80 bg-muted/10 flex flex-col shrink-0">
      <div className="px-4 py-2.5 border-b">
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">AI 对话</span>
      </div>
      <div className="flex-1 flex items-center justify-center">
        <p className="text-xs text-muted-foreground">选择章节后开始对话</p>
      </div>
      <div className="p-3 border-t">
        <div className="flex items-center gap-2">
          <input type="text" placeholder="输入消息..." disabled
            className="flex-1 h-8 rounded-md border bg-background px-3 text-xs text-muted-foreground" />
          <button disabled className="w-8 h-8 flex items-center justify-center rounded-md bg-muted text-muted-foreground/50">→</button>
        </div>
      </div>
    </aside>
  )
}
