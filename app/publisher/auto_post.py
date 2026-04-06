import os
import time
import sys

from app.core.database import get_connection
from app.core.shopee_api import get_affiliate_link
from app.publisher.update_vitrine import generate_html_vitrine
from app.publisher.whatsapp_groups import publish_to_whatsapp_group

from selenium import webdriver
# O POSTADOR LEGADO DE SELENIUM FOI REMOVIDO PARA EVITAR BUGS DE TELA/CAPTCHAS.
# O Sistema SIAA-2026 utiliza a conexão nativa Meta Graph API para 100% de invisibilidade
# implementada no Módulo Mestre (app/publisher/meta_api_publisher.py).

def run_publisher():
    from app.core.scheduler_engine import obter_posts_prontos_para_agora, marcar_como_postado
    
    posts = obter_posts_prontos_para_agora()
    
    if not posts:
        print("[AUTO-PUBLISHER] Não há posts agendados para este horário específico. Volto mais tarde.")
        return

    print(f"[AUTO-PUBLISHER] Identificou {len(posts)} posts que atingiram o alarme do relógio! Disparando postagens...")
    
    # Busca grupo JID do env se definido, senão envia config vazia
    wa_group_jid = os.getenv("WHATSAPP_GROUP_JID", "")
    
    for row in posts:
        p_id = row[0]
        a_id = row[1]
        legenda = row[2]
        midia = row[3]
        link_afiliado = row[4]
        
        print("-" * 30)
        
        # Faz a postagem (Para WhatsApp)
        if wa_group_jid:
            # Analytics Passo C: Link específico para WhatsApp
            link_wa = get_affiliate_link(link_afiliado, sub_id=f"post_{p_id}_wa")
            texto_wa = f"{legenda}\n\n👉 Compre aqui: {link_wa}"
            publish_to_whatsapp_group(wa_group_jid, texto_wa, midia)
        
        # Faz a postagem (Para o Instagram via META API Graph)
        from app.publisher.meta_api_publisher import MetaGraphPublisher
        meta_bot = MetaGraphPublisher()
        
        # Analytics Passo C: Referência ao post na Vitrine
        # Regra do Instagram: Links clicáveis não existem no Feed/Reels.
        # Por isso focamos no #ID para o usuário buscar no link da Bio.
        legenda_ig_segura = f"{legenda}\n\n🛍️ Procure pelo Achado #{p_id} no Link da nossa Bio para comprar!"
        
        # (O loop continuaria com publish_to_instagram...)
        
        sucesso = meta_bot.publish_to_instagram(url_publica_midia, legenda_ig_segura, is_video)
            
        if sucesso:
            # Marca como publicado nos dois BDs
            marcar_como_postado(p_id, a_id)
            print(f"[AUTO-PUBLISHER] Produto ID #{p_id} mudou de status para POSTED.")
            
    print("-" * 30)
    print("[AUTO-PUBLISHER] Todos os posts da vez foram enviados.")
    
    # Vitrine (Site HTML) deve ser atualizada em tempo real garantindo que
    # se você postou algo, o link entra no site HOJE de imediato.
    print("[AUTO-PUBLISHER] Acionando a atualização da Vitrine Web...")
    generate_html_vitrine()

if __name__ == "__main__":
    run_publisher()
