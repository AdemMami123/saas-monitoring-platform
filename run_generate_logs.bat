@echo off
REM Helper script to run generate_logs.py in WSL virtual environment

echo Running log generator in virtual environment...
wsl -d Ubuntu bash -c "cd /home/ademm/saas-monitoring-platform && source venv/bin/activate && python generate_logs.py"

echo.
echo Done! Check the uploads/ folder for generated files.
pause
