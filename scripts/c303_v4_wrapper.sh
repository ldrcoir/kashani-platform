#!/bin/bash
# Wrapper for v4 sieve — keeps it running, restarts on crashes
# Checks for factor found, stops if so

LOG=/home/z/my-project/download/c303_sieve_v4_run.log
SCRIPT=/home/z/my-project/scripts/c303_sieve_v4.py
PYTHON=/home/z/.venv/bin/python3
RESULTS=/home/z/my-project/download/c303_sieve_v4_results.txt
CHECKPOINT=/home/z/my-project/download/c303_sieve_v4_checkpoint.json

# Make sure gmpy2 is installed
$PYTHON -c "import gmpy2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[$(date)] Installing gmpy2..." >> $LOG
    $PYTHON -m pip install --quiet gmpy2 >> $LOG 2>&1
fi

while true; do
    echo "===========================================" >> $LOG
    echo "[$(date)] Starting v4 sieve..." >> $LOG
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
        if [ -n "$LAST_K" ] && [ "$LAST_K" -ge 1000000000000 ]; then
            echo "[$(date)] Reached k=1T. Stopping wrapper." >> $LOG
            exit 0
        fi
    fi
    
    # Reinstall gmpy2 in case it was lost
    $PYTHON -c "import gmpy2" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "[$(date)] Reinstalling gmpy2..." >> $LOG
        $PYTHON -m pip install --quiet gmpy2 >> $LOG 2>&1
    fi
    
    echo "[$(date)] Restarting in 3 seconds..." >> $LOG
    sleep 3
done
