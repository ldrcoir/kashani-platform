// volunteer-client/src/main.rs — English CLI output
// Persian text garbles in Windows CMD, so use English for CLI

use clap::Parser;
use std::time::{Duration, Instant};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::thread;
use serde::{Deserialize, Serialize};

#[derive(Parser, Debug, Clone)]
#[command(name = "volunteer-client", version = "1.0.0")]
#[command(about = "Volunteer computing client - Science Platform")]
struct Args {
    #[arg(short, long, default_value = "https://your-domain.com")]
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
    #[arg(long, value_name = "FILE")]
    process_tasks: Option<String>,
    #[arg(long, value_name = "FILE")]
    output: Option<String>,
}

const VERSION: &str = "1.0.0";

fn main() {
    if check_debugger() { eprintln!("Debugger detected. Exiting."); std::process::exit(1); }
    
    println!("===============================================================");
    println!("  volunteer-client v{} (Rust)", VERSION);
    println!("  Science Platform - Multidisciplinary Research");
    println!("===============================================================");
    println!();

    let args = Args::parse();

    if args.list_languages { list_languages(); return; }
    if args.storage_report { print_storage_report(); return; }
    if args.show_specs { print_system_specs(); print_storage_report(); return; }
    if args.benchmark { run_benchmark(args.workers.unwrap_or_else(num_cpus)); return; }
    if let Some(tf) = &args.process_tasks { process_task_file(tf, args.output.as_deref()); return; }
    if args.api_key.is_none() {
        eprintln!("API key required.");
        eprintln!("Or just benchmark: ./volunteer-client --benchmark");
        eprintln!("Languages: ./volunteer-client --list-languages");
        return;
    }
    if let Err(e) = run_volunteer_loop(args) {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
}

#[derive(Debug, Clone, Serialize)]
struct SystemSpecs { cpu: CpuSpecs, ram: RamSpecs, disk: DiskSpecs, os: OsSpecs }
#[derive(Debug, Clone, Serialize)]
struct CpuSpecs { model: String, cores: usize, threads: usize }
#[derive(Debug, Clone, Serialize)]
struct RamSpecs { total_mb: u64, available_mb: u64 }
#[derive(Debug, Clone, Serialize)]
struct DiskSpecs { total_gb: u64, free_gb: u64, disk_type: String }
#[derive(Debug, Clone, Serialize)]
struct OsSpecs { name: String, version: String }

fn collect_system_specs() -> SystemSpecs {
    let cpu = CpuSpecs { model: std::env::consts::ARCH.to_string(), cores: num_cpus(), threads: num_cpus() };
    let (rt, ra) = read_meminfo();
    let (dt, df) = read_diskinfo();
    SystemSpecs {
        cpu, ram: RamSpecs { total_mb: rt, available_mb: ra },
        disk: DiskSpecs { total_gb: dt, free_gb: df, disk_type: detect_disk_type() },
        os: OsSpecs { name: std::env::consts::OS.to_string(), version: read_os_version() },
    }
}

fn print_system_specs() {
    let s = collect_system_specs();
    println!("CPU: {} ({} cores)", s.cpu.model, s.cpu.cores);
    println!("RAM: {} MB total, {} MB available", s.ram.total_mb, s.ram.available_mb);
    println!("Disk: {} GB total, {} GB free ({})", s.disk.total_gb, s.disk.free_gb, s.disk.disk_type);
    println!("OS: {} {}", s.os.name, s.os.version);
}

fn num_cpus() -> usize { std::thread::available_parallelism().map(|n| n.get()).unwrap_or(1) }

fn read_meminfo() -> (u64, u64) {
    if let Ok(c) = std::fs::read_to_string("/proc/meminfo") {
        let mut t = 0u64; let mut a = 0u64;
        for l in c.lines() {
            if l.starts_with("MemTotal:") { if let Some(n) = l.split_whitespace().nth(1) { t = n.parse().unwrap_or(0)/1024; } }
            else if l.starts_with("MemAvailable:") { if let Some(n) = l.split_whitespace().nth(1) { a = n.parse().unwrap_or(0)/1024; } }
        }
        return (t, a);
    }
    (0, 0)
}

fn read_diskinfo() -> (u64, u64) {
    if let Ok(o) = std::process::Command::new("df").arg("-k").arg("/").output() {
        let s = String::from_utf8_lossy(&o.stdout);
        for l in s.lines().skip(1) {
            let p: Vec<&str> = l.split_whitespace().collect();
            if p.len() >= 4 { return (p[1].parse::<u64>().unwrap_or(0)/1024/1024, p[3].parse::<u64>().unwrap_or(0)/1024/1024); }
        }
    }
    (0, 0)
}

fn detect_disk_type() -> String {
    if std::path::Path::new("/sys/class/nvme").exists() { "nvme".into() }
    else if std::path::Path::new("/sys/block/sda").exists() {
        if let Ok(r) = std::fs::read_to_string("/sys/block/sda/queue/rotational") {
            if r.trim() == "0" { "ssd".into() } else { "hdd".into() }
        } else { "unknown".into() }
    } else { "unknown".into() }
}

fn read_os_version() -> String {
    if let Ok(c) = std::fs::read_to_string("/etc/os-release") {
        for l in c.lines() { if l.starts_with("PRETTY_NAME=") { return l.trim_start_matches("PRETTY_NAME=").trim_matches('"').to_string(); } }
    }
    std::env::consts::ARCH.to_string()
}

fn print_storage_report() {
    let (t, f) = read_diskinfo();
    let hosting_mb = (f * 1024) / 10;
    println!("Storage Report:");
    println!("  Total: {} GB", t);
    println!("  Free: {} GB", f);
    println!("  Available for hosting: {} MB (10% of free)", hosting_mb);
}

fn list_languages() {
    let langs = [
        ("fa","Farsi","rtl"),("en","English","ltr"),("ar","Arabic","rtl"),
        ("fr","French","ltr"),("de","German","ltr"),("es","Spanish","ltr"),
        ("ru","Russian","ltr"),("zh","Chinese","ltr"),("ja","Japanese","ltr"),
        ("ko","Korean","ltr"),("tr","Turkish","ltr"),("ur","Urdu","rtl"),
        ("hi","Hindi","ltr"),("bn","Bengali","ltr"),("pt","Portuguese","ltr"),
        ("it","Italian","ltr"),("nl","Dutch","ltr"),("sv","Swedish","ltr"),
        ("pl","Polish","ltr"),("uk","Ukrainian","ltr"),("vi","Vietnamese","ltr"),
        ("th","Thai","ltr"),("id","Indonesian","ltr"),("ms","Malay","ltr"),
        ("sw","Swahili","ltr"),("he","Hebrew","rtl"),("el","Greek","ltr"),
        ("la","Latin","ltr"),("eo","Esperanto","ltr"),
    ];
    println!("Supported Languages ({}):", langs.len());
    for (c, n, d) in &langs { println!("  {} ({}) - {}", n, c, d); }
}

fn is_prime_u64(n: u64) -> bool {
    if n < 2 { return false; }
    if n == 2 || n == 3 { return true; }
    if n % 2 == 0 || n % 3 == 0 { return false; }
    let mut i = 5u64;
    while i.saturating_mul(i) <= n { if n % i == 0 || n % (i+2) == 0 { return false; } i += 6; }
    true
}

fn factor_u64(n: u64) -> Option<Vec<u64>> {
    if n < 2 || is_prime_u64(n) { return None; }
    let mut f = Vec::new(); let mut r = n;
    for &p in &[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97] { while r % p == 0 { f.push(p); r /= p; } }
    if r == 1 { return Some(f); }
    while r > 1 && !is_prime_u64(r) { if let Some(d) = pollard_rho(r) { f.push(d); r /= d; } else { f.push(r); break; } }
    if r > 1 { f.push(r); } f.sort(); Some(f)
}

fn pollard_rho(n: u64) -> Option<u64> {
    if n < 2 || is_prime_u64(n) { return None; }
    let mut x = 2u64; let mut y = 2u64; let mut d = 1u64;
    let f = |x: u64| x.wrapping_mul(x).wrapping_add(1) % n;
    let mut i = 0;
    while d == 1 && i < 1_000_000 { x = f(x); y = f(f(y)); d = gcd(if x > y { x - y } else { y - x }, n); i += 1; }
    if d != n && d != 1 { Some(d) } else { None }
}

fn gcd(a: u64, b: u64) -> u64 { if b == 0 { a } else { gcd(b, a % b) } }

fn run_benchmark(workers: usize) {
    println!("Benchmark ({} workers)\n", workers);
    print_system_specs(); println!();
    let start = Instant::now(); let end = 10_000_000u64;
    let chunk = end / workers as u64;
    let pc = Arc::new(AtomicU64::new(0));
    let mut h = vec![];
    for w in 0..workers {
        let pc = Arc::clone(&pc);
        let s = w as u64 * chunk; let e = if w == workers - 1 { end } else { (w as u64 + 1) * chunk };
        h.push(thread::spawn(move || { let mut l = 0u64; for n in s..e { if n >= 2 && is_prime_u64(n) { l += 1; } } pc.fetch_add(l, Ordering::Relaxed); }));
    }
    for t in h { t.join().unwrap(); }
    let el = start.elapsed();
    println!("Prime Counting:");
    println!("  Range: 1 to {}", end);
    println!("  Primes: {}", pc.load(Ordering::Relaxed));
    println!("  Time: {:.2}s", el.as_secs_f64());
    println!("  Rate: {:.0} numbers/sec\n", end as f64 / el.as_secs_f64());
    println!("Factorization:");
    for &n in &[1000000007u64, 999999999989, 123456789012345678] {
        let s = Instant::now();
        match factor_u64(n) {
            Some(f) => { let fs: Vec<String> = f.iter().map(|x| x.to_string()).collect(); println!("  {} = {} ({:.3}ms)", n, fs.join(" x "), s.elapsed().as_secs_f64()*1000.0); }
            None => println!("  {} is prime ({:.3}ms)", n, s.elapsed().as_secs_f64()*1000.0),
        }
    }
}

fn run_volunteer_loop(args: Args) -> anyhow::Result<()> {
    println!("Server: {}", args.server);
    println!("API key: {}...{}", &args.api_key.as_ref().unwrap()[..8], &args.api_key.as_ref().unwrap()[args.api_key.as_ref().unwrap().len()-4..]);
    println!();
    println!("Running local work...");
    let wd = Arc::new(AtomicU64::new(0)); let cr = Arc::new(AtomicU64::new(0));
    let st = Instant::now(); let mut bs = 2_000_000_000u64;
    loop {
        let s = bs; let e = bs + 100_000;
        let ts = Instant::now();
        let mut p = 0u64;
        for n in s..e { if n > 2 && n % 2 != 0 && is_prime_u64(n) { p += 1; } }
        wd.fetch_add(1, Ordering::Relaxed); cr.fetch_add(p, Ordering::Relaxed);
        let tw = wd.load(Ordering::Relaxed); let tc = cr.load(Ordering::Relaxed);
        let te = st.elapsed().as_secs();
        let r = if te > 0 { tw as f64 / te as f64 } else { 0.0 };
        println!("[{}] Work #{}: {} primes in [{}, {}) ({:.2}s) | credit: {} | rate: {:.1}/s",
                 fmt_dur(te), tw, p, s, e, ts.elapsed().as_secs_f64(), tc, r);
        bs = e; thread::sleep(Duration::from_millis(100));
    }
}

fn process_task_file(tf: &str, out: Option<&str>) {
    println!("Processing: {}", tf);
    let c = match std::fs::read_to_string(tf) { Ok(c) => c, Err(e) => { eprintln!("Cannot read: {}", e); return; } };
    let mut res = Vec::new();
    for l in c.lines() {
        let l = l.trim();
        if l.is_empty() || l.starts_with('#') { continue; }
        if let Some(ns) = l.strip_prefix("n=") {
            print!("Factoring {}... ", ns);
            let st = Instant::now();
            match ns.parse::<u64>() {
                Ok(n) => match factor_u64(n) {
                    Some(f) => { let fs: Vec<String> = f.iter().map(|x| x.to_string()).collect(); println!("OK {} factors ({:.3}s)", f.len(), st.elapsed().as_secs_f64()); res.push(format!("n={}\nfactors={}\ntime={:.3}s\n", ns, fs.join(","), st.elapsed().as_secs_f64())); }
                    None => { println!("prime"); res.push(format!("n={}\nfactors=prime\n", ns)); }
                },
                Err(_) => { println!("invalid"); res.push(format!("n={}\nerror=invalid\n", ns)); }
            }
        }
    }
    let o = out.unwrap_or("results.txt");
    match std::fs::write(o, res.join("\n---\n")) { Ok(_) => println!("\nResults: {}", o), Err(e) => eprintln!("Write error: {}", e) }
}

fn check_debugger() -> bool {
    if let Ok(c) = std::fs::read_to_string("/proc/self/status") {
        for l in c.lines() { if l.starts_with("TracerPid:") { if let Some(p) = l.split(':').nth(1) { if p.trim().parse::<i32>().unwrap_or(0) > 0 { return true; } } } }
    }
    false
}

fn fmt_dur(s: u64) -> String { let h = s/3600; let m = (s%3600)/60; let s = s%60; if h > 0 { format!("{}h{}m{}s",h,m,s) } else if m > 0 { format!("{}m{}s",m,s) } else { format!("{}s",s) } }
