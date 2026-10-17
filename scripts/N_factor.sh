#!/bin/bash
# Factor N=42448645709965179520186712586272410887949285176201216206957538377
# 65 digits, no small factors, no P-1 (k not smooth), no rho in 10M iters
# Strategy: ECM with increasing B1, with 2 parallel curves
# User said "two factors: 32 and 33 digits" - so we want B1 that finds ~33-digit factors
# GMP-ECM: for 33 digits need B1=1e6 with ~700 curves, or B1=1e7 with ~60 curves
# Use B1=1e7 first - fast enough, finds 30-35 digit factors

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/tmp/N.txt
LOG=/home/z/my-project/download/N_ecm.log
RESULTS=/home/z/my-project/download/N_factor_found.txt
CKPT=/home/z/my-project/download/N_ecm_ckpt.txt

# B1 progression: 1e7, 1e8, 1e9 (escalate if needed)
# For 32-33 digit factors: B1=1e7 needs ~50-60 curves, B1=1e8 needs ~10-20 curves

# Init
[ -f "$CKPT" ] || echo "0" > "$CKPT"

# Ensure input
echo "42448645709965179520186712586272410887949285176201216206957538377" > $INPUT

C=$(cat $CKPT)
echo "[$(date)] Starting ECM attack on N (65 digits). curves=$C" >> $LOG

# Phase 1: B1=1e7 - should find ~30-35 digit factors quickly
# Each curve ~5 seconds, so 60 curves in ~5 minutes
B1=10000000
TARGET=60
echo "[$(date)] Phase 1: B1=$B1, target $TARGET curves" >> $LOG

while [ $C -lt $TARGET ]; do
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/N_ecm_${C}_w1.log
    LOG2=/tmp/N_ecm_${C}_w2.log
    
    timeout 60 $ECM -sigma $SIG1 $B1 < $INPUT > $LOG1 2>&1 &
    PID1=$!
    timeout 60 $ECM -sigma $SIG2 $B1 < $INPUT > $LOG2 2>&1 &
    PID2=$!
    wait $PID1
    wait $PID2
    C=$((C + 2))
    
    for LOG_FILE in $LOG1 $LOG2; do
        if grep -qi "Factor found" $LOG_FILE 2>/dev/null; then
            FACTOR=$(grep "Factor found" $LOG_FILE | head -1 | grep -oE "[0-9]+$")
            N_VAL=$(cat $INPUT)
            if [ "$FACTOR" != "$N_VAL" ] && [ -n "$FACTOR" ] && [ "$FACTOR" != "1" ]; then
                echo "[$(date)] !!! FACTOR FOUND at curve $C: $FACTOR" >> $LOG
                cat $LOG_FILE >> $RESULTS
                echo "$C" > $CKPT
                echo "FACTOR: $FACTOR" > /home/z/my-project/download/N_STATUS.txt
                exit 0
            else
                echo "[$(date)] curve $C: trivial factor (gcd=N) in $LOG_FILE" >> $LOG
            fi
        fi
    done
    echo "$C" > $CKPT
    
    if [ $((C % 10)) -eq 0 ]; then
        echo "[$(date)] B1=$B1 curves=$C no factor yet" >> $LOG
    fi
done

echo "[$(date)] Phase 1 complete ($C curves at B1=$B1), no factor" >> $LOG

# Phase 2: B1=1e8 - for 35-40 digit factors
B1=100000000
TARGET=$((C + 100))
echo "[$(date)] Phase 2: B1=$B1, target $TARGET curves" >> $LOG

while [ $C -lt $TARGET ]; do
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/N_ecm_${C}_w1.log
    LOG2=/tmp/N_ecm_${C}_w2.log
    
    timeout 300 $ECM -sigma $SIG1 $B1 < $INPUT > $LOG1 2>&1 &
    PID1=$!
    timeout 300 $ECM -sigma $SIG2 $B1 < $INPUT > $LOG2 2>&1 &
    PID2=$!
    wait $PID1
    wait $PID2
    C=$((C + 2))
    
    for LOG_FILE in $LOG1 $LOG2; do
        if grep -qi "Factor found" $LOG_FILE 2>/dev/null; then
            FACTOR=$(grep "Factor found" $LOG_FILE | head -1 | grep -oE "[0-9]+$")
            N_VAL=$(cat $INPUT)
            if [ "$FACTOR" != "$N_VAL" ] && [ -n "$FACTOR" ] && [ "$FACTOR" != "1" ]; then
                echo "[$(date)] !!! FACTOR FOUND at curve $C (B1=$B1): $FACTOR" >> $LOG
                cat $LOG_FILE >> $RESULTS
                echo "$C" > $CKPT
                echo "FACTOR: $FACTOR" > /home/z/my-project/download/N_STATUS.txt
                exit 0
            fi
        fi
    done
    echo "$C" > $CKPT
    
    if [ $((C % 20)) -eq 0 ]; then
        echo "[$(date)] B1=$B1 curves=$C no factor yet" >> $LOG
    fi
done

echo "[$(date)] Phase 2 complete ($C curves total), no factor" >> $LOG

# Phase 3: B1=1e9 - for 40-50 digit factors
B1=1000000000
TARGET=$((C + 200))
echo "[$(date)] Phase 3: B1=$B1, target $TARGET curves" >> $LOG

while [ $C -lt $TARGET ]; do
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/N_ecm_${C}_w1.log
    LOG2=/tmp/N_ecm_${C}_w2.log
    
    timeout 3600 $ECM -sigma $SIG1 $B1 < $INPUT > $LOG1 2>&1 &
    PID1=$!
    timeout 3600 $ECM -sigma $SIG2 $B1 < $INPUT > $LOG2 2>&1 &
    PID2=$!
    wait $PID1
    wait $PID2
    C=$((C + 2))
    
    for LOG_FILE in $LOG1 $LOG2; do
        if grep -qi "Factor found" $LOG_FILE 2>/dev/null; then
            FACTOR=$(grep "Factor found" $LOG_FILE | head -1 | grep -oE "[0-9]+$")
            N_VAL=$(cat $INPUT)
            if [ "$FACTOR" != "$N_VAL" ] && [ -n "$FACTOR" ] && [ "$FACTOR" != "1" ]; then
                echo "[$(date)] !!! FACTOR FOUND at curve $C (B1=$B1): $FACTOR" >> $LOG
                cat $LOG_FILE >> $RESULTS
                echo "$C" > $CKPT
                echo "FACTOR: $FACTOR" > /home/z/my-project/download/N_STATUS.txt
                exit 0
            fi
        fi
    done
    echo "$C" > $CKPT
    
    if [ $((C % 20)) -eq 0 ]; then
        echo "[$(date)] B1=$B1 curves=$C no factor yet" >> $LOG
    fi
done

echo "[$(date)] Phase 3 complete ($C curves total), no factor" >> $LOG
echo "[$(date)] Did not find factor with cumulative ECM effort" >> $LOG
