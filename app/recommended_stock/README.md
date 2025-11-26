# Recommended Stock API

推薦股票 API 模組，提供股票推薦的查詢、建立、刪除功能。

## 📁 模組結構

```
app/recommended_stock/
├── __init__.py          # Blueprint 定義
├── serializer.py        # Marshmallow schemas
├── services.py          # 業務邏輯
├── view.py             # API endpoints
└── README.md           # 本文檔
```

## 🔗 API Endpoints

Base URL: `/api/v0/recommended_stock`

### 1. 取得推薦股票列表

**GET** `/api/v0/recommended_stock`

#### Query Parameters
- `date` (optional): 日期 (YYYY-MM-DD)，預設為今天
- `filter_model` (optional): 篩選模型名稱
- `limit` (optional): 限制結果數量
- `detail` (optional): 是否回傳詳細資訊 (true/false)，預設 false

#### Response (Simple)
```json
[
  {
    "id": 1,
    "stock_id": "2330",
    "update_date": "2025-01-15",
    "filter_model": "月營收近一年次高",
    "stock_name": "台積電"
  }
]
```

#### Response (Detail)
```json
[
  {
    "id": 1,
    "stock_id": "2330",
    "update_date": "2025-01-15",
    "filter_model": "月營收近一年次高",
    "stock_info": {
      "stock_id": "2330",
      "name": "台灣積體電路製造股份有限公司",
      "short_name": "台積電",
      "industry": "半導體",
      "exchange_type": "sii",
      "daily": {
        "close_price": 550.0,
        "change": 10.0,
        "eps": 28.5,
        "pe_ratio": 19.3,
        "dividend_yield": 2.8
      }
    }
  }
]
```

#### Examples
```bash
# 取得今天的推薦
curl http://localhost:5000/api/v0/recommended_stock

# 取得特定日期的推薦
curl http://localhost:5000/api/v0/recommended_stock?date=2025-01-15

# 取得特定篩選模型的推薦
curl http://localhost:5000/api/v0/recommended_stock?filter_model=月營收近一年次高

# 取得詳細資訊
curl http://localhost:5000/api/v0/recommended_stock?detail=true

# 限制結果數量
curl http://localhost:5000/api/v0/recommended_stock?limit=10
```

---

### 2. 建立推薦股票

**POST** `/api/v0/recommended_stock`

#### Request Body
```json
{
  "stock_id": "2330",
  "filter_model": "月營收近一年次高",
  "update_date": "2025-01-15"  // optional, default: today
}
```

#### Response (201 Created)
```json
{
  "id": 1,
  "stock_id": "2330",
  "update_date": "2025-01-15",
  "filter_model": "月營收近一年次高",
  "stock_name": "台積電"
}
```

#### Example
```bash
curl -X POST http://localhost:5000/api/v0/recommended_stock \
  -H "Content-Type: application/json" \
  -d '{
    "stock_id": "2330",
    "filter_model": "月營收近一年次高"
  }'
```

---

### 3. 取得單一推薦詳情

**GET** `/api/v0/recommended_stock/{id}`

#### Response (200 OK)
```json
{
  "id": 1,
  "stock_id": "2330",
  "update_date": "2025-01-15",
  "filter_model": "月營收近一年次高",
  "stock_info": { ... }
}
```

#### Example
```bash
curl http://localhost:5000/api/v0/recommended_stock/1
```

---

### 4. 刪除推薦股票

**DELETE** `/api/v0/recommended_stock/{id}`

#### Response (200 OK)
```json
{
  "message": "Recommendation deleted successfully"
}
```

#### Example
```bash
curl -X DELETE http://localhost:5000/api/v0/recommended_stock/1
```

---

### 5. 取得特定股票的推薦歷史

**GET** `/api/v0/recommended_stock/stock/{stock_id}`

#### Query Parameters
- `days` (optional): 回溯天數，預設 30

#### Response
```json
[
  {
    "id": 1,
    "stock_id": "2330",
    "update_date": "2025-01-15",
    "filter_model": "月營收近一年次高",
    "stock_name": "台積電"
  },
  {
    "id": 2,
    "stock_id": "2330",
    "update_date": "2025-01-10",
    "filter_model": "本益比低於平均",
    "stock_name": "台積電"
  }
]
```

#### Example
```bash
# 取得台積電過去 30 天的推薦記錄
curl http://localhost:5000/api/v0/recommended_stock/stock/2330

# 取得過去 60 天的記錄
curl http://localhost:5000/api/v0/recommended_stock/stock/2330?days=60
```

---

### 6. 取得統計資訊

**GET** `/api/v0/recommended_stock/statistics`

#### Query Parameters
- `date` (optional): 日期 (YYYY-MM-DD)，預設為今天

