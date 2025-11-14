# ⚡ HU Automation - Quick Start Guide

**Guia de Referência Rápida - 5 Minutos para Começar**

---

## 🚀 Instalação Rápida

```bash
# 1. Baixar projeto
git clone https://github.com/kassiacosta-z/hu-automation.git
cd hu-automation

# 2. Criar ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar .env
cp env.example .env
# Edite o .env com suas chaves

# 5. Inicializar banco
python database.py

# 6. Rodar
python app.py
```

**Acesse:** http://127.0.0.1:5000

---

## 🔧 Configuração Mínima (.env)

```env
# Obrigatório
ZELLO_API_KEY=sua-chave-aqui
ZELLO_BASE_URL=https://smartdocs-api-hlg.zello.space

# Opcional (para emails)
EMAIL_USERNAME=seu-email@gmail.com
EMAIL_PASSWORD=senha-de-app-16-digitos
EMAIL_FROM=seu-email@gmail.com

# Padrão
FLASK_PORT=5000
DATABASE_URL=sqlite:///app.db
```

---

## 📁 Estrutura Principal

```
hu-automation/
├── app.py                 # Servidor Flask principal
├── config.py              # Configurações
├── .env                   # Suas credenciais (não compartilhe!)
│
├── models/                # Banco de dados
├── services/              # Lógica do sistema
│   ├── llm_service.py    # IA (OpenAI/Zello)
│   ├── email_service.py  # Envio de email
│   └── file_service.py   # Leitura de arquivos
│
├── templates/             # Páginas HTML
│   └── index.html        # Interface principal
│
└── prompts/               # Instruções para IA
    └── user_story_prompts.py
```

---

## 🎯 Como Usar

### Upload Manual
1. Acesse http://127.0.0.1:5000
2. Arraste arquivo (TXT, PDF, DOCX, MD)
3. Escolha provedor (Zello/OpenAI)
4. Clique "Processar"
5. Copie resultado

### Via API
```bash
curl -X POST http://localhost:5000/api/process \
  -F "file=@transcrição.txt" \
  -F "provider=zello" \
  -F "email=destino@empresa.com"
```

---

## 🔄 Comandos Úteis

```bash
# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Rodar servidor
python app.py

# Aplicar migrations
alembic upgrade head

# Ver status do banco
alembic current

# Criar nova migration
alembic revision --autogenerate -m "descrição"

# Instalar nova dependência
pip install pacote
pip freeze > requirements.txt

# Desativar ambiente
deactivate
```

---

## 🐳 Docker (Alternativa)

```bash
# Build e rodar
docker compose up -d --build

# Ver logs
docker compose logs -f

# Parar
docker compose down

# Rebuild
docker compose build --no-cache
```

**Acesse:** http://localhost:8080

---

## 🛠️ Modificações Comuns

### Mudar Porta
```env
# .env
FLASK_PORT=8080
```

### Adicionar Formato de Arquivo
```python
# config.py
ALLOWED_EXTENSIONS: set = {'txt', 'pdf', 'doc', 'docx', 'md', 'xlsx'}
```

### Modificar Prompt da IA
```python
# prompts/user_story_prompts.py
SYSTEM_PROMPT = """
Suas instruções customizadas aqui...
"""
```

### Alterar Cores da Interface
```html
<!-- templates/index.html -->
<style>
:root {
    --primary-color: #6f42c1;  /* Sua cor */
}
</style>
```

---

## 🔍 Endpoints da API

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Interface web |
| `/api/process` | POST | Processar arquivo |
| `/api/models` | GET | Listar modelos LLM |
| `/api/recent-jobs` | GET | Jobs recentes |
| `/api/repository-stats` | GET | Estatísticas |
| `/api/validate-config` | GET | Validar config |

---

## ⚠️ Troubleshooting Rápido

### Porta em uso
```bash
# Mude a porta no .env
FLASK_PORT=8080
```

### Python não reconhecido
```bash
# Use 'py' no Windows
py --version
py app.py
```

### Erro de API Key
```env
# Verifique se está correto no .env (sem espaços)
ZELLO_API_KEY=chave-aqui
```

### Email não envia
```env
# Use Senha de App do Gmail
# https://myaccount.google.com/apppasswords
EMAIL_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### Módulo não encontrado
```bash
# Reinstale dependências
pip install -r requirements.txt
```

---

## 📚 Links Úteis

- **Guia Completo:** `GUIA_INICIANTE_COMPLETO.md`
- **Guia Avançado:** `GUIA_AVANCADO_MODIFICACOES.md`
- **Documentação:** `DOCUMENTACAO_PROJETO.md`
- **README:** `README.md`

---

## 🎓 Próximos Passos

1. ✅ **Básico:** Use a interface web para processar arquivos
2. 📖 **Intermediário:** Leia `GUIA_INICIANTE_COMPLETO.md`
3. 🔧 **Avançado:** Leia `GUIA_AVANCADO_MODIFICACOES.md`
4. 🚀 **Deploy:** Configure produção com Docker/AWS/Heroku

---

## 📞 Suporte

**Email:** kassia.costa@zello.tec.br  
**Docs:** Veja os outros guias desta pasta

---

**⏱️ Tempo total de setup: 5-10 minutos**

*Última atualização: Novembro 2025*


