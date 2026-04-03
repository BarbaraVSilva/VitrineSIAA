import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from app.core.logger import log_event

load_dotenv()

def generate_hooks(product_desc: str) -> dict:
    """
    Usa o Google Gemini para gerar 3 categorias de copy para um produto da Shopee.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log_event("GEMINI_API_KEY não definida no .env. Recaindo para ganchos genéricos.", component="HookGenerator", status="WARNING")
        return _fallback_hooks(product_desc)
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
Você é um Copywriter Especialista em Marketing de Afiliados de alta conversão.
Sua tarefa é ler sobre este achadinho da Shopee e gerar três roteiros/legendas distintos, otimizados para plataformas específicas.

- Dados capturados do produto:
{product_desc}

Gere APENAS um JSON com 3 chaves. Sem formatações markdown envolta:
{{
  "instagram_reels": "Legenda focada em Desejo e Estética (Lifestyle, use emojis elegantes, foque no quão lindo e útil é). Termine com 'Link na bio ou comenta QUERO'. Inclua 3 ashtags de nicho.",
  "tiktok": "Legenda e roteiro de som (VO) focado em Curiosidade e 'Life Hack' (Rápido, chocante, direto). Ex: 'A Shopee enlouqueceu com isso...'. Termine com 'Link no perfil'.",
  "whatsapp": "Texto curto para grupos focado na Urgência, Preço e Oferta Relâmpago. Formatação clara, use emojis dinâmicos (🚨, 🔥). Termine com chamada para o link."
}}
"""

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Limpa possíveis blocos de código markdown que o Gemini possa retornar
        if content.startswith("```json"):
            content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif content.startswith("```"):
            content = content.replace("```", "", 2).strip()
            
        hooks = json.loads(content)
        
        return hooks
        
    except Exception as e:
        log_event(f"Erro ao gerar ganchos com Gemini: {str(e)}", component="HookGenerator", event="IA_GENERATE", status="ERROR", level=40)
        return _fallback_hooks(product_desc)

def _fallback_hooks(product_desc: str) -> dict:
    return {
        "instagram_reels": f"✨ Achadinho perfeito que vai transformar sua rotina!\n\n{product_desc[:50]}...\n\n👉 Comente 'QUERO' que te envio o link no direct! #achadinhos #shopee #lifestyle",
        "tiktok": f"O lifehack da Shopee que ninguém te conta! 🤯\n\nOlha só que utilidade incrível esse produto. Corre no link do meu perfil antes que esgote!",
        "whatsapp": f"🚨 OFERTA RELÂMPAGO 🚨\n\nImperdível! {product_desc[:60]}...\n⏳ O estoque tá voando e é preço de custo!\n\n🛒 Compre aqui:"
    }

if __name__ == "__main__":
    # Teste rápido
    res = generate_hooks("Projetor de galáxia com controle remoto e 8 modos de nebulosa")
    print(json.dumps(res, indent=4, ensure_ascii=False))
