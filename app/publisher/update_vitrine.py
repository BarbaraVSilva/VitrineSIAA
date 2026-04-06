import os
import sys
import datetime
import html
import subprocess
import json
from urllib.parse import urlparse

# Suporta execução direta `python app/publisher/update_vitrine.py` sem pacote instalado.
_proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

from app.core.database import get_connection
from app.core.telegram_logs import send_admin_log
from app.publisher.vitrine_html import build_vitrine_page_html

THEME_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../theme.json'))


def _safe_href(url: str) -> str:
    if not url:
        return "#"
    p = urlparse(url.strip())
    if p.scheme not in ("http", "https"):
        return "#"
    return html.escape(url, quote=True)


def _safe_text(s: object) -> str:
    return html.escape("" if s is None else str(s))


def _safe_css_url(path: str) -> str:
    """Caminho seguro dentro de url('...') em CSS (sem aspas nem parênteses)."""
    if not path:
        return ""
    p = path.replace("\\", "/").replace("'", "").replace('"', "").replace("(", "").replace(")", "")
    return html.escape(p, quote=False)


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

        # Copiar imagem para a pasta da vitrine (para o GitHub Pages servir)
        midia_url = ""
        if midia and os.path.exists(midia) and not midia.lower().endswith(('.mp4','.mov')):
            import shutil
            assets_dir = os.path.join(os.path.dirname(__file__), '../../vitrine/media')
            os.makedirs(assets_dir, exist_ok=True)
            fname = os.path.basename(midia)
            shutil.copy2(midia, os.path.join(assets_dir, fname))
            midia_url = f"media/{fname}"

        item = {"id": p_id, "nome": nome, "link": link, "dias": dias, "midia": midia_url}
        recentes.append(item)
        if cat not in por_categoria:
            por_categoria[cat] = []
        por_categoria[cat].append(item)

    # ── Coleções (do theme.json) ──
    colecoes = theme.get("colecoes", [])
    colecoes_html = ""
    for col in colecoes:
        href = _safe_href(col.get("url", ""))
        nome_c = _safe_text(col.get("nome", ""))
        colecoes_html += f"""
        <a href="{href}" target="_blank" rel="noopener noreferrer" class="link-btn">
            <span class="link-icon">🛍️</span>
            <span class="link-text">{nome_c}</span>
            <span class="link-arrow">→</span>
        </a>"""

    # ── Últimos produtos como cards ──
    cards_html = ""
    for item in recentes[:12]:
        badge = f"<span class='badge'>🆕 {item['dias']}d atrás</span>" if item['dias'] <= 3 else ""
        if item["midia"]:
            mu = _safe_css_url(item["midia"])
            img_tag = f'<div class="card-img" style="background-image: url(\'{mu}\')"></div>'
        else:
            img_tag = '<div class="card-img no-img">🎁</div>'
        href_p = _safe_href(item.get("link") or "")
        nome_p = _safe_text(item.get("nome"))

        cards_html += f"""
        <a href="{href_p}" target="_blank" rel="noopener noreferrer" class="product-card">
            {img_tag}
            <div class="card-content">
                <div class="card-name">{nome_p}</div>
                {badge}
            </div>
            <div class="card-cta">Ver oferta →</div>
        </a>"""

    # ── Categorias como links ──
    cats_html = ""
    for cat, itens in por_categoria.items():
        cat_e = _safe_text(cat)
        cats_html += f"""
        <div class="category-section">
            <h3 class="cat-title">📌 {cat_e}</h3>
            <div class="cat-grid">"""
        for item in itens[:6]:
            if item["midia"]:
                mu = _safe_css_url(item["midia"])
                img_grid = f'<div class="cat-img" style="background-image: url(\'{mu}\')"></div>'
            else:
                img_grid = ""
            href_c = _safe_href(item.get("link") or "")
            nome_c = _safe_text(item.get("nome"))
            cats_html += f"""
                <a href="{href_c}" target="_blank" rel="noopener noreferrer" class="cat-card">
                    {img_grid}
                    <div class="cat-card-name">{nome_c}</div>
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

    html = build_vitrine_page_html(
        theme=theme,
        agora=agora,
        recentes=recentes,
        colecoes_html=colecoes_html,
        cards_html=cards_html,
        cats_html=cats_html,
        titulo=titulo,
        subtitulo=subtitulo,
        banner_class=banner_class,
    )

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
