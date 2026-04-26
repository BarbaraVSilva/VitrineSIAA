import os
import sys
# Adiciona o diretório raiz ao path para encontrar o módulo 'app'
sys.path.append(os.path.abspath(os.getcwd()))

from app.core.firebase_sync import firebase_sync

test_item = {
    "titulo": "Produto de Teste SIAA",
    "preco": "R$ 99,90",
    "image_url": "https://picsum.photos/seed/test/400/400",
    "source": "Teste Unitário",
    "link_original": "https://shopee.com.br/teste"
}

print("Enviando item de teste para Firebase...")
item_id = firebase_sync.push_mining_item(test_item)

if item_id:
    print(f"Sucesso! Item criado com ID: {item_id}")
else:
    print("Falha ao enviar item.")
