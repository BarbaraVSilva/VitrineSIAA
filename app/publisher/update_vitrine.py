import os
import sqlite3
import datetime
import sys
import subprocess
import json

# Path setup root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.core.database import get_connection
from app.core.telegram_logs import send_admin_log

THEME_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../theme.json'))

def load_theme():
    if os.path.exists(THEME_PATH):
        with open(THEME_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"cores": {"primaria": "#ff5722", "fundo": "#f5f5f5", "texto": "#ffffff"}, "modo_campanha": {"ativo": False}}

def generate_html_vitrine():
    theme = load_theme()
    
    conn = get_connection()
    c = conn.cursor()
    # Elege para a vitrine itens ativos E verifica a data (< 30 dias se existir column)
    try:
        c.execute("SELECT id, nome_produto, link_afiliado, data_criacao, categoria FROM produtos WHERE estoque_ok = 1 ORDER BY id DESC")
    except:
        c.execute("SELECT id, nome_produto, link_afiliado, strftime('%Y-%m-%d %H:%M:%S', 'now') as data_criacao, 'Geral' as categoria FROM produtos WHERE estoque_ok = 1 ORDER BY id DESC")
    
    todos_ativos = c.fetchall()
    
    # Filtrar produtos criados há menos de 30 dias e agrupar por categoria
    ativos_por_categoria = {}
    agora = datetime.datetime.now()
    
    for row in todos_ativos:
        p_id, nome, link, dt_str, categoria = row
        cat = categoria if categoria else 'Geral'
        
        try:
            dt_criacao = datetime.datetime.strptime(dt_str.split(".")[0], "%Y-%m-%d %H:%M:%S")
            if (agora - dt_criacao).days <= 30:
                if cat not in ativos_por_categoria: ativos_por_categoria[cat] = []
                ativos_por_categoria[cat].append((p_id, nome, link))
        except Exception:
            if cat not in ativos_por_categoria: ativos_por_categoria[cat] = []
            ativos_por_categoria[cat].append((p_id, nome, link))
            
    conn.close()

    nav_links = ""
    sections_html = ""
    
    if not ativos_por_categoria:
        sections_html = "<div style='text-align: center; padding: 3rem;'>Nenhum achado recente. O robô já está caçando mais nas próximas horas!</div>"
    else:
        for cat, produtos in ativos_por_categoria.items():
            cat_id = cat.replace(" ", "_").replace("ç", "c").replace("ã", "a").lower()
            nav_links += f"<a href='#{cat_id}' style='margin: 0 10px; color: {theme['cores']['texto']}; text-decoration: none; font-weight: bold; font-family: sans-serif;'>{cat}</a>"
            
            sections_html += f"<section id='{cat_id}' style='margin-top: 40px;'>"
            sections_html += f"<h2 style='color: {theme['cores'].get('secundaria', '#212121')}; border-bottom: 2px solid {theme['cores']['primaria']}; padding-bottom: 5px; font-family: sans-serif;'>📌 {cat}</h2>"
            sections_html += "<div style='display: flex; flex-direction: column;'>"
            
            for idx, (p_id, nome, link) in enumerate(produtos):
                delay = idx * 0.1
                sections_html += f"""
                <div class="product-card" style="animation-delay: {delay}s; border: 1px solid {theme['cores']['primaria']}; border-radius: 8px; margin: 10px 0; padding: 15px; background: {theme['cores']['texto']};">
                    <div class="product-title" style="color: {theme['cores'].get('secundaria', '#212121')}; font-weight: bold; font-family: sans-serif;">{nome}</div>
                    <a href="{link}" target="_blank" rel="noopener noreferrer" class="product-link" style="display: block; margin-top: 10px; color: {theme['cores']['primaria']}; text-decoration: none; font-weight: bold; font-family: sans-serif;">🔥 Comprar com Desconto</a>
                </div>
                """
            sections_html += "</div></section>"

    # Verificar Modo Campanha
    is_campanha = False
    hoje_md = agora.strftime("%d-%m") # Ex: 11-11
    modo_c = theme.get("modo_campanha", {})
    if modo_c.get("ativo", False) or hoje_md in modo_c.get("dias_de_evento", []):
        is_campanha = True
        
    titulo = modo_c.get("titulo", "SALDÃO RELÂMPAGO SHOPEE") if is_campanha else "💎 Vitrine VIP 💎"
    descricao = modo_c.get("descricao", "Aproveite agora!") if is_campanha else "As melhores oportunidades, separadas a dedo."

    # Renderizando Botões Pessoais de "Minhas Coleções"
    coles = theme.get("colecoes", [])
    colecoes_html = ""
    if coles:
        colecoes_html += "<div style='margin-top: 15px; display: flex; flex-direction: column; align-items: center; gap: 10px;'>"
        for col in coles:
            colecoes_html += f"<a href='{col['url']}' target='_blank' rel='noopener noreferrer' style='background-color: {theme['cores']['texto']}; color: {theme['cores']['primaria']}; padding: 10px 20px; border-radius: 25px; text-decoration: none; font-weight: bold; font-family: sans-serif; box-shadow: 0 4px 6px rgba(0,0,0,0.2);'>🎁 {col['nome']}</a>"
        colecoes_html += "</div>"

    html_template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{theme.get('logotipo', 'SIAA DEALS')} - Achadinhos</title>
    <style>body {{ font-family: sans-serif; background-color: {theme['cores']['fundo']}; margin: 0; padding: 20px; scroll-behavior: smooth; }}</style>
</head>
<body>
    <header style="text-align: center; padding: 20px; background-color: {theme['cores'].get('primaria', '#ff5722')}; color: white; border-radius: 10px; margin-bottom: 20px; position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="margin:0;">{titulo}</h1>
        <p style="margin:5px 0 10px 0;">{descricao}</p>
        {colecoes_html}
        <nav style="display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 10px;">
            {nav_links}
        </nav>
    </header>
    
    <main style="max-width: 600px; margin: 0 auto;">
        {sections_html}
    </main>
    
    <footer style="text-align: center; margin-top: 40px; font-size: 0.8em; color: gray;">
        <p>Atualizado automaticamente pelo Robô SIAA-2026 em: {agora.strftime('%d/%m/%Y %H:%M')}</p>
    </footer>
</body>
</html>
"""

    vitrine_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vitrine'))
    os.makedirs(vitrine_dir, exist_ok=True)
    html_path = os.path.join(vitrine_dir, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_template)
        
    total_ativos = sum(len(v) for v in ativos_por_categoria.values())
    print(f"[PUBLISHER/VITRINE] Gerada com sucesso! HTML injetado com {total_ativos} produtos ativos segmentados.")
    
    # Realiza push do Github (Vitrine Hospedada)
    git_push_vitrine(vitrine_dir)
    
def git_push_vitrine(work_dir):
    try:
        # Comando de automação de git (assumindo git pre-configurado)
        # O stderr=subprocess.DEVNULL vai suprimir erros pra não travar a aplicação, servindo de Fallback
        orig_dir = os.getcwd()
        os.chdir(work_dir)
        
        subprocess.run(["git", "add", "index.html"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "Auto-update Vitrine VIP"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        os.chdir(orig_dir)
        print("[VITRINE] Github Pages sinalizado! Pode levar 1 minuto até atualizar o site.")
        
        send_admin_log("📦 Vitrine Inteligente Atualizada! O Push para o Github Pages foi realizado com sucesso.")
    except Exception as e:
        print(f"[VITRINE] Git Push Ignorado (Git não instalado ou repositório não configurado localmente): {e}")

if __name__ == "__main__":
    generate_html_vitrine()
