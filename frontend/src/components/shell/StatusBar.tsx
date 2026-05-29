export default function StatusBar() {
  return (
    <div className="h-7 flex items-center justify-between px-4 border-t bg-muted/20 text-xs text-muted-foreground select-none">
      <div className="flex items-center gap-4">
        <span>字数 0</span>
        <span>行数 0</span>
      </div>
      <span className="flex items-center gap-1">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        已保存
      </span>
    </div>
  )
}
