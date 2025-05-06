@echo off
setlocal

REM --- Edit this subdomain to your desired one ---
set SUBDOMAIN=myaiagent

REM Activate virtual environment
call .\venv\Scripts\activate.bat

REM Start Flask app (on port 5000)
start cmd /k python app.py

REM Wait a few seconds to make sure Flask has started
timeout /t 5

REM Start localtunnel on the same port (5000)
start cmd /k lt --port 5000 --subdomain %SUBDOMAIN%

endlocal
