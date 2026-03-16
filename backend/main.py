import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from routers import alerts, auth, db_stats, etl, system, trigger, export

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hinova DW Monitor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start, 4)
    logger.info(
        "%s %s → %s (%.4fs)",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )
    return response


app.include_router(auth.router, prefix="/api")
app.include_router(etl.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(db_stats.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(trigger.router, prefix="/api")
app.include_router(export.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
