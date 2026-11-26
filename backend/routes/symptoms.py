import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, Query
from database.db import get_db_connection
from typing import Optional, List

router = APIRouter(prefix="/api/symptoms", tags=["Symptoms"])

@router.get("/")
def get_symptoms(category: Optional[str] = None, search: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT id, name, display_name, category, description FROM symptoms WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if search:
        query += " AND (display_name LIKE ? OR name LIKE ?)"
        params.append(f"%{search}%")
        params.append(f"%{search}%")

    query += " ORDER BY category ASC, display_name ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]

@router.get("/categories")
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM symptoms ORDER BY category ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row["category"] for row in rows]

@router.post("/parse-free-text")
def parse_free_text(text: str):
    """Parses arbitrary free-text input and extracts recognized predefined symptom names."""
    if not text:
        return {"matched_symptoms": []}

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, display_name FROM symptoms")
    symptoms = cursor.fetchall()
    conn.close()

    text_lower = text.lower()
    matched = []

    for sym in symptoms:
        raw_name = sym["name"].lower().replace("_", " ")
        disp_name = sym["display_name"].lower()
        if raw_name in text_lower or disp_name in text_lower:
            matched.append(sym["name"])

    return {
        "input_text": text,
        "matched_symptoms": list(set(matched))
    }
