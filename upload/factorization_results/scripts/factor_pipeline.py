#!/usr/bin/env python3.13
"""
Best-effort factorization pipeline for the 125 challenge numbers.
2-worker async scheduler driving GMP-ECM (P-1, P+1, ECM ladder).

GMP-ECM -q semantics (per man page): for each input number ONE line is printed:
  "<found factors...> <remaining cofactor>"  (if nothing found, the input itself)
=> last token of the line is ALWAYS the remaining cofactor, never a new find.

State persisted after every completion -> resumable. Run in FOREGROUND chunks.
"""
import json, os, subprocess, time, traceback, sys
from concurrent.futures import ProcessPoolExecutor, FIRST_COMPLETED, wait
from gmpy2 import mpz, is_prime

ECM = "/home/z/my-project/work/ecmroot/usr/bin/ecm"
ECMENV = dict(os.environ, LD_LIBRARY_PATH="/home/z/my-project/work/ecmroot/usr/lib/x86_64-linux-gnu")
WORK = "/home/z/my-project/work/factor"
STATE_F = f"{WORK}/state.json"
NUMBERS_F = "/home/z/my-project/work/numbers.json"
BUDGET_SEC = float(os.environ.get("BUDGET_SEC", "540"))
DEADLINE = time.time() + BUDGET_SEC
NW = 2

os.makedirs(WORK, exist_ok=True)

with open(NUMBERS_F) as f:
    RAW = json.load(f)
NUMS = {}
for fid, d in RAW.items():
    for i, s in enumerate(d["numbers"]):
        n = mpz(s)
        NUMS[f"{fid}:{i}"] = {"n": n, "digits": len(str(n)), "k": d["k"], "fid": fid, "idx": i}

def load_state():
    if os.path.exists(STATE_F):
        with open(STATE_F) as f:
            return json.load(f)
    return {}

def save_state(st):
    tmp = STATE_F + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
    os.replace(tmp, STATE_F)

def cofactor(key, st):
    c = NUMS[key]["n"]
    for fs in st.get(key, {}).get("factors", []):
        p = mpz(fs)
        while c % p == 0:
            c //= p
    return c

def all_prime(flist):
    return all(is_prime(mpz(f)) for f in flist)

def prod(flist):
    r = mpz(1)
    for f in flist:
        r *= mpz(f)
    return r

def is_full(key, st):
    fl = st.get(key, {}).get("factors", [])
    return bool(fl) and all_prime(fl) and prod(fl) == NUMS[key]["n"]

# ---------- worker-side ----------
def task_batch(job):
    piece, mode = job["piece"], job["mode"]
    if mode == "pm1":
        args = ["-pm1", str(job["B1"])]
    elif mode == "pp1":
        args = ["-pp1", str(job["B1"]), "-x", str(job["seed"])]
    else:
        args = ["-c", str(job["curves"]), str(job["B1"])]
    try:
        proc = subprocess.Popen([ECM, "-q"] + args, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                env=ECMENV, text=True)
        try:
            out, _ = proc.communicate(input=piece + "\n", timeout=job["budget"])
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                out, _ = proc.communicate(timeout=15)
            except Exception:
                out = ""
    except Exception:
        return job, []
    return job, out

