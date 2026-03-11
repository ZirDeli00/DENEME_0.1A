@echo off
setlocal

where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi.
  echo Lutfen Python yukleyin ve PATH'e ekleyin: https://www.python.org/downloads/
  pause
  exit /b 1
)

echo Tarayici aciliyor: http://localhost:4173
start "" http://localhost:4173

echo Sunucu baslatiliyor (kapatmak icin Ctrl+C)...
python -m http.server 4173

endlocal
