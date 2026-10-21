#!/bin/bash
# سوپروایسر ۲۴ ساعته v6
DURATION_SEC=$((24 * 3600))
SCRIPTS_DIR="/home/z/my-project/scripts"
LOG_DIR="/home/z/my-project/download/auto_factor"
SUPERVISOR_LOG="$LOG_DIR/supervisor.log"
RANGE_LOG="$LOG_DIR/worker_range.log"
MASS_LOG="$LOG_DIR/worker_mass_submit.log"
mkdir -p "$LOG_DIR"

log() { ts=$(date '+%Y-%m-%d %H:%M:%S'); line="[$ts] $1"; echo "$line"; echo "$line" >> "$SUPERVISOR_LOG"; }

START_TIME=$(date +%s); END_TIME=$((START_TIME + DURATION_SEC))
log "🚀 سوپروایسر v6 — فقط ۳۰+ رقم متنوع (۳۰-۵۰)"
log "⏰ شروع: $(date -d @${START_TIME} '+%H:%M:%S')"

range_worker_loop() {
    while true; do
        [ $(date +%s) -ge $END_TIME ] && return
        python3 "$SCRIPTS_DIR/multi_range_worker.py" >> "$RANGE_LOG" 2>&1
        sleep 3
    done
}

mass_submit_loop() {
    local r=0
    while true; do
        [ $(date +%s) -ge $END_TIME ] && return
        echo "[$(date '+%H:%M:%S')] v6 دور #$r" >> "$MASS_LOG"
        python3 "$SCRIPTS_DIR/mass_submit_v6.py" >> "$MASS_LOG" 2>&1
        r=$((r+1)); sleep 3
    done
}

( range_worker_loop & ); log "✅ range_worker"
sleep 3; ( mass_submit_loop & ); log "✅ mass_submit_v6"

LAST=$(date +%s)
while true; do
    now=$(date +%s); [ $now -ge $END_TIME ] && { log "⏰ تمام"; exit 0; }
    if [ $((now - LAST)) -ge 300 ]; then
        log "📊 باقی‌مانده: $(( (END_TIME - now) / 60 )) دقیقه"
        [ -f "$LOG_DIR/mass_submit_db.json" ] && log "  📦 $(python3 -c "import json; d=json.load(open('$LOG_DIR/mass_submit_db.json')); n=d.get('numbers',[]); print(f'{len(n)} num, {sum(x.get(\"credited\",0) for x in n)} cred')" 2>/dev/null)"
        [ -f "$LOG_DIR/named_factors.json" ] && log "  📝 $(python3 -c "import json; d=json.load(open('$LOG_DIR/named_factors.json')); n=d.get('named_factors',[]); by={}; [by.update({x['factor_name']:by.get(x['factor_name'],0)+1}) for x in n]; print(' | '.join(f'{k}:{v}' for k,v in sorted(by.items())))" 2>/dev/null)"
        [ -f "$LOG_DIR/held_30_digit_factors.json" ] && log "  🔒 held: $(python3 -c "import json; print(len(json.load(open('$LOG_DIR/held_30_digit_factors.json')).get('held',[])))" 2>/dev/null)"
        LAST=$now
    fi
    sleep 30
done
