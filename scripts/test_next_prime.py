import sys
sys.set_int_max_str_digits(1000000)
import gmpy2
from gmpy2 import mpz, is_prime, powmod
import time
import pickle
import multiprocessing as mp

P = 1237
TWO_P = 2474
M = mpz(2)**P - 1
P70 = mpz("2538207129840687799335203259492870476186248896616401346500027311795983")
C303 = M // P70

WHEEL_MOD = 4849845
with open('/home/z/my-project/download/good_residues.pkl', 'rb') as f:
    GOOD_RESIDUES = pickle.load(f)

def gen_extra_rules(bound):
    sieve = bytearray([1]) * (bound + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(bound**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    primes = [i for i in range(2, bound + 1) if sieve[i]]
    rules = []
    for r in primes:
        if r == 2 or r == 1237: continue
        if r in [3,5,7,11,13,17,19]: continue
        inv_2474 = pow(TWO_P, -1, r)
        blocked = (-inv_2474) % r
        rules.append((r, blocked))
    return rules

EXTRA_RULES = gen_extra_rules(1000)

def test_worker(args):
    """Try a different strategy: use next_prime to jump directly to primes."""
    worker_id, k_start, k_end, stop_event = args
    good_set = set(GOOD_RESIDUES)
    rules = EXTRA_RULES
    
    # Use gmpy2.next_prime to jump from one prime to the next
    # Start: q = 2474*k_start + 1
    q_start = TWO_P * k_start + 1
    q_end = TWO_P * k_end + 1
    
    local_tested = 0
    local_primes = 0
    q = gmpy2.next_prime(q_start - 1)  # next prime >= q_start
    
    while int(q) < q_end and not stop_event.is_set():
        local_primes += 1
        # Check q ≡ 1 mod 2474
        q_int = int(q)
        if (q_int - 1) % TWO_P == 0:
            k = (q_int - 1) // TWO_P
            # Check wheel
            if (k % WHEEL_MOD) in good_set:
                # Already prime, just check pow
                local_tested += 1
                if powmod(2, P, q_int) == 1:
                    if C303 % q_int == 0:
                        print(f"FACTOR! k={k}, q={q_int}", flush=True)
                        stop_event.set()
                        return
        # Jump to next prime
        q = gmpy2.next_prime(q)
    
    print(f"[W{worker_id}] DONE: primes={local_primes:,}, tested={local_tested:,}", flush=True)

if __name__ == '__main__':
    NUM_WORKERS = 2
    K_START = 15_000_000
    K_END = 15_000_000 + 200_000  # 200k total
    
    chunk = (K_END - K_START) // NUM_WORKERS
    
    ctx = mp.get_context('fork')
    workers = []
    manager = mp.Manager()
    stop_event = manager.Event()
    
    t0 = time.time()
    for i in range(NUM_WORKERS):
        w_start = K_START + i * chunk
        w_end = K_END if i == NUM_WORKERS - 1 else w_start + chunk
        args = (i, w_start, w_end, stop_event)
        p = ctx.Process(target=test_worker, args=(args,))
        p.start()
        workers.append(p)
    
    for p in workers:
        p.join()
    
    elapsed = time.time() - t0
    print(f"2 workers, 1M k total, elapsed={elapsed:.1f}s, rate={1_000_000/elapsed:.0f} k/s combined")
    print(f"Extrapolated time to k=100B: {(100_000_000_000 - 15_000_000) / (1_000_000/elapsed):.0f}s = {(100_000_000_000 - 15_000_000) / (1_000_000/elapsed) / 3600:.1f} hours")
