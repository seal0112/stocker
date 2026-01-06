#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate

PIDFILE="/tmp/gunicorn_stocker.pid"

if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Hot reloading (PID: $OLD_PID)..."
        # SIGHUP: 啟動新 workers，等舊 workers 處理完請求後才關閉
        kill -HUP "$OLD_PID"
        echo "Reload signal sent. New workers starting..."
        exit 0
    fi
fi

# 沒有現有服務，直接啟動
echo "Starting new service..."
gunicorn wsgi:app

sleep 2
if [ -f "$PIDFILE" ]; then
    NEW_PID=$(cat "$PIDFILE")
    echo "Service started (PID: $NEW_PID)"
fi

# nohup celery -A celery_worker.celery worker &
exit 0
