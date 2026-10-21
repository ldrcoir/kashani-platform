#!/bin/bash
# Factor N3 with parallel ECM
export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/tmp/N3.txt
LOG=/home/z/my-project/download/N3_ecm.log
RESULTS=/home/z/my-project/download/N3_factor_found.txt
CKPT=/home/z/my-project/download/N3_ecm_ckpt.txt
STATUS=/home/z/my-project/download/N3_STATUS.txt

echo "53557420296729856940815708470943351869321072980535994936566260779217" > $INPUT
[ -f "$CKPT" ] || echo "0" > "$CKPT"
C=$(cat $CKPT)
echo "[$(date)] Starting ECM on N3 (68 digits). curves=$C" >> $LOG

# Phase 1: B1=1e7, 100 curves
B1=10000000
TARGET=$((C + 100))
echo "[$(date)] Phase 1: B1=$B1, target $TARGET curves" >> $LOG

while [ $C -lt $TARGET ]; do
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/N3_${C}_w1.log
    LOG2=/tmp/N3_${C}_w2.log
    
    timeout 60 $ECM -sigma $SIG1 $B1 < $INPUT > $LOG1 2>&1 &
    PID1=$!
    timeout 60 $ECM -sigma $SIG2 $B1 < $INPUT > $LOG2 2>&1 &
    PID2=$!
    wait $PID1
    wait $PID2
    C=$((C + 2))
    
    for LF in $LOG1 $LOG2; do
        if grep -qi "Factor found" $LF 2>/dev/null; then
            F=$(grep "Factor found" $LF | head -1 | grep -oE "[0-9]+$")
            NV=$(cat $INPUT)
            if [ "$F" != "$NV" ] && [ -n "$F" ] && [ "$F" != "1" ]; then
                echo "[$(date)] !!! FACTOR at curve $C (B1=$B1): $F" >> $LOG
                cat $LF >> $RESULTS
                echo "$C" > $CKPT
                echo "FACTOR: $F" > $STATUS
                exit 0
            fi
        fi
    done
    echo "$C" > $CKPT
    if [ $((C % 20)) -eq 0 ]; then
        echo "[$(date)] B1=$B1 curves=$C no factor" >> $LOG
    fi
done

# Phase 2: B1=1e8
B1=100000000
TARGET=$((C + 200))
echo "[$(date)] Phase 2: B1=$B1, target $TARGET curves" >> $LOG
while [ $C -lt $TARGET ]; do
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/N3_${C}_w1.log
    LOG2=/tmp/N3_${C}_w2.log
    
    timeout 300 $ECM -sigma $SIG1 $B1 < $INPUT > $LOG1 2>&1 &
    PID1=$!
    timeout 300 $ECM -sigma $SIG2 $B1 < $INPUT > $LOG2 2>&1 &
    PID2=$!
    wait $PID1
    wait $PID2
    C=$((C + 2))
    for LF in $LOG1 $LOG2; do
        if grep -qi "Factor found" $LF 2>/dev/null; then
            F=$(grep "Factor found" $LF | head -1 | grep -oE "[0-9]+$")
            NV=$(cat $INPUT)
            if [ "$F" != "$NV" ] && [ -n "$F" ] && [ "$F" != "1" ]; then
                echo "[$(date)] !!! FACTOR at curve $C (B1=$B1): $F" >> $LOG
                cat $LF >> $RESULTS
                echo "$C" > $CKPT
                echo "FACTOR: $F" > $STATUS
                exit 0
            fi
        fi
    done
    echo "$C" > $CKPT
done

echo "[$(date)] Failed after $C curves" >> $LOG
