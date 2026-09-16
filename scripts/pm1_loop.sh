#!/bin/bash
# P-1 background loop: runs P-1 on missing primes in batches.
# After each batch, picks the next batch from the current -1 list.
# Logs everything to logs/pm1_loop.log and individual batch logs.
# Stops only when no more -1 entries in [min_n, max_n] remain.

set -u
cd /home/z/my-project
mkdir -p logs

B1=5000000
B2=1000000000
BATCH=20
MIN_N=1500
MAX_N=8000

LOOP_LOG=logs/pm1_loop.log
echo "P-1 loop started $(date)" > "$LOOP_LOG"

batch=1
while true; do
    # Get current missing primes in range, take a batch
    targets=$(awk -F'\t' -v lo="$MIN_N" -v hi="$MAX_N" '$2==-1 && $1>=lo && $1<=hi {print $1}' \
        download/A136030_factors_1_to_8000.txt | head -n "$BATCH")

    if [ -z "$targets" ]; then
        echo "[$(date)] No more missing primes in range [$MIN_N, $MAX_N]. Done." >> "$LOOP_LOG"
        break
    fi

    # Build --specific list
    spec=$(echo "$targets" | tr '\n' ' ')
    count=$(echo "$targets" | wc -l)

    batch_log=logs/pm1_batch_${batch}.log
    echo "[$(date)] === Batch $batch: $count primes ===" >> "$LOOP_LOG"
    echo "[$(date)] Targets: $spec" >> "$LOOP_LOG"

    python3 scripts/pm1_factor.py \
        --b1 "$B1" --b2 "$B2" \
        --specific $spec \
        > "$batch_log" 2>&1

    # Count found vs not
    found=$(grep -c ">>> FOUND" "$batch_log" || true)
    missing_now=$(awk -F'\t' -v lo="$MIN_N" -v hi="$MAX_N" '$2==-1 && $1>=lo && $1<=hi' \
        download/A136030_factors_1_to_8000.txt | wc -l)
    echo "[$(date)] Batch $batch done. Found $found. Remaining missing: $missing_now" >> "$LOOP_LOG"

    batch=$((batch + 1))

    # Safety: small sleep to avoid spinning if nothing changes
    sleep 5
done

echo "[$(date)] P-1 loop completed." >> "$LOOP_LOG"
