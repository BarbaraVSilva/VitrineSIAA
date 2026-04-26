import os
import time
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from app.core.logger import log_event

def generate_feed_card(original_image_path: str, output_path: str = None) -> str:
    """
    Constrói um card estético para o Feed/Stories do Instagram.
    Pega a imagem original (vertical ou horizontal), adiciona um fundo quadrado 1080x1080 
    com desfoque gaussiano, sobrepõe a imagem redimensionada ao centro e desenha selos de oferta.
    """
    if not os.path.exists(original_image_path):
        log_event(f"Imagem não encontrada para gerar o Card: {original_image_path}", component="CardGenerator", status="ERROR")
        return ""
        
    try:
        # 1. Carregar a imagem original
        img = Image.open(original_image_path).convert("RGB")
        
        # 2. Criar o Canvas Quadrado 1080x1080 (Padrão Feed)
        canvas_size = 1080
        background = img.resize((canvas_size, canvas_size))
        
        # Aplicar Desfoque Pesado no fundo
        background = background.filter(ImageFilter.GaussianBlur(radius=40))
        
        # Opcional: Escurecer um pouco o fundo para a imagem central destacar mais
        darker_bg = Image.new('RGB', (canvas_size, canvas_size), color=(0,0,0))
        background = Image.blend(background, darker_bg, alpha=0.3)
        
        # 3. Redimensionar a imagem original mantendo o Aspect Ratio, até caber dentro do canvas (com margem)
        max_size = 900 # Uma margem bonita
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # 4. Colar a imagem original no centro do Canvas
        x_offset = (canvas_size - img.width) // 2
        y_offset = (canvas_size - img.height) // 2
        
        # Simular uma "Sombra" atrás da imagem principal
        shadow = Image.new('RGBA', img.size, color=(0,0,0,150))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=8))
        background.paste(shadow, (x_offset+10, y_offset+15), shadow)
        
        # Colar Imagem Principal
        background.paste(img, (x_offset, y_offset))
        
        # 5. Desenhar Selos / Etiquetas (Ex: "🔥 Oferta Relâmpago")
        draw = ImageDraw.Draw(background)
        
        # Retângulo do topo promocional
        draw.rectangle([0, 0, canvas_size, 80], fill=(234, 43, 43)) # Vermelho forte Shopee
        # Tentar carregar fonte, se não houver Arial, usar padrão nativo 
        try:
            # Em python Windows, arial.ttf geralmente existe
            font = ImageFont.truetype("arial.ttf", 46)
        except:
            font = ImageFont.load_default()
            
        text = "🔥 ACHADINHO VIP - OFERTA LIMITADA 🔥"
        
        # Centralizar texto à moda antiga ou via proporção
        text_bbox = draw.textbbox((0,0), text, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        draw.text(((canvas_size - text_w) / 2, 18), text, font=font, fill=(255, 255, 255))
        
        # 6. Salvar o arquivo final
        if not output_path:
            # Substitui a extensão por um identificador estético
            base, ext = os.path.splitext(original_image_path)
            output_path = f"{base}_feed_ready.jpg"
            
        background.save(output_path, quality=95)
        log_event(f"Card de Feed Gerado! Salvo em: {output_path}", component="CardGenerator", status="SUCCESS")
        
        return output_path
        
    except Exception as e:
        log_event(f"Erro ao desenhar Card com Pillow: {e}", component="CardGenerator", status="ERROR", level=40)
        return ""

def generate_coupon_card(codigo_cupom: str, valor_desconto: str, obs_validade: str = "Resgate antes que expire") -> str:
    """
    Constrói um card "Bomba de Desconto" ultra-agressivo para envio de cupons no WhatsApp.
    Não depende de foto de produto, gera fundo sólido de promoção do absoluto zero.
    """
    try:
        # Canvas 1080x1080 sólido pro Whatsapp
        canvas_size = 1080
        background = Image.new('RGB', (canvas_size, canvas_size), color=(250, 80, 0)) # Laranja Shopee Choque
        draw = ImageDraw.Draw(background)
        
        # Borda interna destacada
        draw.rectangle([30, 30, canvas_size-30, canvas_size-30], outline=(255, 255, 255), width=15)
        
        try:
            font_title = ImageFont.truetype("arialbd.ttf", 90)
            font_code = ImageFont.truetype("arialbd.ttf", 140)
            font_sub = ImageFont.truetype("arial.ttf", 55)
        except:
            font_title = font_code = font_sub = ImageFont.load_default()
            
        # 1. Título "CUPOM SURPRESA"
        title = "🚨 CUPOM LIBERADO 🚨"
        t_box = draw.textbbox((0,0), title, font=font_title)
        draw.text(((canvas_size - (t_box[2]-t_box[0])) / 2, 100), title, font=font_title, fill=(255, 255, 255))
        
        # 2. Caixa branca pro código e o código dentro
        w_box = (canvas_size - 900) // 2
        draw.rectangle([w_box, 300, canvas_size - w_box, 600], fill=(255, 255, 255), outline=(0, 0, 0), width=10)
        
        c_box = draw.textbbox((0,0), codigo_cupom, font=font_code)
        draw.text(((canvas_size - (c_box[2]-c_box[0])) / 2, 380), codigo_cupom, font=font_code, fill=(250, 60, 0))
        
        # 3. Valor do Desconto
        val_txt = f"{valor_desconto} OFF"
        v_box = draw.textbbox((0,0), val_txt, font=font_title)
        draw.text(((canvas_size - (v_box[2]-v_box[0])) / 2, 700), val_txt, font=font_title, fill=(255, 230, 0))
        
        # 4. Observação / Validade
        s_box = draw.textbbox((0,0), obs_validade, font=font_sub)
        draw.text(((canvas_size - (s_box[2]-s_box[0])) / 2, 900), obs_validade, font=font_sub, fill=(255, 255, 255))
        
        # Salva em pasta tmp
        output_path = os.path.abspath(f"cupom_{codigo_cupom}_{int(os.path.getmtime('.'))}.jpg")
        background.save(output_path, quality=90)
        log_event(f"Card de Cupom Gerado! Salvo em: {output_path}", component="CardGenerator", status="SUCCESS")
        
        return output_path
        
    except Exception as e:
        log_event(f"Erro ao gerar Card de Cupom: {e}", component="CardGenerator", status="ERROR", level=40)
        return ""

def generate_ai_fallback_image(product_description: str) -> str:
    """
    Se o Crawler bater no Telegram e o link não tiver foto nenhuma associada 
    (ou se for feia/quebrada), invocamos o DALL-E para criar uma Thumb estilo Ads de Luxo.
    """
    try:
        from openai import OpenAI
        import requests
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return ""
            
        client = OpenAI(api_key=api_key)
        
        prompt = f"Um pôster comercial realista, super atraente estilo ecommerce de alto nível. Um produto principal na cena, descrito como: {product_description}. Sem textos feios, iluminação premium fotográfica."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        img_data = requests.get(image_url).content
        
        path = os.path.join(os.getcwd(), f"ai_thumb_{int(time.time())}.jpg")
        with open(path, 'wb') as handler:
            handler.write(img_data)
            
        print(f"[IA IMAGE] DALL-E construiu a imagem mística para o produto salvando em {path}")
        return path
    except Exception as e:
        print(f"[IA IMAGE] Ocorreu um erro gerando AI Fallback: {e}")
        return ""

if __name__ == "__main__":
    # Teste Rápido se vc passar uma imagem na raiz do terminal
    test_img = "test.jpg"
    if os.path.exists(test_img):
        out = generate_feed_card(test_img)
        print("Arte Gerada:", out)
