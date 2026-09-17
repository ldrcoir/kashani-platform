const { contextBridge, ipcRenderer } = require('electron');

// API امنی برای renderer - فقط این متدها از UI قابل دسترسی هستند
contextBridge.exposeInMainWorld('api', {
  getStatus: () => ipcRenderer.invoke('get-status'),
  activateLicense: (licenseKey) => ipcRenderer.invoke('activate-license', licenseKey),
  deactivateLicense: () => ipcRenderer.invoke('deactivate-license'),
  resetTrial: () => ipcRenderer.invoke('reset-trial'),
  copyText: (text) => ipcRenderer.invoke('copy-text', text)
});
