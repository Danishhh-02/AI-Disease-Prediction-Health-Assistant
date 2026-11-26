import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException
from database.db import get_db_connection
from backend.schemas.schemas import FeedbackRequest

router = APIRouter(prefix="/api/feedback", tags=["Feedback"])

@router.post("/")
def submit_feedback(request: FeedbackRequest, user_id: str = "guest_user"):
    conn = get_db_connection()
    cursor = conn.cursor()

    feedback_id = str(uuid.uuid4())
    cursor.execute("""
        INSERT INTO feedback (id, user_id, prediction_id, rating, comment)
        VALUES (?, ?, ?, ?, ?)
    """, (feedback_id, user_id, request.prediction_id, request.rating, request.comment))

    conn.commit()
    conn.close()

    return {"status": "success", "message": "Thank you for your feedback!", "feedback_id": feedback_id}

@router.get("/")
def list_feedback():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, f.user_id, f.prediction_id, f.rating, f.comment, f.created_at, p.predicted_condition
        FROM feedback f
        LEFT JOIN predictions p ON f.prediction_id = p.id
        ORDER BY f.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
