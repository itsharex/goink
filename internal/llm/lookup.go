package llm

// ProviderModel 在指定 provider 中按 model ID 查找模型元信息。
func (c *Client) ProviderModel(providerName, modelID string) (*ModelInfo, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	p, ok := c.providers[providerName]
	if !ok {
		return nil, false
	}
	for i := range p.Models {
		if p.Models[i].ID == modelID {
			return &p.Models[i], true
		}
	}
	return nil, false
}
