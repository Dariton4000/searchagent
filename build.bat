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
pyinstaller --noconfirm --onefile --console --name "SearchAgent" --clean ^
    --collect-all crawl4ai ^
    --collect-all lmstudio ^
    --collect-all rich ^
    --hidden-import=tiktoken_ext.openai_public ^
    --hidden-import=tiktoken_ext ^
    main.py

echo Build complete!
echo The executable is located in the "dist" folder.
pause
