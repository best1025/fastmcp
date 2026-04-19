# FastMCP Demo 伺服器

> 部署於 Azure App Service（F1 免費方案）的 FastMCP 示範伺服器。

## 功能概覽

| 工具 | 說明 |
|------|------|
| `hello` | 打招呼，測試伺服器連線 |
| `calculate_bmi` | 計算 BMI 並分類 |
| `get_current_time` | 取得目前 UTC 時間 |
| `math_calculator` | 安全數學運算（支援 math 模組） |
| `get_weather` | 查詢城市天氣（wttr.in） |
| `unit_converter` | 長度 / 重量 / 溫度單位換算 |

## 專案結構

```
fastmcp/
│
├── app/
│   ├── main.py        # FastMCP / ASGI 入口
│   └── __init__.py
│
├── requirements.txt   # 相依套件
├── runtime.txt        # Python 3.11
├── startup.txt        # Azure 啟動命令（備忘）
├── .gitignore
└── README.md
```

## 本機開發

```bash
# 建立虛擬環境
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# 安裝相依套件
pip install -r requirements.txt

# 啟動開發伺服器
python -m app.main
# 或
uvicorn app.main:app --reload --port 8000
```

伺服器啟動後，SSE 端點位於：
```
http://localhost:8000/mcp/sse
```

## MCP 客戶端連線設定

```json
{
  "mcpServers": {
    "fastmcp-demo": {
      "url": "https://<your-app>.azurewebsites.net/mcp/sse",
      "transport": "sse"
    }
  }
}
```

## Azure App Service 部署

### 1. 在 Azure Portal 建立 App Service
- 方案：**F1（免費）**
- 執行階段：**Python 3.11 (Linux)**

### 2. 設定啟動命令

在 **設定 → 組態 → 一般設定 → 啟動命令** 填入：

```
gunicorn -w 1 -k uvicorn.workers.UvicornWorker app.main:app
```

### 3. GitHub Actions 自動部署
- 在 Azure Portal 設定 **部署中心 → GitHub**，選擇此倉庫的 `main` 分支。
- 每次推送至 `main` 分支，Azure 將自動拉取程式碼並重新啟動。

### 4. 健康檢查端點
- `GET /mcp/` — FastMCP 根路徑
- SSE 端點：`/mcp/sse`

## 注意事項（F1 免費方案限制）

- **無 Always On**：閒置 20 分鐘後應用程式進入休眠，首次請求會有冷啟動延遲（約 1~2 分鐘）。
- **共享計算資源**，不適合生產負載。
- SSE 長連線在休眠後會中斷，需由客戶端重連。

## 版本

`1.0.0` — 初始版本
