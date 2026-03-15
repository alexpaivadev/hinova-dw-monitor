from datetime import datetime

import psutil
from fastapi import APIRouter

from database import execute_query

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("")
def list_alerts():
    alerts = []
    now_iso = datetime.utcnow().isoformat()

    # 1. ETL errors from ingest_control
    error_sql = """
        SELECT workflow, mensagem
        FROM ingest_control
        WHERE status = 'ERRO'
    """
    for row in execute_query(error_sql):
        alerts.append(
            {
                "severity": "error",
                "source": "ingest_control",
                "message": f"Pipeline '{row['workflow']}' em erro: {row['mensagem']}",
                "detected_at": now_iso,
            }
        )

    # 2. Zombie processes in meta_atualizacao_tabelas
    zombie_sql = """
        SELECT tabela, inicio
        FROM meta_atualizacao_tabelas
        WHERE status = 'executando'
          AND inicio < NOW() - INTERVAL '2 hours'
    """
    zombie_rows = execute_query(zombie_sql)
    zombies_by_tabela = {}
    for row in zombie_rows:
        tabela = row["tabela"]
        if tabela not in zombies_by_tabela:
            zombies_by_tabela[tabela] = {"oldest": row["inicio"], "count": 1}
        else:
            zombies_by_tabela[tabela]["count"] += 1
            if row["inicio"] < zombies_by_tabela[tabela]["oldest"]:
                zombies_by_tabela[tabela]["oldest"] = row["inicio"]

    for tabela, info in zombies_by_tabela.items():
        msg = f"Processo zombie detectado: tabela '{tabela}' executando desde {info['oldest']}"
        if info["count"] > 1:
            msg += f" ({info['count']} instâncias)"
        alerts.append(
            {
                "severity": "warning",
                "source": "meta_atualizacao_tabelas",
                "message": msg,
                "detected_at": now_iso,
            }
        )

    # 3. Stale pipelines (no execution in 25 hours)
    stale_sql = """
        SELECT workflow, ultima_execucao
        FROM ingest_control
        WHERE ultima_execucao < NOW() - INTERVAL '25 hours'
    """
    for row in execute_query(stale_sql):
        alerts.append(
            {
                "severity": "warning",
                "source": "ingest_control",
                "message": f"Pipeline '{row['workflow']}' sem execucao ha mais de 25h (ultima: {row['ultima_execucao']})",
                "detected_at": now_iso,
            }
        )

    # 4. High CPU usage
    try:
        cpu = psutil.cpu_percent(interval=1)
        if cpu > 75:
            alerts.append(
                {
                    "severity": "warning",
                    "source": "system",
                    "message": f"CPU em {cpu}% (limite: 75%)",
                    "detected_at": now_iso,
                }
            )
    except Exception:
        pass

    # 5. High disk usage
    try:
        disk = psutil.disk_usage("/")
        if disk.percent > 80:
            alerts.append(
                {
                    "severity": "error",
                    "source": "system",
                    "message": f"Disco em {disk.percent}% (limite: 80%)",
                    "detected_at": now_iso,
                }
            )
    except Exception:
        pass

    return {
        "alerts": alerts,
        "total": len(alerts),
        "updated_at": now_iso,
    }
