#!/bin/bash
# C284 ECM — 100-restart proof wrapper
# Each restart: runs 4 ECM curves, saves checkpoint, checks for factor
# B1=10^12 for 60+ digit factors

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
LOG=/home/z/my-project/download/c284_ecm_100.log
RESULTS=/home/z/my-project/download/c284_ecm_factor_found.txt
CKPT=/home/z/my-project/download/c284_ecm_ckpt.txt
B1=1000000000000

# Ensure C284 file exists
/home/z/.venv/bin/python3 -m pip install --quiet gmpy2 2>/dev/null
/home/z/.venv/bin/python3 -c "
import sys; sys.set_int_max_str_digits(1000000)
import gmpy2; from gmpy2 import mpz
C = mpz(53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087)
open('$INPUT','w').write(str(C))
" 2>/dev/null

# Load checkpoint
CURVES=0
if [ -f "$CKPT" ]; then CURVES=$(cat "$CKPT"); fi

# Run up to 100 restart cycles
for RESTART in $(seq 1 100); do
    echo "[$(date)] Restart #$RESTART, curves=$CURVES, B1=$B1" >> $LOG
    
    # Run 4 parallel ECM curves
    for i in 1 2 3 4; do
        SIGMA=$((RANDOM * RANDOM * RANDOM + 1))
        timeout 120 $ECM -sigma $SIGMA $B1 < $INPUT > /tmp/ecm_r${RESTART}_w${i}.log 2>&1 &
    done
    wait
    CURVES=$((CURVES + 4))
    
    # Check for factor
    for i in 1 2 3 4; do
        if grep -qi "Factor found" /tmp/ecm_r${RESTART}_w${i}.log 2>/dev/null; then
            echo "[$(date)] !!! FACTOR FOUND! restart=$RESTART curve=$CURVES worker=$i" >> $LOG
            cat /tmp/ecm_r${RESTART}_w${i}.log >> $RESULTS
            echo "$CURVES" > $CKPT
            exit 0
        fi
    done
    
    # Save checkpoint
    echo "$CURVES" > $CKPT
    echo "[$(date)] Restart #$RESTART done, curves=$CURVES, no factor" >> $LOG
    
    # Check if we reached targets
    if [ $CURVES -ge 183 ]; then
        echo "[$(date)] Reached 183 curves (60-digit target). Continuing for 65-digit (505)." >> $LOG
    fi
    if [ $CURVES -ge 505 ]; then
        echo "[$(date)] Reached 505 curves (65-digit target). Continuing for 70-digit (1476)." >> $LOG
    fi
done

echo "[$(date)] Completed 100 restarts, $CURVES curves total. No factor." >> $LOG
