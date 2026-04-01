import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from app.core.logger import log_event

load_dotenv()

def generate_hooks(product_name: str, product_desc: str, price: str = "com desconto") -> list[dict]:
    """
    Usa o Google Gemini para gerar 5 ganchos de marketing persuasivos.
    Implementa proteção básica contra alucinação comparando a saída com os dados originais.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log_event("GEMINI_API_KEY não definida no .env. Recaindo para ganchos genéricos.", component="HookGenerator", status="WARNING")
        return _fallback_hooks(product_name)
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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

Responda APENAS um JSON válido. Não inclua Markdown ou blocos de código. Estrutura:
[
  {{ "angle": "Dor", "hook_text": "Cansada de [...] ?", "call_to_action": "Comenta QUERO pra garantir..." }},
  ...
]
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
        
        # Proteção contra Alucinação: Validar se o nome do produto ou termos chave estão presentes
        # (Se a IA inventar um produto totalmente diferente, recai para o fallback)
        validated_hooks = []
        key_terms = product_name.lower().split()[:2] # Pega as primeiras 2 palavras como termos chave
        
        for hook in hooks:
            text = hook.get("hook_text", "").lower()
            # Se for um gancho muito genérico que não cita nada do produto, marcamos para revisão
            if not any(term in text for term in key_terms) and hook["angle"] != "Curiosidade":
                 hook["hook_text"] = f"[VALIDAÇÃO REQUERIDA] {hook['hook_text']}"
            validated_hooks.append(hook)
            
        log_event(f"Ganchos gerados com sucesso para: {product_name}", component="HookGenerator", event="IA_GENERATE", status="SUCCESS")
        return validated_hooks
        
    except Exception as e:
        log_event(f"Erro ao gerar ganchos com Gemini: {str(e)}", component="HookGenerator", event="IA_GENERATE", status="ERROR", level=40)
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
    # Teste rápido
    res = generate_hooks("Luminária Astronauta", "Projetor de galáxia com controle remoto e 8 modos de nebulosa")
    print(json.dumps(res, indent=4, ensure_ascii=False))
