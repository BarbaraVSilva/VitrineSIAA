import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_hooks(product_name: str, product_desc: str, price: str = "com desconto") -> list[dict]:
    """
    Given an affiliate product, generates 5 distinct marketing hooks 
    (Pain, Benefit, Price, Curiosity, FOMO).
    Returns a list of dictionaries with keys: angle, hook_text, call_to_action
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("[AVISO] OPENAI_API_KEY não definida. Usando ganchos genéricos.")
        return _fallback_hooks(product_name)
        
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
Você é um especialista em Marketing de Vídeos Curtos para TikTok, Reels e Shorts.
Seu objetivo é criar 5 roteiros/textos (voiceovers curtos de até 10 segundos) diferentes para vender o seguinte produto afiliado:
- Produto: {product_name}
- Descrição: {product_desc}
- Preço/Oferta: {price}

Quero exatamente 5 Ângulos:
1. Dor (Foque no problema que o produto resolve)
2. Benefício (Foque no que a vida da pessoa melhora)
3. Preço (Foque que está muito barato e compensa muito)
4. Curiosidade (Gere intriga sobre o funcionamento ou resultado)
5. FOMO (Medo de ficar de fora, urgência)

Responda SOMENTE em JSON válido com essa exata estrutura (mínimo de texto possível, direto e persuasivo):
[
  {{ "angle": "Dor", "hook_text": "Cansada de [...] ?", "call_to_action": "Comenta QUERO pra garantir..." }},
  ...
]
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        hooks = json.loads(content)
        return hooks
    except Exception as e:
        print(f"[ERRO AO GERAR GANCHOS IA] {e}")
        return _fallback_hooks(product_name)

def _fallback_hooks(product_name: str) -> list[dict]:
    return [
        {"angle": "Dor", "hook_text": f"Sabe aquele problema chato? Com o {product_name} você resolve.", "call_to_action": "Link no perfil!"},
        {"angle": "Benefício", "hook_text": f"A melhor coisa que já comprei para facilitar meu dia: {product_name}.", "call_to_action": "Comenta EU QUERO."},
        {"angle": "Preço", "hook_text": f"Achadinho super barato. O {product_name} tá quase de graça hoje.", "call_to_action": "Corra lá no link."},
        {"angle": "Curiosidade", "hook_text": f"O que será que tem dentro dessa caixa? É o famoso {product_name}! Superou as expectativas.", "call_to_action": "Descubra no link!"},
        {"angle": "FOMO", "hook_text": f"O {product_name} tá viralizando e o estoque tá quase no fim. Todo mundo tá amando.", "call_to_action": "Garanta o seu antes que acabe!"}
    ]

if __name__ == "__main__":
    print(json.dumps(generate_hooks("Organizador de Cabos Magnético", "Organizador feito de silicone magnético para grudar fios na mesa sem bagunça", "R$ 15,90"), indent=4, ensure_ascii=False))
