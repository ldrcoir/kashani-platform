; ============================================================
;  LicenseDemo - NSIS Installer Script
;  ساخته‌شده برای ساخت setup.exe واقعی بدون نیاز به wine
; ============================================================

!define APP_NAME "LicenseDemo"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Demo Author"
!define APP_EXE "LicenseDemo.exe"
!define APP_REGKEY "Software\LicenseDemo"
!define APP_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\LicenseDemo"

; ---------- تنظیمات اصلی ----------
Name "${APP_NAME}"
OutFile "LicenseDemo-Setup-${APP_VERSION}.exe"
Unicode true
ShowInstDetails show
ShowUnInstDetails show
SetCompressor /SOLID lzma
RequestExecutionLevel user

InstallDir "$LOCALAPPDATA\${APP_NAME}"
InstallDirRegKey HKCU "${APP_REGKEY}" "InstallDir"

; ---------- اطلاعات نسخه ----------
VIProductVersion "1.0.0.0"
VIAddVersionKey "ProductName" "${APP_NAME}"
VIAddVersionKey "FileVersion" "${APP_VERSION}"
VIAddVersionKey "ProductVersion" "${APP_VERSION}"
VIAddVersionKey "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey "FileDescription" "${APP_NAME} Installer"
VIAddVersionKey "LegalCopyright" "Copyright (c) 2026 ${APP_PUBLISHER}"

; ---------- MUI (Modern UI) ----------
!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "FileFunc.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "اجرای ${APP_NAME}"
!define MUI_FINISHPAGE_SHOWREADME ""
!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED

!define MUI_WELCOMEPAGE_TITLE "خوش آمدید به نصب ${APP_NAME}"
!define MUI_WELCOMEPAGE_TEXT "این ویزارد شما را در نصب ${APP_NAME} راهنمایی می‌کند.$\r$\n$\r$\nروی «بعدی» کلیک کنید تا ادامه دهید."

; زبان فارسی در NSIS به‌طور پیش‌فرض موجود نیست، از انگلیسی استفاده می‌کنیم
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "/home/z/my-project/scripts/license.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

; ============================================================
;  بخش نصب
; ============================================================
Section "Install" SecInstall
  SectionIn RO

  ; تنظیم مسیر خروجی
  SetOutPath "$INSTDIR"

  ; کپی همه فایل‌های win-unpacked
  File /r "/home/z/my-project/electron-license-app/build/win-unpacked\*.*"

  ; ذخیره مسیر نصب در رجیستری
  WriteRegStr HKCU "${APP_REGKEY}" "InstallDir" "$INSTDIR"
  WriteRegStr HKCU "${APP_REGKEY}" "Version" "${APP_VERSION}"

  ; ساخت کلید حذف در Add/Remove Programs
  WriteRegStr HKCU "${APP_UNINST_KEY}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKCU "${APP_UNINST_KEY}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "${APP_UNINST_KEY}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKCU "${APP_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${APP_EXE}"
  WriteRegStr HKCU "${APP_UNINST_KEY}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
  WriteRegStr HKCU "${APP_UNINST_KEY}" "InstallLocation" "$INSTDIR"
  WriteRegDWORD HKCU "${APP_UNINST_KEY}" "NoModify" 1
  WriteRegDWORD HKCU "${APP_UNINST_KEY}" "NoRepair" 1

  ; محاسبه حجم تقریبی برای Add/Remove Programs
  ${GetSize} "$INSTDIR" "/S=0K" $0 $1 $2
  IntFmt $0 "0x%08X" $0
  WriteRegDWORD HKCU "${APP_UNINST_KEY}" "EstimatedSize" "$0"

  ; ساخت uninstaller
  WriteUninstaller "$INSTDIR\uninstall.exe"

  ; ساخت شورتکات‌ها
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0
  CreateShortCut "$SMPROGRAMS\${APP_NAME}\حذف ${APP_NAME}.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}" "" "$INSTDIR\${APP_EXE}" 0

  SectionEnd

; ============================================================
;  بخش حذف
; ============================================================
Section "Uninstall"
  ; حذف فایل‌ها
  RMDir /r /REBOOTOK "$INSTDIR"

  ; حذف شورتکات‌ها
  RMDir /r "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\${APP_NAME}.lnk"

  ; حذف کلیدهای رجیستری
  DeleteRegKey HKCU "${APP_UNINST_KEY}"
  DeleteRegKey HKCU "${APP_REGKEY}"
SectionEnd
