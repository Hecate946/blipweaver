from fastapi import APIRouter
from app.db.postgres import db

router = APIRouter()

@router.post("/nodes/")
async def create_node(label: str, properties: dict):
    query = "INSERT INTO nodes (label, properties) VALUES ($1, $2) RETURNING id"
    result = await db.fetchrow(query, label, properties)
    return {"node_id": result["id"]}
