import asyncio
import json
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

# 加载后的值，会被系统环境变量覆盖
load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        # self.anthropic = Anthropic() # 这个不支持
        self.openai = OpenAI()
    # methods will go here

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""

        # 这里要保持会话连接，所以不能用with
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str, url: str) -> str:
        """Process a query using LLM and available tools"""
        messages = []

        response = await self.session.list_tools()

        print(f"日志打印：query：{query}     url：{url}")

        tool_name = 'fetch_url'
        json_dict = {
            "url": url
        }
        tool_args = json.loads(json.dumps(json_dict, ensure_ascii=True))

        # Execute tool call
        result = await self.session.call_tool(tool_name, tool_args)

        print("爬虫mcp调用成功。。。。。。。。。。。。。。")
        print("爬虫mcp调用结果：", result.content)

        system_prompt = """
你是一个辅助用户从网页内收集资料的助手。
你的任务是从给你的网页内容中收集网页的内容，不要修改内容，只返回给你提供的网页内的内容。
你的任务是将爬虫提供的数据整理成合适的格式，同时参考用户的格式要求。绝对不要自行修改内容，只调整格式即可。
返回格式要求：只包含网页内容，不要添加其他内容。
"""
        system_prompt = system_prompt.format(user_format=query, web_content=result.content)

        user_prompt = """
以下是用户的要求：
{user_format}

以下是爬虫工具爬取的网页信息：
{web_content}
"""
        user_prompt = user_prompt.format(user_format=query, web_content=result.content)

        messages.append({
            "role": "system",
            "content": system_prompt
        })
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        print("开始调用LLM模型整理...")
        # Get next response from LLM
        response = self.openai.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
            max_tokens=10000,
            messages=messages,
            extra_body={"enable_thinking": False,}  # 千问模型的可思考模式
        )
        
        res = response.choices[0].message.content

        return res

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                url = input("\nWeb Url: ").strip()


                response = await self.process_query(query, url)
                print("整体返回：\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)

    client = MCPClient()
    try:
        await client.connect_to_sse_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())