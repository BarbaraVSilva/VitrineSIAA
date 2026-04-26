import os
import asyncio
import uuid
from moviepy.editor import VideoFileClip, vfx, ImageClip, CompositeVideoClip
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np

def create_text_overlay(text, width=720, height=1280, font_size=60, color="yellow"):
    """
    Cria uma imagem transparente (RGBA) com texto centralizado usando Pillow.
    Retorna o path da imagem gerada.
    """
    # Cria uma imagem transparente
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Tenta carregar uma fonte robusta do Windows
    try:
        font = ImageFont.truetype("arialbd.ttf", font_size)
    except:
        font = ImageFont.load_default()
        
    # Quebra o texto em linhas se for muito longo
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        if len(current_line + word) < 20:
            current_line += word + " "
        else:
            lines.append(current_line.strip())
            current_line = word + " "
    lines.append(current_line.strip())
    
    # Desenha o texto centralizado com contorno preto (stroke)
    total_h = len(lines) * (font_size + 10)
    current_y = (height - total_h) // 2
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (width - w) // 2
        
        # Stroke
        for offset_x in range(-2, 3):
            for offset_y in range(-2, 3):
                draw.text((x + offset_x, current_y + offset_y), line, font=font, fill="black")
        
        draw.text((x, current_y), line, font=font, fill=color)
        current_y += font_size + 10
        
    temp_path = f"temp_overlay_{uuid.uuid4().hex[:6]}.png"
    img.save(temp_path)
    return temp_path

async def synthesize_voice(text, output_path="voice.mp3"):
    """
    Usa Edge-TTS (vozes neurais da Microsoft gratuitas) para gerar narração.
    """
    voice = "pt-BR-AntonioNeural" # Ou 'pt-BR-FranciscaNeural' para voz feminina
    print(f"Gerando voz para: '{text[:30]}...'")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    print(f"Voz gerada com sucesso em: {output_path}")
    return output_path

def apply_shadowban_avoidance(video_path, output_path):
    """
    Edita um vídeo fazendo espelhamento (flip) horizontal e alterando
    levemente a velocidade para criar um novo "Hash" digital de arquivo.
    """
    print(f"Processando vídeo de input: {video_path}")
    try:
        clip = VideoFileClip(video_path)
        
        # 1. Flip Horizontal (Muda a configuração dos pixels completamente)
        clip_flipped = clip.fx(vfx.mirror_x)
        
        # 2. Mudança suave na velocidade (1.02x para evitar flag do Tiktok)
        # O moviepy avisa que se o speed mudar, o aúdio também precisa acompanhar
        clip_speed = clip_flipped.fx(vfx.speedx, factor=1.02)
        
        # Renderiza e força compressão libx264 (padrão p/ redes sociais)
        clip_speed.write_videofile(output_path, codec="libx264", audio_codec="aac")
        
        # Limpeza pra evitar travamento de RAM
        clip_speed.close()
        clip.close()
        
        print(f"Vídeo único gerado e salvo em: {output_path}")
        return output_path
    
    except Exception as e:
        print(f"Erro ao processar vídeo pelo MoviePy: {e}")
        return None

def extract_frame_from_video(video_path, output_path=None, t=2.0):
    """
    Extrai um frame estático de um vídeo. Útil se o usuário quiser usar 
    uma foto do produto em vez de postar o Reels/vídeo inteiro.
    Por padrão arranca o frame do segundo 2 (t=2.0s) para evitar telas pretas iniciais.
    """
    if not video_path.lower().endswith(('.mp4', '.mov')):
        return None
        
    try:
        from moviepy.editor import VideoFileClip
        print(f"[EDITOR IA] Tentando extrair foto do vídeo no segundo {t}s...")
        clip = VideoFileClip(video_path)
        
        # Se o vídeo for super curto (menos que 2s), pega a exata metade dele
        if clip.duration < t:
            t = clip.duration / 2.0
            
        if not output_path:
            output_path = video_path.rsplit('.', 1)[0] + f"_thumb.jpg"
            
        clip.save_frame(output_path, t=t)
        clip.close()
        
        print(f"[EDITOR IA] Foto gerada com sucesso e salva em: {output_path}")
        return output_path
    except Exception as e:
        print(f"[EDITOR IA] Falha ao extrair a foto capa: {e}")
        return None


if __name__ == "__main__":
    # Teste Rápido de Voz
    # Para rodar: python app/mineracao/editor_ia.py
    texto_exemplo = "Eu achei um fone com qualidade absurda e que sai praticamente de graça na shopee!"
    asyncio.run(synthesize_voice(texto_exemplo, "teste_voz.mp3"))
    print("Módulo de Edição e IA testados com mock!")
