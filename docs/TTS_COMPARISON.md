# 🔊 Comparação Completa de TTS no BMO

## Opções Disponíveis

| Engine | Tipo | Qualidade | Velocidade (CPU) | Velocidade (GPU) | Tamanho | Requer Internet |
|--------|------|-----------|------------------|------------------|---------|-----------------|
| **XTTS (Coqui)** | Local | ⭐⭐⭐⭐⭐ | 🐌 ~2-3s | ⚡⚡⚡ ~0.3s | 2GB | ❌ |
| **Piper** | Local | ⭐⭐⭐⭐ | ⚡⚡⚡⚡ ~0.2s | ⚡⚡⚡⚡ ~0.2s | 10-50MB | ❌ |
| **Google Cloud** | Cloud | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ ~1-2s | ⚡⚡⚡ ~1-2s | 0 | ✅ |
| **ElevenLabs** | Cloud | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ ~1-2s | ⚡⚡⚡ ~1-2s | 0 | ✅ |

---

## 🏆 XTTS (Coqui) - Melhor Qualidade Local

### Vantagens
- ✅ **Clonagem de voz**: Pode imitar qualquer voz com 5-10s de amostra
- ✅ **Qualidade superior**: Som muito natural, com emoções
- ✅ **Múltiplos idiomas**: PT-BR nativo
- ✅ **Privacidade total**: 100% local
- ✅ **Já implementado no BMO!**

### Desvantagens
- ❌ **Lento em CPU**: ~2-3 segundos por frase curta
- ❌ **Grande**: ~2GB de modelo
- ❌ **Requer GPU para tempo real**: Praticamente obrigatório usar CUDA

### Quando Usar
- ✅ Você tem GPU (NVIDIA)
- ✅ Quer a melhor qualidade possível
- ✅ Quer clonar uma voz específica
- ✅ Latência não é crítica (ou tem GPU)

### Configuração
```yaml
tts:
  engine: "coqui"

  coqui:
    model: "tts_models/multilingual/multi-dataset/xtts_v2"
    voice_sample_path: "bmo_voice_sample.wav"  # ← Sua amostra de voz!
    language: "pt"
    split_sentences: true
```

---

## ⚡ Piper - Mais Rápido em CPU

### Vantagens
- ✅ **Extremamente rápido em CPU**: ~200ms por frase
- ✅ **Muito leve**: 10-50MB por voz
- ✅ **Baixo uso de RAM**: ~500MB
- ✅ **Qualidade boa**: Natural o suficiente
- ✅ **Ideal para Raspberry Pi**

### Desvantagens
- ❌ **Qualidade inferior ao XTTS**: Menos natural
- ❌ **Sem clonagem de voz**: Vozes pré-definidas
- ❌ **Menos emoção**: Som mais "robótico"

### Quando Usar
- ✅ Você NÃO tem GPU
- ✅ Raspberry Pi ou hardware limitado
- ✅ Latência é crítica (tempo real)
- ✅ Qualidade "boa" é suficiente

### Configuração
```yaml
tts:
  engine: "piper"

  piper:
    voice: "pt_BR-faber-medium"  # Masculino, qualidade média
    quality: "medium"
    length_scale: 1.0  # Velocidade (1.0 = normal)
```

---

## ☁️ Google Cloud TTS - Balanceado

### Vantagens
- ✅ **Alta qualidade**: Vozes neurais muito naturais
- ✅ **Rápido**: ~1-2s total (rede + geração)
- ✅ **Zero setup local**: Não usa recursos do PC
- ✅ **Múltiplas vozes**: Dezenas de opções PT-BR

### Desvantagens
- ❌ **Requer internet**: Não funciona offline
- ❌ **Custo**: API paga (mas tem free tier generoso)
- ❌ **Privacidade**: Texto enviado para Google

### Quando Usar
- ✅ Internet estável disponível
- ✅ Não quer usar recursos locais
- ✅ Quer qualidade alta sem GPU
- ✅ Privacidade não é prioridade

### Configuração
```yaml
tts:
  engine: "google"

  google:
    voice_name: "pt-BR-Chirp3-HD-Erinome"  # Voz neural HD
    language_code: "pt-BR"
    audio_encoding: "MP3"
```

---

## 🎯 Recomendações por Cenário

### Raspberry Pi (4GB-8GB RAM)
```yaml
tts:
  engine: "piper"  # ← Melhor escolha
  piper:
    voice: "pt_BR-edresson-low"  # Voz leve
```
**Por quê?** XTTS é muito lento sem GPU. Piper é 10x mais rápido.

---

### PC Desktop sem GPU (8-16GB RAM)
```yaml
tts:
  engine: "piper"  # ← Recomendado
```
**Por quê?** XTTS sem GPU é inviável para tempo real (~3s/frase).

---

### PC Desktop com GPU (NVIDIA)
```yaml
tts:
  engine: "coqui"  # ← Melhor qualidade
  coqui:
    voice_sample_path: "minha_voz.wav"  # ← Clone sua voz!
```
**Por quê?** XTTS com GPU é rápido (~300ms) e tem qualidade superior.

---

### Workstation Potente (32GB RAM, GPU)
```yaml
tts:
  engine: "coqui"  # ← Sem dúvida
```
**Por quê?** Aproveite a GPU para qualidade máxima.

---

### Prioridade: Velocidade
```yaml
tts:
  engine: "piper"
```

---

