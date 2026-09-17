#!/bin/bash
# این اسکریپت توسط cron هر دقیقه فراخوانی می‌شود
# اگر جستجو در حال اجرا نباشد، آن را شروع می‌کند

WORKDIR=/home/z/my-project/A136030_Search_M1237_bg
PID_FILE=$WORKDIR/search.pid

# بررسی جستجوی در حال اجرا
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE" 2>/dev/null)
    if [ -n "$OLD_PID" ] && kill -0 "$OLD_PID" 2>/dev/null; then
        # هنوز در حال اجراست
        exit 0
    fi
fi

# شروع جستجوی جدید
TS=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$TS] شروع/راه‌اندازی مجدد جستجو" >> $WORKDIR/daemon.log

cd /home/z/my-project
nohup python3 -u scripts/M1237_bg_search.py >> $WORKDIR/stdout.log 2>&1 < /dev/null &
NEW_PID=$!
echo $NEW_PID > "$PID_FILE"
disown $NEW_PID 2>/dev/null

echo "[$TS] PID جدید: $NEW_PID" >> $WORKDIR/daemon.log
