#!/bin/bash
cd /home/z/my-project
for i in 1 2 3 4 5 6 7 8 9 10; do
    echo "=== Attempt $i ===" >> /tmp/restart_log.txt
    date >> /tmp/restart_log.txt
    timeout 55 python3 scripts/fill_missing.py >> /tmp/fill_missing.out 2>&1
    echo "Exit code: $?" >> /tmp/restart_log.txt
    sleep 2
done
