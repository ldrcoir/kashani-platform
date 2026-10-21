#!/bin/bash
LOG=/home/z/my-project/download/c284_sieve_run.log
SCRIPT=/home/z/my-project/scripts/c284_sieve.py
PYTHON=/home/z/.venv/bin/python3
RESULTS=/home/z/my-project/download/c284_sieve_results.txt
CHECKPOINT=/home/z/my-project/download/c284_sieve_checkpoint.json

# Make sure gmpy2 is installed
$PYTHON -c "import gmpy2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[$(date)] Installing gmpy2..." >> $LOG
    $PYTHON -m pip install --quiet gmpy2 >> $LOG 2>&1
fi

while true; do
    echo "===========================================" >> $LOG
    echo "[$(date)] Starting C284 sieve..." >> $LOG
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
        if [ -n "$LAST_K" ] && [ "$LAST_K" -ge 10000000000 ]; then
            echo "[$(date)] Reached k=10B. Stopping wrapper." >> $LOG
            exit 0
        fi
    fi
    
    # Reinstall gmpy2 if lost
    $PYTHON -c "import gmpy2" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "[$(date)] Reinstalling gmpy2..." >> $LOG
        $PYTHON -m pip install --quiet gmpy2 >> $LOG 2>&1
    fi
    
    echo "[$(date)] Restarting in 3 seconds..." >> $LOG
    sleep 3
done
