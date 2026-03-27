import os
import json
from PIL import Image, ImageDraw, ImageFont

# Carregar config de tema centralizada
THEME_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../theme.json'))

def load_theme():
    if os.path.exists(THEME_PATH):
        with open(THEME_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    # Fallback default
    return {"cores": {"primaria": "#ff5722"}}

def apply_branding_to_image(image_path, text_overlay="ACHADINHO DA VEZ"):
    """
    Pega uma foto (seja do telegram ou da extração do vídeo), e aplica a identidade 
    visual (borda ou tarja) via biblioteca Pillow para chamar atenção no Feed do Insta.
    """
    if not image_path or not os.path.exists(image_path):
        return image_path
        
    theme = load_theme()
    cor_primaria = theme["cores"].get("primaria", "#ff5722")
    
    try:
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        
        # Cria uma layer de desenho
        drawing = ImageDraw.Draw(img)
        
        # EXECUTANDO: Tarja na base da imagem (ex: 15% inferior de altura)
        banner_height = int(height * 0.15)
        # Retângulo cheio com Alpha (transparente) ou Sólido
        shape = [(0, height - banner_height), (width, height)]
        drawing.rectangle(shape, fill=cor_primaria)
        
        # Tenta carregar uma fonte default ou Arial. Se falhar no Windows/Linux, recai pra default sem erro
        try:
            # Fonte Arial no Windows
            font = ImageFont.truetype("arialbd.ttf", int(height * 0.08))
        except:
            font = ImageFont.load_default()
            
        # Adiciona o Texto (Ex: PROMOÇÃO, ACHADOS DO DIA)
        text_bbox = drawing.textbbox((0, 0), text_overlay, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        text_x = (width - text_width) / 2
        text_y = (height - banner_height) + (banner_height - text_height) / 2
        
        # Sombra dupla para leitura perfeita
        drawing.text((text_x+3, text_y+3), text_overlay, fill="black", font=font)
        drawing.text((text_x, text_y), text_overlay, fill="white", font=font)
        
        # Salva o novo resultado por cima do antigo ou arquivo novo
        out_path = image_path.replace(".jpg", "_branding.jpg").replace(".png", "_branding.png")
        img.convert("RGB").save(out_path, quality=95)
        
        print(f"[BRANDING] Arte convertida e aprimorada com sucesso: {out_path}")
        return out_path
        
    except Exception as e:
        print(f"[BRANDING] Falha ao processar design Pillow na imagem: {e}")
        return image_path
