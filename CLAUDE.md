# Hinova DW Monitor

Dashboard de monitoramento do data warehouse `hinova_dw` e da VPS.

## Stack
- Backend: FastAPI (Python 3.11) na porta 8001
- Frontend: HTML/CSS/JS puro servido via Nginx na porta 3001
- Database: PostgreSQL (container `postgres` na rede `AlexPaivaDev`)
- Deploy: Docker Compose

## Arquivos
- [x] backend/database.py — conexão e queries
- [x] backend/main.py — app FastAPI com CORS e logging
- [x] backend/routers/etl.py — GET /api/etls
- [x] backend/routers/system.py — GET /api/vps
- [x] backend/routers/db_stats.py — GET /api/db/tables + /api/db/health
- [x] backend/routers/alerts.py — GET /api/alerts
- [x] backend/Dockerfile
- [x] backend/requirements.txt
- [x] frontend/index.html — dashboard completo
- [x] docker-compose.yml
- [x] .env

## Schema Real
- `ingest_control`: UMA linha por workflow (upsert), sem histórico
- `meta_atualizacao_tabelas`: append-only, histórico para 4 pipelines de staging
- Status normalizado: SUCESSO→success, ERRO→error, SKIP→skipped, PENDENTE→pending

## Comandos
```bash
docker compose build
docker compose up -d
docker compose logs -f dw-monitor-api
```
