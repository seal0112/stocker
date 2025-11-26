# Test Suite Documentation

## 📁 目錄結構

```
tests/
├── conftest.py                 # 主配置文件（導入其他 fixtures）
├── fixtures/                   # 共用 fixtures（模組化）
│   ├── __init__.py
│   └── models.py              # Model 相關 fixtures
├── models/                     # Model 測試
│   ├── test_basic_information.py
│   ├── test_daily_information.py
│   ├── test_income_sheet.py
│   ├── test_balance_sheet.py
│   ├── test_cash_flow.py
│   ├── test_month_revenue.py
│   ├── test_monthly_valuation.py
│   └── test_recommended_stock.py
└── utils/                      # Utility 測試
    └── test_stock_screener.py

```

## 🔧 Fixtures 架構

### 主配置 (conftest.py)
定義 app 和 session fixtures，並導入其他模組的 fixtures：
```python
pytest_plugins = [
    'tests.fixtures.models',  # Model fixtures
]
```

### App Fixtures (conftest.py)
- `test_app` - 測試環境的 Flask app（session scope）
- `dev_app` - 開發環境的 Flask app（module scope）
- `client` - 測試 client
- `dev_client` - 開發 client
- `db_session` - 資料庫 session with transaction rollback

### Model Fixtures (fixtures/models.py)
- `sample_basic_info` - 單一股票資料（台積電 2330）
- `sample_basic_info_2` - 第二支股票資料（鴻海 2317）
- `sample_basic_info_list` - 多支股票資料列表（2330, 2317, 2454）

### 未來可擴展的 Fixtures
- `fixtures/financial.py` - 財報相關 fixtures
- `fixtures/valuation.py` - 估值相關 fixtures
- `fixtures/api.py` - API 測試相關 fixtures

## 📊 測試覆蓋

### Models (tests/models/)
| 模型 | 測試文件 | 測試數量 | 狀態 |
|------|---------|---------|------|
| BasicInformation | test_basic_information.py | 4 | ✅ |
| DailyInformation | test_daily_information.py | 6 | ✅ |
| IncomeSheet | test_income_sheet.py | 7 | ✅ |
| BalanceSheet | test_balance_sheet.py | 10 | ✅ |
| CashFlow | test_cash_flow.py | 9 | ✅ |
| MonthRevenue | test_month_revenue.py | 4 | ✅ |
| MonthlyValuation | test_monthly_valuation.py | 10 | ✅ |
| RecommendedStock | test_recommended_stock.py | 9 | ✅ |

### Utils (tests/utils/)
| 模組 | 測試文件 | 測試數量 | 狀態 |
|------|---------|---------|------|
| StockScreenerManager | test_stock_screener.py | 18 | ✅ |

**總計：77 個測試案例**

## 🚀 執行測試

### 執行所有測試
```bash
pytest tests/ -v
```

### 執行特定目錄
```bash
# Model 測試
pytest tests/models/ -v

# Utility 測試
pytest tests/utils/ -v
```

### 執行特定文件
```bash
pytest tests/models/test_income_sheet.py -v
```

### 執行特定測試類別
```bash
pytest tests/models/test_income_sheet.py::TestIncomeSheet -v
```

### 執行特定測試方法
```bash
pytest tests/models/test_income_sheet.py::TestIncomeSheet::test_instance_creation -v
```

### 顯示詳細輸出
```bash
pytest tests/ -v -s
```

### 測試覆蓋率報告
```bash
# 命令行輸出
pytest tests/ --cov=app --cov-report=term

# HTML 報告
pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html
```

### 只執行失敗的測試
```bash
pytest tests/ --lf
```

### 並行執行（需要 pytest-xdist）
```bash
pytest tests/ -n auto
```

## 📝 測試命名規範

### 測試文件
- 格式：`test_<module_name>.py`
- 範例：`test_income_sheet.py`

### 測試類別
- 格式：`Test<ClassName>`
- 範例：`TestIncomeSheet`

### 測試方法
- 格式：`test_<what_it_tests>`
- 範例：`test_instance_creation`
- 使用描述性名稱，清楚說明測試目的

### Fixtures
- 使用 `mock_` 前綴表示模擬資料（不寫入資料庫）
- 使用 `sample_` 前綴表示實際資料庫記錄
- 範例：`mock_income_sheet`, `sample_basic_info`

## 🎯 測試風格指南

### 1. 測試結構（AAA Pattern）
```python
def test_example(self, test_app, sample_basic_info):
    """Test description."""
    with test_app.app_context():
        # Arrange - 設置測試資料
        data = create_test_data()

        # Act - 執行要測試的操作
        result = function_under_test(data)

        # Assert - 驗證結果
        assert result == expected_value
```

### 2. 使用 Docstrings
每個測試都應有清楚的 docstring 說明測試目的：
```python
def test_balance_equation(self, mock_balance_sheet):
    """Test that the balance sheet equation holds: Assets = Liabilities + Equity."""
    assert mock_balance_sheet.資產總計 == mock_balance_sheet.負債及權益總計
```

### 3. 測試清理
- 使用 fixtures 的 yield 機制自動清理
- 確保測試之間互不影響
- 刪除測試創建的資料

### 4. 測試獨立性
- 每個測試應該能夠獨立執行
- 不依賴其他測試的執行順序
- 使用 fixtures 提供必要的依賴

## 🔍 測試最佳實踐

### ✅ 好的實踐
```python
# 1. 明確的測試名稱
def test_check_stock_valuation_with_low_eps(self):
    pass

# 2. 使用共用 fixtures
def test_create_recommendation(self, test_app, sample_basic_info):
    pass

# 3. 測試邊界條件
def test_pe_ratio_calculation_with_zero_eps(self):
    pass

# 4. 完整的清理
@pytest.fixture
def sample_data(test_app):
    with test_app.app_context():
        data = create_data()
        db.session.add(data)
        db.session.commit()
        yield data
        db.session.delete(data)
        db.session.commit()
```

### ❌ 避免的做法
```python
# 1. 模糊的測試名稱
def test_1(self):
    pass

# 2. 重複的 fixture 定義
@pytest.fixture
def basic_info(test_app):  # 應該使用 sample_basic_info
    pass

# 3. 沒有清理測試資料
def test_create(self, test_app):
    data = create_data()
    db.session.add(data)
    db.session.commit()
    # 缺少清理！

# 4. 測試之間有依賴關係
def test_step_2(self):  # 依賴 test_step_1 的結果
    pass
```

## 🐛 調試測試

### 使用 pytest 調試工具
```bash
# 進入互動式調試
pytest tests/models/test_income_sheet.py --pdb

# 在第一個錯誤處停止
pytest tests/ -x

# 顯示本地變數
pytest tests/ -l

# 詳細輸出
pytest tests/ -vv
```

### 使用 print 調試
```python
def test_example(self, test_app):
    with test_app.app_context():
        result = function_under_test()
        print(f"Result: {result}")  # 使用 -s flag 顯示
        assert result == expected
```

## 📦 依賴套件

測試所需的 Python 套件：
- `pytest` - 測試框架
- `pytest-cov` - 測試覆蓋率
- `pytest-xdist` - 並行測試（可選）
- `flask` - Web 框架
- `sqlalchemy` - ORM

## 🔄 持續整合

### GitHub Actions 範例
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 📚 參考資源

- [pytest 官方文檔](https://docs.pytest.org/)
- [Flask Testing](https://flask.palletsprojects.com/en/2.0.x/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
