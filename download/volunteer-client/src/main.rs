// kashani-volunteer — نرم‌افزار داوطلبین پلتفرم علمی چندرشته‌ای پارسی
// به افتخار غیاث‌الدین جمشید کاشانی
// ============================================================
// نسخه‌ی یکپارچه (تمام ماژول‌ها در یک فایل — برای پایداری)
// ============================================================

use clap::Parser;
use std::time::{Duration, Instant};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::thread;
use serde::{Deserialize, Serialize};

// ===== CLI Args =====
#[derive(Parser, Debug, Clone)]
#[command(name = "kashani-volunteer", version = "1.0.0")]
#[command(about = "Volunteer computing client — Persian Multidisciplinary Science Platform")]
struct Args {
    #[arg(short, long, default_value = "https://platform-oloom.ir")]
    server: String,
    #[arg(short, long)]
    api_key: Option<String>,
    #[arg(long, default_value = "my-node")]
    node_name: String,
    #[arg(short, long)]
    workers: Option<usize>,
    #[arg(long)]
    benchmark: bool,
    #[arg(long)]
    show_specs: bool,
    #[arg(long)]
    list_languages: bool,
    #[arg(long)]
    storage_report: bool,
    #[arg(long)]
    chat: bool,
    #[arg(long, default_value = "fa")]
    language: String,
    #[arg(long, value_name = "FILE")]
    process_tasks: Option<String>,
    #[arg(long, value_name = "FILE")]
    output: Option<String>,
}

const VERSION: &str = "1.0.0";

fn main() {
    // Anti-debug check
    if check_debugger() {
        eprintln!("⚠️ Debugger detected. Exiting.");
        std::process::exit(1);
    }

    println!("═══════════════════════════════════════════════════════════════");
    println!("  kashani-volunteer v{} (Rust)", VERSION);
    println!("  پلتفرم علمی چندرسته‌ای پارسی");
    println!("═══════════════════════════════════════════════════════════════");
    println!();

    let args = Args::parse();

    if args.list_languages {
        list_languages();
        return;
    }

    if args.storage_report {
        print_storage_report();
        return;
    }

    if args.show_specs {
        print_system_specs();
        print_storage_report();
        return;
    }

    if args.benchmark {
        run_benchmark(args.workers.unwrap_or_else(num_cpus));
        return;
    }

    if let Some(task_file) = &args.process_tasks {
        process_task_file(task_file, args.output.as_deref());
        return;
    }

    if args.api_key.is_none() {
        eprintln!("❌ API key لازم است.");
        eprintln!("💡 یا فقط benchmark: ./kashani-volunteer --benchmark");
        eprintln!("📚 زبان‌ها: ./kashani-volunteer --list-languages");
        return;
    }

    if let Err(e) = run_volunteer_loop(args) {
        eprintln!("❌ خطا: {}", e);
        std::process::exit(1);
    }
}

// ===== System Specs =====
#[derive(Debug, Clone, Serialize)]
struct SystemSpecs {
    cpu: CpuSpecs,
    ram: RamSpecs,
    disk: DiskSpecs,
    os: OsSpecs,
}

#[derive(Debug, Clone, Serialize)]
struct CpuSpecs { model: String, cores: usize, threads: usize }
#[derive(Debug, Clone, Serialize)]
struct RamSpecs { total_mb: u64, available_mb: u64 }
#[derive(Debug, Clone, Serialize)]
struct DiskSpecs { total_gb: u64, free_gb: u64, disk_type: String }
#[derive(Debug, Clone, Serialize)]
struct OsSpecs { name: String, version: String }

fn collect_system_specs() -> SystemSpecs {
    let cpu = CpuSpecs {
        model: std::env::consts::ARCH.to_string(),
        cores: num_cpus(),
        threads: num_cpus(),
    };
    let (ram_total, ram_avail) = read_meminfo();
    let (disk_total, disk_free) = read_diskinfo();
    let disk_type = detect_disk_type();
    SystemSpecs {
        cpu,
        ram: RamSpecs { total_mb: ram_total, available_mb: ram_avail },
        disk: DiskSpecs { total_gb: disk_total, free_gb: disk_free, disk_type },
        os: OsSpecs {
            name: std::env::consts::OS.to_string(),
            version: read_os_version(),
        },
    }
}

fn print_system_specs() {
    let s = collect_system_specs();
    println!("💻 CPU: {} ({} cores)", s.cpu.model, s.cpu.cores);
    println!("💾 RAM: {} MB total, {} MB available", s.ram.total_mb, s.ram.available_mb);
    println!("💿 Disk: {} GB total, {} GB free ({})", s.disk.total_gb, s.disk.free_gb, s.disk.disk_type);
    println!("🖥️ OS: {} {}", s.os.name, s.os.version);
}

