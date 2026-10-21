#!/bin/bash
# Factoring remaining 68 and 69 digit numbers with B1=1e8 fallback
export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm

# 68-digit number
N68="33652296583203221307464156749240536889389747434531945205562694505791"
echo "$N68" > /tmp/N68.txt

# 69-digit number
N69="868624435138141726264151335316773162790585962863785913978383729851307"
echo "$N69" > /tmp/N69.txt

# Also try the 65-digit one that failed
N65="27855762633981389119148809907762615694358689058305929009860182881"
echo "$N65" > /tmp/N65.txt

# For each: try B1=1e7 (50 curves), then B1=1e8 (10 curves)
for label in N65 N68 N69; do
    echo ""
    echo "=== Factoring $label ==="
    INPUT=/tmp/$label.txt
    N_VAL=$(cat $INPUT)
    
    # B1=1e7 with 50 curves
    for i in $(seq 1 25); do
        SIGMA=$((RANDOM * RANDOM + 1))
        timeout 30 $ECM -sigma $SIGMA 10000000 < $INPUT > /tmp/${label}_ecm.log 2>&1 &
        SIGMA2=$((RANDOM * RANDOM + 1))
        timeout 30 $ECM -sigma $SIGMA2 10000000 < $INPUT > /tmp/${label}_ecm2.log 2>&1 &
        wait
        for F in /tmp/${label}_ecm.log /tmp/${label}_ecm2.log; do
            if grep -qi "Factor found" $F 2>/dev/null; then
                FACTOR=$(grep "Factor found" $F | head -1 | grep -oE "[0-9]+$")
                if [ "$FACTOR" != "$N_VAL" ] && [ -n "$FACTOR" ] && [ "$FACTOR" != "1" ]; then
                    echo "FOUND at curve ~$((i*2)) (B1=1e7): $FACTOR"
                    COFACTOR=$(python3 -c "print($N_VAL // $FACTOR)")
                    echo "COFACTOR: $COFACTOR"
                    echo "$FACTOR" > /tmp/${label}_factor.txt
                    break 2
                fi
            fi
        done
    done
    
    if [ ! -f /tmp/${label}_factor.txt ]; then
        echo "B1=1e7 failed. Trying B1=1e8..."
        for i in $(seq 1 10); do
            SIGMA=$((RANDOM * RANDOM + 1))
            timeout 300 $ECM -sigma $SIGMA 100000000 < $INPUT > /tmp/${label}_ecm.log 2>&1 &
            wait
            if grep -qi "Factor found" /tmp/${label}_ecm.log 2>/dev/null; then
                FACTOR=$(grep "Factor found" /tmp/${label}_ecm.log | head -1 | grep -oE "[0-9]+$")
                if [ "$FACTOR" != "$N_VAL" ] && [ -n "$FACTOR" ] && [ "$FACTOR" != "1" ]; then
                    echo "FOUND at curve $i (B1=1e8): $FACTOR"
                    COFACTOR=$(python3 -c "print($N_VAL // $FACTOR)")
                    echo "COFACTOR: $COFACTOR"
                    echo "$FACTOR" > /tmp/${label}_factor.txt
                    break
                fi
            fi
        done
    fi
    
    if [ ! -f /tmp/${label}_factor.txt ]; then
        echo "$label NOT factored."
    fi
done

echo ""
echo "=== Summary ==="
for label in N65 N68 N69; do
    if [ -f /tmp/${label}_factor.txt ]; then
        F=$(cat /tmp/${label}_factor.txt)
        N_VAL=$(cat /tmp/$label.txt)
        COF=$(python3 -c "print($N_VAL // $F)")
        echo "$label = $N_VAL"
        echo "  = $F × $COF"
    else
        echo "$label NOT factored."
    fi
done
