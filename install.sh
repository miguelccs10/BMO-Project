#!/bin/bash

# Cores
GREEN='\039[0;32m'
BLUE='\039[0;34m'
YELLOW='\039[1;33m'
RED='\039[0;31m'
NC='\039[0m'

echo -e "${BLUE}=======================================${NC}"
echo -e "${BLUE}       BMO Multi-Device Installer      ${NC}"
echo -e "${BLUE}=======================================${NC}"
echo ""

echo -e "${YELLOW}Passo 1: Qual é o perfil do seu Hardware?${NC}"
echo "1) Máquina Fraca / PC Antigo (Usa Ollama, ultraleve na CPU/RAM)"
echo "2) Máquina Dedicada / PC Gamer (Usa AirLLM, suporte a placas de vídeo)"
read -p "Escolha (1 ou 2): " PROFILE_CHOICE

if [ "$PROFILE_CHOICE" == "1" ]; then
    PROVIDER="ollama"
elif [ "$PROFILE_CHOICE" == "2" ]; then
    PROVIDER="airllm"
else
    echo -e "${RED}Opção inválida.${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Passo 2: Qual o peso do modelo de IA?${NC}"
echo "1) Small (Modelos de 1.5B/1.8B - Muito rápido, respostas simples)"
echo "2) Medium (Modelos de 7B/8B - Equilibrado, ótimo raciocínio)"
echo "3) Large (Modelos de 14B/27B - Para PCs potentes, alto raciocínio)"
read -p "Escolha (1, 2 ou 3): " WEIGHT_CHOICE

if [ "$WEIGHT_CHOICE" == "1" ]; then
    WEIGHT="small"
elif [ "$WEIGHT_CHOICE" == "2" ]; then
    WEIGHT="medium"
elif [ "$WEIGHT_CHOICE" == "3" ]; then
    WEIGHT="large"
else
    echo -e "${RED}Opção inválida.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Iniciando configuração do Ambiente Virtual...${NC}"

if [ ! -d "venv" ]; then
    echo "Criando virtualenv (venv)..."
    python3 -m venv venv
fi

# Ativa o venv
source venv/bin/activate

echo -e "${GREEN}Instalando dependências Base...${NC}"
pip install -r requirements/base.txt

echo -e "${GREEN}Instalando dependências específicas do perfil ($PROVIDER)...${NC}"
pip install -r requirements/${PROVIDER}.txt

# Se for Ollama, checar instalação e baixar modelo
if [ "$PROVIDER" == "ollama" ]; then
    echo -e "${YELLOW}Verificando instalação do Ollama...${NC}"
    if ! command -v ollama &> /dev/null; then
        echo -e "${YELLOW}Ollama não encontrado. Instalando Ollama Oficial...${NC}"
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo -e "${GREEN}Ollama já está instalado!${NC}"
    fi
    
    # Inicia o serviço do ollama em background caso não esteja rodando
    systemctl is-active --quiet ollama || sudo systemctl start ollama 2>/dev/null || (ollama serve >/dev/null 2>&1 &)
    
    # Determina o modelo exato para o pull baseado no arquivo setup_env.py
    if [ "$WEIGHT" == "small" ]; then OLLAMA_MODEL="qwen2:1.5b"; fi
    if [ "$WEIGHT" == "medium" ]; then OLLAMA_MODEL="llama3.1:8b"; fi
    if [ "$WEIGHT" == "large" ]; then OLLAMA_MODEL="gemma2:27b"; fi
    
    echo -e "${GREEN}Baixando modelo do Ollama ($OLLAMA_MODEL)... Isso pode demorar.${NC}"
    ollama pull $OLLAMA_MODEL
fi

echo -e "${GREEN}Atualizando arquivo config.yaml...${NC}"
python config/setup_env.py --provider $PROVIDER --weight $WEIGHT

echo -e "${GREEN}Verificando recursos do OpenWakeWord...${NC}"
python config/setup_oww.py

echo -e "${BLUE}=======================================${NC}"
echo -e "${GREEN}✨ INSTALAÇÃO CONCLUÍDA COM SUCESSO! ✨${NC}"
echo -e "${BLUE}=======================================${NC}"
echo "Para iniciar o BMO, ative o ambiente e rode:"
echo "source venv/bin/activate"
echo "python -m app.BMO"
