#!/bin/bash
# لانچر که خودش را daemonize می‌کند
cd /home/z/my-project

# اگر از طریق terminal صدا زده شده، خودش را با nohup دوباره اجرا می‌کند
if [ -t 1 ]; then
    nohup bash "$0" > /dev/null 2>&1 < /dev/null &
    exit 0
fi

# حلقه دائمی که جستجو را نگه می‌دارد
while true; do
    # بررسی جستجوی در حال اجرا
    PID_FILE=A136030_Search_M1237_bg/search.pid
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
        if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
            sleep 30
            continue
        fi
    fi
    
    # شروع جستجو
    TS=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TS] شروع/راه‌اندازی مجدد جستجو" >> A136030_Search_M1237_bg/daemon.log
    python3 -u scripts/M1237_bg_search.py >> A136030_Search_M1237_bg/stdout.log 2>&1 &
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    
    # صبر 90 ثانیه قبل از بررسی
    sleep 90
done
