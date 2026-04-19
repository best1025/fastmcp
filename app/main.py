"""
FastMCP Server - Azure App Service 部署版本
啟動命令: gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app
"""

import os
import math
import httpx
from datetime import datetime
from typing import Optional

from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route
from starlette.middleware.cors import CORSMiddleware

# ────────────────────────────────────────────────
# 首頁 HTML（GET /）
# ────────────────────────────────────────────────
HOMEPAGE_HTML = """\
<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>FastMCP Demo Server</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:      #0d1117;
      --card:    #161b22;
      --border:  #30363d;
      --accent:  #58a6ff;
      --green:   #3fb950;
      --purple:  #bc8cff;
      --orange:  #f0883e;
      --text:    #e6edf3;
      --sub:     #8b949e;
    }
    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 48px 16px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(63,185,80,.15);
      border: 1px solid rgba(63,185,80,.4);
      color: var(--green);
      border-radius: 99px;
      padding: 4px 14px;
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: .04em;
      margin-bottom: 24px;
    }
    .dot {
      width: 8px; height: 8px;
      border-radius: 50%;
      background: var(--green);
      animation: pulse 1.6s ease-in-out infinite;
    }
    @keyframes pulse {
      0%,100% { opacity: 1; transform: scale(1); }
      50%      { opacity: .4; transform: scale(.7); }
    }
    h1 {
      font-size: clamp(1.8rem, 4vw, 2.6rem);
      font-weight: 700;
      background: linear-gradient(135deg, var(--accent) 0%, var(--purple) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 10px;
      text-align: center;
    }
    .subtitle {
      color: var(--sub);
      font-size: 1rem;
      margin-bottom: 40px;
      text-align: center;
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
      width: 100%;
      max-width: 860px;
      margin-bottom: 40px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 22px;
      transition: border-color .2s, transform .2s;
    }
    .card:hover { border-color: var(--accent); transform: translateY(-2px); }
    .card-icon { font-size: 1.5rem; margin-bottom: 10px; }
    .card-title { font-weight: 600; font-size: .95rem; margin-bottom: 6px; }
    .card-desc  { color: var(--sub); font-size: .83rem; line-height: 1.6; }
    .card-tag {
      display: inline-block;
      margin-top: 10px;
      background: rgba(88,166,255,.12);
      color: var(--accent);
      border-radius: 6px;
      padding: 2px 8px;
      font-size: .75rem;
      font-family: monospace;
    }
    .section-title {
      color: var(--sub);
      font-size: .78rem;
      font-weight: 600;
      letter-spacing: .08em;
      text-transform: uppercase;
      margin-bottom: 12px;
      align-self: flex-start;
      max-width: 860px;
      width: 100%;
    }
    .endpoint-box {
      width: 100%;
      max-width: 860px;
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 32px;
    }
    .ep-row {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 14px 20px;
      border-bottom: 1px solid var(--border);
    }
    .ep-row:last-child { border-bottom: none; }
    .method {
      font-size: .72rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      font-family: monospace;
      min-width: 42px;
      text-align: center;
    }
    .get  { background: rgba(63,185,80,.2);  color: var(--green); }
    .sse  { background: rgba(240,136,62,.2); color: var(--orange); }
    .ep-path { font-family: monospace; font-size: .88rem; flex: 1; }
    .ep-note { color: var(--sub); font-size: .8rem; }
    footer {
      color: var(--sub);
      font-size: .8rem;
      margin-top: auto;
      padding-top: 32px;
      text-align: center;
    }
    footer a { color: var(--accent); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="badge"><div class="dot"></div>RUNNING</div>
  <h1>FastMCP Demo Server</h1>
  <p class="subtitle">基於 FastMCP 的 MCP 示範伺服器 &mdash; Azure App Service (F1)</p>

  <p class="section-title">可用工具 (Tools)</p>
  <div class="cards">
    <div class="card">
      <div class="card-icon">👋</div>
      <div class="card-title">hello</div>
      <div class="card-desc">打招呼，確認伺服器連線是否正常。</div>
      <div class="card-tag">hello(name)</div>
    </div>
    <div class="card">
      <div class="card-icon">⚖️</div>
      <div class="card-title">calculate_bmi</div>
      <div class="card-desc">輸入體重與身高，計算 BMI 並自動分類。</div>
      <div class="card-tag">calculate_bmi(weight_kg, height_m)</div>
    </div>
    <div class="card">
      <div class="card-icon">🕐</div>
      <div class="card-title">get_current_time</div>
      <div class="card-desc">取得目前 UTC 時間（台灣時間 +8 小時）。</div>
      <div class="card-tag">get_current_time()</div>
    </div>
    <div class="card">
      <div class="card-icon">🧮</div>
      <div class="card-title">math_calculator</div>
      <div class="card-desc">安全數學運算器，支援 math 模組所有函數。</div>
      <div class="card-tag">math_calculator(expression)</div>
    </div>
    <div class="card">
      <div class="card-icon">🌤️</div>
      <div class="card-title">get_weather</div>
      <div class="card-desc">查詢城市即時天氣，使用 wttr.in 免費 API。</div>
      <div class="card-tag">get_weather(city)</div>
    </div>
    <div class="card">
      <div class="card-icon">📏</div>
      <div class="card-title">unit_converter</div>
      <div class="card-desc">長度、重量、溫度單位換算。</div>
      <div class="card-tag">unit_converter(value, from_unit, to_unit)</div>
    </div>
  </div>

  <p class="section-title">端點 (Endpoints)</p>
  <div class="endpoint-box">
    <div class="ep-row">
      <span class="method get">GET</span>
      <span class="ep-path">/</span>
      <span class="ep-note">此頁面（伺服器狀態）</span>
    </div>
    <div class="ep-row">
      <span class="method get">GET</span>
      <span class="ep-path">/health</span>
      <span class="ep-note">健康檢查 JSON</span>
    </div>
    <div class="ep-row">
      <span class="method sse">SSE</span>
      <span class="ep-path">/mcp/sse</span>
      <span class="ep-note">MCP 客戶端連線端點（SSE）</span>
    </div>
    <div class="ep-row">
      <span class="method get">POST</span>
      <span class="ep-path">/mcp/messages/</span>
      <span class="ep-note">MCP 訊息端點</span>
    </div>
  </div>

  <footer>
    FastMCP Demo v1.0.0 &bull;
    <a href="https://github.com/best1025/fastmcp" target="_blank">GitHub</a> &bull;
    <a href="/health" target="_blank">/health</a>
  </footer>
</body>
</html>
"""


