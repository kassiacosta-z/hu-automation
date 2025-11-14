# ✅ Checklist de Instalação - HU Automation

**Imprima esta página e marque conforme avança!**

---

## 📋 Pré-Requisitos

### Sistema Operacional
- [ ] Tenho Windows 10+, macOS ou Linux
- [ ] Tenho acesso de administrador/sudo
- [ ] Tenho conexão com internet

---

## 🛠️ Instalação de Ferramentas

### Python
- [ ] Baixei Python 3.10+ de python.org
- [ ] Instalei Python
- [ ] ✅ Marquei "Add Python to PATH" no instalador (Windows)
- [ ] Testei: `python --version` mostra versão 3.10+

### Git
- [ ] Baixei Git de git-scm.com
- [ ] Instalei Git
- [ ] Testei: `git --version` mostra versão

### Editor de Código (opcional mas recomendado)
- [ ] Baixei VS Code de code.visualstudio.com
- [ ] Instalei VS Code
- [ ] Abri VS Code com sucesso

---

## 📦 Setup do Projeto

### Baixar Projeto
- [ ] Abri terminal/CMD
- [ ] Naveguei para pasta de projetos: `cd C:\Users\...\Projetos`
- [ ] Clonei repositório: `git clone URL`
- [ ] Entrei na pasta: `cd hu-automation`

### Ambiente Virtual
- [ ] Criei venv: `python -m venv venv`
- [ ] Ativei venv:
  - Windows: `venv\Scripts\activate`
  - macOS/Linux: `source venv/bin/activate`
- [ ] Vi `(venv)` antes do prompt

### Dependências
- [ ] Rodei: `pip install -r requirements.txt`
- [ ] Instalação completou sem erros
- [ ] Demorou 2-5 minutos

---

## 🔑 Configuração

### Arquivo .env
- [ ] Copiei modelo: `cp env.example .env` (ou `copy` no Windows)
- [ ] Abri `.env` no editor
- [ ] Configurei chaves de API (veja seção abaixo)
- [ ] Salvei arquivo `.env`

### Chaves de API

#### Zello MIND (Obrigatória)
- [ ] Obtive chave com time de desenvolvimento
- [ ] Colei em: `ZELLO_API_KEY=...`
- [ ] Configurei: `ZELLO_BASE_URL=https://smartdocs-api-hlg.zello.space`

#### OpenAI (Opcional)
- [ ] Criei conta em platform.openai.com
- [ ] Gerei API key
- [ ] Colei em: `OPENAI_API_KEY=sk-proj-...`

#### Email (Opcional)
- [ ] Configurei Gmail:
  - `EMAIL_USERNAME=seu-email@gmail.com`
  - `EMAIL_PASSWORD=senha-de-app-16-digitos`
  - `EMAIL_FROM=seu-email@gmail.com`
- [ ] Gerei senha de app: myaccount.google.com/apppasswords

### Banco de Dados
- [ ] Rodei: `python database.py`
- [ ] Arquivo `app.db` foi criado
- [ ] Sem erros

---

## 🚀 Primeiro Uso

### Iniciar Sistema
- [ ] Ambiente virtual está ativo (vejo `(venv)`)
- [ ] Rodei: `python app.py`
- [ ] Vi mensagem: `Running on http://127.0.0.1:5000`
- [ ] Sem erros no terminal

### Acessar Interface
- [ ] Abri navegador (Chrome, Firefox, Edge)
- [ ] Acessei: `http://127.0.0.1:5000`
- [ ] Página carregou corretamente
- [ ] Vi logo e formulário

### Processar Primeiro Arquivo
- [ ] Criei arquivo de teste `teste.txt`
- [ ] Fiz upload do arquivo (arrastar ou clicar)
- [ ] Selecionei provedor (Zello ou OpenAI)
- [ ] Cliquei em "Processar Documento"
- [ ] Vi barra de progresso
- [ ] Processamento completou
- [ ] Vi resultado na tela
- [ ] Consegui copiar resultado

---

## ✅ Testes de Funcionalidade

### Básico
- [ ] Upload de arquivo funciona
- [ ] Processamento gera resultado
- [ ] Resultado aparece na tela
- [ ] Botão copiar funciona

### Email (se configurou)
- [ ] Digite um email de teste
- [ ] Processou arquivo
- [ ] Email foi recebido
- [ ] Email está formatado corretamente

### Formatos Diferentes
- [ ] Testei arquivo .txt
- [ ] Testei arquivo .pdf (se tiver)
- [ ] Testei arquivo .docx (se tiver)
- [ ] Todos funcionaram

---

## 🐛 Troubleshooting

### Se algo não funcionou, verifique:

