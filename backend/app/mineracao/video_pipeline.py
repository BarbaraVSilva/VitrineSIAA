import os
import asyncio
import edge_tts
import random
import uuid
from moviepy.editor import (
    VideoFileClip, 
    AudioFileClip, 
    ImageClip, 
    CompositeVideoClip, 
    vfx,
    CompositeAudioClip
)
from app.core.firebase_sync import firebase_sync
from app.mineracao.editor_ia import create_text_overlay

async def generate_tts_audio(text: str, output_path: str, voice: str = "pt-BR-AntonioNeural"):
    """Gera áudio via Microsoft Edge TTS (100% gratuito)."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_video_variant(base_video_path: str, hook: dict, variant_index: int, output_dir: str, task_id: str = None):
    """
    Mistura um vídeo base com o áudio TTS gerado a partir do Hook e música de fundo.
    Cria uma legenda central usando Pillow.
    """
    os.makedirs(output_dir, exist_ok=True)
    out_video = os.path.join(output_dir, f"variant_{variant_index}.mp4")
    out_audio_tts = os.path.join(output_dir, f"temp_tts_{variant_index}.mp3")
    
    if task_id:
        firebase_sync.update_processing_status(task_id, f"Gerando Áudio ({variant_index}/5)", 10 + (idx * 15))

    # 1. Gerar Voz Neural
    full_text = f"{hook['hook_text']} {hook['call_to_action']}"
    asyncio.run(generate_tts_audio(full_text, out_audio_tts))
    
    video_clip = None
    tts_clip = None
    bg_music_clip = None
    final_clip = None
    overlay_path = None
    
    try:
        # 2. Carregar Clippings
        video_clip = VideoFileClip(base_video_path).without_audio()
        tts_clip = AudioFileClip(out_audio_tts)
        
        # 3. Música de Fundo (opcional)
        bg_music_dir = os.path.join("media", "bg_music")
        if os.path.exists(bg_music_dir) and os.listdir(bg_music_dir):
            musics = [os.path.join(bg_music_dir, f) for f in os.listdir(bg_music_dir) if f.endswith(".mp3")]
            if musics:
                chosen_music = random.choice(musics)
                bg_music_clip = AudioFileClip(chosen_music).volumex(0.15) # Baixo volume
                bg_music_clip = bg_music_clip.set_duration(tts_clip.duration)
        
        # 4. Mix de Áudio
        if bg_music_clip:
            mixed_audio = CompositeAudioClip([tts_clip, bg_music_clip])
        else:
            mixed_audio = tts_clip
            
        # 5. Ajustar duração do vídeo
        if video_clip.duration < tts_clip.duration:
            video_clip = video_clip.fx(vfx.loop, duration=tts_clip.duration)
        else:
            video_clip = video_clip.subclip(0, tts_clip.duration)
            
        video_clip = video_clip.set_audio(mixed_audio)
        
        # 6. Adicionar Legenda (Pillow Fallback)
        overlay_text = f"{hook['angle'].upper()}\n{hook['hook_text'].split('.')[0]}"
        overlay_path = create_text_overlay(overlay_text, width=video_clip.w, height=video_clip.h)
        
        txt_clip = ImageClip(overlay_path).set_duration(video_clip.duration).set_position('center')
        
        final_clip = CompositeVideoClip([video_clip, txt_clip])
        
        # 7. Renderizar
        if task_id:
            firebase_sync.update_processing_status(task_id, f"Renderizando ({variant_index}/5)", 15 + (variant_index * 15))
            
        final_clip.write_videofile(
            out_video, codec="libx264", audio_codec="aac", 
            fps=24, preset="ultrafast", logger=None
        )
        print(f"✅ Variante {variant_index} renderizada: {out_video}")
        
    except Exception as e:
        print(f"[ERRO PIPELINE VÍDEO] {e}")
        if task_id:
            firebase_sync.update_processing_status(task_id, f"Erro: {str(e)}", 0, status="failed")
    finally:
        if video_clip: video_clip.close()
        if tts_clip: tts_clip.close()
        if bg_music_clip: bg_music_clip.close()
        if final_clip: final_clip.close()
        
        for p in [out_audio_tts, overlay_path]:
            if p and os.path.exists(p):
                try: os.remove(p)
                except: pass

def run_5_videos_pipeline(base_video_path: str, product_name: str, product_desc: str, price: str, product_id: int, task_id: str = None):
    """Orquestra a estratégia de 5 vídeos/dia para o produto."""
    from app.mineracao.hook_generator import generate_video_variant_hooks

    if task_id:
        firebase_sync.update_processing_status(task_id, "Gerando Roteiros IA", 5)

    hooks = generate_video_variant_hooks(product_name, product_desc, price)
    output_dir = os.path.join("vitrine", "videos_bulk", f"prod_{product_id}")
    
    for idx, hook in enumerate(hooks):
        create_video_variant(base_video_path, hook, idx + 1, output_dir, task_id)
        
    if task_id:
        firebase_sync.update_processing_status(task_id, "Concluído", 100, status="completed")
        
    return hooks
