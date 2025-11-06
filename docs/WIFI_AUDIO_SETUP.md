# Wi-Fi Audio Streaming Setup Guide

**Use o microfone do seu celular como entrada de áudio via Wi-Fi para o BMO na Jetson Orin**

Este guia mostra como configurar o BMO para receber áudio do seu celular via Wi-Fi, oferecendo:
- ✅ Qualidade superior ao Bluetooth (48kHz vs 8-16kHz)
- ✅ Latência muito baixa (<50ms em rede local)
- ✅ Mobilidade total (celular como microfone sem fio)
- ✅ Internet compartilhada (tethering do celular)
- ✅ Não requer hardware adicional

---

## 📑 Índice

- [Visão Geral](#visão-geral)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
  - [1. Instalar WO Mic na Jetson](#1-instalar-wo-mic-na-jetson)
  - [2. Instalar App no Celular](#2-instalar-app-no-celular)
- [Configuração](#configuração)
  - [1. Configurar Hotspot do Celular](#1-configurar-hotspot-do-celular)
  - [2. Conectar Jetson ao Hotspot](#2-conectar-jetson-ao-hotspot)
  - [3. Iniciar Transmissão](#3-iniciar-transmissão)
  - [4. Configurar BMO](#4-configurar-bmo)
- [Uso](#uso)
- [Troubleshooting](#troubleshooting)
- [Alternativas](#alternativas)

---

## Visão Geral

O Wi-Fi audio streaming permite que você use o microfone do seu celular como entrada de áudio para o BMO, transformando-o em um microfone sem fio de alta qualidade.

### Arquitetura

```
┌─────────────────┐
│   Celular       │
│  (Android/iOS)  │
├─────────────────┤
│ • Hotspot Wi-Fi │ ← Cria rede Wi-Fi local
│ • WO Mic App    │ ← Captura áudio do microfone
│ • Transmissão   │ ← Envia via Wi-Fi
└────────┬────────┘
         │ Wi-Fi (192.168.43.x)
         │ Latência: ~20-50ms
         │ Qualidade: 48kHz, 16-bit
         ↓
┌────────┴────────┐
│ Jetson Orin     │
├─────────────────┤
│ • Conectada via │ ← Recebe rede do celular
│   Wi-Fi         │
│ • WO Mic Client │ ← Recebe stream de áudio
│ • BMO           │ ← Processa como entrada normal
└─────────────────┘
```

### Vantagens vs Bluetooth

| Aspecto | Wi-Fi Stream | Bluetooth HFP |
|---------|-------------|---------------|
| Qualidade | 48kHz, 16-bit | 8-16kHz, comprimido |
| Latência | 20-50ms | 100-200ms+ |
| Alcance | 5-10m | 5-10m |
| Internet | Sim (tethering) | Não |
| Complexidade | Média | Muito Alta |

---

## Requisitos

### Hardware
- NVIDIA Jetson Orin (Nano/NX/AGX)
- Celular Android ou iOS
- Ambos com Wi-Fi funcional

### Software
- Jetson com Ubuntu 20.04+ ou JetPack 5.x+
- Python 3.8+
- BMO instalado (veja README.md)

---

## Instalação

### 1. Instalar WO Mic na Jetson

Execute o script de instalação automático:

```bash
cd /home/miguel/BMO-Project
bash requirements/setup_wifi_audio.sh
```

Este script irá:
- ✅ Detectar seu sistema operacional
- ✅ Instalar dependências (build tools, PulseAudio, etc.)
- ✅ Baixar e compilar WO Mic client
- ✅ Instalar driver do kernel (snd-aloop)
- ✅ Configurar carregamento automático do módulo

**Nota:** O script pedirá sua senha para instalar pacotes do sistema.

#### Verificar Instalação

```bash
# Verificar se womic está instalado
which womic

# Verificar módulo do kernel
lsmod | grep snd_aloop

# Ou use o utilitário de diagnóstico
python tutorials/detect_wifi_stream.py status
```

### 2. Instalar App no Celular

#### Android
1. Acesse: https://play.google.com/store/apps/details?id=com.wo.voice2
2. Ou busque "WO Mic" na Play Store
3. Instale o app gratuito

#### iOS
1. Acesse: https://apps.apple.com/app/wo-mic/id1260978417
2. Ou busque "WO Mic" na App Store
3. Instale o app gratuito

---

## Configuração

### 1. Configurar Hotspot do Celular

#### Android
1. Vá em **Configurações** → **Conexões** → **Hotspot e Tethering**
2. Ative **Hotspot Móvel**
3. Configure:
   - **Nome da rede**: BMO-Network (ou qualquer nome)
   - **Senha**: sua_senha_aqui
   - **Banda**: 2.4GHz ou 5GHz (ambos funcionam)
4. Anote o IP do hotspot (geralmente `192.168.43.1`)

#### iOS
1. Vá em **Ajustes** → **Hotspot Pessoal**
2. Ative **Permitir que Outros Se Conectem**
3. Anote a senha exibida
4. O IP geralmente é `172.20.10.1`

### 2. Conectar Jetson ao Hotspot

Na Jetson, conecte-se à rede Wi-Fi do celular:

```bash
# Via interface gráfica (se disponível)
# Clique no ícone Wi-Fi → Selecione "BMO-Network" → Digite senha

# Via terminal (nmcli)
nmcli device wifi connect "BMO-Network" password "sua_senha_aqui"

# Verificar conexão
ip route show default
# Deve mostrar algo como: default via 192.168.43.1 dev wlan0
```

### 3. Iniciar Transmissão

#### No Celular (WO Mic App)

1. Abra o app **WO Mic**
2. Configure:
   - **Transport**: Selecione **Wi-Fi**
   - **Quality**: Recomendado **High** (48kHz)
3. Pressione **Start** (botão grande no centro)
4. O app deve mostrar: "Server started"

**Nota:** Mantenha o app em primeiro plano durante uso para melhor desempenho.

#### Na Jetson (WO Mic Client)

Você tem duas opções:

**Opção A: Deixar BMO detectar automaticamente** (Recomendado)

Se você usar `config.jetson_medium.yaml`, o BMO detectará automaticamente. Apenas inicie:

```bash
python app/BMO.py
```

**Opção B: Iniciar manualmente**

```bash
# Detectar IP do celular automaticamente
PHONE_IP=$(ip route show default | grep -oP 'via \K[\d.]+' | head -1)

# Iniciar WO Mic client
womic -t 0 -i $PHONE_IP -p 48000

# Ou com IP específico (Android)
womic -t 0 -i 192.168.43.1 -p 48000

# Ou com IP específico (iOS)
womic -t 0 -i 172.20.10.1 -p 48000
```

**Parâmetros:**
- `-t 0`: Transport type (0 = Wi-Fi)
- `-i <IP>`: IP do celular
- `-p 48000`: Porta (padrão para Wi-Fi)

### 4. Configurar BMO

#### Usando Configuração Pronta (Recomendado)

Copie a configuração otimizada para Jetson com Wi-Fi:

```bash
cp config/config.jetson_medium.yaml config/config.yaml
```

Esta configuração já inclui:
- ✅ Wi-Fi streaming habilitado
- ✅ Auto-detecção de dispositivo
- ✅ Fallback automático para microfone local
- ✅ Modelos de peso médio (LLM 8B, STT medium)

#### Configuração Manual

Se preferir configurar manualmente, edite `config/config.yaml`:

```yaml
recording:
  # ... outras configurações ...

  # Wi-Fi Audio Streaming
  wifi_stream:
    enabled: true              # Habilita Wi-Fi streaming
    auto_detect: true          # Detecta dispositivo automaticamente
    auto_start: true           # Tenta iniciar WO Mic automaticamente
    fallback_to_local: true    # Usa mic local se Wi-Fi falhar

    # Dispositivos preferidos (ordem de prioridade)
    preferred_devices:
      - "wo_mic"
      - "WO Mic"
      - "soundwire"
      - "phone"

    # WO Mic específico
    womic:
      server_ip: null          # null = auto-detect, ou IP específico
      port: 48000              # Porta padrão

  # VAD ajustado para Wi-Fi streaming
  vad:
    enabled: true
    threshold: 0.45            # Ajustado para possível ruído de rede
    min_silence_duration_ms: 800
```

---

## Uso

### Iniciar BMO com Wi-Fi Audio

1. **No Celular:**
   - Ative Hotspot Wi-Fi
   - Abra WO Mic app
   - Pressione **Start**

2. **Na Jetson:**
   - Conecte ao hotspot
   - Inicie BMO:
     ```bash
     python app/BMO.py
     ```

3. **Verificar:**
   - BMO deve mostrar: `✅ Usando dispositivo Wi-Fi stream: [X] WO Mic Device`
   - Fale no celular para testar

### Testar Dispositivo

Use o utilitário de detecção para diagnosticar:

```bash
# Menu interativo
python tutorials/detect_wifi_stream.py

# Comandos diretos
python tutorials/detect_wifi_stream.py detect    # Detectar dispositivo
python tutorials/detect_wifi_stream.py test 4    # Testar dispositivo índice 4
python tutorials/detect_wifi_stream.py status    # Status do WO Mic
python tutorials/detect_wifi_stream.py auto      # Workflow completo
```

### Listar Dispositivos de Áudio

```bash
python tutorials/list_audio_devices.py
```

Procure por dispositivos com nomes como:
- "WO Mic Device"
- "Loopback: PCM"
- "snd_aloop"

---

## Troubleshooting

### Dispositivo não detectado

**Sintomas:** BMO não encontra dispositivo Wi-Fi stream

**Soluções:**

1. **Verificar se WO Mic está transmitindo:**
   ```bash
   python tutorials/detect_wifi_stream.py status
   ```

2. **Verificar conexão de rede:**
   ```bash
   ping -c 3 $(ip route show default | grep -oP 'via \K[\d.]+')
   ```

3. **Iniciar WO Mic manualmente:**
   ```bash
   womic -t 0 -i 192.168.43.1 -p 48000
   ```

4. **Verificar se módulo do kernel está carregado:**
   ```bash
   lsmod | grep snd_aloop
   # Se não estiver, carregar com:
   sudo modprobe snd-aloop
   ```

5. **Listar fontes PulseAudio:**
   ```bash
   pactl list sources short
   # Deve aparecer algo relacionado a wo_mic ou loopback
   ```

### Áudio muito baixo

**Sintomas:** Áudio capturado mas com amplitude muito baixa

**Soluções:**

1. **Aumentar volume do celular** (use botões físicos)

2. **Ajustar ganho do PulseAudio:**
   ```bash
   # Listar fontes
   pactl list sources short

   # Aumentar volume da fonte WO Mic
   pactl set-source-volume <source_name> 150%
   ```

3. **Testar gravação:**
   ```bash
   python tutorials/detect_wifi_stream.py test 4
   # Substitua 4 pelo índice correto do dispositivo
   ```

### Latência alta

**Sintomas:** Delay perceptível entre falar e resposta

**Causas e Soluções:**

1. **Sinal Wi-Fi fraco:**
   - Aproxime celular e Jetson
   - Use banda 5GHz se disponível
   - Evite obstáculos entre dispositivos

2. **Interferência:**
   - Afaste de outros dispositivos Wi-Fi
   - Troque canal do hotspot

3. **Buffer do PulseAudio:**
   ```bash
   # Editar /etc/pulse/daemon.conf
   default-fragments = 2
   default-fragment-size-msec = 25
   ```

4. **Considere cabo USB-C:**
   - WO Mic também suporta conexão USB
   - Latência mínima, sem problemas de sinal

### Áudio cortado/entrecortado

**Sintomas:** Áudio com pausas ou cortes

**Soluções:**

1. **Verificar carga da CPU/GPU:**
   ```bash
   sudo jtop
   ```

2. **Ajustar VAD:**
   Em `config.yaml`:
   ```yaml
   vad:
     threshold: 0.4              # Mais sensível
     min_silence_duration_ms: 1000  # Espera mais para parar
   ```

3. **Melhorar conexão Wi-Fi** (ver "Latência alta")

4. **Reduzir qualidade do stream:**
   No app WO Mic: Settings → Quality → Medium

### WO Mic não inicia

**Sintomas:** Erro ao executar `womic`

**Soluções:**

1. **Reinstalar:**
   ```bash
   bash requirements/setup_wifi_audio.sh
   ```

2. **Verificar dependências:**
   ```bash
   ldd /usr/bin/womic
   ```

3. **Compilar do zero:**
   ```bash
   git clone https://github.com/wolicheng/womic.git
   cd womic/linux
   make
   sudo make install
   ```

### Stream cai frequentemente

**Sintomas:** Conexão perdida após alguns minutos

**Soluções:**

1. **Desabilitar economia de energia do Wi-Fi:**
   ```bash
   # Android: Configurações → Wi-Fi → Avançado → Manter Wi-Fi ligado
   ```

2. **Manter app em primeiro plano** no celular

3. **Habilitar fallback automático** em `config.yaml`:
   ```yaml
   wifi_stream:
     fallback_to_local: true
   ```

4. **Usar cabo USB** para conexão mais estável

---

## Alternativas

### SoundWire

Outra opção para streaming de áudio via Wi-Fi:

**Vantagens:**
- Latência ainda menor (~10-30ms)
- Interface mais polida

**Desvantagens:**
- Versão gratuita limitada
- Cliente Linux não oficial

**Links:**
- Android: https://play.google.com/store/apps/details?id=com.georgie.SoundWireFree
- iOS: https://apps.apple.com/app/soundwire/id1015315381

### Conexão USB

WO Mic também suporta conexão via cabo USB-C:

```bash
# Com celular conectado via USB
womic -t 1

# Vantagens:
# - Latência mínima
# - Sem problemas de sinal
# - Carrega celular simultaneamente
```

### Bluetooth A2DP

Para comparação, veja: [docs/AUDIO_DEVICES.md](AUDIO_DEVICES.md)

---

## Performance Esperada

### Latências (end-to-end com Wi-Fi stream)

```
Wake Word Detection:      ~80ms
Audio Streaming (Wi-Fi):  ~20-50ms
VAD Processing:           ~1ms
STT (medium, GPU):        ~500ms
LLM (llama3.1:8b):        ~2-3s
TTS (Coqui XTTS):         ~400ms
─────────────────────────────────
TOTAL:                    ~3-4 segundos
```

### Uso de Recursos

```
RAM:  ~13-14GB (com modelos medium)
VRAM: ~7-8GB (GPU)
CPU:  ~30-40% (moderado)
Wi-Fi: ~256 kbps (audio stream)
```

### Qualidade de Áudio

```
Sample Rate:  48000 Hz (configurável)
Bit Depth:    16-bit
Channels:     Mono
Codec:        PCM (sem compressão)
```

---

## Referências

- **WO Mic Project:** https://github.com/wolicheng/womic
- **WO Mic Official Site:** http://wolicheng.com/womic/
- **BMO Audio Devices Guide:** [docs/AUDIO_DEVICES.md](AUDIO_DEVICES.md)
- **Jetson Deployment Guide:** [docs/JETSON_ORIN_DEPLOYMENT.md](JETSON_ORIN_DEPLOYMENT.md)

---

## Suporte

- **Issues:** https://github.com/anthropics/claude-code/issues
- **Discussões:** Veja README.md principal

---

**Última atualização:** 2025-10-31
**Versão do BMO:** 4.2
**Testado em:** NVIDIA Jetson Orin NX 16GB, JetPack 5.1
