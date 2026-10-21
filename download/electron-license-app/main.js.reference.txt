const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const crypto = require('crypto');
const os = require('os');
const fs = require('fs');

// ============================================================
//  تنظیمات امنیتی لایسنس
// ============================================================
// این رشته به‌عنوان کلید مخفی HMAC استفاده می‌شود.
// در محیط تولید واقعی، این مقدار باید با یک ابزار بیلد تزریق شود
// و در سورس قابل مشاهده نباشد. برای دمو اینجا قرار گرفته.
const LICENSE_SECRET = 'demo-secret-key-change-me-in-production-2026';
const TRIAL_DAYS = 14;

// ============================================================
//  ماژول تولید Machine ID
// ============================================================
function getMachineId() {
  const cpus = os.cpus();
  const cpuInfo = cpus && cpus.length > 0 ? cpus[0].model : 'unknown';
  const hostname = os.hostname();
  const platform = os.platform();
  const arch = os.arch();
  const totalMem = os.totalmem();
  // در ویندوز می‌توان از MAC آداپتور شبکه نیز استفاده کرد
  const netInterfaces = os.networkInterfaces();
  let mac = '';
  for (const key of Object.keys(netInterfaces)) {
    const ifaces = netInterfaces[key];
    if (!ifaces) continue;
    for (const i of ifaces) {
      if (i.mac && i.mac !== '00:00:00:00:00:00' && !i.internal) {
        mac = i.mac;
        break;
      }
    }
    if (mac) break;
  }
  const raw = [cpuInfo, hostname, platform, arch, totalMem, mac].join('|');
  const hash = crypto.createHash('sha256').update(raw).digest('hex');
  // فقط ۳۲ کاراکتر اول رو برمی‌گردونیم
  return hash.substring(0, 32).toUpperCase();
}

// ============================================================
//  ماژول لایسنس - HMAC-SHA256
// ============================================================
function generateLicense(machineId) {
  const hmac = crypto.createHmac('sha256', LICENSE_SECRET);
  hmac.update(machineId);
  const digest = hmac.digest('hex').toUpperCase();
  // ۳۲ کاراکتر رو به ۴ گروه ۸تایی تقسیم می‌کنیم
  const part = digest.substring(0, 32);
  return part.match(/.{1,8}/g).join('-');
}

function verifyLicense(machineId, licenseKey) {
  if (!machineId || !licenseKey) return false;
  const expected = generateLicense(machineId);
  // نرمال‌سازی: حذف فاصله و خط تیره و بزرگ‌نویسی
  const normalized = licenseKey.replace(/[\s-]/g, '').toUpperCase();
  const expectedNorm = expected.replace(/[\s-]/g, '').toUpperCase();
  // مقایسه زمان‌ثابت برای جلوگیری از timing attack
  if (normalized.length !== expectedNorm.length) return false;
  return crypto.timingSafeEqual(Buffer.from(normalized), Buffer.from(expectedNorm));
}

// ============================================================
//  ماژول دوره آزمایشی (Trial)
// ============================================================
function getTrialFilePath() {
  return path.join(app.getPath('userData'), 'trial.dat');
}

function getLicenseFilePath() {
  return path.join(app.getPath('userData'), 'license.key');
}

// رمزگذاری ساده برای فایل trial (Base64 + XOR)
// توجه: این رمزگذاری ضعیف است و فقط برای جلوگیری از تغییر دستی فایل است.
// در محیط تولید از رمزگذاری قوی‌تر استفاده کنید.
function obfuscate(text) {
  const key = LICENSE_SECRET.substring(0, 16);
  const buf = Buffer.from(text, 'utf8');
  const out = Buffer.alloc(buf.length);
  for (let i = 0; i < buf.length; i++) {
    out[i] = buf[i] ^ key.charCodeAt(i % key.length);
  }
  return out.toString('base64');
}

function deobfuscate(b64) {
  try {
    const key = LICENSE_SECRET.substring(0, 16);
    const buf = Buffer.from(b64, 'base64');
    const out = Buffer.alloc(buf.length);
    for (let i = 0; i < buf.length; i++) {
      out[i] = buf[i] ^ key.charCodeAt(i % key.length);
    }
    return out.toString('utf8');
  } catch (e) {
    return null;
  }
}

