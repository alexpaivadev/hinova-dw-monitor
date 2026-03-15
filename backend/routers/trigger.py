import logging
import urllib.parse
from datetime import datetime

import docker
from fastapi import APIRouter, HTTPException

from database import execute_query

router = APIRouter(prefix="/trigger", tags=["Trigger"])
logger = logging.getLogger(__name__)

PIPELINE_CONFIG = {
    "ETL PowerCRM Cotacoes": {
        "service": "etl_crm",
        "description": "Cotações PowerCRM → hinova_dw",
    },
    "ETL Rel Veiculos Ativos": {
        "service": "etl_relatorio",
        "description": "Relatório veículos ativos",
    },
    "ETL Rel Alteracao Situacao": {
        "service": "etl_relatorio",
        "description": "Relatório alteração situação",
    },
    "ETL Boletos Janela": {
        "service": "etl_janela_14h",
        "description": "Boletos janela (última janela)",
    },
    "ETL Boletos Mês Atual": {
        "service": "etl_janela_madrugada",
        "description": "Boletos mês atual",
    },
    "ETL Boletos Python": {
        "service": "etl_janela_madrugada",
        "description": "Boletos via Python",
    },
    "ETL Veiculos Python": {
        "service": "etl_hinova_madrugada",
        "description": "Veículos via Python (run_etl.py veiculos)",
    },
    "ETL Alteracao Situacao Veiculo API": {
        "service": "etl_hinova_madrugada",
        "description": "Alteração situação via API",
    },
    "ETL Alteracao Situacao Veiculo": {
        "service": "etl_hinova_madrugada",
        "description": "Alteração situação veículo",
    },
}


def _get_service_replicas(service_name: str):
    """Return (docker_service, current_replicas) or raise HTTPException."""
    try:
        client = docker.from_env()
        services = client.services.list(filters={"name": service_name})
        # Filter exact match (docker filters are prefix-based)
        service = None
        for s in services:
            if s.name == service_name:
                service = s
                break
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service Docker '{service_name}' não encontrado no Swarm",
            )
        spec = service.attrs.get("Spec", {})
        replicas = spec.get("Mode", {}).get("Replicated", {}).get("Replicas", 0)
        return service, replicas
    except docker.errors.DockerException as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao conectar Docker: {str(e)}"
        )


@router.post("/{pipeline_name}")
def trigger_pipeline(pipeline_name: str):
    name = urllib.parse.unquote(pipeline_name)

    if name not in PIPELINE_CONFIG:
        raise HTTPException(
            status_code=400,
            detail=f"Pipeline '{name}' não encontrado na whitelist de disparo",
        )

    config = PIPELINE_CONFIG[name]
    service_name = config["service"]

    service, current_replicas = _get_service_replicas(service_name)

    if current_replicas > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Pipeline já está em execução ({current_replicas} réplica ativa)",
        )

    try:
        service.scale(1)
    except docker.errors.DockerException as e:
        raise HTTPException(
            status_code=500, detail=f"Erro ao escalar service: {str(e)}"
        )

    logger.info("Pipeline '%s' disparado (service: %s)", name, service_name)

    return {
        "triggered": True,
        "pipeline": name,
        "service": service_name,
        "triggered_at": datetime.utcnow().isoformat(),
        "message": f"Service '{service_name}' escalado para 1 réplica",
    }


@router.get("/status/{pipeline_name}")
def trigger_status(pipeline_name: str):
    name = urllib.parse.unquote(pipeline_name)

    rows = execute_query(
        "SELECT workflow, status, ultima_execucao, registros_ok, mensagem "
        "FROM ingest_control WHERE workflow = %s",
        (name,),
    )

    service_replicas = 0
    if name in PIPELINE_CONFIG:
        try:
            _, service_replicas = _get_service_replicas(PIPELINE_CONFIG[name]["service"])
        except Exception:
            pass

    db_row = rows[0] if rows else {}

    return {
        "pipeline": name,
        "db_status": db_row.get("status"),
        "last_run": (
            db_row["ultima_execucao"].isoformat()
            if db_row.get("ultima_execucao")
            else None
        ),
        "rows_loaded": db_row.get("registros_ok"),
        "message": db_row.get("mensagem"),
        "service_replicas": service_replicas,
        "is_running": service_replicas > 0,
        "checked_at": datetime.utcnow().isoformat(),
    }


@router.get("/history")
def trigger_history():
    rows = execute_query(
        "SELECT workflow, status, ultima_execucao, registros_ok, mensagem "
        "FROM ingest_control ORDER BY ultima_execucao DESC NULLS LAST"
    )
    return {
        "data": [
            {
                "pipeline": r["workflow"],
                "status": r["status"],
                "last_run": (
                    r["ultima_execucao"].isoformat()
                    if r.get("ultima_execucao")
                    else None
                ),
                "rows_loaded": r.get("registros_ok"),
                "message": r.get("mensagem"),
            }
            for r in rows
        ],
        "updated_at": datetime.utcnow().isoformat(),
    }
