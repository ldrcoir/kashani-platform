#!/bin/bash
# C284 dedicated B1=1e8 attack — finds 45-55 digit factors
# 2-core, ~340s per curve, ~21 curves/hour

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
WORK=/home/z/my-project/download

LOG=$WORK/c284_ecm_1e8_dedicated.log
CKPT=$WORK/c284_ecm_1e8_ckpt.txt
RESULTS=$WORK/c284_ecm_factor_found.txt
STATUS=$WORK/c284_STATUS.txt

B1=100000000

[ -f "$CKPT" ] || echo "0" > "$CKPT"

# Ensure input
if [ ! -f "$INPUT" ] || [ $(wc -c < "$INPUT") -lt 280 ]; then
/home/z/.venv/bin/python3 -c "
import sys; sys.set_int_max_str_digits(1000000)
C = 53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087
open('$INPUT','w').write(str(C))
"
fi

C=$(cat $CKPT)
echo "[$(date)] Starting B1=1e8 dedicated attack. Initial curves=$C" >> $LOG

while true; do
    # Run 2 parallel curves
    SIG1=$((RANDOM * RANDOM + 1))
    SIG2=$((RANDOM * RANDOM + 1))
    LOG1=/tmp/c284_1e8_${C}_w1.log
    LOG2=/tmp/c284_1e8_${C}_w2.log
    
    timeout 1200 $ECM -sigma $SIG1 $B1 < $INPUT > $LOG1 2>&1 &
    PID1=$!
    timeout 1200 $ECM -sigma $SIG2 $B1 < $INPUT > $LOG2 2>&1 &
    PID2=$!
    
    wait $PID1
    wait $PID2
    
    C=$((C + 2))
    
    # Check for factor
    if grep -qi "Factor found" $LOG1 2>/dev/null || grep -qi "Factor found" $LOG2 2>/dev/null; then
        echo "[$(date)] !!! FACTOR FOUND at curve $C !" >> $LOG
        grep -A 5 "Factor found" $LOG1 >> $RESULTS 2>/dev/null
        grep -A 5 "Factor found" $LOG2 >> $RESULTS 2>/dev/null
        cat $LOG1 $LOG2 >> $RESULTS 2>/dev/null
        echo "$C" > $CKPT
        echo "FACTOR FOUND" > $STATUS
        exit 0
    fi
    echo "$C" > $CKPT
    
    # Log every 5 curves
    if [ $((C % 10)) -eq 0 ]; then
        # Show last timing
        LAST_TIME=$(grep "Step 2 took" $LOG1 2>/dev/null | tail -1)
        echo "[$(date)] curves=$C no factor. Last: $LAST_TIME" >> $LOG
    fi
    sync
done
