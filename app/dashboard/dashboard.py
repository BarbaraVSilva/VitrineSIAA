import streamlit as st
import sqlite3
import os
import sys
import subprocess

# Streamlit corre este ficheiro como script; sem `pip install -e .` a raiz do projeto precisa estar no path.
_proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _proj_root not in sys.path:
    sys.path.insert(0, _proj_root)
import json
import datetime
import uuid

import pandas as pd

from app.dashboard.streamlit_theme import DASHBOARD_CUSTOM_CSS
from app.dashboard.studio_helpers import (
    ETAPA_COR,
    ETAPAS,
    generate_copies_por_rede,
    get_achados_por_status,
    mover_etapa,
    render_stepper,
    salvar_legendas,
)
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
st.markdown(DASHBOARD_CUSTOM_CSS, unsafe_allow_html=True)

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
  <div style="margin-left:auto;">
    <a href="http://localhost:8088/pro" target="_blank" style="text-decoration:none;">
      <div style="background:rgba(255,107,53,0.15);border:1px solid #FF6B35;padding:10px 20px;border-radius:12px;color:#FF6B35;font-weight:700;font-size:0.9rem;">🚀 ABRIR MASTER HUB</div>
    </a>
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
#  ABAS PRINCIPAIS
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
#  MENU LATERAL PRINCIPAL
# ─────────────────────────────────────────────
st.sidebar.markdown('## 🧭 Navegação SIAA')
MENU_OPTIONS = [
    '🏡 Início',
    '🎬 Estúdio de Conteúdo',
    '🗂️ Banco de Mídias',
    '💬 Automações & Engajamento',
    '⚙️ Configurações Extra'
]
menu_selecionado = st.sidebar.radio('Navegue:', MENU_OPTIONS)
st.sidebar.markdown('---')
st.sidebar.caption('SIAA 2026 Core v1.5')


