import asyncio
from fastmcp import Client

async def main():
    async with Client("http://127.0.0.1:8001/mcp") as client:
        result = await client.call_tool(
            "hello",
            {"name": "Tom"}
        )
        print(result)

asyncio.run(main())