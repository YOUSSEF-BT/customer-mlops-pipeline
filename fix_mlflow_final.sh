#!/bin/bash

echo "🚀 RÉPARATION COMPLÈTE DE MLFLOW"

cd ~/customer-mlops-pipeline

# 1. Arrêtez tout
docker-compose down

# 2. Supprimez les volumes problématiques
docker volume rm customer-mlops-pipeline_postgres-mlflow-data 2>/dev/null || true

# 3. Supprimez l'image MLflow pour la reconstruire
docker rmi customer-mlops-pipeline-mlflow 2>/dev/null || true

# 4. Assurez-vous que le Dockerfile MLflow est correct
cat > mlflow/Dockerfile << 'DOCKERFILE'
FROM python:3.9-slim

RUN pip install --no-cache-dir \
    mlflow==2.8.1 \
    boto3==1.28.57 \
    psycopg2-binary==2.9.7 \
    pymysql==1.0.3 \
    && rm -rf /tmp/*

EXPOSE 5000

CMD ["mlflow", "server", \
     "--backend-store-uri", "postgresql://mlflow:mlflow@postgres-mlflow/mlflowdb", \
     "--default-artifact-root", "s3://mlflow-artifacts", \
     "--host", "0.0.0.0", \
     "--port", "5000"]
DOCKERFILE

# 5. Créez un fichier .env pour les variables
cat > .env << 'ENVFILE'
MLFLOW_TRACKING_URI=http://localhost:5001
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
AIRFLOW__CORE__FERNET_KEY=46BKJoQYlPPOexq0OhDZnIlNepKFf87WFwLbfzqDDho=
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres-airflow/airflow
ENVFILE

# 6. Redémarrez
echo "🔄 Démarrage des services..."
docker-compose up -d

# 7. Attendez
echo "⏳ Attente du démarrage (45 secondes)..."
sleep 45

# 8. Vérifiez
echo "📊 État final :"
docker-compose ps

echo ""
echo "🔍 Test de MLflow :"
if curl -s --retry 3 --retry-delay 5 http://localhost:5001 > /dev/null; then
    echo "✅ MLflow fonctionne ! Accès : http://localhost:5001"
else
    echo "❌ MLflow échoue. Logs :"
    docker-compose logs --tail=30 mlflow
fi

echo ""
echo "🌐 Autres services :"
echo "   - Airflow:   http://localhost:8080 (admin/admin)"
echo "   - Streamlit: http://localhost:8502"
echo "   - MinIO:     http://localhost:9001 (minioadmin/minioadmin)"
