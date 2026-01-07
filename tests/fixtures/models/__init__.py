"""
Model fixtures package.

This package organizes model fixtures by individual model files for better maintainability.
Each model has its own fixture file in this directory.

Available fixture modules:
=========================

Base Models:
- basic_information: BasicInformation model fixtures
  - sample_basic_info (TSMC 2330)
  - sample_basic_info_2 (Hon Hai 2317)
  - sample_basic_info_list (multiple stocks)

- user: User and Role model fixtures
  - admin_role, moderator_role, user_role
  - admin_user, moderator_user, regular_user, user_no_roles

- permission: Permission model fixtures
  - read_permission, write_permission, delete_permission
  - admin_permission, stock_read_permission, stock_write_permission
  - role_with_permissions

Stock-Related Models:
- stock: All stock-related model fixtures
  - DailyInformation: sample_daily_info, sample_daily_info_2
  - BalanceSheet: sample_balance_sheet, sample_balance_sheet_list
  - IncomeSheet: sample_income_sheet, sample_income_sheet_list
  - CashFlow: sample_cash_flow
  - MonthRevenue: sample_month_revenue, sample_month_revenue_list
  - MonthlyValuation: sample_monthly_valuation, sample_monthly_valuation_list
  - StockCommodity: sample_stock_commodity, sample_stock_commodity_no_derivatives
  - DataUpdateDate: sample_data_update_date
  - StockSearchCounts: sample_stock_search_counts
  - EarningsCall: sample_earnings_call, sample_earnings_call_list
  - RecommendedStock: sample_recommended_stock, sample_recommended_stock_list

Feed-Related Models:
- feed: Feed model fixtures
  - sample_feed

- feed_tag: FeedTag and FeedFeedTag model fixtures
  - sample_feed_tag_earnings, sample_feed_tag_dividend
  - sample_feed_tag_announcement, sample_feed_tag_news
  - sample_feed_with_tags

- announcement_income_sheet_analysis: AnnouncementIncomeSheetAnalysis fixtures
  - sample_announcement_income_sheet_analysis

User-Related Models:
- api_token: ApiToken model fixtures
  - sample_api_token, sample_api_token_readonly
  - expired_api_token, admin_api_token

- follow_stock: Follow_Stock model fixtures
  - sample_follow_stock_long, sample_follow_stock_short
  - sample_follow_stock_deleted, sample_follow_stock_list
  - admin_follow_stock

- push_notification: PushNotification model fixtures
  - sample_push_notification_enabled
  - sample_push_notification_disabled
  - sample_push_notification_partial

Fixture Dependency Order:
========================
1. BasicInformation (base)
2. User, Role, Permission (base)
3. DailyInformation, BalanceSheet, etc. (depends on BasicInformation)
4. Feed (depends on BasicInformation)
5. FeedTag (base)
6. FeedFeedTag (depends on Feed, FeedTag)
7. ApiToken (depends on User)
8. Follow_Stock (depends on User, BasicInformation)
9. PushNotification (depends on User)
10. AnnouncementIncomeSheetAnalysis (depends on Feed, BasicInformation)
"""
