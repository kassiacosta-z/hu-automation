# 🔧 HU Automation - Guia de Manutenção

**"Como Manter o Sistema Rodando Perfeitamente"**

> 🎯 **Objetivo**: Ensinar administradores e responsáveis técnicos a manter o sistema em produção, fazer backups, monitorar e resolver problemas.

---

## 📚 Índice

1. [Checklist Diário](#1-checklist-diário)
2. [Checklist Semanal](#2-checklist-semanal)
3. [Checklist Mensal](#3-checklist-mensal)
4. [Backups](#4-backups)
5. [Monitoramento](#5-monitoramento)
6. [Logs](#6-logs)
7. [Atualizações](#7-atualizações)
8. [Problemas em Produção](#8-problemas-em-produção)
9. [Performance](#9-performance)
10. [Segurança](#10-segurança)

---

## 1. Checklist Diário

### 1.1 Verificação de Saúde do Sistema

**Tempo estimado:** 5 minutos

```bash
# 1. Verificar se o serviço está rodando
systemctl status hu-automation
# ou
docker ps | grep hu-automation

# 2. Verificar último log de erro
tail -n 50 /var/log/hu-automation/error.log

# 3. Verificar uso de disco
df -h

# 4. Verificar memória
free -h

# 5. Verificar processamento recente (via API)
curl http://localhost:5000/api/repository-stats
```

### 1.2 O Que Verificar

- [ ] Serviço está ativo e rodando
- [ ] Sem erros críticos nos logs (últimas 24h)
- [ ] Disco com pelo menos 20% livre
- [ ] Memória RAM disponível (>= 25%)
- [ ] Jobs processados nas últimas 24h

### 1.3 Alertas Críticos

**🚨 Ação Imediata Necessária Se:**

- Serviço parado ou crashando
- Disco com menos de 10% livre
- Memória RAM < 10% disponível
- Taxa de erro > 50% nas últimas 24h
- Nenhum job processado em 24h (quando deveria ter)

---

## 2. Checklist Semanal

### 2.1 Limpeza de Arquivos Temporários

**Tempo estimado:** 10 minutos

```bash
# Limpar uploads antigos (mais de 7 dias)
find ./uploads -type f -mtime +7 -delete

# Limpar logs antigos
find /var/log/hu-automation -name "*.log.*" -mtime +30 -delete

# Limpar cache do Docker (se usando)
docker system prune -f
```

### 2.2 Verificar Espaço em Disco

```bash
# Ver uso por pasta
du -h --max-depth=1 /app

# Identificar arquivos grandes
find /app -type f -size +100M -exec ls -lh {} \;
```

### 2.3 Revisar Logs de Erro

```bash
# Contar erros por tipo
grep "ERROR" /var/log/hu-automation/app.log | awk '{print $5}' | sort | uniq -c | sort -rn

# Ver erros únicos da última semana
grep "ERROR" /var/log/hu-automation/app.log | tail -100 | sort -u
```

### 2.4 Verificar Integrações Externas

- [ ] API Zello MIND respondendo
- [ ] API OpenAI respondendo (se usada)
- [ ] SMTP enviando emails
- [ ] Google APIs funcionando (Gmail/Drive)

**Teste rápido:**

```python
# test_integrations.py
import requests
from config import config

# Teste Zello MIND
response = requests.get(
    f"{config.ZELLO_BASE_URL}/health",
    headers={"Authorization": f"Bearer {config.ZELLO_API_KEY}"},
    timeout=10
)
print(f"Zello: {response.status_code}")

# Teste OpenAI
import openai
openai.api_key = config.OPENAI_API_KEY
try:
    openai.models.list()
    print("OpenAI: OK")
except:
    print("OpenAI: FALHOU")
```

---

## 3. Checklist Mensal

### 3.1 Backup Completo

Ver seção [4. Backups](#4-backups) para detalhes.

- [ ] Backup do banco de dados
- [ ] Backup dos arquivos de configuração
- [ ] Backup dos uploads importantes
- [ ] Backup dos logs (últimos 30 dias)
- [ ] Testar restauração do backup

### 3.2 Atualização de Dependências

```bash
# Listar dependências desatualizadas
pip list --outdated

# Atualizar dependências de segurança
pip install --upgrade pip
pip install --upgrade -r requirements.txt

# Testar após atualização
python -m pytest tests/
```

### 3.3 Revisão de Performance

```bash
# Top 10 endpoints mais lentos (via logs)
grep "api" /var/log/nginx/access.log | awk '{print $7, $10}' | sort -k2 -rn | head -10

# Queries mais lentas do banco (SQLite)
# Habilite query logging primeiro
```

### 3.4 Auditoria de Segurança

- [ ] Senhas/tokens ainda válidos
- [ ] Certificado SSL ainda válido (se HTTPS)
- [ ] Logs de acesso sem atividades suspeitas
- [ ] Dependências sem vulnerabilidades conhecidas

```bash
# Verificar vulnerabilidades
pip install safety
safety check --json
```

### 3.5 Documentação

- [ ] Atualizar documentação com mudanças recentes
- [ ] Documentar incidentes do mês
- [ ] Atualizar diagramas de arquitetura (se mudou)

---

## 4. Backups

### 4.1 Estratégia de Backup

**Regra 3-2-1:**
- **3** cópias dos dados
- **2** tipos diferentes de mídia
- **1** cópia offsite (fora do servidor)

### 4.2 Backup do Banco de Dados

#### SQLite

```bash
#!/bin/bash
# backup_db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
DB_FILE="/app/app.db"

mkdir -p $BACKUP_DIR

# Backup
sqlite3 $DB_FILE ".backup '$BACKUP_DIR/app_$DATE.db'"

# Comprimir
gzip $BACKUP_DIR/app_$DATE.db

# Manter apenas últimos 30 backups
ls -t $BACKUP_DIR/*.db.gz | tail -n +31 | xargs rm -f

echo "Backup concluído: app_$DATE.db.gz"
```

#### PostgreSQL

```bash
#!/bin/bash
# backup_postgres.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/database"
DB_NAME="hu_automation"
DB_USER="postgres"

mkdir -p $BACKUP_DIR

# Backup
pg_dump -U $DB_USER -Fc $DB_NAME > $BACKUP_DIR/${DB_NAME}_$DATE.dump

# Manter últimos 30 dias
find $BACKUP_DIR -name "*.dump" -mtime +30 -delete

echo "Backup concluído: ${DB_NAME}_$DATE.dump"
```

### 4.3 Backup de Arquivos

```bash
#!/bin/bash
# backup_files.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/files"
APP_DIR="/app"

mkdir -p $BACKUP_DIR

# Arquivos importantes
tar -czf $BACKUP_DIR/app_files_$DATE.tar.gz \
    $APP_DIR/.env \
    $APP_DIR/config.py \
    $APP_DIR/uploads \
    $APP_DIR/static/custom \
    --exclude='*.pyc' \
    --exclude='__pycache__'

# Manter últimos 7 backups
ls -t $BACKUP_DIR/app_files_*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup de arquivos concluído"
```

### 4.4 Backup Automático

**Agendar com Cron:**

```bash
# Editar crontab
crontab -e

# Adicionar linhas:
# Backup diário do banco (2h da manhã)
0 2 * * * /app/scripts/backup_db.sh >> /var/log/backups.log 2>&1

# Backup semanal de arquivos (domingo, 3h)
0 3 * * 0 /app/scripts/backup_files.sh >> /var/log/backups.log 2>&1

# Limpeza de uploads (diária, 4h)
0 4 * * * find /app/uploads -mtime +7 -delete
```

### 4.5 Restauração de Backup

#### SQLite

```bash
# Parar aplicação
systemctl stop hu-automation

# Restaurar
gunzip -c /backups/database/app_20250114_020000.db.gz > /app/app.db

# Reiniciar
systemctl start hu-automation
```

#### PostgreSQL

```bash
# Restaurar
pg_restore -U postgres -d hu_automation /backups/database/hu_automation_20250114.dump
```

### 4.6 Teste de Restauração

**⚠️ Teste mensalmente em ambiente separado!**

```bash
# Criar ambiente de teste
mkdir /tmp/restore_test
cd /tmp/restore_test

# Restaurar backup
gunzip -c /backups/database/latest.db.gz > app.db

# Verificar integridade
sqlite3 app.db "PRAGMA integrity_check;"

# Contar registros
sqlite3 app.db "SELECT COUNT(*) FROM transcription_jobs;"
```

---

## 5. Monitoramento

### 5.1 Métricas Importantes

| Métrica | Onde Ver | Threshold Alerta |
|---------|----------|------------------|
| CPU | `top` ou `htop` | > 80% por 5min |
| Memória | `free -h` | < 20% livre |
| Disco | `df -h` | < 10% livre |
| Uptime | `uptime` | Reinicialização não planejada |
| Processos | `ps aux` | hu-automation ausente |
| Logs erro | `tail -f error.log` | > 10 erros/min |
| Taxa sucesso | API `/api/stats` | < 80% |

### 5.2 Dashboard de Monitoramento

**Opção 1: Script Python Simples**

```python
# monitor.py
import psutil
import requests
from datetime import datetime

def check_system():
    """Verifica saúde do sistema."""
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'status': 'OK'
    }
    
    # Verificar API
    try:
        response = requests.get('http://localhost:5000/api/repository-stats', timeout=5)
        if response.status_code == 200:
            report['api_status'] = 'OK'
            report['stats'] = response.json().get('stats', {})
        else:
            report['api_status'] = 'ERROR'
            report['status'] = 'WARN'
    except:
        report['api_status'] = 'DOWN'
        report['status'] = 'CRITICAL'
    
    # Alertas
    alerts = []
    if report['cpu_percent'] > 80:
        alerts.append('CPU alta')
    if report['memory_percent'] > 80:
        alerts.append('Memória alta')
    if report['disk_percent'] > 90:
        alerts.append('Disco cheio')
    
    report['alerts'] = alerts
    if alerts:
        report['status'] = 'WARN'
    
    return report

if __name__ == '__main__':
    report = check_system()
    print(f"Status: {report['status']}")
    print(f"CPU: {report['cpu_percent']}%")
    print(f"Memória: {report['memory_percent']}%")
    print(f"Disco: {report['disk_percent']}%")
    print(f"API: {report['api_status']}")
    
    if report['alerts']:
        print(f"⚠️ Alertas: {', '.join(report['alerts'])}")
```

**Executar de hora em hora:**

```bash
# Crontab
0 * * * * /app/venv/bin/python /app/scripts/monitor.py >> /var/log/monitor.log 2>&1
```

**Opção 2: Prometheus + Grafana**

```yaml
# docker-compose.yml (adicionar)
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 5.3 Alertas por Email

```python
# alert_monitor.py
import smtplib
from email.mime.text import MIMEText
from config import config

def send_alert(subject: str, body: str):
    """Envia alerta por email."""
    msg = MIMEText(body)
    msg['Subject'] = f"[HU Automation] {subject}"
    msg['From'] = config.EMAIL_FROM
    msg['To'] = 'admin@empresa.com'
    
    with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        server.send_message(msg)

# Usar no monitor
report = check_system()
if report['status'] in ['WARN', 'CRITICAL']:
    send_alert(
        f"Sistema em {report['status']}",
        f"Alertas: {report['alerts']}\n\nDetalhes: {report}"
    )
```

---

## 6. Logs

### 6.1 Localização dos Logs

```
/var/log/hu-automation/
├── app.log              # Log principal da aplicação
├── error.log            # Apenas erros
├── access.log           # Acessos (se Nginx)
├── gunicorn.log         # Log do Gunicorn
└── backups.log          # Log de backups
```

### 6.2 Rotação de Logs

**Configurar logrotate:**

```bash
# /etc/logrotate.d/hu-automation

/var/log/hu-automation/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload hu-automation > /dev/null 2>&1 || true
    endscript
}
```

### 6.3 Análise de Logs

**Ver logs em tempo real:**

```bash
# Todos os logs
tail -f /var/log/hu-automation/app.log

# Apenas erros
tail -f /var/log/hu-automation/error.log | grep ERROR

# Filtrar por palavra-chave
tail -f /var/log/hu-automation/app.log | grep "process"
```

**Estatísticas de logs:**

```bash
# Contar erros por hora (últimas 24h)
grep "ERROR" /var/log/hu-automation/app.log | grep $(date +%Y-%m-%d) | cut -d: -f1 | sort | uniq -c

# Top 10 erros mais comuns
grep "ERROR" /var/log/hu-automation/app.log | awk -F'ERROR' '{print $2}' | sort | uniq -c | sort -rn | head -10

# Erros por usuário
grep "ERROR" /var/log/hu-automation/app.log | grep -oP 'user=\K[^\s]+' | sort | uniq -c
```

### 6.4 Logs Estruturados

**Melhorar logging no código:**

```python
import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """Formatter que gera logs em JSON."""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configurar
handler = logging.FileHandler('/var/log/hu-automation/app.json.log')
handler.setFormatter(JsonFormatter())
logger = logging.getLogger()
logger.addHandler(handler)
```

---

## 7. Atualizações

### 7.1 Processo de Atualização Seguro

**Preparação:**

1. **Avisar usuários** (se aplicável)
2. **Fazer backup completo**
3. **Testar em staging primeiro**
4. **Ler changelog/release notes**
5. **Planejar rollback se necessário**

**Execução:**

```bash
# 1. Backup
./scripts/backup_db.sh
./scripts/backup_files.sh

# 2. Entrar no diretório
cd /app/hu-automation

# 3. Baixar atualizações
git fetch origin
git log HEAD..origin/main  # Ver o que mudou
git pull origin main

# 4. Ativar ambiente virtual
source venv/bin/activate

# 5. Atualizar dependências
pip install -r requirements.txt --upgrade

# 6. Aplicar migrations
alembic upgrade head

# 7. Reiniciar serviço
systemctl restart hu-automation

# 8. Verificar
systemctl status hu-automation
curl http://localhost:5000/api/validate-config

# 9. Monitorar logs
tail -f /var/log/hu-automation/app.log
```

### 7.2 Rollback

**Se algo der errado:**

```bash
# 1. Parar serviço
systemctl stop hu-automation

# 2. Voltar código
git log  # Ver commits
git reset --hard HASH_DO_COMMIT_ANTERIOR

# 3. Restaurar banco (se necessário)
gunzip -c /backups/database/latest.db.gz > /app/app.db

# 4. Reinstalar dependências antigas
pip install -r requirements.txt --force-reinstall

# 5. Downgrade migrations (se necessário)
alembic downgrade -1

# 6. Reiniciar
systemctl start hu-automation
```

### 7.3 Atualizações de Segurança

**Prioridade ALTA - aplicar imediatamente:**

```bash
# Verificar vulnerabilidades
pip install safety
safety check

# Se houver vulnerabilidades CRÍTICAS:
pip install PACOTE --upgrade
# Testar
# Deploy imediato
```

---

## 8. Problemas em Produção

### 8.1 Serviço Não Inicia

**Diagnóstico:**

```bash
# Ver status detalhado
systemctl status hu-automation -l

# Ver logs do systemd
journalctl -u hu-automation -n 50

# Tentar rodar manualmente
cd /app/hu-automation
source venv/bin/activate
python app.py
```

**Causas comuns:**
- Porta já em uso
- .env com erro de sintaxe
- Dependência faltando
- Banco de dados corrompido

### 8.2 Performance Lenta

**Diagnóstico:**

```bash
# Ver processos pesados
top -o %CPU

# Ver conexões de rede
netstat -tuln | grep 5000

# Ver queries lentas (se PostgreSQL)
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

**Soluções:**

1. **Aumentar workers do Gunicorn:**
```bash
# /etc/systemd/system/hu-automation.service
ExecStart=/app/venv/bin/gunicorn --workers 8 --timeout 120 app:app
```

2. **Adicionar cache:**
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/stats')
@cache.cached(timeout=300)  # 5 minutos
def get_stats():
    # ...
```

3. **Otimizar queries:**
```python
# Antes (N+1 query)
jobs = TranscriptionJob.query.all()
for job in jobs:
    print(job.artifacts)  # Query para cada job!

# Depois (eager loading)
jobs = TranscriptionJob.query\
    .options(joinedload(TranscriptionJob.artifacts))\
    .all()
```

### 8.3 Erro 500 Intermitente

**Diagnóstico:**

```bash
# Ver erros recentes
grep "500" /var/log/nginx/access.log | tail -20

# Correlacionar com erro no app
grep -A 10 "ERROR" /var/log/hu-automation/error.log | tail -50
```

**Causas comuns:**
- Timeout de API externa (Zello/OpenAI)
- Conexão do banco travando
- Memory leak

**Soluções:**

1. **Aumentar timeouts:**
```python
# services/llm_service.py
requests.post(url, json=data, timeout=120)  # Era 60
```

2. **Adicionar retry:**
```python
from tenacity import retry, wait_exponential, stop_after_attempt

@retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
def call_external_api():
    # ...
```

### 8.4 Banco de Dados Travado

**SQLite:**

```bash
# Verificar se está travado
lsof /app/app.db

# Verificar integridade
sqlite3 /app/app.db "PRAGMA integrity_check;"

# Se corrompido, restaurar backup
cp /app/app.db /app/app.db.corrupted
gunzip -c /backups/database/latest.db.gz > /app/app.db
```

**PostgreSQL:**

```sql
-- Ver locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Ver processos bloqueados
SELECT pid, query FROM pg_stat_activity WHERE wait_event_type IS NOT NULL;

-- Matar processo travado (cuidado!)
SELECT pg_terminate_backend(PID);
```

---

## 9. Performance

### 9.1 Benchmarking

```bash
# Instalar Apache Bench
sudo apt install apache2-utils

# Testar endpoint
ab -n 1000 -c 10 http://localhost:5000/api/repository-stats

# Resultados importantes:
# - Requests per second
# - Time per request
# - Failed requests
```

### 9.2 Otimizações

**Caching:**

```python
# Cache de configurações
from functools import lru_cache

@lru_cache(maxsize=1)
def get_llm_config():
    # Carrega config apenas uma vez
    return {...}
```

**Compressão:**

```python
# Comprimir responses grandes
from flask_compress import Compress

Compress(app)
```

**CDN para assets estáticos:**

```html
<!-- Usar CDN para bibliotecas -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
```

---

## 10. Segurança

### 10.1 Checklist de Segurança

- [ ] HTTPS habilitado (certificado SSL válido)
- [ ] Firewall configurado (apenas portas necessárias)
- [ ] `.env` com permissões 600 (`chmod 600 .env`)
- [ ] Senhas fortes e únicas
- [ ] API keys com escopo mínimo necessário
- [ ] Rate limiting configurado
- [ ] CORS configurado corretamente
- [ ] Dependências sem vulnerabilidades
- [ ] Logs não expõem dados sensíveis
- [ ] Backup criptografado

### 10.2 Configurar HTTPS (Let's Encrypt)

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d seu-dominio.com

# Renovação automática (já vem configurada)
sudo certbot renew --dry-run
```

### 10.3 Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/process')
@limiter.limit("10 per minute")
def process():
    # ...
```

### 10.4 Auditoria de Acessos

```python
# Logar todos os acessos sensíveis
@app.before_request
def log_request():
    if request.path.startswith('/api/'):
        logger.info(f"API Access: {request.method} {request.path} from {request.remote_addr}")
```

---

## 📞 Contato Emergencial

**Durante horário comercial:**
- Email: kassia.costa@zello.tec.br
- Slack: #hu-automation

**Fora do horário (emergências):**
- On-call: [número do responsável]

---

## 📝 Registro de Incidentes

Mantenha um log de incidentes em: `/docs/incidents.md`

**Template:**

```markdown
## Incidente: [Descrição breve]

**Data:** 2025-01-14 15:30  
**Severidade:** Crítica / Alta / Média / Baixa  
**Duração:** 45 minutos  

**Descrição:**
Sistema ficou indisponível devido a disco cheio.

**Impacto:**
- 0 usuários afetados (fora do horário)
- 15 jobs não processados

**Causa Raiz:**
Logs não estavam sendo rotacionados.

**Resolução:**
1. Limpeza manual de logs antigos
2. Configurado logrotate
3. Adicionado alerta de disco

**Ações Preventivas:**
- [ ] Monitorar uso de disco diariamente
- [ ] Alerta automático quando > 80%
- [ ] Revisar política de retenção de logs
```

---

## 🎓 Conclusão

Manter um sistema em produção requer:
- ✅ Monitoramento constante
- ✅ Backups regulares (e testados!)
- ✅ Documentação atualizada
- ✅ Resposta rápida a incidentes
- ✅ Melhorias contínuas

**Lembre-se:** Melhor prevenir que remediar! 🛡️

---

*Última atualização: Novembro 2025*

