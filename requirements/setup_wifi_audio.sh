#!/bin/bash

# ═══════════════════════════════════════════════════════════
# BMO Wi-Fi Audio Streaming Setup
# Instala WO Mic client para receber áudio do celular via Wi-Fi
# ═══════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}    BMO - Wi-Fi Audio Streaming Setup (WO Mic)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ Este script não deve ser executado como root/sudo${NC}"
   echo -e "   Execute sem sudo. Ele pedirá a senha quando necessário.\n"
   exit 1
fi

# ───────────────────────────────────────────────────────────
# 1. Detect System
# ───────────────────────────────────────────────────────────
echo -e "${YELLOW}🔍 Detectando sistema...${NC}"

if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    echo -e "   Sistema: $PRETTY_NAME"
else
    echo -e "${RED}❌ Sistema não suportado. Este script é para Linux.${NC}"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
echo -e "   Arquitetura: $ARCH"

# Check if Jetson
IS_JETSON=false
if [[ -f /etc/nv_tegra_release ]] || command -v jetson_clocks &> /dev/null; then
    IS_JETSON=true
    echo -e "   ${GREEN}✓ NVIDIA Jetson detectado${NC}"
fi

echo ""

# ───────────────────────────────────────────────────────────
# 2. Install Dependencies
# ───────────────────────────────────────────────────────────
echo -e "${YELLOW}📦 Instalando dependências...${NC}"

# Determine package manager
if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt-get"
    UPDATE_CMD="sudo apt-get update"
    INSTALL_CMD="sudo apt-get install -y"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
    UPDATE_CMD="sudo dnf check-update || true"
    INSTALL_CMD="sudo dnf install -y"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
    UPDATE_CMD="sudo pacman -Sy"
    INSTALL_CMD="sudo pacman -S --noconfirm"
else
    echo -e "${RED}❌ Gerenciador de pacotes não suportado${NC}"
    exit 1
fi

# Update package list
echo -e "   Atualizando lista de pacotes..."
$UPDATE_CMD > /dev/null 2>&1

# Install required packages
echo -e "   Instalando pacotes necessários..."
PACKAGES="build-essential linux-headers-$(uname -r) wget git"

if [[ "$PKG_MANAGER" == "apt-get" ]]; then
    $INSTALL_CMD $PACKAGES libpulse-dev pulseaudio > /dev/null 2>&1
elif [[ "$PKG_MANAGER" == "dnf" ]]; then
    $INSTALL_CMD $PACKAGES pulseaudio-libs-devel pulseaudio > /dev/null 2>&1
elif [[ "$PKG_MANAGER" == "pacman" ]]; then
    $INSTALL_CMD $PACKAGES libpulse pulseaudio > /dev/null 2>&1
fi

echo -e "   ${GREEN}✓ Dependências instaladas${NC}\n"

# ───────────────────────────────────────────────────────────
# 3. Download WO Mic Client
# ───────────────────────────────────────────────────────────
echo -e "${YELLOW}⬇️  Baixando WO Mic client...${NC}"

WOMIC_DIR="/tmp/womic_install"
mkdir -p $WOMIC_DIR
cd $WOMIC_DIR

# Download WO Mic for Linux
WOMIC_VERSION="2.3"
WOMIC_URL="https://github.com/wolicheng/womic/releases/download/v${WOMIC_VERSION}/womic-linux-v${WOMIC_VERSION}.tar.gz"

echo -e "   Baixando de $WOMIC_URL..."
if wget -q --show-progress $WOMIC_URL -O womic.tar.gz; then
    echo -e "   ${GREEN}✓ Download concluído${NC}"
else
    echo -e "${RED}❌ Falha no download. Tentando mirror alternativo...${NC}"
    # Alternative: build from source if download fails
    echo -e "${YELLOW}   Compilando do código fonte...${NC}"
    git clone https://github.com/wolicheng/womic.git
    cd womic/linux
    make
    sudo make install
    echo -e "   ${GREEN}✓ Compilado e instalado${NC}\n"
    cd $HOME
    rm -rf $WOMIC_DIR
    exit 0
fi

# Extract
echo -e "   Extraindo arquivos..."
tar -xzf womic.tar.gz
cd womic-*

echo ""

# ───────────────────────────────────────────────────────────
# 4. Install WO Mic
# ───────────────────────────────────────────────────────────
echo -e "${YELLOW}📥 Instalando WO Mic client...${NC}"

# Install kernel module
echo -e "   Instalando módulo do kernel..."
cd driver
make
sudo make install
cd ..

# Load kernel module
echo -e "   Carregando módulo do kernel..."
sudo modprobe snd-aloop

# Make module load on boot
echo "snd-aloop" | sudo tee /etc/modules-load.d/womic.conf > /dev/null

# Install client binary
echo -e "   Instalando cliente..."
sudo cp womic /usr/bin/
sudo chmod +x /usr/bin/womic

echo -e "   ${GREEN}✓ WO Mic instalado com sucesso${NC}\n"

