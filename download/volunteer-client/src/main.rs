// 🦀 Kashani Volunteer Client
// به افتخار غیاث‌الدین جمشید کاشانی
// شبکه داوطلبین پردازش ریاضی

use clap::Parser;
use std::time::Instant;

/// Kashani Volunteer Client
#[derive(Parser, Debug)]
#[command(name = "kashani-volunteer")]
#[command(about = "Volunteer computing client for Persian Math Platform")]
struct Args {
    /// Server URL
    #[arg(short, long, default_value = "https://persian-math.ir")]
    server: String,

    /// Auth token
    #[arg(short, long)]
    token: Option<String>,

    /// Number of worker threads
    #[arg(short, long, default_value = "4")]
    workers: usize,

    /// Benchmark only
    #[arg(long)]
    benchmark: bool,

    /// Verbose logging
    #[arg(short, long)]
    verbose: bool,
}

fn main() {
    let args = Args::parse();
    if args.verbose { env_logger::init(); }
    println!("🕌 Kashani Volunteer Client — به افتخار غیاث‌الدین جمشید کاشانی");
    println!();
    if args.benchmark { run_benchmark(args.workers); return; }
    println!("Server: {} | Workers: {}", args.server, args.workers);
    println!("⚠️ Server not ready yet. Running benchmark...");
    run_benchmark(args.workers);
}

fn run_benchmark(workers: usize) {
    println!("📊 Benchmark ({} workers)", workers);
    let start = Instant::now();
    let mut primes = 0u64;
    let end: u64 = 10_000_000;
    for n in 2..end { if is_prime(n) { primes += 1; } }
    let elapsed = start.elapsed();
    let rate = end as f64 / elapsed.as_secs_f64();
    println!("  Range: 1 to {}", end);
    println!("  Primes: {}", primes);
    println!("  Time: {:.2}s", elapsed.as_secs_f64());
    println!("  Rate: {:,.0}/s", rate);
    println!();
    println!("📊 Factorization benchmark:");
    for &n in &[1000000007u64, 999999999989, 1000000000039] {
        let s = Instant::now();
        match factor_rho(n) {
            Some((p, q)) => println!("  {} = {} × {} ({:.3}ms)", n, p, q, s.elapsed().as_secs_f64()*1000.0),
            None => println!("  {} is prime ({:.3}ms)", n, s.elapsed().as_secs_f64()*1000.0),
        }
    }
}

fn is_prime(n: u64) -> bool {
    if n < 2 { return false; }
    if n == 2 || n == 3 { return true; }
    if n % 2 == 0 || n % 3 == 0 { return false; }
    let mut i = 5;
    while i.saturating_mul(i) <= n {
        if n % i == 0 || n % (i+2) == 0 { return false; }
        i += 6;
    }
    true
}

fn factor_rho(n: u64) -> Option<(u64, u64)> {
    if is_prime(n) { return None; }
    let mut x: u64 = 2; let mut y: u64 = 2; let mut d: u64 = 1;
    let f = |x: u64| x.wrapping_mul(x).wrapping_add(1) % n;
    while d == 1 { x = f(x); y = f(f(y)); d = gcd(if x>y {x-y} else {y-x}, n); }
    if d != n { Some((d, n/d)) } else { None }
}

fn gcd(a: u64, b: u64) -> u64 { if b == 0 { a } else { gcd(b, a % b) } }
