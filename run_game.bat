@echo off
title 64-Thrones: High-Glamour Edition
cd /d "%~dp0"
echo ============================================================
echo Starting 64-Thrones: High-Glamour Edition
echo Running directly from: %CD%
echo ============================================================

if defined RENPY_SDK (
    "%RENPY_SDK%\renpy.exe" .
) else if exist "D:\antigravity\renpy-8.3.4-sdk\renpy.exe" (
    "D:\antigravity\renpy-8.3.4-sdk\renpy.exe" .
) else (
    renpy .
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Game closed with an error code. Check log above or in log.txt.
    pause
)