# Cleanup
cd $HOME
rm -rf $WOMIC_DIR

# ───────────────────────────────────────────────────────────
# 5. Verify Installation
# ───────────────────────────────────────────────────────────
echo -e "${YELLOW}🔍 Verificando instalação...${NC}"

if command -v womic &> /dev/null; then
    echo -e "   ${GREEN}✓ womic command disponível${NC}"
else
    echo -e "   ${RED}❌ womic command não encontrado${NC}"
    exit 1
fi

if lsmod | grep -q snd_aloop; then
    echo -e "   ${GREEN}✓ Módulo do kernel carregado${NC}"
else
    echo -e "   ${YELLOW}⚠️  Módulo do kernel não carregado. Tentando carregar...${NC}"
    sudo modprobe snd-aloop
fi

echo ""

# ───────────────────────────────────────────────────────────
# 6. Instructions
# ───────────────────────────────────────────────────────────
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ WO Mic instalado com sucesso!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}📱 PRÓXIMOS PASSOS:${NC}\n"

echo -e "${YELLOW}1. No Celular:${NC}"
echo -e "   • Instale o app WO Mic:"
echo -e "     Android: https://play.google.com/store/apps/details?id=com.wo.voice2"
echo -e "     iOS: https://apps.apple.com/app/wo-mic/id1260978417"
echo -e ""
echo -e "   • Ative o Hotspot Wi-Fi no celular"
echo -e "     (ou conecte celular e Jetson na mesma rede Wi-Fi)"
echo -e ""
echo -e "   • Abra o app WO Mic e configure:"
echo -e "     - Transport: Wi-Fi"
echo -e "     - Clique em 'Start' para iniciar transmissão"
echo -e ""

echo -e "${YELLOW}2. Na Jetson:${NC}"
echo -e "   • Conecte-se ao hotspot do celular"
echo -e "     (ou à mesma rede Wi-Fi)"
echo -e ""
echo -e "   • Inicie o WO Mic client:"
echo -e "     ${GREEN}womic -t 0 -i <IP_DO_CELULAR> -p 48000${NC}"
echo -e ""
echo -e "   • Ou deixe o BMO detectar automaticamente:"
echo -e "     ${GREEN}python app/BMO.py${NC}"
echo -e "     (se config.jetson_medium.yaml estiver ativo)"
echo -e ""

echo -e "${YELLOW}3. Testar Áudio:${NC}"
echo -e "   • Detectar dispositivo Wi-Fi:"
echo -e "     ${GREEN}python tutorials/detect_wifi_stream.py${NC}"
echo -e ""
echo -e "   • Listar todos dispositivos de áudio:"
echo -e "     ${GREEN}python tutorials/list_audio_devices.py${NC}"
echo -e ""

echo -e "${YELLOW}4. Configurar BMO:${NC}"
echo -e "   • Copie a configuração para Jetson Medium:"
echo -e "     ${GREEN}cp config/config.jetson_medium.yaml config/config.yaml${NC}"
echo -e ""
echo -e "   • O Wi-Fi stream já está habilitado nesta config!"
echo -e "     (wifi_stream.enabled = true)"
echo -e ""

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}📚 DOCUMENTAÇÃO:${NC}"
echo -e "   • docs/WIFI_AUDIO_SETUP.md - Guia completo de setup Wi-Fi"
echo -e "   • docs/AUDIO_DEVICES.md - Troubleshooting de áudio"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"

echo -e "${GREEN}🎉 Setup concluído! Aproveite o BMO com áudio Wi-Fi!${NC}\n"

# ───────────────────────────────────────────────────────────
# 7. Optional: Auto-start test
# ───────────────────────────────────────────────────────────
read -p "Deseja tentar conectar ao celular agora? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "\n${YELLOW}🔍 Detectando IP do celular...${NC}"

    # Get default gateway (likely the phone)
    GATEWAY=$(ip route show default | grep -oP 'via \K[\d.]+' | head -1)

    if [[ -n "$GATEWAY" ]]; then
        echo -e "   Detectado gateway: $GATEWAY"
        echo -e "   Tentando conectar ao WO Mic..."

        # Try to connect
        womic -t 0 -i $GATEWAY -p 48000 &
        WOMIC_PID=$!

        sleep 3

        if ps -p $WOMIC_PID > /dev/null; then
            echo -e "   ${GREEN}✓ WO Mic client iniciado (PID: $WOMIC_PID)${NC}"
            echo -e "   ${GREEN}✓ Teste com: python tutorials/detect_wifi_stream.py${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Não foi possível conectar automaticamente${NC}"
            echo -e "   Verifique se o app WO Mic está transmitindo no celular"
        fi
    else
        echo -e "   ${YELLOW}⚠️  Gateway não detectado${NC}"
        echo -e "   Conecte-se ao hotspot do celular primeiro"
    fi
fi

echo -e "\n${GREEN}Pronto! 🚀${NC}\n"
