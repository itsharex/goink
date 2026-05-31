import { useState, useEffect, useCallback } from 'react'
import { Folder, Loader2, CheckCircle2, AlertCircle } from 'lucide-react'
import { useApp } from '@/hooks/useApp'

export default function GeneralConfigTab() {
  const app = useApp()
  const [dataDir, setDataDir] = useState('')
  const [origDataDir, setOrigDataDir] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    app.GetAppConfig().then(cfg => {
      const dir = (cfg?.data_dir as string) || ''
      setDataDir(dir)
      setOrigDataDir(dir)
    }).catch(() => {})
  }, [app])

  const hasChanged = dataDir !== origDataDir

  const handleSave = useCallback(async () => {
    const trimmed = dataDir.trim()
    if (!trimmed || trimmed === origDataDir) return
    setIsSaving(true)
    setError('')
    setSaved(false)
    try {
      await app.UpdateDataDir(trimmed)
      setOrigDataDir(trimmed)
      setSaved(true)
    } catch (e) {
      setError(String(e))
    } finally {
      setIsSaving(false)
    }
  }, [dataDir, origDataDir, app])

  return (
    <div className="flex-1 flex flex-col">
      <h3 className="text-sm font-medium mb-5">基础配置</h3>

      {/* 数据目录 */}
      <div className="space-y-2">
        <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
          <Folder className="w-3.5 h-3.5" />
          数据目录
        </label>
        <div className="flex items-center gap-2">
          <input
            value={dataDir}
            onChange={e => { setDataDir(e.target.value); setSaved(false); setError('') }}
            placeholder="输入数据目录路径..."
            className="flex-1 h-8 rounded-md border bg-muted/30 px-3 text-xs font-mono focus:outline-none focus:ring-1 focus:ring-primary"
          />
          <button
            onClick={handleSave}
            disabled={!hasChanged || isSaving || !dataDir.trim()}
            className="h-8 px-3 rounded-md bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 disabled:opacity-50 transition-opacity cursor-pointer shrink-0"
          >
            {isSaving ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              '更改'
            )}
          </button>
        </div>

        {saved && (
          <p className="text-xs text-green-600 flex items-center gap-1">
            <CheckCircle2 className="w-3 h-3" />
            数据目录已更改，已重新初始化
          </p>
        )}
        {error && (
          <p className="text-xs text-red-500 flex items-center gap-1">
            <AlertCircle className="w-3 h-3 shrink-0" />
            {error}
          </p>
        )}

        <p className="text-[11px] text-muted-foreground">
          更改后会立即切换到新目录并重新加载所有数据
        </p>
      </div>
    </div>
  )
}
