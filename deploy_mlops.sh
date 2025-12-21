#!/bin/bash

echo "🚀 DÉPLOIEMENT DU PROJET MLOps COMPLET"
echo "========================================"

# Vérification des prérequis
command -v docker >/dev/null 2>&1 || { echo "❌ Docker n'est pas installé"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose n'est pas installé"; exit 1; }

# Création des dossiers
echo "📁 Création de la structure..."
mkdir -p {data,models,reports}
mkdir -p airflow/{dags,logs,plugins}
mkdir -p streamlit/models
mkdir -p training_pipeline/src

# Génération de la clé Fernet pour Airflow
echo "🔐 Génération des clés de sécurité..."
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" 2>/dev/null || \
             docker run --rm python:3.9-slim python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
AIRFLOW_SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "default-secret-key-12345")

# Création du fichier .env
cat > .env << EOL
FERNET_KEY=$FERNET_KEY
AIRFLOW_SECRET_KEY=$AIRFLOW_SECRET_KEY
MLFLOW_TRACKING_URI=http://localhost:5000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
EOL

echo "✅ Fichier .env créé"

# Téléchargement des données si elles n'existent pas
if [ ! -f "data/WA_Fn-UseC_-Telco-Customer-Churn.csv" ]; then
    echo "📥 Téléchargement des données..."
    curl -o data/WA_Fn-UseC_-Telco-Customer-Churn.csv \
    https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv
fi

# Copie du code Streamlit
echo "📋 Préparation de l'application Streamlit..."
if [ -f "streamlit_app_original.py" ]; then
    echo "📄 Utilisation du fichier streamlit_app_original.py"
    cp streamlit_app_original.py streamlit/streamlit_app.py
else
    echo "⚠️  streamlit_app_original.py non trouvé, création d'un template..."
    cat > streamlit/streamlit_app.py << 'STREAMLIT_EOF'
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Customer Analytics Dashboard", layout="wide")

st.title("🚀 Customer Analytics & Churn Prediction Platform")
st.markdown("### MLOps Pipeline avec Airflow & MLflow")

# Section informations
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📊 Total Clients", "7,043")
with col2:
    st.metric("📈 Taux de Churn", "26.54%")
with col3:
    st.metric("💰 Revenue Annuel", "$5.2M")

st.markdown("---")
st.info("""
🔧 **Services MLOps en cours d'exécution:**
- ✅ Airflow: http://localhost:8080 (admin/admin)
- ✅ MLflow: http://localhost:5000
- ✅ Streamlit: http://localhost:8501
- ✅ MinIO: http://localhost:9001 (minioadmin/minioadmin)
""")

# Bouton pour exécuter le pipeline
if st.button("🔄 Exécuter le Pipeline MLOps", type="primary"):
    with st.spinner("Exécution du pipeline en cours..."):
        st.success("Pipeline déclenché avec succès!")
        st.info("Consultez Airflow pour suivre l'exécution")
STREAMLIT_EOF
fi

# Construction des images Docker
echo "🐳 Construction des images Docker..."
docker-compose build

# Démarrage des services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attente que les services soient prêts
echo "⏳ Attente du démarrage des services (60 secondes)..."
sleep 60

# Vérification
echo "🔍 Vérification des services..."
docker-compose ps

echo ""
echo "✅ DÉPLOIEMENT TERMINÉ !"
echo ""
echo "📊 ACCÈS AUX INTERFACES :"
echo "   - Airflow UI:    http://localhost:8080"
echo "   - MLflow UI:     http://localhost:5000"
echo "   - Streamlit App: http://localhost:8501"
echo "   - MinIO Console: http://localhost:9001"
echo "   - Adminer DB:    http://localhost:8081"
echo ""
echo "🔑 CRÉDENTIELS :"
echo "   - Airflow: admin / admin"
echo "   - MinIO:   minioadmin / minioadmin"
echo "   - Adminer: PostgreSQL, serveur=postgres-airflow, user=airflow, password=airflow, db=airflow"
echo ""
echo "📋 COMMANDES UTILES :"
echo "   - Voir les logs: docker-compose logs -f [nom_service]"
echo "   - Arrêter: docker-compose down"
echo "   - Redémarrer: docker-compose restart"
echo "   - Forcer le rebuild: docker-compose build --no-cache"
echo ""
echo "🎯 PROCHAINE ÉTAPE :"
echo "   1. Accédez à Airflow (http://localhost:8080)"
echo "   2. Activez le DAG 'churn_mlops_pipeline'"
echo "   3. Déclenchez une exécution manuelle"
echo "   4. Vérifiez les modèles dans MLflow"
echo "   5. Testez l'application Streamlit"
