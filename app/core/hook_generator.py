import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_hooks(produto_descricao: str) -> list[str]:
    """
    Gera 3 opções de ganchos (hooks) magnéticos para um produto usando a OpenAI API.
    Retorna uma lista de strings.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return [
            "O que a Shopee não quer que você saiba...",
            "Achei o segredo para facilitar sua vida na Shopee!",
            "Pare tudo o que está fazendo e veja esse achadinho!"
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
            max_tokens=150
        )
        conteudo = response.choices[0].message.content.strip()
        # Dividir por traço ou quebra de linha
        linhas = [l.replace("-", "").strip() for l in conteudo.split("\n") if l.strip()]
        # Retorna até 3
        return linhas[:3] if len(linhas) >= 3 else (linhas + ["Achadinho imperdível na Shopee!"] * 3)[:3]
    except Exception as e:
        print(f"[HOOK GENERATOR ERRO] {e}")
        return [
            "O que a Shopee não quer que você saiba...",
            "Achei o segredo para facilitar sua vida na Shopee!",
            "Pare tudo o que está fazendo e veja esse achadinho!"
        ]

if __name__ == "__main__":
    # Teste
    print("Testando ganchos:")
    hooks = generate_hooks("Mini Processador de Alimentos Elétrico USB Portátil")
    for idx, h in enumerate(hooks, 1):
        print(f"{idx}. {h}")
