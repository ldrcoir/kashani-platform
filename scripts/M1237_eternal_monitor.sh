#!/bin/bash
# Eternal Monitor - همیشه مراقب استراتژی 3
# این اسکریپت هر 30 ثانیه چک می‌کنه:
# 1. اگه watcher نیست، شروع کن
# 2. اگه strategy3 نیست (با کمک watcher)، watcher رو restart کن
# 3. اگه ECM پیدا کرد فاکتور رو، گزارش کن

WORKDIR=/home/z/my-project/A136030_M1237_strategy3
WATCHER_PID_FILE=$WORKDIR/watcher.pid
STRATEGY_PID_FILE=$WORKDIR/strategy.pid
FOUND_FILE=$WORKDIR/FOUND_factors.txt
ETERNAL_LOG=$WORKDIR/eternal_monitor.log

# PID خود eternal monitor
echo $$ > $WORKDIR/eternal_monitor.pid

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $ETERNAL_LOG
}

log "=== Eternal Monitor شروع شد (PID $$) ==="

while true; do
    # 1. بررسی watcher
    WATCHER_RUNNING=0
    if [ -f "$WATCHER_PID_FILE" ]; then
        WPID=$(cat "$WATCHER_PID_FILE" 2>/dev/null)
        if [ -n "$WPID" ] && kill -0 "$WPID" 2>/dev/null; then
            WATCHER_RUNNING=1
        fi
    fi
    
    # بررسی با ps هم (در صورت خرابی pid file)
    if [ "$WATCHER_RUNNING" = "0" ]; then
        if pgrep -f "M1237_strategy3_watcher" > /dev/null 2>&1; then
            WATCHER_RUNNING=1
            # به‌روزرسانی pid file
            pgrep -f "M1237_strategy3_watcher" | head -1 > "$WATCHER_PID_FILE"
        fi
    fi
    
    if [ "$WATCHER_RUNNING" = "0" ]; then
        log "[ALERT] watcher نیست! شروع مجدد..."
        cd /home/z/my-project
        setsid bash scripts/M1237_strategy3_watcher.sh > /dev/null 2>&1 < /dev/null &
        NEW_WPID=$!
        disown $NEW_WPID 2>/dev/null
        echo $NEW_WPID > "$WATCHER_PID_FILE"
        log "[OK] watcher جدید شروع شد: PID $NEW_WPID"
    fi
    
    # 2. بررسی strategy3 (با کمک watcher خودش باید restart بشه)
    STRATEGY_RUNNING=0
    if pgrep -f "M1237_strategy3.py" > /dev/null 2>&1; then
        STRATEGY_RUNNING=1
    fi
    
    if [ "$STRATEGY_RUNNING" = "0" ]; then
        log "[ALERT] strategy3 اجرا نیست! watcher باید آن را restart کند..."
        # watcher باید خودش restart کنه. اگه نه، ما مستقیم start می‌کنیم
        # حذف pid file تا watcher راحت restart کنه
        rm -f "$STRATEGY_PID_FILE" 2>/dev/null
    fi
    
    # 3. بررسی فاکتور پیدا شده
    if [ -f "$FOUND_FILE" ]; then
        SIZE=$(stat -c%s "$FOUND_FILE" 2>/dev/null || echo 0)
        if [ "$SIZE" -gt 0 ]; then
            log "[★★★] FACTOR FOUND! حجم فایل FOUND: $SIZE بایت"
            # یک بار log کن و بعد فقط تغییر رو log کن
            if [ ! -f "$WORKDIR/factor_alerted" ]; then
                log "[★★★] محتوای FOUND_factors.txt:"
                cat "$FOUND_FILE" >> "$ETERNAL_LOG"
                touch "$WORKDIR/factor_alerted"
            fi
        fi
    fi
    
    # 4. لاگ دوره‌ای هر 10 دقیقه
    MINUTE=$(date +%M)
    SECOND=$(date +%S)
    if [ "$SECOND" -lt 30 ]; then
        # وضعیت فعلی
        STATE=$(cat "$WORKDIR/state.json" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'step={d.get(\"last_step\",0)}, phase={d.get(\"last_phase\",\"?\")}') " 2>/dev/null || echo "?")
        log "[STATUS] watcher OK, strategy3 state: $STATE"
        # صبر تا دقیقه بعد
        sleep 60
    fi
    
    sleep 30
done
