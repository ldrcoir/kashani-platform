#!/bin/bash
# C284 Combined Attack v2 — fixed wait + better structure
# 2-core / 4GB RAM optimized
# Runs ECM at B1=1e7 (fast, finds 35-45 digit) + occasional P-1 and B1=1e8 ECM

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
WORK=/home/z/my-project/download

LOG_F=$WORK/c284_ecm_1e7.log
CKPT_F=$WORK/c284_ecm_1e7_ckpt.txt
B1_FAST=10000000

LOG_S=$WORK/c284_ecm_1e8.log
CKPT_S=$WORK/c284_ecm_1e8_ckpt.txt
B1_SLOW=100000000

LOG_P=$WORK/c284_pm1_attack.log

RESULTS=$WORK/c284_ecm_factor_found.txt

# Init checkpoints
[ -f "$CKPT_F" ] || echo "0" > "$CKPT_F"
[ -f "$CKPT_S" ] || echo "0" > "$CKPT_S"

# Ensure input
if [ ! -f "$INPUT" ] || [ $(wc -c < "$INPUT") -lt 280 ]; then
/home/z/.venv/bin/python3 -c "
import sys; sys.set_int_max_str_digits(1000000)
C = 53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087
open('$INPUT','w').write(str(C))
"
fi

CF=$(cat $CKPT_F)
CS=$(cat $CKPT_S)

echo "[$(date)] Starting combined v2. Fast curves=$CF, Slow curves=$CS" >> $LOG_F

# Main loop — runs indefinitely
CYCLE=0
while true; do
    CYCLE=$((CYCLE + 1))
    
    # Run 2 parallel B1=1e7 curves (uses both cores, ~47s wall time)
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/c284_f_${CF}_w1.log
    LOG2=/tmp/c284_f_${CF}_w2.log
    
    timeout 90 $ECM -sigma $SIG1 $B1_FAST < $INPUT > $LOG1 2>&1 &
    PID1=$!
    timeout 90 $ECM -sigma $SIG2 $B1_FAST < $INPUT > $LOG2 2>&1 &
    PID2=$!
    
    # Wait for both directly (not via $PIDS string)
    wait $PID1
    wait $PID2
    
    CF=$((CF + 2))
    
    # Check for factor
    F1=$(grep -c "Factor found" $LOG1 2>/dev/null)
    F2=$(grep -c "Factor found" $LOG2 2>/dev/null)
    
    if [ "$F1" != "0" ] || [ "$F2" != "0" ]; then
        echo "[$(date)] !!! FAST FACTOR FOUND! CF=$CF cycle=$CYCLE" >> $LOG_F
        [ "$F1" != "0" ] && cat $LOG1 >> $RESULTS
        [ "$F2" != "0" ] && cat $LOG2 >> $RESULTS
        echo "$CF" > $CKPT_F
        echo "FACTOR FOUND" > $WORK/c284_STATUS.txt
        exit 0
    fi
    echo "$CF" > $CKPT_F
    
    # Every 20 cycles (= 40 fast curves), do one P-1 at B1=1e8
    if [ $((CYCLE % 20)) -eq 0 ]; then
        SIG_P=$((RANDOM * RANDOM + 1))
        LOG_P_TMP=/tmp/c284_pm1_${CYCLE}.log
        timeout 400 $ECM -pm1 -sigma $SIG_P 100000000 1000000000000 < $INPUT > $LOG_P_TMP 2>&1
        if grep -qi "Factor found" $LOG_P_TMP 2>/dev/null; then
            echo "[$(date)] !!! P-1 FACTOR FOUND! cycle=$CYCLE" >> $LOG_P
            cat $LOG_P_TMP >> $RESULTS
            echo "P-1 FACTOR" > $WORK/c284_STATUS.txt
            exit 0
        fi
        echo "[$(date)] P-1 cycle=$CYCLE done, no factor" >> $LOG_P
    fi
    
    # Every 40 cycles (= 80 fast curves), do one B1=1e8 ECM (uses both cores sequentially, ~6 min)
    if [ $((CYCLE % 40)) -eq 0 ]; then
        SIG_S=$((RANDOM * RANDOM + 1))
        LOG_S_TMP=/tmp/c284_s_${CS}.log
        timeout 700 $ECM -sigma $SIG_S $B1_SLOW < $INPUT > $LOG_S_TMP 2>&1
        CS=$((CS + 1))
        if grep -qi "Factor found" $LOG_S_TMP 2>/dev/null; then
            echo "[$(date)] !!! SLOW FACTOR FOUND! CS=$CS cycle=$CYCLE B1=$B1_SLOW" >> $LOG_S
            cat $LOG_S_TMP >> $RESULTS
            echo "$CS" > $CKPT_S
            echo "SLOW FACTOR" > $WORK/c284_STATUS.txt
            exit 0
        fi
        echo "$CS" > $CKPT_S
        echo "[$(date)] Slow cycle CS=$CS done" >> $LOG_S
    fi
    
    # Status log every 10 cycles
    if [ $((CYCLE % 10)) -eq 0 ]; then
        echo "[$(date)] cycle=$CYCLE fast_curves=$CF slow_curves=$CS no factor" >> $LOG_F
    fi
    
    sync
done
