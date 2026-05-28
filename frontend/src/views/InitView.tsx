import { useState, useEffect } from 'react'
import { useApp } from '@/hooks/useApp'
import { Button } from '@/components/ui/button'

interface Props {
  onInitialized: () => void
}

export default function InitView({ onInitialized }: Props) {
  const app = useApp()
  const [dataDir, setDataDir] = useState('')
  const [defaultPath, setDefaultPath] = useState('~/.goink')
  const [platformOS, setPlatformOS] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    app.GetPlatform().then((info) => {
      if (info.defaultPath) {
        setDefaultPath(info.defaultPath as string)
        setDataDir(info.defaultPath as string)
      }
      if (info.os) setPlatformOS(info.os as string)
    })
  }, [])

  async function handleInit() {
    const dir = dataDir.trim()
    if (!dir) return
    setLoading(true)
    setError('')
    try {
      await app.Initialize(dir)
      onInitialized()
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const isWindows = platformOS === 'windows'
  const windowsDrive = defaultPath.match(/^([A-Z]):/)?.[1]

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-full max-w-md mx-auto p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-semibold tracking-tight mb-2">
            欢迎使用 Goink
          </h1>
          <p className="text-muted-foreground text-sm">
            请选择数据存储位置，你的所有创作数据将保存在此目录。
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">
              数据目录
            </label>
            <input
              type="text"
              value={dataDir}
              onChange={(e) => setDataDir(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {isWindows
                ? `默认路径: ${windowsDrive}:\\Goink（配置与数据分开存储）`
                : '默认路径: ~/.goink（配置与数据存储在同一目录）'}
            </p>
          </div>

          {error && (
            <p className="text-sm text-destructive">{error}</p>
          )}

          <Button
            className="w-full"
            onClick={handleInit}
            disabled={loading || !dataDir.trim()}
          >
            {loading ? '正在初始化...' : '开始使用'}
          </Button>
        </div>
      </div>
    </div>
  )
}
