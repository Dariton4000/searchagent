@echo off

REM Check if .venv exists
if not exist .venv\Scripts\python.exe (
	echo Virtual environment not found. Please run install.bat first.
	pause
	exit /b 1
)

echo Ensuring dependencies are installed (uv)...
uv pip install -r requirements.txt --python .venv\Scripts\python.exe

echo Starting the research agent...
.venv\Scripts\python.exe main.py

pause