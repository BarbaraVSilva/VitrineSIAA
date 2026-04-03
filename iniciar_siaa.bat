@echo off
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
echo.

echo [1/4] Iniciando o Cerebro Principal...
start "SIAA - Cerebro" cmd /k "%VENV_CMD% python main.py"
timeout /t 2 /nobreak >nul

echo [2/4] Iniciando o Capturador do Telegram...
start "SIAA - Crawler Telegram" cmd /k "%VENV_CMD% python app\mineracao\crawler_telegram.py"
timeout /t 2 /nobreak >nul

echo [3/4] Iniciando o Dashboard Streamlit...
start "SIAA - Dashboard" cmd /k "%VENV_CMD% streamlit run app\dashboard\dashboard.py"
timeout /t 2 /nobreak >nul

echo [4/5] Iniciando o Servidor Webhook Geral...
start "SIAA - Webhook" cmd /k "%VENV_CMD% uvicorn app.webhook_server:app --port 6000"
timeout /t 2 /nobreak >nul

echo [5/5] Iniciando o Auto-DM Webhook (ManyChat Clone)...
start "SIAA - Auto DM Instagram" cmd /k "%VENV_CMD% python app\social_interactions\instagram_bot.py"

echo.
echo ==================================================
echo SUCESSO! 5 Janelas foram abertas.
echo Nao feche as janelas pretas recem-abertas, 
echo minimize elas para que os robos continuem rodando!
echo ==================================================
echo Pressione qualquer tecla para sair deste inicializador...
pause >nul
