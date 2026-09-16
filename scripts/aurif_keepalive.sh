#!/bin/bash
# Wrapper to keep aurif_full running despite session disconnects
cd /home/z/my-project
while true; do
    if ! pgrep -f "aurif_full.py" > /dev/null; then
        echo "[$(date)] Restarting aurif_full" >> logs/aurif_wrapper.log
        nohup python3 -u scripts/aurif_full.py >> logs/aurif_full_stdout.log 2>&1 < /dev/null &
        disown $!
    fi
    sleep 30
done
