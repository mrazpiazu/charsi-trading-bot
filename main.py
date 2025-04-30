from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
import logging
from threading import Thread

from utils.database.db import engine
from utils.database import models
from utils.brokers.alpaca_market.alpaca_ws import run_stream

logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating database tables if they don't exist...")
    models.Base.metadata.create_all(bind=engine)

    logger.info("Starting websocket stream...")
    stream_thread = Thread(target=run_stream, daemon=True)
    stream_thread.start()

    yield  # Application is running


app = FastAPI(lifespan=lifespan)


# Simple health check route
@app.get("/")
async def root():
    return {"message": "FastAPI is running with an auto-restarting background task"}
