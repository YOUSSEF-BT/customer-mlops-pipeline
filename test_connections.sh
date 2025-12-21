#!/bin/bash
cd ~/customer-mlops-pipeline

echo "🔗 TESTS DE CONNEXION ENTRE SERVICES"
echo "====================================="

echo "1. PostgreSQL (Airflow) :"
docker-compose exec postgres-airflow pg_isready -U airflow && echo "   ✅ OK" || echo "   ❌ Échec"

echo "2. PostgreSQL (MLflow) :"
docker-compose exec postgres-mlflow pg_isready -U mlflow && echo "   ✅ OK" || echo "   ❌ Échec"

echo "3. MinIO :"
docker-compose exec minio mc alias set myminio http://localhost:9000 minioadmin minioadmin 2>/dev/null
docker-compose exec minio mc admin info myminio 2>/dev/null && echo "   ✅ OK" || echo "   ❌ Échec"

echo "4. MLflow (depuis l'hôte) :"
curl -s http://localhost:5001/health | grep -q "OK" && echo "   ✅ OK" || echo "   ❌ Échec"

echo "5. MLflow (depuis le réseau interne) :"
docker-compose exec mlflow curl -s http://localhost:5000/health | grep -q "OK" && echo "   ✅ OK" || echo "   ❌ Échec"

echo "6. Airflow → MLflow :"
docker-compose exec airflow-webserver python -c "
import os
uri = os.getenv('MLFLOW_TRACKING_URI', 'non défini')
print(f'   URI MLflow: {uri}')
import requests
try:
    r = requests.get('http://mlflow:5000', timeout=3)
    print('   ✅ Connexion réussie')
except Exception as e:
    print(f'   ❌ Échec: {e}')
"

echo "7. Streamlit → MLflow :"
docker-compose exec streamlit-app python -c "
import os
uri = os.getenv('MLFLOW_TRACKING_URI', 'non défini')
print(f'   URI MLflow: {uri}')
import requests
try:
    r = requests.get('http://mlflow:5000', timeout=3)
    print('   ✅ Connexion réussie')
except Exception as e:
    print(f'   ❌ Échec: {e}')
"

echo ""
echo "🌐 ACCÈS AUX INTERFACES :"
echo "   Airflow:   http://localhost:8080 (admin/admin)"
echo "   MLflow:    http://localhost:5001"
echo "   Streamlit: http://localhost:8502"
echo "   MinIO:     http://localhost:9001 (minioadmin/minioadmin)"
echo "   Adminer:   http://localhost:8081 (PostgreSQL viewer)"
