@echo off
setlocal
cd /d "%~dp0"
echo Setting up Student Skill Recommendation System...
echo Python 3.10 or 3.11 must be installed. Internet is needed for dependencies.
python --version
if errorlevel 1 goto fail
if not exist ".venv\Scripts\python.exe" python -m venv .venv
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
echo Setup complete. Double-click run_windows.bat to open the app.
pause
exit /b 0
:fail
echo Setup did not complete. Check the error above and README.md.
pause
exit /b 1
