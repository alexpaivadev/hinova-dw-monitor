from datetime import datetime
from fastapi import APIRouter
from database import execute_query

router = APIRouter(prefix="/etls", tags=["ETL"])

STATUS_MAP = {
    "SUCESSO": "success",
    "ERRO": "error",
    "SKIP": "skipped",
    "PENDENTE": "pending",
    "ok": "success",
}


def _normalize_status(raw_status: str) -> str:
    if raw_status in STATUS_MAP:
        return STATUS_MAP[raw_status]
    return raw_status.lower()


@router.get("")
def list_etls():
    sql = """
        SELECT workflow, status, ultima_execucao, registros_ok, mensagem
        FROM ingest_control
        ORDER BY ultima_execucao DESC NULLS LAST
    """
    rows = execute_query(sql)

    data = []
    status_counts = {"success": 0, "error": 0, "running": 0}

    for row in rows:
        normalized = _normalize_status(row["status"]) if row["status"] else "pending"
        if normalized in status_counts:
            status_counts[normalized] += 1

        data.append({
            "pipeline_name": row["workflow"],
            "status": normalized,
            "last_run": row["ultima_execucao"].isoformat() if row["ultima_execucao"] else None,
            "rows_loaded": row["registros_ok"],
            "duration_seconds": None,
            "error_message": row["mensagem"],
            "success_rate_7d": None,
        })

    total = len(data)
    summary = {
        "total": total,
        "success": status_counts["success"],
        "error": status_counts["error"],
        "running": status_counts["running"],
        "success_rate": round(100 * status_counts["success"] / total, 1) if total else 0,
    }

    return {"data": data, "summary": summary, "updated_at": datetime.utcnow().isoformat()}
