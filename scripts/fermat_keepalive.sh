#!/bin/bash
# Keepalive wrapper: restarts Fermat if it dies, runs forever.
cd /home/z/my-project
while true; do
    if ! pgrep -f "fermat_bg.py" > /dev/null; then
        echo "[$(date)] Starting fermat_bg" >> logs/fermat_keepalive.log
        python3 scripts/fermat_bg.py >> logs/fermat_bg_stdout.log 2>&1 &
        disown $!
    fi
    sleep 30
done
