# 📋 HU Automation - Documentação do Projeto

**Versão:** 2.0  
**Data:** Outubro 2025  
**Status:** Em Desenvolvimento/Produção

---

## 🎯 Visão Geral

O **HU Automation** é uma aplicação web Flask que automatiza a transformação de transcrições de reuniões em Histórias de Usuário (User Stories) estruturadas, utilizando Inteligência Artificial (LLMs).

### Principais Funcionalidades

✅ **Processamento de Documentos** - Upload e extração de texto de TXT, PDF, DOC, DOCX, MD  
✅ **Geração de HU via IA** - Integração com OpenAI GPT e Zello MIND LLM  
✅ **Auto-correção Inteligente** - Validação e refinamento automático das histórias geradas  
✅ **Envio de E-mail** - Notificações automáticas com resultados em HTML/Texto/Anexos  
✅ **Integração Gmail** - Coleta automática de transcrições do Gemini via Gmail API  
✅ **Integração Google Drive** - Armazenamento organizado de transcrições e HUs  
✅ **Sistema de Jobs** - Fila de processamento com rastreamento de status  
✅ **Interface Web Moderna** - Dashboard responsivo com upload drag-and-drop  
✅ **Docker Support** - Containerização completa para deploy simplificado

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Flask)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  index.html  │  │admin_monitor │  │ Static Assets/Logo  │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (app.py)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                            │  │
│  │  • /api/process        • /api/collect-emails             │  │
│  │  • /api/process-file   • /api/repository-stats           │  │
│  │  • /api/models         • /api/recent-jobs                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVIÇOS (services/)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ LLM Service  │  │Gmail Service │  │ GDrive Service      │  │
│  │(OpenAI/Zello)│  │(Domain-Wide) │  │(Upload/Download)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │File Service  │  │Email Service │  │Generation Service   │  │
│  │(PDF/DOCX/TXT)│  │(SMTP)        │  │(HU + Validation)    │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │Repo Monitor  │  │Batch Process │                            │
│  │(File Watch)  │  │(Queue)       │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│               BANCO DE DADOS (SQLAlchemy + SQLite)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Models:                                                  │  │
│  │  • TranscriptionJob    • ProcessingArtifact              │  │
│  │  • ProcessingLog                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 INTEGRAÇÕES EXTERNAS                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ OpenAI API   │  │  Zello MIND  │  │  Google Workspace   │  │
│  │              │  │              │  │  (Gmail + Drive)     │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estrutura de Diretórios

```
hu-automarion 2.0/
├── 📄 app.py                      # Aplicação Flask principal
├── 📄 config.py                   # Configurações centralizadas
├── 📄 database.py                 # Setup SQLAlchemy
├── 📄 requirements.txt            # Dependências Python
├── 📄 Dockerfile                  # Container Docker
├── 📄 docker-compose.yml          # Orquestração Docker
├── 📄 alembic.ini                 # Configuração de migrations
├── 📄 env.example                 # Template de variáveis de ambiente
│
├── 📁 models/                     # Modelos de dados (SQLAlchemy)
│   ├── __init__.py               # TranscriptionJob, ProcessingArtifact, ProcessingLog
│
├── 📁 services/                   # Lógica de negócio
│   ├── llm_service.py            # Integração com LLMs (OpenAI/Zello)
│   ├── gmail_service.py          # Coleta de e-mails via Gmail API
│   ├── gdrive_service.py         # Upload/Download Google Drive
│   ├── email_service.py          # Envio de e-mails SMTP
│   ├── file_service.py           # Extração de texto (PDF/DOCX/TXT)
│   ├── generation_service.py     # Geração e validação de HUs
│   ├── repository_monitor.py     # Monitoramento de repositório
│   ├── batch_processor.py        # Processamento em lote
│   ├── file_tracker.py           # Rastreamento de arquivos
│   └── transcription_queue.py    # Fila de processamento
│
├── 📁 prompts/                    # Templates de prompts para LLM
│   └── user_story_prompts.py     # Prompts especializados em HU
│
├── 📁 migrations/                 # Migrations Alembic
│   ├── versions/
│   │   ├── 0001_initial.py
│   │   └── 0002_gmail_gdrive_fields.py
│   └── env.py
│
├── 📁 templates/                  # Templates HTML (Jinja2)
│   ├── index.html                # Interface principal
│   └── admin_monitor.html        # Dashboard administrativo
│
├── 📁 static/                     # Assets estáticos
│   └── hu_automation_icon.png    # Logo do sistema
│
├── 📁 uploads/                    # Arquivos temporários de upload
├── 📁 test_transcriptions/        # Transcrições para teste
├── 📁 LLM ZELLO MIND/            # Configurações Zello MIND
│   ├── IA_Zello.json
│   └── ZELLO MIND.postman_collection.json
│
└── 📁 venv/                       # Ambiente virtual Python
```

