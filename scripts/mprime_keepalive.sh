#!/bin/bash
# Keep mprime running in background, restart if it crashes
cd /home/z/my-project/mprime/work
LOG=/home/z/my-project/scripts/mprime_keepalive.log

echo "[$(date +%H:%M:%S)] Keepalive started" > $LOG

while true; do
    # Check if mprime is running
    if ! pgrep -x mprime > /dev/null; then
        echo "[$(date +%H:%M:%S)] mprime not running, starting..." >> $LOG
        rm -f mprime.pid
        LD_LIBRARY_PATH=/home/z/my-project/mprime LD_PRELOAD=/home/z/my-project/mprime/libgmp.so.10 \
            timeout 540 /home/z/my-project/mprime/mprime -d -w/home/z/my-project/mprime/work >> /tmp/mprime_ecm.log 2>&1
        echo "[$(date +%H:%M:%S)] mprime exited (exit $?)" >> $LOG
    fi
    
    # Check if factor found
    if grep -q "has a factor\|factor found" /home/z/my-project/mprime/work/results.txt 2>/dev/null; then
        echo "[$(date +%H:%M:%S)] *** FACTOR FOUND! ***" >> $LOG
        cat /home/z/my-project/mprime/work/results.txt >> $LOG
        break
    fi
    
    sleep 5
done

echo "[$(date +%H:%M:%S)] Keepalive finished" >> $LOG