# ---------- main ----------
def main():
    st = load_state()
    for key in NUMS:
        e = st.setdefault(key, {"factors": [], "lvl": 0, "lvl_done": 0, "pm1": 0, "pp1": 0})
        e["factors"] = [f for f in e.get("factors", []) if NUMS[key]["n"] % mpz(f) == 0]
    save_state(st)
    t0 = time.time()
    jobs_done = 0
    print(f"Start. Deadline in {BUDGET_SEC:.0f}s, workers={NW}, numbers={len(NUMS)}", flush=True)

    LADDER = [(250_000, 120, 600), (1_000_000, 150, 900),
              (3_000_000, 200, 1400), (11_000_000, 250, 2000)]

    def prio(key):
        # group by number-of-factors first (triples most crackable), then size
        return (NUMS[key]["k"], NUMS[key]["digits"])

    def add_factor(key, fstr, st, src):
        p = mpz(fstr)
        if p <= 1 or NUMS[key]["n"] % p != 0:
            return False
        if fstr in st[key]["factors"]:
            return False
        st[key]["factors"].append(fstr)
        tag = "FULL!" if is_full(key, st) else ""
        print(f"    -> {key} [{src}]: factor {len(fstr)}d "
              f"{'prime' if is_prime(p) else 'COMPOSITE(will split)'} {tag}", flush=True)
        return True

    recent_piece = {}   # piece string -> last attempt ts (avoid spin)

    def next_task():
        now = time.time()
        def fresh(p):
            return now - recent_piece.get(p, 0) > 90
        # 0) split composite recorded factors (cheap, high value)
        for key in sorted(NUMS, key=prio):
            for f in st[key]["factors"]:
                if not is_prime(mpz(f)) and fresh(f):
                    return {"key": key, "piece": f, "mode": "ecm", "B1": 250_000,
                            "curves": 300, "budget": 400, "split": f}
        # 1) lottery pass on all numbers
        for key in sorted(NUMS, key=prio):
            c = cofactor(key, st)
            if c <= 1 or is_prime(c):
                continue
            e = st[key]
            if e["pm1"] < 1:
                e["pm1"] = 1
                return {"key": key, "piece": str(c), "mode": "pm1", "B1": 10_000_000, "budget": 150}
            if e["pp1"] < 2:
                e["pp1"] += 1
                return {"key": key, "piece": str(c), "mode": "pp1", "B1": 10_000_000,
                        "seed": 2 + e["pp1"] * 7, "budget": 150}
        # 2) ECM ladder in priority order
        for key in sorted(NUMS, key=prio):
            c = cofactor(key, st)
            if c <= 1 or is_prime(c):
                continue
            e = st[key]
            pos = e["lvl"]
            if pos >= len(LADDER):
                continue
            B1, chunk, level_budget = LADDER[pos]
            if e["lvl_done"] >= level_budget:
                e["lvl"] = pos + 1
                e["lvl_done"] = 0
                continue
            digits = NUMS[key]["digits"]
            est = 0.55 * (B1 / 250_000) ** 1.15 * (digits / 100.0) ** 1.5
            left = DEADLINE - time.time()
            budget = min(max(est * chunk * 2.5, 25), max(left - 2, 8))
            return {"key": key, "piece": str(c), "mode": "ecm", "B1": B1,
                    "curves": chunk, "budget": budget}
        return None

    in_flight = {}
    with ProcessPoolExecutor(max_workers=NW) as ex:
        while time.time() < DEADLINE - 2:
            while len(in_flight) < NW and time.time() < DEADLINE - 2:
                job = next_task()
                if job is None:
                    time.sleep(3)
                    break
                recent_piece[job["piece"]] = time.time()
                f = ex.submit(task_batch, job)
                in_flight[f] = job
            if not in_flight:
                continue
            done, _ = wait(list(in_flight), timeout=15, return_when=FIRST_COMPLETED)
            for f in done:
                job = in_flight.pop(f)
                _, out = f.result()
                jobs_done += 1
                key = job["key"]
                e = st[key]
                piece = mpz(job["piece"])
                if job["mode"] == "ecm" and "split" not in job:
                    e["lvl_done"] += job["curves"]
                # parse: last token of the (single-line) output is the remaining cofactor
                toks = []
                for line in (out or "").splitlines():
                    ts = [t for t in line.split() if t.isdigit()]
                    if ts:
                        toks.extend(ts)
                if toks:
                    found_pieces, leftover = toks[:-1], mpz(toks[-1])
                    if "split" in job:
                        comp = job["split"]
                        got_new = False
                        for fstr in found_pieces:
                            if mpz(fstr) > 1 and piece % mpz(fstr) == 0:
                                if comp in e["factors"]:
                                    e["factors"].remove(comp)
                                got_new |= add_factor(key, fstr, st, f"split B1={job['B1']}")
                        if leftover < piece and is_prime(leftover) and NUMS[key]["n"] % leftover == 0:
                            if comp in e["factors"]:
                                e["factors"].remove(comp)
                            got_new |= add_factor(key, str(leftover), st, f"split-left B1={job['B1']}")
                    else:
                        for fstr in found_pieces:
                            if mpz(fstr) > 1 and piece % mpz(fstr) == 0:
                                add_factor(key, fstr, st, f"{job['mode']} B1={job.get('B1','-')}")
                        if leftover < piece and is_prime(leftover) and NUMS[key]["n"] % leftover == 0:
                            add_factor(key, str(leftover), st, f"{job['mode']}-left B1={job.get('B1','-')}")
                # generic: append prime cofactor whenever complete
                c = cofactor(key, st)
                if c > 1 and is_prime(c):
                    add_factor(key, str(c), st, "cofactor-prime")
                if jobs_done % 10 == 0:
                    full = sum(1 for k in NUMS if is_full(k, st))
                    print(f"  ..heartbeat {time.time()-t0:.0f}s jobs={jobs_done} FULL={full}", flush=True)
                save_state(st)
            for key in NUMS:
                e = st[key]
                if e["lvl"] < len(LADDER) and e["lvl_done"] >= LADDER[e["lvl"]][2]:
                    e["lvl"] += 1
                    e["lvl_done"] = 0

    save_state(st)
    full = sum(1 for k in NUMS if is_full(k, st))
    partial = sum(1 for k in NUMS if st[k]["factors"] and not is_full(k, st))
    print(f"\nCHUNK DONE in {time.time()-t0:.0f}s, jobs={jobs_done} — FULL: {full}, "
          f"PARTIAL: {partial}, UNFACTORED: {len(NUMS)-full-partial}", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception:
        with open("/home/z/my-project/work/factor/crash.log", "w") as f:
            f.write(traceback.format_exc())
        raise
