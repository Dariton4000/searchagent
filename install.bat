@echo off

echo Creating virtual environment...
uv venv -p 3.11


echo Activating virtual environment...
call .venv\Scripts\activate


echo Installing dependencies...
uv pip install -r requirements.txt

echo Setting up crawl4ai...
crawl4ai-setup

echo Installation complete.
pause