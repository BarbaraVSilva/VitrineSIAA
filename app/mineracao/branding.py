from app.core.logger import log_event
import logging
import os
import json
from PIL import Image, ImageDraw, ImageFont

# Carregar config de tema centralizada
THEME_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../theme.json'))

def load_theme():
    if os.path.exists(THEME_PATH):
        try:
            with open(THEME_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # Fallback default
    return {"cores": {"primaria": "#ff5722"}}

def apply_branding_to_image(image_path, text_overlay="ACHADINHO DA VEZ"):
    """
    Pega uma foto (suporta .jpg, .png, .webp, .jfif), e aplica a identidade 
    visual (borda ou tarja) via biblioteca Pillow.
    """
    if not image_path or not os.path.exists(image_path):
        return image_path
        
    # Validar extensão
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.jfif']:
        log_event(f"Formato de imagem não suportado para branding: {ext}", component="BrandingEngine", status="WARNING")
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
        out_path = image_path.replace(ext, f"_branding{ext}")
        img.convert("RGB").save(out_path, quality=95)
        
        log_event(f"Branding aplicado com sucesso: {out_path}", component="BrandingEngine", status="SUCCESS")
        return out_path
        
    except Exception as e:
        log_event(f"Falha ao processar design Pillow: {str(e)}", component="BrandingEngine", status="ERROR", level=logging.ERROR)
        return image_path
