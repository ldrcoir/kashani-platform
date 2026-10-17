#!/bin/bash
# C284 monitor — checks every 5 min for factor found
# Logs progress and exits when factor found or 24 hours elapsed

WORK=/home/z/my-project/download
START=$(date +%s)

while true; do
    NOW=$(date +%s)
    ELAPSED=$((NOW - START))
    
    # Check if factor found
    if [ -f "$WORK/c284_STATUS.txt" ]; then
        echo "[$(date)] !!! FACTOR FOUND: $(cat $WORK/c284_STATUS.txt)"
        cat $WORK/c284_ecm_factor_found.txt 2>/dev/null | tail -30
        exit 0
    fi
    
    # Get current state
    CKPT=$(cat $WORK/c284_ecm_1e8_ckpt.txt 2>/dev/null)
    PROCS=$(ps -ef | grep -c "[e]cm -sigma")
    
    echo "[$(date)] elapsed=${ELAPSED}s curves=$CKPT ecm_procs=$PROCS"
    
    # Check if main script is still alive
    if [ $PROCS -eq 0 ]; then
        echo "[$(date)] !!! WARNING: No ECM processes running!"
        echo "Main script may have died. Last log:"
        tail -5 $WORK/c284_ecm_1e8_dedicated.log 2>/dev/null
    fi
    
    # Check memory
    MEM=$(free | awk '/^Mem:/ {print int($3/1024)}')
    if [ "$MEM" -gt 3500 ]; then
        echo "[$(date)] WARNING: High memory usage ${MEM}MB"
    fi
    
    # Stop after 24 hours
    if [ $ELAPSED -gt 86400 ]; then
        echo "[$(date)] 24 hours elapsed, exiting monitor"
        exit 0
    fi
    
    sleep 300
done
