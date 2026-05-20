package storage

// PageResult 泛型分页响应，匹配 Python PageResponse 的语义。
type PageResult[T any] struct {
	Items      []T   `json:"items"`
	Total      int64 `json:"total"`
	Page       int   `json:"page"`
	Size       int   `json:"size"`
	TotalPages int   `json:"total_pages"`
}

// NewPageResult 根据 total/size 自动计算 TotalPages。
func NewPageResult[T any](items []T, total int64, page, size int) *PageResult[T] {
	tp := 0
	if size > 0 {
		tp = int(total) / size
		if int(total)%size != 0 {
			tp++
		}
	}
	return &PageResult[T]{
		Items:      items,
		Total:      total,
		Page:       page,
		Size:       size,
		TotalPages: tp,
	}
}
