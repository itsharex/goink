import {
  Chat,
  CreateChapter,
  CreateNovel,
  GetChapterContent,
  SaveChapterContent,
  SetActiveNovel,
  GetAppConfig,
  GetChapters,
  GetNovels,
  GetPlatform,
  GetSettings,
  Initialize,
  IsInitialized,
  SaveSettings,
} from '@/lib/wailsjs/go/app/App'
import type { app, novel, chapter, config } from '@/lib/wailsjs/go/models'

export function useApp() {
  return {
    Chat,
    CreateChapter,
    CreateNovel,
    GetChapterContent,
    SaveChapterContent,
    GetAppConfig,
    GetChapters,
    GetNovels,
    GetPlatform,
    GetSettings,
    Initialize,
    IsInitialized,
    SaveSettings,
    SetActiveNovel,
  }
}

export type { app, novel, chapter, config }
