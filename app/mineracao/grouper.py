import os
import json
import uuid
import datetime
from app.core.database import get_connection
from app.core.logger import log_event
import google.generativeai as genai

def group_achados_with_ai():
    """
    Busca itens PENDING ou APPROVED que não possuem grupo_id e os agrupa por afinidade temática usando Gemini.
    """
    conn = get_connection()
    c = conn.cursor()
    
    # Pegar itens que ainda não foram agrupados
    c.execute("""
        SELECT id, texto_original, categoria 
        FROM achados 
        WHERE (grupo_id IS NULL OR grupo_id = '') 
        AND status IN ('PENDING', 'APPROVED')
        LIMIT 20
    """)
    rows = c.fetchall()
    
    if len(rows) < 3:
        # Precisa de pelo menos 3 itens para valer um agrupamento (carrossel)
        conn.close()
        return False

    items_data = []
    for r in rows:
        items_data.append({
            "id": r[0],
            "text": r[1][:200], # Limitar texto para o prompt
            "category": r[2]
        })

    # Prompt para o Gemini
    prompt = f"""
    Como um assistente de marketing de afiliados, agrupe estes itens em 3 a 5 "Coleções Temáticas" ou "Carrosséis" virais.
    Itens: {json.dumps(items_data, ensure_ascii=False)}
    
    Retorne APENAS um JSON no formato:
    [
      {{
        "tema": "Nome Criativo do Grupo (ex: Cozinha Moderna)",
        "item_ids": [1, 5, 8]
      }},
      ...
    ]
    Tente agrupar pelo menos 3 itens por tema. Se algum item não couber em nenhum grupo temático forte, deixe-o de fora.
    """
    
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        model = genai.GenerativeModel('gemini-1.5-flash')
        resp = model.generate_content(prompt)
        raw_text = resp.text.strip().removeprefix("```json").removesuffix("```").strip()
        groups = json.loads(raw_text)
        
        applied_count = 0
        for g in groups:
            g_id = f"G-{uuid.uuid4().hex[:6].upper()}"
            tema = g["tema"]
            ids = g["item_ids"]
            
            if len(ids) >= 2:
                for a_id in ids:
                    c.execute("UPDATE achados SET grupo_id = ?, tema_grupo = ? WHERE id = ?", (g_id, tema, a_id))
                    applied_count += 1
        
        conn.commit()
        log_event(f"Agrupamento Realizado: {len(groups)} grupos criados, {applied_count} itens processados.", component="GrouperAI", status="SUCCESS")
        conn.close()
        return True
        
    except Exception as e:
        log_event(f"Falha no Agrupamento AI: {str(e)}", component="GrouperAI", status="ERROR")
        conn.close()
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    group_achados_with_ai()
