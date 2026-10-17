#!/bin/bash
# Factor N2 = 44970392094226224655193611221785951576628072532398031171908075269
# Already verified: composite, no factor < 1e7, not perfect power, not in any database

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/tmp/N2.txt
LOG=/home/z/my-project/download/N2_ecm.log
RESULTS=/home/z/my-project/download/N2_factor_found.txt
CKPT=/home/z/my-project/download/N2_ecm_ckpt.txt
STATUS=/home/z/my-project/download/N2_STATUS.txt

echo "44970392094226224655193611221785951576628072532398031171908075269" > $INPUT
[ -f "$CKPT" ] || echo "0" > "$CKPT"

C=$(cat $CKPT)
echo "[$(date)] Starting ECM attack on N2 (65 digits). curves=$C" >> $LOG

# Phase 1: B1=1e7 (finds 30-35 digit factors)
B1=10000000
TARGET=80
echo "[$(date)] Phase 1: B1=$B1, target $TARGET curves" >> $LOG

while [ $C -lt $TARGET ]; do
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/N2_${C}_w1.log
    LOG2=/tmp/N2_${C}_w2.log
    
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
                echo "[$(date)] !!! FACTOR FOUND at curve $C (B1=$B1): $FACTOR" >> $LOG
                cat $LOG_FILE >> $RESULTS
                echo "$C" > $CKPT
                echo "FACTOR: $FACTOR" > $STATUS
                exit 0
            fi
        fi
    done
    echo "$C" > $CKPT
    
    if [ $((C % 10)) -eq 0 ]; then
        echo "[$(date)] B1=$B1 curves=$C no factor yet" >> $LOG
    fi
done

echo "[$(date)] Phase 1 complete ($C curves, no factor)" >> $LOG

# Phase 2: B1=1e8 (finds 35-40 digit factors)
B1=100000000
TARGET=$((C + 200))
echo "[$(date)] Phase 2: B1=$B1, target $TARGET curves" >> $LOG

while [ $C -lt $TARGET ]; do
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/N2_${C}_w1.log
    LOG2=/tmp/N2_${C}_w2.log
    
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
                echo "FACTOR: $FACTOR" > $STATUS
                exit 0
            fi
        fi
    done
    echo "$C" > $CKPT
done

echo "[$(date)] Phase 2 complete ($C curves, no factor)" >> $LOG
