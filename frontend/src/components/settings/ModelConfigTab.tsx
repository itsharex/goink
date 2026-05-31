import { useState, useEffect, useCallback } from 'react'
import { Loader2 } from 'lucide-react'
import { useApp } from '@/hooks/useApp'
import type { llm } from '@/hooks/useApp'
import BuiltinProviderPane from './BuiltinProviderPane'
import CustomProviderPane from './CustomProviderPane'

type SubNav = 'builtin' | 'custom'

export default function ModelConfigTab() {
  const app = useApp()
  const [providers, setProviders] = useState<llm.ProviderView[]>([])
  const [subNav, setSubNav] = useState<SubNav>('builtin')
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [saveMsg, setSaveMsg] = useState('')

  useEffect(() => {
    app.GetLLMConfig().then(config => {
      if (config?.providers) {
        setProviders(config.providers)
      }
    }).catch(() => {}).finally(() => setIsLoading(false))
  }, [])

  const builtinProviders = providers.filter(p => p.source === 'builtin')
  const customProviders = providers.filter(p => p.source === 'custom')

  const handleUpdateProvider = useCallback((key: string, patch: Partial<llm.ProviderView>) => {
    setProviders(prev => prev.map(p => p.key === key ? { ...p, ...patch } as unknown as llm.ProviderView : p))
  }, [])

  const handleAddCustomProvider = useCallback((provider: llm.ProviderView) => {
    setProviders(prev => [...prev, provider])
  }, [])

  const handleRemoveCustomProvider = useCallback((key: string) => {
    setProviders(prev => prev.filter(p => p.key !== key))
  }, [])

  const handleAddCustomModel = useCallback((providerKey: string, model: llm.ModelInfo) => {
    setProviders(prev => prev.map(p => {
      if (p.key !== providerKey) return p
      const models = [...(p.custom_models || []), model]
      return { ...p, custom_models: models } as unknown as llm.ProviderView
    }))
  }, [])

  const handleRemoveCustomModel = useCallback((providerKey: string, modelId: string) => {
    setProviders(prev => prev.map(p => {
      if (p.key !== providerKey) return p
      const models = (p.custom_models || []).filter(m => m.id !== modelId)
      return { ...p, custom_models: models } as unknown as llm.ProviderView
    }))
  }, [])

  const handleSave = useCallback(async () => {
    // 检查有自定义模型但没配 key 的 provider
    const missingKey = providers.filter(p => p.custom_models?.length > 0 && !p.api_key)
    if (missingKey.length > 0) {
      const names = missingKey.map(p => p.name).join('、')
      setSaveMsg(`"${names}" 添加了自定义模型但未配置 API Key，将不会被保存`)
      setTimeout(() => setSaveMsg(''), 4000)
      return
    }

    setIsSaving(true)
    setSaveMsg('')
    try {
      await app.SaveLLMConfig({ providers } as unknown as llm.LLMConfigView)
      setSaveMsg('配置已保存')
      setTimeout(() => setSaveMsg(''), 2000)
    } catch (err) {
      setSaveMsg(`保存失败: ${String(err)}`)
    } finally {
      setIsSaving(false)
    }
  }, [providers, app])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* 子导航 */}
      <div className="flex gap-6 px-1 mb-4">
        <button
          onClick={() => setSubNav('builtin')}
          className={`text-sm pb-1 transition-colors ${
            subNav === 'builtin'
              ? 'text-foreground border-b-2 border-primary font-medium'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          内置服务商
        </button>
        <button
          onClick={() => setSubNav('custom')}
          className={`text-sm pb-1 transition-colors ${
            subNav === 'custom'
              ? 'text-foreground border-b-2 border-primary font-medium'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          自定义服务商
        </button>
      </div>

      {/* 内容区 */}
      <div className="flex-1 overflow-y-auto">
        {subNav === 'builtin' ? (
          <BuiltinProviderPane
            providers={builtinProviders}
            onUpdate={handleUpdateProvider}
            onAddCustomModel={handleAddCustomModel}
            onRemoveCustomModel={handleRemoveCustomModel}
          />
        ) : (
          <CustomProviderPane
            providers={customProviders}
            onAdd={handleAddCustomProvider}
            onUpdate={handleUpdateProvider}
            onRemove={handleRemoveCustomProvider}
            onAddCustomModel={handleAddCustomModel}
            onRemoveCustomModel={handleRemoveCustomModel}
          />
        )}
      </div>

      {/* 底部保存栏 */}
      <div className="flex items-center justify-end gap-3 pt-4 border-t mt-4">
        {saveMsg && (
          <span className={`text-xs ${saveMsg.startsWith('保存失败') ? 'text-red-500' : 'text-emerald-600'}`}>
            {saveMsg}
          </span>
        )}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="h-8 px-4 rounded-md bg-primary text-primary-foreground text-sm disabled:opacity-50"
        >
          {isSaving ? '保存中...' : '保存配置'}
        </button>
      </div>
    </div>
  )
}