---

## 🔧 Tecnologias Utilizadas

### Backend
- **Python 3.12** - Linguagem principal
- **Flask 3.0.0** - Framework web
- **SQLAlchemy 2.0.32** - ORM para banco de dados
- **Alembic 1.13.2** - Migrations de banco de dados
- **SQLite** - Banco de dados (desenvolvimento)

### Integrações IA
- **OpenAI 1.35.0** - GPT-4, GPT-3.5-turbo
- **Zello MIND** - LLM customizado (API REST)

### Processamento de Arquivos
- **PyPDF2 3.0.1** - Extração de texto PDF
- **python-docx 1.1.0** - Processamento DOCX
- **ReportLab 4.0.7** - Geração de PDFs

### Google APIs
- **google-api-python-client 2.139.0** - Cliente Google APIs
- **google-auth 2.35.0** - Autenticação
- **google-auth-httplib2 0.2.0** - HTTP/2 support
- **google-auth-oauthlib 1.2.1** - OAuth 2.0

### Comunicação
- **requests 2.31.0** - HTTP client
- **httpx 0.27.0** - Async HTTP client
- **email-validator 2.1.0** - Validação de e-mails

### Frontend
- **Jinja2 3.1.2** - Template engine
- **JavaScript Vanilla** - Interatividade
- **CSS3** - Estilização moderna

### DevOps
- **Docker** - Containerização
- **Docker Compose** - Orquestração

---

## 🗄️ Modelo de Dados

### TranscriptionJob
Representa um job de processamento de transcrição.

```python
{
    "id": 1,
    "source_uri": "gmail://user@zello.tec.br/msg123",
    "collaborator_email": "user@zello.tec.br",
    "source_hash": "abc123def456",
    "status": "processed",  # discovered, processing, processed, failed
    "attempts": 1,
    "created_at": "2025-10-01T10:00:00",
    "updated_at": "2025-10-01T10:05:00"
}
```

### ProcessingArtifact
Artefatos gerados durante o processamento.

```python
{
    "id": 1,
    "job_id": 1,
    "type": "json",  # pdf, docx, json
    "path": "/app/artifacts/job_1.json",
    "gdrive_path": "drive://file_id_123",
    "size": 45678,
    "created_at": "2025-10-01T10:05:00"
}
```

### ProcessingLog
Logs de processamento.

```python
{
    "id": 1,
    "job_id": 1,
    "level": "info",  # info, warning, error
    "message": "Processamento iniciado",
    "timestamp": "2025-10-01T10:00:00"
}
```

---

## 🔌 API Endpoints

### Processamento

#### `POST /api/process`
Processa um arquivo e gera Histórias de Usuário.

**Request (multipart/form-data):**
```
file: <arquivo>
provider: "openai" | "zello" | "auto"
output_format: "preview" | "pdf" | "docx"
email: "email1@example.com, email2@example.com"
max_attempts: 3
```

**Response:**
```json
{
  "success": true,
  "user_stories": "...",
  "generation_info": {
    "provider": "openai",
    "attempts": 1,
    "auto_correction_used": false
  }
}
```

#### `POST /api/process-file/{job_id}`
Processa um job específico.

**Query Params:**
- `provider`: openai | zello | auto
- `max_attempts`: número de tentativas
- `email`: destinatários (opcional)

**Response:**
```json
{
  "success": true,
  "message": "Processamento concluído",
  "job": { "id": 123, "status": "processed" },
  "artifact": { "type": "json", "path": "artifacts/job_123.json" }
}
```

### Coleta de E-mails

#### `POST /api/collect-emails`
Coleta e-mails do Gemini via Gmail.

**Request:**
```json
{
  "users": ["user1@zello.tec.br", "user2@zello.tec.br"],
  "max": 20
}
```

**Response:**
```json
{
  "success": true,
  "created": 15,
  "errors": []
}
```

### Monitoramento

