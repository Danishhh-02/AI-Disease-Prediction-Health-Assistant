import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException, Query
from database.db import get_db_connection
from typing import Optional

router = APIRouter(prefix="/api/diseases", tags=["Disease Knowledge Base"])

@router.get("/")
def get_diseases(search: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, name, description, common_symptoms, precautions, when_to_seek_help, source FROM diseases"
    params = []

    if search:
        query += " WHERE name LIKE ? OR description LIKE ?"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY name ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["common_symptoms"] = json.loads(item["common_symptoms"]) if item["common_symptoms"] else []
        item["precautions"] = json.loads(item["precautions"]) if item["precautions"] else []
        result.append(item)

    return result

@router.get("/{disease_id_or_name}")
def get_disease_by_id_or_name(disease_id_or_name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description, common_symptoms, precautions, when_to_seek_help, source FROM diseases WHERE id = ? OR name = ?",
        (disease_id_or_name, disease_id_or_name)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Disease educational information not found.")

    item = dict(row)
    item["common_symptoms"] = json.loads(item["common_symptoms"]) if item["common_symptoms"] else []
    item["precautions"] = json.loads(item["precautions"]) if item["precautions"] else []
    return item
