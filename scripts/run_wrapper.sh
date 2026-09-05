#!/bin/bash
# Wrapper to keep search_4thread.py running
# It runs in 8-min bursts and resumes from checkpoint

cd /home/z/my-project
LOG=/home/z/my-project/scripts/wrapper.log

echo "[$(date +%H:%M:%S)] Wrapper started" > $LOG

for i in $(seq 1 100); do
    echo "[$(date +%H:%M:%S)] === Round $i ===" >> $LOG
    timeout 480 python3 scripts/search_4thread.py >> /tmp/search_main.out 2>&1
    
    # Check if factor found
    if [ -f /home/z/my-project/A136030_Search/results.txt ] && grep -q "FACTOR FOUND" /home/z/my-project/A136030_Search/results.txt 2>/dev/null; then
        echo "[$(date +%H:%M:%S)] *** FACTOR FOUND! ***" >> $LOG
        cat /home/z/my-project/A136030_Search/results.txt >> $LOG
        break
    fi
    
    # Check checkpoint
    if [ -f /home/z/my-project/A136030_Search/checkpoint.json ]; then
        CKPT=$(cat /home/z/my-project/A136030_Search/checkpoint.json)
        echo "[$(date +%H:%M:%S)] Checkpoint: $CKPT" >> $LOG
    fi
    
    sleep 2
done

echo "[$(date +%H:%M:%S)] Wrapper finished" >> $LOG
