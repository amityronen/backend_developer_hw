"""Mock exchange-rate provider used by the catalog service.

Behaves like a slightly unreliable third-party API. See README.md.
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Literal

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Rates Mock", version="1.0.0")

Mode = Literal["random", "ok", "fail", "hang"]
RATES = {"USD": "0.27", "EUR": "0.25"}
HANG_SECONDS = 30.0

state: dict[str, str] = {"mode": "random"}


class ChaosIn(BaseModel):
    mode: Mode


def error(status: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}})


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/rates", response_model=None)
async def rates(base: str = Query("ILS")) -> JSONResponse | dict:
    if base.upper() != "ILS":
        return error(400, "unsupported_base", "only ILS is supported as base currency")

    mode = state["mode"]
    if mode == "fail":
        return error(503, "upstream_unavailable", "rates provider is unavailable")
    if mode == "hang":
        await asyncio.sleep(HANG_SECONDS)
    elif mode == "random":
        await asyncio.sleep(random.uniform(0.0, 0.3))  # nosec B311
        roll = random.random()  # nosec B311
        if roll < 0.05:
            await asyncio.sleep(HANG_SECONDS)
        elif roll < 0.20:
            return error(503, "upstream_unavailable", "rates provider is unavailable")

    return {"base": "ILS", "rates": RATES, "as_of": now_iso()}


@app.get("/_chaos")
async def get_chaos() -> dict[str, str]:
    return {"mode": state["mode"]}


@app.post("/_chaos")
async def set_chaos(body: ChaosIn) -> dict[str, str]:
    state["mode"] = body.mode
    return {"mode": state["mode"]}
