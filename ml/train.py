import time
import json
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
from data_preprocessing import MedicalDataPreprocessor

def train_and_evaluate_models():
    os.makedirs("models", exist_ok=True)
    preprocessor = MedicalDataPreprocessor("data/dataset.csv")
    X_train, X_test, y_train, y_test, dataset_stats = preprocessor.prepare_train_test_split()
    
    preprocessor.save_encoder("models/encoder.pkl")
    
    candidate_models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Support Vector Machine": SVC(probability=True, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, random_state=42, eval_metric="mlogloss")
    }
    
    comparison_results = {}
    best_model_name = None
    best_f1 = -1.0
    best_model_obj = None
    
    print("Starting Model Training & Comparison Pipeline...")
    print("=" * 60)
    
    for name, model in candidate_models.items():
        start_time = time.time()
        model.fit(X_train, y_train)
        fit_time = time.time() - start_time
        
        # Inference time test
        infer_start = time.time()
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test) if hasattr(model, "predict_proba") else None
        infer_time_ms = ((time.time() - infer_start) / len(X_test)) * 1000.0
        
        acc = accuracy_score(y_test, y_pred)
        prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(y_test, y_pred, average="macro", zero_division=0)
        prec_weighted, rec_weighted, f1_weighted, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted", zero_division=0)
        
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        comparison_results[name] = {
            "accuracy": round(float(acc), 4),
            "precision_macro": round(float(prec_macro), 4),
            "recall_macro": round(float(rec_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "precision_weighted": round(float(prec_weighted), 4),
            "recall_weighted": round(float(rec_weighted), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "fit_time_sec": round(float(fit_time), 4),
            "inference_time_ms": round(float(infer_time_ms), 4),
            "confusion_matrix": cm
        }
        
        print(f"[{name}] Acc: {acc:.4f} | F1 (macro): {f1_macro:.4f} | Fit: {fit_time:.2f}s | Infer: {infer_time_ms:.3f}ms")
        
        # Select model based on macro F1 score
        if f1_macro > best_f1:
            best_f1 = f1_macro
            best_model_name = name
            best_model_obj = model

    print("=" * 60)
    print(f"Selected Best Model: {best_model_name} with F1-score: {best_f1:.4f}")
    
    # Save best model object
    joblib.dump({
        "model_name": best_model_name,
        "model": best_model_obj,
        "feature_names": preprocessor.feature_names,
        "target_names": preprocessor.target_names
    }, "models/model.pkl")
    
    # Save metadata
    metadata = {
        "selected_model": best_model_name,
        "best_f1_score": round(float(best_f1), 4),
        "trained_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_stats": dataset_stats,
        "model_comparison": comparison_results
    }
    
    with open("models/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
        
    print("Model training pipeline completed successfully! Model artifacts saved to models/")

if __name__ == "__main__":
    train_and_evaluate_models()
