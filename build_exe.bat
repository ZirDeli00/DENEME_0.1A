@echo off
setlocal

where python >nul 2>nul
if errorlevel 1 (
  echo [HATA] Python bulunamadi. https://www.python.org/downloads/
  pause
  exit /b 1
)

python -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
  echo PyInstaller yukleniyor...
  python -m pip install pyinstaller
)

echo EXE olusturuluyor...
python -m PyInstaller --noconfirm --onefile --name FlipyBird launcher.py

if errorlevel 1 (
  echo [HATA] EXE olusturma basarisiz.
  pause
  exit /b 1
)

echo Basarili: dist\FlipyBird.exe
pause
endlocal
