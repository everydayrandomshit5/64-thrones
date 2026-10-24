@echo off
title 64-Thrones: High-Glamour Edition (Phase 6 Playtest)
cd /d "%~dp0"
echo ============================================================
echo Starting 64-Thrones: High-Glamour Edition (Development Build)
echo Running directly from: %CD%
echo ============================================================

"D:\antigravity\renpy-8.3.4-sdk\renpy.exe" .

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Game closed with an error code. Check log above or in log.txt.
    pause
)
