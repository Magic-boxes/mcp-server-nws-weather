# MCP sse's NWS weather service
Introduction: MCP Server (openai interface format) for querying weather in the United States by calling NWS
# Server running:
```shell
python ./server.py --host=0.0.0.0 --port=8080
```
# Client running
```shell
python ./client.py  http://localhost:8080/sse/
```