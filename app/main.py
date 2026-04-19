from fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
import os

# 1. 初始化 FastMCP
mcp = FastMCP(
    name="FastMCP-Demo",
    instructions="這是一個用於 GitHub 示範的 FastMCP 伺服器，支援問候與基礎運算。"
)

# 2. 定義工具 (Tools)
@mcp.tool()
def hello(name: str = "World"):
    """問候工具：回傳歡迎訊息。"""
    return f"Hello, {name}! FastMCP 伺服器運作正常。"

@mcp.tool()
def add(a: int, b: int):
    """運算工具：執行簡單的加法。"""
    return a + b

@mcp.tool()
def get_server_status():
    """狀態工具：確認伺服器運作資訊。"""
    return {"status": "online", "platform": "FastMCP"}

# 3. 建立 ASGI App 物件 (供生產環境 gunicorn/uvicorn 使用)
# 將 path 設為 /mcp 是一個業界常見的規範
app = mcp.http_app(path="/mcp")

# 添加一個美觀的首頁儀表板
@app.route("/")
async def homepage(request):
    html = """
    <html>
        <head>
            <title>FastMCP Demo</title>
            <style>
                body { font-family: sans-serif; background: #0d1117; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; }
                .card { background: #161b22; border: 1px solid #30363d; padding: 2rem; border-radius: 8px; text-align: center; }
                code { color: #58a6ff; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🚀 FastMCP Server is Live</h1>
                <p>SSE Endpoint: <code>/mcp/sse</code></p>
                <p>Status: <span style="color: #3fb950;">Healthy</span></p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(html)

@app.route("/health")
async def health(request):
    return JSONResponse({"status": "ok"})

# 4. 本地開發啟動邏輯
if __name__ == "__main__":
    import uvicorn
    # 使用環境變數 PORT，這能讓代碼直接在 Azure/Heroku 運行
    port = int(os.environ.get("PORT", 8001))
    # 本地開發使用 host="127.0.0.1"，伺服器部署請確保改為 "0.0.0.0"
    uvicorn.run(app, host="0.0.0.0", port=port)