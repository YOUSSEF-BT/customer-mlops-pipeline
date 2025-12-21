# 🚀 Customer Analytics & Churn Prediction MLOps Platform

![MLOps Architecture](https://img.shields.io/badge/MLOps-Platform-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-green)
![Python](https://img.shields.io/badge/Python-3.9-yellow)
![Airflow](https://img.shields.io/badge/Airflow-2.7-red)
![MLflow](https://img.shields.io/badge/MLflow-2.8-orange)

A complete MLOps pipeline for customer churn prediction with automated training, experiment tracking, and real-time monitoring.

## 📊 Architecture

graph TB
    A[Airflow Orchestrator] --> B[Data Processing]
    B --> C[Model Training]
    C --> D[MLflow Tracking]
    D --> E[MinIO Artifact Store]
    D --> F[Streamlit Dashboard]
    G[PostgreSQL] --> D
    G --> A
    H[MinIO Storage] --> E
    I[Streamlit UI] --> F

🏗️ Tech Stack
Component	Purpose	Technology
Orchestration	Workflow automation	Apache Airflow 2.7
Experiment Tracking	ML model versioning	MLflow 2.8
Artifact Storage	Model storage	MinIO (S3-compatible)
Visualization	Real-time dashboard	Streamlit
Metadata Storage	Experiment metadata	PostgreSQL 13
Containerization	Service isolation	Docker Compose
🚀 Quick Start
Prerequisites
Docker 20.10+ & Docker Compose 2.0+

Git

8GB+ RAM recommended

Installation
bash
# Clone the repository
git clone https://github.com/YOUSSEF-BT/customer-mlops-pipeline.git
cd customer-mlops-pipeline

# Start all services
docker-compose up -d

# Wait for services to start
sleep 45

# Initialize Airflow database and create admin user
docker-compose exec airflow-webserver airflow db init
docker-compose exec airflow-webserver airflow users create \
    --username admin --password admin \
    --firstname Admin --lastname User \
    --role Admin --email admin@example.com
📁 Project Structure
text
customer-mlops-pipeline/
├── airflow/                 # Airflow configuration
│   ├── dags/              # Pipeline DAGs
│   ├── Dockerfile         # Airflow container
│   └── requirements.txt   # Python dependencies
├── mlflow/                # MLflow tracking server
│   └── Dockerfile         # MLflow container
├── streamlit/             # Streamlit dashboard
│   ├── Dockerfile         # Streamlit container
│   ├── requirements.txt   # Python dependencies
│   └── streamlit_app.py   # Dashboard application
├── training_pipeline/     # Model training scripts
│   ├── config.yaml       # Configuration file
│   └── src/train_model.py # Training pipeline
├── data/                  # Sample data (gitignored)
├── models/               # Trained models (gitignored)
├── docker-compose.yml    # Complete service orchestration
├── .gitignore           # Git ignore file
├── LICENSE              # MIT License
└── README.md           # This file
🔧 Services Configuration
Service	Port	Default Credentials	Purpose
Airflow Webserver	8080	admin/admin	Workflow orchestration UI
Airflow Scheduler	-	-	Task scheduling
MLflow	5001	-	Experiment tracking UI
MinIO	9000	minioadmin/minioadmin	Object storage API
MinIO Console	9001	minioadmin/minioadmin	Storage management UI
Streamlit	8502	-	Real-time dashboard
Adminer	8081	-	Database management UI
PostgreSQL (Airflow)	5432	airflow/airflow	Airflow metadata
PostgreSQL (MLflow)	5432	mlflow/mlflow	MLflow metadata
📈 Features
✅ Complete MLOps Pipeline
Automated Data Processing: Data ingestion, cleaning, and feature engineering

Model Training: Multiple algorithms with hyperparameter tuning

Experiment Tracking: Full MLflow integration for reproducibility

Artifact Versioning: Model storage in MinIO with version control

Real-time Monitoring: Live dashboard with Streamlit

✅ Scalable Architecture
Microservices: Each component runs in isolated containers

Persistent Storage: PostgreSQL for metadata, MinIO for artifacts

Network Isolation: Secure internal networking between services

Health Checks: Automatic service monitoring and restart

✅ Monitoring & Visualization
Streamlit Dashboard: Interactive customer analytics and predictions

MLflow UI: Experiment comparison and model registry

Airflow UI: Pipeline monitoring and manual triggering

MinIO Console: Artifact storage management

🎯 Usage Guide
Step 1: Start the Platform
bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
Step 2: Access Interfaces
Airflow UI: http://localhost:8080 (admin/admin)

MLflow UI: http://localhost:5001

Streamlit Dashboard: http://localhost:8502

MinIO Console: http://localhost:9001 (minioadmin/minioadmin)

Step 3: Configure MLflow Artifact Storage
bash
# Setup MinIO bucket for MLflow
docker-compose exec minio mc alias set myminio http://localhost:9000 minioadmin minioadmin
docker-compose exec minio mc mb myminio/mlflow-artifacts
Step 4: Run the Training Pipeline
Go to Airflow UI (http://localhost:8080)

Find DAG: churn_mlops_pipeline

Toggle activation switch (ON)

Click trigger button (▶️)

Monitor execution in Graph View

Step 5: View Results
MLflow: Track experiments, compare models, view metrics

Streamlit: Visualize predictions, customer segments, model performance

MinIO: Browse stored models and artifacts

🛠️ Development
Adding New Models
Modify training_pipeline/src/train_model.py

Update training_pipeline/config.yaml

Test locally: python train_model.py

Commit changes and push

Modifying the Dashboard
Edit streamlit/streamlit_app.py

Update dependencies in streamlit/requirements.txt

Rebuild: docker-compose build streamlit-app

Restart: docker-compose up -d streamlit-app

Adding New DAGs
Add Python file to airflow/dags/

Follow Airflow DAG best practices

Test in Airflow UI

🔍 Troubleshooting
Common Issues
MLflow won't start:

bash
# Check PostgreSQL connection
docker-compose exec postgres-mlflow psql -U mlflow -d mlflowdb -c "SELECT 1;"

# Rebuild MLflow service
docker-compose build --no-cache mlflow
docker-compose up -d mlflow
Airflow database errors:

bash
# Initialize Airflow database
docker-compose exec airflow-webserver airflow db init

# Create admin user (if not exists)
docker-compose exec airflow-webserver airflow users create \
    --username admin --password admin \
    --firstname Admin --lastname User \
    --role Admin --email admin@example.com
MinIO bucket permissions:

bash
# Make bucket public (for development)
docker-compose exec minio mc anonymous set public myminio/mlflow-artifacts
Service Logs
bash
# View specific service logs
docker-compose logs mlflow
docker-compose logs airflow-webserver
docker-compose logs streamlit-app

# Follow logs in real-time
docker-compose logs -f mlflow
Resource Issues
bash
# Check resource usage
docker stats

# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v
🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit changes (git commit -m 'Add AmazingFeature')

Push to branch (git push origin feature/AmazingFeature)

Open a Pull Request

Development Guidelines
Follow PEP 8 for Python code

Add docstrings for functions and classes

Update documentation when changing features

Test changes locally before submitting PR

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👤 Author
YOUSSEF-BT

GitHub: @YOUSSEF-BT

Project: Customer MLOps Pipeline

🙏 Acknowledgments
Apache Airflow team for workflow orchestration

MLflow team for experiment tracking

Streamlit team for rapid dashboard development

MinIO team for S3-compatible storage

Docker community for containerization

📚 References
Airflow Documentation

MLflow Documentation

Streamlit Documentation

MinIO Documentation

Docker Compose Documentation

🌟 Show Your Support
Give a ⭐️ if this project helped you!

Happy MLOps Engineering! 🚀

Built with ❤️ by YOUSSEF-BT

📊 Performance Metrics
Metric	Value	Description
Startup Time	~2 minutes	Time for all services to be ready
Model Training	~5-10 minutes	Full pipeline execution
Storage	2GB+	Estimated for 1000+ experiments
Concurrent Users	10+	Dashboard and monitoring
🔄 Continuous Integration
This project includes:

Docker Compose for local development

PostgreSQL for persistent metadata

MinIO for scalable artifact storage

Health checks for all services

Next Steps:

Deploy to cloud (AWS/Azure/GCP)

Add CI/CD pipeline

Implement model monitoring

Add A/B testing capabilities

Last Updated: December 2024
