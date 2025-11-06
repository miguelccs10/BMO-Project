#!/bin/bash
# docker-entrypoint.sh
# Script de entrada para container Docker do BMO

set -e

echo "🤖 BMO Docker Container Starting..."
echo ""

# Verificar se config.yaml existe
if [ ! -f "config/config.yaml" ]; then
    echo "⚠️  config/config.yaml não encontrado!"
    echo "Criando a partir do template..."
    cp config.yaml.example config/config.yaml
fi

# Verificar se .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  .env não encontrado!"
    echo "Criando a partir do template..."
    cp .env.example .env
    echo ""
    echo "⚠️  ATENÇÃO: Configure as API keys no arquivo .env antes de usar!"
fi

# Verificar credenciais Google (se configurado para usar)
if grep -q 'engine: "google"' config/config.yaml 2>/dev/null; then
    if [ ! -f "credentials/google_adc_credentials.json" ]; then
        echo "⚠️  Google TTS configurado mas credenciais não encontradas"
        echo "Coloque google_adc_credentials.json em ./credentials/"
    fi
fi

echo ""
echo "✅ Configuração verificada"
echo ""

# Executar comando baseado no argumento
case "$1" in
    server)
        echo "🚀 Iniciando BMO Server (Web Interface)..."
        echo "Acesse: http://localhost:5000"
        echo ""
        exec python app/bmo_server.py
        ;;
    standalone)
        echo "🎤 Iniciando BMO Standalone (Wake-word detection)..."
        echo "⚠️  Nota: Requer acesso a dispositivos de áudio"
        echo ""
        exec python app/BMO.py
        ;;
    bash)
        echo "🐚 Iniciando shell interativo..."
        exec /bin/bash
        ;;
    *)
        echo "Uso: docker-entrypoint.sh [server|standalone|bash]"
        echo ""
        echo "Executando comando customizado: $@"
        exec "$@"
        ;;
esac
