import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime

class FirebaseSync:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseSync, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        try:
            # Caminho para o config no diretório do servidor
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "server", "firebase-applet-config.json")
            with open(config_path, "r") as f:
                config = json.load(f)
            
            if not firebase_admin._apps:
                firebase_admin.initialize_app(options={'projectId': config['projectId']})
            
            self.db = firestore.client()
            self._initialized = True
            print(f"[FirebaseSync] Conectado ao Firebase: {config['projectId']}")
        except Exception as e:
            print(f"[FirebaseSync] Erro ao inicializar: {e}")
            self.db = None

    def push_mining_item(self, item_data: dict):
        """Envia um item minerado para a coleção 'mining'."""
        if not self.db: return None
        try:
            doc_ref = self.db.collection("mining").document()
            data = {
                "title": item_data.get("titulo", "Sem título"),
                "price": item_data.get("preco", "R$ 0,00"),
                "image": item_data.get("image_url", "https://picsum.photos/400/400"),
                "source": item_data.get("source", "Python Engine"),
                "rawLink": item_data.get("link_original", ""),
                "status": "pending",
                "timestamp": datetime.now().isoformat()
            }
            doc_ref.set(data)
            return doc_ref.id
        except Exception as e:
            print(f"[FirebaseSync] Erro ao enviar item: {e}")
            return None

    def update_analytics(self, clicks=None, conversions=None, revenue=None):
        if not self.db: return
        try:
            doc_ref = self.db.collection("analytics").document("global")
            updates = {}
            if clicks is not None: updates["clicks"] = firestore.Increment(clicks)
            if conversions is not None: updates["conversions"] = firestore.Increment(conversions)
            if revenue is not None: updates["revenue"] = firestore.Increment(revenue)
            if updates: doc_ref.update(updates)
        except Exception as e:
            print(f"[FirebaseSync] Erro ao atualizar analytics: {e}")

    def update_processing_status(self, task_id: str, step: str, progress: int, status: str = "processing"):
        """Atualiza o progresso de uma tarefa de edição/processamento."""
        if not self.db: return
        try:
            doc_ref = self.db.collection("processing").document(task_id)
            doc_ref.set({
                "id": task_id,
                "step": step,
                "progress": progress,
                "status": status,
                "updated_at": datetime.now().isoformat()
            }, merge=True)
        except Exception as e:
            print(f"[FirebaseSync] Erro ao atualizar processamento: {e}")

    def update_engine_status(self, component: str, status: str):
        if not self.db: return
        try:
            doc_ref = self.db.collection("status").document("engine")
            doc_ref.set({
                component: {
                    "status": status,
                    "last_seen": datetime.now().isoformat()
                }
            }, merge=True)
        except Exception as e:
            print(f"[FirebaseSync] Erro ao atualizar status: {e}")

    def heartbeat(self):
        self.update_engine_status("main", "ATIVO")

firebase_sync = FirebaseSync()
