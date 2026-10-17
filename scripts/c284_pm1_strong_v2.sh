#!/bin/bash
# C284 Pollard p-1 with large B1 — single strong shot
# At 100 ECM curves milestone, try P-1 with B1=1e10, B2=1e15
# This finds q with (q-1)/2458 = k having all prime factors <= 1e10 (or 1 large <= 1e15)

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
WORK=/home/z/my-project/download

LOG=$WORK/c284_pm1_strong.log
RESULTS=$WORK/c284_ecm_factor_found.txt

# Use low priority since ECM is primary attack
renice -n 19 $$ 2>/dev/null

# Make sure input is ready
[ -f "$INPUT" ] || exit 1

B1=10000000000
B2=1000000000000000

echo "[$(date)] Strong P-1 attack B1=$B1 B2=$B2 (low priority)" >> $LOG

# Single attempt with default base (P-1 doesn't need base variation)
# Try a few different x0 values for diversity
for X0 in 2 3 5 7; do
    LOG_TMP=/tmp/c284_pm1_strong_x${X0}.log
    echo "[$(date)] P-1 x0=$X0 B1=$B1 B2=$B2 (low priority, will take ~1 hour)" >> $LOG
    timeout 14400 $ECM -pm1 -x0 $X0 $B1 $B2 < $INPUT > $LOG_TMP 2>&1
    
    if grep -qi "Factor found" $LOG_TMP 2>/dev/null; then
        # Check if trivial
        C284=$(cat $INPUT)
        FACTOR=$(grep "Factor found" $LOG_TMP | head -1 | grep -oE "[0-9]+$")
        if [ -z "$FACTOR" ]; then
            FACTOR=$(grep "Factor found" $LOG_TMP | head -1 | awk '{print $NF}')
        fi
        
        if [ "$FACTOR" = "$C284" ] || [ -z "$FACTOR" ] || [ "$FACTOR" = "1" ]; then
            echo "[$(date)] P-1 x0=$X0: TRIVIAL factor (gcd=N)" >> $LOG
        else
            echo "[$(date)] !!! P-1 REAL FACTOR with x0=$X0! Factor=$FACTOR" >> $LOG
            cat $LOG_TMP >> $RESULTS
            echo "$FACTOR" > $WORK/c284_pm1_FACTOR.txt
            echo "P-1 FACTOR x0=$X0 factor=$FACTOR" > $WORK/c284_STATUS.txt
            exit 0
        fi
    else
        echo "[$(date)] P-1 x0=$X0 done, no factor found" >> $LOG
    fi
done

echo "[$(date)] Strong P-1 attack complete. No real factor." >> $LOG
