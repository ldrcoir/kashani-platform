#!/bin/bash
export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
LOG=/home/z/my-project/download/c284_ecm_5e12.log
RESULTS=/home/z/my-project/download/c284_ecm_factor.txt
CKPT=/home/z/my-project/download/c284_ecm_5e12_ckpt.txt
B1=5000000000000

# Ensure input
/home/z/.venv/bin/python3 -m pip install --quiet gmpy2 2>/dev/null
/home/z/.venv/bin/python3 -c "
import sys; sys.set_int_max_str_digits(1000000)
import gmpy2; from gmpy2 import mpz
C = mpz(53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087)
open('$INPUT','w').write(str(C))
" 2>/dev/null

CURVES=0
if [ -f "$CKPT" ]; then CURVES=$(cat "$CKPT"); fi

for RESTART in $(seq 1 100); do
    echo "[$(date)] R#$RESTART curves=$CURVES B1=$B1" >> $LOG
    
    for i in 1 2 3 4; do
        SIGMA=$((RANDOM * RANDOM * RANDOM + 1))
        timeout 120 $ECM -sigma $SIGMA $B1 < $INPUT > /tmp/ecm5_r${RESTART}_w${i}.log 2>&1 &
    done
    wait
    CURVES=$((CURVES + 4))
    
    for i in 1 2 3 4; do
        if grep -qi "Factor found" /tmp/ecm5_r${RESTART}_w${i}.log 2>/dev/null; then
            echo "[$(date)] !!! FACTOR FOUND! R#$RESTART c=$CURVES w=$i" >> $LOG
            cat /tmp/ecm5_r${RESTART}_w${i}.log >> $RESULTS
            echo "$CURVES" > $CKPT
            exit 0
        fi
    done
    
    echo "$CURVES" > $CKPT
    echo "[$(date)] R#$RESTART curves=$CURVES/99 no factor" >> $LOG
done
