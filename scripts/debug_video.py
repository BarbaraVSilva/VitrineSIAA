import sys
import os
import asyncio

# Adiciona raiz ao path
sys.path.append(os.getcwd())

from app.mineracao.video_pipeline import create_video_variant

async def test():
    # Procura por qualquer MP4 na pasta downloads para testar
    downloads = "downloads"
    test_v = None
    if os.path.exists(downloads):
        files = [f for f in os.listdir(downloads) if f.endswith('.mp4')]
        if files:
            test_v = os.path.join(downloads, files[0])
    
    if not test_v:
        print("Nenhum vídeo encontrado em /downloads para teste.")
        return

    hook_data = {
        "angle": "DEBUG TEST",
        "hook_text": "Este é um teste de renderização para diagnosticar erros.",
        "call_to_action": "Link na Bio"
    }
    
    output_dir = "media/debug_test"
    print(f"Iniciando teste com vídeo: {test_v}")
    
    try:
        res = create_video_variant(test_v, hook_data, 999, output_dir)
        if res:
            print(f"Sucesso! Vídeo gerado em: {res}")
        else:
            print("Falha: create_video_variant retornou None.")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
