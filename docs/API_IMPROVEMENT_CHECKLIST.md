# API Improvement Checklist

> 此文件記錄所有需要改善的 API 問題，請逐一修復並勾選完成項目。

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

- [x] [app/earnings_call/views.py:36-39](../app/earnings_call/views.py#L36)
- [x] [app/recommended_stock/view.py:62-66](../app/recommended_stock/view.py#L62)
- [x] [app/monthly_valuation/view.py](../app/monthly_valuation/view.py) - 檢查所有 except block

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

## 進度統計

| Phase | 總項目 | 已完成 | 完成率 |
|-------|--------|--------|--------|
| Phase 1: 安全性 | 23 | 0 | 0% |
| Phase 2: 一致性 | 18 | 0 | 0% |
| Phase 3: 品質 | 7 | 7 | 100% |
| Phase 4: 功能 | 14 | 0 | 0% |
| **總計** | **62** | **17** | **27%** |

---

## 修改記錄

| 日期 | 修改內容 | 修改者 |
|------|----------|--------|
| 2024-12-09 | 完成 3.3 統一使用 Marshmallow Serializer (4項) | Claude |
| 2024-12-09 | 完成 2.1 統一回應格式 (5項) | Claude |
| 2024-12-09 | 完成 2.2 統一 404 Not Found 處理 (3項) | Claude |
| 2024-12-08 | 完成 2.4 統一錯誤訊息語言 (2項) | Claude |
| 2024-12-08 | 完成 3.2 加入 db.session.rollback() (3項) | Claude |
| 2024-12-04 | 完成 1.3 輸入參數驗證 (4項) | Claude |
| 2024-12-04 | 完成 1.2 JSON 解析加上 try-except (14項) | Claude |
