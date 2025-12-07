@echo off

echo Creating virtual environment...
py -3.11 -m venv .venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment with Python 3.11.
    echo Please ensure Python 3.11 is installed and accessible via 'py' launcher.
    pause
    exit /b %errorlevel%
)

echo Activating virtual environment...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b %errorlevel%
)

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo Setting up crawl4ai...
crawl4ai-setup

echo Deactivating virtual environment...
call deactivate

echo Installation complete.
pause