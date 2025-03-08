@echo off
set "subdir=venv"

if exist "%cd%\%subdir%\" (
    start "" .\\venv\\Scripts\\pythonw .\\window.py
    exit
)

python -m venv venv

.\\venv\\Scripts\\pip3.exe install -r .\\requirements.txt
.\\venv\\Scripts\\pythonw .\\window.py