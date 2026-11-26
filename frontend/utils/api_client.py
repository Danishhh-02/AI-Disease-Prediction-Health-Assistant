import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

class APIClient:
    @staticmethod
    def is_backend_online():
        try:
            r = requests.get(f"{BACKEND_URL}/", timeout=2)
            return r.status_code == 200
        except Exception:
            return False

    @staticmethod
    def get_symptoms():
        try:
            r = requests.get(f"{BACKEND_URL}/api/symptoms/", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        # Fallback to direct DB query if API server is not running
        from database.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, display_name, category, description FROM symptoms ORDER BY category ASC, display_name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def predict(symptoms, user_id="guest_user"):
        try:
            r = requests.post(f"{BACKEND_URL}/api/predict", json={"symptoms": symptoms, "user_id": user_id}, timeout=3)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        # Fallback to direct ML predictor call and local database persistence
        from ml.predict import DiseasePredictor
        import uuid
        import json
        from database.db import get_db_connection
        
        predictor = DiseasePredictor()
        res = predictor.predict(symptoms)
        if res.get("status") == "success":
            try:
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
                    user_id or "guest_user",
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
            except Exception as e:
                print(f"Direct DB save error: {e}")
        return res

    @staticmethod
    def get_history(user_id=None):
        try:
            params = {"user_id": user_id} if user_id else {}
            r = requests.get(f"{BACKEND_URL}/api/predictions", params=params, timeout=3)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        from database.db import get_db_connection
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_id and user_id not in ("all", None):
            # Fetch for current user or demo records
            cursor.execute("SELECT * FROM predictions WHERE user_id = ? OR user_id IN ('guest_user', 'user_demo_id') ORDER BY created_at DESC", (user_id,))
        else:
            cursor.execute("SELECT * FROM predictions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        res = []
        for r in rows:
            item = dict(r)
            item["input_symptoms"] = json.loads(item["input_symptoms"]) if isinstance(item["input_symptoms"], str) else item["input_symptoms"]
            item["top_results"] = json.loads(item["top_results_json"]) if isinstance(item["top_results_json"], str) else item["top_results_json"]
            res.append(item)
        return res

    @staticmethod
    def get_recent_predictions(user_id=None, limit=3):
        history = APIClient.get_history(user_id)
        return history[:limit] if history else []

    @staticmethod
    def get_prediction_stats(user_id=None):
        history = APIClient.get_history(user_id)
        if not history:
            return {
                "total_predictions": 0,
                "conditions_tested": 0,
                "avg_confidence": 0,
                "most_frequent_condition": "N/A",
                "latest_date": "No records yet"
            }
        total = len(history)
        conditions = [h.get("predicted_condition", "") for h in history if h.get("predicted_condition")]
        from collections import Counter
        most_common = Counter(conditions).most_common(1)[0][0] if conditions else "N/A"
        scores = [h.get("prediction_score", 0) for h in history if isinstance(h.get("prediction_score"), (int, float))]
        avg_score = round(sum(scores) / len(scores) * 100, 1) if scores else 0
        latest = history[0].get("created_at", "N/A")
        return {
            "total_predictions": total,
            "conditions_tested": len(set(conditions)),
            "avg_confidence": avg_score,
            "most_frequent_condition": most_common,
            "latest_date": latest
        }

    @staticmethod
    def delete_history(prediction_id):
        try:
            requests.delete(f"{BACKEND_URL}/api/predictions/{prediction_id}", timeout=3)
        except Exception:
            pass
        from database.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def clear_history(user_id=None):
        from database.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        if user_id and user_id != "all":
            cursor.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
        else:
            cursor.execute("DELETE FROM predictions")
        conn.commit()
        conn.close()

    @staticmethod
    def get_diseases():
        try:
            r = requests.get(f"{BACKEND_URL}/api/diseases/", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        from database.db import get_db_connection
        import json
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM diseases ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        res = []
        for r in rows:
            item = dict(r)
            item["common_symptoms"] = json.loads(item["common_symptoms"]) if item["common_symptoms"] else []
            item["precautions"] = json.loads(item["precautions"]) if item["precautions"] else []
            res.append(item)
        return res

    @staticmethod
    def submit_feedback(prediction_id, rating, comment, user_id):
        try:
            r = requests.post(f"{BACKEND_URL}/api/feedback/", json={"prediction_id": prediction_id, "rating": rating, "comment": comment}, params={"user_id": user_id}, timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        from database.db import get_db_connection
        import uuid
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (id, user_id, prediction_id, rating, comment) VALUES (?, ?, ?, ?, ?)",
                       (str(uuid.uuid4()), user_id, prediction_id, rating, comment))
        conn.commit()
        conn.close()
        return {"status": "success"}

    @staticmethod
    def get_admin_analytics():
        try:
            r = requests.get(f"{BACKEND_URL}/api/admin/analytics", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        from database.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users")
        u_cnt = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) as cnt FROM predictions")
        p_cnt = cursor.fetchone()["cnt"]
        cursor.execute("SELECT COUNT(*) as cnt FROM feedback")
        f_cnt = cursor.fetchone()["cnt"]
        conn.close()
        return {
            "summary": {"total_users": u_cnt, "active_users": u_cnt, "total_predictions": p_cnt, "total_feedback": f_cnt, "avg_feedback_rating": 4.8},
            "top_symptoms": [],
            "daily_predictions": []
        }

    @staticmethod
    def get_admin_models():
        try:
            r = requests.get(f"{BACKEND_URL}/api/admin/models", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        import json
        if os.path.exists("models/metadata.json"):
            with open("models/metadata.json", "r") as f:
                return json.load(f)
        return {}

    @staticmethod
    def get_admin_users():
        try:
            r = requests.get(f"{BACKEND_URL}/api/admin/users", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        from database.db import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT u.id, u.email, u.role, u.is_active, u.created_at, p.full_name, p.age, p.gender FROM users u LEFT JOIN profiles p ON u.id = p.user_id ORDER BY u.created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def update_user_role(user_id, role, is_active):
        try:
            requests.put(f"{BACKEND_URL}/api/admin/users/role", json={"user_id": user_id, "role": role, "is_active": is_active}, timeout=5)
        except Exception:
            from database.db import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET role = ?, is_active = ? WHERE id = ?", (role, 1 if is_active else 0, user_id))
            conn.commit()
            conn.close()

    @staticmethod
    def get_dataset_stats():
        try:
            r = requests.get(f"{BACKEND_URL}/api/admin/dataset", timeout=5)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        import pandas as pd
        if os.path.exists("data/dataset.csv"):
            df = pd.read_csv("data/dataset.csv")
            return {
                "file_name": "dataset.csv",
                "total_rows": len(df),
                "total_features": len(df.columns) - 1,
                "total_classes": len(df["prognosis"].unique()),
                "missing_values": int(df.isnull().sum().sum()),
                "duplicate_rows": int(df.duplicated().sum()),
                "class_distribution": df["prognosis"].value_counts().to_dict()
            }
        return {}
