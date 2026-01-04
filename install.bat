@echo off

REM Create .env with placeholders (do not overwrite an existing one)
if not exist ".env" (
	echo Creating .env file with placeholders...
	(
		echo # OpenAI API key (required)
		echo OPENAI_API_KEY=
		echo.
		echo # Optional: model name (default: gpt-5-mini)
		echo OPENAI_MODEL=gpt-5-mini
		echo.
        echo # Optional: low ^| medium ^| high (default: medium)
		echo OPENAI_REASONING_EFFORT=medium
		echo.
		echo # Optional: custom OpenAI-compatible endpoint (leave blank for default)
		echo OPENAI_BASE_URL=
	) > ".env"
) else (
	echo .env already exists; leaving it unchanged.
)

echo Creating virtual environment...
uv venv -p 3.11

echo Installing dependencies...
uv pip install -r requirements.txt --python .venv\Scripts\python.exe

echo Setting up crawl4ai...
.venv\Scripts\crawl4ai-setup.exe

echo Installation complete.
pause