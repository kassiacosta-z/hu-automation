# 📘 HU Automation - Guia Para Iniciantes

**"Como Usar Esta Automação Sem Saber Programação"**

> 🎯 **Objetivo deste guia**: Ensinar qualquer pessoa, mesmo sem conhecimento técnico, a instalar, configurar, usar e modificar este sistema de automação de Histórias de Usuário.

---

## 📚 Índice

1. [O Que Você Vai Aprender](#1-o-que-você-vai-aprender)
2. [O Que É Este Sistema?](#2-o-que-é-este-sistema)
3. [Preparando Seu Computador](#3-preparando-seu-computador)
4. [Baixando o Projeto](#4-baixando-o-projeto)
5. [Configurando o Sistema](#5-configurando-o-sistema)
6. [Rodando Pela Primeira Vez](#6-rodando-pela-primeira-vez)
7. [Como Usar o Sistema](#7-como-usar-o-sistema)
8. [Modificando Configurações](#8-modificando-configurações)
9. [Entendendo a Estrutura](#9-entendendo-a-estrutura)
10. [Fazendo Pequenas Alterações](#10-fazendo-pequenas-alterações)
11. [Problemas Comuns e Soluções](#11-problemas-comuns-e-soluções)
12. [Glossário de Termos](#12-glossário-de-termos)

---

## 1. O Que Você Vai Aprender

Depois de ler este guia, você será capaz de:

- ✅ **Instalar** todas as ferramentas necessárias no seu computador
- ✅ **Baixar** o projeto do repositório online
- ✅ **Configurar** as chaves de API e senhas necessárias
- ✅ **Rodar** o sistema no seu computador
- ✅ **Usar** a interface web para processar transcrições
- ✅ **Modificar** configurações básicas (emails, textos, comportamentos)
- ✅ **Resolver** problemas comuns que podem aparecer

---

## 2. O Que É Este Sistema?

### 2.1 Explicação Simples

Este sistema é como um **assistente robô** que:

1. **Recebe** uma transcrição de reunião (arquivo de texto)
2. **Lê** todo o conteúdo
3. **Transforma** em Histórias de Usuário estruturadas
4. **Envia** por email ou mostra na tela

### 2.2 Como Funciona?

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Você faz   │      │  Sistema    │      │  Sistema    │
│  upload de  │ ───► │  usa IA     │ ───► │  mostra o   │
│  arquivo    │      │  para ler   │      │  resultado  │
└─────────────┘      └─────────────┘      └─────────────┘
```

### 2.3 O Que Você Precisa Fornecer?

- ✅ Uma transcrição de reunião (arquivo TXT, PDF, DOCX, MD)
- ✅ Chaves de API da IA (OpenAI ou Zello MIND)
- ✅ (Opcional) Configurações de email para envio automático

---

## 3. Preparando Seu Computador

### 3.1 Verificando Seu Sistema Operacional

Este guia funciona para:
- ✅ **Windows** (10 ou superior)
- ✅ **macOS** (versão recente)
- ✅ **Linux** (Ubuntu, Debian, etc.)

**Como saber qual versão do Windows você tem?**
1. Pressione `Windows + R`
2. Digite `winver` e pressione Enter
3. Verá a versão aparecer

---

### 3.2 Instalando o Python

Python é a "linguagem" que o sistema usa para funcionar.

#### **No Windows:**

1. **Baixar o instalador:**
   - Acesse: https://www.python.org/downloads/
   - Clique em "Download Python 3.12.x" (versão mais recente)

2. **Instalar:**
   - Execute o arquivo baixado
   - ⚠️ **IMPORTANTE**: Marque a caixa "Add Python to PATH"
   - Clique em "Install Now"

3. **Verificar se instalou:**
   - Abra o "Prompt de Comando" (CMD)
     - Pressione `Windows + R`
     - Digite `cmd` e pressione Enter
   - Digite: `python --version`
   - Deve aparecer algo como: `Python 3.12.0`

#### **No macOS:**

```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python@3.12
```

#### **No Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3.12 python3-pip python3-venv
```

---

### 3.3 Instalando o Git

Git é a ferramenta para baixar o projeto.

#### **No Windows:**

1. Baixe: https://git-scm.com/download/win
2. Execute o instalador
3. Use as opções padrão (apenas clique "Next")

#### **No macOS:**

```bash
brew install git
```

#### **No Linux:**

```bash
sudo apt install git
```

**Verificar instalação:**
```bash
git --version
```

---

### 3.4 Instalando um Editor de Código (Opcional mas Recomendado)

Um editor facilita ver e modificar arquivos do projeto.

**Recomendação: VS Code**

1. Baixe: https://code.visualstudio.com/
2. Instale (opções padrão)
3. Abra o VS Code

**Alternativas:**
- Notepad++ (Windows)
- Sublime Text
- Cursor (se você já tem acesso)

---

## 4. Baixando o Projeto

### 4.1 Escolhendo Onde Salvar

1. Escolha uma pasta fácil de lembrar, exemplo:
   - Windows: `C:\Users\SeuNome\Projetos\`
   - macOS/Linux: `~/Projetos/`

2. Crie a pasta se não existir:
   ```bash
   # Windows (no CMD)
   mkdir C:\Users\SeuNome\Projetos
   cd C:\Users\SeuNome\Projetos
   
   # macOS/Linux (no Terminal)
   mkdir ~/Projetos
   cd ~/Projetos
   ```

---

### 4.2 Clonando o Repositório

"Clonar" significa copiar todo o projeto para seu computador.

```bash
git clone https://github.com/kassiacosta-z/hu-automation.git
cd hu-automation
```

**O que aconteceu?**
- Uma pasta chamada `hu-automation` foi criada
- Todos os arquivos do projeto foram copiados para lá

---

### 4.3 Estrutura do Que Foi Baixado

```
hu-automation/
├── app.py                  ← Arquivo principal (não mexa ainda!)
├── config.py               ← Configurações (vamos mexer aqui)
├── requirements.txt        ← Lista de dependências
├── env.example             ← Modelo de configuração
├── models/                 ← Banco de dados
├── services/               ← Lógica do sistema
├── templates/              ← Páginas HTML
└── static/                 ← Imagens e estilos
```

---

## 5. Configurando o Sistema

### 5.1 Criando um Ambiente Virtual

Um "ambiente virtual" é como uma caixa isolada onde instalamos tudo que o projeto precisa, sem bagunçar seu computador.

**Windows (CMD ou PowerShell):**
```bash
cd hu-automation
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd hu-automation
python3 -m venv venv
source venv/bin/activate
```

**Como saber se funcionou?**
- O nome do ambiente aparece antes do prompt: `(venv) C:\...`

---

### 5.2 Instalando Dependências

"Dependências" são bibliotecas/ferramentas que o projeto precisa.

```bash
pip install -r requirements.txt
```

**O que acontece:**
- O Python baixa e instala cerca de 20-30 pacotes
- Pode demorar 2-5 minutos
- Você verá várias linhas passando na tela

**Possíveis erros:**
- Se aparecer "pip not found": Reinstale o Python marcando "Add to PATH"
- Se falhar algum pacote: Tente rodar novamente o comando

---

### 5.3 Configurando Variáveis de Ambiente

As "variáveis de ambiente" são configurações secretas (senhas, chaves de API, etc.).

#### **Passo 1: Copiar o modelo**

**Windows (CMD):**
```bash
copy env.example .env
```

**macOS/Linux:**
```bash
cp env.example .env
```

#### **Passo 2: Abrir o arquivo .env**

**No VS Code:**
1. Abra o VS Code
2. Menu "File" → "Open Folder"
3. Selecione a pasta `hu-automation`
4. No painel esquerdo, clique em `.env`

**Ou use o Bloco de Notas:**
1. Navegue até a pasta do projeto
2. Clique com botão direito no arquivo `.env`
3. "Abrir com" → "Bloco de Notas"

---

#### **Passo 3: Preencher as configurações**

O arquivo `.env` será parecido com isso:

```env
# ================================================================
# CONFIGURAÇÕES DO SISTEMA HU AUTOMATION
# ================================================================
# ⚠️ IMPORTANTE: Este arquivo contém informações sensíveis!
#    NÃO compartilhe este arquivo ou faça commit dele no Git.
# ================================================================

# --------------------------------------------
# CONFIGURAÇÕES DO FLASK (Servidor Web)
# --------------------------------------------
FLASK_HOST=127.0.0.1        # Deixe assim (só você acessa)
FLASK_PORT=5000             # Porta onde o sistema roda
FLASK_DEBUG=True            # True = modo desenvolvimento

# --------------------------------------------
# CHAVES DE API DAS INTELIGÊNCIAS ARTIFICIAIS
# --------------------------------------------

# OpenAI (ChatGPT) - Opcional
# Se quiser usar OpenAI:
# 1. Acesse: https://platform.openai.com/api-keys
# 2. Crie uma chave de API
# 3. Cole aqui (começa com "sk-proj-...")
OPENAI_API_KEY=

# Zello MIND (LLM da empresa) - Recomendado
# Peça a chave com o time de desenvolvimento
ZELLO_API_KEY=sua-chave-zello-aqui
ZELLO_BASE_URL=https://smartdocs-api-hlg.zello.space

# --------------------------------------------
# CONFIGURAÇÕES DE EMAIL (Para envio automático)
# --------------------------------------------

# Servidor SMTP (Gmail)
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# Suas credenciais
# ⚠️ GMAIL: Use "Senha de App", não sua senha normal!
#    Como criar: https://myaccount.google.com/apppasswords
EMAIL_USERNAME=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-de-app-aqui
EMAIL_FROM=seu-email@gmail.com

# --------------------------------------------
# BANCO DE DADOS
# --------------------------------------------
DATABASE_URL=sqlite:///app.db    # Deixe assim (banco local)

# --------------------------------------------
# CONFIGURAÇÕES DE UPLOAD
# --------------------------------------------
MAX_CONTENT_LENGTH=16777216      # 16MB (tamanho máximo)
UPLOAD_FOLDER=uploads            # Pasta de uploads

# --------------------------------------------
# GOOGLE APIS (Opcional - para Gmail e Drive)
# --------------------------------------------
# GOOGLE_CREDENTIALS_JSON=/caminho/para/service-account.json
# GMAIL_DELEGATED_USER=admin@zello.tec.br
# GDRIVE_ROOT_FOLDER_ID=1ABC_folder_id_here
```

---

#### **Passo 4: Obter as chaves de API**

##### **Para Zello MIND:**
1. Entre em contato com o time de desenvolvimento Zello
2. Solicite uma chave de API da Zello MIND
3. Cole a chave no campo `ZELLO_API_KEY`

##### **Para OpenAI (alternativa):**
1. Acesse: https://platform.openai.com/
2. Crie uma conta (se não tiver)
3. Vá em "API Keys"
4. Clique em "Create new secret key"
5. Copie a chave (começa com `sk-proj-...`)
6. Cole no campo `OPENAI_API_KEY`

##### **Para Email (Gmail):**
1. Acesse: https://myaccount.google.com/apppasswords
2. Faça login no Gmail
3. Crie uma "Senha de App":
   - Nome do app: "HU Automation"
   - Gerar
4. Copie a senha de 16 dígitos
5. Cole no campo `EMAIL_PASSWORD`

---

### 5.4 Salvando o Arquivo .env

1. Salve o arquivo (Ctrl + S)
2. ⚠️ **NUNCA compartilhe este arquivo com ninguém!**
3. ⚠️ **NUNCA faça commit deste arquivo no Git!**

---

## 6. Rodando Pela Primeira Vez

### 6.1 Ativando o Ambiente Virtual (se não estiver ativo)

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

---

### 6.2 Inicializando o Banco de Dados

```bash
python database.py
```

**O que acontece:**
- Cria o arquivo `app.db` (banco de dados SQLite)
- Cria as tabelas necessárias

---

### 6.3 Rodando o Sistema

```bash
python app.py
```

**O que você deve ver:**
```
.env carregado
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

### 6.4 Acessando a Interface

1. Abra seu navegador (Chrome, Firefox, Edge, Safari)
2. Digite na barra de endereços: `http://127.0.0.1:5000`
3. Pressione Enter

**O que você deve ver:**
- Uma página bonita com:
  - Logo do HU Automation
  - Área para arrastar arquivos
  - Opções de configuração
  - Status das configurações (bolinhas verdes/vermelhas)

---

## 7. Como Usar o Sistema

### 7.1 Processando Seu Primeiro Arquivo

#### **Passo 1: Preparar um arquivo de teste**

Crie um arquivo chamado `teste.txt` com este conteúdo:

```
Reunião de Planejamento - 14/11/2025

Participantes:
- João (PO)
- Maria (Dev)
- Pedro (UX)

Discussão:
Precisamos criar uma tela de login para o sistema.
O usuário deve poder entrar com email e senha.
Se errar a senha 3 vezes, deve bloquear por 15 minutos.
Precisa ter um botão "Esqueci minha senha".

Requisitos técnicos:
- Integração com Active Directory
- Logs de tentativas de login
- Notificação por email em caso de bloqueio
```

---

#### **Passo 2: Fazer upload**

1. Na interface web, você tem 2 opções:
   - **Arrastar e soltar**: Arraste o arquivo `teste.txt` para a área pontilhada
   - **Clicar**: Clique na área pontilhada e selecione o arquivo

2. O nome do arquivo aparecerá na tela

---

#### **Passo 3: Configurar opções**

**Provedor de IA:**
- `Zello MIND` → Usa a IA da empresa (recomendado)
- `OpenAI GPT` → Usa ChatGPT (alternativa)
- `Auto` → Tenta Zello primeiro, depois OpenAI

**Formato de saída:**
- `Preview` → Mostra na tela
- `HTML Email` → Envia por email em HTML
- `Text Email` → Envia por email em texto simples

**Email (opcional):**
- Se quiser enviar por email, digite o destinatário
- Pode colocar vários emails separados por vírgula:
  ```
  joao@empresa.com, maria@empresa.com
  ```

---

#### **Passo 4: Processar**

1. Clique no botão azul **"Processar Documento"**
2. Aguarde:
   - Aparece uma barra de progresso
   - Podem aparecer mensagens como:
     - "Extraindo texto do arquivo..."
     - "Enviando para IA..."
     - "Gerando Histórias de Usuário..."
   - O processo pode levar 30-60 segundos

---

#### **Passo 5: Ver o resultado**

Quando terminar, você verá:

```markdown
# 📋 Histórias de Usuário Geradas

## História 1: [Login] – Autenticação de usuário com email e senha

**História de Usuário:**
Como usuário do sistema, quero fazer login com meu email e senha 
para acessar funcionalidades protegidas de forma segura.

**Tipo:** Feature

**Critérios de Aceitação:**
1. Sistema deve aceitar email válido e senha
2. Após 3 tentativas erradas, bloquear por 15 minutos
3. Deve haver botão "Esqueci minha senha"
4. Integração com Active Directory deve funcionar
5. Todas as tentativas devem ser registradas em log

... (continua)
```

---

### 7.2 Copiando o Resultado

1. Clique no botão **"Copiar para Clipboard"**
2. Cole onde quiser (Word, Email, Jira, etc.)

---

### 7.3 Enviando Por Email (se configurou)

Se você:
- Configurou as credenciais de email no `.env`
- Escolheu um formato de email (HTML ou Text)
- Digitou um destinatário

O sistema enviará automaticamente um email com o resultado!

---

## 8. Modificando Configurações

### 8.1 Alterando Textos da Interface

**Arquivo:** `templates/index.html`

**Como modificar:**
1. Abra o arquivo no VS Code
2. Procure o texto que quer mudar
3. Edite
4. Salve
5. Recarregue a página no navegador (F5)

**Exemplo - Mudar o título:**

```html
<!-- Procure por isso: -->
<h1>🚀 HU Automation 2.0</h1>

<!-- Mude para: -->
<h1>🎯 Meu Sistema de Histórias</h1>
```

---

### 8.2 Alterando Configurações Gerais

**Arquivo:** `config.py`

**Exemplo - Aumentar tamanho máximo de upload:**

```python
# Antes (16MB):
MAX_CONTENT_LENGTH: int = 16777216

# Depois (32MB):
MAX_CONTENT_LENGTH: int = 33554432
```

**Exemplo - Mudar porta do servidor:**

```python
# Antes:
PORT: int = 5000

# Depois:
PORT: int = 8080
```

Depois das mudanças:
1. Salve o arquivo
2. Pare o servidor (Ctrl + C no terminal)
3. Rode novamente: `python app.py`

---

### 8.3 Modificando Prompts da IA

Os "prompts" são as instruções que damos para a IA.

**Arquivo:** `prompts/user_story_prompts.py`

**Como funciona:**
```python
SYSTEM_PROMPT = """
Você é um especialista em análise de requisitos...
"""
```

**Exemplo - Adicionar uma instrução:**

```python
SYSTEM_PROMPT = """
Você é um especialista em análise de requisitos...

IMPORTANTE: Sempre inclua exemplos de uso em cada critério de aceitação.
"""
```

---

## 9. Entendendo a Estrutura

### 9.1 Arquivos Principais

| Arquivo | O Que Faz |
|---------|-----------|
| `app.py` | Servidor principal - roda o sistema |
| `config.py` | Configurações gerais |
| `.env` | Senhas e chaves secretas |
| `database.py` | Configuração do banco de dados |
| `requirements.txt` | Lista de dependências |

---

### 9.2 Pastas Principais

| Pasta | O Que Contém |
|-------|--------------|
| `models/` | Estrutura do banco de dados |
| `services/` | Lógica do sistema (IA, email, arquivos) |
| `templates/` | Páginas HTML da interface |
| `static/` | Imagens, CSS, JavaScript |
| `uploads/` | Arquivos enviados pelos usuários |
| `migrations/` | Histórico de mudanças no banco |
| `venv/` | Ambiente virtual (não mexa!) |

---

### 9.3 Serviços (Pasta `services/`)

| Arquivo | Responsabilidade |
|---------|------------------|
| `llm_service.py` | Comunicação com IA (OpenAI/Zello) |
| `email_service.py` | Envio de emails |
| `file_service.py` | Leitura de arquivos (PDF, DOCX, TXT) |
| `generation_service.py` | Geração e validação de HUs |
| `gmail_service.py` | Coleta de emails do Gmail |
| `gdrive_service.py` | Upload/download do Google Drive |

---

## 10. Fazendo Pequenas Alterações

### 10.1 Exemplo 1: Mudar o Logo

**Onde está:** `static/hu_automation_icon.png`

**Como trocar:**
1. Prepare sua imagem (PNG recomendado, 100x100 pixels)
2. Renomeie para `hu_automation_icon.png`
3. Substitua o arquivo na pasta `static/`
4. Recarregue a página (Ctrl + F5)

---

### 10.2 Exemplo 2: Adicionar Formato de Arquivo

**Cenário:** Quero aceitar arquivos `.odt`

**Arquivo:** `config.py`

```python
# Procure por:
ALLOWED_EXTENSIONS: set = {'txt', 'pdf', 'doc', 'docx', 'md'}

# Mude para:
ALLOWED_EXTENSIONS: set = {'txt', 'pdf', 'doc', 'docx', 'md', 'odt'}
```

Mas cuidado! Você também precisa adicionar suporte para ler ODT no `file_service.py`.

---

### 10.3 Exemplo 3: Mudar Timeout da IA

**Cenário:** A IA está demorando muito e dando timeout

**Arquivo:** `services/llm_service.py`

Procure por linhas como:
```python
timeout=60  # 60 segundos
```

Mude para:
```python
timeout=120  # 120 segundos (2 minutos)
```

---

### 10.4 Exemplo 4: Adicionar um Campo no Formulário

**Arquivo:** `templates/index.html`

**Adicionar um campo de "Nome do Projeto":**

```html
<!-- Procure pela seção de formulário -->
<div class="form-group">
    <label for="projectName">Nome do Projeto:</label>
    <input 
        type="text" 
        id="projectName" 
        name="projectName" 
        placeholder="Digite o nome do projeto"
    >
</div>
```

Depois, você precisa capturar esse valor no `app.py`:

```python
project_name = request.form.get('projectName', '')
```

---

## 11. Problemas Comuns e Soluções

### 11.1 "Python não é reconhecido"

**Erro:**
```
'python' não é reconhecido como um comando interno ou externo
```

**Solução:**
1. Reinstale o Python
2. Marque "Add Python to PATH" no instalador
3. Reinicie o terminal/CMD
4. Teste: `python --version`

**Alternativa (Windows):**
Use `py` em vez de `python`:
```bash
py --version
py app.py
```

---

### 11.2 "pip install falhou"

**Erro:**
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solução 1 - Permissões:**
```bash
# Windows (CMD como Administrador)
pip install -r requirements.txt

# macOS/Linux
sudo pip3 install -r requirements.txt
```

**Solução 2 - Atualizar pip:**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### 11.3 "Porta 5000 já está em uso"

**Erro:**
```
OSError: [Errno 48] Address already in use
```

**Solução 1 - Usar outra porta:**

No arquivo `.env`:
```env
FLASK_PORT=8080
```

Depois acesse: `http://127.0.0.1:8080`

**Solução 2 - Matar o processo:**

**Windows:**
```bash
# Descobrir o PID
netstat -ano | findstr :5000

# Matar processo (substitua PID)
taskkill /PID 12345 /F
```

**macOS/Linux:**
```bash
# Descobrir o PID
lsof -i :5000

# Matar processo
kill -9 PID
```

---

### 11.4 "API Key inválida"

**Erro:**
```
Error: Invalid API key provided
```

**Solução:**
1. Abra o arquivo `.env`
2. Verifique se a chave está correta (sem espaços extras)
3. Teste a chave diretamente na plataforma (OpenAI ou Zello)
4. Copie e cole novamente

**Formato correto:**
```env
# Errado (tem espaços)
OPENAI_API_KEY = sk-proj-abc123

# Certo
OPENAI_API_KEY=sk-proj-abc123
```

---

### 11.5 "Falha ao ler arquivo PDF"

**Erro:**
```
Error: Could not extract text from PDF
```

**Causas comuns:**
- PDF com imagens (não tem texto real)
- PDF protegido por senha
- PDF corrompido

**Solução:**
1. Abra o PDF e veja se consegue selecionar o texto
2. Se não conseguir, é uma imagem - use OCR (Optical Character Recognition)
3. Se tiver senha, remova a senha antes
4. Teste com outro PDF para confirmar

**Converter PDF imagem para texto:**
- Use ferramentas online como:
  - https://www.onlineocr.net/
  - https://www.ilovepdf.com/ocr_pdf
- Ou instale Tesseract OCR localmente

---

### 11.6 "Email não foi enviado"

**Erro:**
```
Error: Failed to send email
```

**Checklist de verificação:**

1. **Credenciais corretas?**
   ```env
   EMAIL_USERNAME=seu-email@gmail.com
   EMAIL_PASSWORD=senha-de-app-16-digitos
   ```

2. **Usando senha de app?** (Gmail)
   - Não use sua senha normal!
   - Crie em: https://myaccount.google.com/apppasswords

3. **Email remetente igual ao username?**
   ```env
   EMAIL_USERNAME=joao@gmail.com
   EMAIL_FROM=joao@gmail.com  # Devem ser iguais!
   ```

4. **Servidor SMTP correto?**
   - Gmail: `smtp.gmail.com:587`
   - Outlook: `smtp-mail.outlook.com:587`
   - Yahoo: `smtp.mail.yahoo.com:587`

---

### 11.7 "Ambiente virtual não ativa"

**Erro (Windows PowerShell):**
```
cannot be loaded because running scripts is disabled
```

**Solução:**
1. Abra PowerShell como Administrador
2. Execute:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
3. Confirme com `Y`
4. Tente ativar novamente:
   ```powershell
   venv\Scripts\activate
   ```

**Alternativa:**
Use o CMD em vez do PowerShell:
1. Abra CMD (não PowerShell)
2. Execute:
   ```bash
   venv\Scripts\activate.bat
   ```

---

### 11.8 "Página não carrega"

**Problema:** Digitei `http://127.0.0.1:5000` mas não abre

**Checklist:**

1. **Servidor está rodando?**
   - No terminal, deve ter a mensagem:
     ```
     * Running on http://127.0.0.1:5000
     ```
   - Se não tiver, rode: `python app.py`

2. **Endereço correto?**
   - Use: `http://127.0.0.1:5000`
   - Ou: `http://localhost:5000`
   - NÃO use: `https://` (sem S)

3. **Porta certa?**
   - Verifique no terminal qual porta está usando
   - Pode ser 5000, 8080, 3000, etc.

4. **Firewall bloqueando?**
   - Windows: Permita o Python no firewall
   - Configurações → Firewall → Permitir app

---

## 12. Glossário de Termos

### A

**API (Application Programming Interface)**
- "Interface de Programação de Aplicação"
- É como um garçom: você faz um pedido (requisição), ele leva para a cozinha (servidor), e traz a comida (resposta)

**API Key (Chave de API)**
- Uma "senha especial" para usar um serviço online
- Exemplo: Chave do ChatGPT, chave do Zello MIND

**Ambiente Virtual (Virtual Environment)**
- Uma "caixa isolada" onde instalamos as bibliotecas do projeto
- Evita bagunçar seu computador com pacotes

---

### B

**Backend**
- A "cozinha" do sistema
- Parte que o usuário não vê, mas onde a mágica acontece
- Neste projeto: `app.py`, `services/`, etc.

**Banco de Dados (Database)**
- Onde guardamos informações de forma organizada
- Neste projeto: `app.db` (SQLite)

---

### C

**Clone (Git)**
- Copiar um projeto inteiro do GitHub para seu computador
- Comando: `git clone URL`

**CMD (Command Prompt)**
- "Prompt de Comando" do Windows
- Tela preta onde digitamos comandos
- Como abrir: `Windows + R`, digite `cmd`, Enter

**Config (Configuração)**
- Arquivo ou pasta com configurações do sistema
- Exemplo: `config.py`, `.env`

---

### D

**Dependência (Dependency)**
- Uma biblioteca/ferramenta que o projeto precisa para funcionar
- Listadas em: `requirements.txt`

**Deploy**
- "Colocar no ar", publicar o sistema para outras pessoas usarem
- Neste guia: rodamos localmente (só você acessa)

**Debug**
- Modo de "depuração", para encontrar erros
- Mostra mais informações quando algo dá errado

---

### E

**Endpoint**
- Um "caminho" da API
- Exemplo: `/api/process`, `/api/recent-jobs`

**Env (Environment / .env)**
- Arquivo com variáveis de ambiente (senhas, chaves, etc.)
- Nunca compartilhe este arquivo!

---

### F

**Flask**
- Framework (ferramenta) Python para criar sites/aplicações web
- É o que faz o sistema rodar no navegador

**Frontend**
- A "cara" do sistema, o que o usuário vê
- Neste projeto: `templates/`, `static/`

---

### G

**Git**
- Ferramenta para controlar versões do código
- Como um "Ctrl+Z" super poderoso para projetos

**GitHub / GitLab**
- Sites que hospedam projetos Git online
- Como "Google Drive" para código

---

### H

**HTML**
- Linguagem que cria páginas web
- Arquivos em: `templates/`

**HTTP / HTTPS**
- Protocolo de comunicação da web
- HTTP: Sem criptografia
- HTTPS: Com criptografia (mais seguro)

---

### I

**IA / LLM (Large Language Model)**
- Inteligência Artificial que entende e gera texto
- Exemplos: ChatGPT (OpenAI), Zello MIND

**IDE (Integrated Development Environment)**
- Editor de código "turbinado"
- Exemplos: VS Code, Cursor, PyCharm

---

### J

**JSON**
- Formato de dados estruturado
- Parece com dicionário do Python
- Exemplo:
  ```json
  {
    "nome": "João",
    "idade": 30
  }
  ```

---

### L

**Localhost**
- Seu próprio computador
- Endereço: `127.0.0.1` ou `localhost`
- Quando acessamos `http://localhost:5000`, estamos acessando nosso próprio computador

---

### M

**Migration (Migração)**
- Script que modifica o banco de dados
- Pasta: `migrations/`

**Model (Modelo)**
- Estrutura de dados do banco
- Pasta: `models/`

---

### O

**ORM (Object-Relational Mapping)**
- Traduz objetos Python para banco de dados
- Neste projeto: SQLAlchemy

---

### P

**PATH (Caminho)**
- Endereço de um arquivo ou pasta no computador
- Exemplo Windows: `C:\Users\SeuNome\Projetos\`
- Exemplo macOS/Linux: `/home/seunome/projetos/`

**PIP**
- Instalador de pacotes Python
- Comando: `pip install nome-do-pacote`

**Porta (Port)**
- Número que identifica um serviço
- Exemplo: 5000, 8080, 3000
- Como "canais" de TV diferentes

**Prompt**
- Instruções dadas para uma IA
- Arquivo: `prompts/user_story_prompts.py`

**Python**
- Linguagem de programação usada neste projeto
- Criada por Guido van Rossum em 1991

---

### R

**Request (Requisição)**
- Pedido feito ao servidor
- Exemplo: "Me dê a página inicial"

**Response (Resposta)**
- Resposta do servidor
- Exemplo: Retorna HTML da página

**Requirements.txt**
- Arquivo que lista todas as dependências do projeto
- Usado com: `pip install -r requirements.txt`

---

### S

**Service (Serviço)**
- Módulo com uma responsabilidade específica
- Exemplos: `email_service.py`, `llm_service.py`

**SMTP (Simple Mail Transfer Protocol)**
- Protocolo para envio de emails
- Servidores comuns:
  - Gmail: `smtp.gmail.com:587`
  - Outlook: `smtp-mail.outlook.com:587`

**SQLite**
- Banco de dados simples em arquivo
- Neste projeto: `app.db`

**SQLAlchemy**
- ORM usado para trabalhar com banco de dados em Python

---

### T

**Template**
- Modelo de página HTML
- Pasta: `templates/`
- Usa Jinja2 para inserir dados dinâmicos

**Terminal**
- Programa para digitar comandos
- Windows: CMD ou PowerShell
- macOS: Terminal
- Linux: Terminal ou Console

**Timeout**
- Tempo máximo de espera
- Se passar, dá erro

**Token**
- Pedaço de texto que a IA processa
- OpenAI cobra por tokens usados

---

### U

**Upload**
- Enviar arquivo do seu computador para o servidor

**URL (Uniform Resource Locator)**
- Endereço da web
- Exemplo: `http://127.0.0.1:5000`

---

### V

**Variável de Ambiente (Environment Variable)**
- Configuração guardada no sistema/arquivo
- Arquivo: `.env`

**venv (Virtual Environment)**
- Pasta com ambiente virtual Python
- NUNCA apague esta pasta!
- NUNCA faça commit dela no Git!

**VS Code (Visual Studio Code)**
- Editor de código gratuito da Microsoft
- Download: https://code.visualstudio.com/

---

## 📚 Recursos Adicionais

### Documentação Oficial

- **Python:** https://docs.python.org/3/
- **Flask:** https://flask.palletsprojects.com/
- **OpenAI:** https://platform.openai.com/docs

### Tutoriais Recomendados

- **Python para iniciantes:** https://www.python.org/about/gettingstarted/
- **Git e GitHub:** https://guides.github.com/
- **Flask tutorial:** https://flask.palletsprojects.com/en/latest/tutorial/

### Onde Pedir Ajuda

1. **Stack Overflow:** https://stackoverflow.com/
   - Site com milhões de perguntas e respostas

2. **ChatGPT / Claude:**
   - Cole o erro e pergunte como resolver

3. **Time de desenvolvimento:**
   - Email: desenvolvimento@zello.tec.br

---

## ✅ Checklist Final

Marque conforme for completando:

### Instalação
- [ ] Python 3.10+ instalado
- [ ] Git instalado
- [ ] Editor de código instalado (VS Code)

### Setup do Projeto
- [ ] Projeto clonado do Git
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e configurado
- [ ] Banco de dados inicializado

### Testes
- [ ] Servidor rodando sem erros
- [ ] Interface acessível no navegador
- [ ] Primeiro arquivo processado com sucesso
- [ ] Resultado copiado ou enviado por email

### Configurações (Opcional)
- [ ] Email configurado e funcionando
- [ ] API da IA (OpenAI ou Zello) configurada
- [ ] Google APIs configuradas (se necessário)

---

## 🎓 Parabéns!

Se você chegou até aqui, você agora sabe:
- ✅ Como instalar e configurar o sistema
- ✅ Como usar a interface web
- ✅ Como processar transcrições
- ✅ Como fazer modificações básicas
- ✅ Como resolver problemas comuns

Você não é mais um "iniciante absoluto" - você é um **usuário intermediário** do HU Automation! 🎉

---

## 📞 Precisa de Ajuda?

**Email:** kassia.costa@zello.tec.br  
**Documentação completa:** Veja `README.md` e `DOCUMENTACAO_PROJETO.md`  

---

**Desenvolvido com ❤️ para pessoas reais, com linguagem real.**

*Última atualização: Novembro 2025*

