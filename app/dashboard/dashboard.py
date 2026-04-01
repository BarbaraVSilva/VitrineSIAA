import streamlit as st
import sqlite3
import os
import sys
import subprocess

# Corrige o path para garantir que importe módulos irmãos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.core.database import get_connection
from app.core.shopee_api import get_affiliate_link
from app.core.logger import log_event
import json
import datetime

st.set_page_config(page_title="SIAA-2026 Admin", page_icon="🛍️", layout="wide")

st.title("🛍️ Painel de Triagem - SIAA-2026")

proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
log_dir = os.path.join(proj_root, "logs")
os.makedirs(log_dir, exist_ok=True)

@st.cache_resource
def get_process_registry():
    return {}

tab1, tab2, tab3 = st.tabs(["✅ Aprovação", "⚙️ Motores", "📊 Monitoramento NOC"])

with tab1:
    st.markdown("Bem-vinda! Este é o painel de aprovação do seu Bot Inteligente de Afiliados.")

    def get_pendentes():
        conn = get_connection()
        c = conn.cursor()
        # Pega apenas os raspados que ainda não foram aprovados
        try:
            c.execute("SELECT id, texto_original, midia_path, cover_path, link_original, link_backup_1, link_backup_2, categoria FROM achados WHERE status = 'PENDING'")
        except sqlite3.OperationalError:
            c.execute("SELECT id, texto_original, midia_path, NULL as cover_path, link_original, NULL as link_backup_1, NULL as link_backup_2, 'Geral' as categoria FROM achados WHERE status = 'PENDING'")
        rows = c.fetchall()
        conn.close()
        return rows

    pendentes = get_pendentes()

    if not pendentes:
        st.success("Tudo Limpo! Nenhum achado aguardando aprovação agora.")
        st.info("O Crawler no TG (@canal_teste) continua monitorando 24h na AWS/Local.")
    else:
        for p_id, msg, midia, cover, link, b1, b2, cat in pendentes:
            with st.expander(f"📌 Achado #{p_id} ({cat})", expanded=True):
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # Preview Media
                    if midia and os.path.exists(midia):
                        if midia.endswith((".mp4", ".mov")):
                            st.video(midia)
                            if cover and os.path.exists(cover):
                                st.markdown("**Foto Capa Extraída:**")
                                st.image(cover, use_container_width=True)
                        else:
                            st.image(midia, use_container_width=True)
                    else:
                        st.info("Sem mídia ou preview offline.")
                        
                with col2:
                    st.markdown("**Texto Capturado (Telegram):**")
                    st.code(msg, language="markdown")
                    st.write(f"**Link Original Encontrado:** {link}")
                    
                    if st.button(f"✨ Sugerir Ganchos Virais (IA)", key=f"btn_hook_{p_id}"):
                        with st.spinner("Gerando ganchos com IA..."):
                            st.session_state[f"hooks_{p_id}"] = generate_hooks(msg)
                    
                    if st.session_state.get(f"hooks_{p_id}"):
                        st.markdown("**Opções de Hook (Copie e cole na legenda):**")
                        for idx, hook in enumerate(st.session_state[f"hooks_{p_id}"]):
                            st.info(f"👉 {hook}")
                    
                    with st.form(f"aprovar_{p_id}"):
                        # Edição humana
                        texto_editado = st.text_area("✍️ Edite a legenda do post (Para Instagram/TikTok)", msg)
                        nome_prod = st.text_input("📦 Título Curto da Vitrine:")
                        
                        # Seleção de Categoria
                        categorias_disp = ["Geral", "Tecnologia", "Casa e Decoração", "Moda", "Beleza", "Pet", "Outros"]
                        idx_cat = categorias_disp.index(cat) if cat in categorias_disp else 0
                        cat_selecionada = st.selectbox("📑 Categoria na Vitrine:", categorias_disp, index=idx_cat)
                        
                        link_r1 = st.text_input("🔄 Link Reserva 1 (Em caso de esgotar o oficial):", value=b1 if b1 else "")
                        link_r2 = st.text_input("🔄 Link Reserva 2 (Backup Extremo):", value=b2 if b2 else "")
                        
                        Aplicar_tarja = False
                        usar_foto = False
                        if cover and os.path.exists(cover):
                            usar_foto = st.checkbox("📸 Postar APENAS a Foto (Frame do Vídeo) no Instagram", key=f"foto_{p_id}")
                            Aplicar_tarja = st.checkbox("🖌️ Aplicar Tarja (Design SIAA Ofertas) automaticamente?", key=f"tarja_{p_id}")
                        elif midia and not midia.endswith((".mp4", ".mov")) and os.path.exists(midia):
                            Aplicar_tarja = st.checkbox("🖌️ Aplicar Tarja (Design SIAA Ofertas) automaticamente?", key=f"tarja_img_{p_id}")
                        
                        c_submit, c_reject = st.columns(2)
                        aprovar = c_submit.form_submit_button("✅ Aprovar (Gerar Link Afiliado)", type="primary")
                        rejeitar = c_reject.form_submit_button("❌ Descartar Produto")
                        
                        if aprovar:
                            conn = get_connection()
                            c = conn.cursor()
                            
                            # Lógica de Imagem a Publicar + Branding IA (Pillow)
                            imagem_final = cover if usar_foto and cover else midia
                            
                            if Aplicar_tarja and imagem_final and not imagem_final.endswith((".mp4", ".mov")):
                                imagem_final = apply_branding_to_image(imagem_final, "🔥 OFERTA SURREAL 🔥")
                                
                            c.execute("UPDATE achados SET midia_path = ? WHERE id = ?", (imagem_final, p_id))
                            c.execute("UPDATE achados SET status = 'APPROVED', texto_original = ? WHERE id = ?", (texto_editado, p_id))
                            
                            link_afiliado = get_affiliate_link(link) if link else f"https://shope.ee/default_{p_id}"
                            nome = nome_prod if nome_prod else f"Oferta Especial #{p_id}"
                            
                            c.execute("INSERT INTO produtos (achado_id, link_afiliado, link_backup, link_backup_2, nome_produto, categoria) VALUES (?,?,?,?,?,?)", 
                                      (p_id, link_afiliado, link_r1, link_r2, nome, cat_selecionada))
                            conn.commit()
                            conn.close()
                            
                            send_admin_log(f"✅ Produto #{p_id} ({nome}) aprovado!\nFoi inserido no banco para auto-post\nVitrine atualizada.")
                            st.success("Post Aprovado! Link Afiliado Gerado e Inserido na Vitrine.")
                            st.rerun()
                            
                        if rejeitar:
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE achados SET status = 'REJECTED' WHERE id = ?", (p_id,))
                            conn.commit()
                            conn.close()
                            st.warning("Produto descartado!.")
                            st.rerun()

