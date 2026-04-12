# Pyright 类型错误修复任务清单

**基于**: pyright-type-check-analysis.md
**生成日期**: 2026-04-12
**总需修复错误**: ~72-77 个 (真正的 bug)
**预估总工时**: 2.5-3 小时

---

## 🎯 P0 - 立即修复 (会导致运行时崩溃)

### 任务 1: 修复未定义变量 (17个错误)
**优先级**: 🔴🔴🔴 最高
**预估时间**: 30 分钟
**影响**: 运行时 NameError

#### 1.1 agents/reviewer.py - foreshadowing 未定义
- **文件**: `backend/app/agents/reviewer.py`
- **行号**: 394, 395, 396, 397, 398, 399 (共 7 处)
- **问题**: 变量 `foreshadowing` 未定义
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  # 方案A: 如果是模块名，添加导入
  from app.consistency.models import Foreshadowing
  
  # 方案B: 如果是变量名，检查上下文确认正确的变量名
  # 可能是拼写错误或作用域问题
  ```

#### 1.2 characters/router.py - BadRequestException 未定义
- **文件**: `backend/app/characters/router.py`
- **行号**: 310, 330 (共 2 处)
- **问题**: 异常类未导入
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  # 在文件顶部添加:
  from fastapi import HTTPException
  # 然后替换:
  # raise BadRequestException(...) → raise HTTPException(status_code=400, ...)
  
  # 或者如果项目有自定义异常:
  # from app.core.exceptions import BadRequestException
  ```

#### 1.3 locations/router.py - func 和 loc 未定义
- **文件**: `backend/app/locations/router.py`
- **行号**: 34 (`func`), 113 (`loc`)
- **问题**: 变量名错误或作用域问题
- **状态**: ⬜ 待修复
- **修复方案**: 检查上下文，修正变量名

#### 1.4 mcp/server.py - json 未定义
- **文件**: `backend/app/mcp/server.py`
- **行号**: 724, 745 (共 2 处)
- **问题**: 缺少 json 模块导入
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  # 在文件顶部添加:
  import json
  ```

#### 1.5 text/service.py - select 和 Chapter 未定义
- **文件**: `backend/app/text/service.py`
- **行号**: 148 (select), 148 (Chapter x2) 共 3 处
- **问题**: SQLAlchemy select 和 Model 未导入
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  # 在文件顶部添加:
  from sqlalchemy import select
  from app.chapters.models import Chapter
  ```