# ══════════════════════════════════════════════
#  ABA 1 — ESTÚDIO DE CONTEÚDO
# ══════════════════════════════════════════════
if menu_selecionado == '🎬 Estúdio de Conteúdo':
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

    # ── FERRAMENTAS & CAPTURA (Toolbox) ──
    with st.expander("🛠️ Ferramentas Rápidas & Captura", expanded=False):
        t1, t2, t3 = st.columns(3)
        
        with t1:
            st.markdown("**🪄 Organização IA**")
            if st.button("🚀 Rodar Agrupador", use_container_width=True, help="Gemini cria carrosséis automáticos"):
                from app.mineracao.grouper import group_achados_with_ai
                if group_achados_with_ai(): st.success("Grupos Atualizados!"); st.rerun()
            
            # Bulk Approval
            conn_b = get_connection(); cb = conn_b.cursor()
            cb.execute("SELECT DISTINCT tema_grupo, grupo_id FROM achados WHERE grupo_id IS NOT NULL AND status = 'PENDING'")
            grupos_pendentes = cb.fetchall()
            conn_b.close()
            if grupos_pendentes:
                st.info(f"{len(grupos_pendentes)} grupos aguardando.")
                if st.button("✅ Aprovar Todos os Grupos", key="bulk_all"):
                    conn_ap = get_connection(); cap = conn_ap.cursor()
                    cap.execute("UPDATE achados SET status='APPROVED', status_fluxo='Pronto' WHERE grupo_id IS NOT NULL AND status='PENDING'")
                    conn_ap.commit(); conn_ap.close()
                    st.success("Tudo Aprovado!"); st.rerun()

        with t2:
            st.markdown("**📡 Scanner Telegram**")
            if st.button("📡 Buscar Últimas 24h", type="primary", use_container_width=True):
                open(os.path.join(proj_root, ".trigger_scrape_24h"), "w").close()
                st.success("Sinal enviado!")
            
            st.markdown("**🗑️ Limpeza**")
            if st.button("🚨 Ocultar Pendentes", use_container_width=True):
                conn_cl = get_connection(); c_cl = conn_cl.cursor()
                c_cl.execute("UPDATE achados SET status='REJECTED', status_fluxo='Postado' WHERE status='PENDING'")
                conn_cl.commit(); conn_cl.close()
                st.success("Fila limpa!"); st.rerun()

        with t3:
            st.markdown("**➕ Adição Manual**")
            if st.button("📦 Abrir Formulário", use_container_width=True):
                st.session_state["show_manual_form"] = not st.session_state.get("show_manual_form", False)

        if st.session_state.get("show_manual_form", False):
            st.divider()
            with st.form("form_add_manual_new", clear_on_submit=True):
                st.markdown("##### 📦 Dados do Produto")
                cl1, cl2 = st.columns(2)
                l_m = cl1.text_input("🔗 Link (Shopee):")
                n_m = cl2.text_input("📦 Nome curto:")
                d_m = st.text_area("📝 Legenda:", height=80)
                sub_new = st.form_submit_button("✅ Adicionar à Fila", type="primary", use_container_width=True)
                if sub_new:
                    if l_m and n_m:
                        leg = d_m if d_m else f"{n_m}\n\n🛍️ Link: {l_m}"
                        cn = get_connection(); cur = cn.cursor()
                        cur.execute("INSERT INTO achados (texto_original,midia_path,link_original,status,status_fluxo) VALUES(?,NULL,?,'PENDING','Ideia')", (leg, l_m))
                        cn.commit(); cn.close()
                        st.success("Adicionado!"); st.rerun()
                    else: st.error("Link e Nome obrigatórios.")
    st.markdown("#### 🚀 Conteúdo Pendente (Triagem)")

    st.divider()

    # ── Kanban em Abas (Melhor Redimensionamento) ──
    st.markdown("#### 🗂️ Fluxo do Estúdio")
    
    # Substituindo st.columns por st.tabs para melhor uso do espaço
    tab_etapas = st.tabs([f"{e} ({len(get_achados_por_status(e))})" for e in ETAPAS])
    
    for i, etapa in enumerate(ETAPAS):
        cor, bg = ETAPA_COR[etapa]
        cards = get_achados_por_status(etapa)
        
        with tab_etapas[i]:
            st.markdown(f"""
            <div style="background:{bg};border-bottom:2px solid {cor};border-radius:10px;padding:12px;text-align:center;margin-bottom:20px;">
              <b style="color:{cor};font-size:1.1rem;">{etapa.upper()}</b>
            </div>""", unsafe_allow_html=True)
            
            if not cards:
                st.markdown(f"<p style='color:#8B90A0;font-size:0.85rem;text-align:center;opacity:0.5;padding:30px 0;'>🏜️ Nenhum item em {etapa}</p>", unsafe_allow_html=True)
                continue

            for row in cards:
                (a_id, texto, midia, link, cat, s_fluxo,
                 leg_ig, leg_tt, leg_sh, comp_st, status, cover, b1, b2, g_id, tema_g) = row
                
                tag_g = f"<div style='color:#A78BFA;font-size:0.65rem;font-weight:700;margin-top:4px;'>📦 {tema_g[:15]}…</div>" if tema_g else ""
                titulo_compacto = (texto[:30] + "…") if texto and len(texto) > 30 else (texto or f"#{a_id}")
                with st.expander(f"#{a_id} · {titulo_compacto}", expanded=False):
                    if tag_g: st.markdown(tag_g, unsafe_allow_html=True)

                # Stepper visual do card
                render_stepper(s_fluxo or "Ideia")
                st.markdown("<br>", unsafe_allow_html=True)

                col_md, col_ed = st.columns([1, 2])

                # Mídia
                with col_md:
                    if midia and os.path.exists(midia):
                        if midia.lower().endswith((".mp4",".mov")):
                            st.video(midia)
                        else:
                            try:
                                st.image(midia, use_container_width=True)
                            except Exception as e:
                                st.error(f"⚠️ Mídia corrompida ou inválida: {os.path.basename(midia)}")
                                st.caption("Tente Extrair Mídia HD para substituir o arquivo.")
                        with open(midia, "rb") as f_dl:
                            ext_dl = "mp4" if midia.lower().endswith((".mp4",".mov")) else "jpg"
                            st.download_button("📱 Baixar", data=f_dl,
                                file_name=f"siaa_{a_id}.{ext_dl}", key=f"dl_{a_id}")
                    else:
                        st.markdown("""<div style='padding:30px;text-align:center;background:rgba(255,255,255,0.03);border-radius:12px;border:1px dashed rgba(255,255,255,0.1)'>
                          <p style='color:#8B90A0;margin:0;'>📷 Sem mídia</p></div>""", unsafe_allow_html=True)

                    if link and st.button("🔍 Extrair Dados do Anúncio (Shopee)", key=f"scrape_{a_id}"):
                        with st.spinner("Visitando a página oficial pra buscar título, preço e mídia…"):
                            try:
                                from app.mineracao.shopee_scraper import scrape_shopee_data
                                # Se já tem mídia e só quer o texto, passa extract_media=False? 
                                # O usuário deixou em aberto, então vamos tentar extrair sempre pra garantir a melhor qualidade.
                                scrap_meta = scrape_shopee_data(link, extract_media=True)
                                
                                conn_s = get_connection(); cs = conn_s.cursor()
                                msg_att = []
                                
                                if scrap_meta["titulo"]:
                                    novo_texto = f"{scrap_meta['titulo']}\n\nPreço: {scrap_meta['preco']}\n\nLink: {link}"
                                    cs.execute("UPDATE achados SET texto_original=? WHERE id=?", (novo_texto, a_id))
                                    msg_att.append("Textos")
                                    
                                if scrap_meta["path"]:
                                    cs.execute("UPDATE achados SET midia_path=? WHERE id=?", (scrap_meta["path"], a_id))
                                    msg_att.append("Mídia")
                                    
                                conn_s.commit(); conn_s.close()
                                if msg_att:
                                    st.success(f"✅ Extraídos com sucesso: {', '.join(msg_att)}!"); st.rerun()
                                else: 
                                    st.warning("Não foi possível extrair novos dados (Anúncio excluido?).")
                            except Exception as e: st.error(str(e))

                    if midia and not midia.lower().endswith((".mp4",".mov")) and os.path.exists(midia):
                        c_p1, c_p2 = st.columns(2)
                        st_brand = c_p1.selectbox("Estilo:", ["standard", "minimalist_glass"], key=f"st_br_{a_id}")
                        if c_p2.button("🎨 Gerar Arte", key=f"arte2_{a_id}", use_container_width=True):
                            with st.spinner("Gerando..."):
                                from app.mineracao.branding import apply_branding_to_image
                                arte = apply_branding_to_image(midia, style=st_brand)
                                if arte:
                                    conn_s = get_connection(); cs = conn_s.cursor()
                                    cs.execute("UPDATE achados SET midia_path=? WHERE id=?", (arte, a_id))
                                    conn_s.commit(); conn_s.close()
                                    st.success("Aplicado!"); st.rerun()

                    if midia and midia.lower().endswith((".mp4",".mov")) and os.path.exists(midia):
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
                    st.markdown("### 📝 Original & Metadados")
                    with st.container(border=True):
                        st.caption("Texto Base:")
                        st.markdown(f"*{ (texto or '')[:400] }*")
                        if link:
                            st.markdown("---")
                            st.markdown(f"**🔗 Link Shopee:** `{link[:70]}…`" if len(link or "") > 70 else f"**🔗 Link Shopee:** `{link}`")

                    if st.button("✨ Gerar Copies com IA", key=f"gerar_copy_{a_id}", type="primary", use_container_width=True):
                        with st.spinner("Consultando Gemini…"):
                            copies = generate_copies_por_rede(texto or nome_m if 'nome_m' in dir() else texto or "")
                            st.session_state[f"copies_{a_id}"] = copies
                            st.session_state[f"ig_{a_id}"] = copies.get("instagram_reels","")
                            st.session_state[f"tt_{a_id}"] = copies.get("tiktok","")
                            st.session_state[f"sh_{a_id}"] = copies.get("shopee_video","")
                            st.rerun()

                    copies_salvas = st.session_state.get(f"copies_{a_id}", {})

                    st.markdown("### ✍️ Estúdio Formatação")
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
                            # Injeta Sub-ID Individual
                            link_af = get_affiliate_link(link, sub_id=f"studio_a{a_id}") if link else f"https://shope.ee/default_{a_id}"
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

