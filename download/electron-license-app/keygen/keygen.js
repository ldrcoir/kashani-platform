#!/usr/bin/env node
// ============================================================
//  Keygen - ابزار تولید کلید لایسنس
//  استفاده: node keygen.js <Machine-ID>
//  مثال:   node keygen.js A1B2C3D4E5F6789012345678ABCDEF01
// ============================================================

const crypto = require('crypto');

// ⚠️ مهم: این رشته باید دقیقاً با مقدار موجود در main.js یکی باشد.
// در محیط تولید، این مقدار باید کاملاً محرمانه بماند و در اختیار
// تولیدکننده لایسنس (شما) قرار گیرد.
const LICENSE_SECRET = 'demo-secret-key-change-me-in-production-2026';

function generateLicense(machineId) {
  // نرمال‌سازی ورودی
  const normalized = machineId.trim().toUpperCase().replace(/[\s-]/g, '');
  if (!normalized) {
    console.error('خطا: شناسه دستگاه خالی است.');
    process.exit(1);
  }
  if (!/^[A-F0-9]+$/.test(normalized)) {
    console.error('خطا: شناسه دستگاه فقط باید شامل حروف A-F و اعداد 0-9 باشد.');
    process.exit(1);
  }

  const hmac = crypto.createHmac('sha256', LICENSE_SECRET);
  hmac.update(normalized);
  const digest = hmac.digest('hex').toUpperCase();
  const part = digest.substring(0, 32);
  return part.match(/.{1,8}/g).join('-');
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    // حالت تعاملی
    console.log('========================================');
    console.log('  تولیدکننده کلید لایسنس - LicenseDemo');
    console.log('========================================');
    console.log('');
    console.log('این ابزار از شناسه دستگاه (Machine ID) یک کلید لایسنس');
    console.log('منحصربه‌فرد تولید می‌کند که فقط روی همان دستگاه کار می‌کند.');
    console.log('');
    process.stdout.write('شناسه دستگاه را وارد کنید: ');

    process.stdin.setEncoding('utf8');
    process.stdin.on('data', (data) => {
      const machineId = data.trim();
      if (!machineId) {
        console.error('ورودی خالی است. خروج.');
        process.exit(1);
      }
      const license = generateLicense(machineId);
      printResult(machineId, license);
      process.exit(0);
    });
    return;
  }

  // حالت آرگومان خط فرمان
  if (args[0] === '-h' || args[0] === '--help') {
    console.log('استفاده:');
    console.log('  node keygen.js <Machine-ID>');
    console.log('');
    console.log('مثال:');
    console.log('  node keygen.js A1B2C3D4E5F6789012345678ABCDEF01');
    console.log('');
    console.log('یا حالت تعاملی:');
    console.log('  node keygen.js');
    process.exit(0);
  }

  const machineId = args[0];
  const license = generateLicense(machineId);
  printResult(machineId, license);
  process.exit(0);
}

function printResult(machineId, license) {
  console.log('');
  console.log('╔══════════════════════════════════════════════════╗');
  console.log('║          نتیجه تولید کلید لایسنس                ║');
  console.log('╠══════════════════════════════════════════════════╣');
  console.log('║                                                  ║');
  console.log('║  شناسه دستگاه (Machine ID):                      ║');
  console.log('║  ' + machineId.toUpperCase().padEnd(46) + '  ║');
  console.log('║                                                  ║');
  console.log('║  کلید لایسنس (License Key):                      ║');
  console.log('║  ' + license.padEnd(46) + '  ║');
  console.log('║                                                  ║');
  console.log('╚══════════════════════════════════════════════════╝');
  console.log('');
  console.log('این کلید را به کاربر بدهید تا در برنامه وارد کند.');
  console.log('');
}

main();