#### `GET /api/repository-stats`
Estatísticas do repositório.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_jobs": 150,
    "discovered": 20,
    "processing": 5,
    "processed": 120,
    "failed": 5
  }
}
```

#### `GET /api/recent-jobs?limit=50`
Lista jobs recentes.

**Response:**
```json
{
  "success": true,
  "jobs": [
    {
      "id": 123,
      "source_uri": "gmail://...",
      "status": "processed",
      "created_at": "2025-10-01T10:00:00"
    }
  ]
}
```

### Configuração

#### `GET /api/validate-config`
Valida configurações da aplicação.

**Response:**
```json
{
  "success": true,
  "errors": [],
  "config_status": {
    "openai_configured": true,
    "zello_configured": true,
    "email_configured": true,
    "repository_configured": true
  }
}
```

#### `GET /api/models`
Lista modelos disponíveis de cada LLM.

**Response:**
```json
{
  "success": true,
  "models": {
    "openai": ["gpt-4", "gpt-3.5-turbo"],
    "zello": ["zello-mind-v1"]
  }
}
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# Flask
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# LLMs
OPENAI_API_KEY=sk-...
ZELLO_API_KEY=your-zello-key
ZELLO_BASE_URL=https://api.zello.com

# E-mail (SMTP)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com

# Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads

# Banco de dados
DATABASE_URL=sqlite:///app.db

# Repositório de transcrições
TRANSCRIPTION_REPO_PATH=/path/to/transcriptions

# Google APIs
GOOGLE_CREDENTIALS_JSON=/path/to/service-account.json
GMAIL_DELEGATED_USER=admin@zello.tec.br
GDRIVE_ROOT_FOLDER_ID=1ABC_folder_id_here
```

### Google Service Account Setup

Para usar Gmail e Drive APIs com Domain-Wide Delegation:

1. **Criar Service Account** no Google Cloud Console
2. **Ativar APIs**: Gmail API, Drive API, Admin SDK API
3. **Baixar JSON** de credenciais
4. **Configurar DWD** no Admin Console:
   - Ir para Segurança → API Controls → Domain-wide Delegation
   - Adicionar Service Account com escopos:
     ```
     https://www.googleapis.com/auth/gmail.readonly
     https://www.googleapis.com/auth/drive
     https://www.googleapis.com/auth/admin.directory.user.readonly
     ```

---

## 🐳 Docker

### Dockerfile
```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV FLASK_APP=app.py FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
CMD ["python", "app.py"]
```

### Docker Compose
```yaml
services:
  hu-automation:
    build: .
    container_name: hu-automation-hu-automation-1
    ports:
      - "8080:5000"
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000
    env_file:
      - .env
    volumes:
      - ./:/app
    restart: unless-stopped
```

### Comandos Docker

```bash
# Build e start
docker compose up -d --build

# Parar
docker compose down

# Logs
docker compose logs -f

