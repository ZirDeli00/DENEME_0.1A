@echo off
cd /d %~dp0
python -m pip install --upgrade pip
python -m pip install pyinstaller
pyinstaller --onefile --name SubwayCmdGame subway_cmd_game.py

echo.
echo EXE hazir: dist\SubwayCmdGame.exe
pause
