import { useEffect, useState } from 'react'
import { Card, Descriptions, Tag, Button, Space, message, Collapse } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { chapterApi } from '@/services/chapterService'
import { getErrorMessage } from '@/types/error'
import type { ChapterDetail } from '@/types/chapter'
import { Markdown } from '@/components/Markdown'
import dayjs from 'dayjs'

interface OutlineScene {
  name: string
  description: string
  purpose: string
}

interface OutlineChar {
  name: string
  role_in_chapter: string
}

interface OutlineOp {
  action: string
  content: string
}

function formatOutline(outline: Record<string, unknown> | null | undefined): string {
  if (!outline || typeof outline !== 'object') return ''
  const o = outline as Record<string, unknown>
  const chNum = o.chapter_number ?? o.chapterNumber ?? '?'
  const title = String(o.title ?? '未命名')
  const tone = String(o.tone ?? '未指定')
  const words = o.estimated_words ?? o.estimatedWords ?? '?'
  const hook = String(o.chapter_hook ?? o.chapterHook ?? '无')

  let md = `## 第${chNum}章：${title}\n\n`
  md += `**语调**：${tone}　|　**预估字数**：${words}\n\n`
  md += '### 场景\n'

  const scenes = (o.scenes as OutlineScene[]) ?? []
  scenes.forEach((s, i) => {
    md += `${i + 1}. **${s.name}**\n`
    md += `   ${s.description}\n`
    md += `   > 目的：${s.purpose}\n\n`
  })

  const events = (o.key_events as string[]) ?? []
  if (events.length) {
    md += '### 关键事件\n'
    events.forEach(e => { md += `- ${e}\n` })
    md += '\n'
  }

  const chars = (o.focus_characters as (OutlineChar | string)[]) ?? []
  if (chars.length) {
    md += '### 重点角色\n'
    chars.forEach(c => {
      if (typeof c === 'object' && c !== null) {
        md += `- **${c.name ?? '?'}**：${c.role_in_chapter ?? ''}\n`
      } else {
        md += `- ${c}\n`
      }
    })
    md += '\n'
  }

  const ops = (o.foreshadowing_ops as OutlineOp[]) ?? []
  if (ops.length) {
    md += '### 伏笔操作\n'
    const labels: Record<string, string> = { plant: '埋下', advance: '推进', resolve: '回收' }
    ops.forEach(op => {
      const label = labels[op.action] ?? op.action
      md += `- [${label}] ${op.content}\n`
    })
    md += '\n'
  }

  md += `**章末钩子**：${hook}\n`
  return md
}

interface StatusConfig {
  color: string
  text: string
}

function ChapterDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [chapter, setChapter] = useState<ChapterDetail | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (id) {
      loadChapter(parseInt(id))
    }
  }, [id])

  const loadChapter = async (chapterId: number) => {
    setLoading(true)
    try {
      const response = await chapterApi.getChapter(chapterId)
      if (response.success) {
        setChapter(response.data)
      }
    } catch (error) {
      message.error(getErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, StatusConfig> = {
      draft: { color: 'default', text: '草稿' },
      completed: { color: 'success', text: '已完成' },
    }
    const config = statusMap[status]
    return <Tag color={config.color}>{config.text}</Tag>
  }

  if (!chapter) return null

  return (
    <Card
      title={`第${chapter.chapter_number}章 ${chapter.title}`}
      extra={
        <Space>
          <Button onClick={() => navigate(`/novels/${chapter.novel_id}/chapters`)}>
            返回列表
          </Button>
          <Button onClick={() => navigate(`/chapters/${id}/generate`)}>
            AI生成
          </Button>
          <Button type="primary" onClick={() => navigate(`/chapters/${id}/edit`)}>
            编辑
          </Button>
        </Space>
      }
      loading={loading}
    >
      <Descriptions bordered column={2}>
        <Descriptions.Item label="ID">{chapter.id}</Descriptions.Item>
        <Descriptions.Item label="所属小说">
          {chapter.novel?.title || '-'}
        </Descriptions.Item>
        <Descriptions.Item label="章节编号">{chapter.chapter_number}</Descriptions.Item>
        <Descriptions.Item label="状态">{getStatusTag(chapter.status)}</Descriptions.Item>
        <Descriptions.Item label="字数">{chapter.word_count.toLocaleString()}</Descriptions.Item>
        <Descriptions.Item label="创建时间">
          {dayjs(chapter.created_at).format('YYYY-MM-DD HH:mm:ss')}
        </Descriptions.Item>
        <Descriptions.Item label="更新时间" span={2}>
          {dayjs(chapter.updated_at).format('YYYY-MM-DD HH:mm:ss')}
        </Descriptions.Item>
        <Descriptions.Item label="摘要" span={2}>
          {chapter.summary || '-'}
        </Descriptions.Item>
        {chapter.outline_json && (
          <Descriptions.Item label="创作大纲" span={2}>
            <Collapse
              items={[{
                key: 'outline',
                label: `第${chapter.chapter_number}章大纲`,
                children: (
                  <div className="outline-content" style={{ maxHeight: '400px', overflow: 'auto' }}>
                    <Markdown>{formatOutline(chapter.outline_json)}</Markdown>
                  </div>
                ),
              }]}
            />
          </Descriptions.Item>
        )}
        <Descriptions.Item label="内容" span={2}>
          <div style={{ whiteSpace: 'pre-wrap', maxHeight: '400px', overflow: 'auto' }}>
            {chapter.content || '-'}
          </div>
        </Descriptions.Item>
      </Descriptions>
    </Card>
  )
}

export default ChapterDetailPage
