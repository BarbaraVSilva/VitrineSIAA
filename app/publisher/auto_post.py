import os
import time
import sys

from app.core.database import get_connection
from app.publisher.update_vitrine import generate_html_vitrine
from app.publisher.whatsapp_groups import publish_to_whatsapp_group

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def post_to_social_media(video_path, caption):
    """
    Automação Selenium para Instagram Web usando o perfil do usuário atual
    (para não precisar relogar toda vez).
    """
    print(f"[AUTO-PUBLISHER] Preparando Chrome para postagem Headless no Instagram...")
    
    # Caminho absoluto da mídia para o input type file não falhar
    abs_media_path = os.path.abspath(video_path)
    
    chrome_options = Options()
    user_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chrome_profile_ig'))
    chrome_options.add_argument(f"user-data-dir={user_data_dir}")
    # Descomente a linha abaixo para rodar invisível após a primeira configuração de login:
    # chrome_options.add_argument("--headless")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.instagram.com/")
        print("[AUTO-PUBLISHER] Instagram Aberto. Aguardando carregamento (ou pedindo login na 1ª vez)...")
        
        # Aumentar timer na primeira vez se precisar relogar, ou pegar do env
        wait = WebDriverWait(driver, 30)
        
        # 1. Encontrar o botão Criar (Novo Post)
        # O seletor do botão de 'Criar' do menu lateral do Instagram.
        # Geralmente é um SVG com aria-label='Nova publicação'
        criar_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Nova publicação']/../../..")))
        driver.execute_script("arguments[0].click();", criar_btn)
        time.sleep(2)
        
        # O Insta Web abre um Modal e precisamos enviar o arquivo por um input hidden
        file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@accept='image/jpeg,image/png,image/heic,image/heif,video/mp4,video/quicktime']")))
        file_input.send_keys(abs_media_path)
        print(f"[AUTO-PUBLISHER] Mídia anexada: {abs_media_path}")
        time.sleep(3)
        
        # 2. Clicar em Avançar (Crop / Edit)
        avancar1 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Avançar')]")))
        driver.execute_script("arguments[0].click();", avancar1)
        time.sleep(2)
        
        # 3. Clicar em Avançar (Filtros)
        avancar2 = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Avançar')]")))
        driver.execute_script("arguments[0].click();", avancar2)
        time.sleep(2)
        
        # 4. Escrever legenda
        caption_area = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Escreva uma legenda...']")))
        caption_area.send_keys(caption)
        print("[AUTO-PUBLISHER] Legenda digitada.")
        time.sleep(2)
        
        # 5. Compartilhar
        compartilhar = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Compartilhar')]")))
        driver.execute_script("arguments[0].click();", compartilhar)
        print("[AUTO-PUBLISHER] Compartilhando... Aguardando upload.")
        
        # 6. Aguardar sucesso ("A sua publicação foi compartilhada.")
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'postagem foi compartilhada') or contains(text(), 'publicação foi compartilhada')]")))
        print(f"[AUTO-PUBLISHER] Sucesso! Post no Instagram confirmado.")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"[AUTO-PUBLISHER] Erro no Selenium (Instagram Mudou Layout ou Sem Login?): {e}")
        try:
            driver.quit()
        except:
            pass
        return False

def get_approved_posts():
    """Busca posts aguardando publicação nas redes sociais e status APPROVED."""
    conn = get_connection()
    c = conn.cursor()
    # Puxa dados do achado e o link final de afiliado da tabela produtos
    try:
        c.execute('''
            SELECT a.id, a.texto_original, a.midia_path, p.link_afiliado 
            FROM achados a
            JOIN produtos p ON a.id = p.achado_id
            WHERE a.status = 'APPROVED'
        ''')
        rows = c.fetchall()
    except Exception as e:
        print(f"[AUTO-PUBLISHER] Erro na query DB: {e}")
        rows = []
    finally:
        conn.close()
    return rows

def mark_as_posted(achado_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE achados SET status = 'POSTED' WHERE id = ?", (achado_id,))
    conn.commit()
    conn.close()

def run_publisher():
    posts = get_approved_posts()
    
    if not posts:
        print("[AUTO-PUBLISHER] A fila de postagem aprovada está vazia. Volto mais tarde.")
        return

    print(f"[AUTO-PUBLISHER] Identificou {len(posts)} produtos aprovados! Dando inicio à postagem.")
    
    # Busca grupo JID do env se definido, senão envia config vazia
    wa_group_jid = os.getenv("WHATSAPP_GROUP_JID", "")
    
    for p_id, legenda, midia, link_afiliado in posts:
        print("-" * 30)
        
        # Faz a postagem (Para WhatsApp)
        if wa_group_jid:
            texto_wa = f"{legenda}\n\n👉 Compre aqui: {link_afiliado}"
            publish_to_whatsapp_group(wa_group_jid, texto_wa, midia)
        
        # Faz a postagem (Para o Instagram via Selenium)
        sucesso = post_to_social_media(midia, legenda)
            
        if sucesso:
            # Marca como publicado
            mark_as_posted(p_id)
            print(f"[AUTO-PUBLISHER] Produto ID #{p_id} mudou de status para POSTED.")
            
    print("-" * 30)
    print("[AUTO-PUBLISHER] Todos os posts da vez foram enviados.")
    
    # Vitrine (Site HTML) deve ser atualizada em tempo real garantindo que
    # se você postou algo, o link entra no site HOJE de imediato.
    print("[AUTO-PUBLISHER] Acionando a atualização da Vitrine Web...")
    generate_html_vitrine()

if __name__ == "__main__":
    run_publisher()