with tab2:
    st.markdown("### 🖥️ Orquestrador NOC (SIAA-2026)")
    st.info("Painel de monitoramento de processos. Motores ativos garantem a mineração 24/7.")
    
    registry = get_process_registry()
    services = {
        "🧠 Cérebro (main.py)": ["python", "main.py"],
        "🌐 Webhook Server": ["python", "app/webhook_server.py"],
        "🕵️ Crawler Telegram": ["python", "app/mineracao/crawler_telegram.py"],
    }
    
    cmd_env = os.environ.copy()
    
    for name, cmd in services.items():
        st.markdown(f"#### {name}")
        proc_key = name.split(" ")[1] # e.g. "Cérebro"
        
        is_running = proc_key in registry and registry[proc_key].poll() is None
        
        c1, c2, c3 = st.columns([1, 1, 3])
        
        with c1:
            if is_running:
                st.success("🟢 Online")
            else:
                st.error("🔴 Offline")
                
        with c2:
            if st.button(f"▶️ Iniciar", key=f"btn_start_{proc_key}", disabled=is_running):
                # Setup Log Redirect
                log_file = os.path.join(log_dir, f"{proc_key.lower().replace(' ', '_')}.log")
                out_fd = open(log_file, "a")
                
                p = subprocess.Popen(cmd, cwd=proj_root, env=cmd_env, stdout=out_fd, stderr=subprocess.STDOUT)
                registry[proc_key] = p
                st.rerun()
                
            if st.button(f"⏹️ Parar", key=f"btn_stop_{proc_key}", disabled=not is_running):
                registry[proc_key].terminate()
                registry[proc_key].wait()
                st.rerun()
                
        with c3:
            log_file = os.path.join(log_dir, f"{proc_key.lower().replace(' ', '_')}.log")
            
            with st.expander(f"📜 Mostrar Terminal de: {proc_key}"):
                if st.button("🔄 Puxar novos logs", key=f"btn_log_{proc_key}"):
                    pass # Just triggers a rerun to update lines
                    
                if os.path.exists(log_file):
                    with open(log_file, "r", encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        if lines:
                            st.code("".join(lines[-30:]), language="bash")
                        else:
                            st.info("Log Vazio.")
                else:
                    st.info("Nenhum registro no console ainda.")
with tab3:
    st.markdown("### 📊 Centro de Operações (NOC)")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### Status da Vitrine")
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM produtos WHERE estoque_ok = 1")
        ativos = c.fetchone()[0]
        c.execute("SELECT MAX(last_checked) FROM produtos")
        last_check = c.fetchone()[0]
        conn.close()
        
        st.metric("Produtos Ativos", ativos)
        st.caption(f"Última Varredura: {last_check if last_check else 'Nunca'}")
        
    with col_b:
        st.markdown("#### Alertas Recentes")
        # Aqui poderíamos ler do log estruturado e filtrar por ERROR/CRITICAL
        st.warning("Nenhum alerta crítico nas últimas 24h.")

    st.divider()
    st.markdown("#### Logs Estruturados (Real-time)")
    # Simulação de leitura de logs JSON
    log_file = os.path.join(log_dir, "siaa_structured.json") # Vamos configurar main.py pra escrever aqui também
    if st.button("Limpar Logs do Painel"):
        if os.path.exists(log_file): os.remove(log_file)
        
    st.info("Monitorando fluxo de eventos do Cérebro...")

st.sidebar.markdown("### Configurações Rápidas")
if st.sidebar.button("Rodar Crawler (Mock)"):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO achados (texto_original, midia_path, link_original, status) VALUES (?,?,?,?)", 
              ("Achadinho de Teste! Olha que incrível!", "fake.mp4", "https://shopee.com.br/produto-teste", "PENDING"))
    conn.commit()
    conn.close()
    st.sidebar.success("Produto mock inserido! Recarregue a página.")
    st.rerun()

if st.sidebar.button("Atualizar Vitrine (HTML)", type="primary"):
    from app.publisher.update_vitrine import generate_html_vitrine
    generate_html_vitrine()
    st.sidebar.success("Site Github Pages Atualizado com Sucesso!")
