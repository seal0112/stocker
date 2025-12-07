"""
Permission constants for the application.

This is the single source of truth for all permissions.
Permissions are synced to the database on app startup.

Naming convention: {MODULE}_{ACTION}
Permission name format: {module}:{action}
"""


class Permissions:
    """All available permissions in the system."""

    # Feed module
    FEED_READ = 'feed:read'
    FEED_WRITE = 'feed:write'
    FEED_DELETE = 'feed:delete'

    # Stock/Basic Information module
    STOCK_VIEW = 'stock:view'
    STOCK_ANALYZE = 'stock:analyze'
    STOCK_EXPORT = 'stock:export'

    # Follow Stock module
    FOLLOW_STOCK_READ = 'follow_stock:read'
    FOLLOW_STOCK_WRITE = 'follow_stock:write'

    # Recommended Stock module
    RECOMMENDED_STOCK_READ = 'recommended_stock:read'
    RECOMMENDED_STOCK_WRITE = 'recommended_stock:write'

    # Financial Reports (income_sheet, balance_sheet, cash_flow)
    FINANCIAL_REPORT_READ = 'financial_report:read'
    FINANCIAL_REPORT_EXPORT = 'financial_report:export'

    # Announcement Income Sheet Analysis
    ANNOUNCEMENT_READ = 'announcement:read'
    ANNOUNCEMENT_ALERT = 'announcement:alert'

    # Earnings Call
    EARNINGS_CALL_READ = 'earnings_call:read'
    EARNINGS_CALL_TRANSCRIPT = 'earnings_call:transcript'

    # Monthly Valuation
    VALUATION_READ = 'valuation:read'
    VALUATION_ADVANCED = 'valuation:advanced'

    # Push Notification
    NOTIFICATION_RECEIVE = 'notification:receive'
    NOTIFICATION_MANAGE = 'notification:manage'

    # User Management (admin only)
    USER_VIEW = 'user:view'
    USER_MANAGE = 'user:manage'

    # Role Management (admin only)
    ROLE_VIEW = 'role:view'
    ROLE_MANAGE = 'role:manage'

    # System Administration
    SYSTEM_ADMIN = 'system:admin'

    # All permissions with metadata: (name, module, description)
    ALL = [
        # Feed
        (FEED_READ, 'feed', '查看動態'),
        (FEED_WRITE, 'feed', '發布動態'),
        (FEED_DELETE, 'feed', '刪除動態'),

        # Stock
        (STOCK_VIEW, 'stock', '查看股票資訊'),
        (STOCK_ANALYZE, 'stock', '股票分析功能'),
        (STOCK_EXPORT, 'stock', '匯出股票資料'),

        # Follow Stock
        (FOLLOW_STOCK_READ, 'follow_stock', '查看追蹤清單'),
        (FOLLOW_STOCK_WRITE, 'follow_stock', '編輯追蹤清單'),

        # Recommended Stock
        (RECOMMENDED_STOCK_READ, 'recommended_stock', '查看推薦股票'),
        (RECOMMENDED_STOCK_WRITE, 'recommended_stock', '編輯推薦股票'),

        # Financial Reports
        (FINANCIAL_REPORT_READ, 'financial_report', '查看財報'),
        (FINANCIAL_REPORT_EXPORT, 'financial_report', '匯出財報'),

        # Announcement
        (ANNOUNCEMENT_READ, 'announcement', '查看公告分析'),
        (ANNOUNCEMENT_ALERT, 'announcement', '公告提醒通知'),

        # Earnings Call
        (EARNINGS_CALL_READ, 'earnings_call', '查看法說會'),
        (EARNINGS_CALL_TRANSCRIPT, 'earnings_call', '法說會逐字稿'),

        # Valuation
        (VALUATION_READ, 'valuation', '查看估值'),
        (VALUATION_ADVANCED, 'valuation', '進階估值功能'),

        # Notification
        (NOTIFICATION_RECEIVE, 'notification', '接收通知'),
        (NOTIFICATION_MANAGE, 'notification', '管理通知設定'),

        # User Management
        (USER_VIEW, 'user', '查看用戶'),
        (USER_MANAGE, 'user', '管理用戶'),

        # Role Management
        (ROLE_VIEW, 'role', '查看角色'),
        (ROLE_MANAGE, 'role', '管理角色'),

        # System
        (SYSTEM_ADMIN, 'system', '系統管理'),
    ]


# Default permissions for each role
DEFAULT_ROLE_PERMISSIONS = {
    'admin': ['*'],  # All permissions (handled specially in code)
    'moderator': [
        Permissions.FEED_READ,
        Permissions.FEED_WRITE,
        Permissions.FEED_DELETE,
        Permissions.STOCK_VIEW,
        Permissions.STOCK_ANALYZE,
        Permissions.FOLLOW_STOCK_READ,
        Permissions.FOLLOW_STOCK_WRITE,
        Permissions.RECOMMENDED_STOCK_READ,
        Permissions.RECOMMENDED_STOCK_WRITE,
        Permissions.FINANCIAL_REPORT_READ,
        Permissions.ANNOUNCEMENT_READ,
        Permissions.EARNINGS_CALL_READ,
        Permissions.VALUATION_READ,
        Permissions.NOTIFICATION_RECEIVE,
        Permissions.NOTIFICATION_MANAGE,
        Permissions.USER_VIEW,
    ],
    'user': [
        Permissions.FEED_READ,
        Permissions.STOCK_VIEW,
        Permissions.FOLLOW_STOCK_READ,
        Permissions.FINANCIAL_REPORT_READ,
        Permissions.ANNOUNCEMENT_READ,
        Permissions.EARNINGS_CALL_READ,
        Permissions.VALUATION_READ,
        Permissions.NOTIFICATION_RECEIVE,
    ],
}
