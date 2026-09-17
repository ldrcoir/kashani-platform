#!/bin/bash
# Eternal ECM Launcher v2 - فقط یک نمونه
F2="932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281119369604215535391846857906233364905825622441048803673998858526737"
ECM="/home/z/my-project/ecm-extract/usr/bin/ecm"
LD="/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"
WORKDIR="/home/z/my-project/A136030_eternal_ecm"
mkdir -p $WORKDIR
export LD_LIBRARY_PATH="$LD:$LD_LIBRARY_PATH"

echo "[$(date)] Launcher v2 شروع شد" >> $WORKDIR/launcher.log

# فقط یک نمونه ECM - B1=1e10 (برای فاکتور 55-60 رقمی)
echo "$F2" | $ECM -c 10000 -v -timestamp 1e10 >> $WORKDIR/ecm_output.log 2>&1 &
ECM_PID=$!
echo $ECM_PID > $WORKDIR/ecm.pid
disown $ECM_PID 2>/dev/null
echo "[$(date)] ECM PID: $ECM_PID, B1=1e10, 10000 curves" >> $WORKDIR/launcher.log

# فقط چک کن - restart نکن
while true; do
    if ! kill -0 $ECM_PID 2>/dev/null; then
        echo "[$(date)] ECM تموم شد، restart..." >> $WORKDIR/launcher.log
        echo "$F2" | $ECM -c 10000 -v -timestamp 1e10 >> $WORKDIR/ecm_output.log 2>&1 &
        ECM_PID=$!
        echo $ECM_PID > $WORKDIR/ecm.pid
        disown $ECM_PID 2>/dev/null
        echo "[$(date)] ECM PID: $ECM_PID" >> $WORKDIR/launcher.log
    fi
    
    # بررسی FOUND
    if grep -q "Factor found" $WORKDIR/ecm_output.log 2>/dev/null; then
        echo "[$(date)] ✓✓✓ FACTOR FOUND!" >> $WORKDIR/launcher.log
        grep "Factor found" $WORKDIR/ecm_output.log >> $WORKDIR/FOUND_factors.txt
    fi
    
    sleep 120
done
