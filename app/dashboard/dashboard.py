import streamlit as st
import sqlite3
import os
import sys
import subprocess
import json
import datetime
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.core.database import get_connection
from app.core.shopee_api import get_affiliate_link
from app.core.logger import log_event
from app.core.telegram_logs import send_admin_log

# ─────────────────────────────────────────────
#  CONFIGURAÇÃO DA PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="SIAA 2026 · Painel de Comando",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
log_dir = os.path.join(proj_root, "logs")
os.makedirs(log_dir, exist_ok=True)

# ─────────────────────────────────────────────
#  CUSTOM CSS — Dark Mode Premium
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
  .stApp { background: linear-gradient(135deg, #0D0F14 0%, #111520 50%, #0D0F14 100%); color: #E8EAF0; }
  section[data-testid="stSidebar"] { background: linear-gradient(180deg, #12151F 0%, #0D0F17 100%) !important; border-right: 1px solid rgba(255,107,53,0.15) !important; }
  .stTabs [data-baseweb="tab-list"] { background: rgba(255,255,255,0.04); border-radius: 12px; padding: 4px; gap: 4px; border: 1px solid rgba(255,255,255,0.06); }
  .stTabs [data-baseweb="tab"] { border-radius: 8px; color: #8B90A0 !important; font-weight: 500; font-size: 0.85rem; padding: 8px 16px; transition: all 0.2s ease; }
  .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #FF6B35, #FF4500) !important; color: white !important; box-shadow: 0 4px 15px rgba(255,107,53,0.35); }
  .streamlit-expanderHeader { background: rgba(255,255,255,0.04) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 12px !important; color: #E8EAF0 !important; font-weight: 600 !important; }
  .streamlit-expanderContent { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.06) !important; border-radius: 0 0 12px 12px !important; border-top: none !important; }
  .stButton > button[kind="primary"] { background: linear-gradient(135deg, #FF6B35 0%, #FF4500 100%) !important; border: none !important; border-radius: 10px !important; color: white !important; font-weight: 600 !important; padding: 10px 24px !important; box-shadow: 0 4px 20px rgba(255,107,53,0.35) !important; transition: all 0.2s ease !important; }
  .stButton > button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(255,107,53,0.5) !important; }
  .stButton > button { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #E8EAF0 !important; font-weight: 500 !important; transition: all 0.2s ease !important; }
  .stButton > button:hover { background: rgba(255,107,53,0.15) !important; border-color: rgba(255,107,53,0.4) !important; color: #FF6B35 !important; }
  [data-testid="stMetric"] { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 20px; transition: all 0.2s ease; }
  [data-testid="stMetric"]:hover { border-color: rgba(255,107,53,0.3); box-shadow: 0 0 20px rgba(255,107,53,0.1); }
  [data-testid="stMetricLabel"] { color: #8B90A0 !important; font-size: 0.8rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
  [data-testid="stMetricValue"] { color: #FF6B35 !important; font-size: 2rem !important; font-weight: 800 !important; }
  .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > div { background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; color: #E8EAF0 !important; }
  .stAlert { border-radius: 12px !important; border-width: 1px !important; }
  hr { border-color: rgba(255,255,255,0.07) !important; }
  [data-testid="stForm"] { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 16px !important; padding: 20px !important; }
  .stDownloadButton > button { background: rgba(255,107,53,0.12) !important; border: 1px solid rgba(255,107,53,0.35) !important; border-radius: 10px !important; color: #FF6B35 !important; font-weight: 600 !important; }
  .kanban-card { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 14px 16px; margin-bottom: 10px; transition: all 0.2s ease; }
  .kanban-card:hover { border-color: rgba(255,107,53,0.3); box-shadow: 0 0 16px rgba(255,107,53,0.1); }
  .step-active { background: linear-gradient(135deg,#FF6B35,#FF4500); color:#fff; border-radius:8px; padding:6px 14px; font-weight:700; font-size:0.8rem; }
  .step-done { background: rgba(34,197,94,0.15); color:#22C55E; border-radius:8px; padding:6px 14px; font-weight:600; font-size:0.8rem; }
  .step-todo { background: rgba(255,255,255,0.05); color:#8B90A0; border-radius:8px; padding:6px 14px; font-weight:500; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style="background:linear-gradient(135deg,rgba(255,107,53,0.12) 0%,rgba(255,69,0,0.06) 100%);border:1px solid rgba(255,107,53,0.2);border-radius:20px;padding:28px 36px;margin-bottom:28px;display:flex;align-items:center;gap:16px;">
  <div style="font-size:3rem;line-height:1;">🔥</div>
  <div>
    <h1 style="margin:0;font-size:1.9rem;font-weight:800;color:#FFFFFF;letter-spacing:-0.02em;">SIAA <span style="color:#FF6B35;">2026</span></h1>
    <p style="margin:0;color:#8B90A0;font-size:0.9rem;margin-top:4px;">Sistema Inteligente de Automação de Afiliados · Painel de Comando</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  MÉTRICAS DO TOPO
# ─────────────────────────────────────────────
conn_m = get_connection()
cm = conn_m.cursor()
cm.execute("SELECT COUNT(*) FROM achados WHERE status = 'PENDING'")
total_pendentes = cm.fetchone()[0]
cm.execute("SELECT COUNT(*) FROM produtos WHERE estoque_ok = 1")
total_ativos = cm.fetchone()[0]
cm.execute("SELECT COUNT(*) FROM achados WHERE status = 'APPROVED'")
total_aprovados = cm.fetchone()[0]
cm.execute("SELECT COUNT(*) FROM achados WHERE status = 'REJECTED'")
total_rejeitados = cm.fetchone()[0]
conn_m.close()

m1, m2, m3, m4 = st.columns(4)
m1.metric("⏳ Aguardando Triagem", total_pendentes)
m2.metric("✅ Ativos na Vitrine", total_ativos)
m3.metric("📦 Aprovados (Total)", total_aprovados)
m4.metric("🗑️ Descartados", total_rejeitados)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPER: Geração de Copies com Gemini
# ─────────────────────────────────────────────
def generate_copies_por_rede(msg: str, rede: str = "todas") -> dict:
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
Você é especialista em marketing de afiliados Shopee no Brasil.
Com base nesta oferta: {msg[:500]}

Gere copies VIRAIS em JSON com as chaves:
- instagram_reels: legenda para Reels com emojis e até 5 hashtags (máx 150 chars)
- tiktok: legenda curta e agressiva para TikTok (máx 100 chars)
- shopee_video: título persuasivo para Shopee Video (máx 80 chars)
- whatsapp: mensagem informal com urgência (máx 200 chars)

Retorne APENAS JSON válido.
        """
        resp = model.generate_content(prompt)
        raw = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(raw)
    except Exception:
        return {
            "instagram_reels": f"🔥 Oferta imperdível! {msg[:80]} #shopee #achados",
            "tiktok": f"Você PRECISA ver isso! 👀 {msg[:60]}",
            "shopee_video": f"Achado incrível! {msg[:50]}",
            "whatsapp": f"🚨 ACHADO DO DIA: {msg[:100]} Corre que acaba!"
        }

# ─────────────────────────────────────────────
#  ABAS PRINCIPAIS
# ─────────────────────────────────────────────
tab_studio, tab_vitrine, tab_camp, tab_cupons, tab_banco, tab_eng, tab_online = st.tabs([
    "🎬  Estúdio de Conteúdo",
    "📊  Vitrine & Logs",
    "📅  Campanhas",
    "🎟️  Cupons",
    "🗂️  Banco de Mídias",
    "💬  Engajamento",
    "🌐  Vitrine Online",
])

# ══════════════════════════════════════════════
#  ABA 1 — ESTÚDIO DE CONTEÚDO
# ══════════════════════════════════════════════
ETAPAS = ["Ideia", "Editando", "Pronto", "Agendado", "Postado"]
ETAPA_COR = {
    "Ideia":    ("#8B90A0", "rgba(255,255,255,0.05)"),
    "Editando": ("#FBBF24", "rgba(251,191,36,0.08)"),
    "Pronto":   ("#60A5FA", "rgba(96,165,250,0.08)"),
    "Agendado": ("#A78BFA", "rgba(167,139,250,0.08)"),
    "Postado":  ("#22C55E", "rgba(34,197,94,0.08)"),
}

def render_stepper(etapa_atual: str):
    idx_atual = ETAPAS.index(etapa_atual) if etapa_atual in ETAPAS else 0
    cols = st.columns(len(ETAPAS))
    for i, etapa in enumerate(ETAPAS):
        if i < idx_atual:
            css = "step-done"
            icon = "✅"
        elif i == idx_atual:
            css = "step-active"
            icon = "▶"
        else:
            css = "step-todo"
            icon = "○"
        cols[i].markdown(f"<div style='text-align:center'><span class='{css}'>{icon} {etapa}</span></div>", unsafe_allow_html=True)

def get_achados_por_status(status_fluxo: str):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT id, texto_original, midia_path, link_original, categoria,
                   status_fluxo, legenda_instagram, legenda_tiktok, legenda_shopee,
                   compliance_status, status, cover_path, link_backup_1, link_backup_2
            FROM achados WHERE status_fluxo = ? ORDER BY id DESC
        """, (status_fluxo,))
    except Exception:
        c.execute("SELECT id, texto_original, midia_path, link_original, categoria, 'Ideia', NULL, NULL, NULL, 'PENDENTE', status, NULL, NULL, NULL FROM achados WHERE status NOT IN ('REJECTED') ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def mover_etapa(achado_id: int, nova_etapa: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE achados SET status_fluxo = ? WHERE id = ?", (nova_etapa, achado_id))
    conn.commit()
    conn.close()

def salvar_legendas(achado_id: int, ig: str, tt: str, sh: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE achados SET legenda_instagram=?, legenda_tiktok=?, legenda_shopee=? WHERE id=?",
              (ig, tt, sh, achado_id))
    conn.commit()
    conn.close()

with tab_studio:
    # ── Cabeçalho ──
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(255,107,53,0.1),rgba(255,69,0,0.04));border:1px solid rgba(255,107,53,0.2);border-radius:16px;padding:20px 24px;margin-bottom:20px;">
      <h3 style="margin:0;color:#E8EAF0;font-size:1.2rem;font-weight:800;">🎬 Estúdio de Conteúdo</h3>
      <p style="margin:4px 0 0;color:#8B90A0;font-size:0.85rem;">Gerencie cada conteúdo do primeiro rascunho até a publicação final.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Visão geral do pipeline ──
    st.markdown("#### 📊 Pipeline de Conteúdo")
    pipe_cols = st.columns(len(ETAPAS))
    conn_pipe = get_connection()
    cp = conn_pipe.cursor()
    for i, etapa in enumerate(ETAPAS):
        try:
            cp.execute("SELECT COUNT(*) FROM achados WHERE status_fluxo = ?", (etapa,))
        except Exception:
            cp.execute("SELECT 0")
        qtd = cp.fetchone()[0]
        cor, bg = ETAPA_COR[etapa]
        pipe_cols[i].markdown(f"""
        <div style="background:{bg};border:1px solid {cor}40;border-radius:12px;padding:14px;text-align:center;">
          <p style="color:{cor};font-weight:800;font-size:1.5rem;margin:0;">{qtd}</p>
          <p style="color:#8B90A0;font-size:0.75rem;margin:4px 0 0;text-transform:uppercase;">{etapa}</p>
        </div>""", unsafe_allow_html=True)
    conn_pipe.close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Seção de Captura ──
    st.markdown("#### 📥 Capturar Conteúdo")
    cap_col1, cap_col2 = st.columns([1, 2])

    with cap_col1:
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:14px;padding:20px;">
          <p style="color:#FF6B35;font-weight:700;margin:0 0 8px;font-size:0.9rem;">🤖 Varredura Automática</p>
          <p style="color:#8B90A0;font-size:0.8rem;margin:0;">Dispara o crawler do Telegram nos canais configurados.</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📡 Escanear Telegram Agora", type="primary", use_container_width=True, key="btn_scan_tg"):
            try:
                open(os.path.join(proj_root, ".trigger_scrape"), "w").close()
                st.success("✅ Sinal enviado! O crawler inicia em até 5s.")
            except Exception as e:
                st.error(f"Erro: {e}")

    with cap_col2:
        with st.expander("➕ Adicionar Conteúdo Manualmente", expanded=False):
            with st.form("form_add_manual", clear_on_submit=True):
                st.markdown("##### 📦 Dados do Produto")
                c_l, c_n = st.columns(2)
                link_m = c_l.text_input("🔗 Link (Shopee):", placeholder="https://shope.ee/…")
                nome_m = c_n.text_input("📦 Nome curto:", placeholder="Ex: Fone JBL Tune 510BT")
                desc_m = st.text_area("📝 Legenda / Descrição:", placeholder="Texto base para as copies…", height=80)

                c_cat, c_tipo = st.columns(2)
                cat_m = c_cat.selectbox("Categoria:", ["Geral","Tecnologia","Casa","Moda","Beleza","Pet","Outros"], key="cat_m_sel")
                tipo_m = c_tipo.selectbox("Tipo:", ["PRODUTO","COLECAO","CUPOM"], key="tipo_m_sel")

                c_url, c_up = st.columns(2)
                url_img_m = c_url.text_input("🖼️ URL da imagem:", placeholder="https://…")
                upload_m = c_up.file_uploader("Ou upload:", type=["jpg","jpeg","png","webp","mp4","mov"], key="up_m")

                c_b1, c_b2 = st.columns(2)
                b1_m = c_b1.text_input("🔄 Link Reserva 1:", key="b1_m")
                b2_m = c_b2.text_input("🔄 Link Reserva 2:", key="b2_m")

                sub_m = st.form_submit_button("✅ Adicionar à Fila", type="primary", use_container_width=True)
                if sub_m:
                    if not link_m or not nome_m:
                        st.error("Link e Nome são obrigatórios.")
                    else:
                        import requests as req_lib
                        midia_salva = ""
                        media_dir = os.path.join(proj_root, "media")
                        os.makedirs(media_dir, exist_ok=True)
                        if upload_m:
                            ext = upload_m.name.split('.')[-1]
                            fp = os.path.join(media_dir, f"manual_{uuid.uuid4().hex[:8]}.{ext}")
                            with open(fp, "wb") as f: f.write(upload_m.read())
                            midia_salva = fp
                        elif url_img_m:
                            try:
                                r = req_lib.get(url_img_m, timeout=10)
                                if r.status_code == 200:
                                    ext = url_img_m.split('.')[-1].split('?')[0]
                                    ext = ext if ext in ['jpg','jpeg','png','webp','mp4'] else 'jpg'
                                    fp = os.path.join(media_dir, f"manual_{uuid.uuid4().hex[:8]}.{ext}")
                                    with open(fp, "wb") as f: f.write(r.content)
                                    midia_salva = fp
                            except: pass
                        legenda = desc_m if desc_m else f"{nome_m}\n\n🛍️ Link: {link_m}"
                        conn5 = get_connection(); c5 = conn5.cursor()
                        try:
                            c5.execute("""INSERT INTO achados
                                (texto_original,midia_path,link_original,link_backup_1,link_backup_2,
                                 status,status_fluxo,categoria,tipo_link,compliance_status)
                                VALUES(?,?,?,?,?,'PENDING','Ideia',?,?,'SEGURO')""",
                                (legenda, midia_salva, link_m, b1_m or None, b2_m or None, cat_m, tipo_m))
                        except Exception:
                            c5.execute("INSERT INTO achados (texto_original,midia_path,link_original,status,status_fluxo) VALUES(?,?,?,'PENDING','Ideia')",
                                       (legenda, midia_salva, link_m))
                        conn5.commit()
                        novo_id = c5.lastrowid; conn5.close()
                        send_admin_log(f"➕ Produto manual #{novo_id} — {nome_m} adicionado ao Estúdio.")
                        st.success(f"🎉 Produto #{novo_id} adicionado! Veja no Kanban abaixo.")
                        st.rerun()

    st.divider()

    # ── Kanban ──
    st.markdown("#### 🗂️ Kanban de Conteúdo")
    etapa_filtro = st.selectbox("Filtrar por etapa:", ["Todas"] + ETAPAS, key="kanban_filtro")

    etapas_exibir = ETAPAS if etapa_filtro == "Todas" else [etapa_filtro]

    for etapa in etapas_exibir:
        cor, bg = ETAPA_COR[etapa]
        cards = get_achados_por_status(etapa)
        st.markdown(f"""
        <div style="background:{bg};border-left:3px solid {cor};border-radius:10px;padding:10px 16px;margin:16px 0 8px;">
          <b style="color:{cor};">● {etapa}</b>
          <span style="color:#8B90A0;font-size:0.8rem;margin-left:8px;">{len(cards)} conteúdo(s)</span>
        </div>""", unsafe_allow_html=True)

        if not cards:
            st.markdown("<p style='color:#8B90A0;font-size:0.82rem;padding:8px 16px;'>Nenhum conteúdo nesta etapa.</p>", unsafe_allow_html=True)
            continue

        for row in cards:
            (a_id, texto, midia, link, cat, s_fluxo,
             leg_ig, leg_tt, leg_sh, comp_st, status, cover, b1, b2) = row

            titulo_card = (texto[:60] + "…") if texto and len(texto) > 60 else (texto or f"Conteúdo #{a_id}")
            with st.expander(f"#{a_id} · {cat or 'Geral'} · {titulo_card}", expanded=False):

                # Stepper visual do card
                render_stepper(s_fluxo or "Ideia")
                st.markdown("<br>", unsafe_allow_html=True)

                col_md, col_ed = st.columns([1, 2])

                # Mídia
                with col_md:
                    if midia and os.path.exists(midia):
                        if midia.endswith((".mp4",".mov")):
                            st.video(midia)
                        else:
                            st.image(midia, use_container_width=True)
                        with open(midia, "rb") as f_dl:
                            ext_dl = "mp4" if midia.endswith((".mp4",".mov")) else "jpg"
                            st.download_button("📱 Baixar", data=f_dl,
                                file_name=f"siaa_{a_id}.{ext_dl}", key=f"dl_{a_id}")
                    else:
                        st.markdown("""<div style='padding:30px;text-align:center;background:rgba(255,255,255,0.03);border-radius:12px;border:1px dashed rgba(255,255,255,0.1)'>
                          <p style='color:#8B90A0;margin:0;'>📷 Sem mídia</p></div>""", unsafe_allow_html=True)

                    if link and st.button("🔍 Extrair Mídia HD", key=f"scrape_{a_id}"):
                        with st.spinner("Buscando mídia…"):
                            try:
                                from app.mineracao.shopee_scraper import scrape_shopee_media
                                nm = scrape_shopee_media(link)
                                if nm:
                                    conn_s = get_connection(); cs = conn_s.cursor()
                                    cs.execute("UPDATE achados SET midia_path=? WHERE id=?", (nm, a_id))
                                    conn_s.commit(); conn_s.close()
                                    st.success("Mídia extraída!"); st.rerun()
                                else: st.warning("Não encontrada.")
                            except Exception as e: st.error(str(e))

                    if midia and not midia.endswith((".mp4",".mov")) and os.path.exists(midia):
                        if st.button("🎨 Gerar Arte Pillow", key=f"arte2_{a_id}"):
                            with st.spinner("Gerando arte…"):
                                from app.publisher.card_generator import generate_feed_card
                                arte = generate_feed_card(midia)
                                if arte:
                                    conn_s = get_connection(); cs = conn_s.cursor()
                                    cs.execute("UPDATE achados SET midia_path=? WHERE id=?", (arte, a_id))
                                    conn_s.commit(); conn_s.close()
                                    st.success("Arte aplicada!"); st.rerun()

                    if midia and midia.endswith((".mp4",".mov")) and os.path.exists(midia):
                        if st.button("🛡️ Anti-Shadowban", key=f"anti_{a_id}"):
                            with st.spinner("Processando vídeo único…"):
                                try:
                                    from app.mineracao.editor_ia import apply_shadowban_avoidance
                                    out = midia.replace(".mp4","_unico.mp4").replace(".mov","_unico.mp4")
                                    resultado = apply_shadowban_avoidance(midia, out)
                                    if resultado:
                                        conn_s = get_connection(); cs = conn_s.cursor()
                                        cs.execute("UPDATE achados SET midia_path=? WHERE id=?", (resultado, a_id))
                                        conn_s.commit(); conn_s.close()
                                        st.success("Vídeo único gerado!"); st.rerun()
                                except Exception as e: st.error(str(e))

                # Editor por rede social
                with col_ed:
                    st.markdown("**📝 Texto Original:**")
                    st.code((texto or "")[:400], language="markdown")
                    if link:
                        st.markdown(f"**🔗 Link:** `{link[:70]}…`" if len(link or "") > 70 else f"**🔗 Link:** `{link}`")

                    if st.button("✨ Gerar Copies com IA", key=f"gerar_copy_{a_id}", type="primary"):
                        with st.spinner("Consultando Gemini…"):
                            copies = generate_copies_por_rede(texto or nome_m if 'nome_m' in dir() else texto or "")
                            st.session_state[f"copies_{a_id}"] = copies

                    copies_salvas = st.session_state.get(f"copies_{a_id}", {})

                    st.markdown("**✍️ Editor por Rede Social:**")
                    t_ig, t_tt, t_sh, t_wa = st.tabs(["📸 Instagram", "🎵 TikTok", "🛒 Shopee Video", "💬 WhatsApp"])

                    with t_ig:
                        leg_ig_edit = st.text_area("Legenda Instagram (Reels/Feed):", value=leg_ig or copies_salvas.get("instagram_reels",""), height=100, key=f"ig_{a_id}")
                        if leg_ig_edit and st.button("💾 Salvar IG", key=f"sig_{a_id}"):
                            salvar_legendas(a_id, leg_ig_edit, leg_tt or "", leg_sh or "")
                            st.success("Salvo!")

                    with t_tt:
                        leg_tt_edit = st.text_area("Legenda TikTok:", value=leg_tt or copies_salvas.get("tiktok",""), height=80, key=f"tt_{a_id}")
                        if leg_tt_edit and st.button("💾 Salvar TikTok", key=f"stt_{a_id}"):
                            salvar_legendas(a_id, leg_ig or "", leg_tt_edit, leg_sh or "")
                            st.success("Salvo!")

                    with t_sh:
                        leg_sh_edit = st.text_area("Título Shopee Video:", value=leg_sh or copies_salvas.get("shopee_video",""), height=80, key=f"sh_{a_id}")
                        if leg_sh_edit and st.button("💾 Salvar Shopee", key=f"ssh_{a_id}"):
                            salvar_legendas(a_id, leg_ig or "", leg_tt or "", leg_sh_edit)
                            st.success("Salvo!")

                    with t_wa:
                        wa_text = copies_salvas.get("whatsapp","")
                        if wa_text:
                            st.info(wa_text)
                            st.caption("WhatsApp é gerado automaticamente pelo bot. Copie e use nos grupos.")

                    st.divider()

                    # Ações de fluxo
                    idx_etapa = ETAPAS.index(s_fluxo) if s_fluxo in ETAPAS else 0
                    c_mover, c_aprovar, c_rejeitar = st.columns(3)

                    with c_mover:
                        opts_fwd = ETAPAS[idx_etapa+1:] if idx_etapa < len(ETAPAS)-1 else []
                        opts_bck = ETAPAS[:idx_etapa] if idx_etapa > 0 else []
                        if opts_fwd and st.button(f"→ Mover p/ {opts_fwd[0]}", key=f"fwd_{a_id}", type="primary"):
                            mover_etapa(a_id, opts_fwd[0])
                            st.rerun()
                        if opts_bck and st.button(f"← Voltar p/ {opts_bck[-1]}", key=f"bck_{a_id}"):
                            mover_etapa(a_id, opts_bck[-1])
                            st.rerun()

                    with c_aprovar:
                        if status not in ("APPROVED","POSTED","POSTED_SHOPEE") and st.button("✅ Aprovar & Publicar", key=f"apr_{a_id}", type="primary"):
                            conn_ap = get_connection(); cap = conn_ap.cursor()
                            link_af = get_affiliate_link(link) if link else f"https://shope.ee/default_{a_id}"
                            nome_ap = f"Oferta #{a_id}"
                            cap.execute("UPDATE achados SET status='APPROVED', status_fluxo='Pronto' WHERE id=?", (a_id,))
                            cap.execute("INSERT OR IGNORE INTO produtos (achado_id,link_afiliado,nome_produto,categoria) VALUES(?,?,?,?)",
                                        (a_id, link_af, nome_ap, cat or "Geral"))
                            conn_ap.commit(); conn_ap.close()
                            send_admin_log(f"✅ #{a_id} aprovado via Estúdio!")
                            st.success("Aprovado!"); st.rerun()

                    with c_rejeitar:
                        if st.button("🗑️ Descartar", key=f"rej_{a_id}"):
                            conn_rj = get_connection(); crj = conn_rj.cursor()
                            crj.execute("UPDATE achados SET status='REJECTED', status_fluxo='Postado' WHERE id=?", (a_id,))
                            conn_rj.commit(); conn_rj.close()
                            st.warning("Descartado."); st.rerun()

