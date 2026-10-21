#!/bin/bash
# C284 P+1 attack v2 — filters out trivial factors (factor == N)

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
WORK=/home/z/my-project/download

LOG=$WORK/c284_pp1_attack.log
CKPT=$WORK/c284_pp1_ckpt.txt
RESULTS=$WORK/c284_ecm_factor_found.txt

# Read C284 to check for trivial factors
C284=$(cat $INPUT)
[ -f "$CKPT" ] || echo "0" > "$CKPT"

# Low priority
renice -n 19 $$ 2>/dev/null

C=$(cat $CKPT)
echo "[$(date)] Starting P+1 attack v2 (filters trivial). Initial=$C" >> $LOG

# Phase 1: B1=1e6, B2=1e8, many bases
B1=1000000
B2=100000000

# Try bases — many will give trivial gcd = N (P+1 degenerate)
# But some might give real factors

# Bases to try - mix of small numbers, primes, and Mersenne-related values
BASES="3 5 6 7 10 11 12 13 14 15 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97 101 103 107 109 113 127 131 137 139 149 151 157 163 167 173 179 181 191 193 197 199 211 223 227 229 233 239 241 251 257 263 269 271 277 281 283 293"

for BASE in $BASES; do
    LOG_TMP=/tmp/c284_pp1_b${BASE}.log
    timeout 30 $ECM -pp1 -x0 $BASE $B1 $B2 < $INPUT > $LOG_TMP 2>&1
    
    # Check for actual factor found
    if grep -qi "Factor found" $LOG_TMP 2>/dev/null; then
        # Extract the factor
        FACTOR=$(grep "Factor found" $LOG_TMP | head -1 | grep -oE "[0-9]+$")
        
        if [ -z "$FACTOR" ]; then
            # Try alternate extraction
            FACTOR=$(grep "Factor found" $LOG_TMP | head -1 | awk '{print $NF}')
        fi
        
        # Filter trivial factors (N itself, 1, or empty)
        if [ "$FACTOR" = "$C284" ] || [ -z "$FACTOR" ] || [ "$FACTOR" = "1" ]; then
            # Trivial, skip
            JAC=$(grep -i "jacobi\|method" $LOG_TMP 2>/dev/null | head -1)
            [ -n "$JAC" ] && echo "  base=$BASE: TRIVIAL — $JAC" >> $LOG
        else
            # REAL factor!
            echo "[$(date)] !!! REAL P+1 FACTOR with base=$BASE! Factor=$FACTOR" >> $LOG
            cat $LOG_TMP >> $RESULTS
            echo "$FACTOR" > $WORK/c284_pp1_FACTOR.txt
            echo "P+1 FACTOR base=$BASE factor=$FACTOR" > $WORK/c284_STATUS.txt
            exit 0
        fi
    fi
    
    C=$((C + 1))
    echo "$C" > $CKPT
done

echo "[$(date)] Phase 1 complete ($C bases tried). No real factor." >> $LOG

# Phase 2: B1=1e7, B2=1e10, smaller base list
B1=10000000
B2=10000000000
echo "[$(date)] Phase 2: B1=$B1 B2=$B2" >> $LOG

BASES2="3 5 6 7 11 13 17 19 23 29 31 41 43 47 53 59 61"
for BASE in $BASES2; do
    LOG_TMP=/tmp/c284_pp1_v2_b${BASE}.log
    timeout 90 $ECM -pp1 -x0 $BASE $B1 $B2 < $INPUT > $LOG_TMP 2>&1
    
    if grep -qi "Factor found" $LOG_TMP 2>/dev/null; then
        FACTOR=$(grep "Factor found" $LOG_TMP | head -1 | grep -oE "[0-9]+$")
        if [ -z "$FACTOR" ]; then
            FACTOR=$(grep "Factor found" $LOG_TMP | head -1 | awk '{print $NF}')
        fi
        if [ "$FACTOR" = "$C284" ] || [ -z "$FACTOR" ] || [ "$FACTOR" = "1" ]; then
            JAC=$(grep -i "jacobi\|method" $LOG_TMP 2>/dev/null | head -1)
            [ -n "$JAC" ] && echo "  base=$BASE (phase 2): TRIVIAL — $JAC" >> $LOG
        else
            echo "[$(date)] !!! REAL P+1 FACTOR (phase 2) base=$BASE! Factor=$FACTOR" >> $LOG
            cat $LOG_TMP >> $RESULTS
            echo "$FACTOR" > $WORK/c284_pp1_FACTOR.txt
            echo "P+1 FACTOR phase2 base=$BASE factor=$FACTOR" > $WORK/c284_STATUS.txt
            exit 0
        fi
    fi
    
    C=$((C + 1))
    echo "$C" > $CKPT
done

echo "[$(date)] P+1 attack v2 complete. Tried $C bases, no real factor." >> $LOG