# ══════════════════════════════════════════════
#  ABA 2 — VITRINE & LOGS
# ══════════════════════════════════════════════
if menu_selecionado == '🏡 Início':
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(96,165,250,0.1),rgba(96,165,250,0.04));border:1px solid rgba(96,165,250,0.2);border-radius:16px;padding:20px 24px;margin-bottom:20px;">
      <h3 style="margin:0;color:#E8EAF0;font-size:1.2rem;font-weight:800;">📊 Gestão de Vitrine & Logs</h3>
      <p style="margin:4px 0 0;color:#8B90A0;font-size:0.85rem;">Visualize todos os produtos ativos e monitore a saúde do sistema.</p>
    </div>
    """, unsafe_allow_html=True)

    col_v1, col_v2 = st.columns([2, 1])

    with col_v1:
        st.markdown("#### 🛍️ Produtos Ativos")
        conn_v = get_connection()
        try:
            df_prod = pd.read_sql_query("""
                SELECT id, nome_produto, categoria, link_afiliado, data_criacao, estoque_ok
                FROM produtos ORDER BY id DESC
            """, conn_v)
            if not df_prod.empty:
                st.dataframe(df_prod, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum produto na vitrine ainda.")
        except Exception:
            st.warning("Tabela 'produtos' ainda não populada.")
        conn_v.close()

    with col_v2:
        st.markdown("#### 📜 Logs do Sistema")
        if os.path.exists(log_dir):
            log_files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
            if not log_files:
                st.info("Nenhum arquivo de log encontrado.")
            else:
                selected_log = st.selectbox("Selecionar log:", log_files)
                log_path = os.path.join(log_dir, selected_log)
                with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.readlines()
                    st.text_area(f"Visualizando {selected_log}", value="".join(content[-50:]), height=400)
        else:
            st.info("Diretório de logs não encontrado.")

# ══════════════════════════════════════════════
#  ABA 3 — CAMPANHAS (THEME.JSON)
# ══════════════════════════════════════════════
if menu_selecionado == '⚙️ Configurações Extra':
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(167,139,250,0.1),rgba(167,139,250,0.04));border:1px solid rgba(167,139,250,0.2);border-radius:16px;padding:20px 24px;margin-bottom:20px;">
      <h3 style="margin:0;color:#E8EAF0;font-size:1.2rem;font-weight:800;">📅 Gestão de Campanhas & Identidade</h3>
      <p style="margin:4px 0 0;color:#8B90A0;font-size:0.85rem;">Configure eventos especiais e identidade visual da vitrine.</p>
    </div>
    """, unsafe_allow_html=True)

    theme_path = os.path.join(proj_root, "theme.json")
    theme_data = {"logotipo": "SIAA Shop", "cores": {"primaria": "#FF6B35"}, "modo_campanha": {"ativo": False, "titulo": "", "descricao": "", "dias_de_evento": []}}
    if os.path.exists(theme_path):
        with open(theme_path, "r", encoding="utf-8", errors="replace") as f: theme_data = json.load(f)

    with st.form("form_theme"):
        st.markdown("#### 🎨 Identidade Visual")
        c1, c2 = st.columns(2)
        new_logo = c1.text_input("Nome/Logotipo:", value=theme_data.get("logotipo", "SIAA Shop"))
        new_color = c2.color_picker("Cor Primária:", value=theme_data.get("cores", {}).get("primaria", "#FF6B35"))
        
        st.divider()
        st.markdown("#### 🚀 Modo Campanha (Eventos)")
        camp_active = st.toggle("Ativar Modo Campanha", value=theme_data.get("modo_campanha", {}).get("ativo", False))
        c_t, c_d = st.columns(2)
        camp_title = c_t.text_input("Título do Banner:", value=theme_data.get("modo_campanha", {}).get("titulo", ""))
        camp_desc = c_d.text_input("Subtítulo:", value=theme_data.get("modo_campanha", {}).get("descricao", ""))
        
        if st.form_submit_button("💾 Salvar Configurações", type="primary", use_container_width=True):
            theme_data["logotipo"] = new_logo
            theme_data["cores"]["primaria"] = new_color
            theme_data["modo_campanha"]["ativo"] = camp_active
            theme_data["modo_campanha"]["titulo"] = camp_title
            theme_data["modo_campanha"]["descricao"] = camp_desc
            with open(theme_path, "w", encoding="utf-8") as f:
                json.dump(theme_data, f, indent=4, ensure_ascii=False)
            st.success("✅ Configurações salvas!")
            st.rerun()

    st.markdown("#### ⌚ Agendamentos Pendentes")
    conn_c = get_connection()
    try:
        df_ag = pd.read_sql_query("""
            SELECT id, nome_produto, data_agendada, status_publicacao
            FROM produtos WHERE status_publicacao != 'POSTED' AND data_agendada IS NOT NULL
            ORDER BY data_agendada ASC
        """, conn_c)
        if not df_ag.empty:
            st.dataframe(df_ag, use_container_width=True, hide_index=True)
        else:
            st.caption("Nenhum post agendado no momento.")
    except Exception:
        st.caption("Aguardando inicialização da tabela de agendamentos.")
    conn_c.close()