fn num_cpus() -> usize {
    std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1)
}

fn read_meminfo() -> (u64, u64) {
    if let Ok(content) = std::fs::read_to_string("/proc/meminfo") {
        let mut total = 0u64;
        let mut avail = 0u64;
        for line in content.lines() {
            if line.starts_with("MemTotal:") {
                if let Some(n) = line.split_whitespace().nth(1) {
                    total = n.parse().unwrap_or(0) / 1024;
                }
            } else if line.starts_with("MemAvailable:") {
                if let Some(n) = line.split_whitespace().nth(1) {
                    avail = n.parse().unwrap_or(0) / 1024;
                }
            }
        }
        return (total, avail);
    }
    (0, 0)
}

fn read_diskinfo() -> (u64, u64) {
    if let Ok(output) = std::process::Command::new("df").arg("-k").arg("/").output() {
        let s = String::from_utf8_lossy(&output.stdout);
        for line in s.lines().skip(1) {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 4 {
                let total_kb: u64 = parts[1].parse().unwrap_or(0);
                let free_kb: u64 = parts[3].parse().unwrap_or(0);
                return (total_kb / 1024 / 1024, free_kb / 1024 / 1024);
            }
        }
    }
    (0, 0)
}

fn detect_disk_type() -> String {
    if std::path::Path::new("/sys/class/nvme").exists() { "nvme".into() }
    else if std::path::Path::new("/sys/block/sda").exists() {
        if let Ok(rot) = std::fs::read_to_string("/sys/block/sda/queue/rotational") {
            if rot.trim() == "0" { "ssd".into() } else { "hdd".into() }
        } else { "unknown".into() }
    } else { "unknown".into() }
}

fn read_os_version() -> String {
    if let Ok(content) = std::fs::read_to_string("/etc/os-release") {
        for line in content.lines() {
            if line.starts_with("PRETTY_NAME=") {
                return line.trim_start_matches("PRETTY_NAME=").trim_matches('"').to_string();
            }
        }
    }
    std::env::consts::ARCH.to_string()
}

// ===== Storage Report (for decentralized hosting) =====
fn print_storage_report() {
    let (total, free) = read_diskinfo();
    let available_for_hosting_mb = (free * 1024) / 10; // 10% of free
    println!("💾 Storage Report:");
    println!("  Total capacity: {} GB", total);
    println!("  Total free: {} GB", free);
    println!("  Available for hosting: {} MB (10% of free)", available_for_hosting_mb);
}

// ===== Languages (29 languages) =====
fn list_languages() {
    let langs = [
        ("fa", "فارسی", "Persian", "rtl", "🇮🇷"),
        ("en", "English", "English", "ltr", "🇬🇧"),
        ("ar", "العربية", "Arabic", "rtl", "🇸🇦"),
        ("fr", "Français", "French", "ltr", "🇫🇷"),
        ("de", "Deutsch", "German", "ltr", "🇩🇪"),
        ("es", "Español", "Spanish", "ltr", "🇪🇸"),
        ("ru", "Русский", "Russian", "ltr", "🇷🇺"),
        ("zh", "中文", "Chinese", "ltr", "🇨🇳"),
        ("ja", "日本語", "Japanese", "ltr", "🇯🇵"),
        ("ko", "한국어", "Korean", "ltr", "🇰🇷"),
        ("tr", "Türkçe", "Turkish", "ltr", "🇹🇷"),
        ("ur", "اردو", "Urdu", "rtl", "🇵🇰"),
        ("hi", "हिन्दी", "Hindi", "ltr", "🇮🇳"),
        ("bn", "বাংলা", "Bengali", "ltr", "🇧🇩"),
        ("pt", "Português", "Portuguese", "ltr", "🇵🇹"),
        ("it", "Italiano", "Italian", "ltr", "🇮🇹"),
        ("nl", "Nederlands", "Dutch", "ltr", "🇳🇱"),
        ("sv", "Svenska", "Swedish", "ltr", "🇸🇪"),
        ("pl", "Polski", "Polish", "ltr", "🇵🇱"),
        ("uk", "Українська", "Ukrainian", "ltr", "🇺🇦"),
        ("vi", "Tiếng Việt", "Vietnamese", "ltr", "🇻🇳"),
        ("th", "ไทย", "Thai", "ltr", "🇹🇭"),
        ("id", "Indonesia", "Indonesian", "ltr", "🇮🇩"),
        ("ms", "Melayu", "Malay", "ltr", "🇲🇾"),
        ("sw", "Kiswahili", "Swahili", "ltr", "🇰🇪"),
        ("he", "עברית", "Hebrew", "rtl", "🇮🇱"),
        ("el", "Ελληνικά", "Greek", "ltr", "🇬🇷"),
        ("la", "Latina", "Latin", "ltr", "🏛️"),
        ("eo", "Esperanto", "Esperanto", "ltr", "🌍"),
    ];
    println!("📚 زبان‌های پشتیبانی‌شده ({}):", langs.len());
    for (code, name, name_en, dir, flag) in &langs {
        println!("  {} {} ({}) — {} ({})", flag, name, code, name_en, dir);
    }
}

