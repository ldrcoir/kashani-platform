#!/bin/bash
# Watcher برای جستجوی k های بزرگ با FactorDB
# هر ۲۰ ثانیه چک می‌کند و اگر اسکریپت مرده باشد دوباره شروع می‌کند

WORKDIR=/home/z/my-project/A136030_M1237_ksearch
PID_FILE=$WORKDIR/search.pid
SCRIPT=/home/z/my-project/scripts/M1237_ksearch_factordb.py

# شروع از k = 10^14، هر بار 10^6 تا
K_CURRENT=100000000000000
K_STEP=1000000

while true; do
    NEED_START=1
    
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
            NEED_START=0
        fi
    fi
    
    if [ "$NEED_START" = "1" ]; then
        # بارگذاری k_done از state
        if [ -f "$WORKDIR/state.txt" ]; then
            K_CURRENT=$(cat "$WORKDIR/state.txt")
        fi
        
        K_END=$((K_CURRENT + K_STEP))
        
        TS=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[$TS] شروع جستجو: k=[${K_CURRENT}, ${K_END}]" >> $WORKDIR/watcher.log
        
        cd /home/z/my-project
        nohup python3 -u $SCRIPT $K_CURRENT $K_END >> $WORKDIR/stdout.log 2>&1 < /dev/null &
        NEW_PID=$!
        echo $NEW_PID > "$PID_FILE"
        disown $NEW_PID 2>/dev/null
        
        # به‌روزرسانی state برای اجرای بعدی
        echo $K_END > "$WORKDIR/state.txt"
        
        echo "[$TS] PID جدید: $NEW_PID" >> $WORKDIR/watcher.log
    fi
    
    sleep 20
done
