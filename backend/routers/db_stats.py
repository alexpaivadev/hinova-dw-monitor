import logging
from datetime import datetime
from fastapi import APIRouter
from database import execute_query

router = APIRouter(prefix="/db", tags=["Database"])
logger = logging.getLogger(__name__)


@router.get("/tables")
def list_tables():
    sql = """
        SELECT
            schemaname AS schema_name,
            relname AS table_name,
            n_live_tup AS rows_estimate,
            pg_size_pretty(pg_total_relation_size(relid)) AS size_pretty,
            pg_total_relation_size(relid) AS size_bytes
        FROM pg_stat_user_tables
        ORDER BY pg_total_relation_size(relid) DESC NULLS LAST
        LIMIT 15
    """
    rows = execute_query(sql)
    return {"tables": rows}


@router.get("/health")
def db_health():
    result = {
        "total_connections": None,
        "db_size_pretty": None,
        "cache_hit_ratio": None,
        "longest_query_seconds": None,
    }

    try:
        rows = execute_query("SELECT count(*) AS total FROM pg_stat_activity")
        result["total_connections"] = rows[0]["total"]
    except Exception as e:
        logger.warning("total_connections query failed: %s", e)

    try:
        rows = execute_query("""
            SELECT
                pg_size_pretty(pg_database_size(current_database())) AS size_pretty,
                ROUND(pg_database_size(current_database()) / 1073741824.0, 2) AS size_gb
        """)
        result["db_size_pretty"] = rows[0]["size_pretty"]
        result["db_size_gb"] = float(rows[0]["size_gb"])
    except Exception as e:
        logger.warning("db_size query failed: %s", e)

    try:
        rows = execute_query("""
            SELECT ROUND(
                100.0 * sum(blks_hit) / NULLIF(sum(blks_hit) + sum(blks_read), 0), 1
            ) AS ratio
            FROM pg_stat_database
            WHERE datname = current_database()
        """)
        result["cache_hit_ratio"] = float(rows[0]["ratio"]) if rows[0]["ratio"] else None
    except Exception as e:
        logger.warning("cache_hit_ratio query failed: %s", e)

    try:
        rows = execute_query("""
            SELECT COALESCE(
                EXTRACT(EPOCH FROM MAX(NOW() - query_start))::int, 0
            ) AS longest
            FROM pg_stat_activity
            WHERE state != 'idle'
              AND query_start IS NOT NULL
              AND pid != pg_backend_pid()
        """)
        result["longest_query_seconds"] = rows[0]["longest"]
    except Exception as e:
        logger.warning("longest_query query failed: %s", e)

    return {"data": result, "updated_at": datetime.utcnow().isoformat()}
