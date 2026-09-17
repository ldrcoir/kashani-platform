#!/bin/bash
# Keepalive for both Fermat and ECM
cd /home/z/my-project
while true; do
    if ! pgrep -f "ecm_bg.py" > /dev/null; then
        echo "[$(date)] Restarting ecm_bg" >> logs/ecm_keepalive.log
        python3 scripts/ecm_bg.py >> logs/ecm_bg_stdout.log 2>&1 &
        disown $!
    fi
    sleep 30
done
