# 🚀 Quick Start: Wi-Fi Audio + Modelos Médios

**Guia rápido para testar BMO com entrada de áudio Wi-Fi (celular) e modelos de peso médio na Jetson Orin**

---

## ⚡ Setup em 5 Minutos

### 1️⃣ Instalar WO Mic na Jetson

```bash
cd /home/miguel/BMO-Project
bash requirements/setup_wifi_audio.sh
```

**O que este script faz:**
- ✅ Instala dependências do sistema
- ✅ Compila e instala WO Mic client
- ✅ Configura driver do kernel (snd-aloop)
- ✅ Testa conexão automaticamente

**Tempo:** ~3-5 minutos

---

### 2️⃣ Instalar App no Celular

**Android:**
```
Google Play Store → "WO Mic" → Instalar
https://play.google.com/store/apps/details?id=com.wo.voice2
```

**iOS:**
```
App Store → "WO Mic" → Instalar
https://apps.apple.com/app/wo-mic/id1260978417
```

**Tempo:** ~1 minuto

---

### 3️⃣ Configurar BMO para Modelos Médios

```bash
# Copiar configuração otimizada
cp config/config.jetson_medium.yaml config/config.yaml

# Baixar modelo LLM (se ainda não tiver)
ollama pull llama3.1:8b
```

**O que está configurado:**
- 🧠 LLM: llama3.1:8b (~6GB RAM, 2-3s latência)
- 🎤 STT: whisper medium (~5GB VRAM, 92% acurácia)
- 🔊 TTS: Coqui XTTS (~2.5GB VRAM, voz clonada)
- 📡 Wi-Fi: Auto-detecção habilitada

**Tempo:** ~2-10 minutos (download do modelo)

---

### 4️⃣ Conectar e Testar

#### No Celular:

1. **Ativar Hotspot:**
   - Configurações → Hotspot Móvel → Ativar
   - Nome: "BMO-Network" (ou qualquer)
   - Senha: configure uma senha

2. **Iniciar WO Mic:**
   - Abrir app WO Mic
   - Transport: **Wi-Fi**
   - Quality: **High**
   - Pressionar **START** ▶️

#### Na Jetson:

1. **Conectar ao Hotspot:**
   ```bash
   # Via interface gráfica: clique no Wi-Fi → "BMO-Network"

   # Ou via terminal:
   nmcli device wifi connect "BMO-Network" password "sua_senha"
   ```

2. **Verificar Conexão:**
   ```bash
   ip route show default
   # Deve mostrar: default via 192.168.43.1 dev wlan0
   ```

3. **Testar Detecção:**
   ```bash
   python tutorials/detect_wifi_stream.py auto
   ```

   **Você deve ver:**
   - ✅ WO Mic client rodando
   - ✅ Dispositivo Wi-Fi detectado
   - ✅ Teste de gravação bem-sucedido

4. **Iniciar BMO:**
   ```bash
   python app/BMO.py
   ```

   **Você deve ver:**
   ```
   📡 Wi-Fi Audio Streaming habilitado - tentando detectar dispositivo...
   ✅ Usando dispositivo Wi-Fi stream: [X] WO Mic Device
   🎤 Dispositivo de entrada: [X] WO Mic Device
   ✅ BMO está pronto! Escutando pela wake-word 'Ei, BMO'...
   ```

**Tempo:** ~2 minutos

---

## ✅ Teste Completo

1. **Diga "Ei, BMO"** perto do celular
2. **Aguarde** o indicador de wake-word
3. **Fale sua pergunta** (o celular captura o áudio)
4. **Aguarde resposta** (3-4 segundos)

**Exemplo:**
```
Você: "Ei, BMO"
BMO: 💡 BMO Ativado!
Você: "Qual é a capital do Brasil?"
BMO: 🧠 Processando: 'Qual é a capital do Brasil?'
BMO: 🤖 "A capital do Brasil é Brasília!"
```

---

## 🔧 Troubleshooting Rápido

### Dispositivo não detectado

```bash
# 1. Verificar status do WO Mic
python tutorials/detect_wifi_stream.py status

# 2. Iniciar WO Mic manualmente
PHONE_IP=$(ip route show default | grep -oP 'via \K[\d.]+')
womic -t 0 -i $PHONE_IP -p 48000

# 3. Verificar novamente
python tutorials/detect_wifi_stream.py detect
```

### Áudio muito baixo

```bash
# Aumentar volume do PulseAudio
pactl list sources short  # Ver fontes disponíveis
pactl set-source-volume <source_id> 150%  # Aumentar volume
```

### Stream cai

- Mantenha app WO Mic em primeiro plano no celular
- Aproxime celular e Jetson (sinal Wi-Fi)
- Use cabo USB-C como alternativa: `womic -t 1`

### BMO não inicia

