#!/bin/bash
# Watcher برای جستجوی هوشمند M1237
# هر ۲۰ ثانیه چک می‌کند و اگر جستجو مرده باشد دوباره شروع می‌کند

WORKDIR=/home/z/my-project/A136030_Search_M1237_smart
PID_FILE=$WORKDIR/search.pid

while true; do
    NEED_START=1
    
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
            NEED_START=0
        fi
    fi
    
    if [ "$NEED_START" = "1" ]; then
        TS=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TS] شروع/راه‌اندازی مجدد جستجوی هوشمند" >> $WORKDIR/daemon.log
        cd /home/z/my-project
        nohup python3 -u scripts/M1237_smart_search.py >> $WORKDIR/stdout.log 2>&1 < /dev/null &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        disown $NEW_PID 2>/dev/null
        echo "[$TS] PID جدید: $NEW_PID" >> $WORKDIR/daemon.log
    fi
    
    sleep 20
done
