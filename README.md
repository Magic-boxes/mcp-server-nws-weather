# mcp-sse的NWS天气服务
简介：调用NWS查询美国天气的MCP Server（openai接口格式）

# server-sse运行：
```shell
python ./server.py --host=0.0.0.0 --port=8080
```
# client-sse运行
```shell
python ./client.py http://localhost:8080/sse/
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
