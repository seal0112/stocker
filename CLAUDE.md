# Stocker

台灣股票分析平台 - Flask REST API 後端，爬取並儲存台灣上市櫃公司財務資料。

## Commands

```bash
# 開發伺服器
python stocker.py
gunicorn --reload wsgi:app

# 測試
pytest tests/ -v
pytest tests/api/ -v              # API 測試
pytest tests/models/ -v           # Model 測試
pytest tests/ --cov=app           # 含覆蓋率

# 資料庫 migrations
flask db migrate -m "message"
flask db upgrade

# Celery worker
celery -A celery_worker.celery worker --loglevel=info
```

## Architecture

- `app/` - Flask 應用主目錄
  - `database_setup.py` - 財務資料 models (BasicInformation, BalanceSheet, IncomeSheet 等)
  - `models/` - 使用者/內容 models (User, Role, Feed 等)
  - `services/` - 業務邏輯層
  - `<domain>/` - API 模組 (basic_information, income_sheet, balance_sheet 等)
- `tests/` - pytest 測試套件，fixtures 在 `tests/fixtures/`
- `migrations/` - Alembic 資料庫 migrations

## Key Files

- `stocker.py` - Flask app 進入點
- `config.py` - 環境設定 (Development/Testing/Production)
- `celery_worker.py` - Celery worker 進入點

## Testing

- Framework: pytest with modular fixtures
- 測試資料庫自動建立與清理
- Fixtures 按領域分模組 (`tests/fixtures/`)
- 命名慣例: `test_*.py`, `Test*` class, `test_*` method

## Gotchas

- **資料庫欄位使用中文名稱** - 如 `公司名稱`, `資產總計`，需注意 charset
- **Models 分散兩處** - 財務資料在 `database_setup.py`，使用者/內容在 `models/`
- **API 版本混用** - v0 (舊) 和 v1 (新) 並存
- **Permission sync** - App 啟動時同步權限，若 DB 未就緒會靜默失敗

## Work Plans

詳細待辦事項見 [docs/API_IMPROVEMENT_CHECKLIST.md](docs/API_IMPROVEMENT_CHECKLIST.md)

當前進度：
- [ ] Phase 1: 安全性修復 (8%) - 加上 `@jwt_required()` 認證
- [ ] Phase 3: 完成 Stub 實作
- [ ] Phase 5: AI 功能 - 法說會新聞摘要
- [ ] Phase 6: Observability - Prometheus/Loki/Grafana
- [ ] Phase 7: 股票篩選器視覺化
- [ ] 持續擴充 API 單元測試
