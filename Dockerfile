# Dockerfile
# BMO Voice Assistant - Docker Image
# Modo recomendado: Servidor Web (bmo_server.py)
# Para modo autônomo com microfone, execute diretamente no host

FROM python:3.11-slim

LABEL maintainer="BMO Project"
LABEL description="BMO Voice Assistant - Adventure Time inspired AI assistant"

# Evitar interação durante instalação
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pyaudio \
    ffmpeg \
    git \
    flac \
    libsndfile1 \
    alsa-utils \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar arquivos de requisitos primeiro (para cache)
COPY requirements/x86_64.txt /app/requirements/x86_64.txt

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/x86_64.txt

# Copiar o código da aplicação
COPY . /app/

# Criar diretórios necessários
RUN mkdir -p credentials custom_models/wake_word && \
    chmod +x requirements/*.sh

# Baixar modelos OpenWakeWord
RUN python config/setup_oww.py

# Criar usuário não-root para segurança
RUN useradd -m -u 1000 bmo && \
    chown -R bmo:bmo /app

USER bmo

# Expor porta do servidor web
EXPOSE 5000

# Variáveis de ambiente padrão (podem ser sobrescritas)
ENV PYTHONUNBUFFERED=1
ENV BMO_MODE=server

# Healthcheck para verificar se o servidor está rodando
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Script de entrada
COPY --chown=bmo:bmo docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Comando padrão: servidor web
CMD ["server"]
