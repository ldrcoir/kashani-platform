#!/bin/bash
# سوپروایسر ۲۴ ساعته v8 — سریع‌تر + pre-generation
DURATION_SEC=$((24 * 3600))
SCRIPTS_DIR="/home/z/my-project/scripts"
LOG_DIR="/home/z/my-project/download/auto_factor"
SUPERVISOR_LOG="$LOG_DIR/supervisor.log"
MASS_LOG="$LOG_DIR/worker_mass_submit.log"
mkdir -p "$LOG_DIR"
log() { ts=$(date '+%Y-%m-%d %H:%M:%S'); echo "[$ts] $1" | tee -a "$SUPERVISOR_LOG"; }
START=$(date +%s); END=$((START + DURATION_SEC))
log "🚀 v8 — pre-generation + فقط ۳۰+ رقم"
mass_loop() {
    local r=0
    while [ $(date +%s) -lt $END ]; do
        echo "[$(date '+%H:%M:%S')] v8 دور #$r" >> "$MASS_LOG"
        python3 "$SCRIPTS_DIR/mass_submit_v8.py" >> "$MASS_LOG" 2>&1
        r=$((r+1)); sleep 3
    done
}
( mass_loop & ); log "✅ mass_submit_v8"
while [ $(date +%s) -lt $END ]; do
    sleep 300
    log "📊 باقی‌مانده: $(( (END - $(date +%s)) / 60 )) دقیقه | $(python3 -c "import json; d=json.load(open('$LOG_DIR/mass_submit_db.json')); n=d.get('numbers',[]); print(f'{len(n)} num, {sum(x.get(\"credited\",0) for x in n)} cred')" 2>/dev/null)"
done
