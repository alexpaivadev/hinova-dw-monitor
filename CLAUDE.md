# Hinova DW Monitor

Dashboard de monitoramento do data warehouse `hinova_dw` e da VPS com autenticacao, RBAC e exportacao de dados.

## Stack
- Backend: FastAPI (Python 3.11) na porta 8001
- Frontend: HTML/CSS/JS puro servido via Nginx na porta 3001
- Database: PostgreSQL (container `postgres` na rede `AlexPaivaDev`)
- Auth: JWT (PyJWT) + bcrypt
- Deploy: Docker Swarm via Traefik

## Arquivos
- [x] backend/database.py — conexao e queries (execute_query retorna list[dict], NAO faz commit)
- [x] backend/main.py — app FastAPI com CORS e logging, registra todos os routers
- [x] backend/routers/auth.py — autenticacao JWT + CRUD de usuarios (execute_write com autocommit)
- [x] backend/routers/etl.py — GET /api/etls (require_viewer)
- [x] backend/routers/system.py — GET /api/vps (require_viewer)
- [x] backend/routers/db_stats.py — GET /api/db/tables + /api/db/health (require_viewer)
- [x] backend/routers/alerts.py — GET /api/alerts (require_viewer)
- [x] backend/routers/trigger.py — POST/GET /api/trigger/* (require_admin)
- [x] backend/routers/export.py — GET/POST /api/export/* (require_analyst)
- [x] backend/Dockerfile
- [x] backend/requirements.txt — fastapi, psycopg2, psutil, PyJWT, bcrypt, openpyxl
- [x] frontend/index.html — SPA com 4 abas: dashboard, execucoes, exportar, usuarios
- [x] frontend/login.html — tela de login
- [x] frontend/nginx.conf — SPA routing + cache-busting
- [x] frontend/Dockerfile — nginx com login.html e nginx.conf
- [x] docker-compose.yml
- [x] .env

## Autenticacao e RBAC

### Roles
- `admin` — acesso total (dashboard, execucoes, exportar, gerenciamento de usuarios)
- `analyst` — dashboard + exportar (sem execucoes, sem usuarios)
- `viewer` — somente dashboard

### Tabela
```sql
dw_monitor_users (id, username, password_hash, full_name, role, is_active, created_at, last_login)
```

### Endpoints de Auth
- POST /api/auth/login — retorna JWT (24h)
- GET /api/auth/me — dados do usuario logado
- POST /api/auth/logout
- GET /api/auth/users — listar (admin)
- POST /api/auth/users — criar (admin)
- PUT /api/auth/users/{id} — editar (admin)
- DELETE /api/auth/users/{id} — desativar (admin, soft delete)
- POST /api/auth/users/{id}/reactivate — reativar (admin)

### Regras de seguranca
- Senhas sempre bcrypt (nunca texto puro)
- Nao permite auto-desativacao
- Nao permite ficar sem admin ativo
- execute_write() em auth.py faz autocommit (execute_query nao commita)

## Endpoints de Export
- GET /api/export/tables — tabelas exportaveis com contagem
- GET /api/export/preview/{table} — preview 5 linhas
- POST /api/export/start/{table} — inicia job async, retorna job_id
- GET /api/export/progress/{job_id} — polling progresso
- GET /api/export/result/{job_id} — download Excel

## Schema Real
- `ingest_control`: UMA linha por workflow (upsert), sem historico
- `meta_atualizacao_tabelas`: append-only, historico para 4 pipelines de staging
- Status normalizado: SUCESSO->success, ERRO->error, SKIP->skipped, PENDENTE->pending

## Comandos
```bash
# Build
docker build -t hinova-dw-monitor-api:latest ./backend/
docker build -t hinova-dw-monitor-web:latest ./frontend/

# Deploy
docker stack deploy -c docker-compose.yml dw_monitor

# Restart servicos
docker service update --force dw_monitor_dw-monitor-api
docker service update --force dw_monitor_dw-monitor-web

# Logs
docker service logs -f dw_monitor_dw-monitor-api
docker service logs -f dw_monitor_dw-monitor-web
```
