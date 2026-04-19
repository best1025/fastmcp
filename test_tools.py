"""
test_tools.py - FastMCP 工具快速測試腳本
不需要 MCP 客戶端，直接 import 測試所有工具。

執行方式：
    python test_tools.py
"""

import asyncio
import sys
import json
import io

# Windows cp950 終端機相容處理：強制 stdout 使用 UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, ".")


from app.main import (
    hello,
    calculate_bmi,
    get_current_time,
    math_calculator,
    unit_converter,
    get_weather,
)

SEP = "-" * 48


def show(title: str, result) -> None:
    print(f"\n[{title}]")
    print(json.dumps(result, ensure_ascii=False, indent=2)
          if isinstance(result, dict) else result)


def run_sync_tests() -> None:
    print(SEP)
    print("  同步工具測試")
    print(SEP)

    # 1. hello
    show("hello(name='Alice')",
         hello("Alice"))

    # 2. calculate_bmi - 正常範圍
    show("calculate_bmi(70, 1.75)",
         calculate_bmi(70, 1.75))

    # 2b. calculate_bmi - 過輕
    show("calculate_bmi(45, 1.70)",
         calculate_bmi(45, 1.70))

    # 3. get_current_time
    show("get_current_time()",
         get_current_time())

    # 4. math_calculator - 基本運算
    show("math_calculator('2 ** 10')",
         math_calculator("2 ** 10"))

    # 4b. math_calculator - math 模組
    show("math_calculator('math.pi * 5 ** 2')",
         math_calculator("math.pi * 5 ** 2"))

    # 4c. math_calculator - 錯誤測試
    show("math_calculator('import os')",
         math_calculator("import os"))

    # 5. unit_converter - 長度
    show("unit_converter(100, 'km', 'mile')",
         unit_converter(100, "km", "mile"))

    # 5b. unit_converter - 重量
    show("unit_converter(500, 'g', 'lb')",
         unit_converter(500, "g", "lb"))

    # 5c. unit_converter - 溫度
    show("unit_converter(100, 'c', 'f')",
         unit_converter(100, "c", "f"))

    show("unit_converter(37, 'c', 'k')",
         unit_converter(37, "c", "k"))

    # 5d. unit_converter - 錯誤（跨類別）
    show("unit_converter(10, 'km', 'kg')  # 應報錯",
         unit_converter(10, "km", "kg"))


async def run_async_tests() -> None:
    print(f"\n{SEP}")
    print("  非同步工具測試（需要網路）")
    print(SEP)

    for city in ["Taipei", "Tokyo", "London"]:
        show(f"get_weather('{city}')", await get_weather(city))


def main() -> None:
    run_sync_tests()
    asyncio.run(run_async_tests())
    print(f"\n{SEP}")
    print("  全部測試完成")
    print(SEP)


if __name__ == "__main__":
    main()
