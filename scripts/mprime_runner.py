#!/usr/bin/env python3
"""Run mprime in a loop, report progress every minute."""
import subprocess
import time
import os
import sys

WORK = '/home/z/my-project/mprime/work'
LOG = '/home/z/my-project/scripts/mprime_runner.log'

def log(msg):
    with open(LOG, 'a') as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

env = os.environ.copy()
env['LD_LIBRARY_PATH'] = '/home/z/my-project/mprime'

log("=" * 60)
log("شروع اجرای mprime در پس‌زمینه")
log("=" * 60)

# Run 10 rounds of 9 minutes each
for i in range(1, 11):
    log(f"دور {i}/10 شروع شد")
    
    # Check if factor already found
    try:
        with open(f'{WORK}/results.txt') as f:
            content = f.read()
        if 'factor' in content.lower() and 'Found' in content:
            log("*** عامل پیدا شد! ***")
            log(content[-500:])
            break
    except:
        pass
    
    # Run mprime for 9 minutes
    try:
        result = subprocess.run(
            ['/home/z/my-project/mprime/mprime', '-d', f'-w{WORK}'],
            env=env,
            timeout=540,
            capture_output=True,
            text=True
        )
        log(f"دور {i} تموم شد (exit code: {result.returncode})")
    except subprocess.TimeoutExpired:
        log(f"دور {i} timeout شد (نرمال)")
    except Exception as e:
        log(f"دور {i} خطا: {e}")
    
    # Check results
    try:
        with open(f'{WORK}/results.txt') as f:
            content = f.read()
        # Get last result line
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        last = lines[-1] if lines else ""
        log(f"  آخرین نتیجه: {last}")
        
        if 'Found' in content or 'factor' in content.lower():
            log("*** عامل پیدا شد! ***")
            break
    except:
        pass
    
    # Check save file size
    try:
        size = os.path.getsize(f'{WORK}/e0001277')
        log(f"  save file size: {size} bytes")
    except:
        pass
    
    time.sleep(2)

log("=" * 60)
log("کار تموم شد")
log("=" * 60)
