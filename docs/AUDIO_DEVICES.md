# 🎧 Configuração de Dispositivos de Áudio

## 📋 Visão Geral

O BMO permite configurar manualmente quais dispositivos de áudio usar para:
- **Entrada** (microfone/gravação)
- **Saída** (alto-falantes/fones)

Isso é especialmente útil em sistemas com múltiplos dispositivos, como:
- Jetson Orin (USB, HDMI, Jack 3.5mm)
- PCs com múltiplos microfones/alto-falantes
- Ambientes com dispositivos profissionais

---

## 🚀 Quick Start

### 1. Listar Dispositivos Disponíveis

```bash
source venv/bin/activate
python list_audio_devices.py
```

**Saída esperada:**
```
======================================================================
🎧 DISPOSITIVOS DE ÁUDIO DISPONÍVEIS
======================================================================

📥 DISPOSITIVOS DE ENTRADA (Microfones):
----------------------------------------------------------------------

   Índice: 0 [PADRÃO]
   Nome: Built-in Microphone
   Canais: 2
   Taxa de amostragem: 48000 Hz

   Índice: 2
   Nome: USB Audio Device
   Canais: 1
   Taxa de amostragem: 16000 Hz

📤 DISPOSITIVOS DE SAÍDA (Alto-falantes/Fones):
----------------------------------------------------------------------

   Índice: 1 [PADRÃO]
   Nome: Built-in Speaker
   Canais: 2
   Taxa de amostragem: 48000 Hz

   Índice: 3
   Nome: USB Audio Device
   Canais: 2
   Taxa de amostragem: 48000 Hz
```

### 2. Configurar no config.yaml

Edite `config/config.yaml`:

```yaml
recording:
  # Use os índices listados acima
  input_device_index: 2   # USB Microphone
  output_device_index: 3  # USB Speaker
```

### 3. Testar

```bash
python app/BMO.py
```

**Saída esperada:**
```
🎤 Dispositivo de entrada: [2] USB Audio Device
🔊 Dispositivo de saída: [3] USB Audio Device
✅ BMO está pronto! Escutando pela wake-word 'Ei, BMO'...
```

---

## ⚙️ Configurações Detalhadas

### Usar Dispositivo Padrão do Sistema

```yaml
recording:
  input_device_index: null   # Usa padrão do sistema
  output_device_index: null  # Usa padrão do sistema
```

### Especificar Dispositivos Manualmente

```yaml
recording:
  input_device_index: 2   # Microfone USB
  output_device_index: 5  # Alto-falante HDMI
```

### Usar Dispositivos Diferentes

```yaml
# Exemplo: Microfone USB + Saída HDMI
recording:
  input_device_index: 2   # USB mic
  output_device_index: 8  # HDMI output
```

---

## 🔧 Cenários Comuns

### Jetson Orin com USB Audio

```yaml
# Microfone e alto-falante USB
recording:
  input_device_index: 4   # USB Audio Device (input)
  output_device_index: 5  # USB Audio Device (output)
```

### Jetson Orin com HDMI Audio

```yaml
# Microfone USB + Saída HDMI
recording:
  input_device_index: 4   # USB microphone
  output_device_index: 2  # HDMI output (tegra-snd)
```

### PC com Microfone Profissional

```yaml
# Blue Yeti ou similar
recording:
  input_device_index: 3   # Professional USB microphone
  output_device_index: null  # Sistema padrão
```

### Raspberry Pi com USB Audio

```yaml
# USB Audio Card
recording:
  input_device_index: 1   # USB Audio
  output_device_index: 1  # USB Audio
```

---

## 🧪 Testando Dispositivos

### Testar Dispositivo Específico

```bash
# Testar entrada (microfone)
python list_audio_devices.py 2 input

# Testar saída (alto-falante)
python list_audio_devices.py 3 output
```

### Testar com ALSA (Linux)

```bash
# Listar placas de áudio
arecord -l
aplay -l

# Gravar teste (5 segundos)
arecord -D hw:1,0 -f cd -d 5 test.wav

# Reproduzir teste
aplay test.wav

# Reproduzir em dispositivo específico
aplay -D hw:1,0 test.wav
```

---

## 🐛 Troubleshooting

### Problema: Dispositivo não aparece na lista

**Causa:** Dispositivo não reconhecido ou não conectado.

**Soluções:**

1. **Verificar se está conectado:**
   ```bash
   # USB devices
   lsusb

   # ALSA devices
   arecord -l
   aplay -l
   ```

2. **Reconectar dispositivo USB**

3. **Reiniciar serviço de áudio:**
   ```bash
   # PulseAudio
   pulseaudio --kill
   pulseaudio --start

   # Ou reiniciar sistema
   sudo reboot
   ```

---

### Problema: "Invalid device index"

**Causa:** Índice inválido ou dispositivo desconectado.

**Soluções:**

1. **Listar dispositivos novamente:**
   ```bash
   python list_audio_devices.py
   ```

2. **Usar `null` para padrão do sistema:**
   ```yaml
   recording:
     input_device_index: null
     output_device_index: null
   ```

---

### Problema: Sem som na saída

**Causa:** Dispositivo mudo ou volume zero.

**Soluções:**

1. **Verificar volume do sistema:**
   ```bash
   # Ver controles de volume
   alsamixer

   # Ajustar volume
   amixer set Master 80%
   ```

