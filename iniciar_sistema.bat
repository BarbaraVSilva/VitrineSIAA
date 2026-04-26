@echo off
TITLE SIAA-2026 - O Crebro do Marketing de Afiliados
COLOR 0A

echo ========================================================
echo   SIAA-2026: INICIALIZANDO ECOSSISTEMA UNIFICADO
echo ========================================================
echo.

:: 1. Verificar dependncias
echo [*] Verificando dependncias...
if not exist "node_modules" (
    echo [!] Node modules no encontrados. Rodando npm install...
    npm install
)

:: 2. Iniciar Backend (Motor Python) em uma nova janela
echo [*] Iniciando Motor Python (Crebro)...
start "SIAA-2026 - Engine" cmd /k "python backend/main.py"

:: 3. Iniciar Servidor Unificado (Express + Dashboard)
echo [*] Iniciando Servidor de Dashboard (Porta 3000)...
echo [*] Acesse: http://localhost:3000
echo.
npm run dev:server

pause
