#!/bin/bash
# Watcher برای استراتژی جدید
WORKDIR=/home/z/my-project/A136030_M1237_strategy2
PID_FILE=$WORKDIR/strategy.pid

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
        echo "[$TS] شروع استراتژی جدید" >> $WORKDIR/watcher.log
        cd /home/z/my-project
        nohup /usr/bin/python3 -u scripts/M1237_strategy2.py >> $WORKDIR/stdout.log 2>&1 < /dev/null &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        disown $NEW_PID 2>/dev/null
        echo "[$TS] PID: $NEW_PID" >> $WORKDIR/watcher.log
    fi
    
    sleep 60
done
