package rag

// MMRRerank 对检索结果进行最大边际相关性重排序。
// lambda 控制相关性（λ）和多样性（1-λ）的权重，通常取 0.7。
// 返回最多 k 个结果。candidates 不会被修改。
func MMRRerank(query string, candidates []SearchResult, k int, lambda float64) []SearchResult {
	if len(candidates) <= k {
		return candidates
	}

	remaining := make([]SearchResult, len(candidates))
	copy(remaining, candidates)
	selected := make([]SearchResult, 0, k)

	for len(selected) < k && len(remaining) > 0 {
		bestIdx := 0
		bestScore := -1.0

		for i, c := range remaining {
			diversity := 0.0
			for _, s := range selected {
				sim := jaccardRune(c.Content, s.Content)
				if sim > diversity {
					diversity = sim
				}
			}
			score := lambda*c.Relevance - (1-lambda)*diversity
			if score > bestScore {
				bestScore = score
				bestIdx = i
			}
		}

		selected = append(selected, remaining[bestIdx])
		remaining = append(remaining[:bestIdx], remaining[bestIdx+1:]...)
	}

	return selected
}

// jaccardRune 计算两段文本的字符级 Jaccard 相似度。
func jaccardRune(a, b string) float64 {
	ra := []rune(a)
	rb := []rune(b)
	if len(ra) == 0 && len(rb) == 0 {
		return 0
	}

	set := make(map[rune]struct{}, len(ra))
	for _, r := range ra {
		set[r] = struct{}{}
	}

	intersection := 0
	seen := make(map[rune]struct{}, len(rb))
	for _, r := range rb {
		if _, ok := seen[r]; ok {
			continue
		}
		seen[r] = struct{}{}
		if _, ok := set[r]; ok {
			intersection++
		}
	}

	union := len(set) + len(seen) - intersection
	if union == 0 {
		return 0
	}
	return float64(intersection) / float64(union)
}
