#!/bin/bash
# Eternal Monitor v2 - نسخه بهتر
# هر 20 ثانیه چک می‌کنه:
# 1. خود eternal monitor رو هم چک می‌کنه (در صورت نیاز restart)
# 2. اگه watcher نیست، شروع کن
# 3. اگه strategy4 نیست، watcher رو restart کنه
# 4. اگه فاکتور پیدا شده، گزارش کن

WORKDIR=/home/z/my-project/A136030_M1237_strategy4
WATCHER_PID_FILE=$WORKDIR/watcher.pid
STRATEGY_PID_FILE=$WORKDIR/strategy.pid
FOUND_FILE=$WORKDIR/FOUND_factors.txt
ETERNAL_LOG=$WORKDIR/eternal_monitor.log
ETERNAL_PID_FILE=$WORKDIR/eternal_monitor.pid

echo $$ > $ETERNAL_PID_FILE

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $ETERNAL_LOG
}

log "=== Eternal Monitor v2 شروع شد (PID $$) ==="

while true; do
    # بررسی watcher
    WATCHER_RUNNING=0
    if pgrep -f "M1237_strategy4_watcher" > /dev/null 2>&1; then
        WATCHER_RUNNING=1
    fi
    
    if [ "$WATCHER_RUNNING" = "0" ]; then
        log "[ALERT] watcher نیست! شروع مجدد..."
        cd /home/z/my-project
        setsid bash scripts/M1237_strategy4_watcher.sh > /dev/null 2>&1 < /dev/null &
        disown $! 2>/dev/null
        log "[OK] watcher جدید شروع شد"
    fi
    
    # بررسی strategy4
    STRATEGY_RUNNING=0
    if pgrep -f "M1237_strategy4.py" > /dev/null 2>&1; then
        STRATEGY_RUNNING=1
    fi
    
    if [ "$STRATEGY_RUNNING" = "0" ]; then
        log "[ALERT] strategy4 اجرا نیست! watcher باید restart کنه..."
        # حذف pid file تا watcher راحت restart کنه
        rm -f "$STRATEGY_PID_FILE" 2>/dev/null
    fi
    
    # بررسی فاکتور
    if [ -f "$FOUND_FILE" ]; then
        SIZE=$(stat -c%s "$FOUND_FILE" 2>/dev/null || echo 0)
        if [ "$SIZE" -gt 0 ] && [ ! -f "$WORKDIR/factor_alerted" ]; then
            log "[★★★] FACTOR FOUND!"
            cat "$FOUND_FILE" >> "$ETERNAL_LOG"
            touch "$WORKDIR/factor_alerted"
        fi
    fi
    
    # لاگ دوره‌ای هر 5 دقیقه
    MINUTE=$(date +%M)
    if [ "$MINUTE" != "${LAST_MINUTE:-}" ]; then
        STATE=$(cat "$WORKDIR/state.json" 2>/dev/null | /usr/bin/python3 -c "import sys,json; d=json.load(sys.stdin); print(f'step={d.get(\"last_step\",0)}, phase={d.get(\"last_phase\",\"?\")}') " 2>/dev/null || echo "?")
        log "[STATUS] watcher=$WATCHER_RUNNING, strategy=$STRATEGY_RUNNING, state: $STATE"
        LAST_MINUTE=$MINUTE
    fi
    
    sleep 20
done
