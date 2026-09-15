#!/bin/bash
# Eternal ECM Launcher - هرگز نمی‌میره!
# این اسکریپت ECM رو روی F2 اجرا می‌کنه
# و اگه بمیره، دوباره شروع می‌کنه

F2="932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281119369604215535391846857906233364905825622441048803673998858526737"
ECM="/home/z/my-project/ecm-extract/usr/bin/ecm"
LD="/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu"
WORKDIR="/home/z/my-project/A136030_eternal_ecm"
mkdir -p $WORKDIR

export LD_LIBRARY_PATH="$LD:$LD_LIBRARY_PATH"

# لاگ
echo "[$(date)] Eternal ECM Launcher شروع شد" >> $WORKDIR/launcher.log

while true; do
    # بررسی آیا ECM در حال اجراست
    if ! pgrep -f "ecm.*$F2" > /dev/null 2>&1; then
        echo "[$(date)] شروع ECM..." >> $WORKDIR/launcher.log
        
        # ECM با B1=5e9
        echo "$F2" | $ECM -c 5000 -v -timestamp 5e9 >> $WORKDIR/ecm_output.log 2>&1 &
        ECM_PID=$!
        echo $ECM_PID > $WORKDIR/ecm.pid
        disown $ECM_PID 2>/dev/null
        echo "[$(date)] ECM PID: $ECM_PID, B1=5e9, 5000 curves" >> $WORKDIR/launcher.log
    fi
    
    # بررسی FOUND
    if grep -q "Factor found" $WORKDIR/ecm_output.log 2>/dev/null; then
        echo "[$(date)] ✓✓✓ FACTOR FOUND!" >> $WORKDIR/launcher.log
        grep "Factor found" $WORKDIR/ecm_output.log >> $WORKDIR/FOUND_factors.txt
    fi
    
    sleep 60
done
