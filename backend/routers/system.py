import time

import psutil
from fastapi import APIRouter

psutil.PROCFS_PATH = "/host/proc"


def _format_uptime(seconds: int) -> str:
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    return f"{days}d {hours}h {minutes}m"


router = APIRouter(prefix="/vps", tags=["System"])


@router.get("")
def get_vps_stats():
    try:
        cpu_percent = psutil.cpu_percent(interval=1)

        mem = psutil.virtual_memory()
        memory = {
            "total": mem.total,
            "used": mem.used,
            "percent": mem.percent,
            "available": mem.available,
        }

        disk = psutil.disk_usage("/")
        disk_info = {
            "total": disk.total,
            "used": disk.used,
            "percent": disk.percent,
            "free": disk.free,
        }

        uptime_sec = int(time.time() - psutil.boot_time())

        top_processes = []
        for proc in sorted(
            psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]),
            key=lambda p: p.info.get("memory_percent") or 0,
            reverse=True,
        )[:5]:
            top_processes.append(
                {
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "cpu_percent": proc.info["cpu_percent"],
                    "memory_percent": (
                        round(proc.info["memory_percent"], 2)
                        if proc.info["memory_percent"]
                        else 0
                    ),
                }
            )

        return {
            "cpu_percent": cpu_percent,
            "memory": memory,
            "disk": disk_info,
            "uptime_seconds": uptime_sec,
            "uptime_formatted": _format_uptime(uptime_sec),
            "top_processes": top_processes,
        }
    except Exception as e:
        return {"error": str(e), "detail": type(e).__name__}