async def homepage(request: Request) -> HTMLResponse:
    """首頁：顯示伺服器狀態與工具清單。"""
    return HTMLResponse(HOMEPAGE_HTML)


async def health(request: Request) -> JSONResponse:
    """健康檢查端點，供 Azure / 監控系統使用。"""
    return JSONResponse({
        "status": "ok",
        "server": "FastMCP-Demo",
        "version": "1.0.0",
        "utc_time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mcp_endpoint": "/mcp/sse",
    })

# ────────────────────────────────────────────────
# FastMCP 伺服器初始化
# ────────────────────────────────────────────────
mcp = FastMCP(
    name="FastMCP-Demo",
    instructions=(
        "這是一個 FastMCP 示範伺服器，提供天氣查詢、BMI 計算、"
        "數學運算及時間查詢等工具。"
    ),
)


# ────────────────────────────────────────────────
# Tools（工具）
# ────────────────────────────────────────────────

@mcp.tool()
def hello(name: str = "World") -> str:
    """打招呼工具，回傳歡迎訊息。"""
    return f"Hello, {name}! 🎉 FastMCP 伺服器運作正常。"


@mcp.tool()
def calculate_bmi(weight_kg: float, height_m: float) -> dict:
    """
    計算 BMI（身體質量指數）。

    Args:
        weight_kg: 體重（公斤）
        height_m:  身高（公尺）

    Returns:
        包含 BMI 值與分類的字典
    """
    if height_m <= 0 or weight_kg <= 0:
        return {"error": "體重與身高必須為正數"}

    bmi = round(weight_kg / (height_m ** 2), 2)

    if bmi < 18.5:
        category = "體重過輕"
    elif bmi < 24:
        category = "正常體重"
    elif bmi < 27:
        category = "體重過重"
    elif bmi < 30:
        category = "輕度肥胖"
    elif bmi < 35:
        category = "中度肥胖"
    else:
        category = "重度肥胖"

    return {
        "bmi": bmi,
        "category": category,
        "weight_kg": weight_kg,
        "height_m": height_m,
    }


