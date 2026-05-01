"""FastAPI application entry."""

from __future__ import annotations

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from bills_ocr.database import init_db
from bills_ocr.routers import bills as bills_router
from bills_ocr.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db(settings.db_path)
    yield


app = FastAPI(title="Bills OCR", version="0.1.0", lifespan=lifespan)
app.include_router(bills_router.router)


@app.exception_handler(ValueError)
async def value_error_handler(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def run() -> None:
    uvicorn.run(
        "bills_ocr.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )


if __name__ == "__main__":
    run()
