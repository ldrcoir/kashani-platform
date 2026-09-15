#!/bin/bash
# Eternal P-1 Launcher

F2="932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281119369604215535391846857906233364905825622441048803673998858526737"
ECM="/home/z/my-project/ecm-extract/usr/bin/ecm"
LD="/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"
WORKDIR="/home/z/my-project/A136030_eternal_pm1"
mkdir -p $WORKDIR

export LD_LIBRARY_PATH="$LD:$LD_LIBRARY_PATH"

echo "[$(date)] Eternal P-1 Launcher شروع شد" >> $WORKDIR/launcher.log

while true; do
    if ! pgrep -f "ecm -pm1.*$F2" > /dev/null 2>&1; then
        echo "[$(date)] شروع P-1..." >> $WORKDIR/launcher.log
        echo "$F2" | $ECM -pm1 -v -timestamp 1e11 >> $WORKDIR/pm1_output.log 2>&1 &
        PID=$!
        echo $PID > $WORKDIR/pm1.pid
        disown $PID 2>/dev/null
        echo "[$(date)] P-1 PID: $PID, B1=1e11" >> $WORKDIR/launcher.log
    fi
    
    if grep -q "Factor found" $WORKDIR/pm1_output.log 2>/dev/null; then
        echo "[$(date)] ✓✓✓ FACTOR FOUND!" >> $WORKDIR/launcher.log
        grep "Factor found" $WORKDIR/pm1_output.log >> $WORKDIR/FOUND_factors.txt
    fi
    
    sleep 60
done
