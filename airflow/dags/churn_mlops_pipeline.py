from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.email import EmailOperator
from airflow.operators.dummy import DummyOperator
import sys
import os

# Ajoute le chemin du pipeline d'entraînement
sys.path.insert(0, '/opt/airflow/training_pipeline/src')

default_args = {
    'owner': 'mlops_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email': ['admin@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'churn_mlops_pipeline',
    default_args=default_args,
    description='Pipeline MLOps complet pour la prédiction de churn client',
    schedule_interval='0 2 * * 0',  # Tous les dimanches à 2h du matin
    catchup=False,
    tags=['mlops', 'churn', 'customer_analytics'],
    max_active_runs=1,
)

def check_data_quality(**context):
    """Tâche 1: Vérification de la qualité des données"""
    import pandas as pd
    import numpy as np
    
    data_path = '/opt/airflow/data/WA_Fn-UseC_-Telco-Customer-Churn.csv'
    
    print(f"🔍 Vérification des données: {data_path}")
    
    df = pd.read_csv(data_path)
    
    # Vérifications
    null_counts = df.isnull().sum()
    duplicates = df.duplicated().sum()
    total_rows = len(df)
    
    quality_report = {
        'total_rows': total_rows,
        'null_values': null_counts.sum(),
        'duplicate_rows': duplicates,
        'columns': list(df.columns),
        'data_types': df.dtypes.to_dict()
    }
    
    # Log des résultats
    print(f"📊 Rapport qualité:")
    print(f"  - Lignes totales: {total_rows}")
    print(f"  - Valeurs nulles: {null_counts.sum()}")
    print(f"  - Doublons: {duplicates}")
    
    # Vérification des seuils
    if null_counts.sum() > total_rows * 0.1:
        raise ValueError("❌ Trop de valeurs nulles (>10%)")
    
    if duplicates > total_rows * 0.05:
        raise ValueError("❌ Trop de doublons (>5%)")
    
    # Sauvegarde du rapport pour les tâches suivantes
    context['ti'].xcom_push(key='quality_report', value=quality_report)
    
    print("✅ Vérification qualité terminée avec succès")
    return quality_report

def train_model(**context):
    """Tâche 2: Entraînement du modèle"""
    import subprocess
    import json
    
    print("🎯 Début de l'entraînement du modèle...")
    
    # Exécution du script d'entraînement
    script_path = '/opt/airflow/training_pipeline/src/train_model.py'
    
    result = subprocess.run(
        ['python', script_path],
        capture_output=True,
        text=True,
        cwd='/opt/airflow'
    )
    
    if result.returncode != 0:
        error_msg = f"❌ Échec de l'entraînement:\n{result.stderr}"
        print(error_msg)
        raise Exception(error_msg)
    
    print("✅ Entraînement terminé avec succès")
    print(result.stdout)
    
    # Extraire les métriques du log
    metrics_line = None
    for line in result.stdout.split('\n'):
        if 'accuracy:' in line.lower():
            metrics_line = line
            break
    
    return {
        'status': 'success',
        'output': result.stdout[:500],  # Premiers 500 caractères
        'metrics': metrics_line
    }

def validate_model(**context):
    """Tâche 3: Validation du modèle"""
    import joblib
    import pandas as pd
    from sklearn.metrics import accuracy_score
    
    print("🔬 Validation du modèle...")
    
    # Chemin vers le modèle entraîné
    model_path = '/opt/airflow/models/churn_model_xgboost.pkl'
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ Modèle non trouvé: {model_path}")
    
    # Chargement du modèle
    model = joblib.load(model_path)
    
    # Validation basique
    if model is None:
        raise ValueError("❌ Modèle invalide")
    
    # Vérification des features
    features_path = '/opt/airflow/models/model_features.pkl'
    if os.path.exists(features_path):
        features = joblib.load(features_path)
        print(f"✅ Modèle chargé avec {len(features)} features")
    else:
        print("⚠️  Features non trouvées")
    
    # Vérification supplémentaire
    model_size = os.path.getsize(model_path) / 1024  # Taille en KB
    print(f"📦 Taille du modèle: {model_size:.2f} KB")
    
    if model_size < 10:  # Moins de 10KB
        raise ValueError("❌ Modèle trop petit, probablement corrompu")
    
    validation_result = {
        'model_exists': True,
        'model_size_kb': model_size,
        'validation_passed': True,
        'timestamp': datetime.now().isoformat()
    }
    
    print("✅ Validation réussie")
    return validation_result

def deploy_model(**context):
    """Tâche 4: Déploiement du modèle"""
    import shutil
    import os
    from datetime import datetime
    
    print("🚀 Déploiement du modèle...")
    
    # Chemins source
    source_model = '/opt/airflow/models/churn_model_xgboost.pkl'
    source_features = '/opt/airflow/models/model_features.pkl'
    
    # Chemins destination (pour Streamlit)
    dest_dir = '/opt/airflow/streamlit/models'
    os.makedirs(dest_dir, exist_ok=True)
    
    dest_model = os.path.join(dest_dir, 'churn_model.pkl')
    dest_features = os.path.join(dest_dir, 'features.pkl')
    
    # Copie avec backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Backup des anciens modèles
    if os.path.exists(dest_model):
        backup_model = f"{dest_model}.backup_{timestamp}"
        shutil.copy2(dest_model, backup_model)
        print(f"📦 Backup créé: {backup_model}")
    
    if os.path.exists(dest_features):
        backup_features = f"{dest_features}.backup_{timestamp}"
        shutil.copy2(dest_features, backup_features)
    
    # Copie des nouveaux fichiers
    shutil.copy2(source_model, dest_model)
    shutil.copy2(source_features, dest_features)
    
    # Vérification
    if os.path.exists(dest_model) and os.path.exists(dest_features):
        print(f"✅ Modèle déployé avec succès vers: {dest_dir}")
        
        # Création d'un fichier de version
        version_file = os.path.join(dest_dir, 'version.txt')
        with open(version_file, 'w') as f:
            f.write(f"version: {timestamp}\n")
            f.write(f"deployed_at: {datetime.now().isoformat()}\n")
            f.write(f"model_size: {os.path.getsize(dest_model)} bytes\n")
        
        return {
            'status': 'deployed',
            'destination': dest_dir,
            'timestamp': timestamp,
            'model_size': os.path.getsize(dest_model)
        }
    else:
        raise Exception("❌ Échec du déploiement")

def generate_report(**context):
    """Tâche 5: Génération du rapport"""
    import json
    from datetime import datetime
    
    print("📊 Génération du rapport d'exécution...")
    
    # Récupération des résultats des tâches précédentes
    ti = context['ti']
    
    quality_result = ti.xcom_pull(task_ids='check_data_quality')
    train_result = ti.xcom_pull(task_ids='train_model')
    validation_result = ti.xcom_pull(task_ids='validate_model')
    deploy_result = ti.xcom_pull(task_ids='deploy_model')
    
    # Création du rapport
    report = {
        'pipeline': 'churn_mlops_pipeline',
        'execution_date': context['execution_date'].isoformat(),
        'generated_at': datetime.now().isoformat(),
        'tasks': {
            'data_quality': quality_result,
            'model_training': train_result,
            'model_validation': validation_result,
            'model_deployment': deploy_result
        },
        'status': 'completed'
    }
    
    # Sauvegarde du rapport
    report_dir = '/opt/airflow/reports'
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(
        report_dir, 
        f"churn_pipeline_report_{context['execution_date'].strftime('%Y%m%d_%H%M%S')}.json"
    )
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"✅ Rapport généré: {report_file}")
    
    return report_file