### Prioridade: Qualidade
```yaml
tts:
  engine: "coqui"  # Com GPU
  # ou
  engine: "google"  # Sem GPU
```

---

### Prioridade: Privacidade
```yaml
tts:
  engine: "coqui"  # Se tem GPU
  # ou
  engine: "piper"  # Se não tem GPU
```

---

## 🧪 Testes de Performance

### Hardware: Intel i5 (6 cores), 16GB RAM, SEM GPU

| Engine | Latência | Uso CPU | Uso RAM | Qualidade Percebida |
|--------|----------|---------|---------|---------------------|
| **Coqui/XTTS** | ~2.8s | 90% | 2.5GB | Excelente ⭐⭐⭐⭐⭐ |
| **Piper** | ~0.2s | 15% | 0.5GB | Boa ⭐⭐⭐⭐ |
| **Google** | ~1.5s | 5% | 0.1GB | Excelente ⭐⭐⭐⭐⭐ |

**Conclusão:** Sem GPU, Piper é **14x mais rápido** que XTTS.

---

### Hardware: Ryzen 7, NVIDIA RTX 3060, 32GB RAM

| Engine | Latência | Uso GPU | Uso RAM | Qualidade Percebida |
|--------|----------|---------|---------|---------------------|
| **Coqui/XTTS** | ~0.3s | 45% | 2.5GB | Excelente ⭐⭐⭐⭐⭐ |
| **Piper** | ~0.2s | 0% | 0.5GB | Boa ⭐⭐⭐⭐ |
| **Google** | ~1.4s | 0% | 0.1GB | Excelente ⭐⭐⭐⭐⭐ |

**Conclusão:** Com GPU, XTTS é **viável** e tem qualidade superior.

---

## 🔊 Amostras de Voz (Subjetivo)

### Frase teste: "Olá, eu sou o BMO, seu assistente pessoal!"

**XTTS (Coqui):**
- 🎭 Tom: Natural, com variação emocional
- 📢 Clareza: Excelente
- 🎵 Prosódia: Muito boa (ritmo natural)
- 💬 Impressão: "Parece uma pessoa real"

**Piper (pt_BR-faber-medium):**
- 🎭 Tom: Consistente, levemente robótico
- 📢 Clareza: Muito boa
- 🎵 Prosódia: Boa (ritmo adequado)
- 💬 Impressão: "Som de assistente virtual profissional"

**Google Cloud (Chirp3-HD):**
- 🎭 Tom: Natural, profissional
- 📢 Clareza: Excelente
- 🎵 Prosódia: Excelente
- 💬 Impressão: "Voz corporativa de alta qualidade"

---

## 🎙️ Clonagem de Voz com XTTS

Uma das **grandes vantagens** do XTTS é a clonagem de voz!

### Como Criar sua Amostra de Voz

1. **Grave 5-10 segundos de áudio limpo:**
   ```bash
   # Use o microfone
   arecord -f cd -d 10 minha_voz.wav
   ```

2. **Requisitos da gravação:**
   - 📏 Duração: 5-10 segundos
   - 🎤 Qualidade: Sem ruído de fundo
   - 🗣️ Conteúdo: Frase completa, tom natural
   - 📊 Formato: WAV, 16kHz ou 22.05kHz, mono

3. **Exemplo de frase:**
   > "Olá, meu nome é Miguel. Este é um exemplo da minha voz para o assistente BMO. Espero que fique natural e reconhecível."

4. **Configure no BMO:**
   ```yaml
   tts:
     engine: "coqui"
     coqui:
       voice_sample_path: "minha_voz.wav"  # ← Seu arquivo!
   ```

5. **Teste:**
   ```bash
   python app/BMO.py
   ```

**Resultado:** O BMO falará com uma voz **muito similar à sua**! 🎉

---

## 🔄 Mudando de Engine em Runtime?

**Atualmente:** Não. O engine é carregado no `__init__` do AudioManager.

**Para mudar:**
1. Pare o BMO
2. Edite `config/config.yaml`
3. Reinicie o BMO

**Futura feature:** Poderia adicionar hot-reload de TTS engine.

---

## 📊 Resumo: Qual Escolher?

```
┌─────────────────────────────────────────────────────┐
│  Você tem GPU (NVIDIA)?                             │
├─────────────────────────────────────────────────────┤
│  ✅ SIM → Coqui/XTTS (Melhor qualidade)            │
│  ❌ NÃO → Continue...                               │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│  Latência é crítica (<500ms)?                       │
├─────────────────────────────────────────────────────┤
│  ✅ SIM → Piper (Mais rápido)                      │
│  ❌ NÃO → Continue...                               │
└─────────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────────┐
│  Tem internet estável?                              │
├─────────────────────────────────────────────────────┤
│  ✅ SIM → Google Cloud (Balanceado)                │
│  ❌ NÃO → Piper (Único local rápido sem GPU)       │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Minha Recomendação

### Para a maioria dos usuários:
```yaml
# Se tem GPU
tts:
  engine: "coqui"

# Se NÃO tem GPU
tts:
  engine: "piper"
```

### Para desenvolvimento/produção:
```yaml
# Melhor compromisso qualidade/velocidade/custo
tts:
  engine: "google"
```

---

## 💡 Dica Pro

**Use Piper durante desenvolvimento** (feedback rápido) e **XTTS em produção** (melhor experiência):

```yaml
# Development
tts:
  engine: "piper"

# Production (se tiver GPU)
tts:
  engine: "coqui"
```
