@echo off
chcp 65001 >nul
title La Isla de los Cuentos - Recuperar cuenta docente
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  Primero abri iniciar.bat una vez para que se prepare el juego.
  echo.
  pause
  exit /b 1
)
set PYTHONIOENCODING=utf-8
".venv\Scripts\python.exe" -B recuperar_cuenta.py
pause
