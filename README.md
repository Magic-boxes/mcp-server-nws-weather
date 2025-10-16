# mcp-sse的NWS天气服务
简介：调用NWS查询美国天气的MCP Server（openai接口格式）

# 默认python版本：3.11（可自行修改，依赖库下载正常即可）

# 下载依赖
uv sync

# server-sse运行：
```shell
uv run ./server-sse.py --host=0.0.0.0 --port=8080
```
# client-sse运行
```shell
uv run ./client-sse.py http://localhost:8080/sse/
```

# Configure：
```json
{
  "mcpServers": {
    "nws-weather": {
      "command": "python",
      "args": ["./server-stdio.py"]
    }
  }
}
```
