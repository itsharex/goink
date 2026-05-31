# 踩坑记录

## 1. Wails v2: context.Context 与方法绑定

**症状：** Chat() 调用报 `reflect: Call using zero Value argument`

**根因：** Wails v2 不会自动剥离 `context.Context` 参数。生成的 TypeScript binding 包含了它，前端传 `null` 过去 Go reflection 解析不了。这是 Wails v3 才支持的特性，v2 官方明确表示不会 backport。

**修复：** 去掉 `Chat()` 的 `ctx` 参数，函数内从 `a.ctx` 派生：

```go
func (a *App) Chat(input ChatInput) (*ChatResult, error) {
    ctx, cancel := context.WithCancel(a.ctx)  // a.ctx 来自 OnStartup
    defer cancel()
}
```

---

## 2. GORM: bool 零值跳过 + DB 默认值冲突

**症状：** 所有 tool 消息的 `to_frontend` 自动变成 `true`，工具结果泄漏到前端

**根因：** GORM v2 INSERT 时会跳过零值字段。`false` 是 bool 的零值，GORM 直接跳过，不写入 SQL。DB 列有 `DEFAULT 1`，跳过后 DB 填入 `1`，变成了 `true`。

```go
ToFrontend bool `gorm:"default:1"`  // 错：GORM 跳过 false，DB 填 1
```

**修复：** DB 默认值与 Go 零值对齐：

```go
ToFrontend bool `gorm:"default:0"`  // 对：GORM 跳过 false，DB 填 0
```

---

## 3. Go 切片传值 + append 失效

**症状：** LLM 每轮看到的上下文只有初始消息，工具结果和历史对话全部丢失，死循环调用工具

**根因：** Go slice header（指针+长度+容量）是值类型。`appendMsg` 里的 `append` 修改的是副本，外层 `opts.Messages` 的 slice header 没变。下一轮循环 `ChatStream(ctx, opts.Messages)` 拿到的始终是初始消息。

```go
// 错：传值，append 改了副本
func (a *Agent) appendMsg(..., opts RunOptions, ...) {
    opts.Messages = append(opts.Messages, msg)
}

// 对：传指针
func (a *Agent) appendMsg(..., opts *RunOptions, ...) {
    opts.Messages = append(opts.Messages, msg)
}
```

---

## 4. json.RawMessage 裸 JSON 破坏 API 协议

**症状：** DeepSeek 返回 400 `"invalid type: map, expected a string"`

**根因：** OpenAI/DeepSeek 协议规定 `tool_calls[n].function.arguments` 必须是 JSON 字符串（`"{}"`），不是 JSON 对象（`{}`）。`json.RawMessage` 实现了 `json.Marshaler`，序列化时直接输出裸字节不带引号。存到 `extra_metadata` 里变成 `arguments: {}`，回传时 DeepSeek 校验拦截。

```go
// 错：裸 JSON 对象，协议要的是字符串
"arguments": json.RawMessage(o.rawArgs),   // → arguments: {}

// 对：Go 字符串序列化后自动加引号
"arguments": string(o.rawArgs),            // → arguments: "{}"
```

---

## 5. validator 标签顺序错误

**症状：** 所有嵌入 PageArgs 的工具校验失败，LLM 空转重试

**根因：** go-playground/validator 从左到右执行。`validate:"min=1,omitempty"` 先跑 `min=1`，`Page=0` 直接失败，轮不到 `omitempty` 跳过。

```go
Page int `validate:"min=1,omitempty"`  // 错
Page int `validate:"omitempty,min=1"`  // 对
```

共 4 处（PageArgs ×2 + Importance ×2）。
