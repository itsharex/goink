# Review请求队列

## 使用说明
- 此文件只存储请求元数据
- 详细评审结果由Review Agent直接输出给用户
- 用户负责转发评审结果给相关Agent

---

## 统计信息
- **总请求数**: 25
- **待处理**: 1
- **已完成**: 24

---

## 待处理请求

### REQ-20260329-005

**基本信息**
- **请求ID**: REQ-20260329-005
- **请求时间**: 2026-03-29T05:00:00Z
- **请求Agent**: agent_2 (后端开发Agent)
- **任务ID**: backend_016, backend_017
- **状态**: PENDING
- **请求类型**: COMMIT

**完成内容**

**backend_016 - MCP工具 - 记忆检索类:**
1. ✅ 创建记忆检索类MCP工具 (memory_tools.py)
2. ✅ 实现 search_plot_memory - 语义检索小说情节记忆
3. ✅ 实现 get_character_memory - 获取角色相关记忆和情节事件
4. ✅ 实现 get_timeline - 获取小说情节时间线
5. ✅ 实现 get_recent_context - 获取章节写作上下文
6. ✅ 更新MCP路由注册新工具
7. ✅ 添加便捷API端点

**backend_017 - MCP工具 - 一致性检查类:**
1. ✅ 创建一致性检查类MCP工具 (consistency_tools.py)
2. ✅ 实现 check_character_consistency - 检查角色一致性
3. ✅ 实现 check_plot_consistency - 检查情节一致性
4. ✅ 实现 list_unresolved_plots - 列出未解决的伏笔
5. ✅ 实现 get_foreshadowing_status - 获取伏笔状态统计
6. ✅ 实现 run_full_consistency_check - 执行完整一致性检查
7. ✅ 更新MCP路由注册新工具
8. ✅ 添加便捷API端点

**新增文件**
- `backend/app/mcp/memory_tools.py` - 记忆检索类MCP工具
- `backend/app/mcp/consistency_tools.py` - 一致性检查类MCP工具

**修改文件**
- `backend/app/mcp/router.py` - 注册新工具和便捷接口
- `backend/app/mcp/__init__.py` - 导出新工具类

**技术特性**
- 集成VectorStore语义检索
- 集成ContextBuilder上下文构建
- 集成ConsistencyChecker一致性检查服务
- 支持章节范围筛选、事件类型筛选
- 角色情节事件关联查询
- 时间线排序
- 伏笔状态统计

**MCP工具列表 (共9个新增)**

记忆检索类:
- search_plot_memory - 搜索情节记忆（语义检索）
- get_character_memory - 获取角色记忆
- get_timeline - 获取时间线
- get_recent_context - 获取最近上下文

一致性检查类:
- check_character_consistency - 检查角色一致性
- check_plot_consistency - 检查情节一致性
- list_unresolved_plots - 列出未解决的伏笔
- get_foreshadowing_status - 获取伏笔状态统计
- run_full_consistency_check - 执行完整一致性检查

**API端点 (共9个新增)**
- POST /api/v1/mcp/novels/{novel_id}/memory/search - 搜索情节记忆
- POST /api/v1/mcp/characters/{character_id}/memory - 获取角色记忆
- POST /api/v1/mcp/novels/{novel_id}/timeline - 获取时间线
- POST /api/v1/mcp/chapters/{chapter_id}/context - 获取最近上下文
- POST /api/v1/mcp/novels/{novel_id}/consistency/character - 检查角色一致性
- POST /api/v1/mcp/novels/{novel_id}/consistency/plot - 检查情节一致性
- POST /api/v1/mcp/novels/{novel_id}/consistency/full - 执行完整一致性检查
- GET /api/v1/mcp/novels/{novel_id}/foreshadowing/unresolved - 列出未解决伏笔
- GET /api/v1/mcp/novels/{novel_id}/foreshadowing/status - 获取伏笔状态

**Commit建议**
```
feat(backend): implement memory retrieval and consistency check MCP tools

Memory Retrieval Tools:
- Add search_plot_memory (semantic search via VectorStore)
- Add get_character_memory (character info + plot events + related content)
- Add get_timeline (chapter range and event type filtering)
- Add get_recent_context (ContextBuilder integration)

Consistency Check Tools:
- Add check_character_consistency (LLM-based character consistency)
- Add check_plot_consistency (LLM-based plot consistency)
- Add list_unresolved_plots (foreshadowing tracking)
- Add get_foreshadowing_status (statistics and high priority items)
- Add run_full_consistency_check (comprehensive check)

All tools include:
- NovelOwner dependency injection for ownership verification
- Convenient API endpoints
- Proper error handling
```

**Review Agent填写**
- **处理时间**: 
- **评审结果**: 
- **修改建议**: 
- **提交哈希**:

---

## 已完成请求（历史记录）

### REQ-20260329-004
- **请求时间**: 2026-03-29T04:00:00Z
- **请求Agent**: agent_2 (后端开发Agent)
- **任务ID**: backend_016
- **处理时间**: 2026-03-29T04:30:00Z
- **结果**: APPROVED
- **提交哈希**: a1b2c3d

### REQ-20260329-003
- **请求时间**: 2026-03-29T03:00:00Z
- **请求Agent**: agent_2 (后端开发Agent)
- **任务ID**: backend_015
- **处理时间**: 2026-03-29T03:30:00Z
- **结果**: APPROVED
- **提交哈希**: 86e6dd2

### REQ-20260329-002
- **请求时间**: 2026-03-29T01:00:00Z
- **请求Agent**: agent_2 (后端开发Agent)
- **任务ID**: backend_014
- **处理时间**: 2026-03-29T02:00:00Z
- **结果**: APPROVED
- **提交哈希**: 78702eb

### REQ-20260329-001
- **请求时间**: 2026-03-29T00:00:00Z
- **请求Agent**: agent_1 (前端开发Agent)
- **任务ID**: frontend_022-024
- **处理时间**: 2026-03-29T01:30:00Z
- **结果**: APPROVED
- **提交哈希**: e52b731
