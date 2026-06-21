"""add_ai_report_migrate_earnings_call_summary

Revision ID: ab67d43d772d
Revises: e3f4a5b6c7d8
Create Date: 2026-06-21 14:36:14.782292

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = 'ab67d43d772d'
down_revision = 'e3f4a5b6c7d8'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create ai_report table
    op.create_table(
        'ai_report',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.Enum('earnings_call', 'news', name='ai_report_type_enum'), nullable=False),
        sa.Column('subject', sa.String(50), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('prompt_name', sa.String(100), nullable=False),
        sa.Column('ref_id', sa.Integer(), nullable=True),
        sa.Column('processing_status',
                  sa.Enum('pending', 'processing', 'completed', 'failed', name='ai_report_status_enum'),
                  nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('key_points', mysql.JSON(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('raw_ai_response', sa.Text(), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=True),
        sa.Column('cost_twd', sa.Numeric(10, 2), nullable=True),
        sa.Column('model_name', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('report_type', 'subject', 'period_start', 'period_end',
                            name='uix_ai_report_type_subject_period'),
    )
    op.create_index('ix_ai_report_report_type', 'ai_report', ['report_type'])
    op.create_index('ix_ai_report_subject', 'ai_report', ['subject'])
    op.create_index('ix_ai_report_period_start', 'ai_report', ['period_start'])

    # 2. Migrate data from earnings_call_summary -> ai_report
    op.execute("""
        INSERT INTO ai_report (
            report_type, subject, period_start, period_end,
            prompt_name, ref_id, processing_status, error_message,
            summary, key_points, score, sentiment,
            raw_ai_response, input_tokens, output_tokens, total_tokens,
            cost_usd, cost_twd, model_name, created_at, updated_at
        )
        SELECT
            'earnings_call',
            es.stock_id,
            ec.meeting_date,
            ec.meeting_date,
            'earnings-call-summary',
            es.earnings_call_id,
            es.processing_status,
            es.error_message,
            es.reasoning,
            JSON_OBJECT(
                'impact_duration', es.impact_duration,
                'source_reliability', es.source_reliability,
                'capex', es.capex,
                'capex_industry', es.capex_industry,
                'outlook', es.outlook,
                'concerns_and_risks', es.concerns_and_risks,
                'news_contributions', es.news_contributions,
                'source_feed_ids', es.source_feed_ids
            ),
            es.score,
            es.sentiment,
            es.raw_ai_response,
            es.input_tokens,
            es.output_tokens,
            es.total_tokens,
            es.cost_usd,
            es.cost_twd,
            es.model_name,
            es.created_at,
            es.updated_at
        FROM earnings_call_summary es
        JOIN earnings_call ec ON es.earnings_call_id = ec.id
    """)

    # 3. Add schedule columns to ai_prompt
    op.add_column('ai_prompt', sa.Column('report_source', sa.String(20), nullable=True))
    op.add_column('ai_prompt', sa.Column('schedule_enabled', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('ai_prompt', sa.Column('schedule_frequency',
                  sa.Enum('weekly', 'monthly', name='ai_prompt_schedule_freq_enum'), nullable=True))
    op.add_column('ai_prompt', sa.Column('schedule_day', sa.Integer(), nullable=True))
    op.add_column('ai_prompt', sa.Column('schedule_hour', sa.Integer(), nullable=True))
    op.add_column('ai_prompt', sa.Column('schedule_days_back', sa.Integer(), nullable=True))

    # 4. Drop old earnings_call_summary table
    op.drop_table('earnings_call_summary')

    # 5. Drop the old processing_status_enum (MySQL handles enums per column, no action needed)


def downgrade():
    # 1. Recreate earnings_call_summary table
    op.create_table(
        'earnings_call_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('earnings_call_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.String(6), nullable=False),
        sa.Column('capex', sa.Text(), nullable=True),
        sa.Column('capex_industry', sa.Text(), nullable=True),
        sa.Column('outlook', sa.Text(), nullable=True),
        sa.Column('concerns_and_risks', sa.Text(), nullable=True),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('sentiment', sa.String(20), nullable=True),
        sa.Column('impact_duration', sa.String(20), nullable=True),
        sa.Column('source_reliability', sa.String(20), nullable=True),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('news_contributions', mysql.JSON(), nullable=True),
        sa.Column('source_feed_ids', mysql.JSON(), nullable=True),
        sa.Column('raw_ai_response', sa.Text(), nullable=True),
        sa.Column('processing_status',
                  sa.Enum('pending', 'processing', 'completed', 'failed', name='processing_status_enum'),
                  nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Numeric(10, 6), nullable=True),
        sa.Column('cost_twd', sa.Numeric(10, 2), nullable=True),
        sa.Column('model_name', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['earnings_call_id'], ['earnings_call.id']),
        sa.ForeignKeyConstraint(['stock_id'], ['basic_information.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('earnings_call_id'),
    )

    # 2. Restore data from ai_report
    op.execute("""
        INSERT INTO earnings_call_summary (
            earnings_call_id, stock_id, processing_status, error_message,
            reasoning, score, sentiment,
            impact_duration, source_reliability, capex, capex_industry,
            outlook, concerns_and_risks, news_contributions, source_feed_ids,
            raw_ai_response, input_tokens, output_tokens, total_tokens,
            cost_usd, cost_twd, model_name, created_at, updated_at
        )
        SELECT
            ref_id,
            subject,
            processing_status,
            error_message,
            summary,
            score,
            sentiment,
            JSON_UNQUOTE(JSON_EXTRACT(key_points, '$.impact_duration')),
            JSON_UNQUOTE(JSON_EXTRACT(key_points, '$.source_reliability')),
            JSON_UNQUOTE(JSON_EXTRACT(key_points, '$.capex')),
            JSON_UNQUOTE(JSON_EXTRACT(key_points, '$.capex_industry')),
            JSON_UNQUOTE(JSON_EXTRACT(key_points, '$.outlook')),
            JSON_UNQUOTE(JSON_EXTRACT(key_points, '$.concerns_and_risks')),
            JSON_EXTRACT(key_points, '$.news_contributions'),
            JSON_EXTRACT(key_points, '$.source_feed_ids'),
            raw_ai_response,
            input_tokens, output_tokens, total_tokens,
            cost_usd, cost_twd, model_name, created_at, updated_at
        FROM ai_report
        WHERE report_type = 'earnings_call'
    """)

    # 3. Remove schedule columns from ai_prompt
    op.drop_column('ai_prompt', 'schedule_days_back')
    op.drop_column('ai_prompt', 'schedule_hour')
    op.drop_column('ai_prompt', 'schedule_day')
    op.drop_column('ai_prompt', 'schedule_frequency')
    op.drop_column('ai_prompt', 'schedule_enabled')
    op.drop_column('ai_prompt', 'report_source')

    # 4. Drop ai_report table
    op.drop_index('ix_ai_report_period_start', 'ai_report')
    op.drop_index('ix_ai_report_subject', 'ai_report')
    op.drop_index('ix_ai_report_report_type', 'ai_report')
    op.drop_table('ai_report')
