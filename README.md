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
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Swarm-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-00d4ff?style=for-the-badge)](LICENSE)

[Acessar Dashboard](https://monitor.alexpaiva.dev) · [Reportar Bug](https://github.com/AlexPaivaDev/hinova-dw-monitor/issues)

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
                          │    │     (frontend)       login.html         │
                          │    └──► FastAPI (:8001) ── API REST          │
                          │              │                              │
                          │              ├──► PostgreSQL (hinova_dw)     │
                          │              │     └─ ingest_control         │
                          │              │     └─ dw_monitor_users       │
                          │              │     └─ tabelas do DW          │
                          │              │                              │
                          │              └──► Docker API (socket)        │
                          │                    └─ Trigger ETL services   │
                          └─────────────────────────────────────────────┘
```

---

## Funcionalidades

### Autenticacao e Controle de Acesso

| Recurso | Descricao |
|---------|-----------|
| **Login com JWT** | Tela de login dedicada com tokens de 24 horas |
| **3 Perfis de Acesso** | `admin` (acesso total), `analyst` (dashboard + export), `viewer` (somente dashboard) |
| **Gerenciamento de Usuarios** | Criar, editar, desativar e reativar usuarios (somente admin) |
| **Protecoes de Seguranca** | Senhas bcrypt, bloqueio de auto-desativacao, protecao do ultimo admin |

### Dashboard — Aba Principal

| Recurso | Descricao |
|---------|-----------|
| **6 KPI Cards** | Total de pipelines, OK, Erro, Taxa de Sucesso, CPU da VPS, Uso de Disco |
| **Tabela ETL** | Status de cada pipeline com badges coloridos (`success` `error` `running` `warn` `skipped`) |
| **Alertas em Tempo Real** | Erros de ETL, processos zombie, pipelines stale, CPU/disco em nivel critico |
| **Grafico Donut** | Status atual dos pipelines com texto central exibindo o total |
| **Grafico de Barras** | Registros processados por pipeline (barras horizontais) |
| **Gauges SVG** | 3 medidores circulares animados para CPU, RAM e Disco |
| **Top 5 Processos** | Processos mais pesados rodando na VPS |
| **Saude do Banco** | Conexoes ativas, cache hit ratio, tamanho do DB, query mais longa |
| **Maiores Tabelas** | Top 15 tabelas com schema badges e tamanho formatado |
| **Auto-refresh** | Atualizacao automatica a cada 30 segundos + relogio em tempo real |

### Execucoes — Aba de Disparo Manual (admin)

| Recurso | Descricao |
|---------|-----------|
| **9 Pipelines** | Whitelist rigida de pipelines permitidos para disparo |
| **Cards de Pipeline** | Ultimo status, data da execucao e total de registros |
| **Modal de Confirmacao** | Confirmacao obrigatoria antes de cada disparo |
| **Monitor em Tempo Real** | Barra de progresso com polling a cada 2 segundos |
| **Docker Swarm** | Integracao direta com a API do Docker para escalar services |

### Exportar — Aba de Exportacao (analyst+)

| Recurso | Descricao |
|---------|-----------|
| **Selecao de Tabela** | Dropdown com todas as tabelas e contagem de registros |
| **Preview** | Visualizacao das 5 primeiras linhas antes de exportar |
| **Filtro por Data** | Selecao de periodo (data inicio/fim) para tabelas com coluna de data |
| **Export Async** | Job em background com barra de progresso em tempo real |
| **Download Excel** | Arquivo .xlsx estilizado com tema dark, headers fixos e colunas auto-width |
| **Limite de Seguranca** | Maximo 500k linhas por exportacao |

### Usuarios — Aba de Gerenciamento (admin)

| Recurso | Descricao |
|---------|-----------|
| **Tabela de Usuarios** | Username, nome, perfil (badge colorido), status, ultimo login |
| **Criar Usuario** | Modal com validacao de username, senha minima, selecao de perfil |
| **Editar Usuario** | Alterar nome, perfil, senha (username readonly) |
| **Desativar/Reativar** | Soft delete com confirmacao modal |
| **Protecoes** | Nao permite auto-desativacao nem ficar sem admin ativo |

---

## Tech Stack

<table>
<tr>
<td align="center" width="150">

**Backend**

FastAPI · Python 3.11<br>
psutil · bcrypt · PyJWT

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

### Autenticacao

| Metodo | Endpoint | Permissao | Descricao |
|--------|----------|-----------|-----------|
| `POST` | `/api/auth/login` | Publico | Login com username/senha, retorna JWT |
| `GET` | `/api/auth/me` | Autenticado | Dados do usuario logado |
| `POST` | `/api/auth/logout` | Autenticado | Logout |

### Gerenciamento de Usuarios

| Metodo | Endpoint | Permissao | Descricao |
|--------|----------|-----------|-----------|
| `GET` | `/api/auth/users` | Admin | Listar todos os usuarios |
| `POST` | `/api/auth/users` | Admin | Criar novo usuario |
| `PUT` | `/api/auth/users/{id}` | Admin | Editar usuario (nome, perfil, senha, status) |
| `DELETE` | `/api/auth/users/{id}` | Admin | Desativar usuario (soft delete) |
| `POST` | `/api/auth/users/{id}/reactivate` | Admin | Reativar usuario |

### Monitoramento

| Metodo | Endpoint | Permissao | Descricao |
|--------|----------|-----------|-----------|
| `GET` | `/health` | Publico | Health check da API |
| `GET` | `/api/etls` | Viewer+ | Status de todos os pipelines + KPIs |
| `GET` | `/api/vps` | Viewer+ | CPU, RAM, disco, uptime e top 5 processos |
| `GET` | `/api/db/tables` | Viewer+ | 15 maiores tabelas do banco |
| `GET` | `/api/db/health` | Viewer+ | Conexoes, cache hit ratio, tamanho do DB |
| `GET` | `/api/alerts` | Viewer+ | Alertas deduplicados |

### Exportacao de Dados

| Metodo | Endpoint | Permissao | Descricao |
|--------|----------|-----------|-----------|
| `GET` | `/api/export/tables` | Analyst+ | Tabelas exportaveis com contagem |
| `GET` | `/api/export/preview/{table}` | Analyst+ | Preview das 5 primeiras linhas |
| `POST` | `/api/export/start/{table}` | Analyst+ | Iniciar job de exportacao async |
| `GET` | `/api/export/progress/{job_id}` | Analyst+ | Progresso do job |
| `GET` | `/api/export/result/{job_id}` | Analyst+ | Download do arquivo Excel |

### Disparo de ETL

| Metodo | Endpoint | Permissao | Descricao |
|--------|----------|-----------|-----------|
| `POST` | `/api/trigger/{pipeline}` | Admin | Disparo manual de ETL (whitelist) |
| `GET` | `/api/trigger/status/{pipeline}` | Admin | Status em tempo real da execucao |
| `GET` | `/api/trigger/history` | Admin | Historico de execucoes manuais |

---

## Controle de Acesso (RBAC)

| Funcionalidade | Viewer | Analyst | Admin |
|----------------|--------|---------|-------|
| Dashboard (KPIs, ETL, alertas, VPS, DB) | ✓ | ✓ | ✓ |
| Exportacao de dados (Excel) | ✗ | ✓ | ✓ |
| Disparo manual de ETL | ✗ | ✗ | ✓ |
| Gerenciamento de usuarios | ✗ | ✗ | ✓ |

---

## Estrutura do Projeto

```
hinova-dw-monitor/
├── README.md
├── CLAUDE.md                  # Instrucoes para AI assistants
├── .env.example               # Template de variaveis de ambiente
├── .gitignore
├── docker-compose.yml         # Stack de deploy (Docker Swarm)
│
├── backend/
│   ├── Dockerfile             # Imagem do backend (Python 3.11)
│   ├── requirements.txt       # fastapi, psycopg2, psutil, PyJWT, bcrypt, openpyxl
│   ├── main.py                # Entrypoint FastAPI + CORS + logging
│   ├── database.py            # Conexao PostgreSQL (execute_query)
│   └── routers/
│       ├── __init__.py
│       ├── auth.py            # /api/auth/* — login, JWT, CRUD usuarios
│       ├── etl.py             # /api/etls — status dos pipelines
│       ├── system.py          # /api/vps — recursos do sistema
│       ├── db_stats.py        # /api/db/* — saude do banco
│       ├── alerts.py          # /api/alerts — alertas em tempo real
│       ├── trigger.py         # /api/trigger/* — disparo manual
│       └── export.py          # /api/export/* — exportacao Excel
│
└── frontend/
    ├── Dockerfile             # Imagem do frontend (Nginx)
    ├── nginx.conf             # SPA routing + cache-busting
    ├── login.html             # Tela de login
    └── index.html             # SPA completa (dashboard, execucoes, exportar, usuarios)
```

---

## Instalacao e Deploy

### Pre-requisitos

- **Docker** com Docker Swarm inicializado (`docker swarm init`)
- **PostgreSQL** com o banco `hinova_dw`, tabelas `ingest_control` e `dw_monitor_users`
- **Traefik** configurado como reverse proxy (para HTTPS)
- Socket do Docker montado (para disparo de ETL via API)

### Passo a passo

```bash
# 1. Clonar o repositorio
git clone https://github.com/AlexPaivaDev/hinova-dw-monitor.git
cd hinova-dw-monitor

# 2. Configurar variaveis de ambiente
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
JWT_SECRET_KEY=sua-chave-secreta
```

```bash
# 3. Build das imagens
docker build -t hinova-dw-monitor-api:latest ./backend/
docker build -t hinova-dw-monitor-web:latest ./frontend/

# 4. Deploy no Docker Swarm
docker stack deploy -c docker-compose.yml dw_monitor

# 5. Verificar se esta rodando
curl http://localhost:8001/health
# Resposta esperada: {"status": "ok"}

# 6. Verificar os servicos
docker service ls | grep dw_monitor
```

### Verificacao rapida

| Check | Comando |
|-------|---------|
| API rodando? | `curl localhost:8001/health` |
| Frontend rodando? | `curl localhost:80` |
| Servicos ativos? | `docker service ls` |
| Logs do backend | `docker service logs dw_monitor_dw-monitor-api` |
| Logs do frontend | `docker service logs dw_monitor_dw-monitor-web` |

---

## Desenvolvimento Local

Para rodar fora do Docker durante o desenvolvimento:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Frontend (qualquer servidor estatico)
cd frontend
python -m http.server 8080
```

---

## Licenca

Distribuido sob a licenca MIT. Veja [`LICENSE`](LICENSE) para mais informacoes.

---

<div align="center">

Desenvolvido por [**Alex Paiva**](https://github.com/AlexPaivaDev)

`#00d4ff` · Hinova DW Monitor · 2025-2026

</div>
