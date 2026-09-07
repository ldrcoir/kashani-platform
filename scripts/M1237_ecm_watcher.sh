#!/bin/bash
# Watcher برای جستجوی ECM
# هر 30 ثانیه چک می‌کنه و اگه ECM مرده باشه دوباره شروع می‌کنه

WORKDIR=/home/z/my-project/A136030_ECM_M1237
PID_FILE=$WORKDIR/ecm_search.pid
SCRIPT=/home/z/my-project/scripts/M1237_ecm_search.sh

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
        echo "[$TS] شروع/راه‌اندازی مجدد جستجوی ECM" >> $WORKDIR/watcher.log
        cd /home/z/my-project
        setsid bash $SCRIPT > $WORKDIR/stdout.log 2>&1 < /dev/null &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        disown $NEW_PID 2>/dev/null
        echo "[$TS] PID جدید: $NEW_PID" >> $WORKDIR/watcher.log
    fi
    
    sleep 30
done
