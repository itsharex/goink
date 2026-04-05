import { useState, useEffect } from 'react'
import { Card, Tabs, Table, Button, Tag, Collapse, Input, message, Spin, Descriptions, List, Divider, Row, Col, Statistic, Alert, Badge, Tooltip, Space } from 'antd'
import {
  PlayCircleOutlined, SearchOutlined, TeamOutlined,
  CheckCircleOutlined, BookOutlined, BarChartOutlined,
  ExperimentOutlined, AlertOutlined,
  RobotOutlined,
  InfoCircleOutlined, LoadingOutlined,
} from '@ant-design/icons'
import { useParams, useNavigate } from 'react-router-dom'
import { mcpApi } from '@/services/mcpService'
import { getErrorMessage } from '@/types/error'
import type { MCPToolInfo } from '@/types/mcp'
import {
  getToolDisplayName,
  getToolDisplayDescription,
  getToolIcon,
  getToolColor,
  getToolUserAction,
  toolDisplayMap,
} from '@/utils/toolDisplayMap'

const { Panel } = Collapse
const { Search } = Input

interface ExecuteResult {
  type: string
  data: Record<string, unknown>
}

function MCPTools() {
  const [loading, setLoading] = useState(false)
  const [tools, setTools] = useState<MCPToolInfo[]>([])
  const [categories, setCategories] = useState<Record<string, MCPToolInfo[]>>({})
  const [selectedTool, setSelectedTool] = useState<MCPToolInfo | null>(null)
  const [executeResult, setExecuteResult] = useState<ExecuteResult | null>(null)
  const { novelId } = useParams<{ novelId: string }>()
  const navigate = useNavigate()

  useEffect(() => {
    loadTools()
    loadCategories()
  }, [])

  const loadTools = async () => {
    setLoading(true)
    try {
      const response = await mcpApi.listTools()
      if (response.success) {
        setTools(response.data.tools)
      }
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await mcpApi.listCategories()
      if (response.success) {
        setCategories(response.data)
      }
    } catch (error) {
      console.error('加载分类失败:', getErrorMessage(error))
    }
  }

  const getCategoryConfig = (category: string) => {
    const configs: Record<string, { icon: React.ReactNode; label: string; color: string; description: string }> = {
      novel_management: {
        icon: <BookOutlined />,
        label: '资料查阅',
        color: '#1890ff',
        description: '读取小说、章节、角色、进度等基础信息',
      },
      memory_retrieval: {
        icon: <SearchOutlined />,
        label: '记忆检索',
        color: '#eb2f96',
        description: '搜索已有内容、回顾角色经历、获取写作上下文',
      },
      consistency_check: {
        icon: <CheckCircleOutlined />,
        label: '质量检查',
        color: '#ff4d4f',
        description: '检查角色一致性、情节逻辑、伏笔状态等',
      },
      writing_assistant: {
        icon: <TeamOutlined />,
        label: '创作执行',
        color: '#fa8c16',
        description: 'AI生成、编辑修改、时间线管理、任务调度',
      },
    }
    return configs[category] || { icon: <PlayCircleOutlined />, label: category, color: '#999', description: '' }
  }

  const onSearchMemory = async (query: string) => {
    if (!novelId || !query) return
    setLoading(true)
    try {
      const response = await mcpApi.searchPlotMemory(parseInt(novelId), query)
      if (response.success) {
        setExecuteResult({ type: 'memory_search', data: response.data as unknown as Record<string, unknown> })
      }
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const onGetNovelSummary = async () => {
    if (!novelId) return
    setLoading(true)
    try {
      const response = await mcpApi.getNovelSummary(parseInt(novelId))
      if (response.success) {
        setExecuteResult({ type: 'novel_summary', data: response.data as unknown as Record<string, unknown> })
      }
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const onGetNovelProgress = async () => {
    if (!novelId) return
    setLoading(true)
    try {
      const response = await mcpApi.getNovelProgress(parseInt(novelId))
      if (response.success) {
        setExecuteResult({ type: 'novel_progress', data: response.data as unknown as Record<string, unknown> })
      }
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const onCheckConsistency = async () => {
    if (!novelId) return
    setLoading(true)
    try {
      const response = await mcpApi.runFullConsistencyCheck(parseInt(novelId))
      if (response.success) {
        setExecuteResult({ type: 'consistency_check', data: response.data as unknown as Record<string, unknown> })
      }
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const onGetForeshadowingStatus = async () => {
    if (!novelId) return
    setLoading(true)
    try {
      const response = await mcpApi.getForeshadowingStatus(parseInt(novelId))
      if (response.success) {
        setExecuteResult({ type: 'foreshadowing_status', data: response.data as unknown as Record<string, unknown> })
      }
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const renderResult = () => {
    if (!executeResult) return null

    const { type, data } = executeResult

    switch (type) {
      case 'memory_search': {
        const searchData = data as { query: string; total: number; results: Array<{ type: string; relevance_score: number; content: string }> }
        return (
          <Card title="搜索结果" size="small">
            <p>查询: {searchData.query}</p>
            <p>结果数: {searchData.total}</p>
            <List
              dataSource={searchData.results}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={`相关度: ${(item.relevance_score * 100).toFixed(1)}%`}
                    description={item.content.substring(0, 200) + '...'}
                  />
                </List.Item>
              )}
            />
          </Card>
        )
      }
      case 'novel_summary': {
        const summaryData = data as { title: string; genre: string; status: string; chapter_count: number; word_count: number; character_count: number; description: string }
        return (
          <Card title="小说概况" size="small">
            <Descriptions column={2}>
              <Descriptions.Item label="标题">{summaryData.title}</Descriptions.Item>
              <Descriptions.Item label="类型">{summaryData.genre}</Descriptions.Item>
              <Descriptions.Item label="状态">{summaryData.status}</Descriptions.Item>
              <Descriptions.Item label="章节数">{summaryData.chapter_count}</Descriptions.Item>
              <Descriptions.Item label="字数">{summaryData.word_count}</Descriptions.Item>
              <Descriptions.Item label="角色数">{summaryData.character_count}</Descriptions.Item>
            </Descriptions>
            <Divider />
            <p>{summaryData.description}</p>
          </Card>
        )
      }
      case 'novel_progress': {
        const progressData = data as { total_chapters: number; completed_chapters: number; total_words: number; completion_percentage: number }
        return (
          <Card title="写作进度" size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic title="总章节" value={progressData.total_chapters} />
              </Col>
              <Col span={6}>
                <Statistic title="已完成" value={progressData.completed_chapters} />
              </Col>
              <Col span={6}>
                <Statistic title="总字数" value={progressData.total_words} />
              </Col>
              <Col span={6}>
                <Statistic title="完成率" value={progressData.completion_percentage} suffix="%" />
              </Col>
            </Row>
          </Card>
        )
      }
      case 'consistency_check': {
        const checkData = data as { passed: boolean; issues: Array<{ type: string; severity: string; description: string; suggestion: string }> }
        return (
          <Card title="体检报告" size="small">
            <Alert
              title={checkData.passed ? '全部通过' : '发现问题'}
              type={checkData.passed ? 'success' : 'warning'}
              showIcon
              style={{ marginBottom: 16 }}
            />
            {checkData.issues.length > 0 && (
              <List
                dataSource={checkData.issues}
                renderItem={(issue) => (
                  <List.Item>
                    <List.Item.Meta
                      title={<Tag color={issue.severity === 'error' ? 'error' : 'warning'}>{issue.type}</Tag>}
                      description={issue.description}
                    />
                    <p>建议: {issue.suggestion}</p>
                  </List.Item>
                )}
              />
            )}
          </Card>
        )
      }
      case 'foreshadowing_status': {
        const foreshadowData = data as { total: number; resolved: number; pending: number; abandoned: number }
        return (
          <Card title="伏笔追踪" size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic title="总数" value={foreshadowData.total} />
              </Col>
              <Col span={6}>
                <Statistic title="已回收" value={foreshadowData.resolved} />
              </Col>
              <Col span={6}>
                <Statistic title="待处理" value={foreshadowData.pending} />
              </Col>
              <Col span={6}>
                <Statistic title="已放弃" value={foreshadowData.abandoned} />
              </Col>
            </Row>
          </Card>
        )
      }
      default:
        return <Card title="结果"><pre>{JSON.stringify(data, null, 2)}</pre></Card>
    }
  }

  const quickTools = [
    { key: 'summary', icon: <BookOutlined style={{ fontSize: 24, color: '#1890ff' }} />, title: '查看小说概况', desc: '获取基本信息、章节数、字数等', onClick: onGetNovelSummary },
    { key: 'progress', icon: <BarChartOutlined style={{ fontSize: 24, color: '#52c41a' }} />, title: '查看写作进度', desc: '完成率、总字数、最新章节统计', onClick: onGetNovelProgress },
    { key: 'check', icon: <ExperimentOutlined style={{ fontSize: 24, color: '#ff4d4f' }} />, title: '全面体检', desc: '角色+情节+时间线+伏笔综合检查', onClick: onCheckConsistency },
    { key: 'foreshadowing', icon: <AlertOutlined style={{ fontSize: 24, color: '#faad14' }} />, title: '伏笔追踪', desc: '已回收/待处理/已放弃的统计', onClick: onGetForeshadowingStatus },
  ]

  if (loading && tools.length === 0) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
        </div>
      </Card>
    )
  }

  return (
    <div>
      <Card
        title={
          <Space>
            <RobotOutlined />
            <span>AI工具箱</span>
            <Badge count={tools.length} style={{ backgroundColor: '#1890ff' }} />
          </Space>
        }
        extra={
          <Tooltip title="这些是AI在创作过程中可以调用的工具，点击可了解每个工具的具体用途">
            <InfoCircleOutlined style={{ color: '#999' }} />
          </Tooltip>
        }
      >
        <Tabs defaultActiveKey="quick" items={[
          {
            key: 'quick',
            label: '快捷操作',
            children: (
              <>
                <Row gutter={[16, 16]}>
                  {quickTools.map((t) => (
                    <Col span={6} key={t.key}>
                      <Card hoverable onClick={t.onClick}>
                        <Card.Meta avatar={t.icon} title={t.title} description={t.desc} />
                      </Card>
                    </Col>
                  ))}
                  <Col span={12}>
                    <Card>
                      <Card.Meta
                        avatar={<SearchOutlined style={{ fontSize: 24, color: '#eb2f96' }} />}
                        title="搜索情节内容"
                        description="用自然语言搜索小说中已有的相关片段"
                      />
                      <Search
                        placeholder="输入关键词，如「主角在码头遇到了谁」…"
                        enterButton="搜索"
                        size="large"
                        onSearch={onSearchMemory}
                        style={{ marginTop: 16 }}
                      />
                    </Card>
                  </Col>
                </Row>

                {executeResult && (
                  <>
                    <Divider>执行结果</Divider>
                    {renderResult()}
                  </>
                )}
              </>
            ),
          },
          {
            key: 'list',
            label: `全部工具 (${tools.length})`,
            children: (
              <Table
                dataSource={tools}
                rowKey="name"
                pagination={false}
                columns={[
                  {
                    title: '工具',
                    dataIndex: 'name',
                    key: 'name',
                    width: 200,
                    render: (name: string) => (
                      <Space>
                        <span style={{ color: getToolColor(name), fontSize: 16 }}>{getToolIcon(name)}</span>
                        <span style={{ fontWeight: 500 }}>{getToolDisplayName(name)}</span>
                      </Space>
                    ),
                  },
                  {
                    title: '功能说明',
                    dataIndex: 'description',
                    key: 'description',
                    ellipsis: true,
                    render: (_desc: string, record: MCPToolInfo) => (
                      <Tooltip title={getToolDisplayDescription(record.name)}>
                        <span>{getToolDisplayDescription(record.name)}</span>
                      </Tooltip>
                    ),
                  },
                  {
                    title: '分类',
                    dataIndex: 'category',
                    key: 'category',
                    width: 110,
                    render: (category: string) => {
                        const cfg = getCategoryConfig(category)
                        return <Tag color={cfg.color}>{cfg.label}</Tag>
                      },
                  },
                  {
                    title: 'AI调用时显示',
                    key: 'action',
                    width: 220,
                    render: (_: unknown, record: MCPToolInfo) => (
                      <Tag color={getToolColor(record.name)} style={{ maxWidth: 200 }}>
                        {getToolUserAction(record.name)}
                      </Tag>
                    ),
                  },
                  {
                    title: '',
                    key: 'detail',
                    width: 80,
                    render: (_: unknown, record: MCPToolInfo) => (
                      <Button type="link" size="small" onClick={() => setSelectedTool(record)}>
                        详情
                      </Button>
                    ),
                  },
                ]}
              />
            ),
          },
          {
            key: 'categories',
            label: '按类别浏览',
            children: (
              <Collapse accordion>
                {Object.entries(categories).map(([category, categoryTools]) => {
                  const cfg = getCategoryConfig(category)
                  return (
                    <Panel
                      header={
                        <Space>
                          <span style={{ color: cfg.color }}>{cfg.icon}</span>
                          <strong>{cfg.label}</strong>
                          <Tag color={cfg.color}>{categoryTools.length}个工具</Tag>
                          <span style={{ color: '#999', fontSize: 13 }}>{cfg.description}</span>
                        </Space>
                      }
                      key={category}
                    >
                      <List
                        dataSource={categoryTools}
                        renderItem={(tool) => {
                          const info = toolDisplayMap[tool.name]
                          return (
                            <List.Item
                              actions={[
                                <Button key="detail" type="link" size="small" onClick={() => setSelectedTool(tool)}>详情</Button>,
                              ]}
                            >
                              <List.Item.Meta
                                avatar={
                                  <div style={{
                                    width: 40, height: 40, borderRadius: 8,
                                    background: `${info?.color || '#eee'}15`,
                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    color: info?.color || '#999', fontSize: 18,
                                  }}>
                                    {getToolIcon(tool.name)}
                                  </div>
                                }
                                title={
                                  <Space>
                                    <span style={{ fontWeight: 500 }}>{getToolDisplayName(tool.name)}</span>
                                    <Tag color={info?.color} style={{ fontSize: 11, marginLeft: 4 }}>
                                      {getToolUserAction(tool.name)}
                                    </Tag>
                                  </Space>
                                }
                                description={getToolDisplayDescription(tool.name)}
                              />
                            </List.Item>
                          )
                        }}
                      />
                    </Panel>
                  )
                })}
              </Collapse>
            ),
          },
        ]} />

        {selectedTool && (
          <Card
            title={
              <Space>
                {getToolIcon(selectedTool.name)}
                <span>{getToolDisplayName(selectedTool.name)}</span>
                <Tag color={getToolColor(selectedTool.name)}>{getCategoryConfig(selectedTool.category).label}</Tag>
              </Space>
            }
            style={{ marginTop: 16 }}
          >
            <Alert
              type="info"
              showIcon
              icon={<LoadingOutlined />}
              message="AI调用此工具时用户看到的提示"
              description={
                <Tag color={getToolColor(selectedTool.name)} style={{ fontSize: 14, padding: '4px 12px' }}>
                  {getToolUserAction(selectedTool.name)}
                </Tag>
              }
              style={{ marginBottom: 16 }}
            />

            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="友好名称">
                <span style={{ fontWeight: 500, fontSize: 15 }}>{getToolDisplayName(selectedTool.name)}</span>
              </Descriptions.Item>
              <Descriptions.Item label="功能说明">
                {getToolDisplayDescription(selectedTool.name)}
              </Descriptions.Item>
              <Descriptions.Item label="所属分类">
                <Tag color={getCategoryConfig(selectedTool.category).color}>
                  {getCategoryConfig(selectedTool.category).label}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="原始名称（系统内部）">
                <code style={{ background: '#f5f5f5', padding: '2px 8px', borderRadius: 4, color: '#999' }}>
                  {selectedTool.name}
                </code>
              </Descriptions.Item>
              <Descriptions.Item label="原始描述">
                <span style={{ color: '#666', fontSize: 13 }}>{selectedTool.description}</span>
              </Descriptions.Item>
              <Descriptions.Item label="返回值">
                {selectedTool.returns || '-'}
              </Descriptions.Item>
            </Descriptions>

            <Divider>参数定义</Divider>
            <Table
              dataSource={selectedTool.parameters}
              rowKey="name"
              pagination={false}
              size="small"
              columns={[
                { title: '参数名', dataIndex: 'name' },
                { title: '类型', dataIndex: 'type', render: (t: string) => <Tag>{t}</Tag> },
                { title: '必填', dataIndex: 'required', render: (v: boolean) => v ? <Tag color="red">必填</Tag> : <Tag>可选</Tag> },
                { title: '说明', dataIndex: 'description', ellipsis: true },
                { title: '默认值', dataIndex: 'default', render: (v: any) => v !== undefined ? String(v) : '-' },
              ]}
            />

            <Button style={{ marginTop: 16 }} onClick={() => setSelectedTool(null)}>
              关闭
            </Button>
          </Card>
        )}

        <div style={{ marginTop: 16 }}>
          <Button onClick={() => navigate(`/novels/${novelId}`)}>返回小说详情</Button>
        </div>
      </Card>
    </div>
  )
}

export default MCPTools
