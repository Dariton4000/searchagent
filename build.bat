@echo off
echo Building SearchAgent...

REM Check if .venv exists
if not exist .venv\Scripts\python.exe (
    echo Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

echo Installing dependencies...
uv pip install -r requirements.txt --python .venv\Scripts\python.exe

echo Running PyInstaller...
.venv\Scripts\pyinstaller.exe --noconfirm --clean SearchAgent.spec

echo Build complete!
echo The executable is located in the "dist" folder.
pause