#### Python não reconhecido
- [ ] Reinstalei Python marcando "Add to PATH"
- [ ] Reiniciei terminal/CMD
- [ ] Tentei `py` em vez de `python` (Windows)

#### pip install falhou
- [ ] Atualizei pip: `python -m pip install --upgrade pip`
- [ ] Tentei novamente
- [ ] Rodei como administrador (se necessário)

#### Ambiente virtual não ativa
- [ ] Windows: Usei CMD em vez de PowerShell
- [ ] Ou configurei ExecutionPolicy no PowerShell
- [ ] Caminho do venv está correto

#### Porta 5000 em uso
- [ ] Mudei porta no .env: `FLASK_PORT=8080`
- [ ] Acessei nova porta: `http://localhost:8080`

#### API Key inválida
- [ ] Verifiquei chave no .env (sem espaços)
- [ ] Testei chave diretamente na plataforma
- [ ] Copiei e colei novamente

#### Email não envia
- [ ] Usei Senha de App (não senha normal)
- [ ] EMAIL_FROM igual a EMAIL_USERNAME
- [ ] Servidor SMTP correto (smtp.gmail.com)
- [ ] Porta correta (587)

#### Página não carrega
- [ ] Servidor está rodando (vejo mensagem no terminal)
- [ ] Usei `http://` (não `https://`)
- [ ] Porta está correta
- [ ] Firewall não está bloqueando

---

## 📚 Próximos Passos

Agora que está funcionando:

### Aprendizado
- [ ] Li README.md para entender o sistema
- [ ] Salvei link dos guias nos favoritos
- [ ] Li seção de troubleshooting completa

### Personalização
- [ ] Pensei em modificações que quero fazer
- [ ] Identifiquei guia apropriado para isso
- [ ] Fiz backup antes de modificar

### Backup
- [ ] Copiei pasta do projeto como backup
- [ ] Anotei comandos importantes
- [ ] Salvei .env em local seguro (NÃO no Git!)

---

## 🎓 Status de Conhecimento

Marque seu nível atual:

### Iniciante ⭐
- [ ] Consegui instalar tudo
- [ ] Sistema está rodando
- [ ] Processei primeiro arquivo
- [ ] Entendo o básico

### Intermediário ⭐⭐
- [ ] Configurei email
- [ ] Testei diferentes formatos
- [ ] Modifiquei cores da interface
- [ ] Entendo estrutura de pastas

### Avançado ⭐⭐⭐
- [ ] Criei novos endpoints
- [ ] Modifiquei banco de dados
- [ ] Integrei APIs externas
- [ ] Fiz deploy em produção

---

## 📞 Precisa de Ajuda?

Se algo não funcionou:

1. ✅ Consultei troubleshooting desta página
2. ✅ Li seção de problemas do GUIA_INICIANTE_COMPLETO.md
3. ✅ Pesquisei erro no Google/ChatGPT
4. ❌ Ainda não resolveu? Email: kassia.costa@zello.tec.br

---

## 💾 Backup Deste Checklist

**Data da instalação:** ___/___/_____

**Configurações importantes:**
- Porta usada: _____________
- Provedor de IA: ___________
- Email configurado: SIM / NÃO

**Problemas encontrados e soluções:**
```
_________________________________________________________
_________________________________________________________
_________________________________________________________
_________________________________________________________
```

**Anotações:**
```
_________________________________________________________
_________________________________________________________
_________________________________________________________
_________________________________________________________
```

---

## 🎉 Parabéns!

Se marcou todos os itens das seções principais, você:
- ✅ Instalou Python, Git e ferramentas
- ✅ Configurou o projeto completamente
- ✅ Rodou o sistema com sucesso
- ✅ Processou seu primeiro arquivo

**Você está pronto para usar o HU Automation! 🚀**

---

**Guarde este checklist para referência futura ou para ajudar outras pessoas!**

*Versão 1.0 - Novembro 2025*

---

## 📎 Links Rápidos

Depois de completar este checklist:

- **Usar o sistema:** Acesse http://127.0.0.1:5000
- **Aprender mais:** Leia [GUIA_INICIANTE_COMPLETO.md](GUIA_INICIANTE_COMPLETO.md)
- **Personalizar:** Leia [GUIA_AVANCADO_MODIFICACOES.md](GUIA_AVANCADO_MODIFICACOES.md)
- **Comandos rápidos:** Veja [QUICK_START.md](QUICK_START.md)
- **Todos os guias:** Veja [INDICE_GUIAS.md](INDICE_GUIAS.md)

---

**📧 Feedback:** Este checklist foi útil? Mande sugestões para kassia.costa@zello.tec.br

