<p align="center">
  <img src="assets/logo-dark.svg#gh-dark-mode-only" alt="Goink" />
  <img src="assets/logo-light.svg#gh-light-mode-only" alt="Goink" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Go-1.25-00ADD8?style=for-the-badge&logo=go&logoColor=white" alt="Go 1.25" />
  <img src="https://img.shields.io/badge/Wails-v2.12-DF0000?style=for-the-badge&logo=wails&logoColor=white" alt="Wails v2" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=white" alt="React 19" />
  <img src="https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <br />
  <img src="https://img.shields.io/badge/TypeScript-6.0-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript 6" />
  <img src="https://img.shields.io/badge/Tailwind-4.3-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white" alt="Tailwind 4" />
  <img src="https://img.shields.io/badge/ONNX_Runtime-1.26-005BED?style=for-the-badge&logo=onnx&logoColor=white" alt="ONNX Runtime" />
  <img src="https://img.shields.io/badge/license-MIT-716B94?style=for-the-badge&logo=opensourceinitiative&logoColor=white" alt="MIT" />
</p>

---

<p align="center"><strong>Goink 是一个带记忆的桌面 AI 写作工具。角色、伏笔、时间线、世界观——这些创作信息被系统结构化并持续追踪，让每一次 AI 协作都建立在完整的上下文之上。</strong></p>

## 它是怎么工作的

打开 Goink，你看到的是一个对话界面。你和 AI 对话，AI 调用工具来完成具体操作。它不是只会回文字——它可以直接读取章节、写入正文、管理角色档案、记录伏笔、推进弧线、搜索全书内容。

核心流程是：**你提出意图，AI 执行操作，系统自动维护状态**。比如你说"写第 15 章"，AI 会先写成大纲等你确认，通过后写出正文，然后自动检查角色变化、更新伏笔状态、推进弧线节点、刷新读者认知——这一整套维护动作不需要你额外提醒。

AI 可用的工具有 30 多个，按职责分为四类：

| 类别 | 能做什么 |
|---|---|
| **创作执行** | 读章节、写大纲和正文（全文替换 / 查找替换 / 行范围替换）、查阅故事状态文档 |
| **数据管理** | 创建和更新角色档案与关系、记录伏笔和章节计划、推进弧线节点、管理世界观地点 |
| **状态查询** | 按条件检索角色/时间线/弧线/读者认知，查看偏好和历史 |
| **高级能力** | 语义搜索全书任意内容、启动审稿子 Agent 独立检查一致性、启动记忆子 Agent 综合分析 |

写完一章后，系统会自动触发审稿 Agent 从头检查：角色性格前后一致吗？该回收的伏笔处理了吗？弧线节点需要校准吗？审稿结论直接反馈给你。

## 一切创作决策都被追踪

### 创作偏好：说一次，永远生效

写到第三十七章，你还记得当初跟 AI 说过"对话保持冷峻风格"吗？系统记得。全局偏好对所有小说生效，单书偏好只对当前作品起效。说一次就够。

### 角色：不仅仅是名字和简介

每个角色有详细档案（性格、能力、背景），由 AI 根据你的创作持续更新。**角色关系是有向图**——张三对李四是"师徒但暗中互相提防"，和李四对张三的"敬重但有所隐瞒"是两条独立的记录。关系发生变化时，旧记录不被删除，而是保留为历史。你可以随时回顾一段关系是怎么演变的。

### 时间线：伏笔不会石沉大海

章节计划分三档管理创作节奏：下一章写什么、近期方向、远期规划。

伏笔系统记录每条伏笔的目标回收章节和重要程度。快到回收点系统会提醒，过了回收点还没回收会标记异常。AI 写新章节时会自动查看附近的伏笔状态。

### 弧线：跨章节的叙事线索

一条"复仇弧"可能从第 5 章延续到第 50 章。弧线由一串节点链组成（发现真相 → 接近仇人 → 对决 → 结局），每个节点关联目标章节。写完一章，AI 推进节点进度、校准后续目标。一个故事通常有 3–5 条并行弧线。

### 世界观：地点是图，不是列表