#### 1.6 timeline/router.py - select 未定义
- **文件**: `backend/app/timeline/router.py`
- **行号**: 167
- **问题**: SQLAlchemy select 未导入
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  from sqlalchemy import select
  ```

---

### 任务 2: 修复函数调用参数错误 (25个错误)
**优先级**: 🔴🔴🔴 高
**预估时间**: 1 小时
**影响**: 运行时 TypeError 或逻辑错误

#### 2.1 timeline/service.py - 缺少参数
- **文件**: `backend/app/timeline/service.py`
- **行号**: 
  - 452: 缺少 `title` 参数
  - 463: 缺少 `related_entry_ids`, `tags` 参数
- **状态**: ⬜ 待修复
- **修复方案**: 
  - 检查 `_upsert_auto_entry()` 函数签名
  - 补充缺失的必填参数或提供默认值

#### 2.2 characters/router.py 和 service.py
- **文件**: 
  - `backend/app/characters/router.py:239` - 缺少 `data` 参数
  - `backend/app/characters/service.py:265` - 缺少多个参数
- **缺失参数**: `time_horizon`, `source_chapter_id`, `related_entry_ids`, `tags`
- **状态**: ⬜ 待修复
- **修复方案**: 更新函数调用以匹配最新签名

#### 2.3 locations/router.py
- **文件**: `backend/app/locations/router.py`
- **行号**: 
  - 85: 参数名错误 `novel_id` 不存在
  - 88: 参数名错误 `status_code` 不存在
  - 151: 缺少 `data` 参数
- **状态**: ⬜ 待修复
- **修复方案**: 检查函数签名，修正参数名称和补充缺失参数

#### 2.4 memory/router.py
- **文件**: `backend/app/memory/router.py`
- **行号**: 203, 206 (共 2 处)
- **问题**: 缺少 `data` 参数
- **状态**: ⬜ 待修复
- **修复方案**: 补充 data 参数

#### 2.5 novels/router.py
- **文件**: `backend/app/novels/router.py`
- **行号**: 248
- **问题**: 缺少 `data` 参数
- **状态**: ⬜ 待修复
- **修复方案**: 补充 data 参数

#### 2.6 plot_events/router.py
- **文件**: `backend/app/plot_events/router.py`
- **行号**: 225
- **问题**: 缺少 `data` 参数
- **状态**: ⬜ 待修复
- **修复方案**: 补充 data 参数

#### 2.7 mcp/ 工具文件参数问题
- **文件**:
  - `backend/app/mcp/timeline_tools.py:156` - 缺少 `related_entry_ids`
  - `backend/app/mcp/timeline_tools.py:253` - 缺少 `title`, `importance`
  - `backend/app/mcp/base.py:55, 62` - 构造函数/方法参数不匹配
  - `backend/app/mcp/server.py:220, 240, 727, 749` - 参数重复定义
  - `backend/app/mcp/memory_tools.py:266, 273` - select() 参数不匹配
  - `backend/app/mcp/novel_tools.py:1154, 1327` - select() 参数不匹配
  - `backend/app/core/context_builder.py:870` - select() 参数不匹配
- **状态**: ⬜ 待修复
- **修复方案**: 
  - 检查所有相关函数的最新签名
  - 补充缺失参数或更新调用方式
  - 修复参数重复定义问题

---

## 🎯 P1 - 尽快修复 (潜在运行时错误)

### 任务 3: 修复一般类型问题 (20个错误)
**优先级**: 🔴🔴 中高
**预估时间**: 30 分钟
**影响**: 潜在的运行时错误或意外行为

#### 3.1 chat/models.py - Column 条件判断
- **文件**: `backend/app/chat/models.py`
- **行号**: 61, 62, 97 (共 3 处)
- **问题**: 直接对 Column[datetime] 进行布尔判断
- **示例代码**:
  ```python
  if some_datetime_column:  # ❌ 类型错误
      ...
  ```
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  # 方案1: 显式 None 检查
  if some_datetime_column is not None:
      
  # 方案2: 使用 SQLAlchemy 的 is_()/isnot()
  if some_datetime_column.isnot(None):
  ```

---

### 任务 4: 修复属性访问真错误 (10-15个错误)
**优先级**: 🔴🔴 中高
**预估时间**: 30 分钟
**影响**: 运行时 AttributeError

