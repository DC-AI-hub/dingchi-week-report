from mcp.server import MCPServer

from .registry import register_tools

mcp_server = MCPServer(
    "dingchi-week-report",
    instructions="提供鼎驰周报系统的健康检查与 AI 文本生成工具。",
)

register_tools(mcp_server)
