#!/bin/bash
cd /home/z/my-project/mprime/work
rm -f mprime.pid

# Loop: run mprime for 9 min, then check, repeat
for i in 1 2 3 4 5 6 7 8 9 10; do
    echo "[$(date +%H:%M:%S)] === دور $i شروع شد ===" >> /home/z/my-project/scripts/mprime_monitor.log
    LD_LIBRARY_PATH=/home/z/my-project/mprime timeout 540 /home/z/my-project/mprime/mprime -d -w/home/z/my-project/mprime/work > /tmp/mprime_round_${i}.log 2>&1
    echo "[$(date +%H:%M:%S)] === دور $i تموم شد ===" >> /home/z/my-project/scripts/mprime_monitor.log
    
    # Check if factor found
    if grep -q "factor" /home/z/my-project/mprime/work/results.txt 2>/dev/null; then
        echo "[$(date +%H:%M:%S)] !!! عامل پیدا شد !!!" >> /home/z/my-project/scripts/mprime_monitor.log
        grep -i "factor" /home/z/my-project/mprime/work/results.txt >> /home/z/my-project/scripts/mprime_monitor.log
        break
    fi
    
    # Status
    CURVES=$(grep "completed" /home/z/my-project/mprime/work/results.txt | tail -1)
    echo "[$(date +%H:%M:%S)] $CURVES" >> /home/z/my-project/scripts/mprime_monitor.log
    
    sleep 2
done
echo "[$(date +%H:%M:%S)] === کار تموم شد ===" >> /home/z/my-project/scripts/mprime_monitor.log