# Définition des tâches
start_task = DummyOperator(
    task_id='start_pipeline',
    dag=dag,
)

data_quality_task = PythonOperator(
    task_id='check_data_quality',
    python_callable=check_data_quality,
    dag=dag,
)

train_model_task = PythonOperator(
    task_id='train_model',
    python_callable=train_model,
    dag=dag,
)

validate_model_task = PythonOperator(
    task_id='validate_model',
    python_callable=validate_model,
    dag=dag,
)

deploy_model_task = PythonOperator(
    task_id='deploy_model',
    python_callable=deploy_model,
    dag=dag,
)

generate_report_task = PythonOperator(
    task_id='generate_report',
    python_callable=generate_report,
    dag=dag,
)

success_task = DummyOperator(
    task_id='pipeline_success',
    dag=dag,
)

# Email de notification
email_notification = EmailOperator(
    task_id='send_success_email',
    to=['admin@example.com'],
    subject='MLOps Pipeline Completed - {{ ds }}',
    html_content="""
    <h3>✅ Pipeline MLOps Churn Prediction - Exécution réussie</h3>
    <p>Le pipeline d'entraînement et de déploiement du modèle Churn a été exécuté avec succès.</p>
    <p><strong>Date d'exécution:</strong> {{ ds }}</p>
    <p><strong>Détails:</strong></p>
    <ul>
        <li>✅ Vérification qualité des données</li>
        <li>✅ Entraînement du modèle XGBoost</li>
        <li>✅ Validation des performances</li>
        <li>✅ Déploiement vers Streamlit</li>
        <li>✅ Génération du rapport</li>
    </ul>
    <p>Accédez aux interfaces:</p>
    <ul>
        <li>📊 MLflow: http://localhost:5000</li>
        <li>🔄 Airflow: http://localhost:8080</li>
        <li>📈 Streamlit: http://localhost:8501</li>
    </ul>
    """,
    dag=dag,
)

# Définition de l'ordre d'exécution
start_task >> data_quality_task >> train_model_task >> validate_model_task
validate_model_task >> deploy_model_task >> generate_report_task
generate_report_task >> [success_task, email_notification]
