# Dynamic MCP Demo

一个基于 FastAPI 的动态 MCP (Model Context Protocol) 演示服务器，可以根据不同的 URL 端点返回不同的 MCP 描述和工具描述。

## 功能特性

- 🚀 动态 MCP 配置：根据不同的端点返回不同的 MCP 配置
- 📋 工具列表：每个端点提供不同的工具集合
- 🔍 工具详情：可以查询特定工具的详细描述和参数
- 📚 自动文档：FastAPI 自动生成的交互式 API 文档

## 安装

```bash
pip install -e .
```

或者直接安装依赖：

```bash
pip install fastapi uvicorn
```

## 运行

```bash
python -m app.app
```

或者使用 uvicorn：

```bash
uvicorn app.app:app --reload
```

服务器将在 `http://localhost:8000` 启动。

## API 端点

### 1. 根端点
- **GET** `/` - 返回所有可用的 MCP 端点列表

### 2. MCP 配置端点
- **GET** `/mcp/{endpoint}` - 获取指定端点的完整 MCP 配置
  - 示例：`/mcp/weather` - 获取天气相关的 MCP 配置

### 3. 服务器信息端点
- **GET** `/mcp/{endpoint}/server` - 获取指定端点的服务器信息
  - 示例：`/mcp/database/server` - 获取数据库 MCP 服务器的信息

### 4. 工具列表端点
- **GET** `/mcp/{endpoint}/tools` - 获取指定端点的所有工具列表
  - 示例：`/mcp/file/tools` - 获取文件系统相关的所有工具

### 5. 工具详情端点
- **GET** `/mcp/{endpoint}/tools/{tool_name}` - 获取指定工具的详细描述
  - 示例：`/mcp/weather/tools/get_weather` - 获取天气查询工具的详细信息

### 6. 端点列表
- **GET** `/list-endpoints` - 列出所有可用的 MCP 端点及其详细信息

## 可用的 MCP 端点

### 1. `weather` - 天气服务
提供天气查询相关的工具：
- `get_weather` - 获取指定城市的天气信息
- `get_forecast` - 获取指定城市的天气预报

### 2. `database` - 数据库服务
提供数据库操作相关的工具：
- `query_database` - 执行 SQL 查询
- `execute_command` - 执行数据库命令（INSERT, UPDATE, DELETE）
- `list_tables` - 列出数据库中的所有表

### 3. `file` - 文件系统服务
提供文件系统操作相关的工具：
- `read_file` - 读取文件内容
- `write_file` - 写入文件内容
- `list_directory` - 列出目录内容

### 4. `api` - API 客户端服务
提供 HTTP API 调用相关的工具：
- `http_get` - 发送 HTTP GET 请求
- `http_post` - 发送 HTTP POST 请求

## 使用示例

### 获取所有可用端点
```bash
curl http://localhost:8000/
```

### 获取天气 MCP 配置
```bash
curl http://localhost:8000/mcp/weather
```

### 获取数据库 MCP 的工具列表
```bash
curl http://localhost:8000/mcp/database/tools
```

### 获取特定工具的详细信息
```bash
curl http://localhost:8000/mcp/weather/tools/get_weather
```

## API 文档

启动服务器后，访问以下地址查看交互式 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 项目结构

```
dynamic-mcp-demo/
├── app/
│   ├── __init__.py
│   └── app.py          # 主应用文件
├── pyproject.toml      # 项目配置和依赖
└── README.md           # 项目说明文档
```

## 扩展

要添加新的 MCP 端点，只需在 `app/app.py` 的 `MCP_CONFIGS` 字典中添加新的配置：

```python
MCP_CONFIGS["new_endpoint"] = MCPConfig(
    server=ServerInfo(
        name="New MCP Server",
        version="1.0.0",
        description="新端点的描述"
    ),
    tools=[
        Tool(
            name="new_tool",
            description="新工具的描述",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {
                        "type": "string",
                        "description": "参数描述"
                    }
                },
                "required": ["param"]
            }
        )
    ]
)
```

## 许可证

MIT License
