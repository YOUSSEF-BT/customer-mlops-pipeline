#!/bin/bash
cd ~/customer-mlops-pipeline

echo "1. Vérification des services..."
docker-compose ps

echo ""
echo "2. Test MLflow..."
curl -s http://localhost:5001/health && echo "✅ MLflow accessible" || echo "❌ MLflow inaccessible"

echo ""
echo "3. Test Airflow..."
curl -s http://localhost:8080/health && echo "✅ Airflow accessible" || echo "❌ Airflow inaccessible"

echo ""
echo "4. Configuration MinIO pour MLflow..."
# Attendez que MinIO soit prêt
sleep 5

echo ""
echo "🌐 URLs :"
echo "   Airflow:   http://localhost:8080"
echo "   MLflow:    http://localhost:5001"
echo "   MinIO:     http://localhost:9001 (minioadmin/minioadmin)"
echo "   Streamlit: http://localhost:8502"
