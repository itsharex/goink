import {
  Chat,
  CreateChapter,
  CreateNovel,
  GetContent,
  SaveContent,
  SetActiveNovel,
  GetAppConfig,
  GetChapters,
  GetNovels,
  GetPlatform,
  GetSettings,
  Initialize,
  IsInitialized,
  SaveSettings,
  GetModels,
  GetSessions,
  GetSessionMessages,
} from '@/lib/wailsjs/go/app/App'
import type { app, novel, chapter, config, llm, session } from '@/lib/wailsjs/go/models'

export function useApp() {
  return {
    Chat,
    CreateChapter,
    CreateNovel,
    GetContent,
    SaveContent,
    GetAppConfig,
    GetChapters,
    GetNovels,
    GetPlatform,
    GetSettings,
    Initialize,
    IsInitialized,
    SaveSettings,
    SetActiveNovel,
    GetModels,
    GetSessions,
    GetSessionMessages,
  }
}

export type { app, novel, chapter, config, llm, session }
