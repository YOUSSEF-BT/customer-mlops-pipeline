import os
import sys
import pandas as pd
import numpy as np
import mlflow
import mlflow.xgboost
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    f1_score, roc_auc_score, confusion_matrix, classification_report
)
import xgboost as xgb
import joblib
import warnings
from datetime import datetime
import json

warnings.filterwarnings('ignore')

class ChurnModelPipeline:
    def __init__(self, data_path):
        self.data_path = data_path
        self.model = None
        self.features = None
        self.label_encoders = {}
        self.scaler = None
        
    def load_data(self):
        """Charge et prépare les données"""
        print("📥 Chargement des données...")
        df = pd.read_csv(self.data_path)
        
        # Conversion de TotalCharges en numérique
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        
        # Suppression des valeurs nulles
        initial_rows = len(df)
        df = df.dropna()
        print(f"✅ Données nettoyées: {len(df)}/{initial_rows} lignes conservées")
        
        return df
    
    def preprocess_data(self, df):
        """Prétraitement des données"""
        print("🔄 Prétraitement des données...")
        
        # Création de features additionnelles
        df['AvgChargesPerMonth'] = df['TotalCharges'] / (df['tenure'] + 1e-6)
        df['IsLongTermCustomer'] = df['tenure'].apply(lambda x: 1 if x > 24 else 0)
        df['HighSpender'] = df['MonthlyCharges'].apply(lambda x: 1 if x > 70 else 0)
        
        # Encodage des variables catégorielles
        categorical_cols = df.select_dtypes(include=['object']).columns
        categorical_cols = categorical_cols.drop('customerID', errors='ignore')
        
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            self.label_encoders[col] = le
        
        # Séparation features/target
        target = 'Churn'
        if target in df.columns:
            X = df.drop(columns=['customerID', target], errors='ignore')
            y = df[target]
            self.features = list(X.columns)
        else:
            raise ValueError(f"Colonne cible '{target}' non trouvée")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalisation
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"✅ Données prétraitées: {X_train.shape[0]} train, {X_test.shape[0]} test")
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_model(self, X_train, y_train, X_test, y_test):
        """Entraîne le modèle avec MLflow tracking"""
        print("🎯 Début de l'entraînement avec MLflow...")
        
        # Configuration MLflow
        mlflow.set_experiment("Churn_Prediction")
        
        with mlflow.start_run(run_name=f"churn_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Paramètres du modèle
            params = {
                'n_estimators': 150,
                'max_depth': 7,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'eval_metric': 'logloss'
            }
            
            # Log des paramètres
            mlflow.log_params(params)
            
            # Entraînement
            print("🤖 Entraînement du modèle XGBoost...")
            self.model = xgb.XGBClassifier(**params)
            self.model.fit(
                X_train, y_train,
                eval_set=[(X_test, y_test)],
                verbose=False
            )
            
            # Prédictions
            y_pred = self.model.predict(X_test)
            y_pred_proba = self.model.predict_proba(X_test)[:, 1]
            
            # Calcul des métriques
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred),
                'recall': recall_score(y_test, y_pred),
                'f1_score': f1_score(y_test, y_pred),
                'roc_auc': roc_auc_score(y_test, y_pred_proba)
            }
            
            # Log des métriques
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
            
            # Log du modèle
            mlflow.xgboost.log_model(self.model, "churn_model")
            
            # Log des artifacts
            artifact_dir = "artifacts"
            os.makedirs(artifact_dir, exist_ok=True)
            
            # Sauvegarde des encodeurs et scaler
            joblib.dump(self.label_encoders, f"{artifact_dir}/label_encoders.pkl")
            joblib.dump(self.scaler, f"{artifact_dir}/scaler.pkl")
            joblib.dump(self.features, f"{artifact_dir}/features.pkl")
            
            mlflow.log_artifact(f"{artifact_dir}/label_encoders.pkl")
            mlflow.log_artifact(f"{artifact_dir}/scaler.pkl")
            mlflow.log_artifact(f"{artifact_dir}/features.pkl")
            
            # Sauvegarde locale pour backup
            os.makedirs("../../models", exist_ok=True)
            joblib.dump(self.model, "../../models/churn_model_xgboost.pkl")
            joblib.dump(self.features, "../../models/model_features.pkl")
            
            # Rapport de classification
            report = classification_report(y_test, y_pred, output_dict=True)
            with open(f"{artifact_dir}/classification_report.json", "w") as f:
                json.dump(report, f, indent=2)
            mlflow.log_artifact(f"{artifact_dir}/classification_report.json")
            
            print("✅ Entraînement terminé avec succès!")
            print("\n📊 Métriques du modèle:")
            for k, v in metrics.items():
                print(f"  {k}: {v:.4f}")
            
            return metrics
    
    def register_model(self, model_name="churn_xgboost_prod"):
        """Enregistre le modèle dans MLflow Model Registry"""
        print(f"📝 Enregistrement du modèle '{model_name}'...")
        
        client = mlflow.tracking.MlflowClient()
        
        # Vérifie si le modèle existe déjà
        try:
            existing_models = client.search_registered_models(filter_string=f"name='{model_name}'")
            if existing_models:
                print(f"⚠️  Modèle '{model_name}' existe déjà, création d'une nouvelle version")
        except:
            pass
        
        # Enregistre le modèle
        run_id = mlflow.active_run().info.run_id
        model_uri = f"runs:/{run_id}/churn_model"
        
        result = mlflow.register_model(
            model_uri=model_uri,
            name=model_name
        )
        
        print(f"✅ Modèle enregistré: {result.name} version {result.version}")
        
        # Transition vers Production
        client.transition_model_version_stage(
            name=model_name,
            version=result.version,
            stage="Production"
        )
        
        print("🚀 Modèle déplacé en stage 'Production'")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🚀 PIPELINE MLOps - Entraînement Modèle Churn")
    print("=" * 60)
    
    # Configuration
    data_path = "../../data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
    mlflow_tracking_uri = "http://mlflow:5000"
    
    # Configure MLflow
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    print(f"📡 MLflow Tracking URI: {mlflow_tracking_uri}")
    
    # Exécution du pipeline
    pipeline = ChurnModelPipeline(data_path)
    
    # 1. Chargement des données
    df = pipeline.load_data()
    
    # 2. Prétraitement
    X_train, X_test, y_train, y_test = pipeline.preprocess_data(df)
    
    # 3. Entraînement
    metrics = pipeline.train_model(X_train, y_train, X_test, y_test)
    
    # 4. Enregistrement
    pipeline.register_model()
    
    print("\n" + "=" * 60)
    print("🎉 PIPELINE TERMINÉ AVEC SUCCÈS!")
    print("=" * 60)

if __name__ == "__main__":
    main()
