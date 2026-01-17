# API Improvement Checklist

> 此文件記錄所有需要改善的 API 問題，請逐一修復並勾選完成項目。

---

## Phase 0: API 開發規範 (Must Follow)

> ⚠️ 開發新 API 時必須遵守的規範，避免常見錯誤。

### 0.1 URL 路由規範

- [x] 後端已設置 `strict_slashes=False` - [app/__init__.py:36](../app/__init__.py#L36) ✅ 2026-01-03
  - 這讓 `/api/v1/users` 和 `/api/v1/users/` 都能正確路由

**開發新 API 時的檢查項目：**

| 項目 | 正確做法 | 錯誤做法 |
|------|----------|----------|
| Blueprint URL prefix | `/api/v1/users` (無尾部斜杠) | `/api/v1/users/` |
| add_url_rule 路徑 | `''` 或 `'/<int:id>'` | `'/'` |
| 前端 baseURL | `/api/v1/users` | `/api/v1/users/` |
| 前端 API 調用 | `.get('')` 或 `.get('?page=1')` | `.get('/')` |

### 0.2 回應格式規範

```python
# 成功回應
{"status": "ok", "data": {...}}
# 或直接回傳 data
{"data": [...], "total": 100, "page": 1}

# 錯誤回應
{"error": "Error message in English"}, 4xx/5xx
```

### 0.3 認證規範

- 所有 API endpoint 必須加上 `@jwt_required()` 或 `@admin_required`
- 例外：公開 API 需明確標註原因

---

## Phase 1: 安全性修復 (Critical)

### 1.1 認證缺失 - 加上 `@jwt_required()`

#### feed module
- [ ] `GET /api/v0/feed/<stock_id>` - [app/feed/feed_view.py:27](../app/feed/feed_view.py#L27)
- [ ] `GET /api/v0/feed` - [app/feed/feed_view.py:57](../app/feed/feed_view.py#L57)
- [ ] `POST /api/v0/feed` - [app/feed/feed_view.py:70](../app/feed/feed_view.py#L70)
- [ ] `GET /api/v0/feed/announcement_income_sheet_analysis` - [app/feed/feed_view.py](../app/feed/feed_view.py)
- [ ] `PUT /api/v0/feed/<feed_id>/announcement_income_sheet_analysis` - [app/feed/feed_view.py](../app/feed/feed_view.py)

#### basic_information module
- [ ] `GET /api/v0/basic_information/<stock_id>` - [app/basic_information/view.py:41](../app/basic_information/view.py#L41)
- [ ] `POST /api/v0/basic_information/<stock_id>` - [app/basic_information/view.py:54](../app/basic_information/view.py#L54)
- [ ] `PATCH /api/v0/basic_information/<stock_id>` - [app/basic_information/view.py:115](../app/basic_information/view.py#L115)

#### income_sheet module
- [ ] `GET /api/v0/income_sheet/<stock_id>` - [app/income_sheet/view.py:43](../app/income_sheet/view.py#L43)
- [ ] `POST /api/v0/income_sheet/<stock_id>` - [app/income_sheet/view.py:78](../app/income_sheet/view.py#L78)

#### balance_sheet module
- [ ] `GET /api/v0/balance_sheet/<stock_id>` - [app/balance_sheet/view.py:36](../app/balance_sheet/view.py#L36)
- [ ] `POST /api/v0/balance_sheet/<stock_id>` - [app/balance_sheet/view.py:39](../app/balance_sheet/view.py#L39)

#### cash_flow module
- [ ] `GET /api/v0/cash_flow/<stock_id>` - [app/cash_flow/view.py:37](../app/cash_flow/view.py#L37)
- [ ] `POST /api/v0/cash_flow/<stock_id>` - [app/cash_flow/view.py:40](../app/cash_flow/view.py#L40)

#### monthly_valuation module
- [ ] `GET /api/v0/monthly_valuation` - [app/monthly_valuation/view.py:18](../app/monthly_valuation/view.py#L18)
- [ ] `POST /api/v0/monthly_valuation` - [app/monthly_valuation/view.py:25](../app/monthly_valuation/view.py#L25)
- [ ] `PATCH /api/v0/monthly_valuation` - [app/monthly_valuation/view.py:36](../app/monthly_valuation/view.py#L36)

#### month_revenue module
- [ ] `GET /api/v0/month_revenue/<stock_id>` - [app/month_revenue/view.py:42](../app/month_revenue/view.py#L42)
- [ ] `POST /api/v0/month_revenue/<stock_id>` - [app/month_revenue/view.py:53](../app/month_revenue/view.py#L53)

#### recommended_stock module
- [ ] `GET /api/v0/recommended_stock` - [app/recommended_stock/view.py:21](../app/recommended_stock/view.py#L21)
- [ ] `POST /api/v0/recommended_stock` - [app/recommended_stock/view.py:68](../app/recommended_stock/view.py#L68)
- [ ] `GET /api/v0/recommended_stock/<id>` - [app/recommended_stock/view.py:123](../app/recommended_stock/view.py#L123)
- [ ] `DELETE /api/v0/recommended_stock/<id>` - [app/recommended_stock/view.py:154](../app/recommended_stock/view.py#L154)
- [ ] `GET /api/v0/recommended_stock/stock/<stock_id>` - [app/recommended_stock/view.py:186](../app/recommended_stock/view.py#L186)
- [ ] `GET /api/v0/recommended_stock/statistics` - [app/recommended_stock/view.py:222](../app/recommended_stock/view.py#L222)
- [ ] `GET /api/v0/recommended_stock/filter-models` - [app/recommended_stock/view.py:258](../app/recommended_stock/view.py#L258)

---

### 1.2 CSRF 保護

- [x] 啟用 JWT_COOKIE_CSRF_PROTECT - [config.py:49](../config.py#L49) ✅ 2026-01-01
- [x] 前端自動帶入 X-CSRF-TOKEN header - react-stocker/src/utils/DomainSetup.js ✅ 2026-01-01

---

## Phase 2: 一致性修復 (Medium)

### 2.1 統一回應格式

建議採用的標準格式：
```python
# 成功
{"status": "ok", "data": {...}}

# 錯誤
{"status": "error", "error": "錯誤訊息", "code": "ERROR_CODE"}
```

需要修改的檔案：
- [x] [app/basic_information/view.py](../app/basic_information/view.py) - 使用 `json.dumps('Create')` ✅ 2024-12-09 00:20
- [x] [app/basic_information/view.py:50](../app/basic_information/view.py#L50) - 使用 `json.dumps("404 Not Found")` ✅ 2024-12-09 (已在 2.2 修復)
- [x] [app/earnings_call/views.py:34](../app/earnings_call/views.py#L34) - 使用 `{"status": "資料已存在"}` ✅ 2024-12-08 (已在 2.4 修復)
- [x] [app/income_sheet/view.py:72-74](../app/income_sheet/view.py#L72) - 使用字串錯誤訊息 ✅ 2024-12-09 00:20
- [x] [app/month_revenue/view.py:49-50](../app/month_revenue/view.py#L49) - `make_response(404)` 沒有訊息 ✅ 2024-12-09 (已在 2.2 修復)
- [ ] [app/balance_sheet/view.py:36](../app/balance_sheet/view.py#L36) - 回傳純字串 (Stub, 見 3.1)
- [ ] [app/cash_flow/view.py:37](../app/cash_flow/view.py#L37) - 回傳純字串 (Stub, 見 3.1)

---

### 2.2 統一 404 Not Found 處理

- [x] [app/follow_stock/view.py:46-47](../app/follow_stock/view.py#L46) - 回傳 `jsonify(None), 200` 應改為 404 ✅ 2024-12-09 00:15
- [x] [app/month_revenue/view.py:49-50](../app/month_revenue/view.py#L49) - 沒有錯誤訊息 ✅ 2024-12-09 00:15
- [x] [app/basic_information/view.py:48-50](../app/basic_information/view.py#L48) - 格式不一致 ✅ 2024-12-09 00:15

**修正範例：**
```python
# Before
if not follow_data:
    return jsonify(None), 200

# After
if not follow_data:
    return jsonify({"error": "Resource not found"}), 404
```

---

### 2.3 統一 HTTP Method

| 操作 | 建議 Method | 需修改的檔案 |
|------|-------------|-------------|
| 建立 | POST | - |
| 部分更新 | PATCH | - |
| 完整更新 | PUT | - |

需要修改：
- [ ] [app/income_sheet/view.py](../app/income_sheet/view.py) - POST 同時處理建立和更新，建議分開
- [ ] [app/basic_information/view.py](../app/basic_information/view.py) - POST 同時處理建立和更新，建議分開

---

### 2.4 統一錯誤訊息語言

目前混用中英文，建議統一為英文：
- [x] [app/push_notification/view.py](../app/push_notification/view.py) - 中文訊息 ✅ 2024-12-08 23:30
- [x] [app/earnings_call/views.py:34](../app/earnings_call/views.py#L34) - `"資料已存在"` ✅ 2024-12-08 23:30
- [x] [app/earnings_call/views.py:39](../app/earnings_call/views.py#L39) - `"資料錯誤"` ✅ 2024-12-08 (已在 3.2 修復)
- [x] [app/monthly_valuation/view.py](../app/monthly_valuation/view.py) - `"monthly valuation資料建立錯誤"` ✅ 2024-12-08 (已在 3.2 修復)
- [x] [app/income_sheet/view.py](../app/income_sheet/view.py) - 已是英文訊息
- [x] [app/balance_sheet/view.py](../app/balance_sheet/view.py) - 已是英文訊息
- [x] [app/cash_flow/view.py](../app/cash_flow/view.py) - 已是英文訊息
- [x] [app/month_revenue/view.py](../app/month_revenue/view.py) - 已是英文訊息

---

## Phase 3: 程式碼品質 (Medium)

### 3.1 完成 Stub 實作

- [ ] [app/balance_sheet/view.py:36-37](../app/balance_sheet/view.py#L36) - GET 回傳字串
- [ ] [app/cash_flow/view.py:37-38](../app/cash_flow/view.py#L37) - GET 回傳字串
- [ ] [app/earnings_call/views.py:45-47](../app/earnings_call/views.py#L45) - GET detail 是 placeholder

---

### 3.2 加入 db.session.rollback()

- [x] [app/earnings_call/views.py:36-39](../app/earnings_call/views.py#L36) ✅ 2024-12-08
- [x] [app/recommended_stock/view.py:62-66](../app/recommended_stock/view.py#L62) ✅ 2024-12-08
- [x] [app/monthly_valuation/view.py](../app/monthly_valuation/view.py) - 檢查所有 except block ✅ 2024-12-08

**修正範例：**
```python
# Before
except Exception:
    return jsonify({"status": "資料錯誤"}), 400

# After
except Exception as e:
    db.session.rollback()
    logger.error(f"Error: {e}", exc_info=True)
    return jsonify({"error": "Failed to create resource"}), 400
```

---

### 3.3 統一使用 Marshmallow Serializer

目前混用多種序列化方式：
- [x] [app/basic_information/view.py:52](../app/basic_information/view.py#L52) - 使用 `.serialize` property ✅ 2024-12-09
- [x] [app/income_sheet/view.py](../app/income_sheet/view.py) - 新增 IncomeSheetSchema ✅ 2024-12-09
- [x] [app/month_revenue/view.py](../app/month_revenue/view.py) - 新增 MonthRevenueSchema ✅ 2024-12-09
- [x] [app/follow_stock/view.py](../app/follow_stock/view.py) - 改用 FollowStockSchema ✅ 2024-12-09

---

## Phase 4: 功能增強 (Low)

### 4.1 加入分頁功能

- [ ] `GET /api/v0/feed` - 可能回傳大量資料
- [ ] `GET /api/v0/follow_stock` - 使用者追蹤列表
- [ ] `GET /api/v0/announcement_income_sheet_analysis` - 每日列表
- [ ] `GET /api/v0/recommended_stock` - 每日推薦
- [ ] `GET /api/v0/month_revenue/<stock_id>` - 目前硬編碼 limit 60

**實作範例：**
```python
@jwt_required()
def get(self):
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)

    if limit > 100:
        limit = 100

    query = MyModel.query.paginate(page=page, per_page=limit)

    return jsonify({
        "data": MySchema(many=True).dump(query.items),
        "pagination": {
            "page": page,
            "limit": limit,
            "total": query.total,
            "pages": query.pages
        }
    })
```

---

### 4.2 加入 Rate Limiting

- [ ] 安裝 Flask-Limiter
- [ ] 設定全域限流
- [ ] 對公開 endpoint 設定更嚴格限流

---

### 4.3 加入 API 文件 (Docstring)

需要加入 docstring 的檔案：
- [ ] [app/basic_information/view.py](../app/basic_information/view.py)
- [ ] [app/income_sheet/view.py](../app/income_sheet/view.py)
- [ ] [app/balance_sheet/view.py](../app/balance_sheet/view.py)
- [ ] [app/cash_flow/view.py](../app/cash_flow/view.py)
- [ ] [app/month_revenue/view.py](../app/month_revenue/view.py)
- [ ] [app/feed/feed_view.py](../app/feed/feed_view.py)
- [ ] [app/monthly_valuation/view.py](../app/monthly_valuation/view.py)

**參考範例** ([app/recommended_stock/view.py](../app/recommended_stock/view.py)):
```python
def get(self):
    """
    Get recommended stocks with optional filters.

    Query Parameters:
        - date (str): Date in YYYY-MM-DD format (default: today)
        - filter_model (str): Filter model name
        - limit (int): Maximum number of results

    Returns:
        JSON array of recommended stocks
    """
```

---

## Phase 5: AI 功能 (New Feature)

### 5.1 法說會新聞 AI 摘要

> 當有法說會時，自動擷取相關新聞並透過 AI 摘要重點，儲存至資料庫。

> ⚠️ **技術決策**：此功能使用 **Pydantic** 取代 Marshmallow，原因：
> - LLM Structured Output 原生支援 Pydantic schema
> - LangChain/LlamaIndex 內建 Pydantic 整合
> - 自動生成 JSON Schema 可直接餵給 LLM
> - 驗證可行後，可考慮全專案遷移至 Pydantic

#### 5.1.1 資料模型設計
- [ ] 建立 `EarningsCallSummary` model
  - `earnings_call_id` (FK to earnings_call)
  - `stock_id` (FK to basic_information)
  - `created_at` (建立時間)
  - `company_outlook` (公司前景摘要)
  - `capex_plan` (資本支出計畫)
  - `investment_focus` (投資重點：本業/其他)
  - `investment_focus_detail` (投資重點詳細說明)
  - `key_points` (JSON - 其他重點)
  - `source_feed_ids` (JSON - 來源新聞 ID 列表)
  - `raw_ai_response` (原始 AI 回應，供除錯用)
  - `processing_status` (pending/processing/completed/failed)

#### 5.1.2 新聞比對服務
- [ ] 建立 `EarningsCallNewsService`
  - 根據 stock_id 和 meeting_date 查詢相關新聞
  - 時間範圍：法說會前 N 天到當天
  - 過濾條件：feedType = 'news' 或包含 'announcement'

#### 5.1.3 AI 整合
- [ ] 選擇 LLM provider (OpenAI / Anthropic / 其他)
- [ ] 建立 `AIService` 或 `LLMService`
- [ ] 設計結構化 prompt (輸出 JSON 格式)
- [ ] 處理 token 限制和長文本切割
- [ ] 錯誤處理和重試機制

#### 5.1.4 觸發機制
- [ ] 批次排程：每日檢查當日法說會
- [ ] API endpoint：手動觸發摘要生成
  - `POST /api/v1/earnings_call/<id>/summarize`
- [ ] 事件驅動：爬蟲抓到法說會時觸發 (optional)

#### 5.1.5 API Endpoints
- [ ] `GET /api/v1/earnings_call/<id>/summary` - 取得法說會摘要
- [ ] `POST /api/v1/earnings_call/<id>/summarize` - 觸發 AI 摘要
- [ ] `GET /api/v1/earnings_call/summaries` - 列出所有摘要 (分頁)

#### 5.1.6 測試
- [ ] Unit tests for EarningsCallSummary model
- [ ] Unit tests for EarningsCallNewsService
- [ ] Integration tests for AI summarization
- [ ] API endpoint tests

---

## Phase 6: Observability & Monitoring (New Feature)

> 建立完整的可觀測性架構，包含 metrics、logs、tracing。

### 6.1 Prometheus Metrics

- [ ] 安裝 `prometheus-flask-exporter`
- [ ] 設定 `/metrics` endpoint
- [ ] 加入基本 metrics:
  - Request count by endpoint, method, status
  - Request latency histogram
  - Active requests gauge
- [ ] 自訂業務 metrics:
  - Stock API 查詢次數
  - Feed 新增數量
  - AI 摘要生成次數/時間

### 6.2 Loki Log Aggregation

- [x] 設定 structured logging (JSON format) - [app/log_config.py](../app/log_config.py) ✅ 2026-01-18
- [x] 加入 request_id 追蹤 - [app/log_config.py:12](../app/log_config.py#L12) ✅ 2026-01-18
- [ ] 設定 Loki driver 或 Promtail
- [ ] 定義 log labels (app, env, service)
- [ ] 將 logs 從 container 外拉至 Loki

### 6.3 Grafana Dashboards

- [ ] 建立 API Overview dashboard
  - Request rate
  - Error rate
  - Latency percentiles (p50, p95, p99)
- [ ] 建立 Business Metrics dashboard
  - 每日活躍股票查詢
  - Feed 新增趨勢
  - AI 功能使用統計
- [ ] 建立 Logs dashboard (Loki datasource)
  - Error log 查詢面板
  - Request trace 面板

### 6.4 Alerting

- [ ] 設定 Grafana alerting rules
- [ ] Error rate > threshold
- [ ] Latency p99 > threshold
- [ ] Service down alert

### 6.5 Infrastructure

- [ ] docker-compose 加入 Prometheus, Loki, Grafana
- [ ] 設定 Prometheus scrape config
- [ ] 設定 Loki retention policy
- [ ] 設定 Grafana provisioning (datasources, dashboards)

---

## Phase 7: 股票篩選器視覺化 (New Feature)

> 將 `critical_file/screener_format.json` 的 SQL 篩選邏輯改為可拖拉組合的介面。

### 7.1 資料庫：建立 `stock_metrics` 彙總表

> ⚠️ **重要**：先建彙總表，避免每次查詢都執行複雜 JOIN，提升效能從秒級到毫秒級。

- [ ] 設計 `stock_metrics` table schema
  ```sql
  stock_id, update_date,
  -- 預算指標
  latest_eps, eps_yoy, eps_qoq,
  latest_revenue, revenue_yoy, revenue_mom,
  revenue_12m_rank,  -- 近12月營收排名 (1=最高)
  pe_ratio, gross_margin, operating_margin,
  -- 常用篩選 flag
  is_profitable, is_quality
  ```
- [ ] 建立 Alembic migration
- [ ] 建立 `StockMetricsService` 計算並更新彙總表
- [ ] 設定排程 (Celery beat) 每日更新

### 7.2 資料庫：建立篩選器設定表

- [ ] 設計 `screener_template` table (系統預設篩選器)
  - `id`, `name`, `description`
  - `conditions` (JSON - 篩選條件)
  - `exclude_rules` (JSON - 排除規則)
  - `output_fields` (JSON - 輸出欄位)
  - `is_system` (系統內建 vs 用戶自訂)
- [ ] 設計 `user_screener` table (用戶自訂篩選器)
  - `id`, `user_id`, `name`
  - `conditions`, `exclude_rules`, `output_fields`
  - `created_at`, `updated_at`
- [ ] 建立 Alembic migration

### 7.3 後端：定義篩選條件 Schema

- [ ] 定義可用欄位清單 (Pydantic/JSON Schema)
  ```python
  AVAILABLE_FIELDS = {
      "eps": {"label": "每股盈餘", "table": "stock_metrics", "type": "decimal"},
      "eps_yoy": {"label": "EPS年增率", "table": "stock_metrics", "type": "decimal"},
      "pe_ratio": {"label": "本益比", "table": "stock_metrics", "type": "decimal"},
      "revenue_yoy": {"label": "營收年增率", "table": "stock_metrics", "type": "decimal"},
      ...
  }
  ```
- [ ] 定義可用運算子
  ```python
  OPERATORS = [">", ">=", "<", "<=", "=", "!=", "in", "not_in", "is_max", "is_min"]
  ```
- [ ] 定義條件 JSON 格式
  ```json
  {
    "field": "eps_yoy",
    "operator": ">",
    "value": 10,
    "ref_field": null  // 或 "pe_ratio" 表示 eps_yoy > pe_ratio
  }
  ```

### 7.4 後端：篩選器執行引擎

- [ ] 建立 `ScreenerEngine` class
  - `parse_conditions(json)` → 解析 JSON 條件
  - `build_query(conditions)` → 組裝 SQLAlchemy query
  - `execute(conditions, limit, offset)` → 執行並回傳結果
- [ ] 支援條件組合 (AND/OR)
- [ ] 支援欄位間比較 (`eps_yoy > pe_ratio`)
- [ ] 加入 query 快取機制

### 7.5 後端：API Endpoints

- [ ] `GET /api/v1/screener/fields` - 取得可用欄位清單
- [ ] `GET /api/v1/screener/templates` - 取得系統預設篩選器
- [ ] `POST /api/v1/screener/execute` - 執行篩選 (傳入 JSON 條件)
- [ ] `GET /api/v1/screener/user` - 取得用戶自訂篩選器
- [ ] `POST /api/v1/screener/user` - 儲存用戶自訂篩選器
- [ ] `PUT /api/v1/screener/user/<id>` - 更新用戶自訂篩選器
- [ ] `DELETE /api/v1/screener/user/<id>` - 刪除用戶自訂篩選器

### 7.6 前端：拖拉介面 (React)

- [ ] 選擇拖拉套件 (`@dnd-kit/core` 或 `react-dnd`)
- [ ] 建立「條件積木」元件
  - 欄位選擇 dropdown
  - 運算子選擇
  - 數值輸入 / 欄位參照選擇
- [ ] 建立「條件容器」(AND/OR 群組)
- [ ] 建立「排除規則」區塊 (產業、價格門檻)
- [ ] 即時預覽：顯示符合條件的股票數量
- [ ] 儲存/載入自訂篩選器

### 7.7 資料遷移

- [ ] 將 `screener_format.json` 現有篩選器轉換為新格式
- [ ] 匯入為 `screener_template` (is_system=true)

---

## 進度統計

| Phase | 總項目 | 已完成 | 完成率 |
|-------|--------|--------|--------|
| Phase 1: 安全性 | 25 | 2 | 8% |
| Phase 2: 一致性 | 18 | 16 | 89% |
| Phase 3: 品質 | 10 | 7 | 70% |
| Phase 4: 功能 | 14 | 0 | 0% |
| Phase 5: AI 功能 | 16 | 0 | 0% |
| Phase 6: Observability | 17 | 2 | 12% |
| Phase 7: 篩選器視覺化 | 26 | 0 | 0% |
| **總計** | **126** | **27** | **21%** |

---

## 修改記錄

| 日期 | 修改內容 | 修改者 |
|------|----------|--------|
| 2026-01-18 | 完成 6.2 structured logging (structlog) 及 request_id 追蹤 (2項) | Claude |
| 2026-01-15 | 新增 Phase 7: 股票篩選器視覺化 - 拖拉介面、stock_metrics 彙總表 (26項) | Claude |
| 2026-01-14 | 新增 Phase 6: Observability & Monitoring - Prometheus, Loki, Grafana (17項) | Claude |
| 2026-01-07 | 新增 Phase 5: AI 功能 - 法說會新聞 AI 摘要 (16項) | Claude |
| 2026-01-01 | 完成 1.2 CSRF 保護 (2項) | Claude |
| 2024-12-09 | 完成 3.3 統一使用 Marshmallow Serializer (4項) | Claude |
| 2024-12-09 | 完成 2.1 統一回應格式 (5項) | Claude |
| 2024-12-09 | 完成 2.2 統一 404 Not Found 處理 (3項) | Claude |
| 2024-12-08 | 完成 2.4 統一錯誤訊息語言 (2項) | Claude |
| 2024-12-08 | 完成 3.2 加入 db.session.rollback() (3項) | Claude |
| 2024-12-04 | 完成 1.3 輸入參數驗證 (4項) | Claude |
| 2024-12-04 | 完成 1.2 JSON 解析加上 try-except (14項) | Claude |
