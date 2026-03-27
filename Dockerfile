# Usar uma imagem leve e estável do Python
FROM python:3.10-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências do sistema necessárias para algumas libs (como Pillow ou Selenium)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requisitos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código
COPY . .

# Expor portas padronizadas (6000 para Webhooks, 8501 para Streamlit)
EXPOSE 6000 8501

# O comando de inicialização padrão será o Streamlit, mas pode ser sobrescrito no compose
CMD ["streamlit", "run", "app/dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
