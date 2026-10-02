#!/bin/bash
LOG=/home/z/my-project/download/c284_v7_run.log
SCRIPT=/home/z/my-project/scripts/c284_sieve_v7.py
PYTHON=/home/z/.venv/bin/python3
RESULTS=/home/z/my-project/download/c284_v7_results.txt
CHECKPOINT=/home/z/my-project/download/c284_v7_checkpoint.json

$PYTHON -c "import gmpy2" 2>/dev/null
if [ $? -ne 0 ]; then
    $PYTHON -m pip install --quiet gmpy2 >> $LOG 2>&1
fi

while true; do
    echo "[$(date)] Starting v7 sieve..." >> $LOG
    $PYTHON -u $SCRIPT >> $LOG 2>&1
    echo "[$(date)] Sieve exited (code $?)" >> $LOG
    
    if [ -f "$RESULTS" ] && grep -q "FACTOR FOUND" "$RESULTS"; then
        echo "[$(date)] FACTOR FOUND!" >> $LOG
        exit 0
    fi
    
    if [ -f "$CHECKPOINT" ]; then
        LAST_K=$(grep '"last_k_processed"' "$CHECKPOINT" | grep -oE '[0-9]+' | head -1)
        if [ -n "$LAST_K" ] && [ "$LAST_K" -ge 10000000000000 ]; then
            exit 0
        fi
    fi
    
    $PYTHON -c "import gmpy2" 2>/dev/null || $PYTHON -m pip install --quiet gmpy2 >> $LOG 2>&1
    sleep 3
done
