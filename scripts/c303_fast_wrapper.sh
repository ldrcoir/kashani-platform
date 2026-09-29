#!/bin/bash
# Wrapper for ultra-fast sieve

LOG=/home/z/my-project/download/c303_sieve_run.log
SCRIPT=/home/z/my-project/scripts/c303_ultra_fast.py
PYTHON=/home/z/.venv/bin/python3
RESULTS=/home/z/my-project/download/c303_sieve_results_fast.txt
CHECKPOINT=/home/z/my-project/download/c303_sieve_checkpoint_fast.json

while true; do
    echo "===========================================" >> $LOG
    echo "[$(date)] Starting ultra-fast sieve..." >> $LOG
    echo "===========================================" >> $LOG
    
    $PYTHON -u $SCRIPT >> $LOG 2>&1
    EXIT_CODE=$?
    
    echo "[$(date)] Sieve exited with code $EXIT_CODE" >> $LOG
    
    # Check if factor found
    if [ -f "$RESULTS" ]; then
        if grep -q "FACTOR FOUND" "$RESULTS"; then
            echo "[$(date)] FACTOR FOUND! Stopping wrapper." >> $LOG
            exit 0
        fi
    fi
    
    # Check checkpoint
    if [ -f "$CHECKPOINT" ]; then
        LAST_K=$(grep '"last_k_processed"' "$CHECKPOINT" | grep -oE '[0-9]+' | head -1)
        echo "[$(date)] Last k: $LAST_K" >> $LOG
        if [ -n "$LAST_K" ] && [ "$LAST_K" -ge 100000000000 ]; then
            echo "[$(date)] Reached k=100B. Stopping wrapper." >> $LOG
            exit 0
        fi
    fi
    
    echo "[$(date)] Restarting in 5 seconds..." >> $LOG
    sleep 5
done
