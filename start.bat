@echo off

echo Activating virtual environment...
call .venv\Scripts\activate

echo Starting LM-Studio Server
lms server start

echo Starting the research agent...
python main.py

echo Deactivating virtual environment...
deactivate

pause