function initTrial() {
  const trialFile = getTrialFilePath();
  if (!fs.existsSync(trialFile)) {
    // اولین اجرا - فایل trial رو بساز
    const data = {
      firstLaunch: Date.now(),
      lastLaunch: Date.now(),
      version: 1
    };
    fs.writeFileSync(trialFile, obfuscate(JSON.stringify(data)), 'utf8');
    return data;
  }
  // فایل موجود رو بخون
  const content = fs.readFileSync(trialFile, 'utf8');
  const decoded = deobfuscate(content);
  if (!decoded) {
    // فایل خراب شده - دوباره بساز
    const data = {
      firstLaunch: Date.now(),
      lastLaunch: Date.now(),
      version: 1
    };
    fs.writeFileSync(trialFile, obfuscate(JSON.stringify(data)), 'utf8');
    return data;
  }
  try {
    const data = JSON.parse(decoded);
    // جلوگیری از عقب‌کشیدن ساعت
    if (data.lastLaunch > Date.now()) {
      data.lastLaunch = Date.now();
    }
    // آپدیت آخرین اجرا
    data.lastLaunch = Date.now();
    fs.writeFileSync(trialFile, obfuscate(JSON.stringify(data)), 'utf8');
    return data;
  } catch (e) {
    const data = {
      firstLaunch: Date.now(),
      lastLaunch: Date.now(),
      version: 1
    };
    fs.writeFileSync(trialFile, obfuscate(JSON.stringify(data)), 'utf8');
    return data;
  }
}

function getTrialStatus() {
  const data = initTrial();
  const elapsedMs = Date.now() - data.firstLaunch;
  const elapsedDays = Math.floor(elapsedMs / (1000 * 60 * 60 * 24));
  const remainingDays = Math.max(0, TRIAL_DAYS - elapsedDays);
  return {
    firstLaunch: data.firstLaunch,
    elapsedDays,
    remainingDays,
    totalDays: TRIAL_DAYS,
    expired: remainingDays <= 0
  };
}

function getStoredLicense() {
  const licFile = getLicenseFilePath();
  if (!fs.existsSync(licFile)) return null;
  try {
    return fs.readFileSync(licFile, 'utf8').trim();
  } catch (e) {
    return null;
  }
}

function saveLicense(licenseKey) {
  const licFile = getLicenseFilePath();
  fs.writeFileSync(licFile, licenseKey, 'utf8');
}

function deleteLicense() {
  const licFile = getLicenseFilePath();
  if (fs.existsSync(licFile)) {
    fs.unlinkSync(licFile);
  }
}

// ============================================================
//  پنجره اصلی
// ============================================================
let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 900,
    height: 640,
    minWidth: 720,
    minHeight: 540,
    title: 'LicenseDemo - دمو سیستم لایسنس',
    backgroundColor: '#0f172a',
    show: false,
    icon: path.join(__dirname, 'assets', 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  mainWindow.loadFile(path.join(__dirname, 'src', 'index.html'));

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // باز کردن لینک‌های خارجی در مرورگر
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ============================================================
//  IPC Handlers
// ============================================================
ipcMain.handle('get-status', () => {
  const machineId = getMachineId();
  const trial = getTrialStatus();
  const storedLic = getStoredLicense();
  let licensed = false;
  if (storedLic) {
    licensed = verifyLicense(machineId, storedLic);
  }
  return {
    machineId,
    trial,
    licensed,
    licenseKey: storedLic || '',
    appVersion: app.getVersion()
  };
});

ipcMain.handle('activate-license', (event, licenseKey) => {
  const machineId = getMachineId();
  const valid = verifyLicense(machineId, licenseKey);
  if (valid) {
    saveLicense(licenseKey.trim());
    return { success: true, message: 'لایسنس با موفقیت فعال شد.' };
  }
  return { success: false, message: 'کلید لایسنس نامعتبر است. لطفاً بررسی کنید و دوباره امتحان کنید.' };
});

ipcMain.handle('deactivate-license', () => {
  deleteLicense();
  return { success: true, message: 'لایسنس غیرفعال شد.' };
});

ipcMain.handle('reset-trial', () => {
  // فقط برای تست - در محصول واقعی حذف کنید
  const trialFile = getTrialFilePath();
  if (fs.existsSync(trialFile)) {
    fs.unlinkSync(trialFile);
  }
  return { success: true, message: 'دوره آزمایشی بازنشانی شد.' };
});

ipcMain.handle('copy-text', (event, text) => {
  const { clipboard } = require('electron');
  clipboard.writeText(text);
  return { success: true };
});

// ============================================================
//  چرخه حیات برنامه
// ============================================================
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // آپدیت آخرین زمان اجرا
  try {
    initTrial();
  } catch (e) {}
});