```bash
# Verificar configuração
python -c "from config.config_manager import get_config; config = get_config(); print('OK')"

# Se der erro, verificar arquivo YAML
cat config/config.yaml | grep -A 10 "wifi_stream"
```

---

## 📊 Performance Esperada

### Latências (end-to-end)
```
Wake Word:        ~80ms
Audio Stream:     ~20-50ms
STT (medium):     ~500ms
LLM (8B):         ~2-3s
TTS (XTTS):       ~400ms
────────────────────────
TOTAL:            ~3-4 segundos
```

### Recursos
```
RAM:   13-14GB (pico)
VRAM:  7-8GB (GPU)
CPU:   30-40%
Temp:  55-65°C
```

---

## 🎛️ Ajustes Finos

### Mudar Modelo LLM (se não tiver 16GB RAM)

**Para Orin Nano 8GB:**
```yaml
# Em config/config.yaml
llm:
  local:
    model: "llama3.2:3b"  # Mais leve (3B parâmetros)
```

```bash
ollama pull llama3.2:3b
```

### Mudar Modelo STT (para mais velocidade)

```yaml
# Em config/config.yaml
stt:
  local:
    model: "small"  # Mais rápido, menos preciso
    # ou "base" para ainda mais velocidade
```

### Ajustar VAD (se áudio cortado)

```yaml
# Em config/config.yaml
recording:
  vad:
    threshold: 0.35              # Mais sensível
    min_silence_duration_ms: 1000  # Espera mais para parar
```

---

## 📚 Documentação Completa

- **[docs/WIFI_AUDIO_SETUP.md](docs/WIFI_AUDIO_SETUP.md)** - Guia completo de Wi-Fi audio
- **[docs/JETSON_ORIN_DEPLOYMENT.md](docs/JETSON_ORIN_DEPLOYMENT.md)** - Setup completo da Jetson
- **[config/config.jetson_medium.yaml](config/config.jetson_medium.yaml)** - Configuração anotada

---

## 🐛 Comandos Úteis de Debug

```bash
# Ver dispositivos de áudio
python tutorials/list_audio_devices.py

# Testar dispositivo específico
python tutorials/detect_wifi_stream.py test 4  # Substitua 4 pelo índice

# Verificar processos
ps aux | grep womic
ps aux | grep BMO

# Monitorar recursos
sudo jtop  # GPU, RAM, temp

# Ver logs do PulseAudio
pactl list sources
pactl list source-outputs

# Testar gravação manual
arecord -D hw:4 -f S16_LE -r 16000 -c 1 test.wav  # Substitua hw:4
```

---

## 🆘 Suporte

**Problemas comuns:**
1. **"Dispositivo não encontrado"** → Verifique se WO Mic app está transmitindo
2. **"Áudio baixo"** → Aumente volume do celular fisicamente
3. **"Latência alta"** → Aproxime celular da Jetson, use 5GHz se disponível
4. **"OOM (Out of Memory)"** → Use modelo menor (llama3.2:3b)

**Abrir issue:**
- GitHub: https://github.com/anthropics/claude-code/issues
- Inclua: logs, `jtop` screenshot, `config.yaml`

---

## ✨ Próximos Passos

Após configuração básica funcionar:

1. **Gravar voz personalizada para TTS:**
   ```bash
   python custom_models/record_samples.py
   # Grave 10-15 segundos da sua voz
   # Salve em: bmo_voice_sample.wav
   ```

2. **Habilitar ferramentas:**
   ```yaml
   # Em config/config.yaml
   tools:
     spotify: {enabled: true}
     google_calendar: {enabled: true}
     google_search: {enabled: true}
   ```

3. **Otimizar performance:**
   - Ver: docs/JETSON_ORIN_DEPLOYMENT.md
   - Seção: "Performance Tuning"

4. **Modo servidor web:**
   ```bash
   python app/bmo_server.py
   # Acesse: http://192.168.43.100:5000
   ```

---

## 📝 Checklist de Validação

Antes de reportar problemas, verifique:

- [ ] WO Mic instalado na Jetson: `which womic`
- [ ] App WO Mic instalado no celular
- [ ] Celular e Jetson na mesma rede (hotspot ou Wi-Fi)
- [ ] App WO Mic transmitindo (botão START verde)
- [ ] Módulo kernel carregado: `lsmod | grep snd_aloop`
- [ ] Config copiado: `ls -l config/config.yaml`
- [ ] Modelo baixado: `ollama list | grep llama3.1`
- [ ] GPU disponível: `nvidia-smi`
- [ ] Memória suficiente: `free -h` (mínimo 12GB livre)

---

**🎉 Divirta-se com o BMO via Wi-Fi! 🤖📱**

---

**Última atualização:** 2025-10-31
**Versão:** 4.2
**Testado em:** NVIDIA Jetson Orin NX 16GB
