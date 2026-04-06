import os
import asyncio
import edge_tts
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, vfx

async def generate_tts_audio(text: str, output_path: str, voice: str = "pt-BR-AntonioNeural"):
    """Gera áudio via Microsoft Edge TTS (100% gratuito)."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def create_video_variant(base_video_path: str, hook: dict, variant_index: int, output_dir: str):
    """
    Mistura um vídeo base com o áudio TTS gerado a partir do Hook.
    Cria uma legenda central simples se possível.
    """
    os.makedirs(output_dir, exist_ok=True)
    out_video = os.path.join(output_dir, f"variant_{variant_index}.mp4")
    out_audio = os.path.join(output_dir, f"temp_audio_{variant_index}.mp3")
    
    # 1. Gerar Voz Neural
    full_text = f"{hook['hook_text']} {hook['call_to_action']}"
    asyncio.run(generate_tts_audio(full_text, out_audio))
    
    video_clip = None
    tts_clip = None
    final_clip = None
    
    # 2. MoviePy Pipeline
    try:
        video_clip = VideoFileClip(base_video_path).without_audio()
        tts_clip = AudioFileClip(out_audio)
        
        # Loop do vídeo se for menor que a voz, ou corta
        if video_clip.duration < tts_clip.duration:
            # Em versões novas do moviepy .loop é seguro, em antigas iteramos subclips
            video_clip = video_clip.fx(vfx.loop, duration=tts_clip.duration)
        else:
            video_clip = video_clip.subclip(0, tts_clip.duration)
            
        video_clip = video_clip.set_audio(tts_clip)
        
        # Tentativa de Legenda (Requer ImageMagick no Windows)
        try:
            txt = f"{hook['angle'].upper()}\\n{hook['hook_text'].split('.')[0]}"
            txt_clip = TextClip(txt, fontsize=70, color='yellow', stroke_color='black', stroke_width=2, font='Arial-Bold')
            txt_clip = txt_clip.set_position(('center', 'center')).set_duration(video_clip.duration)
            final_clip = CompositeVideoClip([video_clip, txt_clip])
        except Exception as e:
            print(f"[AVISO] Não foi possível injetar a legenda via ImageMagick: {e}. Usando vídeo s/ legenda fixa.")
            final_clip = video_clip
            
        final_clip.write_videofile(
            out_video, codec="libx264", audio_codec="aac", 
            fps=24, preset="ultrafast", logger=None
        )
        print(f"✅ Variante {variant_index} ({hook['angle']}) renderizada com sucesso: {out_video}")
    except Exception as e:
        print(f"[ERRO PIPELINE VÍDEO] {e}")
    finally:
        # Fechar recursos do sistema para evitar lock de arquivos
        if video_clip: video_clip.close()
        if tts_clip: tts_clip.close()
        if final_clip: final_clip.close()
        
        if os.path.exists(out_audio):
            try:
                os.remove(out_audio)
            except:
                pass

def run_5_videos_pipeline(base_video_path: str, product_name: str, product_desc: str, price: str, product_id: int):
    """Orquestra a estratégia de 5 vídeos/dia para o produto."""
    from app.mineracao.hook_generator import generate_video_variant_hooks

    print(f"\n🔄 Iniciando Fábrica de Hooks (5 Variantes) para [{product_name}]...")
    hooks = generate_video_variant_hooks(product_name, product_desc, price)
    
    output_dir = os.path.join("vitrine", "videos_bulk", f"prod_{product_id}")
    
    for idx, hook in enumerate(hooks):
        create_video_variant(base_video_path, hook, idx + 1, output_dir)
        
    print(f"🎉 Pipeline Finalizado! 5 vídeos empacotados em: {output_dir}")
    return hooks
    
if __name__ == "__main__":
    # Teste unitário manual
    import urllib.request
    
    test_video = "test_base.mp4"
    if not os.path.exists(test_video):
        print("Baixando um vídeo de teste para verificar a pipeline...")
        urllib.request.urlretrieve("http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", test_video)
        
    run_5_videos_pipeline(test_video, "Fone Bluetooth XYZ", "Melhor qualidade sonora", "R$ 49,90", 999)
