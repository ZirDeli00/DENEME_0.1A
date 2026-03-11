@echo off
setlocal

set ZIP_NAME=flipy-bird-package.zip
if exist %ZIP_NAME% del /f /q %ZIP_NAME%

powershell -NoProfile -Command "Compress-Archive -Path index.html,README.md,start_windows.bat -DestinationPath %ZIP_NAME% -Force"

if errorlevel 1 (
  echo [HATA] ZIP olusturulamadi.
  pause
  exit /b 1
)

echo Basarili: %ZIP_NAME%
echo Artik bu ZIP dosyasini Drive/WeTransfer'a yukleyip link paylasabilirsin.

endlocal
