# 🎧 Guia Rápido: Configuração de Áudio

## 📋 Resumo

O BMO agora suporta **configuração manual de dispositivos de áudio**, essencial para Jetson Orin e outros sistemas com múltiplos dispositivos.

---

## 🚀 Setup em 3 Passos

### 1️⃣ Descobrir Dispositivos

```bash
python list_audio_devices.py
```

**Saída esperada:**
```
📥 DISPOSITIVOS DE ENTRADA (Microfones):
   Índice: 0 [PADRÃO]
   Nome: Built-in Microphone

   Índice: 4
   Nome: USB Audio Device  ← Use este!

📤 DISPOSITIVOS DE SAÍDA (Alto-falantes):
   Índice: 1 [PADRÃO]
   Nome: Built-in Speaker

   Índice: 5
   Nome: USB Audio Device  ← Use este!
```

---

### 2️⃣ Configurar

Edite `config/config.yaml`:

```yaml
recording:
  input_device_index: 4   # ← Índice do microfone USB
  output_device_index: 5  # ← Índice do speaker USB
```

**Ou use padrão do sistema:**
```yaml
recording:
  input_device_index: null
  output_device_index: null
```

---

### 3️⃣ Testar

```bash
python app/BMO.py
```

**Saída esperada:**
```
🎤 Dispositivo de entrada: [4] USB Audio Device
🔊 Dispositivo de saída: [5] USB Audio Device
✅ BMO está pronto!
```

---

## 🎯 Casos de Uso Comuns

### Jetson Orin com USB Audio

```yaml
# Mais estável e melhor qualidade
recording:
  input_device_index: 4   # USB Mic
  output_device_index: 5  # USB Speaker
```

### Jetson Orin com HDMI Audio

```yaml
# Microfone USB + Saída no monitor/TV
recording:
  input_device_index: 4   # USB Mic
  output_device_index: 2  # HDMI Output
```

### PC Desktop

```yaml
# Microfone USB profissional + Saída padrão
recording:
  input_device_index: 3   # Blue Yeti ou similar
  output_device_index: null  # Sistema padrão
```

### Raspberry Pi

```yaml
# USB Audio Card (RPi não tem entrada onboard)
recording:
  input_device_index: 1   # USB Audio
  output_device_index: 1  # USB Audio
```

---

## 🔧 Comandos Úteis

### Listar Dispositivos
```bash
python list_audio_devices.py
```

### Testar Dispositivo Específico
```bash
# Testar entrada (índice 4)
python list_audio_devices.py 4 input

# Testar saída (índice 5)
python list_audio_devices.py 5 output
```

### Testar com ALSA
```bash
# Gravar 5 segundos
arecord -D hw:1,0 -f cd -d 5 test.wav

# Reproduzir
aplay test.wav
```

### Ver Dispositivos USB
```bash
lsusb
```

---

## 📊 O Que Foi Implementado

| Feature | Status | Descrição |
|---------|--------|-----------|
| **Input Device Selection** | ✅ | Escolher microfone manualmente |
| **Output Device Selection** | ✅ | Escolher alto-falante manualmente |
| **Device Discovery** | ✅ | Script `list_audio_devices.py` |
| **Default Fallback** | ✅ | Usa padrão do sistema se `null` |
| **Device Info Display** | ✅ | Mostra dispositivos no startup |
| **PyAudio Integration** | ✅ | Playback via dispositivo específico |
| **Error Handling** | ✅ | Falha gracefully se inválido |

---

## 📝 Arquivos Modificados

| Arquivo | Mudanças |
|---------|----------|
| `config/config.yaml` | Adicionado `output_device_index` |
| `config/config_manager.py` | Modelo Pydantic atualizado |
| `app/BMO.py` | Suporte a output device + display info |
| **`list_audio_devices.py`** | **Novo script helper** |
| **`docs/AUDIO_DEVICES.md`** | **Documentação completa** |
| `config.jetson.yaml` | Comentários sobre áudio |

---

## 🐛 Troubleshooting Rápido

### Dispositivo não aparece
```bash
# Reconectar USB
# Reiniciar sistema
sudo reboot
```

### Erro "Invalid device index"
```bash
# Listar novamente
python list_audio_devices.py

# Ou usar padrão
# Configurar input_device_index: null
```

### Sem som
```bash
# Verificar volume
alsamixer

# Testar saída
speaker-test -t wav -c 2
```

### Microfone muito baixo
```bash
# Ajustar ganho
alsamixer
# Pressione F4, ajuste com setas
```

---

## 💡 Recomendações

### ✅ Use USB Audio na Jetson

- Mais estável que HDMI
- Melhor controle de ganho
- Compatível com mais dispositivos

### ✅ Configure Manualmente

```yaml
# Ao invés de:
input_device_index: null

# Use:
input_device_index: 4
```

**Por quê?**
- Garante que sempre usa o dispositivo correto
- Evita problemas se dispositivo padrão mudar
- Melhor para deployment em produção

### ✅ Teste Antes de Configurar

```bash
# Sempre teste primeiro!
python list_audio_devices.py
arecord -D hw:X,Y -f cd -d 5 test.wav
aplay test.wav
```

---

## 📚 Documentação Completa

- **Guia Detalhado**: `docs/AUDIO_DEVICES.md`
- **Jetson Deployment**: `docs/JETSON_ORIN_DEPLOYMENT.md`
- **Script Helper**: `list_audio_devices.py`

---

## ✅ Checklist de Setup

- [ ] Execute `python list_audio_devices.py`
- [ ] Anote os índices dos dispositivos desejados
- [ ] Configure `config.yaml` com os índices
- [ ] Teste: `python app/BMO.py`
- [ ] Verifique que dispositivos corretos são exibidos
- [ ] Teste wake word "Ei, BMO"
- [ ] Verifique que áudio de resposta reproduz corretamente

---

**Pronto!** Seu BMO agora usa os dispositivos de áudio que você escolheu! 🎉

Para mais detalhes, consulte `docs/AUDIO_DEVICES.md`.