@mcp.tool()
def get_current_time(timezone: str = "Asia/Taipei") -> dict:
    """
    取得目前時間（UTC）。

    Args:
        timezone: 時區名稱（目前僅供參考，回傳 UTC 時間）

    Returns:
        包含日期、時間資訊的字典
    """
    now = datetime.utcnow()
    return {
        "utc_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "weekday": now.strftime("%A"),
        "note": "回傳 UTC 時間，台灣時間請 +8 小時",
    }


@mcp.tool()
def math_calculator(expression: str) -> dict:
    """
    安全的數學運算器，支援基本四則及 math 模組函數。

    Args:
        expression: 數學運算式，例如 '2 + 3 * 4' 或 'math.sqrt(16)'

    Returns:
        包含結果的字典
    """
    # 同時支援 math.sqrt(16) 和 sqrt(16) 兩種寫法
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("_")
    }
    allowed_names["abs"] = abs
    allowed_names["round"] = round
    allowed_names["math"] = math   # 允許 math.xxx 前綴語法

    try:
        result = eval(expression, {"__builtins__": {}, "math": math}, allowed_names)  # noqa: S307
        return {"expression": expression, "result": result}
    except Exception as exc:
        return {"expression": expression, "error": str(exc)}


@mcp.tool()
async def get_weather(city: str) -> dict:
    """
    查詢城市天氣（使用 wttr.in 免費 API，無需 API Key）。

    Args:
        city: 城市名稱，例如 'Taipei', 'Tokyo', 'London'

    Returns:
        包含天氣概況的字典
    """
    url = f"https://wttr.in/{city}?format=j1"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

        current = data["current_condition"][0]
        return {
            "city": city,
            "temp_c": current["temp_C"],
            "feels_like_c": current["FeelsLikeC"],
            "humidity_pct": current["humidity"],
            "weather_desc": current["weatherDesc"][0]["value"],
            "wind_speed_kmph": current["windspeedKmph"],
            "visibility_km": current["visibility"],
        }
    except httpx.HTTPStatusError as exc:
        return {"city": city, "error": f"HTTP {exc.response.status_code}"}
    except Exception as exc:
        return {"city": city, "error": str(exc)}


