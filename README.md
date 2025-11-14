# 🚀 HU Automation 2.0

Sistema de automação de Histórias de Usuário que transforma transcrições de reuniões em Histórias de Usuário estruturadas usando IA (Zello MIND).

## 📋 Visão Geral

O HU Automation 2.0 é uma aplicação web desenvolvida em Flask que processa transcrições (TXT, PDF, DOC, DOCX, MD) e gera Histórias de Usuário completas e estruturadas seguindo o padrão ProgressoGov.

### ✨ Funcionalidades

- ✅ **Upload Manual**: Interface web para upload de arquivos
- ✅ **Extração Automática**: Suporta múltiplos formatos (TXT, PDF, DOC, DOCX, MD)
- ✅ **Geração com IA**: Usa Zello MIND para gerar HUs estruturadas
- ✅ **Template ProgressoGov**: Formato completo com 10 seções obrigatórias
- ✅ **Envio por E-mail**: Opção de envio automático por e-mail (HTML ou texto)
- ✅ **Interface Moderna**: Design profissional e responsivo
- ✅ **Barra de Progresso**: Feedback visual durante o processamento
- ✅ **Histórico**: Banco de dados SQLite para rastreamento de jobs

## 🛠️ Pré-requisitos

- Python 3.10 ou superior
- ✅ **Zello MIND API Key** (JÁ VEM CONFIGURADA!)
- SMTP configurado para envio de e-mails (opcional)

## 📦 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/kassiacosta-z/hu-automation.git
cd hu-automation
```

### 2. Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure suas credenciais:

```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Flask
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=True

# Zello MIND API (JÁ VEM CONFIGURADA!)
ZELLO_API_KEY=LYIB_WidIVeADAXylsTDcx-6oaWoq5CfPL9W_-bZ5Ag=
ZELLO_BASE_URL=https://smartdocs-api-hlg.zello.space

# Email (SMTP) - Opcional
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app
EMAIL_FROM=seu-email@gmail.com

# Database
DATABASE_URL=sqlite:///app.db

# Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=uploads
```

## 🚀 Como Usar

### Executar a Aplicação

```bash
python app.py
```

A aplicação estará disponível em: **http://127.0.0.1:5000/**

### Fluxo de Uso

1. **Acessar a Interface**: Abra o navegador em http://127.0.0.1:5000/
2. **Upload do Arquivo**: Clique ou arraste um arquivo (TXT, PDF, DOC, DOCX, MD)
3. **Configurar Opções**:
   - E-mail destinatário (opcional)
   - Formato de saída (Preview, HTML, Texto)
4. **Processar**: Clique em "Processar Documento"
5. **Visualizar Resultado**: As HUs geradas aparecem na tela
6. **E-mail**: Se configurado, um e-mail será enviado automaticamente

## 📊 Formato das Histórias de Usuário

Cada História de Usuário gerada contém:

1. **Nome da História**: Formato [Funcionalidade] – [Ação principal]
2. **História de Usuário**: Formato "Como [tipo de usuário], quero [funcionalidade] para [benefício]"
3. **Tipo**: Feature / Melhoria / Bug / Enabler
4. **Critérios de Aceitação**: Numerados e verificáveis
5. **Permissões e Acessos**: Leitor, Gestor, Alta gestão
6. **Regras de Negócios**: Políticas e restrições
7. **Requisitos Técnicos**: Integrações e arquitetura
8. **Regras de Interface**: Comportamento de componentes
9. **Campos e Componentes de UI**: Tabela Markdown
10. **Cenários de Teste**: Formato BDD (Dado/Quando/Então)

## 🏗️ Estrutura do Projeto

```
hu-automation/
├── app.py                      # Aplicação principal Flask
├── config.py                   # Configurações e variáveis de ambiente
├── database.py                 # Configuração do banco de dados
├── requirements.txt            # Dependências Python
├── .env.example                # Exemplo de variáveis de ambiente
├── .env                        # Suas configurações (não versionar!)
├── models/
│   └── __init__.py            # Modelos SQLAlchemy
├── services/
│   ├── llm_service.py         # Integração com Zello MIND
│   ├── email_service.py       # Envio de e-mails
│   ├── file_service.py        # Processamento de arquivos
│   ├── generation_service.py  # Geração e validação de HUs
│   └── repository_monitor.py  # Monitoramento de repositório
├── prompts/
│   └── user_story_prompts.py  # Templates de prompts
├── templates/
│   ├── index.html             # Interface principal
│   └── admin_monitor.html     # Painel administrativo
└── static/
    └── hu_automation_icon.png # Logo da aplicação
```

## 🔧 Configuração Avançada

### Banco de Dados

A aplicação usa SQLite por padrão. Para migrar para PostgreSQL:

1. Atualize `DATABASE_URL` no `.env`:
   ```env
   DATABASE_URL=postgresql://usuario:senha@localhost/hu_automation
   ```

2. Execute as migrações Alembic:
   ```bash
   alembic upgrade head
   ```

### API Zello MIND

A aplicação usa **exclusivamente** a Zello MIND para gerar Histórias de Usuário.

**🎉 Boa notícia:** A chave JÁ VEM CONFIGURADA!
- Você NÃO precisa criar conta
- Você NÃO precisa solicitar chave
- Você NÃO precisa configurar nada
- Basta copiar o `env.example` e está pronto!

### Envio de E-mails

Para habilitar o envio automático de e-mails:

1. **Gmail**: Use "Senha de App" em vez da senha normal
   - Acesse: https://myaccount.google.com/apppasswords
   - Gere uma senha de app e use no `.env`

2. **Outros provedores**: Configure o SMTP apropriado

## 🐛 Troubleshooting

### Erro: "Zello API key não configurada"

**Solução**: Verifique se `ZELLO_API_KEY` está configurado no arquivo `.env`

### Erro: "Timeout na requisição Zello"

**Solução**: A API Zello pode demorar até 60 segundos para responder. Aguarde o processamento completar.

### Erro: "Email não enviado"

**Solução**: 
1. Verifique as credenciais SMTP no `.env`
2. Use "Senha de App" se estiver usando Gmail
3. Verifique se o e-mail destinatário está correto

### Interface não carrega

**Solução**:
1. Verifique se a porta 5000 está disponível
2. Execute `python app.py` novamente
3. Acesse http://127.0.0.1:5000/

## 📝 Changelog

### v2.0.0 (2025-10-27)
- ✅ Implementação completa do HU Automation 2.0
- ✅ Template ProgressoGov com 10 seções obrigatórias
- ✅ Interface web moderna e responsiva
- ✅ Integração com Zello MIND
- ✅ Upload manual de arquivos
- ✅ Geração automática de HUs
- ✅ Envio por e-mail (HTML/Texto)
- ✅ Banco de dados SQLite
- ✅ Barra de progresso e feedback visual

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é propriedade da empresa e está sob licença proprietária.

## 📞 Suporte

Para suporte técnico ou dúvidas:
- 📧 Email: kassia.costa@zello.tec.br
- 📱 Issues: [GitHub Issues](https://github.com/kassiacosta-z/hu-automation/issues)

---

**Desenvolvido com ❤️ para automatizar a criação de Histórias de Usuário**