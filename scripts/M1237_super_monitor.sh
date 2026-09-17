#!/bin/bash
# Super Monitor - بالاترین لایه حفاظت
# هر 2 دقیقه چک می‌کنه:
# 1. اگه eternal monitor نیست، شروع کن
# 2. اگه gmpy2 نصب نیست، نصب کن
# 3. گزارش وضعیت

WORKDIR=/home/z/my-project/A136030_M1237_strategy4
SUPER_LOG=$WORKDIR/super_monitor.log
SUPER_PID_FILE=$WORKDIR/super_monitor.pid

echo $$ > $SUPER_PID_FILE

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $SUPER_LOG
}

log "=== Super Monitor شروع شد (PID $$) ==="

while true; do
    # 1. بررسی eternal monitor
    if ! pgrep -f "M1237_eternal_monitor_v2" > /dev/null 2>&1; then
        log "[ALERT] eternal monitor نیست! شروع مجدد..."
        cd /home/z/my-project
        setsid bash scripts/M1237_eternal_monitor_v2.sh > /dev/null 2>&1 < /dev/null &
        disown $! 2>/dev/null
        log "[OK] eternal monitor restart شد"
    fi
    
    # 2. بررسی gmpy2
    if ! /usr/bin/python3 -c "import gmpy2" 2>/dev/null; then
        log "[ALERT] gmpy2 از بین رفته! نصب مجدد..."
        /usr/bin/python3 -m pip install gmpy2 --break-system-packages > /dev/null 2>&1
        if /usr/bin/python3 -c "import gmpy2" 2>/dev/null; then
            log "[OK] gmpy2 نصب شد"
        else
            log "[FAIL] gmpy2 نصب نشد"
        fi
    fi
    
    # 3. گزارش وضعیت هر 10 دقیقه
    MINUTE=$(date +%M)
    if [ "$MINUTE" != "${LAST_MIN:-}" ]; then
        ECM_RUNNING=$(pgrep -f "ecm -c" | wc -l)
        STRATEGY_RUNNING=$(pgrep -f "strategy4.py" | wc -l)
        WATCHER_RUNNING=$(pgrep -f "strategy4_watcher" | wc -l)
        ETERNAL_RUNNING=$(pgrep -f "eternal_monitor_v2" | wc -l)
        STATE=$(/usr/bin/python3 -c "import json; d=json.load(open('$WORKDIR/state.json')); print(f'step={d.get(\"last_step\",0)}/8, phase={d.get(\"last_phase\",\"?\")}') " 2>/dev/null || echo "?")
        
        log "[STATUS] super=1, eternal=$ETERNAL_RUNNING, watcher=$WATCHER_RUNNING, strategy=$STRATEGY_RUNNING, ecm=$ECM_RUNNING | state: $STATE"
        LAST_MIN=$MINUTE
    fi
    
    sleep 120
done