# ══════════════════════════════════════════════
#  ABA 4 — CUPONS
# ══════════════════════════════════════════════
if menu_selecionado == '⚙️ Configurações Extra':
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(251,191,36,0.1),rgba(251,191,36,0.04));border:1px solid rgba(251,191,36,0.2);border-radius:16px;padding:20px 24px;margin-bottom:20px;">
      <h3 style="margin:0;color:#E8EAF0;font-size:1.2rem;font-weight:800;">🎟️ Gestão de Cupons Shopee</h3>
      <p style="margin:4px 0 0;color:#8B90A0;font-size:0.85rem;">Adicione cupons de desconto para aparecerem na sua vitrine.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🆕 Adicionar Novo Cupom"):
        with st.form("form_add_cupom"):
            c1, c2, c3 = st.columns(3)
            cod = c1.text_input("Código do Cupom:", placeholder="EX: SHOPEE20")
            val = c2.text_input("Valor/Desconto:", placeholder="R$ 20 ou 10%")
            link_c = c3.text_input("Link de Destino:", placeholder="https://shope.ee/...")
            if st.form_submit_button("✅ Salvar Cupom", type="primary", use_container_width=True):
                if cod and val:
                    conn = get_connection(); c = conn.cursor()
                    try:
                        c.execute("INSERT INTO cupons (codigo, valor, link_destino) VALUES (?,?,?)", (cod, val, link_c))
                        conn.commit(); st.success("Cupom adicionado!"); st.rerun()
                    except: st.error("Erro ao adicionar (Código já existe?)")
                    finally: conn.close()

    st.markdown("#### 🎫 Cupons Ativos")
    conn = get_connection()
    try:
        df_cp = pd.read_sql_query("SELECT id, codigo, valor, link_destino, ativo FROM cupons", conn)
        if not df_cp.empty:
            st.data_editor(df_cp, use_container_width=True, hide_index=True, key="editor_cupons")
        else:
            st.info("Nenhum cupom cadastrado.")
    except: st.caption("Tabela de cupons sendo inicializada...")
    conn.close()

