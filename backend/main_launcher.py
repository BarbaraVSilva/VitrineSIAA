import subprocess
import os
import sys
import time
import signal

# Processos a serem iniciados
COMMANDS = [
    ("SIAA Cerebro", ["python", "main.py"]),
    ("Crawler Telegram", ["python", "app/mineracao/crawler_telegram.py"]),
    ("Streamlit Dashboard", ["streamlit", "run", "app/dashboard/dashboard.py"]),
    ("Webhook Server", ["python", "-m", "app.webhook_server"]),
    ("Instagram Auto-DM", ["python", "app/social_interactions/instagram_bot.py"])
]

processes = []

def signal_handler(sig, frame):
    print("\n\n[SIAA] Recebido sinal de interrupção (Ctrl+C). Encerrando os processos com segurança...")
    for p in processes:
        try:
            p.terminate()
        except:
            pass
    print("[SIAA] Todos os serviços encerrados. Até logo!")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("=" * 60)
    print("        INICIALIZANDO O ECOSSISTEMA SIAA-2026 UNIFICADO")
    print("=" * 60)
    print("Iniciando todos os Cripto-Processos em paralelo...\n")

    for name, cmd in COMMANDS:
        print(f"[*] Iniciando: {name}...")
        # Usa Popen para iniciar em subprocesso
        # Não redirecionamos o output para que todos apareçam no mesmo terminal com a Matrix agrupada.
        p = subprocess.Popen(cmd, shell=True if sys.platform == 'win32' else False)
        processes.append(p)
        time.sleep(2)
        
    print("\n" + "=" * 60)
    print("🚀 SUCESSO! CLUSTER ONLINE!")
    print("🌐 Dashboard operando em: http://localhost:8088/pro ou Painel Streamlit Local")
    print("❌ Pressione Ctrl+C a qualquer momento para fechar TODOS os bots simultaneamente.")
    print("=" * 60 + "\n")

    # Mantém o processo principal vivo esperando
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