// ===== Number Theory =====
fn is_prime_u64(n: u64) -> bool {
    if n < 2 { return false; }
    if n == 2 || n == 3 { return true; }
    if n % 2 == 0 || n % 3 == 0 { return false; }
    let mut i: u64 = 5;
    while i.saturating_mul(i) <= n {
        if n % i == 0 || n % (i+2) == 0 { return false; }
        i += 6;
    }
    true
}

fn factor_u64(n: u64) -> Option<Vec<u64>> {
    if n < 2 || is_prime_u64(n) { return None; }
    let mut factors = Vec::new();
    let mut remaining = n;
    for &p in &[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97] {
        while remaining % p == 0 { factors.push(p); remaining /= p; }
    }
    if remaining == 1 { return Some(factors); }
    while remaining > 1 && !is_prime_u64(remaining) {
        if let Some(d) = pollard_rho_u64(remaining) {
            factors.push(d);
            remaining /= d;
        } else { factors.push(remaining); break; }
    }
    if remaining > 1 { factors.push(remaining); }
    factors.sort();
    Some(factors)
}

fn pollard_rho_u64(n: u64) -> Option<u64> {
    if n < 2 || is_prime_u64(n) { return None; }
    let mut x: u64 = 2;
    let mut y: u64 = 2;
    let mut d: u64 = 1;
    let f = |x: u64| x.wrapping_mul(x).wrapping_add(1) % n;
    let mut iter = 0;
    while d == 1 && iter < 1_000_000 {
        x = f(x);
        y = f(f(y));
        d = gcd_u64(if x > y { x - y } else { y - x }, n);
        iter += 1;
    }
    if d != n && d != 1 { Some(d) } else { None }
}

fn gcd_u64(a: u64, b: u64) -> u64 {
    if b == 0 { a } else { gcd_u64(b, a % b) }
}

// ===== Benchmark =====
fn run_benchmark(workers: usize) {
    println!("📊 Benchmark محلی با {} worker", workers);
    println!();
    print_system_specs();
    println!();

    let start = Instant::now();
    let end: u64 = 10_000_000;
    let chunk = end / workers as u64;
    let primes_count = Arc::new(AtomicU64::new(0));
    let mut handles = vec![];
    for w in 0..workers {
        let pc = Arc::clone(&primes_count);
        let s = w as u64 * chunk;
        let e = if w == workers - 1 { end } else { (w as u64 + 1) * chunk };
        handles.push(thread::spawn(move || {
            let mut local = 0u64;
            for n in s..e {
                if n >= 2 && is_prime_u64(n) { local += 1; }
            }
            pc.fetch_add(local, Ordering::Relaxed);
        }));
    }
    for h in handles { h.join().unwrap(); }
    let elapsed = start.elapsed();
    let rate = end as f64 / elapsed.as_secs_f64();
    println!("📈 شمارش اعداد اول:");
    println!("  Range: 1 to {}", end);
    println!("  Primes found: {}", primes_count.load(Ordering::Relaxed));
    println!("  Time: {:.2}s", elapsed.as_secs_f64());
    println!("  Rate: {:.0} numbers/sec", rate);
    println!();

    println!("📈 فاکتور کردن:");
    for &n in &[1000000007u64, 999999999989, 123456789012345678] {
        let s = Instant::now();
        match factor_u64(n) {
            Some(factors) => {
                let fs: Vec<String> = factors.iter().map(|f| f.to_string()).collect();
                println!("  {} = {} ({:.3}ms)", n, fs.join(" × "), s.elapsed().as_secs_f64() * 1000.0);
            }
            None => println!("  {} is prime ({:.3}ms)", n, s.elapsed().as_secs_f64() * 1000.0),
        }
    }
}

