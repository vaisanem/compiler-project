@echo off
poetry run main %*
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%