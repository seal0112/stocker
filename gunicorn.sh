#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate

PIDFILE="/tmp/gunicorn_stocker.pid"
TIMEOUT=30

if [ -f "$PIDFILE" ]; then
    OLD_PID=$(cat "$PIDFILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Upgrading master process (PID: $OLD_PID)..."

        # USR2: 啟動新 master + 新 workers，舊的繼續運行
        kill -USR2 "$OLD_PID"

        # 等待新 master 啟動
        for i in $(seq 1 $TIMEOUT); do
            if [ -f "$PIDFILE.2" ] || [ -f "$PIDFILE" ]; then
                NEW_PID=$(cat "$PIDFILE" 2>/dev/null)
                if [ "$NEW_PID" != "$OLD_PID" ] && kill -0 "$NEW_PID" 2>/dev/null; then
                    echo "New master started (PID: $NEW_PID)"
                    # 優雅關閉舊 master
                    kill -QUIT "$OLD_PID" 2>/dev/null
                    echo "Old master shutting down gracefully..."
                    exit 0
                fi
            fi
            sleep 1
        done

        echo "Upgrade failed, falling back to restart..."
        kill -TERM "$OLD_PID"
        sleep 2
    fi
fi

# 沒有現有服務或升級失敗，直接啟動
echo "Starting new service..."
gunicorn wsgi:app

sleep 2
if [ -f "$PIDFILE" ]; then
    NEW_PID=$(cat "$PIDFILE")
    echo "Service started (PID: $NEW_PID)"
fi

# nohup celery -A celery_worker.celery worker &
exit 0
