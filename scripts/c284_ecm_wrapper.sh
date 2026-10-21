#!/bin/bash
export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
LOG=/home/z/my-project/download/c284_ecm_continuous.log
RESULTS=/home/z/my-project/download/c284_ecm_results.txt

# Make sure gmpy2 is available
/home/z/.venv/bin/python3 -c "import gmpy2" 2>/dev/null || /home/z/.venv/bin/python3 -m pip install --quiet gmpy2

CURVE_COUNT=0
B1_LIST="1000000000 10000000000 100000000000"

while true; do
    for B1 in $B1_LIST; do
        # Run 4 parallel ECM curves
        for i in 1 2 3 4; do
            SIGMA=$((RANDOM * RANDOM + 1))
            timeout 100 $ECM -sigma $SIGMA $B1 < $INPUT > /tmp/ecm_c${CURVE_COUNT}_w${i}.log 2>&1 &
        done
        wait
        
        CURVE_COUNT=$((CURVE_COUNT + 4))
        
        # Check for factor
        for i in 1 2 3 4; do
            if grep -qi "factor" /tmp/ecm_c${CURVE_COUNT}_w${i}.log 2>/dev/null; then
                if grep -qi "found" /tmp/ecm_c${CURVE_COUNT}_w${i}.log 2>/dev/null; then
                    echo "[$(date)] !!! FACTOR FOUND at B1=$B1, curve=$CURVE_COUNT, worker=$i" >> $LOG
                    cat /tmp/ecm_c${CURVE_COUNT}_w${i}.log >> $RESULTS
                    exit 0
                fi
            fi
        done
        
        echo "[$(date)] B1=$B1, curves=$CURVE_COUNT, no factor" >> $LOG
    done
done
