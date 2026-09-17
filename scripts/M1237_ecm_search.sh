#!/bin/bash
# جستجوی ECM پس‌زمینه برای ف2 (303 رقم)
# استراتژی: اجرای متناوب با B1 های مختلف
# - B1=1e6: برای فاکتورهای 25-30 رقمی
# - B1=1e7: برای فاکتورهای 30-35 رقمی
# - B1=1e8: برای فاکتورهای 35-40 رقمی
# - B1=1e9: برای فاکتورهای 40-45 رقمی
# هر بار 1000 منحنی تست می‌کنیم

WORKDIR=/home/z/my-project/A136030_ECM_M1237
mkdir -p $WORKDIR

ECM=/home/z/my-project/ecm-extract/usr/bin/ecm
export LD_LIBRARY_PATH=/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

F2="932346997627937198512116805585638652223533192516806816522982865866804199262267590070758266268742758283545150004345986721379992894347882545052483695173645594473520682900937642680132877292150643356579486299211525438560741941531670625397281199369604215535391846857906233364905825622441048803673998858526737"

# استراتژی B1 - شروع از کوچک و بزرگ‌تر شدن
B1_VALUES=("1e6" "5e6" "1e7" "5e7" "1e8" "5e8" "1e9")
CURVES_PER_B1=500

PID_FILE=$WORKDIR/ecm.pid
LOG_FILE=$WORKDIR/ecm.log
FOUND_FILE=$WORKDIR/FOUND_factors.txt
PROGRESS_FILE=$WORKDIR/progress.txt
STATE_FILE=$WORKDIR/state.json

# تابع لاگ
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> $LOG_FILE
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "شروع جستجوی ECM برای F2 (303 رقم)"
log "F2 = $F2"
log ""

# ذخیره F2 در فایل برای ورودی ECM
echo "$F2" > $WORKDIR/input.txt

# حلقه اصلی - اجرای متناوب با B1 های مختلف
TOTAL_CURVES=0
START_TIME=$(date +%s)

while true; do
    for B1 in "${B1_VALUES[@]}"; do
        # بارگذاری state
        if [ -f "$STATE_FILE" ]; then
            CURRENT_B1=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('current_b1', '1e6'))")
            CURRENT_CURVE=$(python3 -c "import json; print(json.load(open('$STATE_FILE')).get('current_curve', 0))")
        else
            CURRENT_B1="1e6"
            CURRENT_CURVE=0
        fi
        
        # اگه B1 فعلی کمتر از B1 مورد نظر هست، skip کن
        # (برای resume)
        B1_INDEX=0
        for i in "${!B1_VALUES[@]}"; do
            if [ "${B1_VALUES[$i]}" = "$CURRENT_B1" ]; then
                B1_INDEX=$i
                break
            fi
        done
        
        log "=== اجرای ECM با B1=$B1، 500 منحنی ==="
        
        # اجرای ECM
        # -c 500: 500 منحنی
        # -v: verbose
        # -timestamp: timestamp در خروجی
        # B2 به‌صورت پیش‌فرض 100*B1
        START_CURVE=$CURRENT_CURVE
        
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] B1=$B1 starting curve $CURRENT_CURVE" >> $PROGRESS_FILE
        
        # اجرای ECM و ذخیره خروجی
        $ECM -c $CURVES_PER_B1 -v -timestamp $B1 < $WORKDIR/input.txt > $WORKDIR/ecm_run_$B1.log 2>&1 &
        ECM_PID=$!
        echo $ECM_PID > $PID_FILE
        
        # منتظر تموم شدن یا پیدا شدن فاکتور
        while kill -0 $ECM_PID 2>/dev/null; do
            sleep 30
            
            # چک کردن آیا فاکتور پیدا شده
            if grep -q "Factor found" $WORKDIR/ecm_run_$B1.log 2>/dev/null; then
                log "✓✓✓ فاکتور پیدا شد با B1=$B1!"
                grep "Factor found" $WORKDIR/ecm_run_$B1.log >> $FOUND_FILE
                grep "found" $WORKDIR/ecm_run_$B1.log >> $FOUND_FILE
                # ذخیره کل خروجی
                cp $WORKDIR/ecm_run_$B1.log $WORKDIR/FOUND_full_log_$B1.txt
                break 2
            fi
            
            # به‌روزرسانی progress
            CURVES_DONE=$(grep -c "Run\|curves" $WORKDIR/ecm_run_$B1.log 2>/dev/null || echo "0")
            ELAPSED=$(($(date +%s) - START_TIME))
            
            echo "[$(date '+%Y-%m-%d %H:%M:%S')] B1=$B1, elapsed=${ELAPSED}s, total_curves=$TOTAL_CURVES" > $PROGRESS_FILE
        done
        
        wait $ECM_PID 2>/dev/null
        
        # به‌روزرسانی state
        TOTAL_CURVES=$((TOTAL_CURVES + CURVES_PER_B1))
        NEXT_B1_INDEX=$((B1_INDEX + 1))
        if [ $NEXT_B1_INDEX -ge ${#B1_VALUES[@]} ]; then
            NEXT_B1_INDEX=0
        fi
        NEXT_B1=${B1_VALUES[$NEXT_B1_INDEX]}
        
        python3 -c "
import json
state = {
    'current_b1': '$NEXT_B1',
    'current_curve': 0,
    'total_curves': $TOTAL_CURVES,
    'last_b1_done': '$B1',
    'last_update': '$(date \"+%Y-%m-%d %H:%M:%S\")'
}
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
        
        log "تمام $B1 - total curves: $TOTAL_CURVES"
        
        # اگه فاکتور پیدا شده، خارج شو
        if [ -f "$FOUND_FILE" ] && [ -s "$FOUND_FILE" ]; then
            log "فاکتور پیدا شد! خروج."
            exit 0
        fi
    done
done
