#!/bin/bash
# ============================================================
# سوپروایسر ۱۲ ساعته
# ============================================================
DURATION_SEC=$((12 * 3600))
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
log "🚀 سوپروایسر ۱۲ ساعته شروع شد"
log "⏰ شروع: $(date -d @${START_TIME} '+%H:%M:%S')"
log "⏰ پایان: $(date -d @${END_TIME} '+%H:%M:%S')"
log "============================================================"

range_worker_loop() {
    local ranges=("200000000 1000000000" "1000000000 5000000000")
    local idx=0
    while true; do
        local now=$(date +%s)
        if [ $now -ge $END_TIME ]; then
            echo "[$(date '+%H:%M:%S')] range_worker: time up" >> "$RANGE_LOG"
            return
        fi
        local args="${ranges[$idx]}"
        local start=$(echo $args | cut -d' ' -f1)
        local N=$(echo $args | cut -d' ' -f2)
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] range_worker: بازه #idx ($start تا $N)" >> "$RANGE_LOG"
        python3 "$SCRIPTS_DIR/complete_table_parallel.py" --start $start --N $N --workers 2 >> "$RANGE_LOG" 2>&1
        idx=$((idx + 1))
        if [ $idx -ge ${#ranges[@]} ]; then idx=0; fi
        sleep 3
    done
}

mass_submit_loop() {
    local restart_count=0
    while true; do
        local now=$(date +%s)
        if [ $now -ge $END_TIME ]; then
            echo "[$(date '+%H:%M:%S')] mass_submit: time up" >> "$MASS_LOG"
            return
        fi
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] mass_submit: دور #$restart_count" >> "$MASS_LOG"
        python3 "$SCRIPTS_DIR/mass_submit.py" >> "$MASS_LOG" 2>&1
        restart_count=$((restart_count + 1))
        sleep 5
    done
}

# Launch workers in detached subshells
( range_worker_loop & )
log "✅ range_worker شروع شد"
sleep 3
( mass_submit_loop & )
log "✅ mass_submit شروع شد"

LAST_REPORT=$(date +%s)
while true; do
    now=$(date +%s)
    if [ $now -ge $END_TIME ]; then
        log "⏰ زمان ۱۲ ساعت تمام شد."
        exit 0
    fi
    if [ $((now - LAST_REPORT)) -ge 300 ]; then
        log "📊 گزارش — زمان باقی‌مانده: $(( (END_TIME - now) / 60 )) دقیقه"
        if [ -f "$LOG_DIR/mass_submit_db.json" ]; then
            stats=$(python3 -c "import json; d=json.load(open('$LOG_DIR/mass_submit_db.json')); n=d.get('numbers',[]); print(f'{len(n)} numbers, {sum(x.get(\"credited\",0) for x in n)} credit')" 2>/dev/null)
            log "  📦 mass_submit: $stats"
        fi
        LAST_REPORT=$now
    fi
    sleep 30
done
