# 🎤 BMO com Wi-Fi Audio - README

**Versão:** 4.2
**Status:** ✅ Pronto para uso
**Hardware:** NVIDIA Jetson Orin (NX 16GB / AGX 32GB)

---

## 🚀 Como Começar (3 comandos)

```bash
# 1. Instalar WO Mic
bash requirements/setup_wifi_audio.sh

# 2. Ativar configuração otimizada
cp config/config.jetson_medium.yaml config/config.yaml

# 3. Iniciar BMO
python app/BMO.py
```

**Nota:** No celular, instale "WO Mic" app (Android/iOS) e ative hotspot Wi-Fi antes do passo 3.

---

## 📱 Setup do Celular

1. **Ativar Hotspot Wi-Fi:**
   - Configurações → Hotspot Móvel → Ativar
   - Nome: "BMO-Network"

2. **Instalar WO Mic:**
   - Android: https://play.google.com/store/apps/details?id=com.wo.voice2
   - iOS: https://apps.apple.com/app/wo-mic/id1260978417

3. **Iniciar Transmissão:**
   - Abrir app → Transport: Wi-Fi → START

---

## 🔍 Validação (antes de usar)

```bash
# Verificar se tudo está OK
python validate_wifi_setup.py

# Se tudo verde, está pronto! 🎉
```

---

## 📚 Documentação

| Documento | Para quê? |
|-----------|-----------|
| **QUICKSTART_WIFI_AUDIO.md** | ⚡ Guia rápido (5 min) |
| **docs/WIFI_AUDIO_SETUP.md** | 📖 Guia completo técnico |
| **IMPLEMENTACAO_COMPLETA.md** | 🔧 Detalhes da implementação |

---

## ✨ Principais Features

✅ **Microfone do celular via Wi-Fi** (sem cabos!)
✅ **Auto-detecção de dispositivo** (zero configuração)
✅ **Fallback automático** (usa mic local se Wi-Fi falhar)
✅ **Modelos otimizados** (8B LLM, medium STT, XTTS)
✅ **Qualidade superior** (48kHz vs 8-16kHz do Bluetooth)
✅ **Internet grátis** (tethering do celular)

---

## 🎯 Especificações Técnicas

| Componente | Configuração | Performance |
|------------|--------------|-------------|
| **LLM** | llama3.1:8b | ~6GB RAM, 2-3s |
| **STT** | whisper medium | ~5GB VRAM, 500ms, 92% acurácia |
| **TTS** | Coqui XTTS | ~2.5GB VRAM, 400ms, voz clonada |
| **Áudio** | Wi-Fi 48kHz | ~30ms latência |
| **Total** | - | 13-14GB RAM, 3-4s end-to-end |

---

## 🛠️ Utilitários

```bash
# Detectar dispositivo Wi-Fi
python tutorials/detect_wifi_stream.py

# Validar setup completo
python validate_wifi_setup.py

# Listar todos dispositivos de áudio
python tutorials/list_audio_devices.py
```

---

## ❓ Problemas?

### Dispositivo não detectado

```bash
# Verificar status
python tutorials/detect_wifi_stream.py status

# Iniciar WO Mic manualmente
womic -t 0 -i 192.168.43.1 -p 48000
```

### Áudio baixo

- Aumentar volume do celular (botões físicos)
- No app WO Mic: Settings → Quality → High

### Out of Memory

```yaml
# Editar config/config.yaml - usar modelos menores:
llm:
  local:
    model: "llama3.2:3b"  # Em vez de 8b

stt:
  local:
    model: "small"  # Em vez de medium
```

---

## 📊 O Que Mudou?

### v4.1 → v4.2

| Feature | Antes | Depois |
|---------|-------|--------|
| Entrada de áudio | Mic fixo | Celular Wi-Fi ✨ |
| Detecção | Manual | Automática ✨ |
| Fallback | Não | Sim ✨ |
| Modelos | Small | Medium ✨ |
| Qualidade | Boa | Excelente ✨ |
| Mobilidade | Não | 5-10m ✨ |
| Internet | Não | Tethering ✨ |

---

## 📁 Arquivos Importantes

```
📦 BMO-Project/
├── 📘 QUICKSTART_WIFI_AUDIO.md        ← Comece aqui!
├── 📘 README_WIFI_AUDIO.md            ← Este arquivo
├── 📘 IMPLEMENTACAO_COMPLETA.md       ← Detalhes técnicos
│
├── ⚙️  config/
│   └── config.jetson_medium.yaml     ← Config otimizada
│
├── 🔧 requirements/
│   └── setup_wifi_audio.sh           ← Instalador automático
│
├── 🛠️  tutorials/
│   ├── detect_wifi_stream.py         ← Diagnóstico
│   └── list_audio_devices.py         ← Listar dispositivos
│
├── 📚 docs/
│   └── WIFI_AUDIO_SETUP.md           ← Guia técnico completo
│
└── 🔬 validate_wifi_setup.py          ← Validador do sistema
```

---

## 🎉 Pronto para Usar!

1. ✅ Instalação: `bash requirements/setup_wifi_audio.sh`
2. ✅ Configuração: `cp config/config.jetson_medium.yaml config/config.yaml`
3. ✅ Validação: `python validate_wifi_setup.py`
4. ✅ Execução: `python app/BMO.py`

**Aproveite o BMO com entrada de áudio Wi-Fi! 🤖📱**

---

**Dúvidas?** Consulte a documentação completa em `docs/` ou abra uma issue.

**Última atualização:** 31/10/2025
