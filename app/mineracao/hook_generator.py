import os
import json
from typing import Any

import google.generativeai as genai
from dotenv import load_dotenv
from openai import OpenAI

from app.core.logger import log_event

load_dotenv()

def generate_hooks(product_desc: str, style: str = "Padrao") -> dict:
    """
    Usa o Google Gemini para gerar ganchos (copies) específicos com base no estilo solicitado.
    Estilos: "Flash Sale", "Lancamento", "Escassez", "Padrao"
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log_event("GEMINI_API_KEY não definida no .env. Recaindo para ganchos genéricos.", component="HookGenerator", status="WARNING")
        return _fallback_hooks(product_desc)
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
Você é um Copywriter Especialista em Marketing de Afiliados de alta conversão.
Sua tarefa é gerar três roteiros/legendas otimizados para converter esse achadinho da Shopee.

- Estratégia solicitada: {style}
- Dados capturados do produto:
{product_desc}

Diretrizes Baseadas em Gatilhos Mentais:
1. "Escassez": Foque no tempo limitado e poucas unidades. Use 'Últimas 5 unidades', 'O estoque já está acabando'.
2. "Flash Sale": Foque na oportunidade única de preço baixo. Use 'Preço de custo', 'Menor preço do ano'.
3. "Lancamento": Foque na novidade e exclusividade. Use 'Acabou de chegar', 'Ninguém tem nada igual'.

Gere APENAS um JSON com 3 chaves (sem blocos markdown):
{{
  "instagram_reels": "Legenda focada em Desejo e Estética.",
  "tiktok": "Roteiro e legenda focado em Curiosidade e viralismo.",
  "whatsapp": "Texto curto para grupos focado em Clique e Venda Imediata."
}}
"""

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        if "```json" in content:
            content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif "```" in content:
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


def generate_openai_hook_strings(produto_descricao: str) -> list[str]:
    """
    Gera 3 ganchos curtos via OpenAI (legado opcional).
    Exposto aqui para evitar módulo duplicado em app.core.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return [
            "O que a Shopee não quer que você saiba...",
            "Achei o segredo para facilitar sua vida na Shopee!",
            "Pare tudo o que está fazendo e veja esse achadinho!",
        ]

    client = OpenAI(api_key=api_key)
    prompt = (
        f"Gere 3 ganchos (hooks) curtos, magnéticos e altamente virais para as redes sociais "
        f"(Instagram/TikTok) baseados nesta descrição de produto: '{produto_descricao}'.\n"
        f"Os ganchos devem focar em despertar curiosidade absurda e reter a pessoa nos "
        f"primeiros 3 segundos do vídeo. Responda APENAS com as 3 frases, cada uma em uma linha, separadas por '-', sem numeração."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=150,
        )
        conteudo = response.choices[0].message.content.strip()
        linhas = [l.replace("-", "").strip() for l in conteudo.split("\n") if l.strip()]
        return linhas[:3] if len(linhas) >= 3 else (linhas + ["Achadinho imperdível na Shopee!"] * 3)[:3]
    except Exception as e:
        log_event(f"OpenAI hook error: {e}", component="HookGenerator", event="OPENAI_HOOK", status="ERROR", level=40)
        return [
            "O que a Shopee não quer que você saiba...",
            "Achei o segredo para facilitar sua vida na Shopee!",
            "Pare tudo o que está fazendo e veja esse achadinho!",
        ]


def _normalize_video_hook(raw: dict[str, Any]) -> dict[str, str]:
    angle = str(raw.get("angle") or raw.get("angulo") or "Destaque").strip()
    hook_text = str(raw.get("hook_text") or raw.get("texto") or "").strip()
    cta = str(raw.get("call_to_action") or raw.get("cta") or "Corre no link da bio.").strip()
    if not hook_text:
        hook_text = f"{angle}: oferta imperdível na Shopee."
    return {"angle": angle, "hook_text": hook_text, "call_to_action": cta}


def _fallback_video_variant_hooks(product_name: str, product_desc: str, price: str) -> list[dict[str, str]]:
    bloco = f"{product_name}. {product_desc} {price}"
    presets = [
        ("Urgência", f"Estoque acabando: {product_name[:60]}. {price}", "Garante o teu antes que suma do ar."),
        ("Preço", f"{price} num {product_name[:50]} assim? Só hoje.", "Clica e confere o link."),
        ("Prova social", f"Todo mundo tá falando desse {product_name[:40]}.", "Não fica de fora dessa."),
        ("Curiosidade", f"O detalhe que ninguém te contou sobre {product_name[:40]}...", "Assiste até o final e pega o link."),
        ("Oferta relâmpago", f"Achadinho {price} que vale cada centavo.", "Corre que é por tempo limitado."),
    ]
    return [{"angle": a, "hook_text": h, "call_to_action": c} for a, h, c in presets]


def generate_video_variant_hooks(product_name: str, product_desc: str, price: str) -> list[dict[str, str]]:
    """
    Cinco variantes para `video_pipeline.create_video_variant` (angle, hook_text, call_to_action).
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _fallback_video_variant_hooks(product_name, product_desc, price)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
Você é copywriter de vídeos curtos de afiliados Shopee (Brasil).
Produto: {product_name}
Descrição: {product_desc}
Preço: {price}

Gere EXATAMENTE 5 variações de gancho para narração (TTS), cada uma com um ângulo de venda diferente.
Responda APENAS com um JSON array de 5 objetos, sem markdown, no formato:
[
  {{"angle": "nome curto do ângulo", "hook_text": "texto falado em 2 a 4 frases", "call_to_action": "frase curta final pedindo clique"}},
  ...
]
"""
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        if "```json" in content:
            content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif "```" in content:
            content = content.replace("```", "", 2).strip()
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("Resposta não é lista")
        hooks = [_normalize_video_hook(x) for x in data[:5]]
        pad = f"{product_name}. {product_desc}"[:200]
        while len(hooks) < 5:
            hooks.append(
                _normalize_video_hook(
                    {"angle": f"Extra {len(hooks) + 1}", "hook_text": pad, "call_to_action": "Confere o link."}
                )
            )
        return hooks[:5]
    except Exception as e:
        log_event(f"Gemini vídeo hooks: {e}", component="HookGenerator", event="VIDEO_HOOKS", status="WARNING", level=30)
        return _fallback_video_variant_hooks(product_name, product_desc, price)


if __name__ == "__main__":
    # Teste rápido
    res = generate_hooks("Projetor de galáxia com controle remoto e 8 modos de nebulosa")
    print(json.dumps(res, indent=4, ensure_ascii=False))
