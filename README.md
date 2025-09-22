# HU Automation

<div align="center">

![HU Automation](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Sistema de automação para geração de Histórias de Usuário usando IA**

Transforme transcrições de reuniões e documentos de requisitos em Histórias de Usuário estruturadas e profissionais.

[🚀 Começar](#-instalação) • [📖 Documentação](#-documentação) • [🤖 Demo](#-demo) • [📧 Contato](#-contato)

</div>

---

## ✨ Características

- 🤖 **Integração com IA**: Suporte para OpenAI GPT e Zello MIND
- 📄 **Múltiplos Formatos**: Processa TXT, PDF, DOC, DOCX e MD
- 📧 **Envio Automático**: Envia resultados por e-mail em HTML ou texto
- 📊 **Validação Inteligente**: Sistema de auto-correção com feedback
- 🎨 **Interface Moderna**: Design profissional e responsivo
- ⚡ **Processamento Rápido**: Geração eficiente de Histórias de Usuário

## 🚀 Instalação

### Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Conta OpenAI (opcional)
- Conta Zello MIND (opcional)
- Configuração de e-mail SMTP

### 1. Clone o repositório

```bash
git clone https://github.com/kassiacosta-z/hu-automation.git
cd hu-automation
```

### 2. Crie um ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
copy env.example .env

# Edite o arquivo .env com suas configurações
notepad .env
```

### 5. Execute a aplicação

```bash
python app.py
```

Acesse `http://localhost:5000` no seu navegador.

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `env.example`:

```env
# Configurações das LLMs
OPENAI_API_KEY=sk-your-openai-api-key-here
ZELLO_API_KEY=your-zello-api-key-here
ZELLO_BASE_URL=https://smartdocs-api-hlg.zello.space

# Configurações de E-mail
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password-here
EMAIL_FROM=your-email@gmail.com
```

### Configuração de E-mail

Para usar o Gmail:
1. Ative a verificação em 2 etapas
2. Gere uma senha de app
3. Use a senha de app no campo `EMAIL_PASSWORD`

## 📖 Documentação

### Estrutura do Projeto

```
hu-automation/
├── app.py                 # Aplicação Flask principal
├── config.py             # Configurações e variáveis de ambiente
├── requirements.txt      # Dependências Python
├── env.example          # Exemplo de configuração
├── .gitignore           # Arquivos ignorados pelo Git
├── README.md            # Documentação principal
├── services/            # Serviços de negócio
│   ├── __init__.py
│   ├── llm_service.py   # Integração com LLMs
│   ├── file_service.py  # Processamento de arquivos
│   ├── email_service.py # Envio de e-mails
│   └── generation_service.py # Geração de HUs
├── prompts/             # Prompts para IA
│   └── user_story_prompts.py
└── templates/           # Interface web
    └── index.html
```

### API Endpoints

#### `GET /api/validate-config`
Verifica o status das configurações.

**Resposta:**
```json
{
  "success": true,
  "config_status": {
    "openai_configured": true,
    "zello_configured": true,
    "email_configured": true
  }
}
```

#### `GET /api/models`
Lista os modelos disponíveis.

**Resposta:**
```json
{
  "success": true,
  "models": {
    "openai": ["gpt-4o-mini", "gpt-4"],
    "zello": ["zello-mind"]
  }
}
```

#### `POST /api/process`
Processa um documento e gera Histórias de Usuário.

**Parâmetros:**
- `file`: Arquivo a ser processado
- `llm_type`: Tipo de LLM (openai/zello)
- `model`: Modelo específico
- `prompt_type`: Tipo de processamento
- `email_recipients`: E-mails destinatários (opcional)
- `email_format`: Formato do e-mail (html/text)

**Resposta:**
```json
{
  "success": true,
  "user_stories": "Conteúdo das Histórias de Usuário...",
  "generation_info": {
    "content": "Conteúdo gerado...",
    "usage": {
      "prompt_tokens": 150,
      "completion_tokens": 300,
      "total_tokens": 450
    }
  },
  "email_result": {
    "success": true,
    "message": "E-mail enviado com sucesso"
  }
}
```

### Tipos de Processamento

1. **Gerar Histórias de Requisitos**: Converte documentos em HUs
2. **Analisar Histórias Existentes**: Melhora HUs já existentes
3. **Refinar História Específica**: Foca em uma HU específica
4. **Gerar Critérios de Aceitação**: Cria critérios detalhados
5. **Estimar Esforço**: Adiciona estimativas de complexidade

## 🎨 Interface

A interface foi projetada com foco na experiência do usuário:

- **Design Moderno**: Paleta de cores profissional (laranja #FF6F00, preto, cinzas)
- **Responsiva**: Funciona perfeitamente em desktop e mobile
- **Drag & Drop**: Arraste arquivos diretamente para upload
- **Feedback Visual**: Status em tempo real do processamento
- **Resultados Destacados**: Syntax highlighting para melhor legibilidade

## 🔧 Desenvolvimento

### Executando em Modo de Desenvolvimento

```bash
# Ative o ambiente virtual
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# Execute com debug
set FLASK_DEBUG=1  # Windows
export FLASK_DEBUG=1  # Linux/Mac
python app.py
```

### Estrutura de Código

- **app.py**: Rotas Flask e orquestração
- **services/**: Lógica de negócio separada por responsabilidade
- **config.py**: Configurações centralizadas
- **templates/**: Interface web em HTML/CSS/JS

### Adicionando Novos Provedores de IA

1. Adicione a configuração em `config.py`
2. Implemente o método em `services/llm_service.py`
3. Atualize a lista de modelos em `app.py`

## 🚀 Deploy

### Deploy Local

```bash
python app.py
```

### Deploy em Produção

Para deploy em produção, considere:

1. **Configuração de Produção**:
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=False`
   - Configuração de servidor WSGI

2. **Variáveis de Ambiente**:
   - Configure todas as variáveis necessárias
   - Use um gerenciador de segredos

3. **Servidor Web**:
   - Nginx + Gunicorn
   - Apache + mod_wsgi
   - Docker container

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📧 Contato

**Kassia Costa** - [@kassiacosta-z](https://github.com/kassiacosta-z)

- Email: kassia.costa@zello.loc.br
- LinkedIn: [Kassia Costa](https://linkedin.com/in/kassia-costa)

## 🙏 Agradecimentos

- OpenAI pela API GPT
- Zello pela integração MIND
- Comunidade Python/Flask
- Todos os contribuidores

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela!**

[⬆ Voltar ao topo](#-hu-automation)

</div>