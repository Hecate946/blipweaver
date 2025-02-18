from fastapi import FastAPI, Response
from contextlib import asynccontextmanager
from app.db.postgres import db
from app.api.v1.api_v1 import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown without using @app.on_event"""
    await db.connect()
    yield  # Application runs here
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

# Ignore favicon requests
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# Register API routes
app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "BlipWeaver Backend Running"}
