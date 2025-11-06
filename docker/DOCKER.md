# BMO Docker Guide

Este guia explica como executar o BMO usando Docker/Docker Compose.

## 📋 Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- 2GB+ de RAM disponível
- Porta 5000 livre

## 🚀 Quick Start

### 1. Preparar Configuração

```bash
# Criar diretório de credenciais
mkdir -p credentials

# Copiar e editar configuração
cp config.yaml.example config/config.yaml
nano config/config.yaml  # Ajuste conforme necessário

# Copiar e editar variáveis de ambiente
cp .env.example .env
nano .env  # IMPORTANTE: Configure suas API keys
```

### 2. Adicionar Credenciais (se necessário)

Se você vai usar ferramentas do Google:

```bash
# Coloque suas credenciais Google na pasta credentials/
cp ~/Downloads/google_adc_credentials.json credentials/
cp ~/Downloads/credentials.json credentials/
```

### 3. Build e Start

```bash
# Build da imagem
docker-compose build

# Iniciar o container
docker-compose up -d

# Ver logs
docker-compose logs -f
```

### 4. Acessar

Abra seu navegador em: **http://localhost:5000**

## 🎯 Modos de Operação

### Modo Servidor (Padrão)

```bash
# Iniciar servidor web
docker-compose up -d

# Acesse via navegador
open http://localhost:5000
```

### Modo Autônomo (Com microfone)

**Nota:** Requer acesso a dispositivos de áudio do host.

1. Descomente as linhas no `docker-compose.yml`:
```yaml
devices:
  - /dev/snd:/dev/snd
```

2. Execute:
```bash
docker-compose run --rm bmo standalone
```

## 📁 Estrutura de Volumes

O Docker Compose mapeia os seguintes diretórios:

| Local | Container | Descrição |
|-------|-----------|-----------|
| `./config/config.yaml` | `/app/config/config.yaml` | Configuração principal |
| `./config/prompts.yaml` | `/app/config/prompts.yaml` | Prompts do LLM |
| `./.env` | `/app/.env` | Variáveis de ambiente/API keys |
| `./credentials/` | `/app/credentials/` | Credenciais Google |
| `./custom_models/` | `/app/custom_models/` | Modelos wake-word e voice samples |
| `bmo_cache` (volume) | `/app/.cache` | Cache do Spotify (persistente) |

## ⚙️ Comandos Úteis

```bash
# Ver status
docker-compose ps

# Ver logs em tempo real
docker-compose logs -f

# Parar o container
docker-compose stop

# Parar e remover
docker-compose down

# Rebuild após mudanças
docker-compose up -d --build

# Executar shell no container
docker-compose exec bmo bash

# Ver recursos usados
docker stats bmo
```

## 🔧 Configuração Avançada

### Ajustar Recursos

Edite `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'      # Aumentar CPUs
      memory: 4G       # Aumentar RAM
```

### Usar Rede Host (Linux)

Para melhor acesso a dispositivos locais:

```yaml
network_mode: host
```

### Variáveis de Ambiente

Adicione no `docker-compose.yml` ou `.env`:

```yaml
environment:
  - GROQ_API_KEY=sua_chave_aqui
  - SPOTIPY_CLIENT_ID=seu_id_aqui
  - SPOTIPY_CLIENT_SECRET=seu_secret_aqui
```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs

# Verificar configuração
docker-compose config
```

### API keys não funcionam

1. Verifique se o `.env` está configurado
2. Recrie o container: `docker-compose up -d --force-recreate`

### Sem acesso ao áudio

1. Descomente `devices: /dev/snd` no docker-compose.yml
2. Verifique permissões: `ls -l /dev/snd`
3. Adicione seu usuário ao grupo audio: `sudo usermod -aG audio $USER`

### Google OAuth não funciona

OAuth requer acesso ao navegador do host. Para Calendar:

1. Execute fora do Docker na primeira vez para autenticar
2. O `credentials/token.json` será criado
3. Monte o token no container via volume

## 🔒 Segurança

**IMPORTANTE:**

- ❌ Nunca commite `.env` ou `credentials/` no git
- ✅ Use `.env` para secrets, não `docker-compose.yml`
- ✅ O container roda como usuário não-root (`bmo`)
- ✅ Credenciais são montadas como read-only (`:ro`)

## 📊 Monitoramento

### Healthcheck

O container tem healthcheck automático:

```bash
# Ver status de saúde
docker-compose ps
```

### Logs

```bash
# Últimas 100 linhas
docker-compose logs --tail=100

# Logs de erro
docker-compose logs | grep ERROR
```

## 🚫 Limitações do Docker

O modo Docker é recomendado para **servidor web**. Limitações no modo autônomo:

- ⚠️ Acesso a microfone/alto-falante é complexo
- ⚠️ OAuth via navegador requer configuração extra
- ⚠️ Latência ligeiramente maior

**Para melhor experiência com wake-word e microfone, use instalação nativa:**

```bash
bash requirements/install_desktop.sh
source venv/bin/activate
python app/BMO.py
```

## 🔄 Atualizações

```bash
# Puxar código atualizado
git pull

# Rebuild
docker-compose up -d --build

# Limpar imagens antigas
docker image prune
```

## 📝 Exemplo Completo

```bash
# 1. Clone e prepare
git clone <repo>
cd BMO-Project
mkdir -p credentials

# 2. Configure
cp config.yaml.example config/config.yaml
cp .env.example .env
nano .env  # Configure API keys

# 3. Build e start
docker-compose up -d

# 4. Acesse
open http://localhost:5000

# 5. Monitore
docker-compose logs -f
```

## 🆘 Ajuda

- **Logs:** `docker-compose logs -f`
- **Status:** `docker-compose ps`
- **Shell:** `docker-compose exec bmo bash`
- **Docs:** `docs/` no repositório
- **Issues:** GitHub Issues

---

**Dica:** Para desenvolvimento, use instalação nativa. Docker é ideal para deploy/produção do modo servidor.
