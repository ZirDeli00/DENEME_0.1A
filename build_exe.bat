@echo off
REM Windows ortaminda Hakan CELIK API tabanli uygulamasini EXE yapar
python -m pip install --upgrade pyinstaller
pyinstaller --onefile --name "HakanCELIKChat" --add-data "Hakan_CELIK_Chat.html;." --add-data "knowledge_base;knowledge_base" launcher.py

echo.
echo EXE dosyasi olusturuldu: dist\HakanCELIKChat.exe
pause
