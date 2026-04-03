import os
import time
import sys

from app.core.database import get_connection
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
            texto_wa = f"{legenda}\n\n👉 Compre aqui: {link_afiliado}"
            publish_to_whatsapp_group(wa_group_jid, texto_wa, midia)
        
        # Faz a postagem (Para o Instagram via META API Graph)
        from app.publisher.meta_api_publisher import MetaGraphPublisher
        meta_bot = MetaGraphPublisher()
        
        # O API do IG precisa de um link de mídia público e não de arquivo local path_to_file.
        # Caso nosso midia já seja HTTP (ex: direto da shopee sem baixar), passamos ele.
        # Como o SIAA baixa as fotos, assumiremos que vc usou uma CDN/Ngork na URL do Mídia 
        # (Para testes do cliente onde midia as vezes é local, precisará adaptar a host).
        # Regra do Instagram para Perfis sem Seguidores: Links clicáveis não existem no Feed/Reels.
        # A conta deve hospedar a Vitrine (Gerada no Github Pages) no Link da Bio.
        legenda_ig_segura = f"{legenda}\n\n🛍️ Procure pelo Achado #{p_id} no Link da nossa Bio para comprar!"
        
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
