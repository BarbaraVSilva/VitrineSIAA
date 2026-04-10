@echo off
cd /d "%~dp0"
echo ==================================================
echo         INICIALIZANDO O CEREBRO SIAA-2026
echo ==================================================
echo.

REM Verifica se a pasta venv existe e prepara o comando de ativacao
if exist venv\Scripts\activate.bat (
    set VENV_CMD=call venv\Scripts\activate.bat ^&^& 
    echo [INFO] Ambiente virtual ativado com sucesso!
) else (
    set VENV_CMD=
    echo [AVISO] Nenhum ambiente virtual detectado. O Python global sera usado.
)
echo [.] Executando Orquestrador Unificado...
%VENV_CMD% python iniciar_unico.py

echo.
echo ==================================================
echo SISTEMA SIAA FINALIZADO.
echo ==================================================
pause >nul
