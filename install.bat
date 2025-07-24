@echo off

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Setting up crawl4ai...
crawl4ai-setup

echo Deactivating virtual environment...
deactivate

echo Installation complete.
pause