from mcp.server import MCPServer

from .registry import register_tools

mcp_server = MCPServer(
    "dingchi-week-report",
    instructions="提供鼎驰周报系统的健康检查、AI 文本生成，以及按调用方数据范围鉴权的周报数据查询工具。",
)

register_tools(mcp_server)
