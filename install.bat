@echo off

echo Creating virtual environment...
uv venv -p 3.11

echo Installing dependencies...
uv pip install -r requirements.txt --python .venv\Scripts\python.exe

echo Setting up crawl4ai...
.venv\Scripts\crawl4ai-setup.exe

echo Installation complete.
pause