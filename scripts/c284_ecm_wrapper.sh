#!/bin/bash
LOG=/home/z/my-project/download/c284_ecm_wrapper.log
ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
INPUT=/home/z/my-project/C284.txt
export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

while true; do
    echo "[$(date)] Starting ECM B1=1e9..." >> $LOG
    $ECM -v -c 20 1000000000 < $INPUT >> $LOG 2>&1
    echo "[$(date)] ECM exited (code $?)" >> $LOG
    
    if grep -qi "factor found" $LOG 2>/dev/null; then
        echo "[$(date)] FACTOR FOUND!" >> $LOG
        exit 0
    fi
    sleep 3
done
