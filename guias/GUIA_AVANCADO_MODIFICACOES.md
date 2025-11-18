# 🔧 HU Automation - Guia de Modificações Avançadas

**"Como Personalizar e Estender o Sistema"**

> 🎯 **Objetivo**: Este guia ensina como fazer modificações mais profundas no sistema, adicionar funcionalidades e personalizar comportamentos.

---

## 📚 Índice

1. [Antes de Começar](#1-antes-de-começar)
2. [Modificando a Interface](#2-modificando-a-interface)
3. [Personalizando Prompts da IA](#3-personalizando-prompts-da-ia)
4. [Adicionando Novos Formatos de Arquivo](#4-adicionando-novos-formatos-de-arquivo)
5. [Criando Novos Endpoints de API](#5-criando-novos-endpoints-de-api)
6. [Modificando o Banco de Dados](#6-modificando-o-banco-de-dados)
7. [Integrando Novas APIs](#7-integrando-novas-apis)
8. [Customizando Emails](#8-customizando-emails)
9. [Adicionando Validações](#9-adicionando-validações)
10. [Deploy em Produção](#10-deploy-em-produção)

---

## 1. Antes de Começar

### 1.1 Faça Backup!

Antes de qualquer modificação:

```bash
# Windows
xcopy "hu-automation" "hu-automation-backup" /E /I /H

# macOS/Linux
cp -R hu-automation hu-automation-backup
```

---

### 1.2 Use Controle de Versão

```bash
# Inicialize o Git (se não estiver inicializado)
git init

# Crie um commit com o estado atual
git add .
git commit -m "Estado antes das modificações"

# Sempre que fizer uma mudança importante
git add .
git commit -m "Descrição da mudança"
```

**Benefício:** Se algo quebrar, você pode voltar:
```bash
git log  # Ver histórico
git checkout HASH_DO_COMMIT  # Voltar para um commit específico
```

---

### 1.3 Teste em Ambiente de Desenvolvimento

- ✅ Mantenha `FLASK_DEBUG=True` no `.env` enquanto testa
- ✅ Use porta diferente da produção
- ✅ Crie um banco de dados separado para testes

---

## 2. Modificando a Interface

### 2.1 Alterando Cores e Estilo

**Arquivo:** `templates/index.html`

Procure pela seção `<style>` no início do arquivo:

```css
/* Cores principais */
:root {
    --primary-color: #007bff;     /* Azul principal */
    --success-color: #28a745;     /* Verde */
    --danger-color: #dc3545;      /* Vermelho */
    --warning-color: #ffc107;     /* Amarelo */
    --dark-color: #343a40;        /* Cinza escuro */
}

/* Mude para suas cores */
:root {
    --primary-color: #6f42c1;     /* Roxo */
    --success-color: #20c997;     /* Verde água */
    --danger-color: #fd7e14;      /* Laranja */
    --warning-color: #e83e8c;     /* Rosa */
    --dark-color: #212529;        /* Preto */
}
```

---

### 2.2 Adicionando Novo Campo no Formulário

**Cenário:** Adicionar campo "Prioridade" (Alta, Média, Baixa)

#### **Passo 1: Adicionar HTML**

`templates/index.html`:

```html
<!-- Adicione após o campo de email -->
<div class="form-group">
    <label for="priority">
        <i class="fas fa-exclamation-circle"></i> Prioridade
    </label>
    <select id="priority" name="priority" class="form-control">
        <option value="high">Alta</option>
        <option value="medium" selected>Média</option>
        <option value="low">Baixa</option>
    </select>
    <small>Selecione a prioridade das histórias a serem geradas</small>
</div>
```

#### **Passo 2: Capturar no Backend**

`app.py`:

```python
@app.route('/api/process', methods=['POST'])
def process_file():
    # ... código existente ...
    
    # Adicione esta linha
    priority = request.form.get('priority', 'medium')
    
    # Use a prioridade na geração
    print(f"Processando com prioridade: {priority}")
    
    # ... resto do código ...
```

#### **Passo 3: Usar na Geração**

`prompts/user_story_prompts.py`:

```python
def get_system_prompt(priority: str = 'medium') -> str:
    priority_instructions = {
        'high': 'Foque em critérios rigorosos e detalhados.',
        'medium': 'Mantenha equilíbrio entre detalhe e simplicidade.',
        'low': 'Seja conciso e direto ao ponto.'
    }
    
    return f"""
    Você é um especialista em análise de requisitos...
    
    PRIORIDADE: {priority.upper()}
    {priority_instructions.get(priority, '')}
    
    ... resto do prompt ...
    """
```

---

### 2.3 Criando Página de Histórico

**Cenário:** Mostrar todos os processamentos anteriores

#### **Passo 1: Criar Endpoint**

`app.py`:

```python
@app.route('/history')
def history_page():
    """Página de histórico de processamentos."""
    return render_template('history.html')

@app.route('/api/history')
def get_history():
    """API que retorna histórico de jobs."""
    try:
        from models import TranscriptionJob
        
        jobs = TranscriptionJob.query\
            .order_by(TranscriptionJob.created_at.desc())\
            .limit(50)\
            .all()
        
        return jsonify({
            'success': True,
            'jobs': [{
                'id': job.id,
                'filename': job.source_uri.split('/')[-1],
                'status': job.status,
                'created_at': job.created_at.strftime('%d/%m/%Y %H:%M'),
            } for job in jobs]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

#### **Passo 2: Criar Template HTML**

`templates/history.html`:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Histórico - HU Automation</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
</head>
<body>
    <div class="container mt-5">
        <h1>📜 Histórico de Processamentos</h1>
        
        <div id="historyList">
            <p>Carregando...</p>
        </div>
    </div>

    <script>
        // Carregar histórico ao abrir a página
        fetch('/api/history')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayHistory(data.jobs);
                } else {
                    console.error('Erro:', data.error);
                }
            });

        function displayHistory(jobs) {
            const container = document.getElementById('historyList');
            
            if (jobs.length === 0) {
                container.innerHTML = '<p>Nenhum processamento encontrado.</p>';
                return;
            }

            let html = '<table class="table table-striped">';
            html += '<thead><tr><th>ID</th><th>Arquivo</th><th>Status</th><th>Data</th><th>Ações</th></tr></thead><tbody>';
            
            jobs.forEach(job => {
                const statusBadge = getStatusBadge(job.status);
                html += `
                    <tr>
                        <td>${job.id}</td>
                        <td>${job.filename}</td>
                        <td>${statusBadge}</td>
                        <td>${job.created_at}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="viewJob(${job.id})">
                                Ver Detalhes
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function getStatusBadge(status) {
            const badges = {
                'processed': '<span class="badge badge-success">Processado</span>',
                'processing': '<span class="badge badge-warning">Processando</span>',
                'failed': '<span class="badge badge-danger">Falhou</span>',
                'discovered': '<span class="badge badge-info">Descoberto</span>'
            };
            return badges[status] || '<span class="badge badge-secondary">Desconhecido</span>';
        }

        function viewJob(jobId) {
            // Redirecionar para página de detalhes (a ser criada)
            window.location.href = `/job/${jobId}`;
        }
    </script>
</body>
</html>
```

#### **Passo 3: Adicionar Link no Menu**

`templates/index.html`:

```html
<!-- Adicione um botão no topo -->
<div class="text-right mb-3">
    <a href="/history" class="btn btn-outline-primary">
        📜 Ver Histórico
    </a>
</div>
```

---

## 3. Personalizando Prompts da IA

### 3.1 Estrutura Atual dos Prompts

**Arquivo:** `prompts/user_story_prompts.py`

```python
SYSTEM_PROMPT = """
Você é um especialista em análise de requisitos...
"""

USER_PROMPT_TEMPLATE = """
Analise a seguinte transcrição...

{transcription_text}
"""
```

---

### 3.2 Adicionando Seções Personalizadas

**Cenário:** Sua empresa quer adicionar seção "Impacto Financeiro"

```python
SYSTEM_PROMPT = """
Você é um especialista em análise de requisitos...

Cada História de Usuário DEVE conter as seguintes seções:

1. Nome da História
2. História de Usuário (formato padrão)
3. Tipo
4. Critérios de Aceitação
5. Permissões e Acessos
6. Regras de Negócios
7. Requisitos Técnicos
8. Regras de Interface
9. Campos e Componentes de UI
10. Cenários de Teste
11. **Impacto Financeiro** (NOVA SEÇÃO)
    - Estimativa de custo de implementação
    - ROI esperado (Return on Investment)
    - Economia de tempo/recursos

FORMATO DA SEÇÃO IMPACTO FINANCEIRO:
```markdown
## 💰 Impacto Financeiro

**Custo Estimado:**
- Desenvolvimento: X horas (R$ Y)
- Infraestrutura: R$ Z/mês
- Treinamento: R$ W

**ROI Esperado:**
- Economia: R$ A/mês
- Payback: B meses
- Benefícios intangíveis: [lista]
```

... resto do prompt ...
"""
```

---

### 3.3 Criando Templates por Tipo de Projeto

**Cenário:** Diferentes prompts para diferentes projetos

`prompts/user_story_prompts.py`:

```python
TEMPLATES = {
    'ecommerce': {
        'system': """
        Você é especialista em e-commerce...
        Foque em: conversão, jornada do cliente, checkout, pagamentos.
        """,
        'sections': ['Carrinho', 'Checkout', 'Pagamento', 'Logística']
    },
    
    'interno': {
        'system': """
        Você é especialista em sistemas internos corporativos...
        Foque em: eficiência operacional, integrações, permissões.
        """,
        'sections': ['Fluxo de Aprovação', 'Relatórios', 'Auditoria']
    },
    
    'mobile': {
        'system': """
        Você é especialista em aplicativos móveis...
        Foque em: UX mobile, performance, offline-first, notificações.
        """,
        'sections': ['Responsividade', 'Offline', 'Push Notifications']
    }
}

def get_system_prompt(project_type: str = 'default') -> str:
    """Retorna prompt baseado no tipo de projeto."""
    if project_type in TEMPLATES:
        return TEMPLATES[project_type]['system']
    return SYSTEM_PROMPT  # Prompt padrão
```

**Uso no frontend:**

```html
<div class="form-group">
    <label>Tipo de Projeto</label>
    <select name="project_type" class="form-control">
        <option value="default">Padrão</option>
        <option value="ecommerce">E-commerce</option>
        <option value="interno">Sistema Interno</option>
        <option value="mobile">Mobile App</option>
    </select>
</div>
```

---

### 3.4 Adicionando Exemplos ao Prompt

**Melhora a qualidade da resposta da IA:**

```python
SYSTEM_PROMPT = """
... instruções gerais ...

## EXEMPLOS DE SAÍDA ESPERADA:

### Exemplo 1: Feature de Login

**Nome da História:**
[Login] – Autenticação com email e senha

**História de Usuário:**
Como usuário do sistema, quero fazer login com meu email e senha 
para acessar funcionalidades protegidas de forma segura.

**Tipo:** Feature

**Critérios de Aceitação:**
1. ✅ Sistema deve validar formato do email
2. ✅ Senha deve ter mínimo 8 caracteres
3. ✅ Após 3 tentativas erradas, bloquear por 15 minutos
4. ✅ Deve exibir mensagem de erro clara
5. ✅ Deve ter opção "Esqueci minha senha"

... restante do exemplo ...

---

Agora, aplique esse mesmo padrão e nível de detalhe 
nas Histórias de Usuário que você vai gerar.
"""
```

---

## 4. Adicionando Novos Formatos de Arquivo

### 4.1 Suporte a Arquivos Excel (.xlsx)

#### **Passo 1: Instalar Biblioteca**

```bash
pip install openpyxl
```

Adicione ao `requirements.txt`:
```
openpyxl>=3.1.0
```

#### **Passo 2: Criar Extrator**

`services/file_service.py`:

```python
def extract_text_from_excel(file_path: str) -> str:
    """
    Extrai texto de arquivo Excel (.xlsx).
    
    Args:
        file_path: Caminho do arquivo Excel
        
    Returns:
        Texto extraído de todas as células
    """
    try:
        from openpyxl import load_workbook
        
        workbook = load_workbook(file_path, data_only=True)
        all_text = []
        
        for sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
            all_text.append(f"\n=== {sheet_name} ===\n")
            
            for row in sheet.iter_rows(values_only=True):
                row_text = ' | '.join([str(cell) if cell else '' for cell in row])
                if row_text.strip():
                    all_text.append(row_text)
        
        return '\n'.join(all_text)
        
    except Exception as e:
        raise Exception(f"Erro ao processar Excel: {str(e)}")
```

#### **Passo 3: Adicionar ao FileService**

```python
class FileService:
    # ... código existente ...
    
    def extract_text(self, file_path: str) -> str:
        """Extrai texto de qualquer formato suportado."""
        ext = self._get_file_extension(file_path)
        
        extractors = {
            'txt': self._extract_text_from_txt,
            'pdf': extract_text_from_pdf,
            'docx': extract_text_from_docx,
            'doc': extract_text_from_doc,
            'md': self._extract_text_from_txt,
            'xlsx': extract_text_from_excel,  # NOVO!
            'xls': extract_text_from_excel    # NOVO!
        }
        
        if ext not in extractors:
            raise ValueError(f"Formato não suportado: {ext}")
        
        return extractors[ext](file_path)
```

#### **Passo 4: Permitir Upload**

`config.py`:

```python
ALLOWED_EXTENSIONS: set = {
    'txt', 'pdf', 'doc', 'docx', 'md',
    'xlsx', 'xls'  # NOVO!
}
```

---

### 4.2 Suporte a Arquivos de Áudio (Transcrição)

**Requer API de transcrição (OpenAI Whisper, Google Speech-to-Text, etc.)**

#### **Passo 1: Instalar**

```bash
pip install openai-whisper
# ou
pip install google-cloud-speech
```

#### **Passo 2: Criar Serviço de Transcrição**

`services/transcription_service.py`:

```python
import whisper
from typing import Dict

class TranscriptionService:
    """Serviço de transcrição de áudio."""
    
    def __init__(self):
        # Carrega modelo Whisper (roda localmente)
        self.model = whisper.load_model("base")
    
    def transcribe_audio(self, audio_path: str) -> Dict[str, any]:
        """
        Transcreve arquivo de áudio.
        
        Args:
            audio_path: Caminho do arquivo de áudio
            
        Returns:
            Dicionário com texto e metadados
        """
        try:
            result = self.model.transcribe(
                audio_path,
                language='pt',  # Português
                task='transcribe'
            )
            
            return {
                'success': True,
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
```

#### **Passo 3: Integrar**

```python
def extract_text_from_audio(file_path: str) -> str:
    """Extrai texto de áudio via transcrição."""
    service = TranscriptionService()
    result = service.transcribe_audio(file_path)
    
    if not result['success']:
        raise Exception(f"Erro na transcrição: {result['error']}")
    
    return result['text']
```

---

## 5. Criando Novos Endpoints de API

### 5.1 Endpoint de Estatísticas

**Cenário:** Mostrar estatísticas do sistema

`app.py`:

```python
@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """
    Retorna estatísticas gerais do sistema.
    
    Returns:
        JSON com estatísticas de uso
    """
    try:
        from models import TranscriptionJob
        from datetime import datetime, timedelta
        from sqlalchemy import func
        
        # Total de jobs
        total_jobs = TranscriptionJob.query.count()
        
        # Jobs por status
        status_counts = db.session.query(
            TranscriptionJob.status,
            func.count(TranscriptionJob.id)
        ).group_by(TranscriptionJob.status).all()
        
        # Jobs dos últimos 7 dias
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_jobs = TranscriptionJob.query\
            .filter(TranscriptionJob.created_at >= seven_days_ago)\
            .count()
        
        # Taxa de sucesso
        processed = TranscriptionJob.query\
            .filter_by(status='processed')\
            .count()
        success_rate = (processed / total_jobs * 100) if total_jobs > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_jobs': total_jobs,
                'recent_jobs': recent_jobs,
                'success_rate': round(success_rate, 2),
                'status_breakdown': {
                    status: count for status, count in status_counts
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Uso no frontend:**

```javascript
fetch('/api/stats')
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Total de jobs:', data.stats.total_jobs);
            console.log('Taxa de sucesso:', data.stats.success_rate + '%');
        }
    });
```

---

### 5.2 Endpoint de Busca

**Cenário:** Buscar jobs por texto

`app.py`:

```python
@app.route('/api/search', methods=['GET'])
def search_jobs():
    """
    Busca jobs por termo.
    
    Query params:
        q: Termo de busca
        limit: Máximo de resultados (padrão: 20)
        
    Returns:
        JSON com jobs encontrados
    """
    try:
        from models import TranscriptionJob
        
        query_term = request.args.get('q', '')
        limit = int(request.args.get('limit', 20))
        
        if not query_term:
            return jsonify({
                'success': False,
                'error': 'Parâmetro "q" é obrigatório'
            }), 400
        
        # Busca em source_uri e collaborator_email
        jobs = TranscriptionJob.query\
            .filter(
                (TranscriptionJob.source_uri.contains(query_term)) |
                (TranscriptionJob.collaborator_email.contains(query_term))
            )\
            .order_by(TranscriptionJob.created_at.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            'success': True,
            'count': len(jobs),
            'jobs': [{
                'id': job.id,
                'source_uri': job.source_uri,
                'status': job.status,
                'email': job.collaborator_email,
                'created_at': job.created_at.isoformat()
            } for job in jobs]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Uso:**

```bash
# Buscar por email
curl "http://localhost:5000/api/search?q=joao@empresa.com"

# Buscar por nome de arquivo
curl "http://localhost:5000/api/search?q=reuniao&limit=10"
```

---

## 6. Modificando o Banco de Dados

### 6.1 Adicionando Nova Coluna

**Cenário:** Adicionar campo "priority" na tabela TranscriptionJob

#### **Passo 1: Modificar o Model**

`models/__init__.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
import enum

class Priority(enum.Enum):
    """Enum de prioridades."""
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class TranscriptionJob(Base):
    __tablename__ = 'transcription_jobs'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    source_uri: Mapped[str] = mapped_column(String(500))
    collaborator_email: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50))
    
    # NOVO CAMPO
    priority: Mapped[str] = mapped_column(
        String(20),
        default='medium',
        nullable=False
    )
    
    # ... resto dos campos ...
```

#### **Passo 2: Criar Migration**

```bash
# Gerar migration automaticamente
alembic revision --autogenerate -m "add_priority_field"
```

Arquivo gerado em `migrations/versions/xxxx_add_priority_field.py`:

```python
def upgrade():
    op.add_column('transcription_jobs', 
        sa.Column('priority', sa.String(20), 
                  nullable=False, 
                  server_default='medium'))

def downgrade():
    op.drop_column('transcription_jobs', 'priority')
```

#### **Passo 3: Aplicar Migration**

```bash
alembic upgrade head
```

#### **Passo 4: Usar no Código**

```python
# Criar novo job com prioridade
job = TranscriptionJob(
    source_uri='file://test.txt',
    status='discovered',
    priority='high'  # NOVO!
)
db.session.add(job)
db.session.commit()

# Buscar jobs por prioridade
high_priority_jobs = TranscriptionJob.query\
    .filter_by(priority='high')\
    .all()
```

---

### 6.2 Criando Nova Tabela

**Cenário:** Tabela para armazenar feedback dos usuários

#### **Passo 1: Criar Model**

`models/__init__.py`:

```python
class UserFeedback(Base):
    """Tabela de feedbacks dos usuários."""
    __tablename__ = 'user_feedback'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey('transcription_jobs.id'))
    rating: Mapped[int] = mapped_column()  # 1-5 estrelas
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    # Relacionamento
    job: Mapped["TranscriptionJob"] = relationship(back_populates="feedbacks")

# Adicionar no TranscriptionJob
class TranscriptionJob(Base):
    # ... campos existentes ...
    
    # Relacionamento
    feedbacks: Mapped[list["UserFeedback"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan"
    )
```

#### **Passo 2: Criar Migration**

```bash
alembic revision --autogenerate -m "create_user_feedback_table"
alembic upgrade head
```

#### **Passo 3: Criar Endpoint**

```python
@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Salva feedback do usuário."""
    try:
        data = request.get_json()
        
        feedback = UserFeedback(
            job_id=data['job_id'],
            rating=data['rating'],
            comment=data.get('comment')
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Feedback salvo com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

## 7. Integrando Novas APIs

### 7.1 Integração com Slack

**Cenário:** Notificar no Slack quando um job for processado

#### **Passo 1: Instalar**

```bash
pip install slack-sdk
```

#### **Passo 2: Criar Serviço**

`services/slack_service.py`:

```python
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Dict, Optional
from config import config

class SlackService:
    """Serviço de notificações Slack."""
    
    def __init__(self):
        token = config.SLACK_BOT_TOKEN  # Adicionar no .env
        self.client = WebClient(token=token) if token else None
    
    def send_notification(
        self,
        channel: str,
        message: str,
        blocks: Optional[list] = None
    ) -> Dict[str, any]:
        """
        Envia notificação para canal Slack.
        
        Args:
            channel: ID ou nome do canal (#general)
            message: Texto da mensagem
            blocks: Blocos formatados (opcional)
            
        Returns:
            Resultado da operação
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Slack não configurado'
            }
        
        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=message,
                blocks=blocks
            )
            
            return {
                'success': True,
                'message_ts': response['ts']
            }
            
        except SlackApiError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def notify_job_completed(self, job_id: int, status: str):
        """Notifica quando job é concluído."""
        emoji = '✅' if status == 'processed' else '❌'
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Job {job_id} - {status.upper()}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"O job #{job_id} foi {status}."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Ver Detalhes"
                        },
                        "url": f"http://localhost:5000/job/{job_id}"
                    }
                ]
            }
        ]
        
        return self.send_notification(
            channel='#hu-automation',
            message=f"Job {job_id} - {status}",
            blocks=blocks
        )
```

#### **Passo 3: Adicionar no .env**

```env
# Slack
SLACK_BOT_TOKEN=xoxb-your-token-here
SLACK_DEFAULT_CHANNEL=#hu-automation
```

#### **Passo 4: Usar**

```python
# No final do processamento
from services.slack_service import SlackService

slack = SlackService()
slack.notify_job_completed(job_id=123, status='processed')
```

---

### 7.2 Integração com Jira

**Cenário:** Criar Issues no Jira automaticamente

```bash
pip install jira
```

`services/jira_service.py`:

```python
from jira import JIRA
from typing import Dict, Optional

class JiraService:
    """Serviço de integração com Jira."""
    
    def __init__(self):
        self.jira = JIRA(
            server=config.JIRA_SERVER,
            basic_auth=(config.JIRA_EMAIL, config.JIRA_API_TOKEN)
        )
    
    def create_user_story(
        self,
        project_key: str,
        summary: str,
        description: str,
        story_points: Optional[int] = None
    ) -> Dict[str, any]:
        """
        Cria User Story no Jira.
        
        Args:
            project_key: Chave do projeto (ex: PROJ)
            summary: Título da história
            description: Descrição completa
            story_points: Pontos da história (opcional)
            
        Returns:
            Resultado com chave da issue criada
        """
        try:
            issue_dict = {
                'project': {'key': project_key},
                'summary': summary,
                'description': description,
                'issuetype': {'name': 'Story'},
            }
            
            if story_points:
                issue_dict['customfield_10016'] = story_points  # Story Points
            
            new_issue = self.jira.create_issue(fields=issue_dict)
            
            return {
                'success': True,
                'issue_key': new_issue.key,
                'issue_url': f"{config.JIRA_SERVER}/browse/{new_issue.key}"
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_stories_from_hu(
        self,
        project_key: str,
        user_stories_text: str
    ) -> Dict[str, any]:
        """
        Cria múltiplas stories no Jira a partir do texto gerado.
        
        Args:
            project_key: Chave do projeto
            user_stories_text: Texto com todas as HUs
            
        Returns:
            Lista de issues criadas
        """
        # Parse o texto e extrai cada história
        stories = self._parse_user_stories(user_stories_text)
        
        created_issues = []
        errors = []
        
        for story in stories:
            result = self.create_user_story(
                project_key=project_key,
                summary=story['title'],
                description=story['description']
            )
            
            if result['success']:
                created_issues.append(result)
            else:
                errors.append(result)
        
        return {
            'success': len(errors) == 0,
            'created': len(created_issues),
            'issues': created_issues,
            'errors': errors
        }
    
    def _parse_user_stories(self, text: str) -> list:
        """Parse texto e extrai histórias individuais."""
        # Implementar lógica de parsing
        # Retorna lista de dicionários com title e description
        stories = []
        # ... lógica de parsing ...
        return stories
```

**Adicionar no .env:**

```env
# Jira
JIRA_SERVER=https://sua-empresa.atlassian.net
JIRA_EMAIL=seu-email@empresa.com
JIRA_API_TOKEN=seu-token-aqui
```

**Usar:**

```python
from services.jira_service import JiraService

jira = JiraService()
result = jira.create_stories_from_hu(
    project_key='PROJ',
    user_stories_text=generated_stories
)

print(f"Criadas {result['created']} histórias no Jira!")
```

---

## 8. Customizando Emails

### 8.1 Template HTML Personalizado

**Arquivo:** `services/email_service.py`

Crie um template mais elaborado:

```python
def get_html_template(
    user_stories: str,
    company_logo_url: str = None,
    custom_footer: str = None
) -> str:
    """
    Gera template HTML customizado.
    
    Args:
        user_stories: Histórias geradas
        company_logo_url: URL do logo da empresa
        custom_footer: Rodapé personalizado
        
    Returns:
        HTML formatado
    """
    
    # Converter Markdown para HTML
    import markdown
    html_content = markdown.markdown(user_stories, extensions=['tables', 'fenced_code'])
    
    # Template com estilo corporativo
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px 10px 0 0;
                text-align: center;
            }}
            .content {{
                background: white;
                padding: 30px;
                border-radius: 0 0 10px 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
            h2 {{ color: #764ba2; margin-top: 30px; }}
            h3 {{ color: #555; }}
            .criteria {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #667eea; margin: 15px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th {{ background: #667eea; color: white; padding: 12px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
            .footer {{
                text-align: center;
                color: #888;
                font-size: 12px;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #ddd;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            {"<img src='" + company_logo_url + "' style='max-width: 150px; margin-bottom: 10px;'>" if company_logo_url else ""}
            <h1 style="color: white; margin: 0;">📋 Histórias de Usuário Geradas</h1>
            <p style="margin: 5px 0 0 0;">Gerado automaticamente pelo HU Automation</p>
        </div>
        
        <div class="content">
            {html_content}
        </div>
        
        <div class="footer">
            {custom_footer or "Gerado por HU Automation · Desenvolvido com ❤️ pela equipe de tecnologia"}
        </div>
    </body>
    </html>
    """
    
    return html
```

**Usar:**

```python
html = get_html_template(
    user_stories=generated_stories,
    company_logo_url='https://empresa.com/logo.png',
    custom_footer='Empresa XYZ · Todos os direitos reservados'
)

email_service.send_email(
    to=['destinatario@empresa.com'],
    subject='Histórias de Usuário - Projeto ABC',
    body_html=html
)
```

---

### 8.2 Anexando PDFs aos Emails

```python
from email.mime.application import MIMEApplication
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_pdf(user_stories: str, output_path: str):
    """Gera PDF das histórias."""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Adicionar conteúdo
    for line in user_stories.split('\n'):
        if line.startswith('# '):
            story.append(Paragraph(line[2:], styles['Title']))
        elif line.startswith('## '):
            story.append(Paragraph(line[3:], styles['Heading2']))
        else:
            story.append(Paragraph(line, styles['Normal']))
        story.append(Spacer(1, 12))
    
    doc.build(story)

def send_email_with_pdf(
    to: list,
    subject: str,
    body: str,
    user_stories: str
):
    """Envia email com PDF anexo."""
    # Gerar PDF
    pdf_path = '/tmp/user_stories.pdf'
    generate_pdf(user_stories, pdf_path)
    
    # Criar email com anexo
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_FROM
    msg['To'] = ', '.join(to)
    
    # Corpo do email
    msg.attach(MIMEText(body, 'html'))
    
    # Anexar PDF
    with open(pdf_path, 'rb') as f:
        pdf = MIMEApplication(f.read(), _subtype='pdf')
        pdf.add_header('Content-Disposition', 'attachment', filename='historias_usuario.pdf')
        msg.attach(pdf)
    
    # Enviar
    send_smtp_email(msg)
```

---

## 9. Adicionando Validações

### 9.1 Validação de Entrada

**Arquivo:** `app.py`

```python
from email_validator import validate_email, EmailNotValidError

def validate_upload_request(request):
    """
    Valida requisição de upload.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Verificar se tem arquivo
    if 'file' not in request.files:
        return False, 'Nenhum arquivo enviado'
    
    file = request.files['file']
    if file.filename == '':
        return False, 'Nome de arquivo vazio'
    
    # Verificar extensão
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in config.ALLOWED_EXTENSIONS:
        return False, f'Formato não suportado: .{ext}'
    
    # Verificar tamanho
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > config.MAX_CONTENT_LENGTH:
        max_mb = config.MAX_CONTENT_LENGTH / (1024 * 1024)
        return False, f'Arquivo muito grande (máximo: {max_mb}MB)'
    
    # Validar emails (se fornecidos)
    emails = request.form.get('email', '').strip()
    if emails:
        for email in emails.split(','):
            email = email.strip()
            try:
                validate_email(email)
            except EmailNotValidError:
                return False, f'Email inválido: {email}'
    
    return True, None

# Usar no endpoint
@app.route('/api/process', methods=['POST'])
def process_file():
    # Validar primeiro
    is_valid, error = validate_upload_request(request)
    if not is_valid:
        return jsonify({
            'success': False,
            'error': error
        }), 400
    
    # Processar...
```

---

### 9.2 Validação de Qualidade da IA

**Arquivo:** `services/generation_service.py`

```python
def validate_user_stories(text: str) -> Dict[str, any]:
    """
    Valida qualidade das histórias geradas.
    
    Returns:
        Dicionário com resultado da validação
    """
    issues = []
    score = 100
    
    # 1. Verificar seções obrigatórias
    required_sections = [
        'Nome da História',
        'História de Usuário',
        'Tipo',
        'Critérios de Aceitação',
        'Cenários de Teste'
    ]
    
    for section in required_sections:
        if section not in text:
            issues.append(f"Seção obrigatória faltando: {section}")
            score -= 20
    
    # 2. Verificar formato da história
    if not re.search(r'Como .+ quero .+ para .+', text):
        issues.append("Formato da História de Usuário incorreto")
        score -= 15
    
    # 3. Verificar critérios de aceitação
    criteria_count = len(re.findall(r'^\d+\.', text, re.MULTILINE))
    if criteria_count < 3:
        issues.append(f"Poucos critérios de aceitação ({criteria_count})")
        score -= 10
    
    # 4. Verificar cenários de teste
    if not re.search(r'Dado .+ Quando .+ Então', text):
        issues.append("Cenários de teste no formato incorreto (falta Dado/Quando/Então)")
        score -= 15
    
    # 5. Verificar tamanho mínimo
    word_count = len(text.split())
    if word_count < 200:
        issues.append(f"Texto muito curto ({word_count} palavras)")
        score -= 10
    
    return {
        'is_valid': score >= 70,
        'score': max(0, score),
        'issues': issues,
        'needs_retry': score < 50
    }
```

**Usar na geração:**

```python
# Após gerar com IA
result = llm_service.generate(prompt)
validation = validate_user_stories(result)

if not validation['is_valid']:
    if validation['needs_retry']:
        # Tentar novamente com prompt corrigido
        result = llm_service.generate(improved_prompt)
    else:
        # Alertar usuário
        print(f"Atenção: Qualidade baixa ({validation['score']})")
        print("Problemas encontrados:", validation['issues'])
```

---

## 10. Deploy em Produção

### 10.1 Checklist Pré-Deploy

- [ ] Todas as variáveis de ambiente configuradas no `.env`
- [ ] `FLASK_DEBUG=False` em produção
- [ ] `SECRET_KEY` forte e único
- [ ] Banco de dados de produção configurado (PostgreSQL recomendado)
- [ ] Migrations aplicadas: `alembic upgrade head`
- [ ] Dependências atualizadas: `pip freeze > requirements.txt`
- [ ] Logs configurados corretamente
- [ ] Backups automáticos configurados
- [ ] Monitoramento configurado (Sentry, New Relic, etc.)
- [ ] HTTPS configurado

---

### 10.2 Deploy com Docker

**Dockerfile otimizado para produção:**

```dockerfile
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY --chown=appuser:appuser . .

# Mudar para usuário não-root
USER appuser

# Variáveis de ambiente
ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_ENV=production \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# Usar Gunicorn em vez do servidor de desenvolvimento
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

**Instalar Gunicorn:**

```bash
pip install gunicorn
```

Adicionar ao `requirements.txt`:
```
gunicorn>=21.2.0
```

---

### 10.3 Deploy no Heroku

```bash
# Login no Heroku
heroku login

# Criar app
heroku create hu-automation

# Configurar variáveis de ambiente
heroku config:set OPENAI_API_KEY=sk-...
heroku config:set ZELLO_API_KEY=...
heroku config:set DATABASE_URL=...

# Deploy
git push heroku main

# Aplicar migrations
heroku run alembic upgrade head

# Abrir app
heroku open
```

---

### 10.4 Deploy no AWS (EC2)

**Passo 1: Criar instância EC2**
- Ubuntu 22.04 LTS
- t2.medium ou superior
- Abrir portas: 22 (SSH), 80 (HTTP), 443 (HTTPS)

**Passo 2: Conectar e configurar**

```bash
# Conectar via SSH
ssh -i sua-chave.pem ubuntu@seu-ip

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3.12 python3-pip python3-venv nginx -y

# Clonar projeto
git clone https://github.com/sua-empresa/hu-automation.git
cd hu-automation

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env
nano .env
# (colar configurações)

# Aplicar migrations
alembic upgrade head
```

**Passo 3: Configurar Nginx**

`/etc/nginx/sites-available/hu-automation`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ubuntu/hu-automation/static;
    }

    client_max_body_size 20M;
}
```

```bash
# Ativar site
sudo ln -s /etc/nginx/sites-available/hu-automation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Passo 4: Configurar Systemd**

`/etc/systemd/system/hu-automation.service`:

```ini
[Unit]
Description=HU Automation Web Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/hu-automation
Environment="PATH=/home/ubuntu/hu-automation/venv/bin"
ExecStart=/home/ubuntu/hu-automation/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 --timeout 120 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ativar serviço
sudo systemctl daemon-reload
sudo systemctl start hu-automation
sudo systemctl enable hu-automation
sudo systemctl status hu-automation
```

---

## 🎓 Conclusão

Parabéns! Agora você sabe:

- ✅ Modificar a interface e adicionar campos
- ✅ Personalizar prompts da IA
- ✅ Adicionar novos formatos de arquivo
- ✅ Criar endpoints de API
- ✅ Modificar o banco de dados
- ✅ Integrar APIs externas (Slack, Jira)
- ✅ Customizar emails
- ✅ Adicionar validações
- ✅ Fazer deploy em produção

Você agora é um **desenvolvedor avançado** do HU Automation! 🚀

---

## 📞 Precisa de Ajuda?

**Email:** kassia.costa@zello.tec.br  
**Documentação:** `GUIA_INICIANTE_COMPLETO.md` (para conceitos básicos)

---

**Desenvolvido com ❤️ para desenvolvedores que querem ir além.**

*Última atualização: Novembro 2025*