@mcp.tool()
def unit_converter(value: float, from_unit: str, to_unit: str) -> dict:
    """
    單位換算工具（長度、重量、溫度）。

    Args:
        value:     數值
        from_unit: 來源單位（km/m/cm/mile/kg/g/lb/c/f/k）
        to_unit:   目標單位（同上）

    Returns:
        換算結果字典
    """
    conversions = {
        # 長度 → 公尺
        "km": 1000, "m": 1, "cm": 0.01, "mm": 0.001,
        "mile": 1609.344, "yard": 0.9144, "ft": 0.3048, "inch": 0.0254,
        # 重量 → 公克
        "kg": 1000, "g": 1, "mg": 0.001, "lb": 453.592, "oz": 28.3495,
    }

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # 溫度特殊處理
    temp_units = {"c", "f", "k"}
    if from_unit in temp_units or to_unit in temp_units:
        try:
            if from_unit == "c" and to_unit == "f":
                result = value * 9 / 5 + 32
            elif from_unit == "f" and to_unit == "c":
                result = (value - 32) * 5 / 9
            elif from_unit == "c" and to_unit == "k":
                result = value + 273.15
            elif from_unit == "k" and to_unit == "c":
                result = value - 273.15
            elif from_unit == "f" and to_unit == "k":
                result = (value - 32) * 5 / 9 + 273.15
            elif from_unit == "k" and to_unit == "f":
                result = (value - 273.15) * 9 / 5 + 32
            else:
                return {"error": "不支援的溫度換算組合"}
            return {"value": value, "from": from_unit, "to": to_unit, "result": round(result, 4)}
        except Exception as exc:
            return {"error": str(exc)}

    if from_unit not in conversions or to_unit not in conversions:
        return {"error": f"不支援的單位：{from_unit} 或 {to_unit}"}

    # 判斷是否屬於同一類別（長度或重量）
    length_units = {"km", "m", "cm", "mm", "mile", "yard", "ft", "inch"}
    weight_units = {"kg", "g", "mg", "lb", "oz"}

    from_is_length = from_unit in length_units
    to_is_length = to_unit in length_units

    if from_is_length != to_is_length:
        return {"error": "無法在不同類別的單位之間換算（例如長度 vs 重量）"}

    result = value * conversions[from_unit] / conversions[to_unit]
    return {
        "value": value,
        "from": from_unit,
        "to": to_unit,
        "result": round(result, 6),
    }


# ────────────────────────────────────────────────
# Resources（資源）
# ────────────────────────────────────────────────

@mcp.resource("info://server")
def server_info() -> str:
    """回傳伺服器基本資訊。"""
    return (
        "FastMCP-Demo 伺服器\n"
        "版本: 1.0.0\n"
        "部署平台: Azure App Service\n"
        "支援工具: hello, calculate_bmi, get_current_time, "
        "math_calculator, get_weather, unit_converter\n"
        "傳輸協定: SSE (Server-Sent Events)\n"
        "GitHub: https://github.com/best1025/fastmcp"
    )


@mcp.resource("info://tools-guide")
def tools_guide() -> str:
    """回傳工具使用手冊。"""
    return """
# FastMCP 工具使用手冊

## 1. hello(name)
- 功能：打招呼
- 參數：name（預設 "World"）
- 範例：hello(name="Alice")

## 2. calculate_bmi(weight_kg, height_m)
- 功能：計算 BMI
- 範例：calculate_bmi(weight_kg=70, height_m=1.75)

## 3. get_current_time(timezone)
- 功能：取得目前 UTC 時間
- 範例：get_current_time()

## 4. math_calculator(expression)
- 功能：數學運算
- 範例：math_calculator(expression="math.sqrt(144)")

## 5. get_weather(city)
- 功能：查詢天氣（需要網路）
- 範例：get_weather(city="Taipei")

## 6. unit_converter(value, from_unit, to_unit)
- 功能：單位換算（長度/重量/溫度）
- 範例：unit_converter(value=100, from_unit="km", to_unit="mile")
"""


# ────────────────────────────────────────────────
# Prompts（提示詞）
# ────────────────────────────────────────────────

@mcp.prompt()
def health_check_prompt() -> str:
    """產生健康檢查提示詞。"""
    return (
        "請依序呼叫以下工具來驗證伺服器功能：\n"
        "1. hello(name='測試')\n"
        "2. get_current_time()\n"
        "3. calculate_bmi(weight_kg=70, height_m=1.75)\n"
        "4. math_calculator(expression='2**10')\n"
        "並彙總回傳結果。"
    )


# ────────────────────────────────────────────────
# ASGI App 建立（供 Gunicorn / Uvicorn 使用）
# ────────────────────────────────────────────────
_mcp_http = mcp.http_app(path="/mcp")

app = Starlette(
    routes=[
        Route("/",       endpoint=homepage),   # 首頁
        Route("/health", endpoint=health),     # 健康檢查
        Mount("/mcp",    app=_mcp_http),       # MCP SSE
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────
# 本機開發直接執行
# ────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
