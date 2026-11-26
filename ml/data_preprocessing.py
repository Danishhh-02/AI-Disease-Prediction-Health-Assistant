import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class MedicalDataPreprocessor:
    def __init__(self, data_path="data/dataset.csv"):
        self.data_path = data_path
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.target_names = []
        
    def load_and_clean_data(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset file not found at {self.data_path}")
        
        df = pd.read_csv(self.data_path)
        
        # Check for missing values
        missing_count = df.isnull().sum().sum()
        
        # Remove duplicates if any
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            df = df.drop_duplicates().reset_index(drop=True)
            
        # Target column is 'prognosis'
        if "prognosis" not in df.columns:
            raise KeyError("Target column 'prognosis' missing from dataset.")
            
        X = df.drop(columns=["prognosis"])
        y_raw = df["prognosis"]
        
        self.feature_names = list(X.columns)
        
        # Encode target classes
        y_encoded = self.label_encoder.fit_transform(y_raw)
        self.target_names = list(self.label_encoder.classes_)
        
        stats = {
            "total_rows": len(df),
            "num_features": len(self.feature_names),
            "num_classes": len(self.target_names),
            "missing_values": int(missing_count),
            "duplicate_rows": int(duplicate_count),
            "classes": self.target_names
        }
        
        return X, y_encoded, stats
        
    def prepare_train_test_split(self, test_size=0.2, random_state=42):
        X, y, stats = self.load_and_clean_data()
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        return X_train, X_test, y_train, y_test, stats

    def save_encoder(self, path="models/encoder.pkl"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            "label_encoder": self.label_encoder,
            "feature_names": self.feature_names,
            "target_names": self.target_names
        }, path)

if __name__ == "__main__":
    preprocessor = MedicalDataPreprocessor()
    X_train, X_test, y_train, y_test, stats = preprocessor.prepare_train_test_split()
    print("Data Preprocessing Summary:")
    print(f"Total Rows: {stats['total_rows']}, Features: {stats['num_features']}, Classes: {stats['num_classes']}")
    print(f"Train Shape: {X_train.shape}, Test Shape: {X_test.shape}")
