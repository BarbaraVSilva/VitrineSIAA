# STAGE 1: Builder
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

# Configura o APT para retentar downloads em caso de falha na rede (Resiliência 2026)
RUN printf '%s\n' \
    'Acquire::Retries "10";' \
    'Acquire::https::Timeout "240";' \
    'Acquire::http::Timeout "240";' \
    > /etc/apt/apt.conf.d/99-retries.conf

# Patch de segurança e dependências de build (Consolidado)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Evita arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# STAGE 2: Runtime
FROM python:3.12-slim-bookworm AS runtime

# Cria um usuário não-root para rodar a aplicação (Segurança)
RUN useradd -m siaa_user
WORKDIR /app

# Configura o APT para retentar downloads em caso de falha na rede no runtime
RUN printf '%s\n' \
    'Acquire::Retries "10";' \
    'Acquire::https::Timeout "240";' \
    'Acquire::http::Timeout "240";' \
    > /etc/apt/apt.conf.d/99-retries.conf

# Patch de segurança e libs runtime finais (Consolidado)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia dependências instaladas do builder
COPY --from=builder /root/.local /home/siaa_user/.local
ENV PATH=/home/siaa_user/.local/bin:$PATH

# Copia o código fonte e ajusta permissões
COPY --chown=siaa_user:siaa_user . .

# Garante que as pastas de serviço existam
RUN mkdir -p data logs downloads && chown -R siaa_user:siaa_user data logs downloads

# Alterna para o usuário não-root
USER siaa_user

# Expor portas: 6000 (FastAPI), 8501 (Streamlit)
EXPOSE 6000 8501

# Definir volume para persistência do banco SQLite
VOLUME ["/app/data"]
ENV DB_PATH=/app/data/db_siaa.sqlite

# Comando padrão
CMD ["python", "main.py"]
