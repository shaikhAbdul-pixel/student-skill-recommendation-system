@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" goto missing
".venv\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 pause
exit /b
:missing
echo Run setup_windows.bat first, or follow README.md.
pause
exit /b 1
