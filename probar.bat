@echo off
chcp 65001 >nul
title La Isla de los Cuentos - Pruebas
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  Primero abri iniciar.bat una vez para que se prepare el juego.
  echo.
  pause
  exit /b 1
)

echo.
echo  Corriendo las pruebas automaticas (no tocan los datos reales)...
echo.
set PYTHONIOENCODING=utf-8
".venv\Scripts\python.exe" -B -m unittest discover -s tests -v
if errorlevel 1 (
  echo.
  echo  *** HAY PRUEBAS QUE FALLARON. Revisa los mensajes de arriba. ***
) else (
  echo.
  echo  Todas las pruebas pasaron.
)
echo.
pause
