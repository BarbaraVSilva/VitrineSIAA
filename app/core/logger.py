import logging
import json
import os
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "component": getattr(record, "component", "Geral"),
            "message": record.getMessage(),
            "event": getattr(record, "event", "LOG_EVENT"),
            "status": getattr(record, "status", "INFO")
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger(name="SIAA-2026"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Previne handlers duplicados
    if not logger.handlers:
        # Handler para Console (JSON)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
        # Handler para Arquivo (JSON) - Para o Streamlit Monitor
        log_dir = os.path.join(os.getcwd(), "logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = logging.FileHandler(os.path.join(log_dir, "siaa_structured.json"))
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
        
    return logger

# Instância padrão
logger = setup_logger()

def log_event(message, component="Geral", event="LOG_EVENT", status="INFO", level=logging.INFO):
    """
    Função utilitária para registrar um evento estruturado.
    Ex: log_event("Postagem completa", component="InstagramBot", event="POST_API_META", status="SUCCESS")
    """
    extra = {"component": component, "event": event, "status": status}
    logger.log(level, message, extra=extra)

if __name__ == "__main__":
    log_event("Teste de Log Estruturado", component="NOC-Monitoring", event="SISTEMA_START", status="SUCCESS")
