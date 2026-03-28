"""
MCP (Model Context Protocol) 工具模块
为AI Agent提供标准化的工具接口
"""
from .base import BaseMCPTool, MCPToolRegistry, MCPToolResult, MCPToolCategory
from .novel_tools import NovelManagementTools

from .router import router

__all__ = [
    "BaseMCPTool",
    "MCPToolRegistry",
    "MCPToolResult",
    "MCPToolCategory",
    "NovelManagementTools",
    "router",
]
