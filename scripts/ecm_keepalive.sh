#!/bin/bash
cd /home/z/my-project
while true; do
    if ! pgrep -f "ecm_bg2.py" > /dev/null; then
        echo "[$(date)] Restarting ecm_bg2" >> logs/ecm_keepalive2.log
        python3 scripts/ecm_bg2.py >> logs/ecm_bg2_stdout.log 2>&1 &
        disown $!
    fi
    sleep 30
done
