import sys
import os
import uuid
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import APIRouter, HTTPException, Depends
from database.db import get_db_connection
from backend.schemas.schemas import PredictRequest
from ml.predict import DiseasePredictor

router = APIRouter(prefix="/api", tags=["Prediction"])

try:
    predictor = DiseasePredictor()
except Exception as e:
    print(f"Warning: Disease Predictor initialization warning: {e}")
    predictor = None

@router.post("/predict")
def predict_disease(request: PredictRequest):
    global predictor
    if predictor is None:
        try:
            predictor = DiseasePredictor()
        except Exception:
            raise HTTPException(status_code=500, detail="Prediction engine is not ready. Train model first.")

    if not request.symptoms:
        raise HTTPException(status_code=400, detail="Please select at least one symptom.")

    res = predictor.predict(request.symptoms)
    if res.get("status") != "success":
        raise HTTPException(status_code=400, detail=res.get("message", "Prediction failed."))

    # Store prediction record in DB
    user_id = request.user_id or "guest_anonymous"
    prediction_id = str(uuid.uuid4())
    top_pred = res["primary_prediction"]
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO predictions 
        (id, user_id, model_version, input_symptoms, predicted_condition, prediction_score, top_results_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        prediction_id,
        user_id,
        res["model_version"],
        json.dumps(res["matched_symptoms"]),
        top_pred["condition"],
        top_pred["score"],
        json.dumps(res["results"])
    ))

    for sym in res["matched_symptoms"]:
        cursor.execute(
            "INSERT INTO prediction_symptoms (id, prediction_id, symptom_name) VALUES (?, ?, ?)",
            (str(uuid.uuid4()), prediction_id, sym)
        )

    conn.commit()
    conn.close()

    res["prediction_id"] = prediction_id
    return res

@router.get("/predictions")
def get_user_predictions(user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID parameter is required.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, model_version, input_symptoms, predicted_condition, prediction_score, top_results_json, created_at
        FROM predictions
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    predictions = []
    for row in rows:
        item = dict(row)
        item["input_symptoms"] = json.loads(item["input_symptoms"])
        item["top_results"] = json.loads(item["top_results_json"])
        predictions.append(item)

    return predictions

@router.get("/predictions/{prediction_id}")
def get_prediction_detail(prediction_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Prediction record not found.")

    res = dict(row)
    res["input_symptoms"] = json.loads(res["input_symptoms"])
    res["top_results"] = json.loads(res["top_results_json"])
    return res

@router.delete("/predictions/{prediction_id}")
def delete_prediction(prediction_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Prediction {prediction_id} deleted."}
