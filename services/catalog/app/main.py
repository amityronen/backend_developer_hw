import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.db import create_pool
from app.routes import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("catalog")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    app.state.pool = await create_pool(settings)
    logger.info("catalog started (db=%s@%s)", settings.db_name, settings.db_host)
    yield
    await app.state.pool.close()


app = FastAPI(
    title="Melon Market - Catalog",
    version="1.0.0",
    docs_url="/api/catalog/docs",
    openapi_url="/api/catalog/openapi.json",
    lifespan=lifespan,
)
app.include_router(router)


def error_body(code: str, message: str) -> dict:
    return {"error": {"code": code, "message": message}}


@app.exception_handler(HTTPException)
async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict) and "code" in exc.detail:
        body = error_body(exc.detail["code"], exc.detail["message"])
    else:
        code = "not_found" if exc.status_code == 404 else "http_error"
        body = error_body(code, str(exc.detail))
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    first = exc.errors()[0]
    location = ".".join(str(part) for part in first["loc"] if part != "body")
    message = f"{location}: {first['msg']}" if location else first["msg"]
    return JSONResponse(status_code=422, content=error_body("validation_error", message))


@app.exception_handler(Exception)
async def unexpected_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled error: %s", exc)
    return JSONResponse(status_code=500, content=error_body("internal_error", "internal server error"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
