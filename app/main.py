from fastmcp import FastMCP

import os

# 1. 初始化
mcp = FastMCP(name="FastMCP-Demo")

# --- 手動統計清單 ---
MY_TOOLS = []

# 2. 定義工具並加入清單
@mcp.tool()
def hello(name: str = "World"):
    """問候工具"""
    return f"Hello, {name}!"
MY_TOOLS.append({"name": "hello", "desc": "問候工具，範例：hello(name='Tom')"})

@mcp.tool()
def add(a: int, b: int):
    """加法工具"""
    return a + b
MY_TOOLS.append({"name": "add", "desc": "加法工具，範例：add(a=1, b=2)"})


# 3. 生成 App
app = mcp.http_app()


# 4. 首頁 (直接讀取 MY_TOOLS)





if __name__ == "__main__":
    import uvicorn
    # 本地測試連線: http://127.0.0.1:8001/mcp
    uvicorn.run(app, host="0.0.0.0", port=8001)