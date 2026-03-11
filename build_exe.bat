@echo off
REM Windows ortamında EXE oluşturma scripti
python -m pip install --upgrade pyinstaller
pyinstaller --onefile --name "HakanCELIKChat" launcher.py

echo.
echo EXE dosyasi olusturuldu: dist\HakanCELIKChat.exe
pause
