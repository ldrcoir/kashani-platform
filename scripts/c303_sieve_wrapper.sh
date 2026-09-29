#!/bin/bash
# Wrapper script that keeps the sieve running
# Restart the sieve if it dies

LOG=/home/z/my-project/download/c303_sieve_run.log
SCRIPT=/home/z/my-project/scripts/c303_mp_final.py
PYTHON=/home/z/.venv/bin/python3

while true; do
    echo "===========================================" >> $LOG
    echo "[$(date)] Starting sieve..." >> $LOG
    echo "===========================================" >> $LOG
    
    $PYTHON -u $SCRIPT >> $LOG 2>&1
    EXIT_CODE=$?
    
    echo "[$(date)] Sieve exited with code $EXIT_CODE" >> $LOG
    
    # Check if factor found
    if [ -f /home/z/my-project/download/c303_sieve_results.txt ]; then
        if grep -q "FACTOR FOUND" /home/z/my-project/download/c303_sieve_results.txt; then
            echo "[$(date)] FACTOR FOUND! Stopping wrapper." >> $LOG
            exit 0
        fi
    fi
    
    # Check checkpoint
    if [ -f /home/z/my-project/download/c303_sieve_checkpoint.json ]; then
        # Read last_k_processed
        LAST_K=$(grep '"last_k_processed"' /home/z/my-project/download/c303_sieve_checkpoint.json | grep -oE '[0-9]+' | head -1)
        echo "[$(date)] Last k: $LAST_K" >> $LOG
        if [ -n "$LAST_K" ] && [ "$LAST_K" -ge 100000000000 ]; then
            echo "[$(date)] Reached k=100B. Stopping wrapper." >> $LOG
            exit 0
        fi
    fi
    
    # Wait 10 seconds before restart
    echo "[$(date)] Restarting in 10 seconds..." >> $LOG
    sleep 10
done