# ══════════════════════════════════════════════
#  ABA 5 — BANCO DE MÍDIAS
# ══════════════════════════════════════════════
if menu_selecionado == '🗂️ Banco de Mídias':
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(59,130,246,0.04));border:1px solid rgba(59,130,246,0.2);border-radius:16px;padding:20px 24px;margin-bottom:20px;">
      <h3 style="margin:0;color:#E8EAF0;font-size:1.2rem;font-weight:800;">🗂️ Banco de Mídias 2.0</h3>
      <p style="margin:4px 0 0;color:#8B90A0;font-size:0.85rem;">Gerencie arquivos de /media e /downloads, faça upload em lote e envie para o Estúdio.</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Faxina e Upload ──
    with st.expander("🛠️ Ferramentas do Banco", expanded=False):
        c_up, c_clean = st.columns(2)
        with c_up:
            st.markdown("**⬆️ Upload em Lote**")
            up_files = st.file_uploader("Fotos ou vídeos:", type=["jpg","jpeg","png","webp","mp4","mov"], accept_multiple_files=True, key="bulk_up")
            if up_files and st.button("🚀 Iniciar Upload", type="primary"):
                media_path = os.path.join(proj_root, "media")
                for f in up_files:
                    with open(os.path.join(media_path, f.name), "wb") as out: out.write(f.read())
                st.success(f"✅ {len(up_files)} salvos!"); st.rerun()
        
        with c_clean:
            st.markdown("**🗑️ Faxina Severa**")
            st.warning("Apaga DEFINITIVAMENTE todos os arquivos nas pastas /media e /downloads.")
            confirm = st.checkbox("Confirmo que desejo apagar TUDO.")
            if st.button("🚨 EXECUTAR DELETE SEVERO", type="primary", disabled=not confirm):
                import shutil
                m_dir = os.path.join(proj_root, "media")
                d_dir = os.path.join(proj_root, "downloads")
                count = 0
                for folder in [m_dir, d_dir]:
                    for f in os.listdir(folder):
                        fp = os.path.join(folder, f)
                        try:
                            if os.path.isfile(fp): os.unlink(fp); count += 1
                            elif os.path.isdir(fp): shutil.rmtree(fp); count += 1
                        except: pass
                st.success(f"🔥 {count} arquivos eliminados com sucesso!"); st.rerun()


    media_dir = os.path.join(proj_root, "media")
    down_dir = os.path.join(proj_root, "downloads")
    for d in [media_dir, down_dir]: os.makedirs(d, exist_ok=True)
    
    arquivos_m = [(f, media_dir) for f in os.listdir(media_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4'))]
    arquivos_d = [(f, down_dir) for f in os.listdir(down_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.mp4'))]
    all_files = arquivos_m + arquivos_d
    
    if not all_files:
        st.info("Nenhuma mídia encontrada em /media ou /downloads.")
    else:
        st.markdown(f"Exibindo **{len(all_files)}** arquivos detectados.")
        search_m = st.text_input("🔍 Buscar mídia por nome:", "")
        if search_m: all_files = [f for f in all_files if search_m.lower() in f[0].lower()]
        
        # Grid de mídias
        cols_m = st.columns(4)
        for i, (arq, folder) in enumerate(all_files):
            idx = i % 4
            path_arq = os.path.join(folder, arq)
            with cols_m[idx]:
                with st.container(border=True):
                    if arq.lower().endswith('.mp4'):
                        try:
                            st.video(path_arq)
                        except Exception:
                            st.error("Erro")
                    else:
                        try:
                            st.image(path_arq, use_container_width=True)
                        except Exception:
                            st.error("Mídia corrompida")
                    st.caption(f"📄 {arq[:20]}")
                    
                    link_shopee = st.text_input("🔗 Link (Shopee):", placeholder="Opcional", key=f"link_m_{i}")
                    
                    # Botões de ação
                    c_b1, c_b2 = st.columns(2)
                    if c_b1.button("🎨 Arte", key=f"re_pillow_{i}", use_container_width=True):
                        with st.spinner("Gerando..."):
                            try:
                                from app.publisher.card_generator import generate_feed_card
                                nova_arte = generate_feed_card(path_arq)
                                if nova_arte:
                                    st.success("Gerada!"); st.rerun()
                            except Exception as e: st.error("Erro")
                    
                    if c_b2.button("📦 Usar", key=f"use_{i}", type="primary", use_container_width=True):
                        conn_u = get_connection(); cu = conn_u.cursor()
                        # Determina se envia ou não o link
                        # Definimos status default
                        status = 'PENDING' if link_shopee else 'MISSING_LINK'
                        cu.execute("INSERT INTO achados (texto_original, midia_path, link_original, status, status_fluxo) VALUES (?, ?, ?, ?, 'Ideia')",
                                   (f"Nova Mídia Adicionada: {arq}", path_arq, link_shopee, status))
                        conn_u.commit(); conn_u.close()
                        st.success("No Estúdio!"); st.rerun()

# ══════════════════════════════════════════════
#  ABA 6 — ENGAJAMENTO (AUTO-DM)
# ══════════════════════════════════════════════
if menu_selecionado == '💬 Automações & Engajamento':
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(16,185,129,0.1),rgba(16,185,129,0.04));border:1px solid rgba(16,185,129,0.2);border-radius:16px;padding:20px 24px;margin-bottom:20px;">
      <h3 style="margin:0;color:#E8EAF0;font-size:1.2rem;font-weight:800;">💬 Monitor de Engajamento & Auto-DM</h3>
      <p style="margin:4px 0 0;color:#8B90A0;font-size:0.85rem;">Acompanhe em tempo real quem o seu bot está atendendo no Instagram.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🚀 Histórico de Conversas (Auto-DM)")
    conn_e = get_connection()
    try:
        df_bot = pd.read_sql_query("""
            SELECT timestamp, user_id, palavra_gatilho, resposta_enviada
            FROM bot_logs ORDER BY timestamp DESC LIMIT 50
        """, conn_e)
        if not df_bot.empty:
            st.dataframe(df_bot, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma interação registrada ainda. O bot está aguardando gatilhos!")
    except: st.caption("Tabela de logs do bot sendo inicializada...")
    conn_e.close()

    st.divider()
    st.markdown("#### 🔍 Simular Resposta Manual")
    with st.expander("💬 Responder Comentário Específico"):
        c_id = st.text_input("ID do Comentário:", placeholder="123456789...")
        c_msg = st.text_area("Sua Resposta:", placeholder="Oii! Te mandei o link no direct! ✨")
        if st.button("🚀 Enviar Resposta Agora", type="primary"):
            if c_id and c_msg:
                try:
                    from app.social_interactions.instagram_bot import post_public_reply
                    if post_public_reply(c_id, c_msg):
                        st.success("Resposta enviada com sucesso!")
                    else: st.error("Erro ao enviar. Verifique o Access Token.")
                except Exception as e: st.error(str(e))

    st.divider()
    st.markdown("#### ⚙️ Configurações do Bot")
    with st.expander("🛠️ Gerenciar Gatilhos e Mensagens", expanded=False):
        conn_cfg = get_connection()
        df_cfg = pd.read_sql_query("SELECT chave, valor FROM config", conn_cfg)
        conn_cfg.close()
        
        with st.form("form_config"):
            new_triggers = st.text_input("Palavras-Gatilho (separadas por vírgula):", 
                                          value=df_cfg[df_cfg['chave']=='trigger_words']['valor'].values[0] if not df_cfg.empty else "")
            new_reply = st.text_input("Resposta Pública Padrão:", 
                                       value=df_cfg[df_cfg['chave']=='reply_message']['valor'].values[0] if not df_cfg.empty else "")
            
            if st.form_submit_button("💾 Salvar Configurações", type="primary"):
                conn_save = get_connection(); cs = conn_save.cursor()
                cs.execute("UPDATE config SET valor = ? WHERE chave = 'trigger_words'", (new_triggers,))
                cs.execute("UPDATE config SET valor = ? WHERE chave = 'reply_message'", (new_reply,))
                conn_save.commit(); conn_save.close()
                st.success("Configurações atualizadas!"); st.rerun()

    st.divider()
    st.markdown("#### 📑 Histórico de Interações")
    t_comm, t_dm = st.tabs(["💬 Comentários", "✉️ DMs"])

    conn_h = get_connection()
    with t_comm:
        try:
            df_comm = pd.read_sql_query("""
                SELECT timestamp, username, texto, media_id 
                FROM engagement_logs WHERE tipo = 'COMMENT' ORDER BY timestamp DESC LIMIT 50
            """, conn_h)
            if not df_comm.empty:
                st.dataframe(df_comm, use_container_width=True, hide_index=True)
            else: st.info("Nenhum comentário sincronizado.")
        except: st.caption("Inicializando...")

    with t_dm:
        try:
            df_dm = pd.read_sql_query("""
                SELECT timestamp, username, texto 
                FROM engagement_logs WHERE tipo = 'DM' ORDER BY timestamp DESC LIMIT 50
            """, conn_h)
            if not df_dm.empty:
                st.dataframe(df_dm, use_container_width=True, hide_index=True)
            else: st.info("Nenhuma DM sincronizada.")
        except: st.caption("Inicializando...")
    conn_h.close()

# ══════════════════════════════════════════════
#  ABA 7 — VITRINE ONLINE (STATUS)
# ══════════════════════════════════════════════
if menu_selecionado == '⚙️ Configurações Extra':
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(255,107,53,0.1),rgba(255,107,53,0.04));border:1px solid rgba(255,107,53,0.2);border-radius:16px;padding:20px 24px;margin-bottom:20px;">
      <h3 style="margin:0;color:#E8EAF0;font-size:1.2rem;font-weight:800;">🌐 Status da Vitrine Online</h3>
      <p style="margin:4px 0 0;color:#8B90A0;font-size:0.85rem;">Gerencie o deploy do seu site no GitHub Pages.</p>
    </div>
    """, unsafe_allow_html=True)

    col_on1, col_on2 = st.columns(2)

    with col_on1:
        st.markdown("#### 🚀 Sincronização")
        st.info("A vitrine é atualizada automaticamente a cada 1 hora. Se precisar de uma atualização imediata, use o botão abaixo.")
        if st.button("🔄 Atualizar Vitrine Agora", type="primary", use_container_width=True, key="btn_update_online"):
            with st.spinner("Gerando HTML e enviando para o GitHub..."):
                try:
                    # Executa o script de atualização
                    script_path = os.path.join(proj_root, "app/publisher/update_vitrine.py")
                    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
                    if result.returncode == 0:
                        st.success("✅ Vitrine atualizada e enviada para o GitHub!")
                        st.balloons()
                    else:
                        st.error(f"Erro no deploy: {result.stderr}")
                except Exception as e: st.error(str(e))

    with col_on2:
        st.markdown("#### 🔗 Links Úteis")
        git_repo = os.getenv("GITHUB_REPO", "SeuUsuario/SeuRepo")
        # Prevenção de erro caso o repo não tenha '/'
        if '/' in git_repo:
            user_git, repo_git = git_repo.split('/')[:2]
            site_url = f"https://{user_git}.github.io/{repo_git}"
        else:
            site_url = f"https://github.com/{git_repo}"
            
        st.markdown(f"""
        - **Site na Web:** [{site_url}]({site_url})
        - **Repositório GitHub:** [Link do Repo](https://github.com/{git_repo})
        """)
        
        # Preview do theme.json atual
        with st.expander("📄 Ver theme.json atual"):
            theme_path_check = os.path.join(proj_root, "theme.json")
            if os.path.exists(theme_path_check):
                with open(theme_path_check, "r", encoding="utf-8", errors="replace") as f:
                    st.json(json.load(f))