#### Response
```json
{
  "date": "2025-01-15",
  "total_recommendations": 25,
  "by_filter_model": {
    "月營收近一年次高": 10,
    "本益比低於平均": 8,
    "殖利率高於5%": 7
  }
}
```

#### Example
```bash
# 取得今天的統計
curl http://localhost:5000/api/v0/recommended_stock/statistics

# 取得特定日期的統計
curl http://localhost:5000/api/v0/recommended_stock/statistics?date=2025-01-15
```

---

### 7. 取得可用的篩選模型

**GET** `/api/v0/recommended_stock/filter-models`

#### Response
```json
{
  "filter_models": [
    "月營收近一年次高",
    "本益比低於平均",
    "殖利率高於5%"
  ]
}
```

#### Example
```bash
curl http://localhost:5000/api/v0/recommended_stock/filter-models
```

---

## 📊 Schema 說明

### RecommendedStockSchema (簡單版)
| 欄位 | 類型 | 說明 |
|------|------|------|
| id | Integer | 推薦記錄 ID |
| stock_id | String | 股票代碼 |
| update_date | Date | 推薦日期 |
| filter_model | String | 篩選模型名稱 |
| stock_name | String | 股票簡稱（自動查詢） |

### RecommendedStockDetailSchema (詳細版)
包含上述所有欄位，加上：
| 欄位 | 類型 | 說明 |
|------|------|------|
| stock_info | Object | 完整股票資訊 |
| stock_info.name | String | 公司全名 |
| stock_info.short_name | String | 公司簡稱 |
| stock_info.industry | String | 產業類別 |
| stock_info.exchange_type | String | 交易所類型 |
| stock_info.daily | Object | 每日資訊（如果有） |
| stock_info.daily.close_price | Float | 收盤價 |
| stock_info.daily.change | Float | 漲跌 |
| stock_info.daily.eps | Float | 近四季 EPS |
| stock_info.daily.pe_ratio | Float | 本益比 |
| stock_info.daily.dividend_yield | Float | 殖利率 |

---

## 🔧 Service 層方法

### RecommendedStockService

#### get_recommended_stocks(date, filter_model, limit)
取得推薦股票列表

#### get_recommended_stock_by_id(stock_id)
取得單一推薦詳情

#### get_stocks_by_stock_id(stock_id, days)
取得特定股票的推薦歷史

#### get_available_filter_models()
取得所有可用的篩選模型

#### get_statistics(date)
取得統計資訊

#### create_recommendation(data)
建立新推薦

#### delete_recommendation(recommendation_id)
刪除推薦

---

## 🧪 測試

測試文件位於：`tests/api/test_recommended_stock_api.py`

### 執行測試
```bash
# 執行所有 API 測試
pytest tests/api/test_recommended_stock_api.py -v

# 執行特定測試
pytest tests/api/test_recommended_stock_api.py::TestRecommendedStockAPI::test_get_recommended_stocks_with_data -v
```

### 測試覆蓋
- ✅ GET 列表（含各種篩選）
- ✅ GET 詳情
- ✅ POST 建立
- ✅ DELETE 刪除
- ✅ GET 股票歷史
- ✅ GET 統計資訊
- ✅ GET 篩選模型列表
- ✅ 錯誤處理（404, 400, 500）

---

## 💡 使用範例

### Python
```python
import requests

# 取得今天的推薦
response = requests.get('http://localhost:5000/api/v0/recommended_stock')
recommendations = response.json()

# 建立新推薦
payload = {
    'stock_id': '2330',
    'filter_model': '月營收近一年次高'
}
response = requests.post(
    'http://localhost:5000/api/v0/recommended_stock',
    json=payload
)
new_rec = response.json()

# 取得台積電的推薦歷史
response = requests.get('http://localhost:5000/api/v0/recommended_stock/stock/2330')
history = response.json()
```

### JavaScript
```javascript
// 取得推薦列表
fetch('/api/v0/recommended_stock?detail=true')
  .then(res => res.json())
  .then(data => console.log(data));

// 建立推薦
fetch('/api/v0/recommended_stock', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    stock_id: '2330',
    filter_model: '月營收近一年次高'
  })
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 🚀 整合建議

### 與 StockScreenerManager 整合
```python
from app.utils.stock_screener import StockScreenerManager
from app.recommended_stock.services import RecommendedStockService

# 執行篩選並儲存
screener = StockScreenerManager("月營收近一年次高")
result = screener.run_and_save()

# API 即可查詢剛儲存的推薦
service = RecommendedStockService()
today_recs = service.get_recommended_stocks()
```

### 定期任務
```python
# 使用 Celery 定期執行股票篩選並儲存推薦
@celery.task
def daily_stock_screening():
    screener = StockScreenerManager("月營收近一年次高")
    result = screener.run_and_save()
    return result
```
