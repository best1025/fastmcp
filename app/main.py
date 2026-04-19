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
from starlette.routing import Mount
from starlette.middleware.cors import CORSMiddleware

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
    allowed_names = {
        k: v for k, v in math.__dict__.items() if not k.startswith("_")
    }
    allowed_names["abs"] = abs
    allowed_names["round"] = round

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)  # noqa: S307
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
        Mount("/", app=_mcp_http),
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
