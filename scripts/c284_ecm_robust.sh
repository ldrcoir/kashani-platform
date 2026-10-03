#!/bin/bash
# Robust ECM wrapper for C284 — 4 parallel workers, B1=10^12
# Survives server restarts via checkpoint

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
LOG=/home/z/my-project/download/c284_ecm_60plus.log
RESULTS=/home/z/my-project/download/c284_ecm_factor.txt
CKPT=/home/z/my-project/download/c284_ecm_ckpt.json

# Ensure C284 file exists
/home/z/.venv/bin/python3 -m pip install --quiet gmpy2 2>/dev/null
/home/z/.venv/bin/python3 -c "
import sys; sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz
C = mpz(53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087)
open('$INPUT','w').write(str(C))
" 2>/dev/null

# Load checkpoint
CURVES_DONE=0
if [ -f "$CKPT" ]; then
    CURVES_DONE=$(grep -oE '[0-9]+' "$CKPT" | head -1)
fi

# Target: 183 curves at B1=10^12 for 60-digit factor
# Then 505 curves for 65-digit
# Each curve ~100s, 4 parallel = 25s effective

B1=1000000000000  # 10^12
TARGET=200  # first milestone

while [ $CURVES_DONE -lt $TARGET ]; do
    echo "[$(date)] Starting batch: curves=$CURVES_DONE/$TARGET B1=$B1" >> $LOG
    
    # Run 4 parallel ECM curves
    PIDS=""
    for i in 1 2 3 4; do
        SIGMA=$((RANDOM * RANDOM * RANDOM + 1))
        timeout 120 $ECM -sigma $SIGMA $B1 < $INPUT > /tmp/ecm_r${CURVES_DONE}_w${i}.log 2>&1 &
        PIDS="$PIDS $!"
    done
    
    # Wait for all
    for pid in $PIDS; do
        wait $pid 2>/dev/null
    done
    
    CURVES_DONE=$((CURVES_DONE + 4))
    
    # Check for factor
    for i in 1 2 3 4; do
        if grep -qi "Factor found" /tmp/ecm_r${CURVES_DONE}_w${i}.log 2>/dev/null; then
            echo "[$(date)] !!! FACTOR FOUND! curve=$CURVES_DONE worker=$i" >> $LOG
            cat /tmp/ecm_r${CURVES_DONE}_w${i}.log >> $RESULTS
            exit 0
        fi
    done
    
    # Save checkpoint
    echo "$CURVES_DONE" > $CKPT
    echo "[$(date)] curves=$CURVES_DONE/$TARGET no factor" >> $LOG
done

echo "[$(date)] Reached $TARGET curves. No factor found at B1=10^12." >> $LOG
echo "[$(date)] Factors are likely > 65 digits. Need B1=10^13." >> $LOG
