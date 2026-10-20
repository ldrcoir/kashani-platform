#!/usr/bin/env python3
"""
🖥️ نرم‌افزار پردازشی پلتفرم علمی چندرشته‌ای پارسی
=============================================
نرم‌افزار دسکتاپ برای مشارکت در پردازش‌های علمی.

ویژگی‌ها:
  - GUI با tkinter (cross-platform)
  - جمع‌آوری مشخصات سیستم (CPU, RAM, GPU, disk)
  - اتصال به سرور برای گرفتن کار
  - اجرای کار و ثبت credit
  - نمایش زنده‌ی آمار
  - چندسکویی (ویندوز، مک، لینوکس)
  - اجرا در پس‌زمینه

اجرا:
    python3 volunteer_app.py
یا:
    python3 volunteer_app.py --server https://platform-oloom.ir --api-key YOUR_KEY

ساخت executable:
    pip install pyinstaller
    pyinstaller --onefile --windowed volunteer_app.py
"""
import sys
import os
import time
import json
import threading
import platform
import subprocess
import socket
import urllib.request
import urllib.error
from datetime import datetime
from multiprocessing import cpu_count

# Optional: psutil for accurate system info
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Optional: tkinter for GUI
try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext, simpledialog
    HAS_TK = True
except ImportError:
    HAS_TK = False


VERSION = "1.0.0"
APP_NAME = "پلتفرم علمی چندرشته‌ای پارسی"
APP_DEDICATED = "به افتخار غیاث‌الدین جمشید کاشانی"


# ============================================================
# جمع‌آوری مشخصات سیستم
# ============================================================
def collect_system_specs():
    """جمع‌آوری مشخصات سخت‌افزاری سیستم"""
    specs = {
        'cpu': {'model': platform.processor() or 'Unknown', 'cores': cpu_count(), 'threads': cpu_count()},
        'ram': {'total_mb': 0, 'available_mb': 0},
        'disk': {'total_gb': 0, 'free_gb': 0, 'type': 'unknown'},
        'gpu': {'model': None, 'vram_mb': 0, 'cuda': False},
        'os': {'name': platform.system(), 'version': platform.version(), 'arch': platform.machine()},
        'network': {'internet_speed_mbps': 100},
    }
    
    if HAS_PSUTIL:
        vm = psutil.virtual_memory()
        specs['ram']['total_mb'] = vm.total // 1024 // 1024
        specs['ram']['available_mb'] = vm.available // 1024 // 1024
        try:
            disk = psutil.disk_usage('/')
            specs['disk']['total_gb'] = disk.total // 1024 // 1024 // 1024
            specs['disk']['free_gb'] = disk.free // 1024 // 1024 // 1024
        except:
            pass
    
    # Detect GPU on Linux
    if platform.system() == 'Linux':
        try:
            r = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                             capture_output=True, text=True, timeout=5)
            if r.returncode == 0 and r.stdout.strip():
                parts = r.stdout.strip().split(',')
                specs['gpu']['model'] = parts[0].strip()
                if len(parts) > 1:
                    specs['gpu']['vram_mb'] = int(parts[1].strip())
                specs['gpu']['cuda'] = True
        except:
            pass
        # Try lspci
        if not specs['gpu']['model']:
            try:
                r = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                for line in r.stdout.split('\n'):
                    if 'VGA' in line or '3D' in line:
                        specs['gpu']['model'] = line.split(':')[-1].strip()[:200]
                        if 'nvidia' in line.lower():
                            specs['gpu']['cuda'] = True
                        break
            except:
                pass
    
    return specs


# ============================================================
# محاسبات محلی (در صورت قطع اتصال به سرور)
# ============================================================
def is_prime(n):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True


