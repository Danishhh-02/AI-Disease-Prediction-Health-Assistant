import os
import joblib
import numpy as np
import pandas as pd

class DiseasePredictor:
    CRITICAL_SYMPTOMS = {
        "chest_pain": "Chest Pain may indicate acute cardiac or thoracic conditions.",
        "slurred_speech": "Slurred speech or facial drooping may indicate acute cerebrovascular event (Stroke).",
        "weakness_of_one_body_side": "Sudden unilateral weakness is a sign of acute neurological emergency.",
        "altered_sensorium": "Altered sensorium or confusion requires immediate emergency medical evaluation.",
        "coma": "Loss of consciousness is a critical emergency.",
        "acute_liver_failure": "Acute liver insufficiency requires urgent intensive care.",
        "blood_in_sputum": "Hemoptysis (blood in sputum) warrants immediate pulmonology/emergency evaluation."
    }

    def __init__(self, model_path="models/model.pkl", encoder_path="models/encoder.pkl"):
        self.model_path = model_path
        self.encoder_path = encoder_path
        self.model_data = None
        self.encoder_data = None
        self._load_artifacts()

    def _load_artifacts(self):
        if not os.path.exists(self.model_path) or not os.path.exists(self.encoder_path):
            raise FileNotFoundError("Model or encoder artifacts not found. Please train models first.")
        
        self.model_data = joblib.load(self.model_path)
        self.encoder_data = joblib.load(self.encoder_path)
        
        self.model = self.model_data["model"]
        self.model_name = self.model_data["model_name"]
        self.feature_names = self.encoder_data["feature_names"]
        self.target_names = self.encoder_data["target_names"]

    def validate_and_encode(self, selected_symptoms):
        """Converts list of symptom strings to 1D binary feature array."""
        vector = np.zeros(len(self.feature_names), dtype=int)
        matched_symptoms = []
        unmatched_symptoms = []

        symptom_set = set(selected_symptoms)
        for i, feat in enumerate(self.feature_names):
            if feat in symptom_set:
                vector[i] = 1
                matched_symptoms.append(feat)

        for sym in selected_symptoms:
            if sym not in self.feature_names:
                unmatched_symptoms.append(sym)

        return vector, matched_symptoms, unmatched_symptoms

    def check_emergency(self, selected_symptoms):
        alerts = []
        for sym in selected_symptoms:
            if sym in self.CRITICAL_SYMPTOMS:
                alerts.append({
                    "symptom": sym,
                    "warning": self.CRITICAL_SYMPTOMS[sym]
                })
        return {
            "is_emergency": len(alerts) > 0,
            "emergency_alerts": alerts
        }

    def predict(self, selected_symptoms, top_k=3):
        if not selected_symptoms:
            return {"status": "error", "message": "No symptoms provided."}

        vector, matched, unmatched = self.validate_and_encode(selected_symptoms)
        if sum(vector) == 0:
            return {
                "status": "error",
                "message": "None of the selected symptoms matched valid feature inputs."
            }

        input_df = pd.DataFrame([vector], columns=self.feature_names)

        # Get probabilities
        if hasattr(self.model, "predict_proba"):
            probas = self.model.predict_proba(input_df)[0]
        else:
            # Fallback if model doesn't support predict_proba
            pred_idx = self.model.predict(input_df)[0]
            probas = np.zeros(len(self.target_names))
            probas[pred_idx] = 1.0

        # Sort top K
        top_indices = np.argsort(probas)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            condition_name = self.target_names[idx]
            score = float(probas[idx])
            results.append({
                "condition": condition_name,
                "score": round(score, 4),
                "percentage": f"{round(score * 100, 1)}%"
            })

        # Calculate symptom contributions / feature importance
        top_class_idx = top_indices[0] if len(top_indices) > 0 else None
        symptom_contributions = self._explain_prediction(vector, matched, top_class_idx=top_class_idx)

        emergency_info = self.check_emergency(selected_symptoms)

        return {
            "status": "success",
            "model_version": self.model_name,
            "matched_symptoms": matched,
            "unmatched_symptoms": unmatched,
            "primary_prediction": results[0] if results else None,
            "results": results,
            "explainability": {
                "symptom_contributions": symptom_contributions
            },
            "emergency_assessment": emergency_info,
            "disclaimer": (
                "This application provides machine-learning-based health information for educational purposes only. "
                "Its predictions are not a medical diagnosis and should not be used to start, stop, or change treatment. "
                "For persistent, severe, or concerning symptoms, consult a qualified healthcare professional."
            )
        }

    def _explain_prediction(self, vector, matched_symptoms, top_class_idx=None):
        """Generates feature importance scores for user's matched active symptoms."""
        contributions = []
        if not matched_symptoms:
            return contributions

        if top_class_idx is not None and hasattr(self.model, "coef_"):
            coefs = self.model.coef_[top_class_idx]
            raw_scores = {}
            for sym in matched_symptoms:
                if sym in self.feature_names:
                    idx = self.feature_names.index(sym)
                    val = float(coefs[idx])
                    raw_scores[sym] = max(0.05, abs(val) if val != 0 else 0.05)
            total = sum(raw_scores.values()) or 1.0
            for sym, sc in raw_scores.items():
                contributions.append({"symptom": sym, "importance": round(sc / total, 4)})
            contributions.sort(key=lambda x: x["importance"], reverse=True)
        elif hasattr(self.model, "feature_importances_"):
            importances = self.model.feature_importances_
            raw_scores = {}
            for sym in matched_symptoms:
                if sym in self.feature_names:
                    idx = self.feature_names.index(sym)
                    score = float(importances[idx])
                    raw_scores[sym] = max(0.001, score)
            total = sum(raw_scores.values()) or 1.0
            for sym, sc in raw_scores.items():
                contributions.append({"symptom": sym, "importance": round(sc / total, 4)})
            contributions.sort(key=lambda x: x["importance"], reverse=True)
        else:
            uniform_val = round(1.0 / max(1, len(matched_symptoms)), 4)
            for sym in matched_symptoms:
                contributions.append({"symptom": sym, "importance": uniform_val})

        return contributions

if __name__ == "__main__":
    predictor = DiseasePredictor()
    sample = ["fever", "cough", "fatigue", "chest_pain"]
    res = predictor.predict(sample)
    print("Inference Test Result:")
    print(res)
