#!/bin/bash
# C284 Pollard p-1 attack — strong since Mersenne factors have form q=2458k+1
# Try several B1 values to maximize chance of finding smooth-k factors

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
LOG=/home/z/my-project/download/c284_pm1_strong.log
RESULTS=/home/z/my-project/download/c284_ecm_factor_found.txt

# B1 progression: 1e8, 1e9, 1e10 with matching B2
# Each P-1 ~ similar time to ECM stage 1 (no extra stage 2 work that costs a lot)
B1_LIST="100000000 1000000000 10000000000"
B2_LIST="1000000000000 10000000000000 100000000000000"

CYCLE=0
while true; do
    IDX=0
    for B1 in $B1_LIST; do
        B2=$(echo $B2_LIST | cut -d' ' -f$((IDX + 1)))
        SIGMA=$((RANDOM * RANDOM + 1))
        # B1=1e8 takes ~340s for stage 1 (since stage1 only ~ 340s)
        # P-1 stage 1 + stage 2: stage 2 is faster than ECM stage 2
        # Use generous timeout
        case $B1 in
            100000000) TIMEOUT=400 ;;
            1000000000) TIMEOUT=4000 ;;
            10000000000) TIMEOUT=40000 ;;
        esac
        
        echo "[$(date)] P-1 cycle=$CYCLE B1=$B1 B2=$B2 timeout=${TIMEOUT}s" >> $LOG
        timeout $TIMEOUT $ECM -pm1 -sigma $SIGMA $B1 $B2 < $INPUT > /tmp/c284_pm1_strong_${CYCLE}.log 2>&1
        
        if grep -qi "Factor found" /tmp/c284_pm1_strong_${CYCLE}.log 2>/dev/null; then
            echo "[$(date)] !!! P-1 FACTOR FOUND! cycle=$CYCLE B1=$B1 B2=$B2" >> $LOG
            cat /tmp/c284_pm1_strong_${CYCLE}.log >> $RESULTS
            exit 0
        fi
        
        # Show summary line
        SUMMARY=$(grep -E "(Run|Step|Factor)" /tmp/c284_pm1_strong_${CYCLE}.log 2>/dev/null | tail -3)
        echo "[$(date)] cycle=$CYCLE B1=$B1 no factor — $SUMMARY" >> $LOG
        IDX=$((IDX + 1))
    done
    CYCLE=$((CYCLE + 1))
    sync
done
