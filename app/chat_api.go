package app

import (
	"novel/internal/llm"
	"novel/internal/session"
	"novel/internal/storage"
)

// SessionMeta 是前端会话列表的轻量视图。
type SessionMeta struct {
	SessionID string `json:"session_id"`
	Title     string `json:"title"`
	Model     string `json:"model"`
	UpdatedAt string `json:"updated_at"` // ISO 8601
}

// GetModels 返回所有可用模型列表，由后端决定能力和推理程度。
func (a *App) GetModels() []llm.AvailableModel {
	if a.llmClient == nil {
		return nil
	}
	return llm.Models(a.llmClient.Providers())
}

// GetSessions 分页查询当前小说的对话历史。
func (a *App) GetSessions(novelID int64, page int, size int) (*storage.PageResult[SessionMeta], error) {
	if a.session == nil {
		return nil, nil
	}
	sessions, total, err := a.session.ListSessions(a.ctx, novelID, page, size)
	if err != nil {
		a.logger.Error("GetSessions 查询失败", "novel_id", novelID, "err", err)
		return nil, err
	}

	metas := make([]SessionMeta, 0, len(sessions))
	for _, s := range sessions {
		metas = append(metas, SessionMeta{
			SessionID: s.SessionID,
			Title:     s.Title,
			Model:     s.Model,
			UpdatedAt: s.UpdatedAt.Format("2006-01-02T15:04:05"),
		})
	}
	return storage.NewPageResult(metas, total, page, size), nil
}

// GetSessionMessages 加载指定 session 的全部前端可见消息。
func (a *App) GetSessionMessages(sessionID string) ([]session.Message, error) {
	if a.session == nil {
		return nil, nil
	}
	msgs, err := a.session.GetMessagesForFrontend(a.ctx, sessionID)
	if err != nil {
		a.logger.Error("GetSessionMessages 查询失败", "session_id", sessionID, "err", err)
		return nil, err
	}
	if msgs == nil {
		return []session.Message{}, nil
	}
	return msgs, nil
}
