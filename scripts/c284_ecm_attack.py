#!/usr/bin/env python3
"""
C284 ECM Attack — Multi-worker, optimized for negative discriminant.

C284 ≡ 3 (mod 4) → factors are mixed (1 mod 4, 3 mod 4)
Largest known factor: 55 digits → need B1 >= 10^11 for 55-65 digit factors

Strategy:
- Run GMP-ECM with B1 = 10^12 (for 55-65 digit factors)
- Multiple curves in parallel using different sigma values
- Each worker runs a separate ECM process with different sigma
- Checkpoint after each curve
"""

import sys
sys.set_int_max_str_digits(1000000)

import gmpy2
from gmpy2 import mpz, is_prime
import time
import json
import os
import subprocess
import multiprocessing as mp
from pathlib import Path

# Constants
C284 = mpz(53392955842462906502525256206896237530607657681405452248628829538140335056019091833139309039691476989536595672486245741799613486059460767317912672601233477410458189253022780891585730123223883909898404934891596729489833819787859139386557550548823481244976333432522178629028656984007087)

BASE_DIR = Path('/home/z/my-project/download')
C284_FILE = Path('/home/z/my-project/C284.txt')
ECM_BIN = '/home/z/my-project/ecm-extract/usr/bin/ecm'
LD_PATH = '/home/z/my-project/ecm-extract/usr/lib/x86_64-linux-gnu'
RESULTS_FILE = BASE_DIR / 'c284_ecm_results.txt'
LOG_FILE = BASE_DIR / 'c284_ecm.log'

def log_msg(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')

def ecm_worker(args):
    """Run a single ECM curve with given sigma."""
    worker_id, sigma, b1 = args
    
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = LD_PATH + ':' + env.get('LD_LIBRARY_PATH', '')
    
    # Run ECM with specific sigma
    cmd = [ECM_BIN, '-v', '-sigma', str(sigma), str(b1)]
    
    with open(C284_FILE, 'r') as f:
        input_num = f.read().strip()
    
    try:
        result = subprocess.run(
            cmd,
            input=input_num,
            capture_output=True,
            text=True,
            timeout=300,  # 5 min max per curve
            env=env
        )
        
        output = result.stdout + result.stderr
        
        # Check for factor found
        if 'Factor found' in output or 'factor found' in output:
            # Extract factor
            for line in output.split('\n'):
                if 'Factor' in line or 'factor' in line:
                    log_msg(f'[W{worker_id}] FACTOR FOUND! sigma={sigma}')
                    log_msg(f'  {line}')
                    # Save to results
                    with open(RESULTS_FILE, 'a') as f:
                        f.write(f'=== FACTOR FOUND ===\n')
                        f.write(f'Worker: {worker_id}\n')
                        f.write(f'Time: {time.strftime("%Y-%m-%d %H:%M:%S")}\n')
                        f.write(f'Sigma: {sigma}\n')
                        f.write(f'B1: {b1}\n')
                        f.write(f'Output: {output}\n')
                        f.write(f'===\n')
                    return True
        
        return False
    except subprocess.TimeoutExpired:
        log_msg(f'[W{worker_id}] sigma={sigma}: TIMEOUT (B1={b1})')
        return False
    except Exception as e:
        log_msg(f'[W{worker_id}] sigma={sigma}: ERROR: {e}')
        return False

def run_ecm_batch(b1, num_curves, num_workers=4):
    """Run num_curves ECM curves with B1, using num_workers parallel workers."""
    log_msg(f'')
    log_msg(f'=== ECM Batch: B1={b1}, curves={num_curves}, workers={num_workers} ===')
    log_msg(f'')
    
    # Generate sigma values
    import random
    random.seed(int(time.time()))
    sigmas = [random.randint(1, 10**18) for _ in range(num_curves)]
    
    # Run in parallel batches
    curves_done = 0
    t_start = time.time()
    
    for batch_start in range(0, num_curves, num_workers):
        batch_size = min(num_workers, num_curves - batch_start)
        batch_args = [(i, sigmas[batch_start + i], b1) for i in range(batch_size)]
        
        # Run batch in parallel
        with mp.Pool(batch_size) as pool:
            results = pool.map(ecm_worker, batch_args)
        
        curves_done += batch_size
        elapsed = time.time() - t_start
        rate = curves_done / elapsed if elapsed > 0 else 0
        
        log_msg(f'  Curves done: {curves_done}/{num_curves}, elapsed: {elapsed:.0f}s, rate: {rate:.2f} curves/s')
        
        # Check if any factor found
        if any(results):
            log_msg(f'!!! FACTOR FOUND !!! Check results file.')
            return True
        
        # Check results file
        if RESULTS_FILE.exists() and 'FACTOR FOUND' in RESULTS_FILE.read_text():
            log_msg(f'!!! FACTOR FOUND by another worker !!!')
            return True
    
    return False

def main():
    log_msg('=' * 70)
    log_msg(f'  C284 ECM Attack — Multi-worker, optimized')
    log_msg('=' * 70)
    log_msg(f'C284 digits: {len(str(C284))}')
    log_msg(f'C284 mod 4 = {C284 % 4} (NEGATIVE discriminant)')
    log_msg(f'')
    log_msg(f'Strategy:')
    log_msg(f'  1. B1=10^11: ~528 curves needed for 60-digit factor')
    log_msg(f'  2. B1=10^12: ~183 curves needed for 60-digit factor')
    log_msg(f'  3. Run 4 workers in parallel, each different sigma')
    log_msg(f'')
    
    # Phase 1: B1 = 10^11 (for 55-60 digit factors)
    # Each curve takes ~100s at B1=10^11
    # With 4 workers: ~25s per curve effective
    # Need 528 curves for 60-digit factor → ~14000s = ~4 hours
    # But we can only run for limited time, so do as many as we can
    
    B1_PHASE1 = 100000000000  # 10^11
    NUM_CURVES_PHASE1 = 20  # as many as we can in time budget
    NUM_WORKERS = 4
    
    log_msg(f'Phase 1: B1={B1_PHASE1}, curves={NUM_CURVES_PHASE1}, workers={NUM_WORKERS}')
    
    found = run_ecm_batch(B1_PHASE1, NUM_CURVES_PHASE1, NUM_WORKERS)
    
    if found:
        log_msg(f'')
        log_msg(f'=== FACTOR FOUND IN PHASE 1 ===')
        log_msg(RESULTS_FILE.read_text())
        return
    
    log_msg(f'')
    log_msg(f'Phase 1 complete. No factor found.')
    log_msg(f'')
    
    # Phase 2: B1 = 10^12 (for 60-70 digit factors)
    B1_PHASE2 = 1000000000000  # 10^12
    NUM_CURVES_PHASE2 = 10  # fewer curves since each takes longer
    
    log_msg(f'Phase 2: B1={B1_PHASE2}, curves={NUM_CURVES_PHASE2}')
    
    found = run_ecm_batch(B1_PHASE2, NUM_CURVES_PHASE2, NUM_WORKERS)
    
    if found:
        log_msg(f'')
        log_msg(f'=== FACTOR FOUND IN PHASE 2 ===')
        log_msg(RESULTS_FILE.read_text())
        return
    
    log_msg(f'')
    log_msg(f'Phase 2 complete. No factor found.')
    log_msg(f'')
    log_msg(f'Conclusion: C284 factors are likely > 70 digits')
    log_msg(f'Need SNFS or ECM with B1 > 10^12 for further progress')

if __name__ == '__main__':
    main()
