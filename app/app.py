import logging
import os
import uvicorn
import sys
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def configure_logger():
    profile = os.getenv("PROFILE", "dev").lower()
    log_format = "%(asctime)s %(levelname)s %(message)s"
    if profile == "prod":
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        for handler in logger.handlers:
            logger.removeHandler(handler)
        file_handler = logging.FileHandler("app.log", encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    else:
        logging.basicConfig(level=logging.INFO, format=log_format)


configure_logger()

app = FastAPI(
    title="Dynamic MCP Demo",
    description="一个动态的MCP服务器，根据不同的URL端点返回不同的MCP描述和工具描述",
    version="1.0.0"
)


# ==================== 数据模型定义 ====================

class ToolParameter(BaseModel):
    """工具参数定义"""
    name: str
    type: str
    description: str
    required: bool = False


class Tool(BaseModel):
    """工具定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any] = Field(..., alias="inputSchema")


class ServerInfo(BaseModel):
    """服务器信息"""
    name: str
    version: str
    description: Optional[str] = None


class MCPConfig(BaseModel):
    """MCP配置"""
    server: ServerInfo
    tools: List[Tool]


# ==================== MCP配置数据 ====================

# 预定义的不同MCP配置
MCP_CONFIGS: Dict[str, MCPConfig] = {
    "weather": MCPConfig(
        server=ServerInfo(
            name="Weather MCP Server",
            version="1.0.0",
            description="提供天气查询相关的工具"
        ),
        tools=[
            Tool(
                name="get_weather",
                description="获取指定城市的天气信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "要查询天气的城市名称"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "温度单位",
                            "default": "celsius"
                        }
                    },
                    "required": ["city"]
                }
            ),
            Tool(
                name="get_forecast",
                description="获取指定城市的天气预报",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "要查询天气预报的城市名称"
                        },
                        "days": {
                            "type": "integer",
                            "description": "预报天数（1-7天）",
                            "minimum": 1,
                            "maximum": 7,
                            "default": 3
                        }
                    },
                    "required": ["city"]
                }
            )
        ]
    ),
    "database": MCPConfig(
        server=ServerInfo(
            name="Database MCP Server",
            version="1.0.0",
            description="提供数据库操作相关的工具"
        ),
        tools=[
            Tool(
                name="query_database",
                description="执行SQL查询",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "要执行的SQL查询语句"
                        },
                        "database": {
                            "type": "string",
                            "description": "数据库名称",
                            "default": "default"
                        }
                    },
                    "required": ["sql"]
                }
            ),
            Tool(
                name="execute_command",
                description="执行数据库命令（INSERT, UPDATE, DELETE）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "要执行的SQL命令"
                        },
                        "database": {
                            "type": "string",
                            "description": "数据库名称",
                            "default": "default"
                        }
                    },
                    "required": ["command"]
                }
            ),
            Tool(
                name="list_tables",
                description="列出数据库中的所有表",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "database": {
                            "type": "string",
                            "description": "数据库名称",
                            "default": "default"
                        }
                    },
                    "required": []
                }
            )
        ]
    ),
    "file": MCPConfig(
        server=ServerInfo(
            name="File System MCP Server",
            version="1.0.0",
            description="提供文件系统操作相关的工具"
        ),
        tools=[
            Tool(
                name="read_file",
                description="读取文件内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "要读取的文件路径"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "文件编码",
                            "default": "utf-8"
                        }
                    },
                    "required": ["path"]
                }
            ),
            Tool(
                name="write_file",
                description="写入文件内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "要写入的文件路径"
                        },
                        "content": {
                            "type": "string",
                            "description": "要写入的文件内容"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "文件编码",
                            "default": "utf-8"
                        }
                    },
                    "required": ["path", "content"]
                }
            ),
            Tool(
                name="list_directory",
                description="列出目录内容",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "要列出的目录路径",
                            "default": "."
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "是否递归列出子目录",
                            "default": False
                        }
                    },
                    "required": []
                }
            )
        ]
    ),
    "api": MCPConfig(
        server=ServerInfo(
            name="API Client MCP Server",
            version="1.0.0",
            description="提供HTTP API调用相关的工具"
        ),
        tools=[
            Tool(
                name="http_get",
                description="发送HTTP GET请求",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "请求的URL"
                        },
                        "headers": {
                            "type": "object",
                            "description": "HTTP请求头",
                            "additionalProperties": {"type": "string"}
                        }
                    },
                    "required": ["url"]
                }
            ),
            Tool(
                name="http_post",
                description="发送HTTP POST请求",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "请求的URL"
                        },
                        "body": {
                            "type": "object",
                            "description": "请求体（JSON格式）"
                        },
                        "headers": {
                            "type": "object",
                            "description": "HTTP请求头",
                            "additionalProperties": {"type": "string"}
                        }
                    },
                    "required": ["url", "body"]
                }
            )
        ]
    )
}


# ==================== API端点 ====================

@app.get("/")
async def root():
    """根端点，返回可用的MCP端点列表"""
    return {
        "message": "Dynamic MCP Demo Server",
        "available_endpoints": list(MCP_CONFIGS.keys()),
        "endpoints_info": {
            endpoint: {
                "server_name": config.server.name,
                "tools_count": len(config.tools)
            }
            for endpoint, config in MCP_CONFIGS.items()
        }
    }


@app.get("/mcp/{endpoint}", response_model=MCPConfig)
async def get_mcp_config(endpoint: str):
    """
    根据端点名称返回对应的MCP配置
    
    - **endpoint**: MCP端点名称（weather, database, file, api等）
    """
    if endpoint not in MCP_CONFIGS:
        available = ", ".join(MCP_CONFIGS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"MCP端点 '{endpoint}' 不存在。可用的端点: {available}"
        )
    return MCP_CONFIGS[endpoint]


@app.get("/mcp/{endpoint}/server", response_model=ServerInfo)
async def get_mcp_server_info(endpoint: str):
    """
    获取指定MCP端点的服务器信息
    
    - **endpoint**: MCP端点名称
    """
    if endpoint not in MCP_CONFIGS:
        available = ", ".join(MCP_CONFIGS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"MCP端点 '{endpoint}' 不存在。可用的端点: {available}"
        )
    return MCP_CONFIGS[endpoint].server


@app.get("/mcp/{endpoint}/tools", response_model=List[Tool])
async def get_mcp_tools(endpoint: str):
    """
    获取指定MCP端点的工具列表
    
    - **endpoint**: MCP端点名称
    """
    if endpoint not in MCP_CONFIGS:
        available = ", ".join(MCP_CONFIGS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"MCP端点 '{endpoint}' 不存在。可用的端点: {available}"
        )
    return MCP_CONFIGS[endpoint].tools


@app.get("/mcp/{endpoint}/tools/{tool_name}", response_model=Tool)
async def get_tool_description(endpoint: str, tool_name: str):
    """
    获取指定工具的详细描述
    
    - **endpoint**: MCP端点名称
    - **tool_name**: 工具名称
    """
    if endpoint not in MCP_CONFIGS:
        available = ", ".join(MCP_CONFIGS.keys())
        raise HTTPException(
            status_code=404,
            detail=f"MCP端点 '{endpoint}' 不存在。可用的端点: {available}"
        )
    
    config = MCP_CONFIGS[endpoint]
    tool = next((t for t in config.tools if t.name == tool_name), None)
    
    if not tool:
        available_tools = ", ".join(t.name for t in config.tools)
        raise HTTPException(
            status_code=404,
            detail=f"工具 '{tool_name}' 在端点 '{endpoint}' 中不存在。可用的工具: {available_tools}"
        )
    
    return tool


@app.get("/list-endpoints")
async def list_all_endpoints():
    """列出所有可用的MCP端点及其简要信息"""
    return {
        "endpoints": [
            {
                "endpoint": endpoint,
                "server_name": config.server.name,
                "server_version": config.server.version,
                "server_description": config.server.description,
                "tools": [
                    {
                        "name": tool.name,
                        "description": tool.description
                    }
                    for tool in config.tools
                ]
            }
            for endpoint, config in MCP_CONFIGS.items()
        ]
    }


if __name__ == "__main__":
    uvicorn.run("app.app:app", host="0.0.0.0", port=8000, reload=True)