2. **Testar saída:**
   ```bash
   speaker-test -t wav -c 2
   ```

3. **Verificar se dispositivo correto:**
   ```bash
   python list_audio_devices.py
   ```

---

### Problema: Microfone muito baixo/alto

**Causa:** Ganho do microfone não ajustado.

**Soluções:**

1. **Ajustar ganho (ALSA):**
   ```bash
   alsamixer
   # Pressione F4 para captura
   # Ajuste com setas
   ```

2. **Ajustar via PulseAudio:**
   ```bash
   pactl set-source-volume @DEFAULT_SOURCE@ 80%
   ```

3. **Usar dispositivo com controle de ganho hardware**

---

## 📊 Comparação de Dispositivos

### Tipos de Dispositivos

| Tipo | Qualidade | Latência | Configuração | Uso |
|------|-----------|----------|--------------|-----|
| **Built-in** | ⭐⭐ | Baixa | Simples | Testes |
| **USB Basic** | ⭐⭐⭐ | Baixa | Simples | Uso geral |
| **USB Pro** | ⭐⭐⭐⭐⭐ | Média | Moderada | Produção |
| **HDMI** | ⭐⭐⭐ | Baixa | Simples | TVs/Monitores |
| **Bluetooth** | ⭐⭐ | Alta | Complexa | ❌ Não recomendado |

---

### Recomendações por Hardware

#### Jetson Orin

**Melhor opção:** USB Audio Interface

```yaml
# USB Audio Card de qualidade
recording:
  input_device_index: 4   # USB mic
  output_device_index: 5  # USB output
  sample_rate: 16000      # Manter 16kHz para wake word
```

**Alternativa:** HDMI para saída

```yaml
recording:
  input_device_index: 4   # USB mic
  output_device_index: 2  # HDMI (monitor/TV)
```

---

#### Raspberry Pi

**Melhor opção:** USB Audio Card

```yaml
# RPi não tem entrada de áudio onboard
recording:
  input_device_index: 1   # USB Audio
  output_device_index: 1  # USB Audio ou HDMI
```

---

#### PC Desktop

**Melhor opção:** Built-in + USB Mic (opcional)

```yaml
# Built-in speaker + USB microphone profissional
recording:
  input_device_index: 2   # USB microphone
  output_device_index: null  # Sistema padrão
```

---

## 💡 Dicas e Boas Práticas

### 1. Sempre Teste Antes de Configurar

```bash
# Teste de 5 segundos
arecord -D hw:X,Y -f cd -d 5 test.wav
aplay test.wav
```

### 2. Use Taxa de Amostragem Nativa

- Wake word precisa de **16kHz**
- Se o dispositivo não suporta 16kHz, PyAudio fará resample (pode causar problemas)
- Verifique `defaultSampleRate` ao listar dispositivos

### 3. Prefira USB para Jetson

- USB Audio tem drivers mais estáveis
- HDMI Audio pode ter problemas com alguns monitores
- Jack 3.5mm depende do modelo da Jetson

### 4. Evite Bluetooth

- Alta latência (~100-300ms)
- Problemas de sincronização
- Pode causar disconnects

### 5. Configure Ganho Adequadamente

- Muito baixo: VAD não detecta fala
- Muito alto: Distorção e clipping
- Ideal: -12dB a -6dB pico

---

## 🔍 Verificação de Setup

### Checklist

- [ ] Dispositivos listados com `python list_audio_devices.py`
- [ ] Índices corretos no `config.yaml`
- [ ] Teste de gravação bem-sucedido (`arecord`)
- [ ] Teste de reprodução bem-sucedido (`aplay`)
- [ ] BMO inicia mostrando dispositivos corretos
- [ ] Wake word detecta "Ei, BMO"
- [ ] Áudio de resposta reproduz claramente

---

## 📝 Exemplo Completo de Configuração

### config/config.yaml

```yaml
recording:
  # Audio devices (use list_audio_devices.py)
  input_device_index: 2   # USB Microphone
  output_device_index: 3  # USB Speaker

  # Audio settings
  duration_seconds: 5
  sample_rate: 16000
  channels: 1
  chunk_size: 1280
  format: "int16"

  # VAD (recomendado)
  vad:
    enabled: true
    threshold: 0.5
    min_speech_duration_ms: 250
    min_silence_duration_ms: 700
    max_recording_seconds: 30
```

---

## 🎯 Resumo

### Para Usar Dispositivos Padrão (Mais Simples)

```yaml
recording:
  input_device_index: null
  output_device_index: null
```

### Para Configurar Manualmente (Recomendado)

```bash
# 1. Listar dispositivos
python list_audio_devices.py

# 2. Anotar índices
# Input: 2 (USB Mic)
# Output: 3 (USB Speaker)

# 3. Configurar
# Editar config.yaml com os índices

# 4. Testar
python app/BMO.py
```

---

## 📚 Recursos Adicionais

- **ALSA Documentation:** https://alsa-project.org/wiki/Main_Page
- **PyAudio Documentation:** https://people.csail.mit.edu/hubert/pyaudio/docs/
- **Jetson Audio Guide:** https://docs.nvidia.com/jetson/archives/r35.4.1/

---

**Dúvidas?** Verifique os dispositivos com `python list_audio_devices.py`!