// ===== Volunteer Loop =====
fn run_volunteer_loop(args: Args) -> anyhow::Result<()> {
    println!("🔗 سرور: {}", args.server);
    println!("🔑 API key: {}...{}", &args.api_key.as_ref().unwrap()[..8], &args.api_key.as_ref().unwrap()[args.api_key.as_ref().unwrap().len()-4..]);
    println!();

    // For now, just run local benchmark + prime hunting
    println!("🚀 در حال کار محلی (بدون اتصال به سرور)...");
    let work_done = Arc::new(AtomicU64::new(0));
    let credits = Arc::new(AtomicU64::new(0));
    let running = Arc::new(AtomicBool::new(true));
    let start_time = Instant::now();

    // Simple loop: count primes in batches
    let batch_size: u64 = 100_000;
    let mut batch_start: u64 = 2_000_000_000;

    while running.load(Ordering::Relaxed) {
        let s = batch_start;
        let e = batch_start + batch_size;
        let t_start = Instant::now();
        let mut primes = 0u64;
        for n in s..e {
            if n > 2 && n % 2 != 0 && is_prime_u64(n) { primes += 1; }
        }
        let elapsed = t_start.elapsed().as_secs_f64();
        work_done.fetch_add(1, Ordering::Relaxed);
        credits.fetch_add(primes, Ordering::Relaxed);

        let total_work = work_done.load(Ordering::Relaxed);
        let total_credit = credits.load(Ordering::Relaxed);
        let total_elapsed = start_time.elapsed().as_secs();
        let rate = if total_elapsed > 0 { total_work as f64 / total_elapsed as f64 } else { 0.0 };

        println!("[{}] کار #{}: {} عدد اول در [{}, {}) ({:.2}s) | credit: {} | سرعت: {:.1} کار/s",
                 format_duration(total_elapsed), total_work, primes, s, e, elapsed, total_credit, rate);

        batch_start = e;
        thread::sleep(Duration::from_millis(100));
    }

    Ok(())
}

// ===== Task File Processing =====
fn process_task_file(task_file: &str, output_file: Option<&str>) {
    println!("📁 پردازش فایل تسک: {}", task_file);
    let content = match std::fs::read_to_string(task_file) {
        Ok(c) => c,
        Err(e) => { eprintln!("❌ نمی‌توانم فایل را بخوانم: {}", e); return; }
    };

    let mut results = Vec::new();
    for line in content.lines() {
        let line = line.trim();
        if line.is_empty() || line.starts_with('#') { continue; }
        if let Some(n_str) = line.strip_prefix("n=") {
            print!("فاکتور کردن {}... ", n_str);
            let start = Instant::now();
            match n_str.parse::<u64>() {
                Ok(n) => match factor_u64(n) {
                    Some(factors) => {
                        let elapsed = start.elapsed().as_secs_f64();
                        let fs: Vec<String> = factors.iter().map(|f| f.to_string()).collect();
                        println!("✓ {} فاکتور در {:.3}s", factors.len(), elapsed);
                        results.push(format!("n={}\nfactors={}\ntime={:.3}s\n", n_str, fs.join(","), elapsed));
                    }
                    None => {
                        println!("✓ اول است");
                        results.push(format!("n={}\nfactors=prime\ntime={:.3}s\n", n_str, start.elapsed().as_secs_f64()));
                    }
                },
                Err(_) => {
                    println!("✗ عدد نامعتبر");
                    results.push(format!("n={}\nerror=invalid\n", n_str));
                }
            }
        }
    }

    let out = output_file.unwrap_or("results.txt");
    match std::fs::write(out, results.join("\n---\n")) {
        Ok(_) => println!("\n💾 نتایج در: {}", out),
        Err(e) => eprintln!("❌ نوشتن خروجی: {}", e),
    }
}

// ===== Anti-Debug =====
fn check_debugger() -> bool {
    if let Ok(content) = std::fs::read_to_string("/proc/self/status") {
        for line in content.lines() {
            if line.starts_with("TracerPid:") {
                if let Some(pid_str) = line.split(':').nth(1) {
                    let pid: i32 = pid_str.trim().parse().unwrap_or(0);
                    if pid > 0 { return true; }
                }
            }
        }
    }
    false
}

// ===== Helpers =====
fn format_duration(secs: u64) -> String {
    let h = secs / 3600;
    let m = (secs % 3600) / 60;
    let s = secs % 60;
    if h > 0 { format!("{}h {}m {}s", h, m, s) }
    else if m > 0 { format!("{}m {}s", m, s) }
    else { format!("{}s", s) }
}
