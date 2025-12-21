#!/bin/bash

echo "🔧 RÉPARATION DE MLFLOW"

cd ~/customer-mlops-pipeline

# 1. Arrêtez MLflow
docker-compose stop mlflow
docker-compose rm -f mlflow

# 2. Vérifiez que MinIO fonctionne
echo "🔍 Vérification de MinIO..."
curl -s http://localhost:9001 > /dev/null && echo "✅ MinIO fonctionne" || echo "❌ MinIO ne répond pas"

# 3. Vérifiez que PostgreSQL pour MLflow fonctionne
echo "🔍 Vérification de PostgreSQL MLflow..."
if docker-compose exec postgres-mlflow psql -U mlflow -d mlflowdb -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ PostgreSQL MLflow fonctionne"
else
    echo "❌ PostgreSQL MLflow échoue, redémarrage..."
    docker-compose restart postgres-mlflow
    sleep 5
fi

# 4. Recréez MLflow
echo "�� Redémarrage de MLflow..."
docker-compose up -d mlflow

# 5. Attendez
echo "⏳ Attente du démarrage (15 secondes)..."
sleep 15

# 6. Testez
echo "📊 Test de connexion..."
if curl -s --retry 3 --retry-delay 5 http://localhost:5001 > /dev/null; then
    echo "✅ MLflow fonctionne maintenant !"
    echo "🌐 Accès : http://localhost:5001"
else
    echo "❌ MLflow ne fonctionne toujours pas"
    echo "🔍 Logs de MLflow :"
    docker-compose logs --tail=30 mlflow
fi
