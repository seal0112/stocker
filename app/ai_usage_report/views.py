from datetime import datetime, date
from flask import request, jsonify
from sqlalchemy import func

from . import ai_usage_report
from app.decorators.auth import admin_required
from app.ai_report.models import AiReport

# 功能對應中文名稱（未來新增功能在此擴充）
FEATURE_LABELS = {
    'earnings_call': '法說會摘要',
    'news': '新聞摘要',
}


def _parse_date(value, fallback):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date() if value else fallback
    except ValueError:
        return fallback


def _build_sources(date_from, date_to):
    """回傳各來源的原始資料，格式統一供後續彙總使用。"""
    dt_from = datetime.combine(date_from, datetime.min.time())
    dt_to = datetime.combine(date_to, datetime.max.time())

    base = AiReport.query.filter(
        AiReport.processing_status == 'completed',
        AiReport.created_at >= dt_from,
        AiReport.created_at <= dt_to,
    )

    # by_model
    by_model = base.with_entities(
        AiReport.model_name,
        func.sum(AiReport.input_tokens).label('input_tokens'),
        func.sum(AiReport.output_tokens).label('output_tokens'),
        func.sum(AiReport.total_tokens).label('total_tokens'),
        func.sum(AiReport.cost_usd).label('cost_usd'),
        func.sum(AiReport.cost_twd).label('cost_twd'),
        func.count(AiReport.id).label('count'),
    ).group_by(AiReport.model_name).all()

    # daily（每日 × model）
    daily = base.with_entities(
        func.date(AiReport.created_at).label('date'),
        AiReport.model_name,
        func.sum(AiReport.cost_twd).label('cost_twd'),
        func.sum(AiReport.cost_usd).label('cost_usd'),
        func.count(AiReport.id).label('count'),
    ).group_by(
        func.date(AiReport.created_at),
        AiReport.model_name,
    ).order_by(func.date(AiReport.created_at)).all()

    return by_model, daily


@ai_usage_report.route('', methods=['GET'])
@admin_required
def get_usage_report():
    today = date.today()
    date_from = _parse_date(request.args.get('date_from'), date(today.year, today.month, 1))
    date_to = _parse_date(request.args.get('date_to'), today)

    by_model_rows, daily_rows = _build_sources(date_from, date_to)

    # by_feature：目前只有法說會摘要，未來可新增更多來源彙總
    feature_label = FEATURE_LABELS['earnings_call']
    by_feature = [{
        'feature': feature_label,
        'input_tokens': int(sum(r.input_tokens or 0 for r in by_model_rows)),
        'output_tokens': int(sum(r.output_tokens or 0 for r in by_model_rows)),
        'total_tokens': int(sum(r.total_tokens or 0 for r in by_model_rows)),
        'cost_usd': float(sum(r.cost_usd or 0 for r in by_model_rows)),
        'cost_twd': float(sum(r.cost_twd or 0 for r in by_model_rows)),
        'count': int(sum(r.count for r in by_model_rows)),
    }]

    by_model = [{
        'model_name': r.model_name or '未知',
        'input_tokens': int(r.input_tokens or 0),
        'output_tokens': int(r.output_tokens or 0),
        'total_tokens': int(r.total_tokens or 0),
        'cost_usd': float(r.cost_usd or 0),
        'cost_twd': float(r.cost_twd or 0),
        'count': int(r.count),
    } for r in by_model_rows]

    daily = [{
        'date': str(r.date),
        'feature': feature_label,
        'model_name': r.model_name or '未知',
        'cost_twd': float(r.cost_twd or 0),
        'cost_usd': float(r.cost_usd or 0),
        'count': int(r.count),
    } for r in daily_rows]

    return jsonify({
        'date_from': str(date_from),
        'date_to': str(date_to),
        'by_feature': by_feature,
        'by_model': by_model,
        'daily': daily,
    }), 200
