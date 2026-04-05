"""
章节后处理流水线
在章节正文生成完成后执行：
1. 结尾完整性检测与补全
2. 结构化信息解析（未来规划、伏笔/钩子）
3. 时间线条目自动入库（Phase 2 接入）
"""
import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.llm_service import llm_service

logger = logging.getLogger(__name__)

VALID_ENDING_CHARS = set("。！？…」』》\"'")
INCOMPLETE_PUNCTUATION = set("，、；：—·")


def is_ending_complete(text: str) -> bool:
    if not text or len(text.strip()) < 10:
        return False
    stripped = text.rstrip()
    last_char = stripped[-1] if stripped else ""
    if last_char in INCOMPLETE_PUNCTUATION:
        return False
    if last_char in VALID_ENDING_CHARS:
        last_paragraph = _get_last_paragraph(stripped)
        if len(last_paragraph) >= 10:
            return True
    return False


def _get_last_paragraph(text: str) -> str:
    paragraphs = text.rstrip().split("\n")
    for p in reversed(paragraphs):
        if p.strip():
            return p.strip()
    return ""


async def complete_ending(text: str, model: Optional[str] = None) -> str:
    prompt = (
        f"以下是一段小说正文的末尾，它似乎在句子中间被截断了。"
        f"请补全最后一句话，使其自然收尾。\n\n"
        f"原文末尾（约最后200字）：\n{text[-800:]}\n\n"
        f"要求：\n"
        f"- 只输出补全的部分，不要重复原文\n"
        f"- 保持原文风格和语气\n"
        f"- 以合适的标点符号结尾（句号/感叹号/问号）\n"
        f"- 补全内容控制在50-200字以内\n"
        f"直接输出补全文本，不要加任何前缀说明。"
    )
    try:
        completion = ""
        async for chunk in llm_service.generate_stream(
            prompt=prompt,
            system_prompt="你是一个专业的小说编辑助手，擅长自然地补全被截断的文本。",
            model=model,
            max_tokens=200,
        ):
            completion += chunk
        if completion.strip():
            return text + "\n" + completion.strip()
    except Exception as exc:
        logger.warning(f"Failed to complete ending: {exc}")
    return text


class ChapterPostProcessor:
    def __init__(self, db, novel_id: int):
        self.db = db
        self.novel_id = novel_id

    async def process(self, content: str, chapter_number: int, chapter_id: int,
                      model: Optional[str] = None) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "original_content": content,
            "final_content": content,
            "was_truncated": False,
            "ending_completed": False,
            "has_ending_marker": False,
        }
        processed = content
        if not is_ending_complete(processed):
            logger.info(f"Chapter {chapter_number} ending appears incomplete, attempting completion")
            processed = await complete_ending(processed, model)
            result["was_truncated"] = True
            result["ending_completed"] = processed != content
            result["final_content"] = processed
        marker_match = re.search(r'---【第\d+章完结】---', processed)
        if marker_match:
            result["has_ending_marker"] = True
            processed = re.sub(r'\n*---【第\d+章完结】---\n*', '', processed).strip()
            result["final_content"] = processed
        return result

    def _extract_structured_info(self, content: str) -> Optional[Dict[str, Any]]:
        marker_pattern = r'---【第\d+章完结】---\s*\n?(.*?)(?=\n---|\Z)'
        match = re.search(marker_pattern, content, re.DOTALL)
        if not match:
            return None
        info_text = match.group(1).strip()
        parsed: Dict[str, Any] = {
            "foreshadowing_items": [],
            "next_chapter_plan": None,
            "near_term_plans": [],
            "long_term_direction": None,
        }
        foreshadowing_match = re.search(
            r'【本章埋下的伏笔[\/\\s]*钩子】.*?\n((?:-.*\n?)*)',
            info_text, re.DOTALL | re.IGNORECASE
        )
        if foreshadowing_match:
            for line in foreshadowing_match.group(1).split("\n"):
                line = line.strip().lstrip("- ").strip()
                if line:
                    parsed["foreshadowing_items"].append(line)
        next_chapter_match = re.search(
            r'【下章安排】.*?\n((?:-.*\n?)*)',
            info_text, re.DOTALL | re.IGNORECASE
        )
        if next_chapter_match:
            lines = [l.strip().lstrip("- ").strip() for l in next_chapter_match.group(1).split("\n") if l.strip()]
            if lines:
                parsed["next_chapter_plan"] = "\n".join(lines)
        near_term_match = re.search(
            r'【近期规划】.*?\n((?:-.*\n?)*)',
            info_text, re.DOTALL | re.IGNORECASE
        )
        if near_term_match:
            for line in near_term_match.group(1).split("\n"):
                line = line.strip().lstrip("- ").strip()
                if line:
                    parsed["near_term_plans"].append(line)
        long_term_match = re.search(
            r'【远期方向】[：:].*?\n(.*)',
            info_text, re.DOTALL | re.IGNORECASE
        )
        if long_term_match:
            direction = long_term_match.group(1).strip().rstrip("-").strip()
            if direction:
                parsed["long_term_direction"] = direction
        return parsed if any(parsed.values()) else None
