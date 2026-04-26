import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from app.core.logger import log_event

load_dotenv()

def check_compliance(product_text: str) -> dict:
    """
    Usa o Google Gemini para validar o texto de um produto contra as 
    fortes diretrizes de Produtos Proibidos e Restritos da Shopee Video.
    Retorna um dict: {"is_safe": bool, "reason": str}
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log_event("GEMINI_API_KEY não definida. Compliance setado como APPROVED por padrão.", component="ComplianceChecker", status="WARNING")
        return {"is_safe": True, "reason": "Validação desativada (Sem chave API)"}
        
    genai.configure(api_key=api_key)
    # Recomendado o flash por ser rápido e barato
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
Você é um Auditor de Compliance e Risco da Shopee Video. 
Sua tarefa é analisar o seguinte produto/texto e determinar rigidamente se ele viola a Política de Produtos Proibidos e Restritos.

PRODUTO A SER ANALISADO:
"{product_text}"

LISTA RESUMIDA DE PROIBIÇÕES DA SHOPEE (REJEITE SE ENCAIXAR NESTAS CATEGORIAS):
1. Armas e Lâminas: Armas de fogo, peças, estilingues, nunchakus, armas de brinquedo (Nerf) se parecerem reais, lâminas maiores que 30cm (12 polegadas), tasers, spray de pimenta.
2. Saúde e Medicamentos: Qualquer remédio (com ou sem receita), minoxidil, suplementos para emagrecimento, anabolizantes, clareadores dentais >3%, agulhas, cosméticos injetáveis, testes de saúde (HIV, Covid), aparelhos auditivos. Milagres ou promessas exageradas ("cura tudo").
3. Adulto e Sexual: Estimulantes, brinquedos sexuais, pornografia, preservativos sem embalagem.
4. Tabaco e Drogas: Cigarros, Vapes (Cigarro eletrônico), acessórios para fumo (seda, piteira, cachimbo), drogas ilícitas e plantas psicoativas.
5. Eletrônicos Proibidos e Serviços Digitais: Câmeras de espionagem, gravadores de voz espiões, modems piratas, IPTV, CS/IKS, software pirata, e-books, arquivos digitais, ingressos, moedas falsas, dinheiro vivo.
6. Direção e Segurança Veicular: Emuladores de emissão de gás, peças usadas de segurança (airbags, freios), equipamentos para furtar carros, óleos automotivos sem registro ANP.
7. Alimentos e Animais: Laticínios não pasteurizados, alimentos frescos, caseiros. Animais vivos, itens para tortura de animais, medicamentos injetáveis para animais.
8. Explosivos e Inflamáveis: Extintores, maçaricos, fogos de artifício.

Você DEVE retornar APENAS um JSON válido, sem texto adicional ou marcação markdown.
Formato:
{{
  "is_safe": false,
  "reason": "Motivo resumido e objetivo pelo qual o produto foi rejeitado segundo as políticas acima. Se for is_safe=true, deixe a string vazia."
}}
"""

    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # Limpeza de formatação JSON se o Gemini tentar retornar bloco de código
        if content.startswith("```json"):
            content = content.replace("```json", "", 1).replace("```", "", 1).strip()
        elif content.startswith("```"):
            content = content.replace("```", "", 2).strip()
            
        result = json.loads(content)
        
        # Valida as chaves de segurança do JSON
        is_safe = result.get("is_safe", True)
        reason = result.get("reason", "")
        
        status_text = "APROVADO" if is_safe else "REJEITADO"
        log_event(f"Compliance Check: {status_text} | {reason}", component="ComplianceChecker", event="COMPLIANCE_CHECK", status="SUCCESS")
        
        return {
            "is_safe": bool(is_safe),
            "reason": str(reason)
        }
        
    except Exception as e:
        log_event(f"Erro ao verificar compliance com Gemini: {str(e)}", component="ComplianceChecker", event="COMPLIANCE_ERROR", status="ERROR", level=40)
        # Em caso de falha da IA, consideramos safe para não travar a pipeline, mas logamos fortemente
        return {"is_safe": True, "reason": "Erro na IA - Aprovado automaticamente"}

if __name__ == "__main__":
    # Teste rápido
    teste_arma = "Compre agora esse VAPE descartável sabor melancia 10000 puffs shope.ee/teste"
    res1 = check_compliance(teste_arma)
    print("Vape: ", res1)

    teste_livro = "E-book digital como emagrecer em 30 dias PDF s.shopee.com.br/123"
    res2 = check_compliance(teste_livro)
    print("Ebook: ", res2)

    teste_ok = "Secador de cabelo ultra mega max s.shop/123"
    res3 = check_compliance(teste_ok)
    print("Secador: ", res3)
