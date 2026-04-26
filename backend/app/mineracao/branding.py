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

def apply_branding_to_image(image_path, text_overlay="ACHADINHO DA VEZ", style="standard"):
    """
    Aplica identidade visual à imagem. Suporta estilos: 'standard', 'minimalist_glass'.
    """
    if not image_path or not os.path.exists(image_path):
        return image_path
        
    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png', '.webp', '.jfif']:
        log_event(f"Formato não suportado: {ext}", component="BrandingEngine", status="WARNING")
        return image_path
        
    theme = load_theme()
    cor_primaria = theme["cores"].get("primaria", "#ff5722")
    
    try:
        img = Image.open(image_path).convert("RGBA")
        width, height = img.size
        overlay = Image.new("RGBA", img.size, (0,0,0,0))
        drawing = ImageDraw.Draw(overlay)
        
        # Seleção de Fonte
        try:
            # Tentar carregar uma fonte mais moderna se disponível, senão arialbd
            font_size = int(height * 0.07)
            font = ImageFont.truetype("arialbd.ttf", font_size)
        except:
            font = ImageFont.load_default()

        if style == "minimalist_glass":
            # Estilo Glassmorphism: Tarja centralizada ou flutuante com blur (simulado)
            banner_h = int(height * 0.12)
            margin = int(width * 0.05)
            # Retângulo com cantos arredondados e transparência
            shape = [margin, height - banner_h - margin, width - margin, height - margin]
            # Branco semi-transparente para o 'glass'
            drawing.rounded_rectangle(shape, radius=20, fill=(255, 255, 255, 180), outline=(255, 255, 255, 200), width=2)
            
            # Texto centralizado na cor escura para contraste no glass branco
            text_bbox = drawing.textbbox((0, 0), text_overlay, font=font)
            tx_w = text_bbox[2] - text_bbox[0]
            tx_h = text_bbox[3] - text_bbox[1]
            
            tx_x = (width - tx_w) / 2
            tx_y = (height - banner_h - margin) + (banner_h - tx_h) / 2
            drawing.text((tx_x, tx_y), text_overlay, fill=(30, 30, 30, 255), font=font)
            
        else:
            # Estilo Standard (Tarja Sólida na Base)
            banner_h = int(height * 0.15)
            shape = [(0, height - banner_h), (width, height)]
            drawing.rectangle(shape, fill=cor_primaria)
            
            text_bbox = drawing.textbbox((0, 0), text_overlay, font=font)
            tx_w = text_bbox[2] - text_bbox[0]
            tx_h = text_bbox[3] - text_bbox[1]
            
            tx_x = (width - tx_w) / 2
            tx_y = (height - banner_h) + (banner_h - tx_h) / 2
            
            # Sombra e Texto
            drawing.text((tx_x+2, tx_y+2), text_overlay, fill="black", font=font)
            drawing.text((tx_x, tx_y), text_overlay, fill="white", font=font)

        # Mesclar overlay
        out = Image.alpha_composite(img, overlay)
        
        # Salvar
        suffix = "_minimalist" if style == "minimalist_glass" else "_branding"
        out_path = image_path.replace(ext, f"{suffix}{ext}")
        out.convert("RGB").save(out_path, quality=95)
        
        log_event(f"Branding ({style}) aplicado: {out_path}", component="BrandingEngine", status="SUCCESS")
        return out_path
        
    except Exception as e:
        log_event(f"Erro no Branding: {str(e)}", component="BrandingEngine", status="ERROR", level=logging.ERROR)
        return image_path
