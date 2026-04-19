from fastmcp import FastMCP
from starlette.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
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
@app.route("/")
async def homepage(request):
    tools_html = "".join([
        f"""
        <div style='background:#1c2128;padding:15px;margin:10px;border-radius:8px;border:1px solid #30363d;text-align:left;'>
            <b style='color:#58a6ff;font-size:1.1rem;'>{t['name']}</b>
            <div style='color:#8b949e;font-size:0.9rem;margin-top:5px;'>{t['desc']}</div>
        </div>
        """
        for t in MY_TOOLS
    ])
    
    html = f"""
    <html>
        <head><title>FastMCP Dashboard</title></head>
        <body style="font-family:sans-serif;background:#0d1117;color:white;display:flex;flex-direction:column;align-items:center;padding-top:60px;">
            <div style="background:#161b22;padding:40px;border-radius:12px;border:1px solid #30363d;width:100%;max-width:500px;text-align:center;">
                <h1 style="color:#3fb950;margin-bottom:10px;">🚀 FastMCP Dashboard</h1>
                <p style="color:#8b949e;">SSE Endpoint: <code style="color:#58a6ff;">/mcp</code></p>
                
                <div style="margin-top:30px; border-top:1px solid #30363d; padding-top:20px;">
                    <h3 style="text-align:left;color:#f0f6fc;margin-left:10px;">已註冊指令 ({len(MY_TOOLS)})</h3>
                    {tools_html}
                </div>
            </div>
            <p style="margin-top:20px;color:#484f58;font-size:0.8rem;">支援 FastMCP v3.2.4</p>
        </body>
    </html>
    """
    return HTMLResponse(html)

@app.route("/health")
async def health(request):
    return JSONResponse({"status": "ok"})

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

if __name__ == "__main__":
    import uvicorn
    # 本地測試連線: http://127.0.0.1:8001/mcp
    uvicorn.run(app, host="0.0.0.0", port=8001)