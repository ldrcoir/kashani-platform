// ============================================================
//  Renderer - منطق رابط کاربری
// ============================================================

const $ = (id) => document.getElementById(id);

const els = {
  statusBadge: $('statusBadge'),
  licStatus: $('licStatus'),
  trialDays: $('trialDays'),
  appVersion: $('appVersion'),
  firstLaunch: $('firstLaunch'),
  trialBarWrap: $('trialBarWrap'),
  trialBarFill: $('trialBarFill'),
  trialPercent: $('trialPercent'),
  machineIdBox: $('machineIdBox'),
  copyMachineBtn: $('copyMachineBtn'),
  licenseInput: $('licenseInput'),
  activateBtn: $('activateBtn'),
  deactivateBtn: $('deactivateBtn'),
  resetTrialBtn: $('resetTrialBtn'),
  message: $('message'),
  lockCard: $('lockCard'),
  footerVersion: $('footerVersion')
};

// تبدیل اعداد انگلیسی به فارسی
function toPersianNumber(n) {
  const persian = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  return String(n).replace(/\d/g, (d) => persian[+d]);
}

// قالب‌بندی تاریخ
function formatDate(timestamp) {
  try {
    const date = new Date(timestamp);
    const y = date.getFullYear();
    const m = toPersianNumber(String(date.getMonth() + 1).padStart(2, '0'));
    const d = toPersianNumber(String(date.getDate()).padStart(2, '0'));
    const hh = toPersianNumber(String(date.getHours()).padStart(2, '0'));
    const mm = toPersianNumber(String(date.getMinutes()).padStart(2, '0'));
    return `${toPersianNumber(y)}/${m}/${d} - ${hh}:${mm}`;
  } catch (e) {
    return 'نامشخص';
  }
}

function showMessage(text, type) {
  els.message.textContent = text;
  els.message.className = 'message ' + type;
  // پاک کردن خودکار پیام موفق بعد از ۴ ثانیه
  if (type === 'success') {
    setTimeout(() => {
      if (els.message.textContent === text) {
        els.message.textContent = '';
        els.message.className = 'message';
      }
    }, 4000);
  }
}

async function refreshStatus() {
  try {
    const status = await window.api.getStatus();

    // شناسه دستگاه
    els.machineIdBox.textContent = status.machineId;

    // نسخه
    els.appVersion.textContent = toPersianNumber(status.appVersion || '1.0.0');
    els.footerVersion.textContent = toPersianNumber(status.appVersion || '1.0.0');

    // تاریخ اولین اجرا
    els.firstLaunch.textContent = formatDate(status.trial.firstLaunch);

    // روزهای باقی‌مانده
    const remaining = status.trial.remainingDays;
    const total = status.trial.totalDays;
    els.trialDays.textContent = status.licensed
      ? 'غیرفعال (لایسنس فعال است)'
      : (remaining > 0 ? `${toPersianNumber(remaining)} روز` : 'منقضی');

    // نوار پیشرفت
    const used = total - remaining;
    const percent = Math.min(100, Math.round((used / total) * 100));
    els.trialBarFill.style.width = percent + '%';
    els.trialPercent.textContent = toPersianNumber(percent) + '٪';
    if (status.licensed) {
      els.trialBarWrap.style.opacity = '0.4';
      els.trialBarFill.style.background = 'linear-gradient(90deg, #10b981, #34d399)';
    } else {
      els.trialBarWrap.style.opacity = '1';
      els.trialBarFill.style.background = remaining > 3
        ? 'linear-gradient(90deg, #3b82f6, #8b5cf6)'
        : 'linear-gradient(90deg, #ef4444, #f59e0b)';
    }

    // وضعیت لایسنس
    if (status.licensed) {
      els.licStatus.textContent = 'فعال ✓';
      els.licStatus.className = 'status-value success';
      els.statusBadge.textContent = 'لایسنس فعال';
      els.statusBadge.className = 'status-badge licensed';
      els.deactivateBtn.disabled = false;
      els.licenseInput.value = status.licenseKey;
      els.lockCard.classList.add('hidden');
    } else if (status.trial.expired) {
      els.licStatus.textContent = 'منقضی ✗';
      els.licStatus.className = 'status-value danger';
      els.statusBadge.textContent = 'دوره آزمایشی تمام شد';
      els.statusBadge.className = 'status-badge expired';
      els.deactivateBtn.disabled = true;
      els.lockCard.classList.remove('hidden');
    } else {
      els.licStatus.textContent = 'در حال آزمایش';
      els.licStatus.className = 'status-value warning';
      els.statusBadge.textContent = `آزمایشی - ${toPersianNumber(remaining)} روز باقی‌مانده`;
      els.statusBadge.className = 'status-badge trial';
      els.deactivateBtn.disabled = true;
      els.lockCard.classList.add('hidden');
    }
  } catch (e) {
    showMessage('خطا در بارگذاری وضعیت: ' + e.message, 'error');
  }
}

// ============================================================
//  رویدادها
// ============================================================

els.copyMachineBtn.addEventListener('click', async () => {
  const text = els.machineIdBox.textContent;
  await window.api.copyText(text);
  showMessage('شناسه دستگاه در کلیپ‌بورد کپی شد.', 'success');
});

els.activateBtn.addEventListener('click', async () => {
  const key = els.licenseInput.value.trim();
  if (!key) {
    showMessage('لطفاً کلید لایسنس را وارد کنید.', 'error');
    return;
  }
  els.activateBtn.disabled = true;
  els.activateBtn.textContent = 'در حال بررسی...';
  try {
    const result = await window.api.activateLicense(key);
    if (result.success) {
      showMessage(result.message, 'success');
      await refreshStatus();
    } else {
      showMessage(result.message, 'error');
    }
  } catch (e) {
    showMessage('خطا: ' + e.message, 'error');
  } finally {
    els.activateBtn.disabled = false;
    els.activateBtn.textContent = 'فعال‌سازی';
  }
});

els.deactivateBtn.addEventListener('click', async () => {
  if (!confirm('آیا از غیرفعال‌سازی لایسنس مطمئن هستید؟')) return;
  try {
    await window.api.deactivateLicense();
    els.licenseInput.value = '';
    showMessage('لایسنس غیرفعال شد.', 'info');
    await refreshStatus();
  } catch (e) {
    showMessage('خطا: ' + e.message, 'error');
  }
});

els.resetTrialBtn.addEventListener('click', async () => {
  if (!confirm('این اقدام فقط برای تست است. دوره آزمایشی بازنشانی شود؟')) return;
  try {
    await window.api.resetTrial();
    showMessage('دوره آزمایشی بازنشانی شد.', 'success');
    await refreshStatus();
  } catch (e) {
    showMessage('خطا: ' + e.message, 'error');
  }
});

// Enter در کادر لایسنس = فعال‌سازی
els.licenseInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    els.activateBtn.click();
  }
});

// بارگذاری اولیه
window.addEventListener('DOMContentLoaded', refreshStatus);
