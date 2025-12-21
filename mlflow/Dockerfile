FROM python:3.9-slim
RUN pip install --no-cache-dir \
    mlflow==2.8.1 \
    boto3==1.28.57 \
    psycopg2-binary==2.9.7 \
    pymysql==1.0.3
EXPOSE 5000
# La commande finale, avec --host 0.0.0.0
CMD ["mlflow", "server", \
     "--backend-store-uri", "postgresql://mlflow:mlflow@postgres-mlflow/mlflowdb", \
     "--default-artifact-root", "s3://mlflow-artifacts", \
     "--host", "0.0.0.0", \
     "--port", "5000"]
