from datetime import datetime

from flask import request, jsonify
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from app import db
from app.models import AnnouncementIncomeSheetAnalysis, Feed
from . import announcement_income_sheet_analysis
from .serializer import AnnouncementIncomeSheetAnalysisSchema


class AnnouncementIncomeSheetAnalysisListApi(MethodView):

    @jwt_required()
    def get(self):
        """
        GET API for AnnouncementIncomeSheetAnalysis list
        Query parameters:
        - date: filter by update_date (format: YYYY-MM-DD)
        - start_date: filter by update_date >= start_date (format: YYYY-MM-DD)
        - end_date: filter by update_date <= end_date (format: YYYY-MM-DD)
        """
        query = AnnouncementIncomeSheetAnalysis.query

        # Filter by specific date
        date_str = request.args.get('date', None)
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                query = query.filter(AnnouncementIncomeSheetAnalysis.update_date == date_obj)
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        # Filter by date range
        start_date_str = request.args.get('start_date', None)
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                query = query.filter(AnnouncementIncomeSheetAnalysis.update_date >= start_date)
            except ValueError:
                return jsonify({"error": "Invalid start_date format. Use YYYY-MM-DD"}), 400

        end_date_str = request.args.get('end_date', None)
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                query = query.filter(AnnouncementIncomeSheetAnalysis.update_date <= end_date)
            except ValueError:
                return jsonify({"error": "Invalid end_date format. Use YYYY-MM-DD"}), 400

        # Order by update_date descending
        results = query.order_by(AnnouncementIncomeSheetAnalysis.update_date.desc()).all()

        return jsonify(AnnouncementIncomeSheetAnalysisSchema(many=True).dump(results))


class AnnouncementIncomeSheetAnalysisTriggerApi(MethodView):

    @jwt_required()
    def post(self):
        date_str = request.args.get('date') or (request.get_json(silent=True) or {}).get('date')
        if not date_str:
            return jsonify({"error": "date is required"}), 400
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        feeds = Feed.query.filter(
            db.func.date(Feed.releaseTime) == date_obj,
            Feed.feed_kind == 'announcement'
        ).all()

        triggered = 0
        for feed in feeds:
            try:
                analysis = feed.create_default_announcement_income_sheet_analysis()
                db.session.flush()
                analysis.analysis_announcement_income_sheet()
                triggered += 1
            except Exception:
                db.session.rollback()
                continue

        db.session.commit()
        return jsonify({"triggered": triggered, "date": date_str})


announcement_income_sheet_analysis.add_url_rule('',
    view_func=AnnouncementIncomeSheetAnalysisListApi.as_view('AnnouncementIncomeSheetAnalysisListApi'),
    methods=['GET'])

announcement_income_sheet_analysis.add_url_rule('/trigger',
    view_func=AnnouncementIncomeSheetAnalysisTriggerApi.as_view('AnnouncementIncomeSheetAnalysisTriggerApi'),
    methods=['POST'])
