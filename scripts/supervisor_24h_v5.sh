#!/bin/bash
# سوپروایسر ۲۴ ساعته v5
# - فقط ۳۰+ رقم عامل‌ها ثبت می‌شوند
# - تمرکز روی ۴ و ۵ عاملی
# - ۵ بازه‌ی موازی

DURATION_SEC=$((24 * 3600))
SCRIPTS_DIR="/home/z/my-project/scripts"
LOG_DIR="/home/z/my-project/download/auto_factor"
SUPERVISOR_LOG="$LOG_DIR/supervisor.log"
RANGE_LOG="$LOG_DIR/worker_range.log"
MASS_LOG="$LOG_DIR/worker_mass_submit.log"

mkdir -p "$LOG_DIR"

log() {
    ts=$(date '+%Y-%m-%d %H:%M:%S')
    line="[$ts] $1"
    echo "$line"
    echo "$line" >> "$SUPERVISOR_LOG"
}

START_TIME=$(date +%s)
END_TIME=$((START_TIME + DURATION_SEC))
log "============================================================"
log "🚀 سوپروایسر v5 — فقط ۳۰+ رقم، تمرکز روی ۴ و ۵ عاملی"
log "⏰ شروع: $(date -d @${START_TIME} '+%H:%M:%S')"
log "⏰ پایان: $(date -d @${END_TIME} '+%H:%M:%S')"
log "============================================================"

range_worker_loop() {
    while true; do
        local now=$(date +%s)
        if [ $now -ge $END_TIME ]; then return; fi
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] range_worker: شروع" >> "$RANGE_LOG"
        python3 "$SCRIPTS_DIR/multi_range_worker.py" >> "$RANGE_LOG" 2>&1
        sleep 3
    done
}

mass_submit_loop() {
    local restart_count=0
    while true; do
        local now=$(date +%s)
        if [ $now -ge $END_TIME ]; then return; fi
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] mass_submit v5: دور #$restart_count" >> "$MASS_LOG"
        python3 "$SCRIPTS_DIR/mass_submit_v5.py" >> "$MASS_LOG" 2>&1
        restart_count=$((restart_count + 1))
        sleep 3
    done
}

( range_worker_loop & )
log "✅ range_worker شروع شد"
sleep 3
( mass_submit_loop & )
log "✅ mass_submit_v5 شروع شد (فقط ۳۰+ رقم)"

LAST_REPORT=$(date +%s)
while true; do
    now=$(date +%s)
    if [ $now -ge $END_TIME ]; then
        log "⏰ زمان تمام شد."
        exit 0
    fi
    if [ $((now - LAST_REPORT)) -ge 300 ]; then
        remaining=$(( (END_TIME - now) / 60 ))
        log "📊 گزارش — باقی‌مانده: ${remaining} دقیقه"
        if [ -f "$LOG_DIR/mass_submit_db.json" ]; then
            stats=$(python3 -c "import json; d=json.load(open('$LOG_DIR/mass_submit_db.json')); n=d.get('numbers',[]); print(f'{len(n)} numbers, {sum(x.get(\"credited\",0) for x in n)} credit')" 2>/dev/null)
            log "  📦 mass_submit: $stats"
        fi
        if [ -f "$LOG_DIR/named_factors.json" ]; then
            named=$(python3 -c "import json; d=json.load(open('$LOG_DIR/named_factors.json')); n=d.get('named_factors',[]); by={}; [by.update({x['factor_name']:by.get(x['factor_name'],0)+1}) for x in n]; print(' | '.join(f'{k}:{v}' for k,v in sorted(by.items())))" 2>/dev/null)
            log "  📝 named: $named"
        fi
        if [ -f "$LOG_DIR/held_30_digit_factors.json" ]; then
            held=$(python3 -c "import json; print(len(json.load(open('$LOG_DIR/held_30_digit_factors.json')).get('held',[])))" 2>/dev/null)
            log "  🔒 held: $held"
        fi
        LAST_REPORT=$now
    fi
    sleep 30
done
