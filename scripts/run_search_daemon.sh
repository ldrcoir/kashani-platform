#!/bin/bash
# این اسکریپت جستجو را به‌صورت دائمی اجرا می‌کند
# حتی اگر session از بین برود

cd /home/z/my-project

while true; do
    # بررسی اینکه آیا جستجو در حال اجراست
    PID_FILE=A136030_Search_M1237_bg/search.pid
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            # هنوز در حال اجراست، صبر کن
            sleep 30
            continue
        fi
    fi
    
    # شروع دوباره
    echo "[$(date)] شروع جستجو..." >> A136030_Search_M1237_bg/daemon.log
    setsid python3 -u scripts/M1237_bg_search.py >> A136030_Search_M1237_bg/stdout.log 2>&1 < /dev/null &
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    disown $NEW_PID 2>/dev/null
    
    # صبر 60 ثانیه قبل از بررسی
    sleep 60
done
