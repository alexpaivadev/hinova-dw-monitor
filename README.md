<div align="center">

```
██╗  ██╗██╗███╗   ██╗ ██████╗ ██╗   ██╗ █████╗     ██████╗ ██╗    ██╗
██║  ██║██║████╗  ██║██╔═══██╗██║   ██║██╔══██╗    ██╔══██╗██║    ██║
███████║██║██╔██╗ ██║██║   ██║██║   ██║███████║    ██║  ██║██║ █╗ ██║
██╔══██║██║██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║    ██║  ██║██║███╗██║
██║  ██║██║██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║    ██████╔╝╚███╔███╔╝
╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝    ╚═════╝  ╚══╝╚══╝
                        M O N I T O R
```

**Dashboard de monitoramento em tempo real para o Data Warehouse Hinova**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Swarm-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-00d4ff?style=for-the-badge)](LICENSE)

[Acessar Dashboard](https://monitor.alexpaiva.dev) · [API Docs](https://monitor.alexpaiva.dev:8001/docs) · [Reportar Bug](https://github.com/AlexPaivaDev/hinova-dw-monitor/issues)

</div>

---

## Sobre o Projeto

O **Hinova DW Monitor** é um painel de monitoramento em tempo real construído para acompanhar a saúde do Data Warehouse `hinova_dw`, seus pipelines ETL, e os recursos da VPS onde ele opera. Desenvolvido com uma interface dark cyberpunk, o dashboard oferece visibilidade completa sobre o ecossistema de dados — desde a taxa de sucesso dos pipelines até o cache hit ratio do PostgreSQL.

O projeto roda em uma VPS Hostinger com Docker Swarm e é acessível via HTTPS através do Traefik.

### Por que este projeto existe?

Pipelines ETL falham silenciosamente. Discos enchem. Queries travam. Este monitor centraliza todas essas informações em um único painel, com alertas em tempo real e a capacidade de disparar ETLs manualmente quando necessário.

---

## Arquitetura

```
                          ┌─────────────────────────────────────────────┐
                          │                   VPS Hostinger              │
                          │                                             │
Browser ──── HTTPS ──────►│  Traefik (:443)                             │
                          │    ├──► Nginx (:80)    ── index.html         │
                          │    │     (frontend)                         │
                          │    └──► FastAPI (:8001) ── API REST          │
                          │              │                              │
                          │              ├──► PostgreSQL (hinova_dw)     │
                          │              │     └─ ingest_control         │
                          │              │     └─ tabelas do DW          │
                          │              │                              │
                          │              └──► Docker API (socket)        │
                          │                    └─ Trigger ETL services   │
                          └─────────────────────────────────────────────┘
```

---

## Funcionalidades

### Dashboard — Aba Principal

| Recurso | Descrição |
|---------|-----------|
| **6 KPI Cards** | Total de pipelines, OK, Erro, Taxa de Sucesso, CPU da VPS, Uso de Disco |
| **Tabela ETL** | Status de cada pipeline com badges coloridos (`success` `error` `running` `warn` `skipped`) |
| **Alertas em Tempo Real** | Erros de ETL, processos zombie, pipelines stale, CPU/disco em nível crítico |
| **Gráfico Donut** | Status atual dos pipelines com texto central exibindo o total |
| **Gráfico de Barras** | Registros processados por pipeline (barras horizontais) |
| **Gauges SVG** | 3 medidores circulares animados para CPU, RAM e Disco |
| **Top 5 Processos** | Processos mais pesados rodando na VPS |
| **Saúde do Banco** | Conexões ativas, cache hit ratio, tamanho do DB, query mais longa |
| **Maiores Tabelas** | Top 15 tabelas com schema badges e tamanho formatado |
| **Auto-refresh** | Atualização automática a cada 30 segundos + relógio em tempo real |
| **Badge de Conexão** | Indicador visual de conectividade (Conectado / Desconectado) |

### Execucoes — Aba de Disparo Manual

| Recurso | Descrição |
|---------|-----------|
| **9 Pipelines** | Whitelist rígida de pipelines permitidos para disparo |
| **Cards de Pipeline** | Ultimo status, data da execução e total de registros |
| **Modal de Confirmação** | Confirmação obrigatória antes de cada disparo |
| **Monitor em Tempo Real** | Barra de progresso com polling a cada 2 segundos |
| **Docker Swarm** | Integração direta com a API do Docker para escalar services |

---

## Tech Stack

<table>
<tr>
<td align="center" width="150">

**Backend**

FastAPI · Python 3.11<br>
psutil · asyncpg

</td>
<td align="center" width="150">

**Frontend**

HTML · CSS · JS<br>
Chart.js · SVG

</td>
<td align="center" width="150">

**Banco de Dados**

PostgreSQL 14<br>
hinova_dw

</td>
<td align="center" width="150">

**Infraestrutura**

Docker Swarm<br>
Traefik · Nginx

</td>
</tr>
</table>

### Design System

- **Tema:** Dark cyberpunk com grid sutil em cyan
- **Paleta:** `#080b10` (fundo) · `#00d4ff` (accent) · `#00ff9d` (sucesso) · `#ff4d6a` (erro) · `#ffd666` (alerta)
- **Fontes:** [Syne](https://fonts.google.com/specimen/Syne) (UI) + [JetBrains Mono](https://www.jetbrains.com/lp/mono/) (dados)
- **Layout:** Sidebar fixa de 64px + topbar com backdrop blur

---

## API Endpoints

### Monitoramento

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check da API |
| `GET` | `/api/etls` | Status de todos os pipelines + summary com KPIs |
| `GET` | `/api/vps` | CPU, RAM, disco, uptime e top 5 processos |
| `GET` | `/api/db/tables` | 15 maiores tabelas do banco |
| `GET` | `/api/db/health` | Conexões, cache hit ratio, tamanho do DB, query mais longa |
| `GET` | `/api/alerts` | Alertas deduplicados (erros, zombies, stale, CPU, disco) |

### Disparo de ETL

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/trigger/{pipeline}` | Disparo manual de ETL (whitelist) |
| `GET` | `/api/trigger/status/{pipeline}` | Status em tempo real da execução |
| `GET` | `/api/trigger/history` | Histórico de execuções manuais |

> A documentação interativa (Swagger UI) está disponível em [`/docs`](https://monitor.alexpaiva.dev:8001/docs).

---

## Estrutura do Projeto

```
hinova-dw-monitor/
├── README.md                  # Este arquivo
├── .env.example               # Template de variáveis de ambiente
├── .gitignore                 # Arquivos ignorados pelo Git
├── CLAUDE.md                  # Instruções para AI assistants
├── docker-compose.yml         # Stack de deploy (Docker Swarm)
│
├── backend/
│   ├── Dockerfile             # Imagem do backend (Python 3.11)
│   ├── requirements.txt       # Dependências Python
│   ├── main.py                # Entrypoint FastAPI + CORS
│   ├── database.py            # Pool de conexões PostgreSQL
│   └── routers/
│       ├── __init__.py
│       ├── etl.py             # /api/etls — status dos pipelines
│       ├── system.py          # /api/vps — recursos do sistema
│       ├── db_stats.py        # /api/db/* — saúde do banco
│       ├── alerts.py          # /api/alerts — alertas em tempo real
│       └── trigger.py         # /api/trigger/* — disparo manual
│
└── frontend/
    ├── Dockerfile             # Imagem do frontend (Nginx)
    └── index.html             # SPA completa (HTML + CSS + JS)
```

---

## Instalacao e Deploy

### Pre-requisitos

- **Docker** com Docker Swarm inicializado (`docker swarm init`)
- **PostgreSQL** com o banco `hinova_dw` e a tabela `ingest_control`
- **Traefik** configurado como reverse proxy (para HTTPS)
- Socket do Docker montado (para disparo de ETL via API)

### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://github.com/AlexPaivaDev/hinova-dw-monitor.git
cd hinova-dw-monitor

# 2. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Preencha com as credenciais do seu PostgreSQL
```

Edite o `.env` com seus dados:

```env
POSTGRES_HOST=seu-host
POSTGRES_PORT=5432
POSTGRES_DB=hinova_dw
POSTGRES_USER=seu-usuario
POSTGRES_PASSWORD=sua-senha
```

```bash
# 3. Build das imagens
docker build -t hinova-dw-monitor-api:latest ./backend/
docker build -t hinova-dw-monitor-web:latest ./frontend/

# 4. Deploy no Docker Swarm
docker stack deploy -c docker-compose.yml dw_monitor

# 5. Verificar se está rodando
curl http://localhost:8001/health
# Resposta esperada: {"status": "healthy"}

# 6. Verificar os serviços
docker service ls | grep dw_monitor
```

### Verificação rápida

| Check | Comando |
|-------|---------|
| API rodando? | `curl localhost:8001/health` |
| Frontend rodando? | `curl localhost:80` |
| Serviços ativos? | `docker service ls` |
| Logs do backend | `docker service logs dw_monitor_api` |
| Logs do frontend | `docker service logs dw_monitor_web` |

---

## Screenshots

<div align="center">

> Em breve: capturas de tela do dashboard em funcionamento.

<!--
![Dashboard Principal](docs/screenshots/dashboard.png)
![Aba de Execuções](docs/screenshots/execucoes.png)
![Alertas](docs/screenshots/alertas.png)
-->

</div>

---

## Desenvolvimento Local

Para rodar fora do Docker durante o desenvolvimento:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (qualquer servidor estático)
cd frontend
python -m http.server 8080
```

---

## Licenca

Distribuído sob a licença MIT. Veja [`LICENSE`](LICENSE) para mais informações.

---

<div align="center">

Desenvolvido por [**Alex Paiva**](https://github.com/AlexPaivaDev)

`#00d4ff` · Hinova DW Monitor · 2025–2026

</div>
