# 🤖 BMO para NVIDIA Jetson Orin

## 🚀 Instalação Rápida (5 minutos)

```bash
# 1. Clonar repositório
git clone https://github.com/seu-usuario/BMO-Project.git
cd BMO-Project

# 2. Executar script de instalação automática
bash install_jetson.sh

# 3. Gravar amostra de voz (10 segundos)
arecord -f cd -d 10 bmo_voice_sample.wav

# 4. Iniciar BMO
source venv/bin/activate
python app/BMO.py
```

## 📊 Configuração Recomendada

### Jetson Orin Nano/NX 8GB
```yaml
llm:
  local:
    model: "llama3.2:3b"  # Leve
stt:
  local:
    model: "tiny"  # Rápido
tts:
  engine: "coqui"  # ou "piper" se muito lento
```

### Jetson Orin NX 16GB (Recomendado)
```yaml
llm:
  local:
    model: "llama3.1:8b"  # Balanceado
stt:
  local:
    model: "small"  # Boa qualidade
    device: "cuda"  # GPU!
tts:
  engine: "coqui"  # XTTS com GPU
```

### AGX Orin 32GB
```yaml
llm:
  local:
    model: "gemma2:9b"  # Alta qualidade
stt:
  local:
    model: "medium"  # Melhor qualidade
    device: "cuda"
tts:
  engine: "coqui"  # XTTS
```

## ⚡ Performance Esperada

| Componente | Latência | GPU |
|------------|----------|-----|
| Wake Word | ~80ms | 0% |
| VAD | ~1ms | 0% |
| STT (small+GPU) | ~300ms | 40% |
| LLM (8B) | ~1-3s | 60% |
| TTS (XTTS+GPU) | ~300ms | 70% |
| **Total** | **2-5s** | - |

## 🎯 Vantagens na Jetson

- ✅ **100% Local**: Zero dependência de cloud
- ✅ **GPU Integrada**: Acelera STT e TTS
- ✅ **Privacidade**: Dados nunca saem do dispositivo
- ✅ **Baixa Latência**: Comparável ou melhor que cloud
- ✅ **Custo Zero**: Sem APIs pagas
- ✅ **Offline**: Funciona sem internet

## 📖 Documentação Completa

- **Setup Detalhado**: `docs/JETSON_ORIN_DEPLOYMENT.md`
- **Config Exemplo**: `config.jetson.yaml`
- **Modelos Locais**: `docs/LOCAL_MODELS.md`
- **Arquitetura**: `docs/ARCHITECTURE_FLEXIBILITY.md`

## 🔧 Comandos Úteis

```bash
# Modo de performance máxima
sudo nvpmodel -m 0
sudo jetson_clocks

# Monitorar recursos
sudo jtop

# Ver GPU usage
nvidia-smi

# Testar Ollama
ollama run llama3.1:8b "Olá"

# Testar faster-whisper
python -c "from faster_whisper import WhisperModel; print('OK')"
```

## 🐛 Problemas Comuns

### "CUDA out of memory"
→ Use modelo menor: `llama3.2:3b`

### PyTorch sem CUDA
→ Instale wheel oficial da NVIDIA (ver docs)

### Ollama lento
→ Verifique se está usando GPU: `nvidia-smi`

### Sistema superaquece
→ Adicione cooling ativo (ventilador)

## 💡 Dicas

1. **Sempre use `device: "cuda"`** no STT
2. **XTTS requer GPU** para ser viável
3. **Configure swap de 8GB** mínimo
4. **Use `sudo jetson_clocks`** durante uso
5. **Monitore com `jtop`** para otimizar

## 🎉 Resultado

Com Jetson Orin NX 16GB + configuração otimizada:

```
BMO totalmente funcional, 100% local, privado,
com latência de 2-5s por interação!
```

**Melhor que cloud para edge AI!** 🚀

---

**Suporte**: Veja `docs/JETSON_ORIN_DEPLOYMENT.md` para guia completo