#### 4.1 characters/router.py - Schema 字段不存在
- **文件**: `backend/app/characters/router.py`
- **行号**: 
  - 312, 329, 333: 访问不存在的 `novel_id` 属性
  - 397: 访问不存在的 `mark_old_as_dormant` 属性
  - 50: str 类型没有 `contains` 方法
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  # 对于 novel_id 问题:
  # 检查 CharacterRelationCreate schema 定义
  # 要么添加 novel_id 字段到 schema
  # 要么从其他地方获取 novel_id (如 path parameter)
  
  # 对于 contains 问题:
  # 改为: keyword in name
  # 或使用: Table.name.ilike(f"%{keyword}%")
  ```

#### 4.2 consistency/router.py - 导入符号不存在
- **文件**: `backend/app/consistency/router.py`
- **行号**: 63
- **问题**: `get_db_session` 导入错误
- **状态**: ⬜ 待修复
- **修复方案**: 检查正确的导入路径和函数名

#### 4.3 workflows/langgraph_workflow.py - API 方法不存在
- **文件**: `backend/app/workflows/langgraph_workflow.py`
- **行号**: 581
- **问题**: Pregel 对象没有 `get_state` 方法
- **可能原因**: LangGraph 版本 API 变更
- **状态**: ⬜ 待修复
- **修复方案**:
  ```python
  # 查看 LangGraph 文档确认正确的方法名
  # 可能是: .get_state() → .state() 或其他
  ```

#### 4.4 timeline/service.py - 导入不存在
- **文件**: `backend/app/timeline/service.py`
- **行号**: 307
- **问题**: `RelationStatus` 未正确导入
- **状态**: ⬜ 待修复
- **修复方案**: 找到 RelationStatus 的正确定义位置并导入

---

## ✅ 修复检查清单

### 修复前准备
- [ ] 备份当前代码 (git commit 或 branch)
- [ ] 确认测试环境可用
- [ ] 阅读相关文件的上下文代码

### 修复执行
- [ ] **任务 1.1**: agents/reviewer.py foreshadowing
- [ ] **任务 1.2**: characters/router.py BadRequestException
- [ ] **任务 1.3**: locations/router.py func/loc
- [ ] **任务 1.4**: mcp/server.py json import
- [ ] **任务 1.5**: text/service.py imports
- [ ] **任务 1.6**: timeline/router.py select import
- [ ] **任务 2.1**: timeline/service.py 缺失参数
- [ ] **任务 2.2**: characters/ 参数问题
- [ ] **任务 2.3**: locations/router.py 参数
- [ ] **任务 2.4**: memory/router.py data 参数
- [ ] **任务 2.5**: novels/router.py data 参数
- [ ] **任务 2.6**: plot_events/router.py data 参数
- [ ] **任务 2.7**: mcp/ 工具参数问题
- [ ] **任务 3.1**: chat/models.py 条件判断
- [ ] **任务 4.1**: characters/router.py 属性访问
- [ ] **任务 4.2**: consistency/router.py 导入
- [ ] **任务 4.3**: workflows/langgraph_workflow.py API
- [ ] **任务 4.4**: timeline/service.py 导入

### 修复后验证
- [ ] 运行 `pyright` 确认错误数减少
- [ ] 运行单元测试确保无回归
- [ ] 手动测试修改的功能点
- [ ] 更新本文档标记完成状态

---

## 📊 进度跟踪

| 任务 | 错误数 | 状态 | 完成日期 | 备注 |
|-----|--------|------|---------|------|
| 任务 1: 未定义变量 | 17 | ⬜ 待开始 | - | - |
| 任务 2: 函数参数错误 | 25 | ⬜ 待开始 | - | - |
| 任务 3: 一般类型问题 | 20 | ⬜ 待开始 | - | - |
| 任务 4: 属性访问错误 | 10-15 | ⬜ 待开始 | - | - |
| **总计** | **72-77** | **⬜ 0%** | **-** | **预计 2.5-3h** |

---

## 🔧 快速修复命令参考

### 单文件类型检查
```bash
# 检查特定文件
pyright backend/app/agents/reviewer.py

# 只显示错误 (忽略警告)
pyright --level error backend/app/
```

### Git 工作流建议
```bash
# 创建修复分支
git checkout -b fix/pyright-type-errors

# 修复前提交当前状态
git add -A
git commit -m "chore: snapshot before pyright fixes"

# 修复后提交
git add -A
git commit -m "fix: resolve pyright type errors (P0-P1)"

# 推送并创建 PR
git push origin fix/pyright-type-errors
```

---

## 📝 修复日志模板

```markdown
### [日期] - 修复 [任务编号].[子任务编号]

**文件**: `路径/到/文件.py`
**行号**: xxx
**问题描述**: 
**修复前代码**:
```python
# 修复前的代码
```
**修复后代码**:
```python
# 修复后的代码
```
**验证结果**: ✅ 通过 / ❌ 失败
**备注**: 其他说明
```

---

**文档维护者**: AI Assistant
**最后更新**: 2026-04-12
**版本**: 1.0
