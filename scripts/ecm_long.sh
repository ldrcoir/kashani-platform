#!/bin/bash
# Long-running ECM on F2 with various B1 values
# Tries: B1=3e9 with 100 curves (the realistic target for ~45 digit factors)

export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
LOG=/home/z/my-project/logs/ecm_long.log
INPUT=/home/z/my-project/F2.txt

cd /home/z/my-project

echo "[$(date)] Starting long ECM run on F2 (303 digits)" > $LOG
echo "[$(date)] Strategy: B1=3e9 with up to 200 curves" >> $LOG
echo "[$(date)] Expected: ~70 curves for 45-digit factor, ~231 for 50-digit" >> $LOG
echo "" >> $LOG

# Run with -c 200 (200 curves) and let it run
# Each curve takes ~30s at B1=3e9
# 200 curves = ~100 minutes
$ECM -v -timestamp -c 200 3000000000 < $INPUT >> $LOG 2>&1
echo "[$(date)] ECM run finished. exit: $?" >> $LOG
echo "[$(date)] TAIL:" >> $LOG
tail -30 $LOG >> $LOG
