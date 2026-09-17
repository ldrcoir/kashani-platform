#!/bin/bash
# Watcher برای جستجوی π
WORKDIR=/home/z/my-project/A136030_pi_factorization
PID_FILE=$WORKDIR/search.pid

while true; do
    NEED_START=1
    if pgrep -f "pi_innovative_factorization.py" > /dev/null 2>&1; then
        NEED_START=0
    fi
    if [ "$NEED_START" = "1" ]; then
        TS=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TS] شروع جستجوی π" >> $WORKDIR/watcher.log
        cd /home/z/my-project
        nohup /usr/bin/python3 -u scripts/pi_innovative_factorization.py >> $WORKDIR/stdout.log 2>&1 < /dev/null &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        disown $NEW_PID 2>/dev/null
        echo "[$TS] PID: $NEW_PID" >> $WORKDIR/watcher.log
    fi
    sleep 30
done
