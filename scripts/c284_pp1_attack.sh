#!/bin/bash
# C284 P+1 attack — for Mersenne factors q=2458k+1, q+1 = 2(1229k+1)
# If (1229k+1) is smooth, P+1 finds the factor
# Different bases can find different factors

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
WORK=/home/z/my-project/download

LOG=$WORK/c284_pp1_attack.log
CKPT=$WORK/c284_pp1_ckpt.txt
RESULTS=$WORK/c284_ecm_factor_found.txt

B1=10000000
B2=1000000000

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
echo "[$(date)] Starting P+1 attack. Initial=$C B1=$B1 B2=$B2" >> $LOG

# Try many different bases — P+1 success depends on Jacobi(a/N) = -1
# Use small primes / common values as x0 (P+1 starting point)
BASES="2 3 5 6 7 10 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97"

for BASE in $BASES; do
    LOG_TMP=/tmp/c284_pp1_${BASE}.log
    echo "[$(date)] P+1 with base=$BASE (curve=$C)" >> $LOG
    timeout 120 $ECM -pp1 -x0 $BASE $B1 $B2 < $INPUT > $LOG_TMP 2>&1
    
    if grep -qi "Factor found" $LOG_TMP 2>/dev/null; then
        echo "[$(date)] !!! P+1 FACTOR with base=$BASE!" >> $LOG
        cat $LOG_TMP >> $RESULTS
        echo "P+1 FACTOR base=$BASE" > $WORK/c284_STATUS.txt
        exit 0
    fi
    
    # Some bases give "Jacobi symbol = +1, p+1 method won't work" — that's OK
    JAC=$(grep "Jacobi" $LOG_TMP 2>/dev/null | head -1)
    [ -n "$JAC" ] && echo "  -> $JAC" >> $LOG
    
    C=$((C + 1))
    echo "$C" > $CKPT
    sync
done

# Loop back through higher B1 levels
B1_LIST="100000000 1000000000"
B2_LIST="100000000000 10000000000000"

for ROUND in 1 2 3 4 5; do
    IDX=0
    for B1 in $B1_LIST; do
        B2=$(echo $B2_LIST | cut -d' ' -f$((IDX + 1)))
        for BASE in 2 3 5 7 11 13; do
            LOG_TMP=/tmp/c284_pp1_r${ROUND}_b${BASE}.log
            case $B1 in
                100000000) TIMEOUT=600 ;;
                1000000000) TIMEOUT=4000 ;;
            esac
            echo "[$(date)] P+1 round=$ROUND base=$BASE B1=$B1 B2=$B2 (curve=$C)" >> $LOG
            timeout $TIMEOUT $ECM -pp1 -x0 $BASE $B1 $B2 < $INPUT > $LOG_TMP 2>&1
            
            if grep -qi "Factor found" $LOG_TMP 2>/dev/null; then
                echo "[$(date)] !!! P+1 FACTOR round=$ROUND base=$BASE B1=$B1!" >> $LOG
                cat $LOG_TMP >> $RESULTS
                echo "P+1 FACTOR round=$ROUND base=$BASE" > $WORK/c284_STATUS.txt
                exit 0
            fi
            
            JAC=$(grep "Jacobi" $LOG_TMP 2>/dev/null | head -1)
            [ -n "$JAC" ] && echo "  -> $JAC" >> $LOG
            
            C=$((C + 1))
            echo "$C" > $CKPT
            sync
        done
        IDX=$((IDX + 1))
    done
done

echo "[$(date)] P+1 attack complete. No factor found in $C attempts." >> $LOG
