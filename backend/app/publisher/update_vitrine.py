import os
import sys
import datetime
import html
import subprocess
import json
from urllib.parse import urlparse

# Força UTF-8 no terminal Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Root path resolution
_proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)

from app.core.firebase_sync import firebase_sync
from app.publisher.vitrine_html import build_vitrine_page_html

THEME_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../theme.json'))

def _safe_href(url: str) -> str:
    if not url: return "#"
    p = urlparse(url.strip())
    if p.scheme not in ("http", "https"): return "#"
    return html.escape(url, quote=True)

def _safe_text(s: object) -> str:
    return html.escape("" if s is None else str(s))

def _safe_css_url(path: str) -> str:
    if not path: return ""
    p = path.replace("\\", "/").replace("'", "").replace('"', "").replace("(", "").replace(")", "")
    return html.escape(p, quote=False)

def load_theme():
    if os.path.exists(THEME_PATH):
        with open(THEME_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "logotipo": "SIAA Vitrine VIP",
        "logo_img": "https://api.dicebear.com/7.x/bottts/svg?seed=SIAA",
        "cores": {"primaria": "#FF6B35"},
        "colecoes": [
            {"nome": "Grupo VIP WhatsApp", "url": "#"},
            {"nome": "Melhores da Semana", "url": "#"}
        ],
        "modo_campanha": {"ativo": False}
    }

def generate_html_vitrine():
    theme = load_theme()
    agora = datetime.datetime.now()

    print("[VITRINE] Sincronizando com Firestore...")
    # Busca produtos aprovados (status == 'approved' ou vindo da coleção 'vitrine')
    # Para simplificar, vamos buscar da coleção 'mining' onde status == 'approved'
    # Ou se houver uma coleção 'vitrine', use ela.
    try:
        docs = firebase_sync.db.collection("mining").where("status", "==", "approved").order_by("timestamp", direction="DESCENDING").limit(30).get()
        approved_items = [doc.to_dict() for doc in docs]
    except Exception as e:
        print(f"[VITRINE] Erro ao buscar Firestore: {e}. Usando fallback vazio.")
        approved_items = []

    recentes = []
    por_categoria = {}
    
    for item in approved_items:
        nome = item.get("title", "Produto sem nome")
        link = item.get("rawLink", "#")
        categoria = item.get("category", "Geral")
        midia = item.get("image", "")
        
        # Simula dias atrás
        dias = 0
        
        entry = {"nome": nome, "link": link, "dias": dias, "midia": midia}
        recentes.append(entry)
        
        if categoria not in por_categoria:
            por_categoria[categoria] = []
        por_categoria[categoria].append(entry)

    # ── Coleções ──
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

    # ── Cards Recentes ──
    cards_html = ""
    for item in recentes[:12]:
        mu = _safe_css_url(item["midia"])
        img_tag = f'<div class="card-img" style="background-image: url(\'{mu}\')"></div>' if mu else '<div class="card-img no-img">🎁</div>'
        href_p = _safe_href(item.get("link") or "")
        nome_p = _safe_text(item.get("nome"))

        cards_html += f"""
        <a href="{href_p}" target="_blank" rel="noopener noreferrer" class="product-card">
            {img_tag}
            <div class="card-content">
                <div class="card-name">{nome_p}</div>
                <span class='badge'>🆕 Oferta do Dia</span>
            </div>
            <div class="card-cta">Ver oferta →</div>
        </a>"""

    # ── Categorias ──
    cats_html = ""
    for cat, itens in por_categoria.items():
        cat_e = _safe_text(cat)
        cats_html += f"""
        <div class="category-section">
            <h3 class="cat-title">📌 {cat_e}</h3>
            <div class="cat-grid">"""
        for item in itens[:6]:
            mu = _safe_css_url(item["midia"])
            img_grid = f'<div class="cat-img" style="background-image: url(\'{mu}\')"></div>' if mu else ""
            href_c = _safe_href(item.get("link") or "")
            nome_c = _safe_text(item.get("nome"))
            cats_html += f"""
                <a href="{href_c}" target="_blank" rel="noopener noreferrer" class="cat-card">
                    {img_grid}
                    <div class="cat-card-name">{nome_c}</div>
                    <div class="cat-card-cta">🔥 Comprar</div>
                </a>"""
        cats_html += "</div></div>"

    modo_c = theme.get("modo_campanha", {})
    is_campanha = modo_c.get("ativo", False)
    titulo = modo_c.get("titulo", f"✨ {theme.get('logotipo', 'Vitrine VIP')}") if is_campanha else f"✨ {theme.get('logotipo', 'Vitrine VIP')}"
    subtitulo = modo_c.get("descricao", "As melhores ofertas selecionadas") if is_campanha else "As melhores ofertas selecionadas 🛒"
    banner_class = "is-campanha" if is_campanha else ""

    final_html = build_vitrine_page_html(
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

    index_path = os.path.join(_proj_root, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    print(f"[VITRINE] index.html atualizado com {len(recentes)} produtos do Firebase.")
    git_push_vitrine(_proj_root)

def git_push_vitrine(work_dir):
    try:
        orig = os.getcwd()
        os.chdir(work_dir)
        subprocess.run(["git", "add", "index.html"], check=False)
        subprocess.run(["git", "commit", "-m", "SIAA Auto-update Vitrine"], check=False)
        subprocess.run(["git", "push"], check=False)
        os.chdir(orig)
        print("[VITRINE] Push para GitHub realizado!")
    except Exception as e:
        print(f"[VITRINE] Git erro: {e}")

if __name__ == "__main__":
    generate_html_vitrine()
