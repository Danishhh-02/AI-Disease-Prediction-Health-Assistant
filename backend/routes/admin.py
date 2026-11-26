import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException
from database.db import get_db_connection
from backend.schemas.schemas import RoleUpdate

router = APIRouter(prefix="/api/admin", tags=["Admin Dashboard"])

@router.get("/analytics")
def get_admin_analytics():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as cnt FROM users")
    total_users = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE is_active = 1")
    active_users = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM predictions")
    total_predictions = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM feedback")
    total_feedback = cursor.fetchone()["cnt"]

    cursor.execute("SELECT AVG(rating) as avg_rating FROM feedback")
    row_avg = cursor.fetchone()
    avg_rating = round(row_avg["avg_rating"], 2) if row_avg["avg_rating"] is not None else 0.0

    # Top selected symptoms
    cursor.execute("""
        SELECT symptom_name, COUNT(*) as count 
        FROM prediction_symptoms 
        GROUP BY symptom_name 
        ORDER BY count DESC 
        LIMIT 10
    """)
    top_symptoms = [dict(r) for r in cursor.fetchall()]

    # Daily prediction counts
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM predictions 
        GROUP BY DATE(created_at) 
        ORDER BY date DESC 
        LIMIT 14
    """)
    daily_predictions = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return {
        "summary": {
            "total_users": total_users,
            "active_users": active_users,
            "total_predictions": total_predictions,
            "total_feedback": total_feedback,
            "avg_feedback_rating": avg_rating
        },
        "top_symptoms": top_symptoms,
        "daily_predictions": daily_predictions
    }

@router.get("/models")
def get_ml_models_info():
    metadata_path = "models/metadata.json"
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Model metadata not found. Run model training first.")

    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    return metadata

@router.get("/users")
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.id, u.email, u.role, u.is_active, u.created_at, p.full_name, p.age, p.gender 
        FROM users u 
        LEFT JOIN profiles p ON u.id = p.user_id 
        ORDER BY u.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

@router.put("/users/role")
def update_user_role(data: RoleUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (data.user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found.")

    is_act = 1 if data.is_active else 0
    cursor.execute(
        "UPDATE users SET role = ?, is_active = ? WHERE id = ?",
        (data.role.upper(), is_act, data.user_id)
    )
    conn.commit()
    conn.close()

    return {"status": "success", "message": f"User {data.user_id} role updated to {data.role.upper()}."}

@router.get("/dataset")
def get_dataset_stats():
    import pandas as pd
    dataset_path = "data/dataset.csv"
    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset file not found.")

    df = pd.read_csv(dataset_path)
    prognosis_col = "prognosis" if "prognosis" in df.columns else df.columns[-1]

    class_counts = df[prognosis_col].value_counts().to_dict()

    return {
        "file_name": "dataset.csv",
        "total_rows": len(df),
        "total_features": len(df.columns) - 1,
        "total_classes": len(class_counts),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "class_distribution": class_counts
    }