def pollard_rho(n):
    """فاکتور کردن با Pollard Rho"""
    if n < 2 or is_prime(n): return None
    if n % 2 == 0: return 2
    x, y, d = 2, 2, 1
    while d == 1:
        x = (x * x + 1) % n
        y = (y * y + 1) % n
        y = (y * y + 1) % n
        diff = abs(x - y)
        if diff == 0:
            return None
        d = gcd(diff, n)
    return d if d != n else None


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def factor(n):
    """فاکتور کردن کامل"""
    if n < 2: return []
    if is_prime(n): return [n]
    factors = []
    # Trial division
    for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]:
        while n % p == 0:
            factors.append(p)
            n //= p
    if n == 1:
        return sorted(factors)
    # Pollard rho
    stack = [n]
    while stack:
        m = stack.pop()
        if m < 2: continue
        if is_prime(m):
            factors.append(m)
            continue
        d = pollard_rho(m)
        if d is None:
            factors.append(m)
        else:
            stack.append(d)
            stack.append(m // d)
    return sorted(factors)


# ============================================================
# اجرای کار (work types)
# ============================================================
def execute_work(work_type, payload):
    """اجرای یک کار"""
    if work_type in ('factor_small', 'factor_medium', 'factor_large'):
        n = int(payload.get('number', 0))
        if n < 2: return {'error': 'invalid number'}
        factors = factor(n)
        return {'number': str(n), 'factors': factors, 'verified': __import__('functools').reduce(lambda a,b: a*b, factors, 1) == n}
    
    elif work_type == 'prime_hunt':
        start = int(payload.get('range_start', 1))
        end = int(payload.get('range_end', 1000000))
        primes = []
        for n in range(start, min(end, start + 1000000)):
            if is_prime(n):
                primes.append(n)
                if len(primes) >= 100:
                    break
        return {'primes': primes, 'count': len(primes), 'range': [start, end]}
    
    elif work_type == 'mersenne_check':
        p = int(payload.get('exponent', 13))
        if p > 25: return {'error': 'exponent too large'}
        m = (1 << p) - 1
        return {'exponent': p, 'mersenne': str(m), 'is_prime': is_prime(m)}
    
    elif work_type == 'benchmark':
        # Local benchmark
        start_time = time.time()
        primes_count = sum(1 for n in range(2, 100000) if is_prime(n))
        elapsed = time.time() - start_time
        return {'primes_found': primes_count, 'elapsed_seconds': elapsed, 'rate_per_second': 100000 / elapsed}
    
    elif work_type == 'data_analysis':
        data = payload.get('data', [])
        if not data:
            return {'mean': 0, 'count': 0}
        n = len(data)
        mean = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / n
        return {
            'count': n, 'mean': mean, 'std_dev': variance ** 0.5,
            'min': min(data), 'max': max(data)
        }
    
    return {'result': 'executed', 'work_type': work_type}


# ============================================================
# API Client
# ============================================================
class ApiClient:
    def __init__(self, server_url, api_key=None, node_token=None):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.node_token = node_token
        self.node_id = None
    
    def http_request(self, path, data=None, headers=None):
        url = self.server_url + path
        if data is not None:
            body = json.dumps(data).encode('utf-8')
        else:
            body = None
        h = {'Content-Type': 'application/json'}
        if self.api_key:
            h['X-API-Key'] = self.api_key
        if self.node_token:
            h['X-Node-Token'] = self.node_token
        if headers:
            h.update(headers)
        req = urllib.request.Request(url, data=body, headers=h, method='POST' if data else 'GET')
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            return {'error': f'HTTP {e.code}: {e.read().decode("utf-8", errors="ignore")[:200]}'}
        except Exception as e:
            return {'error': str(e)}
    
    def register_node(self, node_name, specs, prefs):
        data = {'node_name': node_name, 'specs': specs, 'preferences': prefs}
        result = self.http_request('/api/work/register', data)
        if result.get('success'):
            self.node_id = result.get('node_id')
            self.node_token = result.get('assigned_token')
        return result
    
    def heartbeat(self, current_specs):
        return self.http_request('/api/work/heartbeat', {'node_id': self.node_id, 'current_specs': current_specs})
    
    def get_next_task(self, current_specs):
        return self.http_request('/api/work/next', {'node_id': self.node_id, 'current_specs': current_specs})
    
    def submit_result(self, task_id, result, time_taken, errors=None):
        return self.http_request('/api/work/submit', {
            'task_id': task_id, 'node_id': self.node_id,
            'result': result, 'time_taken_seconds': time_taken,
            'errors': errors
        })


# ============================================================
# Worker Loop (در thread جدا)
# ============================================================
class WorkerThread(threading.Thread):
    def __init__(self, api_client, node_name, specs, on_status=None, on_credit=None):
        super().__init__(daemon=True)
        self.api_client = api_client
        self.node_name = node_name
        self.specs = specs
        self.on_status = on_status or (lambda msg: print(msg))
        self.on_credit = on_credit or (lambda total: print(f'credit: {total}'))
        self.running = True
        self.work_done = 0
        self.credits_earned = 0
        self.current_task = None
    
    def stop(self):
        self.running = False
    
    def run(self):
        # Register
        prefs = {
            'preferred_work_types': ['factor_small', 'prime_hunt', 'benchmark', 'data_analysis'],
            'blocked_work_types': [],
            'max_concurrent_tasks': 1,
            'max_hours_per_day': 24,
        }
        result = self.api_client.register_node(self.node_name, self.specs, prefs)
        if not result.get('success'):
            self.on_status(f"❌ ثبت نود ناموفق: {result.get('error', 'unknown')}")
            # Run in offline mode
            self.offline_loop()
            return
        
        self.on_status(f"✅ نود ثبت شد (ID: {self.api_client.node_id})")
        eligible = result.get('eligible_work_types', [])
        self.on_status(f"📋 کارهای قابل اجرا: {', '.join(eligible) if eligible else '(در حال محاسبه)'}")
        
        last_heartbeat = time.time()
        while self.running:
            # Heartbeat every 60s
            if time.time() - last_heartbeat > 60:
                cur_specs = collect_system_specs()
                self.api_client.heartbeat(cur_specs)
                last_heartbeat = time.time()
            
            # Get next task
            cur_specs = collect_system_specs()
            task_resp = self.api_client.get_next_task(cur_specs)
            task_id = task_resp.get('task_id')
            
            if not task_id:
                # No work — run local benchmark
                self.on_status("💤 کاری موجود نیست. اجرای محلی...")
                self.run_local_work()
                time.sleep(15)
                continue
            
            work_type = task_resp.get('work_type', 'benchmark')
            payload = task_resp.get('payload', {})
            credit = task_resp.get('credit_per_task', 0)
            self.on_status(f"📋 کار #{task_id} ({work_type}) — credit: {credit}")
            self.current_task = work_type
            
            # Execute
            start = time.time()
            try:
                result = execute_work(work_type, payload)
                elapsed = time.time() - start
                
                if 'error' in result:
                    submit = self.api_client.submit_result(task_id, result, elapsed, result['error'])
                    self.on_status(f"❌ کار شکست خورد: {result['error']}")
                else:
                    submit = self.api_client.submit_result(task_id, result, elapsed)
                    credited = submit.get('credit_awarded', 0)
                    self.credits_earned += credited
                    self.work_done += 1
                    self.on_status(f"✅ کار #{task_id} تکمیل شد در {elapsed:.1f}s — +{credited} credit (مجموع: {self.credits_earned})")
                    self.on_credit(self.credits_earned)
            except Exception as e:
                self.on_status(f"⚠️ خطا: {e}")
                self.api_client.submit_result(task_id, {'error': str(e)}, time.time() - start)
    
    def offline_loop(self):
        """اجرای محلی اگر سرور در دسترس نباشد"""
        self.on_status("🔄 حالت آفلاین — اجرای محلی")
        while self.running:
            self.run_local_work()
            time.sleep(5)
    
    def run_local_work(self):
        """اجرای کار محلی (shmarsh اعداد اول، فاکتور کردن)"""
        n = 100000 + (self.work_done * 1000)
        primes_count = sum(1 for x in range(n, n + 1000) if is_prime(x))
        self.work_done += 1
        self.credits_earned += primes_count
        self.on_credit(self.credits_earned)
        if self.work_done % 10 == 0:
            self.on_status(f"📊 محلی: {self.work_done} کار، {self.credits_earned} credit")


# ============================================================
# GUI (tkinter)
# ============================================================
class VolunteerApp:
    def __init__(self):
        if not HAS_TK:
            print("tkinter not available. Running in CLI mode.")
            self.cli_mode()
            return
        
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("900x700")
        self.root.configure(bg='#f8fafc')
        
        self.api_client = None
        self.worker = None
        self.specs = collect_system_specs()
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header
        header = tk.Frame(self.root, bg='#0f172a', height=80)
        header.pack(fill='x')
        tk.Label(header, text=f"🖥️ {APP_NAME}", font=('Arial', 18, 'bold'),
                 bg='#0f172a', fg='white').pack(pady=10)
        tk.Label(header, text=f"{APP_DEDICATED}", font=('Arial', 10),
                 bg='#0f172a', fg='#94a3b8').pack()
        
        # Main notebook
        nb = ttk.Notebook(self.root)
        nb.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Connection
        conn_frame = ttk.Frame(nb)
        nb.add(conn_frame, text="🔌 اتصال")
        self.setup_conn_tab(conn_frame)
        
        # Tab 2: System Info
        sys_frame = ttk.Frame(nb)
        nb.add(sys_frame, text="💻 سیستم")
        self.setup_sys_tab(sys_frame)
        
        # Tab 3: Work
        work_frame = ttk.Frame(nb)
        nb.add(work_frame, text="🚀 کار")
        self.setup_work_tab(work_frame)
        
        # Tab 4: Log
        log_frame = ttk.Frame(nb)
        nb.add(log_frame, text="📜 لاگ")
        self.setup_log_tab(log_frame)
    
    def setup_conn_tab(self, parent):
        ttk.Label(parent, text="تنظیمات اتصال به سرور", font=('Arial', 14, 'bold')).pack(pady=10)
        
        f = ttk.Frame(parent)
        f.pack(pady=10)
        
        ttk.Label(f, text="آدرس سرور:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.server_var = tk.StringVar(value="https://platform-oloom.ir")
        ttk.Entry(f, textvariable=self.server_var, width=40).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(f, text="API Key:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.apikey_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.apikey_var, width=40, show='*').grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(f, text="نام نود:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.nodename_var = tk.StringVar(value=f"node-{platform.node()[:10]}")
        ttk.Entry(f, textvariable=self.nodename_var, width=40).grid(row=2, column=1, padx=5, pady=5)
        
        self.start_btn = ttk.Button(parent, text="🚀 شروع", command=self.start_worker)
        self.start_btn.pack(pady=20)
        self.stop_btn = ttk.Button(parent, text="⏹️ توقف", command=self.stop_worker, state='disabled')
        self.stop_btn.pack()
    
    def setup_sys_tab(self, parent):
        ttk.Label(parent, text="مشخصات سیستم", font=('Arial', 14, 'bold')).pack(pady=10)
        
        info_text = tk.Text(parent, height=25, width=80, font=('Courier', 10))
        info_text.pack(pady=10, padx=10, fill='both', expand=True)
        
        info = f"""💻 CPU: {self.specs['cpu']['model']}
   Cores: {self.specs['cpu']['cores']}
   Threads: {self.specs['cpu']['threads']}

💾 RAM: {self.specs['ram']['total_mb']} MB total
   Available: {self.specs['ram']['available_mb']} MB

💿 Disk: {self.specs['disk']['total_gb']} GB total
   Free: {self.specs['disk']['free_gb']} GB
   Type: {self.specs['disk']['type']}

🎮 GPU: {self.specs['gpu']['model'] or '(ندارد)'}
   VRAM: {self.specs['gpu']['vram_mb']} MB
   CUDA: {'بله' if self.specs['gpu']['cuda'] else 'خیر'}

🖥️ OS: {self.specs['os']['name']} {self.specs['os']['version']}
   Arch: {self.specs['os']['arch']}

🌐 Network: ~{self.specs['network']['internet_speed_mbps']} Mbps
"""
        info_text.insert('1.0', info)
        info_text.configure(state='disabled')
    
    def setup_work_tab(self, parent):
        ttk.Label(parent, text="آمار کار", font=('Arial', 14, 'bold')).pack(pady=10)
        
        self.work_label = ttk.Label(parent, text="کار انجام‌شده: 0\nCredit: 0\nکار جاری: —", font=('Arial', 12))
        self.work_label.pack(pady=20)
        
        self.work_text = tk.Text(parent, height=20, width=80, font=('Courier', 10))
        self.work_text.pack(pady=10, padx=10, fill='both', expand=True)
    
    def setup_log_tab(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, height=30, width=80, font=('Courier', 10))
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
    
    def log(self, msg):
        if not HAS_TK: return
        ts = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{ts}] {msg}\n")
        self.log_text.see('end')
    
    def update_stats(self, credit):
        if not HAS_TK: return
        self.work_label.config(text=f"کار انجام‌شده: {self.worker.work_done if self.worker else 0}\nCredit: {credit}\nکار جاری: {self.worker.current_task if self.worker and self.worker.current_task else '—'}")
    
    def start_worker(self):
        if self.worker and self.worker.is_alive():
            return
        server = self.server_var.get()
        api_key = self.apikey_var.get()
        node_name = self.nodename_var.get()
        if not api_key:
            messagebox.showwarning("هشدار", "API Key را وارد کنید")
            return
        
        self.api_client = ApiClient(server, api_key=api_key)
        self.worker = WorkerThread(
            self.api_client, node_name, self.specs,
            on_status=self.log, on_credit=self.update_stats
        )
        self.worker.start()
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.log(f"🚀 شروع به کار با سرور: {server}")
    
    def stop_worker(self):
        if self.worker:
            self.worker.stop()
            self.log("⏹️ در حال توقف...")
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
    
    def cli_mode(self):
        print(f"\n🖥️ {APP_NAME} v{VERSION}")
        print(f"{APP_DEDICATED}\n")
        print("مشخصات سیستم:")
        for k, v in self.specs.items():
            print(f"  {k}: {v}")
        print("\n💡 حالت CLI — برای GUI باید tkinter نصب باشد")
        print("   برای نصب: sudo apt install python3-tk")
    
    def run(self):
        if HAS_TK:
            self.root.mainloop()


def main():
    import argparse
    parser = argparse.ArgumentParser(description='نرم‌افزار داوطلبین پلتفرم علمی')
    parser.add_argument('--server', default='https://platform-oloom.ir', help='آدرس سرور')
    parser.add_argument('--api-key', help='API key کاربر')
    parser.add_argument('--node-name', default=f'node-{platform.node()[:10]}', help='نام نود')
    parser.add_argument('--cli', action='store_true', help='اجرای CLI (بدون GUI)')
    parser.add_argument('--show-specs', action='store_true', help='نمایش مشخصات سیستم')
    args = parser.parse_args()
    
    if args.show_specs:
        specs = collect_system_specs()
        print(json.dumps(specs, indent=2, ensure_ascii=False))
        return
    
    if args.cli and args.api_key:
        # CLI mode
        api = ApiClient(args.server, api_key=args.api_key)
        specs = collect_system_specs()
        worker = WorkerThread(api, args.node_name, specs,
                             on_status=print, on_credit=lambda c: print(f"Credit: {c}"))
        worker.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️ توقف")
            worker.stop()
    else:
        # GUI mode
        app = VolunteerApp()
        app.run()


if __name__ == '__main__':
    main()
