#!/bin/bash
cd /home/z/my-project
while true; do
    if ! pgrep -f "fermat_bg.py" > /dev/null; then
        echo "[$(date)] Restarting fermat" >> logs/fermat_keepalive.log
        python3 scripts/fermat_bg.py >> logs/fermat_bg_stdout.log 2>&1 &
        disown $!
    fi
    sleep 30
done