地点系统追踪两件事：**层级包含**（王国 → 王宫 → 大殿）和**空间连通**（A 和 B 之间由山路连通）。AI 可以查询单个地点的详情、子地点和连通关系，也可以查看完整的世界地图。

### 读者认知：你知道的，读者不一定知道

追踪三件事：读者已经知道了什么、读者在等什么答案、读者误解了什么。每条记录标注在哪章种下的、在哪章回收的。对于需要悬念和反转的作品，这个功能让你精确控制信息的释放节奏。

## 三重保障，状态维护不会遗漏

AI 工具常见的问题不是"做不到"，而是"做几次就不做了"。Goink 用三层机制确保维护不被跳过：

**第一层：系统提示词。** Agent 的核心指令写死了维护流程——"创作完成后立即进行状态维护。不是可选步骤。"

**第二层：动态注入。** AI 写完长篇正文后，系统自动注入一条消息，列明具体要检查的项目——角色变化、伏笔状态、弧线节点、读者认知。不是笼统地说"去维护"，而是告诉 AI 具体该查什么。

**第三层：审稿 Agent。** 独立子 Agent 从头审读章节内容与系统状态的一致性，像一位严格的编辑，找出 AI 自己没注意到的问题。

## 语义搜索：几十万字里找一句话

写到第五十章，想找"主角第一次见到那个吊坠是在哪一章来着？"——不用逐章翻。告诉 AI 一句话，它就能在整本书里找到相关段落。

这不是关键词匹配，是按意思搜索。你问"关于吊坠的线索"，它能找到那些没写"吊坠"两个字但确实在暗示吊坠存在的段落。这个能力对 AI 同样有用——写新章节时可以主动搜索前文，确保持续一致。

整套搜索在本机运行，写完一个章节自动在后台索引，不需要网络，不需要额外配置。

## 你的每一次确认

AI 不会直接修改正文。每次要改动章节内容，系统先生成 diff 展示给你看，等你点头再写入。你可以当场批准、拒绝，或者给反馈让 AI 修正。也可以切换到自动模式，AI 连续多轮自由写作，编辑直接生效。

所有修改都有版本历史，任何时候都可以回退。

## 安装

从 [Releases](https://github.com/sigpanic/goink/releases) 下载对应平台的安装包：

- **Windows** — 运行安装程序
- **macOS** — 打开 DMG，拖入 Applications
- **Linux** — 运行 AppImage

需要自行准备 LLM API Key（内置 DeepSeek 模板，兼容 OpenAI 格式 API）。安装包已包含写作所需的一切——不需要安装 Python、Node.js、数据库或 GPU。市面上大量 Python AI 写作工具为了一个语义搜索需要安装数 GB 的依赖，Goink 全部打包在一个安装包里，三平台均小于 60MB。

Windows 下载后 SmartScreen 可能弹出"Windows 保护了你的电脑"提示，这是因为安装包没有数字签名（代码签名证书年费约 $300–500）。点击"更多信息"→"仍要运行"即可继续安装。每次 Release 的 sha256 校验和附在发布页面上，可以验证文件完整性。

### 从源码构建

```bash
# 系统依赖（Ubuntu/Debian）
sudo apt install libsqlite3-dev libgtk-3-dev libwebkit2gtk-4.1-dev gcc

# Go 1.25+
git clone https://github.com/sigpanic/goink
cd goink

make deps      # 下载运行时依赖
make build     # 生产构建
make dev       # 开发模式（热重载）
```

## 技术栈

| 层 | 选型 |
|---|---|
| 桌面框架 | Wails v2（Go + WebView） |
| 编辑器 | Monaco Editor |
| 数据库 | SQLite（mattn/go-sqlite3） |
| 向量搜索 | sqlite-vec |
| 嵌入模型 | bge-small-zh-v1.5（ONNX int8 量化） |
| LLM 客户端 | 原生 net/http + SSE（OpenAI 兼容格式） |
| 前端 | React 19 + TypeScript + Tailwind CSS 4 |
| UI 组件 | shadcn/ui（Radix UI） |

## License

MIT
