#!/bin/bash
export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
LOG=/home/z/my-project/download/c284_ecm_continuous.log
RESULTS=/home/z/my-project/download/c284_ecm_factor_found.txt
PIDFILE=/home/z/my-project/download/c284_ecm_pid.txt

TOTAL_CURVES=0

# B1 progression: 10^11 (60-digit) → 10^12 (65-digit) → 10^13 (70-digit)
B1_LIST="100000000000 1000000000000"

while true; do
    for B1 in $B1_LIST; do
        # Run 4 parallel ECM curves
        PIDS=""
        for i in 1 2 3 4; do
            SIGMA=$((RANDOM * RANDOM * RANDOM + 1))
            timeout 120 $ECM -sigma $SIGMA $B1 < $INPUT > /tmp/ecm_c${TOTAL_CURVES}_w${i}.log 2>&1 &
            PIDS="$PIDS $!"
        done
        
        # Wait for all to complete
        for pid in $PIDS; do
            wait $pid 2>/dev/null
        done
        
        TOTAL_CURVES=$((TOTAL_CURVES + 4))
        
        # Check for factor
        FACTOR_FOUND=0
        for i in 1 2 3 4; do
            if grep -qi "factor" /tmp/ecm_c${TOTAL_CURVES}_w${i}.log 2>/dev/null; then
                if grep -qi "found" /tmp/ecm_c${TOTAL_CURVES}_w${i}.log 2>/dev/null; then
                    echo "[$(date)] !!! FACTOR FOUND! B1=$B1 curve=$TOTAL_CURVES worker=$i" >> $LOG
                    cat /tmp/ecm_c${TOTAL_CURVES}_w${i}.log >> $RESULTS
                    FACTOR_FOUND=1
                fi
            fi
        done
        
        if [ $FACTOR_FOUND -eq 1 ]; then
            echo "[$(date)] FACTOR FOUND! Stopping." >> $LOG
            exit 0
        fi
        
        echo "[$(date)] B1=$B1 curves=$TOTAL_CURVES no factor" >> $LOG
        echo "$TOTAL_CURVES" > $PIDFILE
    done
done
