import os
import sqlite3
import datetime
import sys
import subprocess
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.core.database import get_connection
from app.core.telegram_logs import send_admin_log

THEME_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../theme.json'))

def load_theme():
    if os.path.exists(THEME_PATH):
        with open(THEME_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "logotipo": "Shopee Radar VIP",
        "cores": {"primaria": "#ff5722"},
        "colecoes": [],
        "modo_campanha": {"ativo": False}
    }

def generate_html_vitrine():
    theme = load_theme()
    agora = datetime.datetime.now()

    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT p.id, p.nome_produto, p.link_afiliado, p.data_criacao, p.categoria, a.midia_path
            FROM produtos p
            LEFT JOIN achados a ON p.achado_id = a.id
            WHERE p.estoque_ok = 1
            ORDER BY p.id DESC
            LIMIT 20
        """)
    except Exception:
        c.execute("""
            SELECT id, nome_produto, link_afiliado,
                   strftime('%Y-%m-%d %H:%M:%S', 'now') as data_criacao,
                   'Geral' as categoria, NULL as midia_path
            FROM produtos WHERE estoque_ok = 1 ORDER BY id DESC LIMIT 20
        """)
    produtos = c.fetchall()
    conn.close()

    # ── Coleta dados por categoria ──
    recentes = []
    por_categoria = {}
    for row in produtos:
        p_id, nome, link, dt_str, categoria, midia = row
        cat = categoria or 'Geral'
        try:
            dt = datetime.datetime.strptime(dt_str.split('.')[0], "%Y-%m-%d %H:%M:%S")
            dias = (agora - dt).days
        except Exception:
            dias = 0

        item = {"id": p_id, "nome": nome, "link": link, "dias": dias, "midia": midia or ""}
        recentes.append(item)
        if cat not in por_categoria:
            por_categoria[cat] = []
        por_categoria[cat].append(item)

    # ── Coleções (do theme.json) ──
    colecoes = theme.get("colecoes", [])
    colecoes_html = ""
    for col in colecoes:
        colecoes_html += f"""
        <a href="{col['url']}" target="_blank" rel="noopener noreferrer" class="link-btn">
            <span class="link-icon">🛍️</span>
            <span class="link-text">{col['nome']}</span>
            <span class="link-arrow">→</span>
        </a>"""

    # ── Últimos produtos como cards ──
    cards_html = ""
    for item in recentes[:12]:
        badge = f"<span class='badge'>🆕 {item['dias']}d atrás</span>" if item['dias'] <= 3 else ""
        midia_tag = ""
        if item['midia'] and os.path.exists(item['midia']) and not item['midia'].endswith(('.mp4','.mov')):
            # Converte path local para nada (no GitHub Pages não há acesso ao disco local)
            pass

        cards_html += f"""
        <a href="{item['link']}" target="_blank" rel="noopener noreferrer" class="product-card">
            <div class="card-content">
                <div class="card-name">{item['nome']}</div>
                {badge}
            </div>
            <div class="card-cta">Ver oferta →</div>
        </a>"""

    # ── Categorias como links ──
    cats_html = ""
    for cat, itens in por_categoria.items():
        cats_html += f"""
        <div class="category-section">
            <h3 class="cat-title">📌 {cat}</h3>
            <div class="cat-grid">"""
        for item in itens[:6]:
            cats_html += f"""
                <a href="{item['link']}" target="_blank" rel="noopener noreferrer" class="cat-card">
                    <div class="cat-card-name">{item['nome']}</div>
                    <div class="cat-card-cta">🔥 Comprar</div>
                </a>"""
        cats_html += "</div></div>"

    # Modo campanha
    modo_c = theme.get("modo_campanha", {})
    hoje_md = agora.strftime("%d-%m")
    is_campanha = modo_c.get("ativo", False) or hoje_md in modo_c.get("dias_de_evento", [])
    titulo = modo_c.get("titulo", f"✨ {theme.get('logotipo', 'Vitrine VIP')}") if is_campanha else f"✨ {theme.get('logotipo', 'Vitrine VIP')}"
    subtitulo = modo_c.get("descricao", "As melhores ofertas, separadas a dedo") if is_campanha else "As melhores ofertas, separadas a dedo 🛒"

    banner_class = "is-campanha" if is_campanha else ""

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{theme.get('logotipo', 'Vitrine VIP')} · Melhores Ofertas Shopee</title>
  <meta name="description" content="Achadinhos selecionados com os melhores descontos da Shopee. Links de afiliado curados automaticamente.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Inter', sans-serif;
      background: #0D0F14;
      color: #E8EAF0;
      min-height: 100vh;
      padding-bottom: 48px;
    }}

    /* ── HERO ── */
    .hero {{
      background: linear-gradient(160deg, #1a0a00 0%, #130a1a 40%, #0D0F14 100%);
      padding: 48px 20px 36px;
      text-align: center;
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: '';
      position: absolute;
      top: -80px; left: 50%;
      transform: translateX(-50%);
      width: 400px; height: 400px;
      background: radial-gradient(circle, rgba(255,107,53,0.18) 0%, transparent 70%);
      pointer-events: none;
    }}
    .hero-avatar {{
      width: 90px; height: 90px;
      border-radius: 50%;
      background: linear-gradient(135deg, #FF6B35, #FF4500);
      display: inline-flex; align-items: center; justify-content: center;
      font-size: 2.5rem;
      margin-bottom: 16px;
      box-shadow: 0 0 40px rgba(255,107,53,0.5);
    }}
    .hero-title {{
      font-size: 1.6rem; font-weight: 800;
      color: #fff;
      letter-spacing: -0.02em;
      line-height: 1.2;
    }}
    .hero-title span {{ color: #FF6B35; }}
    .hero-sub {{
      color: #8B90A0; font-size: 0.9rem;
      margin-top: 8px; line-height: 1.5;
    }}
    .hero-badge {{
      display: inline-block;
      background: rgba(255,107,53,0.15);
      border: 1px solid rgba(255,107,53,0.3);
      color: #FF6B35;
      font-size: 0.75rem; font-weight: 600;
      padding: 4px 12px; border-radius: 20px;
      margin-top: 12px;
    }}
    .is-campanha .hero-badge {{
      background: linear-gradient(135deg, #FF6B35, #FF4500);
      color: white;
      animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ box-shadow: 0 0 0 0 rgba(255,107,53,0.4); }}
      50% {{ box-shadow: 0 0 0 8px rgba(255,107,53,0); }}
    }}

    /* ── CONTAINER ── */
    .container {{
      max-width: 480px;
      margin: 0 auto;
      padding: 0 16px;
    }}

    /* ── SEÇÃO ── */
    .section {{ margin-top: 32px; }}
    .section-title {{
      font-size: 0.72rem; font-weight: 700;
      color: #8B90A0;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 12px;
      display: flex; align-items: center; gap: 8px;
    }}
    .section-title::after {{
      content: '';
      flex: 1; height: 1px;
      background: rgba(255,255,255,0.07);
    }}

    /* ── LINK BUTTONS (Coleções) ── */
    .link-btn {{
      display: flex; align-items: center; gap: 12px;
      background: rgba(255,255,255,0.05);
      border: 1px solid rgba(255,255,255,0.09);
      border-radius: 14px;
      padding: 16px 18px;
      margin-bottom: 10px;
      text-decoration: none;
      color: #E8EAF0;
      font-weight: 600; font-size: 0.95rem;
      transition: all 0.2s ease;
    }}
    .link-btn:hover {{
      background: rgba(255,107,53,0.12);
      border-color: rgba(255,107,53,0.4);
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(255,107,53,0.2);
    }}
    .link-icon {{ font-size: 1.3rem; }}
    .link-text {{ flex: 1; }}
    .link-arrow {{ color: #FF6B35; font-size: 1.1rem; }}

    /* ── PRODUCT CARDS (recentes) ── */
    .product-card {{
      display: flex; align-items: center;
      justify-content: space-between;
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.07);
      border-radius: 12px;
      padding: 14px 16px;
      margin-bottom: 8px;
      text-decoration: none;
      color: #E8EAF0;
      transition: all 0.2s ease;
    }}
    .product-card:hover {{
      border-color: rgba(255,107,53,0.35);
      background: rgba(255,107,53,0.06);
    }}
    .card-content {{ flex: 1; min-width: 0; }}
    .card-name {{
      font-size: 0.88rem; font-weight: 600;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .badge {{
      display: inline-block;
      background: rgba(34,197,94,0.15);
      color: #22C55E;
      font-size: 0.68rem; font-weight: 700;
      padding: 2px 8px; border-radius: 6px;
      margin-top: 4px;
    }}
    .card-cta {{
      color: #FF6B35; font-size: 0.82rem; font-weight: 700;
      white-space: nowrap; margin-left: 12px;
    }}

    /* ── CATEGORIA ── */
    .category-section {{ margin-top: 28px; }}
    .cat-title {{
      color: #E8EAF0; font-size: 0.9rem; font-weight: 700;
      margin-bottom: 10px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(255,107,53,0.2);
    }}
    .cat-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }}
    .cat-card {{
      background: rgba(255,255,255,0.04);
      border: 1px solid rgba(255,255,255,0.07);
      border-radius: 10px;
      padding: 12px 14px;
      text-decoration: none;
      color: #E8EAF0;
      transition: all 0.2s;
    }}
    .cat-card:hover {{
      border-color: rgba(255,107,53,0.35);
      background: rgba(255,107,53,0.07);
    }}
    .cat-card-name {{
      font-size: 0.8rem; font-weight: 600;
      overflow: hidden; display: -webkit-box;
      -webkit-line-clamp: 2; -webkit-box-orient: vertical;
      line-height: 1.3; margin-bottom: 8px;
    }}
    .cat-card-cta {{
      color: #FF6B35; font-size: 0.75rem; font-weight: 700;
    }}

    /* ── FOOTER ── */
    .footer {{
      text-align: center; margin-top: 48px;
      color: #3D4050; font-size: 0.72rem;
    }}
    .footer a {{ color: #FF6B35; text-decoration: none; }}
  </style>
</head>
<body>

  <!-- HERO -->
  <div class="hero {banner_class}">
    <div class="hero-avatar">🔥</div>
    <h1 class="hero-title">{titulo}</h1>
    <p class="hero-sub">{subtitulo}</p>
    <span class="hero-badge">⚡ Atualizado automaticamente · {agora.strftime('%d/%m/%Y %H:%M')}</span>
  </div>

  <!-- CONTEÚDO -->
  <div class="container">

    <!-- Coleções -->
    {"" if not colecoes_html else f'''
    <div class="section">
      <p class="section-title">Minhas Coleções</p>
      {colecoes_html}
    </div>
    '''}

    <!-- Produtos Recentes -->
    {"" if not cards_html else f'''
    <div class="section">
      <p class="section-title">Achados Recentes</p>
      {cards_html}
    </div>
    '''}

    <!-- Por Categoria -->
    {"" if not cats_html else f'''
    <div class="section">
      <p class="section-title">Por Categoria</p>
      {cats_html}
    </div>
    '''}

    {"<div style='text-align:center;padding:60px 20px;color:#3D4050;'>Nenhum produto aprovado ainda. O robô está caçando as melhores ofertas! 🤖</div>" if not recentes else ""}

    <div class="footer">
      <p>Gerado por <a href="https://github.com/BarbaraVSilva/VitrineSIAA">SIAA-2026</a> · Sistema Inteligente de Automação de Afiliados</p>
    </div>
  </div>

</body>
</html>"""

    vitrine_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../vitrine'))
    os.makedirs(vitrine_dir, exist_ok=True)
    html_path = os.path.join(vitrine_dir, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    total = len(recentes)
    print(f"[VITRINE] Linktree Premium gerado com {total} produto(s).")
    git_push_vitrine(vitrine_dir)

def git_push_vitrine(work_dir):
    try:
        orig = os.getcwd()
        os.chdir(work_dir)
        subprocess.run(["git", "add", "index.html"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "commit", "-m", "Auto-update Vitrine VIP"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.chdir(orig)
        print("[VITRINE] Push GitHub Pages realizado com sucesso!")
        send_admin_log("📦 Vitrine (Linktree) atualizada no GitHub Pages!")
    except Exception as e:
        print(f"[VITRINE] Git Push ignorado: {e}")

if __name__ == "__main__":
    generate_html_vitrine()
