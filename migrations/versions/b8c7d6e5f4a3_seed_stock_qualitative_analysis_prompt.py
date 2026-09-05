"""seed_stock_qualitative_analysis_prompt

Revision ID: b8c7d6e5f4a3
Revises: a9b8c7d6e5f4
Create Date: 2026-06-27 00:00:00.000000

"""
from alembic import op
from sqlalchemy import text

revision = 'b8c7d6e5f4a3'
down_revision = 'a9b8c7d6e5f4'
branch_labels = None
depends_on = None

PROMPT_CONTENT = """\
你是一位台灣股市分析師。請根據以下資料，對 {{company_name}}（{{stock_id}}）進行近況質化分析。

【近期法說會摘要】
{{earnings_call_summaries}}

【近期相關新聞標題】
{{news_titles}}

請以 JSON 格式回覆，格式如下：
{
  "signal": "買進 / 觀望 / 注意",
  "summary": "一段100字以內的近況摘要",
  "positives": ["正面因素1", "正面因素2"],
  "risks": ["風險因素1", "風險因素2"],
  "data_freshness": "最新資料來源與日期"
}

只輸出 JSON，不要有其他說明文字。\
"""


def upgrade():
    conn = op.get_bind()

    # Find the first active Claude API key
    api_key_row = conn.execute(
        text("SELECT id FROM ai_api_key WHERE provider = 'claude' AND is_active = 1 LIMIT 1")
    ).fetchone()
    api_key_id = api_key_row[0] if api_key_row else None

    existing = conn.execute(
        text("SELECT id FROM ai_prompt WHERE name = 'stock_qualitative_analysis' LIMIT 1")
    ).fetchone()

    if not existing:
        conn.execute(
            text("""
                INSERT INTO ai_prompt
                    (name, provider, content, is_active, description, api_key_id,
                     schedule_enabled, created_by, created_at)
                VALUES
                    ('stock_qualitative_analysis', 'claude', :content, 1,
                     '股票近況質化分析：根據法說會摘要與新聞標題產生買進/觀望/注意信號',
                     :api_key_id, 0, 'migration', NOW())
            """),
            {'content': PROMPT_CONTENT, 'api_key_id': api_key_id},
        )


def downgrade():
    conn = op.get_bind()
    conn.execute(
        text("DELETE FROM ai_prompt WHERE name = 'stock_qualitative_analysis'")
    )
