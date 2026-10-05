@echo off
chcp 65001 >nul
title La Isla de los Cuentos
cd /d "%~dp0"

set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY (where python >nul 2>nul && set "PY=python")
if not defined PY goto :sinpython

if not exist ".venv\Scripts\python.exe" (
  echo.
  echo  Preparando La Isla de los Cuentos por primera vez...
  echo  ^(esto tarda un minuto y necesita internet solo esta vez^)
  echo.
  %PY% -m venv .venv || goto :error
  ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error
)

".venv\Scripts\python.exe" app.py %*
pause
exit /b

:sinpython
echo.
echo  No se encontro Python en esta computadora.
echo  1. Descargalo de https://www.python.org/downloads/
echo  2. Al instalarlo, marca la casilla "Add Python to PATH".
echo  3. Volve a abrir este archivo.
echo.
pause
exit /b

:error
echo.
echo  Ocurrio un error al preparar el programa. Revisa la conexion a internet y volve a intentar.
pause
