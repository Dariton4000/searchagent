@echo off
echo Building SearchAgent...

REM Check if .venv exists
if exist .venv (
    echo Activating virtual environment...
    call .venv\Scripts\activate
) else (
    echo Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

echo Installing dependencies...
pip install -r requirements.txt

echo Running PyInstaller...
pyinstaller --noconfirm --clean SearchAgent.spec

echo Build complete!
echo The executable is located in the "dist" folder.
pause