# Rebuild sem cache
docker compose build --no-cache
```

**Acesso:** http://localhost:8080

---

## 🚀 Fluxos de Trabalho

### 1. Processamento Manual de Arquivo

```
1. Usuário acessa http://localhost:8080
2. Faz upload de arquivo (TXT/PDF/DOCX)
3. Seleciona LLM (OpenAI/Zello)
4. Sistema extrai texto do arquivo
5. LLM gera Histórias de Usuário
6. Sistema valida e corrige automaticamente
7. Resultado exibido na interface
8. Opção de enviar por e-mail
```

### 2. Coleta Automática do Gmail

```
1. Sistema autentica via Service Account
2. Varre Gmail de usuários @zello.tec.br
3. Busca e-mails do Gemini (from:gemini-noreply@google.com)
4. Extrai transcrições de texto
5. Salva no Google Drive (organizado por usuário)
6. Cria job no banco de dados
7. Job aguarda processamento
```

### 3. Processamento de Job

```
1. Job está com status "discovered"
2. Sistema lê transcrição do Drive ou local
3. Envia para LLM com prompt específico
4. LLM gera Histórias de Usuário
5. Sistema valida qualidade
6. Se reprovado, reprocessa (até max_attempts)
7. Se aprovado, salva artefato JSON
8. Atualiza status para "processed"
9. Envia e-mail (se configurado)
```

---

## 🎨 Interface Web

### Página Principal (`/`)
- **Upload de arquivo** com drag-and-drop
- **Seleção de LLM** (OpenAI/Zello)
- **Configuração de saída** (Preview/PDF/DOCX)
- **Status de configuração** em tempo real
- **Preview de resultado** com syntax highlighting
- **Cópia rápida** para clipboard
- **Design responsivo** mobile-friendly

### Dashboard Admin (`/admin/monitor`)
- **Estatísticas do repositório**
- **Lista de jobs recentes**
- **Filtros por status**
- **Ações de reprocessamento**
- **Visualização de logs**

---

## 🔐 Segurança

### Implementado
✅ Variáveis de ambiente para credenciais  
✅ Validação de tipos de arquivo (whitelist)  
✅ Limite de tamanho de upload (16MB)  
✅ CSRF protection (Flask)  
✅ Domain-Wide Delegation para Gmail  
✅ Service Account para Google APIs  

### Recomendações Adicionais
- [ ] Rate limiting nos endpoints
- [ ] Autenticação de usuários (OAuth)
- [ ] HTTPS obrigatório em produção
- [ ] Sanitização de inputs
- [ ] Auditoria de acessos
- [ ] Backup automático do banco

---

## 📊 Monitoramento e Logs

### Logs Disponíveis
- **Flask logs** - Requisições HTTP
- **ProcessingLog** - Eventos de processamento
- **Alembic logs** - Migrations
- **Docker logs** - Container output

### Métricas Rastreadas
- Total de jobs por status
- Taxa de sucesso/falha
- Tempo médio de processamento
- Uso de LLM (tokens)
- Tamanho de arquivos processados

---

## 🐛 Troubleshooting

### Erro: "Gmail não configurado"
**Causa:** GOOGLE_CREDENTIALS_JSON não definido ou inválido  
**Solução:** Configurar Service Account e variável de ambiente

### Erro: "OpenAI/Zello API falhou"
**Causa:** Chave de API inválida ou limite de requisições  
**Solução:** Verificar API_KEY no .env e quotas da API

### Erro: "Falha ao extrair texto do PDF"
**Causa:** PDF com imagens ou criptografado  
**Solução:** Converter PDF para texto antes ou usar OCR

### Container não sobe na porta 8080
**Causa:** Porta já em uso  
**Solução:** `docker ps` para ver conflito, parar outro container

### Versão antiga aparece após rebuild
**Causa:** Cache do browser  
**Solução:** Ctrl+F5 para hard refresh, ou limpar cache

---

## 🔄 Atualizações Recentes

### v2.0 - Outubro 2025
- ✅ Adicionado logo no header (alinhado à esquerda)
- ✅ Migração para porta 8080 no Docker
- ✅ Integração completa Gmail + Drive
- ✅ Sistema de jobs com rastreamento
- ✅ Auto-correção de HUs com validação
- ✅ Docker Compose para deploy
- ✅ Suporte a Domain-Wide Delegation
- ✅ Interface moderna com drag-and-drop

---

## 📝 Próximos Passos

### Curto Prazo
- [ ] Implementar autenticação de usuários
- [ ] Adicionar suporte a mais formatos (Excel, Markdown)
- [ ] Dashboard de métricas e analytics
- [ ] Notificações em tempo real (WebSocket)
- [ ] Exportação em mais formatos (JSON, CSV)

### Médio Prazo
- [ ] Migração para PostgreSQL
- [ ] API REST completa com OpenAPI/Swagger
- [ ] Processamento assíncrono com Celery
- [ ] Cache com Redis
- [ ] Deploy em Kubernetes

### Longo Prazo
- [ ] Integração com Jira/Azure DevOps
- [ ] Treinamento de modelo LLM customizado
- [ ] Análise de sentimento em transcrições
- [ ] Recomendações automáticas de priorização
- [ ] Multi-tenancy para empresas

---

## 👥 Equipe e Suporte

**Desenvolvedor:** Zello Tecnologia  
**Contato:** desenvolvimento@zello.tec.br  
**Repositório:** [GitHub/GitLab interno]  
**Documentação:** Este arquivo

---

## 📄 Licença

Propriedade de Zello Tecnologia.  
Todos os direitos reservados.

---

## 🙏 Agradecimentos

- OpenAI pela API GPT
- Google pela infraestrutura de APIs
- Comunidade Flask e Python
- Time de desenvolvimento Zello

---

**Última atualização:** 01/10/2025  
**Versão do documento:** 1.0

